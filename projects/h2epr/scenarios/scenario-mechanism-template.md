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

## Admission

Reject duplicate IDs, unknown fields/actors/targets, uncovered registry
intents, out-of-domain values, implicit routes, event-specific Python
branches, and a producer-authored receipt that cannot be independently
rederived.
