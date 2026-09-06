# SingHealth Data Breach Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0616`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-06-semantic-contracts-final/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.26b57124e29d077af3150e02` |
| Package SHA-256 | `52dbf7578a745e66cf8066f8743ac91f129deafb849b9fc92d6802fa32b0b5a5` |
| Rule binding SHA-256 | `5b7dcacd27eee069208fa777908807db91c831c0cd8b00e1fb9330b2a07646b4` |
| Run manifest SHA-256 | `f0002f2c2161afd255134d062898cfa0672a191509334d80d13430d9abbe4b7a` |
| Trace SHA-256 | `c326760686ce7e9652546955bc7a2fddaa72ee5d1941af073796d1c7ed96234b` |
| Run seal SHA-256 | `b4834493f4d893676e58f2a221376f9f6eec72ae06f3e7ec34fbd595c7a0c438` |
| Final state SHA-256 | `5c8ecedefd2211d9f41636bdd47a144ec079ed9de97135f764e589ec5f745472` |
| Generated EPG seal | `bf365f5d1306ead1ac0fd46f6feaddfe6e55d8b49546b3512a92f10bdf308dde` |

The run covers 8 action-bearing representations over
20 logical coordinates. Its sealed trace contains
782 records; the trace-derived graph contains
820 nodes and 2318 edges. Terminal
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
  --package /home/lenovo/projects/AgenticFinLab/multiagent-simulation/.local-runtime/h2epr-simulation/working/2026-09-06-contracts/current-candidates/singhealth_data_breach/final-package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-06-semantic-contracts-final/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-06-semantic-contracts-final/reproduction
```

The accompanying [simulation reading](../../../reports/singhealth_data_breach/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
