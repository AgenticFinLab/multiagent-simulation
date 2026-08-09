"""CreditCycle LLM Simulation — LLM-driven agents with persona prompts."""

from __future__ import annotations

import importlib
import logging
from typing import Dict

from dotenv import load_dotenv


from lmbase.inference.api_call import LangChainAPIInference
from masim.player.base import Action, Observation
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from examples.CreditCycle.llm_decision import (
    decide_with_llm_contract,
    infer_max_order_size,
    record_fallback,
)
from examples.CreditCycle.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base LLM-driven investor for CreditCycle."""

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
        self.state.custom_state["max_order_size"] = infer_max_order_size(extras)
        self.state.custom_state["llm_fallback_counts"] = {}
        self.state.custom_state["history_buffer"] = HistoryBuffer(
            folder=f"CreditCycle/LLM/{self.__class__.__name__}", entry_limit=200
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
        max_order_size = self.state.custom_state["max_order_size"]

        system_prompt = load_prompt(self._system_prompt_path)
        user_template = load_prompt(
            "examples.CreditCycle.LLM.prompts:LLM_USER_TEMPLATE"
        )
        user_prompt = user_template.format(
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
            max_order_size=max_order_size,
        )

        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        decision = decide_with_llm_contract(
            llm_client=llm_client,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            cash=cash,
            position=position,
            price=price,
            max_order_size=max_order_size,
            identity=self.identity,
        )
        if decision["fallback"]:
            record_fallback(self.state.custom_state, decision["fallback_type"])

        action_str = decision["action"]
        quantity = decision["quantity"]

        if action_str == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action_str == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {"action": action_str, "quantity": quantity}
        return {
            "action": action_str,
            "quantity": quantity,
            "bid_price": decision["bid_price"],
            "reasoning": decision["reasoning"],
            "fallback": decision["fallback"],
            "fallback_type": decision["fallback_type"],
            "llm_attempts": decision["llm_attempts"],
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class LLMProCyclicalLender(LLMInvestor):
    """LLM-driven pro-cyclical lender — expands credit in booms, tightens in busts. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.CreditCycle.LLM.prompts:LLM_PRO_CYCLICAL_LENDER_SYS"


class LLMMinskyBorrower(LLMInvestor):
    """LLM-driven Minsky borrower — accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = "examples.CreditCycle.LLM.prompts:LLM_MINSKY_BORROWER_SYS"


class LLMCounterCyclicalLender(LLMInvestor):
    """LLM-driven counter-cyclical lender — reserves in booms, liquidity injection in busts. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.CreditCycle.LLM.prompts:LLM_COUNTER_CYCLICAL_LENDER_SYS"
    )


class LLMValueInvestor(LLMInvestor):
    """LLM-driven value investor — fundamental-anchored credit buyer at deep discount. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.CreditCycle.LLM.prompts:LLM_VALUE_INVESTOR_SYS"


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — random uninformed liquidity provider. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.CreditCycle.LLM.prompts:LLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMProCyclicalLender",
    "LLMMinskyBorrower",
    "LLMCounterCyclicalLender",
    "LLMValueInvestor",
    "LLMNoiseTrader",
]
