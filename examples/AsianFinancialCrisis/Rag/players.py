"""AsianFinancialCrisis Rag — RAG-augmented Rule+LLM Asian Financial Crisis Simulation

Design:
    - Market coordinator: identical rule-based currency/equity dynamics as AsianFinancialCrisis.
    - Investors: LLM-powered with two layers of augmentation:
        1. System prompt embeds explicit quantitative rules (from RuleLLM variant)
           alongside a rich persona/profile description.
        2. At initialization, each agent builds a personal RAG library by
           indexing reference documents with LlamaIndex + embedding API.
        3. At every decision round, the agent retrieves the top-k most
           relevant text chunks from its RAG library and injects them into
           the user prompt via the {rag_context} placeholder.

This extends the three-variant comparison:
    AsianFinancialCrisis        — pure rule-based
    AsianFinancialCrisisRuleLLM — LLM with rules in prompt (no external knowledge)
    AsianFinancialCrisisRag     — LLM with rules in prompt + RAG knowledge retrieval

All parameters are configured via players.yml config file.

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

from __future__ import annotations

import importlib
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import validate_order

from examples.AsianFinancialCrisis.Rule.players import Market

logger = logging.getLogger("AsianFinancialCrisis.Rag")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from a module path (module:VARIABLE)."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate the shared AsianFinancialCrisis RAG decision contract."""
    action = decision["action"]
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"[{identity}] invalid action: {action}")
    bid_price = float(decision["bid_price"])
    if bid_price <= 0:
        raise ValueError(f"[{identity}] bid_price must be positive, got {bid_price}")
    quantity = float(decision["quantity"])
    if quantity < 0:
        raise ValueError(f"[{identity}] quantity must be non-negative, got {quantity}")
    return {
        "action": action,
        "bid_price": bid_price,
        "quantity": quantity,
        "reasoning": str(decision["reasoning"]),
        "analysis": str(decision["analysis"]),
    }


class RagLLMInvestor(GeneralPlayer):
    """
    Base class for RAG-augmented Rule+LLM investors in the AsianFinancialCrisis scenario.

    Each subclass uses a system prompt that encodes BOTH persona and rules
    (identical to RuleLLMInvestor). In addition, at initialization:

        1. Documents are loaded from one of three sources (priority order):
               a. Local directory (docs_dir in rag config)
               b. URL CSV file (url_csv in rag config)
               c. Pre-processed documents in processed_dir

        2. A VectorStoreIndex is built over those documents using the embedding
           API, then persisted to disk. On resume, the persisted index is
           reloaded instead of rebuilt.

        3. At every decision round, a query is formulated from the current
           market state and the top-k most relevant chunks are retrieved and
           injected into the user prompt via the {rag_context} placeholder.

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path
        - rag: docs_dir, url_csv, docs_save_dir, rag_persist_dir, top_k,
               embed_model, embed_api_base
        - llm: sys_message, user_message, lm_name, generation_config
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    async def _initialize_agent(self) -> None:
        """One-time initialization: portfolio state + LLM client + RAG index."""
        extras = self.config.extras
        record_path = extras["record_path"]
        base_path = os.path.join(record_path, self.config.identity)
        hot_limit = extras["custom_state_hot_limit"]

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]

        self.state.custom_state["price_history"] = HistoryBuffer(
            folder=os.path.join(base_path, "price"),
            entry_limit=hot_limit,
        )

        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env")
        if not os.getenv("ARK_API_KEY"):
            raise RuntimeError(
                "ARK_API_KEY not found after loading .env. "
                f"Ensure .env file exists at {project_root / '.env'} and contains ARK_API_KEY."
            )

        llm_config = extras["llm"]
        lm_name = llm_config["lm_name"]
        generation_config = llm_config["generation_config"]

        self.state.custom_state["lm_name"] = lm_name
        self.state.custom_state["generation_config"] = generation_config

        llm_client = LangChainAPIInference(
            lm_name=lm_name,
            generation_config=generation_config,
        )
        self.state.custom_state["llm_client"] = llm_client

        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        await self._initialize_rag(rag_cfg, llm_client, extras["llm"])

    async def _initialize_rag(
        self,
        rag_cfg: Dict[str, Any],
        llm_client: Any,
        llm_config: Dict[str, Any],
    ) -> None:
        """Build or load the agent's RAG index using the unified knowledge architecture.

        Resolution Flow:
            1. ResourceManager.resolve_agent_knowledge() merges global + private config
            2. Try loading local RAG index (resume support)
            3. Try copying shared RAG index to local
            4. Fallback: load processed docs and build local index from scratch
        """
        extras = self.config.extras
        record_path = extras["record_path"]

        knowledge_config = extras["knowledge"]
        if not knowledge_config:
            knowledge_config = {
                "backend": "local",
                "global_uri": rag_cfg["docs_dir"],
                "preprocessing": {
                    "parser": "mineru",
                    "output_position": rag_cfg["mineru_output_dir"],
                },
                "rag": {
                    "output_position": rag_cfg["shared_rag_index_dir"],
                },
            }

        resource_manager = ResourceManager(knowledge_config)

        private_knowledge = extras["private_knowledge"]
        if not private_knowledge:
            private_knowledge = {
                "from_global_resources": ["MinerU_processed"],
                "local_resources": {
                    "local_uri": "",
                    "local_resources": [],
                },
                "rag": rag_cfg,
            }

        agent_knowledge = resource_manager.resolve_agent_knowledge(
            agent_id=self.identity,
            private_knowledge=private_knowledge,
            record_path=record_path,
        )

        processed_dir = agent_knowledge["processed_dir"]
        shared_rag_dir = agent_knowledge["shared_rag_dir"]
        local_uri = agent_knowledge["local_uri"]
        local_rag_dir = agent_knowledge["local_rag_dir"]
        resolved_rag = agent_knowledge["rag"]

        os.makedirs(local_uri, exist_ok=True)
        os.makedirs(local_rag_dir, exist_ok=True)

        logger.info(
            "[%s] Knowledge architecture:\n"
            "  global_uri=%s\n  processed_dir=%s\n  shared_rag_dir=%s\n"
            "  local_uri=%s\n  local_rag_dir=%s",
            self.identity,
            agent_knowledge["global_uri"],
            processed_dir,
            shared_rag_dir,
            local_uri,
            local_rag_dir,
        )

        embed_type = resolved_rag["embed_type"]
        embed_model = resolved_rag["embed_model"]
        embed_api_base = resolved_rag["embed_api_base"]
        embed_api_key = resolved_rag["embed_api_key"]
        chunk_size = int(resolved_rag["chunk_size"])
        chunk_overlap = int(resolved_rag["chunk_overlap"])

        if not embed_api_key:
            if embed_type == "litellm":
                embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
            elif embed_type == "openai":
                embed_api_key = os.getenv("ARK_API_KEY", "")

        rag_store = KnowledgeStore(
            embed_model_name=embed_model,
            embed_api_key=embed_api_key,
            embed_api_base=embed_api_base,
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if os.path.isdir(local_rag_dir):
            index_files = [
                f for f in os.listdir(local_rag_dir) if not f.startswith(".")
            ]
            if index_files:
                logger.info(
                    "[%s] Loading agent-local RAG index from %s (%d files)",
                    self.identity,
                    local_rag_dir,
                    len(index_files),
                )
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    logger.info(
                        "[%s] Successfully loaded agent-local RAG index",
                        self.identity,
                    )
                    return
                except Exception as exc:
                    logger.warning(
                        "[%s] Failed to load local index (%s); will try shared",
                        self.identity,
                        exc,
                    )

        shared_rag_dirs = (
            resolved_rag["shared_rag_index_dirs"]
            if "shared_rag_index_dirs" in resolved_rag
            else []
        )
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]

        for s_dir in shared_rag_dirs:
            if os.path.isdir(s_dir):
                shared_index_files = [
                    f for f in os.listdir(s_dir) if not f.startswith(".")
                ]
                if shared_index_files:
                    logger.info(
                        "[%s] Found shared RAG index at %s (%d files). Copying to local...",
                        self.identity,
                        s_dir,
                        len(shared_index_files),
                    )
                    try:
                        for item in shared_index_files:
                            src = os.path.join(s_dir, item)
                            dst = os.path.join(local_rag_dir, item)
                            if os.path.isdir(src):
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src, dst)
                        rag_store.load(local_rag_dir)
                        self.state.custom_state["rag_store"] = rag_store
                        self.state.custom_state["rag_cfg"] = resolved_rag
                        logger.info(
                            "[%s] Successfully copied shared RAG index to local",
                            self.identity,
                        )
                        return
                    except Exception as exc:
                        logger.warning(
                            "[%s] Failed to copy shared index (%s); will build",
                            self.identity,
                            exc,
                        )

        loader = KnowledgeLoader()
        docs: List[Any] = []

        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            logger.info(
                "[%s] Loading processed documents from: %s",
                self.identity,
                processed_dir,
            )
            docs = loader.load_from_dir(processed_dir)
        else:
            logger.error(
                "[%s] No processed documents found in %s. "
                "Ensure ResourceManager pre-processed documents during simulation setup.",
                self.identity,
                processed_dir,
            )
            raise RuntimeError(
                f"[{self.identity}] No processed documents available for RAG. "
                f"Ensure documents are available in {processed_dir} "
                f"or check ResourceManager preprocessing logs."
            )

        logger.info(
            "[%s] Building RAG index over %d document(s)...",
            self.identity,
            len(docs),
        )
        rag_store.build(docs)
        logger.info(
            "[%s] Built and persisted RAG index to local: %s",
            self.identity,
            local_rag_dir,
        )

        try:
            for item in os.listdir(local_rag_dir):
                if item.startswith("."):
                    continue
                src = os.path.join(local_rag_dir, item)
                dst = os.path.join(shared_rag_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            logger.info(
                "[%s] Copied RAG index to shared location: %s",
                self.identity,
                shared_rag_dir,
            )
        except Exception as exc:
            logger.warning(
                "[%s] Failed to copy to shared location: %s",
                self.identity,
                exc,
            )

        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

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
            if "rag_cfg" in custom and "rag_store" not in custom:
                rag_cfg = custom["rag_cfg"]
                local_rag_dir = (
                    rag_cfg["local_index_dir"] if "local_index_dir" in rag_cfg else ""
                )
                if not local_rag_dir and "local_workspace_dir" in rag_cfg:
                    local_rag_dir = os.path.join(
                        rag_cfg["local_workspace_dir"], "rag_index"
                    )

                if not local_rag_dir:
                    logger.warning(
                        "Cannot reconstruct RAG store: no local_index_dir or local_workspace_dir"
                    )
                    return

                embed_type = rag_cfg["embed_type"]
                embed_api_key = rag_cfg["embed_api_key"]
                if not embed_api_key:
                    if embed_type == "litellm":
                        embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
                    elif embed_type == "openai":
                        embed_api_key = os.getenv("ARK_API_KEY", "")

                rag_store = KnowledgeStore(
                    embed_model_name=rag_cfg["embed_model"],
                    embed_api_key=embed_api_key,
                    embed_api_base=rag_cfg["embed_api_base"],
                    embed_type=embed_type,
                    persist_dir=local_rag_dir,
                    chunk_size=int(rag_cfg["chunk_size"]),
                    chunk_overlap=int(rag_cfg["chunk_overlap"]),
                )
                if os.path.isdir(local_rag_dir):
                    try:
                        rag_store.load(local_rag_dir)
                    except Exception as exc:
                        logger.warning(
                            "RAG store reload failed (%s); index unavailable until reinit",
                            exc,
                        )
                custom["rag_store"] = rag_store

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build the user prompt with RAG context + market state."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]
        round_num = self.state.custom_state["round"]
        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"] or {}

        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"] if "top_k" in rag_cfg else 3
            query = KnowledgeQuery(
                text=(
                    f"investment strategy when: "
                    f"price={market_data['price']:.2f}, "
                    f"deviation={market_data['deviation']:+.2%}, "
                    f"fundamental={market_data['fundamental']:.2f}"
                ),
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text

        if not rag_context:
            rag_context = "(No relevant knowledge retrieved this round.)"
        self.state.custom_state["last_rag_context"] = rag_context

        llm_config = self.config.extras["llm"]
        template = load_prompt(llm_config["user_message"])
        return template.format(
            round_num=round_num,
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            deviation=market_data["deviation"],
            fundamental=market_data["fundamental"],
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
            rag_context=rag_context,
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        strategy_name = self.__class__.__name__

        system_prompt = load_prompt(self.config.extras["llm"]["sys_message"])
        user_prompt = self._build_prompt(market_data)

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            try:
                infer_output = llm_client.run([infer_input])
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                decision = _validate_decision(decision, self.identity)
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < max_retries - 1 and (parse_error or retryable_api_error):
                    logger.debug("[%s] LLM call/parse failed, retrying: %s", self.identity, exc)
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM decision contract failed after "
                f"{max_retries} retries: {last_error}"
            )

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        if action == "buy":
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] -= quantity
        else:
            quantity = 0.0

        logger.info(
            "[%s] R%d (%s): Q=%+.2f",
            self.identity,
            round_num,
            strategy_name,
            quantity,
        )

        order = {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": str(decision["reasoning"])[:100],
            "analysis": str(decision["analysis"]),
            "rag_context": self.state.custom_state["last_rag_context"],
        }

        validate_order(order)
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class RagLLMHotMoneyFunder(RagLLMInvestor):
    """RAG-augmented hot money funder — rapidly reverses at first crisis signal. Theory: simulation-bases.md §4.1."""

    pass


class RagLLMContagionTrader(RagLLMInvestor):
    """RAG-augmented contagion trader — spreads selling across borders. Theory: simulation-bases.md §4.2."""

    pass


class RagLLMIMFRescuer(RagLLMInvestor):
    """RAG-augmented IMF rescuer — stabilizing emergency liquidity provider. Theory: simulation-bases.md §4.3."""

    pass


class RagLLMValueContrarian(RagLLMInvestor):
    """RAG-augmented value contrarian — buys oversold crisis assets. Theory: simulation-bases.md §4.4."""

    pass


class RagLLMNoiseTrader(RagLLMInvestor):
    """RAG-augmented noise trader — uninformed random participant. Theory: simulation-bases.md §4.5."""

    pass


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMHotMoneyFunder",
    "RagLLMContagionTrader",
    "RagLLMIMFRescuer",
    "RagLLMValueContrarian",
    "RagLLMNoiseTrader",
]
