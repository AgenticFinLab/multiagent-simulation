"""StatusQuoBias Rule-Based Simulation

Status quo bias causes traders to prefer inaction and maintain current positions
despite new information, leading to suboptimal portfolio responses.

Theoretical Foundation:
- Samuelson & Zeckhauser (1988): Status quo bias in decision making
- Kahneman, Knetsch & Thaler (1991): The endowment effect, loss aversion, and status quo bias
- Fernandez & Rodrik (1991): Resistance to reform — status quo bias with individual-specific uncertainty

Key Dynamics:
- InertialHolder: Strongly prefers maintaining current portfolio; requires overwhelming evidence to change
- DefaultFollower: Follows default allocation suggestions, avoids active decisions
- ActiveRebalancer: Proactively adjusts positions based on new information
- MomentumTrader: Trades on price trends, naturally overcoming status quo inertia
- NoiseTrader: Random uninformed trader providing baseline liquidity

Parameters from config extras (see configs/StatusQuoBias/Rule/players.yml).
"""

import logging
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("StatusQuoBias")


# =============================================================================
# Market
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market for StatusQuoBias simulation.

    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε

    Parameters from config extras:
        - initial_price, fundamental_value
        - price_impact, mean_reversion, noise_std
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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_history"] = []
            self.state.custom_state["volume_history"] = []

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "agent_id": inb.sender_id,
                        "action": order["action"],
                        "quantity": order["quantity"],
                        "agent_type": order["agent_type"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]

        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell

        price_change = extras["price_impact"] * net_demand
        reversion = extras["mean_reversion"] * (fundamental - price)
        noise = random.gauss(0, extras["noise_std"])

        new_price = max(0.01, price + price_change + reversion + noise)
        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(volume)

        logger.debug(
            "[Market] R%d  P=%.2f→%.2f  Dev=%+.2f%%  Net=%+.0f",
            round_num,
            price,
            new_price,
            deviation * 100,
            net_demand,
        )

        market_data = {
            "price": new_price,
            "prev_price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": round_num,
            "volume": volume,
            "net_demand": net_demand,
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


# =============================================================================
# Base Rule Investor
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """
    Base class for rule-based StatusQuoBias investors.

    Parameters from config extras:
        - initial_cash, initial_position
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
                market_data = inb.payload
                self.state.custom_state["price"] = market_data["price"]
                self.state.custom_state["fundamental"] = market_data["fundamental"]
                self.state.custom_state["deviation"] = market_data["deviation"]

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "No configured signal crossed this investor's action threshold.",
        }

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        strategy_name = self.__class__.__name__

        decision = self._make_decision()
        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = int(decision["quantity"])

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        logger.debug(
            "[%-25s] R%d (%s): action=%s qty=%d | Cash=%.2f Pos=%d",
            self.identity,
            self.state.custom_state["round"],
            strategy_name,
            action,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "agent_type": strategy_name,
            "reasoning": str(decision["reasoning"])[:120],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Concrete Agent Types
# =============================================================================


class InertialHolder(BaseInvestor):
    """
    Strongly prefers maintaining current portfolio; requires overwhelming evidence to change.

    Theory: simulation-bases.md §4.1 — InertialHolder
    Theoretical basis: decision inertia (Samuelson & Zeckhauser, 1988).
    See simulation-bases.md §4.1 for mathematical model.

    Parameters from config extras:
        - inertia_strength, change_threshold
    """

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        extras = self.config.extras
        threshold = float(extras["change_threshold"])
        base_size = int(extras["base_size"])
        inertia_strength = float(extras["inertia_strength"])

        if abs(deviation) > threshold:
            qty = max(1, int(base_size * abs(deviation) / threshold * (1.0 - inertia_strength + 0.1)))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "bid_price": price,
                        "quantity": buy_qty,
                        "reasoning": "Large undervaluation finally overcame status quo inertia.",
                    }
            else:
                sell_qty = min(qty, max(int(position), 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "bid_price": price,
                        "quantity": sell_qty,
                        "reasoning": "Large overvaluation finally overcame status quo inertia.",
                    }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Status quo inertia dominates a signal below the change threshold.",
        }


class DefaultFollower(BaseInvestor):
    """
    Follows default allocation suggestions, avoids active decisions.

    Theory: simulation-bases.md §4.2 — DefaultFollower
    Theoretical basis: default bias and decision avoidance.
    See simulation-bases.md §4.2 for mathematical model.

    Parameters from config extras:
        - default_weight, active_deviation
    """

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        extras = self.config.extras
        threshold = float(extras["active_deviation"])
        default_weight = float(extras["default_weight"])
        base_size = int(extras["base_size"])

        if abs(deviation) > threshold:
            qty = max(1, int(base_size * abs(deviation) / threshold * max(default_weight, 0.1)))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "bid_price": price,
                        "quantity": buy_qty,
                        "reasoning": "Default allocation drift is large enough to justify buying undervalued shares.",
                    }
            else:
                sell_qty = min(qty, max(int(position), 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "bid_price": price,
                        "quantity": sell_qty,
                        "reasoning": "Default allocation drift is large enough to justify trimming overvalued shares.",
                    }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Default-following keeps the current allocation when drift is moderate.",
        }


class ActiveRebalancer(BaseInvestor):
    """
    Proactively adjusts positions based on new information regardless of current holdings.

    Theory: simulation-bases.md §4.3 — ActiveRebalancer
    Theoretical basis: rational portfolio rebalancing benchmark.
    See simulation-bases.md §4.3 for mathematical model.

    Parameters from config extras:
        - rebalance_threshold, position_size
    """

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        extras = self.config.extras
        threshold = float(extras["rebalance_threshold"])
        position_size = int(extras["position_size"])

        if abs(deviation) > threshold:
            qty = max(1, int(position_size * abs(deviation) / threshold))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "bid_price": price,
                        "quantity": buy_qty,
                        "reasoning": "Active rebalancing buys when price is below fundamental value.",
                    }
            else:
                sell_qty = min(qty, max(int(position), 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "bid_price": price,
                        "quantity": sell_qty,
                        "reasoning": "Active rebalancing sells when price exceeds fundamental value.",
                    }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Deviation is inside the active rebalancing band.",
        }


class MomentumTrader(BaseInvestor):
    """
    Trades on price trends, naturally overcoming status quo inertia.

    Theory: simulation-bases.md §4.4 — MomentumTrader
    Theoretical basis: momentum-based trading.
    See simulation-bases.md §4.4 for mathematical model.

    Parameters from config extras:
        - lookback, entry_threshold
    """

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        extras = self.config.extras
        entry_threshold = float(extras["entry_threshold"])
        position_size = int(extras["position_size"])

        if abs(deviation) > entry_threshold:
            qty = max(1, int(position_size * abs(deviation) / entry_threshold))
            action = "buy" if deviation > 0 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(int(position), 0))
            if qty > 0:
                return {
                    "action": action,
                    "bid_price": price,
                    "quantity": qty,
                    "reasoning": "Trend-sensitive momentum rule follows the current price deviation.",
                }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Momentum signal is below the entry threshold.",
        }


class NoiseTrader(BaseInvestor):
    """
    Random uninformed trader providing baseline liquidity.

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: noise-trader model.
    See simulation-bases.md §4.5 for mathematical model.

    Parameters from config extras:
        - trade_probability
    """

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        extras = self.config.extras
        trade_probability = float(extras["trade_probability"])
        noise_size = int(extras["noise_size"])

        if random.random() < trade_probability:
            qty = random.randint(1, noise_size)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(int(position), 0))
            if qty > 0:
                return {
                    "action": action,
                    "bid_price": price,
                    "quantity": qty,
                    "reasoning": "Random noise-trader liquidity order.",
                }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Noise trader did not activate this round.",
        }


__all__ = [
    "Market",
    "BaseInvestor",
    "InertialHolder",
    "DefaultFollower",
    "ActiveRebalancer",
    "MomentumTrader",
    "NoiseTrader",
]
