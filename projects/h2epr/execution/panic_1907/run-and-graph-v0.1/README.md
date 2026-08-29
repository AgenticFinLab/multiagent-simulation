# Panic of 1907 run and generated graph v0.1

- Event: `H2EPR-0288`
- Run: `run.h2epr.0288.canonical.v0_1`
- Status: `accepted_run_and_graph_closure`
- Interpretation: deterministic, uncalibrated mechanism coverage

This release records the first complete run of the accepted Panic of 1907
full-roster Rule package. It binds one canonical materialization and one fresh,
same-input, same-seed materialization to the exact executable package. Their
run documents are byte-identical, authoritative replay closes, and the
generated event graph resolves only to the sealed simulation trace.

## Release contents

The tracked surface keeps the records needed to identify and assess the run
without duplicating its largest outputs:

| Record | Responsibility |
|---|---|
| `run-manifest.json` | exact package, bundle, seed, participants, clock, and runtime components |
| `run-seal.json` | ordered tick seals, final-state identity, and terminal transport closure |
| `replay-receipt.json` | trace validation and authoritative final-state replay |
| `execution-receipt.json` | completion, output identities, and semantic coverage |
| `determinism-comparison.json` | byte and canonical-hash comparison for all eight run documents |
| `generated-epg-receipt.json` | graph size, type inventory, source identities, and reference closure |
| `manifest.json` | executable parent, file integrity, large-artifact inventory, code identity, and claim boundary |

The full trace, final state, tick-seal array, and generated EPG remain in the
event-qualified ignored custody directory. The manifest records their exact
serialized and canonical hashes and byte counts. The run manifest, run seal,
replay receipt, and execution receipt are also retained there so that the two
complete materializations can be compared document for document.

## Deterministic execution

Both materializations use the same accepted runtime bundle and seed `1907`.
Operational directory names are not part of run identity. Each execution
launches all sixteen configured actors, retains seventeen capability
projections, evaluates all eighty-eight commitments, exercises all nine
selected Scenario policies, and realizes all thirteen lifecycle families.

The run spans thirty-two logical ticks. These are two partial-order slots for
each civil date from 18 October through 2 November 1907; they do not claim
unobserved intraday timestamps. The trace contains 2,002 hash-chained records,
including eighty-seven participant action intents, 443 action-level Scenario
policy applications, 150 message intents, 300 message dispositions, and 141
authoritative state deltas.

## Replay and graph closure

The replay receipt validates the trace and reproduces the sealed final state
from the admitted initial state and authoritative deltas. No message intent or
recipient remains unresolved at completion.

The generated EPG contains 1,392 nodes and 1,121 directed edges. Every node
names its source trace record and source record hash. Every edge resolves both
graph endpoints and all declared source trace references. The graph seal binds
the complete graph preimage, while this release keeps the graph itself in
ignored custody and tracks its two independent content identities.

## Validation

After installing H2EPR, run from the repository root:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/execution/test_panic_1907_run_release.py

cd projects/h2epr/execution/panic_1907/run-and-graph-v0.1
sha256sum --check SHA256SUMS
```

## Scope

The run is exposed to the full event record and follows declared synthetic
mechanism-coverage values inside the accepted semantic domains. It establishes
an engineering result: the released participants, policies, transport,
authoritative state, replay, and trace-derived graph operate together
deterministically. It does not establish historical calibration, a historical
reconstruction, held-out performance, policy effectiveness, or scientific
validity.
