"""AnchoringEffect LLM Simulation

Anchoring bias simulation with LLM-driven investors using behavioral personas.
Market dynamics are rule-based; investor decisions are LLM-generated.

Theoretical Foundation:
    - Tversky & Kahneman (1974): Judgment under Uncertainty: Heuristics and Biases
    - Northcraft & Neale (1987): Experts, amateurs, and real estate
    - Campbell & Sharpe (2009): Anchoring bias in consensus forecasts

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
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import validate_order

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from masim.utils.llm_utils import (
    parse_llm_response_with_thinking,
    robust_llm_call,
)
from examples.AnchoringEffect.Rule.players import Market

logger = logging.getLogger("AnchoringEffect.LLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from a module path (module:VARIABLE)."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class LLMInvestor(GeneralPlayer):
    """
    Base class for LLM-powered investors in the AnchoringEffect scenario.

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path
        - llm: sys_message, user_message, lm_name, generation_config
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

        # Compute price_change for template (not broadcast by Market)
        price_change = (
            (market_data["price"] - market_data["prev_price"])
            / market_data["prev_price"]
            if market_data["prev_price"] > 0
            else 0.0
        )

        user_prompt = user_template.format(
            round=round_num,
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            fundamental=market_data["fundamental"],
            price_change=price_change,
            deviation=market_data["deviation"],
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
        )

        decision = robust_llm_call(
            llm_client,
            system_prompt,
            user_prompt,
            parse_fn=parse_llm_response_with_thinking,
            max_retries=5,
            fallback="hold",
            identity=self.identity,
        )

        if decision.get("_fallback"):
            logger.warning(
                "[%s] R%d LLM unavailable; emitting noop hold.",
                self.identity,
                round_num,
            )
            fallback_order = {
                "action": "hold",
                "quantity": 0,
                "bid_price": float(market_data["price"]),
                "strategy": strategy_name,
                "investor": self.identity,
                "reasoning": "llm_fallback_noop",
                "analysis": "",
            }
            return {
                **fallback_order,
                "outbound_messages": [
                    {"payload": fallback_order, "content_type": "investor_bid"}
                ],
            }

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        # Guard: LLMs sometimes output bid_price=0 for hold actions.
        # Use the current market price so recorded bids stay meaningful.
        if bid_price <= 0:
            bid_price = market_data["price"]

        if action == "buy":
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif action == "sell":
            quantity = min(quantity, position)
            self.state.custom_state["cash"] += quantity * bid_price
            self.state.custom_state["position"] -= quantity

        logger.info(
            "[%s] R%d (%s %s): Q=%.2f",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
        )

        order = {
            "action": action,
            "quantity": quantity,
            "bid_price": bid_price,
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


class LLMAnchoredTrader(LLMInvestor):
    """LLM-driven anchored trader — anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md §4.1 — AnchoredTrader."""

    pass


class LLMHistoricalAnchor(LLMInvestor):
    """LLM-driven historical anchor — anchors to historical average price. Theory: simulation-bases.md §4.2 — HistoricalAnchor."""

    pass


class LLMRationalUpdater(LLMInvestor):
    """LLM-driven rational updater — Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md §4.3 — RationalUpdater."""

    pass


class LLMMomentumTrader(LLMInvestor):
    """LLM-driven momentum trader — follows price trends. Theory: simulation-bases.md §4.4 — MomentumTrader."""

    pass


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven noise trader — uninformed random participant. Theory: simulation-bases.md §4.5 — NoiseTrader."""

    pass


class LLMDispositionTrader(LLMInvestor):
    """LLM-driven disposition trader — sells winners early, holds losers (Prospect Theory). Theory: simulation-bases.md §4.6 — DispositionTrader."""

    pass


class LLMContrarianTrader(LLMInvestor):
    """LLM-driven contrarian trader — fades cumulative overextension over a short lookback. Theory: simulation-bases.md §4.7 — ContrarianTrader."""

    pass


class LLMFundamentalAnalyst(LLMInvestor):
    """LLM-driven fundamental analyst — slow belief convergence toward fundamental value (conservatism bias). Theory: simulation-bases.md §4.8 — FundamentalAnalyst."""

    pass


class LLMLiquidityProvider(LLMInvestor):
    """LLM-driven liquidity provider — passive two-sided quoting around a short-term EMA. Theory: simulation-bases.md §4.9 — LiquidityProvider."""

    pass


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMAnchoredTrader",
    "LLMHistoricalAnchor",
    "LLMRationalUpdater",
    "LLMMomentumTrader",
    "LLMNoiseTrader",
    "LLMDispositionTrader",
    "LLMContrarianTrader",
    "LLMFundamentalAnalyst",
    "LLMLiquidityProvider",
]
