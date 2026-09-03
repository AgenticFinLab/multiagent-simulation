# SingHealth Data Breach Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0616`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody at
`.local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/current/materialization-a`.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.9ee80f5e54b70d8b041b96b2` |
| Package SHA-256 | `96ab8667be1a283a0bb2488aadeea27335453bc07a11b98c6c0283e2d72c3e3f` |
| Rule binding SHA-256 | `0a386a726de655e4596d6f38651129a2dfd40b9141d05d0b502bfe2e747ca7fe` |
| Run manifest SHA-256 | `200752abaf0d59280d7b8a63d671dbf591b5631c36e5a107ecbef1e23f480415` |
| Trace SHA-256 | `e8b084280da5a790960b78774e63f3a5bf7cd1d57702437eb0a6cdbaf99a42d8` |
| Run seal SHA-256 | `6c1da5d590d7e76fc3cc5909fa4cbe4007ce6f0d980965db0fca9683269798ff` |
| Final state SHA-256 | `29f4b5df4d8e046723a6e8a9ea21fcb6b5812c52f66eed2870a79c420a618b8a` |
| Generated EPG seal | `fcc6ecf944ab2dfac812d3d63ddad4b9e7c6bc2e38276ac2122224c74d318e62` |

The run covers 8 action-bearing representations over
11 logical coordinates. Its sealed trace contains
438 records; the trace-derived graph contains
466 nodes and 1131 edges. Terminal
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
  --package projects/h2epr/events/singhealth_data_breach/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/current/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/current/reproduction
```

The accompanying [simulation reading](../../../reports/singhealth_data_breach/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
