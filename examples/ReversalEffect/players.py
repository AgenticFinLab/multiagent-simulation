"""ReversalEffect - Long-term Mean Reversion Simulation

Phenomenon: Reversal Effect (De Bondt & Thaler, 1985)
    - Past losers outperform past winners over 3-5 year periods
    - Market overreacts to information, then corrects
    - Creates predictable patterns in long-term returns

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
    Central market with mean reversion dynamics.

    Parameters from config extras:
        - fundamental_value, initial_price
        - price_impact, mean_reversion, noise_std
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

            self.state.custom_state["price"] = extras["initial_price"]
            history_limit = extras["history_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=history_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=history_limit,
            )
            self.state.custom_state["return_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "return"),
                entry_limit=history_limit,
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
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact_rate = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        price_impact = price_impact_rate * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["return_history"].append(price_return)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
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
    Base class for reversal effect investors.

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

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            history_limit = extras["history_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=history_limit,
            )

        # Get market data
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


class ContrarianInvestor(BaseInvestor):
    """
    Contrarian investor exploiting mean reversion.

    Parameters from config extras:
        - lookback_window, reversal_threshold, base_position_size, value_sensitivity
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        price_history = self.state.custom_state["price_history"]

        lookback_window = extras["lookback_window"]
        reversal_threshold = extras["reversal_threshold"]
        base_position_size = extras["base_position_size"]
        value_sensitivity = extras["value_sensitivity"]
        strategy_name = self.__class__.__name__

        # Calculate long-term average
        if len(price_history) >= lookback_window:
            long_term_avg = (
                sum(list(price_history)[-lookback_window:]) / lookback_window
            )
        else:
            long_term_avg = price

        # Long-term cumulative return
        if len(price_history) >= lookback_window:
            old_price = list(price_history)[-lookback_window]
            cumulative_return = (price - old_price) / old_price
        else:
            cumulative_return = 0.0

        # Contrarian signal: buy losers, sell winners
        if abs(cumulative_return) > reversal_threshold:
            quantity = -value_sensitivity * cumulative_return * base_position_size
            quantity = max(-30, min(30, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f} cum_ret={cumulative_return*100:+.1f}% | "
            f"Cash={self.state.custom_state['cash']:10.2f}"
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


class MomentumInvestor(BaseInvestor):
    """
    Short-term momentum investor.

    Parameters from config extras:
        - lookback_window, momentum_threshold, base_position_size, momentum_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        lookback_window = extras["lookback_window"]
        momentum_threshold = extras["momentum_threshold"]
        base_position_size = extras["base_position_size"]
        momentum_multiplier = extras["momentum_multiplier"]
        strategy_name = self.__class__.__name__

        # Short-term momentum
        if len(price_history) >= lookback_window:
            old_price = list(price_history)[-lookback_window]
            momentum = (price - old_price) / old_price
        else:
            momentum = 0.0

        if abs(momentum) > momentum_threshold:
            quantity = momentum * base_position_size * momentum_multiplier
            quantity = max(-25, min(25, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f} mom={momentum*100:+.1f}%"
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


class OverconfidentTrader(BaseInvestor):
    """
    Overconfident trader who overreacts to news.

    Parameters from config extras:
        - overconfidence_factor, reaction_threshold, base_position_size, overconfidence_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]

        overconfidence_factor = extras["overconfidence_factor"]
        reaction_threshold = extras["reaction_threshold"]
        base_position_size = extras["base_position_size"]
        overconfidence_multiplier = extras["overconfidence_multiplier"]
        strategy_name = self.__class__.__name__

        # Overreact to recent return
        if abs(price_return) > reaction_threshold:
            signal = price_return * overconfidence_factor
            quantity = signal * base_position_size * overconfidence_multiplier
            quantity = max(-40, min(40, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f} ret={price_return*100:+.1f}%"
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
        - position_volatility, mean_reversion
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        position_volatility = extras["position_volatility"]
        mean_reversion_rate = extras["mean_reversion"]
        strategy_name = self.__class__.__name__

        random_trade = random.gauss(0, position_volatility)
        reversion = -mean_reversion_rate * position

        quantity = random_trade + reversion
        quantity = max(-20, min(20, quantity))
        bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f}"
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


class ValueInvestor(BaseInvestor):
    """
    Value investor based on fundamental analysis.

    Parameters from config extras:
        - value_sensitivity, base_position_size, value_noise, value_threshold
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        value_sensitivity = extras["value_sensitivity"]
        base_position_size = extras["base_position_size"]
        value_noise = extras["value_noise"]
        value_threshold = extras["value_threshold"]
        strategy_name = self.__class__.__name__

        # Estimate fundamental with noise
        estimated_value = fundamental + random.gauss(0, value_noise)

        # Calculate mispricing
        deviation = (estimated_value - price) / price

        if abs(deviation) > value_threshold:
            quantity = value_sensitivity * deviation * base_position_size
            quantity = max(-15, min(15, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f} dev={deviation*100:+.1f}%"
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


class IndexTracker(BaseInvestor):
    """
    Passive index tracker for benchmarking.

    Parameters from config extras:
        - target_position, rebalance_threshold
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        target_position = extras["target_position"]
        rebalance_threshold = extras["rebalance_threshold"]
        strategy_name = self.__class__.__name__

        # Check if rebalancing needed
        position_diff = target_position - position

        if abs(position_diff / target_position) > rebalance_threshold:
            quantity = position_diff * 0.3  # Gradual rebalance
            quantity = max(-10, min(10, quantity))
            bid_price = price
        else:
            quantity = 0.0
            bid_price = 0.0

        quantity = self._apply_constraints(bid_price, quantity)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:15s}): "
            f"Q={quantity:+8.2f} pos={position:.1f}"
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
