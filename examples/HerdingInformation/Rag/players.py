"""HerdingInformation Rag Simulation

Information cascade occurs when individuals ignore private signals and follow the crowd.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: RAG-augmented LLM with personas from prompts.py
"""

import logging

from lmbase.inference import LangChainAPIInference, InferInput

from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.HerdingInformation.Rule.players import Market  # noqa: F401
from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("HerdingInformation.Rag")


class RagLLMInvestor(GeneralPlayer):
    """Base RAG-augmented LLM investor for HerdingInformation."""

    _system_prompt_path: str = ""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras.get("initial_position", 0)
        llm_cfg = extras.get("llm", {})
        self._llm_params = {
            "lm_name": llm_cfg["lm_name"],
            "generation_config": llm_cfg["generation_config"],
        }
        self._llm_client = LangChainAPIInference(
            lm_name=self._llm_params["lm_name"],
            generation_config=self._llm_params["generation_config"],
        )
        self._rag_retriever = self._initialize_rag()

    def _initialize_rag(self):
        """Initialize RAG retriever; returns None if unavailable."""
        try:
            from masim.utils.rag import RAGRetriever

            extras = self.config.extras
            rag_cfg = extras.get("rag", {})
            return RAGRetriever(
                knowledge_base=rag_cfg.get("knowledge_base", ""),
                top_k=rag_cfg.get("top_k", 3),
            )
        except Exception:
            return None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm_client", None)
        state.pop("_rag_retriever", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        params = self.__dict__.get("_llm_params", {})
        if params:
            self._llm_client = LangChainAPIInference(
                lm_name=params["lm_name"],
                generation_config=params["generation_config"],
            )
        self._rag_retriever = self._initialize_rag()

    async def decide(self):
        from examples.HerdingInformation.Rag.prompts import RAG_USER_TEMPLATE
        from masim.utils.prompt_loader import load_prompt

        price = self.state.custom_state.get("price", 0.0)
        fundamental = self.state.custom_state.get("fundamental", 0.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price

        rag_context = ""
        if self._rag_retriever is not None:
            try:
                query = f"information cascade herding price={price:.2f} deviation={deviation:+.2%}"
                rag_context = self._rag_retriever.retrieve(query)
            except Exception:
                rag_context = ""

        system_msg = load_prompt(self._system_prompt_path)
        user_msg = RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )
        infer_input = InferInput(system_msg=system_msg, user_msg=user_msg)
        response = self._llm_client.run([infer_input]).outputs[0].response
        raw = parse_llm_response_with_thinking(response)

        action = raw.get("action", "hold")
        quantity = int(raw.get("quantity", 0))
        quantity = max(0, min(quantity, 5000))

        if action == "buy" and price > 0:
            quantity = min(quantity, int(cash / price))
        elif action == "sell":
            quantity = min(quantity, max(position, 0))

        return {"action": action, "quantity": quantity}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RagLLMCascadeFollower(RagLLMInvestor):
    """RagLLM-driven information cascade follower."""

    _system_prompt_path = (
        "examples.HerdingInformation.Rag.prompts:RAGLLM_CASCADE_FOLLOWER_SYS"
    )


class RagLLMReputationHerder(RagLLMInvestor):
    """RagLLM-driven reputation-based herder."""

    _system_prompt_path = (
        "examples.HerdingInformation.Rag.prompts:RAGLLM_REPUTATION_HERDER_SYS"
    )


class RagLLMIndependentThinker(RagLLMInvestor):
    """RagLLM-driven rational independent thinker."""

    _system_prompt_path = (
        "examples.HerdingInformation.Rag.prompts:RAGLLM_INDEPENDENT_THINKER_SYS"
    )


class RagLLMContrarian(RagLLMInvestor):
    """RagLLM-driven contrarian investor."""

    _system_prompt_path = (
        "examples.HerdingInformation.Rag.prompts:RAGLLM_CONTRARIAN_SYS"
    )


class RagLLMNoiseTrader(RagLLMInvestor):
    """RagLLM-driven uninformed noise trader."""

    _system_prompt_path = (
        "examples.HerdingInformation.Rag.prompts:RAGLLM_NOISE_TRADER_SYS"
    )


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMCascadeFollower",
    "RagLLMReputationHerder",
    "RagLLMIndependentThinker",
    "RagLLMContrarian",
    "RagLLMNoiseTrader",
]
