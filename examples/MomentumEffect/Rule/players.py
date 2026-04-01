"""MomentumEffect - Momentum Trading Simulation Players

Phenomenon: Momentum Effect
    - Past winners continue to outperform (positive momentum)
    - Past losers continue to underperform (negative momentum)
    - 3-12 month formation, 3-12 month holding period typical

Theoretical Foundation:
    - Jegadeesh & Titman (1993): Original momentum documentation
    - Conservatism Bias: Underreaction to new information
    - Information Diffusion: Gradual incorporation of information

Investor Types:
    - MomentumTrader: Buys past winners, sells past losers
    - ContrarianTrader: Mean reversion (opposing force)
    - IndexFund: Passive baseline
    - MarketMaker: Liquidity provision
    - TechnicalTrader: Moving average crossover
    - FundamentalTrader: Value-based anchor

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
import math
from collections import deque
from typing import Any, Dict, List, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("MomentumEffect")


# =============================================================================
# Market - Coordinator with Price Dynamics
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with momentum-aware dynamics.

    Price Model:
        P(t+1) = P(t) + λ × NetDemand + γ × [F(t) - P(t)] + ε

    Fundamental value drifts slowly to create momentum opportunity.

    Parameters from config extras:
        - initial_price, initial_fundamental
        - price_impact, mean_reversion, noise_std
        - drift_persistence, drift_volatility
        - custom_state_hot_limit, record_path
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
            self.state.custom_state["fundamental"] = extras["initial_fundamental"]
            self.state.custom_state["drift"] = 0.0

            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "return"),
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
        fundamental = self.state.custom_state["fundamental"]
        drift = self.state.custom_state["drift"]
        orders = self.state.custom_state["orders"]

        # Update fundamental with persistent drift (creates momentum)
        drift_persistence = extras["drift_persistence"]
        drift_volatility = extras["drift_volatility"]
        new_drift = drift_persistence * drift + random.gauss(0, drift_volatility)
        new_fundamental = fundamental + new_drift

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact_rate = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        noise_std = extras["noise_std"]

        price_impact = price_impact_rate * net_demand
        mean_reversion = mean_reversion_rate * (new_fundamental - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (
            (new_price - current_price) / current_price if current_price > 0 else 0
        )

        # Calculate momentum signal (past 5-round return)
        price_history = self.state.custom_state["price_history"]
        recent_prices = list(price_history)[-6:]
        if len(recent_prices) >= 2:
            momentum_5 = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        else:
            momentum_5 = 0.0

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["drift"] = new_drift
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["return_history"].append(price_return)

        logger.debug(f"\n{'='*70}")
        logger.debug(f"[Market] Round {round_num}")
        logger.debug(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(f"  Fundamental: {new_fundamental:.2f}")
        logger.debug(f"  5-Round Momentum: {momentum_5*100:+.2f}%")
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            logger.debug(f"  Orders ({len(orders)}):")
            for o in orders:
                logger.debug(
                    f"    {o['investor']:20s} [{o['strategy']:16s}]: Q={o['quantity']:+8.2f}"
                )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "fundamental": new_fundamental,
            "momentum_5": momentum_5,
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
# Base Investor
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """
    Base class for all investors.

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

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "returns"),
                entry_limit=custom_state_hot_limit,
            )

        market_data = None
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                break
        self.state.custom_state["market_data"] = market_data

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# MomentumTrader - Jegadeesh & Titman Strategy
# =============================================================================


class MomentumTrader(BaseInvestor):
    """
    Momentum Strategy (Jegadeesh & Titman 1993):
        Buy assets with positive past returns (winners)
        Sell assets with negative past returns (losers)

    Formula:
        signal = weighted average of past N returns
        Q = scale × signal × (max_position - current_position) if signal > threshold

    Financial Theory:
        - Conservatism Bias: Investors underreact to news
        - Information Diffusion: News spreads gradually
        - Self-attribution Bias: Winners attribute success to skill

    Parameters from config extras:
        - lookback_window, momentum_threshold, scale, max_position
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        momentum = market_data["momentum_5"]
        self.state.custom_state["return_history"].append(market_data["return"])

        momentum_threshold = extras["momentum_threshold"]
        scale = extras["scale"]
        max_position = extras["max_position"]

        # Momentum signal
        signal = momentum
        quantity = 0.0

        if signal > momentum_threshold:
            # BUY winner
            buy_capacity = (cash / price) * 0.8
            target = min(buy_capacity, max_position - position)
            quantity = scale * signal * target
            quantity = max(0, min(quantity, buy_capacity))
        elif signal < -momentum_threshold:
            # SELL loser
            sell_capacity = position * 0.8
            quantity = scale * signal * sell_capacity
            quantity = max(-sell_capacity, min(0, quantity))

        # Update position
        if quantity > 0:
            cost = quantity * price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q={quantity:+8.2f} mom={signal*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _hold_order(self, round_num, strategy_name):
        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q=   +0.00 [NO DATA]"
        )
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


# =============================================================================
# ContrarianTrader - Mean Reversion
# =============================================================================


class ContrarianTrader(BaseInvestor):
    """
    Contrarian Strategy (De Bondt & Thaler 1985):
        Buy past losers, sell past winners
        Exploits overreaction hypothesis

    Financial Theory:
        - Overreaction: Markets overshoot and correct
        - Mean reversion: Prices return to fundamentals

    Parameters from config extras:
        - reversion_threshold, scale, max_position
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        momentum = market_data["momentum_5"]

        reversion_threshold = extras["reversion_threshold"]
        scale = extras["scale"]
        max_position = extras["max_position"]

        # Contrarian: opposite of momentum
        signal = -momentum
        quantity = 0.0

        if abs(signal) > reversion_threshold:
            if signal > 0:  # Buy losers
                buy_capacity = (cash / price) * 0.6
                target = min(buy_capacity, max_position - position)
                quantity = scale * signal * target
                quantity = max(0, min(quantity, buy_capacity))
            else:  # Sell winners
                sell_capacity = position * 0.6
                quantity = scale * signal * sell_capacity
                quantity = max(-sell_capacity, min(0, quantity))

        # Update
        if quantity > 0:
            cost = quantity * price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q={quantity:+8.2f} signal={signal*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _hold_order(self, round_num, strategy_name):
        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q=   +0.00 [NO DATA]"
        )
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


# =============================================================================
# IndexFund - Passive Baseline
# =============================================================================


class IndexFund(BaseInvestor):
    """
    Passive Index Fund:
        Maintains fixed allocation regardless of momentum
        Serves as baseline for performance comparison

    Parameters from config extras:
        - target_allocation, rebalance_threshold
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]

        target_allocation = extras["target_allocation"]
        rebalance_threshold = extras["rebalance_threshold"]

        # Calculate current allocation
        equity_value = position * price
        total_value = cash + equity_value
        current_allocation = equity_value / total_value if total_value > 0 else 0

        deviation = current_allocation - target_allocation
        quantity = 0.0

        if abs(deviation) > rebalance_threshold:
            # Rebalance
            target_equity = total_value * target_allocation
            target_position = target_equity / price
            quantity = (target_position - position) * 0.5  # Gradual rebalance

        # Update
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.state.custom_state["position"] += quantity
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.state.custom_state["position"] += quantity
            else:
                quantity = 0

        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q={quantity:+8.2f} alloc={current_allocation*100:.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _hold_order(self, round_num, strategy_name):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


# =============================================================================
# MarketMaker - Liquidity Provider
# =============================================================================


class MarketMaker(BaseInvestor):
    """
    Market Maker providing liquidity.
    Mean-reverts inventory to zero.

    Parameters from config extras:
        - inventory_target, reversion_speed
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]

        inventory_target = extras["inventory_target"]
        reversion_speed = extras["reversion_speed"]

        # Revert to target inventory
        deviation = position - inventory_target
        quantity = -reversion_speed * deviation

        # Apply constraints
        if quantity > 0:
            max_buy = cash / price * 0.5
            quantity = min(quantity, max_buy)
        elif quantity < 0:
            max_sell = position * 0.5
            quantity = max(quantity, -max_sell)

        # Update
        if quantity > 0:
            cost = quantity * price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q={quantity:+8.2f} [MM] | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _hold_order(self, round_num, strategy_name):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


# =============================================================================
# TechnicalTrader - Moving Average Crossover
# =============================================================================


class TechnicalTrader(BaseInvestor):
    """
    Technical Analysis: Moving Average Crossover
        Buy when short MA > long MA (golden cross)
        Sell when short MA < long MA (death cross)

    Parameters from config extras:
        - short_window, long_window, scale, max_position
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]

        short_window = extras["short_window"]
        long_window = extras["long_window"]
        scale = extras["scale"]
        max_position = extras["max_position"]

        # Store price for MA calculation (deque auto-caps at long_window)
        if "ma_prices" not in self.state.custom_state:
            self.state.custom_state["ma_prices"] = deque(maxlen=long_window)
        self.state.custom_state["ma_prices"].append(price)

        prices = list(self.state.custom_state["ma_prices"])
        quantity = 0.0

        if len(prices) >= long_window:
            short_ma = sum(prices[-short_window:]) / short_window
            long_ma = sum(prices) / len(prices)

            signal = (short_ma - long_ma) / long_ma

            if signal > 0.01:  # Golden cross
                buy_capacity = (cash / price) * 0.5
                target = min(buy_capacity, max_position - position)
                quantity = scale * signal * target
                quantity = max(0, min(quantity, buy_capacity))
            elif signal < -0.01:  # Death cross
                sell_capacity = position * 0.5
                quantity = scale * signal * sell_capacity
                quantity = max(-sell_capacity, min(0, quantity))

        # Update
        if quantity > 0:
            cost = quantity * price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _hold_order(self, round_num, strategy_name):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


# =============================================================================
# FundamentalTrader - Value Anchor
# =============================================================================


class FundamentalTrader(BaseInvestor):
    """
    Fundamental Analysis: Trade toward intrinsic value.
    Provides weak stabilizing force against momentum.

    Parameters from config extras:
        - value_threshold, scale, max_position
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        fundamental = market_data["fundamental"]

        value_threshold = extras["value_threshold"]
        scale = extras["scale"]
        max_position = extras["max_position"]

        # Value signal: positive if undervalued
        mispricing = (fundamental - price) / price
        quantity = 0.0

        if mispricing > value_threshold:
            # Undervalued - buy
            buy_capacity = (cash / price) * 0.5
            target = min(buy_capacity, max_position - position)
            quantity = scale * mispricing * target
            quantity = max(0, min(quantity, buy_capacity))
        elif mispricing < -value_threshold:
            # Overvalued - sell
            sell_capacity = position * 0.5
            quantity = scale * mispricing * sell_capacity
            quantity = max(-sell_capacity, min(0, quantity))

        # Update
        if quantity > 0:
            cost = quantity * price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.config.identity:24s}] R{round_num} ({strategy_name:16s}): "
            f"Q={quantity:+8.2f} misp={mispricing*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _hold_order(self, round_num, strategy_name):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }
