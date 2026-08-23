# ADR-0006: accept the Panic of 1907 Scenario Configuration boundary

- Status: accepted
- Date: 23 August 2026
- Scope: H2EPR-0288 Scenario Configuration v0.1
- Resolved decisions: OD-CFG-01 through OD-CFG-04

## Context

Event Scenario Definition v0.1 closes the shared event-world semantics for
all seven named Agent Definitions and five population models. It deliberately
defers exact time boundaries, actor and population assembly, opening records,
structural selections, policy references, sensitivities, and completion
choices to a separate versioned configuration.

The reviewed configuration candidate instantiates all 12 released semantic
products without presenting itself as a historical baseline. Its substantive
review resolved two major ambiguities before owner review: opening depositor
need is now distinct from dated activation, and every sensitivity operation
has a typed exact target. No blocking finding remains, but implementations,
carrier projections, numeric runtime values, and a loader are still absent.

## Decision

### `OD-CFG-01` — purpose and horizon

The first accepted configuration has a mechanism-coverage purpose. It begins
on 18 October 1907, treats 21–26 October as the primary causal window, and
uses the end of 2 November as an analytic horizon. That horizon is a declared
construction choice and is not a historical end date.

### `OD-CFG-02` — assembly

The accepted assembly contains seven named actors, six host-scoped depositor
actors, two bank actors, and one broker actor. It contains ten population
capability units. `member_bank_alpha` composes bank-resource and call-lender
capabilities under one actor, entity, authority graph, and resource owner.

### `OD-CFG-03` — baseline and sensitivities

The eight conservative structural selections are the baseline. Synthetic
population profiles, unit weights, normalized claims, qualitative opening
envelopes, and other construction choices are mechanism-coverage assumptions,
not historical estimates. Every sensitivity overlay must be materialized as
a new exact configuration identity before use and may not replace the
baseline after inspecting an outcome.

### `OD-CFG-04` — non-executable release boundary

Scenario Configuration v0.1 is accepted as a non-executable semantic
configuration. It may not be presented to a runner as executable until a
separately reviewed binding supplies exact policy implementation identities,
an exact carrier projection, and fail-closed loader and conformance checks.
If such implementation is separately authorized, the first slice is the
KT–NBC–NYCH request lineage rather than the full 16-actor integration target.

## Consequences

The versioned release under
`configs/panic_1907/scenario-configuration-v0.1/` is the accepted
configuration authority for H2EPR-0288. The older Rule and compiler canary
configuration files remain frozen engineering references and are not
semantic inputs to this release.

The configuration remains fail-closed and establishes no executable policy,
runtime carrier, simulation result, historical calibration, historical
validation, or scientific-validity claim. This decision does not authorize
Rule v2, LLM/RAG, Contracts mutation, broad event implementation, simulation,
or external publication.

The next eligible engineering question is a separately authorized minimal
loader and KT–NBC–NYCH projection. A reproducible mismatch must be routed to
its semantic owner; it may not be repaired by changing a sealed input or by
introducing an unrecorded backend default.
