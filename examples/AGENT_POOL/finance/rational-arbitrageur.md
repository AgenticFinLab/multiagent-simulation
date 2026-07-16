# Rational Arbitrageur

## Summary

| Field                 | Content                                                                                                           |
|-----------------------|-------------------------------------------------------------------------------------------------------------------|
| Archetype             | Rational arbitrageur                                                                                              |
| Theory Family         | Limits to Arbitrage / Fundamental Valuation                                                                       |
| Behavioral Tendency   | **Converging — shorts overvalued bubble assets and exits when the bubble bursts; converges on fundamental value** |
| Market Role           | **Stabilising** — provides corrective selling pressure against bubble overvaluation                               |
| Time Horizon          | medium                                                                                                            |
| Risk Tolerance        | medium                                                                                                            |
| Information Asymmetry | none                                                                                                              |
| Determinism           | deterministic                                                                                                     |

## Definition and Goals

This agent models a sophisticated rational investor who identifies overvalued bubble assets and shorts them, but faces limits to arbitrage including short-selling costs, capital constraints, and noise-trader risk. The real-world counterpart is a hedge fund or proprietary trading desk that bets against mispricing.

The decision goal is to sell (short) when `deviation = (price - fundamental) / fundamental` is materially positive, and cover the short when deviation narrows. Position sizing is bounded by capital constraints.

In simulation this agent provides the primary corrective force against bubble overvaluation. Non-goals: it must not chase momentum, use leverage procyclically, or ignore fundamental value.

## Theoretical Foundation

**Limits to arbitrage**:
- Theory / Study: Capital constraints and noise-trader risk limit rational arbitrage.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Rational arbitrage is limited by short-selling costs, capital constraints, and the risk that mispricings widen before correcting, forcing premature position closure.
- Mathematical Formulation: `short when deviation > theta_short; q = min(capital_limit, deviation * sizing_scale)`.
- Empirical Evidence: Large persistent mispricings exist despite rational investors due to arbitrage frictions.
- Relevance to This Agent: The agent shorts overvaluation but is constrained by `max_short_position` and `short_cost`.
- Calibration Source: Shleifer & Vishny (1997); scenario normalization.
- Falsification Conditions: If the agent does not short when deviation is positive, the arbitrage channel is absent.
- Alternative Theories: unlimited arbitrage; momentum trading; noise-trader risk premium.

**Noise-trader risk and front-running**:
- Theory / Study: Noise trader risk in financial markets.
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703
- Core Insight: Noise traders' irrational demand creates systematic risk that rational arbitrageurs cannot eliminate. If sentiment turns more bullish, mispricings widen before correcting.
- Mathematical Formulation: `sentiment ~ N(rho_bar, sigma_rho^2)` — noise trader misperception follows an AR(1) process.
- Empirical Evidence: Sentiment proxies forecast cross-sectional return patterns.
- Relevance to This Agent: The agent faces the risk that bubble momentum widens the mispricing before correction.
- Calibration Source: De Long et al. (1990).
- Falsification Conditions: If the agent shorts with unlimited capacity, noise-trader risk is not represented.
- Alternative Theories: rational expectations; complete markets.

## Design Purpose and Activation Triggers

Purpose: Provide corrective selling pressure against bubble overvaluation.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- own `cash` and `position` available

Missing-Signal Policy: hold when either `price` or `fundamental` is missing.

Activation Triggers:
- `deviation > short_threshold`: short (sell) with sized quantity.
- `deviation < cover_threshold`: cover short (buy back).
- `<Default>`: hold.

Deactivation Conditions:
- Capital exhausted: cannot increase short position.
- Short position limit reached: cap exposure.

Behavioral Adaptation by Condition:
| Condition                       | Behavioral change      | Mechanism                                 |
|---------------------------------|------------------------|-------------------------------------------|
| Asset overvalued vs fundamental | Shorts the asset       | Sizing proportional to mispricing         |
| Bubble bursts                   | Covers short and exits | `deviation` narrows below cover threshold |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime               | Contribution | Mechanism                                        |
|----------------------|--------------|--------------------------------------------------|
| Bubble overvaluation | Stabilising  | Short selling pressure counters momentum demand. |
| Post-burst           | Neutral      | Covers short; exits the market.                  |
| Calm                 | Neutral      | Deviation small; minimal trading.                |

Interaction with other agents: Trades against momentum speculators' bubble demand; provides exit liquidity for fundamental investors during the crash.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                              |
|---------------------|--------------|--------------|-----------|------------------------------------|
| `price`             | environment  | `float`      | yes       | Execution reference.               |
| `fundamental`       | environment  | `float`      | yes       | Intrinsic value reference.         |
| `cash`              | agent state  | `float`      | yes       | Capital for short margin.          |
| `position`          | agent state  | `float`      | yes       | Short position (negative = short). |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata.                |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum        | Unit     | Required?   | Meaning                                  |
|---------------|--------|---------------------------|----------|-------------|------------------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}   | —        | yes         | Discrete action selected this call.      |
| `quantity`    | float  | `[0, base_position_size]` | shares   | conditional | Order magnitude; 0 when `action = hold`. |
| `price_level` | float  | `= price` (market order)  | currency | conditional | Execution reference.                     |
| `reasoning`   | string | 1–3 sentences             | —        | yes         | Audit trail explaining WHY.              |

##### Content Constraints

- Required fields: every `Required? = yes` field MUST be present on every call.
- Forbidden fields: undeclared fields MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_position_size]`.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<enum value>",
                "quantity": <float>,
                "price_level": <float>,
                "reasoning": "<explanation>"}</decision>

Rules:
1. Tags are literal ASCII, NOT optional.
2. `<decision>` MUST contain valid JSON matching the Outputs table.
3. Rule-driven variants MAY template `<analysis>`.
4. Model-driven variants MUST include tag+JSON in the prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel.

##### Implementer Contract Reminder

Implementers MUST re-open this §3.6.0 I/O Contract during every coding pass as the single source of truth.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                      |
|---------------|------------|---------------|--------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference.           |
| `fundamental` | Continuous | 1 tick        | Intrinsic value for deviation. |
| `cash`        | State      | persistent    | Short margin constraint.       |
| `position`    | State      | persistent    | Short exposure tracking.       |

Does NOT use: momentum, anchor, cost_basis, peer flow.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `cash`, `position`.
2. Compute `deviation = (price - fundamental) / fundamental`.
3. If `deviation > short_threshold`, compute short quantity: `q = min(base_position_size, deviation * sizing_scale)`, capped by `max_short_position - abs(position)`.
4. If `deviation < cover_threshold` and position is short, compute cover quantity: `q = min(abs(position), base_position_size)`.
5. Otherwise hold.
6. Emit decision and update state post-fill.

#### Action Space

| Aspect                | Specification                                                                                                   |
|-----------------------|-----------------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                                                              |
| Price level rule      | market order at current price                                                                                   |
| Order quantity rule   | short: `min(base_size, deviation * sizing_scale)` capped by short limit; cover: `min(abs(position), base_size)` |
| Order lifetime        | 1 tick                                                                                                          |
| Cancellation policy   | unfilled orders expire                                                                                          |
| Inventory constraint  | `abs(position) <= max_short_position`                                                                           |
| Wealth / leverage cap | `cash >= 0`; short margin required                                                                              |
| Stop-loss / kill rule | none — patient arbitrage                                                                                        |

#### Mathematical Model

```
d_t = (P_t - F_t) / F_t
if d_t > theta_short:
    a_t = sell; q_t = min(Q_max, d_t * k_q); capped by short_limit
elif d_t < theta_cover and position < 0:
    a_t = buy;  q_t = min(abs(position), Q_max)
else:
    a_t = hold; q_t = 0
```

State variables: `cash`, `position`, updated post-fill.
Determinism contract: deterministic.

| Symbol               | Meaning               | Default Value | Source                   |
|----------------------|-----------------------|---------------|--------------------------|
| `theta_short`        | short entry threshold | 0.05          | Shleifer & Vishny (1997) |
| `theta_cover`        | short cover threshold | 0.01          | Scenario calibration     |
| `sizing_scale`       | quantity scale        | 3000.0        | Scenario normalization   |
| `base_position_size` | max order             | 200.0         | Scenario normalization   |
| `max_short_position` | short exposure cap    | 500.0         | Scenario normalization   |

#### Behavioral Properties

- Time horizon: medium, because arbitrage requires patience for mispricing correction.
- Risk tolerance: medium, because the agent faces noise-trader risk but has bounded exposure.
- Information asymmetry: none, all inputs are public.
- Psychological profile: disciplined, fundamental-driven, patient.

## Parameters

| Parameter            | Type  | Default | Valid Range  | Sensitivity | Description                         | Impact                            | Source                   |
|----------------------|-------|---------|--------------|-------------|-------------------------------------|-----------------------------------|--------------------------|
| `short_threshold`    | float | 0.05    | [0.02, 0.15] | high        | Deviation above which agent shorts. | Higher -> later arbitrage entry.  | Shleifer & Vishny (1997) |
| `cover_threshold`    | float | 0.01    | [0, 0.05]    | medium      | Deviation below which agent covers. | Lower -> later profit-taking.     | Scenario calibration     |
| `sizing_scale`       | float | 3000.0  | [500, 8000]  | medium      | Converts deviation to quantity.     | Higher -> larger short orders.    | Scenario normalization   |
| `base_position_size` | float | 200.0   | [50, 500]    | medium      | Maximum order quantity.             | Higher -> larger per-tick impact. | Scenario normalization   |
| `max_short_position` | float | 500.0   | [100, 2000]  | low         | Short exposure cap.                 | Higher -> more cumulative short.  | Scenario normalization   |

## Population and Heterogeneity

| Aspect                         | Specification                      |
|--------------------------------|------------------------------------|
| Default population size        | scenario-dependent (typically 1–3) |
| Parameter heterogeneity policy | identical parameters               |
| Heterogeneity per parameter    | none — representative agent        |
| Cross-agent correlation        | none                               |
| Identity persistence           | persistent across ticks            |

## Worked Numerical Examples

### Case 1 — Short overvaluation
System state: `price=120`, `fundamental=100`, `cash=100000`, `position=0`.
Calculation: `deviation = 0.20`; `0.20 > 0.05` triggers short; `q = min(200, 0.20*3000) = min(200, 600) = 200`; short cap: `min(200, 500) = 200`.
Decision: sell 200 at 120.
State update: position -200; cash receives short proceeds.

### Case 2 — Cover short
System state: `price=105`, `fundamental=100`, `position=-200`.
Calculation: `deviation = 0.05`; `0.05 > 0.01` — still above cover threshold; hold short.
Decision: hold.
State update: unchanged.

### Case 3 — Hold in no-trade band
System state: `price=103`, `fundamental=100`.
Calculation: `deviation = 0.03`; `0.03 < 0.05` — below short threshold.
Decision: hold.
State update: no portfolio change.

### Edge Case — Missing fundamental
System state: `fundamental` unavailable.
Decision: hold.
State update: unchanged.

## Validation and Calibration

**Calibration data sources**:
- `short_threshold` <- Shleifer & Vishny (1997) arbitrage entry ranges.
- `cover_threshold` <- scenario calibration for profit-taking timing.
- `sizing_scale` <- scenario normalization for per-tick impact.

**Expected individual behaviour**:
- Given deviation above 0.05 and capital, agent MUST short.
- Given deviation below 0.01 and short position, agent MUST cover.
- Given deviation inside the band, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys (goes long) when deviation is positive THEN the arbitrage mechanism is inverted because rational arbitrageurs short overvaluation.
- IF `quantity > base_position_size` THEN the sizing constraint is broken.
- IF `abs(position) > max_short_position` THEN the exposure cap is violated.

#### Ablation Hooks

| Ablation name   | Setting                   | Hypothesis tested                          | Expected direction | Metric               |
|-----------------|---------------------------|--------------------------------------------|--------------------|----------------------|
| no-arbitrage    | `short_threshold = 999`   | Arbitrage constrains bubble height.        | larger bubble      | peak price deviation |
| tight-short-cap | `max_short_position = 50` | Short capacity limits corrective pressure. | larger bubble      | peak price deviation |

## Behavioral Verification and Calibration

- Given deviation = 0.10 (above `short_threshold` of 0.05) and available capital, agent must emit a sell (short) order with positive quantity.
- Given deviation = 0.005 (below `cover_threshold` of 0.01) and existing short position, agent must emit a buy (cover) order.
- Given deviation = 0.03 (inside the no-trade band between cover and short thresholds), agent must hold with zero quantity.
- Given `abs(position)` at `max_short_position`, agent must not increase short exposure further.
- Given `fundamental` signal is missing or unavailable, agent must hold and not compute deviation.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_arbitrage` | `short_threshold = 999` | Removing arbitrage allows unconstrained bubble growth | increase | peak price deviation from fundamental |
| `tight_short_cap` | `max_short_position = 50` | Short capacity limits corrective selling pressure | increase | peak price deviation from fundamental |

## Academic References

| # | Citation                                                                                                                                                                  | Notes                                        |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                     | Arbitrage frictions and capital constraints  |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 | Noise-trader risk and mispricing persistence |

## Design Provenance and Versioning

| Field   | Content                                                         |
|---------|-----------------------------------------------------------------|
| Author  | Codex                                                           |
| Created | 2026-07-16                                                      |
| Version | 1.0.0                                                           |
| Icon    | ![](../agent_images/icons/finance-rational-arbitrageur.png)     |
| Status  | draft                                                           |
