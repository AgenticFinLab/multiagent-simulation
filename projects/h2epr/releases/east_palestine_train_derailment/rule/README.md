# East Palestine Train Derailment Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0196`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-06-semantic-contracts/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.c81b945d591680e9f1fbaf03` |
| Package SHA-256 | `897f82abe5197dab4e32c6de9e477d77ff74b6709292d096c83c8eebe6534684` |
| Rule binding SHA-256 | `3071f54542ee566dff373276abac87e832d1b756a0f280fe55a55fb2a8f0cd2c` |
| Run manifest SHA-256 | `d19e1dec7b58e76427cf62ca6db7533d0584fd6982ee26f29158dc39e4297d72` |
| Trace SHA-256 | `bed17c556d05b24d37317f58838fe28d601574b890166e00d3d4af4c9e137c45` |
| Run seal SHA-256 | `a427eaae17e9505faab43fdcd53e62ff478f0330040e49346d046f3af62c98e4` |
| Final state SHA-256 | `79ed8e7961b316ff111e8add369f9de2cbfedd10f47cb45682343c27bc8cb140` |
| Generated EPG seal | `a4eae255bc5b9924c12915dc5c4fec687ca791331ffd3219da14cb3b761f9be1` |

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
  --data-root /home/lenovo/projects/AgenticFinLab/multiagent-simulation/data/h2epr \
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/east_palestine_train_derailment/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-06-semantic-contracts/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-06-semantic-contracts/reproduction
```

The accompanying [simulation reading](../../../reports/east_palestine_train_derailment/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
