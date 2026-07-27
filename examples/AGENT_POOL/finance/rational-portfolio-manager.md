# Rational whole-portfolio manager

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Rational whole-portfolio manager |
| Theory Family         | Modern Portfolio Theory / Rational Choice |
| Behavioral Tendency   | **Converging** — trades contrarian to price deviations, pushing price back toward equilibrium through rational mean-variance optimization |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a fully rational portfolio manager who evaluates the entire portfolio as a single unit without mental accounting, making contrarian trades proportional to price deviations scaled by risk aversion. The real-world counterpart is a quantitative fund manager, institutional optimizer, or mean-variance allocator who follows Markowitz-style portfolio theory without behavioral biases.

The decision goal is to output a buy or sell order (or hold) with quantity determined by the deviation of current price from a reference level, scaled by a risk aversion coefficient. The agent trades contrarian — buying when price is below reference and selling when above — with sizing proportional to the deviation magnitude.

In simulation this agent serves as a rational benchmark against which mental accounting agents are compared. It demonstrates the stabilizing properties of whole-portfolio evaluation versus per-account segregation. Non-goals: (1) it must not segregate positions into mental accounts; (2) it must not exhibit outcome-dependent risk preferences.

## Theoretical Foundation

**Mean-Variance Portfolio Theory**:
- Theory / Study: Portfolio selection
- Citation: Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77-91. DOI:10.2307/2975974
- Core Insight: A rational investor evaluates the entire portfolio jointly, optimizing the trade-off between expected return and variance. This whole-portfolio perspective prevents the sub-optimal behaviors that arise from evaluating positions individually (mental accounting). The optimal holding is proportional to expected excess return divided by risk aversion times variance.
- Mathematical Formulation: `w* = (1 / gamma) * Sigma^{-1} * (mu - r_f)`; in single-asset form: `quantity ~ |deviation| * risk_aversion_scale`
- Empirical Evidence: DeMiguel et al. (2009) show mean-variance portfolios achieve Sharpe ratios 0.1-0.3 higher than naive 1/N in 7 empirical datasets when properly calibrated; Markowitz's framework remains the foundation of institutional portfolio management.
- Relevance to This Agent: The agent implements the contrarian implication of mean-variance optimization — buying undervalued (price below reference) and selling overvalued assets proportional to the mispricing.
- Calibration Source: Markowitz (1952); Campbell & Viceira (2002): risk aversion coefficients of 0.5-2.0 for institutional investors; quantity_scale calibrated to produce comparable activity to mental accounting agents.
- Falsification Conditions: If this agent trades in the same direction as the price deviation (momentum) or sizes independently of deviation magnitude, the rational mean-reversion mechanism is absent.
- Alternative Theories: Behavioral portfolio theory (Shefrin & Statman 2000); mental accounting (Thaler 1999); risk parity.

**Rational Benchmark Against Mental Accounting**:
- Theory / Study: Mental accounting, loss aversion, and individual stock returns
- Citation: Barberis, N. & Huang, M. (2001). Mental accounting, loss aversion, and individual stock returns. *Journal of Finance*, 56(4), 1247-1292. DOI:10.1111/0022-1082.00367
- Core Insight: The deviation between mental accounting behavior and rational whole-portfolio optimization generates welfare losses and predictable patterns in asset returns. A rational benchmark that evaluates portfolio-level risk and return demonstrates the inefficiencies introduced by narrow framing.
- Mathematical Formulation: `rational_utility = E[U(W_total)] vs mental_accounting_utility = sum_i E[v(x_i)]`
- Empirical Evidence: Barberis & Huang (2001) show that narrow framing can explain 3-5% equity premium above rational models; Benartzi & Thaler (1995) document 6.5% welfare loss from myopic loss aversion.
- Relevance to This Agent: Serves as the rational comparator — same market, same information, but whole-portfolio evaluation produces systematically different (more stabilizing) behavior.
- Calibration Source: Barberis & Huang (2001): rational agent risk aversion 0.5-1.0 in their calibrated model.
- Falsification Conditions: If this agent exhibits disposition effect (selling winners more readily than losers), the rational framework is violated.
- Alternative Theories: Bounded rationality (Simon 1955); satisficing rather than optimizing.

## Design Purpose and Activation Triggers

Purpose: Provide rational contrarian demand proportional to price deviations as a benchmark against behavioral agents.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `prev_price` available (for deviation computation)

Missing-Signal Policy: hold if price or prev_price unavailable.

Activation Triggers:
- `|deviation| > deviation_threshold (0.02)`: trade contrarian with deviation-proportional sizing.
- `<Default>`: hold (deviation too small).

Deactivation Conditions:
- Deviation below threshold: hold.
- No price data: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large deviation (price far from prev) | Larger contrarian trade (proportional to |deviation|) | Rational response scales linearly with mispricing |
| Small deviation (within threshold) | No trade | Transaction cost avoidance in rational framework |

Environmental Dependencies: Requires per-tick `price` and `prev_price`. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price |
| `prev_price` | environment | `float` | yes | Previous price for deviation |
| `round` | scheduler | `int` | yes | Current round |
| `identity` | scheduler | `str` | yes | Agent identity |
| `retrieved_knowledge` | retrieval store | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action |
| `quantity` | float | `[0, 500]` | shares | yes | Unsigned trade magnitude |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` MUST be present.
- Forbidden fields: no undeclared fields.
- Value ranges: `quantity` in `[0, base_size]` = `[0, 500]`.
- Units and sign conventions: `quantity` is unsigned; direction carried by `action`.
- Determinism markers: deterministic; no seed.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
                "quantity": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON matching Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"`.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price for deviation |
| `prev_price` | Continuous | 1 tick | Reference for deviation computation |

Does NOT use: `entry_price`, P&L history, mental accounts, fundamental value, order book, peer positions.

#### Core Behavioral Mechanism

1. **Read** `price`, `prev_price`. *(implementation convenience)*
2. **Compute** `deviation = (price - prev_price) / prev_price`. *(Markowitz 1952 — deviation from reference)*
3. **Check** activation: if `|deviation| < deviation_threshold`: hold. *(implementation convenience — transaction cost avoidance)*
4. **Compute** `raw_quantity = int(|deviation| * risk_aversion * quantity_scale)`. *(Markowitz 1952 — proportional response)*
5. **Clamp** `quantity = min(base_size, raw_quantity)`. *(implementation convenience — capacity cap)*
6. **Determine** direction (contrarian): if `deviation > 0`: action=sell; if `deviation < 0`: action=buy. *(Markowitz 1952 — buy low, sell high)*
7. **Write** no persistent state; position updated by engine post-fill.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price |
| Sizing rule | `quantity = min(base_size, int(|deviation| * risk_aversion * quantity_scale))` |
| Action lifetime | 1 tick |
| Revision policy | No revision; recomputes each tick |
| State constraint | No explicit position cap |
| Resource cap | base_size = 500 maximum per tick |
| Exit rule | None |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` per tick.

**Decision logic formalization:**
```
deviation = (price - prev_price) / prev_price

IF |deviation| < deviation_threshold:
    action = hold; quantity = 0
ELSE:
    raw_quantity = int(|deviation| * risk_aversion * quantity_scale)
    quantity = min(base_size, raw_quantity)
    IF deviation > 0: action = sell  # contrarian
    ELIF deviation < 0: action = buy  # contrarian
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `prev_price` | float | first observed price | post-decide |
| `position` | float | 0 | post-execution |

**State evolution:** prev_price updates after each decision. Position updated by engine.

**Determinism contract:** Fully deterministic given price path.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `risk_aversion` | Sensitivity to deviations | 0.7 | Markowitz (1952); Campbell & Viceira (2002) |
| `base_size` | Maximum trade quantity | 500 | Standardised |
| `quantity_scale` | Converts deviation * risk_aversion to shares | 3000 | Standardised |
| `deviation_threshold` | Minimum deviation for trading | 0.02 | Standardised |

#### Behavioral Properties

- Time horizon: medium — responds to single-period deviations but maintains persistent positions.
- Risk tolerance: medium — trades proportional to deviation with risk_aversion dampening.
- Information asymmetry: none — uses only observable price.
- Psychological profile: fully rational; no loss aversion, no mental accounting, no outcome dependence; pure mean-variance optimization.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `risk_aversion` | float | 0.7 | [0.1, 3.0] | high | Coefficient scaling deviation to trade size | Higher -> larger trades per unit deviation; more aggressive stabilization | Markowitz (1952); Barberis & Huang (2001) |
| `base_size` | float | 500 | [100, 2000] | medium | Maximum single-tick trade quantity | Higher -> larger absolute market impact capacity | Standardised |
| `quantity_scale` | float | 3000 | [500, 10000] | high | Multiplier converting deviation*risk_aversion to shares | Higher -> more responsive to small deviations | Standardised |
| `deviation_threshold` | float | 0.02 | [0.005, 0.10] | medium | Minimum price deviation to trigger trade | Higher -> fewer trades; only responds to large moves | Standardised |

## Worked Numerical Examples

### Case 1 — Buy (price fell, contrarian)
```text
System state: price=97, prev_price=100, risk_aversion=0.7, quantity_scale=3000, base_size=500, deviation_threshold=0.02.
Calculation:
  deviation = (97 - 100) / 100 = -0.03
  |deviation| = 0.03 > 0.02 -> activated
  raw_quantity = int(0.03 * 0.7 * 3000) = int(63) = 63
  quantity = min(500, 63) = 63
  deviation < 0 -> contrarian buy
Decision: buy 63 shares.
State update: position increases by 63.
```

### Case 2 — Sell (price rose, contrarian)
```text
System state: price=105, prev_price=100, risk_aversion=0.7, quantity_scale=3000, base_size=500, deviation_threshold=0.02.
Calculation:
  deviation = (105 - 100) / 100 = 0.05
  |deviation| = 0.05 > 0.02 -> activated
  raw_quantity = int(0.05 * 0.7 * 3000) = int(105) = 105
  quantity = min(500, 105) = 105
  deviation > 0 -> contrarian sell
Decision: sell 105 shares.
State update: position decreases by 105.
```

### Case 3 — Hold (small deviation)
```text
System state: price=100.5, prev_price=100, deviation_threshold=0.02.
Calculation:
  deviation = (100.5 - 100) / 100 = 0.005
  |deviation| = 0.005 < 0.02 -> NOT activated
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Large deviation capped at base_size
```text
System state: price=80, prev_price=100, risk_aversion=0.7, quantity_scale=3000, base_size=500.
Calculation:
  deviation = (80 - 100) / 100 = -0.20
  |deviation| = 0.20 > 0.02 -> activated
  raw_quantity = int(0.20 * 0.7 * 3000) = int(420) = 420
  quantity = min(500, 420) = 420
  deviation < 0 -> contrarian buy
Decision: buy 420 shares.
State update: position increases by 420.

Extreme: deviation=-0.50, raw=int(0.5*0.7*3000)=1050, capped to 500.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `risk_aversion` <- Campbell & Viceira (2002): institutional risk aversion 0.5-2.0; Barberis & Huang (2001): rational agent gamma = 0.5-1.0.
- `quantity_scale` <- Standardised to produce comparable order sizes to mental accounting agents.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price below prev_price by more than threshold, agent MUST buy (contrarian).
- Given price above prev_price by more than threshold, agent MUST sell (contrarian).
- Given |deviation| < threshold, agent MUST hold regardless of P&L history.

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent trades in the same direction as deviation (momentum) THEN broken because rational agent is contrarian.
- IF agent's quantity depends on prior P&L (house money effect) THEN broken because rational agent has no outcome dependence.
- IF agent's quantity exceeds base_size THEN broken because capacity cap is violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `high_risk_aversion` | `risk_aversion=2.0` | Higher risk aversion creates stronger stabilization | increase in contrarian trade sizes | Average quantity per trade |
| `low_threshold` | `deviation_threshold=0.005` | Lower threshold increases trade frequency | increase in total number of trades | Trade count per run |
| `small_capacity` | `base_size=100` | Reduced capacity weakens stabilization power | decrease in price stabilization effectiveness | Price volatility in simulation |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77-91. DOI:10.2307/2975974 | Mean-variance framework; whole-portfolio evaluation |
| 2 | Barberis, N. & Huang, M. (2001). Mental accounting, loss aversion, and individual stock returns. *Journal of Finance*, 56(4), 1247-1292. DOI:10.1111/0022-1082.00367 | Rational benchmark vs mental accounting |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-rational-portfolio-manager.png)         |
