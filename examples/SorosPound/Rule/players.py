"""SorosPound Rule-Based Simulation

1992 Black Wednesday — speculative attacks forced GBP exit from the ERM,
demonstrating self-fulfilling currency crises.

Theoretical Foundation:
- Obstfeld (1996): Models of currency crises with self-fulfilling features
- Eichengreen & Wyplosz (1993): The unstable EMS
- Soros (2003): The alchemy of finance

Key Dynamics:
- MacroHedgeFund: Builds massive short positions against currencies with unsustainable pegs
- PegDefender: Attempts to maintain currency peg through interest rate hikes and intervention
- ConvergenceTrader: Takes positions expecting the peg to hold, loses when it breaks
- OpportunisticTrader: Joins speculative attacks once they begin, amplifying selling pressure
- NoiseTrader: Random uninformed trader providing baseline liquidity

Parameters from config extras (see configs/SorosPound/Rule/players.yml).
"""

import logging
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("SorosPound")


# =============================================================================
# Market
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market for SorosPound simulation.

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
    Base class for rule-based SorosPound investors.

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
        return {"action": "hold", "quantity": 0}

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        strategy_name = self.__class__.__name__

        decision = self._make_decision()
        action = decision["action"]
        quantity = decision["quantity"]

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
            "quantity": quantity,
            "agent_type": strategy_name,
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


class MacroHedgeFund(BaseInvestor):
    """Macro speculative attacker.

    Theory: simulation-bases.md §4.1
    """

    def _make_decision(self) -> Dict[str, Any]:
        extras = self.config.extras
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(int(position), 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class PegDefender(BaseInvestor):
    """Peg defender.

    Theory: simulation-bases.md §4.2
    """

    def _make_decision(self) -> Dict[str, Any]:
        extras = self.config.extras
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(int(position), 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class ConvergenceTrader(BaseInvestor):
    """Convergence trader.

    Theory: simulation-bases.md §4.3
    """

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if random.random() < 0.3:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(int(position), 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}


class OpportunisticTrader(BaseInvestor):
    """Opportunistic attack follower.

    Theory: simulation-bases.md §4.4
    """

    def _make_decision(self) -> Dict[str, Any]:
        extras = self.config.extras
        price = self.state.custom_state["price"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(int(position), 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class NoiseTrader(BaseInvestor):
    """Noise trader.

    Theory: simulation-bases.md §4.5
    """

    def _make_decision(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if random.random() < 0.3:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(int(position), 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "BaseInvestor",
    "MacroHedgeFund",
    "PegDefender",
    "ConvergenceTrader",
    "OpportunisticTrader",
    "NoiseTrader",
]
