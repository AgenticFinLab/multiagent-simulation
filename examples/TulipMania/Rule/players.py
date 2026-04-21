import random
import logging
import re

"""TulipMania Rule-Based Simulation

1637 Dutch tulip bubble where speculative frenzy drove tulip prices to extraordinary levels before catastrophic collapse

Theoretical Foundation:
- Garber (2000): Famous first bubbles
- Mackay (1841): Extraordinary popular delusions and the madness of crowds
- Thompson (2007): The tulip mania - Fact or artifact?

Key Dynamics:
- TrendChaser: Buys assets purely because prices are rising, regardless of intrinsic value
- SocialProofFollower: Follows crowd into speculative positions because everyone else is doing it
- IntrinsicValueTrader: Values assets by intrinsic utility, sells when price far exceeds use value
- EarlyExitTrader: Recognizes speculative excess early and exits before the crash
- NoiseTrader: Random uninformed trader providing baseline liquidity

Parameters from config (see configs/TulipMania/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("TulipMania")


class Market(GeneralPlayer):
    """
    Market agent for TulipMania simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "price" not in self.state.custom_state:
            self._initialize_market_state()
        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()

    def _initialize_market_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []
        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]

    def _extract_orders(self, observation) -> list:
        orders = []
        for msg in observation.messages:
            if msg.get("type") == "order":
                orders.append({"agent_id": msg.get("from"), "action": msg.get("action"), "quantity": msg.get("quantity"), "agent_type": msg.get("agent_type")})
        return orders

    def _clear_market(self, orders: list) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]
        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)
        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5
        return {"price": new_price, "volume": volume, "net_demand": net_demand}

    def _update_state(self, market_result: dict) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])

    def _log_market_state(self) -> None:
        logger.debug("Round %d: price=%.2f", self.state.custom_state["round"], self.state.custom_state["price"])

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0
        market_update = {"type": "market_update", "price": price, "fundamental": fundamental, "deviation": deviation, "round": self.state.custom_state["round"]}
        return Action(
            action_type="market_broadcast",
            payload={"market_data": market_update, "outbound_messages": [{"payload": market_update, "content_type": "market_update"}]},
            source_id=self.identity,
        )


class TrendChaser(GeneralPlayer):
    """
    Buys assets purely because prices are rising, regardless of intrinsic value

    Theoretical Basis: Greater fool theory (Mackay, 1841)
    Market Role: destabilizing
    """
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        # Buys assets purely because prices are rising, regardless of intrinsic value
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        momentum_strength = extras["momentum_strength"]
        max_position = extras["max_position"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class SocialProofFollower(GeneralPlayer):
    """
    Follows crowd into speculative positions because everyone else is doing it

    Theoretical Basis: Social proof and crowd psychology (Mackay, 1841)
    Market Role: destabilizing
    """
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        # Follows crowd into speculative positions because everyone else is doing it
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        herd_weight = extras["herd_weight"]
        entry_threshold = extras["entry_threshold"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class IntrinsicValueTrader(GeneralPlayer):
    """
    Values assets by intrinsic utility, sells when price far exceeds use value

    Theoretical Basis: Fundamental value discipline (Garber, 2000)
    Market Role: stabilizing
    """
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        # Values assets by intrinsic utility, sells when price far exceeds use value
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        value_threshold = extras["value_threshold"]
        position_size = extras["position_size"]

        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class EarlyExitTrader(GeneralPlayer):
    """
    Recognizes speculative excess early and exits before the crash

    Theoretical Basis: Rational bubble riding (Thompson, 2007)
    Market Role: stabilizing
    """
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        # Recognizes speculative excess early and exits before the crash
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        exit_threshold = extras["exit_threshold"]
        timing_sensitivity = extras["timing_sensitivity"]

        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """
    Random uninformed trader providing baseline liquidity

    Theoretical Basis: Noise trader model (Black, 1986)
    Market Role: neutral
    """
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        # Random uninformed trader providing baseline liquidity
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        trade_probability = extras["trade_probability"]

        if random.random() < 0.3:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


__all__ = ["Market, TrendChaser, SocialProofFollower, IntrinsicValueTrader, EarlyExitTrader, NoiseTrader"]
