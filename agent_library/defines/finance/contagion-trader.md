# Contagion trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | cross-border contagion seller |
| Theory Family         | Twin Crises / Financial Contagion |
| Behavioral Tendency   | **Diverging** - sells when deviation and momentum jointly signal regional stress |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models regional portfolio managers, hedge funds, and common-creditor channels that reduce exposure across countries after one market shows stress. It produces buy, sell, or hold decisions from a composite contagion signal. The real-world counterpart is an active cross-border investor watching both valuation deviation and recent return momentum.

The decision goal is exposure reduction when crisis signals become jointly negative. It does not diagnose domestic fundamentals country by country; it treats regional stress as correlated.

Inside a market simulation this agent is a second-wave amplifier. It must not be the first hot-money trigger, it must not provide rescue capital, and it must not buy purely as a value investor.

## Theoretical Foundation

**Twin Crises and Contagion**:
- Theory / Study: Banking and balance-of-payments twin crises.
- Citation: Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473-500. https://doi.org/10.1257/aer.89.3.473
- Core Insight: Crisis pressure spreads through common creditors, trade linkages, and panic correlations. Momentum and deviation jointly predict regional selling pressure.
- Mathematical Formulation: `s_t = w_dev * deviation_t + w_ret * return_t`; sell when `s_t < theta_contagion`.
- Empirical Evidence: Kaminsky and Reinhart document clustered banking and currency crises and leading-indicator thresholds across crisis episodes.
- Relevance to This Agent: The composite signal operationalises cross-border contagion pressure.
- Calibration Source: weights 0.40 to 0.80 and threshold -0.05 to -0.01 from crisis-indicator calibration.
- Falsification Conditions: If the signal is below threshold and the agent holds despite positive position, the design is falsified.
- Alternative Theories: Pure momentum trading or common-lender models can be swapped in.

## Design Purpose and Activation Triggers

Purpose: Transmit currency stress through regional selling pressure.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` and `prev_price` available
- `deviation` available
- own `position` available

Missing-Signal Policy: hold when price history is missing.

Activation Triggers:
- composite signal below threshold: sell `phi_sell` of position.
- composite signal non-negative: hold.
- Default: hold.

Deactivation Conditions:
- position is zero.
- price history is stale.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| negative momentum | sells faster | panic correlation |
| stable deviation | holds | no contagion pressure |

Environmental Dependencies: requires previous price in the broadcast.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current price |
| `prev_price` | environment | float | yes | return calculation |
| `deviation` | environment | float | yes | fundamental stress |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"sell", "hold"}` | - | yes | selected action |
| `quantity` | float | `>= 0` | shares / units | yes | action size |
| `reasoning` | string | 1-3 sentences | - | yes | audit trail |

##### Content Constraints

Required fields must be present. Quantity cannot exceed position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Implementers must wire each signal, clamp quantity, and keep the output schema stable across variants.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | current | current stress level |
| `prev_price` | Continuous | 1 tick | return momentum |
| `deviation` | Continuous | current | crisis pressure |
| `position` | Continuous | current | sell capacity |

Does NOT use: official rescue state or private country fundamentals.

#### Core Behavioral Mechanism

1. Read price, previous price, deviation, and position.
2. Compute return as `(price - prev_price) / prev_price`.
3. Compute contagion signal from deviation and return.
4. If signal is below threshold, sell a fixed position fraction.
5. Otherwise hold.
6. Update position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold |
| Action parameter rule | trades at current price |
| Sizing rule | sell `phi_sell * position` |
| Action lifetime | one call |
| Revision policy | recompute next call |
| State constraint | position cannot go below zero |
| Resource cap | sell quantity cannot exceed position |
| Exit rule | hold when position is zero |

#### Mathematical Model

`r_t = (P_t - P_{t-1}) / P_{t-1}` and `s_t = w_dev d_t + w_ret r_t`. If `s_t < theta_contagion`, sell `min(position_t, phi_sell position_t)`. Otherwise hold.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `w_dev` | deviation weight | 0.60 | Kaminsky & Reinhart (1999) |
| `w_ret` | return weight | 0.40 | Kaminsky & Reinhart (1999) |
| `theta_contagion` | trigger threshold | -0.025 | Kaminsky & Reinhart (1999) |
| `phi_sell` | sell fraction | 0.50 | Kaminsky & Reinhart (1999) |

#### Behavioral Properties

- Time horizon: short, because contagion is fast-moving.
- Risk tolerance: medium, because the agent cuts exposure aggressively once conditions align.
- Information asymmetry: partial.
- Psychological profile: regional risk-off herding under common-lender stress.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `w_dev` | float | 0.60 | [0.40, 0.80] | high | deviation signal weight | Higher -> more fundamental-stress selling | Kaminsky & Reinhart (1999) |
| `w_ret` | float | 0.40 | [0.20, 0.60] | medium | return signal weight | Higher -> more momentum selling | Kaminsky & Reinhart (1999) |
| `theta_contagion` | float | -0.025 | [-0.05, -0.01] | high | sell threshold | Higher -> earlier selling | Kaminsky & Reinhart (1999) |
| `phi_sell` | float | 0.50 | [0.30, 0.70] | high | sell fraction | Higher -> deeper cascade | Kaminsky & Reinhart (1999) |

## Worked Numerical Examples

### Case 1 - Sell branch
System state: price 96, previous price 98, deviation -0.04, position 4000.
Calculation: return -0.0204; signal `0.60*-0.04 + 0.40*-0.0204 = -0.0322`.
Decision: sell `0.50 * 4000 = 2000`.
State update: position falls by 2000.

### Case 2 - Hold branch
System state: price 99, previous price 99.5, deviation -0.01.
Calculation: signal above threshold.
Decision: hold.
State update: unchanged.

### Case 3 - Momentum branch
System state: price 94, previous price 100, deviation -0.03.
Calculation: negative return strengthens the signal below threshold.
Decision: sell.
State update: position decreases.

### Edge Case - Missing previous price
System state: previous price unavailable.
Calculation: return cannot be computed.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `w_dev`, `w_ret`, `theta_contagion` <- Kaminsky & Reinhart (1999).

**Expected individual behaviour**:
- Given negative deviation and negative return with signal below threshold, agent MUST sell.
- Given signal above threshold, agent MUST hold.
- Given zero position, sell quantity MUST be zero.

**Sanity bounds**:
- IF sell quantity exceeds position THEN implementation is broken.
- IF signal is not computed from both declared components THEN implementation is broken.
- IF missing previous price causes a sell THEN implementation is broken.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-contagion | `phi_sell = 0` | contagion amplifies crisis | lower AC1 and drawdown | AC1, drawdown |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473-500. https://doi.org/10.1257/aer.89.3.473 | contagion and twin crises |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex |
| Created | 2026-07-05 |
| Version | 1.0.4 |
| Icon | ![](../agent_images/icons/finance-contagion-trader.png) |
| Status | conformant |
