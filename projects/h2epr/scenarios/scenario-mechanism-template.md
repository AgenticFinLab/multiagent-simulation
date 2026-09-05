# Scenario Mechanism template

`scenario-mechanism.json` is the machine authority for executable event-world
semantics. Publish it inside the current Scenario Definition release.

## State fields

Declare each entity/field exactly once with JSON value type, allowed values or
bounds, visibility, and the current environment successor as update authority.
Initial values belong to shared configuration.

## Intent handlers

For every registered intent, declare eligible actors and targets, exact typed
parameter domains, preconditions over declared state, and deterministic
effects. Include a typed `no_op` handler for every active actor. Effects may
set, increment, or append uniquely; messages have no direct write authority.

## Messages and routes

Declare message kinds, eligible senders/recipients, and payload meaning here.
Declare concrete directed routes and latency in shared configuration. Every
emitted message needs one route and a terminal lifecycle before closeout.

## Conflict, annotations, and termination

Use `reject_distinct_concurrent_writes_allow_idempotent_same_value` unless a
reviewed successor defines another policy. Validate every intent against the
same sealed prestate, detect the complete writer set before mutation, and
reject every participant in a distinct conflict. Identical `set` writes may be
accepted idempotently using only semantic serialization keys. Input order and
opaque generated IDs cannot choose a winner. A condition may reference only a
declared field.

`termination_invariants` contains safety/integrity conditions and may be empty.
Do not use it to require every participant to reach a preferred state.
`outcome_expectations` separately names descriptive terminal comparisons, each
with an `expectation_id`, label, field, operator, and value. The run receipt
reports the observed value and whether it matched. An unmet expectation does
not invalidate a sealed, replayable run.

For example, a response that arrives after a request's decision window may
leave its domain status open while all messages have been delivered. This is
a complete run with an unmet outcome. A notice still queued beyond the final
transport barrier prevents a complete release; preserve the failed attempt.

## Admission

Reject duplicate IDs, unknown fields/actors/targets, uncovered registry
intents, out-of-domain values, implicit routes, event-specific Python
branches, and a producer-authored receipt that cannot be independently
rederived.
