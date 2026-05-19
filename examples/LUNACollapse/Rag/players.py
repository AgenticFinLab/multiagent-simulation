"""LUNACollapse Rag Variant Players

RAG-augmented agents for the LUNACollapse simulation using LangChainAPIInference.
"""

import logging

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.LUNACollapse.Rag.prompts import (
    RAG_STABLECOINHOLDER_PROMPT,
    RAG_ARBITRAGEUR_PROMPT,
    RAG_DEFILENDER_PROMPT,
    RAG_ANCHORDEPOSITOR_PROMPT,
    RAG_VALUEBUYER_PROMPT,
    RAG_USER_TEMPLATE,
)
from examples.LUNACollapse.Rule.players import Market
from examples.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking

logger = logging.getLogger("LUNACollapse.Rag")


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented LUNACollapse investors."""

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
        extras = self.config.extras
        if extras.get("rag_context"):
            return extras["rag_context"]
        rag_cfg = extras.get("rag") or extras.get("private_knowledge", {}).get("rag", {})
        if rag_cfg.get("context_template"):
            return rag_cfg["context_template"]
        return "(No scenario-specific RAG context template configured.)"

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        llm_cfg = self.config.extras["llm"]
        llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
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
        decision = None
        last_error = None
        for attempt in range(3):
            try:
                infer_input = InferInput(
                    system_msg=self._system_prompt, user_msg=user_msg
                )
                response = llm.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < 2 and (parse_error or retryable_api_error):
                    logger.debug(
                        "[%s] LLM call/parse failed (attempt %d), retrying: %s",
                        self.identity,
                        attempt + 1,
                        exc,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            logger.warning(
                "[%s] LLM failed after 3 retries: %s. Holding.",
                self.identity,
                last_error,
            )
            decision = {
                "action": "hold",
                "bid_price": self.state.custom_state["price"],
                "quantity": 0,
                "reasoning": f"LLM fallback hold after retries: {last_error}",
            }

        return decision

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = int(decision_payload["quantity"])
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
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


class RagLLMStablecoinHolder(RagLLMInvestor):
    """RAG StablecoinHolder: redeems stablecoin on peg break."""

    _system_prompt = RAG_STABLECOINHOLDER_PROMPT


class RagLLMArbitrageur(RagLLMInvestor):
    """RAG Arbitrageur: amplifies death spiral through arbitrage."""

    _system_prompt = RAG_ARBITRAGEUR_PROMPT


class RagLLMDeFiLender(RagLLMInvestor):
    """RAG DeFiLender: automated liquidation cascades."""

    _system_prompt = RAG_DEFILENDER_PROMPT


class RagLLMAnchorDepositor(RagLLMInvestor):
    """RAG AnchorDepositor: exits yield protocol on stress signals."""

    _system_prompt = RAG_ANCHORDEPOSITOR_PROMPT


class RagLLMValueBuyer(RagLLMInvestor):
    """RAG ValueBuyer: contrarian deep-discount buyer."""

    _system_prompt = RAG_VALUEBUYER_PROMPT


__all__ = [
    "Market",
    "RagLLMStablecoinHolder",
    "RagLLMArbitrageur",
    "RagLLMDeFiLender",
    "RagLLMAnchorDepositor",
    "RagLLMValueBuyer",
]
