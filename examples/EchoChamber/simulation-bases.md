# EchoChamber Simulation Bases

## §1 Phenomenon Definition

EchoChamber models social polarization rather than asset trading. Agents hold
opinions in `[-1, 1]` and send `social_action` messages to an opinion
environment. Like-minded reinforcement increases polarization; bridge building,
critical evaluation, and center-pull reduce it. The scenario is intentionally a
special schema and must not be converted into a `bid_price` trading order model.

## §2 Theoretical Foundation

### §2.1 Deliberative Enclaves And Echo Chambers

Sunstein-style enclave deliberation predicts that like-minded discussion can
move participants toward more extreme versions of their initial views. The
`Ideologue` role implements in-group amplification and out-group discounting.

### §2.2 Conformity And Social Proof

Asch-style conformity and social-proof dynamics make agents align with perceived
group opinion. The `Conformist` role moves toward the local group mean and
polarizes once its own position becomes strong enough.

### §2.3 Persuasive Arguments And Critical Evaluation

Critical agents resist group pressure and evaluate whether polarization itself
is evidence of groupthink. The `CriticalThinker` role moves slowly toward the
center and emits depolarizing actions when polarization is high.

### §2.4 Cross-Cutting Exposure And Bridge Building

Deliberative-democracy and filter-bubble literature emphasize cross-cutting
exposure as an antidote to social fragmentation. The `BridgeBuilder` role moves
toward the center and depolarizes when cluster separation is high.

### §2.5 Passive Participation

Passive participants provide social mass without strong agency. The
`PassiveFollower` role drifts toward mean opinion and only occasionally acts.

## §3 Environment Mechanism

The environment consumes actions with this schema:

```json
{
  "action_type": "polarize|neutral|depolarize",
  "intensity": 0.0,
  "agent_role": "role name",
  "agent_id": "agent id",
  "opinion": 0.0,
  "reasoning": "optional for API variants",
  "analysis": "optional for API variants"
}
```

It updates polarization through:

```text
polarization(t+1) = clamp(
    polarization(t)
    + polarization_impact * (sum(polarize intensity) - sum(depolarize intensity))
    + centripetal_force * (0.3 - polarization(t))
    + noise,
    0, 1
)
```

The environment also records mean opinion, cluster separation, cross-cutting
exposure, polarize counts, and depolarize counts.

## §4 Investor Archetypes

### §4.1 Ideologue

**Summary**: Strong opinion holder that amplifies in-group consensus.
**Theoretical and Empirical Basis**: Echo-chamber and group-polarization
theory.
**Design Purpose**: Drive polarization when the environment leans toward the
agent's side.
**Behavioral Framework**: Treats same-sign mean opinion as validation and
opposing mean opinion as discounted out-group information.
**Decision Process**: If `my_opinion * mean_opinion > 0`, update toward
`mean_opinion * extremity_boost` using `in_group_weight`; otherwise discount the
opposing signal using `out_group_discount`. If `abs(my_opinion) > 0.3`, emit
`polarize` with intensity `abs(my_opinion) * spread_eagerness`.
**Worked Numerical Example**: Opinion `0.5` and mean `0.4` produce in-group
validation and a polarizing action around `0.5 * 0.9 = 0.45`.
**Academic References**: Echo chambers, enclave deliberation, and group
polarization literature.

### §4.2 Conformist

**Summary**: Group-oriented follower that adopts perceived local opinion.
**Theoretical and Empirical Basis**: Conformity, social proof, and informational
cascades.
**Design Purpose**: Reinforce group tendencies without independent conviction.
**Behavioral Framework**: Moves toward a local group mean derived from the
population mean and the sign of current opinion.
**Decision Process**: Update opinion using `conformity * (local_group_mean -
my_opinion)`. If `abs(my_opinion) > group_proximity_threshold`, emit `polarize`
with intensity `abs(my_opinion) * conformity_eagerness`.
**Worked Numerical Example**: Opinion `0.2`, local mean `0.6`, and conformity
`0.7` move opinion by `0.28` toward the group.
**Academic References**: Conformity experiments and social-proof models.

### §4.3 CriticalThinker

**Summary**: Evidence-oriented agent that resists group pressure.
**Theoretical and Empirical Basis**: Persuasive-arguments theory and
independent evidence evaluation.
**Design Purpose**: Provide stabilizing pressure when polarization becomes high.
**Behavioral Framework**: Treats high polarization as evidence that views should
move toward the center.
**Decision Process**: Compute `evidence_signal = -my_opinion *
evidence_sensitivity * polarization`, update slowly using `critical_weight`, and
emit `depolarize` when `polarization > 0.3`.
**Worked Numerical Example**: Opinion `0.6`, polarization `0.7`, and
evidence_sensitivity `0.6` create a negative signal that pulls the agent toward
the center.
**Academic References**: Group-polarization and persuasive-arguments research.

### §4.4 BridgeBuilder

**Summary**: Cross-group engager that reduces separation between opinion
clusters.
**Theoretical and Empirical Basis**: Cross-cutting exposure and deliberative
democracy.
**Design Purpose**: Counteract silo formation and provide strong depolarizing
pressure when clusters are far apart.
**Behavioral Framework**: Pulls its own opinion toward zero and emits
depolarizing actions when cluster separation is elevated.
**Decision Process**: Update opinion by `bridge_weight * (0 - my_opinion) *
centering_tendency`; if `cluster_separation > 0.5`, emit `depolarize` with
intensity `bridge_strength * min(cluster_separation, 1.0)`, with a weaker rule
for separation above `0.2`.
**Worked Numerical Example**: Cluster separation `0.8` and bridge strength `0.8`
produce a depolarizing intensity of `0.64`.
**Academic References**: Filter-bubble, deliberative-democracy, and
cross-cutting exposure literature.

### §4.5 PassiveFollower

**Summary**: Low-engagement participant that occasionally aligns with the
population.
**Theoretical and Empirical Basis**: Mass communication and passive audience
models.
**Design Purpose**: Provide background population inertia and stochastic
engagement.
**Behavioral Framework**: Drifts toward mean opinion and usually stays neutral.
**Decision Process**: Move by `drift_rate * (mean_opinion - my_opinion)`. With
probability `engagement_probability`, emit weak neutral or polarizing behavior
depending on opinion strength; otherwise emit `neutral`.
**Worked Numerical Example**: Opinion `0.1`, mean `0.4`, and drift rate `0.1`
move opinion by `0.03`.
**Academic References**: Mass communication and low-engagement audience
literature.

## §5 Agent Diversity Verification

The model includes two polarizing roles (`Ideologue`, `Conformist`), two
depolarizing roles (`CriticalThinker`, `BridgeBuilder`), and one low-engagement
background role (`PassiveFollower`). This diversity lets analysis separate
polarization generation from resistance and passive drift.

## §6 Parameter Table

| Config Path | Parameter | Runtime Meaning | Scenario Role |
|---|---|---|---|
| `environment.extras.initial_polarization` | `0.15` | Starting polarization | Moderate initial state |
| `environment.extras.polarization_impact` | `0.12` | Action intensity impact | Converts actions into polarization movement |
| `environment.extras.centripetal_force` | `0.01` | Center pull | Weak stabilizer |
| `ideologue.extras.in_group_weight` | `0.6` | In-group updating | Echo-chamber amplification |
| `ideologue.extras.spread_eagerness` | `0.9` | Polarizing intensity | Strong polarizer |
| `conformist.extras.conformity` | `0.7` | Group alignment | Social proof |
| `critical_thinker.extras.critical_eagerness` | `0.7` | Depolarizing intensity | Evidence resistance |
| `bridge_builder.extras.bridge_strength` | `0.8` | Cross-group repair | Strong depolarizer |
| `passive_follower.extras.engagement_probability` | `0.3` | Occasional engagement | Background participation |

## §7 Communication And Round Structure

The environment broadcasts polarization, mean opinion, cluster separation, and
cross-cutting exposure. Social agents update their personal opinion and emit a
`social_action`. The environment aggregates those actions and records the next
state. API variants preserve the same schema but use LLM reasoning to decide
`action_type` and `intensity`.

## §8 Historical Case Studies

### §8.1 Political Enclave Deliberation

Like-minded political discussion can create more extreme group positions by
validating shared assumptions and excluding dissenting evidence.

### §8.2 Algorithmic Filter Bubbles

Personalized feeds can reduce cross-cutting exposure and make the information
environment more homogeneous, increasing cluster separation.

### §8.3 Online Community Radicalization

Highly engaged communities can reward strong in-group signals, discount
out-group claims, and make moderate members drift toward group extremes.

## §9 Variant Comparison Preview

Rule implements the opinion dynamics directly. LLM uses persona-only reasoning
under the same special schema. RuleLLM gives the model explicit formulas. Rag
adds retrieved social-science context and records retrieval coverage.
