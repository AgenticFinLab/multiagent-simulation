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
import os
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger(__name__)


class Market(GeneralPlayer):
    """Credit market — clears orders and broadcasts price each round."""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = float(extras["initial_price"])
            self.state.custom_state["fundamental"] = float(extras["fundamental_value"])
            self.state.custom_state["price_impact"] = float(extras["price_impact"])
            self.state.custom_state["mean_reversion"] = float(extras["mean_reversion"])
            self.state.custom_state["noise_std"] = float(extras["noise_std"])
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "fundamental"),
                entry_limit=custom_state_hot_limit,
            )
        orders: List[Dict] = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict):
                    orders.append(payload)

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        buy_vol = sum(o["quantity"] for o in orders if o["action"] == "buy")
        sell_vol = sum(o["quantity"] for o in orders if o["action"] == "sell")
        net_demand = buy_vol - sell_vol

        price_change = self.state.custom_state["price_impact"] * net_demand
        reversion = self.state.custom_state["mean_reversion"] * (fundamental - price)
        noise = random.gauss(0, self.state.custom_state["noise_std"])
        new_price = max(price + price_change + reversion + noise, 0.01)
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["fundamental_history"].append(fundamental)

        if fundamental <= 0:
            # Fundamental must be positive in this scenario — it seeds mean
            # reversion, deviation, and every downstream decision rule.  A
            # silent 0.0 deviation fallback would mask a broken configuration
            # AND coincide with the "at fundamental" null hypothesis that
            # nearly every rule tests for.  Fail loudly instead.
            raise ValueError(
                f"CreditCycle Coordinator: non-positive fundamental "
                f"({fundamental!r}) at round {observation.round}; "
                "cannot compute deviation."
            )
        deviation = (new_price - fundamental) / fundamental
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

    Theory: simulation-bases.md §4.1 — ProCyclicalLender
    Theoretical basis: Adrian & Shin (2010) pro-cyclical leverage; lending standards
    loosen with rising asset prices and tighten when prices fall, amplifying the cycle.
    See simulation-bases.md §4.1 for mathematical model.
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        expansion_threshold = float(extras["expansion_threshold"])
        credit_multiplier = float(extras["credit_multiplier"])
        order_size = int(extras["order_size"])

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
        price = self.state.custom_state["market_data"]["price"]
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

    Theory: simulation-bases.md §4.2 — MinskyBorrower
    Theoretical basis: Minsky (1986) financial instability hypothesis; periods of
    stability breed instability as agents accumulate debt through hedge→speculative→Ponzi.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["leverage"] = float(extras["initial_leverage"])
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        max_leverage = float(extras["max_leverage"])
        crisis_threshold = float(extras["crisis_threshold"])
        order_size = int(extras["order_size"])

        # Track stability
        if abs(deviation) < 0.02:
            self.state.custom_state["stable_rounds"] = (
                self.state.custom_state["stable_rounds"] + 1
            )
        else:
            self.state.custom_state["stable_rounds"] = 0

        stable = self.state.custom_state["stable_rounds"]
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
        price = self.state.custom_state["market_data"]["price"]
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

    Theory: simulation-bases.md §4.3 — CounterCyclicalLender
    Theoretical basis: Geanakoplos (2010) leverage cycle; counter-cyclical capital buffers
    dampen boom-bust by accumulating reserves during booms and deploying in crises.
    See simulation-bases.md §4.3 for mathematical model.
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        crisis_buy_threshold = float(extras["crisis_buy_threshold"])
        boom_sell_threshold = float(extras["boom_sell_threshold"])
        order_size = int(extras["order_size"])

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
        price = self.state.custom_state["market_data"]["price"]
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

    Theory: simulation-bases.md §4.4 — ValueInvestor
    Theoretical basis: Graham (1949) value investing with margin of safety; buys
    deeply discounted credit assets and sells overpriced, anchoring price to fundamentals.
    See simulation-bases.md §4.4 for mathematical model.
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        value_discount = float(extras["value_discount"])
        order_size = int(extras["order_size"])

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
        price = self.state.custom_state["market_data"]["price"]
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

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: Black (1986) noise trader model; random orders provide
    liquidity and stochastic price variance independent of the credit cycle state.
    See simulation-bases.md §4.5 for mathematical model.
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
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
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
        price = self.state.custom_state["market_data"]["price"]
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
