"""SunkCostFallacy Rule-Based Simulation

Sunk cost fallacy causes traders to continue investing based on past unrecoverable
costs rather than future prospects, leading to suboptimal capital allocation.

Theoretical Foundation:
- Arkes & Blumer (1985): The psychology of sunk cost
- Thaler (1980): Toward a positive theory of consumer choice
- Staw (1976): Knee-deep in the big muddy: A study of escalating commitment

Key Dynamics:
- SunkCostHolder: Holds losing positions because of prior investment, refuses to cut losses
- CommitmentEscalator: Doubles down on losing positions to justify prior commitment
- RationalCutter: Cuts losses based on forward-looking assessment, ignores past investment
- OpportunityCostTrader: Evaluates by opportunity cost, reallocates from underperformers
- NoiseTrader: Random uninformed trader providing baseline liquidity

Parameters from config extras (see configs/SunkCostFallacy/Rule/players.yml).
"""

import logging
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("SunkCostFallacy")


class Market(GeneralPlayer):
    """Market agent for SunkCostFallacy simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_history"] = []
            self.state.custom_state["volume_history"] = []
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload if hasattr(inb, "payload") else inb
                content_type = getattr(inb, "content_type", None)
                if (
                    isinstance(payload, dict)
                    and (
                        content_type == "investor_order"
                        or payload.get("type") == "order"
                        or "action" in payload
                    )
                ):
                    orders.append(payload)

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell

        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]
        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)
        new_price = max(price + price_change + reversion + noise, 0.01)
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(volume)
        logger.debug(
            "Round %d: price=%.2f fundamental=%.2f",
            round_num,
            new_price,
            fundamental,
        )

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0.0
        market_data = {
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
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
    """Base class for SunkCostFallacy investors."""

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "No configured sunk-cost or reallocation trigger fired.",
        }

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload if hasattr(inb, "payload") else inb
                if isinstance(market_data, dict) and "price" in market_data:
                    self.state.custom_state["price"] = market_data["price"]
                    self.state.custom_state["fundamental"] = market_data["fundamental"]
                    self.state.custom_state["deviation"] = market_data["deviation"]

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        decision = self._make_decision(price, fundamental, deviation)

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = int(decision["quantity"])
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
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


class SunkCostHolder(BaseInvestor):
    """Holds losing positions because of prior investment, refuses to cut losses.

    Theory: simulation-bases.md §4.1 — SunkCostHolder
    Theoretical basis: sunk cost escalation (Arkes & Blumer, 1985).
    See simulation-bases.md §4.1 for mathematical model.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        extras = self.config.extras
        hold_threshold = float(extras["hold_threshold"])
        base_size = int(extras["base_size"])

        if deviation > hold_threshold:
            qty = max(1, int(base_size * deviation / hold_threshold))
            buy_qty = min(qty, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {
                    "action": "buy",
                    "bid_price": price,
                    "quantity": buy_qty,
                    "reasoning": "Positive performance reinforces attachment to the prior investment.",
                }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Sunk-cost attachment prevents selling the losing position.",
        }


class CommitmentEscalator(BaseInvestor):
    """Doubles down on losing positions, increasing exposure to justify prior commitment.

    Theory: simulation-bases.md §4.2 — CommitmentEscalator
    Theoretical basis: escalation of commitment (Staw, 1976).
    See simulation-bases.md §4.2 for mathematical model.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        extras = self.config.extras
        threshold = float(extras["escalation_threshold"])
        escalation_size = int(extras["escalation_size"])

        if deviation < -threshold:
            qty = max(1, int(escalation_size * abs(deviation) / threshold))
            buy_qty = min(qty, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {
                    "action": "buy",
                    "bid_price": price,
                    "quantity": buy_qty,
                    "reasoning": "Escalation of commitment buys more after losses to average down.",
                }
        if deviation > threshold:
            qty = max(1, int(escalation_size * 0.5 * deviation / threshold))
            buy_qty = min(qty, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {
                    "action": "buy",
                    "bid_price": price,
                    "quantity": buy_qty,
                    "reasoning": "Prior commitment is reinforced by favorable price movement.",
                }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Commitment remains high but deviation is below escalation threshold.",
        }


class RationalCutter(BaseInvestor):
    """Cuts losses based on forward-looking assessment, ignores past investment.

    Theory: simulation-bases.md §4.3 — RationalCutter
    Theoretical basis: forward-looking rationality.
    See simulation-bases.md §4.3 for mathematical model.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        threshold = float(extras["cut_threshold"])
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
                        "reasoning": "Forward-looking value signal dominates sunk-cost emotions.",
                    }
            else:
                sell_qty = min(qty, int(position))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "bid_price": price,
                        "quantity": sell_qty,
                        "reasoning": "Forward-looking overvaluation signal justifies cutting exposure.",
                    }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Forward-looking signal is inside the rational cut band.",
        }


class OpportunityCostTrader(BaseInvestor):
    """Evaluates positions by opportunity cost, reallocates capital from underperformers.

    Theory: simulation-bases.md §4.4 — OpportunityCostTrader
    Theoretical basis: opportunity cost analysis.
    See simulation-bases.md §4.4 for mathematical model.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        threshold = float(extras["realloc_threshold"])
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
                        "reasoning": "Opportunity-cost screen reallocates capital into undervalued value.",
                    }
            else:
                sell_qty = min(qty, int(position))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "bid_price": price,
                        "quantity": sell_qty,
                        "reasoning": "Opportunity-cost screen reallocates away from overvalued exposure.",
                    }
        return {
            "action": "hold",
            "bid_price": price,
            "quantity": 0,
            "reasoning": "Current position remains acceptable relative to alternatives.",
        }


class NoiseTrader(BaseInvestor):
    """Random uninformed trader providing baseline liquidity.

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: noise-trader model.
    See simulation-bases.md §4.5 for mathematical model.
    """

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> Dict[str, Any]:
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
                qty = min(qty, int(position))
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
    "SunkCostHolder",
    "CommitmentEscalator",
    "RationalCutter",
    "OpportunityCostTrader",
    "NoiseTrader",
]
