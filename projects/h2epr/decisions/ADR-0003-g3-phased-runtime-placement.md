# ADR-0003: place G3 in an opt-in paired phased runtime

Status: accepted as the evolvable G3 architecture-canary baseline

Resolves: the pre-G3 placement/reconsideration items in ADR-0001 and ADR-0002

## Decision

The G3 canary uses an explicitly imported `PhasedSimulator` / `PhasedSimulationRunner`
pair. Domain-neutral observation, intent, disposition, reducer-authority,
transport, trace and seal mechanics live under `masim.integrations.event_process`.
The fixed participant policy, world effects, G2 adapter and P007 detectors remain
under `projects/h2epr/src/h2epr/runtime`.

The standard `GeneralSimulator`, its paired runner, its level execution, and
legacy message dispatch remain unchanged. The phased runtime preserves MASim's
outer lifecycle while replacing level dispatch with the ten explicit atomic
barriers required for same-prestate event-process simulation.

## Scientific boundary

Each G3 run accepts exactly one sealed row from the existing nine-row G2 matrix
and its regenerated EventBundle. It is an `architecture_demo_only`,
`full_draft_exposed`, Rule-only engineering canary. Dates are logical clock
coordinates, not a historical schedule. P007 annotations cite generated trace
records only. No Generated EPG or evaluation is produced.

## Evolvability

The generic types and phased lifecycle are versioned extension points, not a
permanent universal event ontology. A successor may revise their public
contracts with migration tests. Event-specific roster, thresholds, resource
equations and identities must not move into the generic package.

## Consequences

- participant completion order is canonicalized before reduction;
- only the reducer commits state and increments the version once per tick;
- messages have append-only dispositions and cannot cause a second decision in
  their send tick;
- the trace is hash chained, tick sealed, run sealed and replayed;
- local Ray is an execution mechanism, never scientific provenance.

The accepted Gate is `PASS_WITH_RECORDED_LIMITATIONS`. It approves this
Reference-blind Rule-runtime engineering baseline, not historical calibration,
scientific validity, Generated EPG correctness, evaluation, or a permanent
package layout. G4 must validate and wrap the immutable G3 scientific package
before treating a trace as compiler/evaluator eligible.
