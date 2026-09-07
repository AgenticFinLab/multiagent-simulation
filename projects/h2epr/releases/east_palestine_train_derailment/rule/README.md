# East Palestine Train Derailment Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0196`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-07-four-task-maintenance/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.1e712ffee7592ef9081ae7b0` |
| Package SHA-256 | `e30a8f3ee5455fb0e18b1c29d3bc76e2baee22c2159e0b568e191cbf37031b10` |
| Rule binding SHA-256 | `a28899ecf5b16eb25e291aa1950fb02c3050453322b906947d7c8aac496fb1f7` |
| Run manifest SHA-256 | `831a57e7157cb944dab1bc91a2d7900abe1d210b5f1dd5bea52c8f2367935571` |
| Trace SHA-256 | `74e5fabd0297dba4afda38235d5381cda655022e1fa2119cd490d4ebe3fdd43e` |
| Run seal SHA-256 | `088afa67e8b6d33eb5d257a539b844858f0ff6d9e2dedc8d3ba35f8280c1e8b1` |
| Final state SHA-256 | `79ed8e7961b316ff111e8add369f9de2cbfedd10f47cb45682343c27bc8cb140` |
| Generated EPG seal | `9529df7d884462a222b577f3b39d8d0fdc11c471b448dd306ccd65f61e0317cc` |

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

Run from the repository root with an absent output directory. The command uses
the formal tracked package, verified against the package identity above; no
ignored candidate package is required. Set `H2EPR_DATA_ROOT` to the admitted
dataset root if it is not `data/h2epr`. That root must contain the exact
`development_samples_v1/events/H2EPR-0196/` files pinned by the
package Source Profile: `event_spec.json`, `frozen_evidence.json`, and
`draft_epg.json`. No other dataset file is needed.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root "${H2EPR_DATA_ROOT:-data/h2epr}" \
  --package projects/h2epr/events/east_palestine_train_derailment/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-07-four-task-maintenance/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-07-four-task-maintenance/reproduction
```

The accompanying [simulation reading](../../../reports/east_palestine_train_derailment/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
