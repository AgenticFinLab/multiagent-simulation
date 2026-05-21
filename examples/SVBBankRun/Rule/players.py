"""SVBBankRun Rule-Based Simulation

March 2023 SVB collapse — $42B deposit outflow in one day triggered by social media panic.

Theoretical Foundation:
- Diamond & Dybvig (1983): Bank runs, deposit insurance, and liquidity
- Iyer & Puri (2012): Social networks in bank runs
- Duffie et al. (2023): SVB failure analysis

Key Dynamics:
- Depositor: Withdraws deposits when bank health deteriorates
- SocialMediaInfluencer: Amplifies panic signals to accelerate bank run
- BankManager: Manages duration risk and attempts to stabilize
- Regulator: May intervene with guarantees or liquidity support
- BondTrader: Trades bonds based on interest rate expectations

Parameters from config extras (see configs/SVBBankRun/Rule/players.yml).
"""

import logging
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("SVBBankRun")


# =============================================================================
# Market
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market for SVBBankRun simulation.

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
            "[Market] R%d  P=%.2f→%.2f  Dev=%+.2f%%  Buy=%d  Sell=%d",
            round_num,
            price,
            new_price,
            deviation * 100,
            total_buy,
            total_sell,
        )

        market_data = {
            "price": new_price,
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
# Base Rule-Based Investor
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """
    Base class for rule-based SVBBankRun participants.

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
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
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


class Depositor(BaseInvestor):
    """Depositor who exits the bank-health proxy when health deteriorates.

    Theory: simulation-bases.md §4.1 — Depositor
    Theoretical basis: Diamond and Dybvig (1983) coordination-run logic.
    See simulation-bases.md §4.1 for the proxy withdrawal model.

    Parameters from config extras:
        - withdrawal_threshold, social_influence
    """

    def _make_decision(self) -> Dict[str, Any]:
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        position = self.state.custom_state["position"]
        withdrawal_threshold = extras["withdrawal_threshold"]

        if deviation < -withdrawal_threshold:
            sell_qty = min(1000, max(int(position), 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class SocialMediaInfluencer(BaseInvestor):
    """Social media amplifier that converts weak stress signals into sell pressure.

    Theory: simulation-bases.md §4.2 — SocialMediaInfluencer
    Theoretical basis: information cascade and social-contagion amplification.
    See simulation-bases.md §4.2 for the amplification model.

    Parameters from config extras:
        - amplification_factor
    """

    def _make_decision(self) -> Dict[str, Any]:
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        position = self.state.custom_state["position"]
        amplification = extras["amplification_factor"]

        if deviation < -0.05:
            sell_qty = min(
                int(abs(deviation) * amplification * 2000), max(int(position), 0)
            )
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


class BankManager(BaseInvestor):
    """Bank manager who supports the proxy market when duration stress appears.

    Theory: simulation-bases.md §4.3 — BankManager
    Theoretical basis: asset-liability duration mismatch and stabilization.
    See simulation-bases.md §4.3 for the support rule.

    Parameters from config extras:
        - duration_gap
    """

    def _make_decision(self) -> Dict[str, Any]:
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        extras["duration_gap"]

        if deviation < -0.05:
            buy_qty = min(500, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}


class Regulator(BaseInvestor):
    """Regulator who may provide lender-of-last-resort proxy support.

    Theory: simulation-bases.md §4.4 — Regulator
    Theoretical basis: deposit guarantees and lender-of-last-resort policy.
    See simulation-bases.md §4.4 for the intervention rule.

    Parameters from config extras:
        - intervention_threshold, guarantee_probability
    """

    def _make_decision(self) -> Dict[str, Any]:
        extras = self.config.extras
        deviation = self.state.custom_state["deviation"]
        intervention_threshold = extras["intervention_threshold"]
        guarantee_prob = extras["guarantee_probability"]

        if deviation < -intervention_threshold and random.random() < guarantee_prob:
            return {"action": "buy", "quantity": 2000}
        return {"action": "hold", "quantity": 0}


class BondTrader(BaseInvestor):
    """Bond trader who reprices bank exposure from duration-loss signals.

    Theory: simulation-bases.md §4.5 — BondTrader
    Theoretical basis: fixed-income duration and mark-to-market losses.
    See simulation-bases.md §4.5 for the bond-loss pressure rule.

    Parameters from config extras: (none specific)
    """

    def _make_decision(self) -> Dict[str, Any]:
        deviation = self.state.custom_state["deviation"]
        price = self.state.custom_state["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if abs(deviation) > 0.03:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, int(position))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "BaseInvestor",
    "Depositor",
    "SocialMediaInfluencer",
    "BankManager",
    "Regulator",
    "BondTrader",
]
