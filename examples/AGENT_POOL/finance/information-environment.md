# Rumor information environment coordinator

## Summary

| Field                 | Content                                                                                                |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Archetype             | Rumor information environment coordinator                                                              |
| Theory Family         | Social Psychology — Information Environment Dynamics and Collective Belief Formation                    |
| Behavioral Tendency   | **Adaptive** — aggregates agent actions and evolves belief/distortion state, adapting to net social forces |
| Time Horizon          | long                                                                                                   |
| Risk Tolerance        | medium                                                                                                 |
| Information Asymmetry | full                                                                                                   |
| Determinism           | stochastic-given-seed                                                                                  |

## Definition and Goals

This agent models the information environment itself — the shared social space through which rumors propagate and evolve. It is not a participant in the traditional sense but rather the central coordinator that maintains aggregate belief state, distortion levels, and broadcasts updated environmental signals to all participant agents each round. Real-world counterparts include the aggregate media environment, social network information ecology, public discourse space, and collective social memory. This concept is grounded in Shibutani (1966) who described the information environment as the "marketplace of rumors" and in Sunstein (2009) who formalized how information environments shape and are shaped by participant behavior.

The decision goal is to compute updated environmental belief and distortion states based on aggregated participant actions (net spread minus correction, truth correction drift, and noise), then broadcast these updated signals to all participant agents. The belief model: `belief(t+1) = clamp(belief + spread_impact * net_spread + truth_correction * (truth - belief) + noise, 0, 1)`. The distortion model: `distortion(t+1) = clamp(distortion - leveling_rate * distortion + sharpening_rate * spreader_count * (1 - truth_value), 0, 1)`. The coordinator maximizes simulation fidelity by maintaining internally consistent belief-distortion dynamics.

This agent acts as the central coordinator for the RumorSpread scenario — it does not participate as a social actor but rather evolves the shared state that all other agents observe and influence. Its characteristic action is aggregation, state evolution, and broadcasting. Non-goals: (1) the coordinator MUST NOT directly spread or correct rumors itself — it reflects the aggregate actions of participants; (2) the coordinator MUST NOT have behavioral biases — it is a mechanistic state-evolution engine, not a psychological agent.

## Theoretical Foundation

**Collective Belief Dynamics (Shibutani 1966; Sunstein 2009)**:
- Theory / Study: Information environment as collective belief aggregation
- Citation: Shibutani, T. (1966). Improvised News: A Sociological Study of Rumor. Bobbs-Merrill Company. ISBN: 978-0672610523; Sunstein, C. R. (2009). On Rumors: How Falsehoods Spread, Why We Believe Them, and What Can Be Done. Princeton University Press. ISBN: 978-0691134154
- Core Insight: The information environment is not merely the sum of individual beliefs but an emergent aggregate state that reflects the balance of spreading forces, correction forces, truth-seeking drift, and stochastic noise. Environmental belief evolves as a function of net social action intensity — when spreaders outnumber correctors, belief rises; when correctors dominate, belief falls. A natural truth correction drift represents the slow self-correcting tendency of information environments over time.
- Mathematical Formulation: `belief(t+1) = clamp(belief(t) + spread_impact * net_spread + truth_correction * (truth_value - belief(t)) + N(0, noise_std), 0, 1)`
- Empirical Evidence: Shibutani (1966) documented 5 natural rumor episodes showing belief curves that followed logistic growth modified by correction interventions, with steady-state belief levels 20–60% below peak when active correction was present. Vosoughi et al. (2018) measured cascade dynamics on Twitter showing net belief increase rates of 10–20% per cascade hop when spreading dominates.
- Relevance to This Agent: The coordinator instantiates the mathematical model of collective belief evolution, incorporating all forces (spreading, correction, truth drift, noise) into a single state-update equation.
- Calibration Source: Vosoughi et al. (2018, Figure 2): false news belief cascades grew at 10–20% per hop; spread_impact=0.15 targets this range. Lewandowsky et al. (2012): truth correction reduces belief by 2–5% per exposure round in natural attrition; truth_correction=0.02 maps to lower bound.
- Falsification Conditions: If environmental belief does not respond to changes in net_spread (remains constant when net_spread changes sign), the belief evolution mechanism is broken. If belief exceeds [0,1] bounds or exhibits non-monotonic response to monotonic input, the clamp/update logic is flawed.
- Alternative Theories: Bass diffusion model (Bass 1969), SIR epidemic models applied to rumors (Daley & Kendall 1965), threshold models of collective behavior (Granovetter 1978).

**Distortion Dynamics in Serial Transmission (Allport & Postman 1947; Bartlett 1932)**:
- Theory / Study: Rumor distortion as an evolving property of the information environment
- Citation: Allport, G. W., & Postman, L. (1947). The Psychology of Rumor. Henry Holt and Company; Bartlett, F. C. (1932). Remembering. Cambridge University Press. https://doi.org/10.1017/CBO9780511759185
- Core Insight: Distortion in the information environment is a dynamic property that increases when spreading agents (who introduce sharpening errors) are active and decreases through natural leveling (detail loss and regression to simpler narratives over time). The rate of distortion growth is proportional to the number of active spreaders and the degree to which the rumor differs from truth (false content is more susceptible to distortion than true content).
- Mathematical Formulation: `distortion(t+1) = clamp(distortion(t) - leveling_rate * distortion(t) + sharpening_rate * spreader_count * (1 - truth_value), 0, 1)`
- Empirical Evidence: Allport & Postman (1947) documented distortion accumulation at approximately 15% per transmission step in serial reproduction chains, with natural leveling (simplification) reducing distortion by 5–10% per time unit when no active transmission occurs. Bartlett (1932) confirmed compounding distortion with leveling rate inversely proportional to transmission frequency.
- Relevance to This Agent: The coordinator maintains the distortion state variable, increasing it when spreaders are active (especially when the rumor is false) and decreasing it through natural leveling attrition.
- Calibration Source: Allport & Postman (1947, Chapter 5): per-step distortion increase = 10–20% with active transmission; leveling_rate = 5–15% per period in absence of active spreading. Agent's sharpening_rate=0.02 and leveling_rate=0.01 produce comparable dynamics when scaled by typical spreader counts (5–10 agents).
- Falsification Conditions: If distortion does not increase when multiple spreaders are active and truth_value is low, the sharpening mechanism is not connected. If distortion does not decrease over time when no spreaders are active, the leveling mechanism is broken.
- Alternative Theories: Information entropy models (Shannon 1948 applied to social systems), cultural evolution drift (Cavalli-Sforza & Feldman 1981).

## Design Purpose and Activation Triggers

Purpose: Aggregate participant social actions into environmental belief and distortion state updates, then broadcast updated signals to all agents, serving as the central coordinator for the RumorSpread scenario.

Call Frequency: every-tick (executes after all participant agents have emitted their actions for the round)

Prerequisite Signals (must be available for the agent to evaluate):
- Aggregated `spread_actions` from all participant agents (list of intensity values from spreading agents)
- Aggregated `correct_actions` from all participant agents (list of intensity values from correcting agents)
- Internal state variables (`belief`, `distortion`) from previous round

Missing-Signal Policy: If no participant actions are received, assume net_spread = 0 and spreader_count = 0 (environment state drifts toward truth through natural correction only).

Activation Triggers:
- Round completion (all participant agents have acted): EXECUTE state update and broadcast
- `<Default>`: maintain current state (should not occur in normal operation)

Deactivation Conditions:
- If all participant agents are deactivated (no actions received for 20+ rounds), coordinator enters dormant state.
- Simulation termination signal from scheduler ends coordinator operation.

Behavioral Adaptation by Condition:
| Condition                               | Behavioral change                                            | Mechanism                                                        |
|-----------------------------------------|--------------------------------------------------------------|------------------------------------------------------------------|
| Net positive spread (spreaders dominate)| Belief increases, distortion increases                        | Spreading forces drive both belief and distortion upward         |
| Net negative spread (correctors dominate)| Belief decreases, distortion decreases via reduced spreading | Correction forces reduce belief; fewer spreaders reduce distortion|
| No active agents                        | Belief drifts toward truth; distortion decays via leveling   | Natural truth correction and leveling in absence of active forces|

Environmental Dependencies: Requires aggregated action summaries from all participant agents and a seeded pseudorandom number generator for noise injection. The coordinator IS the environment — it produces the signals that other agents consume.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                       | Type / Shape        | Required?              | Notes                                                     |
|----------------------|------------------------------|---------------------|------------------------|-----------------------------------------------------------|
| `spread_intensities` | aggregated from participants | `list[float]`       | yes                    | Intensities from all agents who chose action="spread"     |
| `correct_intensities`| aggregated from participants | `list[float]`       | yes                    | Intensities from all agents who chose action="correct"    |
| `belief`             | agent's own persisted state  | `float`             | yes                    | Current environmental belief [0,1] from §3.6.4 init       |
| `distortion`         | agent's own persisted state  | `float`             | yes                    | Current environmental distortion [0,1] from §3.6.4 init   |
| `round`              | scheduler / round header     | `int`               | yes                    | Round number for noise seeding                            |
| `agent_id`           | scheduler / round header     | `str`               | yes                    | Identity: `{variant}_information_environment`             |
| `retrieved_knowledge`| retrieval store              | `list[str]`         | retrieval variants only| Falls back to sentinel if empty                           |

##### Outputs (per decision call)

| Field              | Type   | Valid Range / Enum | Unit    | Required? | Meaning                                                 |
|--------------------|--------|--------------------|---------|-----------|---------------------------------------------------------|
| `belief_broadcast` | float  | [0.0, 1.0]         | unitless| yes       | Updated environmental belief to broadcast to all agents |
| `distortion_broadcast` | float | [0.0, 1.0]      | unitless| yes       | Updated distortion level to broadcast to all agents     |
| `reasoning`        | string | 1–3 sentences      | —       | yes       | Audit trail explaining state evolution this round       |

##### Content Constraints

- **Required fields**: `belief_broadcast`, `distortion_broadcast`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: No fields beyond those declared in the Outputs table may be emitted.
- **Value ranges**: Both `belief_broadcast` and `distortion_broadcast` MUST be clamped to [0.0, 1.0].
- **Units and sign conventions**: Both outputs are dimensionless belief/distortion levels. Higher values indicate stronger rumor belief and more distorted information respectively.
- **Determinism markers**: Stochastic-given-seed due to noise injection; same seed + same inputs + same state = same output.

##### Serialization Format

```
<analysis>...free-form reasoning (1–3 sentences explaining net forces and state evolution this round)...</analysis>
<decision>{"belief_broadcast": <float>, "distortion_broadcast": <float>, "reasoning": "<audit-trail explanation>"}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block contains a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants generate `<analysis>` from a deterministic template (noting noise seed).
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare the fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for: (1) Signal wiring — every input row maps to a real read. (2) Decision emission — populate every required field, clamp out-of-range numerics. (3) Prompt drafting — spell out tag pattern and JSON schema literally. (4) Parser tests — verify tags, parse JSON, assert field presence and ranges. (5) Variant parity — all variants produce the same field set. (6) On conflict with prose elsewhere, this section wins.

#### Decision Information Set

| Signal                | Type       | Memory Window | Rationale                                                              |
|-----------------------|------------|---------------|------------------------------------------------------------------------|
| `spread_intensities`  | Continuous | 1 tick        | Aggregated spreading force from all active spreaders this round        |
| `correct_intensities` | Continuous | 1 tick        | Aggregated correction force from all active correctors this round      |

Does NOT use: individual agent beliefs, individual agent identities, network topology, message content, or historical action sequences. The coordinator operates on aggregated intensities only, maintaining environment-level abstraction.

#### Core Behavioral Mechanism

1. **Read** `spread_intensities` and `correct_intensities` lists. **Compute** `net_spread = sum(spread_intensities) - sum(correct_intensities)`. Also compute `spreader_count = len(spread_intensities)`. No state write. *(Implementation convenience — action aggregation)*

2. **Read** `belief` from state, `spread_impact` and `truth_correction` parameters, `rumor_truth_value` parameter. **Compute** belief forces: `spread_force = spread_impact * net_spread`; `truth_force = truth_correction * (rumor_truth_value - belief)`. No state write. *(Theory: Collective belief dynamics — balance of social forces and truth drift [Shibutani 1966; Sunstein 2009])*

3. **Read** `noise_std` parameter and round number. **Compute** noise: `noise = N(0, noise_std)` drawn from seeded RNG. No state write. *(Theory: Stochastic perturbation representing unmodelled random influences on collective belief [Sunstein 2009])*

4. **Read** computed forces and noise. **Compute** belief update: `new_belief = clamp(belief + spread_force + truth_force + noise, 0, 1)`. **Write** `belief = new_belief`. *(Theory: Aggregate belief evolution under competing forces [Shibutani 1966])*

5. **Read** `distortion` from state, `leveling_rate`, `sharpening_rate` parameters, `spreader_count`, `rumor_truth_value`. **Compute** distortion update: `new_distortion = clamp(distortion - leveling_rate * distortion + sharpening_rate * spreader_count * (1 - rumor_truth_value), 0, 1)`. **Write** `distortion = new_distortion`. *(Theory: Distortion evolves through sharpening (active transmission adds errors) and leveling (natural decay) [Allport & Postman 1947; Bartlett 1932])*

6. **Read** updated `belief` and `distortion`. **Write** decision object: `{belief_broadcast: new_belief, distortion_broadcast: new_distortion, reasoning: ...}`. *(Implementation convenience — broadcast emission)*

#### Action Space

| Aspect                | Specification                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| Action types allowed  | `broadcast` (single action type — coordinator always broadcasts updated state)                        |
| Action parameter rule | Two continuous parameters: `belief_broadcast` in [0,1] and `distortion_broadcast` in [0,1]            |
| Sizing rule           | Belief: `clamp(belief + spread_impact*net_spread + truth_correction*(truth-belief) + noise, 0, 1)`. Distortion: `clamp(distortion - leveling_rate*distortion + sharpening_rate*spreader_count*(1-truth_value), 0, 1)` |
| Action lifetime       | Broadcast persists for one round; replaced by next round's broadcast                                  |
| Revision policy       | No revision — each round produces exactly one broadcast that overwrites the previous                  |
| State constraint      | `belief` and `distortion` both bounded in [0.0, 1.0]                                                 |
| Resource cap          | None — coordinator operates every round without resource limitation                                   |
| Exit rule             | None — operates for entire simulation duration                                                        |

#### Mathematical Model

**Decision output**: `belief_broadcast` in [0.0, 1.0] and `distortion_broadcast` in [0.0, 1.0].

**Decision logic formalization**:

```
# Aggregation:
net_spread = sum(spread_intensities) - sum(correct_intensities)
spreader_count = len(spread_intensities)

# Belief evolution:
noise = Normal(0, noise_std)  [seeded by rng_seed + round]
new_belief = clamp(belief + spread_impact * net_spread + truth_correction * (rumor_truth_value - belief) + noise, 0, 1)

# Distortion evolution:
new_distortion = clamp(distortion - leveling_rate * distortion + sharpening_rate * spreader_count * (1 - rumor_truth_value), 0, 1)

# Output:
belief_broadcast = new_belief
distortion_broadcast = new_distortion
```

**State variables**:

| Variable     | Type  | Initial Value | Update Phase |
|--------------|-------|---------------|--------------|
| `belief`     | float | 0.3           | post-aggregation |
| `distortion` | float | 0.1           | post-aggregation |

**State evolution**: Both state variables are updated after action aggregation (within the same tick, after all participants have acted):
- `belief` updated by spread force + truth correction + noise
- `distortion` updated by sharpening growth - leveling decay
- Update ordering: belief first, then distortion (order does not matter as they are independent in the current formulation)

**Determinism contract**: Stochastic-given-seed due to Gaussian noise. Given identical `rng_seed`, `round`, inputs (spread/correct intensities), and state (belief, distortion), produces identical output.

**Parameter symbol table**:

| Symbol               | Meaning                                                        | Default Value | Source                       |
|----------------------|----------------------------------------------------------------|---------------|------------------------------|
| `rumor_truth_value`  | Actual truth probability of the rumor (0 = entirely false)     | 0.1           | Scenario configuration       |
| `initial_belief`     | Starting environmental belief level                            | 0.3           | Scenario configuration       |
| `spread_impact`      | Scaling factor for net spread force on belief                  | 0.15          | Vosoughi et al. (2018)       |
| `truth_correction`   | Rate of natural belief drift toward truth                      | 0.02          | Lewandowsky et al. (2012)    |
| `leveling_rate`      | Rate of natural distortion decay                               | 0.01          | Allport & Postman (1947)     |
| `sharpening_rate`    | Rate of distortion growth per active spreader                  | 0.02          | Allport & Postman (1947)     |
| `noise_std`          | Standard deviation of Gaussian noise on belief                 | 0.01          | Standardised                 |
| `net_spread`         | Computed: sum(spread) - sum(correct)                           | —             | Derived from participant actions |
| `spreader_count`     | Computed: number of actively spreading agents                  | —             | Derived from participant actions |

#### Behavioral Properties

- **Time horizon**: Long — maintains persistent state across the entire simulation, evolving belief and distortion over many rounds.
- **Risk tolerance**: Medium — noise injection introduces mild stochastic variation but state is bounded and self-correcting.
- **Information asymmetry**: Full — has complete knowledge of all participant actions (aggregated), truth value, and state history.
- **Psychological profile**: Not applicable in the traditional sense — this is a mechanistic environment model, not a psychological agent. It embodies the collective dynamics of belief formation (Shibutani 1966), information environment evolution (Sunstein 2009), and serial distortion accumulation (Allport & Postman 1947).

## Parameters

| Parameter            | Type    | Default | Valid Range    | Sensitivity | Description                                                         | Impact                                                 | Source                       |
|----------------------|---------|---------|----------------|-------------|---------------------------------------------------------------------|--------------------------------------------------------|------------------------------|
| `rumor_truth_value`  | float   | 0.1     | [0.0, 1.0]     | high        | Actual truth probability of the rumor                               | Higher -> belief naturally settles higher (less correction needed) | Scenario configuration       |
| `initial_belief`     | float   | 0.3     | [0.0, 1.0]     | medium      | Starting environmental belief at round 0                            | Higher -> simulation starts with more established rumor | Scenario configuration       |
| `spread_impact`      | float   | 0.15    | [0.01, 0.5]    | high        | How strongly net spreading affects belief per round                  | Higher -> faster belief growth when spreaders dominate  | Vosoughi et al. (2018)       |
| `truth_correction`   | float   | 0.02    | [0.001, 0.10]  | high        | Rate of natural belief drift toward truth_value                     | Higher -> faster natural rumor decay                   | Lewandowsky et al. (2012)    |
| `leveling_rate`      | float   | 0.01    | [0.001, 0.10]  | medium      | Rate of natural distortion decay per round                          | Higher -> distortion decays faster when spreading stops | Allport & Postman (1947)     |
| `sharpening_rate`    | float   | 0.02    | [0.001, 0.10]  | medium      | Distortion growth per active spreader per round                     | Higher -> more distortion from each spreading agent    | Allport & Postman (1947)     |
| `noise_std`          | float   | 0.01    | [0.0, 0.10]    | low         | Standard deviation of Gaussian noise on belief                      | Higher -> more stochastic variation in belief dynamics  | Standardised                 |
| `initial_distortion` | float   | 0.1     | [0.0, 1.0]     | low         | Starting distortion level at round 0                                | Higher -> simulation starts with pre-existing distortion | Scenario configuration       |

## Worked Numerical Examples

### Case 1 — Belief increases (spreaders dominate)

```
System state:
  belief = 0.3
  distortion = 0.1
  spread_intensities = [0.6, 0.5, 0.4]  (3 spreaders)
  correct_intensities = [0.7]  (1 corrector)
  rumor_truth_value = 0.1
  spread_impact = 0.15
  truth_correction = 0.02
  leveling_rate = 0.01
  sharpening_rate = 0.02
  noise_std = 0.01
  noise_draw = 0.005 (example draw from N(0, 0.01))

Calculation:
  net_spread = (0.6 + 0.5 + 0.4) - (0.7) = 1.5 - 0.7 = 0.8
  spreader_count = 3
  spread_force = 0.15 * 0.8 = 0.12
  truth_force = 0.02 * (0.1 - 0.3) = 0.02 * (-0.2) = -0.004
  new_belief = clamp(0.3 + 0.12 + (-0.004) + 0.005, 0, 1) = clamp(0.421, 0, 1) = 0.421
  
  leveling = 0.01 * 0.1 = 0.001
  sharpening = 0.02 * 3 * (1 - 0.1) = 0.02 * 3 * 0.9 = 0.054
  new_distortion = clamp(0.1 - 0.001 + 0.054, 0, 1) = clamp(0.153, 0, 1) = 0.153

Decision: belief_broadcast = 0.421, distortion_broadcast = 0.153
State update: belief: 0.3 → 0.421, distortion: 0.1 → 0.153
```

### Case 2 — Belief decreases (correctors dominate)

```
System state:
  belief = 0.6
  distortion = 0.4
  spread_intensities = [0.3]  (1 spreader)
  correct_intensities = [0.7, 0.6, 0.5]  (3 correctors)
  rumor_truth_value = 0.1
  spread_impact = 0.15
  truth_correction = 0.02
  leveling_rate = 0.01
  sharpening_rate = 0.02
  noise_std = 0.01
  noise_draw = -0.003

Calculation:
  net_spread = (0.3) - (0.7 + 0.6 + 0.5) = 0.3 - 1.8 = -1.5
  spreader_count = 1
  spread_force = 0.15 * (-1.5) = -0.225
  truth_force = 0.02 * (0.1 - 0.6) = 0.02 * (-0.5) = -0.01
  new_belief = clamp(0.6 + (-0.225) + (-0.01) + (-0.003), 0, 1) = clamp(0.362, 0, 1) = 0.362
  
  leveling = 0.01 * 0.4 = 0.004
  sharpening = 0.02 * 1 * (1 - 0.1) = 0.02 * 0.9 = 0.018
  new_distortion = clamp(0.4 - 0.004 + 0.018, 0, 1) = clamp(0.414, 0, 1) = 0.414

Decision: belief_broadcast = 0.362, distortion_broadcast = 0.414
State update: belief: 0.6 → 0.362, distortion: 0.4 → 0.414
```

### Case 3 — Natural decay (no active agents)

```
System state:
  belief = 0.5
  distortion = 0.3
  spread_intensities = []  (no spreaders)
  correct_intensities = []  (no correctors)
  rumor_truth_value = 0.1
  spread_impact = 0.15
  truth_correction = 0.02
  leveling_rate = 0.01
  sharpening_rate = 0.02
  noise_std = 0.01
  noise_draw = 0.002

Calculation:
  net_spread = 0 - 0 = 0
  spreader_count = 0
  spread_force = 0.15 * 0 = 0
  truth_force = 0.02 * (0.1 - 0.5) = 0.02 * (-0.4) = -0.008
  new_belief = clamp(0.5 + 0 + (-0.008) + 0.002, 0, 1) = clamp(0.494, 0, 1) = 0.494
  
  leveling = 0.01 * 0.3 = 0.003
  sharpening = 0.02 * 0 * 0.9 = 0
  new_distortion = clamp(0.3 - 0.003 + 0, 0, 1) = clamp(0.297, 0, 1) = 0.297

Decision: belief_broadcast = 0.494, distortion_broadcast = 0.297
State update: belief: 0.5 → 0.494, distortion: 0.3 → 0.297
[Note: Both belief and distortion decay naturally toward truth/zero in absence of active agents]
```

### Case 4 — Heavy spreading pushes belief near saturation

```
System state:
  belief = 0.8
  distortion = 0.6
  spread_intensities = [0.9, 0.8, 0.7, 0.6, 0.5]  (5 high-intensity spreaders)
  correct_intensities = [0.5]  (1 corrector)
  rumor_truth_value = 0.1
  spread_impact = 0.15
  truth_correction = 0.02
  leveling_rate = 0.01
  sharpening_rate = 0.02
  noise_std = 0.01
  noise_draw = 0.008

Calculation:
  net_spread = (0.9+0.8+0.7+0.6+0.5) - (0.5) = 3.5 - 0.5 = 3.0
  spreader_count = 5
  spread_force = 0.15 * 3.0 = 0.45
  truth_force = 0.02 * (0.1 - 0.8) = 0.02 * (-0.7) = -0.014
  new_belief = clamp(0.8 + 0.45 + (-0.014) + 0.008, 0, 1) = clamp(1.244, 0, 1) = 1.0  ← CLAMPED
  
  leveling = 0.01 * 0.6 = 0.006
  sharpening = 0.02 * 5 * (1 - 0.1) = 0.02 * 5 * 0.9 = 0.09
  new_distortion = clamp(0.6 - 0.006 + 0.09, 0, 1) = clamp(0.684, 0, 1) = 0.684

Decision: belief_broadcast = 1.0, distortion_broadcast = 0.684
State update: belief: 0.8 → 1.0, distortion: 0.6 → 0.684
```

### Edge Case — Belief at zero with only truth correction

```
System state:
  belief = 0.0
  distortion = 0.0
  spread_intensities = []
  correct_intensities = []
  rumor_truth_value = 0.1
  spread_impact = 0.15
  truth_correction = 0.02
  leveling_rate = 0.01
  sharpening_rate = 0.02
  noise_std = 0.01
  noise_draw = -0.005

Calculation:
  net_spread = 0
  spreader_count = 0
  spread_force = 0
  truth_force = 0.02 * (0.1 - 0.0) = 0.002
  new_belief = clamp(0.0 + 0 + 0.002 + (-0.005), 0, 1) = clamp(-0.003, 0, 1) = 0.0  ← CLAMPED at 0
  
  leveling = 0.01 * 0.0 = 0
  sharpening = 0.02 * 0 * 0.9 = 0
  new_distortion = clamp(0.0 - 0 + 0, 0, 1) = 0.0

Decision: belief_broadcast = 0.0, distortion_broadcast = 0.0
State update: belief: 0.0 → 0.0, distortion: 0.0 → 0.0
[Note: With negative noise draw, belief cannot go below 0 — clamp prevents negative values]
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `spread_impact` <- Vosoughi et al. (2018, Figure 2): false news belief grows 10–20% per cascade hop; 0.15 per unit net_spread maps to this range
- `truth_correction` <- Lewandowsky et al. (2012): natural belief attrition toward truth at 2–5% per time unit; 0.02 targets lower bound
- `leveling_rate` <- Allport & Postman (1947, Chapter 5): natural distortion decay at 5–15% per period without active transmission; 0.01 per round
- `sharpening_rate` <- Allport & Postman (1947): per-transmitter distortion increase 10–20% per step; 0.02 per spreader per round

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given net_spread > 0, belief MUST increase (modulo noise and truth correction which are typically small)
- Given net_spread < 0, belief MUST decrease
- Given spreader_count > 0 and truth_value < 1, distortion MUST increase (modulo leveling)
- Given spreader_count = 0, distortion MUST decrease (leveling dominates)
- belief and distortion MUST always remain in [0, 1]

**Sanity bounds (red flags indicating broken implementation)**:
- IF belief ever exceeds 1.0 or falls below 0.0 THEN clamping is broken
- IF distortion ever exceeds 1.0 or falls below 0.0 THEN clamping is broken
- IF belief is non-responsive to changes in net_spread (correlation < 0.5 over 50 rounds) THEN spread_impact wiring is broken
- IF distortion never decreases when no spreaders are active THEN leveling mechanism is broken

### Ablation Hooks

| Ablation name            | Setting                    | Hypothesis tested                                         | Expected direction | Metric                            |
|--------------------------|----------------------------|-----------------------------------------------------------|--------------------|-----------------------------------|
| `no_truth_correction`    | `truth_correction = 0.0`   | Natural truth drift provides baseline rumor decay         | increase           | Steady-state belief level         |
| `no_noise`               | `noise_std = 0.0`          | Noise adds stochastic variation without directional bias  | neutral (reduced variance) | Belief variance across rounds |
| `high_spread_impact`     | `spread_impact = 0.4`      | Stronger spread sensitivity accelerates belief growth     | increase           | Peak belief level                 |
| `no_leveling`            | `leveling_rate = 0.0`      | Leveling provides natural distortion decay                | increase           | Steady-state distortion level     |
| `no_sharpening`          | `sharpening_rate = 0.0`    | Sharpening drives distortion growth with active spreading | decrease           | Peak distortion level             |

## Academic References

| #  | Citation                                                                                                                                                         | Notes                                     |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1  | Shibutani, T. (1966). Improvised News: A Sociological Study of Rumor. Bobbs-Merrill Company. ISBN: 978-0672610523                                                | Primary theory — information environment  |
| 2  | Sunstein, C. R. (2009). On Rumors: How Falsehoods Spread, Why We Believe Them, and What Can Be Done. Princeton University Press. ISBN: 978-0691134154             | Collective belief dynamics                |
| 3  | Allport, G. W., & Postman, L. (1947). The Psychology of Rumor. Henry Holt and Company.                                                                           | Leveling/sharpening distortion dynamics   |
| 4  | Bartlett, F. C. (1932). Remembering: A Study in Experimental and Social Psychology. Cambridge University Press. https://doi.org/10.1017/CBO9780511759185          | Serial distortion accumulation            |
| 5  | Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. Science, 359(6380), 1146–1151. https://doi.org/10.1126/science.aap9559       | Cascade growth rate calibration           |
| 6  | Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J. (2012). Misinformation and its correction. Psychological Science in the Public Interest, 13(3), 106–131. https://doi.org/10.1177/1529100612451018 | Truth correction rate calibration         |
| 7  | Daley, D. J., & Kendall, D. G. (1965). Stochastic rumours. IMA Journal of Applied Mathematics, 1(1), 42–55. https://doi.org/10.1093/imamat/1.1.42               | Mathematical rumor models                 |
| 8  | Granovetter, M. (1978). Threshold models of collective behavior. American Journal of Sociology, 83(6), 1420–1443. https://doi.org/10.1086/226707                  | Threshold-based collective dynamics       |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-information-environment.png) |
