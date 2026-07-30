"""GFC2008 Rag — RAG-augmented LLM simulation of 2008 Global Financial Crisis dynamics."""

from __future__ import annotations

import importlib
import logging
import os
import shutil
import sys
from pathlib import Path

from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

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

from examples.GFC2008.Rule.players import Market, _build_order
from examples.GFC2008.Rag.prompts import RAG_USER_TEMPLATE

logger = logging.getLogger(__name__)

# Single source of truth for the RAG fallback sentinel; Rag/analysis.py imports from here.
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RagLLMInvestor(GeneralPlayer):
    """Base RAG-augmented LLM investor for GFC2008."""

    _system_prompt_path: str = ""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        self.state.custom_state["round"] = observation.round
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["deviation"] = 0.0

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

        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        await self._initialize_rag(rag_cfg, llm_client, llm_cfg)

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
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

        shared_rag_dirs = resolved_rag["shared_rag_index_dirs"]
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
                local_rag_dir = rag_cfg["local_index_dir"]
                if not local_rag_dir:
                    local_ws = rag_cfg["local_workspace_dir"]
                    if local_ws:
                        local_rag_dir = os.path.join(local_ws, "rag_index")
                if not local_rag_dir:
                    return
                embed_type = rag_cfg["embed_type"]
                embed_api_key = rag_cfg["embed_api_key"]
                if not embed_api_key:
                    embed_api_key = (
                        os.getenv("HUNYUAN_API_KEY", "")
                        if embed_type == "litellm"
                        else os.getenv("ARK_API_KEY", "")
                    )
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
                        logger.warning("RAG store reload failed: %s", exc)
                custom["rag_store"] = rag_store

    async def decide(self) -> dict:
        """Build RAG-augmented prompt and call LLM for trading decision."""

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price

        rag_store: Optional[KnowledgeStore] = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]
        rag_context = ""
        if rag_store and rag_store.is_built():
            query = KnowledgeQuery(
                text=(
                    f"GFC2008 financial crisis MBS leverage trading strategy "
                    f"price={price:.2f} fundamental={fundamental:.2f} deviation={deviation:+.2%}"
                ),
                top_k=rag_cfg["top_k"],
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text
        if not rag_context:
            rag_context = _RAG_FALLBACK
        self.state.custom_state["last_rag_context"] = rag_context

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

        llm_client: Optional[LangChainAPIInference] = self.state.custom_state["llm_client"]
        if llm_client is None:
            raise RuntimeError(f"[{self.identity}] LLM client not initialized")

        decision = None
        last_error = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_msg, user_msg=user_msg)
                response = llm_client.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                if decision["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"Invalid action: {decision['action']}")
                if float(decision["bid_price"]) <= 0:
                    raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
                if not str(decision["reasoning"]).strip():
                    raise ValueError("Missing reasoning")
                break
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
            )

        action = decision["action"]
        quantity = int(decision["quantity"])

        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty, 3000)
        elif action == "sell":
            quantity = min(quantity, max(position, 0), 3000)
        else:
            quantity = 0

        quantity = max(0, quantity)
        order = _build_order(
            self,
            action,
            quantity,
            float(decision["bid_price"]),
            str(decision["reasoning"]),
        )
        return {
            **order,
            "rag_context": self.state.custom_state["last_rag_context"],
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order to market."""
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class RagLLMMBSOriginator(RagLLMInvestor):
    """RAG-augmented MBSOriginator: creates structured securities with lax screening. Theory: simulation-bases.md §4.1."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_MBS_ORIGINATOR_SYS"


class RagLLMRatingAgency(RagLLMInvestor):
    """RAG-augmented RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md §4.2."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_RATING_AGENCY_SYS"


class RagLLMLeveragedInvestor(RagLLMInvestor):
    """RAG-augmented LeveragedInvestor: high leverage, forced to sell in downturn. Theory: simulation-bases.md §4.3."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_LEVERAGED_INVESTOR_SYS"


class RagLLMDistressedBuyer(RagLLMInvestor):
    """RAG-augmented DistressedBuyer: buys assets at deep discount during panic. Theory: simulation-bases.md §4.4."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_DISTRESSED_BUYER_SYS"


class RagLLMRegulator(RagLLMInvestor):
    """RAG-augmented Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md §4.5."""

    _system_prompt_path = "examples.GFC2008.Rag.prompts:RAGLLM_REGULATOR_SYS"


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMMBSOriginator",
    "RagLLMRatingAgency",
    "RagLLMLeveragedInvestor",
    "RagLLMDistressedBuyer",
    "RagLLMRegulator",
]
