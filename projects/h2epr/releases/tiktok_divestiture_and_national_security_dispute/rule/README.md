# TikTok Divestiture and National Security Dispute Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0170`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-06-semantic-contracts/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.2a983fc27557518b15624c54` |
| Package SHA-256 | `13ea21a15889014555de7f3c8c6603325a3fb42525fd538492f2e996fc768a05` |
| Rule binding SHA-256 | `7590f24b391353120b53ddf981c6c97c5f6003faa49b651879e6ddc89cfa3023` |
| Run manifest SHA-256 | `3c37d1a7c6992eacfedec7ce514737ab647bb04e235cb6c9254ad371e3c001f5` |
| Trace SHA-256 | `c0675d758934200aa78ebaa0e7ac4c2b7d56ffae56ed0dd9196112d2ab9688a8` |
| Run seal SHA-256 | `2781db8c44b4c8a461e2d30159af1597a1980e6c1cd6316120dab446a08b2461` |
| Final state SHA-256 | `0749d3f388ca92fd77275afde9c0e5075f614b561efed216c430e9b50eda0269` |
| Generated EPG seal | `c671f1e35f06899cfa83c42222a4ba8dd3e2ab7594221d5bcff3ab014d4b1dbb` |

The run covers 10 action-bearing representations over
22 logical coordinates. Its sealed trace contains
1101 records; the trace-derived graph contains
1142 nodes and 3297 edges. Terminal
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
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/tiktok_divestiture_and_national_security_dispute/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-06-semantic-contracts/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-06-semantic-contracts/reproduction
```

The accompanying [simulation reading](../../../reports/tiktok_divestiture_and_national_security_dispute/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
