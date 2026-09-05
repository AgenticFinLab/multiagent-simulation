# Angola Yellow Fever Outbreak Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0551`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-passive-admission/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.b21a925f5048915d999d5433` |
| Package SHA-256 | `938f441d834a8c928fb64ec12eb6e3692ef6e00c91d06016ba681f8d6f540e3d` |
| Rule binding SHA-256 | `530e0f3316aa7af6275cc5a58cf2f9e254de00de9999cdf4c6c0f28025e7890c` |
| Run manifest SHA-256 | `5e10251862bbd661410e14d83088e7f8a4aecf89f44ab48e16290084f9348b0d` |
| Trace SHA-256 | `5e965a9efb553601a63c198ffb39c7272875e2cf7b276804a3b07c0888f22ead` |
| Run seal SHA-256 | `3398b1370e68f60717977daf843ba64205c6d1edfcdd8fed93aebbaa2caa26ab` |
| Final state SHA-256 | `6e43cbba3847a1df9b6dd5c5395932c964d8baf6f086717e7c04f375da0ea26e` |
| Generated EPG seal | `9d7fc08164e978db67672e71f365bca58250e9d62a151df4624be5a75741eb84` |

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
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-passive-admission/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-passive-admission/reproduction
```

The accompanying [simulation reading](../../../reports/angola_yellow_fever_outbreak/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
