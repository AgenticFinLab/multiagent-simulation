"""LTCMCollapse Rag Variant Players

RAG-augmented agents for the LTCMCollapse simulation using LangChainAPIInference.
"""

import logging

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.LTCMCollapse.Rag.prompts import (
    RAG_CONVERGENCEARBITRAGEUR_PROMPT,
    RAG_LEVERAGETRADER_PROMPT,
    RAG_RISKMANAGER_PROMPT,
    RAG_LIQUIDITYPROVIDER_PROMPT,
    RAG_CENTRALBANK_PROMPT,
    RAG_USER_TEMPLATE,
)
from examples.LTCMCollapse.Rule.players import Market
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("LTCMCollapse.Rag")


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented LTCMCollapse investors."""

    _system_prompt = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _initialize_rag(self):
        """Initialize RAG context from config extras."""
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


class RagLLMConvergenceArbitrageur(RagLLMInvestor):
    """RAG ConvergenceArbitrageur: leveraged spread convergence trader."""

    _system_prompt = RAG_CONVERGENCEARBITRAGEUR_PROMPT


class RagLLMLeverageTrader(RagLLMInvestor):
    """RAG LeverageTrader: forced deleveraging under margin pressure."""

    _system_prompt = RAG_LEVERAGETRADER_PROMPT


class RagLLMRiskManager(RagLLMInvestor):
    """RAG RiskManager: VaR-based position cutting."""

    _system_prompt = RAG_RISKMANAGER_PROMPT


class RagLLMLiquidityProvider(RagLLMInvestor):
    """RAG LiquidityProvider: market maker withdrawing under stress."""

    _system_prompt = RAG_LIQUIDITYPROVIDER_PROMPT


class RagLLMCentralBank(RagLLMInvestor):
    """RAG CentralBank: lender of last resort."""

    _system_prompt = RAG_CENTRALBANK_PROMPT


__all__ = [
    "Market",
    "RagLLMConvergenceArbitrageur",
    "RagLLMLeverageTrader",
    "RagLLMRiskManager",
    "RagLLMLiquidityProvider",
    "RagLLMCentralBank",
]
