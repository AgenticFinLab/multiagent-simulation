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
"""

import os
import random
import math
from typing import Any, Dict, List, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market - Coordinator with Price Dynamics
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with momentum-aware dynamics.

    Price Model:
        P(t+1) = P(t) + λ × NetDemand + γ × [F(t) - P(t)] + ε

    Fundamental value drifts slowly to create momentum opportunity.
    """

    INITIAL_PRICE = 100.0
    INITIAL_FUNDAMENTAL = 100.0

    PRICE_IMPACT = 0.08
    MEAN_REVERSION = 0.01  # Slow - allows momentum to persist
    NOISE_STD = 0.3

    # Fundamental drift (creates momentum opportunities)
    DRIFT_PERSISTENCE = 0.95  # Autocorrelated drift
    DRIFT_VOLATILITY = 0.5

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
                "record_path", "EXPERIMENT/MomentumEffect/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["fundamental"] = self.INITIAL_FUNDAMENTAL
            self.state.custom_state["drift"] = 0.0

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "return"),
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
        fundamental = self.state.custom_state["fundamental"]
        drift = self.state.custom_state["drift"]
        orders = self.state.custom_state["orders"]

        # Update fundamental with persistent drift (creates momentum)
        new_drift = self.DRIFT_PERSISTENCE * drift + random.gauss(
            0, self.DRIFT_VOLATILITY
        )
        new_fundamental = fundamental + new_drift

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (new_fundamental - current_price)
        noise = random.gauss(0, self.NOISE_STD)

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

        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(f"  Fundamental: {new_fundamental:.2f}")
        print(f"  5-Round Momentum: {momentum_5*100:+.2f}%")
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  Orders ({len(orders)}):")
            for o in orders:
                print(
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
    """Base class for all investors."""

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
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/MomentumEffect/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "returns"),
                entry_limit=self.HISTORY_LIMIT,
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
        Q = SCALE × signal × (max_position - current_position) if signal > threshold

    Financial Theory:
        - Conservatism Bias: Investors underreact to news
        - Information Diffusion: News spreads gradually
        - Self-attribution Bias: Winners attribute success to skill
    """

    STRATEGY_NAME = "momentum_trader"
    LOOKBACK_WINDOW = 5
    MOMENTUM_THRESHOLD = 0.02  # 2% threshold
    SCALE = 3.0  # Aggressiveness
    MAX_POSITION = 100.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position, 0)

        price = market_data["price"]
        momentum = market_data["momentum_5"]
        self.state.custom_state["return_history"].append(market_data["return"])

        # Momentum signal
        signal = momentum
        quantity = 0.0

        if signal > self.MOMENTUM_THRESHOLD:
            # BUY winner
            buy_capacity = (cash / price) * 0.8
            target = min(buy_capacity, self.MAX_POSITION - position)
            quantity = self.SCALE * signal * target
            quantity = max(0, min(quantity, buy_capacity))
        elif signal < -self.MOMENTUM_THRESHOLD:
            # SELL loser
            sell_capacity = position * 0.8
            quantity = self.SCALE * signal * sell_capacity
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

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
            f"Q={quantity:+8.2f} mom={signal*100:+.1f}% | "
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

    def _hold_order(self, round_num, cash, position, momentum):
        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
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
    """

    STRATEGY_NAME = "contrarian_trader"
    REVERSION_THRESHOLD = 0.03  # 3% deviation
    SCALE = 2.0
    MAX_POSITION = 80.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position)

        price = market_data["price"]
        momentum = market_data["momentum_5"]

        # Contrarian: opposite of momentum
        signal = -momentum
        quantity = 0.0

        if abs(signal) > self.REVERSION_THRESHOLD:
            if signal > 0:  # Buy losers
                buy_capacity = (cash / price) * 0.6
                target = min(buy_capacity, self.MAX_POSITION - position)
                quantity = self.SCALE * signal * target
                quantity = max(0, min(quantity, buy_capacity))
            else:  # Sell winners
                sell_capacity = position * 0.6
                quantity = self.SCALE * signal * sell_capacity
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

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
            f"Q={quantity:+8.2f} signal={signal*100:+.1f}% | "
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
        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
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
# IndexFund - Passive Baseline
# =============================================================================


class IndexFund(BaseInvestor):
    """
    Passive Index Fund:
        Maintains fixed allocation regardless of momentum
        Serves as baseline for performance comparison
    """

    STRATEGY_NAME = "index_fund"
    TARGET_ALLOCATION = 0.6  # 60% equity
    REBALANCE_THRESHOLD = 0.05  # 5% deviation triggers rebalance

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
        current_allocation = equity_value / total_value if total_value > 0 else 0

        deviation = current_allocation - self.TARGET_ALLOCATION
        quantity = 0.0

        if abs(deviation) > self.REBALANCE_THRESHOLD:
            # Rebalance
            target_equity = total_value * self.TARGET_ALLOCATION
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

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
            f"Q={quantity:+8.2f} alloc={current_allocation*100:.1f}% | "
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
# MarketMaker - Liquidity Provider
# =============================================================================


class MarketMaker(BaseInvestor):
    """
    Market Maker providing liquidity.
    Mean-reverts inventory to zero.
    """

    STRATEGY_NAME = "market_maker"
    INVENTORY_TARGET = 0.0
    REVERSION_SPEED = 0.2

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position)

        price = market_data["price"]

        # Revert to target inventory
        deviation = position - self.INVENTORY_TARGET
        quantity = -self.REVERSION_SPEED * deviation

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

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
            f"Q={quantity:+8.2f} [MM] | "
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
# TechnicalTrader - Moving Average Crossover
# =============================================================================


class TechnicalTrader(BaseInvestor):
    """
    Technical Analysis: Moving Average Crossover
        Buy when short MA > long MA (golden cross)
        Sell when short MA < long MA (death cross)
    """

    STRATEGY_NAME = "technical_trader"
    SHORT_WINDOW = 3
    LONG_WINDOW = 10
    SCALE = 2.0
    MAX_POSITION = 60.0

    INITIAL_POSITION = 20.0  # Start with some position

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position)

        price = market_data["price"]

        # Store price for MA calculation
        if "ma_prices" not in self.state.custom_state:
            self.state.custom_state["ma_prices"] = []
        self.state.custom_state["ma_prices"].append(price)

        # Keep limited history
        if len(self.state.custom_state["ma_prices"]) > self.LONG_WINDOW:
            self.state.custom_state["ma_prices"] = self.state.custom_state["ma_prices"][
                -self.LONG_WINDOW :
            ]

        prices = self.state.custom_state["ma_prices"]
        quantity = 0.0

        if len(prices) >= self.LONG_WINDOW:
            short_ma = sum(prices[-self.SHORT_WINDOW :]) / self.SHORT_WINDOW
            long_ma = sum(prices) / len(prices)

            signal = (short_ma - long_ma) / long_ma

            if signal > 0.01:  # Golden cross
                buy_capacity = (cash / price) * 0.5
                target = min(buy_capacity, self.MAX_POSITION - position)
                quantity = self.SCALE * signal * target
                quantity = max(0, min(quantity, buy_capacity))
            elif signal < -0.01:  # Death cross
                sell_capacity = position * 0.5
                quantity = self.SCALE * signal * sell_capacity
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

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
            f"Q={quantity:+8.2f} | "
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
# FundamentalTrader - Value Anchor
# =============================================================================


class FundamentalTrader(BaseInvestor):
    """
    Fundamental Analysis: Trade toward intrinsic value.
    Provides weak stabilizing force against momentum.
    """

    STRATEGY_NAME = "fundamental_trader"
    VALUE_THRESHOLD = 0.05  # 5% mispricing
    SCALE = 1.5
    MAX_POSITION = 50.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        if market_data is None:
            return self._hold_order(round_num, cash, position)

        price = market_data["price"]
        fundamental = market_data["fundamental"]

        # Value signal: positive if undervalued
        mispricing = (fundamental - price) / price
        quantity = 0.0

        if mispricing > self.VALUE_THRESHOLD:
            # Undervalued - buy
            buy_capacity = (cash / price) * 0.5
            target = min(buy_capacity, self.MAX_POSITION - position)
            quantity = self.SCALE * mispricing * target
            quantity = max(0, min(quantity, buy_capacity))
        elif mispricing < -self.VALUE_THRESHOLD:
            # Overvalued - sell
            sell_capacity = position * 0.5
            quantity = self.SCALE * mispricing * sell_capacity
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

        print(
            f"[{self.config.identity:24s}] R{round_num} ({self.STRATEGY_NAME:16s}): "
            f"Q={quantity:+8.2f} misp={mispricing*100:+.1f}% | "
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
