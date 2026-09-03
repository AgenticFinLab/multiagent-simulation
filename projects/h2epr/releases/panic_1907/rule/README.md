# Panic of 1907 Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0288`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody at
`.local-runtime/h2epr-simulation/runs/benchmark/panic_1907/rule/current/materialization-a`.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.e37134e71ff5370299ec8f78` |
| Package SHA-256 | `185797e8e4987b3f485a246569039514a415114ac5d05dc4005b696ea8f115ee` |
| Rule binding SHA-256 | `5c02b8087844740e2c86cbeb172a16231f519a7010002a0b608871cfcb50fb22` |
| Run manifest SHA-256 | `ed118fc3684d0f90854e52691ee40ff11a517ab5f48165c3cf6b294f2398a3ff` |
| Trace SHA-256 | `f3d9eb95d35daef823e1914f3e623905753b46547cf2fb32de82a8b08264be48` |
| Run seal SHA-256 | `7276f199dbfcee0af9fb21f57c1c439f056c536d686e1c1d07420d0cb46c8c19` |
| Final state SHA-256 | `2db6c38a541b4356c045c1f33abf821f1d3023ed484b46aecae124d71bb49dc5` |
| Generated EPG seal | `850c1d87a1bbe32c2faaf35e2a1df1de7e328e0846d4877b1f8b789154e94f6a` |

The run covers 12 action-bearing representations over
15 logical coordinates. Its sealed trace contains
813 records; the trace-derived graph contains
851 nodes and 2074 edges. Terminal
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
  --package projects/h2epr/events/panic_1907/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/panic_1907/rule/current/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/panic_1907/rule/current/reproduction
```

The accompanying [simulation reading](../../../reports/panic_1907/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
