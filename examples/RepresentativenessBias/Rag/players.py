"""RepresentativenessBias Rag-Driven Simulation Players."""

import logging
from typing import Any, Dict, List, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from examples.llm_utils import parse_llm_response_with_thinking

from .prompts import (
    RAG_USER_TEMPLATE,
    RULELLM_BAYESIAN_UPDATER_SYS,
    RULELLM_CATEGORY_OVERGENERALIZER_SYS,
    RULELLM_CONTRARIAN_STATISTICAL_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_PATTERN_MATCHER_SYS,
)
from examples.RepresentativenessBias.Rule.players import Market

logger = logging.getLogger("RepresentativenessBias.Rag")


class RagLLMInvestor(GeneralPlayer):
    """Base Rag-augmented LLM investor for RepresentativenessBias simulation."""

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

    def _initialize_agent(self) -> None:
        """Initialize agent state on first perceive call."""
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self._initialize_rag()

    def _initialize_rag(self) -> None:
        """Initialize RAG retriever. Override in subclass if needed."""
        self.state.custom_state["rag_initialized"] = True

    def _retrieve_rag_context(
        self, price: float, fundamental: float, deviation: float
    ) -> str:
        """Retrieve relevant context for current market state."""
        rag_cfg = self.config.extras["rag"]
        context_template = rag_cfg["context_template"]
        return context_template

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            self._initialize_agent()
        for msg in observation.inbounds:
            payload = msg["payload"]
            if payload["type"] == "market_update":
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

        rag_context = self._retrieve_rag_context(price, fundamental, deviation)
        user_prompt = RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
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


class RagLLMPatternMatcher(RagLLMInvestor):
    """Rag-augmented PatternMatcher — pattern-based investor with retrieved knowledge."""

    _system_prompt = RULELLM_PATTERN_MATCHER_SYS


class RagLLMCategoryOvergeneralizer(RagLLMInvestor):
    """Rag-augmented CategoryOvergeneralizer — category-based investor with retrieved knowledge."""

    _system_prompt = RULELLM_CATEGORY_OVERGENERALIZER_SYS


class RagLLMBayesianUpdater(RagLLMInvestor):
    """Rag-augmented BayesianUpdater — Bayesian investor with retrieved knowledge."""

    _system_prompt = RULELLM_BAYESIAN_UPDATER_SYS


class RagLLMContrarianStatistical(RagLLMInvestor):
    """Rag-augmented ContrarianStatistical — contrarian investor with retrieved knowledge."""

    _system_prompt = RULELLM_CONTRARIAN_STATISTICAL_SYS


class RagLLMNoiseTrader(RagLLMInvestor):
    """Rag-augmented NoiseTrader — noise trader with retrieved knowledge."""

    _system_prompt = RULELLM_NOISE_TRADER_SYS


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMPatternMatcher",
    "RagLLMCategoryOvergeneralizer",
    "RagLLMBayesianUpdater",
    "RagLLMContrarianStatistical",
    "RagLLMNoiseTrader",
]
