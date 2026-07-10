"""ArchegosCollapse Rule-Based Simulation

March 2021 — Archegos Capital Management lost $20B, triggering forced block trade fire sales.

Theoretical Foundation:
    - Becketti (2021): Total Return Swap leverage dynamics
    - Concentrated portfolio liquidation and cascade selling
    - Prime broker competition and information asymmetry in forced liquidation

Key Dynamics:
    - ConcentratedFund: Holds large positions via TRS; forced to sell on margin call
    - PrimeBrokerFirstMover: First-mover liquidator — sells quickly, receives better prices
    - PrimeBrokerDelayedLiquidator: Delayed liquidator — faces worse prices due to cascade
    - BlockTradeBuyer: Opportunistic buyer at discount during fire sale
    - InformationTrader: Detects liquidation signals and trades ahead of selling pressure

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.format.order import validate_order
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("ArchegosCollapse")


class Market(GeneralPlayer):
    """
    Central market for ArchegosCollapse simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
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
            self.state.custom_state["demand_scale"] = extras["demand_scale"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
            self.state.custom_state["initial_shock_round"] = extras[
                "initial_shock_round"
            ]
            self.state.custom_state["initial_shock_quantity"] = extras[
                "initial_shock_quantity"
            ]
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
        demand_scale = self.state.custom_state["demand_scale"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]
        initial_shock_round = self.state.custom_state["initial_shock_round"]
        initial_shock_quantity = self.state.custom_state["initial_shock_quantity"]
        if demand_scale <= 0:
            raise ValueError("demand_scale must be positive")

        buy_qty = sum(o["quantity"] for o in orders if o["action"] == "buy")
        sell_qty = sum(o["quantity"] for o in orders if o["action"] == "sell")
        if round_num == initial_shock_round:
            sell_qty += initial_shock_quantity
        net_demand = buy_qty - sell_qty

        noise = random.gauss(0, noise_std)
        new_price = (
            current_price
            + price_impact * net_demand / demand_scale
            + mean_reversion * (fundamental - current_price)
            + noise
        )
        new_price = max(new_price, 0.01)

        if fundamental <= 0:
            raise ValueError("fundamental_value must be positive")
        deviation = (new_price - fundamental) / fundamental
        prev_price = current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["prev_price"] = prev_price
        self.state.custom_state["deviation"] = deviation
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "Round %d: price=%.2f deviation=%+.2f%%",
            round_num,
            new_price,
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


class ConcentratedFund(GeneralPlayer):
    """
    TRS-leveraged concentrated fund (TRS-based).

    Theory: simulation-bases.md §4.1 — ConcentratedFund
    Theoretical basis: Total Return Swap Leverage (Becketti, 2021); Hidden leverage and TRS exposure (Becketti, 2021; FSB, 2022).
    Forced to sell when price drops below margin threshold.
    Sells trs_sell_ratio * position when margin call triggered.
    See simulation-bases.md §4.1.5.4 for mathematical model.
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
            self.state.custom_state["margin_threshold"] = extras["margin_threshold"]
            self.state.custom_state["trs_sell_ratio"] = extras["trs_sell_ratio"]
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
        position = self.state.custom_state["position"]
        cash = self.state.custom_state["cash"]
        margin_threshold = self.state.custom_state["margin_threshold"]
        trs_sell_ratio = self.state.custom_state["trs_sell_ratio"]

        price = market_data["price"]
        deviation = market_data["deviation"]

        action = "hold"
        quantity = 0.0

        if deviation < margin_threshold:
            quantity = position * trs_sell_ratio
            quantity = min(quantity, max(position, 0.0))
            if quantity > 0:
                action = "sell"

        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "ConcentratedFund",
            "reasoning": "TRS margin threshold rule",
        }
        validate_order(order)

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["market_data"]["price"]

        if action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class PrimeBrokerFirstMover(GeneralPlayer):
    """
    First-mover prime broker liquidator.

    Theory: simulation-bases.md §4.2 — PrimeBrokerFirstMover
    Theoretical basis: Creditor Run / Liquidation Race (Gorton & Metrick, 2012).
    Acts when price drops below liquidation_threshold.
    Sells liquidation_sell_ratio * position per round at market price.
    First-mover advantage: receives full market price (no price_penalty).
    See simulation-bases.md §4.2.5.4 for mathematical model.
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
            self.state.custom_state["liquidation_threshold"] = extras[
                "liquidation_threshold"
            ]
            self.state.custom_state["liquidation_sell_ratio"] = extras[
                "liquidation_sell_ratio"
            ]
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
        position = self.state.custom_state["position"]
        liquidation_threshold = self.state.custom_state["liquidation_threshold"]
        liquidation_sell_ratio = self.state.custom_state["liquidation_sell_ratio"]

        deviation = market_data["deviation"]

        action = "hold"
        quantity = 0.0

        if deviation < liquidation_threshold:
            quantity = position * liquidation_sell_ratio
            quantity = min(quantity, max(position, 0.0))
            if quantity > 0:
                action = "sell"

        price = market_data["price"]
        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "PrimeBrokerFirstMover",
            "reasoning": "first-mover liquidation threshold rule",
        }
        validate_order(order)

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["market_data"]["price"]

        if action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class PrimeBrokerDelayedLiquidator(GeneralPlayer):
    """
    Delayed second-mover prime broker.

    Theory: simulation-bases.md §4.3 — PrimeBrokerDelayedLiquidator
    Theoretical basis: Creditor Run / Liquidation Race (Gorton & Metrick, 2012).
    Higher threshold required before acting (waits longer than PrimeBrokerFirstMover).
    Faces worse prices due to first-mover's prior liquidation selling pressure.
    Effective price = market_price * price_penalty.
    See simulation-bases.md §4.3.5.4 for mathematical model.
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
            self.state.custom_state["liquidation_threshold"] = extras[
                "liquidation_threshold"
            ]
            self.state.custom_state["liquidation_sell_ratio"] = extras[
                "liquidation_sell_ratio"
            ]
            self.state.custom_state["price_penalty"] = extras["price_penalty"]
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
        position = self.state.custom_state["position"]
        liquidation_threshold = self.state.custom_state["liquidation_threshold"]
        liquidation_sell_ratio = self.state.custom_state["liquidation_sell_ratio"]
        price_penalty = self.state.custom_state["price_penalty"]

        deviation = market_data["deviation"]
        price = market_data["price"]

        action = "hold"
        quantity = 0.0

        if deviation < liquidation_threshold:
            quantity = position * liquidation_sell_ratio
            quantity = min(quantity, max(position, 0.0))
            if quantity > 0:
                action = "sell"

        order = {
            "action": action,
            "bid_price": price * price_penalty,
            "quantity": quantity,
            "price_penalty": price_penalty,
            "effective_price": price * price_penalty,
            "investor": self.identity,
            "strategy": "PrimeBrokerDelayedLiquidator",
            "reasoning": "second-mover liquidation threshold rule",
        }
        validate_order(order)

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        effective_price = decision_payload["effective_price"]

        if action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * effective_price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class BlockTradeBuyer(GeneralPlayer):
    """
    Opportunistic block trade buyer purchasing at distressed block discount.

    Theory: simulation-bases.md §4.4 — BlockTradeBuyer
    Theoretical basis: Fire-Sale Arbitrage / Liquidity Provider (Shleifer & Vishny, 1992).
    Buys when price drops below discount_threshold (relative to fundamental).
    Deploys buy_ratio of available cash per round.
    See simulation-bases.md §4.4.5.4 for mathematical model.
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
            self.state.custom_state["discount_threshold"] = extras["discount_threshold"]
            self.state.custom_state["buy_ratio"] = extras["buy_ratio"]
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
        discount_threshold = self.state.custom_state["discount_threshold"]
        buy_ratio = self.state.custom_state["buy_ratio"]

        price = market_data["price"]
        deviation = market_data["deviation"]

        action = "hold"
        quantity = 0.0

        if deviation < discount_threshold:
            if price <= 0:
                raise ValueError("market price must be positive")
            deploy = cash * buy_ratio
            quantity = deploy / price
            if quantity > 0:
                action = "buy"

        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "BlockTradeBuyer",
            "reasoning": "distressed block discount buying rule",
        }
        validate_order(order)

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

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class InformationTrader(GeneralPlayer):
    """
    Front-running information trader detecting liquidation signals.

    Theory: simulation-bases.md §4.5 — InformationTrader
    Theoretical basis: Informed Trading / Front-Running (Kyle, 1985; Brunnermeier & Pedersen, 2005).
    Detects distress signal when deviation < detection_threshold with
    probability detection_ability. Sells front_run_size shares.
    Covers short when deviation recovers above cover_threshold.
    See simulation-bases.md §4.5.5.4 for mathematical model.
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
            self.state.custom_state["detection_ability"] = extras["detection_ability"]
            self.state.custom_state["detection_threshold"] = extras[
                "detection_threshold"
            ]
            self.state.custom_state["front_run_size"] = extras["front_run_size"]
            self.state.custom_state["cover_threshold"] = extras["cover_threshold"]
            self.state.custom_state["cover_size"] = extras["cover_size"]
            self.state.custom_state["short_position"] = 0.0
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
        short_position = self.state.custom_state["short_position"]
        detection_ability = self.state.custom_state["detection_ability"]
        detection_threshold = self.state.custom_state["detection_threshold"]
        front_run_size = self.state.custom_state["front_run_size"]
        cover_threshold = self.state.custom_state["cover_threshold"]
        cover_size = self.state.custom_state["cover_size"]

        price = market_data["price"]
        deviation = market_data["deviation"]

        action = "hold"
        quantity = 0.0

        if deviation < detection_threshold and random.random() < detection_ability:
            sell_qty = min(front_run_size, max(position, 0.0))
            if sell_qty > 0:
                action = "sell"
                quantity = sell_qty
        elif deviation > cover_threshold and short_position > 0:
            buy_qty = min(cover_size, short_position)
            if price <= 0:
                raise ValueError("market price must be positive")
            affordable = cash / price
            buy_qty = min(buy_qty, affordable)
            if buy_qty > 0:
                action = "buy"
                quantity = buy_qty

        order = {
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "investor": self.identity,
            "strategy": "InformationTrader",
            "reasoning": "probabilistic liquidation-signal rule",
        }
        validate_order(order)

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["market_data"]["price"]

        if action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
            self.state.custom_state["short_position"] += quantity
        elif action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
            short_pos = self.state.custom_state["short_position"]
            self.state.custom_state["short_position"] = max(0.0, short_pos - quantity)

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "ConcentratedFund",
    "PrimeBrokerFirstMover",
    "PrimeBrokerDelayedLiquidator",
    "BlockTradeBuyer",
    "InformationTrader",
]
