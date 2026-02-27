"""LiquidityDryup - Market Maker Inventory Model Simulation

Phenomenon: Liquidity Dry-up
    - Market makers withdraw liquidity during stress
    - Creates self-reinforcing cycles of illiquidity
    - Reference: Grossman & Miller (1988), Amihud & Mendelson (1986)
"""

import os
import random
import math
from typing import Any, Dict, Optional
from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


class Market(GeneralPlayer):
    """Market with liquidity-dependent pricing."""

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0
    PRICE_IMPACT = 0.08
    MEAN_REVERSION = 0.015
    NOISE_STD = 0.4
    HISTORY_LIMIT = 200

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "price" not in self.state.custom_state:
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/LiquidityDryup/records"
            )
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["total_liquidity"] = 100.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=self.HISTORY_LIMIT
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
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
                        "provides_liquidity": order["provides_liquidity"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        liquidity_provided = sum(o["provides_liquidity"] for o in orders)
        total_liquidity = 50.0 + liquidity_provided

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy - total_sell

        # Illiquidity amplifies price impact
        liquidity_factor = 100.0 / max(total_liquidity, 10.0)
        price_impact = self.PRICE_IMPACT * net_demand * liquidity_factor
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)

        new_price = max(
            1.0,
            current_price
            + price_impact
            + mean_reversion
            + random.gauss(0, self.NOISE_STD),
        )
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["total_liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["liquidity_history"].append(total_liquidity)

        print(
            f"\n[Market] R{round_num} Price: {current_price:.2f}→{new_price:.2f} ({price_return*100:+.2f}%) Liq: {total_liquidity:.0f}"
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
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


class BaseInvestor(GeneralPlayer):
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
                "record_path", "EXPERIMENT/LiquidityDryup/records"
            )
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload
                self.state.custom_state["price_history"].append(inb.payload["price"])

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash, pos = self.state.custom_state["cash"], self.state.custom_state["position"]
        if quantity > 0 and bid_price > 0:
            quantity = min(quantity, cash / bid_price)
        elif quantity < 0:
            quantity = max(-pos, quantity) if pos > 0 else 0
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


class MarketMaker(BaseInvestor):
    """Market maker who provides liquidity but withdraws in stress."""

    STRATEGY_NAME = "market_maker"
    VOLATILITY_THRESHOLD = 0.02
    BASE_LIQUIDITY = 30.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = abs(market_data["return"])
        position = self.state.custom_state["position"]

        if volatility > self.VOLATILITY_THRESHOLD:
            provides_liquidity = 0  # WITHDRAW
            quantity = -position * 0.3 if position != 0 else 0
        else:
            provides_liquidity = self.BASE_LIQUIDITY
            quantity = -position * 0.2

        quantity = max(-25, min(25, quantity))
        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:20s}] Q={quantity:+6.1f} liq={'YES' if provides_liquidity else 'WITHDRAW'}"
        )
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "provides_liquidity": provides_liquidity,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                        "provides_liquidity": provides_liquidity,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class LiquiditySeeker(BaseInvestor):
    """Investor who needs liquidity - struggles during dry-up."""

    STRATEGY_NAME = "liquidity_seeker"

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        liquidity = market_data["liquidity"]

        # Wants to trade but liquidity affects execution
        target_quantity = random.gauss(0, 15)
        # Reduce order when liquidity is low
        liquidity_adjustment = min(1.0, liquidity / 100.0)
        quantity = target_quantity * liquidity_adjustment
        quantity = max(-20, min(20, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "provides_liquidity": 0,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                        "provides_liquidity": 0,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class ValueTrader(BaseInvestor):
    """Value trader who provides liquidity to the market."""

    STRATEGY_NAME = "value"

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        deviation = (fundamental - price) / fundamental
        provides_liquidity = 20 if abs(deviation) > 0.05 else 0
        quantity = deviation * 30 if abs(deviation) > 0.03 else 0
        quantity = max(-25, min(25, quantity))
        bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "provides_liquidity": provides_liquidity,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                        "provides_liquidity": provides_liquidity,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class MomentumTrader(BaseInvestor):
    """Momentum trader - can trigger liquidity crises."""

    STRATEGY_NAME = "momentum"

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        ret = market_data["return"]

        quantity = ret * 200 if abs(ret) > 0.01 else 0
        quantity = max(-35, min(35, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "provides_liquidity": 0,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                        "provides_liquidity": 0,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class NoiseTrader(BaseInvestor):
    """Noise trader providing random trades."""

    STRATEGY_NAME = "noise"

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        quantity = random.gauss(0, 10)
        quantity = max(-15, min(15, quantity))
        bid_price = price
        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)
        print(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "provides_liquidity": 0,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": self.STRATEGY_NAME,
                        "provides_liquidity": 0,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }
