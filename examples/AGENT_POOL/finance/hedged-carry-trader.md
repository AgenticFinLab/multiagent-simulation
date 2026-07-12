# Hedged carry trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Volatility-managed hedged carry trader |
| Theory Family         | Volatility-managed carry |
| Behavioral Tendency   | **Adaptive** - accumulates carry in low volatility and exits when volatility rises |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a macro fund that runs carry exposure with explicit volatility controls or option hedges. It is a fork of the volatility-managed hedging family, adapted to FX carry rather than generic crash insurance. The agent emits buy, sell, or hold orders based on deviation and rolling volatility.

The decision goal is risk-adjusted carry participation. Non-goals: it must not add exposure when volatility is above threshold, and it must not ignore the hedge ratio when sizing trades.

## Theoretical Foundation

**Global FX volatility factor**:
- Theory / Study: Carry trades and global foreign exchange volatility.
- Citation: Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). Carry trades and global foreign exchange volatility. *Journal of Finance*, 67(2), 681-718. https://doi.org/10.1111/j.1540-6261.2012.01728.x
- Core Insight: Carry returns are negatively related to global FX volatility, so volatility-aware traders reduce exposure as volatility rises.
- Mathematical Formulation: `adj_qty = base_size * (1 - hedge_ratio)` when `rolling_vol < vol_threshold`; sell `adj_qty` when `rolling_vol > vol_threshold`.
- Empirical Evidence: Menkhoff et al. document the global FX volatility risk factor in carry returns.
- Relevance to This Agent: The agent conditions carry participation on rolling volatility and hedge ratio.
- Calibration Source: `hedge_ratio` 0.20-0.50, `vol_threshold` 0.03-0.08.
- Falsification Conditions: If high volatility does not reduce exposure, volatility-managed carry is absent.
- Alternative Theories: Static carry; long-vol hedge overlay.

## Design Purpose and Activation Triggers

Purpose: Participate in carry only when volatility is low and exit early when volatility rises.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `deviation` available
- `rolling_vol` available
- own `cash` and `position` available

Missing-Signal Policy: hold when price, deviation, or volatility is unavailable.

Activation Triggers:
- `deviation < 0 and rolling_vol < vol_threshold`: buy `base_size * (1 - hedge_ratio)`.
- `rolling_vol > vol_threshold and position > 0`: sell `min(position, base_size * (1 - hedge_ratio))`.
- `<Default>`: hold.

Deactivation Conditions:
- high volatility persists.
- cash or position exhausted.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| low volatility | accumulates hedged carry | volatility-managed exposure |
| high volatility | exits exposure | risk control |

Environmental Dependencies: requires a price-history window sufficient to compute rolling volatility.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `deviation` | environment | float | yes | carry opportunity |
| `rolling_vol` | environment or agent state | float | yes | volatility trigger |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | hedged order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Quantity equals hedged size capped by cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

All variants must preserve volatility gating and hedge-ratio sizing.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `deviation` | Continuous | 1 tick | carry opportunity |
| `rolling_vol` | Continuous | recent window | volatility risk state |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell capacity |

Does NOT use: media narrative, private policy signals, unrelated equity momentum.

#### Core Behavioral Mechanism

1. Read price, deviation, rolling volatility, cash, and position.
2. Compute hedged size `adj_qty = base_size * (1 - hedge_ratio)`.
3. If volatility is low and carry conditions are favorable, buy capped by cash.
4. If volatility is high and position is positive, sell capped by position.
5. Otherwise hold and preserve state.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `base_size * (1 - hedge_ratio)` capped by resources |
| Action lifetime | one decision call |
| Revision policy | re-evaluate volatility every tick |
| State constraint | no leverage above hedged size |
| Resource cap | buy capped by cash; sell capped by position |
| Exit rule | exit when `rolling_vol > vol_threshold` |

#### Mathematical Model

`adj_qty = base_size * (1 - hedge_ratio)`. Buy if `deviation < 0 and rolling_vol < vol_threshold`; sell if `rolling_vol > vol_threshold and position > 0`; otherwise hold.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `hedge_ratio` | hedged share | 0.30 | Menkhoff et al. (2012) |
| `vol_threshold` | volatility exit threshold | 0.05 | Menkhoff et al. (2012) |
| `base_size` | base order units | 500.0 | scenario normalization |

#### Behavioral Properties

- Time horizon: medium.
- Risk tolerance: medium.
- Information asymmetry: partial.
- Psychological profile: volatility-aware institutional discipline.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `hedge_ratio` | float | 0.30 | [0.20, 0.50] | low | hedged share | Higher -> smaller directional quantity | Menkhoff et al. (2012) |
| `vol_threshold` | float | 0.05 | [0.03, 0.08] | medium | volatility exit threshold | Higher -> later exit | Menkhoff et al. (2012) |
| `base_size` | float | 500.0 | > 0 | medium | base order size | Higher -> larger entry and exit | scenario normalization |

## Worked Numerical Examples

### Case 1 - Low-Vol Entry
System state: deviation -0.02, rolling_vol 0.03, cash 300000.
Calculation: `adj_qty = 500 * (1 - 0.30) = 350`.
Decision: buy 350.
State update: position increases.

### Case 2 - High-Vol Exit
System state: rolling_vol 0.06, position 350.
Calculation: `q = min(350, 350) = 350`.
Decision: sell 350.
State update: position decreases.

### Case 3 - High-Vol No Position
System state: rolling_vol 0.06, position 0.
Calculation: no sell capacity.
Decision: hold.
State update: unchanged.

### Edge Case - Missing Volatility
System state: rolling_vol unavailable.
Calculation: missing-signal policy.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given low volatility and negative deviation, agent must buy hedged size.
- Given high volatility and positive position, agent must sell.
- Given missing volatility, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-vol-exit | `vol_threshold = 1.0` | volatility exits reduce peak forced selling | increase | drawdown and late sell volume |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). Carry trades and global foreign exchange volatility. https://doi.org/10.1111/j.1540-6261.2012.01728.x | Volatility-managed carry exposure |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-08 |
| Version | 1.0.1 |
| Icon | ![](../agent_images/icons/finance-hedged-carry-trader.png) |
| Change log | Initial CarryTradeUnwind fork from volatility-managed hedging family; 1.0.1 — Added Icon row via polish-simulation-pipeline Step 2 icon-repair |
| Status | draft |
