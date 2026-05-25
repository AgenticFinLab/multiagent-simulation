"""AvailabilityBias Rule-Based Simulation

Availability bias causes traders to overweight salient and recent information,
creating persistent overreaction to dramatic events.

Theoretical Foundation:
    - Tversky & Kahneman (1973): Availability heuristic
    - Schwarz et al. (1991): Ease of retrieval as information
    - Mullainathan (2002): A memory-based model for bounded rationality

Key Dynamics:
    - RecentEventOverweighter: Overweights recent dramatic market events
    - MediaInfluencedTrader: Overweights information from prominent media/social signals
    - SystematicAnalyst: Weighs all information by objective relevance (benchmark)
    - ValueTrader: Trades on fundamentals regardless of available narratives
    - NoiseTrader: Random uninformed trader providing baseline liquidity

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("AvailabilityBias")


def _require_positive(value: float, label: str) -> None:
    """Fail fast when a required positive market scalar is invalid."""
    if value <= 0:
        raise ValueError(f"{label} must be positive, got {value}")


def _build_order(
    player: GeneralPlayer,
    action: str,
    quantity: float,
    price: float,
    reasoning: str,
    strategy: str,
) -> Dict[str, Any]:
    """Build the canonical order schema consumed by the market and record loaders."""
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"{player.identity} emitted invalid action: {action}")
    _require_positive(price, "bid_price")
    return {
        "type": "order",
        "from": player.identity,
        "action": action,
        "bid_price": price,
        "quantity": max(0.0, float(quantity)),
        "reasoning": reasoning,
        "agent_type": player.__class__.__name__,
        "strategy": strategy,
        "investor": player.identity,
    }


def _apply_order(player: GeneralPlayer, order: Dict[str, Any]) -> None:
    """Apply a filled canonical order to local portfolio state."""
    action = order["action"]
    quantity = float(order["quantity"])
    price = float(order["bid_price"])
    _require_positive(price, "bid_price")
    if action == "buy" and quantity > 0:
        player.state.custom_state["cash"] -= quantity * price
        player.state.custom_state["position"] += quantity
    elif action == "sell" and quantity > 0:
        player.state.custom_state["cash"] += quantity * price
        player.state.custom_state["position"] -= quantity


class Market(GeneralPlayer):
    """
    Central market for AvailabilityBias simulation.

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
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, "market", "price"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(record_path, "market", "fundamental"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(record_path, "market", "volume"),
                entry_limit=hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict) and "order" in payload:
                    payload = payload["order"]
                if isinstance(payload, dict) and payload["type"] == "order":
                    orders.append(payload)

        current_price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        _require_positive(current_price, "current_price")
        _require_positive(fundamental, "fundamental")
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        buy_qty = sum(o["quantity"] for o in orders if o["action"] == "buy")
        sell_qty = sum(o["quantity"] for o in orders if o["action"] == "sell")
        net_demand = buy_qty - sell_qty
        volume = buy_qty + sell_qty

        noise = random.gauss(0, noise_std)
        new_price = (
            current_price
            + price_impact * net_demand
            + mean_reversion * (fundamental - current_price)
            + noise
        )
        new_price = max(new_price, 0.01)

        deviation = (new_price - fundamental) / fundamental
        prev_price = current_price
        _require_positive(prev_price, "prev_price")
        return_pct = (new_price - prev_price) / prev_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["prev_price"] = prev_price
        self.state.custom_state["deviation"] = deviation
        self.state.custom_state["return_pct"] = return_pct
        self.state.custom_state["volume"] = volume
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["fundamental_history"].append(fundamental)
        self.state.custom_state["volume_history"].append(volume)

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
        return_pct = self.state.custom_state["return_pct"]
        round_num = self.state.custom_state["round"]

        market_data = {
            "price": price,
            "prev_price": prev_price,
            "fundamental": fundamental,
            "deviation": deviation,
            "return_pct": return_pct,
            "volume": self.state.custom_state["volume"],
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


class RecentEventOverweighter(GeneralPlayer):
    """
    Overweights recent dramatic market events in decision-making.

    Theory: simulation-bases.md §4.1 — RecentEventOverweighter
    Theoretical basis: Tversky & Kahneman (1973) — Availability heuristic recency channel.
    Perceived signal = recency_weight * recent_return + (1-recency_weight) * deviation.
    Trades when perceived signal exceeds salience_threshold.
    See simulation-bases.md §4.1.4.3 for mathematical model.
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
            self.state.custom_state["recency_weight"] = extras["recency_weight"]
            self.state.custom_state["salience_threshold"] = extras["salience_threshold"]
            self.state.custom_state["max_order"] = extras["max_order"]
            self.state.custom_state["quantity_scale"] = extras["quantity_scale"]
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
        recency_weight = self.state.custom_state["recency_weight"]
        salience_threshold = self.state.custom_state["salience_threshold"]
        max_order = self.state.custom_state["max_order"]
        quantity_scale = self.state.custom_state["quantity_scale"]

        price = market_data["price"]
        _require_positive(price, "market price")
        deviation = market_data["deviation"]
        return_pct = market_data["return_pct"]

        perceived_signal = (
            recency_weight * return_pct + (1 - recency_weight) * deviation
        )

        action = "hold"
        quantity = 0.0

        if abs(perceived_signal) > salience_threshold:
            quantity = min(max_order, abs(perceived_signal) * quantity_scale)
            if perceived_signal > 0:
                affordable = cash / price
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0

        order = _build_order(
            self,
            action,
            quantity,
            price,
            f"perceived_signal={perceived_signal:+.4f}",
            "RecentEventOverweighter",
        )

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        _apply_order(self, decision_payload)

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class MediaInfluencedTrader(GeneralPlayer):
    """
    Overweights information from prominent media/social coverage.

    Theory: simulation-bases.md §4.2 — MediaInfluencedTrader
    Theoretical basis: Schwarz et al. (1991); Tetlock (2007) — Media-driven availability channel.
    Amplifies the perceived deviation by social_amplification factor,
    then trades when media-weighted signal exceeds threshold.
    See simulation-bases.md §4.2.4.3 for mathematical model.
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
            self.state.custom_state["media_weight"] = extras["media_weight"]
            self.state.custom_state["social_amplification"] = extras[
                "social_amplification"
            ]
            self.state.custom_state["media_threshold"] = extras["media_threshold"]
            self.state.custom_state["max_order"] = extras["max_order"]
            self.state.custom_state["quantity_scale"] = extras["quantity_scale"]
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
        media_weight = self.state.custom_state["media_weight"]
        social_amplification = self.state.custom_state["social_amplification"]
        media_threshold = self.state.custom_state["media_threshold"]
        max_order = self.state.custom_state["max_order"]
        quantity_scale = self.state.custom_state["quantity_scale"]

        price = market_data["price"]
        _require_positive(price, "market price")
        deviation = market_data["deviation"]

        amplified_signal = media_weight * deviation * social_amplification

        action = "hold"
        quantity = 0.0

        if abs(amplified_signal) > media_threshold:
            quantity = min(max_order, abs(amplified_signal) * quantity_scale)
            if amplified_signal > 0:
                affordable = cash / price
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0

        order = _build_order(
            self,
            action,
            quantity,
            price,
            f"amplified_signal={amplified_signal:+.4f}",
            "MediaInfluencedTrader",
        )

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        _apply_order(self, decision_payload)

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class SystematicAnalyst(GeneralPlayer):
    """
    Systematic analyst — weighs all information by objective relevance (benchmark).

    Theory: simulation-bases.md §4.3 — SystematicAnalyst
    Theoretical basis: Mullainathan (2002) — Bayesian rational processing; absence of bias.
    Trades on fundamental deviation without availability bias.
    See simulation-bases.md §4.3.4.3 for mathematical model.
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
            self.state.custom_state["evidence_threshold"] = extras[
                "evidence_threshold"
            ]
            self.state.custom_state["max_order"] = extras["max_order"]
            self.state.custom_state["quantity_scale"] = extras["quantity_scale"]
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
        evidence_threshold = self.state.custom_state["evidence_threshold"]
        max_order = self.state.custom_state["max_order"]
        quantity_scale = self.state.custom_state["quantity_scale"]

        price = market_data["price"]
        _require_positive(price, "market price")
        deviation = market_data["deviation"]

        action = "hold"
        quantity = 0.0

        if abs(deviation) > evidence_threshold:
            quantity = min(max_order, abs(deviation) * quantity_scale)
            if deviation < 0:
                affordable = cash / price
                quantity = min(quantity, affordable)
                if quantity > 0:
                    action = "buy"
            else:
                quantity = min(quantity, max(position, 0.0))
                if quantity > 0:
                    action = "sell"
                else:
                    quantity = 0.0

        order = _build_order(
            self,
            action,
            quantity,
            price,
            f"deviation={deviation:+.4f}",
            "SystematicAnalyst",
        )

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        _apply_order(self, decision_payload)

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class ValueTrader(GeneralPlayer):
    """
    Value trader — trades on fundamentals, ignores media narratives.

    Theory: simulation-bases.md §4.4 — ValueTrader
    Theoretical basis: Graham (1949); Baker & Wurgler (2007) — Value investing discipline.
    Trades when deviation exceeds deviation_threshold with fixed position_size.
    See simulation-bases.md §4.4.4.3 for mathematical model.
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
            self.state.custom_state["deviation_threshold"] = extras[
                "deviation_threshold"
            ]
            self.state.custom_state["position_size"] = extras["position_size"]
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
        deviation_threshold = self.state.custom_state["deviation_threshold"]
        position_size = self.state.custom_state["position_size"]

        price = market_data["price"]
        _require_positive(price, "market price")
        deviation = market_data["deviation"]

        action = "hold"
        quantity = 0.0

        if deviation < -deviation_threshold:
            affordable = cash / price
            quantity = min(position_size, affordable)
            if quantity > 0:
                action = "buy"
        elif deviation > deviation_threshold:
            quantity = min(position_size, max(position, 0.0))
            if quantity > 0:
                action = "sell"

        order = _build_order(
            self,
            action,
            quantity,
            price,
            f"deviation={deviation:+.4f}",
            "ValueTrader",
        )

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        _apply_order(self, decision_payload)

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """
    Random uninformed trader providing baseline liquidity.

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: Black (1986) — Noise traders.
    Trades randomly with probability trade_probability each round.
    See simulation-bases.md §4.5.4.3 for mathematical model.
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
        _require_positive(price, "market price")

        action = "hold"
        quantity = 0.0

        if random.random() < trade_prob:
            quantity = random.uniform(min_order, max_order)
            if random.random() > 0.5:
                affordable = cash / price
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

        order = _build_order(
            self,
            action,
            quantity,
            price,
            f"random_trade_probability={trade_prob:.2f}",
            "NoiseTrader",
        )

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        _apply_order(self, decision_payload)

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "RecentEventOverweighter",
    "MediaInfluencedTrader",
    "SystematicAnalyst",
    "ValueTrader",
    "NoiseTrader",
]
