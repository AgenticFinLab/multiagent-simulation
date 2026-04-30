"""OverconfidenceBias Rule-Based Simulation Players.

Phenomenon: Overconfidence Bias
    - Traders overestimate their signal precision and trade too frequently
    - Self-attribution: success attributed to skill, failure to bad luck
    - Results in excess trading volume and increased volatility

Theoretical Foundation:
    - Daniel, Hirshleifer & Subrahmanyam (1998): Investor psychology
    - Odean (1998): Volume, volatility when all traders are above average
    - Barber & Odean (2001): Boys will be boys

Agent Types:
    - OverconfidentTrader: Overestimates signal precision, trades too frequently
    - SelfAttributor: Attributes success to skill, failure to bad luck
    - CalibratedTrader: Correctly estimates signal precision, trades appropriately
    - ContrarianInvestor: Trades against overconfident moves
    - NoiseTrader: Random uninformed trader
"""

import logging
import os
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("OverconfidenceBias")


# =============================================================================
# Market
# =============================================================================


class Market(GeneralPlayer):
    """Central market for OverconfidenceBias simulation.

    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F - P(t)) + ε
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=custom_state_hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload.get("type") == "order":
                    orders.append(
                        {
                            "agent_id": inb.sender_id,
                            "action": payload.get("action"),
                            "quantity": payload.get("quantity", 0),
                            "agent_type": payload.get("agent_type", ""),
                        }
                    )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]

        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        price_impact = extras["price_impact"]
        mean_reversion = extras["mean_reversion"]
        noise_std = extras["noise_std"]

        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)

        new_price = max(0.01, price + price_change + reversion + noise)
        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(volume)

        logger.debug(
            "[Market] R%d  P=%.2f  F=%.2f  Dev=%+.2f%%  ND=%+.0f",
            round_num,
            new_price,
            fundamental,
            deviation * 100,
            net_demand,
        )

        market_update = {
            "type": "market_update",
            "price": new_price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": round_num,
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


# =============================================================================
# BaseInvestor
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """Base investor for OverconfidenceBias simulation."""

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

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        return {"action": "hold", "quantity": 0}

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state.get("price", 0.0)
        fundamental = self.state.custom_state.get("fundamental", 0.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        agent_type = self.__class__.__name__

        decision = self._make_decision(price, fundamental, deviation)

        order = {
            "type": "order",
            "action": decision["action"],
            "quantity": decision["quantity"],
            "agent_type": agent_type,
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Concrete Investor Types
# =============================================================================


class OverconfidentTrader(BaseInvestor):
    """Overestimates signal precision, trades too frequently."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        precision_over = extras["precision_overestimate"]

        signal = deviation * precision_over
        if abs(signal) > 0.01:
            qty = min(800, int(abs(signal) * 5000))
            if signal > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    self.state.custom_state["cash"] -= buy_qty * price
                    self.state.custom_state["position"] += buy_qty
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, position)
                if sell_qty > 0:
                    self.state.custom_state["cash"] += sell_qty * price
                    self.state.custom_state["position"] -= sell_qty
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class SelfAttributor(BaseInvestor):
    """Attributes success to skill, failure to bad luck."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        confidence_boost = extras["confidence_boost"]

        if position > 0 and deviation > 0:
            boosted_qty = min(1000, int(800 * (1 + confidence_boost)))
            buy_qty = min(boosted_qty, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                self.state.custom_state["cash"] -= buy_qty * price
                self.state.custom_state["position"] += buy_qty
                return {"action": "buy", "quantity": buy_qty}
        elif deviation < -0.02:
            sell_qty = min(600, position)
            if sell_qty > 0:
                self.state.custom_state["cash"] += sell_qty * price
                self.state.custom_state["position"] -= sell_qty
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class CalibratedTrader(BaseInvestor):
    """Correctly estimates signal precision, trades appropriately."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        signal_precision = extras["signal_precision"]
        trade_threshold = extras["trade_threshold"]

        if abs(deviation) > trade_threshold:
            qty = min(500, int(abs(deviation) * signal_precision * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    self.state.custom_state["cash"] -= buy_qty * price
                    self.state.custom_state["position"] += buy_qty
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, position)
                if sell_qty > 0:
                    self.state.custom_state["cash"] += sell_qty * price
                    self.state.custom_state["position"] -= sell_qty
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class ContrarianInvestor(BaseInvestor):
    """Trades against overconfident moves."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        contrarian_threshold = extras["contrarian_threshold"]

        if abs(deviation) > contrarian_threshold:
            qty = min(400, int(abs(deviation) * 2000))
            if deviation > 0:
                sell_qty = min(qty, position)
                if sell_qty > 0:
                    self.state.custom_state["cash"] += sell_qty * price
                    self.state.custom_state["position"] -= sell_qty
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    self.state.custom_state["cash"] -= buy_qty * price
                    self.state.custom_state["position"] += buy_qty
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}


class NoiseTrader(BaseInvestor):
    """Random uninformed trader."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras["trade_probability"]

        if random.random() < prob:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, position)
            if qty > 0:
                if action == "buy":
                    self.state.custom_state["cash"] -= qty * price
                    self.state.custom_state["position"] += qty
                else:
                    self.state.custom_state["cash"] += qty * price
                    self.state.custom_state["position"] -= qty
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "BaseInvestor",
    "OverconfidentTrader",
    "SelfAttributor",
    "CalibratedTrader",
    "ContrarianInvestor",
    "NoiseTrader",
]
