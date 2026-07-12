# Hot-money funder

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | hot-money short-term foreign funder |
| Theory Family         | Sudden Stops / Capital Flow Reversal |
| Behavioral Tendency   | **Diverging** - exits into small depreciation and amplifies currency pressure |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models short-term foreign creditors and portfolio investors that fund emerging-market positions during benign periods and reverse exposure when currency stress appears. The real-world counterpart is a hedge fund, foreign bank treasury desk, or money-market lender with low switching costs and short rollover horizons. It emits buy, sell, or hold decisions with a quantity sized from available cash or current position.

The decision goal is not fundamental valuation; it is fast balance-sheet protection. When exchange-rate deviation is mildly negative, the agent sells a fixed fraction of remaining exposure. When deviation is positive again, it cautiously re-enters.

Inside a market simulation this agent is a crisis initiator. It must not provide official support, it must not act as a long-horizon value buyer, and it must not use private policy signals not declared by the environment.

## Theoretical Foundation

**Sudden Stops and Hot-Money Reversal**:
- Theory / Study: East Asian crisis sudden-stop diagnosis.
- Citation: Radelet, S., & Sachs, J. (1998). The East Asian financial crisis: Diagnosis, remedies, prospects. *Brookings Papers on Economic Activity*, 1998(1), 1-90. https://doi.org/10.1353/eca.1998.0009
- Core Insight: Short-term foreign capital can reverse abruptly after small stress signals. The reversal is procyclical because selling lowers prices and validates further exit.
- Mathematical Formulation: `sell if deviation < -theta_reversal; Q_sell = phi_sell * position`.
- Empirical Evidence: Radelet and Sachs document short-term debt and reserve mismatch in Thailand before the 1997 depeg.
- Relevance to This Agent: The agent operationalises rapid capital exit after a small negative deviation.
- Calibration Source: `theta_reversal` 0.01 to 0.05 and `phi_sell` 0.40 to 0.80 from sudden-stop crisis ranges.
- Falsification Conditions: If deviation is below threshold and the agent does not sell positive remaining exposure, the design is falsified.
- Alternative Theories: First-generation reserve exhaustion or pure speculative attack can replace the sudden-stop trigger.

## Design Purpose and Activation Triggers

Purpose: Reverse short-term foreign exposure when exchange-rate stress appears.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `deviation` available
- own `cash` and `position` available

Missing-Signal Policy: hold when a required signal is unavailable.

Activation Triggers:
- `deviation < -theta_reversal`: sell `phi_sell` of current position.
- `deviation > theta_reversal`: buy with `phi_buy` of available cash.
- Default: hold.

Deactivation Conditions:
- position is zero and sell trigger persists.
- cash is insufficient and buy trigger persists.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| mild depreciation | accelerates exit | sudden-stop risk control |
| positive recovery | cautious re-entry | post-crisis return seeking |

Environmental Dependencies: none beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current tradable price |
| `deviation` | environment | float | yes | stress trigger |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | - | yes | selected action |
| `quantity` | float | `>= 0` | shares / units | yes | action size |
| `reasoning` | string | 1-3 sentences | - | yes | audit trail |

##### Content Constraints

Required fields must be present. Extra fields are forbidden. Quantity is clamped to available cash or current position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Implementers must map each input to a real state read, emit exactly the output fields, and preserve this schema across rule-driven, model-driven, hybrid, and retrieval-augmented variants.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | current | values buys and sales |
| `deviation` | Continuous | current | sudden-stop trigger |
| `cash` | Continuous | current | buy capacity |
| `position` | Continuous | current | sell capacity |

Does NOT use: policy announcements, peer identities, or hidden reserves.

#### Core Behavioral Mechanism

1. Read price, deviation, cash, and position.
2. If deviation is below `-theta_reversal`, compute sell quantity from position.
3. If deviation is above `theta_reversal`, compute buy quantity from cash and price.
4. Clamp quantity to resource capacity.
5. Emit buy, sell, or hold with reasoning.
6. Update cash and position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | trades at current price |
| Sizing rule | sell `phi_sell * position`; buy `phi_buy * cash / price` |
| Action lifetime | one decision call |
| Revision policy | next call replaces prior intent |
| State constraint | position and cash cannot go below zero |
| Resource cap | buy quantity cannot exceed cash / price; sell quantity cannot exceed position |
| Exit rule | hold when both resource caps bind |

#### Mathematical Model

Decision output is `(action, quantity)`. If `d_t < -theta_reversal`, action is sell and `q_t = min(position_t, phi_sell position_t)`. If `d_t > theta_reversal`, action is buy and `q_t = min(cash_t / price_t, phi_buy cash_t / price_t)`. Otherwise action is hold and `q_t = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_reversal` | stress threshold | 0.02 | Radelet & Sachs (1998) |
| `phi_sell` | sell fraction | 0.60 | Radelet & Sachs (1998) |
| `phi_buy` | re-entry fraction | 0.30 | Calvo (1998) |

#### Behavioral Properties

- Time horizon: short, because rollover-risk decisions happen quickly.
- Risk tolerance: medium, because the agent holds exposure in calm states but exits aggressively.
- Information asymmetry: partial.
- Psychological profile: risk-off herding under sudden-stop stress.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `theta_reversal` | float | 0.02 | [0.01, 0.05] | high | stress threshold | Higher -> later exit | Radelet & Sachs (1998) |
| `phi_sell` | float | 0.60 | [0.40, 0.80] | high | sell fraction | Higher -> deeper first shock | Radelet & Sachs (1998) |
| `phi_buy` | float | 0.30 | [0.10, 0.40] | medium | re-entry fraction | Higher -> faster recovery buying | Calvo (1998) |

## Worked Numerical Examples

### Case 1 - Sell branch
System state: price 98, deviation -0.03, position 3000.
Calculation: `0.03 > 0.02`; `q = 0.60 * 3000 = 1800`.
Decision: sell 1800.
State update: position falls by 1800.

### Case 2 - Buy branch
System state: price 102, deviation 0.02, cash 800000.
Calculation: `q = 0.30 * 800000 / 102 = 2352`.
Decision: buy 2352.
State update: cash falls by trade value.

### Case 3 - Hold branch
System state: price 100, deviation 0.00.
Calculation: no trigger crossed.
Decision: hold.
State update: unchanged.

### Edge Case - No position
System state: deviation -0.05, position 0.
Calculation: sell trigger fires but cap is zero.
Decision: hold with zero quantity.
State update: unchanged.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `theta_reversal` <- Radelet & Sachs (1998).
- `phi_sell` <- sudden-stop liquidation ranges.

**Expected individual behaviour**:
- Given deviation below threshold and positive position, agent MUST sell.
- Given deviation inside the band, agent MUST hold.
- Given positive deviation and cash, agent MAY buy.

**Sanity bounds**:
- IF quantity exceeds position on sell THEN implementation is broken.
- IF quantity exceeds cash / price on buy THEN implementation is broken.
- IF missing deviation causes a non-hold action THEN implementation is broken.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-hot-money-exit | `phi_sell = 0` | sudden-stop exit is necessary | lower drawdown | max drawdown |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Radelet, S., & Sachs, J. (1998). The East Asian financial crisis: Diagnosis, remedies, prospects. *Brookings Papers on Economic Activity*, 1998(1), 1-90. https://doi.org/10.1353/eca.1998.0009 | sudden stops |
| 2 | Calvo, G. A. (1998). Capital flows and capital-market crises: The simple economics of sudden stops. *Journal of Applied Economics*, 1(1), 35-54. | re-entry and sudden-stop calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex |
| Created | 2026-07-05 |
| Version | 1.0.1 |
| Icon | ![](../agent_images/icons/finance-hot-money-funder.png) |
| Change log | 1.0.0 - Created for AsianFinancialCrisis create-pipeline replay.<br>1.0.1 - Added AGENT_POOL Icon row via polish-simulation-pipeline Step 2 icon-repair (icon PNG was already present under agent_images/icons/; profile row and design.md mapping were the missing links). |
| Status | experimental |
