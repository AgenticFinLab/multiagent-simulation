# East Palestine Train Derailment Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0196`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-05-passive-admission/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.293a2a817e42f1ea0578dc45` |
| Package SHA-256 | `2dfca76550db4a9d68db3cb7e03336e39bbddafe15f575ec9109d1096014330e` |
| Rule binding SHA-256 | `78f974583e36330d9cde19ff5f5133e7cbd42bbc1d279958f74b7baed4e711d8` |
| Run manifest SHA-256 | `fff11a9e17f5392ff66ea08f0e0812e8ac6c89980658876c20cfac53a9766a78` |
| Trace SHA-256 | `71d715fd6272d5d7d89a9b487f443125a124c0a66ba2fdf3920ca7e58906c1e8` |
| Run seal SHA-256 | `a3a0b6fb18c602982c51c2a293d0be62c0490150c290ab38260cae78cd9c4484` |
| Final state SHA-256 | `79ed8e7961b316ff111e8add369f9de2cbfedd10f47cb45682343c27bc8cb140` |
| Generated EPG seal | `3d3101e92c31c36ba3dee05583bf77d6a8642f49aed226ff600290bdaa3ee13f` |

The run covers 7 action-bearing representations over
11 logical coordinates. Its sealed trace contains
405 records; the trace-derived graph contains
432 nodes and 1210 edges. Terminal
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
  --package projects/h2epr/events/east_palestine_train_derailment/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-05-passive-admission/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-05-passive-admission/reproduction
```

The accompanying [simulation reading](../../../reports/east_palestine_train_derailment/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
