# Selective scanner

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Confirmation-bias-driven selective information processor |
| Theory Family         | Behavioral Finance / Cognitive Bias |
| Behavioral Tendency   | **Diverging** - reinforces existing beliefs by selectively attending to confirming signals, amplifying trends |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial (self-imposed) |
| Determinism           | deterministic |

## Definition and Goals

This agent models a retail investor or analyst who selectively attends to information that confirms a pre-existing belief about market direction, while discounting or ignoring disconfirming evidence. The real-world counterpart is the confirmation-biased investor documented by Nickerson (1998) and the limited-attention trader formalised by Peng and Xiong (2006). The agent maintains a directional prior and filters incoming signals through a confirmation lens, trading more aggressively when confirming signals arrive.

The decision goal is to act on perceived confirming information to build or maintain a directional position. It is not an unbiased information aggregator. Non-goals: it must not weigh confirming and disconfirming signals equally, and it must not update its prior symmetrically in response to contradictory evidence.

## Theoretical Foundation

**Confirmation bias in reasoning**:
- Theory / Study: Confirmation bias: A ubiquitous phenomenon in many guises.
- Citation: Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology*, 2(2), 175-220. https://doi.org/10.1037/1089-2680.2.2.175
- Core Insight: People tend to search for, interpret, and recall information in a way that confirms pre-existing beliefs. In financial markets, this leads investors to over-weight supporting signals and under-weight contradictions.
- Mathematical Formulation: `effective_signal = w_confirm * confirming_signal + w_disconfirm * disconfirming_signal` where `w_confirm >> w_disconfirm`.
- Empirical Evidence: Nickerson documents confirmation bias across dozens of experimental paradigms including hypothesis testing, medical diagnosis, and investment selection.
- Relevance to This Agent: The agent applies asymmetric weighting: `confirm_weight` for aligned signals, `disconfirm_weight` for opposing signals.
- Calibration Source: `confirm_weight` 0.7-1.0, `disconfirm_weight` 0.0-0.3.
- Falsification Conditions: If the agent weights confirming and disconfirming signals equally, the design is falsified.
- Alternative Theories: Rational Bayesian updating; overconfidence models.

**Limited attention and information processing**:
- Theory / Study: Investor attention, overconfidence, and category learning.
- Citation: Peng, L., & Xiong, W. (2006). Investor attention, overconfidence and category learning. *Journal of Financial Economics*, 80(3), 563-602. https://doi.org/10.1016/j.jfineco.2005.05.003
- Core Insight: Investors with limited attention capacity allocate disproportionate processing to market-level or category-level signals that confirm existing positions, leading to correlated trading and momentum.
- Mathematical Formulation: Attention allocation `a_i = prior_belief_strength * signal_alignment_i / sum(alignment)`.
- Empirical Evidence: Peng & Xiong show limited-attention investors generate excess comovement and momentum in asset prices.
- Relevance to This Agent: The agent attends primarily to signals aligned with its prior, generating trend-following behaviour as a by-product of cognitive bias.
- Calibration Source: `attention_capacity` bounds the number of signals processed per tick.
- Falsification Conditions: If the agent processes all available signals with equal weight, the design is falsified.
- Alternative Theories: Full-information rational expectations; Grossman-Stiglitz (1980).

## Design Purpose and Activation Triggers

Purpose: Maintain and reinforce directional positions by selectively weighting confirming market signals more heavily than disconfirming ones.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `signal` available (aggregate market signal, positive = bullish, negative = bearish)
- own `cash`, `position`, and `prior_direction` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `signal * prior_direction > 0` (confirming): trade in prior direction, sized by `confirm_weight * base_size`.
- `signal * prior_direction < 0` AND `|signal| > stubbornness_threshold` (strong disconfirm): reluctantly reduce position by `disconfirm_weight * base_size`.
- `signal * prior_direction < 0` AND `|signal| <= stubbornness_threshold`: ignore signal, hold.
- `<Default>`: hold.

Deactivation Conditions:
- cash exhausted when prior is bullish.
- position exhausted when prior is bearish.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| confirming signal | increases position aggressively | confirmation bias amplification |
| weak disconfirming signal | ignores and holds | selective attention filters noise |
| strong disconfirming signal | small reluctant reduction | bounded rationality override |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `signal` | environment | float | yes | aggregate market signal (-1 to +1 scale) |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity / current exposure |
| `prior_direction` | own state | int | yes | +1 (bullish) or -1 (bearish) |

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
| `signal` | Continuous | 1 tick | directional information |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint |
| `prior_direction` | State | persistent | confirmation filter |

Does NOT use: full order book, fundamental valuation models, peer portfolio data.

#### Core Behavioral Mechanism

1. Read `price`, `signal`, `cash`, `position`, and `prior_direction`.
2. Compute `alignment = signal * prior_direction`.
3. If `alignment > 0` (confirming): compute `q = confirm_weight * base_size * |signal|`.
   - If `prior_direction = +1`: buy `min(q, cash / price)`.
   - If `prior_direction = -1`: sell `min(q, position)`.
4. If `alignment < 0` and `|signal| > stubbornness_threshold` (strong disconfirm):
   - Reluctantly reverse: `q = disconfirm_weight * base_size * |signal|`.
   - If `prior_direction = +1`: sell `min(q, position)`.
   - If `prior_direction = -1`: buy `min(q, cash / price)`.
5. Otherwise hold.
6. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `weight * base_size * |signal|`, capped by resource constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | only reduces when disconfirming signal exceeds stubbornness threshold |

#### Mathematical Model

`q_confirm = min(resource_cap, confirm_weight * base_size * |signal|)` if `signal * prior_direction > 0`; `q_disconfirm = min(resource_cap, disconfirm_weight * base_size * |signal|)` if `signal * prior_direction < 0` and `|signal| > stubbornness_threshold`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `confirm_weight` | weight applied to confirming signals | 0.85 | Nickerson (1998) |
| `disconfirm_weight` | weight applied to disconfirming signals | 0.15 | Nickerson (1998) |
| `base_size` | base order size | 200.0 | scenario calibration |
| `stubbornness_threshold` | signal strength needed to override prior | 0.60 | Peng & Xiong (2006) |
| `prior_direction` | initial directional belief | +1 | scenario-dependent |

#### Behavioral Properties

- Time horizon: short, because confirmation bias drives reactive trading.
- Risk tolerance: medium, because the agent trades actively but not with extreme leverage.
- Information asymmetry: partial (self-imposed through selective attention).
- Psychological profile: cognitively biased investor who reinforces beliefs through selective information processing.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `confirm_weight` | float | 0.85 | [0.70, 1.0] | high | multiplier for confirming signals | Higher -> stronger trend reinforcement | Nickerson (1998) |
| `disconfirm_weight` | float | 0.15 | [0.0, 0.30] | high | multiplier for disconfirming signals | Lower -> more stubbornness | Nickerson (1998) |
| `base_size` | float | 200.0 | [50, 500] | medium | base order quantity before weighting | Higher -> larger orders | scenario calibration |
| `stubbornness_threshold` | float | 0.60 | [0.40, 0.80] | medium | minimum disconfirming signal to trigger action | Higher -> ignores more contradictions | Peng & Xiong (2006) |
| `prior_direction` | int | +1 | {-1, +1} | high | initial directional belief | Determines buy vs sell bias | scenario-dependent |

## Worked Numerical Examples

### Case 1 - Confirming Signal (Bullish Prior, Positive Signal)

System state: price 100.0, signal +0.70, cash 50000, position 300, prior_direction +1.
Calculation: `alignment = 0.70 * 1 = 0.70 > 0` -> confirming.
`q = 0.85 * 200 * 0.70 = 119`. `min(119, 50000/100) = 119`.
Decision: buy 119.
State update: position increases to 419; cash decreases by 11900.

### Case 2 - Weak Disconfirming Signal (Ignored)

System state: price 100.0, signal -0.40, cash 50000, position 300, prior_direction +1.
Calculation: `alignment = -0.40 * 1 = -0.40 < 0`. `|signal| = 0.40 < stubbornness_threshold (0.60)`.
Decision: hold.
State update: unchanged.

### Case 3 - Strong Disconfirming Signal (Reluctant Reduction)

System state: price 100.0, signal -0.80, cash 50000, position 300, prior_direction +1.
Calculation: `alignment = -0.80 < 0`. `|signal| = 0.80 > 0.60` -> disconfirm override.
`q = 0.15 * 200 * 0.80 = 24`. `min(24, 300) = 24`.
Decision: sell 24.
State update: position decreases to 276.

### Edge Case - No Position to Sell on Disconfirm

System state: price 100.0, signal -0.90, cash 50000, position 0, prior_direction +1.
Calculation: strong disconfirm but `position = 0` -> `q = min(0, 27) = 0`.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given confirming signal, agent must trade in prior direction with high weight.
- Given weak disconfirming signal (below stubbornness threshold), agent must hold.
- Given strong disconfirming signal, agent must reluctantly reduce position with low weight.
- Ratio of confirm to disconfirm response must be at least 3:1.
- Agent must never weight disconfirming information more than confirming.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| unbiased-scanner | `confirm_weight = 0.50, disconfirm_weight = 0.50` | bias removal improves pricing accuracy | decrease | price deviation from fundamental |
| extreme-bias | `confirm_weight = 1.0, disconfirm_weight = 0.0` | maximum bias creates stronger momentum | increase | price momentum persistence |
| low-stubbornness | `stubbornness_threshold = 0.20` | lower threshold improves responsiveness | decrease | trend overshoot |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology*, 2(2), 175-220. https://doi.org/10.1037/1089-2680.2.2.175 | Core confirmation bias theory |
| 2 | Peng, L., & Xiong, W. (2006). Investor attention, overconfidence and category learning. *Journal of Financial Economics*, 80(3), 563-602. https://doi.org/10.1016/j.jfineco.2005.05.003 | Limited attention and comovement |
| 3 | Rabin, M., & Schrag, J. L. (1999). First impressions matter: A model of confirmatory bias. *Quarterly Journal of Economics*, 114(1), 37-82. https://doi.org/10.1162/003355399555945 | Formal model of confirmation bias in belief updating |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-selective-scanner.png) |
| Status | draft |
