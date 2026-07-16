# New Economy Evangelist

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Paradigm-shift technology investor |
| Theory Family         | Technological Revolutions / Narrative Economics |
| Behavioral Tendency   | **Amplifying** - accumulates "new economy" stocks regardless of valuation, reinforcing bubbles |
| Time Horizon          | long |
| Risk Tolerance        | high |
| Information Asymmetry | high (overconfident) |
| Determinism           | stochastic |

## Definition and Goals

This agent models an investor who believes a paradigm shift (internet, AI, blockchain) renders traditional valuation metrics obsolete. The real-world counterpart is the late-1990s technology investor documented by Perez (2002) and the narrative-driven speculator described by Shiller (2019). The agent emits buy or hold orders whenever a narrative-strength signal is elevated, irrespective of price-to-fundamental ratios.

The decision goal is to accumulate exposure to "new economy" assets whenever the prevailing narrative is strong, without regard to valuation discipline. It is not a value investor and it does not hedge. Non-goals: it must not sell based on valuation signals, and it must not reduce exposure when narratives weaken unless a capitulation threshold is breached.

## Theoretical Foundation

**Technological revolutions and narrative economics**:
- Theory / Study: Technological revolutions and financial capital; Narrative Economics.
- Citation: Perez, C. (2002). *Technological Revolutions and Financial Capital*. Edward Elgar. https://doi.org/10.4337/9781781005323
- Citation: Shiller, R. J. (2019). *Narrative Economics*. Princeton University Press. https://doi.org/10.2307/j.ctvdf0jm5
- Core Insight: During technological revolutions, investors overweight narrative momentum and believe "this time is different," leading to systematic overvaluation. Narratives spread virally and sustain bubbles beyond fundamental support.
- Mathematical Formulation: `Q = narrative_weight * cash / price` when `narrative_strength > belief_threshold`.
- Empirical Evidence: Perez documents recurring installation-deployment cycles; Shiller shows narrative contagion drives asset prices beyond fundamentals.
- Relevance to This Agent: The agent operationalizes narrative-driven buying with valuation indifference.
- Calibration Source: `belief_threshold` 0.3-0.7, `narrative_weight` 0.10-0.40.
- Falsification Conditions: If the agent considers P/E ratios or sells on valuation grounds, the design is falsified.
- Alternative Theories: Rational bubble models (Blanchard & Watson 1982); momentum trading without narrative mechanism.

## Design Purpose and Activation Triggers

Purpose: Inject narrative-driven demand that inflates asset prices during technological hype cycles, contributing to bubble formation and delayed correction.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `narrative_strength` available (0-1 index of paradigm-shift narrative intensity)
- own `cash` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `narrative_strength > belief_threshold` AND `cash > 0`: buy with `narrative_weight * cash / price`.
- `narrative_strength < capitulation_threshold` AND `position > 0`: sell `panic_fraction * position` (capitulation).
- `<Default>`: hold.

Deactivation Conditions:
- cash fully deployed.
- narrative collapses below capitulation threshold and position fully liquidated.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| strong narrative | aggressive buying | paradigm-shift belief |
| moderate narrative | cautious holding | waiting for confirmation |
| narrative collapse | panic selling | capitulation, belief reversal |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `narrative_strength` | environment | float [0,1] | yes | paradigm narrative intensity |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity for capitulation |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is clamped to available cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `narrative_strength` | Continuous | 1 tick | belief activation |
| `cash` | State | persistent | budget constraint |
| `position` | State | persistent | capitulation capacity |

Does NOT use: P/E ratios, fundamental valuation, dividend yields, analyst reports.

#### Core Behavioral Mechanism

1. Read `price`, `narrative_strength`, `cash`, and `position`.
2. If `narrative_strength > belief_threshold` and `cash > 0`, compute buy quantity as `narrative_weight * cash / price`, apply noise.
3. If `narrative_strength < capitulation_threshold` and `position > 0`, compute sell quantity as `panic_fraction * position`.
4. Otherwise, hold.
5. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `narrative_weight * cash / price` for buys; `panic_fraction * position` for sells |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot go negative |
| Resource cap | buy quantity cannot exceed cash / price |
| Exit rule | sell only on narrative collapse (capitulation) |

#### Mathematical Model

`q_buy = min(cash / price, narrative_weight * cash / price * (1 + epsilon))` if `narrative_strength > belief_threshold`; `q_sell = min(position, panic_fraction * position)` if `narrative_strength < capitulation_threshold`; otherwise `q = 0`. Where `epsilon ~ N(0, noise_sigma)`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `belief_threshold` | narrative strength needed to buy | 0.50 | Perez (2002) |
| `capitulation_threshold` | narrative collapse trigger | 0.15 | Shiller (2019) |
| `narrative_weight` | fraction of cash to deploy per tick | 0.15 | calibration |
| `panic_fraction` | fraction of position to sell on collapse | 0.50 | calibration |
| `noise_sigma` | stochastic noise | 0.05 | calibration |

#### Behavioral Properties

- Time horizon: long, because paradigm believers hold through volatility.
- Risk tolerance: high, because valuation is ignored.
- Information asymmetry: high (overconfident), relying on narrative not fundamentals.
- Psychological profile: true believer; conviction-driven, prone to euphoria and eventual capitulation.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `belief_threshold` | float | 0.50 | [0.30, 0.70] | high | narrative strength to trigger buying | Higher -> fewer entries | Perez (2002) |
| `capitulation_threshold` | float | 0.15 | [0.05, 0.25] | high | narrative collapse sell trigger | Lower -> later capitulation | Shiller (2019) |
| `narrative_weight` | float | 0.15 | [0.10, 0.40] | high | fraction of cash deployed per tick | Higher -> faster accumulation | calibration |
| `panic_fraction` | float | 0.50 | [0.20, 1.00] | medium | fraction of position sold on collapse | Higher -> sharper crash contribution | calibration |
| `noise_sigma` | float | 0.05 | [0.0, 0.15] | low | stochastic sizing noise | Higher -> more heterogeneity | calibration |

## Worked Numerical Examples

### Case 1 - Narrative Buy

System state: price 200.0, narrative_strength 0.70, cash 50000, position 100.
Calculation: `q = 0.15 * 50000 / 200 = 37.5 units`.
Decision: buy 37.
State update: cash decreases by 7400, position increases by 37.

### Case 2 - Narrative Hold

System state: price 200.0, narrative_strength 0.40, cash 50000, position 100.
Calculation: `0.40 < 0.50` belief threshold not met; `0.40 > 0.15` not capitulating.
Decision: hold.
State update: unchanged.

### Case 3 - Capitulation Sell

System state: price 80.0, narrative_strength 0.10, cash 5000, position 200.
Calculation: `q = 0.50 * 200 = 100 units`.
Decision: sell 100.
State update: position decreases by 100, cash increases by 8000.

### Edge Case - No Cash, Strong Narrative

System state: price 200.0, narrative_strength 0.80, cash 0, position 500.
Calculation: cash is zero, cannot buy; narrative above belief threshold so no sell.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `narrative_strength > belief_threshold` and `cash > 0`, agent must buy.
- Given `narrative_strength < capitulation_threshold` and `position > 0`, agent must sell.
- Agent must never sell on valuation grounds (P/E, dividend yield).
- Given missing `narrative_strength`, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-capitulation | `capitulation_threshold = 0` | capitulation absent -> bubble persists longer | increase | bubble duration |
| low-belief | `belief_threshold = 0.30` | lower threshold -> earlier bubble entry | increase | pre-peak volume |
| no-noise | `noise_sigma = 0` | heterogeneity dampens coordination | decrease | order size variance |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Perez, C. (2002). Technological Revolutions and Financial Capital. https://doi.org/10.4337/9781781005323 | Installation-deployment cycle |
| 2 | Shiller, R. J. (2019). Narrative Economics. https://doi.org/10.2307/j.ctvdf0jm5 | Viral narratives drive asset prices |
| 3 | Blanchard, O. J., & Watson, M. W. (1982). Bubbles, rational expectations, and financial markets. https://doi.org/10.3386/w0945 | Rational bubble alternative |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-new-economy-evangelist.png) |
| Status | draft |
