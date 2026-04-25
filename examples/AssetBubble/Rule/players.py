"""AssetBubble - Rule-based Asset Bubble Simulation

Phenomenon: Asset Bubbles
    Asset prices severely and persistently deviate from fundamental value,
    driven by speculative momentum and limited arbitrage forces.
    → simulation-bases.md §1

Theoretical Foundation:
    - Greater Fool Theory: Buy expensive expecting to sell higher
      → simulation-bases.md §2.1
    - Limits to Arbitrage (Shleifer & Vishny, 1997)
      → simulation-bases.md §2.2
    - Noise Trader Risk (De Long et al., 1990)
      → simulation-bases.md §2.3
    - Synchronization Risk (Abreu & Brunnermeier, 2003)
      → simulation-bases.md §2.4

Key Dynamics:
    1. Initial positive shock → Price rises above fundamental
    2. Momentum speculators chase returns → Further price increase
    3. Arbitrageurs attempt to short → But face constraints
    4. Noise traders follow the crowd → Amplify bubble
    5. Eventually bubble bursts when speculators run out
    → simulation-bases.md §3

All parameters are configured via players.yml config file.
    → simulation-bases.md §6
"""

import logging
import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("AssetBubble")


# =============================================================================
# Market - Coordinator with Bubble-Prone Dynamics
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with price dynamics favorable to bubble formation.
    → simulation-bases.md §3

    Price Model:
        P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + ε
        → simulation-bases.md §3.1

    Where:
        - λ: High price impact (amplifies demand effects)    → simulation-bases.md §6
        - γ: Low mean reversion (slow correction to fundamentals)  → simulation-bases.md §6
        - F: Fundamental value (grows slowly)               → simulation-bases.md §3.2

    The key to bubble formation:
        - High λ: Small excess demand causes big price moves
        - Low γ: Price doesn't quickly return to fundamental
        - This creates positive feedback loop
        → simulation-bases.md §3.3

    All parameters configured via extras in players.yml:
        - fundamental_value, initial_price                  → simulation-bases.md §6
        - price_impact, mean_reversion, fundamental_growth, noise_std  → simulation-bases.md §6
        - short_cost_rate, custom_state_hot_limit            → simulation-bases.md §6
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

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]

            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "fundamental"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["bubble_metric_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "bubble_metric"),
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
        current_fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]

        # Update fundamental value (slow growth)
        fundamental_growth = extras["fundamental_growth"]
        new_fundamental = current_fundamental * (1 + fundamental_growth)

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics - bubble prone
        price_impact = extras["price_impact"] * net_demand
        mean_reversion = extras["mean_reversion"] * (new_fundamental - current_price)
        noise = random.gauss(0, extras["noise_std"])

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
        logger.debug(f"\n{'='*70}")
        logger.debug(f"[Market] Round {round_num}")
        logger.debug(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)"
        )
        logger.debug(f"  Fundamental: {new_fundamental:.2f}")
        logger.debug(f"  Bubble Ratio: {bubble_ratio:.2f}x")
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            logger.debug(f"  Orders ({len(orders)}):")
            for o in orders:
                logger.debug(
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
            "short_cost_rate": extras["short_cost_rate"],
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
    Base class for bubble simulation investors.
    → simulation-bases.md §4

    All parameters configured via extras in players.yml:
        - initial_cash, initial_position, custom_state_hot_limit
        → simulation-bases.md §6
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
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["short_position"] = 0.0  # Shares borrowed & sold
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=extras["custom_state_hot_limit"],
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
    → simulation-bases.md §4 — MomentumSpeculator

    Theory: Greater Fool Theory
        Buy even if overvalued, expecting to sell to a "greater fool."
        → simulation-bases.md §2.1

    Behavior:
        - Only looks at price momentum, ignores fundamentals
        - Extremely low risk aversion
        - Uses leverage (larger positions)
        - Buys aggressively when price is rising

    Effect: STRONGLY DESTABILIZING - Primary bubble driver

    Formula:
        momentum = (price - MA_short) / MA_short
        quantity = aggressiveness × momentum × base_size
        → simulation-bases.md §4 — MomentumSpeculator (Rule-Based Behavior)

    Parameters from config extras:
        - lookback_short, aggressiveness, base_position_size, leverage_multiplier
        → simulation-bases.md §6
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        lookback_short = extras["lookback_short"]
        aggressiveness = extras["aggressiveness"]
        base_position_size = extras["base_position_size"]
        leverage_multiplier = extras["leverage_multiplier"]

        # Calculate momentum
        if len(price_history) >= lookback_short:
            recent_prices = list(price_history)[-lookback_short:]
            ma_short = sum(recent_prices) / len(recent_prices)
            momentum = (price - ma_short) / ma_short
        else:
            momentum = 0.0

        # Aggressive momentum chasing
        if momentum > 0.01:  # Price rising
            quantity = (
                aggressiveness * momentum * base_position_size * leverage_multiplier
            )
            quantity = min(quantity, 100)  # Cap at max
        elif momentum < -0.02:  # Price falling sharply - panic sell
            quantity = aggressiveness * momentum * base_position_size
            quantity = max(quantity, -80)
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        strategy_name = "momentum_speculator"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} mom={momentum:+.3f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
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
    → simulation-bases.md §4 — RationalArbitrageur

    Theory: Limits to Arbitrage (Shleifer & Vishny, 1997)
        - Arbitrageurs face constraints: short-selling costs, margin requirements
        - Cannot fully correct mispricings due to these limits
        - May be forced to close positions before prices correct
        → simulation-bases.md §2.2

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
        → simulation-bases.md §4 — RationalArbitrageur (Rule-Based Behavior)

    Parameters from config extras:
        - deviation_threshold, base_position_size, max_short_position, short_cost_sensitivity
        → simulation-bases.md §6
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        short_cost = market_data["short_cost_rate"]
        short_position = self.state.custom_state["short_position"]

        deviation_threshold = extras["deviation_threshold"]
        base_position_size = extras["base_position_size"]
        max_short_position = extras["max_short_position"]
        short_cost_sensitivity = extras["short_cost_sensitivity"]

        # Calculate mispricing
        deviation = (price - fundamental) / fundamental

        if deviation > deviation_threshold:
            # Overvalued - want to short
            # But face short-selling costs and limits
            if short_position < max_short_position:
                # Reduce position based on short cost
                cost_penalty = 1.0 - short_cost_sensitivity * short_cost * 10
                cost_penalty = max(0.2, cost_penalty)

                short_size = deviation * base_position_size * cost_penalty
                quantity = -min(short_size, max_short_position - short_position)
            else:
                quantity = 0.0  # Hit short limit

        elif deviation < -deviation_threshold:
            # Undervalued - buy
            buy_size = abs(deviation) * base_position_size
            quantity = min(buy_size, 30)
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        strategy_name = "rational_arbitrageur"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} dev={deviation:+.2%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}, "
            f"Short={short_position:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
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
    → simulation-bases.md §4 — NoiseTrader

    Theory: De Long et al. (1990) - Noise Trader Risk
        Uninformed traders who create systematic deviations from fundamental value.
        → simulation-bases.md §2.3

    Behavior:
        - Trades based on "sentiment" (random with bias)
        - Tends to follow recent price direction (herding)
        - Can amplify bubbles by joining buying frenzy
        - Sentiment can flip, causing sudden selling

    Effect: DESTABILIZING - Amplifies bubbles through herding

    Formula:
        total_sentiment = random_sentiment + herding_weight × price_return × 10
        → simulation-bases.md §4 — NoiseTrader (Rule-Based Behavior)

    Parameters from config extras:
        - sentiment_volatility, herding_weight, base_position_size
        → simulation-bases.md §6
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]

        sentiment_volatility = extras["sentiment_volatility"]
        herding_weight = extras["herding_weight"]
        base_position_size = extras["base_position_size"]

        # Generate sentiment: random + herding component
        random_sentiment = random.gauss(0, sentiment_volatility)
        herding_sentiment = herding_weight * price_return * 10  # Amplified

        total_sentiment = random_sentiment + herding_sentiment

        # Trade based on sentiment
        if total_sentiment > 0.1:
            quantity = total_sentiment * base_position_size
            quantity = min(quantity, 40)
        elif total_sentiment < -0.1:
            quantity = total_sentiment * base_position_size
            quantity = max(quantity, -40)
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        strategy_name = "noise_trader"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} sent={total_sentiment:+.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
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
    → simulation-bases.md §4 — FundamentalInvestor

    Theory: Traditional value investing
        → simulation-bases.md §2 (context: slow correction vs momentum forces)

    Behavior:
        - Compares price to fundamental value
        - Buys undervalued, sells overvalued
        - Very patient, trades slowly
        - Provides weak anchoring force

    Effect: WEAKLY STABILIZING - Too slow to prevent bubbles

    Formula:
        deviation = (fundamental - price) / price
        quantity = value_sensitivity × deviation × base_position_size  (every N rounds)
        → simulation-bases.md §4 — FundamentalInvestor (Rule-Based Behavior)

    Parameters from config extras:
        - trade_frequency, value_sensitivity, base_position_size
        → simulation-bases.md §6
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        trade_frequency = extras["trade_frequency"]
        value_sensitivity = extras["value_sensitivity"]
        base_position_size = extras["base_position_size"]

        # Only trade at certain frequency
        if round_num % trade_frequency != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            deviation = (fundamental - price) / price

            # Trade based on deviation
            quantity = value_sensitivity * deviation * base_position_size
            quantity = max(-15, min(15, quantity))
            bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        strategy_name = "fundamental_investor"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
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
    → simulation-bases.md §4 — LeveragedBuyer

    Theory: Leverage amplifies both gains and losses
        During bubbles, leveraged buyers amplify upside
        During crashes, forced deleveraging amplifies downside
        → simulation-bases.md §2 (context: synchronization risk and crash dynamics)

    Behavior:
        - Uses leverage to increase position sizes
        - Faces margin calls when prices fall
        - Forced to sell during downturns (procyclical)

    Effect: STRONGLY DESTABILIZING - Amplifies both bubbles and crashes

    Formula:
        equity_ratio = portfolio_value / initial_equity
        If equity_ratio < margin_call_threshold: forced deleverage (sell 50%)
        Else: quantity = price_return × base_position_size × leverage_ratio
        → simulation-bases.md §4 — LeveragedBuyer (Rule-Based Behavior)

    Parameters from config extras:
        - leverage_ratio, margin_call_threshold, base_position_size, initial_equity
        → simulation-bases.md §6
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        position = self.state.custom_state["position"]
        cash = self.state.custom_state["cash"]

        leverage_ratio = extras["leverage_ratio"]
        margin_call_threshold = extras["margin_call_threshold"]
        base_position_size = extras["base_position_size"]
        initial_equity = extras["initial_equity"]

        # Calculate current equity and leverage
        portfolio_value = cash + position * price
        equity_ratio = portfolio_value / initial_equity

        # Check for margin call
        if equity_ratio < margin_call_threshold and position > 0:
            # Forced to deleverage - sell everything
            quantity = -position * 0.5  # Sell half
            logger.debug(f"    [MARGIN CALL] Forced deleveraging!")
        else:
            # Normal leveraged buying on positive momentum
            if price_return > 0.005:
                quantity = price_return * base_position_size * leverage_ratio
                quantity = min(quantity, 60)
            elif price_return < -0.01:
                quantity = price_return * base_position_size
                quantity = max(quantity, -40)
            else:
                quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        strategy_name = "leveraged_buyer"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} eq_ratio={equity_ratio:.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
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
    → simulation-bases.md §4 — ConservativeHolder

    Behavior:
        - Holds steady position
        - Rarely trades
        - Provides small stabilizing force
        - Rebalances slowly

    Effect: VERY WEAKLY STABILIZING

    Formula:
        gap = target_position - position
        quantity = gap × rebalance_rate  (every N rounds, capped at ±10)
        → simulation-bases.md §4 — ConservativeHolder (Rule-Based Behavior)

    Parameters from config extras:
        - target_position, rebalance_frequency, rebalance_rate
        → simulation-bases.md §6
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        target_position = extras["target_position"]
        rebalance_frequency = extras["rebalance_frequency"]
        rebalance_rate = extras["rebalance_rate"]

        # Only rebalance occasionally
        if round_num % rebalance_frequency != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            # Slowly move toward target
            gap = target_position - position
            quantity = gap * rebalance_rate
            quantity = max(-10, min(10, quantity))
            bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        strategy_name = "conservative_holder"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }
