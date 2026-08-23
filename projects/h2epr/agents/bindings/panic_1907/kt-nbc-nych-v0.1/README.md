# KT--NBC--NYCH bounded binding v0.1

This package is the accepted E6 input for the bounded H2EPR-0288 conformance
lineage. It pins Scenario Configuration v0.1, its E5 admission receipt, the
consolidated Roster mapping profile, the machine binding, and the four Python
implementation surfaces used by the slice.

The externally anchored release-manifest SHA-256 is:

```text
4c263bec986fd49c260881a6dc17422598f51f5114ceb69e500a9ead3319f1c1
```

## Bound surface

The binding contains exactly three named actors and four semantic actions:

1. Knickerbocker Trust submits one bounded request to NBC;
2. NBC forwards it once as a pure courier, preserving the original request
   reference, content hash, mandate and represented sender;
3. NYCH records and classifies only the request actually delivered on the
   second hop; and
4. NYCH issues one scoped disposition to Knickerbocker without declaring a
   universal prohibition, delivery, resource commitment or rescue outcome.

The slice binds `POL-TIME-01`, `POL-INFO-01`, `POL-REVIEW-01`,
`POL-FACILITY-01`, `POL-LIFECYCLE-01`, and `POL-RESULT-01` only for this
lineage. The facility implementation is used to prove that the later dated
member facility is not back-projected into 21 October. `POL-AMOUNT-01`,
`POL-SERVICE-01`, and `POL-VENUE-01` remain unbound.

## Status boundary

This is a full-draft-exposed positive conformance binding. It does not change
the accepted Scenario Configuration, whose nine policy selections remain
`unbound` and whose `execution_eligible` value remains false. It starts no
simulator and authorizes no full-roster runtime, historical calibration,
evaluation, or validity claim.

The earlier two-role mapping and runner remain frozen reference assets. This
package succeeds their direct `KT -> NYCH` abstraction only for the new
three-role lineage; it does not rewrite their identities or results.

S3 proves exact upstream loading, selected policy identity, positive
participant decisions, legal actor-scoped observations, V1 ActionIntent and
MessageIntent projection, two-hop provenance, and separated disposition/result
layers. S4 owns adversarial negatives, deterministic trace/replay evidence,
implementation review, and reusable method closeout.

## S3 closeout

The focused E6 suite passed 4 tests. The combined configuration and Agent
regression passed 118 tests, Contracts V1 passed 349 tests, and the import
boundary passed 2 tests. Local release checksums, `git diff --check`, the
accepted configuration raw hash, and all S2 receipt-pinned surface hashes also
passed.

The depth audit found no scope expansion: the implementation contains no
TraceWriter, replay runner, simulator, Ray integration, calibration,
evaluation, or actor outside KT, NBC and NYCH. Its larger loader surface is
confined to external hash anchors, exact field/reference checks, and V1
projection; event breadth remains four actions. S4 may reuse this surface but
may not widen it while adding negative cases and one deterministic trace.

## Files

- `binding.json` declares the exact actors, relationships, observations,
  actions, routes, policies and excluded scope.
- `manifest.json` pins the binding, implementation files and upstream E5/E4
  identities; its internal `manifest_sha256` is the canonical self-hash, while
  the hash above is the required raw-file anchor supplied to the loader.
- `SHA256SUMS` records the local package-file hashes.
- `scenarios/panic_1907/lineage_v0_1/` contains the fail-closed loader, V1
  projector, participant policies and bounded environment policies.
- `tests/agents/test_panic_1907_lineage_binding.py` exercises the positive E6
  surface without running a simulation.
