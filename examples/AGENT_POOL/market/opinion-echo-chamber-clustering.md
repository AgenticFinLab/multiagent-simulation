# Opinion field coordinator with echo-chamber clustering dynamics

## Summary

| Field                | Content                                                                                                                                                                                                     |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Market Type          | `opinion` — Opinion / Social-Influence Field                                                                                                                                                                |
| Coordinator Role     | Central population-opinion coordinator that aggregates polarize/depolarize actions and tracks polarization, mean opinion, cluster separation, and cross-cutting exposure                                    |
| Mechanism Family     | Linear polarization dynamics with centripetal moderation and Gaussian noise; cluster/exposure moments derived from submitted opinions                                                                       |
| Shared State         | `polarization`, `mean_opinion`, `cluster_separation`, `cross_cutting_exposure`, `polarization_change`, `num_polarizers`, `num_depolarizers`, `net_polarization_intensity`, `round`                            |
| Broadcast Cadence    | every-tick (one broadcast per simulation round, after all agents submit polarize / depolarize / neutral actions)                                                                                            |
| Determinism          | stochastic-given-seed (ε ~ N(0, σ²) drawn from a seeded RNG; identical seed + identical inbound action sequence + identical submitted opinions reproduce byte-equal broadcasts)                             |
| Feedback Direction   | **Regime-dependent** — inside the moderate band (polarization near the equilibrium anchor `p*`), the centripetal term dominates and the mechanism is stabilising; outside that band, if `polarization_impact · |net_polarization|` exceeds `centripetal_force · |p − p*|`, the mechanism amplifies clustering [Ref 1, Ref 2] |
| Scenario Portability | 1 pool scenario bound via `players.yml → market.archetype: opinion-echo-chamber-clustering`. **Full ✅**: EchoChamber (dedicated `OpinionEnvironment` class with `polarization` + `cluster_separation` + `cross_cutting_exposure` state). **Approximated ⚠**: (none). See also the Scenario Status row below. |
| Scenario Status      | **Full** = coordinator code implements the archetype's mechanism signature verbatim; **Approximated** = archetype bound via `players.yml → market.archetype:` for icon/UI/narrative purposes, but the coordinator code currently uses the standard price-impact formula `P(t+1)=P(t)+λ·NetDemand+γ·(F-P(t))+ε` as a placeholder — the archetype's specialized state and dynamics are intended but not yet realized in code. |

## Definition and Goals

This coordinator models a **single-population, continuous-polarization
opinion field with a designated echo-chamber clustering mechanism** —
the workhorse coordinator used to study group polarization, filter
bubbles, and homophily-driven opinion dynamics at the population
level. The real-world counterpart is a deliberative or social-media
population where like-minded individuals reinforce each other's views
through selective exposure, approximated at the round (deliberation
cycle) granularity, similar in spirit to the setup analysed by
Sunstein (2001) [Ref 1] and formalised in the opinion-dynamics
literature by DeGroot (1974) [Ref 2] and Del Vicario et al. (2016)
[Ref 3]. The coordinator is deliberately field-level rather than
peer-graph-matched, because the round granularity of the enclosing
simulation makes an explicit interaction network both unnecessary and
(per Deffuant et al. 2000 [Ref 4]) analytically equivalent to a
linear net-influence rule at sufficient aggregation.

The coordination goal is to **aggregate all participant
polarize/depolarize actions submitted this round, produce exactly one
new polarization scalar `P(t+1)` via the equation `P(t+1) =
clip(P(t) + α · NetPolarization + β · (p* − P(t)) + ε, 0, 1)`, derive
the moment observables (mean opinion, cluster separation,
cross-cutting exposure) from the submitted opinions, and broadcast
`{polarization, prev_polarization, polarization_change, mean_opinion,
cluster_separation, cross_cutting_exposure, num_polarizers,
num_depolarizers, net_polarization_intensity, round}` to every
participant.** The broadcast is identical for every participant
(symmetric information environment).

Non-goals (this coordinator MUST NOT):

- MUST NOT filter or route actions based on participant identity,
  role label, or history — homophily is expressed in participant
  profiles (via `agent_role` and personal opinion), not in the
  coordinator.
- MUST NOT inject exogenous news, moral shocks, or media events from
  within its own logic — such drivers enter via the Exogenous Driver
  Boundary declared in §5.
- MUST NOT enforce individual participant opinion bounds (e.g. clamp
  a participant's submitted `opinion` to `[-1, 1]`) — validation of
  submitted actions is a shared responsibility of the format layer
  and the coordinator's Missing-Input Policy, but individual bounds
  are self-imposed at the participant side.
- MUST NOT modify the equilibrium anchor `p* = polarization_equilibrium`
  from its own logic; equilibrium drift, if any, is a scenario
  overlay written into `extras` by the scenario runner before
  `perceive` (see §5).

## Theoretical / Mechanistic Foundation

**Linear opinion-influence aggregation (DeGroot 1974)**:

- Theory / Study: Reaching a consensus by iterated linear averaging
  of neighbours' opinions
- Citation: DeGroot, M. H. (1974). "Reaching a Consensus." *Journal
  of the American Statistical Association*, 69(345), 118–121.
  DOI: `10.1080/01621459.1974.10480137`
- Core Insight: In a population that updates by linear averaging of
  net social influence, the change in the collective opinion
  statistic is a **linear function of the aggregate signed
  influence** whose slope captures how much a marginal net-polarize
  action moves the population index. Higher slope means the
  population is more receptive to social pressure; lower slope means
  the population is more inertial.
- Mathematical Formulation: `ΔP_influence = α · NetPolarization`,
  where `NetPolarization = Σ_polarize intensity_i − Σ_depolarize
  intensity_i`.
- Empirical Evidence: Friedkin & Johnsen (1990) [Ref 5, Table 2]
  estimate influence-weight aggregates of `0.05–0.30` per round in
  small-group opinion-change experiments; our default `α = 0.1`
  operates at simulation units (`intensity ∈ [0, 1]`, `polarization
  ∈ [0, 1]`) and reproduces the target polarization-shift-per-round
  of ≈ 10% at `|NetPolarization| = 1`, consistent with the
  net-influence magnitudes reported by Moscovici & Zavalloni (1969)
  [Ref 6] for group-polarization laboratory studies.
- Relevance to This Coordinator: Provides the influence-driven
  polarization change term `α · NetPolarization` in the transition
  equation.
- Calibration Source: Friedkin & Johnsen 1990 [Ref 5, Table 2] and
  Moscovici & Zavalloni 1969 [Ref 6, Table 1]; simulation-unit-adjusted
  range `α ∈ [0.02, 0.30]`.
- Falsification Conditions: If a doubling of `NetPolarization`
  (holding all else constant, including seed for ε) does NOT
  approximately double `ΔP_influence` in a broadcast pair, the
  linear-influence property is broken.
- Alternative Mechanisms: Bounded-confidence non-linear coupling
  (Deffuant et al. 2000) [Ref 4]; threshold-cascade models [Ref 7].

**Group polarization with centripetal moderation (Sunstein 2001;
Moscovici & Zavalloni 1969)**:

- Theory / Study: Deliberative-enclave and echo-chamber group
  polarization with a weak moderation force
- Citation: Sunstein, C. R. (2001). *Echo Chambers: Bush v. Gore,
  Impeachment, and Beyond*. Princeton University Press;
  Moscovici, S., & Zavalloni, M. (1969). "The Group as a Polarizer
  of Attitudes." *Journal of Personality and Social Psychology*,
  12(2), 125–135. DOI: `10.1037/h0027568`
- Core Insight: In populations exposed to homophilic interaction,
  the collective polarization is systematically pulled back toward a
  moderate equilibrium `p*` at a rate that depends on the effective
  weight of bridge builders and cross-cutting exposure, capturing
  the empirically observed slow relaxation of polarization toward
  the population's baseline moderation level.
- Mathematical Formulation: `ΔP_moderation = β · (p* − P(t))`.
- Empirical Evidence: Isenberg (1986) [Ref 8, meta-analysis]
  documents polarization drift toward group extremity of `0.15–0.40`
  standardised units over 10-minute discussions; Del Vicario et al.
  (2016) [Ref 3] show that Facebook opinion clusters relax at
  half-lives of 1–3 weeks in the absence of new content. On a
  round-granularity simulation with 20–100 rounds, `β ∈ [0.02, 0.15]`
  reproduces comparable relative relaxation rates.
- Relevance to This Coordinator: Provides the moderation pull term
  `β · (p* − P(t))` that is required to prevent scenarios from
  drifting monotonically to full polarization.
- Calibration Source: Sunstein 2001 [Ref 1, Ch. 3] and Del Vicario
  et al. 2016 [Ref 3, §Results]; consistent with Moscovici–Zavalloni
  half-life when reinterpreted at round granularity.
- Falsification Conditions: If, holding `NetPolarization = 0` and
  `ε = 0`, ten consecutive broadcasts do NOT monotonically reduce
  `|polarization − p*|`, the centripetal term is broken.
- Alternative Mechanisms: Zero-moderation Deffuant bounded confidence
  [Ref 4]; media-driven equilibrium shifts (Prior 2013) [Ref 9].

**Selective exposure and cluster geometry (Allport 1954; Del Vicario
et al. 2016)**:

- Theory / Study: Homophilic contact and clustered echo chambers as
  the geometry of collective opinion
- Citation: Allport, G. W. (1954). *The Nature of Prejudice*.
  Addison-Wesley;
  Del Vicario, M., et al. (2016). "The Spreading of Misinformation
  Online." *PNAS*, 113(3), 554–559. DOI: `10.1073/pnas.1517441113`
- Core Insight: A population that engages in selective exposure
  develops distinct left/right clusters whose separation grows as
  cross-cutting contact drops; the cross-cutting exposure fraction
  is a leading indicator of imminent polarization jumps.
- Mathematical Formulation:
  `cluster_separation(t) = mean(opinions[opinions ≥ 0]) −
   mean(opinions[opinions < 0])`;
  `cross_cutting_exposure(t) =
   |{i : |opinion_i| < moderate_opinion_threshold}| /
   |actions|`.
- Empirical Evidence: Del Vicario et al. (2016) [Ref 3, Fig. 2]
  document cross-cutting exposure below 8% in echo-chamber
  communities during periods of rapid polarization; our
  moderate_opinion_threshold default of `0.2` reproduces this cutoff
  when the population is bimodal.
- Relevance to This Coordinator: Provides the derived observables
  `cluster_separation` and `cross_cutting_exposure` broadcast
  alongside the primary polarization state.
- Calibration Source: Del Vicario et al. 2016 [Ref 3, §Methods];
  moderate-threshold sensitivity checked over `[0.1, 0.3]`.
- Falsification Conditions: If `cluster_separation` is computed from
  a metric other than the split-mean of submitted opinions (e.g. a
  variance-based proxy) OR if `cross_cutting_exposure` fails to
  respect `moderate_opinion_threshold`, the mechanism has been
  altered.
- Alternative Mechanisms: Variance-based polarization index [Ref 10];
  network-modularity cluster identification [Ref 3].

**Gaussian idiosyncratic noise (population-level residual)**:

- Theory / Study: Zero-mean Gaussian residual for unmodelled
  micro-level heterogeneity in opinion updating
- Citation: DeGroot 1974 [Ref 2]; Friedkin & Johnsen 1990 [Ref 5]
- Core Insight: Even in mechanism-driven opinion fields,
  round-to-round polarization changes carry an irreducible
  idiosyncratic component due to individual-level updating
  heterogeneity not captured by the linear influence term; modelling
  this as zero-mean Gaussian is a widely-adopted simplification.
- Mathematical Formulation: `ε ~ N(0, σ²)`, with σ = `noise_std`.
- Empirical Evidence: Friedkin & Johnsen (1990) [Ref 5, §Discussion]
  report residual variance of `0.01–0.05` in polarization units after
  controlling for observed influence weights; our default
  `σ = 0.02` (in polarization units) corresponds to the low end of
  that range.
- Relevance to This Coordinator: Adds the term `ε` and makes the
  mechanism stochastic-given-seed rather than deterministic.
- Calibration Source: Friedkin & Johnsen 1990 [Ref 5, §Discussion].
- Falsification Conditions: If ε is drawn from a distribution with
  materially non-zero mean or from a non-Gaussian family (fat tails
  from a different generator), the mechanism has been altered.
- Alternative Mechanisms: Heavy-tailed shocks (moral outrage
  cascades) [Ref 11]; state-dependent noise scaling with polarization
  level [Ref 4].

## Activation, Lifecycle, and Coordination Cadence

Purpose: Aggregate all participant polarize/depolarize/neutral
actions each round, apply the linear-influence + centripetal-moderation
+ noise transition to polarization, derive cluster/exposure moments
from submitted opinions, and broadcast one authoritative opinion-field
snapshot.

Coordination Cadence: **every-tick** (one broadcast per simulation
round; the round advances only after `act()` completes).

Lifecycle Mapping (MANDATORY):

- `perceive(observation, prev_result)`:
  1. Read `round_num = observation.round` and write it to
     `state["round"]`.
  2. If `"polarization"` is not yet in `state.custom_state`, run the
     State Initialization block below.
  3. Drain `observation.inbounds`; each inbound payload is a
     participant action dict with `action_type ∈ {polarize,
     depolarize, neutral}`, `intensity ∈ [0, 1]`, `agent_role: str`,
     `opinion ∈ [-1, 1]`.
  4. Validate each action per §4.6.6 Failure Modes (raise `ValueError`
     on out-of-range fields); store the validated action list in
     `state["actions"]` — READ phase only, no field-derived writes.
- `decide()`:
  1. Compute aggregates per §4.6.1 (`total_polarize`,
     `total_depolarize`, `net_polarization`, `submitted_opinions`,
     `left/right split`).
  2. Draw `ε ~ N(0, σ²)` from the seeded RNG.
  3. Compute
     `new_polarization = clip(P(t) + α · NetPolarization +
     β · (p* − P(t)) + ε, 0, 1)`,
     `new_mean_opinion`, `new_cluster_separation`,
     `new_cross_cutting_exposure`. WRITE the new state atomically:
     `prev_polarization ← P(t); polarization ← new_polarization;
     mean_opinion ← …; cluster_separation ← …; cross_cutting_exposure
     ← …; polarization_history.append(new_polarization)` plus the
     other history buffers.
  4. Return the broadcast dict `{polarization, prev_polarization,
     polarization_change, mean_opinion, cluster_separation,
     cross_cutting_exposure, num_polarizers, num_depolarizers,
     net_polarization_intensity, round}` assembled from committed
     state.
- `act(decision)`:
  1. Wrap the dict as `EnvironmentBroadcast` (or engine equivalent)
     with `action_type="environment_broadcast"` and emit to every
     participant via the standard outbox. No writes.

Deviation from the stock-market lifecycle: because
`cluster_separation` and `cross_cutting_exposure` depend on the
submitted-opinion vector — which is only fully known after action
aggregation — the state-write step is placed inside `decide` rather
than `perceive`. `perceive` only validates and stores the raw action
list; `decide` performs the transition and the write. `act` remains
write-free. Implementations MUST preserve this ordering because it is
observable via invariant #1 (see §4.6.6).

State Initialization (MANDATORY):

- Trigger: `"polarization" not in self.state.custom_state`.
- Required extras (raise `KeyError` on missing): `initial_polarization`,
  `initial_mean_opinion`, `initial_cluster_separation`,
  `initial_cross_cutting_exposure`, `polarization_equilibrium`,
  `polarization_impact`, `centripetal_force`, `noise_std`,
  `moderate_opinion_threshold`, `record_path`,
  `custom_state_hot_limit`.
- Initial state writes (single atomic block):
  - `state["polarization"] = extras["initial_polarization"]`
  - `state["prev_polarization"] = extras["initial_polarization"]`
    (equal to current on round 0 — cold-start "no change yet")
  - `state["mean_opinion"] = extras["initial_mean_opinion"]`
  - `state["cluster_separation"] =
    extras["initial_cluster_separation"]`
  - `state["cross_cutting_exposure"] =
    extras["initial_cross_cutting_exposure"]`
  - `state["polarization_history"] = HistoryBuffer(
    folder=<record>/<identity>/polarization, entry_limit=hot_limit)`
  - Similar `HistoryBuffer` instances for `mean_opinion_history`,
    `cluster_separation_history`, `polarize_count_history`,
    `depolarize_count_history`.
- Warm-up rounds: `0` (broadcast is trustworthy from round 0, though
  `prev_polarization == polarization` on round 0 must be interpreted
  correctly by participants).
- Cold-start reading rule for participants: on round 0,
  `prev_polarization == polarization`, so the participant-side
  polarization-change signal SHOULD be treated as "no observation
  yet" rather than "change of zero".

Inbound Message Types:

- **SocialAction**: `{"action_type": "polarize" | "depolarize" |
  "neutral", "intensity": float ∈ [0, 1], "agent_role": str,
  "opinion": float ∈ [-1, 1]}`.
  - `polarize` / `depolarize` with `intensity > 0` contribute to the
    net-polarization aggregate.
  - `neutral` or `intensity == 0` are counted in `n_active` logging
    but do not shift polarization.
  - `opinion` participates in the mean-opinion, cluster-separation,
    and cross-cutting-exposure derivations regardless of
    `action_type`.
- **Default (no message)**: treated as `neutral` with `intensity = 0`
  and `opinion` omitted from moment computation.

Broadcast Trigger: after every round tick, at the end of `decide`
following the state-write phase.

Missing-Input Policy:

- Missing required extras → **raise `KeyError`** from `perceive`; do
  NOT default.
- Zero inbound actions → set `total_polarize = total_depolarize =
  net_polarization = 0`; carry forward `mean_opinion`,
  `cluster_separation`, `cross_cutting_exposure` from previous round.
- Individual action with `action_type` outside the valid set → raise
  `ValueError` from `perceive` (halt-on-invalid).
- Individual action with `intensity` outside `[0, 1]` or `opinion`
  outside `[-1, 1]` → raise `ValueError` from `perceive`
  (halt-on-invalid).
- `NaN` / `Inf` in the computed `new_polarization` → **raise
  `ValueError`** from `decide`; do NOT emit a broadcast this round.
- NEVER silently substitute a default for a required field.

Exogenous Driver Boundary (MANDATORY):

- This coordinator MUST NOT generate exogenous media events, moral
  shocks, or algorithmic-feed changes from within its own logic.
- Equilibrium changes (e.g. media-driven baseline shifts) enter via
  either (a) a distinguished inbound message from a scenario-provided
  `MediaEnvironmentAgent`, in which case `perceive` reads it as an
  ordinary aggregate signal that shifts `state[
  "polarization_equilibrium"]`, OR (b) a mutation of `config.extras[
  "polarization_equilibrium"]` by the scenario runner performed
  BEFORE this coordinator's `perceive`. The coordinator itself
  remains passive.

Environmental Dependencies:

- Required extras (see §4.7): `initial_polarization`,
  `initial_mean_opinion`, `initial_cluster_separation`,
  `initial_cross_cutting_exposure`, `polarization_equilibrium`,
  `polarization_impact`, `centripetal_force`, `noise_std`,
  `moderate_opinion_threshold`, `record_path`,
  `custom_state_hot_limit`.
- Optional extras: none in the default profile.
- No scenario driver signals are required beyond what enters via the
  Exogenous Driver Boundary.

## Coordination Framework

#### I/O Contract **(MANDATORY, contract-strength)**

##### Inputs (per coordination call)

| Input               | Source                          | Type / Shape                                                                                                       | Required? | Notes                                                                    |
|---------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------|
| `inbound_actions`   | mailbox from participant agents | `list[dict]`; each dict has `action_type: str`, `intensity: float`, `agent_role: str`, `opinion: float`             | yes       | `opinion` participates in moment computation regardless of action_type    |
| `current_state`     | coordinator's persisted state   | `{"polarization": float, "mean_opinion": float, "cluster_separation": float, "cross_cutting_exposure": float, ...}` | yes       | Populated on first call by State Initialization                          |
| `context_metadata`  | scheduler / round header        | `{"round": int, "identity": str, "seed": int}`                                                                     | yes       | Identity naming: `{variant}_environment_opinion`                          |
| `scenario_driver`   | scenario overlay                | `dict` or `None`                                                                                                   | no        | Only if scenario declares exogenous equilibrium changes                   |

##### Outputs (per coordination call)

The coordinator emits exactly one broadcast dict per call. Every
participant sees the identical dict.

| Field                       | Type   | Valid Range / Enum          | Unit               | Required? | Meaning                                                             |
|-----------------------------|--------|-----------------------------|--------------------|-----------|---------------------------------------------------------------------|
| `polarization`              | float  | `[0, 1]`                    | polarization index | yes       | Post-transition polarization P(t+1) for this round                   |
| `prev_polarization`         | float  | `[0, 1]`                    | polarization index | yes       | Polarization broadcast in the previous round (P(t))                  |
| `polarization_change`       | float  | `[-1, 1]`                   | polarization index | yes       | `polarization − prev_polarization`                                   |
| `mean_opinion`              | float  | `[-1, 1]`                   | opinion units      | yes       | Population-average submitted opinion this round                      |
| `cluster_separation`        | float  | `[0, 2]`                    | opinion units      | yes       | `mean(opinions[≥0]) − mean(opinions[<0])`                            |
| `cross_cutting_exposure`    | float  | `[0, 1]`                    | fraction           | yes       | Fraction of actions with `|opinion| < moderate_opinion_threshold`     |
| `num_polarizers`            | int    | `≥ 0`                       | count              | yes       | Number of `polarize` actions this round                              |
| `num_depolarizers`          | int    | `≥ 0`                       | count              | yes       | Number of `depolarize` actions this round                            |
| `net_polarization_intensity`| float  | any                         | intensity units    | yes       | `total_polarize − total_depolarize`                                  |
| `round`                     | int    | `≥ 0`                       | —                  | yes       | Round number that produced this broadcast                             |

Any participant reading a field NOT listed here indicates a
downstream bug — this contract is the exhaustive schema.

##### Content Constraints

- **Required fields**: all ten fields above MUST be present every
  round.
- **Forbidden fields**: fields not declared above MUST NOT be added
  (silently breaks downstream parsers that read participant broadcasts
  as fixed-schema dicts).
- **Value ranges**: `polarization`, `cross_cutting_exposure` clipped
  to `[0, 1]` before emission; `mean_opinion` clipped to `[-1, 1]`;
  `cluster_separation` clipped to `[0, 2]`; all fields
  numeric-finite (no NaN / Inf — enforced by the Missing-Input
  Policy above).
- **Units and sign conventions**: `polarization ∈ [0, 1]` where `0`
  = perfectly moderate consensus and `1` = maximum bimodal
  polarization; `mean_opinion ∈ [-1, 1]` where sign encodes ideological
  direction; `cluster_separation` is always non-negative by
  construction (right-mean ≥ left-mean because the split uses `≥ 0`
  vs `< 0`).
- **Determinism markers**: the seed used for ε on each round MUST
  be recoverable from the round number plus the coordinator's base
  seed; two runs with identical seed + identical action sequence +
  identical submitted opinions produce byte-equal broadcasts.

##### Serialization Format

Broadcast payload is a **plain Python `dict`** (no `<analysis>` /
`<decision>` tags — those bind participant agents, not coordinators).
The canonical shape is:

```json
{
  "polarization":               0.523,
  "prev_polarization":          0.501,
  "polarization_change":        0.022,
  "mean_opinion":              -0.081,
  "cluster_separation":         0.845,
  "cross_cutting_exposure":     0.14,
  "num_polarizers":            18,
  "num_depolarizers":           7,
  "net_polarization_intensity": 6.2,
  "round":                     12
}
```

Every implementation variant (`Rule`, `LLM`, `RuleLLM`, `Rag` or any
scheme declared in the target's §10.1) that instantiates this
coordinator MUST emit the identical dict shape. LLM-side variants
never wrap the broadcast in narrative text — the coordinator is
rule-executed even when participants are model-driven.

##### Implementer Contract Reminder

1. **Extras wiring** — every broadcast field's producing formula
   uses only inbound aggregates or `config.extras` keys declared
   in §4.7. No hidden constants.
2. **Broadcast emission** — `decide` populates every `Required = yes`
   field; `polarization` and `cross_cutting_exposure` are clipped to
   `[0, 1]`, `mean_opinion` clipped to `[-1, 1]`, and
   `cluster_separation` derived from the split-mean formula BEFORE
   the state-write, not later.
3. **Format-layer compatibility** — the broadcast satisfies the
   participant-side format contract for opinion-domain scenarios.
   Implementers MUST NOT silently omit any required field; the
   participant-side parser is entitled to raise on missing keys.
4. **Variant parity** — every declared variant emits the same
   10-field dict.
5. **Contract-versus-prose conflict resolution** — if the mechanism
   in §4.6.2 or the parameters in §4.7 seem to contradict this
   contract, the contract wins.

#### Input Aggregation Rules

| Aggregate signal          | Derivation                                                                        | Rationale                                                              |
|---------------------------|-----------------------------------------------------------------------------------|------------------------------------------------------------------------|
| `total_polarize`          | `sum(a["intensity"] for a in actions if a["action_type"]=="polarize")`             | Total polarization pressure this round                                  |
| `total_depolarize`        | `sum(a["intensity"] for a in actions if a["action_type"]=="depolarize")`           | Total depolarization pressure this round                                |
| `net_polarization`        | `total_polarize − total_depolarize`                                                | Signed influence driving α term                                         |
| `submitted_opinions`      | `[a["opinion"] for a in actions if a["opinion"] is not None]`                      | Basis for mean-opinion and cluster split                                |
| `left_opinions`           | `[o for o in submitted_opinions if o < 0]`                                         | Left cluster for cluster_separation                                     |
| `right_opinions`          | `[o for o in submitted_opinions if o ≥ 0]`                                         | Right cluster for cluster_separation                                    |
| `center_agents`           | `sum(1 for a in actions if |a["opinion"]| < moderate_opinion_threshold)`           | Numerator for cross_cutting_exposure                                    |
| `n_active`                | `len([a for a in actions if a["action_type"] != "neutral"])`                       | Count of non-neutral participants; used only for logging                |

Does NOT use: individual participant identities; participant
`agent_role` (label is stored but not aggregated); peer-to-peer
topology; any private state of individual participants.

Completeness rule check: all eight aggregates above are consumed in
§4.6.2 (net_polarization in step 4; submitted_opinions/left/right in
step 6; center_agents in step 7; n_active in step 8 logging).

#### Core Coordination Mechanism

1. **READ** `round_num`, `inbound_actions` from `observation`. Read
   `state["polarization"] = P(t)` and extras
   `{α = polarization_impact, β = centripetal_force, σ = noise_std,
   p* = polarization_equilibrium, τ = moderate_opinion_threshold}`.
   Traces to §4.4 DeGroot 1974 + Sunstein 2001 readings.
2. **VALIDATE** each action against valid types (`polarize`,
   `depolarize`, `neutral`), intensity range `[0, 1]`, opinion range
   `[-1, 1]`; raise `ValueError` on violation. Traces to §4.6.6
   Failure Modes.
3. **COMPUTE** aggregates from §4.6.1: `total_polarize`,
   `total_depolarize`, `net_polarization`, `submitted_opinions`,
   `left_opinions`, `right_opinions`, `center_agents`.
4. **COMPUTE** the noise draw `ε = rng.gauss(0, σ)` from the seeded
   RNG. Traces to §4.4 Gaussian residual.
5. **COMPUTE** the raw transition:
   `P_raw = P(t) + α · net_polarization + β · (p* − P(t)) + ε`.
   Traces to §4.4 DeGroot 1974 (first term), Sunstein 2001 (second
   term).
6. **COMPUTE** the clip:
   `new_polarization = clip(P_raw, 0, 1)`. Traces to §4.6.6 invariant
   #5 (polarization stays in [0, 1]).
7. **COMPUTE** derived moments:
   `new_mean_opinion = mean(submitted_opinions) if non-empty else
   prev`; `new_cluster_separation =
   mean(right_opinions) − mean(left_opinions)` (each mean defaults to
   `0` if its side is empty); `new_cross_cutting_exposure =
   center_agents / len(actions) if actions else prev`. Traces to §4.4
   Del Vicario et al. 2016.
8. **WRITE** atomically in this order:
   `state["prev_polarization"] = P(t)`;
   `state["polarization"] = new_polarization`;
   `state["mean_opinion"] = new_mean_opinion`;
   `state["cluster_separation"] = new_cluster_separation`;
   `state["cross_cutting_exposure"] = new_cross_cutting_exposure`;
   `polarization_history.append(new_polarization)` (and the four
   sibling history buffers). Traces to §4.6.6 invariant #1.
9. **EMIT** in `decide` the 10-field dict `{polarization,
   prev_polarization, polarization_change, mean_opinion,
   cluster_separation, cross_cutting_exposure, num_polarizers,
   num_depolarizers, net_polarization_intensity, round}`. Traces to
   §4.6.0 Outputs.

#### Broadcast Space

| Aspect                       | Specification                                                                                                              |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| Broadcast fields             | `polarization`, `prev_polarization`, `polarization_change`, `mean_opinion`, `cluster_separation`, `cross_cutting_exposure`, `num_polarizers`, `num_depolarizers`, `net_polarization_intensity`, `round` (verbatim §4.6.0 Outputs) |
| State transition rule        | `P(t+1) = clip(P(t) + α·net_polarization + β·(p* − P(t)) + ε, 0, 1)`                                                       |
| Value bounds                 | `polarization ∈ [0, 1]`, `mean_opinion ∈ [-1, 1]`, `cluster_separation ∈ [0, 2]`, `cross_cutting_exposure ∈ [0, 1]`         |
| Freshness policy             | Every-tick; broadcast reflects state committed in the current `decide`                                                     |
| Revision policy              | No — a broadcast MUST NOT be retracted or amended within a round; if a bug is detected, the round is aborted (see Failure Modes) |
| State-history retention      | Hot buffer of `custom_state_hot_limit` (default 10000) entries with cold spill to `<record_path>/<identity>/…` via `HistoryBuffer` |
| Resource cap                 | Unbounded on-disk (history spills); RAM bounded by hot-limit                                                               |
| Termination rule             | Coordinator stops broadcasting when `round == total_rounds`; the simulation runner handles shutdown                        |

#### Mathematical Model

1. **Broadcast outputs**:
   - `polarization ∈ [0, 1] ⊂ ℝ`
   - `prev_polarization ∈ [0, 1] ⊂ ℝ`
   - `polarization_change ∈ [-1, 1] ⊂ ℝ`
   - `mean_opinion ∈ [-1, 1] ⊂ ℝ`
   - `cluster_separation ∈ [0, 2] ⊂ ℝ`
   - `cross_cutting_exposure ∈ [0, 1] ⊂ ℝ`
   - `num_polarizers, num_depolarizers ∈ ℤ⁺ ∪ {0}`
   - `net_polarization_intensity ∈ ℝ`
   - `round ∈ ℤ⁺ ∪ {0}`

2. **State transition logic**:
   ```
   P(t+1) = clip( P(t) + α · NetPolarization(t) + β · (p* − P(t)) + ε(t),
                  0, 1 )
   ε(t)   ~ N(0, σ²)   — one draw per round, seeded by (base_seed, t)
   NetPolarization(t) = Σ_{i: action_i.type == "polarize"}   intensity_i
                      − Σ_{i: action_i.type == "depolarize"} intensity_i
   mean_opinion(t)       = mean(submitted_opinions)   if non-empty else carry-forward
   cluster_separation(t) = mean(right_opinions) − mean(left_opinions)
                                              (each side → 0 if empty)
   cross_cutting_exposure(t) = |{i : |opinion_i| < τ}| / |actions|
                                              (carry-forward if |actions| = 0)
   ```

3. **State variables**:

   | Variable                       | Type            | Initial value                                                              |
   |--------------------------------|-----------------|----------------------------------------------------------------------------|
   | `polarization`                 | float           | `extras["initial_polarization"]`                                           |
   | `prev_polarization`            | float           | `extras["initial_polarization"]`                                           |
   | `mean_opinion`                 | float           | `extras["initial_mean_opinion"]`                                           |
   | `cluster_separation`           | float           | `extras["initial_cluster_separation"]`                                     |
   | `cross_cutting_exposure`       | float           | `extras["initial_cross_cutting_exposure"]`                                 |
   | `polarization_history`         | `HistoryBuffer` | empty, `<record>/<identity>/polarization`, hot_limit                        |
   | `mean_opinion_history`         | `HistoryBuffer` | empty                                                                      |
   | `cluster_separation_history`   | `HistoryBuffer` | empty                                                                      |
   | `polarize_count_history`       | `HistoryBuffer` | empty                                                                      |
   | `depolarize_count_history`     | `HistoryBuffer` | empty                                                                      |
   | `round`                        | int             | `0`                                                                        |

4. **State evolution ordering**: all state writes happen at the end
   of `decide` (step 8 of §4.6.2), AFTER the transition computation
   and BEFORE the broadcast dict is returned. `prev_polarization` is
   written before `polarization` so that invariant #1 holds; both use
   the pre-transition value.

5. **Determinism contract**: **stochastic-given-seed**. The single
   randomness source is the Gaussian draw for ε. The RNG is seeded
   from a base seed provided at construction plus the round number,
   so two runs with the same base seed and identical inbound-action
   sequences produce byte-equal broadcasts.

6. **Parameter symbol table**:

   | Symbol                        | Meaning                                                | Default Value | Source                                       |
   |-------------------------------|--------------------------------------------------------|---------------|----------------------------------------------|
   | `α`                           | Polarization impact per unit of net influence          | `0.1`         | DeGroot 1974 [Ref 2]; Friedkin–Johnsen [Ref 5] |
   | `β`                           | Centripetal moderation rate toward `p*`                | `0.02`        | Sunstein 2001 [Ref 1]                          |
   | `σ`                           | Std dev of Gaussian noise per round                    | `0.02`        | Friedkin–Johnsen 1990 [Ref 5]                  |
   | `p*`                          | Polarization equilibrium (moderation anchor)           | `0.2`         | Scenario config                                |
   | `τ`                           | Moderate-opinion threshold for cross-cutting exposure  | `0.2`         | Del Vicario et al. 2016 [Ref 3]                |
   | `P(0)`                        | Initial polarization                                   | `0.3`         | Scenario config                                |
   | `t`                           | Round index                                            | `0` at start  | Scheduler                                      |

#### Coordination Properties

- **Time granularity**: round-based (one tick per participant action
  round).
- **Feedback loop**: mixed — centripetal moderation produces negative
  feedback around `p*`; sustained one-sided net-polarization
  produces positive-feedback polarization drift; the crossover
  depends on parameter ratio `α/β` and the persistence of
  `net_polarization`.
- **Information environment**: symmetric — every participant sees
  the identical broadcast. Private opinion state exists only inside
  participant profiles.
- **Stochasticity profile**: one Gaussian ε draw per round; no
  other randomness inside the coordinator.

#### Invariants and Failure Modes **(MANDATORY)**

Round-boundary Invariants:

| # | Invariant                                                                                              | Enforcement                                              |
|---|--------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| 1 | `broadcast[t+1].prev_polarization == broadcast[t].polarization` (byte-equal float)                     | §4.6.2 step 8 writes `prev_polarization ← P(t)` first    |
| 2 | Every required field in §4.6.0 Outputs is present and non-null                                         | `decide` assertion at emit                                |
| 3 | `polarization, cross_cutting_exposure ∈ [0, 1]` in every broadcast                                     | §4.6.2 step 6, step 7 clip                                |
| 4 | `mean_opinion ∈ [-1, 1]` in every broadcast                                                            | Implicit from opinion validation + averaging              |
| 5 | `cluster_separation ≥ 0` in every broadcast                                                            | Split formula (right-mean ≥ left-mean by construction)    |
| 6 | `broadcast[t+1].round == broadcast[t].round + 1`                                                       | Set from `observation.round` in `perceive`                |
| 7 | `polarization_equilibrium` (`p*`) unchanged across rounds UNLESS Exogenous Driver Boundary is invoked  | §4.5 boundary rule                                        |
| 8 | Two runs with identical `base_seed` and identical inbound-action sequence produce byte-equal broadcasts | Seeded RNG only                                          |
| 9 | `polarization_change == polarization − prev_polarization`                                              | §4.6.2 emission step                                      |

Domain-Specific Invariants:

- **Cluster non-inversion**: `cluster_separation ≥ 0` by
  construction, since the right cluster is defined as opinions `≥ 0`
  and the left cluster as opinions `< 0` — invariant #5.
- **Exposure fraction validity**: `cross_cutting_exposure ∈ [0, 1]`
  by construction (fraction of a non-empty set with carry-forward on
  empty).
- **No cross-round leakage**: each history buffer grows by exactly 1
  entry per round.
- **Conservation**: not applicable — the coordinator is
  polarization-forming only, not authoritative for individual
  participant opinions.

Failure Modes:

| Condition                                                       | Coordinator behaviour                                       | Broadcast effect                                              |
|-----------------------------------------------------------------|-------------------------------------------------------------|---------------------------------------------------------------|
| Zero inbound actions                                            | Continue; carry forward `mean_opinion`, `cluster_separation`, `cross_cutting_exposure` from previous round; `net_polarization = 0` | Broadcast with pure centripetal-moderation + noise move        |
| All polarizers (`total_depolarize = 0`)                         | Continue                                                    | Amplifying pressure on `polarization`                          |
| All depolarizers (`total_polarize = 0`)                         | Continue                                                    | Damping pressure on `polarization`                             |
| Action with invalid `action_type`                               | Raise `ValueError` from `perceive`                           | No broadcast; simulation halts                                 |
| Action with `intensity` outside `[0, 1]`                        | Raise `ValueError` from `perceive`                           | No broadcast; simulation halts                                 |
| Action with `opinion` outside `[-1, 1]`                         | Raise `ValueError` from `perceive`                           | No broadcast; simulation halts                                 |
| Empty left OR right cluster (all opinions same sign)            | Default missing side's mean to `0`; compute cluster_separation normally | Broadcast reflects one-sided cluster geometry                  |
| Required extras key missing                                     | Raise `KeyError` from `perceive`                             | No broadcast; simulation halts                                 |
| `new_polarization` computes to NaN / Inf                        | Raise `ValueError` from `decide`                             | No broadcast; simulation halts (implementation defect)         |
| Scenario driver mutates `extras["polarization_equilibrium"]` mid-run | Next `perceive` reads new value; log the change             | Next broadcast reflects the new equilibrium                    |
| `HistoryBuffer` disk write fails                                | Raise from `decide`; do NOT emit stale broadcast             | No broadcast; simulation halts                                 |

## Environmental Parameters

### 4.7.1 Parameter Categorisation

#### A. Initial Conditions

| Parameter                          | Type  | Default | Valid Range | Sensitivity | Description                                        | Impact                                          | Source                          |
|------------------------------------|-------|---------|-------------|-------------|----------------------------------------------------|-------------------------------------------------|---------------------------------|
| `initial_polarization`             | float | `0.3`   | `[0, 1]`    | high        | Round-0 polarization seed                          | Higher → higher starting bimodality              | Scenario config (Sunstein 2001) |
| `initial_mean_opinion`             | float | `0.0`   | `[-1, 1]`   | medium      | Round-0 mean-opinion seed                          | Sign encodes initial ideological tilt            | Scenario config                 |
| `initial_cluster_separation`       | float | `0.0`   | `[0, 2]`    | low         | Round-0 cluster-separation seed                    | Higher → starting geometry already clustered     | Scenario config                 |
| `initial_cross_cutting_exposure`   | float | `0.5`   | `[0, 1]`    | medium      | Round-0 cross-cutting-exposure seed                | Higher → less initial homophily                  | Scenario config                 |

#### B. Mechanism Coefficients

| Parameter                    | Type  | Default | Valid Range | Sensitivity | Description                                                    | Impact                                                              | Source                             |
|------------------------------|-------|---------|-------------|-------------|----------------------------------------------------------------|---------------------------------------------------------------------|------------------------------------|
| `polarization_impact`        | float | `0.1`   | `≥ 0`       | high        | α — polarization move per unit of net influence                 | Higher → 2× more responsive to influence imbalance                  | DeGroot 1974 [Ref 2]; Friedkin–Johnsen [Ref 5] |
| `centripetal_force`          | float | `0.02`  | `[0, 1]`    | high        | β — moderation pull rate toward `p*`                            | Higher → faster relaxation to equilibrium; halves relaxation half-life | Sunstein 2001 [Ref 1]              |
| `noise_std`                  | float | `0.02`  | `≥ 0`       | medium      | σ — Gaussian noise std dev added per round                      | Higher → more idiosyncratic polarization oscillation                | Friedkin–Johnsen 1990 [Ref 5]      |
| `polarization_equilibrium`   | float | `0.2`   | `[0, 1]`    | high        | `p*` — anchor for centripetal moderation                        | Higher → moderation pulls toward more-polarized equilibrium         | Scenario config                    |
| `moderate_opinion_threshold` | float | `0.2`   | `(0, 1]`    | medium      | τ — cutoff below which an opinion counts as moderate            | Higher → more agents classed as cross-cutting                       | Del Vicario et al. 2016 [Ref 3]    |

#### C. Structural / Boundary Parameters

None. The `[0, 1]` polarization clip and `[-1, 1]` opinion range are
domain-fundamental invariants, not tunable parameters.

#### D. Recording / Infrastructure Parameters

| Parameter                | Type | Default    | Valid Range | Sensitivity | Description                              | Impact                              | Source        |
|--------------------------|------|------------|-------------|-------------|------------------------------------------|-------------------------------------|---------------|
| `record_path`            | str  | `""`       | non-empty   | low         | Root directory for HistoryBuffer spills  | Higher size → more disk footprint   | Standardised  |
| `custom_state_hot_limit` | int  | `10000`    | `≥ 1`       | low         | HistoryBuffer hot-tier size (entries)    | Higher → more RAM, less disk I/O    | Standardised  |

## Worked Numerical Examples

### Case 1 — Polarization pressure round (positive net polarization, inside moderation band)

System state (round `t = 3`):

- `P(t) = 0.35`, `p* = 0.2`, `α = 0.1`, `β = 0.02`, `σ = 0.02`,
  `τ = 0.2`.
- Inbound actions:
  - 3 polarizers: intensity 0.8/0.6/0.5, opinions 0.9/-0.85/0.75
  - 2 depolarizers: intensity 0.4/0.3, opinions 0.05/-0.10
  - 1 neutral: intensity 0.0, opinion 0.15

Calculation:

- `total_polarize = 0.8 + 0.6 + 0.5 = 1.9`
- `total_depolarize = 0.4 + 0.3 = 0.7`
- `net_polarization = 1.2`
- `submitted_opinions = [0.9, -0.85, 0.75, 0.05, -0.10, 0.15]`
  (6 entries)
- `left_opinions = [-0.85, -0.10]`, `left_mean = -0.475`
- `right_opinions = [0.9, 0.75, 0.05, 0.15]`, `right_mean = 0.4625`
- `center_agents = |{o : |o| < 0.2}| = |{0.05, -0.10, 0.15}| = 3`
- `ε` draw `= +0.005`.
- Influence term: `0.1 · 1.2 = +0.12`
- Moderation term: `0.02 · (0.2 − 0.35) = −0.003`
- `P_raw = 0.35 + 0.12 − 0.003 + 0.005 = 0.472`
- Clip: `clip(0.472, 0, 1) = 0.472`
- Mean opinion: `sum / 6 ≈ 0.15`
- Cluster separation: `0.4625 − (−0.475) = 0.9375`
- Cross-cutting exposure: `3 / 6 = 0.5`

Decision (broadcast dict):

```json
{"polarization": 0.472, "prev_polarization": 0.35,
 "polarization_change": 0.122, "mean_opinion": 0.15,
 "cluster_separation": 0.9375, "cross_cutting_exposure": 0.5,
 "num_polarizers": 3, "num_depolarizers": 2,
 "net_polarization_intensity": 1.2, "round": 3}
```

### Case 2 — Depolarization pressure round (negative net polarization)

System state (round `t = 4`, following Case 1):

- `P(t) = 0.472`, `p* = 0.2`, same coefficients.
- Inbound actions:
  - 1 polarizer: intensity 0.3, opinion 0.85
  - 4 depolarizers: intensity 0.7/0.6/0.5/0.4, opinions
    0.1/-0.15/0.05/-0.05

Calculation:

- `total_polarize = 0.3`, `total_depolarize = 2.2`,
  `net_polarization = -1.9`
- `submitted_opinions = [0.85, 0.1, -0.15, 0.05, -0.05]` (5 entries)
- `left_opinions = [-0.15, -0.05]`, `left_mean = -0.10`
- `right_opinions = [0.85, 0.1, 0.05]`, `right_mean = 0.333`
- `center_agents = |{0.1, -0.15, 0.05, -0.05}| = 4`
- `ε` draw `= -0.008`.
- Influence term: `0.1 · (-1.9) = -0.19`
- Moderation term: `0.02 · (0.2 − 0.472) = -0.00544`
- `P_raw = 0.472 − 0.19 − 0.00544 − 0.008 = 0.269`
- Clip: `clip(0.269, 0, 1) = 0.269`
- Mean opinion: `(0.85+0.1−0.15+0.05−0.05)/5 = 0.16`
- Cluster separation: `0.333 − (−0.10) = 0.433`
- Cross-cutting exposure: `4/5 = 0.8`

Decision:

```json
{"polarization": 0.269, "prev_polarization": 0.472,
 "polarization_change": -0.203, "mean_opinion": 0.16,
 "cluster_separation": 0.433, "cross_cutting_exposure": 0.8,
 "num_polarizers": 1, "num_depolarizers": 4,
 "net_polarization_intensity": -1.9, "round": 4}
```

Invariant #1 check: `broadcast[4].prev_polarization ==
broadcast[3].polarization == 0.472` ✓.

### Case 3 — Balanced round (zero net polarization, centripetal moderation dominates)

System state (round `t = 5`, following Case 2):

- `P(t) = 0.269`, `p* = 0.2`, same coefficients.
- Inbound actions:
  - 2 polarizers: intensity 0.5/0.5, opinions 0.7/-0.7
  - 2 depolarizers: intensity 0.5/0.5, opinions 0.05/0.10
  - 1 neutral: intensity 0.0, opinion 0.0

Calculation:

- `total_polarize = 1.0`, `total_depolarize = 1.0`,
  `net_polarization = 0`
- `submitted_opinions = [0.7, -0.7, 0.05, 0.10, 0.0]` (5)
- `left_opinions = [-0.7]`, `left_mean = -0.7`
- `right_opinions = [0.7, 0.05, 0.10, 0.0]`, `right_mean = 0.2125`
- `center_agents = |{0.05, 0.10, 0.0}| = 3`
- `ε` draw `= +0.003`.
- Influence term: `0`
- Moderation term: `0.02 · (0.2 − 0.269) = -0.00138`
- `P_raw = 0.269 + 0 − 0.00138 + 0.003 = 0.271`
- Mean opinion: `0.15/5 = 0.03`
- Cluster separation: `0.2125 − (−0.7) = 0.9125`
- Cross-cutting exposure: `3/5 = 0.6`

Decision:

```json
{"polarization": 0.271, "prev_polarization": 0.269,
 "polarization_change": 0.002, "mean_opinion": 0.03,
 "cluster_separation": 0.9125, "cross_cutting_exposure": 0.6,
 "num_polarizers": 2, "num_depolarizers": 2,
 "net_polarization_intensity": 0.0, "round": 5}
```

Observation: with zero net polarization, the polarization moves
almost entirely due to the moderation term (small pull toward `p*`)
plus noise.

### Edge Case — Cold-start (round 0) + zero actions

System state (round `t = 0`, first call):

- `state.custom_state` is empty. `initial_polarization = 0.3`,
  `p* = 0.2`, `α = 0.1`, `β = 0.02`, `σ = 0.02`, `τ = 0.2`.
- Inbound actions: none (all participants also in cold-start
  `perceive` and produced no actions yet).

Calculation:

- State Initialization runs: `polarization ← 0.3`,
  `prev_polarization ← 0.3` (cold-start convention: equal to
  current), `mean_opinion ← 0.0`, `cluster_separation ← 0.0`,
  `cross_cutting_exposure ← 0.5`, history buffers instantiated
  empty.
- Aggregates: `net_polarization = 0`, `submitted_opinions = []`.
- `ε` draw `= -0.005`.
- `P_raw = 0.3 + 0 + 0.02·(0.2 − 0.3) − 0.005 = 0.293`.
- Mean opinion: no submissions → carry forward `0.0`.
- Cluster separation: empty splits → both means default to `0`;
  `cluster_separation = 0.0`.
- Cross-cutting exposure: `len(actions) == 0` → carry forward `0.5`.

Decision:

```json
{"polarization": 0.293, "prev_polarization": 0.3,
 "polarization_change": -0.007, "mean_opinion": 0.0,
 "cluster_separation": 0.0, "cross_cutting_exposure": 0.5,
 "num_polarizers": 0, "num_depolarizers": 0,
 "net_polarization_intensity": 0.0, "round": 0}
```

Cold-start reading rule for participants: because
`prev_polarization == 0.3 == initial_polarization`, participants MUST
treat this as "no polarization-change observation yet" rather than
"change of −0.007".

## Coordinator Verification and Calibration

**Calibration data sources**:

- `polarization_impact` (α) ← Friedkin–Johnsen 1990 [Ref 5, Table 2]
  and Moscovici–Zavalloni 1969 [Ref 6, Table 1].
  Simulation-unit-adjusted range: `[0.02, 0.30]`.
- `centripetal_force` (β) ← Sunstein 2001 [Ref 1, Ch. 3] and
  Del Vicario et al. 2016 [Ref 3] half-life reinterpretation. Range:
  `[0.005, 0.15]`.
- `noise_std` (σ) ← Friedkin–Johnsen 1990 [Ref 5, §Discussion].
  Range: `[0.005, 0.10]` in polarization units.
- `moderate_opinion_threshold` (τ) ← Del Vicario et al. 2016 [Ref 3,
  §Methods]. Range: `[0.1, 0.3]`.

**Expected coordinator behaviour** (given `p* = 0.2`, defaults):

- Given `net_polarization = +1.2` and `ε = 0`, the coordinator MUST
  push polarization up by `≈ +0.12` minus any small moderation pull.
- Given `net_polarization = 0`, `P(t) = 0.5`, and `ε = 0`, the
  coordinator MUST push polarization toward `p*`, producing a
  broadcast with `polarization_change` strictly negative.
- Given `net_polarization = 0`, `P(t) = 0.2`, and `ε = 0`, the
  coordinator MUST emit `polarization == 0.2` exactly (no drift from
  any source).
- Given identical `base_seed` and identical inbound-action sequence,
  the coordinator MUST produce byte-equal broadcasts across two
  independent runs.

**Sanity bounds** (red flags for a broken implementation):

- IF `broadcast[t+1].prev_polarization != broadcast[t].polarization`
  THEN the state-write ordering is broken (invariant #1).
- IF any broadcast omits a `Required = yes` field THEN the contract
  is broken (invariant #2).
- IF `polarization` falls outside `[0, 1]` THEN the clip is broken
  (invariant #3).
- IF `net_polarization > 0` AND `centripetal_force == 0` AND
  `noise_std == 0` YET `polarization` falls THEN the sign convention
  is broken.
- IF `net_polarization == 0` AND `polarization == polarization_equilibrium`
  YET `noise_std == 0` YET `polarization` changes across rounds THEN
  the transition equation has a spurious drift term.
- IF two runs with identical seed + actions produce different
  broadcasts THEN the RNG seeding is broken (invariant #8).
- IF `cluster_separation` is negative in any broadcast THEN the
  split-mean formula is broken (invariant #5).

### Ablation Hooks

| Ablation name         | Setting                | Hypothesis tested                                                        | Expected direction                                       | Metric                                                              |
|-----------------------|------------------------|--------------------------------------------------------------------------|----------------------------------------------------------|---------------------------------------------------------------------|
| `no-moderation`       | `β = 0`                | Removes centripetal anchor; polarization trajectory becomes influence-only | Higher variance of `polarization` over 100 rounds        | `Var(polarization) − baseline`                                       |
| `zero-influence`      | `α = 0`                | Actions no longer move polarization; only moderation + noise remain       | Polarization → `p*`                                       | `mean_over_rounds(|polarization − p*|)` shrinks near 0                |
| `high-noise`          | `σ *= 10`              | Overwhelms deterministic signal                                          | Random-walk-like broadcast series                        | `Autocorr(polarization_change, lag=1) → 0`                            |
| `no-noise`            | `σ = 0`                | Fully deterministic given actions                                        | Identical replay across seeds                            | `max_over_seeds(|broadcast_a − broadcast_b|) = 0`                     |
| `narrow-moderation`   | `τ = 0.05`             | Only strict-centrists count as cross-cutting                             | Cross-cutting exposure drops even with mild opinions      | `mean(cross_cutting_exposure) − baseline` becomes negative            |
| `high-equilibrium`    | `p* = 0.6`             | Anchor pulls toward a more-polarized equilibrium                          | Long-run polarization settles at `p*`                     | `mean_over_last_10_rounds(polarization) ≈ p*`                          |

## Academic / Empirical References

| #  | Citation                                                                                                                                                                        | Notes                                                                                          |
|----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 1  | Sunstein, C. R. (2001). *Echo Chambers: Bush v. Gore, Impeachment, and Beyond*. Princeton University Press. ISBN: 978-0691070254                                                | Origin of echo-chamber and deliberative-enclave polarization; centripetal-moderation basis      |
| 2  | DeGroot, M. H. (1974). Reaching a Consensus. *Journal of the American Statistical Association*, 69(345), 118–121. DOI: 10.1080/01621459.1974.10480137                            | Linear opinion-averaging model (α-term basis)                                                   |
| 3  | Del Vicario, M., et al. (2016). The Spreading of Misinformation Online. *PNAS*, 113(3), 554–559. DOI: 10.1073/pnas.1517441113                                                    | Empirical calibration of cluster/exposure geometry                                              |
| 4  | Deffuant, G., Neau, D., Amblard, F., & Weisbuch, G. (2000). Mixing beliefs among interacting agents. *Advances in Complex Systems*, 3(1–4), 87–98. DOI: 10.1142/S0219525900000078 | Alternative bounded-confidence non-linear coupling                                              |
| 5  | Friedkin, N. E., & Johnsen, E. C. (1990). Social influence and opinions. *Journal of Mathematical Sociology*, 15(3–4), 193–206. DOI: 10.1080/0022250X.1990.9990069               | Empirical α calibration; residual variance for σ                                                |
| 6  | Moscovici, S., & Zavalloni, M. (1969). The Group as a Polarizer of Attitudes. *Journal of Personality and Social Psychology*, 12(2), 125–135. DOI: 10.1037/h0027568              | Foundational group-polarization empirical effect                                                |
| 7  | Granovetter, M. (1978). Threshold Models of Collective Behavior. *American Journal of Sociology*, 83(6), 1420–1443. DOI: 10.1086/226707                                          | Alternative threshold-cascade mechanism                                                         |
| 8  | Isenberg, D. J. (1986). Group Polarization: A Critical Review and Meta-Analysis. *Journal of Personality and Social Psychology*, 50(6), 1141–1151. DOI: 10.1037/0022-3514.50.6.1141 | Group-polarization meta-analysis effect sizes                                                    |
| 9  | Prior, M. (2013). Media and Political Polarization. *Annual Review of Political Science*, 16, 101–127. DOI: 10.1146/annurev-polisci-100711-135242                                | Media-driven equilibrium shifts (alternative Exogenous Driver scenario)                          |
| 10 | Esteban, J. M., & Ray, D. (1994). On the Measurement of Polarization. *Econometrica*, 62(4), 819–851. DOI: 10.2307/2951734                                                       | Alternative variance-based polarization index                                                   |
| 11 | Brady, W. J., et al. (2017). Emotion shapes the diffusion of moralized content in social networks. *PNAS*, 114(28), 7313–7318. DOI: 10.1073/pnas.1618923114                      | Heavy-tailed moral-outrage cascade dynamics                                                     |
| 12 | Allport, G. W. (1954). *The Nature of Prejudice*. Addison-Wesley. ISBN: 978-0201001754                                                                                          | Foundational contact-hypothesis and cross-cutting exposure theory                               |

## Design Provenance and Versioning

| Field       | Content                                                                     |
|-------------|-----------------------------------------------------------------------------|
| Market Type | `opinion` — Opinion / Social-Influence Field                                |
| Author      | AgenticFinLab                                                               |
| Reviewed by | — (pending)                                                                 |
| Created     | 2026-07-16                                                                  |
| Version     | 1.0.0                                                                       |
| Status      | canonical                                                                   |
| Icon        | ![](../agent_images/icons/market/opinion-echo-chamber-clustering.png)       |
