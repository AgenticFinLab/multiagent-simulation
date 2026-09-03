# East Palestine Train Derailment Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0196`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/current/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.4cc6658590d5447313ff426b` |
| Package SHA-256 | `f1f30080e857417ed06cb45b3cbb25b37ea5a7fac72339978185f37dd657e297` |
| Rule binding SHA-256 | `9588486a9e93f5a46a94b3e1f4e9a3bb1f000ab3b61332f4437a5af611a4b17d` |
| Run manifest SHA-256 | `2e9b537403377fc0d8f8f5f17e12c71239a0b1611161cc2070dcf501ea97f399` |
| Trace SHA-256 | `a90e4b657e6f46c137e5d847a1e77da378f9309614e72be0fb1e66551cd7438a` |
| Run seal SHA-256 | `33d3a6f4471e29f12c33e6f44e84fbd1dc25380d108b97c052f4c35643a3b7b2` |
| Final state SHA-256 | `1b7dbf7b8e8e85bd7ff1fa172fd544d6d57a434d572fa1f446ade7d4333d5599` |
| Generated EPG seal | `b36314507aa0b70878f8346ccec20df418cb804401fe91ffc63ca3754ec0eab2` |

The run covers 7 action-bearing representations over
11 logical coordinates. Its sealed trace contains
405 records; the trace-derived graph contains
432 nodes and 1056 edges. Terminal
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
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/current/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/current/reproduction
```

The accompanying [simulation reading](../../../reports/east_palestine_train_derailment/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
