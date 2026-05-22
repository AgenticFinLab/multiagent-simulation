"""OverconfidenceBias Rag Players - RAG-augmented overconfidence simulation.

Design:
    - Market: Rule-based (same as Rule variant)
    - Investors: LLM-powered with system prompts embedding rules + RAG context
"""

import logging
import math
import os
import shutil
from typing import Any, Dict, List, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from .prompts import (
    RULELLM_OVERCONFIDENT_TRADER_SYS,
    RULELLM_SELF_ATTRIBUTOR_SYS,
    RULELLM_CALIBRATED_TRADER_SYS,
    RULELLM_CONTRARIAN_INVESTOR_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RAG_USER_TEMPLATE,
)
from examples.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking
from examples.OverconfidenceBias.Rule.players import (  # noqa: F401
    Market,
    _build_order,
    _require_positive,
)

logger = logging.getLogger("OverconfidenceBias.Rag")


_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def safe_max_affordable(cash: float, price: float) -> int:
    """Return a finite affordable quantity for API-driven portfolio updates."""
    if not math.isfinite(cash) or not math.isfinite(price) or price <= 0:
        return 0
    return max(0, int(cash / price))


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate the shared overconfidence RAG decision contract."""
    action = decision["action"]
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"[{identity}] invalid action: {action}")
    bid_price = float(decision["bid_price"])
    _require_positive(bid_price, "bid_price")
    quantity = int(decision["quantity"])
    if quantity < 0:
        raise ValueError(f"[{identity}] quantity must be non-negative, got {quantity}")
    return {
        "action": action,
        "bid_price": bid_price,
        "quantity": quantity,
        "reasoning": decision["reasoning"],
        "analysis": decision["analysis"],
    }


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented overconfidence investors.

    Theoretical basis: simulation-bases.md §4.
    Strategy specification: RuleLLM prompts plus retrieved knowledge map to
        simulation-bases.md §4.
    Parameters: simulation-bases.md §6.
    """

    _system_prompt: str = ""

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
                payload = inb.payload
                if payload["type"] == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        """One-time initialization: LLM client + RAG index."""
        extras = self.config.extras
        record_path = extras["record_path"]

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]

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
        await self._initialize_rag(rag_cfg, llm_client, llm_config)

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        """Build or load the agent's RAG index."""
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
                "rag": {
                    "output_position": "rag_index",
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
                    return
                except Exception as exc:  # pylint: disable=broad-except
                    logger.warning(
                        "[%s] Failed to load local index: %s", self.identity, exc
                    )

        shared_rag_dirs = resolved_rag.get("shared_rag_index_dirs", [])
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]

        for shared_dir in shared_rag_dirs:
            if not os.path.isdir(shared_dir):
                continue
            shared_index_files = [
                f for f in os.listdir(shared_dir) if not f.startswith(".")
            ]
            if shared_index_files:
                try:
                    for item in shared_index_files:
                        src = os.path.join(shared_dir, item)
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
                        "[%s] Failed to copy shared index: %s", self.identity, exc
                    )

        loader = KnowledgeLoader()
        docs: List[Any] = []
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            logger.error(
                "[%s] No processed documents found in %s.", self.identity, processed_dir
            )
            raise RuntimeError(f"[{self.identity}] No documents available for RAG.")

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
            logger.warning("[%s] Failed to copy shared index: %s", self.identity, exc)
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
                local_rag_dir = rag_cfg["local_index_dir"]
                if not local_rag_dir:
                    local_workspace_dir = rag_cfg["local_workspace_dir"]
                    if local_workspace_dir:
                        local_rag_dir = os.path.join(local_workspace_dir, "rag_index")
                if local_rag_dir:
                    embed_api_key = rag_cfg["embed_api_key"]
                    if not embed_api_key:
                        embed_type = rag_cfg["embed_type"]
                        if embed_type == "litellm":
                            embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
                        elif embed_type == "openai":
                            embed_api_key = os.getenv("ARK_API_KEY", "")
                    rag_store = KnowledgeStore(
                        embed_model_name=rag_cfg["embed_model"],
                        embed_api_key=embed_api_key,
                        embed_api_base=rag_cfg["embed_api_base"],
                        embed_type=rag_cfg["embed_type"],
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

    def _build_prompt(self, rag_context: str = "") -> str:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        return RAG_USER_TEMPLATE.format(
            rag_context=rag_context or _RAG_FALLBACK,
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        _require_positive(price, "price")
        strategy_name = self.__class__.__name__
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]

        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=f"overconfidence trading strategy price={price:.2f}",
                top_k=top_k,
                round_num=round_num,
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text
        if not rag_context:
            rag_context = _RAG_FALLBACK
        self.state.custom_state["last_rag_context"] = rag_context

        user_prompt = self._build_prompt(rag_context)

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(
                system_msg=self._system_prompt, user_msg=user_prompt
            )
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
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM call/parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM decision contract failed after "
                f"{max_retries} retries: {last_error}"
            )

        action = decision["action"]
        quantity = int(decision["quantity"])
        bid_price = float(decision["bid_price"])
        _require_positive(bid_price, "bid_price")

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy" and quantity > 0:
            max_affordable = safe_max_affordable(cash, price)
            quantity = min(quantity, max_affordable)
            if quantity > 0:
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(int(position), 0))
            if quantity > 0:
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity
        else:
            quantity = 0
            action = "hold"

        logger.debug(
            "[%-20s] R%d (%-20s): %s Q=%d",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
        )

        order = _build_order(
            self,
            action,
            quantity,
            bid_price,
            str(decision["reasoning"]),
        )
        order["analysis"] = str(decision["analysis"])
        order["strategy"] = strategy_name
        order["rag_context"] = self.state.custom_state["last_rag_context"]
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


class RagLLMOverconfidentTrader(RagLLMInvestor):
    """RAG-augmented OverconfidentTrader.

    Theoretical basis: simulation-bases.md §4.1 — OverconfidentTrader.
    Strategy specification: simulation-bases.md §4.1.4.
    """

    _system_prompt = RULELLM_OVERCONFIDENT_TRADER_SYS


class RagLLMSelfAttributor(RagLLMInvestor):
    """RAG-augmented SelfAttributor.

    Theoretical basis: simulation-bases.md §4.2 — SelfAttributor.
    Strategy specification: simulation-bases.md §4.2.4.
    """

    _system_prompt = RULELLM_SELF_ATTRIBUTOR_SYS


class RagLLMCalibratedTrader(RagLLMInvestor):
    """RAG-augmented CalibratedTrader.

    Theoretical basis: simulation-bases.md §4.3 — CalibratedTrader.
    Strategy specification: simulation-bases.md §4.3.4.
    """

    _system_prompt = RULELLM_CALIBRATED_TRADER_SYS


class RagLLMContrarianInvestor(RagLLMInvestor):
    """RAG-augmented ContrarianInvestor.

    Theoretical basis: simulation-bases.md §4.4 — ContrarianInvestor.
    Strategy specification: simulation-bases.md §4.4.4.
    """

    _system_prompt = RULELLM_CONTRARIAN_INVESTOR_SYS


class RagLLMNoiseTrader(RagLLMInvestor):
    """RAG-augmented NoiseTrader.

    Theoretical basis: simulation-bases.md §4.5 — NoiseTrader.
    Strategy specification: simulation-bases.md §4.5.4.
    """

    _system_prompt = RULELLM_NOISE_TRADER_SYS


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMOverconfidentTrader",
    "RagLLMSelfAttributor",
    "RagLLMCalibratedTrader",
    "RagLLMContrarianInvestor",
    "RagLLMNoiseTrader",
]
