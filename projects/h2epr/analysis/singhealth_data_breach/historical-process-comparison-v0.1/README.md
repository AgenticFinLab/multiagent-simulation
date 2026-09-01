# SingHealth historical-process comparison v0.1

This package is the analysis entry for the accepted H2EPR-0616 generated
process. Its first stage is complete: the canonical Generated EPG and the
sealed simulation records needed to interpret it have been read in full.

## Current document

| Document | Responsibility |
|---|---|
| [Generated-process reading](generated-process-reading.md) | Simulation-only account of the trajectory, graph structure, actor interaction, state development, and limits visible in the accepted run |

The [event entry](../../../events/singhealth_data_breach/README.md) owns the
research question and event boundary. The
[run and generated-graph release](../../../execution/singhealth_data_breach/run-and-graph-v0.1/)
owns the accepted run, replay, graph identity, and claim boundary.

## Reading identity

| Field | Value |
|---|---|
| Event and run | `H2EPR-0616`; `run.h2epr.0616.canonical.v0_1` |
| Canonical graph serialized SHA-256 | `515094262784d8c57cbf14f454dda443343b3d39c6bf1bbf90eb08c2b9bb870e` |
| Graph preimage seal | `327f129b2ac73f92e3da9b54211695f30477ceacfdc9f5e9ee72f462316fa599` |
| Determinism witness | independent-repeat graph is byte-identical |
| Reading coverage | 752 of 752 nodes and 623 of 623 edges |

## Current boundary

No Draft EPG or Reference EPG was opened for this stage, and historical
material was not used as comparison evidence. The reading is an
interpretation of one deterministic mechanism-coverage run, not an empirical
comparison. A Draft-retention study, primary-source historical comparison,
and final synthesis remain possible later stages, each requiring an explicit
scope and its own evidence account.
