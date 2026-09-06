# Baoneng–Vanke Takeover Battle Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-1031`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-06-semantic-contracts/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.f53d0be85dbb76fc46dcdde4` |
| Package SHA-256 | `06cdd22424efcb091e4b9850f38b5965ea222e652e3e7cec31ecf2282a7bb976` |
| Rule binding SHA-256 | `89de3ff815ff6649a37df3191cf28fa0a3a191d490d47772dd75512c1a4e7452` |
| Run manifest SHA-256 | `4816bcfacf04000bf3b1f5512eb387dd937d90d79c7b48b6df882fe4f09d42f2` |
| Trace SHA-256 | `3b6d399af0cf8247b2f284a375b1d69e347bf95ad3f10ce79390c0250423e475` |
| Run seal SHA-256 | `114604c982effaab1e166b1652745439eba0bb6f2d83582ae93058ad1e1fe0ae` |
| Final state SHA-256 | `b5c58efa2c78ab645c4eac75ff0481a2c122576551084ab6227cfe2735c8ec32` |
| Generated EPG seal | `06d315f500d23348b3c3a888d6f1f859ca872e7b254d1f1494ef3aadcd8ba1e2` |

The run covers 8 action-bearing representations over
20 logical coordinates. Its sealed trace contains
823 records; the trace-derived graph contains
861 nodes and 2465 edges. Terminal
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
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/baoneng_vanke_takeover_battle/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-06-semantic-contracts/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-06-semantic-contracts/reproduction
```

The accompanying [simulation reading](../../../reports/baoneng_vanke_takeover_battle/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
