# Samsung Galaxy Note7 Battery Recall Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0481`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody at
`.local-runtime/h2epr-simulation/runs/benchmark/samsung_note7_battery_recall/rule/current/materialization-a`.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.9493ae39f4127dc9e84172f3` |
| Package SHA-256 | `30e615792ef9f1b035e2d3c6f20c1b88cfd21f13ed0ff796d3c6c4f5c47b3b2e` |
| Rule binding SHA-256 | `584a18ec84c1af98e2523876c8dbaf8ea2c06c5c8981aff9c00af19c76f43739` |
| Run manifest SHA-256 | `6ffeb1ccf51cfbdf80cbc8d52e7359aea9859ce0c681b750bdc49c36cd3f4739` |
| Trace SHA-256 | `f5c3acff8535e54424bbeba2392541d92047c8766f19a41e23fef88aaaa3987f` |
| Run seal SHA-256 | `dbc088535802788b23e904a33a3abea7366a458fe261400fd5fb1fcdfa2bab7f` |
| Final state SHA-256 | `b95c4d0db0dd2bf4576db7ebdbddcc20bad34f9692f84839ae2cd2c5cdbc43ab` |
| Generated EPG seal | `52c0d0a6cb08f173de89d90cbcc1bfbda0de0880262b8f36026987beb43ced08` |

The run covers 8 action-bearing representations over
19 logical coordinates. Its sealed trace contains
729 records; the trace-derived graph contains
772 nodes and 1872 edges. Terminal
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
  --package projects/h2epr/events/samsung_note7_battery_recall/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/samsung_note7_battery_recall/rule/current/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/samsung_note7_battery_recall/rule/current/reproduction
```

The accompanying [simulation reading](../../../reports/samsung_note7_battery_recall/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
