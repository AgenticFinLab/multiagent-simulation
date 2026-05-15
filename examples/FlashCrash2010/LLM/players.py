"""FlashCrash2010 LLM-Based Simulation

Design:
    - Market coordinator: rule-based price dynamics (same as FlashCrash2010 Rule)
    - Investors: LLM-driven with agent persona system prompts

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
from masim.format.order import validate_order
from examples.FlashCrash2010.Rule.players import Market  # noqa: F401

logger = logging.getLogger("FlashCrash2010.LLM")


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-powered FlashCrash2010 investors."""

    _system_prompt_path: str = ""

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
        self.state.custom_state["llm_params"] = llm_cfg
        self.state.custom_state["llm_client"] = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
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
            if "llm_params" in custom and "llm_client" not in custom:
                llm_cfg = custom["llm_params"]
                custom["llm_client"] = LangChainAPIInference(
                    lm_name=llm_cfg["lm_name"],
                    generation_config=llm_cfg["generation_config"],
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
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

        decision = None
        last_error = None
        for attempt in range(3):
            try:
                output = llm_client.run(
                    [InferInput(system_msg=system_prompt, user_msg=user_prompt)]
                )
                decision = parse_llm_response_with_thinking(output.outputs[0].response)
                break
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
            )

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        # Guard: LLMs sometimes output bid_price=0 for hold actions.
        # Use the current market price so recorded bids stay meaningful.
        if bid_price <= 0:
            bid_price = market_data["price"]

        if action == "buy":
            max_buy = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_buy)
        elif action == "sell":
            quantity = max(quantity, -position)

        if action == "buy":
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] += quantity

        strategy_name = self.__class__.__name__
        order = {
            "action": action,
            "bid_price": bid_price,
            "action": action,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": str(decision["reasoning"])[:120],
            "analysis": str(decision["analysis"]),
            "agent_type": "llm",
            "provides_liquidity": False,
        }
        validate_order(order)
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


class LLMHFTMarketMaker(LLMInvestor):
    """LLM-driven HFT market maker — liquidity withdrawal under stress via LLM reasoning. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_HFT_MARKET_MAKER_SYS"


class LLMMomentumChaser(LLMInvestor):
    """LLM-driven momentum chaser — trend amplification via LLM systematic reasoning. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_MOMENTUM_CHASER_SYS"


class LLMFundamentalTrader(LLMInvestor):
    """LLM-driven fundamental trader — value-based stabilization via LLM analytical reasoning. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_FUNDAMENTAL_SYS"


class LLMStopLossTrader(LLMInvestor):
    """LLM-driven stop-loss trader — cascade selling via LLM risk management reasoning. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_STOP_LOSS_SYS"


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — random background activity via LLM reasoning. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMHFTMarketMaker",
    "LLMMomentumChaser",
    "LLMFundamentalTrader",
    "LLMStopLossTrader",
    "LLMNoiseTrader",
]
