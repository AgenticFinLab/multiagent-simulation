# Opinion Environment

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Opinion signal broadcaster (environment agent) |
| Theory Family         | Social Influence / Opinion Dynamics |
| Behavioral Tendency   | **Neutral** - broadcasts opinion signals without trading; shapes other agents' beliefs |
| Time Horizon          | N/A (environment agent) |
| Risk Tolerance        | N/A (environment agent) |
| Information Asymmetry | full (signal generator) |
| Determinism           | stochastic |

## Definition and Goals

This agent models the social opinion environment that broadcasts sentiment and belief signals to trading agents. It does not trade itself but acts as an exogenous opinion-formation process based on DeGroot (1974) consensus dynamics and bounded-confidence models (Hegselmann & Krause 2002). It aggregates recent market states and peer opinions to produce a public opinion signal that influences susceptible agents.

The decision goal is to produce a credible opinion signal each tick that reflects the weighted average of recent price momentum, prior opinion, and random shocks. It is not a trading agent and it does not hold positions. Non-goals: it must not emit trade orders, and it must not directly manipulate prices.

## Theoretical Foundation

**Social influence and opinion dynamics**:
- Theory / Study: Reaching a consensus; Opinion dynamics and bounded confidence.
- Citation: DeGroot, M. H. (1974). Reaching a consensus. *Journal of the American Statistical Association*, 69(345), 118-121. https://doi.org/10.1080/01621459.1974.10480137
- Citation: Hegselmann, R., & Krause, U. (2002). Opinion dynamics and bounded confidence models, analysis, and simulation. *Journal of Artificial Societies and Social Simulation*, 5(3).
- Core Insight: Agents iteratively update beliefs as weighted averages of neighbors' beliefs. With bounded confidence, only sufficiently similar opinions are considered, leading to clustering or consensus depending on the confidence bound.
- Mathematical Formulation: `opinion(t+1) = alpha * opinion(t) + beta * momentum(t) + (1 - alpha - beta) * shock(t)`.
- Empirical Evidence: DeGroot shows convergence to consensus under connected networks; Hegselmann & Krause show polarization under bounded confidence.
- Relevance to This Agent: The agent implements the opinion update rule as an exogenous signal generator.
- Calibration Source: `alpha` 0.5-0.9, `beta` 0.05-0.30, `shock_sigma` 0.01-0.10.
- Falsification Conditions: If the opinion signal is constant or unresponsive to market momentum, the design is falsified.
- Alternative Theories: Bayesian social learning (Acemoglu et al. 2011); information cascades (Bikhchandani et al. 1992).

## Design Purpose and Activation Triggers

Purpose: Generate and broadcast a time-varying opinion signal that captures social sentiment dynamics, enabling other agents to condition their behavior on the prevailing mood.

Call Frequency: every-tick.

Prerequisite Signals:
- `price_momentum` available (recent price return)
- own `opinion_state` available (previous opinion value)

Missing-Signal Policy: emit previous opinion unchanged when momentum is unavailable.

Activation Triggers:
- Always active: computes and broadcasts updated opinion each tick.
- `<Default>`: update opinion using the weighted-average rule.

Deactivation Conditions:
- Never deactivated (persistent environment agent).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| strong positive momentum | opinion drifts bullish | momentum weight |
| strong negative momentum | opinion drifts bearish | momentum weight |
| low momentum | opinion mean-reverts via persistence | autoregressive decay |

Environmental Dependencies: receives price momentum from market; broadcasts opinion to all subscribing agents.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price_momentum` | environment | float | yes | recent price return |
| `opinion_state` | own state | float [-1,1] | yes | previous opinion |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"hold"}` | none | yes | always hold (non-trading) |
| `quantity` | float | `0` | units | yes | always zero |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |
| `opinion_signal` | float | `[-1, 1]` | sentiment | yes | broadcast opinion |

##### Content Constraints

Required fields are `action`, `quantity`, `reasoning`, and `opinion_signal`. Action is always "hold" and quantity is always 0. The opinion signal is the primary output.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"hold","quantity":0.0,"reasoning":"...","opinion_signal":0.0}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields including `opinion_signal`.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price_momentum` | Continuous | 1 tick | exogenous market input |
| `opinion_state` | State | persistent | autoregressive persistence |

Does NOT use: individual agent positions, private information, order book data.

#### Core Behavioral Mechanism

1. Read `price_momentum` and `opinion_state`.
2. Draw shock `epsilon ~ N(0, shock_sigma)`.
3. Compute raw opinion: `raw = alpha * opinion_state + beta * price_momentum + (1 - alpha - beta) * epsilon`.
4. Clamp to [-1, 1]: `opinion_signal = clip(raw, -1, 1)`.
5. Update `opinion_state = opinion_signal`.
6. Emit decision object with `action = hold`, `quantity = 0`, and the `opinion_signal`.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | hold (non-trading agent) |
| Action parameter rule | no market orders |
| Sizing rule | N/A |
| Action lifetime | one decision call |
| Revision policy | opinion updates each tick |
| State constraint | opinion bounded in [-1, 1] |
| Resource cap | N/A |
| Exit rule | N/A |

#### Mathematical Model

`o(t+1) = clip(alpha * o(t) + beta * m(t) + (1 - alpha - beta) * epsilon(t), -1, 1)` where `epsilon ~ N(0, shock_sigma)`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `alpha` | opinion persistence (autoregressive weight) | 0.70 | DeGroot (1974) |
| `beta` | momentum sensitivity | 0.20 | calibration |
| `shock_sigma` | random shock standard deviation | 0.05 | calibration |

#### Behavioral Properties

- Time horizon: N/A (environment agent, no investment horizon).
- Risk tolerance: N/A (non-trading).
- Information asymmetry: full (generates the signal others consume).
- Psychological profile: N/A; represents aggregate social opinion dynamics.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `alpha` | float | 0.70 | [0.50, 0.90] | high | autoregressive persistence of opinion | Higher -> slower opinion shifts | DeGroot (1974) |
| `beta` | float | 0.20 | [0.05, 0.30] | high | sensitivity to price momentum | Higher -> more reactive to market | calibration |
| `shock_sigma` | float | 0.05 | [0.01, 0.10] | medium | random shock volatility | Higher -> noisier signal | calibration |
| `initial_opinion` | float | 0.00 | [-1.0, 1.0] | low | starting opinion state | Sets initial bias | calibration |

## Worked Numerical Examples

### Case 1 - Bullish Drift

System state: opinion_state 0.20, price_momentum 0.05, shock drawn 0.01.
Calculation: `raw = 0.70*0.20 + 0.20*0.05 + 0.10*0.01 = 0.14 + 0.01 + 0.001 = 0.151`.
Decision: hold, opinion_signal = 0.151.
State update: opinion_state becomes 0.151.

### Case 2 - Bearish Pressure

System state: opinion_state 0.10, price_momentum -0.08, shock drawn -0.02.
Calculation: `raw = 0.70*0.10 + 0.20*(-0.08) + 0.10*(-0.02) = 0.07 - 0.016 - 0.002 = 0.052`.
Decision: hold, opinion_signal = 0.052.
State update: opinion_state becomes 0.052.

### Case 3 - Strong Persistence

System state: opinion_state 0.80, price_momentum 0.00, shock drawn 0.00.
Calculation: `raw = 0.70*0.80 + 0.20*0.00 + 0.10*0.00 = 0.56`.
Decision: hold, opinion_signal = 0.56.
State update: opinion_state becomes 0.56.

### Edge Case - Clamping at Boundary

System state: opinion_state 0.95, price_momentum 0.10, shock drawn 0.08.
Calculation: `raw = 0.70*0.95 + 0.20*0.10 + 0.10*0.08 = 0.665 + 0.02 + 0.008 = 0.693`. Within bounds, no clamping needed.
Alternative: opinion_state 0.99, momentum 0.50, shock 0.30: `raw = 0.693 + 0.10 + 0.03 = 0.823`. Clamp not needed. Extreme: `raw = 1.05 -> clip to 1.0`.
Decision: hold, opinion_signal = 1.0.
State update: opinion_state becomes 1.0.

## Behavioral Verification and Calibration

- Opinion signal must update every tick.
- Opinion must remain within [-1, 1] at all times.
- Agent must never emit buy or sell orders.
- Given zero momentum and zero shock, opinion must decay toward zero (mean-reversion via `alpha < 1`).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-persistence | `alpha = 0` | opinion persistence creates trends | decrease | opinion autocorrelation |
| no-momentum | `beta = 0` | market feedback matters for opinion | decrease | opinion-price correlation |
| high-noise | `shock_sigma = 0.20` | noise disrupts opinion formation | decrease | opinion predictability |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | DeGroot, M. H. (1974). Reaching a consensus. https://doi.org/10.1080/01621459.1974.10480137 | Weighted-average opinion dynamics |
| 2 | Hegselmann, R., & Krause, U. (2002). Opinion dynamics and bounded confidence models. JASSS 5(3). | Bounded-confidence clustering |
| 3 | Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. https://doi.org/10.1086/261849 | Information cascade alternative |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-opinion-environment.png) |
| Status | draft |
