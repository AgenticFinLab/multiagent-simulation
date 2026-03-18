"""LiquidityDryup - Market Maker Inventory Model Simulation

Phenomenon: Liquidity Dry-up
    - Market makers withdraw liquidity during stress
    - Creates self-reinforcing cycles of illiquidity
    - Reference: Grossman & Miller (1988), Amihud & Mendelson (1986)

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

logger = logging.getLogger("LiquidityDryup")


class Market(GeneralPlayer):
    """
    Market with liquidity-dependent pricing.

    Parameters from config extras:
        - fundamental_value, initial_price
        - price_impact, mean_reversion, noise_std
        - custom_state_hot_limit, record_path, base_liquidity
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["total_liquidity"] = 100.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=custom_state_hot_limit
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
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
        liquidity_provided = sum(o["provides_liquidity"] for o in orders)
        total_liquidity = base_liquidity + liquidity_provided

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy - total_sell

        # Illiquidity amplifies price impact
        price_impact_rate = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        liquidity_factor = 100.0 / max(total_liquidity, 10.0)
        price_impact = price_impact_rate * net_demand * liquidity_factor
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)

        new_price = max(
            1.0,
            current_price + price_impact + mean_reversion + random.gauss(0, noise_std),
        )
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["total_liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["liquidity_history"].append(total_liquidity)

        logger.debug(
            f"\n[Market] R{round_num} Price: {current_price:.2f}→{new_price:.2f} ({price_return*100:+.2f}%) Liq: {total_liquidity:.0f}"
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
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
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=custom_state_hot_limit,
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
    """
    Market maker who provides liquidity but withdraws in stress.

    Parameters from config extras:
        - volatility_threshold, base_liquidity, withdraw_rebalance, normal_rebalance
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = abs(market_data["return"])
        position = self.state.custom_state["position"]

        volatility_threshold = extras["volatility_threshold"]
        base_liquidity = extras["base_liquidity"]
        withdraw_rebalance = extras["withdraw_rebalance"]
        normal_rebalance = extras["normal_rebalance"]
        strategy_name = self.__class__.__name__

        if volatility > volatility_threshold:
            provides_liquidity = 0  # WITHDRAW
            quantity = -position * withdraw_rebalance if position != 0 else 0
        else:
            provides_liquidity = base_liquidity
            quantity = -position * normal_rebalance

        quantity = max(-25, min(25, quantity))
        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:20s}] Q={quantity:+6.1f} liq={'YES' if provides_liquidity else 'WITHDRAW'}"
        )
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "provides_liquidity": provides_liquidity,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "provides_liquidity": provides_liquidity,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class LiquiditySeeker(BaseInvestor):
    """
    Investor who needs liquidity - struggles during dry-up.

    Parameters from config extras:
        - target_volatility, liquidity_base
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        liquidity = market_data["liquidity"]

        target_volatility = extras["target_volatility"]
        liquidity_base = extras["liquidity_base"]
        strategy_name = self.__class__.__name__

        # Wants to trade but liquidity affects execution
        target_quantity = random.gauss(0, target_volatility)
        # Reduce order when liquidity is low
        liquidity_adjustment = min(1.0, liquidity / liquidity_base)
        quantity = target_quantity * liquidity_adjustment
        quantity = max(-20, min(20, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "provides_liquidity": 0,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "provides_liquidity": 0,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class ValueTrader(BaseInvestor):
    """
    Value trader who provides liquidity to the market.

    Parameters from config extras:
        - liquidity_threshold, trade_threshold, base_liquidity_provision, value_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        liquidity_threshold = extras["liquidity_threshold"]
        trade_threshold = extras["trade_threshold"]
        base_liquidity_provision = extras["base_liquidity_provision"]
        value_multiplier = extras["value_multiplier"]
        strategy_name = self.__class__.__name__

        deviation = (fundamental - price) / fundamental
        provides_liquidity = (
            base_liquidity_provision if abs(deviation) > liquidity_threshold else 0
        )
        quantity = (
            deviation * value_multiplier if abs(deviation) > trade_threshold else 0
        )
        quantity = max(-25, min(25, quantity))
        bid_price = price if quantity != 0 else 0.0

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "provides_liquidity": provides_liquidity,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "provides_liquidity": provides_liquidity,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class MomentumTrader(BaseInvestor):
    """
    Momentum trader - can trigger liquidity crises.

    Parameters from config extras:
        - momentum_threshold, momentum_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        ret = market_data["return"]

        momentum_threshold = extras["momentum_threshold"]
        momentum_multiplier = extras["momentum_multiplier"]
        strategy_name = self.__class__.__name__

        quantity = ret * momentum_multiplier if abs(ret) > momentum_threshold else 0
        quantity = max(-35, min(35, quantity))
        bid_price = price

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "provides_liquidity": 0,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "provides_liquidity": 0,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


class NoiseTrader(BaseInvestor):
    """
    Noise trader providing random trades.

    Parameters from config extras:
        - noise_volatility
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]

        noise_volatility = extras["noise_volatility"]
        strategy_name = self.__class__.__name__

        quantity = random.gauss(0, noise_volatility)
        quantity = max(-15, min(15, quantity))
        bid_price = price
        quantity = self._apply_constraints(bid_price, quantity)
        if quantity != 0:
            self._execute_trade(bid_price, quantity)
        logger.debug(f"[{self.identity:20s}] Q={quantity:+6.1f}")
        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "provides_liquidity": 0,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "provides_liquidity": 0,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }
