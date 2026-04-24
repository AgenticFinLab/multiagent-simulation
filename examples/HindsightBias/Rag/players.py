"""HindsightBias Rag Variant Players

RAG-augmented agents for the HindsightBias simulation using LangChainAPIInference.
"""

import logging

from lmbase.inference import LangChainAPIInference, InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.HindsightBias.Rag.prompts import (
    RAG_HINDSIGHTOVERCONFIDENT_PROMPT,
    RAG_OUTCOMELEARNER_PROMPT,
    RAG_PROCESSEVALUATOR_PROMPT,
    RAG_CONTRARIANSKEPTIC_PROMPT,
    RAG_NOISETRADER_PROMPT,
    RAG_USER_TEMPLATE,
)
from examples.HindsightBias.Rule.players import Market
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("HindsightBias.Rag")


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented HindsightBias investors."""

    _system_prompt = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _initialize_rag(self):
        """Initialize RAG retriever from config extras."""
        return self.config.extras.get("rag_context", "No additional context available.")

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        llm_cfg = self.config.extras.get("llm", {})
        llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg.get("generation_config", {}),
        )
        price = self.state.custom_state.get("price", 0)
        fundamental = self.state.custom_state.get("fundamental", 0)
        deviation = self.state.custom_state.get("deviation", 0)
        cash = self.state.custom_state.get("cash", 0)
        position = self.state.custom_state.get("position", 0)
        round_num = self.state.custom_state.get("round", 0)
        portfolio_value = cash + position * price
        rag_context = self._initialize_rag()
        user_msg = RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )
        infer_input = InferInput(system_msg=self._system_prompt, user_msg=user_msg)
        try:
            response = llm.run([infer_input]).outputs[0].response
            result = parse_llm_response_with_thinking(response)
            decision = result.get("decision", {})
        except Exception:
            decision = {"action": "hold", "quantity": 0}
        return decision

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = int(decision_payload.get("quantity", 0))
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state.get("cash", 0)
        position = self.state.custom_state.get("position", 0)
        if action == "buy" and quantity > 0 and price > 0:
            quantity = min(quantity, int(cash / price))
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(position, 0))
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        else:
            quantity = 0
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RagLLMHindsightOverconfident(RagLLMInvestor):
    """RAG HindsightOverconfident: excessive confidence from hindsight reasoning."""

    _system_prompt = RAG_HINDSIGHTOVERCONFIDENT_PROMPT


class RagLLMOutcomeLearner(RagLLMInvestor):
    """RAG OutcomeLearner: judges decisions by outcomes, not process."""

    _system_prompt = RAG_OUTCOMELEARNER_PROMPT


class RagLLMProcessEvaluator(RagLLMInvestor):
    """RAG ProcessEvaluator: evaluates decisions by process quality."""

    _system_prompt = RAG_PROCESSEVALUATOR_PROMPT


class RagLLMContrarianSkeptic(RagLLMInvestor):
    """RAG ContrarianSkeptic: distrusts post-hoc narratives."""

    _system_prompt = RAG_CONTRARIANSKEPTIC_PROMPT


class RagLLMNoiseTrader(RagLLMInvestor):
    """RAG NoiseTrader: random trader providing baseline liquidity."""

    _system_prompt = RAG_NOISETRADER_PROMPT


__all__ = [
    "Market",
    "RagLLMHindsightOverconfident",
    "RagLLMOutcomeLearner",
    "RagLLMProcessEvaluator",
    "RagLLMContrarianSkeptic",
    "RagLLMNoiseTrader",
]
