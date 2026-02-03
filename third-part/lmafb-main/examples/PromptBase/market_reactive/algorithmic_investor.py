"""
MarketReactiveInvestor: Technical Signal-Driven Investment Strategy

A market microstructure-responsive investor that reacts directly to observable
market signals rather than internal beliefs or utility functions.

This investor type implements technical analysis and market microstructure principles,
responding to real-time market dynamics through a linear reaction model.

Academic References
This implementation draws from key works in market microstructure and technical analysis:

[1] Chordia, T., & Subrahmanyam, A. (2004).
    "Order Imbalance and Individual Stock Returns."
    Journal of Finance, 59(6), 2599-2640.

    Foundational work on how order imbalances predict stock returns. Shows that
    excess demand/supply is a strong predictor of price movements. Motivates the
    excess_demand signal in this model.

[2] Hasbrouck, J., & Sinha, A. (2001).
    "Intraday Price Formation in U.S. Equity Index Markets."
    Journal of Finance, 56(6), 2375-2400.

    Analyzes how market microstructure variables (spread, volatility, volume)
    affect price discovery. Demonstrates that bid-ask spread and volatility are
    key market state indicators that predict short-term price movements.

[3] Jegadeesh, N., & Titman, S. (1993).
    "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency."
    Journal of Finance, 48(1), 65-91.

    Classic paper on momentum effect. Shows that price momentum (recent returns)
    predicts future returns in the short term. Provides theoretical foundation for
    momentum-based trading signals.

[4] Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011).
    "Does Algorithmic Trading Improve Liquidity?"
    Journal of Finance, 66(1), 1-33.

    Shows how algorithmic traders react to market microstructure signals and
    improve market efficiency. Provides empirical evidence that technical signal
    response is a valid trading strategy in modern markets.

[5] Harris, L. (2003).
    "Trading and Exchanges: Market Microstructure for Practitioners."
    Oxford University Press.

    Comprehensive reference on market microstructure. Explains the relationship
    between bid-ask spread, volatility, volume, and price movements. Theoretical
    foundation for understanding how market signals interact.

Theoretical Foundations

Market Microstructure Theory (Hasbrouck & Sinha, 2001; Harris, 2003):
- Market signals contain information about supply/demand imbalances
- Price, volume, spread, and volatility reflect information asymmetries
- Technical traders exploit these signals for short-term profit

Order Flow Analysis (Chordia & Subrahmanyam, 2004):
- Excess demand (buy pressure) predicts positive returns
- Order imbalances reflect informed trading
- Market absorbs these imbalances through price adjustments

Momentum Effect (Jegadeesh & Titman, 1993):
- Recent price movements predict near-term continuations
- Driven by both information diffusion and behavioral factors
- Exploitable through momentum-based trading rules

Algorithmic Trading (Hendershott et al., 2011):
- Technical signal response is a valid market-making strategy
- Speed and reaction to signals create competitive advantage
- Improves market liquidity and efficiency

This investor responds to five market signals in a linear reaction model:

Signal 1: MOMENTUM (β₁ * momentum)
- Definition: Price change rate = (P_t - P_{t-1}) / P_{t-1}
- Interpretation: Upward momentum → increase allocation, downward → decrease
- Theory (Jegadeesh & Titman, 1993): Recent winners continue outperforming
- Coefficient β₁ > 0 captures momentum-following behavior

Signal 2: VOLUME CHANGE (β₂ * volume_change)
- Definition: Volume growth rate = (V_t - V_{t-1}) / (V_{t-1} + ε)
- Interpretation: Increasing volume → more trading interest
- Theory: High volume confirms trend validity; indicates conviction
- Coefficient β₂ > 0 amplifies positions when volume increases

Signal 3: VOLATILITY (−β₃ * volatility)
- Definition: Realized volatility σ_t from price movements
- Interpretation: Higher volatility → reduce risk exposure
- Theory (Hasbrouck & Sinha, 2001): Volatility indicates uncertainty
- Coefficient β₃ > 0 causes negative relationship (risk-off when volatile)

Signal 4: BID-ASK SPREAD (−β₄ * spread)
- Definition: Spread = Ask price - Bid price
- Interpretation: Wider spread → higher trading costs, less attractive
- Theory (Harris, 2003): Spread reflects information asymmetry and liquidity
- Coefficient β₄ > 0 reduces allocation when spreads widen

Signal 5: EXCESS DEMAND (β₅ * excess_demand)
- Definition: Excess demand = Quantity demanded at ask - Quantity supplied at bid
- Interpretation: Positive excess demand → stronger buy pressure
- Theory (Chordia & Subrahmanyam, 2004): Order imbalances predict returns
- Coefficient β₅ > 0 increases allocation with stronger buy pressure


Target allocation formula:
ω* = β₀ + β₁·momentum + β₂·volume_change - β₃·volatility - β₄·spread + β₅·excess_demand

Where:
- β₀ = intercept (base allocation)
- β₁ = momentum sensitivity
- β₂ = volume sentiment sensitivity
- β₃ = risk aversion to volatility
- β₄ = spread aversion
- β₅ = order imbalance sensitivity
- ω* = target allocation [min_allocation, max_allocation]
"""

import asyncio
import numpy as np
from typing import Any, List, Dict
from datetime import datetime
from collections import deque

from llmgt.communication.base import M2IMessage, I2MMessage
from llmgt.investor import base
from llmgt.investor.general import GeneralInvestor


class MarketReactiveInvestor(GeneralInvestor):
    """
    This investor reacts to external market signals and dynamics rather than
    internal beliefs or utility functions. Implements a linear reaction model
    to five market microstructure signals.

    Responds directly to:
    - Price momentum (recent trend)
    - Volume changes (trading conviction)
    - Volatility (risk environment)
    - Bid-ask spread (liquidity costs)
    - Excess demand (order imbalance)

    Markets are informational efficient in the short-term;
    the best strategy is to follow observable technical signals and market
    microstructure indicators.
    """

    def __init__(self, config, market_ids):
        """
        Initialize AlgorithmicInvestor with configuration.
        """
        super().__init__(config, market_ids)

        # These coefficients define how strongly the investor reacts to each signal
        # Higher absolute value → stronger reaction to that signal

        # momentum_sensitivity (β₁): Reaction to price momentum
        # β₁ > 0: Follow momentum (buy winners, sell losers)
        # β₁ < 0: Contrarian (fade momentum, mean reversion)
        # Typical range: [-0.5, 0.5]
        # Based on: Jegadeesh & Titman (1993) momentum premium
        self.beta_momentum = config.extras["beta_momentum"]
        # volume_sensitivity (β₂): Reaction to volume changes
        # β₂ > 0: Increase allocation when volume increases
        # β₂ < 0: Decrease allocation when volume increases
        # Typical range: [-1.0, 1.0]
        # Interpretation: volume increase confirms or contradicts momentum
        self.beta_volume = config.extras["beta_volume"]
        # volatility_aversion (β₃): Risk aversion to volatility
        # β₃ > 0 with minus sign: Higher volatility reduces allocation
        # The model uses: −β₃ * volatility (negative relationship)
        # Typical range: [0.1, 1.0] (always positive in config)
        # Interpretation: Risk-off behavior when uncertainty increases
        self.beta_volatility = config.extras["beta_volatility"]
        # spread_aversion (β₄): Reaction to bid-ask spread
        # β₄ > 0 with minus sign: Wider spread reduces allocation
        # The model uses: −β₄ * spread (negative relationship)
        # Typical range: [0.1, 1.0]
        # Interpretation: Less attractive to trade when liquidity costs rise
        self.beta_spread = config.extras["beta_spread"]
        # demand_imbalance_sensitivity (β₅): Reaction to excess demand
        # β₅ > 0: Positive demand imbalance increases allocation
        # β₅ < 0: Positive demand imbalance decreases allocation
        # Typical range: [0.001, 0.01]
        # Interpretation: Order imbalances predict price movements
        # Based on: Chordia & Subrahmanyam (2004)
        self.beta_demand = config.extras["beta_demand"]
        # signal_intercept (β₀): Base allocation without any signals
        # Default: 0.5 (neutral 50% allocation)
        # Can be positive (bullish base) or negative (bearish base)
        self.intercept = config.extras.get("beta_intercept", 0.0)

        # Constraints
        self.min_allocation = config.extras["min_allocation"]
        self.max_allocation = config.extras["max_allocation"]

        # Wealth
        self.wealth = config.extras["initial_wealth"]
        self.transaction_cost_rate = config.extras["transaction_cost_rate"]

        # Memory
        self.price_history = deque(maxlen=20)
        self.volume_history = deque(maxlen=20)
        self.spread_history = deque(maxlen=20)
        self.volatility_history = deque(maxlen=20)
        self.excess_demand_history = deque(maxlen=20)

        self.current_positions = {}
        self._round_index = 0
        self.computation_delay = config.extras["computation_delay"]

    def _extract_signals(self, decision_content: Dict) -> Dict[str, float]:
        """
        Extracts five market microstructure signals from the market state and
        computes derived signals (momentum, volume change, volatility change).

        Signals extracted:
        1. Price: Current market clearing price
        2. Volume: Trading volume (absolute value)
        3. Spread: Bid-ask spread (liquidity cost)
        4. Volatility: Realized volatility (risk measure)
        5. Excess Demand: Order imbalance (demand vs supply)

        Derived signals:
        - Momentum: Price change rate from previous period
        - Volume Change: Volume growth rate from previous period
        - Volatility Change: Volatility change from previous period
        """
        cl = decision_content.get("clearing", {})

        price = (
                cl.get("price")
                or decision_content.get("current_price")
                or (self.price_history[-1] if len(self.price_history) else 0.0)
        )

        volume = abs(cl.get("volume", 0.0))

        ask = cl.get("ask")
        bid = cl.get("bid")
        spread = cl.get("spread")
        if spread is None:
            spread = (ask - bid) if (ask is not None and bid is not None) \
                else (self.spread_history[-1] if len(self.spread_history) else 0.001 * price)

        excess_demand = (
            cl.get("excess_demand")
            if "excess_demand" in cl
            else decision_content.get("additions", {}).get("excess_demand", 0.0)
        )

        volatility = decision_content.get(
            "volatility",
            decision_content.get("additions", {}).get("realized_volatility", 0.0),
        )

        # Append to histories
        self.price_history.append(price)
        self.volume_history.append(volume)
        self.spread_history.append(spread)
        self.volatility_history.append(volatility)
        self.excess_demand_history.append(excess_demand)

        # 1: Momentum = Price change rate
        # Measures trend direction and strength
        momentum = 0.0
        if len(self.price_history) >= 2:
            prev, curr = self.price_history[-2], self.price_history[-1]
            momentum = (curr - prev) / prev if prev != 0 else 0.0

        # 2: Volatility Change = Change in market uncertainty
        # Measures acceleration/deceleration of risk
        vol_change = 0.0
        if len(self.volatility_history) >= 2:
            vol_change = self.volatility_history[-1] - self.volatility_history[-2]

        # 3: Volume Change = Volume growth rate
        # Measures change in trading intensity
        volume_change = 0.0
        if len(self.volume_history) >= 2:
            # Add small epsilon to prevent division by zero
            volume_change = (self.volume_history[-1] - self.volume_history[-2]) / (self.volume_history[-2] + 1e-6)

        return {
            "price": price,
            "momentum": momentum,
            "volume_change": volume_change,
            "volatility": volatility,
            "vol_change": vol_change,
            "spread": spread,
            "excess_demand": excess_demand
        }

    def _compute_allocation(self, signals: Dict[str, float]) -> float:
        """
        Compute target allocation using linear reaction to market signals.

        Implements the core trading model:
        ω* = β₀ + β₁·momentum + β₂·volume_change - β₃·volatility - β₄·spread + β₅·excess_demand

        This is a linear model where each market signal contributes independently
        to the final allocation decision. Signals are combined additively with
        their respective sensitivity coefficients.
        """
        # Linear combination of intercept and signal reactions
        raw_allocation = (
            # Base allocation (intercept)
                self.intercept
                # Momentum term: β₁ * momentum
                + self.beta_momentum * signals["momentum"]
                # Volume term: β₂ * volume_change
                + self.beta_volume * signals["volume_change"]
                # Volatility term: −β₃ * volatility (negative relationship)
                - self.beta_volatility * signals["volatility"]
                # Spread term: −β₄ * spread (negative relationship)
                - self.beta_spread * signals["spread"]
                # Demand term: β₅ * excess_demand (scaled by 1/1000 to normalize)
                + self.beta_demand * signals["excess_demand"] / 1000.0
        )

        # Clip to hard bounds
        allocation_with_constraints = np.clip(raw_allocation, self.min_allocation, self.max_allocation)
        return float(allocation_with_constraints)

    async def decide(self, messages: List[M2IMessage]) -> base.InvestorDecision:
        """
        Core decision routine called each trading period.

        This implements the technical signal-based trading strategy:
        1. Extract market signals from message
        2. Compute target allocation from signals
        3. Compare current vs target allocation
        4. Execute balancing trade
        5. Deduct transaction costs
        6. Compile reasoning and diagnostics
        """
        await asyncio.sleep(self.computation_delay)
        message_received_time = datetime.now().isoformat()

        # 1.Extract signals
        msg = messages[-1]
        market_id = msg.market_id
        decision_content = msg.decision_content
        signals = self._extract_signals(decision_content)
        price = float(signals["price"])  # 原来从 clearing 取的那行删掉

        # 2.Compute allocation
        target_allocation = self._compute_allocation(signals)
        # 3.Assess Current Portfolio
        portfolio_value = self.wealth
        # Current holdings
        current_shares = self.current_positions.get(market_id, {}).get("shares", 0.0)
        # Current position value
        current_value = current_shares * price
        # Current allocation ratio
        current_allocation = current_value / portfolio_value if portfolio_value > 0 else 0.0

        # 4.Compute trade size
        target_value = portfolio_value * target_allocation
        # Convert to shares
        target_shares = (target_value / price) if price > 0 else current_shares
        # Trade size
        shares_to_trade = target_shares - current_shares
        # Trade value and costs
        trade_value = abs(shares_to_trade * price)
        transaction_cost = trade_value * self.transaction_cost_rate

        # 5.Update states
        self.wealth -= transaction_cost

        # Update position
        self.current_positions[market_id] = {"shares": target_shares, "avg_price": price}
        self._round_index += 1

        # 6.Compile reasoning
        reasoning = (
            f"📈 Market-Reactive Decision (Type IV)\n"
            f"Momentum={signals['momentum']:+.3f}, VolumeΔ={signals['volume_change']:+.3f}, "
            f"Volatility={signals['volatility']:.3f}, "
            f"Spread={signals['spread']:.4f}, Demand={signals['excess_demand']:.2f}\n"
            f"Target Allocation={target_allocation:.2%}, Current={current_allocation:.2%}\n"
            f"Shares Traded={shares_to_trade:.2f}, Transaction Cost=${transaction_cost:.2f}"
        )

        decision = base.InvestorDecision(
            action={
                market_id: {
                    "order_type": "market",
                    "shares": float(shares_to_trade),
                    "price": float(price),
                    "target_allocation": float(target_allocation)
                }
            },
            reason=reasoning,
            confidence=1.0,
            violations={},
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=message_received_time,
            additions={**signals, "target_allocation": target_allocation}
        )

        decision.ensure_valid()
        return decision

    def build_i2m_message(
            self,
            messages: List[M2IMessage],
            decision: base.InvestorDecision,
    ) -> List[I2MMessage]:
        """
        Construct messages to send back to markets.
        """
        i2m_messages = []

        for market_id, action in decision.action.items():
            market_decision = base.InvestorDecision(
                action={market_id: action},
                reason=decision.reason,
                confidence=decision.confidence,
                violations=decision.violations,
                round_index=decision.round_index,
                message_received_time=decision.message_received_time,
                decision_start_time=decision.decision_start_time,
                additions=decision.additions,
            )

            msg = I2MMessage(
                investor_id=self.identity,
                market_id=market_id,
                decision_content=market_decision,
                additions={
                    "wealth": float(self.wealth),
                    "reaction_coefficients": {
                        "momentum": self.beta_momentum,
                        "volume": self.beta_volume,
                        "volatility": self.beta_volatility,
                        "spread": self.beta_spread,
                        "demand": self.beta_demand,
                    },
                },
            )

            i2m_messages.append(msg)

        return i2m_messages
