"""VolatilityClusteringLLM - LLM-based Multi-Agent Market Simulation

LLM-powered investors for studying market dynamics through
heterogeneous agent interactions.

Market Parameters (from config.extras):
    - record_path: Path for output records
    - fundamental_value: True value for mean reversion
    - initial_price: Starting price
    - price_impact: Price impact coefficient
    - mean_reversion: Mean reversion strength
    - garch_omega: GARCH constant term
    - garch_alpha: GARCH return-squared coefficient
    - garch_beta: GARCH variance persistence
    - min_volatility: Minimum volatility floor
    - max_volatility: Maximum volatility ceiling
    - custom_state_hot_limit: Maximum history buffer size

Investor Parameters (from config.extras):
    - record_path: Path for output records
    - initial_cash: Starting cash balance
    - initial_position: Starting share position
    - custom_state_hot_limit: Maximum history buffer size
    - llm: LLM configuration (sys_message, user_message, lm_name, generation_config)
"""

import logging
import os
import json
import random
import re
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer
from masim.utils.llm_utils import parse_llm_response_with_thinking

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from .prompts import (
    LLM_FUNDAMENTALIST_SYS,
    LLM_TREND_FOLLOWER_SYS,
    LLM_NOISE_TRADER_SYS,
    LLM_SLOW_ADAPTER_SYS,
    LLM_VOLATILITY_TRADER_SYS,
)

logger = logging.getLogger("VolatilityClusteringLLM")


class Market(GeneralPlayer):
    """Central market with GARCH(1,1) volatility dynamics.

    All parameters read from config.extras (no class constants).
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
            self.state.custom_state["volatility"] = 1.0
            self.state.custom_state["prev_return"] = 0.0

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
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
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        current_vol = self.state.custom_state["volatility"]
        prev_return = self.state.custom_state["prev_return"]
        orders = self.state.custom_state["orders"]

        # Get parameters from config
        fundamental_value = extras["fundamental_value"]
        price_impact_coef = extras["price_impact"]
        mean_reversion_strength = extras["mean_reversion"]
        garch_omega = extras["garch_omega"]
        garch_alpha = extras["garch_alpha"]
        garch_beta = extras["garch_beta"]
        min_volatility = extras["min_volatility"]
        max_volatility = extras["max_volatility"]

        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # GARCH(1,1) volatility update
        new_variance = (
            garch_omega + garch_alpha * (prev_return**2) + garch_beta * (current_vol**2)
        )
        new_vol = math.sqrt(new_variance)
        new_vol = max(min_volatility, min(max_volatility, new_vol))

        # Price dynamics
        price_impact = price_impact_coef * net_demand
        mean_reversion = mean_reversion_strength * (fundamental_value - current_price)
        noise = random.gauss(0, new_vol)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        return_pct = price_return * 100

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["volatility"] = new_vol
        self.state.custom_state["prev_return"] = price_return

        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volatility_history"].append(new_vol)
        self.state.custom_state["volume_history"].append(total_volume)

        logger.debug(f"\n{'='*70}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"[Market] Round {round_num}"
        )  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)"
        )
        logger.debug(
            f"  Volatility: {current_vol:.3f} → {new_vol:.3f}"
        )  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}"
        )  # pylint: disable=logging-fstring-interpolation
        if orders:
            logger.debug(
                f"  LLM Orders ({len(orders)}):"
            )  # pylint: disable=logging-fstring-interpolation
            for o in orders:
                logger.debug(
                    f"    {o['investor']:25s} [{o['strategy']:15s}]: Q={o['quantity']:+8.2f}"
                )
                if o["reasoning"]:
                    logger.debug(
                        f"      → {o['reasoning'][:80]}..."
                    )  # pylint: disable=logging-fstring-interpolation

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": return_pct,
            "volatility": new_vol,
            "prev_volatility": current_vol,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "fundamental": fundamental_value,
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


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-powered volatility-clustering investors."""

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
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
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=custom_state_hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                self.state.custom_state["volatility_history"].append(
                    market_data["volatility"]
                )

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build user prompt with market data including volatility."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]
        vol_history = self.state.custom_state["volatility_history"]

        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )
        recent_vols = (
            list(vol_history)[-5:] if len(vol_history) >= 5 else list(vol_history)
        )
        return (
            f"Price: ${market_data['price']:.2f}  prev=${market_data['prev_price']:.2f}"
            f"  ret={market_data['return_pct']:+.2f}%\n"
            f"Volatility: {market_data['volatility']:.4f}  prev={market_data['prev_volatility']:.4f}\n"
            f"Volume: {market_data['volume']:.0f}  net_demand={market_data['net_demand']:+.2f}"
            f"  fundamental=${market_data['fundamental']:.2f}\n"
            f"Recent prices: {recent_prices}\n"
            f"Recent vols: {[f'{v:.4f}' for v in recent_vols]}\n"
            f"Portfolio: cash={cash:.2f}  position={position:.4f}"
            f"  value={cash + position * market_data['price']:.2f}\n"
            "Respond with <analysis>...</analysis> then "
            '<decision>{"bid_price":...,"quantity":...,"reasoning":"..."}'
            "</decision>"
        )

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with thinking and decision sections.

        Delegates to shared utility in examples/llm_utils.py
        """
        return parse_llm_response_with_thinking(response_text)

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(market_data)
        system_prompt = self._system_prompt
        llm_client = self._get_llm()

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(
                system_msg=system_prompt,
                user_msg=user_prompt,
            )
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.outputs[0].response)
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        f"[{self.identity}] LLM parse failed, retrying ({attempt + 1}/{max_retries})..."
                    )

        strategy_name = self.__class__.__name__

        # If LLM failed after all retries, skip trading this round (hold)
        if decision is None:
            logger.warning(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}. "
                f"Skipping trade this round."
            )
            order = {
                "bid_price": market_data["price"],
                "quantity": 0.0,
                "strategy": strategy_name,
                "investor": self.identity,
                "reasoning": f"LLM parse failed: held position",
                "analysis": "",
                "cash": self.state.custom_state["cash"],
                "position": self.state.custom_state["position"],
            }
            return {
                **order,
                "outbound_messages": [
                    {"payload": order, "content_type": "investor_bid"}
                ],
            }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        quantity = self._apply_constraints(bid_price, quantity, market_data["price"])

        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision.get("analysis", ""),
            "cash": self.state.custom_state["cash"],
            "position": self.state.custom_state["position"],
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


class LLMFundamentalist(LLMInvestor):
    """LLM-powered Fundamentalist - Slow mean reversion."""

    _system_prompt = LLM_FUNDAMENTALIST_SYS


class LLMTrendFollower(LLMInvestor):
    """LLM-powered Trend Follower - Fast momentum, vol-sensitive."""

    _system_prompt = LLM_TREND_FOLLOWER_SYS


class LLMNoiseTrader(LLMInvestor):
    """LLM-powered Noise Trader - Random liquidity."""

    _system_prompt = LLM_NOISE_TRADER_SYS


class LLMSlowAdapter(LLMInvestor):
    """LLM-powered Slow Adapter - Conservative, delayed."""

    _system_prompt = LLM_SLOW_ADAPTER_SYS


class LLMVolatilityTrader(LLMInvestor):
    """LLM-powered Volatility Trader - Trades vol regime."""

    _system_prompt = LLM_VOLATILITY_TRADER_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMFundamentalist",
    "LLMTrendFollower",
    "LLMNoiseTrader",
    "LLMSlowAdapter",
    "LLMVolatilityTrader",
]
