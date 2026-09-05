# East Palestine Train Derailment Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0196`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-05-behavior/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.af195d6305dad7006bc55759` |
| Package SHA-256 | `2dfca76550db4a9d68db3cb7e03336e39bbddafe15f575ec9109d1096014330e` |
| Rule binding SHA-256 | `78f974583e36330d9cde19ff5f5133e7cbd42bbc1d279958f74b7baed4e711d8` |
| Run manifest SHA-256 | `dc2101f342b8d38e9ab494699357e3510df651f4e1f2749e32af1c4805673685` |
| Trace SHA-256 | `40bd5f55e6008cd419f21bb6125f9ef0682e7d841c087b997a7cfd5aa7199a56` |
| Run seal SHA-256 | `45209e477e465be10a9932c5b507fc946059d82b6dc362123fd2a9cd0c7110ae` |
| Final state SHA-256 | `79ed8e7961b316ff111e8add369f9de2cbfedd10f47cb45682343c27bc8cb140` |
| Generated EPG seal | `d7d2cd47e81955c6ebe4d9211c2276ac0361954b94e151d6dd13a68b4bb5ed27` |

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
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-05-behavior/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-05-behavior/reproduction
```

The accompanying [simulation reading](../../../reports/east_palestine_train_derailment/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
