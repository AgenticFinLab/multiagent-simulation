# Angola Yellow Fever Outbreak of 2016 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0551`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/current/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.2c5f37a8e456f99bdb1eff02` |
| Package SHA-256 | `d6456af798b2593d264b18f7b1a4f0bf360682cfe36a26965ed3d29dbfe5c2b6` |
| Rule binding SHA-256 | `be5013c6677d8aae4de67f0ce37064966c590c4380cf16fb523d687b1f50a269` |
| Run manifest SHA-256 | `32527f4ebacc54e2762a392d28daf5d0c0b9b7297c44ae9f79e738b392c37dcb` |
| Trace SHA-256 | `edec83529744119588cc50c14acb83c270f93699335121ecc791a858b404b1e0` |
| Run seal SHA-256 | `2bdddf577ba041e109dbd804b6655bd250e7750fc72d5ca0a84ac6d2e75977ae` |
| Final state SHA-256 | `0a0b2245ca514c0ad69a212a0f0338cc836ad08065a301e1d024bd75aae700a4` |
| Generated EPG seal | `e76b4c4960a607af51ab274bb0634834562cc54ef8da4af1d05fb89ff7cd346f` |

The run covers 8 action-bearing representations over
20 logical coordinates. Its sealed trace contains
826 records; the trace-derived graph contains
866 nodes and 2147 edges. Terminal
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
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/current/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/current/reproduction
```

The accompanying [simulation reading](../../../reports/angola_yellow_fever_outbreak/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
