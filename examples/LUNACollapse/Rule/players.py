"""LUNACollapse Rule-Based Simulation

May 2022 Terra/LUNA crash — $40B wiped out in algorithmic stablecoin death spiral.

Theoretical Foundation:
- Klages-Mundt et al. (2020): Algorithmic stablecoin mechanism design
- Levy (2022): Death spiral dynamics
- Werner et al. (2022): DeFi contagion

Key Dynamics:
- StablecoinHolder: Redeems UST for LUNA when confidence drops, creating selling pressure
- Arbitrageur: Arbitrage between UST and LUNA amplifies the death spiral
- DeFiLender: Forced liquidations create additional cascading selling pressure
- AnchorDepositor: Withdraws from yield protocol when confidence deteriorates
- ValueBuyer: Attempts to buy at deep discount but gets overwhelmed by selling
"""

import logging
import os
import random
import hashlib

from masim.player.base import Action
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("LUNACollapse")


def _require_positive(value: float, name: str) -> None:
    """Validate a positive market scalar."""
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


def _build_order(
    player: GeneralPlayer,
    action: str,
    quantity: int,
    price: float,
    reasoning: str,
) -> dict:
    """Build the canonical order payload shared by all LUNA variants."""
    if action not in ("buy", "sell", "hold"):
        raise ValueError(f"invalid action: {action}")
    _require_positive(float(price), "bid_price")
    quantity = int(quantity)
    if quantity < 0:
        raise ValueError(f"quantity must be non-negative, got {quantity}")
    return {
        "type": "order",
        "from": player.identity,
        "action": action,
        "bid_price": float(price),
        "quantity": quantity,
        "reasoning": reasoning,
        "agent_type": player.__class__.__name__,
        "strategy": player.__class__.__name__,
    }


def _decision(action: str, quantity: int, reasoning: str) -> dict:
    """Build a Rule decision payload before execution constraints."""
    return {"action": action, "quantity": int(quantity), "reasoning": reasoning}


def _round_rng(seed: int, identity: str, round_num: int) -> random.Random:
    """Return a stable per-agent, per-round RNG independent of actor ordering."""
    material = f"{seed}:{identity}:{round_num}".encode("utf-8")
    derived_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return random.Random(derived_seed)


def _apply_trade(state: dict, action: str, quantity: int, price: float) -> int:
    """Clip an order to available resources and update portfolio state."""
    quantity = max(int(quantity), 0)
    if action == "buy" and quantity > 0:
        quantity = min(quantity, int(state["cash"] / price))
        state["cash"] -= quantity * price
        state["position"] += quantity
    elif action == "sell" and quantity > 0:
        quantity = min(quantity, max(int(state["position"]), 0))
        state["cash"] += quantity * price
        state["position"] -= quantity
    else:
        quantity = 0
    return quantity


class Market(GeneralPlayer):
    """
    Market agent for LUNACollapse simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]
            price = float(extras["initial_price"])
            fundamental = float(extras["fundamental_value"])
            _require_positive(price, "initial_price")
            _require_positive(fundamental, "fundamental_value")
            self.state.custom_state["price"] = price
            self.state.custom_state["fundamental"] = fundamental
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "fundamental"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["price_impact"] = float(extras["price_impact"])
            self.state.custom_state["mean_reversion"] = float(extras["mean_reversion"])
            self.state.custom_state["noise_std"] = float(extras["noise_std"])
            self.state.custom_state["market_depth"] = float(extras["market_depth"])
            self.state.custom_state["random_seed"] = int(extras["random_seed"])
            self.state.custom_state["price_floor"] = float(extras["price_floor"])
            self.state.custom_state["shock_schedule"] = extras["shock_schedule"]
        orders = []
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and "order" in payload:
                payload = payload["order"]
            if isinstance(payload, dict) and payload.get("type") == "order":
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
        market_depth = self.state.custom_state["market_depth"]
        _require_positive(market_depth, "market_depth")
        price_change = self.state.custom_state["price_impact"] * net_demand / market_depth
        reversion = self.state.custom_state["mean_reversion"] * (fundamental - price)
        round_num = self.state.custom_state["round"]
        rng = _round_rng(self.state.custom_state["random_seed"], self.identity, round_num)
        noise = rng.gauss(0, self.state.custom_state["noise_std"])
        schedule = self.state.custom_state["shock_schedule"]
        shock_return = float(schedule[round_num]) if round_num in schedule else 0.0
        shock = fundamental * shock_return
        new_price = max(
            price + price_change + reversion + noise + shock,
            self.state.custom_state["price_floor"],
        )
        self.state.custom_state["prev_price"] = price
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["fundamental_history"].append(fundamental)
        volume = min(buy_vol, sell_vol) + abs(net_demand) * 0.5
        self.state.custom_state["volume_history"].append(volume)
        logger.debug(
            "Round %d: price=%.2f", self.state.custom_state["round"], new_price
        )

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0
        prev_price = self.state.custom_state.get("prev_price", price)
        market_update = {
            "type": "market_update",
            "price": price,
            "prev_price": prev_price,
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


class StablecoinHolder(GeneralPlayer):
    """Redeems stablecoin for base token when confidence drops.

    Theory: simulation-bases.md §4.1 — StablecoinHolder
    Theoretical Basis: Algorithmic stablecoin redemption mechanics
    Market Role: destabilizing — redemptions amplify LUNA supply collapse
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        position = self.state.custom_state["position"]
        redemption_threshold = extras["redemption_threshold"]
        if deviation < -redemption_threshold:
            sell_qty = min(int(abs(position) * 0.5), max(position, 0))
            if sell_qty > 0:
                return _decision("sell", sell_qty, "peg break redemption pressure")
        return _decision("hold", 0, "peg deviation below redemption threshold")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        decision_payload["outbound_messages"] = [{"payload": order, "content_type": "order"}]
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class Arbitrageur(GeneralPlayer):
    """Arbitrage between stablecoin and base token amplifies the death spiral.

    Theory: simulation-bases.md §4.2 — Arbitrageur
    Theoretical Basis: Algorithmic stablecoin arbitrage mechanism
    Market Role: destabilizing — arbitrage activity amplifies price collapse
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        price = self.state.custom_state["price"]
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        arb_threshold = extras["arb_threshold"]
        if abs(deviation) > arb_threshold:
            qty = min(5000, int(abs(deviation) * 100000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return _decision("sell", sell_qty, "positive spread arbitrage sale")
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return _decision("sell", sell_qty, "depeg redemption mints and sells base token")
        return _decision("hold", 0, "spread below arbitrage threshold")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        decision_payload["outbound_messages"] = [{"payload": order, "content_type": "order"}]
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class DeFiLender(GeneralPlayer):
    """DeFi protocol triggering forced liquidations when collateral value falls.

    Theory: simulation-bases.md §4.3 — DeFiLender
    Theoretical Basis: DeFi contagion (Werner et al., 2022)
    Market Role: destabilizing — liquidation cascades amplify sell pressure
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        position = self.state.custom_state["position"]
        liq_threshold = extras["liquidation_threshold"]
        if deviation < -liq_threshold:
            sell_qty = min(int(abs(position) * 0.6), max(position, 0))
            if sell_qty > 0:
                return _decision("sell", sell_qty, "collateral breach liquidation")
        return _decision("hold", 0, "collateral deviation below liquidation threshold")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        decision_payload["outbound_messages"] = [{"payload": order, "content_type": "order"}]
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class AnchorDepositor(GeneralPlayer):
    """Withdraws from high-yield protocol when ecosystem confidence drops.

    Theory: simulation-bases.md §4.4 — AnchorDepositor
    Theoretical Basis: Bank run dynamics in DeFi yield protocols
    Market Role: destabilizing — rapid withdrawals collapse TVL
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        extras = self.config.extras
        position = self.state.custom_state["position"]
        yield_threshold = extras["yield_threshold"]
        if deviation < -yield_threshold:
            sell_qty = min(int(position * 0.4), max(position, 0))
            if sell_qty > 0:
                return _decision("sell", sell_qty, "Anchor confidence withdrawal")
        return _decision("hold", 0, "ecosystem stress below withdrawal threshold")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        decision_payload["outbound_messages"] = [{"payload": order, "content_type": "order"}]
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class ValueBuyer(GeneralPlayer):
    """Contrarian value investor attempting to buy at deep discount.

    Theory: simulation-bases.md §4.5 — ValueBuyer
    Theoretical Basis: Mean reversion / fundamental value investing
    Market Role: stabilizing — but overwhelmed by selling pressure in crisis
    """

    async def perceive(self, observation, prev_result=None) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.inbounds:
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload.get("type") == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        deviation = self.state.custom_state["deviation"]
        price = self.state.custom_state["price"]
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        discount_threshold = extras["discount_threshold"]
        if deviation < -discount_threshold:
            buy_qty = min(1000, int(cash * 0.2 / price) if price > 0 else 0)
            if buy_qty > 0:
                return _decision("buy", buy_qty, "deep discount value entry")
        return _decision("hold", 0, "discount below value-entry threshold")

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state["price"]
        quantity = _apply_trade(self.state.custom_state, action, quantity, price)
        order = _build_order(self, action, quantity, price, decision_payload["reasoning"])
        decision_payload["outbound_messages"] = [{"payload": order, "content_type": "order"}]
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
    "StablecoinHolder",
    "Arbitrageur",
    "DeFiLender",
    "AnchorDepositor",
    "ValueBuyer",
]
