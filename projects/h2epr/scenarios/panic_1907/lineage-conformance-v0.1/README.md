# KT--NBC--NYCH lineage conformance v0.1

Status: `PASS_BOUNDED_LINEAGE_CONFORMANCE`

This package reviews the accepted KT--NBC--NYCH binding across three actors,
four actions, three routes, and one fixed five-tick synthetic path. It uses
only the six policies already present in the binding, starts no simulator, and
does not change the non-executable Scenario Configuration.

## Evidence

- `src/h2epr/scenarios/panic_1907/lineage_conformance_v0_1.py` builds the
  positive projection, checks cross-hop provenance and delivery gates, emits a
  hash-chained trace with tick and run seals, and replays the authoritative
  deltas.
- `tests/agents/test_panic_1907_lineage_conformance.py` covers carrier,
  provenance, delivery, dated-facility, result-layer, determinism, tamper, and
  replay-prestate cases.
- `receipt.json` records the reproducible expected vector instead of storing a
  duplicate trace.
- `implementation-review.md` records the findings, scope review, method
  implications, and next-event decision.
- `SHA256SUMS` covers files owned by this release package.

The trace uses the domain-neutral `TraceWriter` envelope. Observation,
ActionIntent, MessageIntent, ActionDisposition, CommunicationDisposition, and
StateDelta payloads are validated against Contracts V1. The compact trace
envelope used by this case is not presented as a complete V1 `TraceRecord`.

## Validation

After installing H2EPR, run from the repository root:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_panic_1907_lineage_conformance.py

cd projects/h2epr/scenarios/panic_1907/lineage-conformance-v0.1
sha256sum --check SHA256SUMS
```

## Boundary and next action

This is full-draft-exposed engineering conformance evidence. It is not a full
16-actor runtime, full-event simulation, calibration, historical fit,
held-out construction, post-seal evaluation, or historical/scientific validity
evidence.

The normal next action is to apply the standardized method to another event.
Deeper work on H2EPR-0288 requires a new research question and authorization.
