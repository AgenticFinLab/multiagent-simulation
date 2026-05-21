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


def _require_positive(value: float, label: str) -> None:
    """Fail fast when a required positive scalar is invalid."""
    if value <= 0:
        raise ValueError(f"{label} must be positive, got {value}")


def _build_order(
    player: GeneralPlayer,
    action: str,
    quantity: int,
    price: float,
    reasoning: str,
) -> Dict[str, Any]:
    """Build the canonical order payload shared by all variants."""
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
            _require_positive(self.state.custom_state["price"], "initial_price")
            _require_positive(self.state.custom_state["fundamental"], "fundamental_value")
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

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if "type" not in payload and "order" in payload:
                    payload = payload["order"]
                if payload["type"] == "order":
                    orders.append(
                        {
                            "agent_id": payload["from"],
                            "action": payload["action"],
                            "quantity": payload["quantity"],
                            "agent_type": payload["agent_type"],
                            "bid_price": payload["bid_price"],
                            "reasoning": payload["reasoning"],
                        }
                    )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        _require_positive(price, "price")
        _require_positive(fundamental, "fundamental")
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
        deviation = (new_price - fundamental) / fundamental

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["fundamental_history"].append(fundamental)
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
    """Base investor for OverconfidenceBias simulation.

    Theoretical basis: simulation-bases.md §4.
    Strategy specification: simulation-bases.md §4.1-§4.5.
    Parameters: simulation-bases.md §6.
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
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload["type"] == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        return {"action": "hold", "quantity": 0, "reasoning": "baseline hold"}

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        agent_type = self.__class__.__name__

        decision = self._make_decision(price, fundamental, deviation)
        _require_positive(price, "price")

        order = _build_order(
            self,
            decision["action"],
            decision["quantity"],
            price,
            decision["reasoning"],
        )
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
    """Overestimates signal precision, trades too frequently.

    Theoretical basis: simulation-bases.md §4.1 — OverconfidentTrader.
    Strategy specification: simulation-bases.md §4.1.4.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        precision_over = extras["precision_overestimate"]
        base_size = extras["base_size"]

        signal = deviation * precision_over
        if abs(signal) > 0.01:
            qty = min(base_size * 2, int(abs(signal) * 5000))
            if signal > 0:
                _require_positive(price, "price")
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    self.state.custom_state["cash"] -= buy_qty * price
                    self.state.custom_state["position"] += buy_qty
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": f"overestimated signal={signal:+.3f}",
                    }
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    self.state.custom_state["cash"] += sell_qty * price
                    self.state.custom_state["position"] -= sell_qty
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": f"overestimated negative signal={signal:+.3f}",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "signal below overconfidence threshold"}


class SelfAttributor(BaseInvestor):
    """Attributes success to skill, failure to bad luck.

    Theoretical basis: simulation-bases.md §4.2 — SelfAttributor.
    Strategy specification: simulation-bases.md §4.2.4.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        confidence_boost = extras["confidence_boost"]
        base_size = extras["base_size"]

        if position > 0 and deviation > 0:
            _require_positive(price, "price")
            boosted_qty = min(base_size * 2, int(base_size * (1 + confidence_boost)))
            buy_qty = min(boosted_qty, int(cash / price))
            if buy_qty > 0:
                self.state.custom_state["cash"] -= buy_qty * price
                self.state.custom_state["position"] += buy_qty
                return {
                    "action": "buy",
                    "quantity": buy_qty,
                    "reasoning": f"self-attribution confidence_boost={confidence_boost:.2f}",
                }
        elif deviation < -0.02:
            sell_qty = min(int(base_size * 1.5), max(position, 0))
            if sell_qty > 0:
                self.state.custom_state["cash"] += sell_qty * price
                self.state.custom_state["position"] -= sell_qty
                return {
                    "action": "sell",
                    "quantity": sell_qty,
                    "reasoning": "loss blamed externally but exposure trimmed",
                }
        return {"action": "hold", "quantity": 0, "reasoning": "no self-attribution trigger"}


class CalibratedTrader(BaseInvestor):
    """Correctly estimates signal precision, trades appropriately.

    Theoretical basis: simulation-bases.md §4.3 — CalibratedTrader.
    Strategy specification: simulation-bases.md §4.3.4.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        signal_precision = extras["signal_precision"]
        trade_threshold = extras["trade_threshold"]
        base_size = extras["base_size"]

        if abs(deviation) > trade_threshold:
            qty = min(base_size, int(abs(deviation) * signal_precision * 3000))
            if deviation < 0:
                _require_positive(price, "price")
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    self.state.custom_state["cash"] -= buy_qty * price
                    self.state.custom_state["position"] += buy_qty
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": f"calibrated undervaluation deviation={deviation:+.2%}",
                    }
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    self.state.custom_state["cash"] += sell_qty * price
                    self.state.custom_state["position"] -= sell_qty
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": f"calibrated overvaluation deviation={deviation:+.2%}",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "deviation below calibrated threshold"}


class ContrarianInvestor(BaseInvestor):
    """Trades against overconfident moves.

    Theoretical basis: simulation-bases.md §4.4 — ContrarianInvestor.
    Strategy specification: simulation-bases.md §4.4.4.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        contrarian_threshold = extras["contrarian_threshold"]
        base_size = extras["base_size"]

        if abs(deviation) > contrarian_threshold:
            qty = min(base_size, int(abs(deviation) * 2000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    self.state.custom_state["cash"] += sell_qty * price
                    self.state.custom_state["position"] -= sell_qty
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": f"contrarian fade overvaluation={deviation:+.2%}",
                    }
            else:
                _require_positive(price, "price")
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    self.state.custom_state["cash"] -= buy_qty * price
                    self.state.custom_state["position"] += buy_qty
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": f"contrarian buy undervaluation={deviation:+.2%}",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "contrarian threshold not crossed"}


class NoiseTrader(BaseInvestor):
    """Random uninformed trader.

    Theoretical basis: simulation-bases.md §4.5 — NoiseTrader.
    Strategy specification: simulation-bases.md §4.5.4.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras["trade_probability"]
        noise_size = extras["noise_size"]

        if random.random() < prob:
            qty = random.randint(1, noise_size)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                _require_positive(price, "price")
                qty = min(qty, int(cash / price))
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                if action == "buy":
                    self.state.custom_state["cash"] -= qty * price
                    self.state.custom_state["position"] += qty
                else:
                    self.state.custom_state["cash"] += qty * price
                    self.state.custom_state["position"] -= qty
                return {
                    "action": action,
                    "quantity": qty,
                    "reasoning": f"noise draw under trade_probability={prob:.2f}",
                }
        return {"action": "hold", "quantity": 0, "reasoning": "noise hold"}


__all__ = [
    "Market",
    "BaseInvestor",
    "OverconfidentTrader",
    "SelfAttributor",
    "CalibratedTrader",
    "ContrarianInvestor",
    "NoiseTrader",
]
