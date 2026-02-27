"""EquityPremium - Equity Premium Puzzle Simulation

Phenomenon: Equity Premium Puzzle (Mehra & Prescott, 1985)
    - Stocks historically return ~6% more than bonds
    - Standard theory cannot explain this premium with reasonable risk aversion
    - Myopic Loss Aversion (Benartzi & Thaler, 1995) provides behavioral explanation:
      * Investors evaluate portfolios frequently
      * Losses hurt more than gains feel good (λ ≈ 2.25)
      * Short evaluation periods → stocks look risky → high premium demanded
"""

import os
import random
import math
from typing import Any, Dict, Optional
from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


class Market(GeneralPlayer):
    """Market with two assets: stock and bond."""

    STOCK_EXPECTED_RETURN = 0.06 / 252  # ~6% annual / 252 trading days
    BOND_RETURN = 0.01 / 252  # ~1% annual risk-free rate
    STOCK_VOLATILITY = 0.15 / math.sqrt(252)  # ~15% annual volatility
    INITIAL_STOCK_PRICE = 100.0
    HISTORY_LIMIT = 200

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "stock_price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["stock_price"] = self.INITIAL_STOCK_PRICE
            self.state.custom_state["stock_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "stock"), entry_limit=self.HISTORY_LIMIT
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"), entry_limit=self.HISTORY_LIMIT
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "stock_qty": order["stock_qty"],
                        "strategy": order["strategy"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["stock_price"]
        orders = self.state.custom_state["orders"]

        # Stock return with demand impact
        net_stock_demand = sum(o["stock_qty"] for o in orders)
        demand_impact = 0.001 * net_stock_demand

        base_return = self.STOCK_EXPECTED_RETURN + random.gauss(
            0, self.STOCK_VOLATILITY
        )
        stock_return = base_return + demand_impact

        new_price = max(1.0, current_price * (1 + stock_return))
        total_volume = sum(abs(o["stock_qty"]) for o in orders)

        self.state.custom_state["stock_price"] = new_price
        self.state.custom_state["stock_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)

        print(
            f"\n[Market] R{round_num} Stock: {current_price:.2f}→{new_price:.2f} ({stock_return*100:+.3f}%) Bond: {self.BOND_RETURN*100:.4f}%"
        )

        market_data = {
            "stock_price": new_price,
            "prev_stock_price": current_price,
            "stock_return": stock_return,
            "bond_return": self.BOND_RETURN,
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


class BaseInvestor(GeneralPlayer):
    STRATEGY_NAME = "base"
    INITIAL_CASH = 10000.0
    INITIAL_STOCK = 0.0
    HISTORY_LIMIT = 50

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["stock"] = self.INITIAL_STOCK
            self.state.custom_state["stock_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "stock"),
                entry_limit=self.HISTORY_LIMIT,
            )
        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload
                self.state.custom_state["stock_history"].append(
                    inb.payload["stock_price"]
                )

    def _execute_trade(self, stock_qty: float, price: float) -> None:
        if stock_qty > 0:
            cost = stock_qty * price
            if cost <= self.state.custom_state["cash"]:
                self.state.custom_state["cash"] -= cost
                self.state.custom_state["stock"] += stock_qty
        elif stock_qty < 0 and self.state.custom_state["stock"] >= abs(stock_qty):
            proceeds = abs(stock_qty) * price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["stock"] += stock_qty

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class MyopicLossAverseInvestor(BaseInvestor):
    """
    Myopic Loss Averse Investor (Benartzi & Thaler, 1995)
    - Evaluates portfolio frequently (myopia)
    - Loss aversion λ ≈ 2.25
    - Demands high premium for risky stocks
    """

    STRATEGY_NAME = "myopic_loss_averse"
    LOSS_AVERSION = 2.25
    EVALUATION_WINDOW = 5  # Short horizon (myopic)
    RISK_AVERSION = 2.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]
        stock_history = self.state.custom_state["stock_history"]
        cash = self.state.custom_state["cash"]
        stock = self.state.custom_state["stock"]

        # Calculate recent volatility (myopic evaluation)
        if len(stock_history) >= self.EVALUATION_WINDOW:
            recent = list(stock_history)[-self.EVALUATION_WINDOW :]
            returns = [
                (recent[i] - recent[i - 1]) / recent[i - 1]
                for i in range(1, len(recent))
            ]
            vol = (
                (sum(r**2 for r in returns) / len(returns)) ** 0.5 if returns else 0.02
            )
            loss_prob = (
                sum(1 for r in returns if r < 0) / len(returns) if returns else 0.5
            )
        else:
            vol = 0.02
            loss_prob = 0.5

        # Myopic loss aversion: weight losses more heavily
        perceived_risk = vol * (1 + self.LOSS_AVERSION * loss_prob)

        # Target allocation based on perceived risk
        target_stock_pct = max(0.1, 0.5 - self.RISK_AVERSION * perceived_risk)
        portfolio_value = cash + stock * stock_price
        target_stock_value = target_stock_pct * portfolio_value
        current_stock_value = stock * stock_price

        stock_qty = (
            (target_stock_value - current_stock_value) / stock_price * 0.3
        )  # Gradual
        stock_qty = max(-10, min(10, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        print(
            f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f} target_pct={target_stock_pct:.1%}"
        )
        return {
            "stock_qty": stock_qty,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": self.STRATEGY_NAME},
                    "content_type": "investor_bid",
                }
            ],
        }


class LongHorizonInvestor(BaseInvestor):
    """Long-horizon investor - less myopic, accepts more risk."""

    STRATEGY_NAME = "long_horizon"
    EVALUATION_WINDOW = 50  # Long horizon

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]
        cash = self.state.custom_state["cash"]
        stock = self.state.custom_state["stock"]

        # Long-horizon investors accept more stock
        target_stock_pct = 0.6
        portfolio_value = cash + stock * stock_price
        target_stock_value = target_stock_pct * portfolio_value
        current_stock_value = stock * stock_price

        stock_qty = (target_stock_value - current_stock_value) / stock_price * 0.2
        stock_qty = max(-15, min(15, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        print(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")
        return {
            "stock_qty": stock_qty,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": self.STRATEGY_NAME},
                    "content_type": "investor_bid",
                }
            ],
        }


class RiskNeutralInvestor(BaseInvestor):
    """Risk-neutral investor - theoretically optimal."""

    STRATEGY_NAME = "risk_neutral"

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]

        # Expected excess return
        excess_return = market_data["stock_return"] - market_data["bond_return"]
        stock_qty = excess_return * 500  # Buy if positive excess return
        stock_qty = max(-20, min(20, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        print(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")
        return {
            "stock_qty": stock_qty,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": self.STRATEGY_NAME},
                    "content_type": "investor_bid",
                }
            ],
        }


class ConservativeInvestor(BaseInvestor):
    """Conservative investor - prefers bonds."""

    STRATEGY_NAME = "conservative"

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]
        stock = self.state.custom_state["stock"]

        # Very low stock allocation
        target_stock_pct = 0.2
        cash = self.state.custom_state["cash"]
        portfolio_value = cash + stock * stock_price
        target_stock_value = target_stock_pct * portfolio_value
        current_stock_value = stock * stock_price

        stock_qty = (target_stock_value - current_stock_value) / stock_price * 0.1
        stock_qty = max(-5, min(5, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        print(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")
        return {
            "stock_qty": stock_qty,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": self.STRATEGY_NAME},
                    "content_type": "investor_bid",
                }
            ],
        }


class NoiseTrader(BaseInvestor):
    """Noise trader with random allocation changes."""

    STRATEGY_NAME = "noise"

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]

        stock_qty = random.gauss(0, 8)
        stock_qty = max(-10, min(10, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        print(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")
        return {
            "stock_qty": stock_qty,
            "strategy": self.STRATEGY_NAME,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": self.STRATEGY_NAME},
                    "content_type": "investor_bid",
                }
            ],
        }
