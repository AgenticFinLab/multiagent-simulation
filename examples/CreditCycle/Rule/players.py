"""CreditCycle Rule-Based Simulation

Credit cycle where leverage expands during booms and contracts during crises,
amplifying business cycle fluctuations.

Theoretical Foundation:
- Geanakoplos (2010): The leverage cycle
- Minsky (1986): Stabilizing an unstable economy
- Adrian & Shin (2010): Liquidity and leverage

Agents:
- Market: Price formation via net-demand + mean-reversion
- ProCyclicalLender: Expands credit during booms, tightens during downturns (destabilizing)
- MinskyBorrower: Increases debt during stability, creating fragility (destabilizing)
- CounterCyclicalLender: Lends counter-cyclically, provides liquidity during crises (stabilizing)
- ValueInvestor: Invests on fundamentals, providing stability during expansions (stabilizing)
- NoiseTrader: Random uninformed trader providing baseline liquidity (neutral)
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger(__name__)


class Market(GeneralPlayer):
    """Credit market — clears orders and broadcasts price each round."""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["price"] = float(extras["initial_price"])
            self.state.custom_state["fundamental"] = float(extras["fundamental_value"])
            self.state.custom_state["price_impact"] = float(extras["price_impact"])
            self.state.custom_state["mean_reversion"] = float(extras["mean_reversion"])
            self.state.custom_state["noise_std"] = float(extras["noise_std"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CreditCycle/Market", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        orders: List[Dict] = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict):
                    orders.append(payload)

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        buy_vol = sum(o.get("quantity", 0) for o in orders if o.get("action") == "buy")
        sell_vol = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "sell"
        )
        net_demand = buy_vol - sell_vol

        price_change = self.state.custom_state["price_impact"] * net_demand
        reversion = self.state.custom_state["mean_reversion"] * (fundamental - price)
        noise = random.gauss(0, self.state.custom_state["noise_std"])
        new_price = max(price + price_change + reversion + noise, 0.01)
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0
        self.state.custom_state["deviation"] = deviation
        logger.debug(
            "Round %d: price=%.2f deviation=%.4f",
            observation.round,
            new_price,
            deviation,
        )

    async def decide(self) -> Dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
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


class ProCyclicalLender(GeneralPlayer):
    """Expands credit during booms, tightens during downturns — amplifies credit cycle.

    Theory: Adrian & Shin (2010) pro-cyclical leverage. Lending standards loosen
    when asset prices rise and tighten when prices fall.
    Role: destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CreditCycle/ProCyclicalLender", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        expansion_threshold = float(extras.get("expansion_threshold", 0.03))
        credit_multiplier = float(extras.get("credit_multiplier", 2.0))
        order_size = int(extras.get("order_size", 600))

        action, quantity = "hold", 0
        if deviation > expansion_threshold:
            # Boom: loosen lending, buy more credit assets
            qty = min(
                int(order_size * credit_multiplier),
                int(cash / price) if price > 0 else 0,
            )
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation < -expansion_threshold:
            # Bust: tighten lending, sell credit assets
            qty = min(order_size, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class MinskyBorrower(GeneralPlayer):
    """Increases leverage during stability, creating fragility that leads to crisis.

    Theory: Minsky (1986) financial instability hypothesis. Periods of stability
    breed instability as agents take on more debt.
    Role: destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["leverage"] = float(
                extras.get("initial_leverage", 1.0)
            )
            self.state.custom_state["stable_rounds"] = 0
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CreditCycle/MinskyBorrower", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        max_leverage = float(extras.get("max_leverage", 5.0))
        crisis_threshold = float(extras.get("crisis_threshold", -0.05))
        order_size = int(extras.get("order_size", 500))

        # Track stability
        if abs(deviation) < 0.02:
            self.state.custom_state["stable_rounds"] = (
                self.state.custom_state.get("stable_rounds", 0) + 1
            )
        else:
            self.state.custom_state["stable_rounds"] = 0

        stable = self.state.custom_state.get("stable_rounds", 0)
        action, quantity = "hold", 0

        if deviation < crisis_threshold:
            # Crisis: forced deleveraging — sell everything
            qty = min(int(order_size * 2), max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        elif stable > 3:
            # Extended stability: increase leverage (buy more)
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class CounterCyclicalLender(GeneralPlayer):
    """Lends counter-cyclically — provides liquidity during crises when others withdraw.

    Theory: Geanakoplos (2010) leverage cycle. Counter-cyclical capital buffers.
    Role: stabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CreditCycle/CounterCyclicalLender", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        crisis_buy_threshold = float(extras.get("crisis_buy_threshold", -0.05))
        boom_sell_threshold = float(extras.get("boom_sell_threshold", 0.05))
        order_size = int(extras.get("order_size", 500))

        action, quantity = "hold", 0
        if deviation < crisis_buy_threshold:
            # Crisis: inject liquidity (buy)
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty
        elif deviation > boom_sell_threshold:
            # Boom: build reserves (sell)
            sell_qty = min(order_size, max(position, 0))
            if sell_qty > 0:
                action, quantity = "sell", sell_qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class ValueInvestor(GeneralPlayer):
    """Invests based on fundamental value — stabilizing force during credit expansions.

    Theory: Graham (1949) value investing with margin of safety.
    Role: stabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CreditCycle/ValueInvestor", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        value_discount = float(extras.get("value_discount", 0.10))
        order_size = int(extras.get("order_size", 400))

        action, quantity = "hold", 0
        if deviation < -value_discount:
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty
        elif deviation > value_discount:
            sell_qty = min(order_size, max(position, 0))
            if sell_qty > 0:
                action, quantity = "sell", sell_qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class NoiseTrader(GeneralPlayer):
    """Random uninformed trader providing baseline liquidity.

    Theory: Black (1986) noise trader model.
    Role: neutral.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CreditCycle/NoiseTrader", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        prob = float(extras["trade_probability"])

        action, quantity = "hold", 0
        if random.random() < prob:
            qty = random.randint(100, 500)
            side = "buy" if random.random() > 0.5 else "sell"
            if side == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                action, quantity = side, qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


__all__ = [
    "Market",
    "ProCyclicalLender",
    "MinskyBorrower",
    "CounterCyclicalLender",
    "ValueInvestor",
    "NoiseTrader",
]
