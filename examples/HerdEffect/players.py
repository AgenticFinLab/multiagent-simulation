"""Herd Effect Simulation - Emergent Herding Model (No Pre-defined Imitator)

Emergent Herding Model: 涌现型羊群效应
- Herd behavior EMERGES from interaction of rational agents
- NO explicit imitator (HerdingInvestor removed)
- Key insight: Information cascade forms without "blind followers"

Market Model:
    - Order-based clearing with demand-supply dynamics
    - Price = f(net_demand) + mean_reversion + noise
    - Volume feedback amplifies momentum signals

Investor Strategies (5 types):
1. Momentum:   Q ∝ +ΔP%, trend following → DESTABILIZING
2. Contrarian: Q ∝ (F-P)/P, value investing → STABILIZING
3. RiskAverse: Q ∝ 1/σ², volatility-adjusted → EARLY EXIT
4. Aggressive: Q = κ×ΔP% + accel, leveraged momentum → EXTREME AMPLIFIER
5. Noise:      Q ~ N(0, σ²), random trading → TRIGGER/LIQUIDITY

Emergent Herding Mechanism:
    NoiseTrader random buy → Price↑ → MomentumInvestor buys
    → Price↑↑ + Volume↑ → AggressiveInvestor amplifies
    → ALL investors converge (emergent behavior, not imitation)

Key Difference from Explicit Herding:
    - Traditional model: HerdingInvestor copies others directly
    - This model: Behavioral convergence EMERGES from positive feedback
    - Academic value: Reveals MECHANISM, not just PHENOMENON

References:
- Jegadeesh, N. & Titman, S. (1993): Momentum effect
- De Bondt, W.F.M. & Thaler, R. (1985): Contrarian/Value
- Shiller, R.J. (1984): Positive feedback trading
- De Long, J.B. et al. (1990): Noise trader risk
- Markowitz, H. (1952): Mean-variance optimization

Flow per Round:
    Market broadcasts (price, volume) → Investors submit (P, Q) orders → Market clears
"""

import os
import random
import math
import numpy as np
from typing import Any, Dict, List, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market Player - Order-Based Clearing
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with order-based clearing mechanism.

    Clearing Logic:
    1. Collect all buy orders (P, Q) from investors
    2. Sort orders by price descending
    3. Accumulate quantity until supply met (assume unlimited supply at fundamental)
    4. Clearing price = weighted average of executed orders
    5. Broadcast (clearing_price, total_volume) to all

    Price dynamics include mean reversion toward fundamental value.

    Memory Optimization:
    - Uses HistoryBuffer (hot deque + cold disk) for bounded memory
    - Full history persisted automatically via HistoryBuffer
    - Requires record_path in config.extras
    """

    # Market parameters
    INITIAL_PRICE = 100.0
    FUNDAMENTAL_VALUE = 100.0  # True intrinsic value
    SUPPLY_ELASTICITY = 0.1  # How much price responds to excess demand
    MEAN_REVERSION = 0.02  # Speed of price correction toward fundamental
    NOISE_STD = 0.5  # Market microstructure noise

    # History buffer limit (prevents memory explosion)
    HISTORY_LIMIT = 200

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize on first round
        if "price" not in self.state.custom_state:
            self.state.custom_state["price"] = self.INITIAL_PRICE
            # Use HistoryBuffer: hot (memory) + cold (disk)
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/HerdEffect/history"
            )
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
                initial_values=[self.INITIAL_PRICE],
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=self.HISTORY_LIMIT,
                initial_values=[0],
            )
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "return"),
                entry_limit=self.HISTORY_LIMIT,
                initial_values=[0.0],
            )

        # Collect orders from investors
        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],  # Limit price
                        "quantity": order["quantity"],  # Desired quantity
                        "strategy": order["strategy"],
                        "cash": order["cash"],
                        "position": order["position"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # === Order-Based Clearing ===
        # Sort orders by price descending (highest bidder first)
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        buy_orders.sort(key=lambda x: x["price"], reverse=True)

        # Calculate aggregate demand and supply
        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty

        # Calculate clearing price using demand-supply imbalance
        # Price impact = supply elasticity × net demand
        price_impact = self.SUPPLY_ELASTICITY * net_demand

        # Mean reversion toward fundamental
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)

        # Market noise
        noise = random.gauss(0, self.NOISE_STD)

        # New clearing price
        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)

        # Calculate return
        price_return = (new_price - current_price) / current_price

        # Total volume (absolute sum)
        total_volume = total_buy_qty + total_sell_qty

        # Update state
        prev_price = self.state.custom_state["price"]
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["return_history"].append(price_return)

        # Log
        print(f"\n{'='*60}")
        print(f"[Market] Round {round_num}")
        print(f"  Price: {prev_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)")
        print(f"  Net Demand: {net_demand:+.2f}")
        print(f"  Total Volume: {total_volume:.2f}")
        print(f"  Price Impact: {price_impact:+.4f}")
        print(f"  Mean Reversion: {mean_reversion:+.4f}")
        if orders:
            print(f"  Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:20s} [{o['strategy']:12s}]: "
                    f"P={o['price']:7.2f}, Q={o['quantity']:+7.2f}"
                )

        # Broadcast market data (Emergent model: no all_orders needed)
        market_data = {
            "price": new_price,
            "prev_price": prev_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
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
# Base Investor with Cash/Position Constraints
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """
    Base class for all investors with realistic constraints.

    State:
    - cash: Available capital (starts at 10,000)
    - position: Current holdings (starts at 0)
    - price_history: Track recent prices for volatility calculation (HistoryBuffer)

    Memory Optimization:
    - Uses HistoryBuffer (hot deque + cold disk) for bounded memory
    - Requires record_path in config.extras
    """

    STRATEGY_NAME = "base"
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 0.0
    HISTORY_LIMIT = 100  # Only need recent data for most strategies

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize
        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            # Use HistoryBuffer: hot (memory) + cold (disk)
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/HerdEffect/history"
            )
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=self.HISTORY_LIMIT,
            )

        # Get market data
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                self.state.custom_state["volume_history"].append(market_data["volume"])

    def calculate_bid(self) -> tuple:
        """Override in subclass. Returns (bid_price, quantity)."""
        raise NotImplementedError

    def _apply_cash_constraint(self, price: float, quantity: float) -> float:
        """Constrain quantity based on available cash."""
        cash = self.state.custom_state["cash"]
        if quantity > 0:  # Buying
            max_affordable = cash / price
            quantity = min(quantity, max_affordable)
        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        bid_price, quantity = self.calculate_bid()

        # Apply cash constraint
        quantity = self._apply_cash_constraint(bid_price, quantity)

        # Update position and cash (simplified execution)
        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity  # negative

        print(
            f"[{self.identity:20s}] R{round_num} ({self.STRATEGY_NAME:12s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
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


# =============================================================================
# Investor Strategies - Price-Volume Dual Dimension Model
# =============================================================================


class MomentumInvestor(BaseInvestor):
    """
    Momentum Strategy (Trend Following)
    Reference: Jegadeesh & Titman (1993)

    Formula:
        P = P_last × (1 + λ × r)
        Q = β × r × cash / P

    Where:
        r = last period return
        λ = price aggressiveness (0.5)
        β = capital allocation ratio (0.3)

    Behavior: Buys when price rises, sells when price falls.
    Effect: DESTABILIZING - amplifies trends, creates momentum bubbles.
    """

    STRATEGY_NAME = "momentum"
    LAMBDA = 0.5  # Price aggressiveness
    BETA = 0.3  # Capital allocation ratio

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        ret = market_data["return"]
        cash = self.state.custom_state["cash"]

        # P = P_last × (1 + λ × r)
        bid_price = price * (1 + self.LAMBDA * ret)
        bid_price = max(1.0, bid_price)

        # Q = β × r × cash / P
        quantity = self.BETA * ret * cash / bid_price

        # Limit order size
        quantity = max(-50, min(50, quantity))

        return bid_price, quantity


class ContrarianInvestor(BaseInvestor):
    """
    Contrarian/Value Strategy
    Reference: De Bondt & Thaler (1985)

    Formula:
        P = F + ε  (bid around fundamental value)
        Q = β × (F - P_last) / P_last × cash / P

    Where:
        F = fundamental value (100)
        β = value sensitivity (0.5)

    Behavior: Buys when price < fundamental, sells when price > fundamental.
    Effect: STABILIZING - dampens trends, provides mean reversion.
    """

    STRATEGY_NAME = "contrarian"
    FUNDAMENTAL = 100.0
    BETA = 0.5  # Value deviation sensitivity
    NOISE_STD = 0.5  # Bid noise

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        cash = self.state.custom_state["cash"]

        # P = F + ε (bid around fundamental)
        bid_price = self.FUNDAMENTAL + random.gauss(0, self.NOISE_STD)
        bid_price = max(1.0, bid_price)

        # Q = β × (F - P) / P × cash / bid_price
        deviation = (self.FUNDAMENTAL - price) / price
        quantity = self.BETA * deviation * cash / bid_price

        # Limit order size
        quantity = max(-50, min(50, quantity))

        return bid_price, quantity


# NOTE: HerdingInvestor REMOVED for Emergent Herding Model
# In the emergent model, herd behavior arises from the interaction of:
#   - MomentumInvestor (trend following → positive feedback)
#   - AggressiveInvestor (acceleration → extreme amplification)
# Without an explicit imitator, herding EMERGES from market dynamics.


class RiskAverseInvestor(BaseInvestor):
    """
    Risk-Averse Strategy (Mean-Variance Optimization)
    Reference: Markowitz (1952)

    Formula:
        P = P_last (accepts market price)
        Q = k / σ² × cash / P

    Where:
        σ² = recent price variance
        k = risk tolerance coefficient (0.5)

    Behavior: Reduces position when volatility is high.
    Effect: Can trigger early exit from bubble (sell before crash).
    """

    STRATEGY_NAME = "risk_averse"
    K = 0.5  # Risk tolerance coefficient
    LOOKBACK = 5  # Periods for volatility calculation

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        cash = self.state.custom_state["cash"]
        price_history = self.state.custom_state["price_history"]
        position = self.state.custom_state["position"]

        # Calculate variance
        if len(price_history) >= self.LOOKBACK:
            recent = price_history[-self.LOOKBACK :]
            variance = np.var(recent)
        else:
            variance = 1.0  # Default low variance

        # Avoid division by zero
        variance = max(variance, 0.1)

        # P = P_last (market price)
        bid_price = price

        # Q = k / σ² × cash / P
        # Position sizing inversely proportional to variance
        target_value = self.K / variance * cash
        target_qty = target_value / price

        # Trade toward target
        quantity = (target_qty - position) * 0.3  # Gradual adjustment
        quantity = max(-20, min(20, quantity))

        return bid_price, quantity


class NoiseTrader(BaseInvestor):
    """
    Noise Trader (Random/Uninformed Trading)
    Reference: De Long et al. (1990)

    Formula:
        P ~ N(P_last, σ_price²)
        Q ~ N(0, σ_qty²) - position × mean_reversion

    Where:
        σ_price = price noise (2.0)
        σ_qty = quantity noise (5.0)
        mean_reversion = 0.1 (position mean reversion)

    Behavior: Random trading, provides liquidity.
    Effect: Can accidentally trigger herd behavior when momentum traders
            misinterpret random noise as signal.
    """

    STRATEGY_NAME = "noise"
    PRICE_NOISE_STD = 2.0
    QTY_NOISE_STD = 5.0
    POSITION_MEAN_REVERSION = 0.1

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        # P ~ N(P_last, σ²)
        bid_price = price + random.gauss(0, self.PRICE_NOISE_STD)
        bid_price = max(1.0, bid_price)

        # Q ~ N(0, σ²) - position × mean_reversion
        random_qty = random.gauss(0, self.QTY_NOISE_STD)
        mean_reversion = -position * self.POSITION_MEAN_REVERSION
        quantity = random_qty + mean_reversion

        return bid_price, quantity


# =============================================================================
# Alternative: Aggressive Momentum (for extreme herd scenarios)
# =============================================================================


class AggressiveInvestor(BaseInvestor):
    """
    Aggressive/Leveraged Momentum Strategy

    Formula:
        P = P_last × (1 + κ × r)  where κ > λ
        Q = β × r × cash / P + acceleration_bonus

    Where:
        κ = aggressive price factor (1.0)
        β = aggressive allocation (0.5)
        acceleration = second derivative of price

    Behavior: Amplified momentum with acceleration bonus.
    Effect: EXTREMELY DESTABILIZING - can create rapid bubbles.
    """

    STRATEGY_NAME = "aggressive"
    KAPPA = 1.0  # Aggressive price factor
    BETA = 0.5  # Aggressive capital allocation
    ACCEL_BONUS = 0.3  # Acceleration trading bonus

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        ret = market_data["return"]
        cash = self.state.custom_state["cash"]
        price_history = self.state.custom_state["price_history"]

        # P = P_last × (1 + κ × r)
        bid_price = price * (1 + self.KAPPA * ret)
        bid_price = max(1.0, bid_price)

        # Base quantity
        quantity = self.BETA * ret * cash / bid_price

        # Add acceleration (2nd derivative) bonus
        if len(price_history) >= 3:
            p1, p2, p3 = price_history[-3:]
            acceleration = (p3 - p2) - (p2 - p1)
            quantity += self.ACCEL_BONUS * acceleration

        quantity = max(-80, min(80, quantity))

        return bid_price, quantity
