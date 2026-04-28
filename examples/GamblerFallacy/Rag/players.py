"""GamblerFallacy Rag — RAG-augmented LLM simulation of gambler's fallacy trading dynamics."""

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

from examples.llm_utils import parse_llm_response_with_thinking
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.GamblerFallacy.Rule.players import Market

logger = logging.getLogger(__name__)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RagLLMInvestor(GeneralPlayer):
    """Base RAG-augmented LLM investor for GamblerFallacy."""

    _system_prompt_path: str = ""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        self.state.custom_state["round"] = observation.round
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]

        project_root = Path(__file__).parent.parent.parent
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

        private_knowledge = extras.get("private_knowledge", {})
        rag_cfg = private_knowledge.get("rag", extras.get("rag", {}))
        await self._initialize_rag(rag_cfg, llm_client, llm_cfg)

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        extras = self.config.extras
        record_path = extras.get("record_path", "EXPERIMENT")

        knowledge_config = extras.get("knowledge", {})
        if not knowledge_config:
            knowledge_config = {
                "backend": "local",
                "global_uri": rag_cfg.get("docs_dir", "examples/document-sources"),
                "preprocessing": {
                    "parser": "mineru",
                    "output_position": rag_cfg.get(
                        "mineru_output_dir", "MinerU_processed"
                    ),
                },
                "rag": {
                    "output_position": rag_cfg.get("shared_rag_index_dir", "rag_index"),
                },
            }

        resource_manager = ResourceManager(knowledge_config)
        private_knowledge = extras.get("private_knowledge", {})
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

        embed_type = resolved_rag.get("embed_type", "litellm")
        embed_api_key = resolved_rag.get("embed_api_key", "")
        if not embed_api_key:
            embed_api_key = (
                os.getenv("HUNYUAN_API_KEY", "")
                if embed_type == "litellm"
                else os.getenv("ARK_API_KEY", "")
            )
        rag_store = KnowledgeStore(
            embed_model_name=resolved_rag.get(
                "embed_model", "openai/hunyuan-embedding"
            ),
            embed_api_key=embed_api_key,
            embed_api_base=resolved_rag.get("embed_api_base", ""),
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=int(resolved_rag.get("chunk_size", 512)),
            chunk_overlap=int(resolved_rag.get("chunk_overlap", 64)),
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

        shared_rag_dirs = resolved_rag.get("shared_rag_index_dirs", [])
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
                f"[{self.identity}] No processed documents in {processed_dir}. "
                "Ensure ResourceManager pre-processed documents during simulation setup."
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
                local_rag_dir = rag_cfg.get("local_index_dir", "")
                if not local_rag_dir:
                    local_ws = rag_cfg.get("local_workspace_dir", "")
                    if local_ws:
                        local_rag_dir = os.path.join(local_ws, "rag_index")
                if not local_rag_dir:
                    return
                embed_type = rag_cfg.get("embed_type", "litellm")
                embed_api_key = rag_cfg.get("embed_api_key", "")
                if not embed_api_key:
                    embed_api_key = (
                        os.getenv("HUNYUAN_API_KEY", "")
                        if embed_type == "litellm"
                        else os.getenv("ARK_API_KEY", "")
                    )
                rag_store = KnowledgeStore(
                    embed_model_name=rag_cfg.get(
                        "embed_model", "openai/hunyuan-embedding"
                    ),
                    embed_api_key=embed_api_key,
                    embed_api_base=rag_cfg.get("embed_api_base", ""),
                    embed_type=embed_type,
                    persist_dir=local_rag_dir,
                    chunk_size=int(rag_cfg.get("chunk_size", 512)),
                    chunk_overlap=int(rag_cfg.get("chunk_overlap", 64)),
                )
                if os.path.isdir(local_rag_dir):
                    try:
                        rag_store.load(local_rag_dir)
                    except Exception as exc:
                        logger.warning("RAG store reload failed: %s", exc)
                custom["rag_store"] = rag_store

    def _build_prompt(self) -> str:
        from examples.GamblerFallacy.Rag.prompts import RAG_USER_TEMPLATE

        price = self.state.custom_state.get("price", 0.0)
        fundamental = self.state.custom_state.get("fundamental", 0.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price

        rag_store: Optional[KnowledgeStore] = self.state.custom_state.get("rag_store")
        rag_cfg: Dict[str, Any] = self.state.custom_state.get("rag_cfg", {})
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg.get("top_k", 3)
            query = KnowledgeQuery(
                text=(
                    f"gambler fallacy streak reversal trading strategy "
                    f"price={price:.2f} deviation={deviation:+.2%}"
                ),
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text
        if not rag_context:
            rag_context = "(No relevant knowledge retrieved this round.)"

        return RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
            round=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
        )

    async def decide(self) -> Dict[str, Any]:
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        system_prompt = load_prompt(self._system_prompt_path)
        user_prompt = self._build_prompt()

        price = self.state.custom_state.get("price", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        decision = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                infer_output = llm_client.run([infer_input])
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except Exception as exc:
                logger.warning(
                    "[%s] LLM attempt %d failed: %s", self.identity, attempt + 1, exc
                )
                if attempt == 2:
                    decision = None

        if decision is None:
            return {
                "action": "hold",
                "quantity": 0,
                "outbound_messages": [
                    {
                        "payload": {"type": "order", "action": "hold", "quantity": 0},
                        "content_type": "order",
                    }
                ],
            }

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))

        if action == "buy" and price > 0:
            quantity = min(quantity, int(cash / price), 1000)
        elif action == "sell":
            quantity = min(quantity, max(position, 0), 1000)
        else:
            quantity = 0
        quantity = max(0, quantity)

        if action in ("buy", "sell") and quantity > 0:
            if action == "buy":
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
            else:
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity

        order = {"type": "order", "action": action, "quantity": quantity}
        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        order = {
            "type": "order",
            "action": decision_payload["action"],
            "quantity": decision_payload["quantity"],
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RagLLMStreakReversalTrader(RagLLMInvestor):
    """RagLLM-driven streak reversal trader: expects reversals after consecutive moves. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = (
        "examples.GamblerFallacy.Rag.prompts:RAGLLM_STREAK_REVERSAL_TRADER_SYS"
    )


class RagLLMHotHandTrader(RagLLMInvestor):
    """RagLLM-driven hot hand trader: believes in streak continuation. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = (
        "examples.GamblerFallacy.Rag.prompts:RAGLLM_HOT_HAND_TRADER_SYS"
    )


class RagLLMIndependentAssessor(RagLLMInvestor):
    """RagLLM-driven independent assessor: ignores streak patterns, trades on fundamentals. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = (
        "examples.GamblerFallacy.Rag.prompts:RAGLLM_INDEPENDENT_ASSESSOR_SYS"
    )


class RagLLMArbitrageur(RagLLMInvestor):
    """RagLLM-driven arbitrageur: exploits gambler's fallacy mispricing. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.GamblerFallacy.Rag.prompts:RAGLLM_ARBITRAGEUR_SYS"


class RagLLMNoiseTrader(RagLLMInvestor):
    """RagLLM-driven uninformed noise trader. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.GamblerFallacy.Rag.prompts:RAGLLM_NOISE_TRADER_SYS"


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMStreakReversalTrader",
    "RagLLMHotHandTrader",
    "RagLLMIndependentAssessor",
    "RagLLMArbitrageur",
    "RagLLMNoiseTrader",
]
