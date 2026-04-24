"""HindsightBias LLM Variant Players

LLM-driven agents for the HindsightBias simulation using LangChainAPIInference.
"""

import logging

from lmbase.inference import LangChainAPIInference, InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.HindsightBias.LLM.prompts import (
    LLM_HINDSIGHTOVERCONFIDENT_PROMPT,
    LLM_OUTCOMELEARNER_PROMPT,
    LLM_PROCESSEVALUATOR_PROMPT,
    LLM_CONTRARIANSKEPTIC_PROMPT,
    LLM_NOISETRADER_PROMPT,
)
from examples.HindsightBias.Rule.players import Market
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("HindsightBias.LLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven HindsightBias investors."""

    _system_prompt = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

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
            lm_name=llm_cfg["model"],
            generation_config={"temperature": llm_cfg.get("temperature", 0.3)},
        )
        price = self.state.custom_state.get("price", 0)
        fundamental = self.state.custom_state.get("fundamental", 0)
        deviation = self.state.custom_state.get("deviation", 0)
        cash = self.state.custom_state.get("cash", 0)
        position = self.state.custom_state.get("position", 0)
        round_num = self.state.custom_state.get("round", 0)
        portfolio_value = cash + position * price
        user_msg = (
            f"Current Market State (Round {round_num}):\n"
            f"- Current Price: ${price:.2f}\n"
            f"- Fundamental Value: ${fundamental:.2f}\n"
            f"- Price Deviation: {deviation * 100:+.2f}%\n"
            f"- Your Cash: ${cash:.2f}\n"
            f"- Your Position: {position} shares\n"
            f"- Portfolio Value: ${portfolio_value:.2f}\n\n"
            "Based on your trading strategy and current market conditions, what action do you take?\n"
            "Provide your analysis and decision in the specified format."
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


class LLMHindsightOverconfident(LLMInvestor):
    """LLM-driven HindsightOverconfident: excessive confidence from hindsight reasoning."""

    _system_prompt = LLM_HINDSIGHTOVERCONFIDENT_PROMPT


class LLMOutcomeLearner(LLMInvestor):
    """LLM-driven OutcomeLearner: judges decisions by outcomes, not process."""

    _system_prompt = LLM_OUTCOMELEARNER_PROMPT


class LLMProcessEvaluator(LLMInvestor):
    """LLM-driven ProcessEvaluator: evaluates decisions by process quality."""

    _system_prompt = LLM_PROCESSEVALUATOR_PROMPT


class LLMContrarianSkeptic(LLMInvestor):
    """LLM-driven ContrarianSkeptic: distrusts post-hoc narratives, takes contrarian positions."""

    _system_prompt = LLM_CONTRARIANSKEPTIC_PROMPT


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven NoiseTrader: random trader providing baseline liquidity."""

    _system_prompt = LLM_NOISETRADER_PROMPT


__all__ = [
    "Market",
    "LLMHindsightOverconfident",
    "LLMOutcomeLearner",
    "LLMProcessEvaluator",
    "LLMContrarianSkeptic",
    "LLMNoiseTrader",
]
