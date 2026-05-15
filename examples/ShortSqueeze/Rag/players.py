"""ShortSqueezeRag — RAG-augmented Rule+LLM Short Squeeze Simulation

Design:
    - Market coordinator: identical rule-based price dynamics as ShortSqueeze.
    - Investors: LLM-powered with two layers of augmentation:
        1. System prompt embeds explicit quantitative rules (from rule-based)
           alongside a rich persona/profile description (same as RuleLLM).
        2. At initialization, each agent builds a personal RAG library by
           downloading reference documents and indexing them with LlamaIndex + ARK embedding API.
        3. At every decision round, the agent retrieves the top-k most
           relevant text chunks from its RAG library and injects them into
           the user prompt before calling the LLM.

This extends the three-variant comparison:
    ShortSqueeze        — pure rule-based
    ShortSqueezeRuleLLM — LLM with rules in prompt (no external knowledge)
    ShortSqueezeRag     — LLM with rules in prompt + RAG knowledge retrieval

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "ShortSqueezeRag" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/ShortSqueeze/Rag/run_flash_crash_ragllm.py \
       -c configs/ShortSqueeze/Rag/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

from __future__ import annotations

import importlib
import json
import logging
import os
import random
import re
import shutil
import time
from typing import Any, Dict, List, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.knowledge.manager import KnowledgeManager
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from examples.llm_utils import parse_llm_response_with_thinking

from .prompts import (
    RAGLLM_SHORT_SELLER_SYS,
    RAGLLM_MOMENTUM_BUYER_SYS,
    RAGLLM_RETAIL_TRADER_SYS,
    RAGLLM_VALUE_INVESTOR_SYS,
    RAGLLM_INSTITUTIONAL_HOLDER_SYS,
)

logger = logging.getLogger("ShortSqueezeRag")


# =============================================================================
# Market — Rule-Based Coordinator (identical to ShortSqueezeRuleLLM.Market)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with liquidity-sensitive pricing.

    Price model (rule-based, unchanged from ShortSqueeze):
        Price impact increases when liquidity is low (short squeeze mechanism).
        P(t+1) = P(t) + price_impact * liquidity_factor * NetDemand
                 + mean_reversion * (F - P(t)) + epsilon

    Parameters from config extras:
        - fundamental_value, initial_price
        - base_price_impact, mean_reversion, noise_std
        - low_liquidity_threshold, high_impact_multiplier, base_liquidity
        - custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["liquidity"] = 100.0
            self.state.custom_state["_random"] = random

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],
                        "quantity": order["quantity"],
                        "strategy": order["strategy"],
                        "provides_liquidity": order["provides_liquidity"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        rng = self.state.custom_state["_random"]

        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        base_liquidity = extras["base_liquidity"]
        low_liquidity_threshold = extras["low_liquidity_threshold"]
        high_impact_multiplier = extras["high_impact_multiplier"]
        base_price_impact = extras["base_price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        liquidity_provision = sum(
            abs(o["quantity"]) for o in orders if o["provides_liquidity"]
        )
        total_liquidity = base_liquidity + liquidity_provision

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        if total_liquidity < low_liquidity_threshold:
            liquidity_factor = high_impact_multiplier
        else:
            liquidity_factor = (
                1.0 + (low_liquidity_threshold / total_liquidity - 1.0) * 0.5
            )

        price_impact = base_price_impact * net_demand * liquidity_factor
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = rng.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["liquidity_history"].append(total_liquidity)

        logger.debug(
            "[Market] R%d  P=%.2f→%.2f (%+.2f%%)  Liq=%.1f  IF=%.2f  ND=%+.2f",
            round_num,
            current_price,
            new_price,
            price_return * 100,
            total_liquidity,
            liquidity_factor,
            net_demand,
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "liquidity": total_liquidity,
            "round": round_num,
            "fundamental": fundamental_value,
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_price"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Base RagLLM Investor
# =============================================================================


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented short-squeeze investors."""

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        llm_cfg = self.config.extras["llm"]
        self._llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )
        return self._llm

    # ------------------------------------------------------------------
    # perceive
    # ------------------------------------------------------------------

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
        """One-time initialization: LLM client + RAG index."""
        extras = self.config.extras
        record_path = extras["record_path"]
        base_path = os.path.join(record_path, self.config.identity)
        hot_limit = extras["custom_state_hot_limit"]

        # Portfolio state
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]

        # Price history buffer
        self.state.custom_state["price_history"] = HistoryBuffer(
            folder=os.path.join(base_path, "price"),
            entry_limit=hot_limit,
        )

        # LLM client for RAG initialization
        llm_client = self._get_llm()

        # RAG index
        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        await self._initialize_rag(rag_cfg, llm_client, extras["llm"])

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        """Build or load the agent's RAG index using the unified knowledge architecture."""
        extras = self.config.extras
        record_path = extras["record_path"]

        # STEP 1: Resolve knowledge config via ResourceManager
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

        # STEP 2: Build KnowledgeStore with resolved RAG config
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

        # STEP 3: Try loading existing local RAG index (resume support)
        if os.path.isdir(local_rag_dir):
            index_files = [
                f for f in os.listdir(local_rag_dir) if not f.startswith(".")
            ]
            if index_files:
                logger.info(
                    "[%s] Loading agent-local RAG index from %s",
                    self.identity,
                    local_rag_dir,
                )
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    logger.info(
                        "[%s] Successfully loaded agent-local RAG index", self.identity
                    )
                    return
                except Exception as exc:
                    logger.warning(
                        "[%s] Failed to load local index (%s); will try shared",
                        self.identity,
                        exc,
                    )

        # STEP 4: Try copying shared RAG index to local
        shared_rag_dirs = resolved_rag["shared_rag_index_dirs"]
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]

        for s_dir in shared_rag_dirs:
            if os.path.isdir(s_dir):
                shared_index_files = [
                    f for f in os.listdir(s_dir) if not f.startswith(".")
                ]
                if shared_index_files:
                    logger.info(
                        "[%s] Found shared RAG index at %s. Copying to local...",
                        self.identity,
                        s_dir,
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

        # STEP 5: Load processed documents and build index from scratch
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
                "[%s] No processed documents found in %s.",
                self.identity,
                processed_dir,
            )
            raise RuntimeError(
                f"[{self.identity}] No processed documents available for RAG. "
                f"Ensure documents are available in {processed_dir}."
            )

        logger.info(
            "[%s] Building RAG index over %d document(s)...", self.identity, len(docs)
        )
        rag_store.build(docs)
        logger.info(
            "[%s] Built and persisted RAG index to local: %s",
            self.identity,
            local_rag_dir,
        )

        # Copy to shared location for other agents to reuse
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
                "[%s] Failed to copy to shared location: %s", self.identity, exc
            )

        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    # ------------------------------------------------------------------
    # Serialization (exclude non-picklable objects for Ray)
    # ------------------------------------------------------------------

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
                local_rag_dir = rag_cfg["local_index_dir"]
                if not local_rag_dir:
                    local_workspace_dir = rag_cfg["local_workspace_dir"]
                    if local_workspace_dir:
                        local_rag_dir = os.path.join(local_workspace_dir, "rag_index")

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

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build the user prompt with RAG context + market state."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]
        round_num = self.state.custom_state["round"]
        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]

        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )

        # Retrieve relevant context from RAG library
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=(
                    f"trading strategy when: "
                    f"price={market_data['price']:.2f}, "
                    f"liquidity={market_data['liquidity']:.1f}, "
                    f"return={market_data['return_pct']:+.2f}%, "
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

        return (
            f"Round {round_num}\n"
            f"RAG Context:\n{rag_context}\n\n"
            f"Price: ${market_data['price']:.2f}  prev=${market_data['prev_price']:.2f}"
            f"  ret={market_data['return_pct']:+.2f}%\n"
            f"Short interest: {market_data['short_interest']:.1f}%"
            f"  squeeze_pressure={market_data['squeeze_pressure']:.2f}\n"
            f"Liquidity: {market_data['liquidity']:.1f}  fundamental=${market_data['fundamental']:.2f}\n"
            f"Recent prices: {recent_prices}\n"
            f"Portfolio: cash={cash:.2f}  position={position:.4f}"
            f"  value={cash + position * market_data['price']:.2f}\n"
            "Respond with <analysis>...</analysis> then "
            '<decision>{"bid_price":...,"quantity":...,"reasoning":"...","provides_liquidity":false}</decision>'
        )

    # ------------------------------------------------------------------
    # LLM response parsing
    # ------------------------------------------------------------------

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with analysis and decision sections."""
        return parse_llm_response_with_thinking(response_text)

    # ------------------------------------------------------------------
    # Portfolio constraints
    # ------------------------------------------------------------------

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        """Enforce cash / position limits."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    # ------------------------------------------------------------------
    # decide
    # ------------------------------------------------------------------

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(market_data)
        system_prompt = self._system_prompt
        llm_client = self._get_llm()

        max_retries = 3
        decision: Dict[str, Any] = {}
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.outputs[0].response)
                break
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"[{self.identity}] LLM failed after {max_retries} attempts: {e}"
                    )
                logger.debug(
                    "[%s] LLM parse failed (attempt %d), retrying…",
                    self.identity,
                    attempt + 1,
                )

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity)

        # Execute trade
        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        logger.debug(
            "[%-25s] R%d (%-25s): P=%7.2f  Q=%+7.2f | Cash=%8.2f  Pos=%+7.2f",
            self.identity,
            round_num,
            strategy_name,
            bid_price,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:120],
            "analysis": decision["analysis"],
            "provides_liquidity": decision["provides_liquidity"],
        }

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


# =============================================================================
# Concrete RAG+LLM Investor Types
# =============================================================================


class RagLLMShortSeller(RagLLMInvestor):
    """RAG-augmented short seller."""

    _system_prompt = RAGLLM_SHORT_SELLER_SYS


class RagLLMRetailCoordinator(RagLLMInvestor):
    """RAG-augmented retail coordinator."""

    _system_prompt = RAGLLM_RETAIL_TRADER_SYS


class RagLLMMomentumBuyer(RagLLMInvestor):
    """RAG-augmented momentum buyer."""

    _system_prompt = RAGLLM_MOMENTUM_BUYER_SYS


class RagLLMValueInvestor(RagLLMInvestor):
    """RAG-augmented value investor."""

    _system_prompt = RAGLLM_VALUE_INVESTOR_SYS


class RagLLMInstitutionalHolder(RagLLMInvestor):
    """RAG-augmented institutional holder."""

    _system_prompt = RAGLLM_INSTITUTIONAL_HOLDER_SYS


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMShortSeller",
    "RagLLMRetailCoordinator",
    "RagLLMMomentumBuyer",
    "RagLLMValueInvestor",
    "RagLLMInstitutionalHolder",
]
