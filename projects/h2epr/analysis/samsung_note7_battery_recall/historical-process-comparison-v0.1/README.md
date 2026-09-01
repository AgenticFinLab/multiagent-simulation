# Note7 historical-process comparison v0.1

This package is the analysis entry for the accepted H2EPR-0481 generated
process. Its first stage is complete: the canonical Generated EPG and the
sealed simulation records needed to interpret it have been read in full.

## Current document

| Document | Responsibility |
|---|---|
| [Generated-process reading](generated-process-reading.md) | Simulation-only account of the trajectory, graph structure, actor interaction, state development, and limits visible in the accepted run |

The [event entry](../../../events/samsung_note7_battery_recall/README.md) owns
the research question and event boundary. The
[run and generated-graph release](../../../execution/samsung_note7_battery_recall/run-and-graph-v0.1/)
owns the accepted run, replay, graph identity, and claim boundary.

## Reading identity

| Field | Value |
|---|---|
| Event and run | `H2EPR-0481`; `run.h2epr.0481.canonical.v0_1` |
| Canonical graph serialized SHA-256 | `3214b509cbaab993a8041f693f53d2b572a3d5820fc715e3f57b200d6f644ff3` |
| Graph preimage seal | `b957a03bb186d9fc5148f393fae84fb085a4093d7c7c5e2c1bb9001a066d8aac` |
| Determinism witness | independent-repeat graph is byte-identical |
| Reading coverage | 374 of 374 nodes and 302 of 302 edges |

## Current boundary

No Draft EPG or Reference EPG was opened for this stage, and historical
material was not used as comparison evidence. The reading is an
interpretation of one deterministic mechanism-coverage run, not an empirical
comparison. A Draft-retention study, primary-source historical comparison,
and final synthesis remain possible later stages, each requiring an explicit
scope and its own evidence account.
