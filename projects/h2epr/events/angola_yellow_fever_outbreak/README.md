# Angola Yellow Fever Outbreak of 2016

H2EPR-0551 uses the stable slug `angola_yellow_fever_outbreak` and covers the
dataset Draft from late December 2015 through its open-ended surveillance
stage after 7 September 2016. The Source Profile is `full_draft_exposed`; the
bounded objective is a dataset-conditioned Rule simulation of represented
detection, laboratory confirmation, vaccination response, cross-border
coordination, emergency review, and continuing surveillance.

## Event assets

The [Source Profile](source-profile.json) seals exactly `event_spec.json`,
`frozen_evidence.json`, and `draft_epg.json`. The
[roster and actor map](../../agents/rosters/angola_yellow_fever_outbreak/)
preserve 10 unique source participant IDs and 31 appearances. Seven
[Agent Definitions](../../agents/defines/angola_yellow_fever_outbreak/) and
one [Population Model](../../populations/models/angola_yellow_fever_outbreak/angola_drc_affected_residents.md)
provide the human semantic parents; the
[participant-interface release](../../agents/interfaces/angola_yellow_fever_outbreak/)
closes observations, intents, and lifecycles. P_7 and P_10 remain world-state
dispositions because the Draft exposes no autonomous choice for them.

The [Scenario release](../../scenarios/angola_yellow_fever_outbreak/) owns the
event world and declarative mechanism. The
[shared configuration](../../configs/angola_yellow_fever_outbreak/shared/)
selects coordinates, opening state, routes, and termination; the
[Rule configuration](../../configs/angola_yellow_fever_outbreak/backends/rule/)
selects deterministic decisions only. The
[Rule realization](../../execution/angola_yellow_fever_outbreak/rule/) pins the
common implementation. [Package assembly](package-assembly.json) compiles to
the backend-neutral [event package](package/).

The Draft includes reversed relation direction, participant names inconsistent
with their IDs, changing P_3 geographic scope, and an open end. These source
conditions remain visible in the Source Profile and roster. Executable
authority is rebuilt through the reviewed actor map and Scenario rather than
copied from inconsistent relation rows.

## Backend status

| Backend | Status | Current evidence or failure |
|---|---|---|
| Rule | implemented | admitted configuration and realization; current package binding; independently verified [run release](../../releases/angola_yellow_fever_outbreak/rule/) |
| LLM | planned | no registered implementation, model provenance, parser, retry, or failure evidence; admission fails closed |
| RuleLLM | planned | no proposal/admission implementation or repair evidence; admission fails closed |

Attaching Rule leaves the package-core identity unchanged. Planned catalog
entries declare availability status and cannot act as fallback backends.

## Current result

The current canonical seed-0 Rule run is `run.c8e90196fadcf5a18b9b9f9a`. Its
8 actors execute 20 coordinates and produce
826 trace records, 866 graph nodes, and
2,481 graph edges. Exact identities, deterministic A/B evidence,
generated-ID invariance, replay, and terminal transport are in the
[run release](../../releases/angola_yellow_fever_outbreak/rule/).

The current policy uses bounded activation windows, retained received messages,
and own-action memory. Descriptive expectations are distinct from validity:
trace, seals, actual-state replay, graph provenance, and zero unresolved
transport remain mandatory. The
[simulation reading](../../reports/angola_yellow_fever_outbreak/rule/simulation-reading.md)
reviews the full output with a complete machine scan and coordinate-level
semantic analysis. Raw custody is retained under ignored
`.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-behavior/`.

The [current-event registry](../current-events.json) and
[cross-event Rule conformance](../../releases/cross-event/rule/) cover the
current event set. Use the maintained CLI and complete unittest suite for
package admission, fresh materialization, independent publication, and
registry verification.

## Claim boundary

The current result supports dataset-conditioned semantic construction,
package admission, deterministic Rule execution, integrity seals,
authoritative replay, trace-derived graph provenance, bounded simulation-only
description, and two-event engineering conformance. Full-Draft exposure,
mixed actorization, and explicit logical-time compression are part of that
result.

It does not support historical fit, parameter calibration, held-out evaluation
or performance, vaccination or public-health effectiveness, medical causality,
policy conclusions, scientific validity, or universal generality. Values such
as `participating`, `fractional_response_recorded`,
`no_recent_confirmed_cases_reported`, and `declared_ended` remain modeled
process or report states.
