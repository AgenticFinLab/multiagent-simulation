# Critical thinker

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Contrarian critical thinker |
| Theory Family         | Contrarian Investing / Information Aggregation |
| Behavioral Tendency   | **Stabilising** - trades against crowd consensus when reasoning diverges from market price |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models an independent-minded investor who evaluates market consensus critically and trades against the crowd when fundamental reasoning diverges from the prevailing price. The real-world counterpart is the contrarian value manager documented in the "wisdom of crowds" breakdown literature (Surowiecki 2004) and the limits of collective intelligence under correlated information (Hong & Stein 2003). The agent emits buy, sell, or hold orders with quantity sized by the magnitude of divergence between its own valuation signal and the consensus price.

The decision goal is to profit from mean reversion when crowd consensus becomes unanchored from fundamentals. The agent assumes that extreme crowd agreement often reflects herding rather than genuine information aggregation, and positions against such consensus. It operates as a stabilising force by providing liquidity to one-sided markets. Non-goals: it must not trade purely on momentum in the direction of the crowd, and it must not ignore its own position limits when conviction is high.

The agent activates only when consensus divergence exceeds a threshold; otherwise it holds. It is designed for scenarios exploring echo chambers, herding cascades, and market efficiency breakdowns where independent thinking is crowded out.

## Theoretical Foundation

**Contrarian wisdom and crowd breakdown**:
- Theory / Study: The Wisdom of Crowds — conditions for crowd accuracy and failure modes.
- Citation: Surowiecki, J. (2004). *The Wisdom of Crowds*. Doubleday. https://doi.org/10.1002/bdm.479
- Core Insight: Crowds produce accurate estimates only when opinions are diverse, decentralised, and independently formed. When correlations rise (herding), crowd accuracy collapses, creating contrarian opportunity.
- Mathematical Formulation: `Q = conviction_size * divergence_signal / divergence_threshold` when `abs(divergence_signal) > divergence_threshold`.
- Empirical Evidence: Surowiecki documents multiple cases where diverse independent judgement outperforms experts, and where loss of diversity destroys accuracy.
- Relevance to This Agent: The agent exploits moments when crowd diversity collapses and consensus overshoots fundamental value.
- Calibration Source: `divergence_threshold` 0.03-0.10, `conviction_size` 200-800, `max_position` 5000-20000.
- Falsification Conditions: If the agent trades with the crowd rather than against it when divergence exceeds threshold, the design is falsified.
- Alternative Theories: Momentum investing (Jegadeesh & Titman 1993); rational herding (Banerjee 1992).

**Disagreement and asset pricing**:
- Theory / Study: Disagreement and the stock market.
- Citation: Hong, H. & Stein, J. C. (2007). Disagreement and the stock market. *Journal of Economic Perspectives*, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
- Core Insight: Divergence of opinion among investors predicts returns and volatility; short-sale constraints cause overpricing when optimists dominate.
- Mathematical Formulation: When consensus is bullish and short constraints bind, the asset is overpriced by the extent of disagreement.
- Empirical Evidence: Hong & Stein show that high disagreement portfolios underperform, consistent with overpricing.
- Relevance to This Agent: The agent sells into bullish consensus and buys into bearish consensus, capturing reversion.
- Calibration Source: Disagreement proxies: analyst forecast dispersion, breadth indicators.
- Falsification Conditions: If the agent does not reduce position when divergence narrows, design is falsified.
- Alternative Theories: Efficient markets hypothesis (Fama 1970); noise trader risk (De Long et al. 1990).

## Design Purpose and Activation Triggers

Purpose: Trade against market consensus when crowd reasoning appears unanchored from fundamentals, providing a stabilising counterweight to herding.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `consensus_signal` available (crowd average expectation or order-flow imbalance)
- `fundamental_value` available (private valuation estimate)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `divergence > divergence_threshold` (consensus above fundamental): sell sized by `conviction_size * (divergence / divergence_threshold)`, capped by position.
- `divergence < -divergence_threshold` (consensus below fundamental): buy sized by `conviction_size * abs(divergence / divergence_threshold)`, capped by cash.
- `<Default>`: hold.

Deactivation Conditions:
- position limit reached during buying.
- inventory exhausted during selling.
- divergence returns within threshold band.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| high consensus divergence above fundamental | sells aggressively against crowd | contrarian mean-reversion |
| high consensus divergence below fundamental | buys aggressively against crowd | contrarian value capture |
| low divergence | holds, waits for signal | discipline preservation |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `consensus_signal` | environment | float | yes | crowd expectation or order-flow imbalance |
| `fundamental_value` | private model | float | yes | agent's own valuation estimate |
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
| `consensus_signal` | Continuous | 1 tick | crowd sentiment measure |
| `fundamental_value` | Continuous | 1 tick | private valuation anchor |
| `cash` | State | persistent | position sizing |
| `position` | State | persistent | sell constraint |

Does NOT use: insider information, central bank policy signals, peer agent identities.

#### Core Behavioral Mechanism

1. Read `price`, `consensus_signal`, `fundamental_value`, `cash`, and `position`.
2. Compute `divergence = consensus_signal - fundamental_value`.
3. If `divergence > divergence_threshold`, compute sell quantity as `min(position, conviction_size * divergence / divergence_threshold)`.
4. If `divergence < -divergence_threshold`, compute buy quantity as `min(cash / price, conviction_size * abs(divergence) / divergence_threshold)`.
5. If neither threshold is crossed, hold.
6. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `conviction_size * abs(divergence) / divergence_threshold`, capped by resource constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy quantity cannot exceed cash / price |
| Exit rule | reduce contrarian position when divergence narrows |

#### Mathematical Model

`q_sell = min(position, conviction_size * divergence / theta)` if `divergence > theta`; `q_buy = min(cash / price, conviction_size * abs(divergence) / theta)` if `divergence < -theta`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta` | divergence threshold | 0.05 | Surowiecki (2004), calibrated |
| `conviction_size` | base contrarian order size | 500.0 | scenario normalization |
| `max_position` | position limit | 10000.0 | risk management |
| `divergence_scale` | scaling factor for divergence sizing | 1.0 | scenario normalization |

#### Behavioral Properties

- Time horizon: medium, because contrarian trades require time for mean reversion.
- Risk tolerance: medium, because the agent sizes positions proportionally rather than maximally.
- Information asymmetry: partial, because the agent uses a private fundamental estimate.
- Psychological profile: independent analytical temperament resistant to social pressure.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `divergence_threshold` | float | 0.05 | [0.03, 0.10] | high | minimum divergence to trigger contrarian trade | Higher -> fewer but larger trades | Surowiecki (2004) |
| `conviction_size` | float | 500.0 | [200, 800] | high | base order size for contrarian positions | Higher -> larger market impact | scenario normalization |
| `max_position` | float | 10000.0 | [5000, 20000] | medium | maximum position the agent will accumulate | Higher -> more capital at risk | risk management |
| `divergence_scale` | float | 1.0 | [0.5, 2.0] | medium | multiplier for divergence-proportional sizing | Higher -> more aggressive scaling | scenario normalization |

## Worked Numerical Examples

### Case 1 - Contrarian Sell (Bullish Crowd)
System state: price 100.0, consensus_signal 108.0, fundamental_value 100.0, position 3000.
Calculation: divergence = 108 - 100 = 8.0; 8.0 > 5.0 (threshold met at 0.05 * 100). `q = min(3000, 500 * 8.0 / 5.0) = min(3000, 800) = 800`.
Decision: sell 800.
State update: position decreases to 2200.

### Case 2 - Contrarian Buy (Bearish Crowd)
System state: price 100.0, consensus_signal 92.0, fundamental_value 100.0, cash 200000.
Calculation: divergence = 92 - 100 = -8.0; abs(-8.0) > 5.0. `q = min(200000 / 100, 500 * 8.0 / 5.0) = min(2000, 800) = 800`.
Decision: buy 800.
State update: position increases by 800; cash decreases by 80000.

### Case 3 - Hold (Low Divergence)
System state: price 100.0, consensus_signal 102.0, fundamental_value 100.0.
Calculation: divergence = 2.0; abs(2.0) < 5.0 threshold.
Decision: hold.
State update: unchanged.

### Edge Case - Position Limit Reached
System state: price 100.0, consensus_signal 90.0, fundamental_value 100.0, cash 20000, position 9800, max_position 10000.
Calculation: divergence = -10.0, buy signal. `q_raw = 500 * 10 / 5 = 1000`. Available capacity = min(20000/100, 10000-9800) = min(200, 200) = 200.
Decision: buy 200.
State update: position reaches 10000 cap.

## Behavioral Verification and Calibration

- Given `divergence > divergence_threshold`, agent must sell if position is positive.
- Given `divergence < -divergence_threshold`, agent must buy if cash permits and position cap allows.
- Given missing `consensus_signal`, agent must hold.
- Agent must never trade in the direction of consensus (i.e., buy when consensus is above fundamental, or sell when below).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-contrarian | `divergence_threshold = infinity` | contrarian force stabilises prices | increase | price volatility |
| high-conviction | `conviction_size = 800` | larger contrarian trades accelerate mean reversion | decrease | time to reversion |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Surowiecki, J. (2004). The Wisdom of Crowds. https://doi.org/10.1002/bdm.479 | Conditions for crowd accuracy and breakdown |
| 2 | Hong, H. & Stein, J. C. (2007). Disagreement and the stock market. https://doi.org/10.1257/jep.21.2.109 | Disagreement predicts returns |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-critical-thinker.png) |
| Status | draft |
