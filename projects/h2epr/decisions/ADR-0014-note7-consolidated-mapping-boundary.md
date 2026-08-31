# ADR-0014: Note7 consolidated mapping boundary

- Date: 31 August 2026
- Status: accepted for authoring-window candidate release
- Event: `H2EPR-0481`

## Context

The accepted roster release contains four Agent Definitions and four
Population Models spanning corporate product response, recall authority,
transport-warning and emergency-order issuance, regional implementation,
retail remedy, consumer choice, and operator response. The mapping phase must
preserve the full surface without altering participant behavior.

## Decisions

### `OD-0481-CM-01` — complete source surface

Use the exact roster release as the sole participant-semantic authority and
map all 8 products, 22 situations, 40 observations, 28 private-state
placements, and 37 intents.

### `OD-0481-CM-02` — Population identity

Represent regional, outlet, consumer, and operator products as distinct
unit-local actors. Population reuse creates no collective policy, memory,
authority, or knowledge.

### `OD-0481-CM-03` — lifecycle and authority separation

Use twelve Scenario-owned lifecycle families. Keep product and remedy
proposals, recall/warning/order issuance, publication, effect, delivery,
implementation, enforcement, physical result, and later observation distinct.

### `OD-0481-CM-04` — carrier disposition

Retain Contracts V1. Use event-qualified internal mapping and Scenario
semantics; no concrete successor counterexample has been found.

## Consequences

The mapping is complete as an engineering design and provides a fixed input to
Scenario Definition. It is not executable and makes no historical or
scientific claim. Review was performed in the authoring fork; the original max
supervisor remains the independent final reviewer.
