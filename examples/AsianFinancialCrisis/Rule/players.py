"""AsianFinancialCrisis Rule-Based Simulation

1997 Asian financial crisis where currency collapses spread from Thailand
across East Asia through financial contagion.

Theoretical Foundation:
    - Radelet & Sachs (1998): The East Asian financial crisis - Diagnosis, remedies, prospects
    - Kaminsky & Reinhart (1999): The twin crises - Banking and balance-of-payments problems
    - Corsetti, Pesenti & Roubini (1999): Paper tigers? A model of the Asian crisis

Key Dynamics:
    - HotMoneyFunder: Provides short-term foreign currency loans that reverse rapidly at first
      sign of trouble (destabilizing)
    - ContagionTrader: Spreads crisis from one market to another through correlated selling
      across borders (destabilizing)
    - IMFRescuer: Provides emergency liquidity packages conditional on structural reforms
      (stabilizing)
    - ValueContrarian: Buys oversold regional assets when contagion pushes prices below
      fundamentals (stabilizing)
    - NoiseTrader: Random uninformed trader providing baseline liquidity (neutral)

Parameters from config (see configs/AsianFinancialCrisis/Rule/players.yml):
"""

import logging
import os
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("AsianFinancialCrisis")


class Market(GeneralPlayer):
    """
    Market coordinator for AsianFinancialCrisis simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
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
                order = inb.payload
                orders.append(order)
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]
        round_num = self.state.custom_state["round"]

        price_impact = self.state.custom_state["price_impact"]
        mean_reversion_rate = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        buy_orders = [o for o in orders if o.get("action") == "buy"]
        sell_orders = [o for o in orders if o.get("action") == "sell"]
        total_buy = sum(o.get("quantity", 0) for o in buy_orders)
        total_sell = sum(o.get("quantity", 0) for o in sell_orders)
        net_demand = total_buy - total_sell

        price_change = price_impact * net_demand
        reversion = mean_reversion_rate * (fundamental - price)
        noise = random.gauss(0, noise_std)
        new_price = max(price + price_change + reversion + noise, 0.01)

        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5
        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(volume)

        logger.debug(
            "Round %d: price=%.2f deviation=%.3f", round_num, new_price, deviation
        )

        market_data = {
            "price": new_price,
            "prev_price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "volume": volume,
            "round": round_num,
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_data"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class HotMoneyFunder(GeneralPlayer):
    """
    Provides short-term foreign currency loans that reverse rapidly at first sign of trouble.

    Theoretical Basis: Hot money reversal (Radelet & Sachs, 1998)
    Market Role: destabilizing

    Strategy:
        - When deviation > reversal_threshold (market rising): deploy buy_ratio of cash
        - When deviation < -reversal_threshold (market falling): sell sell_ratio of position
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
                self.state.custom_state["market_data"] = market_data

    async def decide(self) -> Dict[str, Any]:
        if "market_data" not in self.state.custom_state:
            order = {
                "action": "hold",
                "quantity": 0,
                "agent_type": self.__class__.__name__,
            }
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras

        reversal_threshold = extras["reversal_speed"]
        sell_ratio = extras["sell_ratio"]
        buy_ratio = extras["buy_ratio"]

        action = "hold"
        quantity = 0

        if deviation < -reversal_threshold:
            sell_qty = int(position * sell_ratio)
            if sell_qty > 0:
                action = "sell"
                quantity = sell_qty
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity
        elif deviation > reversal_threshold:
            deploy_cash = cash * buy_ratio
            buy_qty = int(deploy_cash / price) if price > 0 else 0
            if buy_qty > 0:
                action = "buy"
                quantity = buy_qty
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity

        order = {
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
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class ContagionTrader(GeneralPlayer):
    """
    Spreads crisis from one market to another through correlated selling across borders.

    Theoretical Basis: Financial contagion (Kaminsky & Reinhart, 1999)
    Market Role: destabilizing

    Strategy:
        - Signal = contagion_weight * deviation + cross_border_sensitivity * return
        - When signal < contagion_threshold: sell sell_ratio of position
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
                self.state.custom_state["market_data"] = market_data

    async def decide(self) -> Dict[str, Any]:
        if "market_data" not in self.state.custom_state:
            order = {
                "action": "hold",
                "quantity": 0,
                "agent_type": self.__class__.__name__,
            }
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        prev_price = market_data["prev_price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras

        price_return = (price - prev_price) / prev_price if prev_price > 0 else 0.0
        contagion_weight = extras["contagion_weight"]
        cross_border_sensitivity = extras["cross_border_sensitivity"]
        contagion_threshold = extras["contagion_threshold"]
        sell_ratio = extras["sell_ratio"]

        signal = contagion_weight * deviation + cross_border_sensitivity * price_return

        action = "hold"
        quantity = 0

        if signal < contagion_threshold:
            sell_qty = int(position * sell_ratio)
            if sell_qty > 0:
                action = "sell"
                quantity = sell_qty
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity

        order = {
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
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class IMFRescuer(GeneralPlayer):
    """
    Provides emergency liquidity packages conditional on structural reforms.

    Theoretical Basis: International lender of last resort (Corsetti et al., 1999)
    Market Role: stabilizing

    Strategy:
        - When deviation < rescue_threshold (severely oversold): buy buy_ratio of cash
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
                self.state.custom_state["market_data"] = market_data

    async def decide(self) -> Dict[str, Any]:
        if "market_data" not in self.state.custom_state:
            order = {
                "action": "hold",
                "quantity": 0,
                "agent_type": self.__class__.__name__,
            }
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        extras = self.config.extras

        rescue_threshold = extras["rescue_threshold"]
        buy_ratio = extras["buy_ratio"]

        action = "hold"
        quantity = 0

        if deviation < rescue_threshold:
            deploy_cash = cash * buy_ratio
            buy_qty = int(deploy_cash / price) if price > 0 else 0
            if buy_qty > 0:
                action = "buy"
                quantity = buy_qty
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity

        order = {
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
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class ValueContrarian(GeneralPlayer):
    """
    Buys oversold regional assets when contagion pushes prices below fundamentals.

    Theoretical Basis: Contrarian crisis investing (Radelet & Sachs, 1998 baseline)
    Market Role: stabilizing

    Strategy:
        - When deviation < oversold_threshold: buy buy_ratio of cash
        - When deviation > overbought_threshold: sell sell_ratio of position
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
                self.state.custom_state["market_data"] = market_data

    async def decide(self) -> Dict[str, Any]:
        if "market_data" not in self.state.custom_state:
            order = {
                "action": "hold",
                "quantity": 0,
                "agent_type": self.__class__.__name__,
            }
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        deviation = market_data["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras

        oversold_threshold = extras["oversold_threshold"]
        overbought_threshold = extras["overbought_threshold"]
        buy_ratio = extras["buy_ratio"]
        sell_ratio = extras["sell_ratio"]

        action = "hold"
        quantity = 0

        if deviation < oversold_threshold:
            deploy_cash = cash * buy_ratio
            buy_qty = int(deploy_cash / price) if price > 0 else 0
            if buy_qty > 0:
                action = "buy"
                quantity = buy_qty
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
        elif deviation > overbought_threshold:
            sell_qty = int(position * sell_ratio)
            if sell_qty > 0:
                action = "sell"
                quantity = sell_qty
                self.state.custom_state["cash"] += quantity * price
                self.state.custom_state["position"] -= quantity

        order = {
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
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """
    Random uninformed trader providing baseline liquidity.

    Theoretical Basis: Noise trader model (Black, 1986)
    Market Role: neutral

    Strategy:
        - With probability trade_probability: randomly buy or sell a random quantity
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
                self.state.custom_state["market_data"] = market_data

    async def decide(self) -> Dict[str, Any]:
        if "market_data" not in self.state.custom_state:
            order = {
                "action": "hold",
                "quantity": 0,
                "agent_type": self.__class__.__name__,
            }
            return {
                **order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            }

        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras

        trade_probability = extras["trade_probability"]

        action = "hold"
        quantity = 0

        if random.random() < trade_probability:
            qty = random.randint(100, 500)
            chosen_action = "buy" if random.random() > 0.5 else "sell"
            if chosen_action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(int(position), 0))
            if qty > 0:
                action = chosen_action
                quantity = qty
                if action == "buy":
                    self.state.custom_state["cash"] -= quantity * price
                    self.state.custom_state["position"] += quantity
                else:
                    self.state.custom_state["cash"] += quantity * price
                    self.state.custom_state["position"] -= quantity

        order = {
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
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "HotMoneyFunder",
    "ContagionTrader",
    "IMFRescuer",
    "ValueContrarian",
    "NoiseTrader",
]
