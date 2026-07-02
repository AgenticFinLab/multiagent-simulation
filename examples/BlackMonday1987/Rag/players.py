"""BlackMonday1987 Rag — RAG-augmented LLM simulation of the 1987 crash.

Design:
    - Market: Rule-based price dynamics (same as Rule variant).
    - Investors: LLM-powered with RAG context injected into user prompt.

October 19, 1987 — Dow fell 22.6% in one day driven by portfolio insurance,
index arbitrage, and program trading positive-feedback loops.
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

from masim.utils.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.format.order import validate_order
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from examples.BlackMonday1987.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate canonical trading decision fields before portfolio mutation."""
    action = decision["action"]
    if action not in {"buy", "sell", "hold"}:
        raise ValueError(f"[{identity}] invalid action: {action}")
    bid_price = float(decision["bid_price"])
    if bid_price <= 0:
        raise ValueError(f"[{identity}] invalid bid_price: {bid_price}")
    quantity = float(decision["quantity"])
    if quantity < 0:
        raise ValueError(f"[{identity}] invalid quantity: {quantity}")
    reasoning = str(decision["reasoning"]).strip()
    if not reasoning:
        raise ValueError(f"[{identity}] empty reasoning")
    analysis = str(decision["analysis"]).strip()
    if not analysis:
        raise ValueError(f"[{identity}] empty analysis")
    if action == "hold":
        quantity = 0.0
    return {
        **decision,
        "action": action,
        "bid_price": bid_price,
        "quantity": quantity,
        "reasoning": reasoning,
        "analysis": analysis,
    }


class RagLLMInvestor(GeneralPlayer):
    """Base RAG-augmented LLM investor for BlackMonday1987."""

    _system_prompt_path: str = ""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def _initialize_agent(self) -> None:
        """One-time initialization: portfolio state, LLM client, and RAG index."""
        extras = self.config.extras
        self.state.custom_state["cash"] = float(extras["initial_cash"])
        self.state.custom_state["position"] = int(extras["initial_position"])
        self.state.custom_state["price_history"] = []
        self.state.custom_state["market_data"] = {}
        self.state.custom_state["history_buffer"] = HistoryBuffer(
            folder=f"BlackMonday1987/Rag/{self.__class__.__name__}", entry_limit=200
        )

        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env")

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

        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        await self._initialize_rag(rag_cfg, llm_client, llm_cfg)

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        """Build or load the agent's RAG index."""
        extras = self.config.extras
        record_path = extras["record_path"]

        knowledge_config = extras["knowledge"]

        resource_manager = ResourceManager(knowledge_config)

        private_knowledge = extras["private_knowledge"]

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
            "[%s] Knowledge paths: global_uri=%s processed=%s shared_rag=%s local_rag=%s",
            self.identity,
            agent_knowledge["global_uri"],
            processed_dir,
            shared_rag_dir,
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

        # Try loading existing local index
        if os.path.isdir(local_rag_dir):
            index_files = [
                f for f in os.listdir(local_rag_dir) if not f.startswith(".")
            ]
            if index_files:
                logger.info(
                    "[%s] Loading local RAG index from %s", self.identity, local_rag_dir
                )
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    return
                except Exception as exc:  # pylint: disable=broad-except
                    logger.warning(
                        "[%s] Local index load failed: %s", self.identity, exc
                    )

        # Try copying from shared index
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
                    logger.info(
                        "[%s] Copying shared index from %s", self.identity, s_dir
                    )
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
                        return
                    except Exception as exc:  # pylint: disable=broad-except
                        logger.warning(
                            "[%s] Shared copy failed: %s", self.identity, exc
                        )

        # Build from processed documents
        loader = KnowledgeLoader()
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            raise RuntimeError(
                f"[{self.identity}] No processed documents in {processed_dir}."
            )

        logger.info("[%s] Building RAG index over %d docs", self.identity, len(docs))
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
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("[%s] Copy to shared failed: %s", self.identity, exc)

        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    def __getstate__(self) -> Dict:
        state = self.__dict__.copy()
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = dict(self.state.custom_state)
            for key in ("llm_client", "rag_store"):
                custom.pop(key, None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state: Dict) -> None:
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
                    local_ws = (
                        rag_cfg["local_workspace_dir"]
                        if "local_workspace_dir" in rag_cfg
                        else ""
                    )
                    if local_ws:
                        local_rag_dir = os.path.join(local_ws, "rag_index")
                if not local_rag_dir:
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
                    except Exception as exc:  # pylint: disable=broad-except
                        logger.warning("RAG store reload failed: %s", exc)
                custom["rag_store"] = rag_store

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build user prompt with RAG context and current market state."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = (
            self.state.custom_state["round"]
            if "round" in self.state.custom_state
            else 0
        )
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        deviation = market_data["deviation"]
        portfolio_value = cash + position * price

        rag_store: Optional[KnowledgeStore] = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"] or {}
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"] if "top_k" in rag_cfg else 3
            query = KnowledgeQuery(
                text=(
                    f"trading strategy: price={price:.2f}, "
                    f"fundamental={fundamental:.2f}, deviation={deviation:+.2%}"
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

        template = load_prompt("examples.BlackMonday1987.Rag.prompts:RAG_USER_TEMPLATE")
        return template.format(
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
            rag_context=rag_context,
        )

    async def decide(self) -> Dict:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        system_prompt = load_prompt(self._system_prompt_path)
        user_prompt = self._build_prompt(market_data)
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]

        decision = None
        last_error = None
        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            try:
                result = llm_client.run([infer_input])
                response = result.outputs[0].response
                parsed = parse_llm_response_with_thinking(response)
                decision = _validate_decision(parsed, self.identity)
                break
            except Exception as exc:  # pylint: disable=broad-except
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < max_retries - 1 and (parse_error or retryable_api_error):
                    logger.debug(
                        "[%s] LLM call/parse failed, retrying: %s",
                        self.identity,
                        exc,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after {max_retries} retries: {last_error}"
            ) from last_error

        action_str = decision["action"]
        bid_price = decision["bid_price"]
        quantity = decision["quantity"]
        if action_str == "buy":
            max_buy = cash / bid_price
            quantity = min(quantity, max_buy)
        elif action_str == "sell":
            quantity = min(quantity, max(position, 0))

        if action_str == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action_str == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] -= quantity

        order = {
            "action": action_str,
            "bid_price": bid_price,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": self.__class__.__name__,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
            "rag_context": self.state.custom_state["last_rag_context"],
        }
        validate_order(order)
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class RagLLMPortfolioInsurer(RagLLMInvestor):
    """RAG-augmented portfolio insurer — dynamic hedging seller. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.BlackMonday1987.Rag.prompts:RAG_PORTFOLIO_INSURER_SYS"
    )


class RagLLMIndexArbitrageur(RagLLMInvestor):
    """RAG-augmented index arbitrageur — exploits futures/spot gaps. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.BlackMonday1987.Rag.prompts:RAG_INDEX_ARBITRAGEUR_SYS"
    )


class RagLLMProgramTrader(RagLLMInvestor):
    """RAG-augmented program trader — automated feedback amplifier. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = "examples.BlackMonday1987.Rag.prompts:RAG_PROGRAM_TRADER_SYS"


class RagLLMValueInvestor(RagLLMInvestor):
    """RAG-augmented value investor — buys at deep discount to fundamentals. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.BlackMonday1987.Rag.prompts:RAG_VALUE_INVESTOR_SYS"


class RagLLMNoiseTrader(RagLLMInvestor):
    """RAG-augmented noise trader — random uninformed liquidity provider. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.BlackMonday1987.Rag.prompts:RAG_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMPortfolioInsurer",
    "RagLLMIndexArbitrageur",
    "RagLLMProgramTrader",
    "RagLLMValueInvestor",
    "RagLLMNoiseTrader",
]
