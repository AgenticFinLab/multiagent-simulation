# Carry trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Leveraged currency carry trader |
| Theory Family         | Carry Trade / Risk-On-Risk-Off |
| Behavioral Tendency   | **Diverging** - accumulates carry exposure in calm markets and exits into funding-currency appreciation |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a hedge fund, macro fund, or leveraged currency investor that borrows in a low-yield funding currency and holds a higher-yield target-currency position. The real-world counterpart is the carry-trade participant documented by Brunnermeier, Nagel, and Pedersen (2009). The agent emits buy, sell, or hold orders with quantity tied to leverage, base size, and exchange-rate deviation.

The decision goal is to earn carry in stable conditions while reducing exposure when the funding currency appreciates. It is not a value investor and it does not provide liquidity as a dealer. Non-goals: it must not use private central-bank information, and it must not ignore its own leverage constraint when the funding-currency shock appears.

## Theoretical Foundation

**Carry trade crash risk**:
- Theory / Study: Carry trades and currency crashes.
- Citation: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). Carry trades and currency crashes. *NBER Macroeconomics Annual*, 23(1), 313-348. https://doi.org/10.1086/593088
- Core Insight: Leveraged carry positions earn a premium in calm states but suffer concentrated losses when funding currencies appreciate. Crowding makes exits correlated.
- Mathematical Formulation: `Q = leverage * carry_size` when `abs(deviation) > unwind_threshold`, with direction set by deviation sign.
- Empirical Evidence: Brunnermeier et al. document negative skewness and crash exposure in carry returns.
- Relevance to This Agent: The agent operationalises carry accumulation and unwind thresholds.
- Calibration Source: `unwind_threshold` 0.01-0.04, `carry_size` 400-1200, `leverage` 3.0-8.0.
- Falsification Conditions: If the agent does not reduce exposure after funding-currency appreciation crosses threshold, the design is falsified.
- Alternative Theories: Momentum FX strategy; uncovered-interest-parity arbitrage without crash risk.

## Design Purpose and Activation Triggers

Purpose: Build carry exposure in benign conditions and unwind when funding-currency appreciation breaches the carry risk threshold.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `deviation` available
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `deviation < -unwind_threshold`: buy carry exposure sized by `leverage * carry_size`.
- `deviation > unwind_threshold`: sell carry exposure sized by `min(position, leverage * carry_size)`.
- `<Default>`: hold.

Deactivation Conditions:
- position exhausted during unwind.
- cash insufficient during accumulation.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| calm negative deviation | accumulates exposure | carry premium harvesting |
| funding-currency appreciation | exits exposure | crash-risk control |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `deviation` | environment | float | yes | carry and unwind trigger |
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
| `price` | Continuous | 1 tick | execution reference |
| `deviation` | Continuous | 1 tick | carry/unwind threshold |
| `cash` | State | persistent | position sizing |
| `position` | State | persistent | sell constraint |

Does NOT use: media sentiment, private policy signals, peer topology.

#### Core Behavioral Mechanism

1. Read `price`, `deviation`, `cash`, and `position`.
2. If `deviation < -unwind_threshold`, compute buy quantity as `leverage * carry_size`, capped by cash.
3. If `deviation > unwind_threshold`, compute sell quantity as `min(position, leverage * carry_size)`.
4. If neither threshold is crossed, hold.
5. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `leverage * carry_size`, capped by resource constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero unless scenario explicitly allows short carry |
| Resource cap | buy quantity cannot exceed cash / price |
| Exit rule | sell when `deviation > unwind_threshold` |

#### Mathematical Model

`q_buy = min(cash / price, leverage * carry_size)` if `deviation < -theta`; `q_sell = min(position, leverage * carry_size)` if `deviation > theta`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta` | unwind threshold | 0.02 | Brunnermeier et al. (2009) |
| `leverage` | leverage multiplier | 5.0 | Brunnermeier et al. (2009) |
| `carry_size` | base carry units | 800.0 | Brunnermeier et al. (2009), scenario normalization |
| `deviation_scale` | deviation sizing scale | 5000.0 | Brunnermeier et al. (2009), scenario normalization |

#### Behavioral Properties

- Time horizon: medium, because carry trades accumulate before stress.
- Risk tolerance: high, because leverage is central.
- Information asymmetry: partial.
- Psychological profile: yield-seeking risk-on discipline with crash-risk exit.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `unwind_threshold` | float | 0.02 | [0.01, 0.04] | high | funding-currency appreciation trigger | Higher -> later unwind | Brunnermeier et al. (2009) |
| `leverage` | float | 5.0 | [3.0, 8.0] | high | position multiplier | Higher -> larger order imbalance | Brunnermeier et al. (2009) |
| `carry_size` | float | 800.0 | [400, 1200] | medium | base carry order size | Higher -> larger buildup and unwind | Brunnermeier et al. (2009), scenario normalization |
| `deviation_scale` | float | 5000.0 | [2500, 7500] | medium | deviation-proportional sizing scale | Higher -> more quantity per unit deviation | Brunnermeier et al. (2009), scenario normalization |

## Worked Numerical Examples

### Case 1 - Accumulate
System state: price 1.0, deviation -0.03, cash 500000, position 500.
Calculation: `q = min(500000 / 1.0, 5 * 800) = 4000`.
Decision: buy 4000.
State update: position increases after execution.

### Case 2 - Unwind
System state: price 1.04, deviation 0.04, position 500.
Calculation: `q = min(500, 5 * 800) = 500`.
Decision: sell 500.
State update: position decreases after execution.

### Case 3 - Hold
System state: price 1.0, deviation 0.0.
Calculation: no threshold crossed.
Decision: hold.
State update: unchanged.

### Edge Case - No Inventory
System state: deviation 0.04, position 0.
Calculation: `q = min(0, 500) = 0`.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `deviation < -unwind_threshold`, agent must buy if cash permits.
- Given `deviation > unwind_threshold`, agent must sell if position is positive.
- Given missing price, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-carry-accumulation | `carry_size = 0` | carry buildup is required for unwind volume | decrease | carry volume |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). Carry trades and currency crashes. https://doi.org/10.1086/593088 | Core carry crash theory |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-08 |
| Version | 1.0.0 |
| Change log | Initial CarryTradeUnwind AGENT_POOL design |
| Status | draft |
