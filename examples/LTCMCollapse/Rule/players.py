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
import random

from masim.player.base import Action
from masim.player.general import GeneralPlayer

logger = logging.getLogger("LTCMCollapse")


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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_history"] = []
            self.state.custom_state["volume_history"] = []
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
        orders = []
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "order":
                orders.append(
                    {
                        "action": payload["action"],
                        "quantity": payload["quantity"],
                    }
                )
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
        volume = min(buy_vol, sell_vol) + abs(net_demand) * 0.5
        self.state.custom_state["volume_history"].append(volume)
        logger.debug(
            "Round %d: price=%.2f", self.state.custom_state["round"], new_price
        )

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0
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
    """
    Bets on spread convergence between related securities using high leverage.

    Theoretical Basis: Limits to arbitrage (Shleifer & Vishny, 1997)
    Market Role: destabilizing — amplifies swings when leveraged bets unwind
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
            if deviation < 0:
                buy_qty = (
                    min(int(leveraged_cash * abs(deviation) / price), max_position)
                    if price > 0
                    else 0
                )
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = (
                    min(int(leveraged_cash * abs(deviation) / price), max(position, 0))
                    if price > 0
                    else 0
                )
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LeverageTrader(GeneralPlayer):
    """
    Highly leveraged trader forced to deleverage when losses mount.

    Theoretical Basis: Leverage cycle (Geanakoplos, 2010)
    Market Role: destabilizing — fire-sale selling amplifies downturns
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
                return {"action": "sell", "quantity": min(delever_qty, position)}
            if position < 0:
                return {"action": "buy", "quantity": delever_qty}
        elif deviation < -0.03 and price > 0:
            buy_qty = min(int(cash * leverage_ratio * 0.01 / price), 5000)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class RiskManager(GeneralPlayer):
    """
    Monitors portfolio risk and cuts positions when VaR thresholds are breached.

    Theoretical Basis: VaR-based risk management
    Market Role: stabilizing short-term, but can amplify crises through simultaneous cuts
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
                return {"action": "sell", "quantity": min(cut_qty, position)}
            if position < 0:
                return {"action": "buy", "quantity": cut_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class LiquidityProvider(GeneralPlayer):
    """
    Provides market liquidity under normal conditions but withdraws under stress.

    Theoretical Basis: Liquidity black holes (Morris & Shin, 2004)
    Market Role: stabilizing when normal, but amplifies crises when withdrawing
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
            return {"action": "hold", "quantity": 0}
        if abs(position) < inventory_limit:
            qty = min(500, inventory_limit - abs(position))
            if deviation > 0:
                return {"action": "sell", "quantity": qty}
            return {
                "action": "buy",
                "quantity": min(qty, int(cash / price) if price > 0 else 0),
            }
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "action": action, "quantity": quantity}
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class CentralBank(GeneralPlayer):
    """
    Lender of last resort providing emergency liquidity during crisis.

    Theoretical Basis: Bagehot (1873): lend freely at a penalty rate against good collateral
    Market Role: stabilizing — arrests panic and prevents systemic collapse
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
            return {"action": "buy", "quantity": 2000}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0 and price > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        order = {"type": "order", "action": action, "quantity": quantity}
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
