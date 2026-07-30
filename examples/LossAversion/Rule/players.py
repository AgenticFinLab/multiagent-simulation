"""LossAversion Rule-Based Simulation

Loss aversion from prospect theory causes investors to hold losers too long
and sell winners too early.

Theoretical Foundation:
- Kahneman & Tversky (1979): Prospect Theory
- Tversky & Kahneman (1992): Cumulative Prospect Theory
- Odean (1998): Are investors reluctant to realize their losses?

Key Dynamics:
- LossAverseInvestor: Values losses 2-2.5x more than gains, holds losers, sells winners
- BreakEvenTrader: Takes excessive risk to get back to break-even
- RationalTrader: Makes decisions based on expected utility without bias
- MomentumTrader: Follows price trends
- MarketMaker: Provides liquidity and earns spread

All parameters are configured via players.yml config file.
"""

import logging
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("LossAversion")


class Market(GeneralPlayer):
    """Market agent for LossAversion simulation.

    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F - P(t)) + ε

    Where:
        - λ: Price impact coefficient
        - γ: Mean reversion strength
        - F: Fundamental value
        - ε: Random noise
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        self.state.custom_state["round"] = observation.round

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = __import__("os").path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=__import__("os").path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict) and payload.get("type") == "order":
                    orders.append(
                        {
                            "agent_id": inb.sender_id,
                            "action": payload["action"],
                            "quantity": payload["quantity"],
                            "agent_type": payload["agent_type"],
                        }
                    )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]
        round_num = self.state.custom_state["round"]

        price_impact = extras["price_impact"]
        mean_reversion = extras["mean_reversion"]
        noise_std = extras["noise_std"]

        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell

        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        rng = random.Random(int(extras["random_seed"]) + int(round_num))
        noise = rng.gauss(0, noise_std)
        shock_schedule = extras["shock_schedule"]
        shock_return = (
            float(shock_schedule[round_num]) if round_num in shock_schedule else 0.0
        )

        new_price = max(
            price + price_change + reversion + noise + fundamental * shock_return,
            extras["price_floor"],
        )
        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "[Market] Round %d: price=%.2f, fundamental=%.2f, deviation=%+.2f%%",
            round_num,
            new_price,
            fundamental,
            deviation * 100,
        )

        market_update = {
            "type": "market_update",
            "price": new_price,
            "prev_price": price,
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


class BaseInvestor(GeneralPlayer):
    """Base class for all LossAversion investors."""

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        self.state.custom_state["round"] = observation.round

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["entry_price"] = extras["initial_price"]

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload if hasattr(inb, "payload") else inb
                if isinstance(payload, dict) and payload["type"] == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        """Override in subclasses to implement agent-specific trading logic."""
        return {"action": "hold", "quantity": 0}

    def _execute_trade(self, action: str, quantity: int) -> None:
        price = self.state.custom_state["price"]
        if action == "buy" and quantity > 0:
            old_position = self.state.custom_state["position"]
            old_entry = self.state.custom_state["entry_price"]
            new_position = old_position + quantity
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] = new_position
            self.state.custom_state["entry_price"] = (
                old_entry * old_position + price * quantity
            ) / new_position
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)
        action = decision["action"]
        quantity = max(0, int(decision["quantity"]))

        if action == "buy":
            quantity = min(quantity, int(self.state.custom_state["cash"] / price))
        elif action == "sell":
            quantity = min(quantity, max(self.state.custom_state["position"], 0))
        else:
            action = "hold"
            quantity = 0

        self._execute_trade(action, quantity)

        order = {
            "type": "order",
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": f"{self.__class__.__name__} configured rule",
            "cash": self.state.custom_state["cash"],
            "position": self.state.custom_state["position"],
            "entry_price": self.state.custom_state["entry_price"],
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


class LossAverseInvestor(BaseInvestor):
    """Loss averse: values losses 2.25x more than gains (prospect theory).

    Sells winners too early and holds losers too long.

    Theory: simulation-bases.md §4.1
    Foundation: Kahneman & Tversky (1979) doi:10.2307/1914185;
                Odean (1998) doi:10.1111/0022-1082.00072
    Activation: pnl_pct > sell_gain_threshold (gain) or
                pnl_pct < −sell_gain × loss_aversion_lambda (loss)
    Formula (gain): sell_qty = min(position, int(position × 0.7))
    Formula (loss): sell_qty = min(position, int(position × 0.2))
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        position = self.state.custom_state["position"]
        loss_lambda = extras["loss_aversion_lambda"]
        sell_gain = extras["sell_gain_threshold"]
        gain_fraction = extras["gain_sell_fraction"]
        loss_fraction = extras["loss_sell_fraction"]
        base_size = extras["base_size"]

        entry_price = self.state.custom_state["entry_price"]
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0.0

        if "last_realization_domain" not in self.state.custom_state:
            self.state.custom_state["last_realization_domain"] = None

        active_domain = None
        if pnl_pct > sell_gain:
            active_domain = "gain"
        elif pnl_pct < -sell_gain * loss_lambda:
            active_domain = "loss"

        if active_domain is None:
            self.state.custom_state["last_realization_domain"] = None
            return {"action": "hold", "quantity": 0}
        if self.state.custom_state["last_realization_domain"] == active_domain:
            return {"action": "hold", "quantity": 0}

        if active_domain == "gain":
            sell_qty = min(max(position, 0), int(position * gain_fraction), base_size)
            if sell_qty > 0:
                self.state.custom_state["last_realization_domain"] = active_domain
                return {"action": "sell", "quantity": sell_qty}
        else:
            sell_qty = min(max(position, 0), int(position * loss_fraction), base_size)
            if sell_qty > 0:
                self.state.custom_state["last_realization_domain"] = active_domain
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class BreakEvenTrader(BaseInvestor):
    """Break-even effect: takes excessive risk to recover losses.

    Theory: simulation-bases.md §4.2
    Foundation: Tversky & Kahneman (1992) doi:10.1007/BF00122574;
                Barberis & Xiong (2009) doi:10.1111/j.1540-6261.2009.01448.x
    Activation: pnl_pct < −0.05
    Formula: risky_qty = min(int(|pnl_pct| × risk_increase_factor × 5000), int(cash/price))
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        risk_increase = extras["risk_increase_factor"]
        loss_trigger = extras["loss_trigger"]
        sizing_scale = extras["sizing_scale"]
        base_size = extras["base_size"]

        entry_price = self.state.custom_state["entry_price"]
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0.0

        if pnl_pct < loss_trigger:
            risky_qty = min(
                int(abs(pnl_pct) * risk_increase * sizing_scale),
                int(cash / price) if price > 0 else 0,
                base_size,
            )
            if risky_qty > 0:
                return {"action": "buy", "quantity": risky_qty}
        return {"action": "hold", "quantity": 0}


class RationalTrader(BaseInvestor):
    """Rational: makes decisions based on expected utility, no bias.

    Theory: simulation-bases.md §4.3
    Foundation: Glosten & Milgrom (1985) doi:10.1016/0304-405X(85)90044-3
    Activation: |deviation| > 0.03
    Formula: qty = min(500, int(|deviation| × risk_aversion × 3000))
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_aversion = extras["risk_aversion"]
        threshold = extras["deviation_threshold"]
        sizing_scale = extras["sizing_scale"]
        base_size = extras["base_size"]

        if abs(deviation) > threshold:
            qty = min(base_size, int(abs(deviation) * risk_aversion * sizing_scale))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class MomentumTrader(BaseInvestor):
    """Momentum: follows price trends.

    Theory: simulation-bases.md §4.4
    Foundation: Jegadeesh & Titman (1993) doi:10.1111/j.1540-6261.1993.tb04702.x
    Activation: |deviation| > entry_threshold (0.03)
    Formula: qty = min(500, int(|deviation| × 3000))
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras["entry_threshold"]
        sizing_scale = extras["sizing_scale"]
        base_size = extras["base_size"]

        if abs(deviation) > entry_threshold:
            qty = min(base_size, int(abs(deviation) * sizing_scale))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class MarketMaker(BaseInvestor):
    """Market maker: provides liquidity and earns spread.

    Theory: simulation-bases.md §4.5
    Foundation: Glosten & Milgrom (1985) doi:10.1016/0304-405X(85)90044-3;
                Ho & Stoll (1981) doi:10.1016/0304-405X(81)90020-9
    Activation: |position| < inventory_limit
    Formula: qty = 300 (fixed); contrarian to deviation direction
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        inventory_limit = extras["inventory_limit"]
        base_size = extras["base_size"]

        if abs(position) < inventory_limit:
            qty = base_size
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(
                    qty,
                    int(cash / price) if price > 0 else 0,
                    max(inventory_limit - position, 0),
                )
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "BaseInvestor",
    "LossAverseInvestor",
    "BreakEvenTrader",
    "RationalTrader",
    "MomentumTrader",
    "MarketMaker",
]
