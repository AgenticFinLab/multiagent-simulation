"""OverconfidenceBias LLM Players - LLM-driven overconfidence simulation.

Design:
    - Market: Rule-based (same as Rule variant)
    - Investors: LLM-driven with behavioral personas

Market Parameters (from config.extras):
    - record_path, initial_price, fundamental_value
    - price_impact, mean_reversion, noise_std
    - custom_state_hot_limit

Investor Parameters (from config.extras):
    - initial_cash, initial_position, custom_state_hot_limit, record_path
    - llm: model, temperature (optional)
"""

import logging
import os
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from .prompts import (
    LLM_OVERCONFIDENT_TRADER_PROMPT,
    LLM_SELF_ATTRIBUTOR_PROMPT,
    LLM_CALIBRATED_TRADER_PROMPT,
    LLM_CONTRARIAN_INVESTOR_PROMPT,
    LLM_NOISE_TRADER_PROMPT,
    LLM_USER_TEMPLATE,
)
from masim.utils.llm_utils import (
    is_retryable_llm_error,
    parse_llm_response_with_thinking,
    robust_llm_call,
)
from masim.format import get_order_format
from examples.OverconfidenceBias.Rule.players import (  # noqa: F401
    Market,
    _build_order,
    _require_positive,
    _to_nonnegative_int,
    configured_order_limit,
    safe_max_affordable,
)

logger = logging.getLogger("OverconfidenceBias.LLM")


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate the shared overconfidence LLM decision contract."""
    action = decision["action"]
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"[{identity}] invalid action: {action}")
    bid_price = float(decision["bid_price"])
    _require_positive(bid_price, "bid_price")
    quantity = _to_nonnegative_int(decision["quantity"], f"[{identity}] quantity")
    return {
        "action": action,
        "bid_price": bid_price,
        "quantity": quantity,
        "reasoning": decision["reasoning"],
        "analysis": decision["analysis"],
    }


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven overconfidence investors.

    Theoretical basis: simulation-bases.md §4.
    Strategy specification: persona prompts map to simulation-bases.md §4.
    Parameters: simulation-bases.md §6.
    """

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        if not getattr(self, "_llm", None):
            llm_cfg = self.config.extras["llm"]
            self._llm = LangChainAPIInference(
                lm_name=llm_cfg["lm_name"],
                generation_config=llm_cfg["generation_config"],
            )
        return self._llm

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload["type"] == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    def _build_prompt(self) -> str:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        return LLM_USER_TEMPLATE.format(
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        _require_positive(price, "price")
        strategy_name = self.__class__.__name__
        llm = self._get_llm()

        user_prompt = self._build_prompt()

        decision = robust_llm_call(
            llm,
            self._system_prompt,
            user_prompt,
            parse_fn=parse_llm_response_with_thinking,
            validate_fn=get_order_format("OverconfidenceBias").validate_decision,
            max_retries=5,
            fallback="hold",
            identity=self.identity,
        )

        if decision.get("_fallback"):
            logger.warning(
                "[%s] R%d LLM unavailable; emitting noop hold.",
                self.identity,
                round_num,
            )
            order = _build_order(
                self, "hold", 0, float(price), "llm_fallback_noop"
            )
            order["analysis"] = ""
            order["strategy"] = strategy_name
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        action = decision["action"]
        quantity = _to_nonnegative_int(decision["quantity"], f"[{self.identity}] quantity")
        bid_price = float(decision["bid_price"])
        _require_positive(bid_price, "bid_price")

        # Enforce portfolio constraints
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        order_limit = configured_order_limit(self.config.extras)
        if order_limit > 0:
            quantity = min(quantity, order_limit)
        if action == "buy" and quantity > 0:
            max_affordable = safe_max_affordable(cash, price)
            quantity = min(quantity, max_affordable)
            if quantity > 0:
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(int(position), 0))
            if quantity > 0:
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity
        else:
            quantity = 0
            action = "hold"

        logger.debug(
            "[%-20s] R%d (%-20s): %s Q=%d",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
        )

        order = _build_order(
            self,
            action,
            quantity,
            bid_price,
            str(decision["reasoning"]),
        )
        order["analysis"] = str(decision["analysis"])
        order["strategy"] = strategy_name
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Concrete LLM Investor Types
# =============================================================================


class LLMOverconfidentTrader(LLMInvestor):
    """LLM-driven OverconfidentTrader.

    Theoretical basis: simulation-bases.md §4.1 — OverconfidentTrader.
    Strategy specification: simulation-bases.md §4.1.4.
    """

    _system_prompt = LLM_OVERCONFIDENT_TRADER_PROMPT


class LLMSelfAttributor(LLMInvestor):
    """LLM-driven SelfAttributor.

    Theoretical basis: simulation-bases.md §4.2 — SelfAttributor.
    Strategy specification: simulation-bases.md §4.2.4.
    """

    _system_prompt = LLM_SELF_ATTRIBUTOR_PROMPT


class LLMCalibratedTrader(LLMInvestor):
    """LLM-driven CalibratedTrader.

    Theoretical basis: simulation-bases.md §4.3 — CalibratedTrader.
    Strategy specification: simulation-bases.md §4.3.4.
    """

    _system_prompt = LLM_CALIBRATED_TRADER_PROMPT


class LLMContrarianInvestor(LLMInvestor):
    """LLM-driven ContrarianInvestor.

    Theoretical basis: simulation-bases.md §4.4 — ContrarianInvestor.
    Strategy specification: simulation-bases.md §4.4.4.
    """

    _system_prompt = LLM_CONTRARIAN_INVESTOR_PROMPT


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven NoiseTrader.

    Theoretical basis: simulation-bases.md §4.5 — NoiseTrader.
    Strategy specification: simulation-bases.md §4.5.4.
    """

    _system_prompt = LLM_NOISE_TRADER_PROMPT


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMOverconfidentTrader",
    "LLMSelfAttributor",
    "LLMCalibratedTrader",
    "LLMContrarianInvestor",
    "LLMNoiseTrader",
]
