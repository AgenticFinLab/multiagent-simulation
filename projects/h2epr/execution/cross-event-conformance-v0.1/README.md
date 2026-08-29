# Cross-event Rule execution conformance v0.1

This release compares the accepted Panic of 1907 and SingHealth Data Breach
full-roster runs at the boundary they are intended to share. Both events use
the same compact run contract, deterministic comparison, replay requirements,
generated-graph closure, and claim boundary. Their participants, policies,
time systems, state, and causal content remain event-specific.

## Compared event paths

| Property | Panic of 1907 | SingHealth Data Breach |
|---|---:|---:|
| Runtime actors | 16 | 13 |
| Actor-capability bindings | 17 | 13 |
| Decision commitments evaluated | 88 | 41 |
| Scenario policies exercised | 9 | 9 |
| Lifecycle families realized | 13 | 11 |
| Logical coordinates | 32 | 50 |
| Trace records | 2,002 | 1,554 |
| Generated EPG nodes | 1,392 | 752 |
| Generated EPG edges | 1,121 | 623 |

These values are not normalization targets. They follow from two different
event configurations and should differ wherever the event models differ.
Cross-event conformance requires a shared document and verification grammar,
not equal trajectories or equal graph sizes.

## Common execution contract

For each event, the release admits the exact full-roster executable parent and
then validates six compact records against the same eight-document run
surface. The comparison establishes that:

- a canonical run and a fresh same-input, same-seed run have identical bytes
  and canonical content for every run document;
- the terminal seal has no unresolved intent or recipient;
- authoritative replay reproduces the sealed final state;
- every generated-graph node and edge resolves to its trace lineage;
- the trace and graph use the same record, node, and relation vocabularies;
  and
- both releases preserve the same evidence-exposure and validity limits.

The shared H2EPR closure code receives event identity and expected coverage as
parameters. Participant rules, institutional adjudication, schedules,
reducers, and graph semantics remain in the relevant event scenario. MASim
continues to provide unchanged public event-process and phased-runner
interfaces as a read-only base framework.

## Release contents

| File | Purpose |
|---|---|
| [conformance.json](conformance.json) | machine-readable comparison and accepted event vectors |
| [manifest.json](manifest.json) | exact source releases, code identity, scope, and integrity |
| [substantive-review.md](substantive-review.md) | review of shared invariants and event-specific boundaries |
| [SHA256SUMS](SHA256SUMS) | integrity record for this release directory |

The complete traces, final states, tick seals, and generated EPGs remain in
their event-qualified ignored custody. Their identities and compact closure
evidence are retained by the two source releases; this comparison does not
duplicate those larger artifacts.

## Validation

After installing H2EPR, run from the repository root:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/execution/test_cross_event_execution_conformance.py

cd projects/h2epr/execution/cross-event-conformance-v0.1
sha256sum --check SHA256SUMS
```

## Interpretation

This is a two-event engineering result. It establishes that the H2EPR path
from accepted semantic parents through full-roster Rule execution,
authoritative replay, and trace-derived graph generation closes under one
shared verification contract in two distinct domains. It does not establish
historical reconstruction, parameter calibration, held-out performance,
policy effectiveness, general domain validity, or scientific validity.
