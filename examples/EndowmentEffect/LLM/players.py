"""EndowmentEffect LLM Simulation — LLM agents with investor personas."""

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

from examples.EndowmentEffect.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base LLM investor for EndowmentEffect simulation."""

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
            folder=f"EndowmentEffect/LLM/{self.__class__.__name__}", entry_limit=200
        )
        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env")
        llm_cfg = extras["llm"]
        self.state.custom_state["llm_params"] = llm_cfg
        self.state.custom_state["llm_client"] = LangChainAPIInference(
            lm_name=llm_cfg["model"],
            generation_config={
                "temperature": llm_cfg.get("temperature", 0.3),
                "max_tokens": llm_cfg.get("max_tokens", 512),
            },
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
                    lm_name=llm_cfg["model"],
                    generation_config={
                        "temperature": llm_cfg.get("temperature", 0.3),
                        "max_tokens": llm_cfg.get("max_tokens", 512),
                    },
                )

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        fundamental = market_data.get("fundamental", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state.get("round", 0)
        portfolio_value = cash + position * price
        system_prompt = load_prompt(self._system_prompt_path)
        user_template = load_prompt(
            "examples.EndowmentEffect.LLM.prompts:LLM_USER_TEMPLATE"
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
                action_str = parsed.get("action", "hold")
                quantity = int(parsed.get("quantity", 0))
                if action_str not in ("buy", "sell", "hold"):
                    action_str = "hold"
                quantity = max(0, quantity)
                if action_str == "buy":
                    quantity = min(quantity, int(cash / price) if price > 0 else 0)
                elif action_str == "sell":
                    quantity = min(quantity, max(position, 0))
                break
            except Exception as exc:  # pylint: disable=broad-except
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


class LLMEndowedHolder(LLMInvestor):
    """LLM attachment-driven endowed holder."""

    _system_prompt_path = "examples.EndowmentEffect.LLM.prompts:LLM_ENDOWED_HOLDER_SYS"


class LLMStatusQuoSeller(LLMInvestor):
    """LLM status-quo-biased seller."""

    _system_prompt_path = (
        "examples.EndowmentEffect.LLM.prompts:LLM_STATUS_QUO_SELLER_SYS"
    )


class LLMRationalArbitrageur(LLMInvestor):
    """LLM rational arbitrageur."""

    _system_prompt_path = (
        "examples.EndowmentEffect.LLM.prompts:LLM_RATIONAL_ARBITRAGEUR_SYS"
    )


class LLMNewBuyer(LLMInvestor):
    """LLM unbiased new buyer."""

    _system_prompt_path = "examples.EndowmentEffect.LLM.prompts:LLM_NEW_BUYER_SYS"


class LLMNoiseTrader(LLMInvestor):
    """LLM noise trader."""

    _system_prompt_path = "examples.EndowmentEffect.LLM.prompts:LLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMEndowedHolder",
    "LLMStatusQuoSeller",
    "LLMRationalArbitrageur",
    "LLMNewBuyer",
    "LLMNoiseTrader",
]
