"""BlackMonday1987 RuleLLM Simulation — LLM agents with explicit numerical trading rules."""

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
from masim.format.order import validate_order
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from masim.utils.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from examples.BlackMonday1987.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate canonical trading decision fields before portfolio mutation."""
    action = decision["action"]
    if action not in {"buy", "sell", "hold"}:
        raise ValueError(f"[{identity}] invalid action: {action}")
    bid_price = float(decision["bid_price"])
    if bid_price <= 0:
        raise ValueError(f"[{identity}] invalid bid_price: {bid_price}")
    quantity = float(decision["quantity"])
    if quantity < 0:
        raise ValueError(f"[{identity}] invalid quantity: {quantity}")
    reasoning = str(decision["reasoning"]).strip()
    if not reasoning:
        raise ValueError(f"[{identity}] empty reasoning")
    analysis = str(decision["analysis"]).strip()
    if not analysis:
        raise ValueError(f"[{identity}] empty analysis")
    if action == "hold":
        quantity = 0.0
    return {
        **decision,
        "action": action,
        "bid_price": bid_price,
        "quantity": quantity,
        "reasoning": reasoning,
        "analysis": analysis,
    }


class RuleLLMInvestor(GeneralPlayer):
    """Base RuleLLM investor for BlackMonday1987."""

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
            folder=f"BlackMonday1987/RuleLLM/{self.__class__.__name__}", entry_limit=200
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
            "examples.BlackMonday1987.RuleLLM.prompts:RULELLM_USER_TEMPLATE"
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
        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            try:
                result = llm_client.run([infer_input]).outputs[0]
                response = result.response
                parsed = parse_llm_response_with_thinking(response)
                decision = _validate_decision(parsed, self.identity)
                break
            except Exception as exc:  # pylint: disable=broad-except
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < max_retries - 1 and (parse_error or retryable_api_error):
                    logger.debug(
                        "[%s] LLM call/parse failed, retrying: %s",
                        self.identity,
                        exc,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after {max_retries} retries: {last_error}"
            ) from last_error

        action_str = decision["action"]
        bid_price = decision["bid_price"]
        quantity = decision["quantity"]
        if action_str == "buy":
            max_buy = cash / bid_price
            quantity = min(quantity, max_buy)
        elif action_str == "sell":
            quantity = min(quantity, max(position, 0))

        if action_str == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action_str == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] -= quantity

        order = {
            "action": action_str,
            "bid_price": bid_price,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": self.__class__.__name__,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
        }
        validate_order(order)
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class RuleLLMPortfolioInsurer(RuleLLMInvestor):
    """RuleLLM-driven portfolio insurer — dynamic hedging seller. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.BlackMonday1987.RuleLLM.prompts:RULELLM_PORTFOLIO_INSURER_SYS"
    )


class RuleLLMIndexArbitrageur(RuleLLMInvestor):
    """RuleLLM-driven index arbitrageur — exploits futures/spot gaps. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.BlackMonday1987.RuleLLM.prompts:RULELLM_INDEX_ARBITRAGEUR_SYS"
    )


class RuleLLMProgramTrader(RuleLLMInvestor):
    """RuleLLM-driven program trader — automated feedback amplifier. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.BlackMonday1987.RuleLLM.prompts:RULELLM_PROGRAM_TRADER_SYS"
    )


class RuleLLMValueInvestor(RuleLLMInvestor):
    """RuleLLM-driven value investor — buys at deep discount to fundamentals. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.BlackMonday1987.RuleLLM.prompts:RULELLM_VALUE_INVESTOR_SYS"
    )


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """RuleLLM-driven noise trader — random uninformed liquidity provider. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = (
        "examples.BlackMonday1987.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS"
    )


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMPortfolioInsurer",
    "RuleLLMIndexArbitrageur",
    "RuleLLMProgramTrader",
    "RuleLLMValueInvestor",
    "RuleLLMNoiseTrader",
]
