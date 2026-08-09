# Ideologue

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Ideologically rigid belief-driven trader |
| Theory Family         | Behavioral Finance / Confirmation Bias |
| Behavioral Tendency   | **Destabilising** - trades based on rigid prior beliefs regardless of market evidence, distorting prices |
| Time Horizon          | long |
| Risk Tolerance        | high |
| Information Asymmetry | none (believes it has informational advantage but does not) |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor with rigid ideological beliefs about asset value or market direction that override incoming market signals. The real-world counterpart is the ideologically committed trader documented in studies of confirmation bias (Nickerson 1998) and belief perseverance (Lord, Ross, & Lepper 1979) who selectively processes information to reinforce pre-existing views. The agent emits buy, sell, or hold orders with direction fixed by its ideological belief and quantity modulated by conviction strength.

The decision goal is to implement a fixed directional view regardless of price action. If the agent believes the asset is fundamentally worth more than the current price (bullish ideologue), it buys persistently; if bearish, it sells persistently. It does not update beliefs based on disconfirming evidence. Non-goals: it must not reverse its directional bias based on market signals, and it must not engage in hedging or risk management that contradicts its belief.

The agent is designed for scenarios exploring echo chambers, polarisation, belief persistence, and how rigid agents can distort price discovery when they interact with adaptive agents.

## Theoretical Foundation

**Confirmation bias**:
- Theory / Study: Confirmation bias: A ubiquitous phenomenon in many guises.
- Citation: Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology*, 2(2), 175-220. https://doi.org/10.1037/1089-2680.2.2.175
- Core Insight: People seek, interpret, and remember information in ways that confirm pre-existing beliefs while ignoring or downweighting disconfirming evidence. In financial contexts this produces persistent mispricing.
- Mathematical Formulation: `Q = conviction_size * belief_strength` in the direction of the fixed belief, regardless of price signals.
- Empirical Evidence: Nickerson reviews decades of experimental evidence showing the ubiquity and persistence of confirmation bias across domains.
- Relevance to This Agent: The agent never updates its directional view; it operationalises the "belief perseverance" failure mode.
- Calibration Source: `belief_strength` 0.5-1.0, `conviction_size` 200-600, `belief_direction` {bull, bear}.
- Falsification Conditions: If the agent reverses direction in response to market signals, the design is falsified.
- Alternative Theories: Bayesian updating (rational); adaptive learning; prospect theory framing.

**Belief perseverance under disconfirmation**:
- Theory / Study: Biased assimilation and attitude polarization.
- Citation: Lord, C. G., Ross, L., & Lepper, M. R. (1979). Biased assimilation and attitude polarization: The effects of prior theories on subsequently considered evidence. *Journal of Personality and Social Psychology*, 37(11), 2098-2109. https://doi.org/10.1037/0022-3514.37.11.2098
- Core Insight: When presented with mixed evidence, subjects with strong prior beliefs interpret ambiguous evidence as supporting their position, leading to attitude polarisation rather than convergence.
- Mathematical Formulation: Effective belief update: `new_belief = old_belief + bias_weight * confirming_evidence - (1 - bias_weight) * disconfirming_evidence`, where bias_weight approaches 1.0.
- Empirical Evidence: Lord et al. show that subjects exposed to identical evidence became more extreme in their original positions.
- Relevance to This Agent: Justifies the agent's zero-update behaviour: even disconfirming price action is reinterpreted as confirmation.
- Calibration Source: Polarisation multiplier of 1.0 (no updating) based on extreme belief perseverance.
- Falsification Conditions: If the agent moderates its belief over time without exogenous instruction, design is falsified.
- Alternative Theories: Rational learning from prices; social learning and imitation.

## Design Purpose and Activation Triggers

Purpose: Trade persistently in one direction based on fixed ideological beliefs, representing confirmation bias and belief perseverance in markets.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- own `cash` and `position` available

Missing-Signal Policy: hold when price is unavailable (but belief persists).

Activation Triggers:
- `belief_direction = bull`: buy sized by `conviction_size * belief_strength`, capped by cash.
- `belief_direction = bear` and `position > 0`: sell sized by `min(position, conviction_size * belief_strength)`.
- `<Default>`: hold (when resources exhausted in belief direction).

Deactivation Conditions:
- cash exhausted (bullish ideologue cannot buy more).
- position exhausted (bearish ideologue has sold all).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| any price, bullish belief | buys persistently | rigid positive conviction |
| any price, bearish belief | sells persistently | rigid negative conviction |
| resources exhausted | holds involuntarily | constraint binding, not belief change |

Environmental Dependencies: none beyond price and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash or position. Reasoning always references the ideological belief.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference only |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint |

Does NOT use: market consensus, fundamental analysis, momentum signals, peer actions (ignores all disconfirming information).

#### Core Behavioral Mechanism

1. Read `price`, `cash`, and `position`.
2. If `belief_direction = bull`, compute buy quantity as `min(cash / price, conviction_size * belief_strength)`.
3. If `belief_direction = bear`, compute sell quantity as `min(position, conviction_size * belief_strength)`.
4. If resources exhausted in belief direction, hold.
5. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `conviction_size * belief_strength`, capped by resources |
| Action lifetime | one decision call |
| Revision policy | same direction every tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy cannot exceed cash / price |
| Exit rule | never voluntarily exits; holds until resources exhausted |

#### Mathematical Model

`q_buy = min(cash/price, conviction_size * B)` if `direction = bull`; `q_sell = min(position, conviction_size * B)` if `direction = bear`; otherwise `q = 0` (resources exhausted).

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `B` | belief strength (intensity) | 0.8 | Nickerson (1998), calibration |
| `conviction_size` | base order size | 400.0 | scenario normalization |
| `direction` | ideological belief direction | bull | scenario parameter |
| `belief_decay` | rate of belief erosion (0 = never decays) | 0.0 | Lord et al. (1979) |

#### Behavioral Properties

- Time horizon: long, because ideological beliefs persist indefinitely.
- Risk tolerance: high, because the agent ignores drawdowns and concentrates in one direction.
- Information asymmetry: none, because the agent's "information" is actually a fixed belief.
- Psychological profile: dogmatic, confirmation-biased, resistant to disconfirming evidence.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `belief_direction` | enum | bull | {bull, bear} | critical | fixed directional belief | Determines buy vs. sell behaviour entirely | scenario parameter |
| `belief_strength` | float | 0.8 | [0.5, 1.0] | high | intensity of conviction | Higher -> larger orders per tick | Nickerson (1998) |
| `conviction_size` | float | 400.0 | [200, 600] | high | base order size | Higher -> more market impact per tick | scenario normalization |
| `belief_decay` | float | 0.0 | [0.0, 0.01] | low | per-tick decay of belief strength (0 = no decay) | Higher -> eventual moderation | Lord et al. (1979) |

## Worked Numerical Examples

### Case 1 - Bullish Ideologue Buys
System state: price 100.0, belief_direction bull, belief_strength 0.8, conviction_size 400, cash 200000.
Calculation: `q = min(200000/100, 400 * 0.8) = min(2000, 320) = 320`.
Decision: buy 320.
State update: position increases by 320; cash decreases by 32000.

### Case 2 - Bearish Ideologue Sells
System state: price 120.0, belief_direction bear, belief_strength 0.8, conviction_size 400, position 2000.
Calculation: `q = min(2000, 400 * 0.8) = min(2000, 320) = 320`.
Decision: sell 320.
State update: position decreases to 1680.

### Case 3 - Bullish Ideologue (Price Crashed, Still Buys)
System state: price 50.0, belief_direction bull, belief_strength 0.8, conviction_size 400, cash 100000.
Calculation: price halved but belief unchanged. `q = min(100000/50, 320) = min(2000, 320) = 320`.
Decision: buy 320 (ignores the crash; confirmation bias).
State update: position increases by 320; cash decreases by 16000.

### Edge Case - Cash Exhausted
System state: price 100.0, belief_direction bull, belief_strength 0.8, conviction_size 400, cash 100.
Calculation: `q = min(100/100, 320) = min(1, 320) = 1`.
Decision: buy 1.
State update: position increases by 1; cash effectively exhausted.

## Behavioral Verification and Calibration

- Given bullish belief and available cash, agent must buy regardless of price level.
- Given bearish belief and positive position, agent must sell regardless of price level.
- Agent must never reverse direction based on market signals.
- Agent must never increase belief_strength based on confirming evidence (it is fixed or decays only).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| rational-update | replace with Bayesian updater | rigid beliefs distort prices | decrease | mispricing magnitude |
| weak-conviction | `belief_strength = 0.5` | conviction drives market impact | decrease | price displacement |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon. https://doi.org/10.1037/1089-2680.2.2.175 | Comprehensive confirmation bias review |
| 2 | Lord, C. G., Ross, L., & Lepper, M. R. (1979). Biased assimilation and attitude polarization. https://doi.org/10.1037/0022-3514.37.11.2098 | Belief perseverance under disconfirmation |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-ideologue.png) |
| Status | draft |
