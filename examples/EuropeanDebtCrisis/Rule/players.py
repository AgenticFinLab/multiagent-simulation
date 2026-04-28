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
        buy_volume = sum(o["quantity"] for o in orders if o.get("action") == "buy")
        sell_volume = sum(o["quantity"] for o in orders if o.get("action") == "sell")
        net_demand = buy_volume - sell_volume
        price_impact = float(extras["price_impact"])
        mean_reversion = float(extras["mean_reversion"])
        noise_std = float(extras["noise_std"])
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

    Theory: simulation-bases.md §4.1 — PeripheryBondSeller
    Theoretical basis: De Grauwe (2011) self-fulfilling speculation; speculative
    selling on negative signals amplifies price falls in a reflexive crisis loop.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        sell_threshold = float(extras["sell_threshold"])
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

    Theory: simulation-bases.md §4.2 — CreditorPanicker
    Theoretical basis: Acharya et al. (2014) sovereign-bank contagion; funding
    withdrawal amplifies the crisis by cutting off periphery bank liquidity.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        panic_threshold = float(extras["panic_threshold"])
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

    Theory: simulation-bases.md §4.3 — CoreBondBuyer
    Theoretical basis: De Grauwe & Ji (2012) flight-to-safety; capital rotation
    from periphery to core bonds indirectly deepens the periphery crisis.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        flight_threshold = float(extras["flight_threshold"])
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

    Theory: simulation-bases.md §4.4 — ECBIntervenor
    Theoretical basis: Draghi (2012) 'whatever it takes' backstop mechanism; credible
    central bank commitment halts self-fulfilling crisis spiral.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        intervention_threshold = float(extras["intervention_threshold"])
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

    Theory: simulation-bases.md §4.5 — HedgedFund
    Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits
    spread dislocations but constrained by margin calls and fund redemptions.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        entry_threshold = float(extras["entry_threshold"])
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
