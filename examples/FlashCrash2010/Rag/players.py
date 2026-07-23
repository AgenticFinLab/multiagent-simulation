"""FlashCrash2010 Rag - RAG-augmented Rule+LLM Flash Crash 2010 Simulation

Design:
    - Market coordinator: identical rule-based price dynamics as FlashCrash2010
    - Investors: LLM-powered with rule-embedded prompts + RAG knowledge retrieval

All parameters are configured via players.yml config file.
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
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import validate_order
from examples.FlashCrash2010.Rule.players import Market  # noqa: F401

logger = logging.getLogger("FlashCrash2010.Rag")

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def agent_type_for_strategy(strategy_name: str) -> str:
    """Map RAG class names to the market agent types used by Rule mode."""
    lowered = strategy_name.lower()
    if "hft" in lowered or "momentum" in lowered:
        return "hft"
    if "fundamental" in lowered:
        return "fundamental"
    if "stoploss" in lowered or "stop_loss" in lowered:
        return "stoploss"
    if "noise" in lowered:
        return "noise"
    return "llm"


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented Rule+LLM FlashCrash2010 investors."""

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
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def _initialize_agent(self) -> None:
        extras = self.config.extras
        record_path = extras["record_path"]
        base_path = os.path.join(record_path, self.config.identity)
        hot_limit = extras["custom_state_hot_limit"]

        self.state.custom_state["cash"] = float(extras["initial_cash"])
        self.state.custom_state["position"] = int(extras["initial_position"])
        self.state.custom_state["price_history"] = HistoryBuffer(
            folder=os.path.join(base_path, "price"),
            entry_limit=hot_limit,
        )

        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env")
        if not os.getenv("ARK_API_KEY"):
            raise RuntimeError(
                f"ARK_API_KEY not found. Ensure .env exists at {project_root / '.env'}"
            )

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
                    "output_position": rag_cfg["shared_rag_index_dir"]
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
                        "[%s] Failed to load local index (%s); will try shared",
                        self.identity,
                        exc,
                    )

        shared_rag_dirs = resolved_rag["shared_rag_index_dirs"]
        if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
            shared_rag_dirs = [shared_rag_dir]

        for s_dir in shared_rag_dirs:
            if os.path.isdir(s_dir):
                shared_index_files = [
                    f for f in os.listdir(s_dir) if not f.startswith(".")
                ]
                if shared_index_files:
                    try:
                        for item in shared_index_files:
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
                            "[%s] Failed to copy shared index (%s); will build",
                            self.identity,
                            exc,
                        )

        loader = KnowledgeLoader()
        docs: List[Any] = []
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            raise RuntimeError(
                f"[{self.identity}] No processed documents in {processed_dir}."
            )

        rag_store.build(docs)
        try:
            for item in os.listdir(local_rag_dir):
                if not item.startswith("."):
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
                            logger.warning("RAG store reload failed (%s)", exc)
                    custom["rag_store"] = rag_store

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]

        price = market_data["price"]
        price_hist = list(self.state.custom_state["price_history"])
        recent_prices = price_hist[-5:] if len(price_hist) >= 5 else price_hist

        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=(
                    f"trading strategy when: price={price:.2f}, "
                    f"return={market_data['return_pct']:+.2f}%, "
                    f"fundamental={market_data['fundamental']:.2f}"
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

        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])

        user_prompt = user_template.format(
            round=round_num,
            rag_context=rag_context,
            price=price,
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            fundamental=market_data["fundamental"],
            deviation=market_data["deviation"] * 100,
            spread=market_data["spread"],
            depth=market_data["depth"],
            volatility=market_data["volatility"],
            recent_prices=recent_prices,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            try:
                infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
                infer_output = llm_client.run([infer_input])
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except Exception as exc:
                last_error = exc
                parse_error = isinstance(exc, (ValueError, KeyError))
                retryable_api_error = is_retryable_llm_error(exc)
                if attempt < max_retries - 1 and (parse_error or retryable_api_error):
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
            logger.warning(
                "[%s] LLM failed after %d attempts: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            decision = {
                "action": "hold",
                "bid_price": price,
                "quantity": 0.0,
                "reasoning": f"LLM fallback hold after retries: {last_error}",
                "analysis": "",
                "provides_liquidity": False,
                "_skipped": True,
                "_skipped_reason": f"llm_failed_after_{max_retries}_attempts: {last_error}",
            }

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        if bid_price <= 0:
            bid_price = market_data["price"]

        if action == "buy":
            max_buy = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_buy)
        elif action == "sell":
            quantity = max(quantity, -position)

        if action == "buy":
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] += quantity

        strategy_name = self.__class__.__name__
        liquidity_field_missing = decision.get("provides_liquidity") is None
        if liquidity_field_missing:
            logger.warning(
                "[%s] LLM decision omitted provides_liquidity; using conservative false",
                self.identity,
            )

        order = {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": str(decision["reasoning"])[:120],
            "analysis": str(decision["analysis"]),
            "agent_type": agent_type_for_strategy(strategy_name),
            "provides_liquidity": bool(decision.get("provides_liquidity", False)),
            "liquidity_field_missing": liquidity_field_missing,
            "rag_context": self.state.custom_state["last_rag_context"],
        }
        # Propagate LLM-failure sentinel so downstream metrics can exclude
        # synthetic hold rounds from action-distribution statistics.
        if decision.get("_skipped"):
            order["_skipped"] = True
            order["_skipped_reason"] = decision.get(
                "_skipped_reason", "llm_failed"
            )
        validate_order(order)
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


class RagLLMHFTMarketMaker(RagLLMInvestor):
    """RAG-augmented HFT market maker — liquidity withdrawal rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.1."""


class RagLLMMomentumChaser(RagLLMInvestor):
    """RAG-augmented momentum chaser — trend-following rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.2."""


class RagLLMFundamentalTrader(RagLLMInvestor):
    """RAG-augmented fundamental trader — value deviation rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.3."""


class RagLLMStopLossTrader(RagLLMInvestor):
    """RAG-augmented stop-loss trader — trigger rules + LLM risk management + retrieved knowledge. Theory: simulation-bases.md §4.4."""


class RagLLMNoiseTrader(RagLLMInvestor):
    """RAG-augmented noise trader — random trading rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.5."""


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMHFTMarketMaker",
    "RagLLMMomentumChaser",
    "RagLLMFundamentalTrader",
    "RagLLMStopLossTrader",
    "RagLLMNoiseTrader",
]
