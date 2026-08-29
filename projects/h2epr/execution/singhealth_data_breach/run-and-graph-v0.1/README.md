# SingHealth Data Breach run and generated graph v0.1

- Event: `H2EPR-0616`
- Run: `run.h2epr.0616.canonical.v0_1`
- Status: `accepted_run_and_graph_closure`
- Interpretation: deterministic, uncalibrated mechanism coverage

This release records the complete run of the accepted SingHealth Data Breach
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

Both materializations use the same accepted runtime bundle and seed `616`.
Operational directory names are not part of run identity. Each execution
launches all thirteen configured actors, retains thirteen separate capability
projections, evaluates all 41 commitments, exercises all nine selected
Scenario policies, and realizes all eleven lifecycle families.

The run spans fifty logical coordinates: ten declared partial-order barriers
at each of five event anchors from 23 August 2017 through 23 July 2018. These
coordinates preserve accepted causal order without asserting unobserved
intraday timestamps. The trace contains 1,554 hash-chained records, including
41 action intents, 222 action-level Scenario-policy applications, 73 message
intents, 146 message dispositions, and 141 authoritative state deltas.

MOH, CSA, and the notification process remain bounded institutional, route, or
process endpoints rather than autonomous runtime actors. Their admitted
messages reach terminal delivery without receiving an Agent observation or
private decision state. Forty-one open lifecycle objects are retained as typed
carry-forward records at the analytic horizon.

## Replay and graph closure

The replay receipt validates the trace and reproduces the sealed final state
from the admitted initial state and authoritative deltas. No message intent or
recipient remains unresolved at completion.

The generated EPG contains 752 nodes and 623 directed edges. Every node names
its source trace record and source record hash. Every edge resolves both graph
endpoints and all declared source trace references. The graph seal binds the
complete graph preimage, while this release keeps the graph itself in ignored
custody and tracks its two independent content identities.

## Shared execution closure

SingHealth uses the same event-neutral H2EPR document model, full-artifact
validation, deterministic comparison, compact closure checks, and
non-destructive custody functions previously verified against the accepted
Panic release. Event identity, expected coverage, participant behavior,
institutional adjudication, time, reduction, and graph semantics remain in the
SingHealth scenario implementation. MASim remains an unchanged base framework.

## Validation

After installing H2EPR, run from the repository root:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/execution/test_singhealth_run_release.py

cd projects/h2epr/execution/singhealth_data_breach/run-and-graph-v0.1
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
