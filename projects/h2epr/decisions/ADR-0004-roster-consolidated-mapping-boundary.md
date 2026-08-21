# ADR-0004: accept the Panic of 1907 consolidated mapping boundary

- Status: accepted
- Date: 22 August 2026
- Scope: H2EPR-0288 Roster Definition release v0.1
- Resolved decisions: OD-CM-01 through OD-CM-04

## Context

Roster Definition release v0.1 fixes seven Agent Definitions and five
population models as the sole semantic input to consolidated mapping. The
earlier Knickerbocker Trust–New York Clearing House binding remains a tested
two-role reference, but its one-definition-per-participant assumptions cannot
represent the full Roster without duplicating institutions, resources or
business lifecycles.

The consolidated inventory finds 115 observation placements and 107 intent
placements. A read-only carrier review finds no released semantic requirement
that Contracts V1 cannot represent. It does find that the project needs a new
internal mapping profile and fuller Panic of 1907 scenario semantics.

## Decision

One historical or legal entity has one runtime actor interface, one authority
graph and one resource owner. Released Agent Definitions and population models
compose as capability authorities; they do not automatically create separate
runtime actors. Institution-preserving population units keep their identities,
while depositor units are scoped to a host institution and do not share a
wallet or private state.

Observation and intent identities are capability-qualified. Behaviorally
material private state has two authoritative replay paths: effectful process
state is reducer-owned, while a consumption cursor or bounded no-intent posture
that is fully specified by DecisionRecords is reconstructed from the sealed
trace. Backends may not keep hidden persistent behavioral state.

Contracts V1 is retained. A consolidated internal mapping-profile successor
and a Panic of 1907 scenario semantic extension are required; a Contracts
successor is not justified. Action disposition, message delivery, business
disposition, execution result, StateDelta and later observation remain distinct.

The first eligible implementation scope is a mapping-loader and conformance
slice. This decision records that future scope but does not authorize
implementation, simulation, Rule v2, LLM/RAG work or contract changes.

## Consequences

The accepted consolidated mapping specification is the design authority for
translating the fixed Roster release into V1 carriers. The two-role binding is
retained as a frozen engineering reference and is not extended in place.

A later implementation must hash-check all twelve semantic products, preserve
one resource owner across composed capabilities, materialize the required
scenario lifecycles and prove reducer/trace closure. Any request for a V1
successor must first exhibit a concrete semantic loss at a recorded watchpoint.

This decision establishes no executable binding, historical calibration,
simulation result or scientific-validity claim.
