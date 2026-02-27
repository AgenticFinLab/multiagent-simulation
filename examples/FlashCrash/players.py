"""FlashCrash - Market Microstructure Simulation

Phenomenon: Flash Crash
    - Extreme rapid price decline (can be 5-10% in minutes)
    - Caused by algorithmic trading feedback loops
    - Liquidity withdrawal amplifies the crash
    - Quick recovery as fundamental traders step in

Theoretical Foundation:
    - Market Microstructure Theory
    - Kirilenko et al. (2017) - The Flash Crash
    - SEC/CFTC Flash Crash Report (2010)

Architecture:
    - Market: Coordinator with liquidity-sensitive pricing
    - HighFrequencyTrader: Rapid momentum, can trigger cascades
    - MarketMaker: Provides liquidity, but withdraws in stress
    - AlgorithmicTrader: Trend-following algorithm
    - StopLossTrader: Triggered selling at price thresholds
    - FundamentalTrader: Stabilizing, buys during crash
    - RetailTrader: Slow, delayed reaction

Key Flash Crash Mechanism:
    1. Initial selling pressure (can be random or external)
    2. HFTs detect momentum → start selling
    3. Stop-losses triggered → cascade selling
    4. Market makers withdraw liquidity
    5. Price collapses in near-vacuum
    6. Fundamental traders recognize value → buy
    7. Price recovers
"""

import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market - Coordinator with Liquidity-Sensitive Pricing
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with liquidity-sensitive pricing.

    Key feature: Price impact increases when liquidity is low.
    This creates the "air pocket" effect during flash crashes.
    """

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0

    # Normal price dynamics
    BASE_PRICE_IMPACT = 0.05
    MEAN_REVERSION = 0.02
    NOISE_STD = 0.3

    # Liquidity sensitivity
    LOW_LIQUIDITY_THRESHOLD = 50.0
    HIGH_IMPACT_MULTIPLIER = 3.0  # Price impact multiplier when liquidity is low

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
                "record_path", "EXPERIMENT/FlashCrash/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["liquidity"] = 100.0  # Initial liquidity level
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=self.HISTORY_LIMIT,
            )

        # Collect orders
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
                        "provides_liquidity": order["provides_liquidity"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Calculate liquidity (market maker contribution)
        liquidity_provision = sum(
            abs(o["quantity"]) for o in orders if o["provides_liquidity"]
        )
        base_liquidity = 50.0  # Base market liquidity
        total_liquidity = base_liquidity + liquidity_provision

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Liquidity-adjusted price impact
        if total_liquidity < self.LOW_LIQUIDITY_THRESHOLD:
            liquidity_factor = self.HIGH_IMPACT_MULTIPLIER
        else:
            liquidity_factor = (
                1.0 + (self.LOW_LIQUIDITY_THRESHOLD / total_liquidity - 1.0) * 0.5
            )

        price_impact = self.BASE_PRICE_IMPACT * net_demand * liquidity_factor
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["liquidity_history"].append(total_liquidity)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(
            f"  Liquidity: {total_liquidity:.1f}, Impact Factor: {liquidity_factor:.2f}"
        )
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "liquidity": total_liquidity,
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
# Base Investor
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """Base class for flash crash investors."""

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
                "record_path", "EXPERIMENT/FlashCrash/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0 and bid_price > 0:
            max_affordable = cash / bid_price
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    def _execute_trade(self, bid_price: float, quantity: float) -> None:
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
# HighFrequencyTrader - Can Trigger Cascades
# =============================================================================


class HighFrequencyTrader(BaseInvestor):
    """
    High-frequency trader with rapid momentum detection.

    Behavior:
        - Detects very short-term price movements
        - Trades aggressively in direction of movement
        - Can trigger or amplify flash crashes

    Reference: Kirilenko et al. (2017)
    """

    STRATEGY_NAME = "hft"

    LOOKBACK = 2  # Very short lookback
    MOMENTUM_SENSITIVITY = 3.0  # High sensitivity to momentum
    BASE_POSITION_SIZE = 40.0
    SPEED_ADVANTAGE = 1.5  # Trades faster/larger than others

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        price_history = self.state.custom_state["price_history"]

        # Very short-term momentum
        if len(price_history) >= self.LOOKBACK:
            recent = list(price_history)[-self.LOOKBACK :]
            short_momentum = (
                (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
            )
        else:
            short_momentum = price_return

        # Aggressive momentum trading
        signal = short_momentum * self.MOMENTUM_SENSITIVITY
        quantity = signal * self.BASE_POSITION_SIZE * self.SPEED_ADVANTAGE
        quantity = max(-60, min(60, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:10s}): "
            f"Q={quantity:+8.2f} mom={short_momentum*100:+.2f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# MarketMaker - Provides Liquidity, Withdraws in Stress
# =============================================================================


class MarketMaker(BaseInvestor):
    """
    Market maker providing liquidity.

    Behavior:
        - Provides two-sided quotes
        - WITHDRAWS when volatility is high (key flash crash mechanism)
        - Creates liquidity vacuum during stress

    Reference: SEC/CFTC Flash Crash Report (2010)
    """

    STRATEGY_NAME = "market_maker"

    VOLATILITY_THRESHOLD = 0.02  # Withdraw above this volatility
    BASE_LIQUIDITY = 30.0
    SPREAD_SENSITIVITY = 0.5

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = abs(market_data["return"])
        position = self.state.custom_state["position"]

        # Withdraw liquidity during high volatility
        if price_return > self.VOLATILITY_THRESHOLD:
            # HIGH VOLATILITY - WITHDRAW
            provides_liquidity = False
            quantity = -position * 0.3 if position > 0 else 0  # Reduce exposure
            quantity = max(-20, min(20, quantity))
            bid_price = price if quantity != 0 else 0.0
            print(f"  [MM] WITHDRAWING - volatility too high ({price_return*100:.1f}%)")
        else:
            # Normal operation - provide liquidity
            provides_liquidity = True
            # Mean revert position to zero
            quantity = -position * 0.2
            quantity = max(-self.BASE_LIQUIDITY, min(self.BASE_LIQUIDITY, quantity))
            bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:10s}): "
            f"Q={quantity:+8.2f} liq={'YES' if provides_liquidity else 'NO'}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "provides_liquidity": provides_liquidity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# AlgorithmicTrader - Trend Following Algorithm
# =============================================================================


class AlgorithmicTrader(BaseInvestor):
    """
    Algorithmic trend-following trader.

    Similar to HFT but with slightly longer horizon.
    """

    STRATEGY_NAME = "algo"

    LOOKBACK = 3
    TREND_SENSITIVITY = 2.0
    BASE_POSITION_SIZE = 25.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        if len(price_history) >= self.LOOKBACK:
            recent = list(price_history)[-self.LOOKBACK :]
            trend = (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
        else:
            trend = 0.0

        quantity = trend * self.TREND_SENSITIVITY * self.BASE_POSITION_SIZE * 10
        quantity = max(-40, min(40, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:10s}): "
            f"Q={quantity:+8.2f} trend={trend*100:+.2f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# StopLossTrader - Triggered Selling at Price Thresholds
# =============================================================================


class StopLossTrader(BaseInvestor):
    """
    Trader with stop-loss orders.

    Behavior:
        - Holds position normally
        - Sells ALL when price drops below stop level
        - Creates cascade selling during crashes

    This is a key mechanism in flash crashes!
    """

    STRATEGY_NAME = "stop_loss"

    STOP_LOSS_PERCENT = 0.05  # Sell if price drops 5% from recent high
    INITIAL_POSITION = 50.0
    HISTORY_LIMIT = 20

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        await super().perceive(observation, prev_result)

        # Initialize with a position
        if "initialized_position" not in self.state.custom_state:
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["cash"] -= (
                self.INITIAL_POSITION * 100
            )  # Bought at 100
            self.state.custom_state["initialized_position"] = True

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]
        position = self.state.custom_state["position"]

        # Find recent high
        if len(price_history) >= 5:
            recent_high = max(list(price_history)[-10:])
        else:
            recent_high = price

        # Check stop-loss trigger
        stop_price = recent_high * (1 - self.STOP_LOSS_PERCENT)

        if price < stop_price and position > 0:
            # STOP-LOSS TRIGGERED - SELL ALL
            quantity = -position
            bid_price = price
            print(f"  [STOP-LOSS TRIGGERED] Price {price:.2f} < Stop {stop_price:.2f}")
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:10s}): "
            f"Q={quantity:+8.2f} pos={self.state.custom_state['position']:.1f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# FundamentalTrader - Stabilizing Force
# =============================================================================


class FundamentalTrader(BaseInvestor):
    """
    Fundamental value trader - provides recovery force.

    Behavior:
        - Buys when price significantly below fundamental
        - Helps market recover from flash crash
    """

    STRATEGY_NAME = "fundamental"

    VALUE_THRESHOLD = 0.10  # Buy when 10% below fundamental
    BASE_POSITION_SIZE = 30.0
    VALUE_SENSITIVITY = 1.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        # Calculate mispricing
        deviation = (fundamental - price) / fundamental

        if deviation > self.VALUE_THRESHOLD:
            # Price significantly below fundamental - BUY
            quantity = deviation * self.BASE_POSITION_SIZE * self.VALUE_SENSITIVITY * 10
            quantity = max(0, min(50, quantity))  # Only buy
            bid_price = price
            print(f"  [FUNDAMENTAL BUY] Price {deviation*100:.1f}% below fundamental")
        elif deviation < -self.VALUE_THRESHOLD:
            # Price above fundamental - sell
            quantity = deviation * self.BASE_POSITION_SIZE * self.VALUE_SENSITIVITY * 10
            quantity = max(-30, min(0, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:10s}): "
            f"Q={quantity:+8.2f} dev={deviation*100:+.1f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "provides_liquidity": True,  # Fundamental traders provide liquidity
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# RetailTrader - Slow Reaction
# =============================================================================


class RetailTrader(BaseInvestor):
    """
    Retail trader with slow reaction time.

    Behavior:
        - Trades infrequently
        - Often late to the party
        - Can provide liquidity during recovery
    """

    STRATEGY_NAME = "retail"

    TRADE_FREQUENCY = 5  # Only trade every N rounds
    NOISE_STD = 8.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        if round_num % self.TRADE_FREQUENCY != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            # Random trading with position mean reversion
            random_trade = random.gauss(0, self.NOISE_STD)
            reversion = -0.1 * position
            quantity = random_trade + reversion
            quantity = max(-15, min(15, quantity))
            bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:10s}): "
            f"Q={quantity:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }
