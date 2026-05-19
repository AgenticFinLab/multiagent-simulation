"""StatusQuoBias LLM Simulation

Status quo bias causes traders to prefer inaction and maintain current positions
despite new information.

Design:
    - Market: Rule-based coordinator (identical to StatusQuoBias.Rule.Market).
    - Investors: LLM-powered agents with unique personas defined in prompts.py.

All parameters configured via players.yml.
"""

import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from examples.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from .prompts import (
    LLM_INERTIAL_HOLDER_SYS,
    LLM_DEFAULT_FOLLOWER_SYS,
    LLM_ACTIVE_REBALANCER_SYS,
    LLM_MOMENTUM_TRADER_SYS,
    LLM_NOISE_TRADER_SYS,
)
from ..Rule.players import Market  # noqa: F401 — re-exported

logger = logging.getLogger("StatusQuoBias.LLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven StatusQuoBias investors."""

    _system_prompt: str = ""
    _llm: Optional[LangChainAPIInference] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        if self._llm is None:
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
                market_data = inb.payload
                self.state.custom_state["price"] = market_data["price"]
                self.state.custom_state["fundamental"] = market_data["fundamental"]
                self.state.custom_state["deviation"] = market_data["deviation"]

    def _build_prompt(self) -> str:
        """Build user prompt from current market state."""
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price
        return (
            f"Round {round_num} — Market Update\n"
            f"Current Price: ${price:.2f}  Fundamental: ${fundamental:.2f}  "
            f"Deviation: {deviation * 100:+.2f}%\n"
            f"Portfolio — Cash: ${cash:.2f}  Position: {position} shares  "
            f"Value: ${portfolio_value:.2f}\n\n"
            "Based on your strategy and current conditions, decide your action.\n"
            "Respond with <analysis>...</analysis> then <decision>...</decision> containing "
            'JSON: {"action": "buy" or "sell" or "hold", "quantity": integer, '
            '"reasoning": "brief rationale"}'
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        strategy_name = self.__class__.__name__
        llm_client = self._get_llm()

        user_prompt = self._build_prompt()
        system_prompt = self._system_prompt

        decision: Dict[str, Any] = {
            "action": "hold",
            "quantity": 0,
            "reasoning": "fallback hold before LLM response",
        }
        max_retries = 3
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            try:
                infer_output = llm_client.run([infer_input])
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < max_retries - 1 and (parse_error or retryable_api_error):
                    logger.debug("[%s] LLM call/parse failed, retrying: %s", self.identity, exc)
                    continue
                if not parse_error and not retryable_api_error:
                    raise
                logger.warning(
                    "[%s] LLM failed after %d attempts; holding: %s",
                    self.identity,
                    max_retries,
                    last_error,
                )
                decision = {
                    "action": "hold",
                    "quantity": 0,
                    "reasoning": f"fallback hold after retries: {last_error}",
                }

        action = decision["action"]
        quantity = int(decision["quantity"])

        valid_actions = ["buy", "sell", "hold"]
        if action not in valid_actions:
            action = "hold"
            quantity = 0
        quantity = max(0, min(quantity, 5000))

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy":
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif action == "sell":
            quantity = min(quantity, int(position))

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        logger.debug(
            "[%-25s] R%d (%s): action=%s qty=%d | Cash=%.2f Pos=%d",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
            "reasoning": str(decision.get("reasoning", "fallback hold"))[:120],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMInertialHolder(LLMInvestor):
    """LLM-driven inertial holder with strong status quo bias."""

    _system_prompt = LLM_INERTIAL_HOLDER_SYS


class LLMDefaultFollower(LLMInvestor):
    """LLM-driven default follower avoiding active portfolio decisions."""

    _system_prompt = LLM_DEFAULT_FOLLOWER_SYS


class LLMActiveRebalancer(LLMInvestor):
    """LLM-driven active rebalancer adjusting on new information."""

    _system_prompt = LLM_ACTIVE_REBALANCER_SYS


class LLMMomentumTrader(LLMInvestor):
    """LLM-driven momentum trader naturally overcoming status quo."""

    _system_prompt = LLM_MOMENTUM_TRADER_SYS


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader providing random baseline liquidity."""

    _system_prompt = LLM_NOISE_TRADER_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMInertialHolder",
    "LLMDefaultFollower",
    "LLMActiveRebalancer",
    "LLMMomentumTrader",
    "LLMNoiseTrader",
]
