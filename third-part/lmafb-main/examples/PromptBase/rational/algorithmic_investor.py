"""
RationalInvestor: Classical Finance Theory-Based Investment Strategy

An algorithmic investor implementing canonical portfolio optimization frameworks
from modern finance theory. Makes decisions using well-established financial
formulas and optimization techniques.

This investor type represents the "rational agent" baseline - making optimal
decisions based on classical financial theory without behavioral biases,
learning mechanisms, or market reactivity.

Academic References
This implementation synthesizes key frameworks from classical finance theory:

[1] Markowitz, H. M. (1952).
    "Portfolio Selection."
    The Journal of Finance, 7(1), 77-91.

    Foundational modern portfolio theory. Introduces mean-variance optimization:
    investors should maximize expected return subject to risk constraint, or
    minimize risk for target return. Basis for optimal allocation formulas.

[2] Arrow, K. J. (1965).
    "Aspects of the Theory of Risk-Bearing."
    Yrjö Jahnsson Foundation, Helsinki.

    Introduces Constant Absolute Risk Aversion (CARA) utility function and
    derives optimal portfolio allocation. Shows that risk aversion coefficient
    determines the optimal risky asset allocation in closed form.

[3] Tobin, J. (1958).
    "Liquidity Preference as Behavior Towards Risk."
    The Review of Economic Studies, 25(2), 65-86.

    Extends Markowitz with risk-free asset. Derives Two-Fund Separation theorem:
    optimal portfolio combines risk-free asset with single risky portfolio.
    Foundation for understanding cash reserves in portfolio.

[4] Kelly, J. L. (1956).
    "A New Interpretation of Information Rate."
    The Bell System Technical Journal, 35(4), 917-926.

    Derives Kelly Criterion: optimal leverage for growth-maximizing investors.
    Shows that aggressive investors seeking maximal long-term growth should use
    f* = (μ - r) / σ² leverage, though Kelly full leverage is often impractical.

[5] Sharpe, W. F. (1966).
    "Mutual Fund Performance."
    The Journal of Business, 39(S1), 119-138.

    Introduces Sharpe ratio: risk-adjusted performance metric. Provides framework
    for evaluating whether returns justify the risk taken. Used in diagnostics.

[6] Merton, R. C. (1969).
    "Lifetime Portfolio Selection under Uncertainty: The Continuous-Time Case."
    The Review of Economic Studies, 36(3), 239-246.

    Extends portfolio selection to continuous time. Derives optimal allocation
    formula that depends on investment horizon. Theoretical foundation for
    time-varying allocation strategies.


Classical Portfolio Theory (Markowitz, 1952; Tobin, 1958):

The investor solves the optimization problem:
    max_ω E[R_p] - (A/2) * Var[R_p]

Where:
- ω = portfolio weight on risky asset
- E[R_p] = portfolio expected return
- Var[R_p] = portfolio variance
- A = risk aversion coefficient

Solution (Risky Asset Allocation):
    ω* = (E[R] - Rf) / (A * σ²)

Where:
- E[R] = expected return on risky asset
- Rf = risk-free rate
- σ² = variance of risky asset return
- A = Constant Absolute Risk Aversion (CARA) parameter

Interpretation:
- Higher expected excess return → higher allocation
- Higher risk aversion → lower allocation
- Higher volatility → lower allocation

Two-Fund Separation (Tobin, 1958):
- Optimal portfolio is a mix of risk-free asset and single risky portfolio
- Allocation between risk-free and risky assets depends only on risk aversion
- All investors (with different risk aversion) hold same risky portfolio

Kelly Criterion (Kelly, 1956):
For maximizing long-term wealth growth:
    f* = (E[R] - Rf) / σ²

This is the aggressive version (2x the CARA allocation with A=1). Kelly investors
bet heavier, but risk bankruptcy if unlucky. Often fractional Kelly used: f = k * f*

Transaction Costs:
Added to model realistic trading friction:
- Reduces expected return available for allocation
- Creates hysteresis: allocations only adjusted if drift exceeds threshold


Three decision methods implemented:

METHOD 1: CARA (Constant Absolute Risk Aversion)
  Formula: ω* = (μ - Rf) / (A * σ²)
  Characteristics:
  - Closed-form optimal solution
  - Requires: expected return, volatility, risk aversion coefficient
  - Result: constant dollar amount to invest in risky assets
  - Usage: Most common in practice, benchmark for rational agents

METHOD 2: Mean-Variance Optimization
  Optimization: max E[R] - (A/2) * Var[R]
  Characteristics:
  - Maximizes expected utility
  - Mathematically equivalent to CARA for single risky asset
  - Can extend to multiple assets (matrix algebra)
  - Usage: Theoretical foundation, portfolio construction

METHOD 3: Kelly Criterion
  Formula: f* = (μ - Rf) / σ²
  Characteristics:
  - Maximizes log wealth (long-term growth rate)
  - More aggressive than CARA (typically 2x at A=1)
  - Can lead to high leverage and bankruptcy risk
  - Often used with kelly_fraction < 1 for safety
  - Usage: Aggressive growth-seeking investors, hedge funds


Portfolio Theory Parameters:
  - risk_aversion_coefficient (A): CARA utility parameter
    * A > 0: risk-averse investor
    * Higher A: more conservative allocation
    * Typical: 1 to 10

  - expected_return_estimate (μ): Investor's belief about risky asset return
    * Can be constant (rational expectations) or learned

  - volatility_estimate (σ): Investor's belief about risky asset volatility
    * Can be constant or updated adaptively

  - risk_free_rate (Rf): Return on cash/bonds
    * Used to compute excess return (μ - Rf)

Risk Management:
  - min_cash_reserve: Minimum fraction in cash (0 - 1)
    * Implements regulatory or psychological constraint
    * Prevents over-leverage

  - max_position_size: Maximum fraction in risky assets (0 - 1)
    * Hard upper bound on aggressiveness

  - balancing_threshold: balancing trigger
    * Only balance if drift > threshold (transaction cost optimization)

  - transaction_cost_rate: Cost per dollar traded
    * Reduces effective expected return
    * Creates hysteresis in balancing

Behavioral Modifiers:
  - overconfidence_bias: Multiplier on calculated allocation
    * > 1.0: overconfident (over-allocate to risky)
    * < 1.0: under-confident (under-allocate)
    * = 1.0: rational (no bias)

  - confidence_in_estimate: Initial confidence level [0, 1]
    * Used to weight decisions

"""

import asyncio
import numpy as np
from typing import Any, List, Dict
from datetime import datetime
from collections import deque

from llmgt.communication.base import M2IMessage, I2MMessage
from llmgt.investor import base
from llmgt.investor.general import GeneralInvestor


class RationalInvestor(GeneralInvestor):
    """
    Implements optimal portfolio allocation decisions using canonical formulas
    from modern finance theory. Makes decisions according to mean-variance
    optimization and rational actor assumptions.

    This investor represents the theoretical benchmark: making mathematically
    optimal decisions based on classical financial theory, without behavioral
    biases, learning, or market reactivity.

    Core decision mechanism:
    - Believes markets are efficient
    - Has fixed expectations about return and volatility
    - Computes optimal allocation using classical formulas (CARA, MVO, Kelly)
    - Rebalances only when drift justifies transaction costs
    - Acts as rational agent with known preferences
    """

    def __init__(self, config, market_ids):
        """
        Initialize AlgorithmicInvestor with configuration.

        Parameters are read directly from config (not config.extras).
        """
        super().__init__(config, market_ids)

        # risk_aversion_coefficient (A): Constant Absolute Risk Aversion parameter
        # From Arrow (1965) CARA utility: U(W) = -exp(-A*W)
        # Higher A → more risk-averse investor
        # Optimal allocation: ω* = (μ - Rf) / (A * σ²)
        # Typical range: 1 to 10
        self.risk_aversion = config.extras["risk_aversion_coefficient"]
        # risk_free_rate (Rf): Return on cash or government bonds
        # Used to compute excess return: (μ - Rf)
        # Typical: 0.02 to 0.05 annually
        self.risk_free_rate = config.extras["risk_free_rate"]
        # expected_return_estimate (μ): Investor's belief about risky asset return
        # Constant (not updated from experience)
        # Typical: 0.08 to 0.12 annually
        self.expected_return = config.extras["expected_return_estimate"]
        # volatility_estimate (σ): Investor's belief about risky asset volatility
        # Constant throughout investment period
        # Typical: 0.15 to 0.25 annually
        self.volatility = config.extras["volatility_estimate"]
        # decision_method: Which optimization formula to use
        # Options:
        #   "CARA": Constant Absolute Risk Aversion (most common)
        #   "mean_variance_optimization": Mean-variance (equivalent to CARA for 1 asset)
        #   "kelly_criterion": Kelly Criterion (aggressive growth)
        self.decision_method = config.extras["decision_method"]
        # kelly_fraction (f_kelly): Fraction of Kelly leverage to use
        # f_kelly < 1: fractional Kelly (safer, more practical)
        # f_kelly = 1: full Kelly (aggressive, optimal long-term growth)
        # f_kelly > 1: leveraged Kelly (very aggressive, high bankruptcy risk)
        # Typical: 0.25 to 1.0
        self.kelly_fraction = config.extras["kelly_fraction"]

        # Execution / Capital Constraints
        self.wealth = config.extras["initial_wealth"]
        self.initial_wealth = self.wealth
        self.min_cash_reserve = config.extras["min_cash_reserve"]
        self.max_position_size = config.extras["max_position_size"]
        self.transaction_cost_rate = config.extras["transaction_cost_rate"]

        # Balancing Rules
        self.balancing_threshold = config.extras["balancing_threshold"]
        self.min_trade_size = config.extras["min_trade_size"]

        # Reporting / Tracking
        self.confidence = config.extras["confidence_in_estimate"]
        self.overconfidence_bias = config.extras["overconfidence_bias"]
        self.annualization_factor = config.extras["annualization_factor"]
        self.max_history_length = config.extras["max_history_length"]

        # Runtime State
        self.current_positions = {}
        self.price_history = deque(maxlen=2)
        self.return_history = deque(maxlen=self.max_history_length)
        self.portfolio_value_history = deque(maxlen=self.max_history_length)

        self.total_transaction_costs = 0.0
        self.computation_delay = config.extras["computation_delay"]

    def _compute_cara_allocation(self) -> float:
        """
        Compute Constant Absolute Risk Aversion (CARA) optimal allocation.

        Derives from Arrow (1965) CARA utility: U(W) = -exp(-A*W)
        Optimal risky asset allocation formula:
        ω* = (μ - Rf) / (A * σ²)

        Where:
        - μ = expected return on risky asset
        - Rf = risk-free rate
        - A = risk aversion coefficient
        - σ² = variance of risky asset

        Properties:
        - Higher expected excess return → higher allocation
        - Higher risk aversion → lower allocation
        - Higher volatility → lower allocation
        """
        # Calculate numerator: excess return
        excess_return = self.expected_return - self.risk_free_rate
        # Calculate denominator: risk penalty
        risk_penalty_denominator = self.risk_aversion * (self.volatility ** 2)

        if risk_penalty_denominator == 0:
            return 0.0

        # Compute optimal allocation from CARA formula
        optimal_allocation = excess_return / risk_penalty_denominator

        # Crude transaction cost adjustment
        # If there's positive excess return, reduce allocation slightly
        # to account for trading costs (higher costs → more conservative)
        if self.transaction_cost_rate > 0 and excess_return > 0:
            optimal_allocation -= self.transaction_cost_rate / max(excess_return, 1e-12)

        return optimal_allocation

    def _compute_mean_variance_allocation(self) -> float:
        """
        Compute Mean-Variance Optimization allocation.
        Solves the optimization problem (Markowitz, 1952):
        max_ω E[R_p] - (A/2) * Var[R_p]

        Where portfolio return and variance are:
        - E[R_p] = (1-ω)*Rf + ω*μ = Rf + ω*(μ-Rf)
        - Var[R_p] = ω²*σ²

        First-order condition:
        ∂/∂ω [Rf + ω*(μ-Rf) - (A/2)*ω²*σ²] = 0
        (μ-Rf) - A*ω*σ² = 0
        ω* = (μ-Rf) / (A*σ²)

        Mathematically equivalent to CARA for single risky asset.
        """
        return self._compute_cara_allocation()

    def _compute_kelly_allocation(self) -> float:
        """
        Compute Kelly Criterion allocation for maximal long-term growth.
        Kelly (1956) criterion maximizes expected log wealth E[log(W)].

        Optimal leverage for continuous doubling:
        f* = (μ - Rf) / σ²
        This is typically 2x the CARA allocation with A=1 (very aggressive).

        Properties:
        - Maximizes long-term compound growth rate
        - Can lead to high volatility and bankruptcy risk
        - Often used with kelly_fraction < 1 (fractional Kelly)

        Full Kelly allocation would be highly aggressive. We apply kelly_fraction
        to make it more conservative:
        f_kelly = kelly_fraction * f*

        Typical usage:
        - kelly_fraction = 0.25: Very conservative Kelly
        - kelly_fraction = 0.50: Half Kelly (recommended for practitioners)
        - kelly_fraction = 1.00: Full Kelly (theoretical optimum, risky)
        """
        # Calculate numerator: excess return
        excess_return = self.expected_return - self.risk_free_rate
        # Calculate denominator: variance
        variance = self.volatility ** 2

        if variance == 0:
            return 0.0

        # Compute full Kelly leverage
        kelly_full = excess_return / variance
        # Apply fractional Kelly for practical use
        kelly_adjusted = kelly_full * self.kelly_fraction

        return kelly_adjusted

    def _apply_constraints(self, raw_allocation: float) -> float:
        """
        Apply portfolio constraints to allocation.
        Enforces hard bounds on allocation based on policy limits:
        1. Minimum cash reserve requirement
        2. Maximum position size limit

        These constraints reflect:
        - Regulatory requirements (margin limits)
        - Risk management policies
        - Liquidity needs
        - Prudent portfolio construction

        Constraint logic:
        - If min_cash_reserve = 0.10: must keep ≥10% in cash
          → risky allocation ≤ 90%
        - If max_position_size = 0.80: risky allocation ≤ 80%
          → Combined: risky allocation ≤ min(90%, 80%) = 80%
        """
        # Compute lower bound from cash reserve requirement
        # If min_cash_reserve = 0, lower_bound = 0 (no lower limit)
        # If min_cash_reserve = 0.1, lower_bound = 0.9 (risky ≤ 90%)
        lower_bound = 0.0
        if self.min_cash_reserve > 0:
            lower_bound = max(0.0, 1.0 - self.min_cash_reserve)

        # Compute upper bound from maximum position size
        upper_bound = self.max_position_size

        constrained_allocation = np.clip(raw_allocation, lower_bound, upper_bound)

        return float(constrained_allocation)

    def _compute_optimal_allocation(self) -> float:
        """
        Compute optimal allocation based on selected decision method.

        Steps:
        1. Choose allocation formula based on decision_method
        2. Apply overconfidence bias (scale result)
        3. Apply hard portfolio constraints

        Decision methods:
        - "CARA": Classical Constant Absolute Risk Aversion (default)
        - "mean_variance_optimization": Mean-variance (equivalent to CARA)
        - "kelly_criterion": Kelly Criterion (aggressive growth)

        Overconfidence adjustment:
        - overconfidence_bias > 1: Investor over-allocates to risky
        - overconfidence_bias = 1: Rational investor
        - overconfidence_bias < 1: Investor under-allocates
        """
        if self.decision_method == "CARA":
            omega = self._compute_cara_allocation()
        elif self.decision_method == "mean_variance_optimization":
            omega = self._compute_mean_variance_allocation()
        elif self.decision_method == "kelly_criterion":
            omega = self._compute_kelly_allocation()
        else:
            omega = self._compute_mean_variance_allocation()

        # Scales the theoretical optimal allocation by investor's confidence bias
        omega *= self.overconfidence_bias
        omega_final = self._apply_constraints(omega)

        return omega_final

    def _should_balance(self, current_allocation: float, target_allocation: float) -> bool:
        """
        Determine if portfolio balancing is needed.

        Balancing decision is based on:
        1. Allocation drift exceeds balancing_threshold
        2. Drift is materially large (exceeds min_trade_size)

        This optimization prevents constant balancing due to:
        - Market noise in allocation ratio
        - Transaction costs outweighing benefits
        - Bid-ask spread slippage

        Example with threshold=5%, min_trade=1%:
        - drift = 2%: HOLD (below threshold)
        - drift = 6%: REBALANCE (above both)
        - drift = 3%: HOLD (between thresholds)
        """
        # Calculate absolute deviation from target
        allocation_drift = abs(current_allocation - target_allocation)

        # Check if gap exceeds tolerance threshold
        if allocation_drift < self.balancing_threshold:
            return False

        # Check if gap is economically meaningful
        if allocation_drift < self.min_trade_size:
            return False

        return True

    def _compute_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value (stocks + cash).
        """
        stock_value = 0.0
        for market_id, position in self.current_positions.items():
            if market_id in current_prices:
                stock_value += position["shares"] * current_prices[market_id]

        return self.wealth

    async def decide(self, messages: List[M2IMessage]) -> base.InvestorDecision:
        """
        Allow Core decision-making logic using algorithmic investment formulas.

        Steps:
        1. Extract market prices and compute realized returns
        2. Compute optimal allocation from classical formulas
        3. Assess current portfolio allocation
        4. Determine if rebalancing is needed
        5. Execute trading actions
        6. Deduct transaction costs and compile reasoning
        """
        message_received_time = datetime.now().isoformat()
        await asyncio.sleep(self.computation_delay)
        decision_start_time = datetime.now().isoformat()

        # Extract market information
        current_prices = {}
        market_states = {}

        for message in messages:
            market_id = message.market_id
            decision_content = message.decision_content

            if "current_price" in decision_content:
                current_price = float(decision_content["current_price"])
                market_states[market_id] = decision_content
            else:
                current_price = float(decision_content["clearing"]["price"])
                market_states[market_id] = decision_content

            current_prices[market_id] = current_price
            self.price_history.append(current_price)

        # Update beliefs
        if len(self.price_history) >= 2:
            price_old = self.price_history[-2]
            price_new = self.price_history[-1]
            realized_return = (price_new - price_old) / price_old
            self.return_history.append(realized_return)

        # Compute optimal allocation
        target_allocation = self._compute_optimal_allocation()

        # Calculate current allocation
        portfolio_value = self._compute_portfolio_value(current_prices)

        current_stock_value = 0.0
        for market_id, position in self.current_positions.items():
            if market_id in current_prices:
                current_stock_value += position["shares"] * current_prices[market_id]

        current_allocation = current_stock_value / portfolio_value if portfolio_value > 0 else 0.0

        # Decide whether to balance
        should_balance = self._should_balance(current_allocation, target_allocation)

        # Generate actions
        actions = {}
        total_transaction_cost = 0.0
        reasoning_parts = []

        for market_id, current_price in current_prices.items():
            if should_balance or self._round_index == 0:
                target_value = target_allocation * portfolio_value
                target_shares = target_value / current_price

                current_shares = self.current_positions.get(market_id, {}).get("shares", 0.0)
                shares_to_trade = target_shares - current_shares

                trade_value = abs(shares_to_trade * current_price)
                transaction_cost = trade_value * self.transaction_cost_rate
                total_transaction_cost += transaction_cost

                if market_id not in self.current_positions:
                    self.current_positions[market_id] = {"shares": 0.0, "avg_price": current_price}

                new_shares = current_shares + shares_to_trade
                self.current_positions[market_id]["shares"] = new_shares

                if shares_to_trade > 0:
                    old_value = current_shares * self.current_positions[market_id]["avg_price"]
                    new_value = shares_to_trade * current_price
                    total_shares = current_shares + shares_to_trade
                    if total_shares > 0:
                        self.current_positions[market_id]["avg_price"] = (old_value + new_value) / total_shares

                actions[market_id] = {
                    "order_type": "market",
                    "shares": float(shares_to_trade),
                    "price": float(current_price),
                    "target_allocation": float(target_allocation),
                }

                reasoning_parts.append(
                    f"{market_id}: Trade {shares_to_trade:.2f} shares @ ${current_price:.2f} "
                    f"(target allocation: {target_allocation:.2%})"
                )
            else:
                actions[market_id] = {
                    "order_type": "hold",
                    "shares": 0.0,
                    "price": current_price,
                    "target_allocation": target_allocation,
                }

                reasoning_parts.append(
                    f"{market_id}: HOLD (allocation drift {abs(current_allocation - target_allocation):.2%} "
                    f"< threshold {self.balancing_threshold:.2%})"
                )

        # Update wealth
        self.wealth -= total_transaction_cost
        self.total_transaction_costs += total_transaction_cost

        # Build reasoning
        decision_method_name = {
            "CARA": "Constant Absolute Risk Aversion",
            "mean_variance_optimization": "Mean-Variance Optimization",
            "kelly_criterion": "Kelly Criterion",
        }.get(self.decision_method, self.decision_method)

        reasoning = (
                f"🤖 Algorithmic Decision ({decision_method_name})\n"
                f"Beliefs: E[R]={self.expected_return:.2%}, σ={self.volatility:.2%}\n"
                f"Risk Aversion: A={self.risk_aversion:.2f}\n"
                f"Optimal Allocation: {target_allocation:.2%}\n"
                f"Current Allocation: {current_allocation:.2%}\n"
                f"{'balancing' if should_balance else 'No balancing needed'}\n"
                f"Transaction Costs: ${total_transaction_cost:.2f}\n"
                + "\n".join(reasoning_parts)
        )

        # Calculate confidence
        confidence = self.confidence * self.overconfidence_bias
        confidence = min(confidence, 1.0)

        # Check violations
        violations = {}
        if target_allocation > self.max_position_size:
            violations["max_position"] = f"Target {target_allocation:.2%} > max {self.max_position_size:.2%}"
        if (1 - target_allocation) < self.min_cash_reserve:
            violations["min_cash"] = f"Cash {1 - target_allocation:.2%} < min {self.min_cash_reserve:.2%}"

        # Track performance
        self.portfolio_value_history.append(portfolio_value)

        sharpe_ratio = 0.0
        if len(self.return_history) >= 5:
            returns_array = np.array(list(self.return_history))
            mean_return = np.mean(returns_array)
            std_return = np.std(returns_array)
            if std_return > 0:
                sharpe_ratio = (mean_return - self.risk_free_rate / self.annualization_factor) / std_return

        self._round_index += 1

        # Build decision
        decision = base.InvestorDecision(
            action=actions,
            reason=reasoning,
            confidence=confidence,
            violations=violations,
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=decision_start_time,
            additions={
                "target_allocation": float(target_allocation),
                "current_allocation": float(current_allocation),
                "expected_return": float(self.expected_return),
                "volatility": float(self.volatility),
                "portfolio_value": float(portfolio_value),
                "total_transaction_costs": float(self.total_transaction_costs),
                "sharpe_ratio": float(sharpe_ratio),
                "should_balance": bool(should_balance),
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
                    "current_position": self.current_positions.get(market_id, {}),
                    "risk_aversion": float(self.risk_aversion),
                    "expected_return": float(self.expected_return),
                    "volatility": float(self.volatility),
                    "decision_method": str(self.decision_method),
                }
            )

            i2m_messages.append(msg)

        return i2m_messages