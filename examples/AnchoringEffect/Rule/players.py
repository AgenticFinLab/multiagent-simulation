"""AnchoringEffect Rule-Based Simulation

Anchoring causes traders to insufficiently adjust from reference prices,
creating slow price discovery and persistent mispricings.

Theoretical Foundation:
    - Tversky & Kahneman (1974): Judgment under Uncertainty: Heuristics and Biases
    - Northcraft & Neale (1987): Experts, amateurs, and real estate
    - Campbell & Sharpe (2009): Anchoring bias in consensus forecasts

Key Dynamics:
    - AnchoredTrader: Anchors to initial price, adjusts insufficiently toward fundamental
    - HistoricalAnchor: Anchors to historical average price
    - RationalUpdater: Updates beliefs correctly without anchoring bias (benchmark)
    - MomentumTrader: Follows price trends
    - NoiseTrader: Random uninformed trader

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("AnchoringEffect")


class Market(GeneralPlayer):
    """
    Central market for AnchoringEffect simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

    Where:
        lambda: price_impact coefficient (low → anchoring slows price discovery)
        gamma:  mean_reversion strength
        F:      fundamental value
        epsilon: random noise
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
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, "market", "price"),
                entry_limit=hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                orders.append(inb.payload)

        current_price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        buy_qty = sum(o["quantity"] for o in orders if o.get("action") == "buy")
        sell_qty = sum(o["quantity"] for o in orders if o.get("action") == "sell")
        net_demand = buy_qty - sell_qty

        noise = random.gauss(0, noise_std)
        new_price = (
            current_price
            + price_impact * net_demand
            + mean_reversion * (fundamental - current_price)
            + noise
        )
        new_price = max(new_price, 0.01)

        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0
        prev_price = current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["prev_price"] = prev_price
        self.state.custom_state["deviation"] = deviation
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "Round %d: price=%.2f fundamental=%.2f deviation=%+.2f%%",
            round_num,
            new_price,
            fundamental,
            deviation * 100,
        )

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        prev_price = self.state.custom_state["prev_price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        round_num = self.state.custom_state["round"]

        market_data = {
            "price": price,
            "prev_price": prev_price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": round_num,
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_price"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class AnchoredTrader(GeneralPlayer):
    """
    Anchors to initial price, adjusts insufficiently toward fundamental.

    Theory: Tversky & Kahneman (1974) — Anchoring and Insufficient Adjustment.
    Perceived target = anchor + (fundamental - anchor) * adjustment_factor
    Trades when price deviates from perceived target by > 3%.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["anchor_weight"] = extras["anchor_weight"]
            self.state.custom_state["adjustment_factor"] = extras["adjustment_factor"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            self.state.custom_state["anchor_price"] = None
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                if self.state.custom_state["anchor_price"] is None:
                    self.state.custom_state["anchor_price"] = market_data["price"]

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        anchor_price = self.state.custom_state["anchor_price"]
        adjustment_factor = self.state.custom_state["adjustment_factor"]
        base_size = self.state.custom_state["base_position_size"]

        price = market_data["price"]
        fundamental = market_data["fundamental"]

        adjusted_target = (
            anchor_price + (fundamental - anchor_price) * adjustment_factor
        )
        perceived_dev = (
            (price - adjusted_target) / adjusted_target if adjusted_target > 0 else 0.0
        )

        action = "hold"
        quantity = 0.0

        if abs(perceived_dev) > 0.03:
            quantity = min(base_size, abs(perceived_dev) * 1000)
            if perceived_dev < 0:
                affordable = cash / price if price > 0 else 0
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "AnchoredTrader",
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
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
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class HistoricalAnchor(GeneralPlayer):
    """
    Anchors to historical average price, adjusts insufficiently.

    Theory: Northcraft & Neale (1987) — Experts anchor to past prices.
    Perceived deviation = (price - hist_avg) / hist_avg * (1 - anchor_weight)
    Trades when perceived deviation exceeds 3%.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["anchor_weight"] = extras["anchor_weight"]
            self.state.custom_state["lookback"] = extras["lookback"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            self.state.custom_state["historical_prices"] = []
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                lookback = self.state.custom_state["lookback"]
                hist = self.state.custom_state["historical_prices"]
                hist.append(market_data["price"])
                if len(hist) > lookback:
                    self.state.custom_state["historical_prices"] = hist[-lookback:]

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        anchor_weight = self.state.custom_state["anchor_weight"]
        base_size = self.state.custom_state["base_position_size"]
        historical_prices = self.state.custom_state["historical_prices"]

        price = market_data["price"]

        if historical_prices:
            hist_avg = sum(historical_prices) / len(historical_prices)
        else:
            hist_avg = price

        perceived_dev = (
            (price - hist_avg) / hist_avg * (1 - anchor_weight) if hist_avg > 0 else 0.0
        )

        action = "hold"
        quantity = 0.0

        if abs(perceived_dev) > 0.03:
            quantity = min(base_size, abs(perceived_dev) * 1000)
            if perceived_dev < 0:
                affordable = cash / price if price > 0 else 0
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "HistoricalAnchor",
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
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
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class RationalUpdater(GeneralPlayer):
    """
    Bayesian updater — trades without anchoring bias (benchmark).

    Trades directly on true fundamental deviation.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        base_size = self.state.custom_state["base_position_size"]

        price = market_data["price"]
        deviation = market_data["deviation"]

        action = "hold"
        quantity = 0.0

        if abs(deviation) > 0.02:
            quantity = min(base_size, abs(deviation) * 1000)
            if deviation < 0:
                affordable = cash / price if price > 0 else 0
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "RationalUpdater",
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
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
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class MomentumTrader(GeneralPlayer):
    """
    Follows price trends — buys when price rises, sells when it falls.

    Theory: Jegadeesh & Titman (1993) — Momentum effect.
    Trades when deviation exceeds entry_threshold.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["entry_threshold"] = extras["entry_threshold"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = self.state.custom_state["entry_threshold"]
        base_size = self.state.custom_state["base_position_size"]

        price = market_data["price"]
        prev_price = market_data["prev_price"]

        return_pct = (price - prev_price) / prev_price if prev_price > 0 else 0.0

        action = "hold"
        quantity = 0.0

        if abs(return_pct) > entry_threshold:
            quantity = min(base_size, abs(return_pct) * 1000)
            if return_pct > 0:
                affordable = cash / price if price > 0 else 0
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "MomentumTrader",
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
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
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """
    Random uninformed trader providing background liquidity.

    Theory: Black (1986) — Noise traders.
    Trades randomly with probability trade_probability each round.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["trade_probability"] = extras["trade_probability"]
            self.state.custom_state["min_order"] = extras["min_order"]
            self.state.custom_state["max_order"] = extras["max_order"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        trade_prob = self.state.custom_state["trade_probability"]
        min_order = self.state.custom_state["min_order"]
        max_order = self.state.custom_state["max_order"]

        price = market_data["price"]

        action = "hold"
        quantity = 0.0

        if random.random() < trade_prob:
            quantity = random.uniform(min_order, max_order)
            if random.random() > 0.5:
                affordable = cash / price if price > 0 else 0
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    action = "hold"
                    quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "NoiseTrader",
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
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
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "AnchoredTrader",
    "HistoricalAnchor",
    "RationalUpdater",
    "MomentumTrader",
    "NoiseTrader",
]
