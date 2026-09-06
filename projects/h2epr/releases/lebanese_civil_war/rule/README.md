# Lebanese Civil War Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0892`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/lebanese_civil_war/rule/2026-09-06-semantic-contracts/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.391644c9adfa091e6d2109e9` |
| Package SHA-256 | `3c47bb0d6f91b5c5d716c2fb509c44d6cb543b5ef83c8e38333dd3e4533bfac4` |
| Rule binding SHA-256 | `e85d9ea15786c3d954fb4be081c63663b7d0e453ced104154fc4ef82d2fef45a` |
| Run manifest SHA-256 | `3980f0b5d0e063b24d0e631ed66d4be4613fc76123c038a8dd71e02cb2caffaa` |
| Trace SHA-256 | `29fb302aa459662f3aaeb40696c7af45df2eb224b5d7d20ea9152910feeb565b` |
| Run seal SHA-256 | `537ff58de661c7abf5926fd15a4046a0619893a15e3cab8af3b714b04805f250` |
| Final state SHA-256 | `3aff7c57db691e4088eea06b88cb8179c1f21b78d108d437998c2fe68f5cde25` |
| Generated EPG seal | `ed5c47ee5094f03c87a8f8d8898fcaf6a449e676294917decbd055626adccf19` |

The run covers 8 action-bearing representations over
21 logical coordinates. Its sealed trace contains
922 records; the trace-derived graph contains
963 nodes and 2789 edges. Terminal
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
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/lebanese_civil_war/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/lebanese_civil_war/rule/2026-09-06-semantic-contracts/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/lebanese_civil_war/rule/2026-09-06-semantic-contracts/reproduction
```

The accompanying [simulation reading](../../../reports/lebanese_civil_war/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
