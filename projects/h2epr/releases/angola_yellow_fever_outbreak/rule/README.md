# Angola Yellow Fever Outbreak of 2016 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0551`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-07-four-task-maintenance/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.0eb5b7a94ef55fc1bdddf756` |
| Package SHA-256 | `6912a3ad8c7c37cffd31d545a9ace24f07ae94d76eab73e61b4d66996b3af9a3` |
| Rule binding SHA-256 | `e44a24d780f138b524004c363becd767d3b0cdcd5fa7deccaa7179a073ded36d` |
| Run manifest SHA-256 | `bf28737791516b59583699f36c3cc4ca1e0484cd1f39c3114ab63e45755a578d` |
| Trace SHA-256 | `0a59a40b4dc1b65d1fc51f2c303b130314b5d96be1e785c3e401d90245a934fb` |
| Run seal SHA-256 | `9d78393f5d135d454ad2e8343235a5429451300da31afef93f0973d983c46500` |
| Final state SHA-256 | `6e43cbba3847a1df9b6dd5c5395932c964d8baf6f086717e7c04f375da0ea26e` |
| Generated EPG seal | `766ac4821ca634eff173f9fd6ca771d8cbed005de0f1c299cb7bb1d68c3fada4` |

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

Run from the repository root with an absent output directory. The command uses
the formal tracked package, verified against the package identity above; no
ignored candidate package is required. Set `H2EPR_DATA_ROOT` to the admitted
dataset root if it is not `data/h2epr`. That root must contain the exact
`development_samples_v1/events/H2EPR-0551/` files pinned by the
package Source Profile: `event_spec.json`, `frozen_evidence.json`, and
`draft_epg.json`. No other dataset file is needed.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root "${H2EPR_DATA_ROOT:-data/h2epr}" \
  --package projects/h2epr/events/angola_yellow_fever_outbreak/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-07-four-task-maintenance/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-07-four-task-maintenance/reproduction
```

The accompanying [simulation reading](../../../reports/angola_yellow_fever_outbreak/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
