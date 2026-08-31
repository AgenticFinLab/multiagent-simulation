# Samsung Galaxy Note7 battery recall run and generated graph v0.1

- Event: `H2EPR-0481`
- Run: `run.h2epr.0481.canonical.v0_1`
- Status: `accepted_run_and_graph_closure`
- Interpretation: deterministic, uncalibrated mechanism coverage

This release records the complete run of the accepted Note7 full-roster Rule
package. It binds a canonical materialization and a fresh same-input,
same-seed repeat to the exact executable package. All eight run documents are
byte-identical, authoritative replay closes, and the generated event graph
resolves only to the sealed simulation trace.

## Release contents

| Record | Responsibility |
|---|---|
| `run-manifest.json` | exact package, bundle, seed, actors, clock, and components |
| `run-seal.json` | ordered tick seals, final-state identity, and transport closure |
| `replay-receipt.json` | trace validation and authoritative final-state replay |
| `execution-receipt.json` | completion, output identities, and semantic coverage |
| `determinism-comparison.json` | byte and canonical comparison of all eight run documents |
| `generated-epg-receipt.json` | graph inventory, source identities, and reference closure |
| `manifest.json` | executable parent, integrity, code identity, custody, and claim boundary |

The full traces, final states, tick arrays, and generated EPGs remain in the
event-qualified ignored custody directory. The manifest records their exact
serialized and canonical hashes and byte counts. The compact tracked records
are sufficient to identify, admit, and audit the release without duplicating
the largest outputs.

## Deterministic execution

Both materializations use the same admitted bundle and seed `481`. Operational
paths are excluded from run identity. Each execution operates all eight
actors, evaluates all 22 commitments, emits 22 actions, exercises all nine
selected Scenario policies, and realizes all twelve lifecycle families.

The run spans 50 UTC logical coordinates: ten same-time precedence barriers at
each of five event anchors. The coordinates preserve causal order without
asserting unobserved intraday timestamps. The trace contains 926 hash-chained
records, including 22 action intents, 117 policy applications, 37 message
intents, 74 message dispositions, and 52 authoritative state deltas. All 22
open lifecycle objects remain typed carry-forward records at the analytic
horizon.

## Replay and graph closure

Replay begins from the admitted initial state, validates every delta prestate,
and reproduces the sealed final-state hash. No message intent or recipient is
unresolved at completion.

The generated EPG contains 374 nodes and 302 directed edges. Every node names
its source trace record and record hash. Every edge resolves both graph
endpoints and all source trace references. The graph seal covers the complete
graph preimage.

## Reproduction

With the repository's declared dependencies installed, run the Note7 execution
tests and checksum validation from the repository root:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/execution/test_samsung_note7_run_release.py

cd projects/h2epr/execution/samsung_note7_battery_recall/run-and-graph-v0.1
sha256sum --check SHA256SUMS
```

## Scope

The run follows evidence-exposed qualitative mechanism-coverage values inside
the accepted domains. It establishes the engineering result that the released
participants, policies, routes, reducer, replay, and trace-derived graph work
together deterministically. It does not establish historical calibration,
historical reconstruction, held-out performance, recall effectiveness,
causal identification, scientific validity, or universal generality.
