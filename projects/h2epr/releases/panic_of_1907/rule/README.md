# Panic of 1907 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0288`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-05-stage-d/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.1b16d1949b2a609181e1d06d` |
| Package SHA-256 | `cc5229cd7f77b93305450a50a068817e7d8ac786c2f2d2cde9a132749808e030` |
| Rule binding SHA-256 | `f1feac44d4b537f5154da23809af950eb55be1869fc46d98814e8714095c123b` |
| Run manifest SHA-256 | `1dc66598d77d691612ebd227f7c80fe68be6585dbb1abbf0787b5ade3653f2c7` |
| Trace SHA-256 | `0d87bb00c4ae36ed60c987af05fe254f3819747b7661b65667f707846beb1f26` |
| Run seal SHA-256 | `4aabd930c2a33fb4eaef5f3c5d188ae044e378131c6fc3850542308b908e786e` |
| Final state SHA-256 | `76ef0853824b1f9c6205d1ecccad42eec1a43759b7c607800d5fdd1e9a1a7515` |
| Generated EPG seal | `b82fdc940f91db4d578689a3b74cdcb0895b2c9a0833ba2f5488147a7b73c526` |

The run covers 11 action-bearing representations over
20 logical coordinates. Its sealed trace contains
1043 records; the trace-derived graph contains
1084 nodes and 3111 edges. Terminal
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
  --package projects/h2epr/events/panic_of_1907/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-05-stage-d/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-05-stage-d/reproduction
```

The accompanying [simulation reading](../../../reports/panic_of_1907/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
