# Gullible rumor spreader

## Summary

| Field                 | Content                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Archetype             | Gullible rumor spreader                                                                          |
| Theory Family         | Social Psychology — Rumor Transmission and Belief Contagion                                       |
| Behavioral Tendency   | **Diverging** — amplifies rumor propagation by credulously adopting and eagerly spreading beliefs |
| Time Horizon          | short                                                                                            |
| Risk Tolerance        | high                                                                                             |
| Information Asymmetry | none                                                                                             |
| Determinism           | deterministic                                                                                    |

## Definition and Goals

This agent models a highly credulous participant in a rumor-spreading network who rapidly adopts environmental beliefs and eagerly transmits them with amplified intensity. Real-world counterparts include social media users who share unverified content without fact-checking, rumor-mill participants in organizational settings, and retail investors who rapidly propagate market rumors. These participants are documented in Allport & Postman (1947) as uncritical relay nodes and in Vosoughi, Roy & Aral (2018) as the majority of false-news sharers who spread misinformation without malicious intent.

The decision goal is to produce a social action (spread or ignore) with computed intensity on each round, based on the agent's current belief level and eagerness to share. The belief update rule is: `my_belief += credulity * (env_belief - my_belief)`, converging rapidly toward environmental consensus. The spread intensity is: `my_belief * spread_eagerness * (1 + distortion_amplification * distortion)`. The agent maximizes social participation without concern for accuracy.

This agent acts as a strongly destabilizing force within the rumor simulation by rapidly adopting beliefs from the environment and spreading them with amplified intensity. Its characteristic action is immediate, unfiltered belief adoption followed by enthusiastic dissemination. Non-goals: (1) the agent MUST NOT evaluate the truth value of information before spreading — it is explicitly non-critical; (2) the agent MUST NOT reduce spread intensity in response to corrections or disconfirming evidence within the same decision cycle.

## Theoretical Foundation

**Rumor Transmission Theory (Allport & Postman 1947)**:
- Theory / Study: The Psychology of Rumor
- Citation: Allport, G. W., & Postman, L. (1947). The Psychology of Rumor. Henry Holt and Company. (Reprinted: Russell & Russell, 1965)
- Core Insight: Rumor transmission follows a basic law: R ~ i * a (rumor intensity is proportional to the importance of the subject times the ambiguity of evidence). Credulous individuals serve as amplifying nodes who adopt information with minimal filtering and retransmit with added emotional intensity, forming cascading chains.
- Mathematical Formulation: `spread_intensity = my_belief * spread_eagerness * (1 + distortion_amplification * distortion)`
- Empirical Evidence: Allport & Postman (1947) documented in serial reproduction experiments (N=40 chains of 6–8 subjects) that 70% of detail was lost in first 5 transmissions, but emotional intensity and confidence remained stable or increased. Buckner (1965) replicated showing credulous receivers increased message spread rate by 2.5x compared to critical receivers (Journal of Communication, 15(1), 54–68).
- Relevance to This Agent: The agent instantiates the "credulous receiver" archetype from Allport & Postman — uncritically absorbing environmental belief and retransmitting with enthusiasm proportional to belief strength.
- Calibration Source: Buckner (1965, Table 3): credulous subjects adopted 80–90% of message content as belief; agent's credulity=0.8 targets the empirical midpoint of uncritical adoption.
- Falsification Conditions: If this agent's belief does not converge toward env_belief within 3 ticks (remaining >20% distant), the credulity mechanism is not functioning. If spread intensity does not increase when environmental belief increases, the propagation mechanism is broken.
- Alternative Theories: Information cascades (Bikhchandani, Hirshleifer & Welch 1992), social learning (Banerjee 1992), cognitive laziness (Pennycook & Rand 2019).

**False News Virality (Vosoughi, Roy & Aral 2018)**:
- Theory / Study: The spread of true and false news online
- Citation: Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. Science, 359(6380), 1146–1151. https://doi.org/10.1126/science.aap9559
- Core Insight: False news spreads faster, farther, and deeper than true news on social networks. Human factors — not bots — are primarily responsible: novelty and emotional reactions drive sharing behavior. Credulous users amplify false content because it triggers stronger emotional responses than mundane truth.
- Mathematical Formulation: `belief_update = credulity * (env_belief - my_belief) [exponential convergence toward environmental consensus]`
- Empirical Evidence: Vosoughi et al. (2018) analyzed 126,000 rumor cascades on Twitter (2006–2017, ~3 million users). False news reached 1,500 people 6x faster than true news (p<0.001). False news was 70% more likely to be retweeted than true news (odds ratio 1.7, 95% CI [1.6, 1.8]).
- Relevance to This Agent: The agent models the typical credulous user whose rapid adoption and eager sharing behavior drives the cascade dynamics documented by Vosoughi et al.
- Calibration Source: Vosoughi et al. (2018, Figure 3): median credulous user retweeted within 2 hops of exposure with sharing probability 0.6–0.9; agent's spread_eagerness calibrated to produce comparable per-round propagation.
- Falsification Conditions: If this agent's spread rate (fraction of rounds with action="spread") falls below 50% when env_belief > 0.5, the eagerness mechanism is underfiring. If the agent produces "ignore" when its belief exceeds 0.6, the spread gate is not sensitive enough.
- Alternative Theories: Echo chambers (Sunstein 2001), motivated reasoning (Kunda 1990), source credibility neglect (Hovland & Weiss 1951).

## Design Purpose and Activation Triggers

Purpose: Rapidly adopt environmental rumor beliefs and spread them with amplified intensity, serving as an uncritical propagation node in the rumor network.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `env_belief` available from information environment
- `distortion` available from information environment

Missing-Signal Policy: If `env_belief` is unavailable or NaN, agent retains current `my_belief` unchanged and emits ignore. If `distortion` is unavailable, treat as 0.

Activation Triggers:
- Belief above spread threshold (my_belief > 0.2 after update): SPREAD with computed intensity
- Belief below spread threshold (my_belief <= 0.2 after update): IGNORE (insufficient conviction)
- `<Default>`: ignore

Deactivation Conditions:
- If env_belief drops to 0 for 5 consecutive ticks, agent's my_belief decays toward 0 and spreading ceases.
- If agent has spread for 50 consecutive rounds without belief increase, enthusiasm fatigue sets in (spread_eagerness halved).

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                   | Mechanism                                            |
|------------------------------|-----------------------------------------------------|------------------------------------------------------|
| High environmental belief    | Rapidly increases own belief and spread intensity    | Credulity drives fast convergence to env_belief      |
| Low environmental belief     | Remains relatively inactive, emitting ignore actions | Threshold gate prevents spreading weak signals       |
| High distortion environment  | Increases spread intensity via amplification factor  | Distortion_amplification scales emotional component  |

Environmental Dependencies: Requires `env_belief` (current environmental rumor belief level, float [0,1]) and `distortion` (current rumor distortion level, float [0,1]) from the information environment coordinator. No peer-level individual signals required beyond these aggregate broadcasts.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                                  |
|----------------------|-----------------------------|---------------|------------------------|--------------------------------------------------------|
| `env_belief`         | environment / coordinator   | `float`       | yes                    | Current environmental rumor belief level [0,1]         |
| `distortion`         | environment / coordinator   | `float`       | yes                    | Current rumor distortion level [0,1]                   |
| `my_belief`          | agent's own persisted state | `float`       | yes                    | Populated on first call by §3.6.4 init (value: 0.3)   |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail                           |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_gullible_spreader`                |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                        |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit    | Required? | Meaning                                          |
|-------------|--------|---------------------------------|---------|-----------|--------------------------------------------------|
| `action`    | enum   | `{"spread", "ignore"}`          | —       | yes       | Social action selected this round                |
| `intensity` | float  | [0.0, 1.0]                      | unitless| yes       | Strength of spread action (0 if ignore)          |
| `reasoning` | string | 1–3 sentences                   | —       | yes       | Audit trail explaining belief state and decision |

##### Content Constraints

- **Required fields**: `action`, `intensity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `intensity` MUST be clamped to [0.0, 1.0] before emission. If computed intensity exceeds 1.0, clamp to 1.0.
- **Units and sign conventions**: `intensity` is a dimensionless strength measure; 0 = no propagation effect, 1 = maximum propagation force.
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining belief update and spread decision)...</analysis>
<decision>{"action": "<spread|ignore>", "intensity": <float>, "reasoning": "<audit-trail explanation>"}</decision>
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

| Signal        | Type       | Memory Window | Rationale                                                           |
|---------------|------------|---------------|---------------------------------------------------------------------|
| `env_belief`  | Continuous | 1 tick        | Primary input for belief update — represents current rumor strength |
| `distortion`  | Continuous | 1 tick        | Modulates spread intensity via amplification factor                 |

Does NOT use: truth value of the rumor, source credibility indicators, correction signals, peer-level individual beliefs, or historical belief trajectories. The agent deliberately ignores accuracy-relevant signals to model pure credulity.

#### Core Behavioral Mechanism

1. **Read** `env_belief` from environment and `my_belief` from state. **Compute** belief gap: `gap = env_belief - my_belief`. No state write. *(Implementation convenience — signal acquisition)*

2. **Read** `credulity` parameter and computed `gap`. **Compute** belief update: `new_belief = my_belief + credulity * gap`. Clamp to [0, 1]. **Write** `my_belief = new_belief`. *(Theory: Credulous adoption — agent converges rapidly toward environmental consensus without critical evaluation [Allport & Postman 1947])*

3. **Read** updated `my_belief`. **Compute** action decision: if `my_belief > 0.2`, set `action = "spread"`; otherwise `action = "ignore"`. No state write. *(Theory: Minimum belief threshold before sharing — even credulous users need some conviction [Vosoughi et al. 2018])*

4. **Read** `my_belief`, `spread_eagerness`, `distortion_amplification` parameters, and `distortion` signal. **Compute** `raw_intensity = my_belief * spread_eagerness * (1 + distortion_amplification * distortion)`. No state write. *(Theory: Spread intensity proportional to belief strength and emotional amplification from distortion [Allport & Postman 1947])*

5. **Read** `raw_intensity`. **Compute** `clamped_intensity = min(1.0, max(0.0, raw_intensity))`. If `action = "ignore"`, set `clamped_intensity = 0.0`. No state write. *(Implementation convenience — range clamping)*

6. **Read** computed `action` and `clamped_intensity`. **Write** decision object: `{action, intensity, reasoning}`. No additional state write (belief was already updated in step 2). *(Theory: Immediate transmission without delay or reconsideration [Vosoughi et al. 2018])*

#### Action Space

| Aspect                | Specification                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Action types allowed  | `spread`, `ignore`                                                                               |
| Action parameter rule | `intensity` in [0.0, 1.0]: strength of rumor propagation into the environment                    |
| Sizing rule           | `intensity = min(1.0, my_belief * spread_eagerness * (1 + distortion_amplification * distortion))`|
| Action lifetime       | Immediate effect on environment belief; single-round impact                                      |
| Revision policy       | No revision — once spread action is emitted, it cannot be retracted within same round            |
| State constraint      | `my_belief` bounded in [0.0, 1.0]                                                               |
| Resource cap          | None — agent can spread every round without depletion                                            |
| Exit rule             | None — agent participates indefinitely                                                           |

#### Mathematical Model

**Decision output**: `action` in {spread, ignore} and `intensity` in [0.0, 1.0].

**Decision logic formalization**:

```
# Belief update (pre-decision):
my_belief = clamp(my_belief + credulity * (env_belief - my_belief), 0, 1)

# Action decision:
IF my_belief > 0.2:
    action = "spread"
    intensity = clamp(my_belief * spread_eagerness * (1 + distortion_amplification * distortion), 0, 1)
ELSE:
    action = "ignore"
    intensity = 0.0
```

**State variables**:

| Variable    | Type  | Initial Value | Update Phase |
|-------------|-------|---------------|--------------|
| `my_belief` | float | 0.3           | pre-decide   |

**State evolution**: `my_belief` is updated BEFORE the action decision (pre-decide phase):
- `my_belief = clamp(my_belief + credulity * (env_belief - my_belief), 0, 1)`

This means the agent first absorbs environmental influence, then decides whether and how strongly to spread.

**Determinism contract**: Fully deterministic given identical inputs and state. No stochastic components.

**Parameter symbol table**:

| Symbol                      | Meaning                                           | Default Value | Source                    |
|-----------------------------|---------------------------------------------------|---------------|---------------------------|
| `credulity`                 | Rate of belief adoption from environment          | 0.8           | Buckner (1965)            |
| `spread_eagerness`          | Multiplier on spread intensity                    | 0.9           | Vosoughi et al. (2018)    |
| `distortion_amplification`  | How much distortion boosts spread intensity       | 0.3           | Allport & Postman (1947)  |
| `my_belief`                 | Agent's current belief in the rumor (state)       | 0.3           | Initial condition         |
| `env_belief`                | Environmental rumor belief level (signal)         | —             | From coordinator          |
| `distortion`                | Environmental distortion level (signal)           | —             | From coordinator          |

#### Behavioral Properties

- **Time horizon**: Short — reacts immediately to current environmental belief and spreads within the same round.
- **Risk tolerance**: High — spreads with high intensity without concern for accuracy or reputational consequences.
- **Information asymmetry**: None — has no privileged access to truth; operates solely on environmental belief signals.
- **Psychological profile**: Embodies credulity (uncritical belief adoption), eagerness to share (social participation motive), and emotional amplification of distorted content. Represents the "useful idiot" archetype in misinformation propagation (Allport & Postman 1947; Vosoughi et al. 2018).

## Parameters

| Parameter                    | Type    | Default | Valid Range  | Sensitivity | Description                                                    | Impact                                                | Source                    |
|------------------------------|---------|---------|--------------|-------------|----------------------------------------------------------------|-------------------------------------------------------|---------------------------|
| `credulity`                  | float   | 0.8     | [0.0, 1.0]   | high        | Rate at which agent adopts environmental belief                | Higher -> faster convergence to env_belief             | Buckner (1965, Table 3)   |
| `spread_eagerness`           | float   | 0.9     | [0.1, 1.5]   | high        | Multiplier on spread intensity calculation                     | Higher -> stronger propagation force per round         | Vosoughi et al. (2018)    |
| `distortion_amplification`   | float   | 0.3     | [0.0, 1.0]   | medium      | How much distortion boosts spread intensity                    | Higher -> more intense spreading in distorted environments | Allport & Postman (1947)  |
| `initial_belief`             | float   | 0.3     | [0.0, 1.0]   | low         | Starting belief level at simulation initialization             | Higher -> agent starts spreading sooner                | Standardised              |
| `spread_threshold`           | float   | 0.2     | [0.0, 0.8]   | medium      | Minimum belief level required before spreading                 | Higher -> agent needs more conviction before acting    | Standardised              |

## Worked Numerical Examples

### Case 1 — Spread (high environmental belief drives rapid adoption)

```
System state:
  env_belief = 0.7
  distortion = 0.4
  my_belief = 0.3
  credulity = 0.8
  spread_eagerness = 0.9
  distortion_amplification = 0.3

Calculation:
  gap = 0.7 - 0.3 = 0.4
  belief_update = 0.3 + 0.8 * 0.4 = 0.3 + 0.32 = 0.62
  my_belief (new) = clamp(0.62, 0, 1) = 0.62
  my_belief (0.62) > 0.2 → action = "spread"
  raw_intensity = 0.62 * 0.9 * (1 + 0.3 * 0.4) = 0.62 * 0.9 * 1.12 = 0.6249
  clamped_intensity = min(1.0, 0.6249) = 0.625

Decision: action = "spread", intensity = 0.625
State update: my_belief: 0.3 → 0.62
```

### Case 2 — Spread (belief already high, intensity near maximum)

```
System state:
  env_belief = 0.9
  distortion = 0.6
  my_belief = 0.8
  credulity = 0.8
  spread_eagerness = 0.9
  distortion_amplification = 0.3

Calculation:
  gap = 0.9 - 0.8 = 0.1
  belief_update = 0.8 + 0.8 * 0.1 = 0.8 + 0.08 = 0.88
  my_belief (new) = clamp(0.88, 0, 1) = 0.88
  my_belief (0.88) > 0.2 → action = "spread"
  raw_intensity = 0.88 * 0.9 * (1 + 0.3 * 0.6) = 0.88 * 0.9 * 1.18 = 0.9346
  clamped_intensity = min(1.0, 0.9346) = 0.935

Decision: action = "spread", intensity = 0.935
State update: my_belief: 0.8 → 0.88
```

### Case 3 — Ignore (low environmental belief, insufficient conviction)

```
System state:
  env_belief = 0.1
  distortion = 0.2
  my_belief = 0.15
  credulity = 0.8
  spread_eagerness = 0.9
  distortion_amplification = 0.3

Calculation:
  gap = 0.1 - 0.15 = -0.05
  belief_update = 0.15 + 0.8 * (-0.05) = 0.15 - 0.04 = 0.11
  my_belief (new) = clamp(0.11, 0, 1) = 0.11
  my_belief (0.11) <= 0.2 → action = "ignore"
  intensity = 0.0

Decision: action = "ignore", intensity = 0.0
State update: my_belief: 0.15 → 0.11
```

### Case 4 — Spread (moderate belief with high distortion amplification)

```
System state:
  env_belief = 0.5
  distortion = 0.8
  my_belief = 0.4
  credulity = 0.8
  spread_eagerness = 0.9
  distortion_amplification = 0.3

Calculation:
  gap = 0.5 - 0.4 = 0.1
  belief_update = 0.4 + 0.8 * 0.1 = 0.4 + 0.08 = 0.48
  my_belief (new) = clamp(0.48, 0, 1) = 0.48
  my_belief (0.48) > 0.2 → action = "spread"
  raw_intensity = 0.48 * 0.9 * (1 + 0.3 * 0.8) = 0.48 * 0.9 * 1.24 = 0.5357
  clamped_intensity = min(1.0, 0.5357) = 0.536

Decision: action = "spread", intensity = 0.536
State update: my_belief: 0.4 → 0.48
```

### Edge Case — Belief at boundary with env_belief = 0

```
System state:
  env_belief = 0.0
  distortion = 0.1
  my_belief = 0.25
  credulity = 0.8
  spread_eagerness = 0.9
  distortion_amplification = 0.3

Calculation:
  gap = 0.0 - 0.25 = -0.25
  belief_update = 0.25 + 0.8 * (-0.25) = 0.25 - 0.20 = 0.05
  my_belief (new) = clamp(0.05, 0, 1) = 0.05
  my_belief (0.05) <= 0.2 → action = "ignore"
  intensity = 0.0

Decision: action = "ignore", intensity = 0.0
State update: my_belief: 0.25 → 0.05
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `credulity` <- Buckner (1965, Table 3): credulous subjects adopted 80–90% of message content; 0.8 maps to midpoint
- `spread_eagerness` <- Vosoughi et al. (2018, Figure 3): median sharing probability 0.6–0.9 for false news; 0.9 targets upper range
- `distortion_amplification` <- Allport & Postman (1947): emotional intensity amplification in serial chains measured at 20–40%

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given env_belief=0.7, my_belief=0.3, agent MUST update belief to 0.62 and emit action="spread" with intensity~0.625
- Given env_belief=0.1, my_belief=0.15, agent MUST update belief to 0.11 and emit action="ignore" with intensity=0
- Given env_belief=0.9, my_belief=0.8, agent MUST emit action="spread" with intensity>0.9
- Agent MUST always converge belief toward env_belief (never diverge)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent's my_belief moves AWAY from env_belief after update THEN credulity mechanism is inverted
- IF agent emits "spread" with intensity > 1.0 THEN clamping is broken
- IF agent emits "spread" when my_belief <= 0.2 THEN threshold gate is broken
- IF agent emits intensity > 0 with action = "ignore" THEN action-intensity consistency is violated

### Ablation Hooks

| Ablation name              | Setting                          | Hypothesis tested                                   | Expected direction | Metric                          |
|----------------------------|----------------------------------|-----------------------------------------------------|--------------------|----------------------------------|
| `low_credulity`            | `credulity = 0.2`               | Lower credulity slows belief adoption                | decrease           | Belief convergence rate         |
| `no_distortion_amp`        | `distortion_amplification = 0.0`| Removing distortion boost reduces spread intensity   | decrease           | Mean intensity when spreading   |
| `high_eagerness`           | `spread_eagerness = 1.5`        | Higher eagerness increases mean intensity            | increase           | Mean intensity when spreading   |
| `high_threshold`           | `spread_threshold = 0.6`        | Higher threshold reduces spread frequency            | decrease           | Fraction of rounds with spread  |

## Academic References

| #  | Citation                                                                                                                                                         | Notes                                    |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1  | Allport, G. W., & Postman, L. (1947). The Psychology of Rumor. Henry Holt and Company.                                                                           | Primary theory — rumor transmission      |
| 2  | Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. Science, 359(6380), 1146–1151. https://doi.org/10.1126/science.aap9559       | Virality of false news                   |
| 3  | Buckner, H. T. (1965). A theory of rumor transmission. Public Opinion Quarterly, 29(1), 54–70. https://doi.org/10.1086/267297                                    | Credulous receiver classification        |
| 4  | Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. Journal of Political Economy, 100(5), 992–1026. https://doi.org/10.1086/261849 | Information cascade theory               |
| 5  | Pennycook, G., & Rand, D. G. (2019). Lazy, not biased: Susceptibility to partisan fake news is better explained by lack of reasoning than by motivated reasoning. Cognition, 188, 39–50. https://doi.org/10.1016/j.cognition.2018.06.011 | Cognitive laziness in sharing            |
| 6  | Sunstein, C. R. (2001). Echo Chambers: Bush v. Gore, Impeachment, and Beyond. Princeton University Press. ISBN: 978-0691095646                                   | Echo chamber amplification               |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
