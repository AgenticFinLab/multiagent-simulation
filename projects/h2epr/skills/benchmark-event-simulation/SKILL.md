---
name: benchmark-event-simulation
description: Orchestrate a complete H2EPR dataset-only event package, implemented backend, sealed run, and generated-process reading.
---

# Benchmark event simulation

Use this Skill as the thin end-to-end entry point. Invoke the specialized Skill
for each product; do not duplicate its content here.

Read [references/guide.md](references/guide.md) before starting a new event.
It provides the phase contract, artifact handoffs, command sequence, stop/resume
record, feedback classification, and final acceptance checklist.

## Read first

Read `BENCHMARK_PROTOCOL.md`, `ARCHITECTURE.md`, `WORKFLOW.md`,
`NEW_EVENT_PLAYBOOK.md`, the schema catalog, and the selected event entry. Do
not inventory or open Reference or evaluation-only siblings.

## Procedure

1. Record Git and authorization state.
2. Use `benchmark-input-admission` to publish or verify the Source Profile.
3. Use `event-agent-batch`, `agent-definition`, `population-model`, and
   `agent-definition-review` for the complete participant set.
4. Use `roster-mapping-conformance` to close the roster, actor map, and
   interface registries.
5. Use `event-scenario-design` and `scenario-configuration` to close world
   semantics and exact selections.
6. Compile the backend-neutral core in `events/<event>/package/` with the
   generic compiler. Validate source, roster, human semantic parents,
   registries, mechanism, configuration receipts, realization, and
   implementation-source hashes.
7. Use `backend-realization` for one actually implemented backend, attach it
   through the typed registry, and prove the package core identity is stable.
8. Use `run-release-verification` for custody, replay, trace-complete graph,
   repeatability or model provenance, and compact release. For Rule, require
   A/B byte identity, identity perturbation, and zero unresolved transport.
9. Use `generated-process-analysis` for the simulation reading and any
   authorized comparison.
10. Route reusable findings to the owning template, Skill, schema, or shared
    code; keep event-specific findings local.
11. Promote the individually closed event by adding its complete paths to the
    declarative current-event registry; do not add an event tuple or domain
    branch to common code.
12. When promotion yields at least two independent current events, derive
    cross-event conformance for package family, backend catalog, runtime/MASim
    source identities, output roles, replay/graph/transport closure, and claim
    exclusions. Record the exact event count; more events extend evidence
    without changing the contract. With zero or one row, record cross-event
    evidence as not applicable.

## Stop conditions

Stop without promotion on input drift, protected exposure, unresolved semantic
parents, package/config/binding mismatch, missing backend, hidden fallback,
trace/seal/replay/graph failure, or an unmet repeatability/provenance gate.

## Completion record

Report the exact package, run, trace, run-seal, final-state, replay, and graph
identities; manifest, binding, H2EPR runtime, and MASim kernel identities;
actor/tick/record/node/edge counts; unresolved messages; tests; source
exposure; implemented and unimplemented backends; remaining model failures;
and the next legal action.
