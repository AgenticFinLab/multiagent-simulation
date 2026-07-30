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
import os
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("GFC2008")


def _build_order(
    player: GeneralPlayer,
    action: str,
    quantity: int,
    price: float,
    reasoning: str,
) -> Dict[str, Any]:
    """Build the canonical trading order shared by all GFC2008 variants."""
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"{player.identity} emitted invalid action: {action}")
    if price <= 0:
        raise ValueError(f"{player.identity} emitted non-positive bid_price: {price}")
    return {
        "type": "order",
        "from": player.identity,
        "action": action,
        "bid_price": float(price),
        "quantity": max(0, int(quantity)),
        "reasoning": reasoning,
        "agent_type": player.__class__.__name__,
        "strategy": player.__class__.__name__,
    }


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
            if isinstance(payload, dict) and "type" not in payload and "order" in payload:
                payload = payload["order"]
            if isinstance(payload, dict) and payload.get("type") == "order":
                orders.append(
                    {
                        "agent_id": payload["from"],
                        "action": payload["action"],
                        "quantity": payload["quantity"],
                        "agent_type": payload["agent_type"],
                    }
                )
        self.state.custom_state["pending_orders"] = orders

    async def decide(self) -> dict:
        """Clear market and compute new price."""
        orders = self.state.custom_state["pending_orders"]
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
        market_update = {
            "type": "market_update",
            "price": new_price,
            "prev_price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        return {
            "market_data": market_update,
            "outbound_messages": [
                {"payload": market_update, "content_type": "market_update"}
            ],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Broadcast market update to all agents."""
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class MBSOriginator(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.1 — MBSOriginator

    Theoretical basis: Originate-to-distribute model (Keys et al., 2010).
    Creates mortgage-backed securities with lax screening; originate-to-distribute model.
    See simulation-bases.md §4.1 for mathematical model.
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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        """Originate-to-distribute: sell securities at a steady rate regardless of price."""
        extras = self.config.extras
        position = self.state.custom_state["position"]
        origination_rate = extras["origination_rate"]

        sell_qty = int(abs(position) * origination_rate)
        if sell_qty > 0 and position > 0:
            action, quantity = "sell", sell_qty
            reasoning = "originator distributes MBS inventory to generate fee income"
        else:
            action, quantity = "hold", 0
            reasoning = "originator has no positive distribution quantity"

        order = _build_order(
            self, action, quantity,
            self.state.custom_state["price"], reasoning,
        )
        return {
            "action": action,
            "quantity": quantity,
            "bid_price": self.state.custom_state["price"],
            "reasoning": reasoning,
            "order": order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class RatingAgency(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.2 — RatingAgency

    Theoretical basis: Rating agency conflict of interest (Bolton et al., 2012).
    Overrates securities due to issuer-pays model; creates inflated valuations.
    See simulation-bases.md §4.2 for mathematical model.
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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        """Buy when price below overrated fundamental; inflated by overrating bias."""
        extras = self.config.extras
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        cash = self.state.custom_state["cash"]
        overrating_bias = extras["overrating_bias"]

        perceived_fundamental = fundamental * (1 + overrating_bias)
        if price < perceived_fundamental * 0.95:
            buy_qty = min(300, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty
                reasoning = "rating agency buys below inflated perceived fundamental value"
            else:
                action, quantity = "hold", 0
                reasoning = "price is not attractive under the inflated rating view"
        else:
            action, quantity = "hold", 0
            reasoning = "price is not attractive under the inflated rating view"

        order = _build_order(self, action, quantity, price, reasoning)
        return {
            "action": action,
            "quantity": quantity,
            "bid_price": price,
            "reasoning": reasoning,
            "order": order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class LeveragedInvestor(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.3 — LeveragedInvestor

    Theoretical basis: Leverage cycle (Adrian & Shin, 2010).
    Uses high leverage; forced to sell in downturn (margin call / fire sale).
    See simulation-bases.md §4.3 for mathematical model.
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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        """Fire sale 50% of position when deviation drops below margin call trigger."""
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        position = self.state.custom_state["position"]
        margin_trigger = extras["margin_call_trigger"]

        if deviation < -margin_trigger:
            fire_sale_qty = int(abs(position) * 0.5)
            if position > 0 and fire_sale_qty > 0:
                action = "sell"
                quantity = min(fire_sale_qty, position)
                reasoning = "margin-call pressure forces leveraged deleveraging"
            else:
                action, quantity = "hold", 0
                reasoning = "margin-call threshold has not been breached"
        else:
            action, quantity = "hold", 0
            reasoning = "margin-call threshold has not been breached"

        order = _build_order(
            self, action, quantity,
            self.state.custom_state["price"], reasoning,
        )
        return {
            "action": action,
            "quantity": quantity,
            "bid_price": self.state.custom_state["price"],
            "reasoning": reasoning,
            "order": order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class DistressedBuyer(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.4 — DistressedBuyer

    Theoretical basis: Distressed debt investing (Griffin & Xu, 2009).
    Buys assets at deep discount during panic selling.
    See simulation-bases.md §4.4 for mathematical model.
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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        """Buy 30% of cash when price is deeply discounted."""
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        discount_threshold = extras["discount_threshold"]

        if deviation < -discount_threshold:
            buy_qty = min(1000, int(cash * 0.3 / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty
                reasoning = "distressed buyer deploys capital after deep discount signal"
            else:
                action, quantity = "hold", 0
                reasoning = "discount is not deep enough for distressed entry"
        else:
            action, quantity = "hold", 0
            reasoning = "discount is not deep enough for distressed entry"

        order = _build_order(self, action, quantity, price, reasoning)
        return {
            "action": action,
            "quantity": quantity,
            "bid_price": price,
            "reasoning": reasoning,
            "order": order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class Regulator(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.5 — Regulator

    Theoretical basis: Macroprudential regulation (Bernanke, 2015).
    Monitors systemic risk and may intervene during market stress.
    See simulation-bases.md §4.5 for mathematical model.
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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        """Intervene with large buy when systemic stress exceeds threshold."""
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        intervention_threshold = extras["intervention_threshold"]
        rescue_probability = extras["rescue_probability"]

        if deviation < -intervention_threshold and random.random() < rescue_probability:
            action = "buy"
            quantity = int(extras["rescue_size"])
            reasoning = "regulator backstop activates under systemic stress"
        else:
            action, quantity = "hold", 0
            reasoning = "systemic intervention threshold or probability gate not met"

        order = _build_order(
            self, action, quantity,
            self.state.custom_state["price"], reasoning,
        )
        return {
            "action": action,
            "quantity": quantity,
            "bid_price": self.state.custom_state["price"],
            "reasoning": reasoning,
            "order": order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: dict) -> Action:
        """Update portfolio and send order."""
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "_build_order",
    "MBSOriginator",
    "RatingAgency",
    "LeveragedInvestor",
    "DistressedBuyer",
    "Regulator",
]
