# Angola Yellow Fever Outbreak of 2016 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0551`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-06-semantic-contracts/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.8fca27c569b81c55eab3a256` |
| Package SHA-256 | `40dd6cf24ad8c162f861e476cc5665ab8260738a11d4d4dd2157bac46b9e22e7` |
| Rule binding SHA-256 | `1292f017d4c6b01130941e5f5e5648dfd14bf51d91f0c270b3bdd2b1ced86c3d` |
| Run manifest SHA-256 | `e306618d0370a4ce0796890ecbc2d33182e5d8b1fa329ce83895af63fd309ea3` |
| Trace SHA-256 | `78028b7fca6dd0cef5cea19b02c341486e894cafafc11f42f9f97c6a207c1560` |
| Run seal SHA-256 | `0223571c1cf4bbdebe39d653f791421a1522b4312ae23950e38c380d22e75800` |
| Final state SHA-256 | `6e43cbba3847a1df9b6dd5c5395932c964d8baf6f086717e7c04f375da0ea26e` |
| Generated EPG seal | `80c6561b450686e76d2c3bfd4208bcf627ddc87bad8206065e6e978239955146` |

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
  --data-root /home/lenovo/projects/AgenticFinLab/multiagent-simulation/data/h2epr \
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/angola_yellow_fever_outbreak/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-06-semantic-contracts/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-06-semantic-contracts/reproduction
```

The accompanying [simulation reading](../../../reports/angola_yellow_fever_outbreak/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
