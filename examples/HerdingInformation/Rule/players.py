"""HerdingInformation Rule-Based Simulation

Information cascade occurs when individuals ignore private signals and follow the crowd.

Theoretical Foundation:
- Banerjee (1992): A simple model of herd behavior
- Bikhchandani, Hirshleifer & Welch (1992): A theory of fads, fashion, custom, and cultural change
- Scharfstein & Stein (1990): Herd behavior and investment

Key Dynamics:
- CascadeFollower: Ignores private signal when it contradicts observed actions
- ReputationHerder: Follows consensus to protect reputation
- IndependentThinker: Processes all signals correctly without social bias
- Contrarian: Deliberately goes against the crowd
- NoiseTrader: Random uninformed trader

Parameters from config (see configs/HerdingInformation/Rule/players.yml).
"""

import logging
import random

from masim.player.base import Action
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("HerdingInformation")


class Market(GeneralPlayer):
    """Market agent: collects orders, clears market, broadcasts new price."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
            self.state.custom_state["price_history"] = []
            self._history = HistoryBuffer(
                folder=f"history/HerdingInformation/Market",
                entry_limit=200,
            )

        orders = []
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "order":
                orders.append(payload)

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        total_buy = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "buy"
        )
        total_sell = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "sell"
        )
        net_demand = total_buy - total_sell

        new_price = (
            price
            + self.state.custom_state["price_impact"] * net_demand
            + self.state.custom_state["mean_reversion"] * (fundamental - price)
            + random.gauss(0, self.state.custom_state["noise_std"])
        )
        new_price = max(new_price, 0.01)
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        logger.debug(
            "Round %d: price=%.2f",
            self.state.custom_state["round"],
            new_price,
        )

    async def decide(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0.0
        return {
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }

    async def act(self, decision_payload):
        market_update = {
            "type": "market_update",
            "price": decision_payload["price"],
            "fundamental": decision_payload["fundamental"],
            "deviation": decision_payload["deviation"],
            "round": decision_payload["round"],
        }
        return Action(
            action_type="market_broadcast",
            payload={
                "market_data": market_update,
                "outbound_messages": [
                    {"payload": market_update, "content_type": "market_update"}
                ],
            },
            source_id=self.identity,
        )


class CascadeFollower(GeneralPlayer):
    """Information cascade follower: ignores private signal, follows observed actions."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["cascade_count"] = 0
            self.state.custom_state["social_weight"] = extras["social_weight"]
            self.state.custom_state["cascade_trigger"] = extras["cascade_trigger"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        social_weight = self.state.custom_state["social_weight"]
        cascade_trigger = self.state.custom_state["cascade_trigger"]

        cascade_count = self.state.custom_state["cascade_count"]
        if abs(deviation) > 0.03:
            cascade_count += 1
        self.state.custom_state["cascade_count"] = cascade_count

        if cascade_count >= cascade_trigger:
            qty = min(800, int(abs(deviation) * social_weight * 5000))
            if deviation > 0 and price > 0:
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            elif deviation < 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class ReputationHerder(GeneralPlayer):
    """Reputation herder: follows consensus to protect professional reputation."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["reputation_concern"] = extras["reputation_concern"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        reputation_concern = self.state.custom_state["reputation_concern"]

        if abs(deviation) > 0.02:
            qty = min(600, int(abs(deviation) * reputation_concern * 4000))
            if deviation > 0 and price > 0:
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            elif deviation < 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class IndependentThinker(GeneralPlayer):
    """Independent thinker: processes private signals correctly without social bias."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["signal_precision"] = extras["signal_precision"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        signal_precision = self.state.custom_state["signal_precision"]

        if abs(deviation) > 0.03:
            qty = min(500, int(abs(deviation) * signal_precision * 3000))
            if deviation < 0 and price > 0:
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            elif deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class Contrarian(GeneralPlayer):
    """Contrarian trader: deliberately goes against the crowd."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["contrarian_threshold"] = extras[
                "contrarian_threshold"
            ]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        contrarian_threshold = self.state.custom_state["contrarian_threshold"]

        if abs(deviation) > contrarian_threshold * 0.05:
            qty = min(400, int(abs(deviation) * 2000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            elif price > 0:
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """Noise trader: random uninformed trading providing liquidity."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["trade_probability"] = extras["trade_probability"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = self.state.custom_state["trade_probability"]

        if random.random() < prob:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy" and price > 0:
                qty = min(qty, int(cash / price))
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "CascadeFollower",
    "ReputationHerder",
    "IndependentThinker",
    "Contrarian",
    "NoiseTrader",
]
