# Baoneng–Vanke Takeover Battle Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-1031`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-05-passive-admission/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.6f6408d11b70b472f33444ae` |
| Package SHA-256 | `f1b68baa1d90045eb87a8309eb4a2ad606a00ee1d00bb2b53709abe82062b83f` |
| Rule binding SHA-256 | `085c31986dee137449ae7620b9bb60a10d81d17b848e1f7dca16a3e78c02e851` |
| Run manifest SHA-256 | `d7af484b75a2fdb513e208e57b3b3b1bc15469b2c78cc9c669abc29c13adc645` |
| Trace SHA-256 | `ba1be4f43c8f7fe88f48b1a4f87f9f2f07ff77c30ac9822fbaf93f7bad88dffa` |
| Run seal SHA-256 | `092602d090c50e1c629e60d84d17da4438c13f6d26e2fea5dbcbdafd8ee7f793` |
| Final state SHA-256 | `b5c58efa2c78ab645c4eac75ff0481a2c122576551084ab6227cfe2735c8ec32` |
| Generated EPG seal | `52fb60baa637ecaa195b88eb7d4f71a4a67687ed117a2ef14227d8d14200df16` |

The run covers 8 action-bearing representations over
20 logical coordinates. Its sealed trace contains
823 records; the trace-derived graph contains
861 nodes and 2465 edges. Terminal
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
  --package projects/h2epr/events/baoneng_vanke_takeover_battle/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-05-passive-admission/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-05-passive-admission/reproduction
```

The accompanying [simulation reading](../../../reports/baoneng_vanke_takeover_battle/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
