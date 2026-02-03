"""
AlgorithmicMarket: Formula-based market mechanism using classic financial economics.

This class fully inherits from GeneralMarket and implements all its methods.

Implements:
- Geometric Brownian Motion (GBM) for price dynamics
- Walrasian auction for market clearing
- Price impact models (temporary & permanent)
- Dividend payments
- Supply/demand equilibrium
"""

import asyncio
import numpy as np
from typing import Any, List, Dict
from datetime import datetime
from collections import deque

from llmgt.communication.base import I2MMessage, M2IMessage
from llmgt.market import base
from llmgt.market.general import GeneralMarket


class AlgorithmicMarket(GeneralMarket):
    """
    Algorithmic market using classic financial economics formulas.

    Key features:
    1. GBM price process: dS = μS dt + σS dW
    2. Walrasian auction: finds price where supply = demand
    3. Price impact: temporary and permanent components
    4. Dividend payments (optional)
    """

    def __init__(self, config, investor_ids):
        """
        Initialize AlgorithmicMarket with configuration.
        """
        super().__init__(config, investor_ids)

        # Price Dynamics
        self.current_price = config.extras["initial_price"]
        self.initial_price = self.current_price

        # True market parameters
        self.true_drift = config.extras["true_drift"]
        self.true_volatility = config.extras["true_volatility"]
        self.risk_free_rate = config.extras["risk_free_rate"]

        # Time Discretization
        self.dt = config.extras["dt"]
        self.annual_trading_days = config.extras["annual_trading_days"]

        # Price Model
        self.price_model = config.extras["price_model"]

        # Market Structure
        self.clearing_mechanism = config.extras["clearing_mechanism"]

        # Supply
        self.total_shares_outstanding = config.extras["total_shares_outstanding"]
        self.supply_elasticity = config.extras["supply_elasticity"]

        # Market Maker
        self.has_market_maker = config.extras["has_market_maker"]
        self.market_maker_spread = config.extras["market_maker_spread"]
        self.market_maker_depth = config.extras["market_maker_depth"]

        # Dividends
        self.dividend_yield = config.extras["dividend_yield"]
        self.dividend_frequency = config.extras["dividend_frequency"]
        self.next_dividend_round = self._calculate_next_dividend_round()

        # Noise Traders
        self.noise_trader_fraction = config.extras["noise_trader_fraction"]
        self.noise_trader_volatility = config.extras["noise_trader_volatility"]

        # Price Impact
        self.temporary_impact_coef = config.extras["temporary_impact_coef"]
        self.temporary_impact_exponent = config.extras["temporary_impact_exponent"]
        self.permanent_impact_coef = config.extras["permanent_impact_coef"]

        # Auction Parameters
        self.auction_max_iterations = config.extras["auction_max_iterations"]
        self.auction_tolerance = config.extras["auction_tolerance"]
        self.derivative_epsilon = config.extras["derivative_epsilon"]
        self.min_price_multiplier = config.extras["min_price_multiplier"]
        self.max_price_multiplier = config.extras["max_price_multiplier"]

        # State Tracking
        self.price_history = deque(maxlen=config.extras["max_price_history"])
        self.price_history.append(self.current_price)

        self.volume_history = deque(maxlen=config.extras["max_volume_history"])
        self.spread_history = deque(maxlen=config.extras["max_volume_history"])

        self.total_volume = 0.0
        self.total_dividends_paid = 0.0

        # Investor holdings tracking
        self.investor_holdings = {}

        # Performance
        self.computation_delay = config.extras["computation_delay"]
        self.min_history_for_volatility = config.extras["min_history_for_volatility"]
        self.price_floor = config.extras["price_floor"]

    def _calculate_next_dividend_round(self) -> int:
        """Calculate when next dividend payment is due based on config."""
        if self.dividend_frequency == "quarterly":
            return int(self.annual_trading_days / 4)
        elif self.dividend_frequency == "monthly":
            return int(self.annual_trading_days / 12)
        elif self.dividend_frequency == "annual":
            return self.annual_trading_days
        else:
            return 999999

    def build_initial_m2i_messages(self, round_id: int) -> List[M2IMessage]:
        """
        Build initial messages to investors with market state.
        """
        if round_id == 1:
            decision_content = {
                "current_price": self.current_price,
                "round_index": 0,
                "volatility": self.true_volatility,
                "price_history": [self.current_price],
                "total_shares_outstanding": self.total_shares_outstanding,
                "dividend_yield": self.dividend_yield,
                "market_maker_spread": self.market_maker_spread,
                "risk_free_rate": self.risk_free_rate,
            }
        else:
            last_entry = self.history_entry[-1] if self.history_entry else None
            if last_entry:
                decision_content = last_entry["data"]["decision"]
            else:
                decision_content = {
                    "current_price": self.current_price,
                    "round_index": self._round_index,
                }

        messages = []
        for investor_id in self.investor_ids:
            msg = M2IMessage(
                market_id=self.identity,
                investor_id=investor_id,
                decision_content=decision_content,
                rule=f"Market state for round {round_id}",
            )
            messages.append(msg)

        return messages

    def _update_price_gbm(self):
        """
        Update price using Geometric Brownian Motion.
        """
        mu = self.true_drift
        sigma = self.true_volatility

        drift = (mu - 0.5 * sigma ** 2) * self.dt
        shock = np.random.randn()
        diffusion = sigma * np.sqrt(self.dt) * shock

        self.current_price *= np.exp(drift + diffusion)
        self.current_price = max(self.current_price, self.price_floor)

        self.price_history.append(self.current_price)

    def _compute_supply_curve(self, price: float) -> float:
        """
        Compute supply at given price.
        """
        price_ratio = price / self.initial_price
        supply = self.total_shares_outstanding * (price_ratio ** self.supply_elasticity)
        return supply

    @staticmethod
    def _compute_demand_from_orders(orders: List[Dict], price: float) -> float:
        """
        Compute total demand at given price from investor orders.
        """
        total_demand = 0.0

        for order in orders:
            if order["order_type"] == "market":
                total_demand += order["shares"]
            elif order["order_type"] == "limit":
                if order["side"] == "buy" and price <= order.get("limit_price", float('inf')):
                    total_demand += order["shares"]
                elif order["side"] == "sell" and price >= order.get("limit_price", 0):
                    total_demand -= order["shares"]

        return total_demand

    def _add_noise_trader_demand(self) -> float:
        """
        Add noise trader demand/supply.
        """
        if self.noise_trader_fraction == 0:
            return 0.0

        noise_volume = (
                self.noise_trader_fraction *
                self.total_shares_outstanding *
                np.random.randn() *
                self.noise_trader_volatility
        )

        return noise_volume

    def _compute_price_impact(self, order_flow: float, current_volume: float) -> Dict[str, float]:
        """
        Compute price impact from order flow.
        """
        if current_volume > 0 and self.temporary_impact_coef > 0:
            relative_size = abs(order_flow) / current_volume
            temporary_impact = (
                    self.temporary_impact_coef *
                    (relative_size ** self.temporary_impact_exponent)
            )
        else:
            temporary_impact = 0.0

        temporary_impact *= np.sign(order_flow)

        if self.permanent_impact_coef > 0:
            relative_to_float = order_flow / self.total_shares_outstanding
            permanent_impact = self.permanent_impact_coef * relative_to_float
        else:
            permanent_impact = 0.0

        return {
            "temporary": temporary_impact,
            "permanent": permanent_impact,
            "total": temporary_impact + permanent_impact
        }

    def _walrasian_auction(self, orders: List[Dict]) -> Dict[str, Any]:
        """
        Find market-clearing price using Walrasian auction.
        """
        noise_demand = self._add_noise_trader_demand()

        def excess_demand(price: float) -> float:
            demand = self._compute_demand_from_orders(orders, price) + noise_demand
            supply = self._compute_supply_curve(price)
            return demand - supply

        price_guess = self.current_price
        price_low = self.min_price_multiplier * self.current_price
        price_high = self.max_price_multiplier * self.current_price

        for iteration in range(self.auction_max_iterations):
            excess = excess_demand(price_guess)

            if abs(excess) < self.auction_tolerance:
                break

            epsilon = price_guess * self.derivative_epsilon
            excess_plus = excess_demand(price_guess + epsilon)
            derivative = (excess_plus - excess) / epsilon

            if abs(derivative) < 1e-10:
                if excess > 0:
                    price_low = price_guess
                    price_guess = (price_guess + price_high) / 2
                else:
                    price_high = price_guess
                    price_guess = (price_guess + price_low) / 2
            else:
                price_new = price_guess - excess / derivative
                price_new = np.clip(price_new, price_low, price_high)
                price_guess = price_new

        clearing_price = price_guess
        clearing_volume = self._compute_demand_from_orders(orders, clearing_price)

        net_order_flow = clearing_volume
        price_impact = self._compute_price_impact(net_order_flow, abs(clearing_volume))

        clearing_price *= (1 + price_impact["permanent"])

        return {
            "price": clearing_price,
            "volume": clearing_volume,
            "excess_demand": excess_demand(clearing_price),
            "price_impact": price_impact,
            "noise_demand": noise_demand,
        }

    def _allocate_shares(
            self,
            orders: List[Dict],
            clearing_price: float,
            clearing_volume: float
    ) -> Dict[str, Dict]:
        """
        Allocate shares to investors at clearing price.
        """
        allocations = {}

        for order in orders:
            investor_id = order["investor_id"]

            if order["order_type"] == "market":
                shares_allocated = order["shares"]
                allocation_price = clearing_price
            elif order["order_type"] == "limit":
                limit_price = order.get("limit_price", 0)
                if order["side"] == "buy" and clearing_price <= limit_price:
                    shares_allocated = order["shares"]
                    allocation_price = clearing_price
                elif order["side"] == "sell" and clearing_price >= limit_price:
                    shares_allocated = -order["shares"]
                    allocation_price = clearing_price
                else:
                    shares_allocated = 0
                    allocation_price = clearing_price
            else:
                shares_allocated = 0
                allocation_price = clearing_price

            if investor_id not in self.investor_holdings:
                self.investor_holdings[investor_id] = 0.0

            self.investor_holdings[investor_id] += shares_allocated

            allocations[investor_id] = {
                "shares": float(shares_allocated),
                "allocation_price": float(allocation_price),
                "total_cost": float(shares_allocated * allocation_price),
                "current_holdings": float(self.investor_holdings[investor_id]),
            }

        return allocations

    def _pay_dividends(self) -> Dict[str, float]:
        """
        Pay dividends to all shareholders.
        """
        if self._round_index < self.next_dividend_round or self.dividend_yield == 0:
            return {}

        if self.dividend_frequency == "quarterly":
            dividend_per_share = (self.dividend_yield / 4) * self.current_price
        elif self.dividend_frequency == "monthly":
            dividend_per_share = (self.dividend_yield / 12) * self.current_price
        elif self.dividend_frequency == "annual":
            dividend_per_share = self.dividend_yield * self.current_price
        else:
            dividend_per_share = 0.0

        dividend_payments = {}
        for investor_id, shares in self.investor_holdings.items():
            if shares > 0:
                payment = shares * dividend_per_share
                dividend_payments[investor_id] = payment
                self.total_dividends_paid += payment

        self.next_dividend_round = self._round_index + self._calculate_next_dividend_round()

        return dividend_payments

    async def decide(self, messages: List[I2MMessage]) -> base.MarketDecision:
        """
        Allow the Core market clearing logic.
        """
        message_received_time = datetime.now().isoformat()

        await asyncio.sleep(self.computation_delay)

        decision_start_time = datetime.now().isoformat()

        # Update price (GBM)
        if self._round_index > 0:
            self._update_price_gbm()

        # Extract orders
        orders = []
        for msg in messages:
            investor_id = msg.investor_id
            decision_content = msg.decision_content

            if hasattr(decision_content, "action"):
                action = decision_content.action
            elif isinstance(decision_content, dict):
                action = decision_content.get("action", {})
            else:
                continue

            order = {
                "investor_id": investor_id,
                "order_type": action.get("order_type", "market"),
                "shares": action.get("shares", 0.0),
                "price": action.get("price", self.current_price),
                "side": "buy" if action.get("shares", 0.0) > 0 else "sell",
                "limit_price": action.get("limit_price", None),
            }

            orders.append(order)

        # Run market clearing
        if self.clearing_mechanism == "walrasian_auction":
            clearing_result = self._walrasian_auction(orders)
        else:
            prices = [o["price"] for o in orders if o["price"] > 0]
            clearing_result = {
                "price": np.mean(prices) if prices else self.current_price,
                "volume": sum(abs(o["shares"]) for o in orders),
                "excess_demand": 0.0,
                "price_impact": {"temporary": 0.0, "permanent": 0.0, "total": 0.0},
                "noise_demand": 0.0,
            }

        self.current_price = clearing_result["price"]

        # Allocate shares
        allocations = self._allocate_shares(
            orders,
            clearing_result["price"],
            clearing_result["volume"]
        )

        # Pay dividends
        dividend_payments = self._pay_dividends()

        # Track statistics
        self.total_volume += abs(clearing_result["volume"])
        self.volume_history.append(clearing_result["volume"])

        if self.has_market_maker:
            bid_price = self.current_price * (1 - self.market_maker_spread / 2)
            ask_price = self.current_price * (1 + self.market_maker_spread / 2)
            spread = ask_price - bid_price
        else:
            bid_price = self.current_price
            ask_price = self.current_price
            spread = 0.0

        self.spread_history.append(spread)

        # Build reasoning
        prev_price = self.price_history[-2] if len(self.price_history) >= 2 else self.current_price
        price_change = (clearing_result['price'] / prev_price - 1) * 100

        reasoning = (
            f"📊 Market Clearing via {self.clearing_mechanism}\n"
            f"Previous Price: ${prev_price:.2f}\n"
            f"Clearing Price: ${clearing_result['price']:.2f} ({price_change:+.2f}%)\n"
            f"Volume: {clearing_result['volume']:.0f} shares\n"
            f"Price Impact: {clearing_result['price_impact']['total'] * 100:+.2f}%\n"
            f"Excess Demand: {clearing_result['excess_demand']:.0f} shares\n"
        )

        if self.has_market_maker:
            reasoning += f"Bid-Ask Spread: ${spread:.4f}\n"

        if dividend_payments:
            total_dividends = sum(dividend_payments.values())
            reasoning += f"💰 Dividends Paid: ${total_dividends:.2f}\n"

        # Calculate metrics
        if len(self.price_history) >= self.min_history_for_volatility:
            returns = np.diff(np.log(list(self.price_history)[-self.min_history_for_volatility:]))
            realized_vol = np.std(returns) * np.sqrt(self.annual_trading_days)
        else:
            realized_vol = self.true_volatility

        expected_price = self.initial_price * np.exp(
            self.true_drift * self._round_index * self.dt
        )
        price_deviation = abs(self.current_price - expected_price) / expected_price
        market_alignment = max(0.0, 1.0 - price_deviation)

        self._round_index += 1

        # Build decision
        decision = base.MarketDecision(
            reason=reasoning,
            clearing={
                "price": float(clearing_result["price"]),
                "volume": float(clearing_result["volume"]),
                "bid": float(bid_price),
                "ask": float(ask_price),
                "spread": float(spread),
                "excess_demand": float(clearing_result["excess_demand"]),
                "price_impact": clearing_result["price_impact"],
            },
            allocations=allocations,
            penalties={},
            market_alignment=market_alignment,
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=decision_start_time,
            additions={
                "realized_volatility": float(realized_vol),
                "expected_price": float(expected_price),
                "total_volume": float(self.total_volume),
                "dividend_payments": {k: float(v) for k, v in dividend_payments.items()},
                "total_dividends_paid": float(self.total_dividends_paid),
                "price_history": [float(p) for p in list(self.price_history)[-10:]],
                "clearing_mechanism": str(self.clearing_mechanism),
            }
        )

        decision.ensure_valid()
        return decision
