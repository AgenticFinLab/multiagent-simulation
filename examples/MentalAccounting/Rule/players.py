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
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload.get("type") == "order":
                    orders.append(
                        {
                            "agent_id": inb.sender_id,
                            "action": payload.get("action"),
                            "quantity": payload.get("quantity", 0),
                            "agent_type": payload.get("agent_type", ""),
                        }
                    )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
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
        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
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
            self.state.custom_state["entry_price"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]
                    self.state.custom_state["price_history"].append(payload["price"])

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        return {"action": "hold", "quantity": 0}

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state.get("price", 0.0)
        fundamental = self.state.custom_state.get("fundamental", 0.0)
        deviation = self.state.custom_state.get("deviation", 0.0)

        decision = self._make_decision(price, fundamental, deviation)
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)

        # Execute trade
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

        order = {
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
        }

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

    Parameters from config extras:
        - num_accounts, loss_aversion_per_account
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        position = self.state.custom_state["position"]
        cash = self.state.custom_state["cash"]
        num_accounts = extras.get("num_accounts", 3)
        loss_lambda = extras.get("loss_aversion_per_account", 2.0)

        per_account_position = position / num_accounts if num_accounts > 0 else position
        entry_price = self.state.custom_state.get("entry_price", price)
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0

        if pnl > 0.05:
            sell_qty = int(per_account_position * 0.7)
            if sell_qty > 0:
                return {"action": "sell", "quantity": min(sell_qty, position)}
        elif pnl < -0.05 * loss_lambda:
            sell_qty = int(per_account_position * 0.2)
            if sell_qty > 0:
                return {"action": "sell", "quantity": min(sell_qty, position)}
        return {"action": "hold", "quantity": 0}


class HouseMoneyTrader(BaseInvestor):
    """
    Takes more risk with recent gains (house money effect).

    Parameters from config extras:
        - gain_risk_multiplier, loss_risk_multiplier
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        gain_risk = extras.get("gain_risk_multiplier", 1.5)
        loss_risk = extras.get("loss_risk_multiplier", 0.5)

        entry_price = self.state.custom_state.get("entry_price", price)
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0

        risk_factor = gain_risk if pnl > 0 else loss_risk

        if abs(deviation) > 0.02:
            qty = min(
                int(500 * risk_factor),
                int(cash * risk_factor / price) if price > 0 else 0,
            )
            if qty > 0:
                return {"action": "buy" if deviation < 0 else "sell", "quantity": qty}
        return {"action": "hold", "quantity": 0}


class RationalPortfolioManager(BaseInvestor):
    """
    Optimizes entire portfolio without mental accounting.

    Parameters from config extras:
        - risk_aversion
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_aversion = extras.get("risk_aversion", 1.0)

        if abs(deviation) > 0.02:
            qty = min(500, int(abs(deviation) * risk_aversion * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class SunkCostHolder(BaseInvestor):
    """
    Holds losing positions due to already invested capital.

    Parameters from config extras:
        - sunk_cost_weight
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        position = self.state.custom_state["position"]

        entry_price = self.state.custom_state.get("entry_price", price)
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0

        if pnl > 0.1:
            sell_qty = int(position * 0.5)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class NoiseTrader(BaseInvestor):
    """
    Random uninformed trader.

    Parameters from config extras:
        - trade_probability
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras.get("trade_probability", 0.3)

        if random.random() < prob:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "BaseInvestor",
    "MentalAccountant",
    "HouseMoneyTrader",
    "RationalPortfolioManager",
    "SunkCostHolder",
    "NoiseTrader",
]
