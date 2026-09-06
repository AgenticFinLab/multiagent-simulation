# Lebanese Civil War

H2EPR-0892 uses the stable slug `lebanese_civil_war`. Its full-Draft, dataset-only Rule
baseline models a bounded public-record path from the 1975 opening boundary
through coalition, foreign-intervention and camp-conflict records to qualified
Taif and post-war records.

## Event assets

The [Source Profile](source-profile.json) seals exactly `event_spec.json`,
`frozen_evidence.json` and `draft_epg.json`. The
[roster and actor map](../../agents/rosters/lebanese_civil_war/) account for all 12 source
IDs and 40 appearances. Eight
[Agent Definitions](../../agents/defines/lebanese_civil_war/) own the active organizational
semantics; four passive or unknown sources remain explicit context and no
Population Model is required. The
[participant interface](../../agents/interfaces/lebanese_civil_war/) projects four
observation classes, 33 event intents plus `no_op`, and two lifecycles.

The [Scenario](../../scenarios/lebanese_civil_war/) defines a sparse record world, authority,
information routes and reducer. It keeps victim cohorts non-acting, discloses
organizational aggregation and refuses malformed Draft edges as authority. The
[shared configuration](../../configs/lebanese_civil_war/shared/) owns 21 coordinates,
opening state and routes; the
[Rule configuration](../../configs/lebanese_civil_war/backends/rule/) owns selected choices.
The [Rule realization](../../execution/lebanese_civil_war/rule/) pins the common
implementation. [Assembly](package-assembly.json) compiles to the backend-neutral
[event package](package/).

Casualties, displacement, territory, weapons, tactics, military success,
responsibility, constitutional implementation, disarmament, durable peace and
policy effectiveness remain outside the reducer. All war, Taif and post-war
fields are explicitly qualified records.

## Backend status

| Backend | Status | Current evidence or failure |
|---|---|---|
| Rule | implemented | admitted configuration/realization, exact package binding and independently verified run release |
| LLM | planned | no registered model-decision implementation or provenance; admission fails closed |
| RuleLLM | planned | no standardized proposal/admission implementation; admission fails closed |

Rule attaches without changing the backend-neutral package core. Planned catalog
entries provide no execution authority or fallback.

## Current result

The canonical seed-0 run is `run.391644c9adfa091e6d2109e9`: eight actors, 21 coordinates,
922 trace records,
963 graph nodes and
2,789 edges. Fresh A/B, generated-ID perturbation,
trace and tick/run seals, authoritative replay, complete graph reconstruction and
zero unresolved transport are independently verified in the
[run release](../../releases/lebanese_civil_war/rule/).

The [simulation reading](../../reports/lebanese_civil_war/rule/simulation-reading.md)
accounts for every output family, coordinate, non-default action and expectation.
Missing-Amal-invitation and delayed-camp-defence probes demonstrate valid open
endpoints under changed information while preserving release integrity. Raw
custody is retained below ignored `.local-runtime/h2epr-simulation/`.

The [current registry](../current-events.json) and
[cross-event Rule conformance](../../releases/cross-event/rule/) cover the
accepted event set. Descriptive endpoint agreement is separate from execution
and publication integrity.

## Claim boundary

This event establishes dataset-conditioned semantic construction,
state/information-aware deterministic Rule execution, independent verification,
replay, trace-derived graph provenance and bounded simulation-only description.
Full Draft exposure, representation gates, aggregation and logical-time choices
are part of the result.

It does not establish historical fit, parameter calibration, held-out
performance, conflict or peace effects, casualty or responsibility truth,
causality, scientific validity or universal generality. No external research,
Reference or model decision was used.
