"""VolatilityClustering - Heterogeneous Agent Model (HAM) Simulation

This module implements a market simulation demonstrating volatility clustering
(GARCH effect) through interactions between heterogeneous agents.

Phenomenon: Volatility Clustering
    Market volatility is persistent - large price swings tend to be followed
    by large swings, and small swings by small swings. This is captured in
    GARCH models but emerges naturally from agent interactions.

Theoretical Foundation:
    - Heterogeneous Agent Models (HAM)
    - Feedback mechanisms between fundamentalists and chartists
    - Brock & Hommes (1998): Heterogeneous beliefs and routes to chaos

Architecture:
    - Market: Rule-based coordinator with endogenous volatility
    - Fundamentalist: Slow mean reversion, low trading frequency
    - TrendFollower: Fast momentum, high volatility sensitivity
    - NoiseTrader: Random liquidity provision
    - SlowAdapter: Conservative, delayed information processing
    - VolatilityTrader: Trades based on volatility regime

Key Dynamics:
    1. External shock → Price moves
    2. TrendFollowers react quickly → Amplify movement
    3. Fundamentalists react slowly → Cannot immediately dampen
    4. High volatility state attracts more trend trading
    5. Eventually trend exhausts → Volatility subsides
"""

import os
import random
import math
from typing import Any, Dict, List, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market - Coordinator with Endogenous Volatility
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with volatility-aware price dynamics.

    Price Model (simplified for multi-agent):
        P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + σ(t) × ε

    Where:
        - λ: Price impact coefficient
        - γ: Mean reversion speed
        - σ(t): Time-varying volatility (GARCH-like)
        - ε: Random noise

    Volatility follows a simplified GARCH(1,1):
        σ²(t) = ω + α × r²(t-1) + β × σ²(t-1)

    This creates volatility clustering: large returns increase future volatility.
    """

    # Market parameters
    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0

    # Price dynamics
    PRICE_IMPACT = 0.05  # λ: Impact of net demand on price
    MEAN_REVERSION = 0.02  # γ: Speed of reversion to fundamental

    # GARCH parameters for endogenous volatility
    GARCH_OMEGA = 0.0001  # ω: Base variance
    GARCH_ALPHA = 0.15  # α: Shock persistence (ARCH effect)
    GARCH_BETA = 0.80  # β: Volatility persistence (GARCH effect)
    # Note: α + β < 1 for stationarity

    MIN_VOLATILITY = 0.5  # Floor on volatility
    MAX_VOLATILITY = 10.0  # Ceiling on volatility

    HISTORY_LIMIT = 200

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize
        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["volatility"] = 1.0  # Initial volatility
            self.state.custom_state["prev_return"] = 0.0

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=self.HISTORY_LIMIT,
            )

        # Collect orders from investors
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
        current_vol = self.state.custom_state["volatility"]
        prev_return = self.state.custom_state["prev_return"]
        orders = self.state.custom_state["orders"]

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Update volatility using GARCH(1,1)
        # σ²(t) = ω + α × r²(t-1) + β × σ²(t-1)
        new_variance = (
            self.GARCH_OMEGA
            + self.GARCH_ALPHA * (prev_return**2)
            + self.GARCH_BETA * (current_vol**2)
        )
        new_vol = math.sqrt(new_variance)
        new_vol = max(self.MIN_VOLATILITY, min(self.MAX_VOLATILITY, new_vol))

        # Price dynamics
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
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

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)")
        print(f"  Volatility: {current_vol:.3f} → {new_vol:.3f}")
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:25s} [{o['strategy']:15s}]: Q={o['quantity']:+8.2f}"
                )

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
# Base Investor Class
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """
    Base class for volatility clustering investors.

    Common functionality:
    - Portfolio tracking (cash, position)
    - History buffer for recent prices
    - Order constraints (position limits, cash limits)
    """

    STRATEGY_NAME = "base"
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 0.0
    HISTORY_LIMIT = 50

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize
        if "cash" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=self.HISTORY_LIMIT,
            )

        # Get market data
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                self.state.custom_state["volatility_history"].append(
                    market_data["volatility"]
                )

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        """Apply cash/position constraints to quantity."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:  # Buying
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:  # Selling
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    def _execute_trade(self, bid_price: float, quantity: float) -> None:
        """Update portfolio after trade."""
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
# Fundamentalist - Slow Mean Reversion
# =============================================================================


class Fundamentalist(BaseInvestor):
    """
    Fundamentalist investor with slow mean reversion behavior.

    Theory: Brock & Hommes (1998), Heterogeneous Agent Models

    Behavior:
        - Estimates fundamental value (with noise and slow update)
        - Trades slowly towards estimated fair value
        - Low frequency: only trades every N rounds
        - High execution delay

    Effect on Volatility Clustering:
        - STABILIZING in long run (anchors price to fundamentals)
        - TOO SLOW to prevent short-term volatility bursts
        - Creates delayed damping effect

    Formula:
        If round % TRADE_FREQUENCY == 0:
            deviation = (fundamental - price) / price
            quantity = k × deviation × base_size
    """

    STRATEGY_NAME = "fundamentalist"

    # Fundamentalist parameters
    TRADE_FREQUENCY = 3  # Trade every N rounds (slow)
    VALUE_SENSITIVITY = 0.5  # How strongly to react to mispricing
    BASE_POSITION_SIZE = 20.0  # Base trade size
    VALUE_NOISE_STD = 2.0  # Uncertainty in value estimation

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        # Only trade at certain frequency (slow)
        if round_num % self.TRADE_FREQUENCY != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            # Add noise to value estimation (uncertainty)
            estimated_value = fundamental + random.gauss(0, self.VALUE_NOISE_STD)

            # Calculate deviation
            deviation = (estimated_value - price) / price  # Positive = undervalued

            # Conservative position sizing
            quantity = self.VALUE_SENSITIVITY * deviation * self.BASE_POSITION_SIZE
            quantity = max(-20, min(20, quantity))  # Limit size

            # Bid at current price (market order approximation)
            bid_price = price

            # Apply constraints
            quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
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
# TrendFollower - Fast Momentum, Volatility Sensitive
# =============================================================================


class TrendFollower(BaseInvestor):
    """
    Trend-following investor with high volatility sensitivity.

    Theory: Chartist behavior in HAM models

    Behavior:
        - Uses short lookback window for trend detection
        - Trades FAST - every round
        - HIGHLY sensitive to recent volatility
        - Position size increases with trend strength

    Effect on Volatility Clustering:
        - DESTABILIZING - amplifies price movements
        - Reacts immediately to shocks
        - High volatility → larger positions → more volatility
        - Creates positive feedback loop

    Formula:
        trend = sign(price - MA(N))
        volatility_multiplier = volatility / baseline_vol
        quantity = trend × base_size × (1 + vol_sensitivity × vol_multiplier)
    """

    STRATEGY_NAME = "trend_follower"

    # Trend following parameters
    LOOKBACK_WINDOW = 3  # Short memory (fast reaction)
    BASE_POSITION_SIZE = 30.0  # Aggressive base size
    VOLATILITY_SENSITIVITY = 0.8  # How much volatility affects position
    BASELINE_VOLATILITY = 1.0  # Reference volatility level
    TREND_THRESHOLD = 0.005  # Minimum trend to trade

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = market_data["volatility"]
        price_history = self.state.custom_state["price_history"]

        # Calculate recent trend
        if len(price_history) >= self.LOOKBACK_WINDOW:
            recent_prices = list(price_history)[-self.LOOKBACK_WINDOW :]
            ma = sum(recent_prices) / len(recent_prices)
            trend = (price - ma) / ma  # Normalized trend
        else:
            trend = 0.0

        # Volatility-adjusted position sizing
        vol_ratio = volatility / self.BASELINE_VOLATILITY
        vol_multiplier = 1.0 + self.VOLATILITY_SENSITIVITY * (vol_ratio - 1.0)
        vol_multiplier = max(0.5, min(2.0, vol_multiplier))  # Clamp

        # Trade if trend is significant
        if abs(trend) > self.TREND_THRESHOLD:
            direction = 1.0 if trend > 0 else -1.0
            strength = min(abs(trend) / 0.05, 1.0)  # Normalize strength
            quantity = direction * self.BASE_POSITION_SIZE * strength * vol_multiplier
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        # Apply constraints
        quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} vol_mult={vol_multiplier:.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
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
# NoiseTrader - Random Liquidity Provider
# =============================================================================


class NoiseTrader(BaseInvestor):
    """
    Noise trader providing random liquidity.

    Theory: De Long, Shleifer, Summers, Waldmann (1990)

    Behavior:
        - Trades randomly each round
        - Position reverts slowly to zero (mean reversion)
        - Provides market liquidity
        - Can trigger volatility bursts

    Effect on Volatility Clustering:
        - NEUTRAL to mildly destabilizing
        - Provides shocks that start volatility episodes
        - Adds randomness that can be amplified by trend followers
    """

    STRATEGY_NAME = "noise_trader"

    # Noise trading parameters
    POSITION_VOLATILITY = 15.0  # Standard deviation of position changes
    MEAN_REVERSION_SPEED = 0.1  # How fast position reverts to zero

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        # Random component
        random_trade = random.gauss(0, self.POSITION_VOLATILITY)

        # Mean reversion component (slowly reduce extreme positions)
        reversion = -self.MEAN_REVERSION_SPEED * position

        quantity = random_trade + reversion
        quantity = max(-30, min(30, quantity))  # Limit size
        bid_price = price if quantity != 0 else 0.0

        # Apply constraints
        quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
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
# SlowAdapter - Conservative, Delayed Information Processing
# =============================================================================


class SlowAdapter(BaseInvestor):
    """
    Conservative investor with slow information processing.

    Theory: Conservatism bias (Edwards, 1968)

    Behavior:
        - Updates beliefs slowly based on new information
        - Uses long lookback window
        - Small position sizes
        - Filters out short-term noise

    Effect on Volatility Clustering:
        - WEAKLY STABILIZING
        - Cannot react fast enough to dampen volatility
        - Provides gradual price correction
    """

    STRATEGY_NAME = "slow_adapter"

    # Slow adapter parameters
    LOOKBACK_WINDOW = 10  # Long memory
    UPDATE_WEIGHT = 0.1  # Weight on new vs old information
    BASE_POSITION_SIZE = 10.0  # Conservative size

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        price_history = self.state.custom_state["price_history"]

        # Calculate long-term average
        if len(price_history) >= self.LOOKBACK_WINDOW:
            recent_prices = list(price_history)[-self.LOOKBACK_WINDOW :]
            long_ma = sum(recent_prices) / len(recent_prices)
        else:
            long_ma = price

        # Blended value estimate (slow update)
        estimated_value = (
            self.UPDATE_WEIGHT * fundamental + (1 - self.UPDATE_WEIGHT) * long_ma
        )

        # Calculate signal
        deviation = (estimated_value - price) / price

        # Conservative trading
        if abs(deviation) > 0.02:  # Only trade on significant deviations
            quantity = deviation * self.BASE_POSITION_SIZE
            quantity = max(-10, min(10, quantity))  # Very conservative
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        # Apply constraints
        quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
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
# VolatilityTrader - Trades Based on Volatility Regime
# =============================================================================


class VolatilityTrader(BaseInvestor):
    """
    Volatility regime trader - sells in high vol, buys in low vol.

    Theory: Volatility mean reversion, VIX trading strategies

    Behavior:
        - Tracks volatility relative to historical average
        - Sells when volatility is high (expecting mean reversion)
        - Buys when volatility is low (expecting calm to continue)
        - Risk reduction focus

    Effect on Volatility Clustering:
        - WEAKLY STABILIZING
        - Provides liquidity in high volatility episodes
        - Dampens extreme volatility spikes
    """

    STRATEGY_NAME = "volatility_trader"

    # Volatility trading parameters
    VOL_LOOKBACK = 5  # Window for average volatility
    HIGH_VOL_THRESHOLD = 1.5  # Multiple of average vol considered "high"
    LOW_VOL_THRESHOLD = 0.7  # Multiple considered "low"
    BASE_POSITION_SIZE = 15.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = market_data["volatility"]
        vol_history = self.state.custom_state["volatility_history"]

        # Calculate average volatility
        if len(vol_history) >= self.VOL_LOOKBACK:
            recent_vols = list(vol_history)[-self.VOL_LOOKBACK :]
            avg_vol = sum(recent_vols) / len(recent_vols)
        else:
            avg_vol = volatility

        # Volatility ratio
        vol_ratio = volatility / avg_vol if avg_vol > 0 else 1.0

        # Trading signal based on volatility regime
        if vol_ratio > self.HIGH_VOL_THRESHOLD:
            # High volatility - reduce exposure (sell)
            quantity = -self.BASE_POSITION_SIZE * (vol_ratio - 1.0)
            bid_price = price
        elif vol_ratio < self.LOW_VOL_THRESHOLD:
            # Low volatility - increase exposure (buy)
            quantity = self.BASE_POSITION_SIZE * (1.0 - vol_ratio)
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = max(-20, min(20, quantity))

        # Apply constraints
        quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"Q={quantity:+8.2f} vol_ratio={vol_ratio:.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
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
