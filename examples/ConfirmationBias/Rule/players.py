import random
import logging

"""ConfirmationBias Rule-Based Simulation

Confirmation bias causes traders to seek and overweight evidence confirming their existing beliefs

Theoretical Foundation:
- Nickerson (1998): Confirmation bias - A ubiquitous phenomenon in many guises
- Lord, Ross & Lepper (1979): Biased assimilation and attitude polarization
- Rabin & Schrag (1999): First impressions matter - A model of confirmatory bias

Key Dynamics:
- BeliefAnchor: Forms strong prior beliefs and selectively filters confirming evidence
- SelectiveScanner: Actively seeks information supporting current position while ignoring contradictions
- BalancedAnalyst: Evaluates all evidence equally regardless of prior beliefs
- ContrarianTrader: Specifically looks for disconfirming evidence to trade against biased consensus
- NoiseTrader: Random uninformed trader providing baseline liquidity

Parameters from config (see configs/ConfirmationBias/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("ConfirmationBias")


class Market(GeneralPlayer):
    """
    Market agent for ConfirmationBias simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

    Where:
        - lambda: Price impact coefficient
        - gamma: Mean reversion strength
        - F: Fundamental value
        - epsilon: Random noise
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
                orders.append({
                    "agent_id": msg.get("from"),
                    "action": msg.get("action"),
                    "quantity": msg.get("quantity"),
                    "agent_type": msg.get("agent_type"),
                })
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

        return {
            "price": new_price,
            "volume": volume,
            "net_demand": net_demand,
        }

    def _update_state(self, market_result: dict) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])

    def _log_market_state(self) -> None:
        logger.debug(
            "Round %d: price=%.2f",
            self.state.custom_state["round"],
            self.state.custom_state["price"],
        )

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0

        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }

        return Action(
            action_type="market_broadcast",
            payload={"market_data": market_update, "outbound_messages": [{"payload": market_update, "content_type": "market_update"}]},
            source_id=self.identity,
        )


class BeliefAnchor(GeneralPlayer):
    """
    Forms strong prior beliefs and selectively filters confirming evidence

    Theoretical Basis: Confirmatory evidence filtering (Nickerson, 1998)
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
        # Forms strong prior beliefs and selectively filters confirming evidence
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        belief_strength = extras["belief_strength"]
        confirm_weight = extras["confirm_weight"]
        disconfirm_weight = extras["disconfirm_weight"]

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


class SelectiveScanner(GeneralPlayer):
    """
    Actively seeks information supporting current position while ignoring contradictions

    Theoretical Basis: Selective information search (Lord et al., 1979)
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
        # Actively seeks information supporting current position while ignoring contradictions
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        search_bias = extras["search_bias"]
        ignore_contradiction = extras["ignore_contradiction"]

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


class BalancedAnalyst(GeneralPlayer):
    """
    Evaluates all evidence equally regardless of prior beliefs

    Theoretical Basis: Bayesian rationality (Rabin & Schrag, 1999 baseline)
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
        # Evaluates all evidence equally regardless of prior beliefs
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        confirm_weight = extras["confirm_weight"]
        disconfirm_weight = extras["disconfirm_weight"]

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


class ContrarianTrader(GeneralPlayer):
    """
    Specifically looks for disconfirming evidence to trade against biased consensus

    Theoretical Basis: Contrarian strategy against biased markets
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
        # Specifically looks for disconfirming evidence to trade against biased consensus
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        contrarian_threshold = extras["contrarian_threshold"]
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


__all__ = ["Market, BeliefAnchor, SelectiveScanner, BalancedAnalyst, ContrarianTrader, NoiseTrader"]
