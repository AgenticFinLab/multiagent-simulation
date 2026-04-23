"""FramingEffect Rule-Based Simulation

Framing effect causes traders to make different decisions based on how equivalent
information is presented.

Theoretical Foundation:
- Tversky & Kahneman (1981): The framing of decisions and the psychology of choice
- Levin, Schneider & Gaeth (1998): All frames are not created equal
- Kuhberger (1998): The influence of framing on risky decisions

Key Dynamics:
- GainFrameFollower: Overweights gains-framed information, risk-averse on gains
- LossFrameReactor: Overweights loss-framed information, risk-seeking on losses
- FrameInvariantTrader: Evaluates information by substance regardless of framing
- ArbitrageFramer: Exploits framing-induced mispricing
- NoiseTrader: Random uninformed trader providing baseline liquidity
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("FramingEffect")


class Market(GeneralPlayer):
    """
    Market agent for FramingEffect simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """

    async def perceive(self, observation: Observation, prev_result: Optional[StepResult] = None) -> None:
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
            folder = os.path.join("outputs", "FramingEffect", "Rule", "Market")
            self.state.custom_state["history"] = HistoryBuffer(folder=folder, entry_limit=200)

        orders = []
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "order":
                orders.append({
                    "agent_id": payload.get("from"),
                    "action": payload.get("action"),
                    "quantity": payload.get("quantity", 0),
                    "agent_type": payload.get("agent_type"),
                })
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
            self.state.custom_state["round"], new_price, deviation
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
                "outbound_messages": [{"payload": market_update, "content_type": "market_update"}],
            },
            source_id=self.identity,
        )


class GainFrameFollower(GeneralPlayer):
    """
    Overweights gains-framed information, becomes risk-averse when returns are presented as gains.

    Theoretical Basis: Gain frame risk aversion (Tversky & Kahneman, 1981)
    Market Role: destabilizing
    """

    async def perceive(self, observation: Observation, prev_result: Optional[StepResult] = None) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get("fundamental_value", 100.0)
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get("price", self.state.custom_state["price"])
                self.state.custom_state["fundamental"] = payload.get("fundamental", self.state.custom_state["fundamental"])
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Buy when price > fundamental (gain frame), sell when below."""
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
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
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class LossFrameReactor(GeneralPlayer):
    """
    Overweights loss-framed information, becomes risk-seeking when presented with potential losses.

    Theoretical Basis: Loss frame risk seeking (Tversky & Kahneman, 1981)
    Market Role: destabilizing
    """

    async def perceive(self, observation: Observation, prev_result: Optional[StepResult] = None) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get("fundamental_value", 100.0)
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get("price", self.state.custom_state["price"])
                self.state.custom_state["fundamental"] = payload.get("fundamental", self.state.custom_state["fundamental"])
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """React aggressively to loss frames: sell on gain, buy on loss."""
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
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
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class FrameInvariantTrader(GeneralPlayer):
    """
    Evaluates information by substance regardless of framing, computes equivalent outcomes.

    Theoretical Basis: Frame-invariant rationality (Levin et al., 1998 baseline)
    Market Role: stabilizing
    """

    async def perceive(self, observation: Observation, prev_result: Optional[StepResult] = None) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get("fundamental_value", 100.0)
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get("price", self.state.custom_state["price"])
                self.state.custom_state["fundamental"] = payload.get("fundamental", self.state.custom_state["fundamental"])
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Contrarian: buy when price < fundamental (|deviation| > 5%), sell when above."""
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
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
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class ArbitrageFramer(GeneralPlayer):
    """
    Exploits framing-induced mispricing by recognizing when same data drives different prices.

    Theoretical Basis: Framing arbitrage (Kuhberger, 1998)
    Market Role: stabilizing
    """

    async def perceive(self, observation: Observation, prev_result: Optional[StepResult] = None) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get("fundamental_value", 100.0)
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get("price", self.state.custom_state["price"])
                self.state.custom_state["fundamental"] = payload.get("fundamental", self.state.custom_state["fundamental"])
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Exploit framing mispricing: buy cheap, sell expensive."""
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
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
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """
    Random uninformed trader providing baseline liquidity.

    Theoretical Basis: Noise trader model (Black, 1986)
    Market Role: neutral
    """

    async def perceive(self, observation: Observation, prev_result: Optional[StepResult] = None) -> None:
        """Initialize portfolio; read market update from inbounds."""
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["deviation"] = 0.0

        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload.get("price", self.state.custom_state["price"])
                self.state.custom_state["deviation"] = payload.get("deviation", 0.0)

    async def decide(self) -> dict:
        """Random 30% chance to trade 100-500 shares."""
        extras = self.config.extras
        trade_probability = extras.get("trade_probability", 0.3)
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if random.random() < trade_probability:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
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
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "GainFrameFollower",
    "LossFrameReactor",
    "FrameInvariantTrader",
    "ArbitrageFramer",
    "NoiseTrader",
]
