"""ConfirmationBias Rag — RAG-augmented LLM simulation of confirmation bias dynamics."""

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

from examples.ConfirmationBias.Rule.players import Market  # noqa: F401

logger = logging.getLogger(__name__)

# Canonical fallback message emitted when a RAG query returns no hits. This is
# imported by analysis.py so that per-round retrieval-failure counting stays in
# lock-step with the runtime string (single-source-of-truth invariant).
_RAG_FALLBACK: str = "(No relevant knowledge retrieved this round.)"


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RagLLMInvestor(GeneralPlayer):
    """Base RAG-augmented LLM investor for ConfirmationBias."""

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
        extras = self.config.extras
        self.state.custom_state["cash"] = float(extras["initial_cash"])
        self.state.custom_state["position"] = int(extras["initial_position"])
        self.state.custom_state["price_history"] = []
        self.state.custom_state["market_data"] = {}
        self.state.custom_state["history_buffer"] = HistoryBuffer(
            folder=f"ConfirmationBias/Rag/{self.__class__.__name__}", entry_limit=200
        )
        project_root = Path(__file__).parent.parent.parent.parent
        load_dotenv(project_root / ".env")
        llm_cfg = extras["llm"]
        lm_name = llm_cfg["lm_name"]
        generation_config = llm_cfg["generation_config"]
        self.state.custom_state["lm_name"] = lm_name
        self.state.custom_state["generation_config"] = generation_config
        llm_client = LangChainAPIInference(
            lm_name=lm_name, generation_config=generation_config
        )
        self.state.custom_state["llm_client"] = llm_client
        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        await self._initialize_rag(rag_cfg, llm_client, llm_cfg)

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        extras = self.config.extras
        record_path = extras["record_path"]
        knowledge_config = extras.get("knowledge", {})
        if not knowledge_config:
            knowledge_config = {
                "backend": "local",
                "global_uri": "examples/document-sources",
                "resource_csv": [
                    "examples/document-sources/books.csv",
                    "examples/document-sources/source",
                ],
                "preprocessing": {
                    "parser": "mineru",
                    "output_position": "MinerU_processed",
                },
                "rag": {"output_position": "rag_index"},
            }

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
        embed_type = resolved_rag["embed_type"]
        embed_api_key = resolved_rag["embed_api_key"]
        if not embed_api_key:
            embed_api_key = (
                os.getenv("HUNYUAN_API_KEY", "")
                if embed_type == "litellm"
                else os.getenv("ARK_API_KEY", "")
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
        if os.path.isdir(local_rag_dir):
            index_files = [
                f for f in os.listdir(local_rag_dir) if not f.startswith(".")
            ]
            if index_files:
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    return
                except Exception as exc:
                    logger.warning(
                        "[%s] Local index load failed: %s", self.identity, exc
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
                        return
                    except Exception as exc:
                        logger.warning(
                            "[%s] Shared copy failed: %s", self.identity, exc
                        )
        loader = KnowledgeLoader()
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            raise RuntimeError(
                f"[{self.identity}] No processed documents in {processed_dir}."
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
                    embed_api_key = (
                        os.getenv("HUNYUAN_API_KEY", "")
                        if embed_type == "litellm"
                        else os.getenv("ARK_API_KEY", "")
                    )
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
                        logger.warning("RAG store reload failed: %s", exc)
                custom["rag_store"] = rag_store

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
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
                    f"confirmation bias trading: price={price:.2f}, "
                    f"fundamental={fundamental:.2f}, deviation={deviation:+.2%}"
                ),
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text
        if not rag_context:
            rag_context = _RAG_FALLBACK
        self.state.custom_state["last_rag_context"] = rag_context
        template = load_prompt(
            "examples.ConfirmationBias.Rag.prompts:RAG_USER_TEMPLATE"
        )
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
        last_error = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                result = llm_client.run([infer_input])
                response = result.outputs[0].response
                parsed = parse_llm_response_with_thinking(response)
                action_str = parsed["action"]
                if action_str not in ("buy", "sell", "hold"):
                    raise ValueError(
                        f"[{self.identity}] Invalid LLM action: {action_str}"
                    )
                bid_price = float(parsed["bid_price"])
                reasoning = parsed["reasoning"]
                analysis = parsed["analysis"]
                quantity = int(parsed["quantity"])
                quantity = max(0, quantity)
                if action_str == "buy":
                    quantity = min(quantity, int(cash / price) if price > 0 else 0)
                elif action_str == "sell":
                    quantity = min(quantity, max(position, 0))
                else:
                    quantity = 0
                break
            except Exception as exc:
                logger.warning("LLM attempt %d failed: %s", attempt + 1, exc)
                last_error = exc
                if attempt == 2:
                    raise RuntimeError(
                        f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
                    ) from last_error
        if action_str == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action_str == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        rag_context = self.state.custom_state["last_rag_context"]
        order = {
            "type": "order",
            "from": self.identity,
            "action": action_str,
            "bid_price": bid_price,
            "quantity": quantity,
            "reasoning": reasoning,
            "analysis": analysis,
            "agent_type": self.__class__.__name__,
            "strategy": self.__class__.__name__,
            "rag_context": rag_context,
        }
        return {
            "action": action_str,
            "bid_price": bid_price,
            "quantity": quantity,
            "reasoning": reasoning,
            "analysis": analysis,
            "from": self.identity,
            "agent_type": self.__class__.__name__,
            "strategy": self.__class__.__name__,
            "rag_context": rag_context,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class RagLLMBeliefAnchor(RagLLMInvestor):
    """RAG-augmented belief anchor — strong prior, selectively filters confirming signals. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.ConfirmationBias.Rag.prompts:RAG_BELIEF_ANCHOR_SYS"


class RagLLMSelectiveScanner(RagLLMInvestor):
    """RAG-augmented selective scanner — seeks confirming info, ignores contradictions. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.ConfirmationBias.Rag.prompts:RAG_SELECTIVE_SCANNER_SYS"
    )


class RagLLMBalancedAnalyst(RagLLMInvestor):
    """RAG-augmented balanced analyst — Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.ConfirmationBias.Rag.prompts:RAG_BALANCED_ANALYST_SYS"
    )


class RagLLMContrarianTrader(RagLLMInvestor):
    """RAG-augmented contrarian — exploits systematic bias errors of biased traders. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = (
        "examples.ConfirmationBias.Rag.prompts:RAG_CONTRARIAN_TRADER_SYS"
    )


class RagLLMNoiseTrader(RagLLMInvestor):
    """RAG-augmented noise trader — random uninformed liquidity provider. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.ConfirmationBias.Rag.prompts:RAG_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMBeliefAnchor",
    "RagLLMSelectiveScanner",
    "RagLLMBalancedAnalyst",
    "RagLLMContrarianTrader",
    "RagLLMNoiseTrader",
]
