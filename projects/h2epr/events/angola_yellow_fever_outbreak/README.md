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
| Rule | implemented | admitted configuration and realization; package binding `be5013c…a269`; independently verified [run release](../../releases/angola_yellow_fever_outbreak/rule/) |
| LLM | planned | no registered implementation, model provenance, parser, retry, or failure evidence; admission fails closed |
| RuleLLM | planned | no proposal/admission implementation or repair evidence; admission fails closed |

Attaching Rule leaves the package-core identity unchanged. Planned catalog
entries declare availability status and cannot act as fallback backends.

## Current result

The accepted canonical seed-0 Rule run is
`run.2c5f37a8e456f99bdb1eff02`. Package SHA-256 is
`d6456af798b2593d264b18f7b1a4f0bf360682cfe36a26965ed3d29dbfe5c2b6`;
run-manifest SHA-256 is
`32527f4ebacc54e2762a392d28daf5d0c0b9b7297c44ae9f79e738b392c37dcb`;
trace SHA-256 is
`edec83529744119588cc50c14acb83c270f93699335121ecc791a858b404b1e0`;
final-state SHA-256 is
`0a0b2245ca514c0ad69a212a0f0338cc836ad08065a301e1d024bd75aae700a4`;
and the Generated EPG seal is
`e76b4c4960a607af51ab274bb0634834562cc54ef8da4af1d05fb89ff7cd346f`.

Eight actors execute 20 coordinates. The trace has 826 records; the
trace-derived graph has 866 nodes and 2,147 edges; terminal transport has zero
unresolved messages. Canonical A/B outputs are byte-identical, the
generated-ID perturbation preserves semantic trace/graph and exact final
state, and authoritative replay passes. The
[simulation-only reading](../../reports/angola_yellow_fever_outbreak/rule/simulation-reading.md)
traverses every record, node, and edge. Raw custody remains under ignored
`.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/current/`.

This event is one of two rows in `current-events.json`. The
[two-event Rule conformance release](../../releases/cross-event/rule/) covers
the complete registry and passes with receipt
`0d5d612447e8541e4f5f2f387574649a9d7f2f7880e9de7f31a674445bf88364`.

Validation uses `python -B -m h2epr.cli validate-package`, three fresh
materializations, `python -B -m h2epr.cli identity-conformance`, independent
`publish-run-release`, `python -B -m h2epr.cli validate-registry`, independent
`publish-cross-event-release`, and the complete dependency-light unittest
suite from the repository root with
`PYTHONPATH=projects/h2epr/src:projects/h2epr/tests`.

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
as `participating`, `implemented_fractional`,
`no_recent_confirmed_cases_reported`, and `declared_ended` remain modeled
process or report states.

The next legal action is a separately authorized third unseen event,
perturbation, or backend implementation. This release does not authorize
LLM/RuleLLM development or scientific evaluation.
