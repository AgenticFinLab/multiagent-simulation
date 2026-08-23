# KT--NBC--NYCH implementation review

## Review basis

The review uses the exact binding release identified in `receipt.json` and the
`h2epr-roster-mapping-conformance` rubric. The binding's implementation
surfaces are treated as upstream inputs rather than changed to satisfy the
conformance case.

## Findings

No blocking or major defect remains.

1. **Per-object validation did not prove cross-object provenance.** A
   well-formed courier action can carry a different valid content hash, and a
   well-formed intake action can cite another stable message ID. The sequence
   validator therefore checks original action/message identity, request
   identity and version, content hash, mandate, represented sender, courier
   role, delivered hop, case lineage, and scoped result.
2. **Trace evidence required a stable identity without a runtime.** The fixed
   runner pins the binding release and its own implementation hash, emits a
   deterministic five-tick record chain, seals every tick and the run, and
   reconstructs the same final state. It adds no scheduler, simulator,
   distributed actor, stochastic branch, or event loop.
3. **Action acceptance and delivery needed separate evidence.** The trace
   records action admission, scoped business disposition, outbound message,
   and later delivery as distinct layers.
4. **A stored full trace would duplicate reproducible data.** The release keeps
   an expected-vector receipt. Tests regenerate the trace, compare records and
   seals, validate the chain, and compare replayed state.

## Negative-conformance coverage

The focused cases reject or detect:

- binding-manifest drift;
- Knickerbocker bypass of the courier or borrowed authority;
- validly shaped courier provenance drift;
- downstream activation without exact delivery;
- an incorrect but well-formed delivered-message reference;
- use of the later member facility on 21 October;
- conflation of action admission, business result, resource effect, and
  delivery; and
- trace mutation or replay from an incorrect pre-state.

These cases protect separate accepted invariants. They do not add an
exhaustive field matrix or unsupported participant branches.

## Scope and depth review

The executable surface remains limited to Knickerbocker Trust, National Bank
of Commerce, and New York Clearing House. Its four actions, three routes, and
six policy implementations are unchanged. Amount, service, and venue policies
remain unbound, and the accepted configuration remains non-executable.

The conformance state contains only the symbolic fields needed for ordering,
result separation, and replay. One fixed branch and five logical ticks do not
approximate a full event. Calibration, historical fitting, held-out
construction, post-seal evaluation, and validity claims remain outside scope.
Additional actors, branches, or event time steps would deepen the first event
without testing a new repository interface.

## Reusable method finding

The roster-mapping conformance method now records a bounded-lineage procedure:
freeze the accepted binding, separate carrier checks from cross-hop checks,
choose high-information negative cases, reuse domain-neutral trace/seal/replay
primitives, store a reproducible expected vector, and review scope before
closing the lineage.

The method remains provisional until another event tests it independently.

## Verdict

`PASS_BOUNDED_LINEAGE_CONFORMANCE`

H2EPR-0288 stops at this bounded baseline. A second-event application should
start from its own accepted inputs and must not copy Panic of 1907 actors,
identifiers, policies, or outcomes.
