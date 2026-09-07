# TikTok Divestiture and National Security Dispute Rule run release

This compact release records the dataset-conditioned Rule materialization of
`H2EPR-0170`. Raw trace, state, seals, replay output, and Generated
EPG bytes remain in ignored local custody. The receipt records this logical
custody locator:
`.local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-07-four-task-maintenance/materialization-a`.
Canonical A/B physical directories may differ while sharing that identity.

## Release identity

| Item | Identity |
|---|---|
| Run | `run.62bbe5fca5c9ff9df58411c1` |
| Package SHA-256 | `f2f4e3262bf1612a01a89e30548aead483d620ee34cebb3a98010312fd908391` |
| Rule binding SHA-256 | `3c9c973203242cff6bacd7fe9e76560c1e4ed0297c88e3211a62f644f0e997d9` |
| Run manifest SHA-256 | `85e01307c02dcf6f180bc041c651be462a0cb067d34e7cf158be90e817128d00` |
| Trace SHA-256 | `1fd04a881ceea2e1fa45b680ef322ec0f907b3aa05ec6beace708b5be9d0c66f` |
| Run seal SHA-256 | `7910558254cca590707109a0756454e5ba170a16717287a4b4928362b1be34d9` |
| Final state SHA-256 | `0749d3f388ca92fd77275afde9c0e5075f614b561efed216c430e9b50eda0269` |
| Generated EPG seal | `2d4572b4d075e11276779c5f03ce4b336e41a8788e6e665756472ee35ae231d9` |

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

Run from the repository root with an absent output directory. The command uses
the formal tracked package, verified against the package identity above; no
ignored candidate package is required. Set `H2EPR_DATA_ROOT` to the admitted
dataset root if it is not `data/h2epr`. That root must contain the exact
`development_samples_v1/events/H2EPR-0170/` files pinned by the
package Source Profile: `event_spec.json`, `frozen_evidence.json`, and
`draft_epg.json`. No other dataset file is needed.

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root "${H2EPR_DATA_ROOT:-data/h2epr}" \
  --package projects/h2epr/events/tiktok_divestiture_and_national_security_dispute/package \
  --backend rule --seed 0 --identity-variant canonical \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-07-four-task-maintenance/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-07-four-task-maintenance/reproduction
```

The accompanying [simulation reading](../../../reports/tiktok_divestiture_and_national_security_dispute/rule/simulation-reading.md) describes the
generated process. This release establishes engineering and method closure
only, not held-out performance, historical fit, calibration, causality,
scientific validity, or universal generality.
