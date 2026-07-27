# Passive Bystander

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Inattentive observer who rarely trades |
| Theory Family         | Rational Inattention / Information Processing Constraints |
| Behavioral Tendency   | **Stabilising** - absorbs information passively and only acts under extreme deviations, dampening noise |
| Time Horizon          | long |
| Risk Tolerance        | very low |
| Information Asymmetry | high (uninformed by choice) |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor who observes the market but rarely trades due to attention costs and information-processing constraints. The real-world counterpart is the rationally inattentive household investor documented by Sims (2003) and Gabaix (2014). The agent only acts when price deviations from a perceived fundamental exceed an extreme threshold, reflecting the idea that processing and acting on information is costly.

The decision goal is to remain inactive unless an extreme mispricing is observed, at which point it provides stabilising liquidity. It is not an active trader and it does not seek alpha. Non-goals: it must not trade in normal market conditions, and it must not respond to small price fluctuations.

## Theoretical Foundation

**Rational inattention**:
- Theory / Study: Implications of rational inattention; A sparsity-based model of bounded rationality.
- Citation: Sims, C. A. (2003). Implications of rational inattention. *Journal of Monetary Economics*, 50(3), 665-690. https://doi.org/10.1016/S0304-3932(03)00029-1
- Citation: Gabaix, X. (2014). A sparsity-based model of bounded rationality. *Quarterly Journal of Economics*, 129(4), 1661-1710. https://doi.org/10.1093/qje/qju024
- Core Insight: Information processing has a finite capacity (Shannon entropy constraint). Agents optimally ignore small signals and respond only to large deviations that justify the cognitive cost of processing and acting.
- Mathematical Formulation: `Q = rebalance_size` when `abs(price - fundamental) / fundamental > inaction_threshold`.
- Empirical Evidence: Sims shows infrequent portfolio adjustment is optimal under capacity constraints; Gabaix shows sparse attention matches observed household behavior.
- Relevance to This Agent: The agent operationalizes the inaction band from rational inattention theory.
- Calibration Source: `inaction_threshold` 0.10-0.30, `rebalance_size` 50-500.
- Falsification Conditions: If the agent trades when price is within the inaction band, the design is falsified.
- Alternative Theories: Transaction cost models (Constantinides 1986); pure buy-and-hold with no rebalancing trigger.

## Design Purpose and Activation Triggers

Purpose: Represent the large mass of inactive investors who provide stabilising demand only during extreme mispricings, creating implicit price floors and ceilings.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available (perceived fair value)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `(price - fundamental) / fundamental < -inaction_threshold` AND `cash > 0`: buy `rebalance_size` units.
- `(price - fundamental) / fundamental > inaction_threshold` AND `position > 0`: sell `min(position, rebalance_size)` units.
- `<Default>`: hold.

Deactivation Conditions:
- price returns within inaction band.
- resources exhausted (cash or position).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| extreme undervaluation | buys | perceived bargain exceeds attention cost |
| extreme overvaluation | sells | perceived bubble exceeds attention cost |
| normal conditions | holds | attention cost exceeds expected gain |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `fundamental` | environment | float | yes | perceived fair value |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is clamped to available cash/price or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | deviation calculation |
| `fundamental` | Continuous | 1 tick | reference value |
| `cash` | State | persistent | buy constraint |
| `position` | State | persistent | sell constraint |

Does NOT use: order flow, peer signals, momentum, sentiment, leverage.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `cash`, and `position`.
2. Compute deviation: `dev = (price - fundamental) / fundamental`.
3. If `dev < -inaction_threshold` and `cash > 0`, buy `min(cash / price, rebalance_size)`.
4. If `dev > inaction_threshold` and `position > 0`, sell `min(position, rebalance_size)`.
5. Otherwise, hold.
6. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | fixed `rebalance_size`, capped by resources |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot go negative |
| Resource cap | buy quantity cannot exceed cash / price |
| Exit rule | sell when overvaluation exceeds threshold |

#### Mathematical Model

`q_buy = min(cash / price, rebalance_size)` if `(price - fundamental) / fundamental < -theta`; `q_sell = min(position, rebalance_size)` if `(price - fundamental) / fundamental > theta`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta` | inaction threshold | 0.15 | Sims (2003), Gabaix (2014) |
| `rebalance_size` | fixed order size when triggered | 200 | calibration |

#### Behavioral Properties

- Time horizon: long, because the agent almost never trades.
- Risk tolerance: very low, because action requires extreme mispricing.
- Information asymmetry: high (uninformed by choice), attends only to gross deviations.
- Psychological profile: detached, low-frequency rebalancer; resistant to market noise.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `inaction_threshold` | float | 0.15 | [0.10, 0.30] | high | minimum abs deviation to trigger trade | Higher -> less frequent action | Sims (2003) |
| `rebalance_size` | float | 200 | [50, 500] | medium | fixed order size when triggered | Higher -> larger stabilising volume | calibration |
| `fundamental` | float | scenario | > 0 | low | perceived fair value reference | Anchors deviation calc | scenario parameter |

## Worked Numerical Examples

### Case 1 - Extreme Undervaluation Buy

System state: price 80.0, fundamental 100.0, cash 50000, position 100.
Calculation: `dev = (80 - 100)/100 = -0.20`. `|-0.20| > 0.15`. `q = min(50000/80, 200) = min(625, 200) = 200`.
Decision: buy 200.
State update: cash decreases by 16000, position increases by 200.

### Case 2 - Extreme Overvaluation Sell

System state: price 120.0, fundamental 100.0, cash 10000, position 300.
Calculation: `dev = (120 - 100)/100 = 0.20`. `0.20 > 0.15`. `q = min(300, 200) = 200`.
Decision: sell 200.
State update: position decreases by 200, cash increases by 24000.

### Case 3 - Within Inaction Band

System state: price 105.0, fundamental 100.0, cash 50000, position 300.
Calculation: `dev = (105 - 100)/100 = 0.05`. `0.05 < 0.15`.
Decision: hold.
State update: unchanged.

### Edge Case - Triggered but No Position

System state: price 120.0, fundamental 100.0, cash 10000, position 0.
Calculation: `dev = 0.20 > 0.15`, sell triggered but position is 0. `q = min(0, 200) = 0`.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `abs(dev) > inaction_threshold` and resources available, agent must trade.
- Given `abs(dev) <= inaction_threshold`, agent must hold regardless of resources.
- Given missing `fundamental`, agent must hold.
- Agent must never trade more than `rebalance_size` per tick.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-inaction | `inaction_threshold = 0` | inaction band stabilises price | increase | trade frequency |
| wide-band | `inaction_threshold = 0.30` | wider band -> less stabilisation | increase | price volatility |
| large-rebalance | `rebalance_size = 500` | larger orders dampen extremes more | decrease | tail deviation frequency |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Sims, C. A. (2003). Implications of rational inattention. https://doi.org/10.1016/S0304-3932(03)00029-1 | Information capacity constraints |
| 2 | Gabaix, X. (2014). A sparsity-based model of bounded rationality. https://doi.org/10.1093/qje/qju024 | Sparse attention, inaction bands |
| 3 | Constantinides, G. M. (1986). Capital market equilibrium with transaction costs. https://doi.org/10.1086/261302 | Transaction cost alternative |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-passive-bystander.png) |
| Status | draft |
