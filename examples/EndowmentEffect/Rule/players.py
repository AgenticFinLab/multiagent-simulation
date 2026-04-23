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
            self.state.custom_state["price"] = float(extras["initial_price"])
            self.state.custom_state["fundamental"] = float(extras["fundamental_value"])
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="EndowmentEffect/Rule/Market", entry_limit=200
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


class EndowedHolder(GeneralPlayer):
    """Values owned assets above market price, reluctant to sell at fair value.

    Theory: Kahneman et al. (1990) — Ownership-based overvaluation.
    Effect: DESTABILIZING — inflates prices by withholding supply.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
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
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        fundamental = market_data.get("fundamental", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        endowment_premium = float(extras.get("endowment_premium", 0.15))
        sell_reluctance = float(extras.get("sell_reluctance", 0.8))
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


class StatusQuoSeller(GeneralPlayer):
    """Holds positions too long due to status quo bias, demands premium to sell.

    Theory: Samuelson & Zeckhauser (1988) — Status quo bias in decision making.
    Effect: DESTABILIZING — reduces liquidity by hoarding positions.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
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
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        fundamental = market_data.get("fundamental", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        status_quo_threshold = float(extras.get("status_quo_threshold", 0.20))
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


class RationalArbitrageur(GeneralPlayer):
    """Exploits the gap between subjective and objective valuations.

    Theory: Shleifer & Vishny (1997) — Limits to arbitrage.
    Effect: STABILIZING — pushes prices toward fundamental value.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
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
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        fundamental = market_data.get("fundamental", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        arb_threshold = float(extras.get("arb_threshold", 0.05))
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


class NewBuyer(GeneralPlayer):
    """Evaluates assets at market price without ownership bias.

    Theory: Kahneman et al. (1990) — Buyers unaffected by endowment effect.
    Effect: STABILIZING — provides rational price discovery from buyer side.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
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
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        fundamental = market_data.get("fundamental", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        buy_threshold = float(extras.get("buy_threshold", -0.03))
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


class NoiseTrader(GeneralPlayer):
    """Random uninformed trader providing baseline liquidity.

    Theory: Black (1986) — Noise trading and market efficiency.
    Effect: NEUTRAL — provides random liquidity with no directional bias.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
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
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        trade_probability = float(extras.get("trade_probability", 0.4))
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
    "EndowedHolder",
    "StatusQuoSeller",
    "RationalArbitrageur",
    "NewBuyer",
    "NoiseTrader",
]
