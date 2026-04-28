"""FlashCrash2010 RuleLLM - Hybrid Rule+LLM Flash Crash 2010 Simulation

Design:
    - Market coordinator: identical rule-based price dynamics as FlashCrash2010
    - Investors: LLM-powered with system prompts that embed explicit quantitative
      rules from the rule-based counterpart alongside agent persona descriptions

All parameters are configured via players.yml config file.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from typing import Any, Dict, Optional

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from examples.llm_utils import parse_llm_response_with_thinking
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from examples.FlashCrash2010.Rule.players import Market  # noqa: F401

logger = logging.getLogger("FlashCrash2010.RuleLLM")


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RuleLLMInvestor(GeneralPlayer):
    """Base class for hybrid Rule+LLM FlashCrash2010 investors."""

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        record_path = extras["record_path"]
        base_path = os.path.join(record_path, self.config.identity)
        hot_limit = extras["custom_state_hot_limit"]

        self.state.custom_state["cash"] = float(extras["initial_cash"])
        self.state.custom_state["position"] = int(extras["initial_position"])
        self.state.custom_state["price_history"] = HistoryBuffer(
            folder=os.path.join(base_path, "price"),
            entry_limit=hot_limit,
        )

        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        load_dotenv(os.path.join(project_root, ".env"))

        llm_cfg = extras["llm"]
        lm_name = llm_cfg["lm_name"]
        generation_config = llm_cfg["generation_config"]
        self.state.custom_state["lm_name"] = lm_name
        self.state.custom_state["generation_config"] = generation_config
        self.state.custom_state["llm_client"] = LangChainAPIInference(
            lm_name=lm_name,
            generation_config=generation_config,
        )

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            custom.pop("llm_client", None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "lm_name" in custom and "llm_client" not in custom:
                custom["llm_client"] = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])

        price = market_data["price"]
        price_hist = list(self.state.custom_state["price_history"])
        recent_prices = price_hist[-5:] if len(price_hist) >= 5 else price_hist

        user_prompt = user_template.format(
            round=round_num,
            price=price,
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            fundamental=market_data["fundamental"],
            deviation=market_data["deviation"] * 100,
            spread=market_data["spread"],
            depth=market_data["depth"],
            volatility=market_data["volatility"],
            recent_prices=recent_prices,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] Parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            logger.warning(
                "[%s] LLM failed after %d attempts: %s",
                self.identity,
                max_retries,
                last_error,
            )
            order = {
                "bid_price": price,
                "quantity": 0.0,
                "strategy": self.__class__.__name__,
                "investor": self.identity,
                "reasoning": "LLM parse failed: held position",
                "analysis": "",
                "provides_liquidity": False,
            }
            return {
                **order,
                "outbound_messages": [
                    {"payload": order, "content_type": "investor_order"}
                ],
            }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        if quantity > 0:
            max_buy = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_buy)
        elif quantity < 0:
            quantity = max(quantity, -position)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        strategy_name = self.__class__.__name__
        logger.debug(
            "[%-25s] R%d (%-25s): P=%7.2f  Q=%+7.2f",
            self.identity,
            round_num,
            strategy_name,
            bid_price,
            quantity,
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": str(decision["reasoning"])[:120],
            "analysis": str(decision["analysis"]),
            "provides_liquidity": bool(decision["provides_liquidity"]),
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class RuleLLMHFTMarketMaker(RuleLLMInvestor):
    """Hybrid: HFT liquidity withdrawal rules + LLM reasoning. Theory: simulation-bases.md §4.1."""


class RuleLLMMomentumChaser(RuleLLMInvestor):
    """Hybrid: Trend-following momentum rules + LLM reasoning. Theory: simulation-bases.md §4.2."""


class RuleLLMFundamentalTrader(RuleLLMInvestor):
    """Hybrid: Value deviation rules + LLM analytical reasoning. Theory: simulation-bases.md §4.3."""


class RuleLLMStopLossTrader(RuleLLMInvestor):
    """Hybrid: Stop-loss trigger rules + LLM risk management reasoning. Theory: simulation-bases.md §4.4."""


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """Hybrid: Random trading probability rules + LLM reasoning. Theory: simulation-bases.md §4.5."""


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMHFTMarketMaker",
    "RuleLLMMomentumChaser",
    "RuleLLMFundamentalTrader",
    "RuleLLMStopLossTrader",
    "RuleLLMNoiseTrader",
]
