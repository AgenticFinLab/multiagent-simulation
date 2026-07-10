# IMF rescuer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | official crisis-rescue liquidity provider |
| Theory Family         | Policy Intervention / Crisis Lending |
| Behavioral Tendency   | **Converging** - buys only after severe dislocation and pushes price toward stability |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models official-sector crisis lending such as IMF-style support or a sovereign stabilisation fund. The counterpart is a policy institution with large resources but a delayed activation rule. It emits buy or hold decisions based on the crisis deviation.

The decision goal is stabilisation, not profit maximisation. It deploys a fraction of remaining support capacity after stress crosses a severe threshold.

Inside a market simulation this agent is a delayed floor. It must not initiate the crisis, it must not sell into depreciation, and it must not provide unlimited support without a trigger.

## Theoretical Foundation

**IMF Crisis Lending and Conditional Rescue**:
- Theory / Study: Asian crisis policy-intervention model.
- Citation: Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigers? A model of the Asian crisis. *European Economic Review*, 43(7), 1211-1236. https://doi.org/10.1016/S0014-2921(98)00111-0
- Core Insight: Official support can stabilise expectations but often arrives after deep stress and with conditionality. Delay allows overshooting before support forms a floor.
- Mathematical Formulation: `buy if deviation < theta_rescue; Q_buy = phi_rescue * cash / price`.
- Empirical Evidence: Asian crisis programmes were announced after large depreciations and disbursed over time.
- Relevance to This Agent: The agent buys after severe stress and uses a gradual deployment fraction.
- Calibration Source: rescue thresholds -0.15 to -0.03 and buy ratio 0.10 to 0.40.
- Falsification Conditions: If stress is severe and the agent has cash but does not buy, the design is falsified.
- Alternative Theories: Domestic central-bank reserve defence can replace the international rescue mechanism.

## Design Purpose and Activation Triggers

Purpose: Supply delayed official demand after severe exchange-rate stress.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `deviation` available
- own `cash` available

Missing-Signal Policy: hold when required signals are unavailable.

Activation Triggers:
- `deviation < theta_rescue`: buy with `phi_rescue` of available cash.
- Default: hold.

Deactivation Conditions:
- cash is exhausted.
- deviation recovers above the rescue threshold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| severe depreciation | deploys support | crisis lending |
| recovery | pauses support | conditional stabilisation |

Environmental Dependencies: none beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current price |
| `deviation` | environment | float | yes | rescue trigger |
| `cash` | own state | float | yes | support capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "hold"}` | - | yes | selected action |
| `quantity` | float | `>= 0` | shares / units | yes | support size |
| `reasoning` | string | 1-3 sentences | - | yes | audit trail |

##### Content Constraints

Quantity cannot exceed cash divided by price. Extra fields are forbidden.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Implementers must preserve this schema and the delayed-trigger support rule across variants.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | current | sizes support |
| `deviation` | Continuous | current | rescue trigger |
| `cash` | Continuous | current | support capacity |

Does NOT use: profit target, private creditor losses, or peer trades.

#### Core Behavioral Mechanism

1. Read price, deviation, and cash.
2. If deviation is below rescue threshold, compute buy capacity.
3. Clamp buy quantity to available support cash.
4. If threshold is not met, hold.
5. Emit decision and reasoning.
6. Update cash after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, hold |
| Action parameter rule | buys at current price |
| Sizing rule | buy `phi_rescue * cash / price` |
| Action lifetime | one call |
| Revision policy | recompute each call |
| State constraint | cash cannot go below zero |
| Resource cap | quantity cannot exceed cash / price |
| Exit rule | hold when cash is exhausted or deviation recovers |

#### Mathematical Model

If `d_t < theta_rescue`, action is buy and `q_t = min(cash_t / P_t, phi_rescue cash_t / P_t)`. Otherwise action is hold and `q_t = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_rescue` | rescue threshold | -0.05 | Corsetti, Pesenti & Roubini (1999) |
| `phi_rescue` | cash deployment fraction | 0.25 | Corsetti, Pesenti & Roubini (1999) |

#### Behavioral Properties

- Time horizon: medium, because support is delayed and persistent.
- Risk tolerance: low, because action is conditional and stabilising.
- Information asymmetry: partial.
- Psychological profile: rules-based official-sector stabiliser.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `theta_rescue` | float | -0.05 | [-0.15, -0.03] | high | rescue trigger | Higher -> earlier rescue | Corsetti, Pesenti & Roubini (1999) |
| `phi_rescue` | float | 0.25 | [0.10, 0.40] | medium | deployment fraction | Higher -> stronger floor | Corsetti, Pesenti & Roubini (1999) |
| `initial_cash` | float | 5000000.0 | > 0 | high | support capacity | Higher -> more durable floor | Corsetti, Pesenti & Roubini (1999) |

## Worked Numerical Examples

### Case 1 - Rescue branch
System state: price 94, deviation -0.06, cash 5000000.
Calculation: trigger met; quantity `0.25 * 5000000 / 94 = 13297`.
Decision: buy 13297.
State update: cash falls by trade value.

### Case 2 - Hold branch
System state: price 97, deviation -0.03.
Calculation: threshold not met.
Decision: hold.
State update: unchanged.

### Case 3 - Repeated support
System state: price 90, deviation -0.10, cash 3000000.
Calculation: trigger met; support size falls with remaining cash.
Decision: buy.
State update: cash decreases.

### Edge Case - No cash
System state: deviation -0.20, cash 0.
Calculation: trigger met but capacity zero.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `theta_rescue` and `phi_rescue` <- Corsetti, Pesenti & Roubini (1999).

**Expected individual behaviour**:
- Given deviation below threshold and cash, agent MUST buy.
- Given deviation above threshold, agent MUST hold.
- Given no cash, agent MUST emit zero quantity.

**Sanity bounds**:
- IF buy quantity exceeds cash / price THEN implementation is broken.
- IF the agent sells THEN implementation is broken.
- IF support activates before threshold THEN implementation is broken.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-official-rescue | `phi_rescue = 0` | rescue creates floor | deeper drawdown | max drawdown |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigers? A model of the Asian crisis. *European Economic Review*, 43(7), 1211-1236. https://doi.org/10.1016/S0014-2921(98)00111-0 | policy intervention |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex |
| Created | 2026-07-05 |
| Version | 1.0.1 |
| Icon | ![](../agent_images/icons/finance-imf-rescuer.png) |
| Change log | 1.0.0 - Created for AsianFinancialCrisis create-pipeline replay.<br>1.0.1 - Added AGENT_POOL icon via agent-icon-generation-skill. |
| Status | experimental |
