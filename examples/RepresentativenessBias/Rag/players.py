"""RepresentativenessBias Rag-Driven Simulation Players."""

import logging
import os
from typing import Any, Dict, List, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)

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
from examples.RepresentativenessBias.Rule.players import Market, _info_payload

logger = logging.getLogger("RepresentativenessBias.Rag")
RAG_FALLBACK_CONTEXT = "(No relevant knowledge retrieved this round.)"


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


class RagLLMInvestor(GeneralPlayer):
    """Base Rag-augmented LLM investor for RepresentativenessBias simulation."""

    _system_prompt: str = ""

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        state.pop("_llm", None)
        state.pop("_rag_store", None)
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        self._llm = None
        self._rag_store = None

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
        self._initialize_rag(extras)

    def _initialize_rag(self, extras: Dict[str, Any]) -> None:
        """Build or load the per-agent RAG index."""
        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        knowledge_config = {
            "backend": "local",
            "global_uri": "examples/document-sources",
            "preprocessing": {"output_position": "MinerU_processed"},
            "rag": {"output_position": "rag_index"},
        }
        resource_manager = ResourceManager(knowledge_config)
        agent_knowledge = resource_manager.resolve_agent_knowledge(
            agent_id=self.identity,
            private_knowledge=private_knowledge,
            record_path=extras["record_path"],
        )
        resolved_rag = agent_knowledge["rag"]
        local_rag_dir = agent_knowledge["local_rag_dir"]
        processed_dir = agent_knowledge["processed_dir"]

        embed_type = resolved_rag["embed_type"]
        embed_api_key = resolved_rag["embed_api_key"]
        if not embed_api_key:
            embed_api_key = os.getenv(
                "HUNYUAN_API_KEY" if embed_type == "litellm" else "ARK_API_KEY",
                "",
            )

        rag_store = KnowledgeStore(
            embed_model_name=resolved_rag["embed_model"],
            embed_api_key=embed_api_key,
            embed_api_base=resolved_rag["embed_api_base"],
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=int(resolved_rag["chunk_size"]),
            chunk_overlap=int(resolved_rag["chunk_overlap"]),
        )
        if os.path.isdir(local_rag_dir) and os.listdir(local_rag_dir):
            try:
                rag_store.load(local_rag_dir)
                self._rag_store = rag_store
                self.state.custom_state["rag_cfg"] = resolved_rag
                return
            except Exception as exc:
                logger.warning("[%s] Failed to load RAG index: %s", self.identity, exc)

        if not os.path.isdir(processed_dir) or not os.listdir(processed_dir):
            logger.warning("[%s] No processed RAG documents in %s", self.identity, processed_dir)
            self._rag_store = None
            self.state.custom_state["rag_cfg"] = resolved_rag
            return

        docs = KnowledgeLoader().load_from_dir(processed_dir)
        rag_store.build(docs)
        self._rag_store = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    def _retrieve_rag_context(
        self, price: float, fundamental: float, deviation: float
    ) -> str:
        """Retrieve relevant context for current market state."""
        rag_store = getattr(self, "_rag_store", None)
        if rag_store and rag_store.is_built():
            rag_cfg = self.state.custom_state["rag_cfg"]
            query = KnowledgeQuery(
                text=(
                    "representativeness heuristic base-rate neglect trading "
                    f"price={price:.2f} fundamental={fundamental:.2f} "
                    f"deviation={deviation:+.2%}"
                ),
                top_k=int(rag_cfg["top_k"]),
                round_num=self.state.custom_state["round"],
                agent_id=self.identity,
            )
            result = rag_store.query(query)
            if result.formatted_text:
                return result.formatted_text
        return RAG_FALLBACK_CONTEXT

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            self._initialize_agent()
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
                        "[%s] RAG LLM parse failed on attempt %d; retrying",
                        self.identity,
                        attempt + 1,
                    )
        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] RAG LLM parse failed after 3 attempts: {last_error}"
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
            "rag_context": rag_context,
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
            "rag_context": decision_payload["rag_context"],
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "rag_context": decision_payload["rag_context"],
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RagLLMPatternMatcher(RagLLMInvestor):
    """RagLLM pattern matcher — prototype trading with retrieved context. Theory: simulation-bases.md §4.1."""

    _system_prompt = RULELLM_PATTERN_MATCHER_SYS


class RagLLMCategoryOvergeneralizer(RagLLMInvestor):
    """RagLLM category generalizer — small-sample extrapolation with retrieval. Theory: simulation-bases.md §4.2."""

    _system_prompt = RULELLM_CATEGORY_OVERGENERALIZER_SYS


class RagLLMBayesianUpdater(RagLLMInvestor):
    """RagLLM Bayesian updater — base-rate benchmark with retrieval. Theory: simulation-bases.md §4.3."""

    _system_prompt = RULELLM_BAYESIAN_UPDATER_SYS


class RagLLMContrarianStatistical(RagLLMInvestor):
    """RagLLM contrarian arbitrageur — correction with retrieved context. Theory: simulation-bases.md §4.4."""

    _system_prompt = RULELLM_CONTRARIAN_STATISTICAL_SYS


class RagLLMNoiseTrader(RagLLMInvestor):
    """RagLLM noise trader — liquidity baseline with retrieval. Theory: simulation-bases.md §4.5."""

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
