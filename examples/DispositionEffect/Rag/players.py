"""DispositionEffect Rag - RAG-augmented Disposition Effect Simulation

Design:
    - Market coordinator: identical rule-based price dynamics as DispositionEffect.
    - Investors: LLM-powered with two layers of augmentation:
        1. System prompt embeds explicit quantitative rules (from rule-based)
           alongside a rich persona/profile description (same as RuleLLM).
        2. At initialization, each agent builds a personal RAG library by
           downloading reference documents and indexing them with LlamaIndex.
        3. At every decision round, the agent retrieves the top-k most
           relevant text chunks from its RAG library and injects them into
           the user prompt before calling the LLM.

This extends the four-variant comparison:
    DispositionEffect (Rule)     — pure rule-based
    DispositionEffect LLM        — LLM with persona prompts (no external knowledge)
    DispositionEffect RuleLLM    — LLM with rules in prompt (no external knowledge)
    DispositionEffect Rag        — LLM with rules in prompt + RAG knowledge retrieval

RAG Knowledge Sources for Disposition Effect:
    - Prospect Theory papers (Kahneman & Tversky)
    - Disposition Effect studies (Shefrin & Statman, Odean)
    - Behavioral finance case studies
    - Real investor decision patterns

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "DispositionEffectRag" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/DispositionEffect/Rag/run_disposition_rag.py \\
       -c configs/DispositionEffect/Rag/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

from __future__ import annotations

import importlib
import logging
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Add examples directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import parse_llm_response_with_thinking
from masim.knowledge import KnowledgeLoader, KnowledgeQuery, KnowledgeStore
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("DispositionEffectRag")
RAG_FALLBACK_CONTEXT = "(No relevant knowledge retrieved this round.)"
_DECISION_PARAM_SKIP_KEYS = {
    "record_path",
    "initial_cash",
    "initial_position",
    "initial_purchase_price",
    "custom_state_hot_limit",
    "llm",
    "rag",
}


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from a module path (``module:VARIABLE``)."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def format_decision_params(extras: Dict[str, Any]) -> str:
    """Format configured rule parameters for prompt injection."""
    params = {
        key: value
        for key, value in extras.items()
        if key not in _DECISION_PARAM_SKIP_KEYS
    }
    if not params:
        return "None."
    return "\n".join(f"- {key}: {value}" for key, value in sorted(params.items()))


# =============================================================================
# Market — Rule-Based Coordinator (identical to DispositionEffect.Market)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with standard price dynamics and news shocks.

    Price model (rule-based, unchanged from DispositionEffect):
        P(t+1) = P(t) + lambda × NetDemand + gamma × [F - P(t)] + epsilon + NewsShock

    Parameters from config extras:
        - fundamental_value, initial_price, price_impact, mean_reversion
        - noise_std, news_probability, news_impact_range
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

            self.state.custom_state["price"] = extras["initial_price"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
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
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Random news shock
        news_probability = extras["news_probability"]
        news_impact_range = extras["news_impact_range"]
        news_shock = 0.0
        if random.random() < news_probability:
            news_shock = random.uniform(-news_impact_range, news_impact_range)

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact_rate = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        price_impact = price_impact_rate * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(
            1.0, current_price + price_impact + mean_reversion + noise + news_shock
        )
        price_return = (new_price - current_price) / current_price

        # Update
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "\\n%s\\n[Market] Round %d\\n  Price: %.2f → %.2f (%+.2f%%)%s\\n  Net Demand: %+.2f, Volume: %.2f",
            "=" * 70,
            round_num,
            current_price,
            new_price,
            price_return * 100,
            f"\\n  NEWS SHOCK: {news_shock:+.2f}" if news_shock != 0 else "",
            net_demand,
            total_volume,
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "news_shock": news_shock,
            "round": round_num,
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
# Base RAG Investor with Reference Point Tracking
# =============================================================================


class BaseRagInvestor(GeneralPlayer):
    """
    Base class for RAG-augmented investors with reference point tracking.

    Extends standard investor with:
        - Knowledge store initialization
        - RAG query formulation
        - Context injection into prompts

    Parameters from config extras:
        - initial_cash, initial_position, initial_purchase_price
        - llm config (sys_message, user_message, lm_name, generation_config)
        - rag config (persist_dir, knowledge_sources)
    """

    def __init__(self, config: Any):
        super().__init__(config)
        self._init_llm_client()
        self._init_knowledge_store()

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("llm_client", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if not hasattr(self, "llm_client"):
            llm_config = self.config.extras["llm"]
            self.llm_client = LangChainAPIInference(
                lm_name=llm_config["lm_name"],
                generation_config=llm_config["generation_config"],
            )

    def _init_llm_client(self) -> None:
        """Initialize LLM inference client from config."""
        load_dotenv()

        llm_config = self.config.extras["llm"]
        self.sys_message_path = llm_config["sys_message"]
        self.user_message_path = llm_config["user_message"]

        self.llm_client = LangChainAPIInference(
            lm_name=llm_config["lm_name"],
            generation_config=llm_config["generation_config"],
        )
        logger.info("Initialized LLM client for %s", self.config.identity)

    def _init_knowledge_store(self) -> None:
        """Initialize RAG knowledge store for this investor.

        Supports multiple knowledge source types from config:
        - docs_dir: Local directory with PDF/Markdown files
        - url_csv: CSV file with URLs to fetch
        - urls: List of explicit URLs to fetch
        - agent_autonomous: Use load_for_agent based on identity
        - llm_suggested: Use suggest_and_download with LLM

        Also supports embedding configuration:
        - embed_type: "huggingface" or "openai"
        - embed_model: Model name (e.g., "BAAI/bge-small-en-v1.5")
        - embed_api_base: API base URL for OpenAI-compatible endpoints
        """
        rag_config = self.config.extras["rag"]
        persist_dir = rag_config["persist_dir"]

        # Embedding configuration
        embed_type = rag_config["embed_type"]
        embed_model = rag_config["embed_model"]
        embed_api_base = rag_config["embed_api_base"]
        if embed_type == "litellm":
            embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
        elif embed_type == "openai":
            embed_api_key = os.getenv("ARK_API_KEY", "")
        else:
            embed_api_key = ""

        # Chunking configuration
        chunk_size = rag_config["chunk_size"]
        chunk_overlap = rag_config["chunk_overlap"]

        logger.info(
            "[%s] Initializing KnowledgeStore: embed_type=%s, model=%s, persist_dir=%s",
            self.config.identity,
            embed_type,
            embed_model,
            persist_dir,
        )

        self.knowledge_store = KnowledgeStore(
            embed_model_name=embed_model,
            embed_api_key=embed_api_key,
            embed_api_base=embed_api_base,
            embed_type=embed_type,
            persist_dir=persist_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Try to load persisted index first (resume support)
        if persist_dir and os.path.isdir(persist_dir):
            try:
                self.knowledge_store.load(persist_dir)
                logger.info(
                    "[%s] Loaded persisted RAG index from %s",
                    self.config.identity,
                    persist_dir,
                )
                return
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to load persisted index (%s); building new index",
                    self.config.identity,
                    exc,
                )

        # Load documents from configured sources
        docs = self._load_knowledge_documents(rag_config)

        if docs:
            logger.info(
                "[%s] Building RAG index with %d document(s)...",
                self.config.identity,
                len(docs),
            )
            try:
                self.knowledge_store.build(docs)
                logger.info(
                    "[%s] Successfully built RAG index",
                    self.config.identity,
                )
            except Exception as exc:
                logger.error(
                    "[%s] Failed to build RAG index: %s",
                    self.config.identity,
                    exc,
                )
                raise
        else:
            logger.warning(
                "[%s] No documents loaded for RAG; index will be empty",
                self.config.identity,
            )

    def _load_knowledge_documents(self, rag_config: Dict[str, Any]) -> list:
        """Load documents from various sources based on config.

        Source priority (first match wins):
        1. docs_dir - Local directory with PDF/Markdown files
        2. url_csv - CSV file with URLs
        3. urls - Explicit list of URLs
        4. agent_autonomous - Auto-select based on agent identity
        5. llm_suggested - LLM suggests and downloads documents

        Returns:
            List of KnowledgeDocument objects
        """

        # Allow partial loading
        loader = KnowledgeLoader(fail_fast=False)
        docs = []

        # Source 1: Local directory
        docs_dir = rag_config["docs_dir"]
        if docs_dir and os.path.isdir(docs_dir):
            logger.info(
                "[%s] Loading documents from local directory: %s",
                self.config.identity,
                docs_dir,
            )
            try:
                docs = loader.load_from_dir(docs_dir)
                if docs:
                    logger.info(
                        "[%s] Loaded %d documents from %s",
                        self.config.identity,
                        len(docs),
                        docs_dir,
                    )
                    return docs
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to load from docs_dir: %s",
                    self.config.identity,
                    exc,
                )

        # Source 2: URL CSV file
        url_csv = rag_config["url_csv"]
        if url_csv and os.path.isfile(url_csv):
            logger.info(
                "[%s] Loading documents from URL CSV: %s",
                self.config.identity,
                url_csv,
            )
            try:
                docs = loader.load_from_url_csv(url_csv)
                if docs:
                    logger.info(
                        "[%s] Loaded %d documents from CSV %s",
                        self.config.identity,
                        len(docs),
                        url_csv,
                    )
                    return docs
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to load from url_csv: %s",
                    self.config.identity,
                    exc,
                )

        # Source 3: Explicit URLs list
        urls = rag_config["urls"]
        if urls:
            logger.info(
                "[%s] Loading documents from %d explicit URL(s)",
                self.config.identity,
                len(urls),
            )
            try:
                docs = loader.load_from_urls(urls)
                if docs:
                    logger.info(
                        "[%s] Loaded %d documents from URLs",
                        self.config.identity,
                        len(docs),
                    )
                    return docs
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to load from URLs: %s",
                    self.config.identity,
                    exc,
                )

        # Source 4: Agent-autonomous selection
        if rag_config["agent_autonomous"]:
            # Optional key
            docs_save_dir = rag_config["docs_save_dir"]
            # Optional key
            catalog_path = rag_config["catalog_path"]
            logger.info(
                "[%s] Using agent-autonomous document selection (save_dir=%s)",
                self.config.identity,
                docs_save_dir or "(none)",
            )
            try:
                docs = loader.load_for_agent(
                    identity=self.config.identity,
                    catalog_path=catalog_path,
                    save_dir=docs_save_dir,
                )
                if docs:
                    logger.info(
                        "[%s] Autonomous selection loaded %d documents",
                        self.config.identity,
                        len(docs),
                    )
                    return docs
            except Exception as exc:
                logger.warning(
                    "[%s] Failed agent-autonomous loading: %s",
                    self.config.identity,
                    exc,
                )

        # Source 5: LLM-suggested documents
        if rag_config["llm_suggested"]:
            n_urls = rag_config["llm_suggested_n_urls"]
            # Optional key
            docs_save_dir = rag_config["docs_save_dir"]
            persona_desc = self.config.extras["persona_description"]

            logger.info(
                "[%s] Using LLM-suggested document discovery (n_urls=%d)",
                self.config.identity,
                n_urls,
            )
            try:
                # Need LLM client for this - use the one we already have
                docs = loader.suggest_and_download(
                    persona_desc=persona_desc or f"{self.config.identity} investor",
                    llm_client=self.llm_client,
                    n_urls=n_urls,
                    save_dir=docs_save_dir,
                )
                if docs:
                    logger.info(
                        "[%s] LLM suggested %d documents",
                        self.config.identity,
                        len(docs),
                    )
                    return docs
            except Exception as exc:
                logger.warning(
                    "[%s] Failed LLM-suggested loading: %s",
                    self.config.identity,
                    exc,
                )

        # Legacy: knowledge_sources list (for backward compatibility)
        # Optional key
        knowledge_sources = rag_config["knowledge_sources"]
        if knowledge_sources:
            logger.info(
                "[%s] Loading from legacy knowledge_sources: %s",
                self.config.identity,
                knowledge_sources,
            )
            for source in knowledge_sources:
                try:
                    if os.path.isdir(source):
                        source_docs = loader.load_from_dir(source)
                    elif source.endswith(".csv"):
                        source_docs = loader.load_from_url_csv(source)
                    else:
                        source_docs = loader.load_from_urls([source])
                    docs.extend(source_docs)
                except Exception as exc:
                    logger.warning(
                        "[%s] Failed to load knowledge source %s: %s",
                        self.config.identity,
                        source,
                        exc,
                    )
            if docs:
                logger.info(
                    "[%s] Loaded %d documents from knowledge_sources",
                    self.config.identity,
                    len(docs),
                )

        return docs

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            initial_cash = extras["initial_cash"]
            initial_position = extras["initial_position"]
            initial_purchase_price = extras["initial_purchase_price"]

            self.state.custom_state["cash"] = initial_cash
            self.state.custom_state["position"] = initial_position
            self.state.custom_state["purchase_price"] = initial_purchase_price
            self.state.custom_state["total_cost"] = (
                initial_position * initial_purchase_price
            )

        market_data = None
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                break
        self.state.custom_state["market_data"] = market_data

    def update_reference_point(
        self, quantity: float, price: float, move_reference: bool = True
    ) -> None:
        """Update position and cost basis after a RAG investor trade."""
        position = self.state.custom_state["position"]
        total_cost = self.state.custom_state["total_cost"]

        if quantity > 0:
            new_cost = quantity * price
            total_cost += new_cost
            position += quantity
            if move_reference and position > 0:
                self.state.custom_state["purchase_price"] = total_cost / position
        elif quantity < 0:
            if position > 0:
                cost_per_share = total_cost / position
                total_cost -= abs(quantity) * cost_per_share
            position += quantity

        self.state.custom_state["position"] = position
        self.state.custom_state["total_cost"] = max(0, total_cost)

    def _formulate_rag_query(self, market_data: Dict[str, Any]) -> str:
        """Formulate a RAG query based on current market state."""
        price = market_data["price"]
        purchase_price = self.state.custom_state["purchase_price"]
        if purchase_price <= 0:
            raise ValueError("purchase_price must be positive")
        gain_loss = (price - purchase_price) / purchase_price

        if gain_loss > 0.05:
            return f"profit taking strategy when gain is {gain_loss*100:.1f}%"
        elif gain_loss < -0.05:
            return f"loss realization decision when loss is {gain_loss*100:.1f}%"
        else:
            return "holding strategy for small price movements"

    def _retrieve_context(self, query_text: str) -> str:
        """Retrieve relevant context from RAG knowledge store."""
        try:
            rag_config = self.config.extras["rag"]
            top_k = rag_config["top_k"]
            round_num = self.state.custom_state["round"]

            query = KnowledgeQuery(
                text=query_text,
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = self.knowledge_store.query(query)

            if result and result.chunks:
                return "\n\n".join(
                    f"[Knowledge {i+1}]: {chunk[:500]}"
                    for i, chunk in enumerate(result.chunks)
                )
        except Exception as e:
            logger.warning("RAG query failed: %s", e)
        return ""

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        if purchase_price <= 0:
            raise ValueError("purchase_price must be positive")
        gain_loss = (price - purchase_price) / purchase_price

        # RAG retrieval
        rag_query = self._formulate_rag_query(market_data)
        rag_context = self._retrieve_context(rag_query)

        # Load prompts
        sys_prompt = load_prompt(self.sys_message_path)
        user_template = load_prompt(self.user_message_path)

        prev_price = market_data["prev_price"]
        price_return = market_data["return"]
        volume = market_data["volume"]
        net_demand = market_data["net_demand"]
        news_shock = market_data["news_shock"]

        # Format user prompt — {rag_context} placeholder filled here per §8.4 spec
        injected_rag_context = rag_context if rag_context else RAG_FALLBACK_CONTEXT
        user_prompt = user_template.format(
            round=round_num,
            price=price,
            prev_price=prev_price,
            return_pct=price_return * 100,
            volume=volume,
            net_demand=net_demand,
            news_event=f"Shock: {news_shock:+.2f}" if news_shock != 0 else "None",
            cash=cash,
            position=position,
            purchase_price=purchase_price,
            gain_loss_pct=gain_loss * 100,
            portfolio_value=cash + position * price,
            decision_params=format_decision_params(extras),
            rag_context=injected_rag_context,
        )

        # Call LLM
        max_retries = 3
        raw_decision = None
        last_error = None
        for attempt in range(max_retries):
            try:
                llm_input = InferInput(system_msg=sys_prompt, user_msg=user_prompt)
                result = self.llm_client.run([llm_input])
                raw_decision = parse_llm_response_with_thinking(
                    result.outputs[0].response
                )
                if raw_decision["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"invalid action: {raw_decision['action']}")
                if float(raw_decision["bid_price"]) <= 0:
                    raise ValueError(
                        f"invalid bid_price: {raw_decision['bid_price']}"
                    )
                if not str(raw_decision["reasoning"]).strip():
                    raise ValueError("missing reasoning")
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug("[%s] LLM parse failed, retrying...", self.identity)

        if raw_decision is None:
            raise RuntimeError(
                f"[{self.config.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )

        action = raw_decision["action"]
        bid_price = float(raw_decision["bid_price"])
        quantity = float(raw_decision["quantity"])

        if action == "buy":
            quantity = min(quantity, int(cash / bid_price))
        elif action == "sell":
            quantity = min(quantity, int(abs(position)))
        else:
            quantity = 0.0

        if action == "sell":
            quantity = -abs(quantity)
        elif action == "buy":
            quantity = abs(quantity)

        move_reference = "Disposition" not in strategy_name
        if quantity > 0:
            cost = quantity * bid_price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, bid_price, move_reference)
            else:
                quantity = 0.0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * bid_price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, bid_price)
            else:
                quantity = 0.0

        order = {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "reasoning": raw_decision["reasoning"],
            "analysis": raw_decision["analysis"],
            "strategy": strategy_name,
            "rag_context": injected_rag_context,
        }
        decision = {
            **order,
            "outbound_messages": [
                {"payload": order, "content_type": "investor_bid"}
            ],
        }

        return decision

    def _hold_order(self, round_num: int, strategy_name: str) -> Dict[str, Any]:
        return {
            "action": "hold",
            "bid_price": 0.0,
            "quantity": 0.0,
            "reasoning": "No market data",
            "strategy": strategy_name,
            "rag_context": RAG_FALLBACK_CONTEXT,
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# RAG-Enhanced Investor Types
# =============================================================================


class RagDispositionInvestor(BaseRagInvestor):
    """
    RAG-enhanced disposition-prone investor.

    Has access to Prospect Theory and behavioral finance literature
    through RAG, but still exhibits disposition effect tendencies
    in decision-making.

    Theory: simulation-bases.md §4.1 — DispositionInvestor
    Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; RAG retrieves disposition effect studies.
    See simulation-bases.md §4.1 for mathematical model.
    """


class RagRationalInvestor(BaseRagInvestor):
    """
    RAG-enhanced rational investor.

    Uses academic research to make informed decisions,
    potentially overcoming disposition biases.

    Theory: simulation-bases.md §4.2 — RationalInvestor
    Theoretical basis: Expected Utility Theory; RAG retrieves rational portfolio management research.
    See simulation-bases.md §4.2 for mathematical model.
    """


class RagTaxAwareInvestor(BaseRagInvestor):
    """
    RAG-enhanced tax-aware investor.

    Has access to tax-loss harvesting strategies and
    related academic literature.

    Theory: simulation-bases.md §4.3 — TaxAwareInvestor
    Theoretical basis: Constantinides (1983) tax-loss harvesting; RAG retrieves tax strategy literature.
    See simulation-bases.md §4.3 for mathematical model.
    """


class RagInstitutionalInvestor(BaseRagInvestor):
    """
    RAG-enhanced institutional investor.

    Theory: simulation-bases.md §4.5 — InstitutionalInvestor
    Theoretical basis: Shapira & Venezia (2001) professional discipline; RAG retrieves institutional risk-control evidence.
    See simulation-bases.md §4.5 for mathematical model.
    """


class RagLossAverse(BaseRagInvestor):
    """
    RAG-enhanced extreme loss-averse investor.

    Theory: simulation-bases.md §4.1 — DispositionInvestor
    Theoretical basis: Prospect Theory loss aversion; RAG retrieves loss-aversion and disposition-effect studies.
    See simulation-bases.md §4.1 for mathematical model.
    """


__all__ = [
    "Market",
    "BaseRagInvestor",
    "RagDispositionInvestor",
    "RagRationalInvestor",
    "RagTaxAwareInvestor",
    "RagInstitutionalInvestor",
    "RagLossAverse",
]
