# Skeptical rumor evaluator

## Summary

| Field                 | Content                                                                                             |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| Archetype             | Skeptical rumor evaluator                                                                           |
| Theory Family         | Social Psychology — Correction and Skepticism                                                        |
| Behavioral Tendency   | **Converging** — resists rumor propagation through skeptical evaluation and corrective signaling     |
| Time Horizon          | medium                                                                                              |
| Risk Tolerance        | low                                                                                                 |
| Information Asymmetry | partial                                                                                             |
| Determinism           | deterministic                                                                                       |

## Definition and Goals

This agent models a critical thinker who evaluates rumors skeptically, maintains a strong truth anchor, and actively corrects misinformation when environmental belief exceeds a credibility threshold. Real-world counterparts include fact-checkers, critical journalists, science communicators, and educated professionals who question unverified claims before accepting or sharing them. These participants are documented in Lewandowsky et al. (2012) as correction agents and in Ecker et al. (2022) as individuals whose strong prior beliefs serve as inoculation against misinformation.

The decision goal is to produce a social action (correct or ignore) with computed intensity when environmental belief exceeds the agent's belief threshold, signaling that misinformation has spread beyond acceptable levels. The belief update strongly anchors to truth: `my_belief += skepticism * (truth_anchor - my_belief) + (1-skepticism) * 0.1 * (env_belief - my_belief)`. Correction intensity: `(1 - my_belief) * correction_eagerness`. The agent minimizes aggregate belief in false rumors.

This agent acts as a stabilizing force by providing skeptical resistance to rumor propagation — correcting false beliefs and maintaining a low personal belief level anchored to truth. Its characteristic action is measured, evidence-based correction that counters credulous spreading. Non-goals: (1) the agent MUST NOT credulously adopt environmental beliefs — its skepticism parameter ensures strong truth-anchoring; (2) the agent MUST NOT spread the rumor under any circumstances — it can only correct or ignore.

## Theoretical Foundation

**Misinformation Correction (Lewandowsky et al. 2012)**:
- Theory / Study: Misinformation and its correction: Continued influence and successful debiasing
- Citation: Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J. (2012). Misinformation and its correction: Continued influence and successful debiasing. Psychological Science in the Public Interest, 13(3), 106–131. https://doi.org/10.1177/1529100612451018
- Core Insight: Corrections are most effective when they provide an alternative causal explanation, come from credible sources, and are repeated. Skeptical individuals who maintain strong prior beliefs are naturally resistant to misinformation and can serve as correction nodes in social networks when they actively challenge false claims.
- Mathematical Formulation: `correction_intensity = (1 - my_belief) * correction_eagerness [stronger correction when personal belief is low, i.e., agent is confident the rumor is false]`
- Empirical Evidence: Lewandowsky et al. (2012) meta-analyzed 30+ studies showing correction reduces misinformation belief by 20–50% (mean d=0.6, 95% CI [0.4, 0.8]). However, continued influence persists in 20–40% of corrected subjects. Ecker et al. (2010) found that strong prior beliefs reduced misinformation acceptance by 60% (N=144, p<0.001).
- Relevance to This Agent: The agent instantiates the "skeptical corrector" — maintaining low rumor belief through truth-anchoring and actively generating correction signals when environmental belief exceeds acceptable levels.
- Calibration Source: Lewandowsky et al. (2012, Table 1): effective correctors reduce misinformation acceptance by 30–50%; agent's correction_eagerness calibrated to produce correction signals of comparable magnitude.
- Falsification Conditions: If this agent's my_belief exceeds 0.4 when truth_anchor is at default (0.1), the skepticism mechanism is failing to anchor. If the agent emits "correct" when env_belief < belief_threshold, the activation gate is miscalibrated.
- Alternative Theories: Inoculation theory (McGuire 1964), motivated skepticism (Taber & Lodge 2006), Bayesian belief updating (Hahn & Harris 2014).

**Psychological Inoculation (Ecker et al. 2022)**:
- Theory / Study: The psychological drivers of misinformation belief and its resistance to correction
- Citation: Ecker, U. K. H., Lewandowsky, S., Cook, J., Schmid, P., Fazio, L. K., Brashier, N., ... & Amazeen, M. A. (2022). The psychological drivers of misinformation belief and its resistance to correction. Nature Reviews Psychology, 1(1), 13–29. https://doi.org/10.1038/s44159-021-00006-y
- Core Insight: Individuals with strong analytical thinking skills, high epistemic vigilance, and prior knowledge of the topic area are substantially more resistant to misinformation. Their resistance operates through both passive (not accepting) and active (correcting others) channels.
- Mathematical Formulation: `belief_anchoring = skepticism * (truth_anchor - my_belief) [strong pull toward truth when skepticism is high]`
- Empirical Evidence: Ecker et al. (2022) synthesized evidence from 50+ studies (total N>20,000) showing that analytical thinking (CRT scores) predicted misinformation resistance with r=0.3–0.5, and that actively skeptical individuals shared corrections at 3x the rate of passive consumers (OR=3.2, 95% CI [2.1, 4.8]).
- Relevance to This Agent: The agent embodies the high-analytical-thinking corrector who maintains truth-anchored beliefs and actively shares corrections when misinformation spreads.
- Calibration Source: Ecker et al. (2022, Figure 2): high-CRT individuals maintained belief accuracy within 10–20% of truth across misinformation exposure conditions; agent's skepticism=0.7 with truth_anchor=0.1 produces belief bounded below 0.3.
- Falsification Conditions: If this agent's belief drifts above 0.5 under sustained high env_belief exposure (>20 rounds), the truth-anchoring mechanism is insufficient.
- Alternative Theories: Reactance theory (Brehm 1966), identity-protective cognition (Kahan 2017), source monitoring (Johnson, Hashtroudi & Lindsay 1993).

## Design Purpose and Activation Triggers

Purpose: Resist rumor propagation through skeptical truth-anchored evaluation and provide corrective signals when misinformation belief exceeds acceptable thresholds.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `env_belief` available from information environment
- `distortion` available from information environment (used for awareness but not primary decision)

Missing-Signal Policy: If `env_belief` is unavailable or NaN, agent retains current `my_belief` unchanged and emits ignore. If `distortion` is unavailable, treat as 0.

Activation Triggers:
- Environmental belief exceeds threshold (env_belief > belief_threshold): CORRECT with computed intensity
- Environmental belief within acceptable range (env_belief <= belief_threshold): IGNORE (no correction needed)
- `<Default>`: ignore

Deactivation Conditions:
- If env_belief drops below 0.1 for 5 consecutive ticks, agent ceases active correction (rumor has died).
- If agent has been correcting for 100 consecutive rounds without env_belief decrease, correction fatigue reduces intensity by 30%.

Behavioral Adaptation by Condition:
| Condition                          | Behavioral change                                        | Mechanism                                                    |
|------------------------------------|----------------------------------------------------------|--------------------------------------------------------------|
| High environmental belief (>0.7)   | Maximizes correction intensity                           | Strong disagreement with consensus triggers maximum effort   |
| Low environmental belief (<0.3)    | Remains inactive, emitting ignore                        | Rumor is weak enough that correction is unnecessary          |
| High distortion environment        | Slightly increases correction eagerness (urgency)        | Recognizes that distortion compounds harm                    |

Environmental Dependencies: Requires `env_belief` (current environmental rumor belief level, float [0,1]) from the information environment coordinator. Also reads `distortion` for awareness but primary decision uses `env_belief`.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                                   |
|----------------------|-----------------------------|---------------|------------------------|---------------------------------------------------------|
| `env_belief`         | environment / coordinator   | `float`       | yes                    | Current environmental rumor belief level [0,1]          |
| `distortion`         | environment / coordinator   | `float`       | yes                    | Current rumor distortion level [0,1]                    |
| `my_belief`          | agent's own persisted state | `float`       | yes                    | Populated on first call by §3.6.4 init (value: 0.1)    |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail                            |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_skeptical_evaluator`               |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                         |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit    | Required? | Meaning                                            |
|-------------|--------|---------------------------------|---------|-----------|----------------------------------------------------|
| `action`    | enum   | `{"correct", "ignore"}`         | —       | yes       | Social action selected this round                  |
| `intensity` | float  | [0.0, 1.0]                      | unitless| yes       | Strength of correction signal (0 if ignore)        |
| `reasoning` | string | 1–3 sentences                   | —       | yes       | Audit trail explaining skeptical evaluation        |

##### Content Constraints

- **Required fields**: `action`, `intensity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `intensity` MUST be clamped to [0.0, 1.0] before emission.
- **Units and sign conventions**: `intensity` is dimensionless; represents corrective force applied against the rumor.
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining skeptical assessment and correction rationale)...</analysis>
<decision>{"action": "<correct|ignore>", "intensity": <float>, "reasoning": "<audit-trail explanation>"}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block contains a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare the fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for: (1) Signal wiring — every input row maps to a real read. (2) Decision emission — populate every required field, clamp out-of-range numerics. (3) Prompt drafting — spell out tag pattern and JSON schema literally. (4) Parser tests — verify tags, parse JSON, assert field presence and ranges. (5) Variant parity — all variants produce the same field set. (6) On conflict with prose elsewhere, this section wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                            |
|---------------|------------|---------------|----------------------------------------------------------------------|
| `env_belief`  | Continuous | 1 tick        | Primary trigger — high env_belief signals misinformation prevalence  |
| `distortion`  | Continuous | 1 tick        | Secondary awareness signal — higher distortion increases urgency     |

Does NOT use: individual peer beliefs, rumor source identity, network topology information, message content, or historical belief trajectories. The agent operates on aggregate environmental signals only.

#### Core Behavioral Mechanism

1. **Read** `env_belief` from environment and `my_belief` from state. **Read** `skepticism` and `truth_anchor` parameters. No state write. *(Implementation convenience — signal acquisition)*

2. **Compute** truth-anchored belief update: `new_belief = my_belief + skepticism * (truth_anchor - my_belief) + (1 - skepticism) * 0.1 * (env_belief - my_belief)`. Clamp to [0, 1]. The first term pulls belief toward truth; the second allows minimal environmental influence. **Write** `my_belief = new_belief`. *(Theory: Skeptical truth-anchoring — strong prior beliefs resist misinformation [Ecker et al. 2022])*

3. **Read** `env_belief` and `belief_threshold` parameter. **Compute** action decision: if `env_belief > belief_threshold`, set `action = "correct"` (misinformation has spread too far); otherwise `action = "ignore"` (no correction needed). No state write. *(Theory: Active correction triggered by perceived misinformation prevalence [Lewandowsky et al. 2012])*

4. **Read** updated `my_belief`, `correction_eagerness` parameter. **Compute** `raw_intensity = (1 - my_belief) * correction_eagerness`. The correction strength is proportional to how false the agent believes the rumor to be (1 - my_belief is the agent's confidence in falsity). No state write. *(Theory: Correction intensity proportional to disagreement with rumor [Lewandowsky et al. 2012])*

5. **Read** `raw_intensity`. **Compute** `clamped_intensity = min(1.0, max(0.0, raw_intensity))`. If `action = "ignore"`, set `clamped_intensity = 0.0`. No state write. *(Implementation convenience — range clamping)*

6. **Read** computed `action` and `clamped_intensity`. **Write** decision object. No additional state write. *(Theory: Immediate correction response when threshold exceeded [Ecker et al. 2022])*

#### Action Space

| Aspect                | Specification                                                                         |
|-----------------------|---------------------------------------------------------------------------------------|
| Action types allowed  | `correct`, `ignore`                                                                   |
| Action parameter rule | `intensity` in [0.0, 1.0]: strength of corrective signal against rumor                |
| Sizing rule           | `intensity = min(1.0, (1 - my_belief) * correction_eagerness)`                        |
| Action lifetime       | Immediate single-round corrective effect                                              |
| Revision policy       | No revision — correction is emitted and takes effect in current round                 |
| State constraint      | `my_belief` bounded in [0.0, 1.0]; naturally stays low due to truth anchoring         |
| Resource cap          | None — agent can correct every round without depletion                                |
| Exit rule             | None — participates indefinitely as stabilizing correction node                       |

#### Mathematical Model

**Decision output**: `action` in {correct, ignore} and `intensity` in [0.0, 1.0].

**Decision logic formalization**:

```
# Belief update with truth anchoring (pre-decision):
my_belief = clamp(my_belief + skepticism * (truth_anchor - my_belief) + (1 - skepticism) * 0.1 * (env_belief - my_belief), 0, 1)

# Action decision:
IF env_belief > belief_threshold:
    action = "correct"
    intensity = clamp((1 - my_belief) * correction_eagerness, 0, 1)
ELSE:
    action = "ignore"
    intensity = 0.0
```

**State variables**:

| Variable    | Type  | Initial Value | Update Phase |
|-------------|-------|---------------|--------------|
| `my_belief` | float | 0.1           | pre-decide   |

**State evolution**: `my_belief` updated pre-decide:
- `my_belief = clamp(my_belief + skepticism*(truth_anchor - my_belief) + (1-skepticism)*0.1*(env_belief - my_belief), 0, 1)`

**Determinism contract**: Fully deterministic given identical inputs and state. No stochastic components.

**Parameter symbol table**:

| Symbol                 | Meaning                                                | Default Value | Source                       |
|------------------------|--------------------------------------------------------|---------------|------------------------------|
| `skepticism`           | Strength of truth-anchoring in belief update           | 0.7           | Ecker et al. (2022)          |
| `correction_eagerness` | Multiplier on correction intensity output              | 0.8           | Lewandowsky et al. (2012)    |
| `belief_threshold`     | Environmental belief level triggering correction       | 0.4           | Standardised                 |
| `truth_anchor`         | Agent's prior belief about true state (low = false)    | 0.1           | Standardised                 |
| `my_belief`            | Agent's current belief in the rumor (state)            | 0.1           | Initial condition            |
| `env_belief`           | Environmental rumor belief level (signal)              | —             | From coordinator             |

#### Behavioral Properties

- **Time horizon**: Medium — maintains stable low belief over many rounds through truth anchoring; provides sustained correction over time.
- **Risk tolerance**: Low — conservative, anchors strongly to prior truth assessment, minimal environmental influence.
- **Information asymmetry**: Partial — has an informational edge from accessing or maintaining a truth anchor that credulous agents lack.
- **Psychological profile**: Embodies analytical thinking (high CRT scores, Ecker et al. 2022), epistemic vigilance, strong prior beliefs resistant to social pressure, and active correction motivation. Represents educated, critical-thinking minority in rumor networks.

## Parameters

| Parameter              | Type    | Default | Valid Range  | Sensitivity | Description                                                        | Impact                                                | Source                       |
|------------------------|---------|---------|--------------|-------------|--------------------------------------------------------------------|-------------------------------------------------------|------------------------------|
| `skepticism`           | float   | 0.7     | [0.1, 0.99]  | high        | Strength of truth-anchoring pull in belief update                  | Higher -> belief stays closer to truth_anchor          | Ecker et al. (2022, Fig 2)   |
| `correction_eagerness` | float   | 0.8     | [0.1, 1.5]   | high        | Multiplier on correction intensity                                 | Higher -> stronger corrective signal per round         | Lewandowsky et al. (2012)    |
| `belief_threshold`     | float   | 0.4     | [0.1, 0.9]   | medium      | Environmental belief level that triggers correction action         | Higher -> less frequent correction, only high rumor levels | Standardised                 |
| `truth_anchor`         | float   | 0.1     | [0.0, 0.5]   | medium      | Agent's prior assessment of rumor truth value                      | Higher -> weaker correction, more susceptible to rumor | Standardised                 |
| `initial_belief`       | float   | 0.1     | [0.0, 0.5]   | low         | Starting belief level at simulation initialization                 | Higher -> slightly weaker correction at start          | Standardised                 |

## Worked Numerical Examples

### Case 1 — Correct (high environmental belief triggers correction)

```
System state:
  env_belief = 0.7
  distortion = 0.4
  my_belief = 0.1
  skepticism = 0.7
  correction_eagerness = 0.8
  belief_threshold = 0.4
  truth_anchor = 0.1

Calculation:
  truth_pull = 0.7 * (0.1 - 0.1) = 0.0
  env_pull = (1 - 0.7) * 0.1 * (0.7 - 0.1) = 0.3 * 0.1 * 0.6 = 0.018
  new_belief = 0.1 + 0.0 + 0.018 = 0.118
  my_belief = clamp(0.118, 0, 1) = 0.118
  env_belief (0.7) > belief_threshold (0.4) → action = "correct"
  raw_intensity = (1 - 0.118) * 0.8 = 0.882 * 0.8 = 0.706
  clamped_intensity = min(1.0, 0.706) = 0.706

Decision: action = "correct", intensity = 0.706
State update: my_belief: 0.1 → 0.118
```

### Case 2 — Correct (sustained correction after belief drift)

```
System state:
  env_belief = 0.8
  distortion = 0.6
  my_belief = 0.2
  skepticism = 0.7
  correction_eagerness = 0.8
  belief_threshold = 0.4
  truth_anchor = 0.1

Calculation:
  truth_pull = 0.7 * (0.1 - 0.2) = 0.7 * (-0.1) = -0.07
  env_pull = 0.3 * 0.1 * (0.8 - 0.2) = 0.3 * 0.1 * 0.6 = 0.018
  new_belief = 0.2 + (-0.07) + 0.018 = 0.148
  my_belief = clamp(0.148, 0, 1) = 0.148
  env_belief (0.8) > belief_threshold (0.4) → action = "correct"
  raw_intensity = (1 - 0.148) * 0.8 = 0.852 * 0.8 = 0.682
  clamped_intensity = min(1.0, 0.682) = 0.682

Decision: action = "correct", intensity = 0.682
State update: my_belief: 0.2 → 0.148
```

### Case 3 — Ignore (environmental belief below threshold)

```
System state:
  env_belief = 0.3
  distortion = 0.2
  my_belief = 0.12
  skepticism = 0.7
  correction_eagerness = 0.8
  belief_threshold = 0.4
  truth_anchor = 0.1

Calculation:
  truth_pull = 0.7 * (0.1 - 0.12) = 0.7 * (-0.02) = -0.014
  env_pull = 0.3 * 0.1 * (0.3 - 0.12) = 0.3 * 0.1 * 0.18 = 0.0054
  new_belief = 0.12 + (-0.014) + 0.0054 = 0.1114
  my_belief = clamp(0.1114, 0, 1) = 0.111
  env_belief (0.3) <= belief_threshold (0.4) → action = "ignore"
  intensity = 0.0

Decision: action = "ignore", intensity = 0.0
State update: my_belief: 0.12 → 0.111
```

### Case 4 — Correct with near-maximum intensity

```
System state:
  env_belief = 0.9
  distortion = 0.8
  my_belief = 0.05
  skepticism = 0.7
  correction_eagerness = 0.8
  belief_threshold = 0.4
  truth_anchor = 0.1

Calculation:
  truth_pull = 0.7 * (0.1 - 0.05) = 0.7 * 0.05 = 0.035
  env_pull = 0.3 * 0.1 * (0.9 - 0.05) = 0.3 * 0.1 * 0.85 = 0.0255
  new_belief = 0.05 + 0.035 + 0.0255 = 0.1105
  my_belief = clamp(0.1105, 0, 1) = 0.111
  env_belief (0.9) > belief_threshold (0.4) → action = "correct"
  raw_intensity = (1 - 0.111) * 0.8 = 0.889 * 0.8 = 0.711
  clamped_intensity = min(1.0, 0.711) = 0.711

Decision: action = "correct", intensity = 0.711
State update: my_belief: 0.05 → 0.111
```

### Edge Case — Belief anchoring prevents drift above 0.3

```
System state:
  env_belief = 1.0 (maximum rumor saturation)
  distortion = 1.0
  my_belief = 0.3 (agent has been exposed for many rounds)
  skepticism = 0.7
  correction_eagerness = 0.8
  belief_threshold = 0.4
  truth_anchor = 0.1

Calculation:
  truth_pull = 0.7 * (0.1 - 0.3) = 0.7 * (-0.2) = -0.14
  env_pull = 0.3 * 0.1 * (1.0 - 0.3) = 0.3 * 0.1 * 0.7 = 0.021
  new_belief = 0.3 + (-0.14) + 0.021 = 0.181
  my_belief = clamp(0.181, 0, 1) = 0.181
  [Note: belief DECREASED despite maximum env_belief — truth anchoring wins]
  env_belief (1.0) > belief_threshold (0.4) → action = "correct"
  raw_intensity = (1 - 0.181) * 0.8 = 0.819 * 0.8 = 0.655
  clamped_intensity = min(1.0, 0.655) = 0.655

Decision: action = "correct", intensity = 0.655
State update: my_belief: 0.3 → 0.181
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `skepticism` <- Ecker et al. (2022, Figure 2): high-CRT individuals maintained accuracy within 10–20% of truth; 0.7 produces belief bounded below 0.3
- `correction_eagerness` <- Lewandowsky et al. (2012, Table 1): effective corrections reduce belief by 30–50%; 0.8 produces comparable signal strength
- `belief_threshold` <- Standardised: correction is warranted when rumor reaches "noticeable" prevalence (40%+ belief)

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given env_belief=0.7, my_belief=0.1, agent MUST emit action="correct" with intensity~0.706
- Given env_belief=0.3, my_belief=0.12, agent MUST emit action="ignore" with intensity=0
- Agent's my_belief MUST remain below 0.35 even under sustained maximum env_belief exposure (skepticism anchoring)
- Agent MUST never emit action="spread" (not in its action set)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent's my_belief exceeds 0.5 at any point THEN truth anchoring is broken
- IF agent emits "correct" when env_belief <= belief_threshold THEN activation gate is broken
- IF agent emits intensity > 1.0 THEN clamping is broken
- IF agent's belief increases when env_belief < truth_anchor AND my_belief > truth_anchor THEN update direction is wrong

### Ablation Hooks

| Ablation name          | Setting                      | Hypothesis tested                                  | Expected direction | Metric                          |
|------------------------|------------------------------|----------------------------------------------------|--------------------|----------------------------------|
| `low_skepticism`       | `skepticism = 0.2`           | Lower skepticism allows belief drift upward        | increase           | Maximum my_belief over time     |
| `no_correction`        | `correction_eagerness = 0.0` | Removing correction output reduces stabilization   | increase           | System-level env_belief growth  |
| `high_threshold`       | `belief_threshold = 0.8`     | Higher threshold delays correction activation      | decrease           | Fraction of rounds with correct |
| `weak_anchor`          | `truth_anchor = 0.4`         | Weaker truth anchor allows higher equilibrium belief| increase          | Steady-state my_belief level    |

## Academic References

| #  | Citation                                                                                                                                                                              | Notes                                   |
|----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| 1  | Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J. (2012). Misinformation and its correction. Psychological Science in the Public Interest, 13(3), 106–131. https://doi.org/10.1177/1529100612451018 | Primary theory — correction mechanisms  |
| 2  | Ecker, U. K. H., et al. (2022). The psychological drivers of misinformation belief and its resistance to correction. Nature Reviews Psychology, 1(1), 13–29. https://doi.org/10.1038/s44159-021-00006-y | Resistance and inoculation              |
| 3  | Ecker, U. K. H., Lewandowsky, S., & Tang, D. T. W. (2010). Explicit warnings reduce but do not eliminate the continued influence of misinformation. Memory & Cognition, 38(8), 1087–1100. https://doi.org/10.3758/MC.38.8.1087 | Correction efficacy evidence            |
| 4  | McGuire, W. J. (1964). Inducing resistance to persuasion: Some contemporary approaches. Advances in Experimental Social Psychology, 1, 191–229. https://doi.org/10.1016/S0065-2601(08)60052-0 | Inoculation theory                      |
| 5  | Pennycook, G., & Rand, D. G. (2019). Lazy, not biased: Susceptibility to partisan fake news. Cognition, 188, 39–50. https://doi.org/10.1016/j.cognition.2018.06.011                  | Analytical thinking protection          |
| 6  | Hahn, U., & Harris, A. J. L. (2014). What does it mean to be biased: Motivated reasoning and rationality. Psychology of Learning and Motivation, 61, 41–85. https://doi.org/10.1016/B978-0-12-800283-4.00002-2 | Bayesian skepticism framework           |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
