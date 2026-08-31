# Samsung--regional--outlet--consumer lineage conformance v0.1

Status: `PASS_BOUNDED_LINEAGE_CONFORMANCE`

This package closes the accepted H2EPR-0481 binding across four actors, seven
actions, four directed participant carriers, one product-posture result, one
Scenario-owned remedy-offer delivery, and fifteen synthetic ticks. It starts
no simulator and does not make the non-executable Scenario Configuration
executable.

## Evidence

- `src/h2epr/scenarios/samsung_note7_battery_recall/lineage_conformance_v0_1.py`
  reconstructs the fixed branch, verifies exact cross-hop identity, records a
  hash-chained trace with tick and run seals, and replays authoritative deltas.
- `tests/agents/test_samsung_note7_lineage_binding.py` owns the carrier,
  authority, route, idempotency, result-separation, and 2017-firewall checks.
- `tests/agents/test_samsung_note7_lineage_conformance.py` owns deterministic
  reconstruction, Contracts V1 payloads, cross-hop substitutions, trace order,
  tamper detection, replay prestate, and receipt identity.
- `receipt.json` records the expected vector without storing a duplicate full
  trace.
- `implementation-review.md` records findings, scope, transfer evidence, and
  the stopping decision.
- `SHA256SUMS` covers files owned by this closeout package.

The trace uses the domain-neutral MASim event-process envelope. Observation,
ActionIntent, MessageIntent, ActionDisposition, CommunicationDisposition, and
StateDelta payloads use Contracts V1. Compact trace wrappers and event-owned
posture and offer records are not represented as complete V1 TraceRecord
objects.

The final outlet response reaches the consumer, but its proposed path is not a
fulfillment result. The run seal therefore retains the consumer request and
the outlet recipient as unresolved.

## Validation

After installing the project dependencies, run from the repository root:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_samsung_note7_lineage_binding.py \
  projects/h2epr/tests/agents/test_samsung_note7_lineage_conformance.py

cd projects/h2epr/scenarios/samsung_note7_battery_recall/lineage-conformance-v0.1
sha256sum --check SHA256SUMS
```

## Boundary and successor

This package is full-draft-exposed synthetic engineering conformance. It is not
a full-roster Rule runtime, simulation, calibration, historical fit, held-out
construction, post-seal evaluation, policy-effectiveness result, or historical
or scientific validity result. It does not read the target Reference EPG.

The next legal action is the separately authorized full-roster Policy
Realization and Rule successor, with all unrepresented mechanisms kept
explicitly bounded.
