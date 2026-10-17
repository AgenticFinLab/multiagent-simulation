# Uninformed passive bystander

## Summary

| Field                 | Content                                                                                           |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Archetype             | Uninformed passive bystander                                                                      |
| Theory Family         | Social Psychology — Passive Audience and Bystander Effects                                         |
| Behavioral Tendency   | **Adaptive** — occasionally spreads due to stochastic engagement but mostly remains passive        |
| Time Horizon          | short                                                                                             |
| Risk Tolerance        | low                                                                                               |
| Information Asymmetry | none                                                                                              |
| Determinism           | stochastic-given-seed                                                                             |

## Definition and Goals

This agent models a passive member of the rumor audience who does not actively seek, evaluate, or deliberately spread rumors, but occasionally engages in transmission through incidental social participation. Real-world counterparts include casual social media scrollers who occasionally share content without deep processing, watercooler conversation participants who half-hear and occasionally repeat rumors, and the "silent majority" in information networks. These participants are documented in Shibutani (1966) as the passive audience that forms the background medium through which active rumor transmission occurs.

The decision goal is to produce a social action (spread or ignore) determined stochastically — the agent engages with probability `engagement_probability` and, when engaged, spreads with probability `spread_probability`. The belief update is weak: `my_belief += 0.1 * (env_belief - my_belief)`. The agent provides ambient background noise in the rumor network without deliberate amplification or correction.

This agent acts as a neutral background element — neither strongly destabilizing nor stabilizing. Its characteristic action is mostly inaction, punctuated by occasional, low-intensity spreading that adds mild stochastic noise to the system dynamics. Non-goals: (1) the agent MUST NOT actively fact-check or correct rumors — it lacks the motivation and knowledge; (2) the agent MUST NOT exhibit high credulity or eagerness — its occasional spreading is incidental, not driven by conviction.

## Theoretical Foundation

**Passive Audience Theory (Shibutani 1966)**:
- Theory / Study: Improvised News: A Sociological Study of Rumor
- Citation: Shibutani, T. (1966). Improvised News: A Sociological Study of Rumor. Bobbs-Merrill Company. ISBN: 978-0672610523
- Core Insight: Rumor propagation occurs within a social field that includes active transmitters, critical evaluators, and a large passive audience. The passive audience forms the background population that occasionally participates in transmission through normal social interaction without deliberate intent. Their participation is incidental and low-intensity, but their aggregate effect provides the medium through which rumor chains persist.
- Mathematical Formulation: `P(engage_this_round) = engagement_probability; P(spread | engaged) = spread_probability`
- Empirical Evidence: Shibutani (1966) observed in 5 natural rumor episodes that only 15–30% of the exposed population actively retransmitted rumors, while 50–70% remained passive observers who occasionally shared in conversational contexts. Hampton et al. (2014) confirmed in social media contexts that only 25–35% of users actively share content (Pew Research, N=1801, margin of error 2.6%).
- Relevance to This Agent: The agent instantiates the passive majority — present in the network, weakly influenced by ambient belief, but engaging in transmission only through stochastic incidental action.
- Calibration Source: Shibutani (1966): passive audience engagement rate 15–30%; Hampton et al. (2014): social media lurker-to-sharer ratio approximately 70:30; agent's engagement_probability=0.3 targets the boundary between passive and active.
- Falsification Conditions: If this agent's spread rate (fraction of rounds with action="spread") exceeds 50% over 100 rounds, it is behaving more actively than the bystander archetype permits. If belief converges as rapidly as a credulous agent (within 3 rounds), the weak update is not functioning.
- Alternative Theories: Two-step flow theory (Lazarsfeld & Katz 1955), spiral of silence (Noelle-Neumann 1974), diffusion of innovations late majority (Rogers 2003).

**Bystander Effect in Information Sharing (Latane & Darley 1970)**:
- Theory / Study: The Unresponsive Bystander: Why Doesn't He Help?
- Citation: Latane, B., & Darley, J. M. (1970). The Unresponsive Bystander: Why Doesn't He Help? Appleton-Century-Crofts. (See also: Latane & Nida, 1981, meta-analysis) https://doi.org/10.1037/0022-3514.21.2.183
- Core Insight: In the presence of other potential actors, individuals experience diffusion of responsibility and are less likely to take action. Applied to information sharing, passive network participants assume others will share or correct, reducing their own engagement probability. The larger the perceived audience, the lower individual engagement.
- Mathematical Formulation: `engagement_gate = random() < engagement_probability [stochastic engagement independent of others' behavior]`
- Empirical Evidence: Latane & Darley (1968) found bystander intervention probability dropped from 85% (alone) to 31% (in groups of 5) for emergencies (N=72, p<0.01). Meta-analysis by Fischer et al. (2011) confirmed bystander effect with d=0.35 across 105 studies (N>7700). Applied to information sharing: Muller & Peres (2019) found sharing probability decreases with perceived audience size (OR=0.7 per doubling of audience).
- Relevance to This Agent: The agent's low engagement_probability reflects the bystander/diffusion-of-responsibility effect — it participates only occasionally because it implicitly assumes others will carry the transmission burden.
- Calibration Source: Fischer et al. (2011): average bystander non-intervention rate ~65%; agent's engagement_probability=0.3 (non-engagement=0.7) matches this benchmark.
- Falsification Conditions: If this agent engages in more than 50% of rounds over 200+ rounds, the stochastic engagement gate is not constraining behavior to bystander-appropriate levels.
- Alternative Theories: Social loafing (Karau & Williams 1993), free-rider problem (Olson 1965), rational inattention (Sims 2003).

## Design Purpose and Activation Triggers

Purpose: Represent the passive background population that weakly absorbs environmental belief and occasionally, stochastically transmits at low intensity.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `env_belief` available from information environment
- Pseudorandom seed available for stochastic decisions

Missing-Signal Policy: If `env_belief` is unavailable or NaN, agent retains current `my_belief` unchanged and emits ignore.

Activation Triggers:
- Stochastic engagement gate passes (random() < engagement_probability) AND spread roll succeeds (random() < spread_probability): SPREAD at low intensity
- Engagement gate fails OR spread roll fails: IGNORE
- `<Default>`: ignore

Deactivation Conditions:
- None explicit — agent is always available but mostly inactive due to low engagement probability.
- If env_belief = 0 for 20+ consecutive rounds, agent's already-low belief decays to 0 and spreading becomes impossible.

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                  | Mechanism                                        |
|------------------------------|----------------------------------------------------|--------------------------------------------------|
| High environmental belief    | Slow belief drift upward, marginally more intensity| Weak env_belief influence gradually raises belief |
| Low environmental belief     | Belief drifts toward 0, very unlikely to spread    | Weak adoption combined with low starting belief  |
| Any condition                | Engagement remains at fixed probability            | Stochastic gate is independent of environment    |

Environmental Dependencies: Requires `env_belief` from the information environment coordinator and a seeded pseudorandom number generator for stochastic decisions.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                                    |
|----------------------|-----------------------------|---------------|------------------------|----------------------------------------------------------|
| `env_belief`         | environment / coordinator   | `float`       | yes                    | Current environmental rumor belief level [0,1]           |
| `my_belief`          | agent's own persisted state | `float`       | yes                    | Populated on first call by §3.6.4 init (value: 0.1)     |
| `rng_seed`           | scheduler / round header    | `int`         | yes                    | Seed for stochastic engagement/spread decisions          |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail and RNG seeding             |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_uninformed_bystander`               |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit    | Required? | Meaning                                           |
|-------------|--------|---------------------------------|---------|-----------|---------------------------------------------------|
| `action`    | enum   | `{"spread", "ignore"}`          | —       | yes       | Social action selected this round                 |
| `intensity` | float  | [0.0, 1.0]                      | unitless| yes       | Strength of incidental spread (0 if ignore)       |
| `reasoning` | string | 1–3 sentences                   | —       | yes       | Audit trail explaining engagement decision        |

##### Content Constraints

- **Required fields**: `action`, `intensity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `intensity` MUST be clamped to [0.0, 1.0] before emission.
- **Units and sign conventions**: `intensity` is dimensionless; represents weak, incidental propagation force.
- **Determinism markers**: Decision is stochastic-given-seed; same seed + same inputs + same state = same output. Implementation MUST log or derive the per-round RNG state deterministically from `rng_seed` and `round`.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining engagement roll and spread decision)...</analysis>
<decision>{"action": "<spread|ignore>", "intensity": <float>, "reasoning": "<audit-trail explanation>"}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block contains a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants generate `<analysis>` from a deterministic template (with stochastic outcome noted).
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare the fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for: (1) Signal wiring — every input row maps to a real read. (2) Decision emission — populate every required field, clamp out-of-range numerics. (3) Prompt drafting — spell out tag pattern and JSON schema literally. (4) Parser tests — verify tags, parse JSON, assert field presence and ranges. (5) Variant parity — all variants produce the same field set. (6) On conflict with prose elsewhere, this section wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                    |
|---------------|------------|---------------|--------------------------------------------------------------|
| `env_belief`  | Continuous | 1 tick        | Weak ambient influence on bystander belief                    |

Does NOT use: distortion signals, truth values, peer individual beliefs, correction signals, network position information, or any active information-seeking signals. The bystander is deliberately uninformed and passive.

#### Core Behavioral Mechanism

1. **Read** `env_belief` from environment and `my_belief` from state. **Compute** weak belief update: `new_belief = my_belief + 0.1 * (env_belief - my_belief)`. Clamp to [0, 1]. **Write** `my_belief = new_belief`. *(Theory: Weak ambient influence — passive exposure drifts belief slowly [Shibutani 1966])*

2. **Read** `engagement_probability` parameter. **Compute** engagement roll: generate uniform random number r1 from seeded RNG; if `r1 < engagement_probability`, set engaged = true; else engaged = false. No state write. *(Theory: Bystander effect — low probability of individual engagement [Latane & Darley 1970])*

3. **Read** engaged flag and `spread_probability` parameter. **Compute** spread roll: if engaged = true, generate uniform random r2; if `r2 < spread_probability`, set `action = "spread"`; else `action = "ignore"`. If engaged = false, `action = "ignore"`. No state write. *(Theory: Even when engaged, spreading is not guaranteed — incidental participation [Shibutani 1966])*

4. **Read** updated `my_belief` and action. **Compute** intensity: if `action = "spread"`, set `raw_intensity = my_belief * 0.5` (bystanders spread at reduced intensity); else `raw_intensity = 0.0`. No state write. *(Theory: Passive participants transmit with lower conviction and intensity [Shibutani 1966])*

5. **Read** `raw_intensity`. **Compute** `clamped_intensity = min(1.0, max(0.0, raw_intensity))`. No state write. *(Implementation convenience — range clamping)*

6. **Read** computed `action` and `clamped_intensity`. **Write** decision object. No additional state write. *(Implementation convenience — emission)*

#### Action Space

| Aspect                | Specification                                                                     |
|-----------------------|-----------------------------------------------------------------------------------|
| Action types allowed  | `spread`, `ignore`                                                                |
| Action parameter rule | `intensity` in [0.0, 1.0]: incidental propagation force (typically low)           |
| Sizing rule           | `intensity = my_belief * 0.5` when spreading; 0 otherwise                         |
| Action lifetime       | Immediate single-round effect                                                     |
| Revision policy       | No revision — stochastic outcome is final for current round                       |
| State constraint      | `my_belief` bounded [0, 1]; drifts slowly                                         |
| Resource cap          | None — but engagement probability naturally limits activity                       |
| Exit rule             | None — perpetually available as background participant                             |

#### Mathematical Model

**Decision output**: `action` in {spread, ignore} and `intensity` in [0.0, 1.0].

**Decision logic formalization**:

```
# Belief update (pre-decision):
my_belief = clamp(my_belief + 0.1 * (env_belief - my_belief), 0, 1)

# Stochastic engagement:
r1 = uniform_random(seed, round, 1)  # first random draw
r2 = uniform_random(seed, round, 2)  # second random draw

IF r1 < engagement_probability AND r2 < spread_probability:
    action = "spread"
    intensity = clamp(my_belief * 0.5, 0, 1)
ELSE:
    action = "ignore"
    intensity = 0.0
```

**State variables**:

| Variable    | Type  | Initial Value | Update Phase |
|-------------|-------|---------------|--------------|
| `my_belief` | float | 0.1           | pre-decide   |

**State evolution**: `my_belief` updated pre-decide:
- `my_belief = clamp(my_belief + 0.1 * (env_belief - my_belief), 0, 1)`
- Convergence is very slow (10% per round toward env_belief).

**Determinism contract**: Stochastic-given-seed. Given identical `rng_seed`, `round`, inputs, and state, the agent produces identical output. The RNG is seeded deterministically per round.

**Parameter symbol table**:

| Symbol                   | Meaning                                              | Default Value | Source                       |
|--------------------------|------------------------------------------------------|---------------|------------------------------|
| `engagement_probability` | Probability of engaging with rumor on any given round| 0.3           | Shibutani (1966)             |
| `spread_probability`     | Probability of spreading when engaged                | 0.5           | Hampton et al. (2014)        |
| `belief_drift_rate`      | Rate of belief convergence toward env_belief         | 0.1           | Standardised                 |
| `intensity_scaling`      | Bystander intensity discount factor                  | 0.5           | Standardised                 |
| `my_belief`              | Agent's current belief (state)                       | 0.1           | Initial condition            |

#### Behavioral Properties

- **Time horizon**: Short — no planning; purely reactive with stochastic engagement per round.
- **Risk tolerance**: Low — minimal commitment to either spreading or correcting; mostly observes.
- **Information asymmetry**: None — no privileged information; weaker access than even credulous agents who at least actively process environmental signals.
- **Psychological profile**: Embodies bystander effect (Latane & Darley 1970), passive audience behavior (Shibutani 1966), low cognitive engagement with rumor content, and diffusion of responsibility. Represents the majority of network participants who form the background medium.

## Parameters

| Parameter                | Type    | Default | Valid Range  | Sensitivity | Description                                                     | Impact                                               | Source                    |
|--------------------------|---------|---------|--------------|-------------|-----------------------------------------------------------------|------------------------------------------------------|---------------------------|
| `engagement_probability` | float   | 0.3     | [0.05, 0.8]  | high        | Probability of engaging with rumor each round                   | Higher -> more frequent stochastic spreading         | Shibutani (1966)          |
| `spread_probability`     | float   | 0.5     | [0.1, 0.9]   | high        | Probability of spreading when engaged                           | Higher -> more spreading events when engaged         | Hampton et al. (2014)     |
| `belief_drift_rate`      | float   | 0.1     | [0.01, 0.5]  | medium      | Rate of belief convergence toward environmental belief          | Higher -> faster ambient influence, more conviction   | Standardised              |
| `intensity_scaling`      | float   | 0.5     | [0.1, 1.0]   | medium      | Discount factor on spread intensity (bystanders spread weakly)  | Higher -> stronger per-event propagation             | Standardised              |
| `initial_belief`         | float   | 0.1     | [0.0, 0.5]   | low         | Starting belief at initialization                               | Higher -> slightly earlier potential spreading       | Standardised              |

## Worked Numerical Examples

### Case 1 — Spread (both stochastic gates pass)

```
System state:
  env_belief = 0.6
  my_belief = 0.1
  engagement_probability = 0.3
  spread_probability = 0.5
  intensity_scaling = 0.5
  r1 = 0.15 (< 0.3, engaged)
  r2 = 0.35 (< 0.5, spreads)

Calculation:
  belief_update = 0.1 + 0.1 * (0.6 - 0.1) = 0.1 + 0.05 = 0.15
  my_belief = clamp(0.15, 0, 1) = 0.15
  r1 (0.15) < engagement_probability (0.3) → engaged = true
  r2 (0.35) < spread_probability (0.5) → action = "spread"
  raw_intensity = 0.15 * 0.5 = 0.075
  clamped_intensity = 0.075

Decision: action = "spread", intensity = 0.075
State update: my_belief: 0.1 → 0.15
```

### Case 2 — Ignore (engagement gate fails)

```
System state:
  env_belief = 0.7
  my_belief = 0.2
  engagement_probability = 0.3
  spread_probability = 0.5
  intensity_scaling = 0.5
  r1 = 0.55 (> 0.3, not engaged)

Calculation:
  belief_update = 0.2 + 0.1 * (0.7 - 0.2) = 0.2 + 0.05 = 0.25
  my_belief = clamp(0.25, 0, 1) = 0.25
  r1 (0.55) >= engagement_probability (0.3) → engaged = false
  action = "ignore"
  intensity = 0.0

Decision: action = "ignore", intensity = 0.0
State update: my_belief: 0.2 → 0.25
```

### Case 3 — Ignore (engaged but spread roll fails)

```
System state:
  env_belief = 0.5
  my_belief = 0.3
  engagement_probability = 0.3
  spread_probability = 0.5
  intensity_scaling = 0.5
  r1 = 0.20 (< 0.3, engaged)
  r2 = 0.75 (> 0.5, does not spread)

Calculation:
  belief_update = 0.3 + 0.1 * (0.5 - 0.3) = 0.3 + 0.02 = 0.32
  my_belief = clamp(0.32, 0, 1) = 0.32
  r1 (0.20) < engagement_probability (0.3) → engaged = true
  r2 (0.75) >= spread_probability (0.5) → action = "ignore"
  intensity = 0.0

Decision: action = "ignore", intensity = 0.0
State update: my_belief: 0.3 → 0.32
```

### Case 4 — Spread after many rounds of drift (belief has accumulated)

```
System state:
  env_belief = 0.8
  my_belief = 0.55 (after many rounds of slow drift)
  engagement_probability = 0.3
  spread_probability = 0.5
  intensity_scaling = 0.5
  r1 = 0.10 (< 0.3, engaged)
  r2 = 0.30 (< 0.5, spreads)

Calculation:
  belief_update = 0.55 + 0.1 * (0.8 - 0.55) = 0.55 + 0.025 = 0.575
  my_belief = clamp(0.575, 0, 1) = 0.575
  r1 (0.10) < engagement_probability (0.3) → engaged = true
  r2 (0.30) < spread_probability (0.5) → action = "spread"
  raw_intensity = 0.575 * 0.5 = 0.2875
  clamped_intensity = 0.288

Decision: action = "spread", intensity = 0.288
State update: my_belief: 0.55 → 0.575
```

### Edge Case — env_belief = 0, belief decays toward zero

```
System state:
  env_belief = 0.0
  my_belief = 0.3
  engagement_probability = 0.3
  spread_probability = 0.5
  intensity_scaling = 0.5
  r1 = 0.10 (engaged)
  r2 = 0.20 (would spread)

Calculation:
  belief_update = 0.3 + 0.1 * (0.0 - 0.3) = 0.3 - 0.03 = 0.27
  my_belief = clamp(0.27, 0, 1) = 0.27
  r1 (0.10) < 0.3 → engaged
  r2 (0.20) < 0.5 → action = "spread"
  raw_intensity = 0.27 * 0.5 = 0.135
  clamped_intensity = 0.135
  [Note: even with env_belief=0, belief decays slowly — still capable of weak spread]

Decision: action = "spread", intensity = 0.135
State update: my_belief: 0.3 → 0.27
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `engagement_probability` <- Shibutani (1966): 15–30% of exposed population actively retransmits; Hampton et al. (2014): ~30% of social media users are active sharers
- `spread_probability` <- Hampton et al. (2014): among engaged users, approximately 50% actually share any given piece of content
- `belief_drift_rate` <- Standardised: weak ambient influence at 10% per exposure period, consistent with low-attention processing

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Over 100 rounds, the fraction of rounds with action="spread" MUST be approximately engagement_probability * spread_probability = 0.3 * 0.5 = 15% (within statistical tolerance)
- Belief MUST converge slowly toward env_belief (not rapidly like credulous agents)
- When spreading, intensity MUST be low (my_belief * 0.5, typically 0.05–0.3)
- Agent MUST never emit "correct" (not in its action set)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent spreads more than 50% of rounds over 200+ rounds THEN engagement/spread gates are too permissive
- IF agent's belief converges to env_belief within 3 rounds THEN drift rate is too high (not bystander behavior)
- IF agent emits intensity > 0.5 regularly THEN intensity scaling is not constraining output
- IF same seed+round+state produces different outputs THEN stochastic determinism is broken

### Ablation Hooks

| Ablation name           | Setting                          | Hypothesis tested                                   | Expected direction | Metric                          |
|-------------------------|----------------------------------|-----------------------------------------------------|--------------------|----------------------------------|
| `high_engagement`       | `engagement_probability = 0.8`   | Higher engagement converts bystander to active node | increase           | Fraction of rounds with spread  |
| `no_spread_gate`        | `spread_probability = 1.0`       | Removing second gate increases spread frequency     | increase           | Fraction of rounds with spread  |
| `fast_drift`            | `belief_drift_rate = 0.5`        | Faster drift makes bystander more responsive        | increase           | Mean intensity when spreading   |
| `full_intensity`        | `intensity_scaling = 1.0`        | Full intensity removes bystander discount           | increase           | Mean intensity when spreading   |

## Academic References

| #  | Citation                                                                                                                                                         | Notes                                    |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1  | Shibutani, T. (1966). Improvised News: A Sociological Study of Rumor. Bobbs-Merrill Company. ISBN: 978-0672610523                                                | Primary theory — passive audience        |
| 2  | Latane, B., & Darley, J. M. (1970). The Unresponsive Bystander: Why Doesn't He Help? Appleton-Century-Crofts.                                                   | Bystander effect theory                  |
| 3  | Hampton, K. N., Rainie, L., Lu, W., Dwyer, M., Shin, I., & Purcell, K. (2014). Social media and the spiral of silence. Pew Research Center.                    | Social media engagement rates            |
| 4  | Fischer, P., et al. (2011). The bystander-effect: A meta-analytic review. Psychological Bulletin, 137(4), 517–537. https://doi.org/10.1037/a0023304               | Bystander effect meta-analysis           |
| 5  | Noelle-Neumann, E. (1974). The spiral of silence: A theory of public opinion. Journal of Communication, 24(2), 43–51. https://doi.org/10.1111/j.1460-2466.1974.tb00367.x | Silence/passivity theory                 |
| 6  | Rogers, E. M. (2003). Diffusion of Innovations (5th ed.). Free Press. ISBN: 978-0743222099                                                                       | Late majority/laggard categorization     |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
