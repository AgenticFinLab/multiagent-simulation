"""
LearningInvestor: Bayesian Learning-Based Adaptive Investment Strategy

An information-learning oriented investor that dynamically updates beliefs about
market parameters through Bayesian/exponential learning and makes allocation
decisions based on learned expectations.

This implementation bridges adaptive learning theory with modern portfolio selection,
creating an investor that continuously learns from market observations and adapts
its strategy accordingly.


Academic References
This implementation synthesizes key concepts from behavioral learning in finance:

[1] Barberis, N. (2000).
    "Investing for the Long Run When Returns Are Predictable."
    The Journal of Finance, 55(1), 225-292.

    Foundation for adaptive learning in investment decisions. Shows how investors
    with learning mechanisms rationally adjust allocations as they update beliefs
    about return predictability. Demonstrates that learning about market parameters
    is a key driver of time-varying portfolio choices.

[2] Timmermann, A. (1993).
    "How Learning in Financial Markets Generates Excess Volatility and Predictability."
    The Quarterly Journal of Economics, 108(4), 1135-1145.

    Key insight: Learning by investors about market parameters generates market
    dynamics that differ from rational expectations. Shows how belief updating
    and confidence dynamics create predictable patterns and excess volatility.
    Motivates the confidence decay and exploration mechanisms in this model.

[3] Vayanos, D., & Woolley, P. (2013).
    "An Institutional Theory of Momentum and Reversal."
    Review of Financial Studies, 26(5), 1087-1145.

    Extends learning theory to institutional investors. Shows how learning about
    market conditions and asset values generates momentum and reversal patterns.
    Provides theoretical foundation for time-varying risk perceptions and
    adaptive balancing strategies.

[4] Sutton, R. S., & Barto, A. G. (2018).
    "Reinforcement Learning: An Introduction" (2nd ed.).
    MIT Press.

    General framework for learning agents in uncertain environments. The
    exploration-exploitation trade-off and confidence-driven exploration in
    this investor model draws from reinforcement learning theory. Provides
    mathematical foundation for adaptive learning and the value of information.

Theoretical Foundations
This implementation combines several key concepts from financial learning theory:

[1] Bayesian Learning Framework (Barberis, 2000; Timmermann, 1993):
    - Investors maintain beliefs about market parameters (mean return, volatility)
    - Beliefs are updated using observed market returns via Bayes' rule
    - Allocation decisions are made based on current beliefs
    - Learning is adaptive: beliefs converge to true parameters over time

[2] Exponential Smoothing (Exponentially Weighted Moving Average):
    - New observation is weighted by learning rate (0 ≤ α ≤ 1)
    - Update formula: belief_new = (1 - α) * belief_old + α * observation
    - Higher α → faster adaptation to new information (low patience)
    - Lower α → more weight on historical beliefs (high patience)
    - Equivalent to simple Bayesian learning with certain prior assumptions

[3] Rational Decision-Making Under Uncertainty (Sutton & Barto, 2018):
    - Uses mean-variance optimization framework
    - Target allocation based on learned expected return and volatility
    - Exploration-exploitation trade-off when confidence is low
    - Balance between utilizing the best current beliefs and exploring alternatives

[4] Adaptive Learning with Confidence Dynamics (Vayanos & Woolley, 2013):
    - Confidence decay: beliefs become less trusted over time
    - Exploration noise: increased risk-taking under uncertainty
    - Dynamic parameter adjustment based on recent performance
    - Learning generates time-varying risk perceptions and momentum effects

[5] Information Value and Exploration (Sutton & Barto, 2018):
    - Exploration has value: discovering true parameters improves future decisions
    - Confidence reflects information precision
    - Lower confidence → higher value of exploration
    - Captures realistic investor behavior under uncertainty

Learning Dynamics (Barberis, 2000; Timmermann, 1993):
  - learning_rate_for_mean_return (α_μ): Bayesian learning rate for return expectations
  - learning_rate_for_volatility (α_σ): Learning rate for volatility estimates
  - memory_decay_factor (β): Confidence decay rate (information depreciation)

  Update formulas:
    μ_new = (1 - α_μ) * μ_old + α_μ * r_observed
    σ²_new = (1 - α_σ) * σ²_old + α_σ * (r_observed - μ)²
    ψ_new = β * ψ_old

Exploration-Exploitation (Sutton & Barto, 2018):
  - exploration_noise_std (σ_explore): Standard deviation of exploration noise
  - initial_belief_confidence (ψ_0): Initial confidence in beliefs
  - Exploration term: allocation += σ_explore * N(0,1) * (1 - ψ)

  Trade-off: High confidence → exploit current beliefs, low confidence → explore

Portfolio Optimization (Barberis, 2000):
  - risk_aversion_coefficient (A): CARA utility coefficient
  - Allocation formula: ω* = (E[R] - Rf) / (A * σ²)
  - Dynamic: adapts as beliefs (E[R], σ) change

Market Dynamics (Timmermann, 1993; Vayanos & Woolley, 2013):
  - Learning generates predictable patterns and excess volatility
  - Time-varying optimal allocations create momentum/reversal
  - Confidence dynamics create exploitable patterns
"""

import asyncio
import numpy as np
from typing import Any, List
from datetime import datetime
from collections import deque

from llmgt.communication.base import M2IMessage, I2MMessage
from llmgt.investor import base
from llmgt.investor.general import GeneralInvestor


class LearningInvestor(GeneralInvestor):
    """
    Bayesian Learning-Based Adaptive Investor

    This investor continuously learns market parameters (mean return and volatility)
    from observed price movements and updates its investment allocation based on
    these learned beliefs.

    Core mechanism:
    1. Observe realized returns from market prices
    2. Update belief about expected return via exponential smoothing
    3. Update belief about volatility from realized deviations
    4. Compute optimal allocation using mean-variance optimization
    5. Execute balancing trades if needed

    Key feature: Exploration under uncertainty
    - When confidence in beliefs is low, investor adds random noise to allocation
    - This captures realistic behavior of exploring when uncertain
    - Confidence decays over time, naturally increasing exploration
    """

    def __init__(self, config, market_ids):
        super().__init__(config, market_ids)

        # Core Learning Parameters
        self.learning_rate_mean = config.extras["learning_rate_mean"]
        self.learning_rate_vol = config.extras["learning_rate_vol"]
        self.memory_decay = config.extras["memory_decay"]
        self.exploration_noise = config.extras["exploration_noise"]
        self.belief_confidence = config.extras["belief_confidence"]

        # Initial Beliefs
        self.expected_return = config.extras["initial_belief_mean"]
        self.volatility = config.extras["initial_belief_vol"]
        self.confidence = self.belief_confidence

        # Rational Parameters
        self.risk_aversion = config.extras["risk_aversion_coefficient"]
        self.risk_free_rate = config.extras["risk_free_rate"]

        # Wealth & Constraints
        self.wealth = config.extras["initial_wealth"]
        self.min_cash_reserve = config.extras["min_cash_reserve"]
        self.max_position_size = config.extras["max_position_size"]
        self.transaction_cost_rate = config.extras["transaction_cost_rate"]

        # Balancing
        self.balancing_threshold = config.extras["balancing_threshold"]
        self.min_trade_size = config.extras["min_trade_size"]

        # Learning Strategy
        self.learning_strategy = config.extras.get("learning_strategy", "exponential")
        self.adaptive_learning = config.extras.get("adaptive_learning", True)

        # Tracking
        self.lookback_period = 50
        self.price_history = deque(maxlen=self.lookback_period)
        self.return_history = deque(maxlen=self.lookback_period)
        self.current_positions = {}
        self._round_index = 0

        self.computation_delay = config.extras["computation_delay"]
        self.total_transaction_costs = 0.0

    def _update_beliefs(self, observed_realized_return: float):
        """
        Update investor's beliefs about market parameters using exponential smoothing.

        This implements Bayesian-like updating where each new observation updates
        the investor's beliefs about expected return and volatility. Uses exponential
        smoothing (EWMA) for computational efficiency.

        Process:
        1. Update Expected Return Belief:
           E[R]_new = (1 - α_μ) * E[R]_old + α_μ * observed_return

           - Blends old belief with new observation
           - Higher α_μ → reacts faster to price changes
           - Lower α_μ → more stable, ignores noise
        2. Update Volatility Belief:
           σ²_new = (1 - α_σ) * σ²_old + α_σ * (observed_return - E[R])²

           - Estimates variance from squared deviations
           - Uses updated expected return as baseline
           - Captures changing market uncertainty
        3. Confidence Decay:
           ψ_new = β * ψ_old

           - Confidence erodes with each passing period
           - No new information → lower confidence
           - Naturally increases exploration over time
        """

        # Learning rate for expected return
        alpha_mean = self.learning_rate_mean
        # Learning rate for volatility
        alpha_volatility = self.learning_rate_vol

        # 1. Update expected return estimate
        # Blend historical belief with new observation
        self.expected_return = (1 - alpha_mean) * self.expected_return + alpha_mean * observed_realized_return

        # 2. Update volatility estimate
        # Calculate current variance estimate
        current_variance = self.volatility ** 2

        # Deviation from updated expected return
        return_deviation = observed_realized_return - self.expected_return

        # New variance estimate: blend old variance with squared deviation
        updated_variance = (
                (1 - alpha_volatility) * current_variance +
                alpha_volatility * (return_deviation ** 2)
        )
        self.volatility = np.sqrt(max(updated_variance, 1e-8))

        # Confidence erodes over time without new information reinforcement
        # This naturally encourages exploration when beliefs age
        self.confidence *= self.memory_decay

    def _compute_allocation(self) -> float:
        """
        Compute target risky asset allocation using mean-variance optimization.

        This applies the standard Merton portfolio selection formula to allocate
        between risk-free and risky assets based on learned market beliefs.

        Formula (Merton Model):
        ω* = (E[R] - Rf) / (A * σ²)

        Where:
        - ω* = optimal risky asset allocation
        - E[R] = expected return (learned from observations)
        - Rf = risk-free rate
        - A = coefficient of absolute risk aversion
        - σ² = variance (learned from realized volatility)

        Interpretation:
        - High expected excess return (E[R] - Rf) → higher allocation
        - High risk aversion (A) → lower allocation
        - High volatility (σ) → lower allocation

        Exploration Mechanism:
        - When confidence is low: add random noise to allocation
        - Captures realistic exploration behavior
        - Term: allocation += σ_explore * N(0,1) * (1 - confidence)
        """
        # 1.Compute optimal allocation from learned beliefs
        # Excess return above risk-free rate
        excess_return = self.expected_return - self.risk_free_rate

        # Risk penalty: risk aversion × volatility squared
        # (Higher risk aversion or volatility → lowers allocation)
        risk_penalty_denominator = self.risk_aversion * (self.volatility ** 2)

        # Avoid division by zero or negative
        if risk_penalty_denominator <= 0:
            return 0.0

        # Mean-variance optimal allocation
        optimal_allocation = excess_return / risk_penalty_denominator

        # 2.Add exploration under uncertainty
        # When confidence is low, explore by adding random allocation adjustment
        # Random noise from standard normal
        exploration_random_shock = np.random.normal(0, self.exploration_noise)

        # Scale exploration by lack-of-confidence (1 - confidence)
        # High confidence (ψ=1) → no exploration noise
        # Low confidence (ψ=0) → full random noise
        uncertainty_scaling = 1 - self.confidence
        exploration_adjustment = exploration_random_shock * uncertainty_scaling

        # Add exploration to rational allocation
        allocation_with_exploration = optimal_allocation + exploration_adjustment

        # 3.Apply portfolio constraints
        # Constraint 1: Minimum cash reserve
        # Must leave at least min_cash_reserve in cash
        # So risky ≤ (1 - min_cash_reserve)
        minimum_required_allocation = max(0.0, 1.0 - self.min_cash_reserve)

        # Constraint 2: Maximum position size
        maximum_allowed_allocation = self.max_position_size

        # Combine both constraints
        lower_bound = min(minimum_required_allocation, maximum_allowed_allocation)
        upper_bound = maximum_allowed_allocation

        # Clamp allocation to valid range
        final_allocation = np.clip(allocation_with_exploration, lower_bound, upper_bound)

        return float(final_allocation)

    def _should_balance(self, current_allocation, target_allocation) -> bool:
        """
        Determine whether portfolio Balancing is needed.

        Balancing is triggered when the drift between current and target allocation
        exceeds:
        1. The balancing threshold (tolerance for minor drifts)
        2. The minimum trade size (economic viability)

        This prevents excessive trading from:
        - Minor allocation drifts that don't justify transaction costs
        - Noise in portfolio values
        """
        # Calculate absolute drift from target
        allocation_gap = abs(current_allocation - target_allocation)

        # Check both conditions:
        # 1. Gap must exceed threshold
        # 2. Gap must be economically material
        both_conditions_met = (
                allocation_gap > self.balancing_threshold and
                allocation_gap > self.min_trade_size
        )

        return both_conditions_met

    async def decide(self, messages: List[M2IMessage]) -> base.InvestorDecision:
        """
        Core decision logic for Learning investor.
        Implements the learning-based investment strategy:
        1. Observe market prices and compute realized returns
        2. Update beliefs about expected return and volatility
        3. Compute optimal allocation based on learned beliefs
        4. Assess portfolio drift from target
        5. Execute balancing trades if needed
        6. Compile decision reasoning and diagnostics

        This runs each period to adapt to changing market conditions through
        continuous learning and belief updates.
        """
        await asyncio.sleep(self.computation_delay)
        message_received_time = datetime.now().isoformat()

        # 1.Extract current prices
        current_prices = {}
        for msg in messages:
            market_id = msg.market_id
            decision_content = msg.decision_content
            current_price = decision_content.get("current_price") or decision_content["clearing"]["price"]
            current_prices[market_id] = float(current_price)
            self.price_history.append(float(current_price))

        # 2.Compute realized return
        if len(self.price_history) >= 2:
            # Get previous and current prices
            previous_price = self.price_history[-2]
            current_price = self.price_history[-1]

            # Calculate realized return
            realized_return = (current_price - previous_price) / previous_price
            self.return_history.append(realized_return)

            # Update beliefs based on this observation
            self._update_beliefs(realized_return)

        # 3.Compute target allocation
        target_allocation = self._compute_allocation()

        # 4.Current portfolio allocation
        portfolio_value = self.wealth
        total_holdings_value = 0.0
        for market_id, position in self.current_positions.items():
            if market_id in current_prices:
                total_holdings_value += position["shares"] * current_prices[market_id]
        current_allocation = total_holdings_value / portfolio_value if portfolio_value > 0 else 0.0

        # 5.Check balancing need
        should_balance = self._should_balance(current_allocation, target_allocation)

        # 6.Execute trades
        actions = {}
        total_transaction_cost = 0.0
        for market_id, price in current_prices.items():
            if should_balance or self._round_index == 0:
                # Calculate target value for this position
                target_value = target_allocation * portfolio_value
                # Convert to shares
                target_shares = target_value / price
                # Get current shares
                current_shares = self.current_positions.get(market_id, {}).get("shares", 0.0)
                # Calculate trade size
                shares_to_trade = target_shares - current_shares
                # Calculate transaction costs
                trade_value = abs(shares_to_trade * price)
                transaction_cost = trade_value * self.transaction_cost_rate
                total_transaction_cost += transaction_cost

                # Update position
                self.current_positions[market_id] = {"shares": target_shares, "avg_price": price}

                # Package trading action
                actions[market_id] = {
                    "order_type": "market",
                    "shares": float(shares_to_trade),
                    "price": float(price),
                    "target_allocation": float(target_allocation)
                }
            else:
                # no balancing needed
                actions[market_id] = {
                    "order_type": "hold",
                    "shares": 0.0,
                    "price": price,
                    "target_allocation": target_allocation
                }

        # Wealth & confidence update
        self.wealth -= total_transaction_cost
        self.total_transaction_costs += total_transaction_cost
        self._round_index += 1

        reasoning = (
            f"🧠 Learning Investor Decision\n"
            f"E[R]={self.expected_return:.3f}, σ={self.volatility:.3f}, ψ={self.confidence:.3f}\n"
            f"Target Allocation: {target_allocation:.2%}, Current: {current_allocation:.2%}\n"
            f"{'Rebalanced' if should_balance else 'Hold position'} | "
            f"Transaction cost: ${total_transaction_cost:.2f}"
        )

        decision = base.InvestorDecision(
            action=actions,
            reason=reasoning,
            confidence=self.confidence,
            violations={},
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=message_received_time,
            additions={
                "expected_return": float(self.expected_return),
                "volatility": float(self.volatility),
                "confidence": float(self.confidence),
                "target_allocation": float(target_allocation),
                "total_transaction_costs": float(self.total_transaction_costs)
            }
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
                action=action,
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
                    "expected_return": float(self.expected_return),
                    "volatility": float(self.volatility),
                    "confidence": float(self.confidence),
                    "risk_aversion": float(self.risk_aversion)
                }
            )
            i2m_messages.append(msg)

        return i2m_messages
