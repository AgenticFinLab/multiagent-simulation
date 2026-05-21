"""LTCMCollapse Rule-Based Simulation

August-September 1998 LTCM crisis — Russian default triggered a catastrophic
liquidity crisis as highly leveraged convergence trades unwound.

Theoretical Foundation:
- Shleifer & Vishny (1997): Limits to arbitrage
- Geanakoplos (2010): Leverage cycle
- Morris & Shin (2004): Liquidity black holes
- Bagehot (1873): Lender of last resort

Key Dynamics:
- ConvergenceArbitrageur: Bets on spread convergence using high leverage
- LeverageTrader: Forced to deleverage rapidly when losses mount
- RiskManager: Cuts positions when VaR thresholds are breached
- LiquidityProvider: Provides market liquidity but withdraws under stress
- CentralBank: Intervenes as lender of last resort during crisis
"""

import logging
import os
import random

from masim.player.base import Action
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("LTCMCollapse")


def _require_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


def _build_order(player: GeneralPlayer, action: str, quantity: int, price: float, reasoning: str) -> dict:
    """Build the canonical trading order shared by all variants."""
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"{player.identity} emitted invalid action: {action}")
    _require_positive(price, "bid_price")
    return {
        "type": "order",
        "from": player.identity,
        "action": action,
        "bid_price": price,
        "quantity": max(0, int(quantity)),
        "reasoning": reasoning,
        "agent_type": player.__class__.__name__,
        "strategy": player.__class__.__name__,
    }


def _decision(action: str, quantity: int, reasoning: str) -> dict:
    """Return a small deterministic decision dict."""
    return {"action": action, "quantity": quantity, "reasoning": reasoning}


def _apply_trade(state: dict, action: str, quantity: int, price: float) -> int:
    """Apply cash/position constraints and update state."""
    _require_positive(price, "price")
    quantity = max(0, int(quantity))
    if action == "buy" and quantity > 0:
        quantity = min(quantity, int(state["cash"] / price))
        if quantity > 0:
            state["cash"] -= quantity * price
            state["position"] += quantity
    elif action == "sell" and quantity > 0:
        quantity = min(quantity, max(int(state["position"]), 0))
        if quantity > 0:
            state["cash"] += quantity * price
            state["position"] -= quantity
    else:
        quantity = 0
    return quantity


class Market(GeneralPlayer):
    """
    Market agent for LTCMCollapse simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            _require_positive(self.state.custom_state["price"], "initial_price")
            _require_positive(self.state.custom_state["fundamental"], "fundamental_value")
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "fundamental"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
        orders = []
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and "type" not in payload and "order" in payload:
                payload = payload["order"]
            if isinstance(payload, dict) and payload["type"] == "order":
                orders.append(
                    {
                        "from": payload["from"],
                        "action": payload["action"],
                        "quantity": payload["quantity"],
                        "bid_price": payload["bid_price"],
                        "reasoning": payload["reasoning"],
                        "agent_type": payload["agent_type"],
                    }
                )
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        _require_positive(price, "price")
        _require_positive(fundamental, "fundamental")
        buy_vol = sum(o["quantity"] for o in orders if o["action"] == "buy")
        sell_vol = sum(o["quantity"] for o in orders if o["action"] == "sell")
        net_demand = buy_vol - sell_vol
        price_change = self.state.custom_state["price_impact"] * net_demand
        reversion = self.state.custom_state["mean_reversion"] * (fundamental - price)
        noise = random.gauss(0, self.state.custom_state["noise_std"])
        new_price = max(price + price_change + reversion + noise, 0.01)
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        volume = min(buy_vol, sell_vol) + abs(net_demand) * 0.5
        self.state.custom_state["fundamental_history"].append(fundamental)
        self.state.custom_state["volume_history"].append(volume)
        logger.debug(
            "Round %d: price=%.2f", self.state.custom_state["round"], new_price
        )

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        _require_positive(fundamental, "fundamental")
        deviation = (price - fundamental) / fundamental
        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        return {
            **market_update,
            "outbound_messages": [
                {"payload": market_update, "content_type": "market_update"}
            ],
        }

    async def act(self, decision_payload: dict) -> Action:
        price = decision_payload["price"]
        fundamental = decision_payload["fundamental"]
        deviation = decision_payload["deviation"]
        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
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


class ConvergenceArbitrageur(GeneralPlayer):
    """Bets on spread convergence between related securities using high leverage.

    Theory: simulation-bases.md §4.1 — ConvergenceArbitrageur
    Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_spread = extras["entry_spread"]
        leverage = extras["leverage"]
        max_position = extras["max_position"]
        if abs(deviation) > entry_spread:
            leveraged_cash = cash * leverage
            _require_positive(price, "price")
            if deviation < 0:
                buy_qty = min(int(leveraged_cash * abs(deviation) / price), max_position)
                if buy_qty > 0:
                    return _decision("buy", buy_qty, f"spread discount deviation={deviation:+.2%}")
            sell_qty = min(int(leveraged_cash * abs(deviation) / price), max(position, 0))
            if sell_qty > 0:
                return _decision("sell", sell_qty, f"spread premium deviation={deviation:+.2%}")
        return _decision("hold", 0, "spread below entry threshold")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LeverageTrader(GeneralPlayer):
    """Highly leveraged trader forced to deleverage when losses mount.

    Theory: simulation-bases.md §4.2 — LeverageTrader
    Theoretical basis: Geanakoplos (2010) leverage cycle.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        leverage_ratio = extras["leverage_ratio"]
        margin_call = extras["margin_call_threshold"]
        portfolio_value = cash + position * price
        equity = portfolio_value - abs(position * price) / leverage_ratio
        if equity < abs(position * price) * margin_call:
            delever_qty = int(abs(position) * 0.3)
            if position > 0:
                return _decision("sell", min(delever_qty, position), "margin call deleveraging")
            if position < 0:
                return _decision("buy", delever_qty, "margin call short-covering")
        elif deviation < -0.03:
            _require_positive(price, "price")
            buy_qty = min(int(cash * leverage_ratio * 0.01 / price), 5000)
            if buy_qty > 0:
                return _decision("buy", buy_qty, "leveraged undervaluation entry")
        return _decision("hold", 0, "no margin call or value trigger")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RiskManager(GeneralPlayer):
    """Monitors portfolio risk and cuts positions when VaR thresholds are breached.

    Theory: simulation-bases.md §4.3 — RiskManager
    Theoretical basis: Jorion (2000) VaR and LTCM risk-management lessons.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        position = self.state.custom_state["position"]
        var_limit = extras["var_limit"]
        if abs(deviation) > var_limit * 3:
            cut_qty = int(abs(position) * 0.5)
            if position > 0:
                return _decision("sell", min(cut_qty, position), "VaR breach risk cut")
            if position < 0:
                return _decision("buy", cut_qty, "VaR breach short-cover")
        return _decision("hold", 0, "risk within VaR limit")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LiquidityProvider(GeneralPlayer):
    """Provides market liquidity under normal conditions but withdraws under stress.

    Theory: simulation-bases.md §4.4 — LiquidityProvider
    Theoretical basis: Morris & Shin (2004) liquidity black holes.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        inventory_limit = extras["inventory_limit"]
        price = self.state.custom_state["price"]
        if abs(deviation) > 0.05:
            return _decision("hold", 0, "stress withdrawal")
        if abs(position) < inventory_limit:
            _require_positive(price, "price")
            qty = min(500, inventory_limit - abs(position))
            if deviation > 0:
                return _decision("sell", qty, "normal liquidity supply")
            return _decision("buy", min(qty, int(cash / price)), "normal liquidity demand")
        return _decision("hold", 0, "inventory limit reached")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class CentralBank(GeneralPlayer):
    """Lender of last resort providing emergency liquidity during crisis.

    Theory: simulation-bases.md §4.5 — CentralBank
    Theoretical basis: Bagehot (1873) lender of last resort.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = 0
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        intervention_threshold = extras["intervention_threshold"]
        rescue_prob = extras["rescue_probability"]
        if deviation < -intervention_threshold and random.random() < rescue_prob:
            return _decision("buy", 2000, "lender-of-last-resort intervention")
        return _decision("hold", 0, "intervention threshold not met")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
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
    "ConvergenceArbitrageur",
    "LeverageTrader",
    "RiskManager",
    "LiquidityProvider",
    "CentralBank",
]
