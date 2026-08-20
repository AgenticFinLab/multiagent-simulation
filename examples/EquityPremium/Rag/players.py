"""EquityPremium Rag stock/bond allocation simulation."""

from __future__ import annotations

import importlib
import json
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
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.EquityPremium.LLM.players import Market
from examples.EquityPremium.decision import parse_equity_premium_decision

logger = logging.getLogger("EquityPremium.Rag")

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from a module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RagLLMInvestor(GeneralPlayer):
    """Base RAG investor for stock/bond allocation decisions."""

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

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize the API client."""
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
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            await self._initialize_agent()

        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload

    async def _initialize_agent(self) -> None:
        """Initialize portfolio and local RAG index."""
        extras = self.config.extras
        initial_cash = extras["initial_cash"]
        self.state.custom_state["cash"] = initial_cash * extras["initial_cash_ratio"]
        self.state.custom_state["stocks"] = extras["initial_stock_shares"]
        self.state.custom_state["bonds"] = initial_cash * extras["initial_bond_ratio"]

        private_knowledge = extras["private_knowledge"]
        await self._initialize_rag(private_knowledge["rag"])

    async def _initialize_rag(self, rag_cfg: Dict[str, Any]) -> None:
        """Build or load this agent's RAG index."""
        extras = self.config.extras
        record_path = extras["record_path"]
        knowledge_config = extras["knowledge"]
        resource_manager = ResourceManager(knowledge_config)
        agent_knowledge = resource_manager.resolve_agent_knowledge(
            agent_id=self.identity,
            private_knowledge=extras["private_knowledge"],
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

        embed_type = resolved_rag["embed_type"]
        embed_api_key = resolved_rag["embed_api_key"]
        if not embed_api_key:
            if embed_type == "litellm":
                embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
            elif embed_type == "openai":
                embed_api_key = os.getenv("ARK_API_KEY", "")

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
            index_files = [f for f in os.listdir(local_rag_dir) if not f.startswith(".")]
            if index_files:
                try:
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    return
                except Exception as exc:
                    logger.warning("[%s] local RAG load failed: %s", self.identity, exc)

        shared_dirs = resolved_rag["shared_rag_index_dirs"]
        if not shared_dirs and os.path.isdir(shared_rag_dir):
            shared_dirs = [shared_rag_dir]
        for shared_dir in shared_dirs:
            if not os.path.isdir(shared_dir):
                continue
            shared_files = [f for f in os.listdir(shared_dir) if not f.startswith(".")]
            if not shared_files:
                continue
            try:
                for item in shared_files:
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
            except Exception as exc:
                logger.warning("[%s] shared RAG load failed: %s", self.identity, exc)

        if not os.path.isdir(processed_dir) or not os.listdir(processed_dir):
            raise RuntimeError(
                f"[{self.identity}] No processed documents available for RAG in {processed_dir}."
            )

        docs: List[Any] = KnowledgeLoader().load_from_dir(processed_dir)
        rag_store.build(docs)

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

    def _retrieve_context(self, market_data: Dict[str, Any], stock_pct: float) -> str:
        """Retrieve equity-premium context for the current allocation state."""
        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]
        rag_context = ""
        if rag_store and rag_store.is_built():
            query = KnowledgeQuery(
                text=(
                    "equity premium puzzle myopic loss aversion allocation "
                    f"stock_return={market_data['stock_return_pct']:+.2f}% "
                    f"bond_return={market_data['bond_return_pct'] * 252:.2f}% "
                    f"stock_allocation={stock_pct:.1f}%"
                ),
                top_k=rag_cfg["top_k"],
                round_num=market_data["round"],
                agent_id=self.config.identity,
            )
            result = rag_store.query(query)
            rag_context = result.formatted_text
        if not rag_context:
            rag_context = _RAG_FALLBACK
        self.state.custom_state["last_rag_context"] = rag_context
        return rag_context

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build RAG user prompt from stock/bond market state."""
        stock_value = self.state.custom_state["stocks"] * market_data["stock_price"]
        total_value = (
            self.state.custom_state["cash"]
            + stock_value
            + self.state.custom_state["bonds"]
        )
        stock_pct = (stock_value / total_value) * 100 if total_value > 0 else 0.0
        rag_context = self._retrieve_context(market_data, stock_pct)
        llm_cfg = self.config.extras["llm"]
        template = load_prompt(llm_cfg["user_message"])
        return template.format(
            rag_context=rag_context,
            round=market_data["round"],
            stock_price=market_data["stock_price"],
            prev_stock_price=market_data["prev_stock_price"],
            stock_return_pct=market_data["stock_return_pct"],
            bond_return_pct=market_data["bond_return_pct"] * 252,
            cash=self.state.custom_state["cash"],
            stocks=self.state.custom_state["stocks"],
            bonds=self.state.custom_state["bonds"],
            stock_pct=stock_pct,
            total_value=total_value,
        )

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_prompt = self._build_prompt(market_data)
        llm_client = self._get_llm()

        decision: Optional[Dict[str, Any]] = None
        last_error = ""
        for attempt in range(3):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = parse_equity_premium_decision(
                    infer_output.outputs[0].response
                )
                break
            except ValueError as exc:
                last_error = str(exc)

        if decision is None:
            # Strict fail-fast: do NOT fabricate a hold decision. Raise so
            # the simulator surfaces the failure to the runner which halts
            # the whole round loudly.
            raise RuntimeError(
                f"[{self.identity}] LLM decision unavailable after 3 retries. "
                f"Last error: {last_error}"
            )

        stock_qty = float(decision["stock_qty"])
        price = market_data["stock_price"]
        cash = self.state.custom_state["cash"]
        stocks = self.state.custom_state["stocks"]

        if stock_qty > 0:
            stock_qty = min(stock_qty, cash / price if price > 0 else 0.0)
        else:
            stock_qty = max(stock_qty, -stocks)

        if stock_qty > 0:
            self.state.custom_state["cash"] -= stock_qty * price
            self.state.custom_state["stocks"] += stock_qty
        elif stock_qty < 0:
            self.state.custom_state["cash"] += abs(stock_qty) * price
            self.state.custom_state["stocks"] += stock_qty

        strategy_name = self.__class__.__name__
        order = {
            "stock_qty": stock_qty,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:120],
            "analysis": decision["analysis"],
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


class RagLLMMyopicLossAverse(RagLLMInvestor):
    """RAG myopic loss-averse allocator. Theory: simulation-bases.md §4.1."""


class RagLLMLongTermInvestor(RagLLMInvestor):
    """RAG long-horizon allocator. Theory: simulation-bases.md §4.2."""


class RagLLMInstitutionalInvestor(RagLLMInvestor):
    """RAG risk-neutral institutional allocator. Theory: simulation-bases.md §4.3."""


class RagLLMRiskAverseSaver(RagLLMInvestor):
    """RAG conservative saver allocator. Theory: simulation-bases.md §4.4."""


class RagLLMRationalOptimizer(RagLLMInvestor):
    """RAG noise-trader/rational benchmark allocator. Theory: simulation-bases.md §4.5."""


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMMyopicLossAverse",
    "RagLLMLongTermInvestor",
    "RagLLMInstitutionalInvestor",
    "RagLLMRiskAverseSaver",
    "RagLLMRationalOptimizer",
]
