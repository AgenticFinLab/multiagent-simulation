"""CurrencyCrisis Rule-Based Simulation

Self-fulfilling speculative currency attacks where market expectations of
devaluation trigger the crisis itself.

Theoretical Foundation:
- Obstfeld (1996): Models of currency crises with self-fulfilling features
- Krugman (1979): A model of balance-of-payments crises
- Morris & Shin (1998): Unique equilibrium in a model of self-fulfilling currency attacks

Agents:
- Market: Price formation via net-demand + mean-reversion
- SpeculativeAttacker: Builds short positions in vulnerable currency (destabilizing)
- SelfFulfillingTrader: Sells based on expectation others will sell (destabilizing)
- CentralBankDefender: Defends currency peg using reserves (stabilizing)
- FundamentalHedger: Hedges based on fundamentals, not speculation (stabilizing)
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
    """Currency market — clears orders and broadcasts price each round."""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
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

        self.state.custom_state["round"] = observation.round
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

        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0
        self.state.custom_state["deviation"] = deviation
        logger.debug(
            "Round %d: price=%.4f deviation=%.4f",
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


class SpeculativeAttacker(GeneralPlayer):
    """Builds short positions in vulnerable currency, profiting from forced devaluation.

    Theory: simulation-bases.md §4.1 — SpeculativeAttacker
    Theoretical basis: Krugman (1979) first-generation crisis model; speculators attack
    when reserves appear insufficient; attack size scales with deviation severity.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CurrencyCrisis/SpeculativeAttacker", entry_limit=200
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
        attack_threshold = float(extras["attack_threshold"])
        order_size = int(extras["order_size"])

        action, quantity = "hold", 0
        if deviation < -attack_threshold:
            # Currency weak — attack by selling
            qty = min(order_size, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        elif deviation > attack_threshold:
            # Currency recovered — cover short (buy)
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


class SelfFulfillingTrader(GeneralPlayer):
    """Sells currency based on expectation that others will sell — making crisis inevitable.

    Theory: simulation-bases.md §4.2 — SelfFulfillingTrader
    Theoretical basis: Obstfeld (1996) second-generation model; crises arise from
    self-fulfilling expectations when momentum signals coordination among sellers.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CurrencyCrisis/SelfFulfillingTrader", entry_limit=200
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
        contagion_threshold = float(extras["contagion_sensitivity"])
        order_size = int(extras["order_size"])

        action, quantity = "hold", 0
        # Self-fulfilling: any negative deviation triggers selling
        if deviation < -contagion_threshold:
            qty = min(order_size, max(position, 0))
            if qty > 0:
                action, quantity = "sell", qty
        elif deviation > contagion_threshold * 2:
            qty = min(order_size // 2, int(cash / price) if price > 0 else 0)
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


class CentralBankDefender(GeneralPlayer):
    """Defends currency peg using foreign reserves and interest rate adjustments.

    Theory: simulation-bases.md §4.3 — CentralBankDefender
    Theoretical basis: Central bank defense mechanisms (Obstfeld, 1996); intervenes
    by buying domestic currency; limited by reserve capacity.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CurrencyCrisis/CentralBankDefender", entry_limit=200
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
        defense_threshold = float(extras["defense_threshold"])
        order_size = int(extras["order_size"])

        action, quantity = "hold", 0
        if deviation < -defense_threshold:
            # Currency under attack — buy to defend
            qty = min(order_size, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation > defense_threshold:
            # Currency overvalued — sell reserves
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


class FundamentalHedger(GeneralPlayer):
    """Hedges based on fundamental analysis rather than speculative expectations.

    Theory: simulation-bases.md §4.4 — FundamentalHedger
    Theoretical basis: Morris & Shin (1998) global games; fundamental analysis anchors
    against self-fulfilling crises when underlying value is sound.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CurrencyCrisis/FundamentalHedger", entry_limit=200
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
        hedge_threshold = float(extras["hedge_ratio"])
        order_size = int(extras["order_size"])

        action, quantity = "hold", 0
        if deviation < -hedge_threshold:
            qty = min(order_size, int(cash / price) if price > 0 else 0)
            if qty > 0:
                action, quantity = "buy", qty
        elif deviation > hedge_threshold:
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


class NoiseTrader(GeneralPlayer):
    """Random uninformed trader providing baseline liquidity.

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: Black (1986) noise trader model; random orders provide
    FX market thickness and baseline variance independent of crisis dynamics.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="CurrencyCrisis/NoiseTrader", entry_limit=200
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
    "SpeculativeAttacker",
    "SelfFulfillingTrader",
    "CentralBankDefender",
    "FundamentalHedger",
    "NoiseTrader",
]
