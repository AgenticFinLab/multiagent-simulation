"""RepresentativenessBias RuleLLM-Driven Simulation Players."""

import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from examples.llm_utils import parse_llm_response_with_thinking

from .prompts import (
    RULELLM_BAYESIAN_UPDATER_SYS,
    RULELLM_CATEGORY_OVERGENERALIZER_SYS,
    RULELLM_CONTRARIAN_STATISTICAL_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_PATTERN_MATCHER_SYS,
    RULELLM_USER_TEMPLATE,
)
from examples.RepresentativenessBias.Rule.players import Market, _info_payload

logger = logging.getLogger("RepresentativenessBias.RuleLLM")


class RuleLLMInvestor(GeneralPlayer):
    """Base RuleLLM investor for RepresentativenessBias simulation."""

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
            if isinstance(payload, dict) and payload.get("type") == "market_update":
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

        user_prompt = RULELLM_USER_TEMPLATE.format(
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
        try:
            response = llm.run([infer_input]).outputs[0].response
            decision = parse_llm_response_with_thinking(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}

        action = decision["action"]
        quantity = int(decision["quantity"])
        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
        quantity = max(0, min(quantity, 1000))
        return {"action": action, "quantity": quantity}

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
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RuleLLMPatternMatcher(RuleLLMInvestor):
    """RuleLLM PatternMatcher — rule-guided pattern matching investor."""

    _system_prompt = RULELLM_PATTERN_MATCHER_SYS


class RuleLLMCategoryOvergeneralizer(RuleLLMInvestor):
    """RuleLLM CategoryOvergeneralizer — rule-guided category overgeneralizer."""

    _system_prompt = RULELLM_CATEGORY_OVERGENERALIZER_SYS


class RuleLLMBayesianUpdater(RuleLLMInvestor):
    """RuleLLM BayesianUpdater — rule-guided Bayesian rational investor."""

    _system_prompt = RULELLM_BAYESIAN_UPDATER_SYS


class RuleLLMContrarianStatistical(RuleLLMInvestor):
    """RuleLLM ContrarianStatistical — rule-guided contrarian arbitrageur."""

    _system_prompt = RULELLM_CONTRARIAN_STATISTICAL_SYS


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """RuleLLM NoiseTrader — rule-guided noise/liquidity trader."""

    _system_prompt = RULELLM_NOISE_TRADER_SYS


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMPatternMatcher",
    "RuleLLMCategoryOvergeneralizer",
    "RuleLLMBayesianUpdater",
    "RuleLLMContrarianStatistical",
    "RuleLLMNoiseTrader",
]
