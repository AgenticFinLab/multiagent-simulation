# ADR-0012: accept the SingHealth lineage-conformance boundary

- Status: accepted
- Date: 26 August 2026
- Scope: H2EPR-0616 SCM technical--operations--GCIO lineage conformance
- Resolved decisions: OD-CNF-01 through OD-CNF-04

## Context

The accepted H2EPR-0616 binding projects four selected participant intents and
four directed message carriers across one SCM technical unit, one operations
unit, and the SingHealth GCIO. It proves carrier compatibility but does not by
itself prove cross-hop identity, trace order, deterministic seals, or replay
from an explicit prestate.

The compatibility review found that the existing domain-neutral trace,
canonical hashing, tick-seal, run-seal, validation, and replay primitives can
close those questions without changing Contracts V1, MASim, the binding, or
the accepted non-executable configuration.

## Decision

### `OD-CNF-01` — exact binding, lineage, and horizon

Use only the accepted binding release identified by raw manifest SHA-256
`377b93361a6e47307ed8498f7bd86a7adc4174b09a49baf37803623181195343`.
The complete conformance horizon is three actors, four actions, four directed
routes, one verification result, and logical ticks zero through eight. Any
pinned binding drift returns to the binding phase.

### `OD-CNF-02` — deterministic trace and minimal replay state

Record one fixed branch with the existing trace, hash, seal, validation, and
replay primitives. Retain only state version plus finding, verification
request, verification result, escalation, and clarification stages. Repeated
construction must be byte-identical. Do not start a simulator, scheduler,
distributed actor system, or complete scenario runtime.

### `OD-CNF-03` — cross-hop checks and closeout evidence

Validate the selected V1 payloads and focused failures for manifest drift,
capacity, delivery, request, result, escalation, clarification, semantic
record order, trace mutation, and replay prestate. Keep action and
communication dispositions, message delivery, verification result, state
change, and later observation separate. Preserve the delivered clarification
as unresolved because the selected branch contains no reply.

### `OD-CNF-04` — release and stopping boundary

Publish one deterministic expected-vector receipt and one concise review after
focused, cross-event, full-suite, integrity, link, and package validation. Stop
at `PASS_BOUNDED_LINEAGE_CONFORMANCE`. Full-roster runtime, unrelated policies,
simulation, calibration, held-out or clean-builder work, evaluation, and
historical or scientific validity claims remain outside scope.

## Consequences

H2EPR-0616 reaches the same bounded lineage-conformance baseline as the Panic
of 1907 event without copying its event-specific actors, semantics, or outcome.
The second application shows that the repository's trace, seal, replay, and
closeout method transfers across distinct event domains without a shared
interface change.

The complete thirteen-actor configuration remains non-executable. The final
clarification remains an open request rather than a fabricated response, and
the synthetic positive branch remains engineering evidence rather than a
historical reconstruction or scientific evaluation.
