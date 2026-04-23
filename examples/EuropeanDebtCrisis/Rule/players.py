"""EuropeanDebtCrisis Rule-Based Simulation

2010-2012 European sovereign debt crisis — self-fulfilling speculation amplified fiscal vulnerability.

Theoretical Foundation:
- De Grauwe (2011): The governance of the euro area in a speculative crisis
- De Grauwe & Ji (2012): Self-fulfilling crises in the eurozone
- Acharya et al. (2014): Sovereign yield curves and financial crises

Agents:
- Market: Rule-based price formation (peripheral bond price dynamics)
- PeripheryBondSeller: Sells periphery sovereign bonds on risk signals, amplifying yield spreads
- CreditorPanicker: Withdraws funding from periphery banks on spread widening
- CoreBondBuyer: Buys core sovereign bonds as flight-to-quality
- ECBIntervenor: Provides liquidity support and bond purchases to stabilize spreads
- HedgedFund: Takes relative value positions between core and periphery bonds
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger(__name__)


class Market(GeneralPlayer):
    """Central market agent tracking peripheral bond price (inverse of yield spread)."""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["price"] = float(extras["initial_price"])
            self.state.custom_state["fundamental"] = float(extras["fundamental_value"])
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EuropeanDebtCrisis/Rule/Market", entry_limit=200
            )
        self.state.custom_state["round"] = observation.round
        orders: List[Dict] = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict) and "action" in payload:
                    orders.append(payload)
        extras = self.config.extras
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        buy_volume = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "buy"
        )
        sell_volume = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "sell"
        )
        net_demand = buy_volume - sell_volume
        price_impact = float(extras.get("price_impact", 0.0001))
        mean_reversion = float(extras.get("mean_reversion", 0.02))
        noise_std = float(extras.get("noise_std", 0.5))
        noise = random.gauss(0, noise_std)
        new_price = (
            price
            + price_impact * net_demand
            + mean_reversion * (fundamental - price)
            + noise
        )
        new_price = max(new_price, 0.01)
        self.state.custom_state["price"] = new_price
        self.state.custom_state["history_buffer"].append(new_price)

    async def decide(self) -> Dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0.0
        market_data = {
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_update"}
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class PeripheryBondSeller(GeneralPlayer):
    """Sells periphery sovereign bonds on risk signals, amplifying yield spreads.

    Theory: De Grauwe (2011) — Self-fulfilling speculation in sovereign bond markets.
    Effect: DESTABILIZING — sells on negative signals, amplifying price falls.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EuropeanDebtCrisis/Rule/PeripheryBondSeller", entry_limit=200
            )
        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        fundamental = market_data.get("fundamental", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        sell_threshold = float(extras.get("sell_threshold", -0.03))
        action, quantity = "hold", 0
        if deviation < sell_threshold:
            qty = min(600, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        elif deviation > 0.08:
            qty = min(400, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"action": action, "quantity": quantity}
        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class CreditorPanicker(GeneralPlayer):
    """Withdraws funding from periphery banks on spread widening.

    Theory: Acharya et al. (2014) — Contagion from sovereign to bank credit risk.
    Effect: DESTABILIZING — amplifies crisis through funding withdrawal.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EuropeanDebtCrisis/Rule/CreditorPanicker", entry_limit=200
            )
        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        panic_threshold = float(extras.get("panic_threshold", -0.05))
        action, quantity = "hold", 0
        if deviation < panic_threshold:
            qty = min(700, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        elif deviation > 0.06:
            qty = min(300, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"action": action, "quantity": quantity}
        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class CoreBondBuyer(GeneralPlayer):
    """Buys core sovereign bonds as flight-to-quality, compressing core yields.

    Theory: De Grauwe & Ji (2012) — Flight-to-safety in eurozone sovereign markets.
    Effect: NEUTRAL — moves capital from periphery to core, indirectly destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EuropeanDebtCrisis/Rule/CoreBondBuyer", entry_limit=200
            )
        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        flight_threshold = float(extras.get("flight_threshold", -0.04))
        action, quantity = "hold", 0
        if deviation < flight_threshold:
            qty = min(400, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation > 0.10:
            qty = min(400, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"action": action, "quantity": quantity}
        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class ECBIntervenor(GeneralPlayer):
    """Provides liquidity support and bond purchases to stabilize spreads.

    Theory: Draghi (2012) — 'Whatever it takes' ECB backstop mechanism.
    Effect: STRONGLY STABILIZING — primary crisis backstop.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EuropeanDebtCrisis/Rule/ECBIntervenor", entry_limit=200
            )
        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        fundamental = market_data.get("fundamental", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        intervention_threshold = float(extras.get("intervention_threshold", -0.06))
        action, quantity = "hold", 0
        if deviation < intervention_threshold:
            qty = min(800, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation > 0.05:
            qty = min(500, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"action": action, "quantity": quantity}
        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class HedgedFund(GeneralPlayer):
    """Takes relative value positions between core and periphery bonds.

    Theory: Shleifer & Vishny (1997) — Limits to arbitrage in crisis conditions.
    Effect: NEUTRAL/STABILIZING — exploits spread opportunities.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EuropeanDebtCrisis/Rule/HedgedFund", entry_limit=200
            )
        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        entry_threshold = float(extras.get("entry_threshold", 0.05))
        action, quantity = "hold", 0
        if deviation < -entry_threshold:
            qty = min(500, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation > entry_threshold:
            qty = min(500, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"action": action, "quantity": quantity}
        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


__all__ = [
    "Market",
    "PeripheryBondSeller",
    "CreditorPanicker",
    "CoreBondBuyer",
    "ECBIntervenor",
    "HedgedFund",
]
