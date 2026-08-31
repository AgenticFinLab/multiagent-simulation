# ADR-0017: accept the Note7 bounded-lineage binding boundary

- Status: accepted for authoring-window candidate release
- Date: 31 August 2026
- Scope: H2EPR-0481 Samsung--regional--outlet--consumer remedy binding
- Resolved decisions: OD-0481-BND-01 through OD-0481-BND-04

## Context

The accepted H2EPR-0481 configuration identifies a four-participant remedy
lineage. Static admission fixes its actors, routes, seven semantic intents,
unbound policy meanings, and non-executable boundary, but supplies no Contracts
V1 projection or policy implementation.

Binding preparation found and returned one causal-order defect to the
configuration: an outlet response had preceded the consumer request. The
re-admitted release now orders request before response and the shared validator
requires every cross-capability transition to follow a declared lineage route.

## Decision

### `OD-0481-BND-01` — lineage and logical horizon

Bind exactly four actors, three accepted bidirectional configuration routes,
seven semantic intents, four directed message carriers, one non-message outlet
posture action, and a synthetic positive sequence from logical tick zero
through fourteen. The outlet--consumer carrier is exercised in both
directions.

### `OD-0481-BND-02` — exact derived semantic profile

Pin the v0.2 Scenario Configuration, admission receipt, Roster, consolidated
mapping, semantic inventory, four selected products, and all implementation
surfaces by SHA-256. Bind the complete 20-observation surface of those products
while implementing only the seven configured intents.

### `OD-0481-BND-03` — bounded policies and result separation

Bind only time, information, route, authority, product-posture, remedy, and
lifecycle policies. Keep direction, program, coordination, proposal, outlet
posture, posture result, offer delivery, consumer request, outlet response,
eligibility, stock, handoff, payment, completion, and later observation
distinct. Hazard and public-action policies remain unbound.

### `OD-0481-BND-04` — stopping boundary

Validate selected Contracts V1 carriers, exact capacities and routes,
request/response provenance, non-message action handling, lifecycle reopening,
idempotency, and focused negative cases. Do not add full-roster execution,
simulation, calibration, evaluation, or historical or scientific validity
claims. Deterministic lineage trace and replay are the next bounded phase.

## Consequences

The binding is event-qualified and does not replace the complete mapping or
make the accepted configuration executable. It actively rejects a response
that cites another request, an offer derived from another proposal or posture
result, a message on the wrong route, or an outcome embedded in participant
parameters. Final independent review remains with the original max supervisor.
