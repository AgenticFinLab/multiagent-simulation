# ADR-0007: accept the SingHealth consolidated mapping boundary

- Status: accepted
- Date: 25 August 2026
- Scope: H2EPR-0616 Roster Definition release v0.1
- Resolved decisions: OD-CM-05 through OD-CM-08

## Context

Roster Definition release v0.1 fixes seven office-level Agent Definitions and
two responsibility-unit Population Models. Their 29 decision situations use
62 observation placements, 44 private-state placements, and 54 intent
placements. Several offices share an institutional host, while reader-facing
observation and intent labels recur across capabilities.

The consolidated review finds no missing autonomous participant and no
released semantic requirement that H2EPR Contracts V1 cannot represent. It
does find that H2EPR-0616 needs an event-qualified internal mapping profile and
event-specific Scenario semantics for technical state, delivery, lifecycles,
authority, results, and replay.

## Decision

IHiS, SingHealth, MOH, MCI, and CSA retain canonical institutional identities.
Office actors and responsibility units are scoped sub-entities with their own
observations, private state, decisions, intents, and recipient histories. They
do not create duplicate institutional, system, resource, relationship,
delivery, or result truth.

Observation, private-state, decision, intent, action, and schema identities
are event- and capability-qualified while preserving the released
reader-facing names. All 44 behaviorally material private-state placements use
reducer-versioned, capability-scoped paths. Participant state may retain
assessments and references but may not become a second copy of technical or
institutional truth.

Contracts V1 is retained. The internal profile identity is
`h2epr.roster-consolidated-mapping.0616.v0_1`; a Contracts successor is not
justified. Action admission, message materialization, route and delivery,
institutional processing, technical execution, result, StateDelta, and later
observation remain distinct.

If implementation is separately authorized after configuration admission, the
first slice is an exact fail-closed release/mapping loader and one bounded
technical-to-institutional lineage. This decision does not authorize all 54
intent implementations or a full-event simulation.

## Consequences

The accepted consolidated mapping is the design authority for projecting the
fixed H2EPR-0616 Roster release into Contracts V1. The Panic of 1907 profile
remains an event-specific reference and is not relabeled or reused as the
SingHealth mapping.

A later loader must validate every source hash and exact semantic set, reject
ambiguous capacity and recipient scope, preserve correction and partial-result
lineage, and assert generated StableId bounds. Any request for a Contracts
successor must first demonstrate an irreducible loss at a recorded watchpoint.

This decision establishes no configuration, executable policy, runtime,
simulation, calibration, evaluation, historical-validity, or
scientific-validity claim.
