"""BlackMonday1987 LLM Simulation — LLM-driven agents with persona prompts."""

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
from examples.BlackMonday1987.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from a module path in the form 'module:VAR'."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """Base LLM-driven investor for BlackMonday1987."""

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
            folder=f"BlackMonday1987/LLM/{self.__class__.__name__}", entry_limit=200
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
        if "custom_state" in state["state"].__dict__:
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
            "examples.BlackMonday1987.LLM.prompts:LLM_USER_TEMPLATE"
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
                    max_buy = int(cash / price) if price > 0 else 0
                    quantity = min(quantity, max_buy)
                elif action_str == "sell":
                    quantity = min(quantity, max(position, 0))
                break
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("LLM attempt %d failed: %s", attempt + 1, exc)
                last_error = exc
                if attempt == 2:
                    raise RuntimeError(
                        f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
                    ) from last_error

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


class LLMPortfolioInsurer(LLMInvestor):
    """LLM-driven portfolio insurer — dynamic hedging seller. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.BlackMonday1987.LLM.prompts:LLM_PORTFOLIO_INSURER_SYS"
    )


class LLMIndexArbitrageur(LLMInvestor):
    """LLM-driven index arbitrageur — exploits futures/spot gaps. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.BlackMonday1987.LLM.prompts:LLM_INDEX_ARBITRAGEUR_SYS"
    )


class LLMProgramTrader(LLMInvestor):
    """LLM-driven program trader — automated feedback amplifier. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = "examples.BlackMonday1987.LLM.prompts:LLM_PROGRAM_TRADER_SYS"


class LLMValueInvestor(LLMInvestor):
    """LLM-driven value investor — buys at deep discount to fundamentals. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.BlackMonday1987.LLM.prompts:LLM_VALUE_INVESTOR_SYS"


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — random uninformed liquidity provider. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.BlackMonday1987.LLM.prompts:LLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMPortfolioInsurer",
    "LLMIndexArbitrageur",
    "LLMProgramTrader",
    "LLMValueInvestor",
    "LLMNoiseTrader",
]
