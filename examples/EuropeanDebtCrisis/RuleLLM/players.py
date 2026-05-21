"""EuropeanDebtCrisis RuleLLM Simulation — LLM agents with explicit numerical trading rules."""

from __future__ import annotations

import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import parse_llm_response_with_thinking
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from examples.EuropeanDebtCrisis.Rule.players import Market, _build_order  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RuleLLMInvestor(GeneralPlayer):
    """Base RuleLLM investor for EuropeanDebtCrisis simulation."""

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

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = float(extras["initial_cash"])
        self.state.custom_state["position"] = int(extras["initial_position"])
        self.state.custom_state["market_data"] = {}
        self.state.custom_state["history_buffer"] = HistoryBuffer(
            folder=f"EuropeanDebtCrisis/RuleLLM/{self.__class__.__name__}",
            entry_limit=200,
        )
        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env")
        llm_cfg = extras["llm"]
        self.state.custom_state["llm_params"] = llm_cfg
        self.state.custom_state["llm_client"] = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )

    def __getstate__(self) -> Dict:
        state = self.__dict__.copy()
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = dict(self.state.custom_state)
            custom.pop("llm_client", None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state: Dict) -> None:
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "llm_params" in custom and "llm_client" not in custom:
                llm_cfg = custom["llm_params"]
                custom["llm_client"] = LangChainAPIInference(
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
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price
        system_prompt = load_prompt(self._system_prompt_path)
        user_template = load_prompt(
            "examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE"
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
        decision = None
        last_error = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                result = llm_client.run([infer_input])
                response = result.outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                if decision["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"Invalid action: {decision['action']}")
                if float(decision["bid_price"]) <= 0:
                    raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
                if not str(decision["reasoning"]).strip():
                    raise ValueError("Missing reasoning")
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

        action_str = decision["action"]
        quantity = max(0, int(decision["quantity"]))
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
        order = _build_order(
            self,
            action_str,
            quantity,
            float(decision["bid_price"]),
            str(decision["reasoning"]),
        )
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class RuleLLMPeripheryBondSeller(RuleLLMInvestor):
    """RuleLLM periphery bond seller — explicit spread threshold rules with LLM crisis narrative. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_PERIPHERY_BOND_SELLER_SYS"
    )


class RuleLLMCreditorPanicker(RuleLLMInvestor):
    """RuleLLM creditor panicker — explicit panic threshold rules with LLM contagion reasoning. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_CREDITOR_PANICKER_SYS"
    )


class RuleLLMCoreBondBuyer(RuleLLMInvestor):
    """RuleLLM core bond buyer — flight-to-quality rules with LLM safe-haven reasoning. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_CORE_BOND_BUYER_SYS"
    )


class RuleLLMECBIntervenor(RuleLLMInvestor):
    """RuleLLM ECB intervenor — backstop threshold rules with LLM policy reasoning. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_ECB_INTERVENOR_SYS"
    )


class RuleLLMHedgedFund(RuleLLMInvestor):
    """RuleLLM hedge fund — spread arbitrage rules with LLM relative-value reasoning. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = (
        "examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_HEDGED_FUND_SYS"
    )


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMPeripheryBondSeller",
    "RuleLLMCreditorPanicker",
    "RuleLLMCoreBondBuyer",
    "RuleLLMECBIntervenor",
    "RuleLLMHedgedFund",
]
