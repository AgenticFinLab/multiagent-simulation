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

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("VolatilityClustering")


class Market(GeneralPlayer):
    """
    Central market with volatility-aware price dynamics.

    Price Model (simplified for multi-agent):
        P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + σ(t) × ε

    Volatility follows a simplified GARCH(1,1):
        σ²(t) = ω + α × r²(t-1) + β × σ²(t-1)

    Parameters from config extras:
        - fundamental_value, initial_price, price_impact, mean_reversion
        - garch_omega, garch_alpha, garch_beta
        - min_volatility, max_volatility, custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["volatility"] = 1.0  # Initial volatility
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
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        current_vol = self.state.custom_state["volatility"]
        prev_return = self.state.custom_state["prev_return"]
        orders = self.state.custom_state["orders"]

        fundamental_value = extras["fundamental_value"]
        price_impact = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        garch_omega = extras["garch_omega"]
        garch_alpha = extras["garch_alpha"]
        garch_beta = extras["garch_beta"]
        min_volatility = extras["min_volatility"]
        max_volatility = extras["max_volatility"]

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
            garch_omega + garch_alpha * (prev_return**2) + garch_beta * (current_vol**2)
        )
        new_vol = math.sqrt(new_variance)
        new_vol = max(min_volatility, min(max_volatility, new_vol))

        # Price dynamics
        price_impact_effect = price_impact * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, new_vol)

        new_price = max(
            1.0, current_price + price_impact_effect + mean_reversion + noise
        )
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
        logger.debug(f"\n{'='*70}")
        logger.debug(f"[Market] Round {round_num}")
        logger.debug(f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)")
        logger.debug(f"  Volatility: {current_vol:.3f} → {new_vol:.3f}")
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            logger.debug(f"  Orders ({len(orders)}):")
            for o in orders:
                logger.debug(
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


class BaseInvestor(GeneralPlayer):
    """
    Base class for volatility clustering investors.

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path
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
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=custom_state_hot_limit,
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


class Fundamentalist(BaseInvestor):
    """
    Fundamentalist investor with slow mean reversion behavior.

    Parameters from config extras:
        - trade_frequency, value_sensitivity, base_position_size, value_noise_std
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
        value_noise_std = extras["value_noise_std"]
        strategy_name = self.__class__.__name__

        # Only trade at certain frequency (slow)
        if round_num % trade_frequency != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            # Add noise to value estimation (uncertainty)
            estimated_value = fundamental + random.gauss(0, value_noise_std)

            # Calculate deviation
            deviation = (estimated_value - price) / price  # Positive = undervalued

            # Conservative position sizing
            quantity = value_sensitivity * deviation * base_position_size
            quantity = max(-20, min(20, quantity))  # Limit size

            # Bid at current price (market order approximation)
            bid_price = price

            # Apply constraints
            quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
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


class TrendFollower(BaseInvestor):
    """
    Trend-following investor with high volatility sensitivity.

    Parameters from config extras:
        - lookback_window, base_position_size, volatility_sensitivity
        - baseline_volatility, trend_threshold
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = market_data["volatility"]
        price_history = self.state.custom_state["price_history"]

        lookback_window = extras["lookback_window"]
        base_position_size = extras["base_position_size"]
        volatility_sensitivity = extras["volatility_sensitivity"]
        baseline_volatility = extras["baseline_volatility"]
        trend_threshold = extras["trend_threshold"]
        strategy_name = self.__class__.__name__

        # Calculate recent trend
        if len(price_history) >= lookback_window:
            recent_prices = list(price_history)[-lookback_window:]
            ma = sum(recent_prices) / len(recent_prices)
            trend = (price - ma) / ma  # Normalized trend
        else:
            trend = 0.0

        # Volatility-adjusted position sizing
        vol_ratio = volatility / baseline_volatility
        vol_multiplier = 1.0 + volatility_sensitivity * (vol_ratio - 1.0)
        vol_multiplier = max(0.5, min(2.0, vol_multiplier))  # Clamp

        # Trade if trend is significant
        if abs(trend) > trend_threshold:
            direction = 1.0 if trend > 0 else -1.0
            strength = min(abs(trend) / 0.05, 1.0)  # Normalize strength
            quantity = direction * base_position_size * strength * vol_multiplier
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        # Apply constraints
        quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f} vol_mult={vol_multiplier:.2f} | "
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


class NoiseTrader(BaseInvestor):
    """
    Noise trader providing random liquidity.

    Parameters from config extras:
        - position_volatility, mean_reversion_speed
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        position_volatility = extras["position_volatility"]
        mean_reversion_speed = extras["mean_reversion_speed"]
        strategy_name = self.__class__.__name__

        # Random component
        random_trade = random.gauss(0, position_volatility)

        # Mean reversion component (slowly reduce extreme positions)
        reversion = -mean_reversion_speed * position

        quantity = random_trade + reversion
        quantity = max(-30, min(30, quantity))  # Limit size
        bid_price = price if quantity != 0 else 0.0

        # Apply constraints
        quantity = self._apply_constraints(bid_price, quantity, price)

        # Execute trade
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
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


class SlowAdapter(BaseInvestor):
    """
    Conservative investor with slow information processing.

    Parameters from config extras:
        - lookback_window, update_weight, base_position_size
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        price_history = self.state.custom_state["price_history"]

        lookback_window = extras["lookback_window"]
        update_weight = extras["update_weight"]
        base_position_size = extras["base_position_size"]
        strategy_name = self.__class__.__name__

        # Calculate long-term average
        if len(price_history) >= lookback_window:
            recent_prices = list(price_history)[-lookback_window:]
            long_ma = sum(recent_prices) / len(recent_prices)
        else:
            long_ma = price

        # Blended value estimate (slow update)
        estimated_value = update_weight * fundamental + (1 - update_weight) * long_ma

        # Calculate signal
        deviation = (estimated_value - price) / price

        # Conservative trading
        if abs(deviation) > 0.02:  # Only trade on significant deviations
            quantity = deviation * base_position_size
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

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
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


class VolatilityTrader(BaseInvestor):
    """
    Volatility regime trader - sells in high vol, buys in low vol.

    Parameters from config extras:
        - vol_lookback, high_vol_threshold, low_vol_threshold, base_position_size
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = market_data["volatility"]
        vol_history = self.state.custom_state["volatility_history"]

        vol_lookback = extras["vol_lookback"]
        high_vol_threshold = extras["high_vol_threshold"]
        low_vol_threshold = extras["low_vol_threshold"]
        base_position_size = extras["base_position_size"]
        strategy_name = self.__class__.__name__

        # Calculate average volatility
        if len(vol_history) >= vol_lookback:
            recent_vols = list(vol_history)[-vol_lookback:]
            avg_vol = sum(recent_vols) / len(recent_vols)
        else:
            avg_vol = volatility

        # Volatility ratio
        vol_ratio = volatility / avg_vol if avg_vol > 0 else 1.0

        # Trading signal based on volatility regime
        if vol_ratio > high_vol_threshold:
            # High volatility - reduce exposure (sell)
            quantity = -base_position_size * (vol_ratio - 1.0)
            bid_price = price
        elif vol_ratio < low_vol_threshold:
            # Low volatility - increase exposure (buy)
            quantity = base_position_size * (1.0 - vol_ratio)
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

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f} vol_ratio={vol_ratio:.2f} | "
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
