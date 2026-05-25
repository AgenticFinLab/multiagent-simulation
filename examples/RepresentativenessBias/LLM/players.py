"""RepresentativenessBias LLM-Driven Simulation Players."""

import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from examples.llm_utils import parse_llm_response_with_thinking

from .prompts import (
    LLM_BAYESIAN_UPDATER_PROMPT,
    LLM_CATEGORY_OVERGENERALIZER_PROMPT,
    LLM_CONTRARIAN_STATISTICAL_PROMPT,
    LLM_NOISE_TRADER_PROMPT,
    LLM_PATTERN_MATCHER_PROMPT,
    LLM_USER_TEMPLATE,
)
from examples.RepresentativenessBias.Rule.players import Market, _info_payload

logger = logging.getLogger("RepresentativenessBias.LLM")


def _validate_decision(decision: Dict[str, Any]) -> None:
    """Validate canonical trading decision JSON."""
    if decision["action"] not in ("buy", "sell", "hold"):
        raise ValueError(f"Invalid action: {decision['action']}")
    if float(decision["bid_price"]) <= 0:
        raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
    if int(decision["quantity"]) < 0:
        raise ValueError(f"Invalid quantity: {decision['quantity']}")
    if not str(decision["reasoning"]).strip():
        raise ValueError("Missing reasoning")


class LLMInvestor(GeneralPlayer):
    """Base LLM-driven investor for RepresentativenessBias simulation."""

    _system_prompt: str = ""

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
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
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = _info_payload(msg)
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        portfolio_value = cash + position * price

        user_prompt = LLM_USER_TEMPLATE.format(
            round_num=self.state.custom_state["round"],
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )
        llm = self._get_llm()
        infer_input = InferInput(system_msg=self._system_prompt, user_msg=user_prompt)
        decision = None
        last_error = None
        for attempt in range(3):
            try:
                response = llm.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                _validate_decision(decision)
                break
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    logger.debug(
                        "[%s] LLM parse failed on attempt %d; retrying",
                        self.identity,
                        attempt + 1,
                    )
        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after 3 attempts: {last_error}"
            )

        action = decision["action"]
        quantity = int(decision["quantity"])
        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
        else:
            quantity = 0
        quantity = max(0, min(quantity, 1000))
        return {
            "action": action,
            "bid_price": float(decision["bid_price"]),
            "quantity": quantity,
            "reasoning": str(decision["reasoning"]),
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "bid_price": float(decision_payload["bid_price"]),
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision_payload["reasoning"],
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LLMPatternMatcher(LLMInvestor):
    """LLM-driven pattern matcher — prototype-based trading. Theory: simulation-bases.md §4.1."""

    _system_prompt = LLM_PATTERN_MATCHER_PROMPT


class LLMCategoryOvergeneralizer(LLMInvestor):
    """LLM-driven category generalizer — small-sample extrapolation. Theory: simulation-bases.md §4.2."""

    _system_prompt = LLM_CATEGORY_OVERGENERALIZER_PROMPT


class LLMBayesianUpdater(LLMInvestor):
    """LLM-driven Bayesian updater — base-rate disciplined benchmark. Theory: simulation-bases.md §4.3."""

    _system_prompt = LLM_BAYESIAN_UPDATER_PROMPT


class LLMContrarianStatistical(LLMInvestor):
    """LLM-driven contrarian arbitrageur — exploits biased mispricing. Theory: simulation-bases.md §4.4."""

    _system_prompt = LLM_CONTRARIAN_STATISTICAL_PROMPT


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — uninformed liquidity baseline. Theory: simulation-bases.md §4.5."""

    _system_prompt = LLM_NOISE_TRADER_PROMPT


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMPatternMatcher",
    "LLMCategoryOvergeneralizer",
    "LLMBayesianUpdater",
    "LLMContrarianStatistical",
    "LLMNoiseTrader",
]
