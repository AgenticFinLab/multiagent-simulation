# East Palestine Train Derailment

H2EPR-0196 uses the stable slug `east_palestine_train_derailment` and covers the dataset Draft from the February 2023 derailment through its January 2025 endpoint. The Source Profile is `full_draft_exposed`; the bounded objective is a dataset-conditioned Rule simulation of the represented response, cleanup, legal, public-reporting, and settlement process.

## Event assets

The [Source Profile](source-profile.json) seals exactly `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`. The [roster and actor map](../../agents/rosters/east_palestine_train_derailment/) preserve 7 unique participant IDs and 26 appearances. Six [Agent Definitions](../../agents/defines/east_palestine_train_derailment/) and one [Population Model](../../populations/models/east_palestine_train_derailment/east_palestine_residents.md) provide the human semantic parents; the [participant-interface release](../../agents/interfaces/east_palestine_train_derailment/) closes their observations, intents, and lifecycles.

The [Scenario release](../../scenarios/east_palestine_train_derailment/) owns the event world and declarative mechanism. The [shared configuration](../../configs/east_palestine_train_derailment/shared/) selects its coordinates, opening state, routes, and termination, while the [Rule configuration](../../configs/east_palestine_train_derailment/backends/rule/) selects deterministic decisions only. The [Rule realization](../../execution/east_palestine_train_derailment/rule/) pins the common implementation. [Package assembly](package-assembly.json) compiles to the backend-neutral [event package](package/).

The Draft contains relation-direction and participant-semantic inconsistencies. The roster preserves source participant facts, but executable authority is rebuilt through the reviewed actor map and interface rather than copied from those relation rows.

## Backend status

| Backend | Status | Current evidence or failure |
|---|---|---|
| Rule | implemented | admitted configuration and realization; package binding `9588486a…a4b17d`; independently verified [run release](../../releases/east_palestine_train_derailment/rule/) |
| LLM | planned | no registered implementation, model provenance, parser, retry, or failure evidence; admission fails closed |
| RuleLLM | planned | no proposal/admission implementation or repair evidence; admission fails closed |

Attaching Rule leaves the package-core identity unchanged. Planned catalog entries are availability declarations, not substitute backends.

## Current result

The accepted canonical seed-0 Rule run is `run.4cc6658590d5447313ff426b`. Package SHA-256 is `f1f30080e857417ed06cb45b3cbb25b37ea5a7fac72339978185f37dd657e297`; run-manifest SHA-256 is `2e9b537403377fc0d8f8f5f17e12c71239a0b1611161cc2070dcf501ea97f399`; trace SHA-256 is `a90e4b657e6f46c137e5d847a1e77da378f9309614e72be0fb1e66551cd7438a`; final-state SHA-256 is `1b7dbf7b8e8e85bd7ff1fa172fd544d6d57a434d572fa1f446ade7d4333d5599`; and the Generated EPG seal is `b36314507aa0b70878f8346ccec20df418cb804401fe91ffc63ca3754ec0eab2`.

Seven actors execute 11 coordinates. The trace has 405 records; the trace-derived graph has 432 nodes and 1,056 edges; terminal transport has zero unresolved messages. Canonical A/B outputs are byte-identical, the generated-ID perturbation preserves semantic trace/graph and exact final state, and authoritative replay passes. The [simulation-only reading](../../reports/east_palestine_train_derailment/rule/simulation-reading.md) traverses every record, node, and edge. Raw custody remains under ignored `.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/current/`.

This event is one of two rows in `current-events.json`. The
[two-event Rule conformance release](../../releases/cross-event/rule/) covers
the complete registry and passes with receipt
`0d5d612447e8541e4f5f2f387574649a9d7f2f7880e9de7f31a674445bf88364`.

Validation uses `python -B -m h2epr.cli validate-package`, three fresh materializations, independent `publish-run-release`, `python -B -m h2epr.cli validate-registry`, and the complete dependency-light unittest suite from the repository root with `PYTHONPATH=projects/h2epr/src:projects/h2epr/tests`.

## Claim boundary

The current result supports dataset-conditioned semantic construction, package admission, deterministic Rule execution, integrity seals, authoritative replay, trace-derived graph provenance, and a bounded simulation-only process description. Full-Draft exposure and explicit logical-time compression are part of that result.

It does not support historical fit, parameter calibration, held-out evaluation or performance, cleanup or policy effectiveness, medical or environmental causality, scientific validity, or universal generality. Process labels such as `filed`, `characterization`, and `announced` do not prove downstream implementation or real-world outcome.

The next legal action is a separately authorized third unseen event,
perturbation, or future backend comparison. This release does not authorize
LLM/RuleLLM development or scientific evaluation.
