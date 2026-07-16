"""LossAversion Rag Simulation

Loss aversion from prospect theory causes investors to hold losers too long
and sell winners too early.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: RAG-augmented LLM with rule-embedded prompts and retrieved knowledge

All parameters are configured via players.yml config file.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.knowledge.manager import KnowledgeManager
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.utils.llm_utils import parse_llm_response_with_thinking
from examples.LossAversion.RuleLLM.prompts import (
    RULELLM_LOSS_AVERSE_PROMPT,
    RULELLM_BREAK_EVEN_PROMPT,
    RULELLM_RATIONAL_PROMPT,
    RULELLM_MOMENTUM_PROMPT,
    RULELLM_MARKET_MAKER_PROMPT,
)
from examples.LossAversion.RuleLLM.players import _rule_decision
from examples.LossAversion.Rag.prompts import RAG_USER_TEMPLATE
from examples.LossAversion.Rule.players import Market  # noqa: F401

logger = logging.getLogger("LossAversion.Rag")
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def _decision_parameters_text(extras: Dict[str, Any], agent_class: str) -> str:
    """Format required Rule-variant parameters for prompt grounding."""
    parameter_keys = {
        "RagLLMLossAverseInvestor": (
            "loss_aversion_lambda",
            "sell_gain_threshold",
            "gain_sell_fraction",
            "loss_sell_fraction",
            "base_size",
        ),
        "RagLLMBreakEvenTrader": (
            "risk_increase_factor", "loss_trigger", "sizing_scale", "base_size",
        ),
        "RagLLMRationalTrader": (
            "risk_aversion", "deviation_threshold", "sizing_scale", "base_size",
        ),
        "RagLLMMomentumTrader": ("entry_threshold", "sizing_scale", "base_size"),
        "RagLLMMarketMaker": ("inventory_limit", "base_size"),
    }
    keys = parameter_keys[agent_class] + ("quantity_tolerance",)
    return "\n".join(f"- {key}: {extras[key]}" for key in keys)


def _validate_decision(decision: Dict[str, Any]) -> None:
    """Validate the canonical trading decision contract."""
    if decision["action"] not in ("buy", "sell", "hold"):
        raise ValueError(f"Invalid action: {decision['action']}")
    if float(decision["bid_price"]) <= 0:
        raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
    if int(decision["quantity"]) < 0:
        raise ValueError(f"Invalid quantity: {decision['quantity']}")
    if not str(decision["reasoning"]).strip():
        raise ValueError("Missing reasoning")


class RagLLMInvestor(GeneralPlayer):
    """Base class for RAG-augmented investors in LossAversion simulation.

    Combines rule-embedded system prompts with retrieved knowledge context.
    """

    _system_prompt: str = ""

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
                payload = inb.payload if hasattr(inb, "payload") else inb
                if isinstance(payload, dict) and payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    async def _initialize_agent(self) -> None:
        """One-time initialization: portfolio state + LLM client + RAG index."""
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["entry_price"] = extras["initial_price"]

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

        await self._initialize_rag(extras, llm_client)

    async def _initialize_rag(self, extras: Dict[str, Any], llm_client: Any) -> None:
        """Build or load the agent RAG index."""
        record_path = extras["record_path"]
        knowledge_config = extras["knowledge"]
        private_knowledge = extras["private_knowledge"]
        rag_cfg = private_knowledge["rag"]

        resource_manager = ResourceManager(
            knowledge_config
            or {
                "backend": "local",
                "global_uri": rag_cfg["docs_dir"],
                "rag": {
                    "output_position": rag_cfg["shared_rag_index_dir"]
                },
            }
        )

        agent_knowledge = resource_manager.resolve_agent_knowledge(
            agent_id=self.identity,
            private_knowledge=private_knowledge
            or {
                "from_global_resources": [],
                "local_resources": {"local_uri": "", "local_resources": []},
                "rag": rag_cfg,
            },
            record_path=record_path,
        )

        local_rag_dir = agent_knowledge["local_rag_dir"]
        processed_dir = agent_knowledge["processed_dir"]
        shared_rag_dir = agent_knowledge["shared_rag_dir"]
        resolved_rag = agent_knowledge["rag"]

        os.makedirs(local_rag_dir, exist_ok=True)

        embed_type = resolved_rag["embed_type"]
        embed_model = resolved_rag["embed_model"]
        embed_api_base = resolved_rag["embed_api_base"]
        embed_api_key = resolved_rag["embed_api_key"]
        if not embed_api_key:
            embed_api_key = os.getenv(
                "HUNYUAN_API_KEY" if embed_type == "litellm" else "ARK_API_KEY", ""
            )

        rag_store = KnowledgeStore(
            embed_model_name=embed_model,
            embed_api_key=embed_api_key,
            embed_api_base=embed_api_base,
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=int(resolved_rag["chunk_size"]),
            chunk_overlap=int(resolved_rag["chunk_overlap"]),
        )

        # Try loading existing index
        if os.path.isdir(local_rag_dir) and os.listdir(local_rag_dir):
            try:
                rag_store.load(local_rag_dir)
                self.state.custom_state["rag_store"] = rag_store
                self.state.custom_state["rag_cfg"] = resolved_rag
                return
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to load local index (%s)", self.identity, exc
                )

        # Build from processed documents
        loader = KnowledgeLoader()
        docs: List[Any] = []
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            logger.warning(
                "[%s] No processed documents in %s; RAG unavailable.",
                self.identity,
                processed_dir,
            )
            self.state.custom_state["rag_store"] = None
            self.state.custom_state["rag_cfg"] = resolved_rag
            return

        rag_store.build(docs)
        self.state.custom_state["rag_store"] = rag_store
        self.state.custom_state["rag_cfg"] = resolved_rag

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]

        llm_client: LangChainAPIInference = self.state.custom_state["llm_client"]
        rag_store: KnowledgeStore = self.state.custom_state["rag_store"]
        rag_cfg: Dict[str, Any] = self.state.custom_state["rag_cfg"]

        # Retrieve RAG context
        rag_context = ""
        if rag_store and rag_store.is_built():
            top_k = rag_cfg["top_k"]
            query = KnowledgeQuery(
                text=(
                    f"loss aversion trading strategy when: "
                    f"price={price:.2f}, fundamental={fundamental:.2f}, "
                    f"deviation={deviation*100:+.2f}%"
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

        user_msg = RAG_USER_TEMPLATE.format(
            rag_context=rag_context,
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            entry_price=self.state.custom_state["entry_price"],
            portfolio_value=cash + position * price,
            decision_parameters=_decision_parameters_text(
                self.config.extras,
                self.__class__.__name__,
            ),
        )

        decision = None
        last_error = None
        for attempt in range(3):
            try:
                output = llm_client.run(
                    [InferInput(system_msg=self._system_prompt, user_msg=user_msg)]
                )
                decision = parse_llm_response_with_thinking(output.outputs[0].response)
                _validate_decision(decision)
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

        rule_class = self.__class__.__name__.replace("RagLLM", "RuleLLM")
        rule_action, rule_quantity = _rule_decision(
            rule_class, self.config.extras, price, fundamental, cash, position,
            self.state.custom_state["entry_price"],
        )
        if self.__class__.__name__ == "RagLLMLossAverseInvestor":
            if "last_realization_domain" not in self.state.custom_state:
                self.state.custom_state["last_realization_domain"] = None
            pnl = (price - self.state.custom_state["entry_price"]) / self.state.custom_state["entry_price"]
            active_domain = None
            if pnl > self.config.extras["sell_gain_threshold"]:
                active_domain = "gain"
            elif pnl < -self.config.extras["sell_gain_threshold"] * self.config.extras["loss_aversion_lambda"]:
                active_domain = "loss"
            if active_domain is None:
                self.state.custom_state["last_realization_domain"] = None
            elif self.state.custom_state["last_realization_domain"] == active_domain:
                rule_action, rule_quantity = "hold", 0
            elif rule_action == "sell":
                self.state.custom_state["last_realization_domain"] = active_domain
        action = rule_action
        if rule_action == "hold" or rule_quantity <= 0:
            quantity = 0
        else:
            tolerance = float(self.config.extras["quantity_tolerance"])
            lower = max(1, int(rule_quantity * (1 - tolerance)))
            upper = max(lower, int(rule_quantity * (1 + tolerance)))
            quantity = min(max(quantity, lower), upper, int(self.config.extras["base_size"]))

        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
            if self.__class__.__name__ == "RagLLMMarketMaker":
                quantity = min(
                    quantity,
                    max(int(self.config.extras["inventory_limit"]) - position, 0),
                )
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
        else:
            quantity = 0

        if action == "buy" and quantity > 0:
            old_position = self.state.custom_state["position"]
            old_entry = self.state.custom_state["entry_price"]
            new_position = old_position + quantity
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] = new_position
            self.state.custom_state["entry_price"] = (
                old_entry * old_position + price * quantity
            ) / new_position
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision["reasoning"][:120],
            "rag_context": self.state.custom_state["last_rag_context"],
            "cash": self.state.custom_state["cash"],
            "position": self.state.custom_state["position"],
            "entry_price": self.state.custom_state["entry_price"],
        }
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


class RagLLMLossAverseInvestor(RagLLMInvestor):
    """RAG-augmented: LossAverseInvestor rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.1"""

    _system_prompt = RULELLM_LOSS_AVERSE_PROMPT


class RagLLMBreakEvenTrader(RagLLMInvestor):
    """RAG-augmented: BreakEvenTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.2"""

    _system_prompt = RULELLM_BREAK_EVEN_PROMPT


class RagLLMRationalTrader(RagLLMInvestor):
    """RAG-augmented: RationalTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.3"""

    _system_prompt = RULELLM_RATIONAL_PROMPT


class RagLLMMomentumTrader(RagLLMInvestor):
    """RAG-augmented: MomentumTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.4"""

    _system_prompt = RULELLM_MOMENTUM_PROMPT


class RagLLMMarketMaker(RagLLMInvestor):
    """RAG-augmented: MarketMaker rules + LLM + retrieved knowledge. Theory: simulation-bases.md §4.5"""

    _system_prompt = RULELLM_MARKET_MAKER_PROMPT


__all__ = [
    "_RAG_FALLBACK",
    "Market",
    "RagLLMInvestor",
    "RagLLMLossAverseInvestor",
    "RagLLMBreakEvenTrader",
    "RagLLMRationalTrader",
    "RagLLMMomentumTrader",
    "RagLLMMarketMaker",
]
