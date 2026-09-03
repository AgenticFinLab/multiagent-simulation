# Execution cycle closeout template

## Cycle boundary

Record package, backend realization, configuration, seed/model settings,
runtime/compiler identities, custody paths, and excluded claims.

## Coverage inventory

List actors, decision calls, action/message intents, dispositions, state
deltas, lifecycle terminals, unresolved transport, ticks, trace records,
Generated EPG nodes, and edges.

## Integrity and replay

Record trace validation, tick/run seals, authoritative replay, final-state
identity, graph provenance, endpoint closure, and checksum results.

## Repeatability or model provenance

For deterministic runs, compare two fresh materializations byte for byte. For
model runs, pin model and decoding inputs and report observed variation without
claiming determinism unless it is demonstrated.

## Disposition

Use `complete`, `complete with recorded limitations`, or `return to owning
layer`. State exactly what the run establishes and what it does not.
