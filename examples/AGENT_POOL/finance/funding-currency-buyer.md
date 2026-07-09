# Funding-currency buyer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Safe-haven funding-currency buyer |
| Theory Family         | Safe-haven currency demand |
| Behavioral Tendency   | **Converging** - supplies partial counterflow during carry unwind stress |
| Time Horizon          | short to medium |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models reserve managers, risk-averse institutions, repatriating investors, or safe-haven allocators that buy the funding currency during market stress. It emits buy or hold decisions when funding-currency stress exceeds a threshold. The agent is deliberately smaller than forced sellers so it stabilizes partially without eliminating the crash.

The decision goal is capital preservation and safe-haven allocation. Non-goals: it must not become a leveraged carry seller, and it must not absorb unlimited forced liquidation.

## Theoretical Foundation

**Safe-haven currency demand**:
- Theory / Study: Safe haven currencies.
- Citation: Ranaldo, A., & Soderlind, P. (2010). Safe haven currencies. *Review of Finance*, 14(3), 385-407. https://doi.org/10.1093/rof/rfq007
- Core Insight: Certain currencies appreciate in risk-off states because investors seek liquidity and safety.
- Mathematical Formulation: `buy_qty = position_size` when `deviation < -risk_threshold`.
- Empirical Evidence: The study documents safe-haven behavior in CHF and JPY under stress.
- Relevance to This Agent: The agent is the stabilizing demand source during the funding-currency shock.
- Calibration Source: `risk_threshold` 0.03-0.08 and `position_size` 300-800.
- Falsification Conditions: If severe stress does not trigger buying, the safe-haven mechanism is absent.
- Alternative Theories: Central-bank intervention; long-horizon PPP value investing.

## Design Purpose and Activation Triggers

Purpose: Provide bounded safe-haven demand when funding-currency stress is severe.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `deviation` available
- own `cash` available

Missing-Signal Policy: hold when required inputs are missing.

Activation Triggers:
- `deviation < -risk_threshold`: buy `position_size`, capped by cash.
- `<Default>`: hold.

Deactivation Conditions:
- cash exhausted.
- deviation returns below risk threshold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| calm | hold | no safe-haven trigger |
| stress | buy funding currency | flight to quality |

Environmental Dependencies: none beyond declared signals and own cash.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `deviation` | environment | float | yes | downside stress trigger |
| `cash` | own state | float | yes | buy capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "hold"}` | none | yes | safe-haven action |
| `quantity` | float | `>= 0` | units | yes | buy quantity |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Quantity must not exceed cash divided by price.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

All variants must preserve the same threshold and bounded-buy output.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `deviation` | Continuous | 1 tick | downside stress threshold |
| `cash` | State | persistent | resource cap |

Does NOT use: carry yield, leverage, private dealer inventory.

#### Core Behavioral Mechanism

1. Read `price`, `deviation`, and `cash`.
2. If `deviation < -risk_threshold`, compute buy quantity as `position_size`.
3. Cap buy quantity by cash available.
4. Otherwise hold.
5. Emit decision and update state after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `min(position_size, cash / price)` |
| Action lifetime | one decision call |
| Revision policy | repeat bounded buying while stress persists |
| State constraint | no leverage |
| Resource cap | buy quantity capped by cash |
| Exit rule | stop buying when stress falls below threshold or cash is exhausted |

#### Mathematical Model

`q_buy = min(position_size, cash / price)` if `deviation < -risk_threshold`; otherwise `q_buy = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `risk_threshold` | safe-haven activation threshold | 0.05 | Ranaldo & Soderlind (2010) |
| `position_size` | bounded buy size | 500.0 | Ranaldo & Soderlind (2010), scenario normalization |

#### Behavioral Properties

- Time horizon: short to medium.
- Risk tolerance: low.
- Information asymmetry: partial.
- Psychological profile: capital preservation and safe-haven demand.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `risk_threshold` | float | 0.05 | [0.03, 0.08] | medium | stress threshold | Higher -> later support | Ranaldo & Soderlind (2010) |
| `position_size` | float | 500.0 | [300, 800] | medium | buy quantity | Higher -> stronger stabilization | Ranaldo & Soderlind (2010) |
| `cash_floor` | float | 0.0 | >= 0 | low | reserve floor | Higher -> less support | scenario normalization |

## Worked Numerical Examples

### Case 1 - Stress Buy
System state: deviation 0.06, price 1.05, cash 300000.
Calculation: `q = min(500, 300000 / 1.05) = 500`.
Decision: buy 500.
State update: cash decreases after execution.

### Case 2 - Calm Hold
System state: deviation 0.02.
Calculation: threshold not crossed.
Decision: hold.
State update: unchanged.

### Case 3 - Cash Cap
System state: deviation 0.06, price 1.05, cash 100.
Calculation: `q = min(500, 100 / 1.05) = 95.24`.
Decision: buy 95.24.
State update: cash nearly exhausted.

### Edge Case - Missing Price
System state: price unavailable.
Calculation: missing-signal policy.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `deviation < -risk_threshold`, agent must buy if cash permits.
- Given `cash = 0`, agent must hold.
- Given `deviation >= -risk_threshold`, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-safe-haven-buyer | `position_size = 0` | safe-haven flow limits crash depth | increase | max drawdown |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Ranaldo, A., & Soderlind, P. (2010). Safe haven currencies. https://doi.org/10.1093/rof/rfq007 | Safe-haven currency demand |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-08 |
| Version | 1.0.0 |
| Change log | Initial CarryTradeUnwind AGENT_POOL design |
| Status | draft |
