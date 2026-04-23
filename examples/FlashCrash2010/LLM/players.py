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
        import os

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
            lm_name=llm_cfg["model"],
            generation_config={
                "temperature": llm_cfg.get("temperature", 0.3),
                "max_tokens": llm_cfg.get("max_tokens", 512),
            },
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
                    lm_name=llm_cfg["model"],
                    generation_config={
                        "temperature": llm_cfg.get("temperature", 0.3),
                        "max_tokens": llm_cfg.get("max_tokens", 512),
                    },
                )

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state.get("market_data", {})
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])

        price = market_data.get("price", 0.0)
        user_prompt = user_template.format(
            round=round_num,
            price=price,
            prev_price=market_data.get("prev_price", price),
            return_pct=market_data.get("return_pct", 0.0),
            fundamental=market_data.get("fundamental", price),
            deviation=market_data.get("deviation", 0.0) * 100,
            spread=market_data.get("spread", 0.0),
            depth=market_data.get("depth", 0.0),
            volatility=market_data.get("volatility", 0.0),
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

        decision = None
        for _ in range(3):
            try:
                output = llm_client.run(
                    [InferInput(system_msg=system_prompt, user_msg=user_prompt)]
                )
                decision = parse_llm_response_with_thinking(output.outputs[0].response)
                break
            except Exception:  # pylint: disable=broad-except
                decision = None

        if decision is None:
            decision = {
                "bid_price": price,
                "quantity": 0,
                "reasoning": "parse error",
                "analysis": "",
            }

        bid_price = float(decision.get("bid_price", price))
        quantity = float(decision.get("quantity", 0))

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
        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": str(decision.get("reasoning", ""))[:120],
            "analysis": str(decision.get("analysis", "")),
            "agent_type": "llm",
            "provides_liquidity": False,
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


class LLMHFTMarketMaker(LLMInvestor):
    """LLM-driven HFT market maker."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_HFT_MARKET_MAKER_SYS"


class LLMMomentumChaser(LLMInvestor):
    """LLM-driven momentum chaser."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_MOMENTUM_CHASER_SYS"


class LLMFundamentalTrader(LLMInvestor):
    """LLM-driven fundamental trader."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_FUNDAMENTAL_SYS"


class LLMStopLossTrader(LLMInvestor):
    """LLM-driven stop-loss trader."""

    _system_prompt_path = "examples.FlashCrash2010.LLM.prompts:LLM_STOP_LOSS_SYS"


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader."""

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
