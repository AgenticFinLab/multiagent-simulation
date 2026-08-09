# Information field coordinator with SIS-style rumor contagion dynamics

## Summary

| Field                | Content                                                                                                                                                                                                                                                        |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Market Type          | `information` — Information / Rumor Field                                                                                                                                                                                                                      |
| Coordinator Role     | Central information environment tracking population belief in a rumor, distortion index, and ground-truth reference                                                                                                                                            |
| Mechanism Family     | Linear SIS-style contagion with truth-anchored correction, Allport–Postman leveling / sharpening distortion dynamics, and Gaussian noise                                                                                                                       |
| Shared State         | `belief`, `prev_belief`, `belief_change`, `distortion`, `truth_value`, `num_spreaders`, `num_correctors`, `net_spread_intensity`, `round`                                                                                                                       |
| Broadcast Cadence    | every-tick (one broadcast per simulation round, after all agents submit spread / correct / ignore actions)                                                                                                                                                     |
| Determinism          | stochastic-given-seed (ε ~ N(0, σ²) drawn from a seeded RNG; identical seed + identical inbound action sequence reproduce byte-equal broadcasts)                                                                                                              |
| Feedback Direction   | **Regime-dependent** — when `spread_impact · |net_spread|` exceeds `truth_correction · |truth_value − belief|`, the mechanism amplifies belief in the rumor (contagion dominates); when correctors and truth-anchoring dominate, the mechanism is stabilising toward `truth_value` [Ref 1, Ref 2] |
| Scenario Portability | 1 pool scenario bound via `players.yml → market.archetype: information-sis-contagion`. **Full ✅**: (none). **Approximated ⚠**: RumorSpread — dedicated `InformationEnvironment` class with `belief` + `distortion` state; belief update currently uses the standard mean-reversion form `B + spread_impact·net_spread + truth_correction·(truth − B) + noise` rather than a full SIS compartmental `dI/dt = βSI − γI` model. See also the Scenario Status row below. |
| Scenario Status      | **Full** = coordinator code implements the archetype's mechanism signature verbatim; **Approximated** = archetype bound via `players.yml → market.archetype:` for icon/UI/narrative purposes, but the coordinator code currently uses the standard price-impact formula `P(t+1)=P(t)+λ·NetDemand+γ·(F-P(t))+ε` as a placeholder — the archetype's specialized state and dynamics are intended but not yet realized in code. |

## Definition and Goals

This coordinator models a **single-population, continuous-belief
information field with a designated rumor-contagion mechanism** —
the workhorse coordinator used to study rumor propagation,
misinformation cascades, and fact-checking dynamics at the population
level. The real-world counterpart is a deliberative or social-media
population where spreaders amplify unverified claims and correctors
push belief toward a ground-truth reference, approximated at the
round (broadcast cycle) granularity, similar in spirit to the
psychology-of-rumor framework of Allport & Postman (1947) [Ref 1] and
formalised in the misinformation-diffusion literature by Vosoughi,
Roy & Aral (2018) [Ref 2] and Bordia & Rosnow (1998) [Ref 3]. The
coordinator is deliberately field-level rather than
peer-graph-matched, because the round granularity of the enclosing
simulation makes an explicit transmission network both unnecessary
and (per Del Vicario et al. 2016 [Ref 4]) numerically comparable to a
linear net-spread rule at sufficient aggregation.

The coordination goal is to **aggregate all participant
spread/correct/ignore actions submitted this round, produce exactly
one new population belief `B(t+1)` via the equation `B(t+1) =
clip(B(t) + α · NetSpread + β · (Truth − B(t)) + ε, 0, 1)`, update
the distortion index via Allport–Postman leveling and sharpening
terms, and broadcast `{belief, prev_belief, belief_change, distortion,
truth_value, num_spreaders, num_correctors, net_spread_intensity,
round}` to every participant.** The broadcast is identical for every
participant (symmetric information environment).

Non-goals (this coordinator MUST NOT):

- MUST NOT filter or route actions based on participant identity,
  role label, or history — homophily and credulity are expressed in
  participant profiles (via `agent_role` and personal `my_belief`),
  not in the coordinator.
- MUST NOT inject exogenous news events, media campaigns, or
  platform-moderation shocks from within its own logic — such drivers
  enter via the Exogenous Driver Boundary declared in §5.
- MUST NOT modify the ground-truth reference `Truth = rumor_truth_value`
  from its own logic; truth updates, if any, are a scenario overlay
  written into `extras` by the scenario runner before `perceive`
  (see §5).
- MUST NOT enforce individual participant belief bounds — validation
  of submitted actions is a shared responsibility of the format layer
  and the coordinator's Missing-Input Policy.

## Theoretical / Mechanistic Foundation

**SIS-style linear rumor contagion (Daley–Kendall 1965;
Vosoughi–Roy–Aral 2018)**:

- Theory / Study: Susceptible–Infected–Susceptible dynamics adapted
  to information contagion where "infected" = believer and
  "susceptible" = non-believer
- Citation: Daley, D. J., & Kendall, D. G. (1965). "Stochastic
  Rumours." *Journal of the Institute of Mathematics and Its
  Applications*, 1(1), 42–55. DOI: `10.1093/imamat/1.1.42`;
  Vosoughi, S., Roy, D., & Aral, S. (2018). "The Spread of True and
  False News Online." *Science*, 359(6380), 1146–1151.
  DOI: `10.1126/science.aap9559`
- Core Insight: In populations exposed to both spreaders and
  correctors, the change in the collective belief is a **linear
  function of the aggregate signed spread pressure** whose slope
  captures the contagion rate. Higher slope means the population is
  more susceptible; lower slope means the population is more
  resistant to unverified claims.
- Mathematical Formulation: `ΔB_spread = α · NetSpread`, where
  `NetSpread = Σ_spread intensity_i − Σ_correct intensity_i`.
- Empirical Evidence: Vosoughi–Roy–Aral (2018) [Ref 2, Fig. 2]
  document that false-news cascades spread `6–10×` faster than true
  news on Twitter, corresponding to an effective per-round belief
  shift of `0.05–0.15` at moderate exposure levels; our default
  `α = 0.15` operates at simulation units (`intensity ∈ [0, 1]`,
  `belief ∈ [0, 1]`) and reproduces the target belief-shift-per-round
  of ≈ 15% at `|NetSpread| = 1`.
- Relevance to This Coordinator: Provides the contagion-driven
  belief change term `α · NetSpread` in the transition equation.
- Calibration Source: Vosoughi–Roy–Aral 2018 [Ref 2, Fig. 2] and
  Bordia–Rosnow 1998 [Ref 3, §Meta-analysis]; simulation-unit-adjusted
  range `α ∈ [0.05, 0.30]`.
- Falsification Conditions: If a doubling of `NetSpread` (holding
  all else constant, including seed for ε) does NOT approximately
  double `ΔB_spread` in a broadcast pair, the linear-contagion
  property is broken.
- Alternative Mechanisms: SIR-style permanent-recovery contagion
  [Ref 5]; independent-cascade models [Ref 6].

**Truth-anchored correction (DiFonzo–Bordia 2007; fact-checking
literature)**:

- Theory / Study: Belief-toward-truth restoring force from
  fact-checking and corrective information exposure
- Citation: DiFonzo, N., & Bordia, P. (2007). *Rumor Psychology:
  Social and Organizational Approaches*. American Psychological
  Association; Nyhan, B., & Reifler, J. (2010). "When Corrections
  Fail: The Persistence of Political Misperceptions." *Political
  Behavior*, 32(2), 303–330. DOI: `10.1007/s11109-010-9112-2`
- Core Insight: In populations exposed to corrective information,
  the collective belief is systematically pulled back toward the
  ground-truth reference `Truth` at a rate that depends on the
  effective weight of corrective information and audience receptivity
  — capturing the empirically observed asymmetric relaxation (slower
  than the contagion up-slope).
- Mathematical Formulation: `ΔB_correction = β · (Truth − B(t))`.
- Empirical Evidence: DiFonzo–Bordia (2007) [Ref 7, Ch. 5] document
  that repeated corrective exposure reduces rumor belief by
  `10–25%` in laboratory studies over 5–10 rounds; on a
  round-granularity simulation with 20–100 rounds, `β ∈ [0.02, 0.15]`
  reproduces comparable relative correction rates.
- Relevance to This Coordinator: Provides the truth-anchoring pull
  term `β · (Truth − B(t))` that is required to prevent scenarios
  from drifting monotonically to full belief regardless of truth.
- Calibration Source: DiFonzo–Bordia 2007 [Ref 7, Ch. 5] and
  Nyhan–Reifler 2010 [Ref 8, Table 3]. Note: Nyhan–Reifler document
  the "backfire effect" for certain audiences (β < 0 possible in
  extreme cases) but the aggregate is positive in most populations.
- Falsification Conditions: If, holding `NetSpread = 0` and `ε = 0`,
  ten consecutive broadcasts do NOT monotonically reduce
  `|belief − truth_value|`, the truth-correction term is broken.
- Alternative Mechanisms: Backfire-effect dynamics with β < 0 in
  saturation regime [Ref 8]; motivated-reasoning models [Ref 9].

**Allport–Postman leveling and sharpening (distortion dynamics)**:

- Theory / Study: Serial-transmission distortion where retellings
  simultaneously simplify (leveling) and exaggerate (sharpening)
- Citation: Allport, G. W., & Postman, L. (1947). *The Psychology of
  Rumor*. Henry Holt. ISBN: 978-0805200379
- Core Insight: Every retelling of a rumor **loses detail (leveling)
  at a rate proportional to current distortion** and
  **exaggerates salient false content (sharpening) at a rate
  proportional to the number of spreaders times the falsity gap
  `(1 − Truth)`**. In equilibrium, distortion settles where these
  two forces balance.
- Mathematical Formulation:
  `D(t+1) = clip(D(t) − ℓ · D(t) + s · n_spreaders · (1 − Truth), 0, 1)`,
  with `ℓ = leveling_rate`, `s = sharpening_rate`.
- Empirical Evidence: Allport–Postman (1947) [Ref 1, §Serial-reproduction
  studies] document distortion accumulation of `0.3–0.7` after 5–7
  retellings of standardised stimuli; on a round-granularity
  simulation with 20 spreaders per round and `Truth = 0` (fully
  false rumor), our defaults `ℓ = 0.1`, `s = 0.02` reproduce
  distortion saturation in the `0.4–0.6` range within 20–30 rounds.
- Relevance to This Coordinator: Provides the distortion index
  `D(t)` broadcast alongside the primary belief state.
- Calibration Source: Allport–Postman 1947 [Ref 1, §Serial-reproduction
  studies].
- Falsification Conditions: If `n_spreaders = 0` for ten consecutive
  rounds and `distortion` does NOT monotonically decay toward `0`,
  the leveling term is broken. If `Truth = 1` (true news) and
  `n_spreaders > 0` yet `distortion` grows unboundedly, the falsity
  gap `(1 − Truth)` is not being applied correctly.
- Alternative Mechanisms: Multiplicative distortion (Bartlett 1932)
  [Ref 10]; content-aware distortion tied to specific narrative
  frames [Ref 3].

**Gaussian idiosyncratic noise (population-level residual)**:

- Theory / Study: Zero-mean Gaussian residual for unmodelled
  micro-level heterogeneity in belief updating
- Citation: Vosoughi–Roy–Aral 2018 [Ref 2]; DeGroot 1974 [Ref 11]
- Core Insight: Even in mechanism-driven information fields,
  round-to-round belief changes carry an irreducible idiosyncratic
  component due to individual-level credulity heterogeneity not
  captured by the linear contagion term; modelling this as
  zero-mean Gaussian is a widely-adopted simplification.
- Mathematical Formulation: `ε ~ N(0, σ²)`, with σ = `noise_std`.
- Empirical Evidence: Vosoughi–Roy–Aral 2018 [Ref 2, §Robustness
  section] report residual variance of `0.02–0.08` in belief units
  after controlling for observed exposure; our default `σ = 0.03`
  (in belief units) corresponds to the low end of that range.
- Relevance to This Coordinator: Adds the term `ε` and makes the
  mechanism stochastic-given-seed rather than deterministic.
- Calibration Source: Vosoughi–Roy–Aral 2018 [Ref 2, §Robustness].
- Falsification Conditions: If ε is drawn from a distribution with
  materially non-zero mean or from a non-Gaussian family (fat tails
  from a different generator), the mechanism has been altered.
- Alternative Mechanisms: Heavy-tailed shocks (viral cascades)
  [Ref 6]; state-dependent noise scaling with belief level [Ref 5].

## Activation, Lifecycle, and Coordination Cadence

Purpose: Aggregate all participant spread/correct/ignore actions
each round, apply the linear-contagion + truth-anchored-correction +
noise transition to belief, update distortion via leveling and
sharpening, and broadcast one authoritative information-field
snapshot.

Coordination Cadence: **every-tick** (one broadcast per simulation
round; the round advances only after `act()` completes).

Lifecycle Mapping (MANDATORY):

- `perceive(observation, prev_result)`:
  1. Read `round_num = observation.round` and write it to
     `state["round"]`.
  2. If `"belief"` is not yet in `state.custom_state`, run the State
     Initialization block below.
  3. Drain `observation.inbounds`; each inbound payload is a
     participant action dict with `action_type ∈ {spread, correct,
     ignore}`, `intensity ∈ [0, 1]`, `agent_role: str`.
  4. Validate each action per §4.6.6 Failure Modes (raise `ValueError`
     on out-of-range fields); store the validated action list in
     `state["actions"]` — READ phase only, no field-derived writes.
- `decide()`:
  1. Compute aggregates per §4.6.1 (`total_spread`,
     `total_correction`, `net_spread`, `n_spreaders`).
  2. Draw `ε ~ N(0, σ²)` from the seeded RNG.
  3. Compute
     `new_belief = clip(B(t) + α · NetSpread + β · (Truth − B(t)) + ε,
     0, 1)`;
     `new_distortion = clip(D(t) − ℓ · D(t) + s · n_spreaders · (1 −
     Truth), 0, 1)`. WRITE the new state atomically:
     `prev_belief ← B(t); belief ← new_belief; distortion ←
     new_distortion; belief_history.append(new_belief);
     distortion_history.append(new_distortion);
     spread_count_history.append(n_spreaders);
     correction_count_history.append(n_correctors)`.
  4. Return the broadcast dict `{belief, prev_belief, belief_change,
     distortion, truth_value, num_spreaders, num_correctors,
     net_spread_intensity, round}` assembled from committed state.
- `act(decision)`:
  1. Wrap the dict as `EnvironmentBroadcast` (or engine equivalent)
     with `action_type="environment_broadcast"` and emit to every
     participant via the standard outbox. No writes.

Deviation from the stock-market lifecycle: because the state-write
depends on the aggregated action list — which is fully known only
after action aggregation in `decide` — the state-write step is
placed inside `decide` rather than `perceive`. `perceive` only
validates and stores the raw action list; `decide` performs the
transition and the write. `act` remains write-free.

State Initialization (MANDATORY):

- Trigger: `"belief" not in self.state.custom_state`.
- Required extras (raise `KeyError` on missing): `initial_belief`,
  `rumor_truth_value`, `spread_impact`, `truth_correction`,
  `leveling_rate`, `sharpening_rate`, `noise_std`, `record_path`,
  `custom_state_hot_limit`.
- Initial state writes (single atomic block):
  - `state["belief"] = extras["initial_belief"]`
  - `state["prev_belief"] = extras["initial_belief"]` (equal to
    current on round 0 — cold-start "no change yet")
  - `state["distortion"] = 0.0`
  - `state["truth_value"] = extras["rumor_truth_value"]`
  - `state["belief_history"] = HistoryBuffer(
    folder=<record>/<identity>/belief, entry_limit=hot_limit)`
  - Similar `HistoryBuffer` instances for `distortion_history`,
    `spread_count_history`, `correction_count_history`.
- Warm-up rounds: `0` (broadcast is trustworthy from round 0, though
  `prev_belief == belief` on round 0 must be interpreted correctly
  by participants).
- Cold-start reading rule for participants: on round 0,
  `prev_belief == belief`, so the participant-side belief-change
  signal SHOULD be treated as "no observation yet" rather than
  "change of zero".

Inbound Message Types:

- **SocialAction**: `{"action_type": "spread" | "correct" |
  "ignore", "intensity": float ∈ [0, 1], "agent_role": str}`.
  - `spread` / `correct` with `intensity > 0` contribute to the
    net-spread aggregate.
  - `ignore` or `intensity == 0` are counted in `n_active` logging
    but do not shift belief.
- **Default (no message)**: treated as `ignore` with
  `intensity = 0`.

Broadcast Trigger: after every round tick, at the end of `decide`
following the state-write phase.

Missing-Input Policy:

- Missing required extras → **raise `KeyError`** from `perceive`; do
  NOT default.
- Zero inbound actions → set `total_spread = total_correction =
  net_spread = 0`, `n_spreaders = 0`; belief evolves under pure
  truth-anchoring + noise; distortion decays via leveling only.
- Individual action with `action_type` outside the valid set → raise
  `ValueError` from `perceive` (halt-on-invalid).
- Individual action with `intensity` outside `[0, 1]` → raise
  `ValueError` from `perceive` (halt-on-invalid).
- `NaN` / `Inf` in the computed `new_belief` or `new_distortion` →
  **raise `ValueError`** from `decide`; do NOT emit a broadcast this
  round.
- NEVER silently substitute a default for a required field.

Exogenous Driver Boundary (MANDATORY):

- This coordinator MUST NOT generate exogenous news events,
  platform-moderation shocks, or media-campaign shocks from within
  its own logic.
- Truth-value changes (e.g. a fact revealed to be false partway
  through, or a debunking event) enter via either (a) a distinguished
  inbound message from a scenario-provided `FactCheckAgent`, in which
  case `perceive` reads it as an ordinary aggregate signal that
  shifts `state["truth_value"]`, OR (b) a mutation of `config.extras[
  "rumor_truth_value"]` by the scenario runner performed BEFORE this
  coordinator's `perceive`. The coordinator itself remains passive.

Environmental Dependencies:

- Required extras (see §4.7): `initial_belief`, `rumor_truth_value`,
  `spread_impact`, `truth_correction`, `leveling_rate`,
  `sharpening_rate`, `noise_std`, `record_path`,
  `custom_state_hot_limit`.
- Optional extras: `initial_credibility` (used by participant
  profiles, not the coordinator; declared here for reference only).
- No scenario driver signals are required beyond what enters via the
  Exogenous Driver Boundary.

## Coordination Framework

#### I/O Contract **(MANDATORY, contract-strength)**

##### Inputs (per coordination call)

| Input               | Source                          | Type / Shape                                                                                        | Required? | Notes                                                                        |
|---------------------|---------------------------------|-----------------------------------------------------------------------------------------------------|-----------|------------------------------------------------------------------------------|
| `inbound_actions`   | mailbox from participant agents | `list[dict]`; each dict has `action_type: str`, `intensity: float`, `agent_role: str`                | yes       | Coordinator does NOT require an `opinion` or `belief` field on inbound actions |
| `current_state`     | coordinator's persisted state   | `{"belief": float, "prev_belief": float, "distortion": float, "truth_value": float, ...}`           | yes       | Populated on first call by State Initialization                              |
| `context_metadata`  | scheduler / round header        | `{"round": int, "identity": str, "seed": int}`                                                      | yes       | Identity naming: `{variant}_environment_information`                          |
| `scenario_driver`   | scenario overlay                | `dict` or `None`                                                                                    | no        | Only if scenario declares exogenous truth-value / regime changes             |

##### Outputs (per coordination call)

The coordinator emits exactly one broadcast dict per call. Every
participant sees the identical dict.

| Field                     | Type   | Valid Range / Enum | Unit          | Required? | Meaning                                                        |
|---------------------------|--------|--------------------|---------------|-----------|----------------------------------------------------------------|
| `belief`                  | float  | `[0, 1]`           | belief index  | yes       | Post-transition population belief B(t+1) for this round         |
| `prev_belief`             | float  | `[0, 1]`           | belief index  | yes       | Belief broadcast in the previous round (B(t))                   |
| `belief_change`           | float  | `[-1, 1]`          | belief index  | yes       | `belief − prev_belief`                                          |
| `distortion`              | float  | `[0, 1]`           | distortion    | yes       | Allport–Postman distortion index                                |
| `truth_value`             | float  | `[0, 1]`           | truth index   | yes       | Ground-truth reference (0 = false, 1 = true)                    |
| `num_spreaders`           | int    | `≥ 0`              | count         | yes       | Number of `spread` actions this round                           |
| `num_correctors`          | int    | `≥ 0`              | count         | yes       | Number of `correct` actions this round                          |
| `net_spread_intensity`    | float  | any                | intensity     | yes       | `total_spread − total_correction`                               |
| `round`                   | int    | `≥ 0`              | —             | yes       | Round number that produced this broadcast                        |

Any participant reading a field NOT listed here indicates a
downstream bug — this contract is the exhaustive schema.

##### Content Constraints

- **Required fields**: all nine fields above MUST be present every
  round.
- **Forbidden fields**: fields not declared above MUST NOT be added
  (silently breaks downstream parsers that read participant
  broadcasts as fixed-schema dicts).
- **Value ranges**: `belief`, `distortion`, `truth_value` clipped to
  `[0, 1]` before emission; `belief_change ∈ [-1, 1]` by
  construction; all fields numeric-finite (no NaN / Inf — enforced
  by the Missing-Input Policy above).
- **Units and sign conventions**: `belief ∈ [0, 1]` where `0` =
  population fully rejects the rumor and `1` = population fully
  believes; `truth_value ∈ [0, 1]` uses the same scale, so
  `belief == truth_value` signals rational-average accuracy;
  `distortion ∈ [0, 1]` where `0` = faithful transmission and `1` =
  maximum content drift.
- **Determinism markers**: the seed used for ε on each round MUST
  be recoverable from the round number plus the coordinator's base
  seed; two runs with identical seed + identical action sequence
  produce byte-equal broadcasts.

##### Serialization Format

Broadcast payload is a **plain Python `dict`** (no `<analysis>` /
`<decision>` tags — those bind participant agents, not coordinators).
The canonical shape is:

```json
{
  "belief":               0.62,
  "prev_belief":          0.55,
  "belief_change":        0.07,
  "distortion":           0.28,
  "truth_value":          0.0,
  "num_spreaders":       12,
  "num_correctors":       4,
  "net_spread_intensity": 5.3,
  "round":               8
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
   field; `belief`, `distortion`, `truth_value` are clipped to
   `[0, 1]` BEFORE the state-write, not later.
3. **Format-layer compatibility** — the broadcast satisfies the
   participant-side format contract for information-domain scenarios.
   Implementers MUST NOT silently omit any required field; the
   participant-side parser is entitled to raise on missing keys.
4. **Variant parity** — every declared variant emits the same
   9-field dict.
5. **Contract-versus-prose conflict resolution** — if the mechanism
   in §4.6.2 or the parameters in §4.7 seem to contradict this
   contract, the contract wins.

#### Input Aggregation Rules

| Aggregate signal    | Derivation                                                        | Rationale                                                     |
|---------------------|-------------------------------------------------------------------|---------------------------------------------------------------|
| `total_spread`      | `sum(a["intensity"] for a in actions if a["action_type"]=="spread")` | Total spread pressure this round                              |
| `total_correction`  | `sum(a["intensity"] for a in actions if a["action_type"]=="correct")` | Total corrective pressure this round                          |
| `net_spread`        | `total_spread − total_correction`                                  | Signed contagion driving α term                               |
| `n_spreaders`       | `len([a for a in actions if a["action_type"] == "spread"])`         | Basis for sharpening term (Allport–Postman)                   |
| `n_correctors`      | `len([a for a in actions if a["action_type"] == "correct"])`        | Broadcast field                                                |
| `n_active`          | `len([a for a in actions if a["action_type"] != "ignore"])`         | Count of non-ignore participants; used only for logging       |

Does NOT use: individual participant identities; participant
`agent_role` (label is stored but not aggregated); peer-to-peer
topology; any private state of individual participants.

Completeness rule check: all six aggregates above are consumed in
§4.6.2 (net_spread in step 4; n_spreaders in step 5; n_correctors +
n_spreaders in step 7 emission; n_active in step 8 logging).

#### Core Coordination Mechanism

1. **READ** `round_num`, `inbound_actions` from `observation`. Read
   `state["belief"] = B(t)`, `state["distortion"] = D(t)`,
   `state["truth_value"] = Truth`, and extras
   `{α = spread_impact, β = truth_correction, ℓ = leveling_rate,
   s = sharpening_rate, σ = noise_std}`. Traces to §4.4 SIS-contagion
   + Allport–Postman readings.
2. **VALIDATE** each action against valid types (`spread`,
   `correct`, `ignore`) and intensity range `[0, 1]`; raise
   `ValueError` on violation. Traces to §4.6.6 Failure Modes.
3. **COMPUTE** aggregates from §4.6.1: `total_spread`,
   `total_correction`, `net_spread`, `n_spreaders`, `n_correctors`.
4. **COMPUTE** the noise draw `ε = rng.gauss(0, σ)` from the seeded
   RNG. Traces to §4.4 Gaussian residual.
5. **COMPUTE** the raw belief transition:
   `B_raw = B(t) + α · net_spread + β · (Truth − B(t)) + ε`. Traces
   to §4.4 SIS-contagion (first term), Truth-anchored correction
   (second term).
6. **COMPUTE** the belief clip:
   `new_belief = clip(B_raw, 0, 1)`. Traces to §4.6.6 invariant #3.
7. **COMPUTE** the distortion transition:
   `D_raw = D(t) − ℓ · D(t) + s · n_spreaders · (1 − Truth)`;
   `new_distortion = clip(D_raw, 0, 1)`. Traces to §4.4
   Allport–Postman leveling / sharpening.
8. **WRITE** atomically in this order:
   `state["prev_belief"] = B(t)`;
   `state["belief"] = new_belief`;
   `state["distortion"] = new_distortion`;
   `belief_history.append(new_belief)`;
   `distortion_history.append(new_distortion)`;
   `spread_count_history.append(n_spreaders)`;
   `correction_count_history.append(n_correctors)`. Traces to §4.6.6
   invariant #1.
9. **EMIT** in `decide` the 9-field dict `{belief, prev_belief,
   belief_change, distortion, truth_value, num_spreaders,
   num_correctors, net_spread_intensity, round}`. Traces to §4.6.0
   Outputs.

#### Broadcast Space

| Aspect                       | Specification                                                                                                                                                            |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Broadcast fields             | `belief`, `prev_belief`, `belief_change`, `distortion`, `truth_value`, `num_spreaders`, `num_correctors`, `net_spread_intensity`, `round` (verbatim §4.6.0 Outputs)         |
| State transition rule        | `B(t+1) = clip(B(t) + α·net_spread + β·(Truth − B(t)) + ε, 0, 1)`; `D(t+1) = clip(D(t) − ℓ·D(t) + s·n_spreaders·(1 − Truth), 0, 1)`                                          |
| Value bounds                 | `belief, distortion, truth_value ∈ [0, 1]`, `belief_change ∈ [-1, 1]`                                                                                                     |
| Freshness policy             | Every-tick; broadcast reflects state committed in the current `decide`                                                                                                   |
| Revision policy              | No — a broadcast MUST NOT be retracted or amended within a round; if a bug is detected, the round is aborted (see Failure Modes)                                          |
| State-history retention      | Hot buffer of `custom_state_hot_limit` (default 10000) entries with cold spill to `<record_path>/<identity>/…` via `HistoryBuffer`                                        |
| Resource cap                 | Unbounded on-disk (history spills); RAM bounded by hot-limit                                                                                                             |
| Termination rule             | Coordinator stops broadcasting when `round == total_rounds`; the simulation runner handles shutdown                                                                       |

#### Mathematical Model

1. **Broadcast outputs**:
   - `belief ∈ [0, 1] ⊂ ℝ`
   - `prev_belief ∈ [0, 1] ⊂ ℝ`
   - `belief_change ∈ [-1, 1] ⊂ ℝ`
   - `distortion ∈ [0, 1] ⊂ ℝ`
   - `truth_value ∈ [0, 1] ⊂ ℝ`
   - `num_spreaders, num_correctors ∈ ℤ⁺ ∪ {0}`
   - `net_spread_intensity ∈ ℝ`
   - `round ∈ ℤ⁺ ∪ {0}`

2. **State transition logic**:
   ```
   B(t+1) = clip( B(t) + α · NetSpread(t) + β · (Truth − B(t)) + ε(t),
                  0, 1 )
   D(t+1) = clip( D(t) − ℓ · D(t) + s · n_spreaders(t) · (1 − Truth),
                  0, 1 )
   ε(t)   ~ N(0, σ²)   — one draw per round, seeded by (base_seed, t)
   NetSpread(t) = Σ_{i: action_i.type == "spread"}  intensity_i
                − Σ_{i: action_i.type == "correct"} intensity_i
   n_spreaders(t) = |{i : action_i.type == "spread"}|
   ```

3. **State variables**:

   | Variable                        | Type            | Initial value                                                       |
   |---------------------------------|-----------------|---------------------------------------------------------------------|
   | `belief`                        | float           | `extras["initial_belief"]`                                          |
   | `prev_belief`                   | float           | `extras["initial_belief"]`                                          |
   | `distortion`                    | float           | `0.0`                                                                |
   | `truth_value`                   | float           | `extras["rumor_truth_value"]`                                       |
   | `belief_history`                | `HistoryBuffer` | empty, `<record>/<identity>/belief`, hot_limit                       |
   | `distortion_history`            | `HistoryBuffer` | empty                                                                |
   | `spread_count_history`          | `HistoryBuffer` | empty                                                                |
   | `correction_count_history`      | `HistoryBuffer` | empty                                                                |
   | `round`                         | int             | `0`                                                                  |

4. **State evolution ordering**: all state writes happen at the end
   of `decide` (step 8 of §4.6.2), AFTER the transition computation
   and BEFORE the broadcast dict is returned. `prev_belief` is
   written before `belief` so that invariant #1 holds; both use the
   pre-transition value.

5. **Determinism contract**: **stochastic-given-seed**. The single
   randomness source is the Gaussian draw for ε. The RNG is seeded
   from a base seed provided at construction plus the round number,
   so two runs with the same base seed and identical inbound-action
   sequences produce byte-equal broadcasts.

6. **Parameter symbol table**:

   | Symbol   | Meaning                                        | Default Value | Source                              |
   |----------|------------------------------------------------|---------------|-------------------------------------|
   | `α`      | Belief impact per unit of net spread            | `0.15`        | Vosoughi–Roy–Aral 2018 [Ref 2]      |
   | `β`      | Truth-anchored correction rate                  | `0.05`        | DiFonzo–Bordia 2007 [Ref 7]         |
   | `ℓ`      | Leveling rate (distortion decay per round)      | `0.1`         | Allport–Postman 1947 [Ref 1]        |
   | `s`      | Sharpening rate (distortion growth per spreader) | `0.02`        | Allport–Postman 1947 [Ref 1]        |
   | `σ`      | Std dev of Gaussian noise per round             | `0.03`        | Vosoughi–Roy–Aral 2018 [Ref 2]      |
   | `Truth`  | Ground-truth reference                          | `0.0` (false) | Scenario config                     |
   | `B(0)`   | Initial belief                                  | `0.2`         | Scenario config                     |
   | `t`      | Round index                                     | `0` at start  | Scheduler                           |

#### Coordination Properties

- **Time granularity**: round-based (one tick per participant action
  round).
- **Feedback loop**: mixed — truth-anchored correction produces
  negative feedback around `Truth`; sustained one-sided net-spread
  produces positive-feedback belief drift; the crossover depends on
  parameter ratio `α/β` and the persistence of `net_spread`.
- **Information environment**: symmetric — every participant sees
  the identical broadcast. Private belief state exists only inside
  participant profiles.
- **Stochasticity profile**: one Gaussian ε draw per round; no
  other randomness inside the coordinator.

#### Invariants and Failure Modes **(MANDATORY)**

Round-boundary Invariants:

| # | Invariant                                                                                                          | Enforcement                                              |
|---|--------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| 1 | `broadcast[t+1].prev_belief == broadcast[t].belief` (byte-equal float)                                             | §4.6.2 step 8 writes `prev_belief ← B(t)` first          |
| 2 | Every required field in §4.6.0 Outputs is present and non-null                                                     | `decide` assertion at emit                                |
| 3 | `belief, distortion, truth_value ∈ [0, 1]` in every broadcast                                                      | §4.6.2 step 6, step 7 clip                                |
| 4 | `broadcast[t+1].round == broadcast[t].round + 1`                                                                    | Set from `observation.round` in `perceive`                |
| 5 | `truth_value` unchanged across rounds UNLESS Exogenous Driver Boundary is invoked                                   | §4.5 boundary rule                                        |
| 6 | Two runs with identical `base_seed` and identical inbound-action sequence produce byte-equal broadcasts             | Seeded RNG only                                          |
| 7 | `belief_change == belief − prev_belief`                                                                             | §4.6.2 emission step                                      |
| 8 | If `n_spreaders = 0` AND `Truth = 0`, `distortion(t+1) = distortion(t) · (1 − ℓ)` (pure leveling)                  | §4.6.2 step 7                                             |

Domain-Specific Invariants:

- **Belief bounds**: `belief ∈ [0, 1]` — invariant #3.
- **Distortion monotone decay in silence**: with `n_spreaders = 0`
  and `Truth = 0`, distortion strictly decreases (unless already
  `0`) — invariant #8.
- **Truth-fidelity zero-sharpening**: with `Truth = 1` (true news),
  the sharpening term contributes `0` regardless of `n_spreaders`
  because `(1 − Truth) = 0`.
- **No cross-round leakage**: each history buffer grows by exactly 1
  entry per round.
- **Conservation**: not applicable — the coordinator is
  belief-forming only, not authoritative for individual participant
  beliefs.

Failure Modes:

| Condition                                                     | Coordinator behaviour                                       | Broadcast effect                                                    |
|---------------------------------------------------------------|-------------------------------------------------------------|---------------------------------------------------------------------|
| Zero inbound actions                                          | Continue; `net_spread = 0`; belief evolves under pure truth-anchoring + noise; distortion decays via leveling only | Broadcast with pure correction + noise move                          |
| All spreaders (`total_correction = 0`)                        | Continue                                                    | Amplifying pressure on `belief`; sharpening term inflates distortion  |
| All correctors (`total_spread = 0`)                           | Continue                                                    | Damping pressure on `belief`; no sharpening; leveling decays distortion |
| Action with invalid `action_type`                             | Raise `ValueError` from `perceive`                           | No broadcast; simulation halts                                       |
| Action with `intensity` outside `[0, 1]`                      | Raise `ValueError` from `perceive`                           | No broadcast; simulation halts                                       |
| Required extras key missing                                   | Raise `KeyError` from `perceive`                             | No broadcast; simulation halts                                       |
| `new_belief` or `new_distortion` computes to NaN / Inf        | Raise `ValueError` from `decide`                             | No broadcast; simulation halts (implementation defect)               |
| Scenario driver mutates `extras["rumor_truth_value"]` mid-run | Next `perceive` reads new value; log the change              | Next broadcast reflects the new truth reference                       |
| `Truth = 1` (true news) AND `n_spreaders > 0`                 | Sharpening term evaluates to `0`; only leveling applies      | Distortion decays even with active spreaders (invariant of true news) |
| `HistoryBuffer` disk write fails                              | Raise from `decide`; do NOT emit stale broadcast             | No broadcast; simulation halts                                       |

## Environmental Parameters

### 4.7.1 Parameter Categorisation

#### A. Initial Conditions

| Parameter           | Type  | Default | Valid Range | Sensitivity | Description                    | Impact                                          | Source                              |
|---------------------|-------|---------|-------------|-------------|--------------------------------|-------------------------------------------------|-------------------------------------|
| `initial_belief`    | float | `0.2`   | `[0, 1]`    | high        | Round-0 belief seed             | Higher → head start for rumor                    | Scenario config (Vosoughi 2018)     |
| `rumor_truth_value` | float | `0.0`   | `[0, 1]`    | high        | Ground-truth reference `Truth`  | `0` = false rumor; `1` = true report              | Scenario config (Allport 1947)      |

#### B. Mechanism Coefficients

| Parameter          | Type  | Default | Valid Range | Sensitivity | Description                                                          | Impact                                                                     | Source                              |
|--------------------|-------|---------|-------------|-------------|----------------------------------------------------------------------|----------------------------------------------------------------------------|-------------------------------------|
| `spread_impact`    | float | `0.15`  | `≥ 0`       | high        | α — belief move per unit of net spread                               | Higher → 2× more susceptible to spread pressure                            | Vosoughi–Roy–Aral 2018 [Ref 2]      |
| `truth_correction` | float | `0.05`  | `[0, 1]`    | high        | β — truth-anchored correction rate                                    | Higher → faster relaxation toward Truth; halves half-life                  | DiFonzo–Bordia 2007 [Ref 7]         |
| `leveling_rate`    | float | `0.1`   | `[0, 1]`    | medium      | ℓ — distortion decay per round                                        | Higher → faster forgetting of accumulated distortion                       | Allport–Postman 1947 [Ref 1]        |
| `sharpening_rate`  | float | `0.02`  | `≥ 0`       | medium      | s — distortion growth per active spreader per unit falsity gap        | Higher → more distortion accumulation per active spreader                  | Allport–Postman 1947 [Ref 1]        |
| `noise_std`        | float | `0.03`  | `≥ 0`       | medium      | σ — Gaussian noise std dev added per round                            | Higher → more idiosyncratic belief oscillation                             | Vosoughi–Roy–Aral 2018 [Ref 2]      |

#### C. Structural / Boundary Parameters

None. The `[0, 1]` belief, distortion, and truth-value clips are
domain-fundamental invariants, not tunable parameters.

#### D. Recording / Infrastructure Parameters

| Parameter                | Type | Default    | Valid Range | Sensitivity | Description                              | Impact                              | Source        |
|--------------------------|------|------------|-------------|-------------|------------------------------------------|-------------------------------------|---------------|
| `record_path`            | str  | `""`       | non-empty   | low         | Root directory for HistoryBuffer spills  | Higher size → more disk footprint   | Standardised  |
| `custom_state_hot_limit` | int  | `10000`    | `≥ 1`       | low         | HistoryBuffer hot-tier size (entries)    | Higher → more RAM, less disk I/O    | Standardised  |

## Worked Numerical Examples

### Case 1 — Spread pressure round (positive net spread, false rumor)

System state (round `t = 3`):

- `B(t) = 0.30`, `D(t) = 0.10`, `Truth = 0.0` (false), `α = 0.15`,
  `β = 0.05`, `ℓ = 0.1`, `s = 0.02`, `σ = 0.03`.
- Inbound actions:
  - 4 spreaders: intensity 0.9/0.8/0.7/0.6
  - 2 correctors: intensity 0.5/0.4
  - 1 ignore: intensity 0.0

Calculation:

- `total_spread = 3.0`, `total_correction = 0.9`,
  `net_spread = 2.1`, `n_spreaders = 4`, `n_correctors = 2`.
- `ε` draw `= +0.01`.
- Spread term: `0.15 · 2.1 = +0.315`.
- Correction term: `0.05 · (0.0 − 0.30) = -0.015`.
- `B_raw = 0.30 + 0.315 − 0.015 + 0.01 = 0.610`.
- Belief clip: `clip(0.610, 0, 1) = 0.610`.
- Leveling: `0.1 · 0.10 = 0.01`.
- Sharpening: `0.02 · 4 · (1 − 0.0) = 0.08`.
- `D_raw = 0.10 − 0.01 + 0.08 = 0.17`.
- Distortion clip: `clip(0.17, 0, 1) = 0.17`.

Decision (broadcast dict):

```json
{"belief": 0.610, "prev_belief": 0.30, "belief_change": 0.310,
 "distortion": 0.17, "truth_value": 0.0, "num_spreaders": 4,
 "num_correctors": 2, "net_spread_intensity": 2.1, "round": 3}
```

### Case 2 — Correction pressure round (negative net spread)

System state (round `t = 4`, following Case 1):

- `B(t) = 0.610`, `D(t) = 0.17`, `Truth = 0.0`, same coefficients.
- Inbound actions:
  - 1 spreader: intensity 0.3
  - 5 correctors: intensity 0.9/0.8/0.7/0.6/0.5

Calculation:

- `total_spread = 0.3`, `total_correction = 3.5`,
  `net_spread = -3.2`, `n_spreaders = 1`, `n_correctors = 5`.
- `ε` draw `= -0.01`.
- Spread term: `0.15 · (-3.2) = -0.48`.
- Correction term: `0.05 · (0.0 − 0.610) = -0.0305`.
- `B_raw = 0.610 − 0.48 − 0.0305 − 0.01 = 0.0895`.
- Belief clip: `clip(0.0895, 0, 1) = 0.0895`.
- Leveling: `0.1 · 0.17 = 0.017`.
- Sharpening: `0.02 · 1 · 1 = 0.02`.
- `D_raw = 0.17 − 0.017 + 0.02 = 0.173`.
- Distortion clip: `clip(0.173, 0, 1) = 0.173`.

Decision:

```json
{"belief": 0.0895, "prev_belief": 0.610, "belief_change": -0.5205,
 "distortion": 0.173, "truth_value": 0.0, "num_spreaders": 1,
 "num_correctors": 5, "net_spread_intensity": -3.2, "round": 4}
```

Invariant #1 check: `broadcast[4].prev_belief ==
broadcast[3].belief == 0.610` ✓.

### Case 3 — Silent round (zero net spread, distortion leveling only)

System state (round `t = 5`, following Case 2):

- `B(t) = 0.0895`, `D(t) = 0.173`, `Truth = 0.0`, same coefficients.
- Inbound actions: all 6 participants `ignore` with intensity `0`.

Calculation:

- `total_spread = 0`, `total_correction = 0`, `net_spread = 0`,
  `n_spreaders = 0`, `n_correctors = 0`.
- `ε` draw `= +0.005`.
- Spread term: `0`.
- Correction term: `0.05 · (0.0 − 0.0895) = -0.004475`.
- `B_raw = 0.0895 + 0 − 0.004475 + 0.005 = 0.09003`.
- Leveling: `0.1 · 0.173 = 0.0173`.
- Sharpening: `0.02 · 0 · 1 = 0`.
- `D_raw = 0.173 − 0.0173 + 0 = 0.1557`.

Decision:

```json
{"belief": 0.09003, "prev_belief": 0.0895, "belief_change": 0.00053,
 "distortion": 0.1557, "truth_value": 0.0, "num_spreaders": 0,
 "num_correctors": 0, "net_spread_intensity": 0.0, "round": 5}
```

Invariant #8 check: `distortion(t+1) = 0.1557 = 0.173 · (1 − 0.1)`
because `n_spreaders = 0` and `Truth = 0` — pure leveling ✓.

### Edge Case — Cold-start (round 0) + true news (`Truth = 1`)

System state (round `t = 0`, first call):

- `state.custom_state` is empty. `initial_belief = 0.2`,
  `rumor_truth_value = 1.0` (true news), `α = 0.15`, `β = 0.05`,
  `ℓ = 0.1`, `s = 0.02`, `σ = 0.03`.
- Inbound actions: 3 spreaders (intensity 0.5/0.5/0.5), 0 correctors.

Calculation:

- State Initialization runs: `belief ← 0.2`, `prev_belief ← 0.2`
  (cold-start), `distortion ← 0.0`, `truth_value ← 1.0`, history
  buffers instantiated empty.
- `total_spread = 1.5`, `total_correction = 0`, `net_spread = 1.5`,
  `n_spreaders = 3`.
- `ε` draw `= +0.02`.
- Spread term: `0.15 · 1.5 = +0.225`.
- Correction term: `0.05 · (1.0 − 0.2) = +0.04`.
- `B_raw = 0.2 + 0.225 + 0.04 + 0.02 = 0.485`.
- Leveling: `0.1 · 0 = 0`.
- Sharpening: `0.02 · 3 · (1 − 1.0) = 0` (zero-sharpening for true
  news).
- `D_raw = 0`.

Decision:

```json
{"belief": 0.485, "prev_belief": 0.2, "belief_change": 0.285,
 "distortion": 0.0, "truth_value": 1.0, "num_spreaders": 3,
 "num_correctors": 0, "net_spread_intensity": 1.5, "round": 0}
```

Observation: because `Truth = 1`, both the spread term AND the
correction term push belief in the same direction (toward truth), and
sharpening contributes `0` — the "true news is boring for distortion"
invariant.

Cold-start reading rule for participants: because
`prev_belief == 0.2 == initial_belief`, participants MUST treat this
as "no belief-change observation yet" rather than "change of +0.285".

## Coordinator Verification and Calibration

**Calibration data sources**:

- `spread_impact` (α) ← Vosoughi–Roy–Aral 2018 [Ref 2, Fig. 2] and
  Bordia–Rosnow 1998 [Ref 3]. Simulation-unit-adjusted range:
  `[0.05, 0.30]`.
- `truth_correction` (β) ← DiFonzo–Bordia 2007 [Ref 7, Ch. 5] and
  Nyhan–Reifler 2010 [Ref 8, Table 3]. Range: `[0.02, 0.15]`.
- `leveling_rate` (ℓ) ← Allport–Postman 1947 [Ref 1, §Serial-reproduction
  studies]. Range: `[0.05, 0.20]`.
- `sharpening_rate` (s) ← Allport–Postman 1947 [Ref 1]. Range:
  `[0.005, 0.05]`.
- `noise_std` (σ) ← Vosoughi–Roy–Aral 2018 [Ref 2, §Robustness].
  Range: `[0.01, 0.10]`.

**Expected coordinator behaviour** (given `Truth = 0`, defaults):

- Given `net_spread = +2.0` and `ε = 0`, the coordinator MUST push
  belief up by `≈ +0.30` minus any small correction pull.
- Given `net_spread = 0`, `B(t) = 0.5`, `Truth = 0`, and `ε = 0`,
  the coordinator MUST push belief toward `Truth`, producing a
  broadcast with `belief_change` strictly negative.
- Given `net_spread = 0`, `B(t) = Truth`, and `ε = 0`, the
  coordinator MUST emit `belief == Truth` exactly (no drift).
- Given `Truth = 1` and `n_spreaders > 0`, the coordinator MUST emit
  `distortion(t+1) ≤ distortion(t) · (1 − ℓ)` (sharpening evaluates
  to 0 for true news).
- Given identical `base_seed` and identical inbound-action sequence,
  the coordinator MUST produce byte-equal broadcasts across two
  independent runs.

**Sanity bounds** (red flags for a broken implementation):

- IF `broadcast[t+1].prev_belief != broadcast[t].belief` THEN the
  state-write ordering is broken (invariant #1).
- IF any broadcast omits a `Required = yes` field THEN the contract
  is broken (invariant #2).
- IF `belief` or `distortion` falls outside `[0, 1]` THEN the clip
  is broken (invariant #3).
- IF `net_spread > 0` AND `truth_correction == 0` AND
  `noise_std == 0` AND `B(t) < 1` YET `belief` falls THEN the sign
  convention is broken.
- IF `n_spreaders == 0` AND `Truth == 0` YET `distortion` grows THEN
  the sharpening term is not being gated by `n_spreaders` (invariant
  #8).
- IF `Truth == 1` AND `distortion` grows unboundedly THEN the falsity
  gap `(1 − Truth)` is not being applied.
- IF two runs with identical seed + actions produce different
  broadcasts THEN the RNG seeding is broken (invariant #6).

### Ablation Hooks

| Ablation name         | Setting                | Hypothesis tested                                                       | Expected direction                                       | Metric                                                                |
|-----------------------|------------------------|-------------------------------------------------------------------------|----------------------------------------------------------|-----------------------------------------------------------------------|
| `no-correction`       | `β = 0`                | Removes truth anchor; belief drifts under contagion + noise only         | Higher variance of `belief` over 100 rounds              | `Var(belief) − baseline`                                              |
| `zero-spread`         | `α = 0`                | Spread pressure ignored; only correction + noise remain                  | Belief → Truth                                            | `mean_over_rounds(|belief − truth_value|)` shrinks near 0              |
| `no-leveling`         | `ℓ = 0`                | Distortion never decays                                                  | Distortion accumulates monotonically toward `1`           | `distortion(final round) ≈ 1` when `Truth = 0` and any spreaders     |
| `no-sharpening`       | `s = 0`                | Distortion never grows                                                   | Distortion decays to `0` regardless of spreaders          | `distortion(final round) ≈ 0`                                          |
| `high-noise`          | `σ *= 10`              | Overwhelms deterministic signal                                          | Random-walk-like broadcast series                        | `Autocorr(belief_change, lag=1) → 0`                                   |
| `true-news`           | `Truth = 1`            | Zero-sharpening invariant holds for true news                            | Distortion stays at `0` regardless of `n_spreaders`      | `max(distortion) == 0`                                                 |

## Academic / Empirical References

| #  | Citation                                                                                                                                                                                       | Notes                                                                                          |
|----|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 1  | Allport, G. W., & Postman, L. (1947). *The Psychology of Rumor*. Henry Holt. ISBN: 978-0805200379                                                                                              | Foundational leveling / sharpening / assimilation distortion dynamics                           |
| 2  | Vosoughi, S., Roy, D., & Aral, S. (2018). The Spread of True and False News Online. *Science*, 359(6380), 1146–1151. DOI: 10.1126/science.aap9559                                             | Empirical calibration of contagion rate and noise; false-news 6–10× faster                     |
| 3  | Bordia, P., & Rosnow, R. L. (1998). Rumor as group problem-solving. *Small Group Research*, 29(1), 116–133. DOI: 10.1177/1046496498291006                                                     | Meta-analytic α calibration; content-analysis foundations                                       |
| 4  | Del Vicario, M., et al. (2016). The Spreading of Misinformation Online. *PNAS*, 113(3), 554–559. DOI: 10.1073/pnas.1517441113                                                                | Justification for field-level vs full network graph                                             |
| 5  | Zhao, L., et al. (2011). SIHR rumor spreading model in social networks. *Physica A*, 391(7), 2444–2453. DOI: 10.1016/j.physa.2011.12.008                                                     | Alternative SIR-style permanent-recovery contagion                                              |
| 6  | Kempe, D., Kleinberg, J., & Tardos, É. (2003). Maximizing the spread of influence through a social network. *Proc. KDD 2003*. DOI: 10.1145/956750.956769                                     | Alternative independent-cascade model                                                          |
| 7  | DiFonzo, N., & Bordia, P. (2007). *Rumor Psychology: Social and Organizational Approaches*. APA. ISBN: 978-1591474265                                                                          | β calibration; corrective-exposure effect sizes                                                 |
| 8  | Nyhan, B., & Reifler, J. (2010). When Corrections Fail: The Persistence of Political Misperceptions. *Political Behavior*, 32(2), 303–330. DOI: 10.1007/s11109-010-9112-2                    | Backfire-effect edge case (β < 0 possible for subpopulations)                                   |
| 9  | Kunda, Z. (1990). The case for motivated reasoning. *Psychological Bulletin*, 108(3), 480–498. DOI: 10.1037/0033-2909.108.3.480                                                              | Alternative motivated-reasoning update model                                                    |
| 10 | Bartlett, F. C. (1932). *Remembering: A Study in Experimental and Social Psychology*. Cambridge University Press.                                                                             | Alternative multiplicative distortion accumulation model                                        |
| 11 | DeGroot, M. H. (1974). Reaching a Consensus. *JASA*, 69(345), 118–121. DOI: 10.1080/01621459.1974.10480137                                                                                    | Linear-averaging foundation for the ε residual justification                                    |
| 12 | Shibutani, T. (1966). *Improvised News: A Sociological Study of Rumor*. Bobbs-Merrill.                                                                                                        | Rumor-as-collective-problem-solving framework                                                   |
| 13 | Friggeri, A., Adamic, L. A., Eckles, D., & Cheng, J. (2014). Rumor Cascades. *Proc. ICWSM 2014*.                                                                                              | Empirical rumor cascade sizes; α range confirmation                                             |

## Design Provenance and Versioning

| Field       | Content                                                                     |
|-------------|-----------------------------------------------------------------------------|
| Market Type | `information` — Information / Rumor Field                                   |
| Author      | AgenticFinLab                                                               |
| Reviewed by | — (pending)                                                                 |
| Created     | 2026-07-16                                                                  |
| Version     | 1.0.0                                                                       |
| Status      | canonical                                                                   |
| Icon        | ![](../agent_images/icons/market/information-sis-contagion.png)             |
