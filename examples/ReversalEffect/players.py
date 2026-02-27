"""ReversalEffect - Long-term Mean Reversion Simulation

Phenomenon: Reversal Effect (De Bondt & Thaler, 1985)
    - Past losers outperform past winners over 3-5 year periods
    - Market overreacts to information, then corrects
    - Creates predictable patterns in long-term returns

Theoretical Foundation:
    - Overreaction Hypothesis (De Bondt & Thaler, 1985)
    - Representativeness Heuristic (Kahneman & Tversky)
    - Investor Overconfidence (Daniel, Hirshleifer, Subrahmanyam, 1998)

Architecture:
    - Market: Order-based clearing with mean reversion
    - ContrarianInvestor: Buys losers, sells winners (KEY driver)
    - MomentumInvestor: Short-term trend following
    - OverconfidentTrader: Overreacts to news
    - NoiseTrader: Random liquidity
    - ValueInvestor: Slow fundamental investor
    - IndexTracker: Passive benchmark

Key Dynamics:
    1. Initial shock → Overreaction by OverconfidentTraders
    2. Price deviates from fundamental
    3. ContrarianInvestors recognize mispricing
    4. Gradual reversal back to fundamental (3-5 year horizon)
"""

import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market - Coordinator
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with mean reversion dynamics.

    Implements long-horizon price dynamics that allow:
    - Initial overreaction to news
    - Slow mean reversion toward fundamental
    """

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0

    # Price dynamics
    PRICE_IMPACT = 0.08  # Impact of net demand
    MEAN_REVERSION = 0.01  # Slow reversion to fundamental
    NOISE_STD = 0.5

    HISTORY_LIMIT = 200

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/ReversalEffect/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "return"),
                entry_limit=self.HISTORY_LIMIT,
            )

        # Collect orders
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
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["return_history"].append(price_return)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "fundamental": self.FUNDAMENTAL_VALUE,
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
# Base Investor
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """Base class for reversal effect investors."""

    STRATEGY_NAME = "base"
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 0.0
    HISTORY_LIMIT = 100

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/ReversalEffect/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )

        # Get market data
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0 and bid_price > 0:
            max_affordable = cash / bid_price
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    def _execute_trade(self, bid_price: float, quantity: float) -> None:
        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# ContrarianInvestor - KEY Driver of Reversal Effect
# =============================================================================


class ContrarianInvestor(BaseInvestor):
    """
    Contrarian investor exploiting mean reversion.

    Theory: De Bondt & Thaler (1985) - Overreaction Hypothesis

    Strategy:
        - Buys past losers (prices below long-term average)
        - Sells past winners (prices above long-term average)
        - Uses long lookback window (3-5 years in theory, ~30-50 rounds here)

    Effect: STABILIZING - drives long-term reversal toward fundamental
    """

    STRATEGY_NAME = "contrarian"

    LOOKBACK_WINDOW = 30  # Long-term horizon
    REVERSAL_THRESHOLD = 0.15  # 15% deviation triggers trade
    BASE_POSITION_SIZE = 25.0
    VALUE_SENSITIVITY = 0.6

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        price_history = self.state.custom_state["price_history"]

        # Calculate long-term average
        if len(price_history) >= self.LOOKBACK_WINDOW:
            long_term_avg = (
                sum(list(price_history)[-self.LOOKBACK_WINDOW :]) / self.LOOKBACK_WINDOW
            )
        else:
            long_term_avg = price

        # Long-term cumulative return
        if len(price_history) >= self.LOOKBACK_WINDOW:
            old_price = list(price_history)[-self.LOOKBACK_WINDOW]
            cumulative_return = (price - old_price) / old_price
        else:
            cumulative_return = 0.0

        # Contrarian signal: buy losers, sell winners
        # Negative cumulative return = buy signal
        if abs(cumulative_return) > self.REVERSAL_THRESHOLD:
            # Counter-trend trading
            quantity = (
                -self.VALUE_SENSITIVITY * cumulative_return * self.BASE_POSITION_SIZE
            )
            quantity = max(-30, min(30, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} cum_ret={cumulative_return*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# MomentumInvestor - Short-term Trend Follower
# =============================================================================


class MomentumInvestor(BaseInvestor):
    """
    Short-term momentum investor.

    Strategy: Follow recent price trends (Jegadeesh & Titman style)

    Effect: Creates initial overreaction, setting up reversal opportunity
    """

    STRATEGY_NAME = "momentum"

    LOOKBACK_WINDOW = 5
    MOMENTUM_THRESHOLD = 0.02
    BASE_POSITION_SIZE = 20.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        # Short-term momentum
        if len(price_history) >= self.LOOKBACK_WINDOW:
            old_price = list(price_history)[-self.LOOKBACK_WINDOW]
            momentum = (price - old_price) / old_price
        else:
            momentum = 0.0

        if abs(momentum) > self.MOMENTUM_THRESHOLD:
            quantity = momentum * self.BASE_POSITION_SIZE * 10  # Amplify momentum
            quantity = max(-25, min(25, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} mom={momentum*100:+.1f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# OverconfidentTrader - Causes Initial Overreaction
# =============================================================================


class OverconfidentTrader(BaseInvestor):
    """
    Overconfident trader who overreacts to news.

    Theory: Daniel, Hirshleifer, Subrahmanyam (1998)

    Behavior:
        - Overweights own information
        - Trades aggressively on price changes
        - Creates initial overreaction

    Effect: DESTABILIZING - causes prices to overshoot
    """

    STRATEGY_NAME = "overconfident"

    OVERCONFIDENCE_FACTOR = 2.5  # Overweights signals by 2.5x
    REACTION_THRESHOLD = 0.01
    BASE_POSITION_SIZE = 30.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]

        # Overreact to recent return
        if abs(price_return) > self.REACTION_THRESHOLD:
            # Amplify the signal with overconfidence
            signal = price_return * self.OVERCONFIDENCE_FACTOR
            quantity = signal * self.BASE_POSITION_SIZE * 10
            quantity = max(-40, min(40, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} ret={price_return*100:+.1f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# NoiseTrader - Random Liquidity
# =============================================================================


class NoiseTrader(BaseInvestor):
    """Noise trader providing random liquidity."""

    STRATEGY_NAME = "noise"

    POSITION_VOLATILITY = 10.0
    MEAN_REVERSION = 0.1

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        random_trade = random.gauss(0, self.POSITION_VOLATILITY)
        reversion = -self.MEAN_REVERSION * position

        quantity = random_trade + reversion
        quantity = max(-20, min(20, quantity))
        bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# ValueInvestor - Slow Fundamental Investor
# =============================================================================


class ValueInvestor(BaseInvestor):
    """
    Value investor based on fundamental analysis.

    Strategy: Buy when price < fundamental, sell when price > fundamental
    """

    STRATEGY_NAME = "value"

    VALUE_SENSITIVITY = 0.4
    BASE_POSITION_SIZE = 15.0
    VALUE_NOISE = 2.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        # Estimate fundamental with noise
        estimated_value = fundamental + random.gauss(0, self.VALUE_NOISE)

        # Calculate mispricing
        deviation = (estimated_value - price) / price

        if abs(deviation) > 0.03:  # 3% threshold
            quantity = self.VALUE_SENSITIVITY * deviation * self.BASE_POSITION_SIZE
            quantity = max(-15, min(15, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} dev={deviation*100:+.1f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# IndexTracker - Passive Benchmark
# =============================================================================


class IndexTracker(BaseInvestor):
    """
    Passive index tracker for benchmarking.

    Strategy: Maintains constant market exposure
    """

    STRATEGY_NAME = "index"

    TARGET_POSITION = 50.0  # Target position
    REBALANCE_THRESHOLD = 0.1  # 10% deviation triggers rebalance

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        # Check if rebalancing needed
        position_diff = self.TARGET_POSITION - position

        if abs(position_diff / self.TARGET_POSITION) > self.REBALANCE_THRESHOLD:
            quantity = position_diff * 0.3  # Gradual rebalance
            quantity = max(-10, min(10, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} pos={position:.1f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }
