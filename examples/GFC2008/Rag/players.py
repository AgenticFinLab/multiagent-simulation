"""GFC2008 Rag Variant Players

RAG-augmented LLM-driven agents for the GFC2008 simulation.
"""

import logging
from typing import Any, Dict, Optional

from lmbase.inference import InferInput, LangChainAPIInference

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.GFC2008.Rule.players import Market
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("GFC2008.Rag")


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented LLM-driven GFC2008 investors."""

    _system_prompt_path: str = ""

    async def perceive(self, observation: Observation, prev_result: Optional[StepResult] = None) -> None:
        """Initialize portfolio and LLM client; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get("fundamental_value", 100.0)
            self.state.custom_state["deviation"] = 0.0
            await self._initialize_agent()

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get("price", self.state.custom_state["price"])
                self.state.custom_state["fundamental"] = payload.get("fundamental", self.state.custom_state["fundamental"])
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def _initialize_agent(self) -> None:
        """Initialize LangChainAPIInference client and RAG retriever from config."""
        llm_cfg = self.config.extras.get("llm", {})
        self._llm_params = {
            "lm_name": llm_cfg["lm_name"],
            "generation_config": llm_cfg["generation_config"],
        }
        self._llm_client = LangChainAPIInference(
            lm_name=self._llm_params["lm_name"],
            generation_config=self._llm_params["generation_config"],
        )
        self._rag_retriever = None
        rag_cfg = self.config.extras.get("rag", {})
        if rag_cfg:
            self._rag_retriever = self._build_rag_retriever(rag_cfg)

    def _build_rag_retriever(self, rag_cfg: dict):
        """Build RAG retriever from config."""
        return None

    def _retrieve_rag_context(self, query: str) -> str:
        """Retrieve relevant context from RAG system."""
        if self._rag_retriever is None:
            return "No RAG context available."
        try:
            results = self._rag_retriever.retrieve(query)
            return "\n".join(str(r) for r in results)
        except Exception:
            return "RAG retrieval unavailable."

    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        state.pop("_llm_client", None)
        state.pop("_rag_retriever", None)
        return state

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        self._rag_retriever = None
        if hasattr(self, "_llm_params"):
            self._llm_client = LangChainAPIInference(
                lm_name=self._llm_params["lm_name"],
                generation_config=self._llm_params["generation_config"],
            )

    async def decide(self) -> dict:
        """Retrieve RAG context, call LLM, parse decision."""
        from examples.GFC2008.Rag.prompts import RAG_USER_TEMPLATE
        from masim.utils.prompt_loader import load_prompt

        system_msg = load_prompt(self._system_prompt_path)
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        portfolio_value = cash + position * price

        rag_query = (
            f"GFC2008 financial crisis leverage MBS price {price:.2f} "
            f"fundamental {fundamental:.2f} deviation {deviation:+.2%}"
        )
        rag_context = self._retrieve_rag_context(rag_query)

        user_msg = RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
            round=self.state.custom_state["round"],
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )

        try:
            infer_input = InferInput(system_msg=system_msg, user_msg=user_msg)
            response = self._llm_client.run([infer_input]).outputs[0].response
            decision = parse_llm_response_with_thinking(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))
        price_val = self.state.custom_state["price"]

        if action == "buy":
            max_qty = int(cash / price_val) if price_val > 0 else 0
            quantity = min(quantity, max_qty, 3000)
        elif action == "sell":
            quantity = min(quantity, max(position, 0), 3000)
        else:
            quantity = 0

        quantity = max(0, quantity)
        return {"action": action, "quantity": quantity}

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
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
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class RagLLMMBSOriginator(RagLLMInvestor):
    """RAG-augmented MBSOriginator."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_MBS_ORIGINATOR_SYS"


class RagLLMRatingAgency(RagLLMInvestor):
    """RAG-augmented RatingAgency."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_RATING_AGENCY_SYS"


class RagLLMLeveragedInvestor(RagLLMInvestor):
    """RAG-augmented LeveragedInvestor."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_LEVERAGED_INVESTOR_SYS"


class RagLLMDistressedBuyer(RagLLMInvestor):
    """RAG-augmented DistressedBuyer."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_DISTRESSED_BUYER_SYS"


class RagLLMRegulator(RagLLMInvestor):
    """RAG-augmented Regulator."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_REGULATOR_SYS"


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMMBSOriginator",
    "RagLLMRatingAgency",
    "RagLLMLeveragedInvestor",
    "RagLLMDistressedBuyer",
    "RagLLMRegulator",
]
