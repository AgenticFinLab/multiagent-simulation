"""FlashCrash - Market Microstructure Simulation

Phenomenon: Flash Crash
    - Extreme rapid price decline (can be 5-10% in minutes)
    - Caused by algorithmic trading feedback loops
    - Liquidity withdrawal amplifies the crash
    - Quick recovery as fundamental traders step in

Key Mechanism:
    1. Initial selling pressure
    2. HFTs detect momentum → start selling
    3. Stop-losses triggered → cascade selling
    4. Market makers withdraw liquidity
    5. Price collapses
    6. Fundamental traders recognize value → buy
    7. Price recovers

All parameters are configured via players.yml config file.
"""

import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


class Market(GeneralPlayer):
    """
    Central market with liquidity-sensitive pricing.

    Parameters from config extras:
        - fundamental_value, initial_price
        - base_price_impact, mean_reversion, noise_std
        - low_liquidity_threshold, high_impact_multiplier, base_liquidity
        - history_limit, record_path
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
            history_limit = extras["history_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["liquidity"] = 100.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=history_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=history_limit,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=history_limit,
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
                        "provides_liquidity": order["provides_liquidity"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        base_liquidity = extras["base_liquidity"]
        low_liquidity_threshold = extras["low_liquidity_threshold"]
        high_impact_multiplier = extras["high_impact_multiplier"]
        base_price_impact = extras["base_price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        liquidity_provision = sum(
            abs(o["quantity"]) for o in orders if o["provides_liquidity"]
        )
        total_liquidity = base_liquidity + liquidity_provision

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        if total_liquidity < low_liquidity_threshold:
            liquidity_factor = high_impact_multiplier
        else:
            liquidity_factor = (
                1.0 + (low_liquidity_threshold / total_liquidity - 1.0) * 0.5
            )

        price_impact = base_price_impact * net_demand * liquidity_factor
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["liquidity_history"].append(total_liquidity)

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
    Base class for flash crash investors.

    Parameters from config extras:
        - initial_cash, initial_position, history_limit, record_path
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
            history_limit = extras["history_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=history_limit,
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


class HighFrequencyTrader(BaseInvestor):
    """
    High-frequency trader with rapid momentum detection.

    Parameters from config extras:
        - lookback, momentum_sensitivity, base_position_size, speed_advantage
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        price_history = self.state.custom_state["price_history"]

        lookback = extras["lookback"]
        momentum_sensitivity = extras["momentum_sensitivity"]
        base_position_size = extras["base_position_size"]
        speed_advantage = extras["speed_advantage"]
        strategy_name = self.__class__.__name__

        if len(price_history) >= lookback:
            recent = list(price_history)[-lookback:]
            short_momentum = (
                (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
            )
        else:
            short_momentum = price_return

        signal = short_momentum * momentum_sensitivity
        quantity = signal * base_position_size * speed_advantage
        quantity = max(-60, min(60, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:10s}): "
            f"Q={quantity:+8.2f} mom={short_momentum*100:+.2f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class MarketMaker(BaseInvestor):
    """
    Market maker providing liquidity, withdraws in stress.

    Parameters from config extras:
        - volatility_threshold, base_liquidity, spread_sensitivity
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = abs(market_data["return"])
        position = self.state.custom_state["position"]

        volatility_threshold = extras["volatility_threshold"]
        base_liquidity = extras["base_liquidity"]
        strategy_name = self.__class__.__name__

        if price_return > volatility_threshold:
            provides_liquidity = False
            quantity = -position * 0.3 if position > 0 else 0
            quantity = max(-20, min(20, quantity))
            bid_price = price if quantity != 0 else 0.0
            print(f"  [MM] WITHDRAWING - volatility too high ({price_return*100:.1f}%)")
        else:
            provides_liquidity = True
            quantity = -position * 0.2
            quantity = max(-base_liquidity, min(base_liquidity, quantity))
            bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:10s}): "
            f"Q={quantity:+8.2f} liq={'YES' if provides_liquidity else 'NO'}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "provides_liquidity": provides_liquidity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class AlgorithmicTrader(BaseInvestor):
    """
    Algorithmic trend-following trader.

    Parameters from config extras:
        - lookback, trend_sensitivity, base_position_size, trend_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        lookback = extras["lookback"]
        trend_sensitivity = extras["trend_sensitivity"]
        base_position_size = extras["base_position_size"]
        trend_multiplier = extras["trend_multiplier"]
        strategy_name = self.__class__.__name__

        if len(price_history) >= lookback:
            recent = list(price_history)[-lookback:]
            trend = (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
        else:
            trend = 0.0

        quantity = trend * trend_sensitivity * base_position_size * trend_multiplier
        quantity = max(-40, min(40, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:10s}): "
            f"Q={quantity:+8.2f} trend={trend*100:+.2f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class StopLossTrader(BaseInvestor):
    """
    Trader with stop-loss orders - creates cascade selling.

    Parameters from config extras:
        - stop_loss_percent, initial_buy_price
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        await super().perceive(observation, prev_result)

        if "initialized_position" not in self.state.custom_state:
            extras = self.config.extras
            initial_buy_price = extras["initial_buy_price"]
            self.state.custom_state["cash"] -= (
                self.state.custom_state["position"] * initial_buy_price
            )
            self.state.custom_state["initialized_position"] = True

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]
        position = self.state.custom_state["position"]

        stop_loss_percent = extras["stop_loss_percent"]
        strategy_name = self.__class__.__name__

        if len(price_history) >= 5:
            recent_high = max(list(price_history)[-10:])
        else:
            recent_high = price

        stop_price = recent_high * (1 - stop_loss_percent)

        if price < stop_price and position > 0:
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
            f"[{self.identity:25s}] R{round_num} ({strategy_name:10s}): "
            f"Q={quantity:+8.2f} pos={self.state.custom_state['position']:.1f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class FundamentalTrader(BaseInvestor):
    """
    Fundamental value trader - provides recovery force.

    Parameters from config extras:
        - value_threshold, base_position_size, value_sensitivity, value_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        value_threshold = extras["value_threshold"]
        base_position_size = extras["base_position_size"]
        value_sensitivity = extras["value_sensitivity"]
        value_multiplier = extras["value_multiplier"]
        strategy_name = self.__class__.__name__

        deviation = (fundamental - price) / fundamental

        if deviation > value_threshold:
            quantity = (
                deviation * base_position_size * value_sensitivity * value_multiplier
            )
            quantity = max(0, min(50, quantity))
            bid_price = price
            print(f"  [FUNDAMENTAL BUY] Price {deviation*100:.1f}% below fundamental")
        elif deviation < -value_threshold:
            quantity = (
                deviation * base_position_size * value_sensitivity * value_multiplier
            )
            quantity = max(-30, min(0, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:10s}): "
            f"Q={quantity:+8.2f} dev={deviation*100:+.1f}%"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "provides_liquidity": True,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class RetailTrader(BaseInvestor):
    """
    Retail trader with slow reaction time.

    Parameters from config extras:
        - trade_frequency, noise_std, position_mean_reversion
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        trade_frequency = extras["trade_frequency"]
        noise_std = extras["noise_std"]
        position_mean_reversion = extras["position_mean_reversion"]
        strategy_name = self.__class__.__name__

        if round_num % trade_frequency != 0:
            quantity = 0.0
            bid_price = 0.0
        else:
            random_trade = random.gauss(0, noise_std)
            reversion = -position_mean_reversion * position
            quantity = random_trade + reversion
            quantity = max(-15, min(15, quantity))
            bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:10s}): "
            f"Q={quantity:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "provides_liquidity": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }
