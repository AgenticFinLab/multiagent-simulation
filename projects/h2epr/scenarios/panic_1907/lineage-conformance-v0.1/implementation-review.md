# E7 implementation review and method closeout

## Review basis

The review used the accepted E6 raw manifest anchor
`4c263bec986fd49c260881a6dc17422598f51f5114ceb69e500a9ead3319f1c1`,
the `h2epr-roster-mapping-conformance` review rubric, and the S4 authorization.
The four E6 implementation files and their hashes were treated as frozen.

## Findings and dispositions

No blocking or major defect remains.

1. **Cross-object provenance was not provable by per-object validation alone.**
   A well-formed NBC carrier can contain a different valid SHA-256, and a
   well-formed NYCH carrier can cite a different stable message ID. The E7
   sequence validator now checks original action/message identity, request
   identity/version/content hash, mandate, represented sender, courier role,
   exact delivered hop, case lineage, and scoped result. This is an E7
   conformance rule; it does not change E6 semantics.
2. **Trace evidence needed an exact identity without creating a runtime.** The
   fixed runner pins the E6 release and its own implementation hash, emits 50
   deterministic records across five logical ticks, seals every tick and the
   run, and reconstructs the same eight-delta final state. No scheduler,
   simulator, Ray actor, stochastic branch, or full-event loop was added.
3. **Action acceptance could still be mistaken for delivery.** The trace now
   records accepted action disposition, scoped business disposition with no
   resource action, outbound message, and later delivery as separate layers.
4. **A tracked full trace would duplicate reproducible evidence.** The closeout
   stores only the expected-vector receipt. Tests regenerate the trace twice,
   compare exact records and seals, validate its chain, and compare the receipt.

## Negative-conformance coverage

The focused suite rejects or detects:

- external E6 manifest drift;
- KT bypass of NBC and borrowed authority;
- validly shaped NBC provenance drift;
- downstream activation without exact delivery;
- a wrong but well-formed NYCH delivered-message reference;
- back-projection of the later member facility into 21 October;
- conflation of action admission, business result, resource effect, and
  delivery; and
- trace mutation or replay from a wrong prestate.

These cases protect distinct accepted invariants. No exhaustive field matrix
or unsupported participant branch was added.

## Mainline and depth audit

The work remains on the standardization mainline:

- scope is still KT, NBC, and NYCH; no other actor appears in the executable
  conformance surface;
- action/route inventories remain four and three;
- policy coverage remains the six E6 lineage implementations; the amount,
  service, and venue policies remain unbound;
- the accepted configuration remains non-executable with all nine top-level
  policy selections unchanged;
- all E5 and E6 protected hashes reverify unchanged;
- the only runtime-like state is seven fixed symbolic fields plus its version,
  and every one supports ordering, result separation, or replay;
- the runner has one fixed positive branch and five ticks, so it does not
  approximate a full event; and
- calibration, historical fitting, held-out construction, post-seal
  evaluation, and validity claims remain absent.

Depth is proportionate to the reusable boundary: one fixture builder, one
cross-hop validator, one deterministic trace/replay runner, one focused test
module, and one receipt. Further negatives, policy branches, actors, or event
time steps would now deepen the first event without testing a new standardized
seam.

## Reusable method delta

The existing `h2epr-roster-mapping-conformance` Skill now links a narrow
`bounded-lineage-conformance` reference. It formalizes the demonstrated
E6--E7 handoff: freeze E6, separate carrier and cross-hop checks, choose
high-information negatives, reuse domain-neutral trace/seal/replay primitives,
store a reproducible expected vector, and perform a mainline/depth gate before
closing.

The method remains a working candidate until another event forward-tests it.

## Verdict and next-event decision

Verdict: `PASS_BOUNDED_LINEAGE_CONFORMANCE`.

H2EPR-0288 should stop at this E7 baseline. The next standardization task is a
second-event application beginning at the stage supported by its accepted
inputs; it should not copy H2EPR-specific actors, IDs, policies, or outcomes.
