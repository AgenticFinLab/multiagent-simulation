"""DotComBubble RuleLLM Simulation — LLM agents with explicit numerical trading rules."""

from __future__ import annotations

import copy
import importlib
import logging
import math
from typing import Any, Dict

from dotenv import load_dotenv

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.player.base import Action, Observation
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from masim.utils.llm_utils import (
    parse_llm_response_with_thinking,
    robust_llm_call,
)
from masim.format import get_order_format
from examples.DotComBubble.Rule.players import Market, _build_order  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate the required LLM decision fields without hidden fallbacks."""
    required = {"action", "bid_price", "quantity", "reasoning"}
    missing = required.difference(decision)
    if missing:
        raise KeyError(f"{identity} decision missing fields: {sorted(missing)}")
    action = str(decision["action"]).lower()
    if action not in {"buy", "sell", "hold"}:
        raise ValueError(f"{identity} emitted invalid action: {action}")
    bid_price = float(decision["bid_price"])
    quantity_value = float(decision["quantity"])
    if not math.isfinite(bid_price) or bid_price <= 0:
        raise ValueError(f"{identity} emitted invalid bid_price: {bid_price}")
    if not math.isfinite(quantity_value) or quantity_value < 0:
        raise ValueError(f"{identity} emitted invalid quantity: {quantity_value}")
    if not quantity_value.is_integer():
        raise ValueError(f"{identity} quantity must be a whole number: {quantity_value}")
    reasoning = str(decision["reasoning"]).strip()
    if not reasoning:
        raise ValueError(f"{identity} emitted empty reasoning")
    return {
        "action": action,
        "bid_price": bid_price,
        "quantity": int(quantity_value),
        "reasoning": reasoning,
    }


class RuleLLMInvestor(GeneralPlayer):
    """Base RuleLLM investor for DotComBubble."""

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
            folder=f"DotComBubble/RuleLLM/{self.__class__.__name__}", entry_limit=200
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
            player_state = copy.copy(self.state)
            player_state.custom_state = dict(self.state.custom_state)
            player_state.custom_state.pop("llm_client", None)
            state["state"] = player_state
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
        price_history = self.state.custom_state["price_history"]
        previous_price = price_history[-2] if len(price_history) >= 2 else price
        if previous_price <= 0:
            raise ValueError("Momentum context requires a positive previous price")
        price_change = (price - previous_price) / previous_price

        llm_cfg = self.config.extras["llm"]
        if llm_cfg["sys_message"] != self._system_prompt_path:
            raise ValueError(
                f"{self.identity} sys_message does not match its investor class"
            )
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])
        user_prompt = user_template.format(
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            previous_price=previous_price,
            price_change=price_change,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )

        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]

        def _validate_and_normalize(parsed: Dict[str, Any]) -> None:
            normalized = _validate_decision(parsed, self.identity)
            parsed.update(normalized)

        max_attempts = int(llm_cfg.get("max_attempts", 3))
        if max_attempts <= 0:
            raise ValueError(f"{self.identity} llm.max_attempts must be positive")

        used_fallback = False
        decision = robust_llm_call(
            llm_client,
            system_prompt,
            user_prompt,
            parse_fn=parse_llm_response_with_thinking,
            validate_fn=get_order_format("DotComBubble").validate_decision,
            max_retries=max_attempts,
            fallback="hold",
            identity=self.identity,
        )

        if decision.get("_fallback"):
            logger.warning(
                "[%s] R%d LLM unavailable; emitting noop hold.",
                self.identity,
                round_num,
            )
            used_fallback = True
            fallback_order = _build_order(
                self,
                "hold",
                0,
                float(price),
                "llm_fallback_noop",
            )
            fallback_order["llm_fallback"] = used_fallback
            return {
                **fallback_order,
                "outbound_messages": [
                    {"payload": fallback_order, "content_type": "order"}
                ],
            }

        action_str = decision["action"]
        quantity = decision["quantity"]
        if action_str == "buy":
            quantity = min(quantity, int(cash / price) if price > 0 else 0)
        elif action_str == "sell":
            quantity = min(quantity, max(position, 0))

        order = _build_order(
            self,
            action_str,
            quantity,
            float(decision["bid_price"]),
            str(decision["reasoning"]),
        )
        order["llm_fallback"] = used_fallback
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = int(decision_payload["quantity"])
        price = self.state.custom_state["market_data"]["price"]
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class RuleLLMNewEconomyEvangelist(RuleLLMInvestor):
    """RuleLLM-driven new economy evangelist — narrative rules embedded. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.DotComBubble.RuleLLM.prompts:RULELLM_NEW_ECONOMY_EVANGELIST_SYS"
    )


class RuleLLMIPOFlipper(RuleLLMInvestor):
    """RuleLLM-driven IPO flipper — flip threshold rules embedded. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.DotComBubble.RuleLLM.prompts:RULELLM_IPO_FLIPPER_SYS"
    )


class RuleLLMMomentumFollower(RuleLLMInvestor):
    """RuleLLM-driven momentum follower — momentum threshold rules embedded. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.DotComBubble.RuleLLM.prompts:RULELLM_MOMENTUM_FOLLOWER_SYS"
    )


class RuleLLMSkepticalValueInvestor(RuleLLMInvestor):
    """RuleLLM-driven skeptical value investor — value threshold rules embedded. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.DotComBubble.RuleLLM.prompts:RULELLM_SKEPTICAL_VALUE_INVESTOR_SYS"
    )


class RuleLLMShortSeller(RuleLLMInvestor):
    """RuleLLM-driven short seller — short/cover threshold rules embedded. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = (
        "examples.DotComBubble.RuleLLM.prompts:RULELLM_SHORT_SELLER_SYS"
    )


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMNewEconomyEvangelist",
    "RuleLLMIPOFlipper",
    "RuleLLMMomentumFollower",
    "RuleLLMSkepticalValueInvestor",
    "RuleLLMShortSeller",
]
