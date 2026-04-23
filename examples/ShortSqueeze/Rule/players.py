"""ShortSqueeze - Supply-Demand Imbalance Simulation

Phenomenon: Short Squeeze
    - Heavily shorted stock rises, forcing short sellers to cover
    - Creates positive feedback loop (buying to cover → price rises → more covering)
    - GameStop 2021 is a famous example

Architecture:
    - Market: Tracks short interest and borrow costs
    - ShortSeller: Borrows and sells, must cover when losses mount
    - MomentumBuyer: Buys on upward momentum
    - ValueInvestor: Buys when undervalued
    - RetailTrader: Can trigger initial squeeze
    - InstitutionalHolder: Large passive holder

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

logger = logging.getLogger("ShortSqueeze")


class Market(GeneralPlayer):
    """
    Market with short interest tracking.

    Parameters from config extras:
        - fundamental_value, initial_price
        - price_impact, mean_reversion, noise_std
        - custom_state_hot_limit, record_path
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["short_interest"] = 0.0

            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=custom_state_hot_limit
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"), entry_limit=custom_state_hot_limit
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
                        "is_short_cover": order["is_short_cover"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        cover_buying = sum(
            o["quantity"] for o in orders if o["is_short_cover"] and o["quantity"] > 0
        )
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Short cover buying has extra price impact (forced buying)
        short_squeeze_impact = cover_buying * 0.05  # Extra impact from covering

        price_impact_rate = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        price_impact = price_impact_rate * net_demand + short_squeeze_impact
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)

        logger.debug(f"\n{'='*70}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"[Market] Round {round_num} - ShortSqueeze")  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Cover Buying: {cover_buying:.1f}")  # pylint: disable=logging-fstring-interpolation

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
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
    Base investor class.

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=custom_state_hot_limit
            )
        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload
                self.state.custom_state["price_history"].append(inb.payload["price"])

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if quantity > 0 and bid_price > 0:
            quantity = min(quantity, cash / bid_price)
        elif quantity < 0:
            quantity = max(-position, quantity) if position > 0 else 0
        return quantity

    def _execute_trade(self, bid_price: float, quantity: float) -> None:
        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class ShortSeller(BaseInvestor):
    """
    Short seller who must cover when losses mount.

    Parameters from config extras:
        - short_initial_position, short_entry_price, cover_threshold
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        await super().perceive(observation, prev_result)
        if "short_entry_price" not in self.state.custom_state:
            extras = self.config.extras
            short_entry_price = extras["short_entry_price"]
            short_initial_position = extras["short_initial_position"]
            self.state.custom_state["short_entry_price"] = short_entry_price
            self.state.custom_state["position"] = short_initial_position
            self.state.custom_state["cash"] += (
                abs(short_initial_position) * short_entry_price
            )

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]
        entry_price = self.state.custom_state["short_entry_price"]

        cover_threshold = extras["cover_threshold"]
        strategy_name = self.__class__.__name__

        is_short_cover = False
        if position < 0:  # Have short position
            loss_pct = (price - entry_price) / entry_price
            if loss_pct > cover_threshold:
                # COVER - buy to close short
                quantity = abs(position) * 0.5  # Cover half
                is_short_cover = True
                logger.debug(f"  [SHORT COVER] Loss {loss_pct*100:.1f}% > threshold")  # pylint: disable=logging-fstring-interpolation
            else:
                quantity = 0.0
        else:
            quantity = 0.0

        bid_price = price if quantity > 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:12s}): Q={quantity:+8.2f}"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": strategy_name,
                "investor": self.identity,
                "is_short_cover": is_short_cover,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "is_short_cover": is_short_cover,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class MomentumBuyer(BaseInvestor):
    """
    Momentum buyer who amplifies squeeze.

    Parameters from config extras:
        - lookback, base_size, momentum_threshold, momentum_multiplier, max_quantity
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        lookback = extras["lookback"]
        base_size = extras["base_size"]
        momentum_threshold = extras["momentum_threshold"]
        momentum_multiplier = extras["momentum_multiplier"]
        max_quantity = extras["max_quantity"]
        strategy_name = self.__class__.__name__

        if len(price_history) >= lookback:
            momentum = (
                list(price_history)[-1] - list(price_history)[-lookback]
            ) / list(price_history)[-lookback]
        else:
            momentum = 0.0

        quantity = (
            momentum * base_size * momentum_multiplier
            if momentum > momentum_threshold
            else 0.0
        )
        quantity = max(0, min(max_quantity, quantity))  # Only buy
        bid_price = price if quantity > 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:12s}): Q={quantity:+8.2f} mom={momentum*100:+.1f}%"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": strategy_name,
                "investor": self.identity,
                "is_short_cover": False,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "is_short_cover": False,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class RetailTrader(BaseInvestor):
    """
    Retail trader who can trigger squeeze.

    Parameters from config extras:
        - noise_std, bullish_bias, min_quantity, max_quantity
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]

        noise_std = extras["noise_std"]
        bullish_bias = extras["bullish_bias"]
        min_quantity = extras["min_quantity"]
        max_quantity = extras["max_quantity"]
        strategy_name = self.__class__.__name__

        quantity = random.gauss(bullish_bias, noise_std)
        quantity = max(min_quantity, min(max_quantity, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:12s}): Q={quantity:+8.2f}"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": strategy_name,
                "investor": self.identity,
                "is_short_cover": False,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "is_short_cover": False,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class ValueInvestor(BaseInvestor):
    """
    Value investor buying undervalued stock.

    Parameters from config extras:
        - value_threshold, base_size, value_multiplier, max_quantity
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        value_threshold = extras["value_threshold"]
        base_size = extras["base_size"]
        value_multiplier = extras["value_multiplier"]
        max_quantity = extras["max_quantity"]
        strategy_name = self.__class__.__name__

        deviation = (fundamental - price) / fundamental
        quantity = (
            deviation * base_size * value_multiplier
            if deviation > value_threshold
            else 0.0
        )
        quantity = max(0, min(max_quantity, quantity))
        bid_price = price if quantity > 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:12s}): Q={quantity:+8.2f}"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": strategy_name,
                "investor": self.identity,
                "is_short_cover": False,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "is_short_cover": False,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class InstitutionalHolder(BaseInvestor):
    """
    Large passive institutional holder.
    Rarely trades, initial_position from config defines holdings.
    """

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        strategy_name = self.__class__.__name__

        # Passive - rarely trades
        quantity = 0.0
        bid_price = 0.0
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:12s}): Q={quantity:+8.2f} (passive)"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": strategy_name,
                "investor": self.identity,
                "is_short_cover": False,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "is_short_cover": False,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }
