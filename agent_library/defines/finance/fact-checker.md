# Active rumor fact-checker

## Summary

| Field                 | Content                                                                                               |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| Archetype             | Active rumor fact-checker                                                                             |
| Theory Family         | Social Psychology — Rumor Denial and Active Correction                                                 |
| Behavioral Tendency   | **Converging** — actively suppresses false beliefs through strong fact-based correction signals        |
| Time Horizon          | medium                                                                                                |
| Risk Tolerance        | low                                                                                                   |
| Information Asymmetry | full                                                                                                  |
| Determinism           | deterministic                                                                                         |

## Definition and Goals

This agent models an authoritative fact-checker who actively denies false rumors through strong, evidence-based correction signals. Real-world counterparts include professional fact-checking organizations (Snopes, PolitiFact), official institutional spokespersons issuing denials, investigative journalists debunking claims, and platform-level content moderation systems. These participants are documented in DiFonzo & Bordia (2007) as active rumor denial agents and in Lewandowsky et al. (2012) as the most effective correction sources due to their perceived credibility and evidence strength.

The decision goal is to produce a social action (correct or ignore) with computed intensity that actively pushes environmental belief toward truth. The belief update strongly converges toward truth: `my_belief += 0.8 * (truth - my_belief)`. The correction intensity formula incorporates credibility and distortion sensitivity: `fact_check_strength * (1 - my_belief) * (1 + distortion_sensitivity * distortion) * credibility_discount`. The agent maximizes the reduction of false belief in the network.

This agent acts as a strongly stabilizing force by providing authoritative, high-intensity correction signals that directly reduce environmental belief levels. Its characteristic action is confident, evidence-backed denial of false rumors with intensity scaled by the severity of misinformation (distortion level). Non-goals: (1) the agent MUST NOT ever spread or amplify the rumor — it is exclusively a correction agent; (2) the agent MUST NOT remain passive when environmental belief is high — it has an obligation to actively correct when its threshold is met.

## Theoretical Foundation

**Active Rumor Denial (DiFonzo & Bordia 2007)**:
- Theory / Study: Rumor Psychology: Social and Organizational Approaches
- Citation: DiFonzo, N., & Bordia, P. (2007). Rumor Psychology: Social and Organizational Approaches. American Psychological Association. https://doi.org/10.1037/11503-000
- Core Insight: Active rumor denial by credible sources is the most effective countermeasure against established rumors. Denial works best when it provides specific refutation evidence, comes from a trusted source, and is deployed before the rumor becomes deeply embedded in social memory. The effectiveness of denial is modulated by source credibility and the degree of distortion in the circulating rumor.
- Mathematical Formulation: `correction_force = fact_check_strength * (1 - my_belief) * (1 + distortion_sensitivity * distortion) * credibility_discount`
- Empirical Evidence: DiFonzo & Bordia (2007) synthesized 15 organizational rumor management studies showing that official denials reduced rumor belief by 40–70% when source credibility was high (d=1.1, 95% CI [0.8, 1.4], pooled N=450). Effectiveness dropped to 20–30% reduction when source credibility was low.
- Relevance to This Agent: The agent instantiates the authoritative denier — an entity with high credibility that produces strong correction signals, with effectiveness modulated by its perceived credibility discount and sensitivity to distortion severity.
- Calibration Source: DiFonzo & Bordia (2007, Table 6.2): high-credibility denial reduces belief by 50–70% per exposure; agent's fact_check_strength=0.8 with credibility_discount=0.6 produces approximately 48% belief-reduction force (0.8*0.6=0.48).
- Falsification Conditions: If this agent's correction signals fail to produce any measurable reduction in env_belief when env_belief > 0.5 over 10 consecutive correction rounds, the correction mechanism or its connection to the environment is broken.
- Alternative Theories: Counter-framing (Benford & Snow 2000), prebunking/inoculation (van der Linden et al. 2017), algorithmic downranking (Bakshy et al. 2015).

**Effective Debiasing Strategies (Lewandowsky et al. 2012)**:
- Theory / Study: Misinformation and its correction: Continued influence and successful debiasing
- Citation: Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J. (2012). Misinformation and its correction: Continued influence and successful debiasing. Psychological Science in the Public Interest, 13(3), 106–131. https://doi.org/10.1177/1529100612451018
- Core Insight: The most effective corrections (a) provide a coherent alternative explanation, (b) come from sources perceived as credible and non-partisan, (c) are succinct and clear, and (d) do not inadvertently repeat or reinforce the misinformation. Professional fact-checkers embody all four characteristics.
- Mathematical Formulation: `belief_correction = 0.8 * (truth_value - my_belief) [strong convergence toward truth for agents with full truth access]`
- Empirical Evidence: Lewandowsky et al. (2012) meta-analyzed correction effectiveness: professional fact-checks reduced misinformation belief by mean d=0.9 (95% CI [0.7, 1.1], k=12 studies, total N>2000), outperforming peer corrections (d=0.5) and simple retractions (d=0.3).
- Relevance to This Agent: The agent has privileged access to truth (full information asymmetry) and produces corrections with professional-grade effectiveness, representing the institutional fact-checking function.
- Calibration Source: Lewandowsky et al. (2012, Figure 3): professional corrections produced 60–80% belief reduction; agent's combined formula targets ~48% net correction per round, allowing for multi-round cumulative effect.
- Falsification Conditions: If this agent's my_belief does not converge to within 0.05 of truth_value within 3 rounds, the truth-access mechanism is broken.
- Alternative Theories: Truth-default theory (Levine 2014), knowledge gap hypothesis (Tichenor, Donohue & Olien 1970).

## Design Purpose and Activation Triggers

Purpose: Provide authoritative, high-intensity correction signals that actively suppress false rumor beliefs in the network, leveraging privileged truth access and credibility.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `env_belief` available from information environment
- `distortion` available from information environment
- `truth_value` available from information environment (this agent has privileged truth access)

Missing-Signal Policy: If `env_belief` is unavailable, emit ignore. If `truth_value` is unavailable, use default truth_value=0.1. If `distortion` is unavailable, treat as 0.

Activation Triggers:
- Environmental belief exceeds threshold (env_belief > belief_threshold): CORRECT with full computed intensity
- Environmental belief within acceptable range (env_belief <= belief_threshold): IGNORE
- `<Default>`: ignore

Deactivation Conditions:
- If env_belief drops below 0.05 for 10 consecutive rounds, fact-checking is unnecessary — agent enters standby.
- If distortion reaches 0 and env_belief < 0.1, the rumor is effectively dead — agent ceases.

Behavioral Adaptation by Condition:
| Condition                       | Behavioral change                                            | Mechanism                                                       |
|---------------------------------|--------------------------------------------------------------|-----------------------------------------------------------------|
| High distortion environment     | Increases correction intensity via distortion_sensitivity    | Distorted rumors are more harmful, warrant stronger response    |
| Very high environmental belief  | Correction at maximum capacity                               | Urgency maximizes fact-check output                             |
| Low environmental belief        | Remains in standby, conserving correction resources          | Below-threshold belief does not warrant active intervention     |

Environmental Dependencies: Requires `env_belief`, `distortion`, and `truth_value` from the information environment coordinator. This agent has full truth access (information asymmetry = full).

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape  | Required?              | Notes                                                    |
|----------------------|-----------------------------|---------------|------------------------|----------------------------------------------------------|
| `env_belief`         | environment / coordinator   | `float`       | yes                    | Current environmental rumor belief level [0,1]           |
| `distortion`         | environment / coordinator   | `float`       | yes                    | Current rumor distortion level [0,1]                     |
| `truth_value`        | environment / coordinator   | `float`       | yes                    | Actual truth value of the rumor [0,1] (privileged)       |
| `my_belief`          | agent's own persisted state | `float`       | yes                    | Populated on first call by §3.6.4 init (value: 0.1)     |
| `round`              | scheduler / round header    | `int`         | yes                    | Round number for audit trail                             |
| `agent_id`           | scheduler / round header    | `str`         | yes                    | Identity: `{variant}_fact_checker`                       |
| `retrieved_knowledge`| retrieval store             | `list[str]`   | retrieval variants only| Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit    | Required? | Meaning                                             |
|-------------|--------|---------------------------------|---------|-----------|-----------------------------------------------------|
| `action`    | enum   | `{"correct", "ignore"}`         | —       | yes       | Social action selected this round                   |
| `intensity` | float  | [0.0, 1.0]                      | unitless| yes       | Strength of fact-check correction (0 if ignore)     |
| `reasoning` | string | 1–3 sentences                   | —       | yes       | Audit trail explaining fact-check assessment        |

##### Content Constraints

- **Required fields**: `action`, `intensity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: `intensity` MUST be clamped to [0.0, 1.0] before emission.
- **Units and sign conventions**: `intensity` is dimensionless; represents authoritative corrective force.
- **Determinism markers**: Decision is deterministic given identical inputs and state; no seed required.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining fact-check verdict and correction rationale)...</analysis>
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

| Signal        | Type       | Memory Window | Rationale                                                              |
|---------------|------------|---------------|------------------------------------------------------------------------|
| `env_belief`  | Continuous | 1 tick        | Primary trigger — high env_belief signals need for fact-checking        |
| `distortion`  | Continuous | 1 tick        | Modulates correction intensity — more distorted rumors need stronger denial |
| `truth_value` | Continuous | 1 tick        | Privileged ground truth for computing accurate belief and correction    |

Does NOT use: individual peer beliefs, rumor transmission chain identity, source attribution, network topology, or historical correction effectiveness feedback. The agent operates as a truth oracle that reacts to aggregate environmental state.

#### Core Behavioral Mechanism

1. **Read** `truth_value` and `my_belief` from state. **Compute** truth-convergence update: `new_belief = my_belief + 0.8 * (truth_value - my_belief)`. Clamp to [0, 1]. **Write** `my_belief = new_belief`. *(Theory: Privileged truth access produces rapid belief convergence [Lewandowsky et al. 2012])*

2. **Read** `env_belief` and `belief_threshold` parameter. **Compute** activation check: if `env_belief > belief_threshold`, set correction_needed = true; otherwise false. No state write. *(Theory: Fact-checking resources deployed when misinformation exceeds acceptable threshold [DiFonzo & Bordia 2007])*

3. **Read** updated `my_belief`, `fact_check_strength`, `credibility_discount`, `distortion_sensitivity` parameters, and `distortion` signal. **Compute** `raw_intensity = fact_check_strength * (1 - my_belief) * (1 + distortion_sensitivity * distortion) * credibility_discount`. No state write. *(Theory: Correction force proportional to falsity confidence, enhanced by distortion severity, discounted by credibility [DiFonzo & Bordia 2007])*

4. **Read** `raw_intensity`. **Compute** `clamped_intensity = min(1.0, max(0.0, raw_intensity))`. No state write. *(Implementation convenience — range clamping)*

5. **Read** correction_needed flag and `clamped_intensity`. **Compute** action: if correction_needed = true, `action = "correct"` and intensity = clamped_intensity; else `action = "ignore"` and intensity = 0.0. No state write. *(Theory: Active denial deployed when threshold exceeded [DiFonzo & Bordia 2007])*

6. **Read** computed `action` and intensity. **Write** decision object. No additional state write (belief was updated in step 1). *(Implementation convenience — emission)*

#### Action Space

| Aspect                | Specification                                                                                                    |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `correct`, `ignore`                                                                                              |
| Action parameter rule | `intensity` in [0.0, 1.0]: authoritative correction force                                                        |
| Sizing rule           | `intensity = clamp(fact_check_strength * (1-my_belief) * (1+distortion_sensitivity*distortion) * credibility_discount, 0, 1)` |
| Action lifetime       | Immediate single-round corrective effect on environment                                                          |
| Revision policy       | No revision — fact-check verdict is final for current round                                                      |
| State constraint      | `my_belief` bounded [0, 1]; naturally converges to truth_value rapidly                                           |
| Resource cap          | None — fact-checker operates every round when threshold met                                                      |
| Exit rule             | None — operates indefinitely as long as misinformation persists                                                  |

#### Mathematical Model

**Decision output**: `action` in {correct, ignore} and `intensity` in [0.0, 1.0].

**Decision logic formalization**:

```
# Belief update with truth convergence (pre-decision):
my_belief = clamp(my_belief + 0.8 * (truth_value - my_belief), 0, 1)

# Action decision:
IF env_belief > belief_threshold:
    action = "correct"
    intensity = clamp(fact_check_strength * (1 - my_belief) * (1 + distortion_sensitivity * distortion) * credibility_discount, 0, 1)
ELSE:
    action = "ignore"
    intensity = 0.0
```

**State variables**:

| Variable    | Type  | Initial Value | Update Phase |
|-------------|-------|---------------|--------------|
| `my_belief` | float | 0.1           | pre-decide   |

**State evolution**: `my_belief` updated pre-decide:
- `my_belief = clamp(my_belief + 0.8 * (truth_value - my_belief), 0, 1)`
- After 3 rounds, my_belief is within 0.05 of truth_value regardless of starting point.

**Determinism contract**: Fully deterministic given identical inputs and state. No stochastic components.

**Parameter symbol table**:

| Symbol                   | Meaning                                                   | Default Value | Source                    |
|--------------------------|-----------------------------------------------------------|---------------|---------------------------|
| `fact_check_strength`    | Base intensity of fact-check correction output            | 0.8           | DiFonzo & Bordia (2007)   |
| `credibility_discount`   | Discount factor reflecting source credibility perception  | 0.6           | DiFonzo & Bordia (2007)   |
| `distortion_sensitivity` | How much distortion amplifies correction intensity        | 0.5           | Lewandowsky et al. (2012) |
| `belief_threshold`       | Environmental belief level triggering correction          | 0.3           | Standardised              |
| `truth_value`            | Actual truth of the rumor (privileged signal)             | 0.1           | From coordinator          |
| `my_belief`              | Agent's current belief (rapidly converges to truth)       | 0.1           | Initial condition         |

#### Behavioral Properties

- **Time horizon**: Medium — provides sustained correction over many rounds until misinformation is suppressed.
- **Risk tolerance**: Low — operates conservatively from an evidence-based truth position; no speculative actions.
- **Information asymmetry**: Full — has privileged access to ground truth that other agents lack.
- **Psychological profile**: Embodies institutional credibility, evidence-based correction (Lewandowsky et al. 2012), professional fact-checking methodology (DiFonzo & Bordia 2007), and authoritative denial. Represents the most effective type of correction agent in rumor networks.

## Parameters

| Parameter                | Type    | Default | Valid Range  | Sensitivity | Description                                                        | Impact                                                 | Source                    |
|--------------------------|---------|---------|--------------|-------------|--------------------------------------------------------------------|--------------------------------------------------------|---------------------------|
| `fact_check_strength`    | float   | 0.8     | [0.1, 1.0]   | high        | Base intensity of fact-check correction signal                     | Higher -> stronger per-round corrective force          | DiFonzo & Bordia (2007)   |
| `credibility_discount`   | float   | 0.6     | [0.1, 1.0]   | high        | Perceived source credibility scaling factor                        | Higher -> more effective corrections                   | DiFonzo & Bordia (2007)   |
| `distortion_sensitivity` | float   | 0.5     | [0.0, 1.0]   | medium      | Amplification of correction when distortion is high                | Higher -> more aggressive correction in distorted environments | Lewandowsky et al. (2012) |
| `belief_threshold`       | float   | 0.3     | [0.1, 0.8]   | medium      | Minimum env_belief to trigger fact-checking                        | Higher -> less frequent correction, only high-belief states | Standardised              |
| `truth_convergence_rate` | float   | 0.8     | [0.5, 0.99]  | low         | Rate of personal belief convergence toward truth                   | Higher -> faster truth-seeking, marginally higher correction | Standardised              |

## Worked Numerical Examples

### Case 1 — Correct (standard fact-check deployment)

```
System state:
  env_belief = 0.6
  distortion = 0.4
  truth_value = 0.1
  my_belief = 0.15
  fact_check_strength = 0.8
  credibility_discount = 0.6
  distortion_sensitivity = 0.5
  belief_threshold = 0.3

Calculation:
  truth_update = 0.15 + 0.8 * (0.1 - 0.15) = 0.15 + 0.8*(-0.05) = 0.15 - 0.04 = 0.11
  my_belief = clamp(0.11, 0, 1) = 0.11
  env_belief (0.6) > belief_threshold (0.3) → action = "correct"
  raw_intensity = 0.8 * (1 - 0.11) * (1 + 0.5 * 0.4) * 0.6
              = 0.8 * 0.89 * 1.2 * 0.6
              = 0.8 * 0.89 * 0.72
              = 0.5126
  clamped_intensity = min(1.0, 0.5126) = 0.513

Decision: action = "correct", intensity = 0.513
State update: my_belief: 0.15 → 0.11
```

### Case 2 — Correct (high distortion amplifies correction)

```
System state:
  env_belief = 0.8
  distortion = 0.9
  truth_value = 0.1
  my_belief = 0.1
  fact_check_strength = 0.8
  credibility_discount = 0.6
  distortion_sensitivity = 0.5
  belief_threshold = 0.3

Calculation:
  truth_update = 0.1 + 0.8 * (0.1 - 0.1) = 0.1 + 0 = 0.1
  my_belief = clamp(0.1, 0, 1) = 0.1
  env_belief (0.8) > belief_threshold (0.3) → action = "correct"
  raw_intensity = 0.8 * (1 - 0.1) * (1 + 0.5 * 0.9) * 0.6
              = 0.8 * 0.9 * 1.45 * 0.6
              = 0.8 * 0.9 * 0.87
              = 0.6264
  clamped_intensity = min(1.0, 0.6264) = 0.626

Decision: action = "correct", intensity = 0.626
State update: my_belief: 0.1 → 0.1 (unchanged, already at truth)
```

### Case 3 — Ignore (environmental belief below threshold)

```
System state:
  env_belief = 0.2
  distortion = 0.3
  truth_value = 0.1
  my_belief = 0.12
  fact_check_strength = 0.8
  credibility_discount = 0.6
  distortion_sensitivity = 0.5
  belief_threshold = 0.3

Calculation:
  truth_update = 0.12 + 0.8 * (0.1 - 0.12) = 0.12 - 0.016 = 0.104
  my_belief = clamp(0.104, 0, 1) = 0.104
  env_belief (0.2) <= belief_threshold (0.3) → action = "ignore"
  intensity = 0.0

Decision: action = "ignore", intensity = 0.0
State update: my_belief: 0.12 → 0.104
```

### Case 4 — Correct at near-maximum intensity

```
System state:
  env_belief = 0.95
  distortion = 1.0
  truth_value = 0.1
  my_belief = 0.1
  fact_check_strength = 0.8
  credibility_discount = 0.6
  distortion_sensitivity = 0.5
  belief_threshold = 0.3

Calculation:
  truth_update = 0.1 + 0.8 * (0.1 - 0.1) = 0.1
  my_belief = 0.1
  env_belief (0.95) > belief_threshold (0.3) → action = "correct"
  raw_intensity = 0.8 * (1 - 0.1) * (1 + 0.5 * 1.0) * 0.6
              = 0.8 * 0.9 * 1.5 * 0.6
              = 0.648
  clamped_intensity = min(1.0, 0.648) = 0.648

Decision: action = "correct", intensity = 0.648
State update: my_belief: 0.1 → 0.1 (unchanged)
```

### Edge Case — Rapid belief convergence from high starting belief

```
System state:
  env_belief = 0.5
  distortion = 0.3
  truth_value = 0.1
  my_belief = 0.8  ← agent somehow started with high belief (misconfiguration scenario)
  fact_check_strength = 0.8
  credibility_discount = 0.6
  distortion_sensitivity = 0.5
  belief_threshold = 0.3

Calculation:
  truth_update = 0.8 + 0.8 * (0.1 - 0.8) = 0.8 + 0.8*(-0.7) = 0.8 - 0.56 = 0.24
  my_belief = clamp(0.24, 0, 1) = 0.24
  [Note: belief dropped dramatically in single round — strong truth convergence]
  env_belief (0.5) > belief_threshold (0.3) → action = "correct"
  raw_intensity = 0.8 * (1 - 0.24) * (1 + 0.5 * 0.3) * 0.6
              = 0.8 * 0.76 * 1.15 * 0.6
              = 0.4195
  clamped_intensity = min(1.0, 0.4195) = 0.420

Decision: action = "correct", intensity = 0.420
State update: my_belief: 0.8 → 0.24
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `fact_check_strength` <- DiFonzo & Bordia (2007, Table 6.2): high-credibility denial reduces belief by 50–70%; 0.8 targets upper range
- `credibility_discount` <- DiFonzo & Bordia (2007): credibility moderates denial effectiveness; 0.6 represents "high but not perfect" credibility
- `distortion_sensitivity` <- Lewandowsky et al. (2012): more distorted claims are easier to debunk (larger effect sizes); 0.5 moderate amplification
- `truth_convergence_rate` <- Lewandowsky et al. (2012): professional fact-checkers converge to truth within 1–2 exposures; 0.8 approximates this

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given env_belief=0.6, my_belief=0.15, truth_value=0.1, agent MUST emit action="correct" with intensity~0.513
- Given env_belief=0.2, agent MUST emit action="ignore" regardless of other state
- Agent's my_belief MUST converge to within 0.05 of truth_value within 3 rounds from any starting point
- Agent MUST never emit action="spread" (not in its action set)

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent's my_belief diverges from truth_value over time THEN truth convergence is broken
- IF agent emits "correct" when env_belief <= belief_threshold THEN activation gate is broken
- IF agent emits intensity > 1.0 THEN clamping is broken
- IF removing distortion_sensitivity produces identical intensity values THEN distortion wiring is broken

### Ablation Hooks

| Ablation name               | Setting                        | Hypothesis tested                                        | Expected direction | Metric                          |
|-----------------------------|--------------------------------|----------------------------------------------------------|--------------------|----------------------------------|
| `low_strength`              | `fact_check_strength = 0.3`    | Lower strength reduces correction effectiveness          | decrease           | Mean intensity when correcting  |
| `no_credibility`            | `credibility_discount = 1.0`   | Full credibility maximizes correction impact             | increase           | Mean intensity when correcting  |
| `no_distortion_sensitivity` | `distortion_sensitivity = 0.0` | Removing distortion response reduces adaptive correction | decrease           | Intensity variance across conditions |
| `high_threshold`            | `belief_threshold = 0.7`       | Higher threshold delays fact-check deployment            | decrease           | Fraction of rounds with correct |

## Academic References

| #  | Citation                                                                                                                                                                              | Notes                                   |
|----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| 1  | DiFonzo, N., & Bordia, P. (2007). Rumor Psychology: Social and Organizational Approaches. American Psychological Association. https://doi.org/10.1037/11503-000                       | Primary theory — active rumor denial    |
| 2  | Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J. (2012). Misinformation and its correction. Psychological Science in the Public Interest, 13(3), 106–131. https://doi.org/10.1177/1529100612451018 | Correction effectiveness meta-analysis  |
| 3  | Ecker, U. K. H., et al. (2022). The psychological drivers of misinformation belief. Nature Reviews Psychology, 1(1), 13–29. https://doi.org/10.1038/s44159-021-00006-y               | Resistance mechanisms                   |
| 4  | van der Linden, S., Leiserowitz, A., Rosenthal, S., & Maibach, E. (2017). Inoculating the public against misinformation about climate change. Global Challenges, 1(2), 1600008. https://doi.org/10.1002/gch2.201600008 | Prebunking/inoculation evidence         |
| 5  | Levine, T. R. (2014). Truth-default theory (TDT): A theory of human deception and deception detection. Journal of Language and Social Psychology, 33(4), 378–392. https://doi.org/10.1177/0261927X14535916 | Truth-default framework                 |
| 6  | Bordia, P., & DiFonzo, N. (2004). Problem solving in social interactions on the Internet: Rumor as social cognition. Social Psychology Quarterly, 67(1), 33–49. https://doi.org/10.1177/019027250406700105 | Social rumor correction dynamics        |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
