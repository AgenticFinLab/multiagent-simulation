# Distorting rumor relayer

## Summary

| Field                 | Content                                                                                                   |
|-----------------------|-----------------------------------------------------------------------------------------------------------|
| Archetype             | Distorting rumor relayer                                                                                   |
| Theory Family         | Social Psychology — Rumor Transmission and Serial Distortion                                               |
| Behavioral Tendency   | **Diverging** — distorts information through sharpening and leveling during relay, degrading signal quality |
| Time Horizon          | short                                                                                                      |
| Risk Tolerance        | high                                                                                                       |
| Information Asymmetry | none                                                                                                       |
| Determinism           | deterministic                                                                                              |

## Definition and Goals

This agent models a participant who relays rumors while systematically distorting them through cognitive processes of sharpening (emphasizing dramatic elements) and leveling (dropping qualifying details). Real-world counterparts include gossip chain participants who embellish stories, social media users who add sensational framing to shared content, and market participants who amplify the emotional valence of information as they pass it along. These behaviors are documented in Allport & Postman (1947) as fundamental mechanisms of serial reproduction and in Bartlett (1932) as systematic memory distortion patterns.

The decision goal is to produce a social action (spread or ignore) with computed intensity, while the act of spreading itself introduces distortion into the system. The belief update includes sharpening and leveling: `my_belief += credulity * (env_belief - my_belief) + sharpening_factor * distortion`. The spread intensity is: `my_belief * relay_eagerness`. The agent participates in rumor propagation while increasing system-level distortion.

This agent acts as a destabilizing force by degrading information quality during transmission — its relay activity increases the distortion level in the environment, which in turn amplifies the behavior of other credulous agents. Its characteristic action is enthusiastic retransmission with systematic amplification of sensational elements. Non-goals: (1) the agent MUST NOT attempt to verify or correct distorted information before relaying; (2) the agent MUST NOT preserve the original fidelity of the message — its cognitive processes inherently modify content during relay.

## Theoretical Foundation

**Leveling and Sharpening in Serial Transmission (Allport & Postman 1947)**:
- Theory / Study: The Psychology of Rumor — Leveling, Sharpening, and Assimilation
- Citation: Allport, G. W., & Postman, L. (1947). The Psychology of Rumor. Henry Holt and Company. (Reprinted: Russell & Russell, 1965)
- Core Insight: During serial transmission, rumors undergo three systematic transformations: leveling (loss of detail, simplification), sharpening (selective emphasis on dramatic or personally relevant details), and assimilation (distortion toward cognitive schemas). The net effect is that retransmitted content becomes shorter, more pointed, and more extreme than the original.
- Mathematical Formulation: `distorted_belief = my_belief + sharpening_factor * distortion - leveling_factor * (my_belief - 0.5)^2`
- Empirical Evidence: Allport & Postman (1947) found in 40 serial reproduction chains (6–8 links each) that 70% of detail was lost (leveling) while emotional/dramatic elements were preserved or amplified (sharpening increased salience ratings by 40–60% for dramatic details). Bartlett (1932) replicated across cultural contexts with similar distortion rates.
- Relevance to This Agent: The agent instantiates the serial distortion mechanism — when it relays, it adds sharpening (amplifying dramatic elements captured in the distortion signal) while the leveling process simplifies and biases the belief.
- Calibration Source: Allport & Postman (1947, Chapter 5): 5–6 reproductions produced 70% detail loss (leveling_factor~0.3 per step) and 40–60% salience amplification for dramatic elements (sharpening_factor~0.4).
- Falsification Conditions: If this agent relays without contributing to system distortion (its spreading does not increase distortion metric over 10 rounds), the sharpening mechanism is non-functional. If the agent's belief becomes more moderate over time (converging to 0.5) when it should sharpen away from center, leveling is dominating inappropriately.
- Alternative Theories: Chinese whispers as random noise (not systematic), social amplification of risk (Kasperson et al. 1988), frame alignment (Snow & Benford 1988).

**Reconstructive Memory and Rumor Distortion (Bartlett 1932)**:
- Theory / Study: Remembering: A Study in Experimental and Social Psychology
- Citation: Bartlett, F. C. (1932). Remembering: A Study in Experimental and Social Psychology. Cambridge University Press. (Reprinted 1995) https://doi.org/10.1017/CBO9780511759185
- Core Insight: Memory is not a faithful recording but a reconstructive process guided by schemas. When people retell stories, they systematically distort content to fit their pre-existing cognitive frameworks, introducing errors that compound through transmission chains. This makes serial reproduction inherently distorting.
- Mathematical Formulation: `schema_distortion = sharpening_factor * (current_distortion) [positive feedback — distortion breeds more distortion]`
- Empirical Evidence: Bartlett (1932) tested serial reproduction with "War of the Ghosts" narrative across 10+ transmission steps (N=20 chains). Content accuracy dropped from 100% to ~30% after 6 reproductions, while narrative coherence (schema conformity) increased. Systematic errors compounded at approximately 15–25% per transmission.
- Relevance to This Agent: The agent's belief update incorporates the schema-driven sharpening mechanism — existing distortion amplifies belief extremity, reflecting how pre-existing frameworks bias reconstructive relay.
- Calibration Source: Bartlett (1932, Chapter 5): 15–25% error compounding per relay step; agent's sharpening_factor=0.4 produces comparable distortion accumulation over multi-agent chains.
- Falsification Conditions: If this agent's output belief consistently equals input env_belief without any sharpening-driven divergence, the schema distortion mechanism is not active.
- Alternative Theories: Signal detection theory noise (Green & Swets 1966), rational inattention (Sims 2003).

## Design Purpose and Activation Triggers

Purpose: Relay rumors while introducing systematic distortion through sharpening and leveling, degrading information quality across transmission chains.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `env_belief` available from information environment
- `distortion` available from information environment

Missing-Signal Policy: If `env_belief` is unavailable or NaN, agent retains current `my_belief` unchanged and emits ignore. If `distortion` is unavailable, treat as 0 (no sharpening boost).

Activation Triggers:
- Belief above relay threshold (my_belief > 0.25 after update): SPREAD with computed intensity
- Belief below relay threshold (my_belief <= 0.25 after update): IGNORE
- `<Default>`: ignore

Deactivation Conditions:
- If env_belief drops to 0 for 5 consecutive ticks, agent ceases spreading and belief decays.
- If my_belief saturates at 1.0 for 10 consecutive rounds, sharpening can no longer increase it — agent continues spreading at maximum intensity but without further distortion contribution.

Behavioral Adaptation by Condition:
| Condition                      | Behavioral change                                           | Mechanism                                                     |
|--------------------------------|-------------------------------------------------------------|---------------------------------------------------------------|
| High distortion environment    | Sharpening pushes belief higher, increasing intensity       | Distortion-driven sharpening amplifies belief extremity       |
| Low environmental belief       | Agent stays below threshold, remains inactive               | Threshold gate prevents relay of very weak signals            |
| Belief near 1.0 saturation    | Intensity maximized but sharpening effect diminishes        | Ceiling effect — clamp prevents belief from exceeding 1.0     |

Environmental Dependencies: Requires `env_belief` (current environmental rumor belief level, float [0,1]) and `distortion` (current rumor distortion level, float [0,1]) from the information environment coordinator.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                                   |
|----------------------|-----------------------------|---------------|------------------------|---------------------------------------------------------|
| `env_belief`         | environment / coordinator   | `float`       | yes                    | Current environmental rumor belief level [0,1]          |
| `distortion`         | environment / coordinator   | `float`       | yes                    | Current rumor distortion level [0,1]                    |
| `my_belief`          | agent's own persisted state | `float`       | yes                    | Populated on first call by §3.6.4 init (value: 0.3)    |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail                            |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_distorting_relayer`                |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                         |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit    | Required? | Meaning                                            |
|-------------|--------|---------------------------------|---------|-----------|----------------------------------------------------|
| `action`    | enum   | `{"spread", "ignore"}`          | —       | yes       | Social action selected this round                  |
| `intensity` | float  | [0.0, 1.0]                      | unitless| yes       | Strength of spread/relay action (0 if ignore)      |
| `reasoning` | string | 1–3 sentences                   | —       | yes       | Audit trail explaining distortion and relay logic  |

##### Content Constraints

- **Required fields**: `action`, `intensity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `intensity` MUST be clamped to [0.0, 1.0] before emission.
- **Units and sign conventions**: `intensity` is dimensionless; 0 = no propagation, 1 = maximum relay force.
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining distortion effects and relay decision)...</analysis>
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

| Signal        | Type       | Memory Window | Rationale                                                              |
|---------------|------------|---------------|------------------------------------------------------------------------|
| `env_belief`  | Continuous | 1 tick        | Primary input for belief adoption and convergence                      |
| `distortion`  | Continuous | 1 tick        | Feeds sharpening mechanism — higher distortion amplifies belief update |

Does NOT use: truth value, source credibility, correction signals, peer individual beliefs, or message content fidelity measures. The agent deliberately ignores quality indicators to model pure serial distortion processes.

#### Core Behavioral Mechanism

1. **Read** `env_belief` and `distortion` from environment, `my_belief` from state. **Compute** base adoption gap: `gap = env_belief - my_belief`. No state write. *(Implementation convenience — signal acquisition)*

2. **Read** `credulity`, `sharpening_factor`, `leveling_factor` parameters and `distortion` signal. **Compute** distorted belief update: `new_belief = my_belief + credulity * gap + sharpening_factor * distortion - leveling_factor * (my_belief - 0.5)^2`. Clamp to [0, 1]. The sharpening term adds distortion-driven amplification; the leveling term provides mild regression toward 0.5 (detail loss simplifies extreme beliefs slightly). **Write** `my_belief = new_belief`. *(Theory: Leveling and sharpening in serial reproduction [Allport & Postman 1947; Bartlett 1932])*

3. **Read** updated `my_belief`. **Compute** action decision: if `my_belief > 0.25`, set `action = "spread"`; otherwise `action = "ignore"`. No state write. *(Theory: Minimum conviction for relay — even distorting relayers need some belief to motivate transmission [Buckner 1965])*

4. **Read** `my_belief`, `relay_eagerness` parameter. **Compute** `raw_intensity = my_belief * relay_eagerness`. No state write. *(Theory: Relay intensity proportional to current belief strength [Allport & Postman 1947])*

5. **Read** `raw_intensity`. **Compute** `clamped_intensity = min(1.0, max(0.0, raw_intensity))`. If `action = "ignore"`, set `clamped_intensity = 0.0`. No state write. *(Implementation convenience — range clamping)*

6. **Read** computed `action` and `clamped_intensity`. **Write** decision object. No additional state write. *(Theory: Immediate relay without reflection — serial distortion is automatic [Bartlett 1932])*

#### Action Space

| Aspect                | Specification                                                                     |
|-----------------------|-----------------------------------------------------------------------------------|
| Action types allowed  | `spread`, `ignore`                                                                |
| Action parameter rule | `intensity` in [0.0, 1.0]: strength of relay into the environment                 |
| Sizing rule           | `intensity = min(1.0, my_belief * relay_eagerness)`                               |
| Action lifetime       | Immediate single-round effect; contributes to environment distortion accumulation  |
| Revision policy       | No revision — relay is immediate and irrevocable within same round                |
| State constraint      | `my_belief` bounded in [0.0, 1.0]                                                |
| Resource cap          | None — agent can relay every round                                                |
| Exit rule             | None — participates indefinitely                                                  |

#### Mathematical Model

**Decision output**: `action` in {spread, ignore} and `intensity` in [0.0, 1.0].

**Decision logic formalization**:

```
# Belief update with sharpening and leveling (pre-decision):
gap = env_belief - my_belief
my_belief = clamp(my_belief + credulity * gap + sharpening_factor * distortion - leveling_factor * (my_belief - 0.5)^2, 0, 1)

# Action decision:
IF my_belief > 0.25:
    action = "spread"
    intensity = clamp(my_belief * relay_eagerness, 0, 1)
ELSE:
    action = "ignore"
    intensity = 0.0
```

**State variables**:

| Variable    | Type  | Initial Value | Update Phase |
|-------------|-------|---------------|--------------|
| `my_belief` | float | 0.3           | pre-decide   |

**State evolution**: `my_belief` updated pre-decide:
- `my_belief = clamp(my_belief + credulity*(env_belief - my_belief) + sharpening_factor*distortion - leveling_factor*(my_belief - 0.5)^2, 0, 1)`

**Determinism contract**: Fully deterministic given identical inputs and state. No stochastic components.

**Parameter symbol table**:

| Symbol             | Meaning                                                  | Default Value | Source                   |
|--------------------|----------------------------------------------------------|---------------|--------------------------|
| `credulity`        | Base rate of environmental belief adoption               | 0.6           | Buckner (1965)           |
| `relay_eagerness`  | Multiplier converting belief to spread intensity         | 0.8           | Allport & Postman (1947) |
| `sharpening_factor`| Rate at which distortion amplifies belief                | 0.4           | Allport & Postman (1947) |
| `leveling_factor`  | Rate of detail-loss regression toward neutral            | 0.1           | Bartlett (1932)          |
| `my_belief`        | Agent's current belief in the rumor (state)              | 0.3           | Initial condition        |
| `env_belief`       | Environmental rumor belief level (signal)                | —             | From coordinator         |
| `distortion`       | Environmental distortion level (signal)                  | —             | From coordinator         |

#### Behavioral Properties

- **Time horizon**: Short — processes and relays within single rounds; no multi-period memory or planning.
- **Risk tolerance**: High — relays without concern for accuracy, reputation, or social consequences.
- **Information asymmetry**: None — operates on publicly broadcast environmental signals only.
- **Psychological profile**: Embodies serial distortion through sharpening and leveling (Allport & Postman 1947), reconstructive memory errors (Bartlett 1932), and schema-driven information processing. Represents the "telephone game" distortion node in rumor chains.

## Parameters

| Parameter          | Type    | Default | Valid Range  | Sensitivity | Description                                                       | Impact                                                  | Source                   |
|--------------------|---------|---------|--------------|-------------|-------------------------------------------------------------------|---------------------------------------------------------|--------------------------|
| `credulity`        | float   | 0.6     | [0.0, 1.0]   | high        | Base rate of belief adoption from environment                     | Higher -> faster convergence to environmental belief    | Buckner (1965, Table 3)  |
| `relay_eagerness`  | float   | 0.8     | [0.1, 1.5]   | high        | Multiplier converting belief level to spread intensity            | Higher -> stronger propagation force per relay          | Allport & Postman (1947) |
| `sharpening_factor`| float   | 0.4     | [0.0, 1.0]   | high        | Rate at which distortion amplifies belief extremity               | Higher -> more belief amplification from distorted env  | Allport & Postman (1947) |
| `leveling_factor`  | float   | 0.1     | [0.0, 0.5]   | medium      | Rate of belief regression toward neutral (0.5)                    | Higher -> more moderate beliefs, less extreme spreading | Bartlett (1932)          |
| `relay_threshold`  | float   | 0.25    | [0.0, 0.8]   | medium      | Minimum belief level to trigger relay action                      | Higher -> fewer relay events, only strong beliefs       | Standardised             |

## Worked Numerical Examples

### Case 1 — Spread with sharpening boost

```
System state:
  env_belief = 0.6
  distortion = 0.5
  my_belief = 0.3
  credulity = 0.6
  relay_eagerness = 0.8
  sharpening_factor = 0.4
  leveling_factor = 0.1

Calculation:
  gap = 0.6 - 0.3 = 0.3
  sharpening_boost = 0.4 * 0.5 = 0.2
  leveling_drag = 0.1 * (0.3 - 0.5)^2 = 0.1 * 0.04 = 0.004
  new_belief = 0.3 + 0.6*0.3 + 0.2 - 0.004 = 0.3 + 0.18 + 0.2 - 0.004 = 0.676
  my_belief = clamp(0.676, 0, 1) = 0.676
  my_belief (0.676) > 0.25 → action = "spread"
  raw_intensity = 0.676 * 0.8 = 0.541
  clamped_intensity = min(1.0, 0.541) = 0.541

Decision: action = "spread", intensity = 0.541
State update: my_belief: 0.3 → 0.676
```

### Case 2 — Spread with moderate distortion

```
System state:
  env_belief = 0.5
  distortion = 0.2
  my_belief = 0.5
  credulity = 0.6
  relay_eagerness = 0.8
  sharpening_factor = 0.4
  leveling_factor = 0.1

Calculation:
  gap = 0.5 - 0.5 = 0.0
  sharpening_boost = 0.4 * 0.2 = 0.08
  leveling_drag = 0.1 * (0.5 - 0.5)^2 = 0.1 * 0 = 0.0
  new_belief = 0.5 + 0.6*0.0 + 0.08 - 0.0 = 0.58
  my_belief = clamp(0.58, 0, 1) = 0.58
  my_belief (0.58) > 0.25 → action = "spread"
  raw_intensity = 0.58 * 0.8 = 0.464
  clamped_intensity = min(1.0, 0.464) = 0.464

Decision: action = "spread", intensity = 0.464
State update: my_belief: 0.5 → 0.58
```

### Case 3 — Ignore (low belief after leveling dominates)

```
System state:
  env_belief = 0.15
  distortion = 0.05
  my_belief = 0.2
  credulity = 0.6
  relay_eagerness = 0.8
  sharpening_factor = 0.4
  leveling_factor = 0.1

Calculation:
  gap = 0.15 - 0.2 = -0.05
  sharpening_boost = 0.4 * 0.05 = 0.02
  leveling_drag = 0.1 * (0.2 - 0.5)^2 = 0.1 * 0.09 = 0.009
  new_belief = 0.2 + 0.6*(-0.05) + 0.02 - 0.009 = 0.2 - 0.03 + 0.02 - 0.009 = 0.181
  my_belief = clamp(0.181, 0, 1) = 0.181
  my_belief (0.181) <= 0.25 → action = "ignore"
  intensity = 0.0

Decision: action = "ignore", intensity = 0.0
State update: my_belief: 0.2 → 0.181
```

### Case 4 — Belief saturation near 1.0

```
System state:
  env_belief = 0.9
  distortion = 0.8
  my_belief = 0.85
  credulity = 0.6
  relay_eagerness = 0.8
  sharpening_factor = 0.4
  leveling_factor = 0.1

Calculation:
  gap = 0.9 - 0.85 = 0.05
  sharpening_boost = 0.4 * 0.8 = 0.32
  leveling_drag = 0.1 * (0.85 - 0.5)^2 = 0.1 * 0.1225 = 0.01225
  new_belief = 0.85 + 0.6*0.05 + 0.32 - 0.01225 = 0.85 + 0.03 + 0.32 - 0.01225 = 1.18775
  my_belief = clamp(1.18775, 0, 1) = 1.0  ← CLAMPED
  my_belief (1.0) > 0.25 → action = "spread"
  raw_intensity = 1.0 * 0.8 = 0.8
  clamped_intensity = min(1.0, 0.8) = 0.8

Decision: action = "spread", intensity = 0.8
State update: my_belief: 0.85 → 1.0
```

### Edge Case — Zero distortion, belief near threshold

```
System state:
  env_belief = 0.25
  distortion = 0.0
  my_belief = 0.28
  credulity = 0.6
  relay_eagerness = 0.8
  sharpening_factor = 0.4
  leveling_factor = 0.1

Calculation:
  gap = 0.25 - 0.28 = -0.03
  sharpening_boost = 0.4 * 0.0 = 0.0
  leveling_drag = 0.1 * (0.28 - 0.5)^2 = 0.1 * 0.0484 = 0.00484
  new_belief = 0.28 + 0.6*(-0.03) + 0.0 - 0.00484 = 0.28 - 0.018 + 0 - 0.00484 = 0.2572
  my_belief = clamp(0.2572, 0, 1) = 0.257
  my_belief (0.257) > 0.25 → action = "spread" (barely above threshold)
  raw_intensity = 0.257 * 0.8 = 0.206
  clamped_intensity = min(1.0, 0.206) = 0.206

Decision: action = "spread", intensity = 0.206
State update: my_belief: 0.28 → 0.257
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `credulity` <- Buckner (1965, Table 3): moderate-credulous subjects adopted 50–70% of content; 0.6 is midpoint
- `sharpening_factor` <- Allport & Postman (1947, Chapter 5): dramatic element amplification 40–60% per step; 0.4 targets lower bound
- `leveling_factor` <- Bartlett (1932, Chapter 5): 15–25% detail loss per reproduction; 0.1 maps to mild per-round regression
- `relay_eagerness` <- Allport & Postman (1947): active relayers transmitted at 70–90% of maximum capacity

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given env_belief=0.6, distortion=0.5, my_belief=0.3, agent MUST update belief to ~0.676 and emit action="spread" with intensity~0.541
- Given env_belief=0.15, distortion=0.05, my_belief=0.2, agent MUST update belief to ~0.181 and emit action="ignore"
- Sharpening MUST increase belief when distortion is high (positive sharpening_factor * distortion term)
- Agent MUST never emit intensity > 1.0 or < 0.0

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent's belief remains constant when env_belief differs and distortion > 0 THEN update mechanism is broken
- IF agent emits intensity > 1.0 THEN clamping is broken
- IF agent emits "spread" when my_belief <= 0.25 THEN threshold gate is broken
- IF sharpening has no effect (removing sharpening_factor produces identical behavior) THEN sharpening is not wired

### Ablation Hooks

| Ablation name            | Setting                    | Hypothesis tested                                   | Expected direction | Metric                         |
|--------------------------|----------------------------|-----------------------------------------------------|--------------------|--------------------------------|
| `no_sharpening`          | `sharpening_factor = 0.0`  | Sharpening amplifies belief extremity               | decrease           | Mean belief level over time    |
| `no_leveling`            | `leveling_factor = 0.0`    | Leveling provides mild centering                    | increase           | Mean belief level over time    |
| `high_sharpening`        | `sharpening_factor = 0.8`  | More sharpening accelerates belief to saturation    | increase           | Time to reach my_belief > 0.9 |
| `low_eagerness`          | `relay_eagerness = 0.3`    | Lower eagerness reduces propagation intensity       | decrease           | Mean intensity when spreading  |

## Academic References

| #  | Citation                                                                                                                                             | Notes                                       |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| 1  | Allport, G. W., & Postman, L. (1947). The Psychology of Rumor. Henry Holt and Company.                                                               | Primary theory — leveling and sharpening    |
| 2  | Bartlett, F. C. (1932). Remembering: A Study in Experimental and Social Psychology. Cambridge University Press. https://doi.org/10.1017/CBO9780511759185 | Reconstructive memory distortion            |
| 3  | Buckner, H. T. (1965). A theory of rumor transmission. Public Opinion Quarterly, 29(1), 54–70. https://doi.org/10.1086/267297                        | Receiver type classification                |
| 4  | Kasperson, R. E., et al. (1988). The social amplification of risk: A conceptual framework. Risk Analysis, 8(2), 177–187. https://doi.org/10.1111/j.1539-6924.1988.tb01168.x | Social amplification mechanism              |
| 5  | Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. Science, 359(6380), 1146–1151. https://doi.org/10.1126/science.aap9559 | Empirical distortion in online transmission |
| 6  | Snow, D. A., & Benford, R. D. (1988). Ideology, frame resonance, and participant mobilization. International Social Movement Research, 1, 197–217.   | Frame alignment theory                      |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
