"""AnchoringEffect Rag — RAG-augmented Rule+LLM Anchoring Effect Simulation

Design:
    - Market coordinator: identical rule-based price dynamics as AnchoringEffect.
    - Investors: LLM-powered with system prompts embedding explicit quantitative rules
      (from RuleLLM variant) + RAG knowledge retrieval at each decision round.

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

from masim.utils.llm_utils import parse_llm_response_with_thinking
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

from examples.AnchoringEffect.Rule.players import Market

logger = logging.getLogger("AnchoringEffect.Rag")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from a module path (module:VARIABLE)."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RagLLMInvestor(GeneralPlayer):
    """
    Base class for RAG-augmented Rule+LLM investors in the AnchoringEffect scenario.

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path
        - llm: sys_message, user_message, lm_name, generation_config
        - rag / private_knowledge.rag: RAG configuration
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
        hot_limit = extras["custom_state_hot_limit"]

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price_history"] = HistoryBuffer(
            folder=os.path.join(record_path, self.config.identity, "price"),
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
        """Build or load the agent's RAG index using the unified knowledge architecture."""
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
                "local_resources": {"local_uri": "", "local_resources": []},
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
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    logger.info(
                        "[%s] Loaded local RAG index (%d files)",
                        self.identity,
                        len(index_files),
                    )
                    return
                except Exception as exc:
                    logger.warning(
                        "[%s] Failed to load local index (%s); trying shared",
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
                shared_files = [f for f in os.listdir(s_dir) if not f.startswith(".")]
                if shared_files:
                    try:
                        for item in shared_files:
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
                            "[%s] Copied shared RAG index to local", self.identity
                        )
                        return
                    except Exception as exc:
                        logger.warning(
                            "[%s] Failed to copy shared index (%s); building",
                            self.identity,
                            exc,
                        )

        loader = KnowledgeLoader()
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            raise RuntimeError(
                f"[{self.identity}] No processed documents available for RAG in {processed_dir}."
            )

        rag_store.build(docs)

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
        except Exception as exc:
            logger.warning(
                "[%s] Failed to copy to shared location: %s", self.identity, exc
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
                if not local_rag_dir:
                    local_workspace_dir = (
                        rag_cfg["local_workspace_dir"]
                        if "local_workspace_dir" in rag_cfg
                        else ""
                    )
                    if local_workspace_dir:
                        local_rag_dir = os.path.join(local_workspace_dir, "rag_index")
                if not local_rag_dir:
                    logger.warning("Cannot reconstruct RAG store: no local_index_dir")
                    return
                embed_type = (
                    rag_cfg["embed_type"] if "embed_type" in rag_cfg else "litellm"
                )
                embed_api_key = (
                    rag_cfg["embed_api_key"] if "embed_api_key" in rag_cfg else ""
                )
                if not embed_api_key:
                    if embed_type == "litellm":
                        embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
                    elif embed_type == "openai":
                        embed_api_key = os.getenv("ARK_API_KEY", "")
                rag_store = KnowledgeStore(
                    embed_model_name=(
                        rag_cfg["embed_model"]
                        if "embed_model" in rag_cfg
                        else "openai/hunyuan-embedding"
                    ),
                    embed_api_key=embed_api_key,
                    embed_api_base=(
                        rag_cfg["embed_api_base"] if "embed_api_base" in rag_cfg else ""
                    ),
                    embed_type=embed_type,
                    persist_dir=local_rag_dir,
                    chunk_size=(
                        int(rag_cfg["chunk_size"]) if "chunk_size" in rag_cfg else 512
                    ),
                    chunk_overlap=(
                        int(rag_cfg["chunk_overlap"])
                        if "chunk_overlap" in rag_cfg
                        else 64
                    ),
                )
                if os.path.isdir(local_rag_dir):
                    try:
                        rag_store.load(local_rag_dir)
                    except Exception as exc:
                        logger.warning("RAG store reload failed (%s)", exc)
                custom["rag_store"] = rag_store

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build the user prompt with RAG context + market state."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        rag_store: KnowledgeStore = (
            self.state.custom_state["rag_store"]
            if "rag_store" in self.state.custom_state
            else None
        )
        rag_cfg: Dict[str, Any] = (
            self.state.custom_state["rag_cfg"]
            if "rag_cfg" in self.state.custom_state
            else {}
        )

        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=(
                    f"anchoring bias trading strategy when: "
                    f"price={market_data['price']:.2f}, "
                    f"fundamental={market_data['fundamental']:.2f}, "
                    f"deviation={market_data['deviation']:+.2%}"
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

        template = load_prompt(self.config.extras["llm"]["user_message"])
        # Compute price_change for template (not broadcast by Market)
        price_change = (
            (market_data["price"] - market_data["prev_price"])
            / market_data["prev_price"]
            if market_data["prev_price"] > 0
            else 0.0
        )
        return template.format(
            round=round_num,
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            fundamental=market_data["fundamental"],
            price_change=price_change,
            deviation=market_data["deviation"],
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
            infer_output = llm_client.run(infer_input)
            try:
                decision = parse_llm_response_with_thinking(infer_output.response)
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug("[%s] LLM parse failed, retrying...", self.identity)

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after {max_retries} retries: {last_error}"
            )

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        if bid_price <= 0:
            bid_price = market_data["price"]

        if action == "buy":
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            quantity = min(quantity, position)
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] -= quantity

        logger.info(
            "[%s] R%d (%s %s): Q=%.2f",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
        )

        order = {
            "action": action,
            "quantity": quantity,
            "bid_price": bid_price,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
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


class RagLLMAnchoredTrader(RagLLMInvestor):
    """RAG-augmented anchored trader — anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md §4.1 — AnchoredTrader."""

    pass


class RagLLMHistoricalAnchor(RagLLMInvestor):
    """RAG-augmented historical anchor — anchors to historical average price. Theory: simulation-bases.md §4.2 — HistoricalAnchor."""

    pass


class RagLLMRationalUpdater(RagLLMInvestor):
    """RAG-augmented rational updater — Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md §4.3 — RationalUpdater."""

    pass


class RagLLMMomentumTrader(RagLLMInvestor):
    """RAG-augmented momentum trader — follows price trends. Theory: simulation-bases.md §4.4 — MomentumTrader."""

    pass


class RagLLMNoiseTrader(RagLLMInvestor):
    """RAG-augmented noise trader — uninformed random participant. Theory: simulation-bases.md §4.5 — NoiseTrader."""

    pass


class RagLLMDispositionTrader(RagLLMInvestor):
    """RAG-augmented disposition trader — sells winners early, holds losers (Prospect Theory). Theory: simulation-bases.md §4.6 — DispositionTrader."""

    pass


class RagLLMContrarianTrader(RagLLMInvestor):
    """RAG-augmented contrarian trader — fades cumulative overextension over a short lookback. Theory: simulation-bases.md §4.7 — ContrarianTrader."""

    pass


class RagLLMFundamentalAnalyst(RagLLMInvestor):
    """RAG-augmented fundamental analyst — slow belief convergence toward fundamental value (conservatism bias). Theory: simulation-bases.md §4.8 — FundamentalAnalyst."""

    pass


class RagLLMLiquidityProvider(RagLLMInvestor):
    """RAG-augmented liquidity provider — passive two-sided quoting around a short-term EMA. Theory: simulation-bases.md §4.9 — LiquidityProvider."""

    pass


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMAnchoredTrader",
    "RagLLMHistoricalAnchor",
    "RagLLMRationalUpdater",
    "RagLLMMomentumTrader",
    "RagLLMNoiseTrader",
    "RagLLMDispositionTrader",
    "RagLLMContrarianTrader",
    "RagLLMFundamentalAnalyst",
    "RagLLMLiquidityProvider",
]
