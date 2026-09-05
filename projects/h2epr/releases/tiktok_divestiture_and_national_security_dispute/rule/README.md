# TikTok Divestiture and National Security Dispute Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0170`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-05-stage-e/accepted/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.2cb97929423c768bbd0cf72d` |
| Package SHA-256 | `667de386997afde4f415f0b6ea491138acce8bfa081150bcfb88f156f67aa7fd` |
| Rule binding SHA-256 | `705273c8305f79d568c90b20875fdcbbea18fdc3ed055ddd10e4f7e24f6d9339` |
| Run manifest SHA-256 | `811ac05dce1d4f12420f3873421520a19b68ae688df5a2272492cdc6cd0bc055` |
| Trace SHA-256 | `075a63a6862cced760b2b360d2974a89269aa4ef8da98446772fab499b6adec7` |
| Run seal SHA-256 | `96ca389b6b91857e50bcdd4cff63938c8c3c9f791d06f6c3e8c596f7777d30af` |
| Final state SHA-256 | `0749d3f388ca92fd77275afde9c0e5075f614b561efed216c430e9b50eda0269` |
| Generated EPG seal | `0da5c0b2c32ab760711e0ed2d7c7f848e26ab5e8bce8545992da2bc9431c4828` |

The run covers 10 action-bearing representations over
22 logical coordinates. Its sealed trace contains
1101 records; the trace-derived graph contains
1142 nodes and 3297 edges. Terminal
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
  --package projects/h2epr/events/tiktok_divestiture_and_national_security_dispute/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-05-stage-e/accepted/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-05-stage-e/accepted/reproduction
```

The accompanying [simulation reading](../../../reports/tiktok_divestiture_and_national_security_dispute/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
