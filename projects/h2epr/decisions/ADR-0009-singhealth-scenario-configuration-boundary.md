# ADR-0009: accept the SingHealth Scenario Configuration boundary

- Status: accepted
- Date: 25 August 2026
- Scope: H2EPR-0616 Scenario Configuration v0.1
- Resolved decisions: OD-CFG-05 through OD-CFG-08

## Context

The accepted Event Scenario Definition and consolidated mapping close the
event-world and participant interfaces for seven office-level Agent
Definitions and two responsibility-unit Population Models. They deliberately
leave exact configuration purpose, time bounds, assembly instances, opening
records, structural selections, exogenous inputs, policy meanings,
sensitivities, completion, and the first bounded lineage to a separately
versioned Scenario Configuration.

The reviewed configuration instantiates all nine released semantic products
through seven office actors and six function-specific responsibility units.
Its revision review resolved four material gaps in capacity/availability,
route identity, opening technical objects, and exact sensitivity operations,
plus two traceability and publication-boundary defects. No semantic finding
remains open. The representation is still provisional and no required policy
has an implementation.

## Decision

### `OD-CFG-05` — purpose and horizon

The accepted configuration has a mechanism-coverage purpose. It begins around
23 August 2017, begins participant response on 18 January 2018, treats
11 June through 20 July as the acute interval, closes its core horizon on
20 July, and observes recipient-specific notification delivery through
23 July. These bounds preserve accepted precision and do not assert a
historical end, replay, calibration, validation, or outcome fit.

### `OD-CFG-06` — assembly and bounded lineage

The accepted assembly contains seven office actors and six function-specific
responsibility-unit actors. Every office and unit keeps its own identity,
capacity, authority or assignment, availability rule, private state, access
scope, and result history. The only named later implementation candidate is
the SCM application/database technical unit to application/SCM operational
unit to SingHealth GCIO lineage through two explicitly addressed routes.

### `OD-CFG-07` — structural, input, policy, and sensitivity boundary

Six structural baselines, 33 qualitative or explicit-unknown opening records,
six non-outcome-forcing exogenous inputs, nine unbound policy meanings, and six
paired exact sensitivity overlays are accepted. The eight technical-object
identities support assignment and reference closure without claiming an asset
inventory; unsupported object instances, ownership, prestates, delivery, and
results remain unknown until admitted input or adjudication supplies them.

### `OD-CFG-08` — non-executable release boundary

Scenario Configuration v0.1 is accepted as a non-executable semantic
configuration. Successful parsing or later structural admission may not make
it executable. Execution remains prohibited until an admitted representation,
exact fail-closed loading, event-qualified carrier projection, every required
policy implementation, bounded participant binding, runtime identity, and
separate execution authorization all exist.

## Consequences

The versioned release under
`configs/singhealth_data_breach/scenario-configuration-v0.1/` is the accepted
mechanism-coverage configuration authority for H2EPR-0616. Its provisional
serialization makes no conformance claim against the existing v0.1 admission
schema, whose current population-unit alternatives are event-specific to the
Panic of 1907 configuration.

The next legal stage is a separately authorized bounded configuration-
admission preflight. That stage may test compatibility and define the smallest
exact admission surface, but this decision does not itself authorize schema
evolution, a loader, carrier projection, participant binding, policy code,
runtime, simulation, calibration, evaluation, Contracts mutation, or a
historical or scientific-validity claim.

A later mismatch must be returned to its semantic owner. It may not be repaired
with a backend default, merged institutional route, invented technical state,
or outcome-conditioned change.
