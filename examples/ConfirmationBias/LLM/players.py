"""ConfirmationBias LLM Simulation — LLM-driven agents with persona prompts."""

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

from examples.llm_utils import parse_llm_response_with_thinking
from examples.ConfirmationBias.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base LLM-driven investor for ConfirmationBias."""

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
            folder=f"ConfirmationBias/LLM/{self.__class__.__name__}", entry_limit=200
        )
        load_dotenv()
        llm_cfg = extras["llm"]
        self.state.custom_state["llm_params"] = llm_cfg
        self.state.custom_state["llm_client"] = LangChainAPIInference(
            lm_name=llm_cfg["model"],
            generation_config={
                "temperature": llm_cfg["temperature"],
                "max_tokens": llm_cfg["max_tokens"],
            },
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
                lm_name=llm_cfg["model"],
                generation_config={
                    "temperature": llm_cfg["temperature"],
                    "max_tokens": llm_cfg["max_tokens"],
                },
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
            "examples.ConfirmationBias.LLM.prompts:LLM_USER_TEMPLATE"
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
        action_str, quantity = "hold", 0
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                result = llm_client.run([infer_input])
                response = result.outputs[0].response
                parsed = parse_llm_response_with_thinking(response)
                action_str = parsed["action"]
                quantity = int(parsed["quantity"])
                if action_str not in ("buy", "sell", "hold"):
                    action_str = "hold"
                quantity = max(0, quantity)
                if action_str == "buy":
                    quantity = min(quantity, int(cash / price) if price > 0 else 0)
                elif action_str == "sell":
                    quantity = min(quantity, max(position, 0))
                break
            except Exception as exc:
                logger.warning("LLM attempt %d failed: %s", attempt + 1, exc)
                if attempt == 2:
                    action_str, quantity = "hold", 0

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
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class LLMBeliefAnchor(LLMInvestor):
    """LLM-driven belief anchor — strong prior, selectively filters confirming signals. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.ConfirmationBias.LLM.prompts:LLM_BELIEF_ANCHOR_SYS"


class LLMSelectiveScanner(LLMInvestor):
    """LLM-driven selective scanner — seeks confirming information, ignores contradictions. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.ConfirmationBias.LLM.prompts:LLM_SELECTIVE_SCANNER_SYS"
    )


class LLMBalancedAnalyst(LLMInvestor):
    """LLM-driven balanced analyst — Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.ConfirmationBias.LLM.prompts:LLM_BALANCED_ANALYST_SYS"
    )


class LLMContrarianTrader(LLMInvestor):
    """LLM-driven contrarian — exploits systematic bias errors of biased traders. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.ConfirmationBias.LLM.prompts:LLM_CONTRARIAN_TRADER_SYS"
    )


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — random uninformed liquidity provider. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.ConfirmationBias.LLM.prompts:LLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMBeliefAnchor",
    "LLMSelectiveScanner",
    "LLMBalancedAnalyst",
    "LLMContrarianTrader",
    "LLMNoiseTrader",
]
