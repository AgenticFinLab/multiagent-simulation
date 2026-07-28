"""ArchegosCollapse LLM Simulation

Archegos collapse simulation with LLM-driven investors using behavioral personas.
Market dynamics are rule-based; investor decisions are LLM-generated.

Uses the centralized robust_llm_call pipeline from masim.utils.llm_utils for
automatic retry, backoff, error discrimination, and fallback hold.

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import importlib
import logging
import os
import sys
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from lmbase.inference.api_call import LangChainAPIInference

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import normalize_action_quantity, validate_order
from masim.utils.llm_utils import robust_llm_call_async

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.ArchegosCollapse.Rule.players import Market  # noqa: E402

logger = logging.getLogger("ArchegosCollapse.LLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from a module path (module:VARIABLE)."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def _validate_decision(decision: Dict[str, Any]) -> None:
    """Validate canonical trading decision fields.

    Raises ValueError if the decision is malformed. Used as validate_fn
    parameter to robust_llm_call_async.
    """
    action = decision.get("action", "")
    if action not in {"buy", "sell", "hold"}:
        raise ValueError(f"invalid action: {action}")
    bid_price = float(decision.get("bid_price", 0))
    if bid_price <= 0:
        raise ValueError(f"invalid bid_price: {bid_price}")
    quantity = float(decision.get("quantity", 0))
    if quantity < 0:
        raise ValueError(f"invalid quantity: {quantity}")
    reasoning = str(decision.get("reasoning", "")).strip()
    if not reasoning:
        raise ValueError("empty reasoning")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-powered investors in the ArchegosCollapse scenario.

    Uses masim.utils.llm_utils.robust_llm_call_async for centralized
    retry/backoff/fallback. Scenario-specific logic is limited to:
    - Prompt loading (sys_message / user_message from extras["llm"])
    - Portfolio bookkeeping (cash/position mutation after decision)
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

            load_dotenv()
            llm_cfg = extras["llm"]
            lm_name = llm_cfg["lm_name"]
            generation_config = llm_cfg["generation_config"]

            self.state.custom_state["lm_name"] = lm_name
            self.state.custom_state["generation_config"] = generation_config
            self.state.custom_state["llm_client"] = LangChainAPIInference(
                lm_name=lm_name,
                generation_config=generation_config,
            )
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            custom.pop("llm_client", None)
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

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        strategy_name = self.__class__.__name__

        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_template = load_prompt(llm_cfg["user_message"])

        user_prompt = user_template.format(
            round=round_num,
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            fundamental=market_data["fundamental"],
            deviation=market_data["deviation"],
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
        )

        # --- Centralized robust LLM call ---
        decision = await robust_llm_call_async(
            llm_client,
            system_prompt,
            user_prompt,
            validate_fn=_validate_decision,
            max_retries=5,
            fallback="hold",
            identity=self.identity,
        )

        # Fallback hold — skip portfolio mutation, emit noop
        if decision.get("_fallback"):
            logger.warning("[%s] R%d: fallback hold", self.identity, round_num)
            order = {
                "action": "hold",
                "bid_price": market_data["price"],
                "quantity": 0,
                "strategy": strategy_name,
                "investor": self.identity,
                "reasoning": decision["reasoning"],
                "analysis": "",
                "_skipped": True,
            }
            validate_order(order)
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
            }

        # --- Normal path: apply portfolio constraints ---
        action, quantity = normalize_action_quantity(
            decision["action"], decision["quantity"]
        )
        bid_price = float(decision["bid_price"])

        if action == "buy":
            max_affordable = cash / bid_price
            quantity = min(quantity, max_affordable)
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            quantity = min(quantity, max(position, 0.0))
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] -= quantity

        if quantity == 0:
            action = "hold"

        logger.info(
            "[%s] R%d (%s): Q=%+.2f", self.identity, round_num, strategy_name, quantity
        )

        order = {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
        }

        validate_order(order)
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMConcentratedFund(LLMInvestor):
    """LLM-driven concentrated fund — TRS-leveraged, slow to react to margin calls. Theory: simulation-bases.md §4.1."""

    pass


class LLMPrimeBrokerFirstMover(LLMInvestor):
    """LLM-driven prime broker 1 — first-mover liquidator. Theory: simulation-bases.md §4.2."""

    pass


class LLMPrimeBrokerDelayedLiquidator(LLMInvestor):
    """LLM-driven prime broker 2 — delayed liquidator at worse prices. Theory: simulation-bases.md §4.3."""

    pass


class LLMBlockTradeBuyer(LLMInvestor):
    """LLM-driven block trade buyer — opportunistic discount buyer. Theory: simulation-bases.md §4.4."""

    pass


class LLMInformationTrader(LLMInvestor):
    """LLM-driven information trader — front-runs liquidation cascade. Theory: simulation-bases.md §4.5."""

    pass


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMConcentratedFund",
    "LLMPrimeBrokerFirstMover",
    "LLMPrimeBrokerDelayedLiquidator",
    "LLMBlockTradeBuyer",
    "LLMInformationTrader",
    "_validate_decision",
]
