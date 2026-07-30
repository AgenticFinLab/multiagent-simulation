"""Volmageddon Rule-Based Simulation

February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours trading

Theoretical Foundation:
- Volatility product feedback (Bergsma & Jiang, 2022)
- Short volatility crowding (Culp et al., 2018)
- Inverse VIX ETN dynamics

Key Dynamics:
- ShortVolTrader: Sells VIX futures/ETNs, profits from contango but faces tail risk
- VolETNManager: Must buy VIX futures when VIX rises, creating positive feedback
- LongVolHedger: Holds long VIX positions as portfolio hedge
- VolArbitrageur: Trades VIX term structure dislocations
- EquityTrader: Trades equities, affected by volatility spike

Parameters from config (see configs/Volmageddon/Rule/players.yml):
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("Volmageddon")


class Market(GeneralPlayer):
    """Market agent for Volmageddon simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

    Where:
        - lambda: Price impact coefficient
        - gamma: Mean reversion strength
        - F: Fundamental value
        - epsilon: Random noise
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            self._initialize_market_state()

        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()

    def _initialize_market_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []
        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]

    def _extract_orders(self, observation: Observation) -> List[Dict[str, Any]]:
        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                msg = inb.payload if hasattr(inb, "payload") else inb
                content_type = getattr(inb, "content_type", None)
                if (
                    isinstance(msg, dict)
                    and (msg.get("type") == "order" or content_type == "investor_order")
                    and "action" in msg
                    and "quantity" in msg
                ):
                    orders.append(
                        {
                            "agent_id": msg.get("from", getattr(inb, "sender_id", None)),
                            "action": msg["action"],
                            "quantity": msg["quantity"],
                            "agent_type": msg.get("agent_type", "unknown"),
                        }
                    )
        return orders

    def _clear_market(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
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

        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)

        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        return {
            "price": new_price,
            "volume": volume,
            "net_demand": net_demand,
        }

    def _update_state(self, market_result: Dict[str, Any]) -> None:
        self.state.custom_state["prev_price"] = self.state.custom_state["price"]
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])

    def _log_market_state(self) -> None:
        logger.debug(
            "Round %d: price=%.2f",
            self.state.custom_state["round"],
            self.state.custom_state["price"],
        )

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        prev_price = self.state.custom_state.get("prev_price", self.state.custom_state["price"])
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0

        market_update = {
            "type": "market_update",
            "price": price,
            "prev_price": prev_price,
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

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class BaseInvestor(GeneralPlayer):
    """Base investor for Volmageddon simulation."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        return {"action": "hold", "quantity": 0}

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload if hasattr(inb, "payload") else inb
                if isinstance(market_data, dict) and "price" in market_data:
                    self.state.custom_state["price"] = market_data["price"]
                    self.state.custom_state["fundamental"] = market_data["fundamental"]
                    self.state.custom_state["deviation"] = market_data["deviation"]

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)
        action = decision["action"]
        quantity = decision["quantity"]

        if action == "buy" and quantity > 0:
            cost = quantity * price
            if cost <= self.state.custom_state["cash"]:
                self.state.custom_state["cash"] -= cost
                self.state.custom_state["position"] += quantity
            else:
                action = "hold"
                quantity = 0
        elif action == "sell" and quantity > 0:
            position = self.state.custom_state["position"]
            quantity = min(quantity, position)
            if quantity > 0:
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity
            else:
                action = "hold"
                quantity = 0

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class ShortVolTrader(BaseInvestor):
    """Short volatility trader.

    Theory: simulation-bases.md §4.1
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        stop_loss = extras["stop_loss"]

        if deviation > stop_loss:
            buy_qty = min(abs(position), int(abs(position) * 0.8))
            if buy_qty > 0 and position < 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation < -0.02:
            sell_qty = min(1000, int(cash / price) if price > 0 else 0)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class VolETNManager(BaseInvestor):
    """Inverse VIX ETN manager.

    Theory: simulation-bases.md §4.2
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        rebalance_threshold = extras["rebalance_threshold"]
        rebalance_size = extras["rebalance_size"]

        if deviation > rebalance_threshold:
            buy_qty = min(
                int(deviation * rebalance_size),
                int(cash / price) if price > 0 else 0,
            )
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}


class LongVolHedger(BaseInvestor):
    """Long volatility hedger.

    Theory: simulation-bases.md §4.3
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        hedge_ratio = extras["hedge_ratio"]

        if deviation < -0.05:
            buy_qty = min(500, int(cash * hedge_ratio / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation > 0.1:
            sell_qty = min(500, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class VolArbitrageur(BaseInvestor):
    """Volatility arbitrageur.

    Theory: simulation-bases.md §4.4
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras["entry_threshold"]

        if abs(deviation) > entry_threshold:
            qty = min(5000, int(abs(deviation) * 20000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}


class EquityTrader(BaseInvestor):
    """Equity trader.

    Theory: simulation-bases.md §4.5
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_limit = extras["risk_limit"]

        if abs(deviation) > risk_limit * 2:
            qty = min(1000, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "BaseInvestor",
    "ShortVolTrader",
    "VolETNManager",
    "LongVolHedger",
    "VolArbitrageur",
    "EquityTrader",
]
