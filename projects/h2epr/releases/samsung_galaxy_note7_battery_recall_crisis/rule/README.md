# Samsung Galaxy Note7 Battery Recall Crisis Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0481`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-05-stage-d-current/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.88051af3adbca475637d35ec` |
| Package SHA-256 | `cbcb8e37e6b3cfa8c9ffe83055dced7ed948146c60bb35046070c157f3733d5c` |
| Rule binding SHA-256 | `997e4ecb84ff70a2551bc6a10d6aeb428979d9a20a7036f5e50fac89119f4ff0` |
| Run manifest SHA-256 | `720a5a2560eacde5bb90130bb64c597f66655ba57edde9452485d704118523fb` |
| Trace SHA-256 | `9c974e99b0c97ce869e477c966a9c985967f3a11857b7acdc389c08ad9d32575` |
| Run seal SHA-256 | `76080e6b5a240ae925920b5eb12ca6c0ed484d01d5ac9e764ad8c9bea4398ff2` |
| Final state SHA-256 | `ed367bf27f6c59a047b0ac40b07957dbc8f7a3d5a17752b4be522eb829970c32` |
| Generated EPG seal | `21f63fada2e1a44be5568940af012705b4a485e57046dfa55a20debf48c53629` |

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

Run from the repository root with an absent output directory.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root data/h2epr \
  --package projects/h2epr/events/samsung_galaxy_note7_battery_recall_crisis/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-05-stage-d-current/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-05-stage-d-current/reproduction
```

The accompanying [simulation reading](../../../reports/samsung_galaxy_note7_battery_recall_crisis/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
