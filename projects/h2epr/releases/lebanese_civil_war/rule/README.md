# Lebanese Civil War Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0892`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/lebanese_civil_war/rule/2026-09-05-stage-e/accepted/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.108a8c5193199df3dc7e5fa8` |
| Package SHA-256 | `c806337186f2d7b51c5d1183b4ece5f28b2b2282b12f3521d5c2c86a9ecd475e` |
| Rule binding SHA-256 | `01eacf91b148004816000b2b538fadd09381ef521c826edc8676c9b310ccfe65` |
| Run manifest SHA-256 | `216f59cac6d183d6739476792a379265946db5eb89a1ce7553908526f45c08ff` |
| Trace SHA-256 | `a406388abcd62c843c00747cae0d48f3d41a0cfd091847c4fd053ac5881dcf10` |
| Run seal SHA-256 | `cf0872e69826d61f808ac7b8462d5b22acc3c1bda0ce62e84eaaa6ea858c9654` |
| Final state SHA-256 | `3aff7c57db691e4088eea06b88cb8179c1f21b78d108d437998c2fe68f5cde25` |
| Generated EPG seal | `99dcb78ccc7966f06ace39e9e6ffb43214264a3bd766211c608c9a0441812c93` |

The run covers 8 action-bearing representations over
21 logical coordinates. Its sealed trace contains
922 records; the trace-derived graph contains
963 nodes and 2789 edges. Terminal
transport custody contains no unresolved message.

## Independent verification

- the run manifest and current H2EPR/read-only MASim source inventories are
  recomputed rather than trusted from the producer;
- action, decision, disposition, delta, transport, seal, replay, count, and
  graph semantics are rederived from the trace;
- the Generated EPG is independently recompiled and compared byte for byte;
- two fresh seed-0 materializations are byte identical across every output and
  the run receipt; and
- a generated-identity probe changes opaque identities while preserving the
  semantic trace, exact terminal state, and graph semantics.

## Reproduce

Run from the repository root with an absent output directory.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root data/h2epr \
  --package projects/h2epr/events/lebanese_civil_war/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/lebanese_civil_war/rule/2026-09-05-stage-e/accepted/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/lebanese_civil_war/rule/2026-09-05-stage-e/accepted/reproduction
```

The accompanying [simulation reading](../../../reports/lebanese_civil_war/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
