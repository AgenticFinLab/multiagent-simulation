# ADR-0019: admit Note7 full-roster Rule execution and three-event conformance

- Status: accepted
- Date: 31 August 2026
- Scope: H2EPR-0481 deterministic Rule execution and additive three-event conformance
- Extends: ADR-0013

## Context

ADR-0013 established the full-roster Rule-execution boundary using Panic of
1907 and SingHealth as two independently specified consumers. H2EPR-0481 later
completed its Frame, eight-product roster, consolidated mapping, Event
Scenario Definition, qualitative Scenario Configuration, static admission,
bounded carrier binding, and lineage conformance. A third-event execution was
authorized to test the maintained workflow and shared assets without changing
the accepted semantic parents or MASim.

Note7 differs materially from the earlier events. It includes corporate
product-safety choice, jurisdictional recall authority, regional and outlet
implementation, consumer choice, transport-warning and emergency-order
issuance, and air-operator handling. Its core interval ends on 15 October 2016;
January 2017 findings are future-only.

## Decision

### `OD-0481-EXE-01` — event-owned Rule realization

H2EPR-0481 receives its own Policy Realization, executable package, runtime
bundle, reducer behavior, run release, and generated-graph compiler adapter.
The implementation closes eight actor-capability placements, 22 commitments,
37 intents, nine selected Scenario policies, and twelve lifecycle families.
Event semantics remain in the Note7 scenario package.

### `OD-0481-EXE-02` — exact configured routing and authority

All participant messages use one exact sender and recipient and resolve to an
accepted configuration route record. Corporate program, formal recall,
warning, emergency order, delivery, implementation, enforcement, remedy, and
consumer response remain separate. The reducer alone changes authoritative
state; participants do not author physical, institutional, or other-actor
results.

### `OD-0481-EXE-03` — pending reference does not globally lock commitments

A pending active reference may coexist with evaluation of a later distinct
commitment. Idempotency remains qualified by the concrete intent and
commitment. This avoids turning one scalar pending marker into an undeclared
global halt while preserving explicit duplicate dispositions and lifecycle
ownership. The choice is implemented within the existing participant and
lifecycle contracts; no shared schema change is required.

### `OD-0481-EXE-04` — paired run and trace-derived graph

The accepted package is materialized twice from fresh operational roots with
the same bundle and seed `481`. All eight run documents must be byte-identical
and canonically identical. Trace validation, tick and run seals,
authoritative replay, transport closure, and generated-graph reference closure
are mandatory. Large outputs remain in event-qualified ignored custody.

### `OD-0481-EXE-05` — additive conformance successor

The accepted two-event conformance release v0.1 remains unchanged. A v0.2
successor re-admits Panic, SingHealth, and Note7 through the same event-neutral
closure contract while preserving their unequal coverage vectors. Event
identity, actors, semantics, time, counts, policies, state, and graph content
remain parameters rather than shared-kernel constants.

### `OD-0481-EXE-06` — framework and claim boundary

`masim/` remains read-only. H2EPR uses the public phased-runner,
event-process, transport, reducer, trace, seal, and replay interfaces. The
result is limited to deterministic, uncalibrated mechanism-coverage
engineering across three accepted events. It does not establish historical
fit, held-out performance, recall or policy effectiveness, causal validity,
scientific validity, or universal generality.

## Consequences

The repository gains a third complete real-event execution and an additive
three-event conformance release without rewriting either earlier event or the
accepted v0.1 comparison. The third event exercises new institutional and
product-safety mechanisms while reusing the shared H2EPR document, closure,
comparison, custody, participant, and lifecycle contracts.

The current interpreter lacks the optional `lmbase` history-store dependency
used by the generic BaseSimulator. The Note7 phased engine does not consume
that history slot; local formal runs used an in-memory compatibility fixture
there and executed the remaining repository runtime unchanged. This is a
recorded environment limitation requiring a fully provisioned rerun before
external publication, not authorization to weaken dependency or runtime
checks.
