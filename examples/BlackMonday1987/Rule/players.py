"""BlackMonday1987 Rule-Based Simulation

October 19, 1987 stock market crash — Dow fell 22.6% in one day.

Theoretical Foundation:
- Brady Commission (1988): Portfolio insurance as key amplifier
- Genotte & Leland (1990): Noise trading and portfolio insurance
- Jacklin et al. (1992): Information cascades during crash

Agents:
- Market: Price formation via net-demand impact + mean-reversion
- PortfolioInsurer: Dynamic hedging — sells as prices fall (destabilizing)
- IndexArbitrageur: Exploits price gaps between futures and spot (destabilizing)
- ProgramTrader: Automated trading that amplifies price moves (destabilizing)
- ValueInvestor: Buys when price falls below intrinsic value (stabilizing)
- NoiseTrader: Random uninformed trader (neutral)
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger(__name__)


class Market(GeneralPlayer):
    """Market agent — clears orders and broadcasts price each round."""

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
                folder="BlackMonday1987/Market", entry_limit=200
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


class PortfolioInsurer(GeneralPlayer):
    """Dynamic hedging — sells as prices fall (destabilizing).

    Theory: simulation-bases.md §4.1 — PortfolioInsurer
    Theoretical basis: Leland & Rubinstein (1980) portfolio insurance; sells equities
    as prices fall to maintain a synthetic put, creating a positive feedback loop.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="BlackMonday1987/PortfolioInsurer", entry_limit=200
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
        hedge_ratio = float(extras["hedge_ratio"])
        rebalance_threshold = float(extras["rebalance_threshold"])

        action, quantity = "hold", 0
        if abs(deviation) > rebalance_threshold:
            if deviation < 0:
                sell_qty = int(abs(deviation) * hedge_ratio * abs(position))
                sell_qty = min(sell_qty, max(position, 0))
                if sell_qty > 0:
                    action, quantity = "sell", sell_qty
            else:
                buy_qty = (
                    int(deviation * hedge_ratio * cash / price) if price > 0 else 0
                )
                buy_qty = min(buy_qty, 500)
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


class IndexArbitrageur(GeneralPlayer):
    """Exploits price gaps between index futures and spot (destabilizing).

    Theory: simulation-bases.md §4.2 — IndexArbitrageur
    Theoretical basis: MacKinlay & Ramaswamy (1988) index arbitrage; mechanical
    selling when futures fall below spot amplifies downward price pressure.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="BlackMonday1987/IndexArbitrageur", entry_limit=200
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
        arb_threshold = float(extras["arb_threshold"])
        position_size = int(extras["base_size"])

        action, quantity = "hold", 0
        if abs(deviation) > arb_threshold:
            if deviation > 0:
                sell_qty = min(position_size, max(position, 0))
                if sell_qty > 0:
                    action, quantity = "sell", sell_qty
            else:
                buy_qty = min(position_size, int(cash / price) if price > 0 else 0)
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


class ProgramTrader(GeneralPlayer):
    """Automated trading that amplifies price moves (destabilizing).

    Theory: simulation-bases.md §4.3 — ProgramTrader
    Theoretical basis: Brady Commission (1988) program trading feedback loops;
    automated sell triggers on price thresholds cascade into a self-reinforcing crash.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="BlackMonday1987/ProgramTrader", entry_limit=200
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
        trigger_threshold = float(extras["trigger_threshold"])
        sell_size = int(extras["base_size"])
        feedback_strength = float(extras["feedback_strength"])

        action, quantity = "hold", 0
        if deviation < -trigger_threshold:
            amplified = int(sell_size * (1 + feedback_strength * abs(deviation) * 10))
            sell_qty = min(amplified, max(position, 0))
            if sell_qty > 0:
                action, quantity = "sell", sell_qty
        elif deviation > trigger_threshold:
            buy_qty = min(sell_size, int(cash / price) if price > 0 else 0)
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


class ValueInvestor(GeneralPlayer):
    """Buys when price falls below intrinsic value (stabilizing).

    Theory: simulation-bases.md §4.4 — ValueInvestor
    Theoretical basis: Graham (1949) value investing with margin of safety;
    purchases equities at deep discount to fundamental value.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="BlackMonday1987/ValueInvestor", entry_limit=200
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
        value_discount = float(extras["value_discount"])
        order_size = int(extras["base_size"])

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
    """Random uninformed trader (neutral).

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: Black (1986) — noise makes markets possible; provides
    liquidity and baseline price variance independent of fundamentals.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="BlackMonday1987/NoiseTrader", entry_limit=200
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
        min_order = int(extras["min_order"])
        max_order = int(extras["max_order"])

        action, quantity = "hold", 0
        if random.random() < prob:
            qty = random.randint(min_order, max_order)
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
    "PortfolioInsurer",
    "IndexArbitrageur",
    "ProgramTrader",
    "ValueInvestor",
    "NoiseTrader",
]
