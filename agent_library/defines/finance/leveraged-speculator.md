# Leveraged Speculator

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Highly-leveraged directional speculator making concentrated bets |
| Theory Family         | Margin Spirals / Leverage-Induced Feedback |
| Behavioral Tendency   | **Destabilising** - takes large directional positions that amplify price swings and trigger margin cascades |
| Time Horizon          | short |
| Risk Tolerance        | very high |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a speculator (proprietary trader, aggressive hedge fund, or retail margin trader) who uses extreme leverage to make directional bets on price movements. The real-world counterpart is the margin-constrained speculator documented by Brunnermeier and Pedersen (2009): when prices move favorably the speculator doubles down, and when prices move against them the resulting margin calls force liquidation that pushes prices further, creating margin spirals.

The decision goal is to maximise short-term trading profit by taking large leveraged positions in the direction of perceived price movement. Non-goals: the agent does not provide liquidity, does not diversify, and must not ignore margin calls.

## Theoretical Foundation

**Margin spirals and destabilising speculation**:
- Theory / Study: Market liquidity and funding liquidity.
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: Leveraged speculators face margin constraints; adverse price moves reduce their equity, triggering forced liquidation that further depresses prices, creating a feedback loop (margin spiral).
- Mathematical Formulation: `Q = leverage * signal_strength * base_size` when `|signal| > entry_threshold`, direction aligned with signal sign.
- Empirical Evidence: Brunnermeier & Pedersen show that funding illiquidity and market illiquidity are mutually reinforcing through speculator balance sheets.
- Relevance to This Agent: The agent operationalises the leveraged directional bet and forced-liquidation mechanism.
- Calibration Source: `leverage` 8.0-20.0, `entry_threshold` 0.005-0.02, `margin_call_level` 0.70-0.90.
- Falsification Conditions: If the agent does not liquidate when margin is breached, or does not take directional positions when signal exceeds threshold, the design is falsified.
- Alternative Theories: Informed speculation (Kyle 1985) without leverage constraint; pure noise trading.

## Design Purpose and Activation Triggers

Purpose: Take concentrated leveraged directional bets that amplify price movements and demonstrate margin-spiral dynamics when prices reverse.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `signal` available (directional momentum or deviation signal)
- own `cash`, `position`, `equity`, and `margin_used` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `signal > entry_threshold`: buy aggressively with full leverage.
- `signal < -entry_threshold`: sell aggressively with full leverage.
- `margin_ratio < margin_call_level`: forced liquidation of entire position.
- `<Default>`: hold.

Deactivation Conditions:
- equity depleted (margin call wipes out fund).
- position already at maximum leverage capacity.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Strong positive signal | large leveraged buy | directional bet amplifies upward pressure |
| Strong negative signal | large leveraged sell | directional bet amplifies downward pressure |
| Margin breach | forced full liquidation | margin spiral triggers fire sale |
| Position profitable | doubles down (increases position) | winner reinforcement |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `signal` | environment | float | yes | directional indicator (positive = bullish) |
| `cash` | own state | float | yes | available margin |
| `position` | own state | float | yes | current holding (can be negative for short) |
| `equity` | own state | float | yes | net asset value |
| `margin_used` | own state | float | yes | fraction of margin capacity consumed |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must respect maximum leverage capacity and available margin.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution and P&L reference |
| `signal` | Continuous | 1 tick | directional trigger |
| `cash` | State | persistent | margin capacity |
| `position` | State | persistent | current exposure |
| `equity` | State | persistent | margin ratio denominator |
| `margin_used` | State | persistent | margin call check |

Does NOT use: fundamental value, peer signals, long-term indicators.

#### Core Behavioral Mechanism

1. Check margin ratio: if `margin_used > margin_call_level`, liquidate entire position (forced sale).
2. Read `signal`. If `|signal| <= entry_threshold`, hold.
3. If `signal > entry_threshold`: compute buy quantity `q = min(leverage * base_size, max_capacity - position)`.
4. If `signal < -entry_threshold`: compute sell quantity `q = min(leverage * base_size, position)` (or short if allowed).
5. Emit decision.
6. Update equity and margin after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `leverage * base_size`, subject to margin capacity |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | margin_used must not exceed 1.0 except triggering liquidation |
| Resource cap | limited by margin capacity and equity |
| Exit rule | forced liquidation when margin_ratio breaches margin_call_level |

#### Mathematical Model

`q_entry = min(leverage * base_size, margin_capacity_remaining / price)`

`q_liquidate = abs(position)` when `margin_used > margin_call_level`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `leverage` | leverage multiplier | 12.0 | Brunnermeier & Pedersen (2009) |
| `base_size` | base position unit | 500.0 | scenario normalization |
| `entry_threshold` | minimum signal for trade | 0.01 | calibration |
| `margin_call_level` | margin utilization trigger | 0.85 | exchange convention |
| `max_position` | maximum absolute position | 10000.0 | risk limit |

#### Behavioral Properties

- Time horizon: short, because leveraged bets are held briefly.
- Risk tolerance: very high, because extreme leverage implies potential total loss.
- Information asymmetry: partial, uses a signal that may be noisy.
- Psychological profile: aggressive risk-seeker who doubles down on winners and is forcibly removed on losers.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `leverage` | float | 12.0 | [8.0, 20.0] | high | position multiplier relative to equity | Higher -> larger positions, more fragile | Brunnermeier & Pedersen (2009) |
| `base_size` | float | 500.0 | [200, 1000] | medium | base order size before leverage | Higher -> larger market impact | scenario normalization |
| `entry_threshold` | float | 0.01 | [0.005, 0.02] | medium | minimum signal magnitude to trade | Lower -> more frequent entry | calibration |
| `margin_call_level` | float | 0.85 | [0.70, 0.90] | high | margin utilization that triggers forced liquidation | Lower -> earlier forced sales | exchange convention |
| `max_position` | float | 10000.0 | [5000, 20000] | low | hard cap on absolute position size | Lower -> limits systemic impact | risk management |

## Worked Numerical Examples

### Case 1 - Directional Buy
System state: price 100, signal 0.03 (> 0.01 threshold), equity 100000, margin_used 0.30.
Calculation: `q = min(12 * 500, (1.0 - 0.30) * 100000 / 100) = min(6000, 700) = 700`.
Decision: buy 700.
State update: position increases, margin_used increases.

### Case 2 - Directional Sell
System state: price 100, signal -0.025, position 3000, margin_used 0.50.
Calculation: `q = min(12 * 500, 3000) = min(6000, 3000) = 3000`.
Decision: sell 3000.
State update: position decreases to zero.

### Case 3 - Hold (Weak Signal)
System state: price 100, signal 0.005 (< 0.01 threshold).
Calculation: signal below entry threshold.
Decision: hold.
State update: unchanged.

### Edge Case - Margin Call Liquidation
System state: price 80 (dropped from entry at 100), position 5000, margin_used 0.92 (> 0.85).
Calculation: `q_liquidate = abs(5000) = 5000`. Forced liquidation.
Decision: sell 5000 (forced).
State update: position goes to zero, remaining equity preserved.

## Behavioral Verification and Calibration

- Given signal above entry_threshold and available margin, agent must take leveraged position in signal direction.
- Given margin_used exceeding margin_call_level, agent must immediately liquidate entire position.
- Given signal below entry_threshold, agent must hold.
- Given zero equity, agent must cease trading permanently.
- Given missing signal, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| low-leverage | `leverage = 2.0` | high leverage drives margin spirals | decrease | forced-liquidation frequency |
| no-margin-call | `margin_call_level = 1.0` | margin calls cause fire-sale cascades | decrease | crash depth |
| tight-threshold | `entry_threshold = 0.05` | frequent entry amplifies volatility | decrease | price volatility |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 | Core margin spiral theory |
| 2 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 | Informed trading with price impact |
| 3 | Gromb, D., & Vayanos, D. (2002). Equilibrium and welfare in markets with financially constrained arbitrageurs. *Journal of Financial Economics*, 66(2-3), 361-407. | Constrained speculation |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-leveraged-speculator.png) |
| Status | draft |
