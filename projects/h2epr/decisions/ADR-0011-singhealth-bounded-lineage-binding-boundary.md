# ADR-0011: accept the SingHealth bounded-lineage binding boundary

- Status: accepted
- Date: 26 August 2026
- Scope: H2EPR-0616 SCM technical--operations--GCIO carrier binding
- Resolved decisions: OD-BND-01 through OD-BND-04

## Context

The accepted H2EPR-0616 configuration identifies one illustrative lineage
across an SCM application/database technical unit, an application/SCM
operational unit, and the SingHealth GCIO. Static admission established that
the exact configuration and its semantic authorities are internally closed,
but supplied no carrier projection or policy implementation.

The compatibility review found that Contracts V1 can represent the selected
observations, intents, messages, routes, capacities, lifecycle references, and
verification result without a schema change. The earlier Panic of 1907 profile
cannot be reused because its product inventory and lifecycle semantics are
event-specific.

## Decision

### `OD-BND-01` — lineage and logical horizon

Bind exactly three actor instances, the two accepted bidirectional route
records, four semantic intents, and a synthetic positive sequence from logical
tick zero through eight. Project the two route records into four directed
message carriers without changing configuration route identity.

### `OD-BND-02` — exact derived semantic profile

Load the exact configuration, receipt, Roster, mapping, semantic inventory,
selected Definitions, and implementation surfaces by identity and hash. Derive
the nine-product observation, private-state, decision, and intent catalogs from
the released products and reject ambiguous or changed document grammar rather
than inferring a replacement mapping.

### `OD-BND-03` — bounded policies and result separation

Bind only the time, information, technical verification, route, authority, and
lifecycle policies needed by the four intents. Keep message issue and delivery,
verification request and result, escalation and interpretation, and result and
later observation separate. Coordination, incident, and notification policies
remain unbound.

### `OD-BND-04` — conformance and stopping boundary

Validate Contracts V1 projections, exact capacities and routes, causal
predecessors, lifecycle reopening, idempotency, and focused failure cases. Do
not add a full roster runtime, implementations for unrelated policies, a
simulation, calibration, evaluation, or historical or scientific validity
claim. Deterministic trace and replay closure remain the next bounded phase.

## Consequences

The binding demonstrates end-to-end carrier compatibility for one
non-financial, cross-institution lineage while leaving the complete accepted
configuration non-executable. It introduces an event-qualified derived profile
because the release documents share semantic responsibilities but not a
universal machine-readable grammar.

Future events may reuse the profile pattern only after their own released
documents satisfy an explicitly selected grammar and semantic inventory. A
mismatch returns to the source release; it is not repaired by a parser default,
merged capacity, inferred route, or invented result.
