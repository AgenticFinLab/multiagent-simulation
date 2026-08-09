"""DotComBubble Rag — RAG-augmented LLM simulation of dot-com bubble dynamics."""

from __future__ import annotations

import copy
import importlib
import logging
import math
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from filelock import FileLock


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

from examples.DotComBubble.Rule.players import Market, _build_order  # noqa: F401

logger = logging.getLogger(__name__)

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from 'module:VAR' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RagLLMInvestor(GeneralPlayer):
    """Base RAG-augmented LLM investor for DotComBubble."""

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
            folder=f"DotComBubble/Rag/{self.__class__.__name__}", entry_limit=200
        )
        project_root = Path(__file__).resolve().parents[3]
        load_dotenv(project_root / ".env")
        llm_cfg = extras["llm"]
        lm_name = llm_cfg["lm_name"]
        generation_config = llm_cfg["generation_config"]
        self.state.custom_state["lm_name"] = lm_name
        self.state.custom_state["generation_config"] = generation_config
        self.state.custom_state["system_prompt_path"] = llm_cfg["sys_message"]
        self.state.custom_state["user_prompt_path"] = llm_cfg["user_message"]
        llm_client = LangChainAPIInference(
            lm_name=lm_name, generation_config=generation_config
        )
        self.state.custom_state["llm_client"] = llm_client
        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        await self._initialize_rag(rag_cfg)

    async def _initialize_rag(self, rag_cfg: Dict[str, Any]) -> None:
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
                except Exception as exc:  # pylint: disable=broad-except
                    logger.warning(
                        "[%s] Local index load failed: %s", self.identity, exc
                    )
        shared_rag_dirs = resolved_rag["shared_rag_index_dirs"]
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]
        os.makedirs(record_path, exist_ok=True)
        lock_name = f".{Path(shared_rag_dir).name}.lock"
        lock_path = os.path.join(record_path, lock_name)
        with FileLock(lock_path, timeout=900):
            for s_dir in shared_rag_dirs:
                if os.path.isdir(s_dir):
                    shared_files = [
                        item
                        for item in os.listdir(s_dir)
                        if not item.startswith(".")
                    ]
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
                        except Exception as exc:  # pylint: disable=broad-except
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
            os.makedirs(shared_rag_dir, exist_ok=True)
            for item in os.listdir(local_rag_dir):
                if item.startswith("."):
                    continue
                src = os.path.join(local_rag_dir, item)
                dst = os.path.join(shared_rag_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    def __getstate__(self) -> Dict:
        state = self.__dict__.copy()
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = dict(self.state.custom_state)
            for key in ("llm_client", "rag_store"):
                custom.pop(key, None)
            player_state = copy.copy(self.state)
            player_state.custom_state = custom
            state["state"] = player_state
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
                    raise ValueError("RAG local_index_dir must not be empty")
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
                    except Exception as exc:  # pylint: disable=broad-except
                        logger.warning("RAG store reload failed: %s", exc)
                custom["rag_store"] = rag_store

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        deviation = market_data["deviation"]
        portfolio_value = cash + position * price
        rag_store: Optional[KnowledgeStore] = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=(
                    f"dot-com bubble trading: price={price:.2f}, "
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
        template = load_prompt(self.state.custom_state["user_prompt_path"])
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
        if price <= 0:
            raise ValueError(f"[{self.identity}] Market price must be positive")
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        system_prompt = load_prompt(self.state.custom_state["system_prompt_path"])
        user_prompt = self._build_prompt(market_data)
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        decision = None
        last_error = None
        for attempt in range(3):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                result = llm_client.run([infer_input])
                decision = parse_llm_response_with_thinking(result.outputs[0].response)
                if decision["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"Invalid action: {decision['action']}")
                proposed_price = float(decision["bid_price"])
                proposed_quantity = float(decision["quantity"])
                if not math.isfinite(proposed_price) or proposed_price <= 0:
                    raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
                if not math.isfinite(proposed_quantity) or proposed_quantity < 0:
                    raise ValueError(f"Invalid quantity: {decision['quantity']}")
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

        action_str = decision["action"]
        quantity = max(0, int(decision["quantity"]))
        if action_str == "buy":
            quantity = min(quantity, int(cash / price))
        elif action_str == "sell":
            quantity = min(quantity, max(position, 0))
        if action_str == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action_str == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = _build_order(
            self,
            action_str,
            quantity,
            float(decision["bid_price"]),
            str(decision["reasoning"]),
        )
        order["analysis"] = str(decision["analysis"])
        rag_context = self.state.custom_state["last_rag_context"]
        return {
            **order,
            "rag_context": rag_context,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class RagLLMNewEconomyEvangelist(RagLLMInvestor):
    """Narrative buyer augmented with historical bubble context.

    Theory: ``simulation-bases.md §4.1``.
    """



class RagLLMIPOFlipper(RagLLMInvestor):
    """Short-term flipper augmented with historical IPO knowledge.

    Theory: ``simulation-bases.md §4.2``.
    """



class RagLLMMomentumFollower(RagLLMInvestor):
    """Trend amplifier augmented with historical momentum research.

    Theory: ``simulation-bases.md §4.3``.
    """



class RagLLMSkepticalValueInvestor(RagLLMInvestor):
    """Fundamental investor augmented with historical crash knowledge.

    Theory: ``simulation-bases.md §4.4``.
    """



class RagLLMShortSeller(RagLLMInvestor):
    """Short seller augmented with limits-to-arbitrage knowledge.

    Theory: ``simulation-bases.md §4.5``.
    """



__all__ = [
    "Market",
    "_RAG_FALLBACK",
    "RagLLMInvestor",
    "RagLLMNewEconomyEvangelist",
    "RagLLMIPOFlipper",
    "RagLLMMomentumFollower",
    "RagLLMSkepticalValueInvestor",
    "RagLLMShortSeller",
]
