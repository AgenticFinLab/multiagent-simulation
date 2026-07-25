"""CarryTradeUnwind LLM Simulation — LLM-driven agents with persona prompts."""

from __future__ import annotations

import importlib
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from masim.utils.llm_utils import parse_llm_response_with_thinking
from examples.CarryTradeUnwind.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base LLM-driven investor for CarryTradeUnwind."""

    _system_prompt_path: str = ""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = float(extras["initial_cash"])
        self.state.custom_state["position"] = int(extras["initial_position"])
        self.state.custom_state["price_history"] = []
        self.state.custom_state["market_data"] = {}
        self.state.custom_state["history_buffer"] = HistoryBuffer(
            folder=f"CarryTradeUnwind/LLM/{self.__class__.__name__}", entry_limit=200
        )
        load_dotenv()
        llm_cfg = extras["llm"]
        self.state.custom_state["llm_params"] = llm_cfg
        self.state.custom_state["llm_client"] = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )

    def __getstate__(self) -> Dict:
        state = self.__dict__.copy()
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            state["state"].custom_state.pop("llm_client", None)
        return state

    def __setstate__(self, state: Dict) -> None:
        self.__dict__.update(state)
        cs = self.state.custom_state
        if "llm_params" in cs and "llm_client" not in cs:
            llm_cfg = cs["llm_params"]
            cs["llm_client"] = LangChainAPIInference(
                lm_name=llm_cfg["lm_name"],
                generation_config=llm_cfg["generation_config"],
            )

    async def decide(self) -> Dict:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        portfolio_value = cash + position * price
        round_num = self.state.custom_state["round"]

        system_prompt = load_prompt(self._system_prompt_path)
        user_template = load_prompt(
            "examples.CarryTradeUnwind.LLM.prompts:LLM_USER_TEMPLATE"
        )
        user_prompt = user_template.format(
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )

        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        last_error = None
        parsed = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                result = llm_client.run([infer_input]).outputs[0]
                response = result.response
                parsed = parse_llm_response_with_thinking(response)
                action_str = parsed["action"]
                if action_str not in ("buy", "sell", "hold"):
                    raise ValueError(f"Invalid LLM action: {action_str}")
                bid_price = float(parsed["bid_price"])
                if bid_price <= 0:
                    raise ValueError(f"Invalid bid_price: {bid_price}")
                _ = str(parsed["reasoning"])
                break
            except Exception as exc:
                logger.warning("LLM attempt %d failed: %s", attempt + 1, exc)
                last_error = exc
                if attempt == 2:
                    raise RuntimeError(
                        f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
                    ) from last_error

        if parsed is None:
            raise RuntimeError(f"[{self.identity}] LLM produced no parseable decision")

        action_str = parsed["action"]
        quantity = int(parsed["quantity"])
        bid_price = float(parsed["bid_price"])
        quantity = max(0, quantity)
        if action_str == "buy":
            quantity = min(quantity, int(cash / price) if price > 0 else 0)
        elif action_str == "sell":
            quantity = min(quantity, max(position, 0))

        if action_str == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action_str == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "action": action_str,
            "bid_price": bid_price,
            "quantity": quantity,
            "reasoning": str(parsed["reasoning"]),
            "analysis": str(parsed["analysis"]),
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class LLMCarryTrader(LLMInvestor):
    """LLM-driven carry trader — borrows low-yield, invests high-yield. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.CarryTradeUnwind.LLM.prompts:LLM_CARRY_TRADER_SYS"


class LLMLeveragedCarryFund(LLMInvestor):
    """LLM-driven leveraged carry fund — forced rapid unwind on margin calls. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.CarryTradeUnwind.LLM.prompts:LLM_LEVERAGED_CARRY_FUND_SYS"
    )


class LLMFundingCurrencyBuyer(LLMInvestor):
    """LLM-driven funding currency buyer — safe-haven counter-cyclical flow. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.CarryTradeUnwind.LLM.prompts:LLM_FUNDING_CURRENCY_BUYER_SYS"
    )


class LLMHedgedCarryTrader(LLMInvestor):
    """LLM-driven hedged carry trader — volatility-adjusted carry positions. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.CarryTradeUnwind.LLM.prompts:LLM_HEDGED_CARRY_TRADER_SYS"
    )


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — random uninformed liquidity provider. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.CarryTradeUnwind.LLM.prompts:LLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMCarryTrader",
    "LLMLeveragedCarryFund",
    "LLMFundingCurrencyBuyer",
    "LLMHedgedCarryTrader",
    "LLMNoiseTrader",
]
