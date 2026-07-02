"""Volmageddon Rag Simulation

February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours trading

Design:
    - Market: Rule-based coordinator (identical to Volmageddon.Rule.Market).
    - Investors: LLM-powered with system prompts that encode persona + rules,
      plus a personal RAG library injected into each decision round.
      At initialization, each agent builds a VectorStoreIndex over reference documents.
      At each decision round, the top-k most relevant chunks are retrieved
      and injected into the user prompt via {rag_context}.

All parameters configured via players.yml.
"""

import logging
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
from masim.knowledge.manager import KnowledgeManager
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from masim.utils.llm_utils import parse_llm_quantity_response_with_thinking

from .prompts import (
    RAGLLM_EQUITY_TRADER_SYS,
    RAGLLM_LONG_VOL_HEDGER_SYS,
    RAGLLM_SHORT_VOL_TRADER_SYS,
    RAGLLM_VOL_ETN_MANAGER_SYS,
    RAGLLM_VOL_ARBITRAGEUR_SYS,
)
from ..Rule.players import Market  # noqa: F401 — re-exported

logger = logging.getLogger("Volmageddon.Rag")

# Canonical sentinel injected into `retrieved_knowledge` when the RAG store
# returns no relevant chunks for this round. Mirrors the string spelled out
# verbatim in every §4.N.5.0 I/O Contract of examples/Volmageddon/simulation-bases.md
# so a single edit here propagates to prompt drafting and downstream tests.
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented Volmageddon investors."""

    _system_prompt: str = ""
    _llm: Optional[LangChainAPIInference] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            custom.pop("rag_store", None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
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

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        if self._llm is None:
            llm_cfg = self.config.extras["llm"]
            self._llm = LangChainAPIInference(
                lm_name=llm_cfg["lm_name"],
                generation_config=llm_cfg["generation_config"],
            )
        return self._llm

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
                self.state.custom_state["price"] = market_data["price"]
                self.state.custom_state["fundamental"] = market_data["fundamental"]
                self.state.custom_state["deviation"] = market_data["deviation"]

    async def _initialize_agent(self) -> None:
        """One-time initialization: portfolio + RAG index."""
        extras = self.config.extras
        record_path = extras["record_path"]
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        llm_client = self._get_llm()
        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]
        await self._initialize_rag(rag_cfg, llm_client, extras["llm"])

    async def _initialize_rag(
        self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
    ) -> None:
        """Build or load the agent's RAG index."""
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
                    return
                except Exception as exc:
                    logger.warning(
                        "[%s] Failed to load local index (%s)", self.identity, exc
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
                            "[%s] Failed to copy shared index (%s)", self.identity, exc
                        )

        loader = KnowledgeLoader()
        docs: List[Any] = []
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

    def _build_prompt(self) -> str:
        """Build user prompt with RAG context + market state."""
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price

        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]

        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=(
                    f"volatility spike: deviation={deviation * 100:+.2f}%, "
                    f"price={price:.2f}, fundamental={fundamental:.2f}"
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

        return (
            f"Round {round_num} — Market Update\n"
            f"Retrieved Knowledge:\n{rag_context}\n\n"
            f"Current Price: ${price:.2f}  Fundamental: ${fundamental:.2f}  "
            f"Deviation: {deviation * 100:+.2f}%\n"
            f"Portfolio — Cash: ${cash:.2f}  Position: {position} shares  "
            f"Value: ${portfolio_value:.2f}\n\n"
            "Apply your decision rules, informed by retrieved knowledge, to determine action.\n"
            "Respond with <analysis>...</analysis> then <decision>...</decision> containing "
            'JSON: {"action": "buy" or "sell" or "hold", "quantity": integer, '
            '"reasoning": "brief rationale"}. Do not include any price field.'
        )

    def _parse_decision(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the Volmageddon RAG quantity-order contract."""
        decision = parse_llm_quantity_response_with_thinking(response_text)
        missing = [
            field
            for field in ("action", "quantity", "reasoning")
            if field not in decision or decision[field] is None
        ]
        if missing:
            raise ValueError(f"missing decision fields: {', '.join(missing)}")

        action = str(decision["action"]).lower()
        if action not in {"buy", "sell", "hold"}:
            raise ValueError(f"invalid action: {decision['action']!r}")

        try:
            quantity = int(float(decision["quantity"]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid quantity: {decision['quantity']!r}") from exc
        if quantity < 0:
            raise ValueError(f"negative quantity: {quantity}")

        reasoning = str(decision["reasoning"]).strip()
        if not reasoning:
            raise ValueError("empty reasoning")

        return {
            "action": action,
            "quantity": quantity,
            "reasoning": reasoning,
            "analysis": str(decision["analysis"]) if "analysis" in decision else "",
        }

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        strategy_name = self.__class__.__name__
        llm_client = self._get_llm()

        user_prompt = self._build_prompt()
        system_prompt = self._system_prompt

        max_retries = 3
        decision: Optional[Dict[str, Any]] = None
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_decision(infer_output.outputs[0].response)
                break
            except (ValueError, KeyError) as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d/%d): %s",
                        self.identity,
                        attempt + 1,
                        max_retries,
                        exc,
                    )

        if decision is None:
            logger.warning(
                "[%s] LLM parse contract failed after %d attempts: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            decision = {
                "action": "hold",
                "quantity": 0,
                "reasoning": f"fallback hold after LLM parse failure: {last_error}",
                "analysis": "",
            }
            parser_fallback = True
        else:
            parser_fallback = False

        action = decision["action"]
        quantity = int(decision["quantity"])
        reasoning = decision["reasoning"][:120]
        analysis = decision["analysis"]
        quantity = max(0, min(quantity, 5000))

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "hold":
            quantity = 0
        elif action == "buy":
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif action == "sell":
            quantity = min(quantity, int(position))
        if quantity <= 0:
            action = "hold"
            quantity = 0

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        logger.debug(
            "[%-25s] R%d (%s): action=%s qty=%d | Cash=%.2f Pos=%d",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
            "reasoning": reasoning,
            "analysis": analysis,
            "parser_fallback": parser_fallback,
            "rag_context": self.state.custom_state["last_rag_context"],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class RagLLMShortVolTrader(RagLLMInvestor):
    """RAG-augmented short volatility trader.

    Theory: simulation-bases.md §4.1
    """

    _system_prompt = RAGLLM_SHORT_VOL_TRADER_SYS


class RagLLMVolETNManager(RagLLMInvestor):
    """RAG-augmented inverse VIX ETN manager.

    Theory: simulation-bases.md §4.2
    """

    _system_prompt = RAGLLM_VOL_ETN_MANAGER_SYS


class RagLLMLongVolHedger(RagLLMInvestor):
    """RAG-augmented long volatility hedger.

    Theory: simulation-bases.md §4.3
    """

    _system_prompt = RAGLLM_LONG_VOL_HEDGER_SYS


class RagLLMVolArbitrageur(RagLLMInvestor):
    """RAG-augmented volatility arbitrageur.

    Theory: simulation-bases.md §4.4
    """

    _system_prompt = RAGLLM_VOL_ARBITRAGEUR_SYS


class RagLLMEquityTrader(RagLLMInvestor):
    """RAG-augmented equity trader.

    Theory: simulation-bases.md §4.5
    """

    _system_prompt = RAGLLM_EQUITY_TRADER_SYS


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMShortVolTrader",
    "RagLLMVolETNManager",
    "RagLLMLongVolHedger",
    "RagLLMVolArbitrageur",
    "RagLLMEquityTrader",
]
