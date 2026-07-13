# Fundamental-value rational updater

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Fundamental-value rational updater |
| Theory Family         | Quant |
| Behavioral Tendency   | **Converging — updates beliefs toward the observable fundamental using a Bayesian-style rule; converges on fundamental value** |
| Market Role           | **Stabilising** - corrects price deviations from fundamental value |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |
## Definition and Goals

This agent models a rational arbitrageur or disciplined analyst who uses observable fundamental value without behavioral distortion. The real-world counterpart is an arbitrageur, statistical arbitrageur, or fundamentalist using the same public information as other traders.

The decision goal is to output a signed trade quantity from the price-fundamental deviation. It buys undervaluation, sells overvaluation, and holds inside a no-trade band.

In simulation this agent helps produce bounded mispricing and negligible linear return autocorrelation when sufficiently represented. Non-goals: it must not anchor, chase momentum, or create random liquidity shocks.

## Theoretical Foundation

**Efficient Markets and Costly Information**:
- Theory / Study: Efficient markets and the Grossman-Stiglitz information paradox.
- Citation: Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *Journal of Finance*, 25(2), 383-417. https://doi.org/10.2307/2325486; Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408.
- Core Insight: Prices tend toward available fundamental information, but correction requires informed agents with incentives to trade. This agent is the corrective benchmark.
- Mathematical Formulation: `deviation = (P - F) / F`; sell if positive above threshold, buy if negative below threshold.
- Empirical Evidence: Liquid markets show rapid incorporation of public information, while information costs prevent perfect efficiency.
- Relevance to This Agent: It operationalises the unbiased corrective force against biased traders.
- Calibration Source: Fama (1970); Grossman & Stiglitz (1980).
- Falsification Conditions: If it buys when `P > F` or sells when `P < F`, the rule is inverted.
- Alternative Theories: Anchoring and insufficient adjustment; conservative learning.

**Rational Expectations Benchmark**:
- Theory / Study: Rational expectations.
- Citation: Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315-335. https://doi.org/10.2307/1905537
- Core Insight: Agents use all available information consistently with the true model. Forecast errors should not be systematically predictable from public information.
- Mathematical Formulation: `E[P(t+1) | I(t)] = F(t)`.
- Empirical Evidence: The source scenario uses this as the benchmark against anchoring and underreaction.
- Relevance to This Agent: The agent uses the true deviation `(price - fundamental) / fundamental` without bias.
- Calibration Source: Muth (1961); Fama (1970).
- Falsification Conditions: If forecast errors are serially biased for this agent, it is not rational-updating.
- Alternative Theories: Grossman & Stiglitz (1980) partial efficiency under costly information.

## Design Purpose and Activation Triggers

Purpose: Provide a no-bias benchmark that pushes price toward fundamental value.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available

Missing-Signal Policy: hold if either signal is missing, NaN, or stale.

Activation Triggers:
- `deviation < -threshold`: submit buy order.
- `deviation > threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached: hibernate constrained side.
- Cash floor breached: hibernate buy side.


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| High signal noise | Shrinks the Bayesian update step; relies more on the prior | Posterior precision falls as signal variance rises |
| Structural break in `fundamental` | Converges slowly because the prior is anchored on pre-break observations | Prior mean is weighted by historical precision |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Stabilising | Corrects small deviations from `F`. |
| Stress | Stabilising | Supplies arbitrage flow against large mispricing. |

Interaction with other agents: Opposes AnchoredTrader and HistoricalAnchor; complements FundamentalAnalyst.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `fundamental` | environment | `float` | yes | Maps to §3.6.1 `fundamental`. |
| `deviation` | environment | `float` | yes | Maps to §3.6.1 `deviation`. |
| `identity`, `round` | round header | `str`, `int` | yes | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|---|---|---|---|---|---|
| `action` | enum | {"market", "hold-no-op"} | — | yes | Discrete action selected this call. |
| `quantity` | float | `[0, base_position_size]` | shares | conditional | Order magnitude; 0 when `action = hold`. |
| `price_level` | float | `= price` (market order) | currency | conditional | Execution reference; equals observed `price` for market orders. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_position_size]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `fundamental` and `price`.
- Determinism markers: the decision determinism class is declared in §3.2 Summary; no seed is emitted unless the decision is `stochastic-given-seed`.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<one of the declared enum values>",
                "quantity": <float>,
                "price_level": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel for `retrieved_knowledge` (e.g. `"(No relevant knowledge retrieved this round.)"`) and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this §3.6.0 I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current market price |
| `fundamental` | Continuous | 1 tick | Fair value anchor |
| `deviation` | Continuous | 1 tick | Direct mispricing measure |

Does NOT use: `anchor`, `cost_basis`, `momentum`, peer flow.

#### Core Behavioral Mechanism

1. Observe price and fundamental.
2. Compute `deviation = (price - fundamental) / fundamental`.
3. If price is materially below fundamental, buy.
4. If price is materially above fundamental, sell.
5. Scale order size with absolute deviation.
6. Clip order by position and cash constraints.
7. Hold when deviation is inside the band.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at observed price |
| Order quantity rule | `Q = min(base_position_size, abs(deviation) * sizing_scale)` |
| Order lifetime | 1 tick |
| Cancellation policy | unfilled orders expire at end of tick |
| Inventory constraint | inventory bounded by `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  deviation = (P - F) / F
  buy if deviation < -theta
  sell if deviation > theta
  otherwise hold
  ```
- Sizing function:
  ```
  Q = -sign(deviation) * min(base_position_size, abs(deviation) * sizing_scale)
  ```
- State variables: `position`; `cash`.
- State-update rule: no predictive state; update position and cash post-fill.
- Determinism contract: deterministic given price, fundamental, and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta` | fundamental deviation threshold | 0.02 | Standardised |
| `F` | fundamental value | scenario-provided | Fama (1970) |

#### Behavioral Properties

- Time horizon: short, because it responds immediately to mispricing.
- Risk tolerance: medium, because it trades against deviations but caps size.
- Information asymmetry: none.
- Psychological profile: no behavioral bias; rational benchmark.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `threshold` | float | 0.02 | [0, 1] | high | Fundamental deviation needed to trade. | Higher -> less correction and wider arbitrage band. | Standardised |
| `base_position_size` | float | 20.0 | > 0 | high | Maximum order quantity. | Higher -> stronger correction. | Standardised |
| `sizing_scale` | float | 1000.0 | > 0 | medium | Converts deviation into order size. | Higher -> more aggressive arbitrage. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | medium | Self-imposed inventory cap. | Higher -> more persistent arbitrage capacity. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | shared point value |
| Heterogeneity per parameter | `threshold -> Uniform(0.015, 0.03)` optional |
| Cross-agent correlation | none |
| Identity persistence | identical across episodes |

## Worked Numerical Examples

### Case 1 - Buy undervaluation
```text
Market state: P=96, F=100, threshold=0.02.
Calculation: deviation=-0.04.
Decision: buy min(20, 0.04*1000)=20.
State update: position +20; cash -1920.
```

### Case 2 - Sell overvaluation
```text
Market state: P=105, F=100.
Calculation: deviation=0.05.
Decision: sell 20.
State update: position -20; cash +2100.
```

### Case 3 - Hold near fair value
```text
Market state: P=101, F=100.
Calculation: deviation=0.01 inside threshold.
Decision: hold.
State update: unchanged.
```

### Edge Case - Missing fundamental
```text
Market state: P=103, F missing.
Calculation: prerequisite signal unavailable.
Decision: hold.
State update: unchanged.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `threshold` <- transaction/noise band calibration.

**Expected stylized facts** when this agent dominates the population:
- Bounded mispricing relative to fundamentals.
- Weak or negligible return autocorrelation.
- Faster convergence after shocks.

**Sanity bounds (red flags during simulation)**:
- IF the agent exhibits the behaviour described (Agent trades in same direction as mispricing) THEN the implementation is broken because agent trades in same direction as mispricing.
- IF the agent exhibits the behaviour described (Agent acts when fundamental is missing) THEN the implementation is broken because agent acts when fundamental is missing.
- IF the agent exhibits the behaviour described (Position exceeds declared cap) THEN the implementation is broken because position exceeds declared cap.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `wide_band` | `threshold = 0.10` | Arbitrage bands allow larger persistent deviations. |
| `high_capacity` | `base_position_size = 100` | More arbitrage capacity reduces mispricing half-life. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315-335. https://doi.org/10.2307/1905537 | Rational expectations benchmark |
| 2 | Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *Journal of Finance*, 25(2), 383-417. https://doi.org/10.2307/2325486 | Efficient-market benchmark |
| 3 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408. | Information-based trading |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AGenticFinLab |
| Reviewed by | audit_agent_handbook.py v1 |
| Created | 2026-06-27 |
| Version | 1.0.3 |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-rational-updater.png) |
