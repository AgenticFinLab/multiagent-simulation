"""DispositionEffect - Prospect Theory Trading Simulation Players

Phenomenon: Disposition Effect (Shefrin & Statman 1985)
    - Investors sell winners too early (realize gains prematurely)
    - Investors hold losers too long (reluctant to realize losses)

Theoretical Foundation:
    - Prospect Theory (Kahneman & Tversky 1979)
    - Loss Aversion: λ ≈ 2.25 (losses hurt 2.25x more than gains feel good)
    - Reference Point: Purchase price as psychological anchor
    - S-shaped value function: Concave for gains, convex for losses

Investor Types:
    - DispositionInvestor: Exhibits disposition effect (behavioral)
    - RationalInvestor: Expected utility maximizer (rational baseline)
    - TaxAwareInvestor: Considers tax implications (sells losers for tax loss)
    - IndexHolder: Passive buy-and-hold
    - InstitutionalInvestor: Professional, less prone to disposition

Market Implications:
    - Underreaction to news (momentum)
    - Volume higher after price increases
    - Predictable selling pressure at gain thresholds
"""

import os
import random
import math
from typing import Any, Dict, List, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market - Coordinator
# =============================================================================


class Market(GeneralPlayer):
    """Central market with standard price dynamics."""

    INITIAL_PRICE = 100.0
    FUNDAMENTAL_VALUE = 100.0
    PRICE_IMPACT = 0.06
    MEAN_REVERSION = 0.015
    NOISE_STD = 0.4

    # Random news shocks (creates gain/loss situations)
    NEWS_PROBABILITY = 0.15
    NEWS_IMPACT_RANGE = 5.0

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
                "record_path", "EXPERIMENT/DispositionEffect/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
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
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Random news shock
        news_shock = 0.0
        if random.random() < self.NEWS_PROBABILITY:
            news_shock = random.uniform(-self.NEWS_IMPACT_RANGE, self.NEWS_IMPACT_RANGE)

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(
            1.0, current_price + price_impact + mean_reversion + noise + news_shock
        )
        price_return = (new_price - current_price) / current_price

        # Update
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        if news_shock != 0:
            print(f"  NEWS SHOCK: {news_shock:+.2f}")
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:24s} [{o['strategy']:20s}]: Q={o['quantity']:+8.2f}"
                )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "news_shock": news_shock,
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
# Base Investor with Reference Point Tracking
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """Base class with purchase price (reference point) tracking."""

    STRATEGY_NAME = "base"
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 30.0  # Start with position to create gain/loss
    INITIAL_PURCHASE_PRICE = 100.0  # Reference point
    HISTORY_LIMIT = 50

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["purchase_price"] = self.INITIAL_PURCHASE_PRICE
            self.state.custom_state["total_cost"] = (
                self.INITIAL_POSITION * self.INITIAL_PURCHASE_PRICE
            )

        market_data = None
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                break
        self.state.custom_state["market_data"] = market_data

    def update_reference_point(self, quantity: float, price: float):
        """Update average purchase price (reference point) after trade."""
        position = self.state.custom_state["position"]
        total_cost = self.state.custom_state["total_cost"]

        if quantity > 0:  # Buy - adjust average cost
            new_cost = quantity * price
            total_cost += new_cost
            position += quantity
            if position > 0:
                self.state.custom_state["purchase_price"] = total_cost / position
        elif quantity < 0:  # Sell - remove at average cost
            if position > 0:
                cost_per_share = total_cost / position
                total_cost -= abs(quantity) * cost_per_share
            position += quantity

        self.state.custom_state["position"] = position
        self.state.custom_state["total_cost"] = max(0, total_cost)

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# DispositionInvestor - Exhibits Disposition Effect
# =============================================================================


class DispositionInvestor(BaseInvestor):
    """
    Disposition Effect Investor (Prospect Theory):

    Behavior:
        - Sells winners quickly (gain threshold ~10%)
        - Holds losers stubbornly (loss threshold ~30%)

    Value Function (Prospect Theory):
        V(x) = x^α           if x ≥ 0  (gains, α ≈ 0.88)
        V(x) = -λ(-x)^β      if x < 0  (losses, β ≈ 0.88, λ ≈ 2.25)

    This creates asymmetric treatment of gains vs losses.
    """

    STRATEGY_NAME = "disposition_investor"
    GAIN_THRESHOLD = 0.10  # Sell at 10% gain
    LOSS_THRESHOLD = -0.30  # Only sell at 30% loss
    LOSS_AVERSION = 2.25  # λ parameter
    SELL_FRACTION_GAIN = 0.6  # Sell 60% when gain threshold hit
    SELL_FRACTION_LOSS = 0.2  # Reluctantly sell only 20% at loss

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position, purchase_price)

        price = market_data["price"]

        # Calculate gain/loss relative to reference point
        if purchase_price > 0:
            gain_loss = (price - purchase_price) / purchase_price
        else:
            gain_loss = 0

        quantity = 0.0
        action = "HOLD"

        # Disposition effect logic
        if gain_loss >= self.GAIN_THRESHOLD and position > 0:
            # SELL WINNERS quickly (realize gains)
            quantity = -position * self.SELL_FRACTION_GAIN
            action = "SELL_WINNER"
        elif gain_loss <= self.LOSS_THRESHOLD and position > 0:
            # Reluctantly sell losers
            quantity = -position * self.SELL_FRACTION_LOSS
            action = "SELL_LOSER"
        elif gain_loss > 0.02 and position < 50:
            # Small buy when slightly positive
            buy_capacity = (cash / price) * 0.1
            quantity = min(buy_capacity, 5)
            action = "BUY"

        # Execute trade
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, price)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} [{action:12s}] g/l={gain_loss*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }

    def _hold_order(self, round_num, cash, position, ref_price):
        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q=   +0.00 [NO DATA]"
        )
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }


# =============================================================================
# RationalInvestor - Expected Utility Maximizer
# =============================================================================


class RationalInvestor(BaseInvestor):
    """
    Rational Investor (Baseline):

    Makes decisions based on expected future returns,
    NOT affected by sunk costs or reference points.
    Rebalances to optimal allocation regardless of gain/loss.
    """

    STRATEGY_NAME = "rational_investor"
    TARGET_ALLOCATION = 0.5
    REBALANCE_THRESHOLD = 0.1

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position)

        price = market_data["price"]

        # Calculate current allocation
        equity_value = position * price
        total_value = cash + equity_value
        current_alloc = equity_value / total_value if total_value > 0 else 0

        deviation = current_alloc - self.TARGET_ALLOCATION
        quantity = 0.0

        # Rebalance regardless of gain/loss
        if abs(deviation) > self.REBALANCE_THRESHOLD:
            target_equity = total_value * self.TARGET_ALLOCATION
            target_position = target_equity / price
            quantity = (target_position - position) * 0.5

        # Execute
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, price)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} alloc={current_alloc*100:.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }

    def _hold_order(self, round_num, cash, position):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }


# =============================================================================
# TaxAwareInvestor - Tax Loss Harvesting
# =============================================================================


class TaxAwareInvestor(BaseInvestor):
    """
    Tax-Aware Investor:

    Opposite of disposition effect for tax optimization:
    - Sells losers to harvest tax losses
    - Holds winners to defer capital gains tax
    """

    STRATEGY_NAME = "tax_aware_investor"
    TAX_LOSS_THRESHOLD = -0.05  # Sell at 5% loss for tax benefit
    CAPITAL_GAINS_HOLD = 0.20  # Hold until 20% gain (deferral benefit)

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position)

        price = market_data["price"]

        if purchase_price > 0:
            gain_loss = (price - purchase_price) / purchase_price
        else:
            gain_loss = 0

        quantity = 0.0
        action = "HOLD"

        if gain_loss <= self.TAX_LOSS_THRESHOLD and position > 0:
            # Tax loss harvesting - SELL losers
            quantity = -position * 0.5
            action = "TAX_HARVEST"
        elif gain_loss >= self.CAPITAL_GAINS_HOLD:
            # Hold winners for tax deferral (opposite of disposition)
            action = "DEFER_GAINS"

        # Execute
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, price)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} [{action:12s}] g/l={gain_loss*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }

    def _hold_order(self, round_num, cash, position):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }


# =============================================================================
# IndexHolder - Passive Baseline
# =============================================================================


class IndexHolder(BaseInvestor):
    """Passive buy-and-hold investor (no active trading)."""

    STRATEGY_NAME = "index_holder"
    INITIAL_POSITION = 50.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        price = market_data["price"] if market_data else 0

        # Pure hold - no trading
        quantity = 0.0

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} [HOLD] | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }


# =============================================================================
# InstitutionalInvestor - Professional (Less Disposition)
# =============================================================================


class InstitutionalInvestor(BaseInvestor):
    """
    Institutional Investor:

    Professional money managers show weaker disposition effect
    due to training, oversight, and fiduciary duty.
    """

    STRATEGY_NAME = "institutional_investor"
    # Weaker disposition thresholds
    GAIN_THRESHOLD = 0.25  # Hold longer than retail
    LOSS_THRESHOLD = -0.15  # Cut losses earlier than retail
    SELL_FRACTION = 0.4

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position)

        price = market_data["price"]

        if purchase_price > 0:
            gain_loss = (price - purchase_price) / purchase_price
        else:
            gain_loss = 0

        quantity = 0.0
        action = "HOLD"

        # More rational thresholds
        if gain_loss >= self.GAIN_THRESHOLD and position > 0:
            quantity = -position * self.SELL_FRACTION
            action = "TAKE_PROFIT"
        elif gain_loss <= self.LOSS_THRESHOLD and position > 0:
            quantity = -position * self.SELL_FRACTION
            action = "CUT_LOSS"

        # Execute
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, price)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} [{action:12s}] g/l={gain_loss*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }

    def _hold_order(self, round_num, cash, position):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "target": "market",
                }
            ],
        }
