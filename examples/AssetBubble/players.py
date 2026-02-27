"""AssetBubble - Rule-based Asset Bubble Simulation

Phenomenon: Asset Bubbles
    Asset prices severely and persistently deviate from fundamental value,
    driven by speculative momentum and limited arbitrage forces.

Theoretical Foundation:
    - Greater Fool Theory: Buy expensive expecting to sell higher
    - Limits to Arbitrage (Shleifer & Vishny, 1997)
    - Noise Trader Risk (De Long et al., 1990)
    - Synchronization Risk (Abreu & Brunnermeier, 2003)

Key Dynamics:
    1. Initial positive shock → Price rises above fundamental
    2. Momentum speculators chase returns → Further price increase
    3. Arbitrageurs attempt to short → But face constraints
    4. Noise traders follow the crowd → Amplify bubble
    5. Eventually bubble bursts when speculators run out
"""

import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market - Coordinator with Bubble-Prone Dynamics
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with price dynamics favorable to bubble formation.

    Price Model:
        P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + ε

    Where:
        - λ: High price impact (amplifies demand effects)
        - γ: Low mean reversion (slow correction to fundamentals)
        - F: Fundamental value (grows slowly)

    The key to bubble formation:
        - High λ: Small excess demand causes big price moves
        - Low γ: Price doesn't quickly return to fundamental
        - This creates positive feedback loop
    """

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0

    # Bubble-prone parameters
    PRICE_IMPACT = 0.15  # High: demand strongly affects price
    MEAN_REVERSION = 0.005  # Low: slow correction to fundamental
    FUNDAMENTAL_GROWTH = 0.001  # Slow fundamental appreciation
    NOISE_STD = 0.3

    # Short selling constraints (for arbitrageurs)
    SHORT_COST_RATE = 0.02  # Cost of borrowing shares to short

    HISTORY_LIMIT = 300

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["fundamental"] = self.FUNDAMENTAL_VALUE

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "fundamental"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["bubble_metric_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "bubble_metric"),
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
        current_fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]

        # Update fundamental value (slow growth)
        new_fundamental = current_fundamental * (1 + self.FUNDAMENTAL_GROWTH)

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics - bubble prone
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (new_fundamental - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        return_pct = price_return * 100

        # Bubble metric: Price / Fundamental
        bubble_ratio = new_price / new_fundamental

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental

        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["fundamental_history"].append(new_fundamental)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["bubble_metric_history"].append(bubble_ratio)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)")
        print(f"  Fundamental: {new_fundamental:.2f}")
        print(f"  Bubble Ratio: {bubble_ratio:.2f}x")
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:25s} [{o['strategy']:20s}]: Q={o['quantity']:+8.2f}"
                )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": return_pct,
            "fundamental": new_fundamental,
            "bubble_ratio": bubble_ratio,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "short_cost_rate": self.SHORT_COST_RATE,
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
    """Base class for bubble simulation investors."""

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

        if "cash" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["short_position"] = 0.0  # Shares borrowed & sold
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        """Apply cash/position constraints."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:  # Buying
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:  # Selling (including short selling)
            # Can sell what we own + limited short selling
            max_sellable = position + 50  # Allow some short selling
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
            if abs(quantity) <= self.state.custom_state["position"]:
                self.state.custom_state["position"] += quantity
            else:
                # Short selling
                sold_long = self.state.custom_state["position"]
                short_qty = abs(quantity) - sold_long
                self.state.custom_state["position"] = 0
                self.state.custom_state["short_position"] += short_qty

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Momentum Speculator - Bubble Driver
# =============================================================================


class MomentumSpeculator(BaseInvestor):
    """
    Momentum speculator that drives bubble formation.

    Theory: Greater Fool Theory
        Buy even if overvalued, expecting to sell to a "greater fool."

    Behavior:
        - Only looks at price momentum, ignores fundamentals
        - Extremely low risk aversion
        - Uses leverage (larger positions)
        - Buys aggressively when price is rising

    Effect: STRONGLY DESTABILIZING - Primary bubble driver

    Formula:
        momentum = (price - MA_short) / MA_short
        quantity = aggressiveness × momentum × base_size
    """

    STRATEGY_NAME = "momentum_speculator"

    # Speculator parameters - very aggressive
    LOOKBACK_SHORT = 3
    AGGRESSIVENESS = 2.0  # High: amplifies momentum signals
    BASE_POSITION_SIZE = 50.0  # Large positions
    LEVERAGE_MULTIPLIER = 1.5  # Uses leverage

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        # Calculate momentum
        if len(price_history) >= self.LOOKBACK_SHORT:
            recent_prices = list(price_history)[-self.LOOKBACK_SHORT :]
            ma_short = sum(recent_prices) / len(recent_prices)
            momentum = (price - ma_short) / ma_short
        else:
            momentum = 0.0

        # Aggressive momentum chasing
        if momentum > 0.01:  # Price rising
            quantity = (
                self.AGGRESSIVENESS
                * momentum
                * self.BASE_POSITION_SIZE
                * self.LEVERAGE_MULTIPLIER
            )
            quantity = min(quantity, 100)  # Cap at max
        elif momentum < -0.02:  # Price falling sharply - panic sell
            quantity = self.AGGRESSIVENESS * momentum * self.BASE_POSITION_SIZE
            quantity = max(quantity, -80)
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} mom={momentum:+.3f} | "
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
# Rational Arbitrageur - Limited Corrective Force
# =============================================================================


class RationalArbitrageur(BaseInvestor):
    """
    Rational arbitrageur attempting to correct mispricings.

    Theory: Limits to Arbitrage (Shleifer & Vishny, 1997)
        - Arbitrageurs face constraints: short-selling costs, margin requirements
        - Cannot fully correct mispricings due to these limits
        - May be forced to close positions before prices correct

    Behavior:
        - Estimates true value (fundamental)
        - Shorts when price > fundamental (but faces costs)
        - Buys when price < fundamental
        - Limited by capital and short-selling costs

    Effect: WEAKLY STABILIZING - Cannot stop bubbles due to constraints

    Formula:
        deviation = (price - fundamental) / fundamental
        If deviation > threshold: short (with cost penalty)
        If deviation < -threshold: buy
    """

    STRATEGY_NAME = "rational_arbitrageur"

    # Arbitrageur parameters - conservative due to constraints
    DEVIATION_THRESHOLD = 0.10  # Only act on >10% deviation
    BASE_POSITION_SIZE = 25.0  # Moderate size (limited capital)
    MAX_SHORT_POSITION = 40.0  # Limited short capacity
    SHORT_COST_SENSITIVITY = 0.5  # How much short cost affects decision

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        short_cost = market_data["short_cost_rate"]
        short_position = self.state.custom_state["short_position"]

        # Calculate mispricing
        deviation = (price - fundamental) / fundamental

        if deviation > self.DEVIATION_THRESHOLD:
            # Overvalued - want to short
            # But face short-selling costs and limits
            if short_position < self.MAX_SHORT_POSITION:
                # Reduce position based on short cost
                cost_penalty = 1.0 - self.SHORT_COST_SENSITIVITY * short_cost * 10
                cost_penalty = max(0.2, cost_penalty)

                short_size = deviation * self.BASE_POSITION_SIZE * cost_penalty
                quantity = -min(short_size, self.MAX_SHORT_POSITION - short_position)
            else:
                quantity = 0.0  # Hit short limit

        elif deviation < -self.DEVIATION_THRESHOLD:
            # Undervalued - buy
            buy_size = abs(deviation) * self.BASE_POSITION_SIZE
            quantity = min(buy_size, 30)
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} dev={deviation:+.2%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}, "
            f"Short={short_position:+8.2f}"
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
# Noise Trader - Crowd Follower
# =============================================================================


class NoiseTrader(BaseInvestor):
    """
    Noise trader driven by sentiment and crowd behavior.

    Theory: De Long et al. (1990) - Noise Trader Risk
        Uninformed traders who create systematic deviations from fundamental value.

    Behavior:
        - Trades based on "sentiment" (random with bias)
        - Tends to follow recent price direction (herding)
        - Can amplify bubbles by joining buying frenzy
        - Sentiment can flip, causing sudden selling

    Effect: DESTABILIZING - Amplifies bubbles through herding
    """

    STRATEGY_NAME = "noise_trader"

    # Noise trader parameters
    SENTIMENT_VOLATILITY = 0.3
    HERDING_WEIGHT = 0.6  # How much to follow recent returns
    BASE_POSITION_SIZE = 20.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]

        # Generate sentiment: random + herding component
        random_sentiment = random.gauss(0, self.SENTIMENT_VOLATILITY)
        herding_sentiment = self.HERDING_WEIGHT * price_return * 10  # Amplified

        total_sentiment = random_sentiment + herding_sentiment

        # Trade based on sentiment
        if total_sentiment > 0.1:
            quantity = total_sentiment * self.BASE_POSITION_SIZE
            quantity = min(quantity, 40)
        elif total_sentiment < -0.1:
            quantity = total_sentiment * self.BASE_POSITION_SIZE
            quantity = max(quantity, -40)
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} sent={total_sentiment:+.2f} | "
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
# Fundamental Investor - Weak Anchor
# =============================================================================


class FundamentalInvestor(BaseInvestor):
    """
    Fundamental investor anchoring to intrinsic value.

    Theory: Traditional value investing

    Behavior:
        - Compares price to fundamental value
        - Buys undervalued, sells overvalued
        - Very patient, trades slowly
        - Provides weak anchoring force

    Effect: WEAKLY STABILIZING - Too slow to prevent bubbles
    """

    STRATEGY_NAME = "fundamental_investor"

    # Fundamental parameters - conservative
    TRADE_FREQUENCY = 5  # Trade every N rounds
    VALUE_SENSITIVITY = 0.3
    BASE_POSITION_SIZE = 15.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        # Only trade at certain frequency
        if round_num % self.TRADE_FREQUENCY != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            deviation = (fundamental - price) / price

            # Trade based on deviation
            quantity = self.VALUE_SENSITIVITY * deviation * self.BASE_POSITION_SIZE
            quantity = max(-15, min(15, quantity))
            bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
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
# Leveraged Buyer - Amplified Bubble Driver
# =============================================================================


class LeveragedBuyer(BaseInvestor):
    """
    Leveraged buyer using margin to amplify positions.

    Theory: Leverage amplifies both gains and losses
        During bubbles, leveraged buyers amplify upside
        During crashes, forced deleveraging amplifies downside

    Behavior:
        - Uses leverage to increase position sizes
        - Faces margin calls when prices fall
        - Forced to sell during downturns (procyclical)

    Effect: STRONGLY DESTABILIZING - Amplifies both bubbles and crashes
    """

    STRATEGY_NAME = "leveraged_buyer"

    # Leveraged parameters
    LEVERAGE_RATIO = 2.0  # 2x leverage
    MARGIN_CALL_THRESHOLD = 0.3  # Forced sell if equity drops 30%
    BASE_POSITION_SIZE = 40.0
    INITIAL_EQUITY = 10000.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        position = self.state.custom_state["position"]
        cash = self.state.custom_state["cash"]

        # Calculate current equity and leverage
        portfolio_value = cash + position * price
        equity_ratio = portfolio_value / self.INITIAL_EQUITY

        # Check for margin call
        if equity_ratio < self.MARGIN_CALL_THRESHOLD and position > 0:
            # Forced to deleverage - sell everything
            quantity = -position * 0.5  # Sell half
            print(f"    [MARGIN CALL] Forced deleveraging!")
        else:
            # Normal leveraged buying on positive momentum
            if price_return > 0.005:
                quantity = price_return * self.BASE_POSITION_SIZE * self.LEVERAGE_RATIO
                quantity = min(quantity, 60)
            elif price_return < -0.01:
                quantity = price_return * self.BASE_POSITION_SIZE
                quantity = max(quantity, -40)
            else:
                quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} eq_ratio={equity_ratio:.2f} | "
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
# Conservative Holder - Stability Provider
# =============================================================================


class ConservativeHolder(BaseInvestor):
    """
    Conservative long-term holder providing stability.

    Behavior:
        - Holds steady position
        - Rarely trades
        - Provides small stabilizing force
        - Rebalances slowly

    Effect: VERY WEAKLY STABILIZING
    """

    STRATEGY_NAME = "conservative_holder"

    # Conservative parameters
    TARGET_POSITION = 20.0  # Target holding
    REBALANCE_FREQUENCY = 10  # Rebalance every N rounds
    REBALANCE_RATE = 0.2  # Slowly rebalance

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        # Only rebalance occasionally
        if round_num % self.REBALANCE_FREQUENCY != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            # Slowly move toward target
            gap = self.TARGET_POSITION - position
            quantity = gap * self.REBALANCE_RATE
            quantity = max(-10, min(10, quantity))
            bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
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
