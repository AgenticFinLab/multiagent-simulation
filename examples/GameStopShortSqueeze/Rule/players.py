"""GameStopShortSqueeze Rule-Based Simulation

January 2021 GameStop short squeeze - Reddit coordination drove 1,700% price increase.

Theoretical Foundation:
- Gamma squeeze dynamics (Jarrow & Li, 2021)
- Social media and retail coordination (Lyocsa et al., 2022)
- Short sale constraints (Jones & Lamont, 2002)

Key Dynamics:
- RetailCoordinated: Retail traders coordinating via social media to buy and hold
- ShortSellerHF: Heavily short hedge fund forced to cover at higher prices
- MarketMakerGamma: Market maker hedging options exposure creates buying pressure
- InstitutionalValue: Values company based on fundamentals, sees extreme overvaluation
- MomentumRetail: Retail momentum trader driven by fear of missing out

Parameters from config (see configs/GameStopShortSqueeze/Rule/players.yml).
"""

import logging
import random

from masim.player.base import Action
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("GameStopShortSqueeze")


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
                folder=f"history/GameStopShortSqueeze/Market",
                entry_limit=200,
            )

        orders = []
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "order":
                orders.append(payload)

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        total_buy = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "buy"
        )
        total_sell = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "sell"
        )
        net_demand = total_buy - total_sell

        new_price = (
            price
            + price_impact * net_demand
            + mean_reversion * (fundamental - price)
            + random.gauss(0, noise_std)
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


class RetailCoordinated(GeneralPlayer):
    """Retail trader coordinating via social media: buys and holds aggressively."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["buy_pressure"] = extras["buy_pressure"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        buy_pressure = self.state.custom_state["buy_pressure"]
        if cash > price * 50 and price > 0:
            buy_qty = min(int(cash * buy_pressure / price), 500)
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
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class ShortSellerHF(GeneralPlayer):
    """Heavily short hedge fund forced to cover when price rises above threshold."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", -500)
            self.state.custom_state["cover_threshold"] = extras["cover_threshold"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        position = self.state.custom_state["position"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        cover_threshold = self.state.custom_state["cover_threshold"]
        if position < 0 and deviation > cover_threshold:
            cover_qty = min(abs(position), int(abs(position) * 0.5))
            if cover_qty > 0:
                return {"action": "buy", "quantity": cover_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class MarketMakerGamma(GeneralPlayer):
    """Market maker delta-hedging options exposure: buys more when price rises."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["gamma_exposure"] = extras["gamma_exposure"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        gamma = self.state.custom_state["gamma_exposure"]
        hedge_qty = int(abs(deviation) * gamma * 5000)
        if deviation > 0 and hedge_qty > 0 and price > 0:
            buy_qty = min(hedge_qty, int(cash / price))
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
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class InstitutionalValue(GeneralPlayer):
    """Fundamental value investor: sells aggressively when price is extremely overvalued."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 1000)
            self.state.custom_state["sell_threshold"] = extras["sell_threshold"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        position = self.state.custom_state["position"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        sell_threshold = self.state.custom_state["sell_threshold"]
        if deviation > sell_threshold:
            sell_qty = min(1000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload):
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state.get("price", 0)
        if action == "sell" and quantity > 0:
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


class MomentumRetail(GeneralPlayer):
    """FOMO retail trader: buys when price is rising above FOMO threshold."""

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["fomo_threshold"] = extras["fomo_threshold"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self):
        price = self.state.custom_state.get("price", 0)
        cash = self.state.custom_state["cash"]
        deviation = self.state.custom_state.get("deviation", 0.0)
        fomo_threshold = self.state.custom_state["fomo_threshold"]
        if deviation > fomo_threshold and price > 0:
            buy_qty = min(50, int(cash / price))
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
    "RetailCoordinated",
    "ShortSellerHF",
    "MarketMakerGamma",
    "InstitutionalValue",
    "MomentumRetail",
]
