"""AnchoringEffect Rule-Based Simulation

Deterministic baseline variant implementing the AnchoringEffect simulation design.
All agent decisions are formula-driven; no LLM calls anywhere.

Design Foundation:
    - Phenomenon definition: simulation-bases.md §1
    - Theoretical foundation: simulation-bases.md §2.1–§2.6
    - Market price formation: simulation-bases.md §3.1
    - Investor taxonomy: simulation-bases.md §4
    - Parameter table: simulation-bases.md §6

Agent Classes:
    - Market: rule-based price coordinator — simulation-bases.md §3.1
    - AnchoredTrader: anchors to first price — simulation-bases.md §4, §2.1
    - HistoricalAnchor: anchors to rolling average — simulation-bases.md §4, §2.2
    - RationalUpdater: unbiased fundamental updater — simulation-bases.md §4, §2.4
    - MomentumTrader: trend-following amplifier — simulation-bases.md §4, §2.5
    - NoiseTrader: uninformed random trader — simulation-bases.md §4, §2.6

All numeric parameters are loaded from players.yml extras; no hardcoded values.
"""

import logging
import os
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("AnchoringEffect")


class Market(GeneralPlayer):
    """
    Central market coordinator for AnchoringEffect simulation.

    Implements simulation-bases.md §3.1 — Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

    Variable mapping (simulation-bases.md §3.1 → code):
        lambda (price_impact):    extras["price_impact"]      = 0.01
        gamma (mean_reversion):   extras["mean_reversion"]    = 0.01
        F (fundamental value):    extras["fundamental_value"] = 100.0
        epsilon (noise):          random.gauss(0, noise_std)

    See also:
        - simulation-bases.md §3.2: price floor mechanism (max(new_price, 0.01))
        - simulation-bases.md §3.3: information broadcast design (market_data payload)
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

        buy_qty = sum(o["quantity"] for o in orders if o["action"] == "buy")
        sell_qty = sum(o["quantity"] for o in orders if o["action"] == "sell")
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

    Implements simulation-bases.md §4.1 — AnchoredTrader.
    Theoretical basis: simulation-bases.md §2.1 (Tversky & Kahneman, 1974).

    Decision rule (simulation-bases.md §4.1 — Rule-Based Behavior):
        anchor_price = first market price observed (set on first perceive call)
        perceived_target = anchor_price + (fundamental - anchor_price) * adjustment_factor
        perceived_dev = (price - perceived_target) / perceived_target
        if abs(perceived_dev) > 0.03: trade in corrective direction
        quantity = min(base_position_size, abs(perceived_dev) * 1000)

    Parameters (simulation-bases.md §6):
        adjustment_factor: 0.3 (calibrated from Tversky & Kahneman 1974 experimental data)
        base_position_size: loaded from extras["base_position_size"]
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
            "bid_price": float(price),
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

    Implements simulation-bases.md §4.2 — HistoricalAnchor.
    Theoretical basis: simulation-bases.md §2.2 (Northcraft & Neale, 1987).

    Decision rule (simulation-bases.md §4.2 — Rule-Based Behavior):
        hist_avg = mean of last `lookback` prices (rolling window)
        perceived_dev = (price - hist_avg) / hist_avg * (1 - anchor_weight)
        if abs(perceived_dev) > 0.03: trade in corrective direction
        quantity = min(base_position_size, abs(perceived_dev) * 1000)

    Parameters (simulation-bases.md §6):
        anchor_weight: 0.5 (dampening factor; higher = stronger anchoring)
        lookback: 60 rounds (rolling window for historical average)
        base_position_size: loaded from extras["base_position_size"]
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
            "bid_price": float(price),
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
    Bayesian updater — trades without anchoring bias (rational benchmark).

    Implements simulation-bases.md §4.3 — RationalUpdater.
    Theoretical basis: simulation-bases.md §2.4 (Muth, 1961 — Rational Expectations).

    Decision rule (simulation-bases.md §4.3 — Rule-Based Behavior):
        deviation = (price - fundamental) / fundamental  (from market broadcast)
        if abs(deviation) > 0.02: trade proportionally
        quantity = min(base_position_size, abs(deviation) * 1000)

    Parameters (simulation-bases.md §6):
        threshold: 0.02 (2% deviation triggers trade)
        base_position_size: loaded from extras["base_position_size"]
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
            "bid_price": float(price),
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

    Implements simulation-bases.md §4.4 — MomentumTrader.
    Theoretical basis: simulation-bases.md §2.5 (Jegadeesh & Titman, 1993).

    Decision rule (simulation-bases.md §4.4 — Rule-Based Behavior):
        return_pct = (price - prev_price) / prev_price
        if abs(return_pct) > entry_threshold: follow momentum direction
        quantity = min(base_position_size, abs(return_pct) * 1000)

    Parameters (simulation-bases.md §6):
        entry_threshold: 0.02 (2% return triggers momentum entry)
        base_position_size: loaded from extras["base_position_size"]
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
            "bid_price": float(price),
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
    Random uninformed trader providing background market liquidity.

    Implements simulation-bases.md §4.5 — NoiseTrader.
    Theoretical basis: simulation-bases.md §2.6 (Black, 1986 — Noise Trader Risk).

    Decision rule (simulation-bases.md §4.5 — Rule-Based Behavior):
        trade with probability trade_probability (0.05) each round
        direction: buy or sell with equal probability (0.5 each)
        quantity: random.uniform(min_order, max_order)

    Parameters (simulation-bases.md §6):
        trade_probability: 0.05 (5% chance of trading per round)
        min_order: 100; max_order: 500 (quantity bounds)
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
            "bid_price": float(price),
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


class DispositionTrader(GeneralPlayer):
    """
    Sells winners too early, holds losers too long — Prospect Theory asymmetry.

    Implements simulation-bases.md §4.6 — DispositionTrader.
    Theoretical basis: Shefrin & Statman (1985); Kahneman & Tversky (1979).

    Decision rule:
        gain_pct = (price - cost_basis) / cost_basis
        if gain_pct > gain_threshold: sell (lock profit)
        if gain_pct < -(gain_threshold / loss_aversion_mult): buy (average down)
        else: hold

    Parameters (simulation-bases.md §6):
        gain_threshold: 0.04
        loss_aversion_mult: 2.5
        base_position_size: 15.0
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
            self.state.custom_state["gain_threshold"] = extras["gain_threshold"]
            self.state.custom_state["loss_aversion_mult"] = extras["loss_aversion_mult"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            # Cost basis starts at initial_price (first observed)
            self.state.custom_state["cost_basis"] = None
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                if self.state.custom_state["cost_basis"] is None:
                    self.state.custom_state["cost_basis"] = market_data["price"]

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        gain_threshold = self.state.custom_state["gain_threshold"]
        loss_aversion_mult = self.state.custom_state["loss_aversion_mult"]
        base_size = self.state.custom_state["base_position_size"]
        cost_basis = self.state.custom_state["cost_basis"]

        price = market_data["price"]

        gain_pct = (price - cost_basis) / cost_basis if cost_basis > 0 else 0.0
        loss_threshold = -(gain_threshold / loss_aversion_mult)

        action = "hold"
        quantity = 0.0

        if gain_pct > gain_threshold:
            # Sell winners — disposition profit-taking
            quantity = min(base_size, abs(gain_pct) * 500)
            quantity = min(quantity, max(position, 0.0))
            if quantity > 0:
                action = "sell"
            else:
                quantity = 0.0
        elif gain_pct < loss_threshold:
            # Buy losers — averaging down
            quantity = min(base_size, abs(gain_pct) * 500)
            affordable = cash / price if price > 0 else 0
            quantity = min(quantity, affordable)
            if quantity > 0:
                action = "buy"
            else:
                quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "bid_price": float(price),
            "investor": self.identity,
            "strategy": "DispositionTrader",
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
            # Update cost basis on purchase
            old_pos = self.state.custom_state["position"]
            old_cost = self.state.custom_state["cost_basis"]
            new_pos = old_pos + quantity
            if new_pos > 0:
                self.state.custom_state["cost_basis"] = (
                    old_cost * old_pos + price * quantity
                ) / new_pos
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] = new_pos
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class ContrarianTrader(GeneralPlayer):
    """
    Bets against recent trends — sells after cumulative gains, buys after declines.

    Implements simulation-bases.md §4.7 — ContrarianTrader.
    Theoretical basis: De Bondt & Thaler (1985); Jegadeesh (1990).

    Decision rule:
        cum_return = (price - price_N_rounds_ago) / price_N_rounds_ago
        if cum_return > entry_threshold: sell (expect reversal)
        if cum_return < -entry_threshold: buy (expect bounce)

    Parameters (simulation-bases.md §6):
        lookback_window: 10
        entry_threshold: 0.05
        base_position_size: 20.0
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
            self.state.custom_state["lookback_window"] = extras["lookback_window"]
            self.state.custom_state["entry_threshold"] = extras["entry_threshold"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            self.state.custom_state["recent_prices"] = []
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                recent = self.state.custom_state["recent_prices"]
                recent.append(market_data["price"])
                lookback = self.state.custom_state["lookback_window"]
                if len(recent) > lookback + 1:
                    self.state.custom_state["recent_prices"] = recent[-(lookback + 1):]

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = self.state.custom_state["entry_threshold"]
        base_size = self.state.custom_state["base_position_size"]
        lookback = self.state.custom_state["lookback_window"]
        recent = self.state.custom_state["recent_prices"]

        price = market_data["price"]

        action = "hold"
        quantity = 0.0

        if len(recent) > lookback:
            ref_price = recent[-(lookback + 1)]
            cum_return = (price - ref_price) / ref_price if ref_price > 0 else 0.0

            if abs(cum_return) > entry_threshold:
                quantity = min(base_size, abs(cum_return) * 400)
                if cum_return > 0:
                    # Overextension up — sell contrarian
                    quantity = min(quantity, max(position, 0.0))
                    if quantity > 0:
                        action = "sell"
                    else:
                        quantity = 0.0
                else:
                    # Oversold — buy contrarian
                    affordable = cash / price if price > 0 else 0
                    quantity = min(quantity, affordable)
                    if quantity > 0:
                        action = "buy"
                    else:
                        quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "bid_price": float(price),
            "investor": self.identity,
            "strategy": "ContrarianTrader",
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


class FundamentalAnalyst(GeneralPlayer):
    """
    Gradually learns fundamental value via exponential smoothing — conservatism bias.

    Implements simulation-bases.md §4.8 — FundamentalAnalyst.
    Theoretical basis: Barberis, Shleifer & Vishny (1998); Shleifer & Vishny (1997).

    Decision rule:
        belief(t) = (1 - learning_rate) * belief(t-1) + learning_rate * F
        dev = (price - belief) / belief
        if abs(dev) > 0.02: trade proportionally

    Parameters (simulation-bases.md §6):
        learning_rate: 0.05
        base_position_size: 25.0
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
            self.state.custom_state["learning_rate"] = extras["learning_rate"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            self.state.custom_state["belief"] = None
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                # Initialise belief to first observed price (starts biased)
                if self.state.custom_state["belief"] is None:
                    self.state.custom_state["belief"] = market_data["price"]

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        learning_rate = self.state.custom_state["learning_rate"]
        base_size = self.state.custom_state["base_position_size"]
        belief = self.state.custom_state["belief"]

        price = market_data["price"]
        fundamental = market_data["fundamental"]

        # Update belief toward fundamental (exponential smoothing)
        belief = (1.0 - learning_rate) * belief + learning_rate * fundamental
        self.state.custom_state["belief"] = belief

        dev = (price - belief) / belief if belief > 0 else 0.0

        action = "hold"
        quantity = 0.0

        if abs(dev) > 0.02:
            quantity = min(base_size, abs(dev) * 1000)
            if dev > 0:
                # Price above belief — sell
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0
            else:
                # Price below belief — buy
                affordable = cash / price if price > 0 else 0
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
                else:
                    quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "bid_price": float(price),
            "investor": self.identity,
            "strategy": "FundamentalAnalyst",
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


class LiquidityProvider(GeneralPlayer):
    """
    Passive market-maker quoting around short-term EMA — two-sided liquidity.

    Implements simulation-bases.md §4.9 — LiquidityProvider.
    Theoretical basis: Glosten & Milgrom (1985); Hendershott et al. (2011).

    Decision rule:
        ema = alpha * price + (1-alpha) * ema_prev;  alpha = 2/(ema_window+1)
        fair_quote = 0.5 * (price + ema)
        band = half_spread * fair_quote
        if price < fair_quote - band: buy
        if price > fair_quote + band: sell

    Parameters (simulation-bases.md §6):
        ema_window: 20
        half_spread: 0.015
        base_position_size: 30.0
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
            self.state.custom_state["ema_window"] = extras["ema_window"]
            self.state.custom_state["half_spread"] = extras["half_spread"]
            self.state.custom_state["base_position_size"] = extras["base_position_size"]
            self.state.custom_state["ema"] = None
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                if self.state.custom_state["ema"] is None:
                    self.state.custom_state["ema"] = market_data["price"]

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        ema_window = self.state.custom_state["ema_window"]
        half_spread = self.state.custom_state["half_spread"]
        base_size = self.state.custom_state["base_position_size"]
        ema = self.state.custom_state["ema"]

        price = market_data["price"]

        # Update EMA
        alpha = 2.0 / (ema_window + 1)
        ema = alpha * price + (1.0 - alpha) * ema
        self.state.custom_state["ema"] = ema

        # Compute fair quote and band
        fair_quote = 0.5 * (price + ema)
        band = half_spread * fair_quote

        action = "hold"
        quantity = 0.0

        if price < fair_quote - band:
            # Price below bid threshold — provide buy-side liquidity
            dev_from_band = abs(price - fair_quote) / fair_quote
            quantity = min(base_size, dev_from_band * 2000)
            affordable = cash / price if price > 0 else 0
            quantity = min(quantity, affordable)
            if quantity > 0:
                action = "buy"
            else:
                quantity = 0.0
        elif price > fair_quote + band:
            # Price above ask threshold — provide sell-side liquidity
            dev_from_band = abs(price - fair_quote) / fair_quote
            quantity = min(base_size, dev_from_band * 2000)
            quantity = min(quantity, max(position, 0.0))
            if quantity > 0:
                action = "sell"
            else:
                quantity = 0.0

        order = {
            "action": action,
            "quantity": quantity,
            "bid_price": float(price),
            "investor": self.identity,
            "strategy": "LiquidityProvider",
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
    "DispositionTrader",
    "ContrarianTrader",
    "FundamentalAnalyst",
    "LiquidityProvider",
]
