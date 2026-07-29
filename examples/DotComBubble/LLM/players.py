"""Persona-driven investors for the DotComBubble LLM variant.

The model chooses an action, while this module enforces the executable market
contract: finite values, positive prices, cash/inventory limits, and configured
order-size limits.  See ``simulation-bases.md §4.1–§4.5``.
"""

from __future__ import annotations

import copy
import logging
import os
from typing import Dict

from dotenv import load_dotenv

from examples.DotComBubble.Rule.players import Market, _build_order  # noqa: F401
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

logger = logging.getLogger(__name__)


# Re-export the canonical prompt loader from masim.agents._base — this
# gives shipped scenarios the same import_module -> file-based fallback
# that Customized bundles depend on (hyphenated bundle dir names are
# illegal in Python import syntax and require file loading).
from masim.agents._base import load_prompt  # noqa: F401


class LLMInvestor(GeneralPlayer):
    """Base investor that delegates deliberation to a language model."""

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
        base_path = os.path.join(extras["record_path"], self.config.identity)
        self.state.custom_state["history_buffer"] = HistoryBuffer(
            folder=os.path.join(base_path, "llm_history"),
            entry_limit=int(extras["custom_state_hot_limit"]),
        )
        load_dotenv()
        llm_cfg = extras["llm"]
        if llm_cfg["lm_type"] != "api":
            raise ValueError("DotComBubble LLM requires llm.lm_type: api")
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
        history = self.state.custom_state["price_history"]
        previous_price = history[-2] if len(history) >= 2 else price
        momentum = (
            (price - previous_price) / previous_price
            if previous_price > 0
            else 0.0
        )

        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])
        user_prompt = user_template.format(
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
            previous_price=previous_price,
            momentum=momentum,
            max_order_quantity=int(self.config.extras["order_size"]),
        )

        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]

        decision = robust_llm_call(
            llm_client,
            system_prompt,
            user_prompt,
            parse_fn=parse_llm_response_with_thinking,
            validate_fn=get_order_format("DotComBubble").validate_decision,
            max_retries=int(llm_cfg["max_retries"]),
            fallback="hold",
            identity=self.identity,
        )

        if decision.get("_fallback"):
            logger.warning(
                "[%s] R%d LLM unavailable; emitting noop hold.",
                self.identity,
                round_num,
            )
            fallback_order = _build_order(
                self,
                "hold",
                0,
                float(price),
                "llm_fallback_noop",
            )
            return {
                **fallback_order,
                "outbound_messages": [
                    {"payload": fallback_order, "content_type": "order"}
                ],
            }

        action_str = decision["action"]
        quantity = min(
            int(float(decision["quantity"])),
            int(self.config.extras["order_size"]),
        )
        if action_str == "buy":
            quantity = min(quantity, int(cash / price) if price > 0 else 0)
        elif action_str == "sell":
            quantity = min(quantity, max(position, 0))
        else:
            quantity = 0

        if quantity == 0:
            action_str = "hold"

        order = _build_order(
            self,
            action_str,
            quantity,
            price,
            str(decision["reasoning"]),
        )
        order["analysis"] = decision["analysis"]
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = int(decision_payload["quantity"])
        execution_price = float(self.state.custom_state["market_data"]["price"])
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * execution_price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * execution_price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class LLMNewEconomyEvangelist(LLMInvestor):
    """Narrative growth investor. Theory: ``simulation-bases.md §4.1``."""

    pass


class LLMIPOFlipper(LLMInvestor):
    """Short-horizon new-issue trader. Theory: ``simulation-bases.md §4.2``."""

    pass


class LLMMomentumFollower(LLMInvestor):
    """Trend-following investor. Theory: ``simulation-bases.md §4.3``."""

    pass


class LLMSkepticalValueInvestor(LLMInvestor):
    """Fundamental-value investor. Theory: ``simulation-bases.md §4.4``."""

    pass


class LLMShortSeller(LLMInvestor):
    """Inventory-constrained skeptic. Theory: ``simulation-bases.md §4.5``."""

    pass


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMNewEconomyEvangelist",
    "LLMIPOFlipper",
    "LLMMomentumFollower",
    "LLMSkepticalValueInvestor",
    "LLMShortSeller",
]
