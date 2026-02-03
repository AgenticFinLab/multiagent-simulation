"""
BehavioralInvestor: Prospect Theory-Based Investment Decision Framework.

Key Implementations:
- Reference-dependent value function (loss aversion)
- Subjective risk perception with distortion (κ multiplier)
- Reference pressure on exposure (catch-up when behind, protect when ahead)
- Subjective volatility impact on allocation decisions
- Psychological target allocation derived from behavioral factors (not mean-variance)

ACADEMIC REFERENCES:
This implementation is built on foundational work in behavioral finance and
prospect theory. The core theoretical frameworks come from:

[1] Kahneman, D., & Tversky, A. (1979).
    "Prospect Theory: An Analysis of Decision under Risk."
    Econometrica, 47(2), 263-291.

    Foundation for reference-dependent preferences, loss aversion, and the
    value function v(x). Introduces the idea that people evaluate outcomes
    relative to a reference point, not in absolute terms. This is the core
    behavioral principle underlying this investor model.

[2] Prelec, D. (1998).
    "The Probability Weighting Function."
    Econometrica, 66(3), 497-527.

    Provides the theoretical framework for probability distortion in decision-making.
    Introduces the Prelec probability weighting function used for subjective
    probability perception (probability_weighting_gamma parameter).

[3] Barberis, N., & Thaler, R. (2003).
    "A Survey of Behavioral Finance."
    In Handbook of the Economics of Finance (Vol. 1, pp. 1053-1128).

    Comprehensive survey of behavioral finance phenomena including reference
    point adaptation, loss aversion coefficients, and empirical evidence for
    reference-dependent behavior in markets. Provides practical calibrations
    and behavioral anomalies that motivated this implementation.

[4] Benartzi, S., & Thaler, R. (1995).
    "Myopic Loss Aversion and the Equity Premium Puzzle."
    The Quarterly Journal of Economics, 110(1), 73-92.

    Demonstrates the break-even effect and myopic loss aversion. Shows how
    reference-dependent preferences and loss aversion lead to different
    risk-taking behavior when ahead vs. behind a reference point (catch-up
    and protect intensities in this model).
"""

import asyncio
import numpy as np
from typing import Any, List, Dict
from datetime import datetime
from collections import deque

from llmgt.communication.base import M2IMessage, I2MMessage
from llmgt.investor import base
from llmgt.investor.general import GeneralInvestor


class BehavioralInvestor(GeneralInvestor):
    """
    Behavioral / Psychology-Driven Investor

    Decision logic:
    - Evaluates outcomes relative to a reference point r0, not absolute wealth
    - Is loss-averse: losses loom larger than gains
    - Distorts perceived risk: uses subjective volatility σ_tilde instead of σ
    - Adjusts aggressiveness depending on "am I behind or ahead of my reference"
    - Generates a target exposure ω* from psychological pressure terms,
      not from CARA / Kelly / Mean-Variance formulas
    """

    def __init__(self, config, market_ids):
        super().__init__(config, market_ids)

        # Psychological valuation parameters
        self.alpha_gain = config.extras["alpha_gain"]
        self.beta_loss = config.extras["beta_loss"]
        self.loss_aversion = config.extras["loss_aversion"]

        self.reference_point_mode = config.extras["reference_point"]
        self.reference_update_rate = config.extras["reference_update_rate"]
        self.reference_policy = config.extras.get("reference_policy", "adaptive")

        # Will set this after we know initial wealth
        self.reference_level = None

        # Perceived risk / probability distortion
        self.risk_perception_kappa = config.extras["risk_perception_kappa"]
        self.probability_weight_gamma = config.extras["probability_weight_gamma"]
        self.c_risk_scale = config.extras["c_risk_scale"]

        # Catch-up vs protect behavior
        self.catchup_intensity = config.extras["catchup_intensity"]
        self.protect_intensity = config.extras["protect_intensity"]

        # Market beliefs
        # even though this investor is not mean-variance optimizing,
        # it still "knows" rough μ, σ, r from environment for perception
        self.expected_return = config.extras["expected_return_estimate"]
        self.volatility = config.extras["volatility_estimate"]
        self.risk_free_rate = config.extras["risk_free_rate"]
        self.risk_update_method = config.extras.get("risk_update_method", "subjective")
        self.probability_weighting = config.extras.get("probability_weighting", "prelec")
        self.decision_mode = config.extras.get("decision_mode", "reference_value")

        # Wealth & constraints
        self.wealth = config.extras["initial_wealth"]
        self.initial_wealth = self.wealth
        self.min_cash_reserve = config.extras["min_cash_reserve"]
        self.max_position_size = config.extras["max_position_size"]
        self.transaction_cost_rate = config.extras["transaction_cost_rate"]

        # Balancing policy
        self.balancing_threshold = config.extras["balancing_threshold"]
        self.min_trade_size = config.extras["min_trade_size"]

        # Diagnostics / tracking
        self.max_history_length = config.extras["max_history_length"]
        self.annualization_factor = config.extras["annualization_factor"]
        self.computation_delay = config.extras["computation_delay"]

        # Runtime state
        self.current_positions: Dict[str, Dict[str, float]] = {}
        self.price_history = deque(maxlen=2)
        self.return_history = deque(maxlen=self.max_history_length)
        self.portfolio_value_history = deque(maxlen=self.max_history_length)

        self.total_transaction_costs = 0.0

    def _init_reference_level(self):
        """
        Initialize the internal reference level r0_t once at the start.
        """
        if self.reference_level is not None:
            return

        if isinstance(self.reference_point_mode, (int, float)):
            self.reference_level = float(self.reference_point_mode)
        elif self.reference_point_mode == "initial_wealth":
            self.reference_level = float(self.initial_wealth)
        else:
            # if user says "moving_average" or unknown, start at initial wealth
            self.reference_level = float(self.initial_wealth)

    def _update_reference_level(self):
        """
        Adapt reference point towards current wealth.
        This implements "aspiration adaptation" from behavioral finance:

        When an investor experiences positive returns:
        - Reference point rises (they adapt their expectations upward)
        - New baseline becomes higher
        When experiencing losses:
        - Reference point adapts more slowly (sticky downward)
        - Maintained through low ρ parameter

        Update formula (exponential smoothing):
        r0_new = (1 - ρ) * r0_old + ρ * wealth_current
        where ρ = reference_update_rate

        Example with ρ = 0.1:
        - Wealth was $100k, reference was $100k
        - Portfolio grows to $110k
        - New reference: (0.9)*100k + (0.1)*110k = $101k
        - Reference point lags actual wealth (slow adaptation)
        """
        if self.reference_policy != "adaptive":
            return

        rho = self.reference_update_rate
        self.reference_level = (
            (1 - rho) * self.reference_level + rho * self.wealth
        )

    def _subjective_volatility(self) -> float:
        """
        Calculate the subjective (perceived) volatility σ_tilde.
        This distorts the actual market volatility based on the investor's
        risk perception bias.

        Key aspect of behavioral finance: people don't perceive risk accurately.

        Formula: σ_tilde = sqrt(κ) * σ_actual

        Interpretation:
        - κ > 1: Perceives volatility as HIGHER than reality (overestimating risk)
                 Example: κ=1.96 → perceives volatility as 40% higher
                 Typical for risk-averse investors or during crises

        - κ = 1: Perceives volatility accurately

        - κ < 1: Perceives volatility as LOWER than reality (underestimating risk)
                 Example: κ=0.25 → perceives volatility as 50% lower
                 Typical for overconfident investors or in bull markets

        """
        sigma_tilde_sq = self.risk_perception_kappa * (self.volatility ** 2)
        sigma_tilde_sq = max(sigma_tilde_sq, 1e-12)
        return np.sqrt(sigma_tilde_sq)

    def _phi_risk(self, sigma_tilde: float) -> float:
        """
        Define higher perceived risk => lower exposure.
        Risk aversion dampening function: φ_risk(σ_tilde)

        Maps perceived volatility to a risk aversion factor that reduces risky allocation.
        Higher perceived risk → lower target allocation.

        Formula: φ_risk(σ_tilde) = 1 / (1 + c * σ_tilde)

        Properties:
        - As σ_tilde → 0:   φ_risk → 1.0 (no risk aversion, full allocation)
        - As σ_tilde → ∞:   φ_risk → 0.0 (extreme risk aversion, zero allocation)
        - Function is smooth and continuous (no discontinuities)
        - Resembles logistic function: smooth sigmoid-like transition

        This ensures risky allocation decreases smoothly as perceived risk increases,
        capturing the observed behavior that investors flee risky assets when scared.
        """
        return 1.0 / (1.0 + self.c_risk_scale * sigma_tilde)

    def _phi_reference(self, delta_r: float) -> float:
        """
        Adjusts risk exposure based on whether investor is ahead or behind their
        psychological reference point.
        This captures the "break-even" effect.

        Definition: Δr = reference_level - wealth

        Behavior interpretation:
        Case 1: Δr > 0 (INVESTOR IS BEHIND)
        - Current wealth < reference point
        - Investor feels like they're "underwater" or "down"
        - Reaction: INCREASE risk to "catch up" and restore reference point
        - Formula: φ_reference = 1 + a * |Δr|
        - Effect: Target allocation multiplied by (1 + a*gap), making it larger
        Case 2: Δr ≤ 0 (INVESTOR IS AHEAD)
        - Current wealth ≥ reference point
        - Investor feels like they're "winning" or "up"
        - Reaction: REDUCE risk to "lock in" and "protect gains"
        - Formula: φ_reference = 1 - b * |Δr|
        - Effect: Target allocation multiplied by (1 - b*gap), making it smaller

        This asymmetric response (different a vs b) captures empirical findings:
        - Investors take excessive risk when losing (house money effect)
        - Investors reduce risk when winning (stop-loss effect)
        """
        if delta_r > 0:
            return 1.0 + self.catchup_intensity * abs(delta_r)
        else:
            return 1.0 - self.protect_intensity * abs(delta_r)

    def _target_allocation_behavioral(self) -> float:
        """
        Compute behavioral target allocation ω* based on psychological factors.

        This is the core decision mechanism. Instead of mean-variance optimization,
        target allocation comes from prospect theory psychological factors.

        Formula: ω* = φ_risk(σ_tilde) * φ_reference(Δr)

        Interpretation: ω* is the desired fraction of wealth to allocate to risky assets

        Step-by-step logic:
        1. Initialize reference level (if first call)
           → Sets up psychological baseline for this investor
        2. Calculate risk aversion factor
           → φ_risk = 1 / (1 + c * σ_tilde)
           → Reflects: "How much risk do I perceive?"
           → Higher perceived risk → lower allocation
        3. Calculate reference pressure factor
           → φ_reference = (1 + a*|gap|) if behind, or (1 - b*|gap|) if ahead
           → Reflects: "Am I winning or losing relative to my goal?"
           → Behind goal → more aggressive (catch up)
           → Above goal → less aggressive (protect)
        4. Multiply factors to get raw psychological allocation
           → ω_raw = risk_factor × reference_factor
           → Both factors influence final decision independently
        5. Enforce hard constraints
           → No negative allocation (no short-selling)
           → Respect minimum cash reserve requirement
           → Respect maximum position size limit

        Example scenario:
        - Perceived σ_tilde = 20%, c = 1.0
          → φ_risk = 1/(1+1*0.2) = 0.833 (5 portions risky, 6 total)
        - Gap Δr = -$10k (ahead by $10k), b = 0.05
          → φ_reference = 1 - 0.05*10 = 0.5 (reduce allocation)
        - Raw ω* = 0.833 * 0.5 = 0.417 (41.7% risky)
        - With constraints: final ω* = 0.417 (if within limits)
        """
        self._init_reference_level()

        sigma_tilde = self._subjective_volatility()
        risk_term = self._phi_risk(sigma_tilde)

        delta_r = self.reference_level - self.wealth
        ref_term = self._phi_reference(delta_r)

        omega_raw = risk_term * ref_term

        # no negative allocation (no shorting baseline)
        omega_raw = max(0.0, omega_raw)

        # enforce cash reserve + max_position_size
        # must keep at least min_cash_reserve in cash -> risky allocation ≤ 1 - min_cash_reserve
        max_risky_from_cash = max(0.0, 1.0 - self.min_cash_reserve)
        upper_cap = min(max_risky_from_cash, self.max_position_size)

        omega_clamped = float(np.clip(omega_raw, 0.0, upper_cap))
        return omega_clamped

    def _compute_portfolio_value(self) -> float:
        """
        Calculate current portfolio value.

        Important implementation note: In this code, wealth is defined as the
        cash portion of the portfolio after accounting for transaction costs
        and other cash outflows. The market value of held shares is calculated
        separately.

        This is a design choice that separates:
        - Cash wealth: self. wealth (liquid, available for trading)
        - Position value: calculated from shares * price
        - Total portfolio value: wealth + position_value

        For this implementation, we return the cash wealth component.
        """
        return self.wealth

    def _current_allocation(self, current_prices: Dict[str, float], portfolio_value_cash: float) -> float:
        """
        Calculate current allocation ratio: fraction of portfolio in risky assets.

        Current allocation = (Market Value of All Holdings) / Cash Portfolio Value
        This measures how much of the portfolio is currently exposed to risky assets.

        Example calculation:
        - Portfolio cash value: $100,000
        - Holdings: 500 shares at $200 each = $100,000 market value
        - Current allocation: $100,000 / $100,000 = 1.0 (100% risky)

        Note: Can exceed 1.0 if using leverage/margin
        """
        stock_value = 0.0
        for m_id, pos in self.current_positions.items():
            if m_id in current_prices:
                stock_value += pos["shares"] * current_prices[m_id]

        if portfolio_value_cash > 0:
            return stock_value / portfolio_value_cash
        return 0.0

    def _should_balance(self, current_allocation: float, target_allocation: float) -> bool:
        """
        Determine whether portfolio balancing is warranted.

        Balancing is triggered when:
        1. Drift exceeds the balancing threshold AND
        2. Drift represents a material trade size

        This prevents excessive trading from minor allocation drifts.

        Logic:
        ```
        drift = |current - target|
        if drift < threshold:
            return False  (too small, ignore)
        if drift < min_trade_size:
            return False  (too small to trade economically)
        return True  (material drift, rebalance)
        ```

        Example with threshold=0.05, min_trade=0.01:
        - drift = 0.03: return False (below both thresholds)
        - drift = 0.07: return True (exceeds both thresholds)
        - drift = 0.02: return False (between thresholds)

        """
        allocation_drift = abs(current_allocation - target_allocation)

        if allocation_drift < self.balancing_threshold:
            return False

        if allocation_drift < self.min_trade_size:
            return False

        return True

    async def decide(self, messages: List[M2IMessage]) -> base.InvestorDecision:
        """
        Core decision logic for BehavioralInvestor.

        This is the main method that generates investment decisions based on
        current market conditions and behavioral factors.

        Execution flow:

        1. Record timing (message received, computation start)
        2. Extract market prices from messages
        3. Calculate realized returns for diagnostics
        4. Update psychological reference point
        5. Compute behavioral target allocation
        6. Assess current allocation
        7. Determine if balancing needed
        8. Generate trading actions
        9. Deduct transaction costs
        10. Compile diagnostics and reasoning
        11. Package decision with metadata
        """
        message_received_time = datetime.now().isoformat()
        await asyncio.sleep(self.computation_delay)
        decision_start_time = datetime.now().isoformat()

        # 1. read market info
        current_prices: Dict[str, float] = {}
        for msg in messages:
            market_id = msg.market_id
            info = msg.decision_content

            if isinstance(info, dict) and "current_price" in info:
                px = float(info["current_price"])
            else:
                px = float(info["clearing"]["price"])

            current_prices[market_id] = px
            self.price_history.append(px)

        # track realized return for diagnostics only
        if len(self.price_history) >= 2:
            p_old = self.price_history[-2]
            p_new = self.price_history[-1]
            realized_ret = (p_new - p_old) / p_old
            self.return_history.append(realized_ret)

        # 2. update reference level (psychological anchor)
        self._init_reference_level()
        self._update_reference_level()

        # 3. compute target allocation from behavioral rule
        target_allocation = self._target_allocation_behavioral()

        # 4. current allocation
        portfolio_value_cash = self._compute_portfolio_value()
        current_alloc = self._current_allocation(current_prices, portfolio_value_cash)

        # 5. rebalance decision
        should_rebalance = self._should_balance(current_alloc, target_allocation)

        actions: Dict[str, Dict[str, float]] = {}
        total_transaction_cost = 0.0
        reasoning_lines = []

        for m_id, px in current_prices.items():
            if should_rebalance or self._round_index == 0:
                # we interpret `target_allocation * portfolio_value_cash`
                # as the dollar value we want in risky exposure (vs cash)
                target_value = target_allocation * portfolio_value_cash
                target_shares = target_value / px if px > 0 else 0.0

                current_shares = self.current_positions.get(m_id, {}).get("shares", 0.0)
                shares_to_trade = target_shares - current_shares

                trade_notional = abs(shares_to_trade * px)
                txn_cost = trade_notional * self.transaction_cost_rate
                total_transaction_cost += txn_cost

                if m_id not in self.current_positions:
                    self.current_positions[m_id] = {
                        "shares": 0.0,
                        "avg_price": px,
                    }

                new_shares = current_shares + shares_to_trade
                self.current_positions[m_id]["shares"] = new_shares

                # update avg cost if net buying
                if shares_to_trade > 0:
                    old_val = current_shares * self.current_positions[m_id]["avg_price"]
                    new_val = shares_to_trade * px
                    tot_shares = current_shares + shares_to_trade
                    if tot_shares > 0:
                        self.current_positions[m_id]["avg_price"] = (old_val + new_val) / tot_shares

                actions[m_id] = {
                    "order_type": "market",
                    "shares": float(shares_to_trade),
                    "price": float(px),
                    "target_allocation": float(target_allocation),
                }

                reasoning_lines.append(
                    f"{m_id}: trade {shares_to_trade:.2f} @ ${px:.2f} "
                    f"(behavioral target alloc {target_allocation:.2%})"
                )

            else:
                actions[m_id] = {
                    "order_type": "hold",
                    "shares": 0.0,
                    "price": float(px),
                    "target_allocation": float(target_allocation),
                }

                reasoning_lines.append(
                    f"{m_id}: HOLD (drift {abs(current_alloc - target_allocation):.2%} "
                    f"< thresh {self.balancing_threshold:.2%})"
                )

        # 6. pay transaction costs out of cash bucket
        self.wealth -= total_transaction_cost
        self.total_transaction_costs += total_transaction_cost

        # 7. diagnostics / narrative for logging
        sigma_tilde = self._subjective_volatility()
        delta_r = self.reference_level - self.wealth

        reasoning = (
            "[Type II Behavioral Investor]\n"
            f"Reference level r0={self.reference_level:.2f}, current wealth={self.wealth:.2f}, Δr={delta_r:.2f}\n"
            f"Perceived risk σ_tilde={sigma_tilde:.2%} (kappa={self.risk_perception_kappa:.2f})\n"
            f"Target allocation={target_allocation:.2%}, current allocation={current_alloc:.2%}\n"
            f"{'Rebalance' if should_rebalance else 'No Rebalance'} | "
            f"TxnCost=${total_transaction_cost:.2f}\n"
            + "\n".join(reasoning_lines)
        )

        # "confidence" here can be interpreted as commitment to its own psychology,
        # not statistical confidence. We bound it in [0,1] for API consistency.
        # A simple choice: high confidence if kappa<1 (overconfident), else medium.
        base_conf = 0.8 if self.risk_perception_kappa < 1.0 else 0.6
        confidence = min(max(base_conf, 0.0), 1.0)

        # sanity / policy violations
        violations = {}
        if target_allocation > self.max_position_size:
            violations["max_position"] = (
                f"Target {target_allocation:.2%} > max {self.max_position_size:.2%}"
            )
        if (1 - target_allocation) < self.min_cash_reserve:
            violations["min_cash"] = (
                f"Cash {(1 - target_allocation):.2%} < min {self.min_cash_reserve:.2%}"
            )

        # Sharpe-like stat for monitoring (not driving behavior)
        self.portfolio_value_history.append(portfolio_value_cash)
        sharpe_ratio = 0.0
        if len(self.return_history) >= 5:
            arr = np.array(list(self.return_history))
            mean_r = np.mean(arr)
            std_r = np.std(arr)
            if std_r > 0:
                sharpe_ratio = (
                    (mean_r - self.risk_free_rate / self.annualization_factor) / std_r
                )

        self._round_index += 1

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
                "current_allocation": float(current_alloc),
                "reference_level": float(self.reference_level),
                "delta_reference": float(delta_r),
                "subjective_volatility": float(sigma_tilde),
                "risk_perception_kappa": float(self.risk_perception_kappa),
                "transaction_costs_total": float(self.total_transaction_costs),
                "sharpe_like": float(sharpe_ratio),
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
                    "current_position": self.current_positions.get(market_id, {}),
                    "reference_level": float(self.reference_level),
                    "risk_perception_kappa": float(self.risk_perception_kappa),
                    "subjective_volatility": float(self._subjective_volatility()),
                    "decision_mode": str(self.decision_mode),
                }
            )

            i2m_messages.append(msg)

        return i2m_messages
