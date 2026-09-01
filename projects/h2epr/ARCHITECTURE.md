# H2EPR architecture

H2EPR turns bounded event evidence into participant and scenario artifacts,
executes their interaction, and compiles the resulting trace into a generated
event process graph. The architecture separates research meaning from runtime
mechanics so that each result can be traced to its source and owner.

## System flow

```text
explicit sources
  -> typed construction records
  -> participant artifacts and event bundle
  -> actor-specific observations
  -> participant intents and messages
  -> environment adjudication
  -> authoritative state reduction
  -> trace, seals, and replay
  -> generated event process graph
  -> separately scoped human process analysis
```

## Responsibility boundaries

### Construction, runtime, and evaluation

Construction may read only explicitly declared source material. Runtime gives
each participant the information available to that participant and records the
generated interaction. Evaluation compares sealed outputs with separately
governed evidence after a run.

Evaluation data is not a construction input, runtime state, prompt, memory, or
retrieval source. A model built with access to the target continuation cannot
later be described as a clean held-out construction of that event.

Human analysis may begin from a sealed generated graph without opening an
evaluation target. It explains the simulated trajectory and its visible
limits. Comparison with a Draft graph, historical evidence, or a held-out
target is a later activity with its own exposure and claim boundary.

### Participant intent and environment result

Participants emit requests, proposals, decisions, or messages. The environment
checks institutional rules, authority, resources, and concurrent state before
producing an outcome. These are separate records:

- an action is requested;
- the request is accepted for processing;
- an effect is executed; and
- the effect succeeds, fails, is delayed, or has no result.

Only the reducer commits authoritative state. This keeps policy code from
silently manufacturing results and makes replay meaningful.

### H2EPR and MASim

MASim provides the repository's existing reusable execution infrastructure.
Domain-neutral event-process values, transport, reduction, trace, and seal
types live under `masim.integrations.event_process` and are consumed through
their public interfaces. H2EPR treats that package as a read-only base
framework.

H2EPR owns event evidence, participant semantics, institutional policies,
observation rules, event identities, interpretation, graph compilation, and
the shared execution layer needed across H2EPR events. Event-specific and
cross-event H2EPR code both remain in the H2EPR package.

## Project modules

| Module | Responsibility |
|---|---|
| `construction/` | Source authorization, hash checks, parsing, and typed construction records |
| `artifacts/` | Entity resolution, participant envelopes, and provenance |
| `bundles/` | Construction seals, event bundles, and cross-object validation |
| `policies/` | Declarative participant policy inputs |
| `world/` | Normalized world values and pure calculations |
| `agents/` | Definition profiles, semantic mapping, intent, and carrier checks |
| `configuration/` | Configuration schema admission, canonical identity, and receipts |
| `execution/` | Event-neutral run documents, closure checks, deterministic comparison, strict input handling, and local run custody |
| `scenarios/` | Event-specific bindings, environment policies, bounded conformance paths, and accepted comparisons that name specific events |
| `runtime/` | H2EPR simulation adapter, phased execution, detectors, and orchestration |
| `compiler/` | Sealed-trace validation and deterministic graph generation |

All modules in this table are under `projects/h2epr/src/h2epr`. Reviewed
Markdown, JSON, and release records remain in the adjacent project asset
directories.

Policy Realizations, executable successors, and compact run/graph release
records live under `execution/`. Large materialized traces, states, replay
outputs, and generated graphs remain in event-qualified ignored run
directories unless separately selected for release.

Tracked human readings and authorized comparison studies live under
`analysis/`. They reference immutable run identities rather than duplicating
the generated graphs or taking authority from event evidence and execution
releases.

## Construction and bundle assembly

The source adapter receives a list of descriptors and approved roots. It does
not discover sibling files or scan input directories. It verifies paths and
hashes, preserves raw values and exact source pointers, and exports a
deterministic construction snapshot.

```text
construction records
  -> entity registry
  -> reversible roster/loss report
  -> participant artifacts
  -> policy and world inputs
  -> construction seal
  -> runtime scenario bundle
```

Sensitivity values are explicit inputs rather than inferred historical facts.
Execution seeds are runtime inputs and do not change event-bundle identity.

## Participant, scenario, and configuration authority

| Question | Authority |
|---|---|
| Who is in scope and why? | Research roster and roster release |
| What can a participant know, decide, request, and retain? | Agent Definition or population model |
| What institutions, routes, resources, lifecycles, and results exist? | Event Scenario Definition |
| Which actors, units, opening records, selections, and sensitivities are used? | Scenario Configuration |
| How are released semantics represented by Contracts V1? | Consolidated mapping |
| Is one exact configuration structurally admissible? | Configuration schema and loader |
| Which semantics have executable policy behavior? | Versioned binding |
| Which state transition occurred? | Environment and reducer |

An actor-specific observation is projected from authoritative world state. It
contains explicit availability, freshness, source, and unresolved-value
markers. Persistent state that affects later behavior must remain visible to
trace and replay.

## Runtime, trace, and compilation

The H2EPR runtime follows the MASim setup, run, and shutdown lifecycle but uses
explicit phase barriers. Every participant decision for a tick observes the
same pre-state; completion order is canonicalized before reduction.

Runtime records use logical coordinates and deterministic ordering. Records
are hash chained, sealed per tick, and sealed again for the run. Validation
checks record coverage, manifests, committed states, tick identities, and the
run prefix before replay. The compiler accepts only a validated sealed trace
and produces a generated graph plus its graph seal.

## Package and release boundary

H2EPR is distributed from `projects/h2epr/pyproject.toml`, with one importable
package rooted at `src/h2epr`. Semantic scenario assets under `scenarios/` are
not import roots. Release checksums cover files owned by their release package;
hashes of upstream inputs are recorded in manifests.

## Current limitations

The Panic of 1907 construction canary was created with access to the full event
draft and supports architecture review rather than held-out evaluation. Its
bounded KT--NBC--NYCH binding remains a limited conformance release, while a
separate executable successor now covers the complete configured roster and
has produced deterministic trace, replay, and generated-graph closure.

The SingHealth Data Breach and Note7 battery recall also have accepted
full-roster executable successors and deterministic run, replay, and
generated-graph closure. None of the three events has calibrated parameters,
historical fit, held-out evaluation, or a scientific-validity result. Those
are separate research activities, not implied by closure of the engineering
interfaces.

The accepted
[three-event conformance successor](execution/cross-event-conformance-v0.2/)
validates three compact run releases through one H2EPR contract while
preserving the accepted [two-event v0.1 record](execution/cross-event-conformance-v0.1/).
It demonstrates reuse of closure mechanics across three event domains; it does
not establish support for every domain.

## Related documents

- [Event modeling workflow](WORKFLOW.md)
- [Rule execution](execution/README.md)
- [Three-event execution conformance](execution/cross-event-conformance-v0.2/)
- [Evolution and compatibility](EVOLUTION.md)
- [Contracts V1](contracts/v1/README.md)
- [Architecture decisions](decisions/)
