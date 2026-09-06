# Panic of 1907 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0288`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-06-semantic-contracts/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.ae8aa2842bfd4d33c481fc78` |
| Package SHA-256 | `f657f2857d9e4d56cc18b882990f98f0fe12dccbd609252dd3d6858bf87c648f` |
| Rule binding SHA-256 | `4f46b295b13ad1d4c1e779ded1f9c0be4055e12ab84afbf46442d80f0fa60339` |
| Run manifest SHA-256 | `5bd389e910586acc715a4a8cb13194a85ed2f03dc5f3414b399616d650db726b` |
| Trace SHA-256 | `c55af03ad713bd9426f7fa15e7c2f5bb4b2f3e677114fe3336d46cf066a7688b` |
| Run seal SHA-256 | `514b7bb4a2ced7374967d84a8aee43663bb7270735dfc0c629c2a8b0f0e18331` |
| Final state SHA-256 | `76ef0853824b1f9c6205d1ecccad42eec1a43759b7c607800d5fdd1e9a1a7515` |
| Generated EPG seal | `f34dc9527ead73cf341c65ff4b0d91e114ae5c2c168e18babe8ffda7be391700` |

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
  --data-root /home/lenovo/projects/AgenticFinLab/multiagent-simulation/data/h2epr \
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/panic_of_1907/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-06-semantic-contracts/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-06-semantic-contracts/reproduction
```

The accompanying [simulation reading](../../../reports/panic_of_1907/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
