# Angola Yellow Fever Outbreak of 2016 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0551`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-behavior/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.c8e90196fadcf5a18b9b9f9a` |
| Package SHA-256 | `938f441d834a8c928fb64ec12eb6e3692ef6e00c91d06016ba681f8d6f540e3d` |
| Rule binding SHA-256 | `530e0f3316aa7af6275cc5a58cf2f9e254de00de9999cdf4c6c0f28025e7890c` |
| Run manifest SHA-256 | `6072990591323910c30efdeecce60c44835b46a5d829cf39ea81a707c9a786ee` |
| Trace SHA-256 | `a08dd89d287d2e7d12061c6fec04584f954aaaa5306d037efd957a54320fff08` |
| Run seal SHA-256 | `57121ec6e9c26a3f7207d2e08098c79cf0a1725d0a5a302d3e86aae2ece4c8b6` |
| Final state SHA-256 | `6e43cbba3847a1df9b6dd5c5395932c964d8baf6f086717e7c04f375da0ea26e` |
| Generated EPG seal | `b177447f3ba8ba8af9320599ae1e924fa2c0453897056e1b95bf85fb6be0a4c4` |

The run covers 8 action-bearing representations over
20 logical coordinates. Its sealed trace contains
826 records; the trace-derived graph contains
866 nodes and 2481 edges. Terminal
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
  --package projects/h2epr/events/angola_yellow_fever_outbreak/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-behavior/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-behavior/reproduction
```

The accompanying [simulation reading](../../../reports/angola_yellow_fever_outbreak/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
