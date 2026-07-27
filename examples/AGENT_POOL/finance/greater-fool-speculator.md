# Greater fool speculator

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Momentum-driven greater-fool speculator |
| Theory Family         | Greater Fool Theory / Rational Bubbles |
| Behavioral Tendency   | **Destabilising** - buys overvalued assets expecting to resell to a later buyer at even higher prices |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a speculator who knowingly purchases overvalued assets on the expectation that a "greater fool" will buy at an even higher price before the bubble bursts. The real-world counterpart is the momentum trader in bubble markets documented by Tirole (1985) on rational bubbles and Scheinkman and Xiong (2003) on speculative overpricing. The agent emits buy, sell, or hold orders with quantity driven by price momentum and proximity to a perceived exit threshold.

The decision goal is to ride upward price momentum and exit before the bubble collapses. The agent buys when momentum is positive and price remains below its estimated crash threshold, and sells when price approaches or exceeds that threshold. Non-goals: it must not hold through a crash (it attempts to exit), and it must not invest based on fundamental value analysis.

The agent is designed for scenarios exploring asset bubbles, speculative dynamics, coordination failure, and the endogenous timing of bubble collapse.

## Theoretical Foundation

**Rational bubbles**:
- Theory / Study: Asset bubbles and overlapping generations.
- Citation: Tirole, J. (1985). Asset bubbles and overlapping generations. *Econometrica*, 53(6), 1499-1528. https://doi.org/10.2307/1913232
- Core Insight: Rational bubbles can exist in equilibrium when agents expect to sell to future participants at higher prices. Each buyer is rational conditional on finding a buyer; the bubble persists until the marginal fool is exhausted.
- Mathematical Formulation: `Q_buy = momentum_size * momentum_signal` when `price < crash_threshold` and `momentum_signal > 0`.
- Empirical Evidence: Tirole provides theoretical conditions; empirical bubbles in dot-com, housing, and crypto markets exhibit greater-fool dynamics.
- Relevance to This Agent: The agent is a node in the rational bubble chain, buying overvalued assets because it expects a later buyer.
- Calibration Source: `crash_threshold` 1.5-3.0 (multiple of fundamental), `momentum_size` 300-1000, `exit_speed` 0.5-1.0.
- Falsification Conditions: If the agent buys after price exceeds crash_threshold, the design is falsified.
- Alternative Theories: Irrational exuberance (Shiller 2000); herding without rationality.

**Speculative overpricing with heterogeneous beliefs**:
- Theory / Study: Overconfidence and speculative bubbles.
- Citation: Scheinkman, J. A. & Xiong, W. (2003). Overconfidence and speculative bubbles. *Journal of Political Economy*, 111(6), 1183-1220. https://doi.org/10.1086/378531
- Core Insight: When agents disagree and short-sale constraints bind, assets trade above the valuation of the most optimistic holder because they contain a resale option - the right to sell to a future optimist.
- Mathematical Formulation: Asset price = fundamental + resale option value; resale option increases with belief dispersion.
- Empirical Evidence: Scheinkman & Xiong explain why speculative assets trade far above any agent's valuation during bubbles.
- Relevance to This Agent: The agent captures the resale-option logic: it buys not for value but for the embedded option to sell higher.
- Calibration Source: Resale premium estimates from dot-com and crypto bubble data.
- Falsification Conditions: If the agent does not attempt to exit as crash_threshold approaches, design is falsified.
- Alternative Theories: Fundamental-based momentum; information cascade models (Bikhchandani et al. 1992).

## Design Purpose and Activation Triggers

Purpose: Buy into rising markets expecting to resell at higher prices, and exit before the estimated crash point, modelling speculative bubble participation.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `momentum_signal` available (recent price return or trend indicator)
- `fundamental_value` available (for computing overvaluation ratio)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `momentum_signal > 0` and `price < fundamental_value * crash_threshold`: buy sized by `momentum_size * momentum_signal`.
- `price >= fundamental_value * crash_threshold * exit_trigger`: sell all position (exit before crash).
- `momentum_signal < 0` and `position > 0`: sell sized by `exit_speed * position` (momentum reversal exit).
- `<Default>`: hold.

Deactivation Conditions:
- price reaches crash threshold (full exit).
- momentum turns negative and position is liquidated.
- cash exhausted.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| positive momentum, below crash threshold | buys aggressively | greater-fool accumulation |
| price near crash threshold | sells entire position | exit before collapse |
| momentum reversal | sells proportionally | loss-cutting exit |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `momentum_signal` | environment | float | yes | recent return or trend |
| `fundamental_value` | environment | float | yes | intrinsic value anchor |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

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
| `price` | Continuous | 1 tick | execution and threshold check |
| `momentum_signal` | Continuous | 1 tick | buy/exit trigger |
| `fundamental_value` | Continuous | 1 tick | crash threshold anchor |
| `cash` | State | persistent | buy sizing |
| `position` | State | persistent | exit sizing |

Does NOT use: insider information, fundamental analysis for valuation, long-term forecasts.

#### Core Behavioral Mechanism

1. Read `price`, `momentum_signal`, `fundamental_value`, `cash`, and `position`.
2. Compute `overvaluation_ratio = price / fundamental_value`.
3. If `overvaluation_ratio >= crash_threshold * exit_trigger`, sell all position (emergency exit).
4. If `momentum_signal < 0` and `position > 0`, sell `exit_speed * position`.
5. If `momentum_signal > 0` and `overvaluation_ratio < crash_threshold`, buy `min(cash / price, momentum_size * momentum_signal)`.
6. Otherwise, hold.
7. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | buy: `momentum_size * momentum_signal`; sell: `exit_speed * position` or full position |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy cannot exceed cash / price |
| Exit rule | sell all when crash threshold approached; sell proportionally on momentum reversal |

#### Mathematical Model

`q_buy = min(cash/price, momentum_size * m)` if `m > 0` and `P/F < C`; `q_sell = position` if `P/F >= C * E`; `q_sell = exit_speed * position` if `m < 0`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `C` | crash threshold (multiple of fundamental) | 2.0 | Tirole (1985) |
| `E` | exit trigger (fraction of crash threshold) | 0.9 | calibration |
| `momentum_size` | base buy size per unit momentum | 500.0 | scenario normalization |
| `exit_speed` | fraction of position sold on reversal | 0.7 | loss-cutting calibration |

#### Behavioral Properties

- Time horizon: short, because the agent aims to flip before the crash.
- Risk tolerance: high, because the agent knowingly buys overvalued assets.
- Information asymmetry: none, because the agent does not possess private information.
- Psychological profile: speculative, momentum-chasing, overconfident in timing ability.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `crash_threshold` | float | 2.0 | [1.5, 3.0] | high | multiple of fundamental at which agent expects collapse | Higher -> agent rides bubble longer | Tirole (1985) |
| `momentum_size` | float | 500.0 | [300, 1000] | high | base units bought per unit of momentum signal | Higher -> more aggressive accumulation | scenario normalization |
| `exit_speed` | float | 0.7 | [0.5, 1.0] | medium | fraction of position sold on momentum reversal | Higher -> faster exit, less crash exposure | calibration |
| `exit_trigger` | float | 0.9 | [0.8, 0.95] | medium | fraction of crash_threshold that triggers full exit | Lower -> earlier exit, more profit left on table | calibration |

## Worked Numerical Examples

### Case 1 - Buy Into Bubble
System state: price 150.0, fundamental_value 100.0, momentum_signal 0.05, cash 200000, crash_threshold 2.0.
Calculation: overvaluation = 150/100 = 1.5 < 2.0 (crash_threshold). Momentum positive. `q = min(200000/150, 500 * 0.05) = min(1333, 25) = 25`.
Decision: buy 25.
State update: position increases by 25; cash decreases by 3750.

### Case 2 - Exit at Crash Threshold
System state: price 185.0, fundamental_value 100.0, position 500, crash_threshold 2.0, exit_trigger 0.9.
Calculation: overvaluation = 185/100 = 1.85 >= 2.0 * 0.9 = 1.8. Exit triggered. `q = 500`.
Decision: sell 500.
State update: position decreases to 0; cash increases by 92500.

### Case 3 - Momentum Reversal Exit
System state: price 160.0, fundamental_value 100.0, momentum_signal -0.02, position 400, exit_speed 0.7.
Calculation: momentum negative, position > 0. `q = 0.7 * 400 = 280`.
Decision: sell 280.
State update: position decreases to 120.

### Edge Case - No Cash for Buying
System state: price 130.0, fundamental_value 100.0, momentum_signal 0.1, cash 0, position 200.
Calculation: momentum positive, below threshold, but cash = 0. `q = min(0/130, 50) = 0`.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given positive momentum and price below crash threshold, agent must buy if cash permits.
- Given price at or above exit_trigger * crash_threshold * fundamental_value, agent must sell all.
- Given negative momentum and positive position, agent must sell proportionally.
- Agent must never buy above crash_threshold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-exit-threshold | `crash_threshold = infinity` | exit attempts prevent total loss | increase | agent final loss |
| slow-exit | `exit_speed = 0.2` | faster exit reduces crash exposure | increase | position held at crash |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Tirole, J. (1985). Asset bubbles and overlapping generations. https://doi.org/10.2307/1913232 | Rational bubble theory |
| 2 | Scheinkman, J. A. & Xiong, W. (2003). Overconfidence and speculative bubbles. https://doi.org/10.1086/378531 | Resale option and speculative overpricing |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-greater-fool-speculator.png) |
| Status | draft |
