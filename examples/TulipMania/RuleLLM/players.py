"""TulipMania RuleLLM Simulation

Hybrid Rule+LLM variant of TulipMania.

Design:
    - Market: Rule-based coordinator (identical to TulipMania.Rule.Market).
    - Investors: LLM-powered with system prompts encoding BOTH persona AND rules.

All parameters configured via players.yml.
"""

import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.llm_utils import is_retryable_llm_error, parse_llm_quantity_response_with_thinking

from .prompts import (
    RULELLM_EARLY_EXIT_TRADER_SYS,
    RULELLM_INTRINSIC_VALUE_TRADER_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_SOCIAL_PROOF_FOLLOWER_SYS,
    RULELLM_TREND_CHASER_SYS,
)
from ..Rule.players import Market  # noqa: F401 — re-exported

logger = logging.getLogger("TulipMania.RuleLLM")


class RuleLLMInvestor(GeneralPlayer):
    """Base class for hybrid Rule+LLM TulipMania investors."""

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
            "Apply your decision rules to the data above, then output your decision.\n"
            "Respond with <analysis>...</analysis> then <decision>...</decision> containing "
            'JSON: {"action": "buy" or "sell" or "hold", "quantity": integer, '
            '"reasoning": "brief rationale"}. Do not include any price field.'
        )

    def _parse_decision(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the TulipMania quantity-order contract."""
        decision = parse_llm_quantity_response_with_thinking(response_text)
        missing = [
            field
            for field in ("action", "quantity", "reasoning")
            if field not in decision or decision[field] is None
        ]
        if missing:
            raise ValueError(f"missing decision fields: {', '.join(missing)}")
        action = str(decision["action"]).lower()
        if action not in {"buy", "sell", "hold"}:
            raise ValueError(f"invalid action: {decision['action']!r}")
        try:
            quantity = int(float(decision["quantity"]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid quantity: {decision['quantity']!r}") from exc
        if quantity < 0:
            raise ValueError(f"negative quantity: {quantity}")
        reasoning = str(decision.pop("reasoning")).strip()
        if not reasoning:
            raise ValueError("empty reasoning")
        return {
            "action": action,
            "quantity": quantity,
            "reasoning": reasoning,
            "analysis": str(decision["analysis"]) if "analysis" in decision else "",
        }

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        strategy_name = self.__class__.__name__
        llm_client = self._get_llm()

        user_prompt = self._build_prompt()
        system_prompt = self._system_prompt

        decision: Optional[Dict[str, Any]] = None
        max_retries = 3
        last_error: BaseException | None = None
        parser_fallback = False
        fallback_reason = ""
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            try:
                infer_output = llm_client.run([infer_input])
                decision = self._parse_decision(infer_output.outputs[0].response)
                break
            except Exception as exc:  # pylint: disable=broad-except
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if not parse_error and not retryable_api_error:
                    raise
                if attempt == max_retries - 1:
                    logger.warning(
                        "[%s] LLM failed after %d attempts: %s. Holding.",
                        self.identity,
                        max_retries,
                        exc,
                    )
                    decision = {
                        "action": "hold",
                        "quantity": 0,
                        "reasoning": f"LLM fallback hold after retries: {last_error}",
                        "analysis": "",
                    }
                    parser_fallback = parse_error
                    fallback_reason = "parse" if parse_error else "retryable_api"

        if decision is None:
            raise RuntimeError(f"[{self.identity}] LLM decision unavailable")
        action = decision["action"]
        quantity = int(decision["quantity"])
        reasoning = str(decision.pop("reasoning"))[:120]
        analysis = str(decision.pop("analysis"))

        valid_actions = ["buy", "sell", "hold"]
        if action not in valid_actions:
            action = "hold"
            quantity = 0
        quantity = max(0, min(quantity, 5000))

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "hold":
            quantity = 0
        elif action == "buy":
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif action == "sell":
            quantity = min(quantity, int(position))
        if quantity <= 0:
            action = "hold"
            quantity = 0

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
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
            "reasoning": reasoning,
            "analysis": analysis,
            "parser_fallback": parser_fallback,
            "fallback_reason": fallback_reason,
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


class RuleLLMTrendChaser(RuleLLMInvestor):
    """Rule+LLM trend chaser buying assets purely because prices are rising.

    Theory: simulation-bases.md §4.1
    """

    _system_prompt = RULELLM_TREND_CHASER_SYS


class RuleLLMSocialProofFollower(RuleLLMInvestor):
    """Rule+LLM social proof follower joining speculative positions due to crowd behavior.

    Theory: simulation-bases.md §4.2
    """

    _system_prompt = RULELLM_SOCIAL_PROOF_FOLLOWER_SYS


class RuleLLMIntrinsicValueTrader(RuleLLMInvestor):
    """Rule+LLM intrinsic value trader selling when price far exceeds use value.

    Theory: simulation-bases.md §4.3
    """

    _system_prompt = RULELLM_INTRINSIC_VALUE_TRADER_SYS


class RuleLLMEarlyExitTrader(RuleLLMInvestor):
    """Rule+LLM early exit trader recognizing speculative excess and exiting early.

    Theory: simulation-bases.md §4.4
    """

    _system_prompt = RULELLM_EARLY_EXIT_TRADER_SYS


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """Rule+LLM noise trader providing random baseline liquidity.

    Theory: simulation-bases.md §4.5
    """

    _system_prompt = RULELLM_NOISE_TRADER_SYS


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMTrendChaser",
    "RuleLLMSocialProofFollower",
    "RuleLLMIntrinsicValueTrader",
    "RuleLLMEarlyExitTrader",
    "RuleLLMNoiseTrader",
]
