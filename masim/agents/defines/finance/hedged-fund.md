# Hedged fund

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Long-short hedge fund with risk management |
| Theory Family         | Limits of Arbitrage / Performance-Flow Sensitivity |
| Behavioral Tendency   | **Stabilising** - exploits mispricings via long-short positions but deleverages under redemption pressure |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a sophisticated hedge fund that maintains long positions in undervalued assets and short positions in overvalued assets, seeking to earn the spread while hedging market risk. The real-world counterpart is the constrained arbitrageur documented by Shleifer and Vishny (1997) who faces performance-based fund flows and cannot always maintain positions through temporary mispricings. The agent emits buy, sell, or hold orders with quantity driven by the valuation spread and fund-flow constraints.

The decision goal is to earn returns from long-short value spreads while managing risk through position sizing and leverage constraints. The agent increases positions when the spread widens (opportunity) but is forced to reduce exposure when drawdowns trigger fund redemptions or risk limits are breached. Non-goals: it must not take concentrated directional bets without a hedge, and it must not ignore fund-flow constraints when performance deteriorates.

The agent is designed for scenarios exploring limits of arbitrage, how constrained capital can fail to correct mispricings, and how performance-flow sensitivity creates pro-cyclical deleveraging.

## Theoretical Foundation

**Limits of arbitrage**:
- Theory / Study: The limits of arbitrage.
- Citation: Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Arbitrageurs with external capital face agency problems: poor short-term performance triggers capital withdrawals precisely when mispricings are widest, preventing them from correcting prices and potentially forcing them to liquidate at the worst time.
- Mathematical Formulation: `Q_long = spread_size * valuation_spread` when `spread > entry_threshold` and `drawdown < max_drawdown`; force-reduce when `drawdown >= max_drawdown`.
- Empirical Evidence: Shleifer & Vishny explain LTCM-style failures where correct fundamental views are overwhelmed by funding constraints.
- Relevance to This Agent: The agent captures both the arbitrage function and the performance-flow constraint that limits it.
- Calibration Source: `entry_threshold` 0.05-0.15, `spread_size` 300-1000, `max_drawdown` 0.10-0.25.
- Falsification Conditions: If the agent increases positions during drawdown exceeding max_drawdown, the design is falsified.
- Alternative Theories: Unconstrained arbitrage (efficient markets); delegated portfolio management (Vayanos 2004).

**Performance-flow sensitivity**:
- Theory / Study: The behavior of mutual fund investors.
- Citation: Chevalier, J. & Ellison, G. (1997). Risk taking by mutual funds as a response to incentives. *Journal of Political Economy*, 105(6), 1167-1200. https://doi.org/10.1086/516389
- Core Insight: Fund investors withdraw capital after poor performance in a convex flow-performance relationship, forcing managers to reduce positions precisely when opportunities are greatest.
- Mathematical Formulation: Fund outflow = `flow_sensitivity * max(0, drawdown - drawdown_tolerance)`.
- Empirical Evidence: Chevalier & Ellison document the convex flow-performance relationship across thousands of funds.
- Relevance to This Agent: Calibrates the drawdown-triggered deleveraging that constrains the arbitrageur.
- Calibration Source: Outflow rates of 20-50% of AUM per quarter after significant underperformance.
- Falsification Conditions: If the agent does not reduce exposure after sustained drawdown, design is falsified.
- Alternative Theories: Loyal capital (endowments); lock-up provisions.

## Design Purpose and Activation Triggers

Purpose: Exploit valuation spreads via long-short positioning while respecting drawdown-triggered deleveraging constraints, modelling the limits of arbitrage.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `valuation_spread` available (long asset undervaluation - short asset overvaluation signal)
- `drawdown` available (current peak-to-trough loss measure)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `drawdown >= max_drawdown`: sell sized by `deleverage_fraction * position` (forced deleveraging).
- `valuation_spread > entry_threshold` and `drawdown < max_drawdown`: buy sized by `spread_size * valuation_spread`.
- `valuation_spread < -exit_threshold`: sell sized by `min(position, spread_size * abs(valuation_spread))` (spread collapsed, exit).
- `<Default>`: hold.

Deactivation Conditions:
- drawdown triggers full deleveraging.
- valuation spread narrows below entry threshold.
- position fully unwound.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| wide spread, low drawdown | increases long-short position | arbitrage opportunity |
| drawdown exceeds limit | deleverages regardless of opportunity | performance-flow constraint |
| spread narrows | holds or exits | arbitrage thesis resolved |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `valuation_spread` | model | float | yes | long-short opportunity signal |
| `drawdown` | own state | float | yes | peak-to-trough performance |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | current net exposure |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `valuation_spread` | Continuous | 1 tick | arbitrage signal |
| `drawdown` | State | persistent | deleveraging trigger |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint |

Does NOT use: insider information, fund flow predictions, peer positioning data.

#### Core Behavioral Mechanism

1. Read `price`, `valuation_spread`, `drawdown`, `cash`, and `position`.
2. If `drawdown >= max_drawdown`, compute sell quantity as `deleverage_fraction * position` (forced deleveraging takes priority).
3. Else if `valuation_spread > entry_threshold`, compute buy quantity as `min(cash / price, spread_size * valuation_spread)`.
4. Else if `valuation_spread < -exit_threshold`, compute sell quantity as `min(position, spread_size * abs(valuation_spread))`.
5. Otherwise, hold.
6. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | buy: `spread_size * valuation_spread`; sell: `deleverage_fraction * position` or spread-based |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero; net exposure bounded by leverage limit |
| Resource cap | buy cannot exceed cash / price |
| Exit rule | deleverage when drawdown exceeds limit; exit when spread inverts |

#### Mathematical Model

`q_sell = deleverage_fraction * position` if `drawdown >= D`; `q_buy = min(cash/price, spread_size * S)` if `S > theta_entry` and `drawdown < D`; `q_sell = min(position, spread_size * |S|)` if `S < -theta_exit`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `D` | maximum drawdown before forced deleveraging | 0.15 | Shleifer & Vishny (1997) |
| `theta_entry` | spread entry threshold | 0.08 | calibration |
| `theta_exit` | spread exit/reversal threshold | 0.03 | calibration |
| `spread_size` | base position size per unit of spread | 600.0 | scenario normalization |
| `deleverage_fraction` | fraction sold under drawdown | 0.4 | Chevalier & Ellison (1997) |

#### Behavioral Properties

- Time horizon: medium, because arbitrage positions require time to converge.
- Risk tolerance: medium, because the agent hedges but still takes leveraged spread risk.
- Information asymmetry: partial, because the agent uses a valuation model superior to noise traders.
- Psychological profile: disciplined, quantitative, risk-aware but constrained by external capital providers.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `max_drawdown` | float | 0.15 | [0.10, 0.25] | high | drawdown level triggering forced deleveraging | Lower -> more frequent forced exits | Shleifer & Vishny (1997) |
| `spread_size` | float | 600.0 | [300, 1000] | high | base units per unit of valuation spread | Higher -> more aggressive positioning | scenario normalization |
| `entry_threshold` | float | 0.08 | [0.05, 0.15] | medium | minimum spread to initiate position | Higher -> fewer trades, larger opportunities | calibration |
| `deleverage_fraction` | float | 0.4 | [0.2, 0.6] | medium | fraction of position sold during deleveraging | Higher -> faster forced exit | Chevalier & Ellison (1997) |

## Worked Numerical Examples

### Case 1 - Enter Long-Short Position
System state: price 100.0, valuation_spread 0.12, drawdown 0.05, cash 300000, entry_threshold 0.08.
Calculation: spread (0.12) > threshold (0.08), drawdown (0.05) < max (0.15). `q = min(300000/100, 600 * 0.12) = min(3000, 72) = 72`.
Decision: buy 72.
State update: position increases by 72; cash decreases by 7200.

### Case 2 - Forced Deleveraging
System state: price 85.0, valuation_spread 0.20, drawdown 0.18, position 2000, max_drawdown 0.15.
Calculation: drawdown (0.18) >= max_drawdown (0.15). Deleveraging overrides opportunity. `q = 0.4 * 2000 = 800`.
Decision: sell 800.
State update: position decreases to 1200.

### Case 3 - Spread Collapsed (Exit)
System state: price 105.0, valuation_spread -0.05, drawdown 0.03, position 1500, exit_threshold 0.03.
Calculation: spread (-0.05) < -exit_threshold (-0.03). `q = min(1500, 600 * 0.05) = min(1500, 30) = 30`.
Decision: sell 30.
State update: position decreases to 1470.

### Edge Case - Drawdown with Zero Position
System state: price 90.0, drawdown 0.20, position 0.
Calculation: drawdown exceeds max but position = 0. Nothing to sell.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `drawdown >= max_drawdown` and positive position, agent must sell (deleverage).
- Given wide spread and low drawdown, agent must buy if cash permits.
- Given spread inversion and positive position, agent must sell.
- Agent must never increase position when drawdown exceeds max_drawdown.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| unconstrained-arb | `max_drawdown = infinity` | capital constraints prevent price correction | decrease | mispricing duration |
| no-spread-entry | `entry_threshold = infinity` | arbitrageur corrects mispricings | increase | spread persistence |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Limits of arbitrage theory |
| 2 | Chevalier, J. & Ellison, G. (1997). Risk taking by mutual funds as a response to incentives. https://doi.org/10.1086/516389 | Performance-flow sensitivity |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-hedged-fund.png) |
| Status | draft |
