"""EndowmentEffect Rule-Based Simulation

Endowment effect: traders overvalue assets they own versus identical assets they do not.

Theoretical Foundation:
- Kahneman, Knetsch & Thaler (1990): Experimental tests of the endowment effect
- Thaler (1980): Toward a positive theory of consumer choice
- Morewedge & Giblin (2015): Explanations of the endowment effect

Agents:
- Market: Rule-based price formation (price impact + mean reversion)
- EndowedHolder: Values owned assets above market price, reluctant to sell
- StatusQuoSeller: Holds positions too long due to attachment, demands premium
- RationalArbitrageur: Exploits the gap between subjective and objective valuations
- NewBuyer: Evaluates assets at market price without ownership bias
- NoiseTrader: Random uninformed trader providing baseline liquidity
"""

import logging
import os
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger(__name__)


class Market(GeneralPlayer):
    """Central market agent tracking price dynamics for EndowmentEffect simulation."""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price"] = float(extras["initial_price"])
            self.state.custom_state["fundamental"] = float(extras["fundamental_value"])
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "fundamental"),
                entry_limit=custom_state_hot_limit,
            )
        self.state.custom_state["round"] = observation.round
        orders: List[Dict] = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict) and "action" in payload:
                    orders.append(payload)
        # Price dynamics: price impact + mean reversion + noise
        extras = self.config.extras
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        buy_volume = sum(o["quantity"] for o in orders if o["action"] == "buy")
        sell_volume = sum(o["quantity"] for o in orders if o["action"] == "sell")
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
        self.state.custom_state["price_history"].append(new_price)

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


class EndowedHolder(GeneralPlayer):
    """Values owned assets above market price, reluctant to sell at fair value.

    Theory: simulation-bases.md §4.1 — EndowedHolder
    Theoretical basis: Kahneman, Knetsch & Thaler (1990) endowment effect; ownership
    increases subjective value above market price, suppressing rational selling.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EndowmentEffect/Rule/EndowedHolder", entry_limit=200
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
        endowment_premium = float(extras["endowment_premium"])
        sell_reluctance = float(extras["sell_reluctance"])
        action, quantity = "hold", 0
        # Buy when price is below fundamental (endowed holder still buys undervalued)
        if deviation < -0.05:
            qty = min(500, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        # Sell only when price is significantly above endowed value threshold
        elif deviation > (endowment_premium + 0.05):
            sell_q = min(int(position * sell_reluctance), max(position, 0))
            if sell_q > 0:
                action, quantity = "sell", sell_q
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": "endowment premium threshold rule",
            "strategy": self.__class__.__name__,
        }
        return {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": order["reasoning"],
            "strategy": order["strategy"],
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class StatusQuoSeller(GeneralPlayer):
    """Holds positions too long due to status quo bias, demands premium to sell.

    Theory: simulation-bases.md §4.2 — StatusQuoSeller
    Theoretical basis: Samuelson & Zeckhauser (1988) status quo bias; inertia
    prevents rational rebalancing even at significant overvaluation.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EndowmentEffect/Rule/StatusQuoSeller", entry_limit=200
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
        status_quo_threshold = float(extras["status_quo_threshold"])
        action, quantity = "hold", 0
        # Only sell with large premium above fundamental
        if deviation > status_quo_threshold:
            sell_q = min(400, max(position, 0))
            if sell_q > 0:
                action, quantity = "sell", sell_q
        elif deviation < -0.08:
            buy_q = min(300, int(cash / price) if price > 0 else 0)
            if buy_q > 0:
                action, quantity = "buy", buy_q
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": "status quo threshold rule",
            "strategy": self.__class__.__name__,
        }
        return {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": order["reasoning"],
            "strategy": order["strategy"],
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class RationalArbitrageur(GeneralPlayer):
    """Exploits the gap between subjective and objective valuations.

    Theory: simulation-bases.md §4.3 — RationalArbitrageur
    Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits
    the price gap created by endowment bias, pushing prices toward fundamental.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EndowmentEffect/Rule/RationalArbitrageur", entry_limit=200
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
        arb_threshold = float(extras["arb_threshold"])
        action, quantity = "hold", 0
        if deviation < -arb_threshold:
            qty = min(600, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation > arb_threshold:
            qty = min(600, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": "rational arbitrage deviation rule",
            "strategy": self.__class__.__name__,
        }
        return {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": order["reasoning"],
            "strategy": order["strategy"],
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class NewBuyer(GeneralPlayer):
    """Evaluates assets at market price without ownership bias.

    Theory: simulation-bases.md §4.4 — NewBuyer
    Theoretical basis: Kahneman et al. (1990) — buyers unaffected by endowment effect;
    provides rational price discovery and stabilizes the market from the buy side.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EndowmentEffect/Rule/NewBuyer", entry_limit=200
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
        buy_threshold = float(extras["buy_threshold"])
        action, quantity = "hold", 0
        if deviation < buy_threshold:
            qty = min(500, int(cash / price) if price > 0 else 0)
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
        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": "new buyer valuation rule",
            "strategy": self.__class__.__name__,
        }
        return {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": order["reasoning"],
            "strategy": order["strategy"],
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class NoiseTrader(GeneralPlayer):
    """Random uninformed trader providing baseline liquidity.

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: Black (1986) noise trading and market efficiency; uninformed
    random trades provide liquidity and prevent trivial equilibria.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["market_data"] = {}
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EndowmentEffect/Rule/NoiseTrader", entry_limit=200
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
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        trade_probability = float(extras["trade_probability"])
        action, quantity = "hold", 0
        if random.random() < trade_probability:
            if random.random() < 0.5:
                qty = min(
                    random.randint(50, 200), int(cash / price) if price > 0 else 0
                )
                if qty > 0:
                    action, quantity = "buy", qty
            else:
                qty = min(random.randint(50, 200), max(position, 0))
                if qty > 0:
                    action, quantity = "sell", qty
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": "noise trader random activity rule",
            "strategy": self.__class__.__name__,
        }
        return {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "reasoning": order["reasoning"],
            "strategy": order["strategy"],
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


__all__ = [
    "Market",
    "EndowedHolder",
    "StatusQuoSeller",
    "RationalArbitrageur",
    "NewBuyer",
    "NoiseTrader",
]
