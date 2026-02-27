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
"""

import os
import random
import math
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer


# =============================================================================
# Market - Coordinator with Crash-Prone Dynamics
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with liquidity-sensitive pricing.

    Price Model:
        P(t+1) = P(t) + λ(L) × NetDemand + γ × [F - P(t)] + σ × ε

    Where λ(L) is liquidity-adjusted price impact:
        - When liquidity is high: low impact
        - When liquidity is low: high impact (accelerates crashes)

    Key feature: Liquidity spiral - selling begets more selling.
    """

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0

    # Price dynamics
    BASE_PRICE_IMPACT = 0.08
    MEAN_REVERSION = 0.01
    NOISE_STD = 0.5

    # Liquidity dynamics
    LIQUIDITY_DECAY = 0.1  # How fast liquidity drops in stress
    LIQUIDITY_RECOVERY = 0.05  # How fast liquidity recovers
    MIN_LIQUIDITY = 0.1  # Floor on liquidity

    HISTORY_LIMIT = 300

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["liquidity"] = 1.0  # Normalized liquidity
            self.state.custom_state["volatility"] = 1.0
            self.state.custom_state["prev_return"] = 0.0

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=self.HISTORY_LIMIT,
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
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        current_liquidity = self.state.custom_state["liquidity"]
        prev_return = self.state.custom_state["prev_return"]
        orders = self.state.custom_state["orders"]

        # Calculate market maker participation (affects liquidity)
        mm_orders = [o for o in orders if o["is_market_maker"]]
        non_mm_orders = [o for o in orders if not o["is_market_maker"]]

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
            -self.LIQUIDITY_DECAY * (new_volatility / 5.0)  # High vol drains liquidity
            + self.LIQUIDITY_RECOVERY * liquidity_supply_effect  # MMs add liquidity
            + 0.02  # Natural recovery
        )
        new_liquidity = current_liquidity + liquidity_change
        new_liquidity = max(self.MIN_LIQUIDITY, min(1.0, new_liquidity))

        # Price impact inversely proportional to liquidity (crash mechanism)
        adjusted_impact = self.BASE_PRICE_IMPACT / new_liquidity

        # Price dynamics
        price_impact = adjusted_impact * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

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
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)")
        print(f"  Liquidity: {current_liquidity:.2f} → {new_liquidity:.2f}")
        print(f"  Volatility: {new_volatility:.2f}")
        if is_crash:
            print(f"  *** CRASH CONDITIONS DETECTED ***")
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  Orders ({len(orders)}):")
            for o in orders:
                mm_flag = " [MM]" if o.get("is_market_maker") else ""
                print(
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
            "fundamental": self.FUNDAMENTAL_VALUE,
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


# =============================================================================
# Base Investor Class
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """Base class for crash simulation investors."""

    STRATEGY_NAME = "base"
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 0.0
    HISTORY_LIMIT = 50

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION
            self.state.custom_state["entry_price"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["volatility_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volatility"),
                entry_limit=self.HISTORY_LIMIT,
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


# =============================================================================
# Risk Parity Fund - Volatility Targeting
# =============================================================================


class RiskParityFund(BaseInvestor):
    """
    Risk parity fund with volatility targeting strategy.

    Theory: Volatility targeting (risk parity approach)
        Maintains constant risk exposure by adjusting position size
        inversely to volatility.

    Behavior:
        - Targets constant volatility exposure
        - When vol rises: FORCED to reduce position
        - Reduction is MECHANICAL (rule-based, not discretionary)
        - Contributes to crash through procyclical selling

    Effect: PROCYCLICAL - Amplifies crashes through forced deleveraging

    Formula:
        target_position = base_position × (target_vol / realized_vol)
        If current > target: sell (deleverage)
    """

    STRATEGY_NAME = "risk_parity_fund"
    INITIAL_POSITION = 50.0  # Starts with position

    # Risk parity parameters
    TARGET_VOLATILITY = 2.0  # Target vol level
    VOL_LOOKBACK = 5  # Window for realized vol
    REBALANCE_SPEED = 0.3  # How fast to rebalance
    BASE_POSITION = 50.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        current_vol = market_data["volatility"]
        position = self.state.custom_state["position"]

        # Calculate target position based on volatility
        if current_vol > 0:
            vol_ratio = self.TARGET_VOLATILITY / current_vol
            target_position = self.BASE_POSITION * min(vol_ratio, 2.0)  # Cap leverage
        else:
            target_position = self.BASE_POSITION

        # Rebalance toward target
        position_gap = target_position - position
        quantity = position_gap * self.REBALANCE_SPEED

        # If volatility spike, force faster deleveraging
        if current_vol > self.TARGET_VOLATILITY * 2:
            if position > target_position:
                quantity = min(quantity, -position * 0.3)  # Force sell at least 30%
                print(f"    [FORCED DELEVERAGE] Vol={current_vol:.1f}, selling!")

        quantity = max(-50, min(30, quantity))
        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} target={target_position:.1f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# Leveraged Hedge Fund - Margin Constrained
# =============================================================================


class LeveragedHedgeFund(BaseInvestor):
    """
    Leveraged hedge fund subject to margin constraints.

    Theory: Margin-based liquidation (Brunnermeier & Pedersen)
        Hedge funds use leverage, face margin requirements.
        When losses mount, forced to liquidate at any price.

    Behavior:
        - Uses high leverage for returns
        - Monitors margin ratio (equity / position value)
        - When margin falls below threshold: FORCED LIQUIDATION
        - Fire sale at market price (not caring about bid)

    Effect: STRONGLY PROCYCLICAL - Fire sales accelerate crash
    """

    STRATEGY_NAME = "leveraged_hedge_fund"
    INITIAL_CASH = 5000.0
    INITIAL_POSITION = 60.0  # Leveraged position

    # Leverage parameters
    INITIAL_LEVERAGE = 3.0
    MARGIN_CALL_LEVEL = 0.5  # Equity/Position < 50% triggers margin call
    LIQUIDATION_LEVEL = 0.3  # Equity/Position < 30% forces full liquidation
    MOMENTUM_SENSITIVITY = 0.5

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        position = self.state.custom_state["position"]
        cash = self.state.custom_state["cash"]
        entry_price = self.state.custom_state["entry_price"]

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
        if margin_ratio < self.LIQUIDATION_LEVEL and position > 0:
            # FORCED FULL LIQUIDATION
            quantity = -position
            print(f"    [FORCED LIQUIDATION] Margin={margin_ratio:.2%}!")
        elif margin_ratio < self.MARGIN_CALL_LEVEL and position > 0:
            # Partial deleverage
            quantity = -position * 0.5
            print(f"    [MARGIN CALL] Margin={margin_ratio:.2%}, reducing!")
        else:
            # Normal trading - momentum based
            if price_return > 0.01:
                quantity = self.MOMENTUM_SENSITIVITY * price_return * 100
                quantity = min(quantity, 30)
            elif price_return < -0.01:
                quantity = self.MOMENTUM_SENSITIVITY * price_return * 100
                quantity = max(quantity, -20)
            else:
                quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} margin={margin_ratio:.2%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# Market Maker - Liquidity Provider
# =============================================================================


class MarketMaker(BaseInvestor):
    """
    Market maker providing liquidity (and withdrawing in stress).

    Theory: Market Microstructure
        Market makers provide liquidity by standing ready to buy/sell.
        In high volatility, they WITHDRAW to protect from adverse selection.

    Behavior:
        - Normally provides two-sided quotes (buy/sell)
        - When volatility is high: WITHDRAWS quotes
        - When inventory is extreme: reduces exposure
        - Withdrawal causes liquidity evaporation

    Effect: LIQUIDITY PROVISION in normal times, WITHDRAWAL in crashes
    """

    STRATEGY_NAME = "market_maker"

    # Market maker parameters
    VOLATILITY_WITHDRAW_THRESHOLD = 5.0  # Vol level to withdraw
    INVENTORY_LIMIT = 30.0  # Max inventory
    NORMAL_QUOTE_SIZE = 20.0  # Normal liquidity provision
    SPREAD_MULTIPLIER = 0.02

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        volatility = market_data["volatility"]
        position = self.state.custom_state["position"]

        # Check if should withdraw from market
        is_withdrawn = volatility > self.VOLATILITY_WITHDRAW_THRESHOLD

        if is_withdrawn:
            # Market maker withdraws - no quotes
            quantity = 0.0
            print(f"    [MM WITHDRAWN] Vol={volatility:.1f} too high!")
        else:
            # Provide liquidity - mean revert inventory
            inventory_signal = -position / self.INVENTORY_LIMIT
            quantity = inventory_signal * self.NORMAL_QUOTE_SIZE
            quantity = max(
                -self.NORMAL_QUOTE_SIZE, min(self.NORMAL_QUOTE_SIZE, quantity)
            )

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        status = "WITHDRAWN" if is_withdrawn else "ACTIVE"
        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} [{status}] | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "is_market_maker": True,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# Passive Investor - Buy and Hold
# =============================================================================


class PassiveInvestor(BaseInvestor):
    """
    Passive buy-and-hold investor.

    Behavior:
        - Holds steady position
        - Rarely trades
        - Does not contribute to crash dynamics
        - Provides implicit stability

    Effect: NEUTRAL - Neither amplifies nor dampens crashes
    """

    STRATEGY_NAME = "passive_investor"
    INITIAL_POSITION = 30.0

    # Passive parameters
    REBALANCE_FREQUENCY = 20  # Very infrequent
    TARGET_POSITION = 30.0

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        # Very occasional rebalancing
        if round_num % self.REBALANCE_FREQUENCY == 0:
            gap = self.TARGET_POSITION - position
            quantity = gap * 0.2  # Slow rebalance
            quantity = max(-10, min(10, quantity))
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# Panic Seller - Loss-Triggered Selling
# =============================================================================


class PanicSeller(BaseInvestor):
    """
    Panic seller triggered by losses.

    Theory: Loss aversion, panic behavior
        Retail investors often panic and sell after losses,
        especially during rapid declines.

    Behavior:
        - Holds position until losses exceed threshold
        - When loss threshold hit: PANIC SELL
        - Sells regardless of price (market order mentality)

    Effect: PROCYCLICAL - Adds selling pressure during crashes
    """

    STRATEGY_NAME = "panic_seller"
    INITIAL_POSITION = 25.0

    # Panic parameters
    LOSS_THRESHOLD = 0.10  # 10% loss triggers panic
    CRASH_TRIGGER = -0.03  # 3% daily drop triggers partial sell
    PANIC_SELL_FRACTION = 0.5  # Sell half when panicking

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        position = self.state.custom_state["position"]
        entry_price = self.state.custom_state["entry_price"]

        if entry_price == 0:
            entry_price = 100.0

        # Calculate P&L
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0

        # Check panic conditions
        if pnl_pct < -self.LOSS_THRESHOLD and position > 0:
            # Full panic - sell everything
            quantity = -position
            print(f"    [FULL PANIC] Loss={pnl_pct:.1%}!")
        elif price_return < self.CRASH_TRIGGER and position > 0:
            # Partial panic - sell some
            quantity = -position * self.PANIC_SELL_FRACTION
            print(f"    [PANIC SELLING] Daily drop={price_return:.1%}")
        else:
            quantity = 0.0

        bid_price = price if quantity != 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} pnl={pnl_pct:.1%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }


# =============================================================================
# Bottom Fisher - Contrarian Crash Buyer
# =============================================================================


class BottomFisher(BaseInvestor):
    """
    Bottom fisher buying during crashes.

    Theory: Contrarian value investing
        Some investors wait for crashes to buy at discounted prices.

    Behavior:
        - Waits for significant price drops
        - Buys when crash conditions detected
        - Provides eventual price floor
        - Limited capital constrains buying

    Effect: STABILIZING - Provides floor during crashes
    """

    STRATEGY_NAME = "bottom_fisher"

    # Bottom fishing parameters
    CRASH_BUY_THRESHOLD = -0.03  # Buy on 3% drops
    DISCOUNT_THRESHOLD = 0.10  # Buy when 10% below recent average
    BUY_SIZE = 15.0
    LOOKBACK = 10

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_return = market_data["return"]
        price_history = self.state.custom_state["price_history"]

        # Calculate if price is at discount
        if len(price_history) >= self.LOOKBACK:
            recent_avg = sum(list(price_history)[-self.LOOKBACK :]) / self.LOOKBACK
            discount = (price - recent_avg) / recent_avg
        else:
            discount = 0.0

        # Buy conditions
        if (
            price_return < self.CRASH_BUY_THRESHOLD
            and discount < -self.DISCOUNT_THRESHOLD
        ):
            # Crash detected - buy the dip
            quantity = self.BUY_SIZE * abs(price_return) * 10
            quantity = min(quantity, 25)
            print(f"    [BOTTOM FISHING] Discount={discount:.1%}")
        elif discount < -self.DISCOUNT_THRESHOLD * 1.5:
            # Deep value buy
            quantity = self.BUY_SIZE * 0.5
        else:
            quantity = 0.0

        bid_price = price if quantity > 0 else 0.0
        quantity = self._apply_constraints(bid_price, quantity, price)

        if quantity != 0:
            self._execute_trade(bid_price, quantity)

        print(
            f"[{self.identity:25s}] R{round_num} ({self.STRATEGY_NAME:20s}): "
            f"Q={quantity:+8.2f} discount={discount:.1%} | "
            f"Cash={self.state.custom_state['cash']:10.2f}, "
            f"Pos={self.state.custom_state['position']:+8.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }
