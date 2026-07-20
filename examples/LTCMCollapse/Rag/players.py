"""LTCMCollapse Rag Variant Players."""

import logging
import os
import shutil
from typing import Any, Dict, List

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.player.base import Action
from masim.player.general import GeneralPlayer

from examples.LTCMCollapse.Rag.prompts import (
    RAG_CENTRALBANK_PROMPT,
    RAG_CONVERGENCEARBITRAGEUR_PROMPT,
    RAG_LEVERAGETRADER_PROMPT,
    RAG_LIQUIDITYPROVIDER_PROMPT,
    RAG_RISKMANAGER_PROMPT,
    RAG_USER_TEMPLATE,
    RAG_FALLBACK,
)
from examples.LTCMCollapse.Rule.players import (  # noqa: F401
    Market,
    _build_order,
    _require_positive,
)
from masim.utils.llm_utils import is_retryable_llm_error, parse_llm_response_with_thinking

logger = logging.getLogger("LTCMCollapse.Rag")

_RAG_FALLBACK = RAG_FALLBACK


def _validate_decision(decision: Dict[str, Any], identity: str) -> Dict[str, Any]:
    """Validate the shared LTCM RAG decision contract."""
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
    """Base class for RAG-augmented LTCMCollapse investors.

    Theory: simulation-bases.md §4.
    Strategy specification: RuleLLM prompts plus retrieved knowledge map to
    simulation-bases.md §4.
    """

    _system_prompt = ""

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
                            embed_api_key = os.getenv("HUNYUAN_API_KEY")
                        elif embed_type == "openai":
                            embed_api_key = os.getenv("ARK_API_KEY")
                    if not embed_api_key:
                        raise RuntimeError(
                            f"[{self.identity}] missing embedding API key during RAG restore"
                        )
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

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()
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
        rag_cfg = extras["rag"] if "rag" in extras else private_knowledge["rag"]
        await self._initialize_rag(rag_cfg)

    async def _initialize_rag(self, rag_cfg: Dict[str, Any]) -> None:
        extras = self.config.extras
        record_path = extras["record_path"]
        knowledge_config = extras["knowledge"]
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
        private_knowledge = dict(extras["private_knowledge"])
        if "rag" not in private_knowledge:
            private_knowledge["rag"] = rag_cfg
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
        os.makedirs(shared_rag_dir, exist_ok=True)

        embed_api_key = resolved_rag["embed_api_key"]
        if not embed_api_key:
            embed_type = resolved_rag["embed_type"]
            if embed_type == "litellm":
                embed_api_key = os.getenv("HUNYUAN_API_KEY")
            elif embed_type == "openai":
                embed_api_key = os.getenv("ARK_API_KEY")
        if not embed_api_key:
            raise RuntimeError(
                f"[{self.identity}] missing embedding API key for {resolved_rag['embed_type']}"
            )

        rag_store = KnowledgeStore(
            embed_model_name=resolved_rag["embed_model"],
            embed_api_key=embed_api_key,
            embed_api_base=resolved_rag["embed_api_base"],
            embed_type=resolved_rag["embed_type"],
            persist_dir=local_rag_dir,
            chunk_size=int(resolved_rag["chunk_size"]),
            chunk_overlap=int(resolved_rag["chunk_overlap"]),
        )

        if os.path.isdir(local_rag_dir):
            index_files = [f for f in os.listdir(local_rag_dir) if not f.startswith(".")]
            if index_files:
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    return
                except Exception as exc:  # pylint: disable=broad-except
                    logger.warning("[%s] Failed to load local index: %s", self.identity, exc)

        shared_rag_dirs = resolved_rag.get("shared_rag_index_dirs", [])
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]
        for shared_dir in shared_rag_dirs:
            if not os.path.isdir(shared_dir):
                continue
            shared_index_files = [f for f in os.listdir(shared_dir) if not f.startswith(".")]
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
                    logger.warning("[%s] Failed to copy shared index: %s", self.identity, exc)

        loader = KnowledgeLoader()
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs: List[Any] = loader.load_from_dir(processed_dir)
        else:
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

    def _formulate_knowledge_query(self) -> KnowledgeQuery:
        """Build a round-specific retrieval query from mandatory market state."""
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        round_num = self.state.custom_state["round"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]
        return KnowledgeQuery(
            text=(
                "convergence arbitrage leverage liquidity crisis "
                f"price={price:.2f} fundamental={fundamental:.2f} "
                f"deviation={deviation:+.2%}"
            ),
            top_k=rag_cfg["top_k"],
            round_num=round_num,
            agent_id=self.config.identity,
        )

    def _get_rag_context(self) -> str:
        """Retrieve context or return the exact auditable empty-result sentinel."""
        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        if rag_store and rag_store.is_built():
            result = rag_store.query(self._formulate_knowledge_query())
            if result.formatted_text:
                return result.formatted_text
        return _RAG_FALLBACK

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        _require_positive(price, "price")
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        initial_price = self.config.extras["initial_price"]
        initial_position = self.config.extras["initial_position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price
        rag_context = self._get_rag_context()
        self.state.custom_state["last_rag_context"] = rag_context
        user_msg = RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            initial_price=initial_price,
            initial_position=initial_position,
            portfolio_value=portfolio_value,
        )
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        infer_input = InferInput(system_msg=self._system_prompt, user_msg=user_msg)
        decision = None
        last_error = None
        for attempt in range(3):
            try:
                response = llm_client.run([infer_input]).outputs[0].response
                decision = parse_llm_response_with_thinking(response)
                decision = _validate_decision(decision, self.identity)
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < 2 and (parse_error or retryable_api_error):
                    logger.debug(
                        "[%s] LLM call/parse failed (attempt %d), retrying: %s",
                        self.identity,
                        attempt + 1,
                        exc,
                    )
                    continue
                if not parse_error and not retryable_api_error:
                    raise

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM decision contract failed after 3 retries: {last_error}"
            )
        return decision

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = int(decision_payload["quantity"])
        bid_price = float(decision_payload["bid_price"])
        price = self.state.custom_state["price"]
        _require_positive(price, "price")
        _require_positive(bid_price, "bid_price")
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy" and quantity > 0:
            quantity = min(quantity, int(cash / price))
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(position, 0))
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        else:
            quantity = 0
        order = _build_order(
            self,
            action,
            quantity,
            bid_price,
            str(decision_payload["reasoning"]),
        )
        order["analysis"] = str(decision_payload["analysis"])
        order["rag_context"] = self.state.custom_state["last_rag_context"]
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RagLLMConvergenceArbitrageur(RagLLMInvestor):
    """RAG leveraged spread convergence trader. Theory: simulation-bases.md §4.1."""

    _system_prompt = RAG_CONVERGENCEARBITRAGEUR_PROMPT


class RagLLMLeverageTrader(RagLLMInvestor):
    """RAG margin-pressure deleveraging trader. Theory: simulation-bases.md §4.2."""

    _system_prompt = RAG_LEVERAGETRADER_PROMPT


class RagLLMRiskManager(RagLLMInvestor):
    """RAG VaR-based position cutter. Theory: simulation-bases.md §4.3."""

    _system_prompt = RAG_RISKMANAGER_PROMPT


class RagLLMLiquidityProvider(RagLLMInvestor):
    """RAG stress-sensitive liquidity provider. Theory: simulation-bases.md §4.4."""

    _system_prompt = RAG_LIQUIDITYPROVIDER_PROMPT


class RagLLMCentralBank(RagLLMInvestor):
    """RAG lender-of-last-resort intervention agent. Theory: simulation-bases.md §4.5."""

    _system_prompt = RAG_CENTRALBANK_PROMPT


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMConvergenceArbitrageur",
    "RagLLMLeverageTrader",
    "RagLLMRiskManager",
    "RagLLMLiquidityProvider",
    "RagLLMCentralBank",
]
