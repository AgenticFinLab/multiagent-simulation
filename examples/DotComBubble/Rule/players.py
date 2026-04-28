"""DotComBubble Rule-Based Simulation

1995-2001 Internet bubble — NASDAQ rose 400% then fell 78%.

Theoretical Foundation:
- Shiller (2000): Irrational exuberance and narrative economics
- Ofek & Richardson (2003): Internet bubble dynamics
- Abreu & Brunnermeier (2003): Synchronization risk and bubble persistence

Agents:
- Market: Price formation via net-demand + mean-reversion
- NewEconomyEvangelist: Believes in new paradigm, ignores traditional valuation (destabilizing)
- IPOFlipper: Buys IPOs and quickly sells for short-term profit (destabilizing)
- MomentumFollower: Follows price trends and amplifies moves (destabilizing)
- SkepticalValueInvestor: Waits for correction, buys undervalued assets (stabilizing)
- ShortSeller: Bets against overvalued stocks but faces squeeze risk (stabilizing)
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger(__name__)


class Market(GeneralPlayer):
    """Tech/equity market — clears orders and broadcasts price each round."""

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
                folder="DotComBubble/Market", entry_limit=200
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


class NewEconomyEvangelist(GeneralPlayer):
    """Believes in new paradigm — ignores traditional valuation metrics during internet bubble.

    Theory: simulation-bases.md §4.1 — NewEconomyEvangelist
    Theoretical basis: Shiller (2000) narrative economics; tech evangelists dismiss P/E ratios as irrelevant.
    See simulation-bases.md §4.1 for mathematical model.
    Role: destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="DotComBubble/NewEconomyEvangelist", entry_limit=200
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
        order_size = int(extras.get("order_size", 600))

        action, quantity = "hold", 0
        # Ignores overvaluation — keeps buying as long as price is rising
        if deviation > -0.20:
            # Buy as long as not deeply below fundamental
            qty = min(order_size, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation < -0.30:
            # Only sell at extreme crash
            qty = min(order_size // 2, max(position, 0))
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


class IPOFlipper(GeneralPlayer):
    """Buys IPOs and quickly sells for short-term profit.

    Theory: simulation-bases.md §4.2 — IPOFlipper
    Theoretical basis: Ofek & Richardson (2003) IPO dynamics; Ritter (1991) underpricing and flipping.
    See simulation-bases.md §4.2 for mathematical model.
    Role: destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="DotComBubble/IPOFlipper", entry_limit=200
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
        order_size = int(extras.get("order_size", 700))
        flip_threshold = float(extras.get("flip_threshold", 0.05))

        action, quantity = "hold", 0
        if deviation > flip_threshold and position > 0:
            # Price popped — flip (sell)
            qty = min(order_size, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        elif deviation < 0:
            # Price dipped — buy in for next flip
            qty = min(order_size, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty

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


class MomentumFollower(GeneralPlayer):
    """Follows price trends and amplifies moves — trend-chasing behavior.

    Theory: simulation-bases.md §4.3 — MomentumFollower
    Theoretical basis: Abreu & Brunnermeier (2003) momentum synchronization; Jegadeesh & Titman (1993).
    See simulation-bases.md §4.3 for mathematical model.
    Role: destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="DotComBubble/MomentumFollower", entry_limit=200
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
        order_size = int(extras.get("order_size", 500))
        momentum_threshold = float(extras.get("momentum_threshold", 0.02))

        # Compute short-term momentum from price history
        price_history = self.state.custom_state["price_history"]
        action, quantity = "hold", 0
        if len(price_history) >= 2:
            momentum = (
                (price_history[-1] - price_history[-2]) / price_history[-2]
                if price_history[-2] > 0
                else 0
            )
            if momentum > momentum_threshold:
                qty = min(order_size, int(cash / price) if price > 0 else 0)
                if qty > 0:
                    action, quantity = "buy", qty
            elif momentum < -momentum_threshold:
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


class SkepticalValueInvestor(GeneralPlayer):
    """Avoids overvalued tech stocks — waits for correction, then buys.

    Theory: simulation-bases.md §4.4 — SkepticalValueInvestor
    Theoretical basis: Graham (1949) value investing; Abreu & Brunnermeier (2003) rational arbitrageurs too early.
    See simulation-bases.md §4.4 for mathematical model.
    Role: stabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="DotComBubble/SkepticalValueInvestor", entry_limit=200
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
        value_buy_threshold = float(extras.get("value_buy_threshold", -0.10))
        value_sell_threshold = float(extras.get("value_sell_threshold", 0.20))
        order_size = int(extras.get("order_size", 400))

        action, quantity = "hold", 0
        if deviation < value_buy_threshold:
            # Post-crash buying
            qty = min(order_size, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation > value_sell_threshold:
            # Sell overvalued assets
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


class ShortSeller(GeneralPlayer):
    """Bets against overvalued stocks — faces squeeze risk during bubble.

    Theory: simulation-bases.md §4.5 — ShortSeller
    Theoretical basis: Abreu & Brunnermeier (2003) limits to arbitrage; short sellers face synchronization risk.
    See simulation-bases.md §4.5 for mathematical model.
    Role: stabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="DotComBubble/ShortSeller", entry_limit=200
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
        short_threshold = float(extras.get("short_threshold", 0.15))
        cover_threshold = float(extras.get("cover_threshold", -0.05))
        order_size = int(extras.get("order_size", 400))

        action, quantity = "hold", 0
        if deviation > short_threshold:
            # Short (sell) overvalued stocks
            qty = min(order_size, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        elif deviation < cover_threshold:
            # Cover shorts (buy back) as price falls
            qty = min(order_size, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty

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
    "NewEconomyEvangelist",
    "IPOFlipper",
    "MomentumFollower",
    "SkepticalValueInvestor",
    "ShortSeller",
]
