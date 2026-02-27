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
"""

import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


class Market(GeneralPlayer):
    """Market with short interest tracking."""

    FUNDAMENTAL_VALUE = 50.0  # Low fundamental - typical for shorted stocks
    INITIAL_PRICE = 30.0  # Trading below fundamental

    PRICE_IMPACT = 0.1
    MEAN_REVERSION = 0.005  # Weak reversion - allows squeeze to develop
    NOISE_STD = 0.5

    HISTORY_LIMIT = 200

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/ShortSqueeze/records"
            )
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["short_interest"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=self.HISTORY_LIMIT
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"), entry_limit=self.HISTORY_LIMIT
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
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        cover_buying = sum(
            o["quantity"]
            for o in orders
            if o.get("is_short_cover") and o["quantity"] > 0
        )
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Short cover buying has extra price impact (forced buying)
        short_squeeze_impact = cover_buying * 0.05  # Extra impact from covering

        price_impact = self.PRICE_IMPACT * net_demand + short_squeeze_impact
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)

        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num} - ShortSqueeze")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(f"  Net Demand: {net_demand:+.2f}, Cover Buying: {cover_buying:.1f}")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
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


class BaseInvestor(GeneralPlayer):
    """Base investor class."""

    STRATEGY_NAME = "base"
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 0.0
    HISTORY_LIMIT = 50

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/ShortSqueeze/records"
            )
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=self.HISTORY_LIMIT
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
    """Short seller who must cover when losses mount."""

    STRATEGY_NAME = "short_seller"
    INITIAL_POSITION = -50.0  # Start with short position
    COVER_THRESHOLD = 0.20  # Cover at 20% loss

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        await super().perceive(observation, prev_result)
        if "short_entry_price" not in self.state.custom_state:
            self.state.custom_state["short_entry_price"] = (
                30.0  # Shorted at initial price
            )
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["cash"] += (
                abs(self.INITIAL_POSITION) * 30.0
            )  # Proceeds from short

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]
        entry_price = self.state.custom_state["short_entry_price"]

        is_short_cover = False
        if position < 0:  # Have short position
            loss_pct = (price - entry_price) / entry_price
            if loss_pct > self.COVER_THRESHOLD:
                # COVER - buy to close short
                quantity = abs(position) * 0.5  # Cover half
                is_short_cover = True
                print(f"  [SHORT COVER] Loss {loss_pct*100:.1f}% > threshold")
            else:
                quantity = 0.0
        else:
            quantity = 0.0

        bid_price = price if quantity > 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:12s}): Q={quantity:+8.2f}"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": self.STRATEGY_NAME,
                "investor": self.identity,
                "is_short_cover": is_short_cover,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                        "is_short_cover": is_short_cover,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class MomentumBuyer(BaseInvestor):
    """Momentum buyer who amplifies squeeze."""

    STRATEGY_NAME = "momentum_buyer"
    LOOKBACK = 3
    BASE_SIZE = 25.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]

        if len(price_history) >= self.LOOKBACK:
            momentum = (
                list(price_history)[-1] - list(price_history)[-self.LOOKBACK]
            ) / list(price_history)[-self.LOOKBACK]
        else:
            momentum = 0.0

        quantity = momentum * self.BASE_SIZE * 15 if momentum > 0.02 else 0.0
        quantity = max(0, min(40, quantity))  # Only buy
        bid_price = price if quantity > 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:12s}): Q={quantity:+8.2f} mom={momentum*100:+.1f}%"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": self.STRATEGY_NAME,
                "investor": self.identity,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class RetailTrader(BaseInvestor):
    """Retail trader who can trigger squeeze."""

    STRATEGY_NAME = "retail"
    NOISE_STD = 12.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]

        quantity = random.gauss(5, self.NOISE_STD)  # Slightly bullish bias
        quantity = max(-15, min(25, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:12s}): Q={quantity:+8.2f}"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": self.STRATEGY_NAME,
                "investor": self.identity,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class ValueInvestor(BaseInvestor):
    """Value investor buying undervalued stock."""

    STRATEGY_NAME = "value"
    VALUE_THRESHOLD = 0.15
    BASE_SIZE = 20.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        deviation = (fundamental - price) / fundamental
        quantity = (
            deviation * self.BASE_SIZE * 5 if deviation > self.VALUE_THRESHOLD else 0.0
        )
        quantity = max(0, min(30, quantity))
        bid_price = price if quantity > 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:12s}): Q={quantity:+8.2f}"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": self.STRATEGY_NAME,
                "investor": self.identity,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class InstitutionalHolder(BaseInvestor):
    """Large passive institutional holder."""

    STRATEGY_NAME = "institutional"
    INITIAL_POSITION = 100.0

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        await super().perceive(observation, prev_result)
        if "initialized" not in self.state.custom_state:
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["initialized"] = True

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        # Passive - rarely trades
        quantity = 0.0
        bid_price = 0.0
        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:12s}): Q={quantity:+8.2f} (passive)"
        )
        return {
            **{
                "bid_price": bid_price,
                "quantity": quantity,
                "strategy": self.STRATEGY_NAME,
                "investor": self.identity,
            },
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }
