"""Herd Effect Simulation - Multi-Strategy Investor Market

Demonstrates herd behavior in financial markets:
- 1 Market: publishes price, aggregates bids, adjusts price
- 5 Investors: different strategies, respond to market price

Investor Strategies:
1. Momentum: follows price trend (buys when rising, sells when falling)
2. Contrarian: goes against trend (buys low, sells high)
3. RiskAverse: conservative, small adjustments
4. Aggressive: seeks maximum profit, large adjustments
5. NoiseTrader: random behavior, adds market noise

Flow per Round:
    Market → broadcast price → Investors → submit bids → Market → adjust price
"""

import random
import math
from typing import Any, Dict, List, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult


# =============================================================================
# Market Player
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market that:
    1. Publishes current price to all investors
    2. Collects bids from investors
    3. Adjusts price based on aggregate demand
    """

    # Market parameters
    INITIAL_PRICE = 100.0
    FUNDAMENTAL_VALUE = 100.0  # True value the price should converge to
    PRICE_SENSITIVITY = 0.1  # How much price responds to demand imbalance

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize on first round
        if "price" not in self.state.custom_state:
            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["price_history"] = [self.INITIAL_PRICE]
            self.state.custom_state["volume_history"] = []

        # Collect bids from investors
        bids = []
        if observation.inbounds:
            for inb in observation.inbounds:
                bid = inb.payload
                bids.append(
                    {
                        "investor": inb.sender_id,
                        "bid_price": bid["bid_price"],
                        "quantity": bid["quantity"],  # positive=buy, negative=sell
                        "strategy": bid["strategy"],
                    }
                )
        self.state.custom_state["bids"] = bids

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        bids = self.state.custom_state["bids"]

        # Calculate aggregate demand
        total_demand = sum(b["quantity"] for b in bids) if bids else 0

        # Price adjustment based on demand-supply imbalance
        # Positive demand → price increases, negative → decreases
        price_change = self.PRICE_SENSITIVITY * total_demand

        # Mean reversion towards fundamental value
        mean_reversion = 0.02 * (self.FUNDAMENTAL_VALUE - current_price)

        # Add small random noise
        noise = random.gauss(0, 0.5)

        # New price
        new_price = max(1.0, current_price + price_change + mean_reversion + noise)

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(abs(total_demand))

        # Log
        print(f"\n[Market] Round {round_num}")
        print(f"  Price: {current_price:.2f} → {new_price:.2f}")
        print(f"  Aggregate Demand: {total_demand:+.2f}")
        if bids:
            print(f"  Bids received: {len(bids)}")
            for b in bids:
                print(
                    f"    - {b['investor']} ({b['strategy']}): "
                    f"bid={b['bid_price']:.2f}, qty={b['quantity']:+.2f}"
                )

        # Broadcast new price to all investors
        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "change": new_price - current_price,
            "change_pct": (new_price - current_price) / current_price * 100,
            "volume": abs(total_demand),
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


# =============================================================================
# Base Investor
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """Base class for all investors."""

    STRATEGY_NAME = "base"

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize
        if "position" not in self.state.custom_state:
            self.state.custom_state["position"] = 0.0  # Current holdings
            self.state.custom_state["cash"] = 10000.0  # Starting capital
            self.state.custom_state["price_history"] = []

        # Get market data
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def calculate_bid(self) -> tuple:
        """Override in subclass. Returns (bid_price, quantity)."""
        raise NotImplementedError

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]

        bid_price, quantity = self.calculate_bid()

        # Update position (simplified, no actual transaction)
        self.state.custom_state["position"] += quantity

        print(f"[{self.identity}] Round {round_num} ({self.STRATEGY_NAME})")
        print(f"  Market price: {market_data['price']:.2f}")
        print(f"  My bid: {bid_price:.2f}, quantity: {quantity:+.2f}")

        bid = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
        }

        return {
            **bid,
            "outbound_messages": [{"payload": bid, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Investor Strategies
# =============================================================================


class MomentumInvestor(BaseInvestor):
    """
    Momentum Strategy: Follow the trend.
    - Buy when price is rising
    - Sell when price is falling
    - Classic herd behavior amplifier
    """

    STRATEGY_NAME = "momentum"
    SENSITIVITY = 2.0  # How strongly to follow trend

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        change_pct = market_data["change_pct"]

        # Follow the trend
        quantity = self.SENSITIVITY * change_pct / 100 * 10
        bid_price = price * (1 + change_pct / 100 * 0.5)

        return bid_price, quantity


class ContrarianInvestor(BaseInvestor):
    """
    Contrarian Strategy: Go against the trend.
    - Buy when price is falling (undervalued)
    - Sell when price is rising (overvalued)
    - Stabilizing force in market
    """

    STRATEGY_NAME = "contrarian"
    SENSITIVITY = 1.5

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        change_pct = market_data["change_pct"]

        # Go against the trend
        quantity = -self.SENSITIVITY * change_pct / 100 * 10

        # Bid below market if buying, above if selling
        if quantity > 0:
            bid_price = price * 0.98
        else:
            bid_price = price * 1.02

        return bid_price, quantity


class RiskAverseInvestor(BaseInvestor):
    """
    Risk Averse Strategy: Conservative, small positions.
    - Small adjustments to minimize risk
    - Prefers stability over profit
    - Uses volatility-adjusted position sizing
    """

    STRATEGY_NAME = "risk_averse"
    MAX_POSITION = 5.0  # Maximum position size

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        price_history = self.state.custom_state["price_history"]
        position = self.state.custom_state["position"]

        # Calculate recent volatility
        if len(price_history) >= 3:
            recent = price_history[-3:]
            volatility = max(recent) - min(recent)
        else:
            volatility = 1.0

        # Reduce position when volatility is high
        risk_factor = 1.0 / (1.0 + volatility / 10)

        # Target position based on price vs mean
        if len(price_history) >= 5:
            mean_price = sum(price_history[-5:]) / 5
            target = (mean_price - price) / mean_price * self.MAX_POSITION
        else:
            target = 0

        # Small adjustment towards target
        quantity = (target - position) * 0.2 * risk_factor
        quantity = max(-2, min(2, quantity))  # Cap at ±2

        bid_price = price

        return bid_price, quantity


class AggressiveInvestor(BaseInvestor):
    """
    Aggressive Strategy: Maximize profit, high risk tolerance.
    - Large positions
    - Momentum-following with amplification
    - Can create market instability
    """

    STRATEGY_NAME = "aggressive"
    AMPLIFICATION = 3.0

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        change_pct = market_data["change_pct"]
        price_history = self.state.custom_state["price_history"]

        # Strong momentum following with amplification
        base_quantity = self.AMPLIFICATION * change_pct / 100 * 15

        # Add acceleration (second derivative)
        if len(price_history) >= 3:
            accel = (price_history[-1] - price_history[-2]) - (
                price_history[-2] - price_history[-3]
            )
            base_quantity += accel * 0.5

        quantity = base_quantity

        # Aggressive bidding
        if quantity > 0:
            bid_price = price * 1.01  # Bid higher to ensure fill
        else:
            bid_price = price * 0.99

        return bid_price, quantity


class NoiseTrader(BaseInvestor):
    """
    Noise Trader: Random behavior.
    - Adds unpredictable noise to market
    - Simulates uninformed traders
    - Random walk with slight mean reversion
    """

    STRATEGY_NAME = "noise"

    def calculate_bid(self) -> tuple:
        market_data = self.state.custom_state["market_data"]
        price = market_data["price"]
        position = self.state.custom_state["position"]

        # Random quantity with slight mean reversion on position
        random_component = random.gauss(0, 3)
        mean_reversion = -position * 0.1
        quantity = random_component + mean_reversion

        # Random bid around market price
        bid_price = price * random.uniform(0.98, 1.02)

        return bid_price, quantity
