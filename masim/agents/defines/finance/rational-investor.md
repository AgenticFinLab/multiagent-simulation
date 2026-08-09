# Rational expected-utility investor

## Summary

| Field                 | Content                                                                                        |
|-----------------------|------------------------------------------------------------------------------------------------|
| Archetype             | Rational expected-utility investor                                                             |
| Theory Family         | Neoclassical Finance / Expected Utility Theory                                                 |
| Behavioral Tendency   | **Converging** — rebalances portfolio toward target allocation, pulling prices toward equilibrium |
| Time Horizon          | medium                                                                                         |
| Risk Tolerance        | medium                                                                                         |
| Information Asymmetry | none                                                                                           |
| Determinism           | deterministic                                                                                  |

## Definition and Goals

This agent models a rational expected-utility maximizer with a fixed target portfolio allocation who rebalances when drift exceeds a threshold. The real-world counterpart is the disciplined portfolio manager or robo-advisor following a constant-mix strategy as derived from Merton's (1969) portfolio problem under constant relative risk aversion (CRRA). Such investors include systematic allocation funds, target-risk ETFs, and individually managed accounts with rebalancing mandates.

The decision goal is to maintain portfolio weight near `target_allocation` by executing rebalancing trades when the current allocation drifts beyond `rebalance_threshold`. The agent computes the gap between current and target allocation and closes a fraction (`rebalance_speed`) of that gap each tick. The criterion is mean-variance optimal allocation maintenance under CRRA preferences.

Inside the simulation this agent provides stabilising counter-cyclical order flow — it buys when the risky asset is underweight (typically after price drops) and sells when overweight (after price rises). This creates natural mean-reversion pressure. **Non-goals:** (1) The agent must NOT exhibit any behavioral bias — no reference-point dependence, no loss aversion, no disposition effect. (2) The agent must NOT attempt to forecast future returns or time the market. (3) The agent must NOT use momentum, sentiment, or peer-position signals.

## Theoretical Foundation

**Expected Utility Theory and CRRA Preferences**:
- Theory / Study: Theory of games and economic behavior / Lifetime portfolio selection.
- Citation: Merton, R. C. (1969). Lifetime portfolio selection under uncertainty: The continuous-time case. *Review of Economics and Statistics*, 51(3), 247-257. https://doi.org/10.2307/1926560
- Core Insight: Under constant relative risk aversion and iid returns, the optimal fraction of wealth invested in the risky asset is constant over time, equal to `(mu - r) / (gamma * sigma^2)` where mu is expected return, r is risk-free rate, gamma is risk aversion, and sigma is volatility. Deviations from this target should be corrected through rebalancing.
- Mathematical Formulation: `target_weight = (mu - r) / (gamma * sigma^2)`; rebalancing trade: `q = rebalance_speed * (target_allocation - current_allocation) * wealth / price`
- Empirical Evidence: Perold & Sharpe (1988) document that constant-mix rebalancing achieves concave payoff profiles and outperforms buy-and-hold in range-bound markets. DeMiguel et al. (2009) find that 1/N allocation with periodic rebalancing matches or beats optimized portfolios out of sample (Sharpe ratio difference < 0.02, n=7 datasets).
- Relevance to This Agent: The agent implements constant-mix rebalancing toward a fixed target, directly operationalising the Merton solution under simplified assumptions.
- Calibration Source: Merton (1969) equation; target_allocation = 0.5 represents moderate risk aversion (gamma ≈ 2-4 with historical equity premium). Rebalance_threshold 5-15% from practitioner literature (Daryanani 2008).
- Falsification Conditions: If the agent does not rebalance within 1 tick of current allocation exceeding target by more than rebalance_threshold, its rational mandate is falsified.
- Alternative Theories: Prospect-theory portfolio choice (non-CRRA); dynamic strategies (CPPI, Perold & Sharpe 1988); Kelly criterion (full-Kelly, no threshold).

**Efficient Market Hypothesis (Weak Form)**:
- Theory / Study: Efficient capital markets: A review of theory and empirical work.
- Citation: Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *Journal of Finance*, 25(2), 383-417. https://doi.org/10.2307/2325486
- Core Insight: Under weak-form efficiency, past prices contain no exploitable information about future returns. This justifies the agent's deliberate non-use of momentum, technical, or timing signals — it treats expected returns as constant and simply maintains its optimal weight.
- Mathematical Formulation: `E[r_t | r_{t-1}, r_{t-2}, ...] = mu` (constant expected return independent of past prices).
- Empirical Evidence: Fama (1970) reviews evidence that serial correlations in stock returns are near zero (r < 0.03) for daily data, supporting the random walk model. Malkiel (2003) updates: fewer than 10% of active mutual funds beat passive benchmarks over 10-year horizons.
- Relevance to This Agent: The agent does not attempt to forecast returns or time the market — it simply rebalances to maintain its constant-mix target, consistent with treating prices as a random walk around equilibrium.
- Calibration Source: Fama (1970) — serial correlation coefficients near zero for major stock indices. Constant expected return assumed equal to historical equity premium (~6-8% annually).
- Falsification Conditions: If the agent modifies its target_allocation based on recent price history or any momentum signal, it violates the constant-mix / EMH foundation.
- Alternative Theories: Technical analysis (contradicts EMH); adaptive markets hypothesis (Lo 2004); behavioral biases creating predictable patterns.

## Design Purpose and Activation Triggers

Purpose: Maintain a fixed risky-asset allocation by rebalancing toward target weight when portfolio drift exceeds threshold, providing counter-cyclical stabilising flow.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `position` available (own state)
- `cash` available (own state)

Missing-Signal Policy: hold when any required signal is unavailable or stale.

Activation Triggers:
- `abs(current_allocation - target_allocation) > rebalance_threshold` and current_allocation > target_allocation: sell (overweight — reduce risky asset).
- `abs(current_allocation - target_allocation) > rebalance_threshold` and current_allocation < target_allocation: buy (underweight — increase risky asset).
- `<Default>`: hold (within tolerance band).

Deactivation Conditions:
- Cash exhausted and underweight: cannot buy, forced to hold until cash arrives.
- Position zero and overweight: impossible state (already at 0% allocation).

Behavioral Adaptation by Condition:
| Condition              | Behavioral change                      | Mechanism                                   |
|------------------------|----------------------------------------|---------------------------------------------|
| Price drop (underweight) | Buy to restore target allocation     | Counter-cyclical rebalancing                |
| Price rise (overweight)  | Sell to restore target allocation    | Counter-cyclical rebalancing                |
| Flat market (within band)| Hold                                 | Drift within tolerance — no action needed   |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input      | Source      | Type / Shape | Required? | Notes                          |
|------------|-------------|--------------|-----------|--------------------------------|
| `price`    | environment | float        | yes       | current market price           |
| `position` | own state   | float        | yes       | current shares held            |
| `cash`     | own state   | float        | yes       | available capital              |
| `round`    | scheduler   | int          | yes       | current simulation round       |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                      |
|-------------|--------|---------------------------------|--------|-----------|------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | trade direction              |
| `quantity`  | float  | `>= 0`                         | shares | yes       | number of shares to trade    |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | audit trail for the decision |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` must be present on every call.
- Forbidden fields: no fields beyond the three declared.
- Value ranges: `quantity` clamped to `[0, position]` for sells; `[0, cash/price]` for buys.
- Units: quantity in shares; price in environment currency units.
- Sign conventions: positive quantity always; direction conveyed by `action` field.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning, 1-3 sentences...</analysis>
<decision>{"action": "buy|sell|hold", "quantity": 0.0, "reasoning": "..."}</decision>
```

Rules: (1) Tags are literal ASCII, not optional. (2) Decision block contains valid JSON matching Outputs table. (3) Rule-driven variants generate analysis from deterministic template. (4) Model-driven variants must include tag+JSON requirement in prompt.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth.** On conflict with prose elsewhere, this section wins. (1) Signal wiring: every input row maps to a real read. (2) Decision emission: populate all required fields, clamp out-of-range values. (3) Prompt drafting: spell out tag pattern and JSON schema literally. (4) Parser tests: verify tags, parse JSON, assert fields in range. (5) Variant parity: all variants produce same field set. (6) Contract wins on conflict.

#### Decision Information Set

| Signal     | Type       | Memory Window | Rationale                                          |
|------------|------------|---------------|----------------------------------------------------|
| `price`    | Continuous | 1 tick        | Required to compute current portfolio allocation   |
| `position` | State      | persistent    | Needed to calculate risky-asset weight             |
| `cash`     | State      | persistent    | Needed to calculate total wealth and buy capacity  |

Does NOT use: fundamental value estimates, momentum signals, past returns, technical indicators, peer positions, sentiment, volume, volatility measures, or any forecasting model. Treats expected returns as constant per EMH.

#### Core Behavioral Mechanism

1. **Read inputs.** Read `price`, `position`, `cash` from environment and own state. (Implementation convenience — no theoretical claim.)
2. **Compute total wealth.** Calculate `wealth = position * price + cash`. Read: position, price, cash. Write: wealth (transient). (Implementation convenience.)
3. **Compute current allocation.** Calculate `current_allocation = (position * price) / wealth`. Read: position, price, wealth. Write: current_allocation (transient). [Traces to Merton (1969) — monitoring portfolio weight.]
4. **Compute allocation gap.** Calculate `gap = current_allocation - target_allocation`. Read: current_allocation, target_allocation. Write: gap (transient). [Traces to constant-mix rebalancing theory.]
5. **Evaluate rebalancing trigger.** If `abs(gap) > rebalance_threshold`, proceed to trade calculation; otherwise hold. Read: gap, rebalance_threshold. Write: trigger flag. [Traces to threshold-rebalancing literature (Daryanani 2008).]
6. **Compute rebalancing trade.** `trade_value = rebalance_speed * gap * wealth`. If gap > 0 (overweight): sell `q = min(trade_value / price, position)`. If gap < 0 (underweight): buy `q = min(abs(trade_value) / price, cash / price)`. Read: gap, rebalance_speed, wealth, price, position, cash. Write: action, quantity. [Traces to Merton (1969) constant-mix optimal.]
7. **Emit decision object.** Serialize in canonical format. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                          |
|-----------------------|------------------------------------------------------------------------|
| Action types allowed  | buy, sell, hold                                                        |
| Action parameter rule | market order at current price                                          |
| Sizing rule           | `rebalance_speed * abs(gap) * wealth / price`, clamped by constraints  |
| Action lifetime       | one decision call (immediate execution)                                |
| Revision policy       | previous intent replaced each tick                                     |
| State constraint      | position >= 0 (no short selling); allocation in [0, 1]                 |
| Resource cap          | buy quantity <= cash / price; sell quantity <= position                 |
| Exit rule             | none — agent rebalances indefinitely                                   |

#### Mathematical Model

**Decision output:** Action `a` in {buy, sell, hold} and quantity `q >= 0` per tick.

**Decision logic formalization:**

```
wealth = position * price + cash
current_allocation = (position * price) / wealth
gap = current_allocation - target_allocation

If abs(gap) > rebalance_threshold:
    trade_value = rebalance_speed * gap * wealth
    If gap > 0:  # overweight -> sell
        a = sell
        q = min(trade_value / price, position)
    Else:  # underweight -> buy
        a = buy
        q = min(abs(trade_value) / price, cash / price)
Else:
    a = hold
    q = 0
```

**State variables:**

| Variable   | Type  | Initial Value    |
|------------|-------|------------------|
| `position` | float | scenario-defined |
| `cash`     | float | scenario-defined |

**State evolution:**
- Post-execution:
  - Buy: `position += q_filled`; `cash -= q_filled * fill_price`.
  - Sell: `position -= q_filled`; `cash += q_filled * fill_price`.
  - Hold: no state change.
- Update phase: post-execution only.

**Determinism contract:** Fully deterministic. No stochastic component.

**Parameter symbol table:**

| Symbol                | Meaning                              | Default Value | Source                    |
|-----------------------|--------------------------------------|---------------|---------------------------|
| `target_allocation`   | Target fraction of wealth in risky asset | 0.50      | Merton (1969) for gamma ≈ 2 |
| `rebalance_threshold` | Drift tolerance before rebalancing   | 0.10          | Daryanani (2008)          |
| `rebalance_speed`     | Fraction of gap closed per rebalance | 0.50          | Practitioner convention   |

#### Behavioral Properties

- Time horizon: medium — rebalances over multi-tick cycles but does not hold indefinitely without action.
- Risk tolerance: medium — targets 50% risky-asset allocation, neither leveraged nor fully defensive.
- Information asymmetry: none — uses only price and own state, no private information.
- Psychological profile: fully rational; no behavioral biases; no reference dependence; no loss aversion. Embodies von Neumann-Morgenstern expected utility with CRRA preferences.

## Parameters

| Parameter             | Type  | Default | Valid Range   | Sensitivity | Description                            | Impact                                         | Source                    |
|-----------------------|-------|---------|---------------|-------------|----------------------------------------|------------------------------------------------|---------------------------|
| `target_allocation`   | float | 0.50    | [0.10, 0.90]  | high        | Target fraction of wealth in risky asset | Higher -> more equity exposure, larger buys on dips | Merton (1969)            |
| `rebalance_threshold` | float | 0.10    | [0.02, 0.25]  | high        | Drift tolerance before rebalancing     | Higher -> less frequent trading, wider bands   | Daryanani (2008)          |
| `rebalance_speed`     | float | 0.50    | [0.10, 1.00]  | medium      | Fraction of gap closed per rebalance   | Higher -> faster convergence to target         | Practitioner convention   |

## Worked Numerical Examples

### Case 1 — Underweight rebalancing (buy)

System state: price = 80.0, position = 50, cash = 6000, target_allocation = 0.50, rebalance_threshold = 0.10, rebalance_speed = 0.50.
Calculation:
  wealth = 50 * 80.0 + 6000 = 10000
  current_allocation = (50 * 80.0) / 10000 = 0.40
  gap = 0.40 - 0.50 = -0.10
  abs(-0.10) = 0.10 >= 0.10 (rebalance_threshold) -> rebalance triggered
  trade_value = 0.50 * (-0.10) * 10000 = -500 (negative = buy)
  q = min(abs(-500) / 80.0, 6000 / 80.0) = min(6.25, 75.0) = 6.25
Decision: buy 6.25 shares at 80.0.
State update: position: 50 -> 56.25; cash: 6000 -> 5500.

### Case 2 — Overweight rebalancing (sell)

System state: price = 120.0, position = 50, cash = 2000, target_allocation = 0.50, rebalance_threshold = 0.10, rebalance_speed = 0.50.
Calculation:
  wealth = 50 * 120.0 + 2000 = 8000
  current_allocation = (50 * 120.0) / 8000 = 0.75
  gap = 0.75 - 0.50 = 0.25
  abs(0.25) = 0.25 > 0.10 -> rebalance triggered
  trade_value = 0.50 * 0.25 * 8000 = 1000 (positive = sell)
  q = min(1000 / 120.0, 50) = min(8.33, 50) = 8.33
Decision: sell 8.33 shares at 120.0.
State update: position: 50 -> 41.67; cash: 2000 -> 3000.

### Case 3 — Hold (within threshold)

System state: price = 100.0, position = 50, cash = 5500, target_allocation = 0.50, rebalance_threshold = 0.10.
Calculation:
  wealth = 50 * 100.0 + 5500 = 10500
  current_allocation = 5000 / 10500 = 0.476
  gap = 0.476 - 0.50 = -0.024
  abs(-0.024) = 0.024 < 0.10 -> no rebalance
Decision: hold.
State update: no change.

### Edge Case — Insufficient cash for full rebalance

System state: price = 50.0, position = 30, cash = 200, target_allocation = 0.50, rebalance_threshold = 0.10, rebalance_speed = 0.50.
Calculation:
  wealth = 30 * 50.0 + 200 = 1700
  current_allocation = 1500 / 1700 = 0.882
  gap = 0.882 - 0.50 = 0.382
  abs(0.382) > 0.10 -> rebalance triggered
  trade_value = 0.50 * 0.382 * 1700 = 324.7 (positive = sell)
  q = min(324.7 / 50.0, 30) = min(6.49, 30) = 6.49
Decision: sell 6.49 shares at 50.0.
State update: position: 30 -> 23.51; cash: 200 -> 524.7.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `target_allocation` <- Merton (1969) optimal risky-asset share for gamma = 2, mu = 0.08, sigma = 0.16 gives ~0.50
- `rebalance_threshold` <- Daryanani (2008) optimal threshold for tax-free accounts: 5-15% depending on volatility
- `rebalance_speed` <- Practitioner standard partial-rebalancing at 50% of gap per period

**Expected individual behaviour:**
- Given current allocation 15% above target (overweight), agent MUST sell to reduce allocation.
- Given current allocation 12% below target (underweight), agent MUST buy to increase allocation.
- Given allocation within 10% of target, agent MUST hold.
- Given missing price signal, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when overweight (current_allocation > target + threshold) THEN broken: rebalancing logic inverted.
- IF agent sells when underweight (current_allocation < target - threshold) THEN broken: rebalancing logic inverted.
- IF agent trades when abs(gap) < rebalance_threshold THEN broken: threshold not enforced.
- IF agent uses price history, momentum, or external forecasts THEN broken: violates rational constant-mix design.

#### Ablation Hooks

| Ablation name       | Setting                        | Hypothesis tested                          | Expected direction | Metric                    |
|---------------------|--------------------------------|--------------------------------------------|--------------------|---------------------------|
| no-rebalancing      | `rebalance_threshold = 1.0`    | Rebalancing provides counter-cyclical flow | decrease           | Counter-cyclical trade volume |
| aggressive-rebalance| `rebalance_speed = 1.0`        | Faster rebalancing increases mean-reversion| increase           | Allocation tracking error  |
| conservative-target | `target_allocation = 0.30`     | Lower equity target reduces buy-on-dip flow| decrease           | Buy volume after drops     |

## Academic References

| # | Citation                                                                                                                                           | Notes                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| 1 | Merton, R. C. (1969). Lifetime portfolio selection under uncertainty: The continuous-time case. *Review of Economics and Statistics*, 51(3), 247-257. https://doi.org/10.2307/1926560 | Optimal constant-mix allocation    |
| 2 | von Neumann, J. & Morgenstern, O. (1944). *Theory of Games and Economic Behavior*. Princeton University Press. ISBN 978-0691130613.               | Expected utility axioms            |
| 3 | Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *Journal of Finance*, 25(2), 383-417. https://doi.org/10.2307/2325486 | EMH justification for no timing    |
| 4 | Perold, A. F. & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*, 44(1), 16-27. https://doi.org/10.2469/faj.v44.n1.16 | Constant-mix vs. CPPI              |
| 5 | DeMiguel, V., Garlappi, L., & Uppal, R. (2009). Optimal versus naive diversification. *Review of Financial Studies*, 22(5), 1915-1953. https://doi.org/10.1093/rfs/hhm075 | 1/N performance                    |

## Design Provenance and Versioning

| Field   | Content                                                  |
|---------|----------------------------------------------------------|
| Author  | Codex                                                    |
| Created | 2026-07-16                                               |
| Version | 1.0.0                                                    |
| Icon    | ![](../agent_images/icons/finance-rational-investor.png) |
| Status  | draft                                                    |
