"""FlashCrash2010 Rule-Based Simulation

Phenomenon: 2010 Flash Crash
    - Extreme rapid price decline (9% in 36 minutes on May 6, 2010)
    - HFT market makers withdraw liquidity under stress
    - Order book depth collapses, amplifying price impact
    - Stop-loss cascades create feedback selling
    - Fundamental traders eventually stabilize price

Key Mechanism:
    1. Initial selling pressure (large institutional sell order)
    2. HFT market makers detect stress, widen spreads then withdraw
    3. Order book depth collapses → price impact amplified
    4. MomentumChasers accelerate the trend
    5. Stop-loss orders trigger in cascade
    6. Fundamental traders recognize undervaluation, buy aggressively
    7. Price recovers rapidly

All parameters are configured via players.yml config file.
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("FlashCrash2010")


class Market(GeneralPlayer):
    """
    Order book market with dynamic depth and spread.

    Price Formation Model:
        P(t+1) = P(t) + λ × NetOrderFlow / Depth(t) + γ × (F - P(t)) + ε

    Parameters from config extras:
        - initial_price, fundamental_value, base_depth
        - price_impact, mean_reversion, noise_std, stress_threshold
        - custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        import os

        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = float(extras["initial_price"])
            self.state.custom_state["fundamental"] = float(extras["fundamental_value"])
            self.state.custom_state["base_depth"] = float(extras["base_depth"])
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=hot_limit,
            )

        orders: List[Dict] = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict) and "quantity" in payload:
                    orders.append(payload)
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        import os

        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        base_depth = self.state.custom_state["base_depth"]
        orders = self.state.custom_state["orders"]

        price_impact = float(extras["price_impact"])
        mean_reversion = float(extras["mean_reversion"])
        noise_std = float(extras["noise_std"])

        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = abs(sum(o["quantity"] for o in sell_orders))
        net_flow = total_buy - total_sell
        volume = total_buy + total_sell

        hft_orders = [o for o in orders if o.get("agent_type") == "hft"]
        hft_participation = len(hft_orders) / max(len(orders), 1)

        price_hist = list(self.state.custom_state["price_history"])
        if len(price_hist) >= 2:
            recent = price_hist[-min(10, len(price_hist)) :]
            rets = [
                (recent[i] - recent[i - 1]) / recent[i - 1]
                for i in range(1, len(recent))
                if recent[i - 1] > 0
            ]
            volatility = sum(abs(r) for r in rets) / max(len(rets), 1)
        else:
            volatility = 0.0

        stress_factor = 1.0
        if volatility > 0.01:
            stress_factor *= 0.5
        if volatility > 0.02:
            stress_factor *= 0.3
        if hft_participation < 0.3:
            stress_factor *= 0.5
        depth = base_depth * max(stress_factor, 0.1)

        price_change = (price_impact * net_flow / depth) if depth > 0 else 0
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)
        new_price = max(0.01, price + price_change + reversion + noise)

        base_spread = 0.0001
        spread = base_spread + volatility * 0.5
        if hft_participation < 0.3:
            spread *= 3.0
        if volatility > 0.02:
            spread *= 5.0
        spread = min(spread, 0.05)

        self.state.custom_state["price"] = new_price
        self.state.custom_state["spread"] = spread
        self.state.custom_state["depth"] = depth
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(volume)

        price_return = (new_price - price) / price
        logger.debug(
            "[Market] R%d  P=%.2f→%.2f (%+.2f%%)  Depth=%.0f  Vol=%.4f  HFT=%.1f%%",
            round_num,
            price,
            new_price,
            price_return * 100,
            depth,
            volatility,
            hft_participation * 100,
        )

        market_data = {
            "price": new_price,
            "prev_price": price,
            "return_pct": price_return * 100,
            "fundamental": fundamental,
            "deviation": (new_price - fundamental) / fundamental,
            "spread": spread,
            "depth": depth,
            "volume": volume,
            "volatility": volatility,
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


class HFTMarketMaker(GeneralPlayer):
    """
    HFT market maker with liquidity withdrawal under stress.

    Theory: simulation-bases.md §4.1 — HFTMarketMaker
    Theoretical basis: Kirilenko et al. (2017) HFT market maker stress response;
    rapid spread widening and withdrawal when volatility exceeds threshold
    creates a self-reinforcing liquidity vacuum during the 2010 flash crash.
    See simulation-bases.md §4.1 for mathematical model.

    Parameters from config extras:
        - initial_cash, initial_position, normal_spread, stress_spread,
          inventory_limit, withdrawal_threshold, custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        import os

        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]

        withdrawal_threshold = float(extras["withdrawal_threshold"])
        normal_spread = float(extras["normal_spread"])
        stress_spread = float(extras["stress_spread"])

        price_hist = list(self.state.custom_state["price_history"])
        if len(price_hist) >= 5:
            recent = price_hist[-5:]
            rets = [
                abs((recent[i] - recent[i - 1]) / recent[i - 1])
                for i in range(1, len(recent))
                if recent[i - 1] > 0
            ]
            velocity = sum(rets) / max(len(rets), 1)
        else:
            velocity = 0.0

        stressed = velocity > withdrawal_threshold
        spread = stress_spread if stressed else normal_spread
        quantity = 100 if stressed else 500

        if not stressed:
            # Provide liquidity: buy/sell around mid
            order = {
                "quantity": quantity,
                "bid_price": price,
                "strategy": "HFTMarketMaker",
                "agent_type": "hft",
                "spread": spread,
                "stressed": stressed,
                "provides_liquidity": not stressed,
            }
        else:
            # Withdraw
            order = {
                "quantity": 0,
                "bid_price": price,
                "strategy": "HFTMarketMaker",
                "agent_type": "hft",
                "spread": spread,
                "stressed": stressed,
                "provides_liquidity": False,
            }

        logger.debug(
            "[HFTMarketMaker %s] R%d stressed=%s vel=%.4f Q=%+d",
            self.identity,
            round_num,
            stressed,
            velocity,
            order["quantity"],
        )
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


class MomentumChaser(GeneralPlayer):
    """
    HFT momentum chaser - trend-following, amplifies moves.

    Theory: simulation-bases.md §4.2 — MomentumChaser
    Theoretical basis: Positive-feedback trading amplifies directional price
    moves; velocity threshold determines entry, position size scaled by momentum.
    See simulation-bases.md §4.2 for mathematical model.

    Parameters from config extras:
        - initial_cash, initial_position, lookback_window, entry_threshold,
          position_multiplier, custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        import os

        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]

        lookback = int(extras["lookback_window"])
        threshold = float(extras["entry_threshold"])
        multiplier = float(extras["position_multiplier"])

        price_hist = list(self.state.custom_state["price_history"])
        if len(price_hist) >= lookback:
            recent = price_hist[-lookback:]
            velocity = (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0.0
        else:
            velocity = 0.0

        if abs(velocity) > threshold:
            quantity = int(min(abs(velocity) * multiplier, 1000))
            quantity = quantity if velocity > 0 else -quantity
        else:
            quantity = 0

        # Apply constraints
        if quantity > 0:
            max_buy = int(self.state.custom_state["cash"] / price) if price > 0 else 0
            quantity = min(quantity, max_buy)
        elif quantity < 0:
            quantity = max(quantity, -self.state.custom_state["position"])

        if quantity != 0:
            if quantity > 0:
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
            else:
                self.state.custom_state["cash"] += abs(quantity) * price
                self.state.custom_state["position"] += quantity

        order = {
            "quantity": quantity,
            "bid_price": price,
            "strategy": "MomentumChaser",
            "agent_type": "hft",
            "provides_liquidity": False,
        }

        logger.debug(
            "[MomentumChaser %s] R%d vel=%.4f Q=%+d",
            self.identity,
            round_num,
            velocity,
            quantity,
        )
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


class FundamentalTrader(GeneralPlayer):
    """
    Value-based fundamental trader - stabilizing force.

    Theory: simulation-bases.md §4.3 — FundamentalTrader
    Theoretical basis: Shiller (1981) excess volatility; fundamental traders
    recognize undervaluation and buy aggressively, providing the recovery force.
    See simulation-bases.md §4.3 for mathematical model.

    Parameters from config extras:
        - initial_cash, initial_position, value_trigger, order_size,
          custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        import os

        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        fundamental = market_data["fundamental"]

        trigger = float(extras["value_trigger"])
        order_size = int(extras["order_size"])

        if fundamental <= 0:
            quantity = 0
        else:
            deviation = (price - fundamental) / fundamental
            if deviation < -trigger:
                quantity = min(
                    order_size,
                    int(self.state.custom_state["cash"] / price) if price > 0 else 0,
                )
            elif deviation > trigger:
                quantity = -min(order_size, self.state.custom_state["position"])
            else:
                quantity = 0

        if quantity != 0:
            if quantity > 0:
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
            else:
                self.state.custom_state["cash"] += abs(quantity) * price
                self.state.custom_state["position"] += quantity

        order = {
            "quantity": quantity,
            "bid_price": price,
            "strategy": "FundamentalTrader",
            "agent_type": "fundamental",
            "provides_liquidity": True,
        }

        logger.debug(
            "[FundamentalTrader %s] R%d Q=%+d",
            self.identity,
            round_num,
            quantity,
        )
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


class StopLossTrader(GeneralPlayer):
    """
    Trader with stop-loss orders - creates cascade selling.

    Theory: simulation-bases.md §4.4 — StopLossTrader
    Theoretical basis: Stop-loss cascade mechanism; fixed stop levels trigger
    correlated market sells that accelerate the crash once momentum begins.
    See simulation-bases.md §4.4 for mathematical model.

    Parameters from config extras:
        - initial_cash, initial_position, stop_percentage, position_size, entry_price,
          custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        import os

        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            entry_price = float(extras["entry_price"])
            stop_pct = float(extras["stop_percentage"])
            self.state.custom_state["stop_level"] = entry_price * (1 - stop_pct)
            self.state.custom_state["stopped"] = False
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]

        stop_level = self.state.custom_state["stop_level"]
        stopped = self.state.custom_state["stopped"]
        position = self.state.custom_state["position"]

        if stopped or position <= 0:
            quantity = 0
        elif price <= stop_level:
            quantity = -position
            self.state.custom_state["stopped"] = True
            logger.warning(
                "[StopLoss %s] R%d TRIGGERED at %.2f (stop=%.2f)",
                self.identity,
                round_num,
                price,
                stop_level,
            )
        else:
            quantity = 0

        if quantity != 0:
            self.state.custom_state["cash"] += abs(quantity) * price
            self.state.custom_state["position"] += quantity

        order = {
            "quantity": quantity,
            "bid_price": price,
            "strategy": "StopLossTrader",
            "agent_type": "stoploss",
            "provides_liquidity": False,
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


class NoiseTrader(GeneralPlayer):
    """
    Uninformed noise trader - random background activity.

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: Black (1986) noise trader model; random trading provides
    background volume and prevents market microstructure from being trivial.
    See simulation-bases.md §4.5 for mathematical model.

    Parameters from config extras:
        - initial_cash, initial_position, trade_probability, min_order, max_order,
          custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        import os

        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]

        prob = float(extras["trade_probability"])
        min_order = int(extras["min_order"])
        max_order = int(extras["max_order"])

        if random.random() > prob:
            quantity = 0
        else:
            size = random.randint(min_order, max_order)
            quantity = size if random.random() > 0.5 else -size

        if quantity > 0:
            max_buy = int(self.state.custom_state["cash"] / price) if price > 0 else 0
            quantity = min(quantity, max_buy)
        elif quantity < 0:
            quantity = max(quantity, -self.state.custom_state["position"])

        if quantity != 0:
            if quantity > 0:
                self.state.custom_state["cash"] -= quantity * price
                self.state.custom_state["position"] += quantity
            else:
                self.state.custom_state["cash"] += abs(quantity) * price
                self.state.custom_state["position"] += quantity

        order = {
            "quantity": quantity,
            "bid_price": price,
            "strategy": "NoiseTrader",
            "agent_type": "noise",
            "provides_liquidity": False,
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


__all__ = [
    "Market",
    "HFTMarketMaker",
    "MomentumChaser",
    "FundamentalTrader",
    "StopLossTrader",
    "NoiseTrader",
]
