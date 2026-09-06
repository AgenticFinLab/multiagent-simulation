# Samsung Galaxy Note7 Battery Recall Crisis Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0481`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-06-semantic-contracts/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.9120d67d5fe0c22266400e21` |
| Package SHA-256 | `6b37fcffdb633d9696cc757d71e0fe60d62c7cd6e9ac074862f8281f346a48fe` |
| Rule binding SHA-256 | `34f80fc27a8ce458777a94234f4178fbb8cd7ab7a44adec06462d7ed010c5419` |
| Run manifest SHA-256 | `2a5ee513c4271b40510b501cb3d3e46509c1f983e8f546f79ef8c1aa97181d14` |
| Trace SHA-256 | `8696796a7002226e83c62272d8f078ddbe9d8d8b181b75809180f7611f301825` |
| Run seal SHA-256 | `797a72f31f2415c7a9b56e4098fb21c9f33141915bbb07f91737f4c3e3f5adc4` |
| Final state SHA-256 | `ed367bf27f6c59a047b0ac40b07957dbc8f7a3d5a17752b4be522eb829970c32` |
| Generated EPG seal | `daf947cb36ba655f70e76577f0b6d3801be46c63d2166733a0e28abfb818600a` |

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
  --data-root /home/lenovo/projects/AgenticFinLab/multiagent-simulation/data/h2epr \
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/samsung_galaxy_note7_battery_recall_crisis/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-06-semantic-contracts/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-06-semantic-contracts/reproduction
```

The accompanying [simulation reading](../../../reports/samsung_galaxy_note7_battery_recall_crisis/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
