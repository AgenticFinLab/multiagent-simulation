# Samsung Galaxy Note7 Battery Recall Crisis Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0481`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-07-four-task-maintenance/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.9eedae94989891d2df7519e8` |
| Package SHA-256 | `9a34a37f7267f47c8b07b6b37c596968d6ecf8b38a83630c00fa940dcbb6479c` |
| Rule binding SHA-256 | `6b39e17dafd0aaa9d768dd18d1995f6abfd78cb204758dca06ae072e03a0a95d` |
| Run manifest SHA-256 | `788d4936cde79aebfb987eb0f64b8124c7f787dc6247d3888cb54c45851a76c5` |
| Trace SHA-256 | `4cac466657a808a14f536b459fa6865335095e4c2dc1529d85a27f71909e2a47` |
| Run seal SHA-256 | `d83c9964fb612c6ec5a5ee0cec2192319d5e5ae7a41da52297f1d33289122fa4` |
| Final state SHA-256 | `ed367bf27f6c59a047b0ac40b07957dbc8f7a3d5a17752b4be522eb829970c32` |
| Generated EPG seal | `7f120cae71e02739c4876ff4b5f77d95e5b906aa6bc511af410713e36202ed61` |

The run covers 8 action-bearing representations over
29 logical coordinates. Its sealed trace contains
1101 records; the trace-derived graph contains
1152 nodes and 3262 edges. Terminal
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

Run from the repository root with an absent output directory. The command uses
the formal tracked package, verified against the package identity above; no
ignored candidate package is required. Set `H2EPR_DATA_ROOT` to the admitted
dataset root if it is not `data/h2epr`. That root must contain the exact
`development_samples_v1/events/H2EPR-0481/` files pinned by the
package Source Profile: `event_spec.json`, `frozen_evidence.json`, and
`draft_epg.json`. No other dataset file is needed.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root "${H2EPR_DATA_ROOT:-data/h2epr}" \
  --package projects/h2epr/events/samsung_galaxy_note7_battery_recall_crisis/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-07-four-task-maintenance/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-07-four-task-maintenance/reproduction
```

The accompanying [simulation reading](../../../reports/samsung_galaxy_note7_battery_recall_crisis/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
