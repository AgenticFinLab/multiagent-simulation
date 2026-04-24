"""GFC2008 Rule-Based Simulation

2007-2009 Global Financial Crisis: Housing bubble burst triggered global recession.

Theoretical Foundation:
- Gorton (2010): Securitized banking and the run on repo
- Brunnermeier (2009): Deciphering the liquidity and credit crunch
- Acharya & Richardson (2009): Restoring financial stability

Key Dynamics:
- MBSOriginator: Creates mortgage-backed securities with lax screening
- RatingAgency: Overrates securities due to issuer-pays model
- LeveragedInvestor: Uses high leverage, forced to sell in downturn
- DistressedBuyer: Buys assets at deep discount during panic
- Regulator: Monitors systemic risk and may intervene
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("GFC2008")


class Market(GeneralPlayer):
    """
    Market agent for GFC2008 simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        """Collect orders from inbound messages; initialize state on first round."""
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            import os

            extras = self.config.extras
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_history"] = []
            self.state.custom_state["volume_history"] = []
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
            folder = os.path.join("outputs", "GFC2008", "Rule", "Market")
            self.state.custom_state["history"] = HistoryBuffer(
                folder=folder, entry_limit=200
            )

        orders = []
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "order":
                orders.append(
                    {
                        "agent_id": payload.get("from"),
                        "action": payload.get("action"),
                        "quantity": payload.get("quantity", 0),
                        "agent_type": payload.get("agent_type"),
                    }
                )
        self.state.custom_state["pending_orders"] = orders

    async def decide(self) -> dict:
        """Clear market and compute new price."""
        orders = self.state.custom_state.get("pending_orders", [])
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
        new_price = max(price + price_change + reversion + noise, 0.01)
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(volume)

        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0
        logger.debug(
            "Round %d: price=%.2f deviation=%.4f",
            self.state.custom_state["round"],
            new_price,
            deviation,
        )
        return {
            "price": new_price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Broadcast market update to all agents."""
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


class MBSOriginator(GeneralPlayer):
    """
    Creates mortgage-backed securities with lax screening; originate-to-distribute model.

    Theoretical Basis: Originate-to-distribute model (Keys et al., 2010)
    Market Role: destabilizing
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get(
                "fundamental_value", 100.0
            )
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get(
                    "price", self.state.custom_state["price"]
                )
                self.state.custom_state["fundamental"] = payload.get(
                    "fundamental", self.state.custom_state["fundamental"]
                )
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Originate-to-distribute: sell securities at a steady rate regardless of price."""
        extras = self.config.extras
        position = self.state.custom_state["position"]
        origination_rate = extras.get("origination_rate", 0.1)

        sell_qty = int(abs(position) * origination_rate)
        if sell_qty > 0 and position > 0:
            return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RatingAgency(GeneralPlayer):
    """
    Overrates securities due to issuer-pays model; creates inflated valuations.

    Theoretical Basis: Rating agency conflict of interest (Bolton et al., 2012)
    Market Role: destabilizing
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get(
                "fundamental_value", 100.0
            )
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get(
                    "price", self.state.custom_state["price"]
                )
                self.state.custom_state["fundamental"] = payload.get(
                    "fundamental", self.state.custom_state["fundamental"]
                )
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Buy when price below overrated fundamental; inflated by overrating bias."""
        extras = self.config.extras
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        cash = self.state.custom_state["cash"]
        overrating_bias = extras.get("overrating_bias", 0.2)

        perceived_fundamental = fundamental * (1 + overrating_bias)
        if price < perceived_fundamental * 0.95:
            buy_qty = min(300, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LeveragedInvestor(GeneralPlayer):
    """
    Uses high leverage; forced to sell in downturn (margin call / fire sale).

    Theoretical Basis: Leverage cycle (Adrian & Shin, 2010)
    Market Role: destabilizing
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get(
                "fundamental_value", 100.0
            )
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get(
                    "price", self.state.custom_state["price"]
                )
                self.state.custom_state["fundamental"] = payload.get(
                    "fundamental", self.state.custom_state["fundamental"]
                )
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Fire sale 50% of position when deviation drops below margin call trigger."""
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        position = self.state.custom_state["position"]
        margin_trigger = extras.get("margin_call_trigger", 0.1)

        if deviation < -margin_trigger:
            fire_sale_qty = int(abs(position) * 0.5)
            if position > 0 and fire_sale_qty > 0:
                return {"action": "sell", "quantity": min(fire_sale_qty, position)}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class DistressedBuyer(GeneralPlayer):
    """
    Buys assets at deep discount during panic selling.

    Theoretical Basis: Distressed debt investing (Griffin & Xu, 2009)
    Market Role: stabilizing
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get(
                "fundamental_value", 100.0
            )
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get(
                    "price", self.state.custom_state["price"]
                )
                self.state.custom_state["fundamental"] = payload.get(
                    "fundamental", self.state.custom_state["fundamental"]
                )
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Buy 30% of cash when price is deeply discounted."""
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        discount_threshold = extras.get("discount_threshold", 0.15)

        if deviation < -discount_threshold:
            buy_qty = min(1000, int(cash * 0.3 / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class Regulator(GeneralPlayer):
    """
    Monitors systemic risk and may intervene during market stress.

    Theoretical Basis: Macroprudential regulation (Bernanke, 2015)
    Market Role: stabilizing
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras.get("initial_cash", 10000000.0)
            self.state.custom_state["position"] = extras.get("initial_position", 0)
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get(
                "fundamental_value", 100.0
            )
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get(
                    "price", self.state.custom_state["price"]
                )
                self.state.custom_state["fundamental"] = payload.get(
                    "fundamental", self.state.custom_state["fundamental"]
                )
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Intervene with large buy when systemic stress exceeds threshold."""
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        intervention_threshold = extras.get("intervention_threshold", 0.2)
        rescue_probability = extras.get("rescue_probability", 0.3)

        if deviation < -intervention_threshold and random.random() < rescue_probability:
            return {"action": "buy", "quantity": 3000}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload.get("action", "hold")
        quantity = decision_payload.get("quantity", 0)
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
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
    "MBSOriginator",
    "RatingAgency",
    "LeveragedInvestor",
    "DistressedBuyer",
    "Regulator",
]
