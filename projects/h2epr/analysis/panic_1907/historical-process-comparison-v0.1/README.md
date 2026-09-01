# Panic of 1907 historical-process comparison v0.1

This package is the analysis entry for the accepted H2EPR-0288 generated
process. Its first stage is complete: the canonical Generated EPG and the
sealed simulation records needed to interpret it have been read in full.

## Current document

| Document | Responsibility |
|---|---|
| [Generated-process reading](generated-process-reading.md) | Simulation-only account of the trajectory, graph structure, actor interaction, state development, and limits visible in the accepted run |

The [event entry](../../../events/panic_1907/README.md) owns the research
question and event boundary. The
[run and generated-graph release](../../../execution/panic_1907/run-and-graph-v0.1/)
owns the accepted run, replay, graph identity, and claim boundary.

## Reading identity

| Field | Value |
|---|---|
| Event and run | `H2EPR-0288`; `run.h2epr.0288.canonical.v0_1` |
| Canonical graph serialized SHA-256 | `99f6fcaf2b7b571748d5de60de50b2babb135a25c567ca5f9d26594e86bed93a` |
| Graph preimage seal | `9353b1a6a93d01d04e1f50df7e9ff3273838d107bd550c2c9970ffac3bdd56e1` |
| Determinism witness | independent-repeat graph is byte-identical |
| Reading coverage | 1,392 of 1,392 nodes and 1,121 of 1,121 edges |

## Current boundary

No Draft EPG or Reference EPG was opened for this stage, and historical
material was not used as comparison evidence. The reading is an
interpretation of one deterministic mechanism-coverage run, not an empirical
comparison. A Draft-retention study, primary-source historical comparison,
and final synthesis remain possible later stages, each requiring an explicit
scope and its own evidence account.
