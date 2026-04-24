"""LossAversion Rag Simulation

Loss aversion from prospect theory causes investors to hold losers too long
and sell winners too early.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: RAG-augmented LLM with rule-embedded prompts and retrieved knowledge

All parameters are configured via players.yml config file.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.knowledge.manager import KnowledgeManager
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import parse_llm_response_with_thinking
from examples.LossAversion.RuleLLM.prompts import (
    RULELLM_LOSS_AVERSE_PROMPT,
    RULELLM_BREAK_EVEN_PROMPT,
    RULELLM_RATIONAL_PROMPT,
    RULELLM_MOMENTUM_PROMPT,
    RULELLM_MARKET_MAKER_PROMPT,
)
from examples.LossAversion.Rag.prompts import RAG_USER_TEMPLATE
from examples.LossAversion.Rule.players import Market  # noqa: F401

logger = logging.getLogger("LossAversion.Rag")


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented investors in LossAversion simulation.

    Combines rule-embedded system prompts with retrieved knowledge context.
    """

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            for key in ("llm_client", "rag_store"):
                custom.pop(key, None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "lm_name" in custom and "llm_client" not in custom:
                custom["llm_client"] = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        self.state.custom_state["round"] = observation.round

        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload if hasattr(inb, "payload") else inb
                if isinstance(payload, dict) and payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        """One-time initialization: portfolio state + LLM client + RAG index."""
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["entry_price"] = extras.get(
            "initial_price", extras.get("entry_price", 100.0)
        )

        llm_cfg = extras["llm"]
        lm_name = llm_cfg["lm_name"]
        generation_config = llm_cfg["generation_config"]

        self.state.custom_state["lm_name"] = lm_name
        self.state.custom_state["generation_config"] = generation_config

        llm_client = LangChainAPIInference(
            lm_name=lm_name,
            generation_config=generation_config,
        )
        self.state.custom_state["llm_client"] = llm_client

        await self._initialize_rag(extras, llm_client)

    async def _initialize_rag(self, extras: Dict[str, Any], llm_client: Any) -> None:
        """Build or load the agent RAG index."""
        record_path = extras["record_path"]
        knowledge_config = extras.get("knowledge", {})
        private_knowledge = extras.get("private_knowledge", {})
        rag_cfg = private_knowledge.get("rag", extras.get("rag", {}))

        resource_manager = ResourceManager(
            knowledge_config
            or {
                "backend": "local",
                "global_uri": rag_cfg.get("docs_dir", "examples/document-sources"),
                "rag": {
                    "output_position": rag_cfg.get("shared_rag_index_dir", "rag_index")
                },
            }
        )

        agent_knowledge = resource_manager.resolve_agent_knowledge(
            agent_id=self.identity,
            private_knowledge=private_knowledge
            or {
                "from_global_resources": [],
                "local_resources": {"local_uri": "", "local_resources": []},
                "rag": rag_cfg,
            },
            record_path=record_path,
        )

        local_rag_dir = agent_knowledge["local_rag_dir"]
        processed_dir = agent_knowledge["processed_dir"]
        shared_rag_dir = agent_knowledge["shared_rag_dir"]
        resolved_rag = agent_knowledge["rag"]

        os.makedirs(local_rag_dir, exist_ok=True)

        embed_type = resolved_rag.get("embed_type", "litellm")
        embed_model = resolved_rag.get("embed_model", "openai/hunyuan-embedding")
        embed_api_base = resolved_rag.get("embed_api_base", "")
        embed_api_key = resolved_rag.get("embed_api_key", "")
        if not embed_api_key:
            embed_api_key = os.getenv(
                "HUNYUAN_API_KEY" if embed_type == "litellm" else "ARK_API_KEY", ""
            )

        rag_store = KnowledgeStore(
            embed_model_name=embed_model,
            embed_api_key=embed_api_key,
            embed_api_base=embed_api_base,
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=int(resolved_rag.get("chunk_size", 512)),
            chunk_overlap=int(resolved_rag.get("chunk_overlap", 64)),
        )

        # Try loading existing index
        if os.path.isdir(local_rag_dir) and os.listdir(local_rag_dir):
            try:
                rag_store.load(local_rag_dir)
                self.state.custom_state["rag_store"] = rag_store
                self.state.custom_state["rag_cfg"] = resolved_rag
                return
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to load local index (%s)", self.identity, exc
                )

        # Build from processed documents
        loader = KnowledgeLoader()
        docs: List[Any] = []
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            logger.warning(
                "[%s] No processed documents in %s; RAG unavailable.",
                self.identity,
                processed_dir,
            )
            self.state.custom_state["rag_store"] = None
            self.state.custom_state["rag_cfg"] = resolved_rag
            return

        rag_store.build(docs)
        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state.get("price", 100.0)
        fundamental = self.state.custom_state.get("fundamental", 100.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]

        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        rag_store: KnowledgeStore = self.state.custom_state.get("rag_store")
        rag_cfg: Dict[str, Any] = self.state.custom_state.get("rag_cfg", {})

        # Retrieve RAG context
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg.get("top_k", 3)
            query = KnowledgeQuery(
                text=(
                    f"loss aversion trading strategy when: "
                    f"price={price:.2f}, fundamental={fundamental:.2f}, "
                    f"deviation={deviation*100:+.2f}%"
                ),
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text

        if not rag_context:
            rag_context = "(No relevant knowledge retrieved this round.)"

        user_msg = RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

        decision: Dict[str, Any] = {"action": "hold", "quantity": 0}
        for attempt in range(3):
            try:
                output = llm_client.run(
                    [InferInput(system_msg=self._system_prompt, user_msg=user_msg)]
                )
                decision = parse_llm_response_with_thinking(output.outputs[0].response)
                break
            except (ValueError, RuntimeError) as exc:
                logger.debug(
                    "[%s] LLM parse failed (attempt %d): %s",
                    self.identity,
                    attempt + 1,
                    exc,
                )

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))

        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
        else:
            quantity = 0

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
            self.state.custom_state["entry_price"] = price
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision.get("reasoning", "")[:120],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMLossAverseInvestor(RagLLMInvestor):
    """RAG-augmented: LossAverseInvestor rules + LLM + retrieved knowledge."""

    _system_prompt = RULELLM_LOSS_AVERSE_PROMPT


class LLMBreakEvenTrader(RagLLMInvestor):
    """RAG-augmented: BreakEvenTrader rules + LLM + retrieved knowledge."""

    _system_prompt = RULELLM_BREAK_EVEN_PROMPT


class LLMRationalTrader(RagLLMInvestor):
    """RAG-augmented: RationalTrader rules + LLM + retrieved knowledge."""

    _system_prompt = RULELLM_RATIONAL_PROMPT


class LLMMomentumTrader(RagLLMInvestor):
    """RAG-augmented: MomentumTrader rules + LLM + retrieved knowledge."""

    _system_prompt = RULELLM_MOMENTUM_PROMPT


class LLMMarketMaker(RagLLMInvestor):
    """RAG-augmented: MarketMaker rules + LLM + retrieved knowledge."""

    _system_prompt = RULELLM_MARKET_MAKER_PROMPT


__all__ = [
    "Market",
    "RagLLMInvestor",
    "LLMLossAverseInvestor",
    "LLMBreakEvenTrader",
    "LLMRationalTrader",
    "LLMMomentumTrader",
    "LLMMarketMaker",
]
