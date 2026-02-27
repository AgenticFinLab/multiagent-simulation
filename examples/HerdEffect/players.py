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

All parameters are configured via players.yml config file.
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

    All parameters configured via extras in players.yml:
        - initial_price, fundamental_value, supply_elasticity
        - mean_reversion, noise_std, history_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize on first round
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["price"] = extras["initial_price"]

            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            history_limit = extras["history_limit"]

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=history_limit,
                initial_values=[extras["initial_price"]],
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=history_limit,
                initial_values=[0],
            )
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "return"),
                entry_limit=history_limit,
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
        extras = self.config.extras
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
        supply_elasticity = extras["supply_elasticity"]
        price_impact = supply_elasticity * net_demand

        # Mean reversion toward fundamental
        fundamental_value = extras["fundamental_value"]
        mean_reversion_rate = extras["mean_reversion"]
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)

        # Market noise
        noise_std = extras["noise_std"]
        noise = random.gauss(0, noise_std)

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
    - cash: Available capital (starts at initial_cash)
    - position: Current holdings (starts at initial_position)
    - price_history: Track recent prices for volatility calculation (HistoryBuffer)

    All parameters configured via extras in players.yml:
        - initial_cash, initial_position, history_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            history_limit = extras["history_limit"]

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=history_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=history_limit,
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

        strategy_name = self.__class__.__name__
        print(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:20s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
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
        λ = price aggressiveness (lambda_price)
        β = capital allocation ratio (beta)

    Behavior: Buys when price rises, sells when price falls.
    Effect: DESTABILIZING - amplifies trends, creates momentum bubbles.

    Parameters from config extras:
        - lambda_price, beta
    """

    def calculate_bid(self) -> tuple:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        ret = market_data["return"]
        cash = self.state.custom_state["cash"]

        lambda_price = extras["lambda_price"]
        beta = extras["beta"]

        # P = P_last × (1 + λ × r)
        bid_price = price * (1 + lambda_price * ret)
        bid_price = max(1.0, bid_price)

        # Q = β × r × cash / P
        quantity = beta * ret * cash / bid_price

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
        F = fundamental value
        β = value sensitivity (beta)

    Behavior: Buys when price < fundamental, sells when price > fundamental.
    Effect: STABILIZING - dampens trends, provides mean reversion.

    Parameters from config extras:
        - fundamental, beta, noise_std
    """

    def calculate_bid(self) -> tuple:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        cash = self.state.custom_state["cash"]

        fundamental = extras["fundamental"]
        beta = extras["beta"]
        noise_std = extras["noise_std"]

        # P = F + ε (bid around fundamental)
        bid_price = fundamental + random.gauss(0, noise_std)
        bid_price = max(1.0, bid_price)

        # Q = β × (F - P) / P × cash / bid_price
        deviation = (fundamental - price) / price
        quantity = beta * deviation * cash / bid_price

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
        k = risk tolerance coefficient

    Behavior: Reduces position when volatility is high.
    Effect: Can trigger early exit from bubble (sell before crash).

    Parameters from config extras:
        - k, lookback
    """

    def calculate_bid(self) -> tuple:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        cash = self.state.custom_state["cash"]
        price_history = self.state.custom_state["price_history"]
        position = self.state.custom_state["position"]

        k = extras["k"]
        lookback = extras["lookback"]

        # Calculate variance
        if len(price_history) >= lookback:
            recent = price_history[-lookback:]
            variance = np.var(recent)
        else:
            variance = 1.0  # Default low variance

        # Avoid division by zero
        variance = max(variance, 0.1)

        # P = P_last (market price)
        bid_price = price

        # Q = k / σ² × cash / P
        # Position sizing inversely proportional to variance
        target_value = k / variance * cash
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
        σ_price = price noise
        σ_qty = quantity noise
        mean_reversion = position mean reversion

    Behavior: Random trading, provides liquidity.
    Effect: Can accidentally trigger herd behavior when momentum traders
            misinterpret random noise as signal.

    Parameters from config extras:
        - price_noise_std, qty_noise_std, position_mean_reversion
    """

    def calculate_bid(self) -> tuple:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        price_noise_std = extras["price_noise_std"]
        qty_noise_std = extras["qty_noise_std"]
        position_mean_reversion = extras["position_mean_reversion"]

        # P ~ N(P_last, σ²)
        bid_price = price + random.gauss(0, price_noise_std)
        bid_price = max(1.0, bid_price)

        # Q ~ N(0, σ²) - position × mean_reversion
        random_qty = random.gauss(0, qty_noise_std)
        mean_reversion = -position * position_mean_reversion
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
        κ = aggressive price factor (kappa)
        β = aggressive allocation (beta)
        acceleration = second derivative of price

    Behavior: Amplified momentum with acceleration bonus.
    Effect: EXTREMELY DESTABILIZING - can create rapid bubbles.

    Parameters from config extras:
        - kappa, beta, accel_bonus
    """

    def calculate_bid(self) -> tuple:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        ret = market_data["return"]
        cash = self.state.custom_state["cash"]
        price_history = self.state.custom_state["price_history"]

        kappa = extras["kappa"]
        beta = extras["beta"]
        accel_bonus = extras["accel_bonus"]

        # P = P_last × (1 + κ × r)
        bid_price = price * (1 + kappa * ret)
        bid_price = max(1.0, bid_price)

        # Base quantity
        quantity = beta * ret * cash / bid_price

        # Add acceleration (2nd derivative) bonus
        if len(price_history) >= 3:
            p1, p2, p3 = price_history[-3:]
            acceleration = (p3 - p2) - (p2 - p1)
            quantity += accel_bonus * acceleration

        quantity = max(-80, min(80, quantity))

        return bid_price, quantity
