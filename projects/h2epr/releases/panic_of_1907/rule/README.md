# Panic of 1907 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0288`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-07-four-task-maintenance/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.7abdebdad001e59c7d01db71` |
| Package SHA-256 | `ddde21973e04ea8d9757c54db7ac1fe96069f55af23dafa8536aad1400f03b98` |
| Rule binding SHA-256 | `fc3f185fe0148ce67f2e2498c278fb4a1d5715fbdf906a496fd0c3173efd1b58` |
| Run manifest SHA-256 | `a57205a71afcddf7d8807d6dd9dcd6fef2df29171a4f22ed88b6a6788d33822a` |
| Trace SHA-256 | `b21294d8338b8e8a7da60739477fab23a58ceff8187a7cfc41bc3f615f989c6a` |
| Run seal SHA-256 | `4b1995512a7cba13b09e758fb19932dd482d2f93aaa33432adca0b2b92b4656f` |
| Final state SHA-256 | `76ef0853824b1f9c6205d1ecccad42eec1a43759b7c607800d5fdd1e9a1a7515` |
| Generated EPG seal | `f09c45f8b766f2cf19b51d79b37eba93ee01950f4c40950ccd028b2bf14107f3` |

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

Run from the repository root with an absent output directory. The command uses
the formal tracked package, verified against the package identity above; no
ignored candidate package is required. Set `H2EPR_DATA_ROOT` to the admitted
dataset root if it is not `data/h2epr`. That root must contain the exact
`development_samples_v1/events/H2EPR-0288/` files pinned by the
package Source Profile: `event_spec.json`, `frozen_evidence.json`, and
`draft_epg.json`. No other dataset file is needed.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root "${H2EPR_DATA_ROOT:-data/h2epr}" \
  --package projects/h2epr/events/panic_of_1907/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-07-four-task-maintenance/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-07-four-task-maintenance/reproduction
```

The accompanying [simulation reading](../../../reports/panic_of_1907/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
