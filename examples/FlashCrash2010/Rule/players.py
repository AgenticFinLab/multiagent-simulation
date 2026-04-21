"""FlashCrash2010 Rule-Based Simulation

This module implements the 2010 Flash Crash simulation with rule-based agents.

Theoretical Foundation:
- Kirilenko et al. (2017): HFT liquidity provision and withdrawal
- Biais, Foucault & Moinas (2015): Order book dynamics
- Brunnermeier & Pedersen (2005): Predatory trading

Key Dynamics:
1. HFT market makers provide liquidity with tight spreads normally
2. Under stress (rapid price moves), HFTs widen spreads or withdraw
3. Order book depth collapses, amplifying price impact
4. Stop-loss orders trigger, creating feedback loops
5. Fundamental traders eventually provide stability

Parameters from config (see configs/FlashCrash2010/Rule/players.yml):
- Market: price_impact, mean_reversion, noise_std, initial_price, fundamental_value
- HFTMarketMaker: normal_spread, stress_spread, inventory_limit, withdrawal_threshold
- MomentumChaser: lookback_window, entry_threshold, position_multiplier
- FundamentalTrader: value_trigger, order_size
- StopLossTrader: stop_percentage, position_size
- NoiseTrader: trade_probability, min_order, max_order
"""

import asyncio
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

    Where:
        - λ: Price impact coefficient (from config)
        - Depth(t): Dynamic order book depth (shrinks during stress)
        - γ: Mean reversion strength
        - F: Fundamental value
        - ε: Random noise

    Order Book Depth Dynamics:
        Depth(t) = BaseDepth × LiquidityFactor(t)
        LiquidityFactor = f(Spread, RecentVolatility, HFTParticipation)

    Key Features:
        - Bid-ask spread widens during stress
        - Market depth decreases during volatile periods
        - Trade-through protection at price limits
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            self._initialize_market_state()

        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()

    def _initialize_market_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["base_depth"] = extras["base_depth"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []
        self.state.custom_state["spread_history"] = []
        self.state.custom_state["hft_participation"] = []

        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]
        self.state.custom_state["stress_threshold"] = extras["stress_threshold"]

        logger.info(
            "Market initialized: price=%.2f, fundamental=%.2f",
            extras["initial_price"],
            extras["fundamental_value"],
        )

    def _extract_orders(self, observation: Observation) -> List[Dict[str, Any]]:
        orders = []
        for msg in observation.messages:
            if msg.get("type") == "order":
                orders.append(
                    {
                        "agent_id": msg.get("from"),
                        "action": msg.get("action"),
                        "quantity": msg.get("quantity"),
                        "agent_type": msg.get("agent_type"),
                    }
                )
        return orders

    def _clear_market(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        base_depth = self.state.custom_state["base_depth"]

        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]

        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_flow = total_buy - total_sell

        hft_orders = [o for o in orders if o.get("agent_type") == "hft"]
        hft_participation = len(hft_orders) / len(orders) if orders else 0
        self.state.custom_state["hft_participation"].append(hft_participation)

        recent_returns = self._calculate_recent_returns()
        volatility = (
            sum(abs(r) for r in recent_returns) / len(recent_returns)
            if recent_returns
            else 0
        )

        depth = self._calculate_dynamic_depth(base_depth, volatility, hft_participation)

        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        price_change = (price_impact * net_flow / depth) if depth > 0 else 0
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)

        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)

        spread = self._calculate_spread(volatility, hft_participation)
        bid = new_price * (1 - spread / 2)
        ask = new_price * (1 + spread / 2)

        volume = min(total_buy, total_sell) + abs(total_buy - total_sell) * 0.5

        return {
            "price": new_price,
            "bid": bid,
            "ask": ask,
            "spread": spread,
            "depth": depth,
            "volume": volume,
            "net_flow": net_flow,
            "hft_participation": hft_participation,
            "volatility": volatility,
        }

    def _calculate_recent_returns(self, window: int = 10) -> List[float]:
        history = self.state.custom_state["price_history"]
        if len(history) < 2:
            return []

        returns = []
        for i in range(1, min(window, len(history))):
            ret = (
                (history[-i] - history[-i - 1]) / history[-i - 1]
                if history[-i - 1] > 0
                else 0
            )
            returns.append(ret)
        return returns

    def _calculate_dynamic_depth(
        self,
        base_depth: float,
        volatility: float,
        hft_participation: float,
    ) -> float:
        stress_factor = 1.0

        if volatility > 0.01:
            stress_factor *= 0.5
        if volatility > 0.02:
            stress_factor *= 0.3
        if hft_participation < 0.3:
            stress_factor *= 0.5

        return base_depth * max(stress_factor, 0.1)

    def _calculate_spread(self, volatility: float, hft_participation: float) -> float:
        base_spread = 0.0001

        spread = base_spread + volatility * 0.5

        if hft_participation < 0.3:
            spread *= 3.0
        if volatility > 0.02:
            spread *= 5.0

        return min(spread, 0.05)

    def _update_state(self, market_result: Dict[str, Any]) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["bid"] = market_result["bid"]
        self.state.custom_state["ask"] = market_result["ask"]
        self.state.custom_state["spread"] = market_result["spread"]
        self.state.custom_state["depth"] = market_result["depth"]

        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])
        self.state.custom_state["spread_history"].append(market_result["spread"])

    def _log_market_state(self) -> None:
        price = self.state.custom_state["price"]
        spread = self.state.custom_state["spread"]
        depth = self.state.custom_state["depth"]
        hft_part = (
            self.state.custom_state["hft_participation"][-1]
            if self.state.custom_state.get("hft_participation")
            else 0
        )

        logger.debug(
            "Round %d: price=%.2f, spread=%.4f, depth=%.0f, hft=%.1f%%",
            self.state.custom_state["round"],
            price,
            spread,
            depth,
            hft_part * 100,
        )

    async def step(self) -> Action:
        price = self.state.custom_state["price"]
        bid = self.state.custom_state["bid"]
        ask = self.state.custom_state["ask"]
        fundamental = self.state.custom_state["fundamental"]
        spread = self.state.custom_state["spread"]
        depth = self.state.custom_state["depth"]

        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0

        market_update = {
            "type": "market_update",
            "price": price,
            "bid": bid,
            "ask": ask,
            "fundamental": fundamental,
            "deviation": deviation,
            "spread": spread,
            "depth": depth,
            "round": self.state.custom_state["round"],
        }

        return Action(
            action_type="market_broadcast",
            payload={
                "market_data": market_update,
                "outbound_messages": [
                    {"payload": market_update, "content_type": "market_update"}
                ],
            },
            source_id=self.identity,
        )


class HFTMarketMaker(GeneralPlayer):
    """
    High-frequency market maker providing liquidity via limit orders.

    Based on Kirilenko et al. (2017) findings about HFT behavior during flash crash.

    Normal Behavior:
        - Places limit orders on both sides of the book
        - Maintains tight spreads (0.01% of price)
        - Aims to earn spread while managing inventory

    Stress Behavior (Withdrawal):
        When price velocity > threshold OR inventory > limit:
        - Widens spread dramatically (0.5% of price)
        - May withdraw one side of the book
        - Reduces position size

    Parameters from config:
        - normal_spread: 0.0001 (0.01%)
        - stress_spread: 0.005 (0.5%)
        - inventory_limit: 1000 shares
        - withdrawal_threshold: 0.02 (2% price change)
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self._update_market_info(msg)

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["inventory"] = 0

        self.state.custom_state["normal_spread"] = extras["normal_spread"]
        self.state.custom_state["stress_spread"] = extras["stress_spread"]
        self.state.custom_state["inventory_limit"] = extras["inventory_limit"]
        self.state.custom_state["withdrawal_threshold"] = extras["withdrawal_threshold"]

        self.state.custom_state["price_history"] = []
        self.state.custom_state["spread"] = extras["normal_spread"]
        self.state.custom_state["active"] = True

        logger.info(
            "HFT Market Maker initialized: cash=%.2f, spread=%.4f",
            extras["initial_cash"],
            extras["normal_spread"],
        )

    def _update_market_info(self, msg: Dict[str, Any]) -> None:
        self.state.custom_state["price"] = msg.get("price")
        self.state.custom_state["fundamental"] = msg.get("fundamental")
        self.state.custom_state["market_spread"] = msg.get("spread")
        self.state.custom_state["depth"] = msg.get("depth")

        self.state.custom_state["price_history"].append(msg.get("price"))
        if len(self.state.custom_state["price_history"]) > 20:
            self.state.custom_state["price_history"].pop(0)

    def _calculate_price_velocity(self) -> float:
        history = self.state.custom_state["price_history"]
        if len(history) < 5:
            return 0.0

        recent = history[-5:]
        returns = []
        for i in range(1, len(recent)):
            if recent[i - 1] > 0:
                ret = (recent[i] - recent[i - 1]) / recent[i - 1]
                returns.append(abs(ret))

        return sum(returns) / len(returns) if returns else 0.0

    def _is_stressed(self) -> bool:
        velocity = self._calculate_price_velocity()
        inventory = abs(self.state.custom_state["inventory"])
        inventory_limit = self.state.custom_state["inventory_limit"]
        withdrawal_threshold = self.state.custom_state["withdrawal_threshold"]

        return velocity > withdrawal_threshold or inventory > inventory_limit

    async def step(self) -> Action:
        price = self.state.custom_state["price"]
        stressed = self._is_stressed()

        if stressed:
            spread = self.state.custom_state["stress_spread"]
            self.state.custom_state["active"] = False
        else:
            spread = self.state.custom_state["normal_spread"]
            self.state.custom_state["active"] = True

        self.state.custom_state["spread"] = spread

        bid_price = price * (1 - spread / 2)
        ask_price = price * (1 + spread / 2)

        if stressed:
            quantity = 100
        else:
            quantity = 500

        order = {
            "type": "order",
            "action": "market_making",
            "bid_price": bid_price,
            "ask_price": ask_price,
            "quantity": quantity,
            "agent_type": "hft",
            "spread": spread,
            "stressed": stressed,
        }

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class MomentumChaser(GeneralPlayer):
    """
    HFT momentum chaser accelerating price trends.

    Based on feedback trading models (De Long et al., 1990).

    Strategy:
        - Monitors short-term price velocity
        - Enters when velocity exceeds threshold
        - Position size proportional to velocity
        - Creates positive feedback loops

    Parameters from config:
        - lookback_window: 10 seconds/rounds
        - entry_threshold: 0.001 (0.1% move)
        - position_multiplier: 10000
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self._update_market_info(msg)

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]

        self.state.custom_state["lookback"] = extras["lookback_window"]
        self.state.custom_state["threshold"] = extras["entry_threshold"]
        self.state.custom_state["multiplier"] = extras["position_multiplier"]

        self.state.custom_state["price_history"] = []

        logger.info("Momentum Chaser initialized")

    def _update_market_info(self, msg: Dict[str, Any]) -> None:
        self.state.custom_state["price"] = msg.get("price")
        self.state.custom_state["fundamental"] = msg.get("fundamental")

        self.state.custom_state["price_history"].append(msg.get("price"))
        if (
            len(self.state.custom_state["price_history"])
            > self.state.custom_state["lookback"]
        ):
            self.state.custom_state["price_history"].pop(0)

    def _calculate_velocity(self) -> float:
        history = self.state.custom_state["price_history"]
        lookback = self.state.custom_state["lookback"]

        if len(history) < lookback:
            return 0.0

        recent = history[-lookback:]
        if recent[0] > 0:
            return (recent[-1] - recent[0]) / recent[0]
        return 0.0

    async def step(self) -> Action:
        velocity = self._calculate_velocity()
        threshold = self.state.custom_state["threshold"]
        multiplier = self.state.custom_state["multiplier"]

        if abs(velocity) > threshold:
            quantity = int(abs(velocity) * multiplier)
            quantity = min(quantity, 1000)

            action = "buy" if velocity > 0 else "sell"

            order = {
                "type": "order",
                "action": action,
                "quantity": quantity,
                "agent_type": "hft",
                "velocity": velocity,
            }
            return Action(
                action_type="order",
                payload={
                    "order": order,
                    "outbound_messages": [{"payload": order, "content_type": "order"}],
                },
                source_id=self.identity,
            )

        return Action(
            action_type="hold",
            payload={},
            source_id=self.identity,
        )


class FundamentalTrader(GeneralPlayer):
    """
    Value-based fundamental trader providing stabilizing force.

    Knows the true fundamental value and trades against deviations.

    Strategy:
        - Buy when price < fundamental × (1 - trigger)
        - Sell when price > fundamental × (1 + trigger)
        - Provides liquidity during extreme moves

    Parameters from config:
        - value_trigger: 0.05 (5% deviation)
        - order_size: 500 shares
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self._update_market_info(msg)

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["trigger"] = extras["value_trigger"]
        self.state.custom_state["order_size"] = extras["order_size"]

        logger.info("Fundamental Trader initialized")

    def _update_market_info(self, msg: Dict[str, Any]) -> None:
        self.state.custom_state["price"] = msg.get("price")
        self.state.custom_state["fundamental"] = msg.get("fundamental")

    async def step(self) -> Action:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        trigger = self.state.custom_state["trigger"]
        order_size = self.state.custom_state["order_size"]

        if fundamental <= 0:
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        deviation = (price - fundamental) / fundamental

        if deviation < -trigger:
            order = {
                "type": "order",
                "action": "buy",
                "quantity": order_size,
                "agent_type": "fundamental",
                "deviation": deviation,
            }
            return Action(
                action_type="order",
                payload={
                    "order": order,
                    "outbound_messages": [{"payload": order, "content_type": "order"}],
                },
                source_id=self.identity,
            )

        if deviation > trigger:
            order = {
                "type": "order",
                "action": "sell",
                "quantity": order_size,
                "agent_type": "fundamental",
                "deviation": deviation,
            }
            return Action(
                action_type="order",
                payload={
                    "order": order,
                    "outbound_messages": [{"payload": order, "content_type": "order"}],
                },
                source_id=self.identity,
            )

        return Action(
            action_type="hold",
            payload={},
            source_id=self.identity,
        )


class StopLossTrader(GeneralPlayer):
    """
    Trader with stop-loss orders creating magnet effects.

    Based on predatory trading theory (Brunnermeier & Pedersen, 2005).

    Strategy:
        - Holds initial position at entry price
        - Places stop-loss at entry × (1 - stop_percentage)
        - When triggered, converts to market order
        - Creates cascading effect when many stops cluster

    Parameters from config:
        - stop_percentage: 0.03 (3% stop)
        - position_size: 1000 shares
        - entry_price: $40.00
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self._update_market_info(msg)

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["entry_price"] = extras["entry_price"]
        self.state.custom_state["stop_pct"] = extras["stop_percentage"]
        self.state.custom_state["position_size"] = extras["position_size"]
        self.state.custom_state["stopped"] = False

        stop_level = extras["entry_price"] * (1 - extras["stop_percentage"])
        self.state.custom_state["stop_level"] = stop_level

        logger.info(
            "Stop-Loss Trader initialized: entry=%.2f, stop=%.2f",
            extras["entry_price"],
            stop_level,
        )

    def _update_market_info(self, msg: Dict[str, Any]) -> None:
        self.state.custom_state["price"] = msg.get("price")

    async def step(self) -> Action:
        if self.state.custom_state["stopped"]:
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        price = self.state.custom_state["price"]
        stop_level = self.state.custom_state["stop_level"]
        position_size = self.state.custom_state["position_size"]

        if price <= stop_level:
            self.state.custom_state["stopped"] = True

            order = {
                "type": "order",
                "action": "sell",
                "quantity": position_size,
                "agent_type": "stoploss",
                "triggered": True,
                "stop_level": stop_level,
            }

            logger.warning(
                "Stop-loss triggered at %.2f (stop level: %.2f)",
                price,
                stop_level,
            )

            return Action(
                action_type="order",
                payload={
                    "order": order,
                    "outbound_messages": [{"payload": order, "content_type": "order"}],
                },
                source_id=self.identity,
            )

        return Action(
            action_type="hold",
            payload={},
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """
    Uninformed noise trader creating background activity.

    Based on Black (1986) - noise makes markets possible.

    Strategy:
        - Randomly buys or sells with fixed probability
        - Represents uninformed order flow
        - Creates trading opportunities for informed agents

    Parameters from config:
        - trade_probability: 0.05 (5% per round)
        - min_order: 100 shares
        - max_order: 500 shares
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["prob"] = extras["trade_probability"]
        self.state.custom_state["min_order"] = extras["min_order"]
        self.state.custom_state["max_order"] = extras["max_order"]

        logger.info("Noise Trader initialized")

    async def step(self) -> Action:
        prob = self.state.custom_state["prob"]

        if random.random() > prob:
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        min_order = self.state.custom_state["min_order"]
        max_order = self.state.custom_state["max_order"]
        quantity = random.randint(min_order, max_order)

        action = "buy" if random.random() > 0.5 else "sell"

        order = {
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": "noise",
        }

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )
