"""EquityPremium - Equity Premium Puzzle Simulation

Phenomenon: Equity Premium Puzzle (Mehra & Prescott, 1985)
    - Stocks historically return ~6% more than bonds
    - Standard theory cannot explain this premium with reasonable risk aversion
    - Myopic Loss Aversion (Benartzi & Thaler, 1995) provides behavioral explanation:
      * Investors evaluate portfolios frequently
      * Losses hurt more than gains feel good (λ ≈ 2.25)
      * Short evaluation periods → stocks look risky → high premium demanded

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
from typing import Any, Dict, Optional
from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("EquityPremium")


class Market(GeneralPlayer):
    """
    Market with two assets: stock and bond.

    Parameters from config extras:
        - stock_expected_return, bond_return, stock_volatility
        - initial_stock_price, custom_state_hot_limit, record_path
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "stock_price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["stock_price"] = extras["initial_stock_price"]
            self.state.custom_state["stock_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "stock"), entry_limit=custom_state_hot_limit
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"), entry_limit=custom_state_hot_limit
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
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["stock_price"]
        orders = self.state.custom_state["orders"]

        stock_expected_return = extras["stock_expected_return"]
        bond_return = extras["bond_return"]
        stock_volatility = extras["stock_volatility"]

        # Stock return with demand impact
        net_stock_demand = sum(o["stock_qty"] for o in orders)
        demand_impact = 0.001 * net_stock_demand

        base_return = stock_expected_return + random.gauss(0, stock_volatility)
        stock_return = base_return + demand_impact

        new_price = max(1.0, current_price * (1 + stock_return))
        total_volume = sum(abs(o["stock_qty"]) for o in orders)

        self.state.custom_state["stock_price"] = new_price
        self.state.custom_state["stock_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)

        logger.debug(
            f"\n[Market] R{round_num} Stock: {current_price:.2f}→{new_price:.2f} ({stock_return*100:+.3f}%) Bond: {bond_return*100:.4f}%"
        )

        market_data = {
            "stock_price": new_price,
            "prev_stock_price": current_price,
            "stock_return": stock_return,
            "bond_return": bond_return,
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
    """
    Base class for equity premium investors.

    Parameters from config extras:
        - initial_cash, initial_stock, custom_state_hot_limit, record_path
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["stock"] = extras["initial_stock"]
            self.state.custom_state["stock_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "stock"),
                entry_limit=custom_state_hot_limit,
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

    Parameters from config extras:
        - loss_aversion, evaluation_window, risk_aversion
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]
        stock_history = self.state.custom_state["stock_history"]
        cash = self.state.custom_state["cash"]
        stock = self.state.custom_state["stock"]

        loss_aversion = extras["loss_aversion"]
        evaluation_window = extras["evaluation_window"]
        risk_aversion = extras["risk_aversion"]
        strategy_name = self.__class__.__name__

        # Calculate recent volatility (myopic evaluation)
        if len(stock_history) >= evaluation_window:
            recent = list(stock_history)[-evaluation_window:]
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
        perceived_risk = vol * (1 + loss_aversion * loss_prob)

        # Target allocation based on perceived risk
        target_stock_pct = max(0.1, 0.5 - risk_aversion * perceived_risk)
        portfolio_value = cash + stock * stock_price
        target_stock_value = target_stock_pct * portfolio_value
        current_stock_value = stock * stock_price

        stock_qty = (target_stock_value - current_stock_value) / stock_price * 0.3
        stock_qty = max(-10, min(10, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        logger.debug(
            f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f} target_pct={target_stock_pct:.1%}"
        )
        return {
            "stock_qty": stock_qty,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": strategy_name},
                    "content_type": "investor_bid",
                }
            ],
        }


class LongHorizonInvestor(BaseInvestor):
    """
    Long-horizon investor - less myopic, accepts more risk.

    Parameters from config extras:
        - evaluation_window, target_stock_pct
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]
        cash = self.state.custom_state["cash"]
        stock = self.state.custom_state["stock"]

        target_stock_pct = extras["target_stock_pct"]
        strategy_name = self.__class__.__name__

        portfolio_value = cash + stock * stock_price
        target_stock_value = target_stock_pct * portfolio_value
        current_stock_value = stock * stock_price

        stock_qty = (target_stock_value - current_stock_value) / stock_price * 0.2
        stock_qty = max(-15, min(15, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        logger.debug(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")  # pylint: disable=logging-fstring-interpolation
        return {
            "stock_qty": stock_qty,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": strategy_name},
                    "content_type": "investor_bid",
                }
            ],
        }


class RiskNeutralInvestor(BaseInvestor):
    """
    Risk-neutral investor - theoretically optimal.

    Parameters from config extras:
        - excess_return_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]

        excess_return_multiplier = extras["excess_return_multiplier"]
        strategy_name = self.__class__.__name__

        # Expected excess return
        excess_return = market_data["stock_return"] - market_data["bond_return"]
        stock_qty = excess_return * excess_return_multiplier
        stock_qty = max(-20, min(20, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        logger.debug(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")  # pylint: disable=logging-fstring-interpolation
        return {
            "stock_qty": stock_qty,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": strategy_name},
                    "content_type": "investor_bid",
                }
            ],
        }


class ConservativeInvestor(BaseInvestor):
    """
    Conservative investor - prefers bonds.

    Parameters from config extras:
        - target_stock_pct
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]
        stock = self.state.custom_state["stock"]
        cash = self.state.custom_state["cash"]

        target_stock_pct = extras["target_stock_pct"]
        strategy_name = self.__class__.__name__

        portfolio_value = cash + stock * stock_price
        target_stock_value = target_stock_pct * portfolio_value
        current_stock_value = stock * stock_price

        stock_qty = (target_stock_value - current_stock_value) / stock_price * 0.1
        stock_qty = max(-5, min(5, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        logger.debug(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")  # pylint: disable=logging-fstring-interpolation
        return {
            "stock_qty": stock_qty,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": strategy_name},
                    "content_type": "investor_bid",
                }
            ],
        }


class NoiseTrader(BaseInvestor):
    """
    Noise trader with random allocation changes.

    Parameters from config extras:
        - noise_std
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        market_data = self.state.custom_state["market_data"]
        stock_price = market_data["stock_price"]

        noise_std = extras["noise_std"]
        strategy_name = self.__class__.__name__

        stock_qty = random.gauss(0, noise_std)
        stock_qty = max(-10, min(10, stock_qty))

        self._execute_trade(stock_qty, stock_price)

        logger.debug(f"[{self.identity:20s}] stock_qty={stock_qty:+6.2f}")  # pylint: disable=logging-fstring-interpolation
        return {
            "stock_qty": stock_qty,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {"stock_qty": stock_qty, "strategy": strategy_name},
                    "content_type": "investor_bid",
                }
            ],
        }


__all__ = [
    "Market",
    "BaseInvestor",
    "MyopicLossAverseInvestor",
    "LongHorizonInvestor",
    "RiskNeutralInvestor",
    "ConservativeInvestor",
    "NoiseTrader",
]
