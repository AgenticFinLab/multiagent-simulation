"""MomentumEffect LLM Players - LLM-based momentum trading simulation.

LLM investors with different momentum/contrarian strategies interacting
in a market with persistent price drift creating momentum opportunities.

Market Parameters (from config.extras):
    - record_path, initial_price, initial_fundamental
    - price_impact, mean_reversion, noise_std
    - drift_persistence, drift_volatility
    - custom_state_hot_limit

Investor Parameters (from config.extras):
    - record_path, initial_cash, initial_position
    - custom_state_hot_limit
    - llm: model, temperature (optional)
"""

import logging
import os
import random
from collections import deque
from typing import Any, Dict, List, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

from .prompts import (
    LLM_MOMENTUM_TRADER_SYS,
    LLM_CONTRARIAN_SYS,
    LLM_TECHNICAL_SYS,
    LLM_TREND_FOLLOWER_SYS,
    LLM_FUNDAMENTAL_SYS,
    LLM_USER_TEMPLATE,
)
from masim.utils.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("MomentumEffectLLM")


# =============================================================================
# Market - Rule-Based Coordinator
# =============================================================================


class Market(GeneralPlayer):
    """Central market with momentum-aware dynamics.

    Price Model:
        P(t+1) = P(t) + λ × NetDemand + γ × [F(t) - P(t)] + ε
    Fundamental value drifts slowly to create momentum opportunity.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["initial_fundamental"]
            self.state.custom_state["drift"] = 0.0
            self.state.custom_state["returns"] = deque(maxlen=20)

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],
                        "quantity": order["quantity"],
                        "strategy": order["strategy"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        drift = self.state.custom_state["drift"]
        orders = self.state.custom_state["orders"]
        returns = self.state.custom_state["returns"]

        drift_persistence = extras["drift_persistence"]
        drift_volatility = extras["drift_volatility"]
        new_drift = drift_persistence * drift + random.gauss(0, drift_volatility)
        new_fundamental = fundamental + new_drift
        new_fundamental = max(50, min(150, new_fundamental))

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty

        price_impact_coef = extras["price_impact"]
        mean_reversion_strength = extras["mean_reversion"]
        noise_std = extras["noise_std"]

        price_impact = price_impact_coef * net_demand
        mean_reversion = mean_reversion_strength * (new_fundamental - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        returns.append(price_return)
        momentum_5 = sum(list(returns)[-5:]) if len(returns) >= 5 else 0.0
        momentum_10 = sum(list(returns)[-10:]) if len(returns) >= 10 else 0.0

        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["drift"] = new_drift
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "[Market] R%d  P=%.2f→%.2f (%+.2f%%)  M5=%+.2f%%  M10=%+.2f%%",
            round_num,
            current_price,
            new_price,
            price_return * 100,
            momentum_5 * 100,
            momentum_10 * 100,
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "momentum_5": momentum_5,
            "momentum_10": momentum_10,
            "fundamental": new_fundamental,
            "round": round_num,
            "recent_returns": list(returns)[-10:],
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_price"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# LLMInvestor - Base
# =============================================================================


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-powered momentum investors."""

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        if not getattr(self, "_llm", None):
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
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]
        recent_prices = (
            list(price_history)[-10:]
            if len(price_history) >= 10
            else list(price_history)
        )
        return LLM_USER_TEMPLATE.format(
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            momentum_5=market_data["momentum_5"] * 100,
            momentum_10=market_data["momentum_10"] * 100,
            fundamental=market_data["fundamental"],
            recent_returns=[f"{r*100:.2f}%" for r in market_data["recent_returns"]],
            recent_prices=recent_prices,
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
        )

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        strategy_name = self.__class__.__name__
        llm = self._get_llm()

        user_prompt = self._build_prompt(market_data)

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(
                system_msg=self._system_prompt, user_msg=user_prompt
            )
            infer_output = llm.run([infer_input])
            try:
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            logger.warning(
                "[%s] LLM failed after %d attempts: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            order = {
                "bid_price": market_data["price"],
                "quantity": 0.0,
                "strategy": strategy_name,
            }
            return {
                **order,
                "outbound_messages": [
                    {"payload": order, "content_type": "investor_bid"}
                ],
            }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        # Guard: LLMs sometimes output bid_price=0 for hold actions.
        # Use the current market price so recorded bids stay meaningful.
        if bid_price <= 0:
            bid_price = market_data["price"]

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            quantity = max(-position, quantity)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        logger.debug(
            "[%-20s] R%d (%-15s): Q=%+7.2f",
            self.identity,
            round_num,
            strategy_name,
            quantity,
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "reasoning": decision["reasoning"][:120],
        }

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


# =============================================================================
# Concrete LLM Investor Types
# =============================================================================


class LLMMomentumTrader(LLMInvestor):
    """LLM MomentumTrader. Theory: simulation-bases.md §4.1."""

    _system_prompt = LLM_MOMENTUM_TRADER_SYS


class LLMContrarianTrader(LLMInvestor):
    """LLM ContrarianTrader. Theory: simulation-bases.md §4.2."""

    _system_prompt = LLM_CONTRARIAN_SYS


class LLMTechnicalTrader(LLMInvestor):
    """LLM TechnicalTrader. Theory: simulation-bases.md §4.5."""

    _system_prompt = LLM_TECHNICAL_SYS


class LLMTrendFollower(LLMInvestor):
    """LLM TrendFollower. Theory: simulation-bases.md §4.7."""

    _system_prompt = LLM_TREND_FOLLOWER_SYS


class LLMFundamentalAnchor(LLMInvestor):
    """LLM FundamentalAnchor. Theory: simulation-bases.md §4.6."""

    _system_prompt = LLM_FUNDAMENTAL_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMMomentumTrader",
    "LLMContrarianTrader",
    "LLMTechnicalTrader",
    "LLMTrendFollower",
    "LLMFundamentalAnchor",
]
