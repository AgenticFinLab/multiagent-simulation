"""TulipMania Rule-Based Simulation

1637 Dutch tulip bubble where speculative frenzy drove tulip prices to
extraordinary levels before catastrophic collapse, driven by greater-fool
dynamics and social proof herding.

Theoretical Foundation:
- Garber (2000): Famous first bubbles
- Mackay (1841): Extraordinary popular delusions and the madness of crowds
- Thompson (2007): The tulip mania — fact or artifact?

Key Dynamics:
- TrendChaser: Buys assets purely because prices are rising, regardless of intrinsic value
- SocialProofFollower: Follows crowd into speculative positions because everyone else is doing it
- IntrinsicValueTrader: Values assets by intrinsic utility, sells when price far exceeds use value
- EarlyExitTrader: Recognizes speculative excess early and exits before the crash
- NoiseTrader: Random uninformed trader providing baseline liquidity

Parameters from config extras (see configs/TulipMania/Rule/players.yml).
"""

import logging
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("TulipMania")


class Market(GeneralPlayer):
    """Market agent for TulipMania simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
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

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict) and "action" in payload:
                    orders.append(payload)

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
        logger.debug(
            "Round %d: price=%.2f fundamental=%.2f",
            round_num,
            new_price,
            fundamental,
        )

    async def decide(self) -> Dict[str, Any]:
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

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class BaseInvestor(GeneralPlayer):
    """Base class for TulipMania investors."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        return {"action": "hold", "quantity": 0}

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                if isinstance(market_data, dict):
                    self.state.custom_state["price"] = market_data["price"]
                    self.state.custom_state["fundamental"] = market_data["fundamental"]
                    self.state.custom_state["deviation"] = market_data["deviation"]

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        order = self._make_decision(price, fundamental, deviation)

        action = order["action"]
        quantity = order["quantity"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return {
            **order,
            "agent_type": self.__class__.__name__,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class TrendChaser(BaseInvestor):
    """Buys assets purely because prices are rising, regardless of intrinsic value.

    Theoretical Basis: Greater fool theory (Mackay, 1841)
    Market Role: destabilizing
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, int(position))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class SocialProofFollower(BaseInvestor):
    """Follows crowd into speculative positions because everyone else is doing it.

    Theoretical Basis: Social proof and crowd psychology (Mackay, 1841)
    Market Role: destabilizing
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, int(position))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class IntrinsicValueTrader(BaseInvestor):
    """Values assets by intrinsic utility, sells when price far exceeds use value.

    Theoretical Basis: Fundamental value discipline (Garber, 2000)
    Market Role: stabilizing
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, int(position))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class EarlyExitTrader(BaseInvestor):
    """Recognizes speculative excess early and exits before the crash.

    Theoretical Basis: Rational bubble riding (Thompson, 2007)
    Market Role: stabilizing
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, int(position))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class NoiseTrader(BaseInvestor):
    """Random uninformed trader providing baseline liquidity.

    Theoretical Basis: Noise trader model (Black, 1986)
    Market Role: neutral
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if random.random() < 0.3:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, int(position))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "BaseInvestor",
    "TrendChaser",
    "SocialProofFollower",
    "IntrinsicValueTrader",
    "EarlyExitTrader",
    "NoiseTrader",
]
