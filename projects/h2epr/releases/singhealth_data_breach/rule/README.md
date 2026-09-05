# SingHealth Data Breach Rule run release Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0616`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-05-stage-d/canonical`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.5db9a323beb010817c521f46` |
| Package SHA-256 | `9d17581f17e994b2aba4252c8a7457c7b03ecd8f3e9003c83268bf954664a16c` |
| Rule binding SHA-256 | `f304a0fd41650859f626ebc89f7541062ba7e0f7166a141870b68ce519da2d4f` |
| Run manifest SHA-256 | `847b59da4f08b2583796511417ff9051ef10378b2452a61b0e1a5f19d8d1fef5` |
| Trace SHA-256 | `3e20d90bc3ad4a15972286ac80c3acb3e5f7c029fecf37a6c9e46a34e3ebb5f8` |
| Run seal SHA-256 | `e8393967e403da8ad215b1c81186fa6952ca324328332d0423bd25ca646d4fe0` |
| Final state SHA-256 | `e27b32d9df9e035e2e7ad89a073f82397d4491db6ee597cd9b9efc82c649b07d` |
| Generated EPG seal | `04429d76666f687d61eb9ad220675f348a07833390986b63611d448b20d5d8ae` |

The run covers 8 action-bearing representations over
20 logical coordinates. Its sealed trace contains
782 records; the trace-derived graph contains
819 nodes and 2317 edges. Terminal
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
  --package projects/h2epr/events/singhealth_data_breach/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-05-stage-d/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-05-stage-d/reproduction
```

The accompanying [simulation reading](../../../reports/singhealth_data_breach/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
