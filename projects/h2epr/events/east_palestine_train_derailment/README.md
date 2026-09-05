# East Palestine Train Derailment

H2EPR-0196 uses the stable slug `east_palestine_train_derailment` and covers the dataset Draft from the February 2023 derailment through its January 2025 endpoint. The Source Profile is `full_draft_exposed`; the bounded objective is a dataset-conditioned Rule simulation of the represented response, cleanup, legal, public-reporting, and settlement process.

## Event assets

The [Source Profile](source-profile.json) seals exactly `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`. The [roster and actor map](../../agents/rosters/east_palestine_train_derailment/) preserve 7 unique participant IDs and 26 appearances. Six [Agent Definitions](../../agents/defines/east_palestine_train_derailment/) and one [Population Model](../../populations/models/east_palestine_train_derailment/east_palestine_residents.md) provide the human semantic parents; the [participant-interface release](../../agents/interfaces/east_palestine_train_derailment/) closes their observations, intents, and lifecycles.

The [Scenario release](../../scenarios/east_palestine_train_derailment/) owns the event world and declarative mechanism. The [shared configuration](../../configs/east_palestine_train_derailment/shared/) selects its coordinates, opening state, routes, and termination, while the [Rule configuration](../../configs/east_palestine_train_derailment/backends/rule/) selects deterministic decisions only. The [Rule realization](../../execution/east_palestine_train_derailment/rule/) pins the common implementation. [Package assembly](package-assembly.json) compiles to the backend-neutral [event package](package/).

The Draft contains relation-direction and participant-semantic inconsistencies. The roster preserves source participant facts, but executable authority is rebuilt through the reviewed actor map and interface rather than copied from those relation rows.

## Backend status

| Backend | Status | Current evidence or failure |
|---|---|---|
| Rule | implemented | admitted configuration and realization; current package binding; independently verified [run release](../../releases/east_palestine_train_derailment/rule/) |
| LLM | planned | no registered implementation, model provenance, parser, retry, or failure evidence; admission fails closed |
| RuleLLM | planned | no proposal/admission implementation or repair evidence; admission fails closed |

Attaching Rule leaves the package-core identity unchanged. Planned catalog entries are availability declarations, not substitute backends.

## Current result

The current canonical seed-0 Rule run is `run.293a2a817e42f1ea0578dc45`. Its
7 actors execute 11 coordinates and produce
405 trace records, 432 graph nodes, and
1,210 graph edges. Exact identities, deterministic A/B evidence,
generated-ID invariance, replay, and terminal transport are in the
[run release](../../releases/east_palestine_train_derailment/rule/).

The current policy uses bounded activation windows, retained received messages,
and own-action memory. Descriptive expectations are distinct from validity:
trace, seals, actual-state replay, graph provenance, and zero unresolved
transport remain mandatory. The
[simulation reading](../../reports/east_palestine_train_derailment/rule/simulation-reading.md)
reviews the full output with a complete machine scan and coordinate-level
semantic analysis. Raw custody is retained under ignored
`.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-05-passive-admission/`.

The [current-event registry](../current-events.json) and
[cross-event Rule conformance](../../releases/cross-event/rule/) cover the
current event set. Use the maintained CLI and complete unittest suite for
package admission, fresh materialization, independent publication, and
registry verification.

## Claim boundary

The current result supports dataset-conditioned semantic construction, package admission, deterministic Rule execution, integrity seals, authoritative replay, trace-derived graph provenance, and a bounded simulation-only process description. Full-Draft exposure and explicit logical-time compression are part of that result.

It does not support historical fit, parameter calibration, held-out evaluation or performance, cleanup or policy effectiveness, medical or environmental causality, scientific validity, or universal generality. Process labels such as `filed`, `characterization`, and `announced` do not prove downstream implementation or real-world outcome.
