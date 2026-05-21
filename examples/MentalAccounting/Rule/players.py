"""MentalAccounting Rule-Based Simulation

Mental accounting causes investors to treat money differently based on its source or intended use.

Theoretical Foundation:
    - Thaler (1999): Mental Accounting Matters
    - Thaler (1985): Mental accounting and consumer choice
    - Barberis & Huang (2001): Mental accounting, loss aversion, and individual stock returns

Key Dynamics:
    - MentalAccountant: Segregates portfolio into separate accounts, doesn't net gains/losses
    - HouseMoneyTrader: Takes more risk with recent gains (house money effect)
    - RationalPortfolioManager: Optimizes entire portfolio without mental accounting
    - SunkCostHolder: Holds losing positions due to already invested capital
    - NoiseTrader: Random uninformed trader

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("MentalAccounting")


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
    """
    Central market for MentalAccounting simulation.

    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F - P(t)) + ε

    Parameters from config extras:
        - initial_price, fundamental_value
        - price_impact, mean_reversion, noise_std
        - custom_state_hot_limit, record_path
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
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
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

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict) and "order" in payload:
                    payload = payload["order"]
                if payload["type"] == "order":
                    orders.append(
                        {
                            "agent_id": payload["from"],
                            "action": payload["action"],
                            "quantity": payload["quantity"],
                            "agent_type": payload["agent_type"],
                        }
                    )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        _require_positive(price, "price")
        _require_positive(fundamental, "fundamental")
        orders = self.state.custom_state["orders"]

        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell

        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)

        new_price = max(0.01, price + price_change + reversion + noise)
        deviation = (new_price - fundamental) / fundamental
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["fundamental_history"].append(fundamental)
        self.state.custom_state["volume_history"].append(volume)

        logger.debug(
            "[Market] R%d: P=%.2f  F=%.2f  Dev=%+.2f%%  ND=%+.0f",
            round_num,
            new_price,
            fundamental,
            deviation * 100,
            net_demand,
        )

        market_data = {
            "type": "market_update",
            "price": new_price,
            "fundamental": fundamental,
            "deviation": deviation,
            "net_demand": net_demand,
            "volume": volume,
            "round": round_num,
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_update"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class BaseInvestor(GeneralPlayer):
    """
    Base class for MentalAccounting investors.

    Theoretical basis: simulation-bases.md §4
    Strategy specification: simulation-bases.md §4.1-§4.5 behavioral frameworks.
    Parameters: simulation-bases.md §6

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path
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
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            initial_price = extras["initial_price"]
            _require_positive(initial_price, "initial_price")
            self.state.custom_state["entry_price"] = initial_price
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload["type"] == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]
                    self.state.custom_state["price_history"].append(payload["price"])

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        return {"action": "hold", "quantity": 0, "reasoning": "baseline hold"}

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)
        action = decision["action"]
        quantity = max(0, int(decision["quantity"]))
        _require_positive(price, "price")

        if action == "buy":
            quantity = min(quantity, int(self.state.custom_state["cash"] / price))
        elif action == "sell":
            quantity = min(quantity, max(int(self.state.custom_state["position"]), 0))
        elif action == "hold":
            quantity = 0
        else:
            raise ValueError(f"{self.identity} emitted invalid action: {action}")

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
            if self.state.custom_state["entry_price"] == 0:
                self.state.custom_state["entry_price"] = price
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        logger.debug(
            "[%-25s] R%d: %s qty=%d | Cash=%.2f  Pos=%d  P=%.2f",
            self.identity,
            self.state.custom_state["round"],
            action,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
            price,
        )

        order = _build_order(
            self,
            action,
            quantity,
            price,
            decision["reasoning"],
        )

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class MentalAccountant(BaseInvestor):
    """
    Segregates portfolio into separate accounts, doesn't net gains/losses.

    Theoretical basis: simulation-bases.md §4.1 — MentalAccountant
    Strategy specification: simulation-bases.md §4.1.4 — Behavioral Framework
    Parameters: simulation-bases.md §6

    Parameters from config extras:
        - num_accounts, loss_aversion_per_account
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        position = self.state.custom_state["position"]
        cash = self.state.custom_state["cash"]
        num_accounts = extras["num_accounts"]
        if num_accounts <= 0:
            raise ValueError("num_accounts must be positive")
        loss_lambda = extras["loss_aversion_per_account"]

        per_account_position = position / num_accounts
        entry_price = self.state.custom_state["entry_price"]
        _require_positive(entry_price, "entry_price")
        pnl = (price - entry_price) / entry_price

        if pnl > 0.05:
            sell_qty = int(per_account_position * 0.7)
            if sell_qty > 0:
                return {
                    "action": "sell",
                    "quantity": min(sell_qty, position),
                    "reasoning": f"per-account gain pnl={pnl:+.2%}",
                }
        elif pnl < -0.05 * loss_lambda:
            sell_qty = int(per_account_position * 0.2)
            if sell_qty > 0:
                return {
                    "action": "sell",
                    "quantity": min(sell_qty, position),
                    "reasoning": f"loss-account trim pnl={pnl:+.2%}",
                }
        return {"action": "hold", "quantity": 0, "reasoning": "no account threshold crossed"}


class HouseMoneyTrader(BaseInvestor):
    """
    Takes more risk with recent gains (house money effect).

    Theoretical basis: simulation-bases.md §4.2 — HouseMoneyTrader
    Strategy specification: simulation-bases.md §4.2.4 — Behavioral Framework
    Parameters: simulation-bases.md §6

    Parameters from config extras:
        - gain_risk_multiplier, loss_risk_multiplier
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        gain_risk = extras["gain_risk_multiplier"]
        loss_risk = extras["loss_risk_multiplier"]
        base_size = extras["base_size"]
        deviation_threshold = extras["deviation_threshold"]

        entry_price = self.state.custom_state["entry_price"]
        _require_positive(entry_price, "entry_price")
        pnl = (price - entry_price) / entry_price

        risk_factor = gain_risk if pnl > 0 else loss_risk

        if abs(deviation) > deviation_threshold:
            qty = min(
                int(base_size * risk_factor),
                int(cash * risk_factor / price),
            )
            if qty > 0:
                return {
                    "action": "buy" if deviation < 0 else "sell",
                    "quantity": qty,
                    "reasoning": f"house-money risk_factor={risk_factor:.2f}",
                }
        return {"action": "hold", "quantity": 0, "reasoning": "deviation below threshold"}


class RationalPortfolioManager(BaseInvestor):
    """
    Optimizes entire portfolio without mental accounting.

    Theoretical basis: simulation-bases.md §4.3 — RationalPortfolioManager
    Strategy specification: simulation-bases.md §4.3.4 — Behavioral Framework
    Parameters: simulation-bases.md §6

    Parameters from config extras:
        - risk_aversion
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_aversion = extras["risk_aversion"]
        base_size = extras["base_size"]
        quantity_scale = extras["quantity_scale"]
        deviation_threshold = extras["deviation_threshold"]

        if abs(deviation) > deviation_threshold:
            qty = min(base_size, int(abs(deviation) * risk_aversion * quantity_scale))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price))
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": f"portfolio undervaluation deviation={deviation:+.2%}",
                    }
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": f"portfolio overvaluation deviation={deviation:+.2%}",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "deviation below threshold"}


class SunkCostHolder(BaseInvestor):
    """
    Holds losing positions due to already invested capital.

    Theoretical basis: simulation-bases.md §4.4 — SunkCostHolder
    Strategy specification: simulation-bases.md §4.4.4 — Behavioral Framework
    Parameters: simulation-bases.md §6

    Parameters from config extras:
        - sunk_cost_weight
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        position = self.state.custom_state["position"]
        sell_fraction = extras["sunk_cost_weight"]

        entry_price = self.state.custom_state["entry_price"]
        _require_positive(entry_price, "entry_price")
        pnl = (price - entry_price) / entry_price

        if pnl > 0.1:
            sell_qty = int(position * sell_fraction)
            if sell_qty > 0:
                return {
                    "action": "sell",
                    "quantity": sell_qty,
                    "reasoning": f"winner realization pnl={pnl:+.2%}",
                }
        return {"action": "hold", "quantity": 0, "reasoning": "sunk-cost hold"}


class NoiseTrader(BaseInvestor):
    """
    Random uninformed trader.

    Theoretical basis: simulation-bases.md §4.5 — NoiseTrader
    Strategy specification: simulation-bases.md §4.5.4 — Behavioral Framework
    Parameters: simulation-bases.md §6

    Parameters from config extras:
        - trade_probability
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras["trade_probability"]
        noise_size = extras["noise_size"]

        if random.random() < prob:
            qty = random.randint(1, noise_size)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price))
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {
                    "action": action,
                    "quantity": qty,
                    "reasoning": f"noise trade probability={prob:.2f}",
                }
        return {"action": "hold", "quantity": 0, "reasoning": "noise hold"}


__all__ = [
    "Market",
    "BaseInvestor",
    "MentalAccountant",
    "HouseMoneyTrader",
    "RationalPortfolioManager",
    "SunkCostHolder",
    "NoiseTrader",
]
