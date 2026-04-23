"""MarketCrash - Rule-based Market Crash Simulation

Phenomenon: Market Crash
    Rapid price decline with liquidity evaporation, triggered by
    forced deleveraging and liquidity spiral dynamics.

Theoretical Foundation:
    - Minsky Moment: Sudden shift from stability to instability
    - Liquidity Spiral (Brunnermeier & Pedersen, 2009)
    - Fire Sales: Forced selling creates additional price pressure

Key Crash Dynamics:
    1. Initial shock → Price drops
    2. Volatility rises → Risk parity funds reduce exposure
    3. Leveraged funds hit margin → Forced liquidation
    4. Market makers withdraw → Liquidity evaporates
    5. Panic sellers add pressure → Crash accelerates
    6. Bottom fishers provide eventual floor

All parameters are configured via players.yml config file.
"""

import logging
import os
import random
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("MarketCrash")


class Market(GeneralPlayer):
    """
    Central market with liquidity-sensitive pricing.

    Price Model:
        P(t+1) = P(t) + λ(L) × NetDemand + γ × [F - P(t)] + σ × ε

    Parameters from config extras:
        - fundamental_value, initial_price
        - base_price_impact, mean_reversion, noise_std
        - liquidity_decay, liquidity_recovery, min_liquidity
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
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["liquidity"] = 1.0  # Normalized liquidity
            self.state.custom_state["volatility"] = 1.0
            self.state.custom_state["prev_return"] = 0.0

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=custom_state_hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],
                        "quantity": order["quantity"],
                        "strategy": order["strategy"],
                        "is_market_maker": order["is_market_maker"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        current_liquidity = self.state.custom_state["liquidity"]
        prev_return = self.state.custom_state["prev_return"]
        orders = self.state.custom_state["orders"]

        fundamental_value = extras["fundamental_value"]
        base_price_impact = extras["base_price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        noise_std = extras["noise_std"]
        liquidity_decay = extras["liquidity_decay"]
        liquidity_recovery = extras["liquidity_recovery"]
        min_liquidity = extras["min_liquidity"]

        # Calculate market maker participation (affects liquidity)
        mm_orders = [o for o in orders if o["is_market_maker"]]

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Update volatility (simplified EWMA)
        new_volatility = (
            0.9 * self.state.custom_state["volatility"] + 0.1 * abs(prev_return) * 100
        )
        new_volatility = max(0.5, min(20.0, new_volatility))

        # Update liquidity based on market maker presence and volatility
        mm_liquidity_supply = sum(abs(o["quantity"]) for o in mm_orders)
        liquidity_supply_effect = mm_liquidity_supply / 50.0  # Normalized

        # Liquidity decreases with volatility, increases with MM presence
        liquidity_change = (
            -liquidity_decay * (new_volatility / 5.0)  # High vol drains liquidity
            + liquidity_recovery * liquidity_supply_effect  # MMs add liquidity
            + 0.02  # Natural recovery
        )
        new_liquidity = current_liquidity + liquidity_change
        new_liquidity = max(min_liquidity, min(1.0, new_liquidity))

        # Price impact inversely proportional to liquidity (crash mechanism)
        adjusted_impact = base_price_impact / new_liquidity

        # Price dynamics
        price_impact = adjusted_impact * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        return_pct = price_return * 100

        # Detect crash conditions
        is_crash = price_return < -0.05 and new_liquidity < 0.5

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = new_liquidity
        self.state.custom_state["volatility"] = new_volatility
        self.state.custom_state["prev_return"] = price_return

        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["liquidity_history"].append(new_liquidity)
        self.state.custom_state["volatility_history"].append(new_volatility)

        # Log
        logger.debug(f"\n{'='*70}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"[Market] Round {round_num}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"  Liquidity: {current_liquidity:.2f} → {new_liquidity:.2f}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"  Volatility: {new_volatility:.2f}")  # pylint: disable=logging-fstring-interpolation
        if is_crash:
            logger.debug(f"  *** CRASH CONDITIONS DETECTED ***")  # pylint: disable=logging-fstring-interpolation
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")  # pylint: disable=logging-fstring-interpolation
        if orders:
            logger.debug(f"  Orders ({len(orders)}):")  # pylint: disable=logging-fstring-interpolation
            for o in orders:
                mm_flag = " [MM]" if o["is_market_maker"] else ""
                logger.debug(
                    f"    {o['investor']:25s} [{o['strategy']:20s}]: Q={o['quantity']:+8.2f}{mm_flag}"
                )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": return_pct,
            "volatility": new_volatility,
            "liquidity": new_liquidity,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "fundamental": fundamental_value,
            "is_crash": is_crash,
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
    Base class for crash simulation investors.

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
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["entry_price"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=custom_state_hot_limit,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])
                self.state.custom_state["volatility_history"].append(
                    market_data["volatility"]
                )

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    def _execute_trade(self, bid_price: float, quantity: float) -> None:
        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
            if self.state.custom_state["entry_price"] == 0:
                self.state.custom_state["entry_price"] = bid_price
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class RiskParityFund(BaseInvestor):
    """
    Risk parity fund with volatility targeting strategy.

    Parameters from config extras:
        - target_volatility, vol_lookback, rebalance_speed, base_position
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        current_vol = market_data["volatility"]
        position = self.state.custom_state["position"]

        target_volatility = extras["target_volatility"]
        rebalance_speed = extras["rebalance_speed"]
        base_position = extras["base_position"]
        strategy_name = self.__class__.__name__

        # Calculate target position based on volatility
        if current_vol > 0:
            vol_ratio = target_volatility / current_vol
            target_position = base_position * min(vol_ratio, 2.0)  # Cap leverage
        else:
            target_position = base_position

        # Rebalance toward target
        position_gap = target_position - position
        quantity = position_gap * rebalance_speed

        # If volatility spike, force faster deleveraging
        if current_vol > target_volatility * 2:
            if position > target_position:
                quantity = min(quantity, -position * 0.3)  # Force sell at least 30%
                logger.debug(f"    [FORCED DELEVERAGE] Vol={current_vol:.1f}, selling!")  # pylint: disable=logging-fstring-interpolation

        quantity = max(-50, min(30, quantity))
        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} target={target_position:.1f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_market_maker": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class LeveragedHedgeFund(BaseInvestor):
    """
    Leveraged hedge fund subject to margin constraints.

    Parameters from config extras:
        - initial_leverage, margin_call_level, liquidation_level, momentum_sensitivity
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        position = self.state.custom_state["position"]
        cash = self.state.custom_state["cash"]
        entry_price = self.state.custom_state["entry_price"]

        margin_call_level = extras["margin_call_level"]
        liquidation_level = extras["liquidation_level"]
        momentum_sensitivity = extras["momentum_sensitivity"]
        strategy_name = self.__class__.__name__

        if entry_price == 0:
            entry_price = 100.0  # Default

        # Calculate margin status
        position_value = position * price
        pnl = position * (price - entry_price)
        equity = cash + pnl

        if position_value > 0:
            margin_ratio = equity / position_value
        else:
            margin_ratio = 1.0

        # Check for forced liquidation
        if margin_ratio < liquidation_level and position > 0:
            # FORCED FULL LIQUIDATION
            quantity = -position
            logger.debug(f"    [FORCED LIQUIDATION] Margin={margin_ratio:.2%}!")  # pylint: disable=logging-fstring-interpolation
        elif margin_ratio < margin_call_level and position > 0:
            # Partial deleverage
            quantity = -position * 0.5
            logger.debug(f"    [MARGIN CALL] Margin={margin_ratio:.2%}, reducing!")  # pylint: disable=logging-fstring-interpolation
        else:
            # Normal trading - momentum based
            if price_return > 0.01:
                quantity = momentum_sensitivity * price_return * 100
                quantity = min(quantity, 30)
            elif price_return < -0.01:
                quantity = momentum_sensitivity * price_return * 100
                quantity = max(quantity, -20)
            else:
                quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} margin={margin_ratio:.2%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_market_maker": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class MarketMaker(BaseInvestor):
    """
    Market maker providing liquidity (and withdrawing in stress).

    Parameters from config extras:
        - volatility_withdraw_threshold, inventory_limit, normal_quote_size, spread_multiplier
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = market_data["volatility"]
        position = self.state.custom_state["position"]

        volatility_withdraw_threshold = extras["volatility_withdraw_threshold"]
        inventory_limit = extras["inventory_limit"]
        normal_quote_size = extras["normal_quote_size"]
        strategy_name = self.__class__.__name__

        # Check if should withdraw from market
        is_withdrawn = volatility > volatility_withdraw_threshold

        if is_withdrawn:
            # Market maker withdraws - no quotes
            quantity = 0.0
            logger.debug(f"    [MM WITHDRAWN] Vol={volatility:.1f} too high!")  # pylint: disable=logging-fstring-interpolation
        else:
            # Provide liquidity - mean revert inventory
            inventory_signal = -position / inventory_limit
            quantity = inventory_signal * normal_quote_size
            quantity = max(-normal_quote_size, min(normal_quote_size, quantity))

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        status = "WITHDRAWN" if is_withdrawn else "ACTIVE"
        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} [{status}] | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_market_maker": True,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class PassiveInvestor(BaseInvestor):
    """
    Passive buy-and-hold investor.

    Parameters from config extras:
        - rebalance_frequency, target_position
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        rebalance_frequency = extras["rebalance_frequency"]
        target_position = extras["target_position"]
        strategy_name = self.__class__.__name__

        # Very occasional rebalancing
        if round_num % rebalance_frequency == 0:
            gap = target_position - position
            quantity = gap * 0.2  # Slow rebalance
            quantity = max(-10, min(10, quantity))
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_market_maker": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class PanicSeller(BaseInvestor):
    """
    Panic seller triggered by losses.

    Parameters from config extras:
        - loss_threshold, crash_trigger, panic_sell_fraction
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        position = self.state.custom_state["position"]
        entry_price = self.state.custom_state["entry_price"]

        loss_threshold = extras["loss_threshold"]
        crash_trigger = extras["crash_trigger"]
        panic_sell_fraction = extras["panic_sell_fraction"]
        strategy_name = self.__class__.__name__

        if entry_price == 0:
            entry_price = 100.0

        # Calculate P&L
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0

        # Check panic conditions
        if pnl_pct < -loss_threshold and position > 0:
            # Full panic - sell everything
            quantity = -position
            logger.debug(f"    [FULL PANIC] Loss={pnl_pct:.1%}!")  # pylint: disable=logging-fstring-interpolation
        elif price_return < crash_trigger and position > 0:
            # Partial panic - sell some
            quantity = -position * panic_sell_fraction
            logger.debug(f"    [PANIC SELLING] Daily drop={price_return:.1%}")  # pylint: disable=logging-fstring-interpolation
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} pnl={pnl_pct:.1%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_market_maker": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


class BottomFisher(BaseInvestor):
    """
    Bottom fisher buying during crashes.

    Parameters from config extras:
        - crash_buy_threshold, discount_threshold, buy_size, lookback
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        price_history = self.state.custom_state["price_history"]

        crash_buy_threshold = extras["crash_buy_threshold"]
        discount_threshold = extras["discount_threshold"]
        buy_size = extras["buy_size"]
        lookback = extras["lookback"]
        strategy_name = self.__class__.__name__

        # Calculate if price is at discount
        if len(price_history) >= lookback:
            recent_avg = sum(list(price_history)[-lookback:]) / lookback
            discount = (price - recent_avg) / recent_avg
        else:
            discount = 0.0

        # Buy conditions
        if price_return < crash_buy_threshold and discount < -discount_threshold:
            # Crash detected - buy the dip
            quantity = buy_size * abs(price_return) * 10
            quantity = min(quantity, 25)
            logger.debug(f"    [BOTTOM FISHING] Discount={discount:.1%}")  # pylint: disable=logging-fstring-interpolation
        elif discount < -discount_threshold * 1.5:
            # Deep value buy
            quantity = buy_size * 0.5
        else:
            quantity = 0.0

        bid_price = price if quantity > 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:20s}): "
            f"Q={quantity:+8.2f} discount={discount:.1%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_market_maker": False,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }
