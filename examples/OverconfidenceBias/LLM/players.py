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
from examples.llm_utils import parse_llm_response_with_thinking
from examples.OverconfidenceBias.Rule.players import Market  # noqa: F401

logger = logging.getLogger("OverconfidenceBias.LLM")


# =============================================================================
# LLMInvestor - Base
# =============================================================================


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven overconfidence investors."""

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
                lm_name=llm_cfg["model"],
                generation_config={"temperature": llm_cfg.get("temperature", 0.3)},
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
                if payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    def _build_prompt(self) -> str:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state.get("price", 0.0)
        fundamental = self.state.custom_state.get("fundamental", 0.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
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
        price = self.state.custom_state.get("price", 0.0)
        strategy_name = self.__class__.__name__
        llm = self._get_llm()

        user_prompt = self._build_prompt()

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(
                system_msg=self._system_prompt, user_msg=user_prompt
            )
            infer_output = llm.run([infer_input])
            try:
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            logger.warning(
                "[%s] LLM failed after %d attempts: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            order = {
                "type": "order",
                "action": "hold",
                "quantity": 0,
                "agent_type": strategy_name,
            }
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))

        # Enforce portfolio constraints
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy" and quantity > 0:
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
            if quantity > 0:
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, position)
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

        order = {
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
        }
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
    """LLM-driven OverconfidentTrader."""

    _system_prompt = LLM_OVERCONFIDENT_TRADER_PROMPT


class LLMSelfAttributor(LLMInvestor):
    """LLM-driven SelfAttributor."""

    _system_prompt = LLM_SELF_ATTRIBUTOR_PROMPT


class LLMCalibratedTrader(LLMInvestor):
    """LLM-driven CalibratedTrader."""

    _system_prompt = LLM_CALIBRATED_TRADER_PROMPT


class LLMContrarianInvestor(LLMInvestor):
    """LLM-driven ContrarianInvestor."""

    _system_prompt = LLM_CONTRARIAN_INVESTOR_PROMPT


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven NoiseTrader."""

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
