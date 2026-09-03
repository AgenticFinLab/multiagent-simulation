# Event Scenario design guide

## Authority boundary

The Scenario owns the event world: clock, state, institutions, relationships,
resources, routes, admission, deterministic effects, lifecycle results,
annotations, and termination. Participants own choice within their declared
interfaces. Backends produce intents. The reducer alone commits state.

If a Scenario must guess what a participant can observe or choose, return the
gap to the semantic parent. If a participant declares its own successful
effect, return the gap to the Scenario.

## Timeline design

Define the opening state, ordered logical coordinates, endogenous window,
exogenous schedule, transport latency, expiry, named barriers, and termination
before writing handlers. Each coordinate maps to admitted Draft anchors but is
an executable ordering choice, not necessarily a claim about physical time.

Use exogenous inputs only for dataset-provided changes that are not choices of
an active participant. An automatic schedule must not hide a decision merely
to reduce the roster.

## State and mechanism ledger

| Element | Required account |
|---|---|
| state field | entity, JSON type/domain, visibility, single update authority |
| intent handler | eligible actors/targets, typed parameters, preconditions, deterministic effects |
| message kind | sender/recipient classes and payload meaning |
| route | directed endpoints, latency, expiry/failure behavior |
| resource | units, conservation, allocation and conflict policy |
| lifecycle | initial, pending, terminal states and transition owners |
| annotation | condition, participants, one-shot behavior, no mutation authority |
| termination | coordinate completion, transport barrier, state invariants |

Every registered intent, including `no_op`, has one handler. Validate all
concurrent intents against the same sealed prestate. Detect the full writer set
before mutation; reject distinct writes and allow only explicitly idempotent
same-value writes under the current conflict contract.

## Interface-closure cases

Exercise a normal action, invalid actor, invalid target, out-of-domain payload,
failed precondition, missing route, delayed delivery, terminal delivery,
distinct concurrent writes, idempotent same-value writes, resource
contention, annotation firing, and termination with pending transport. Permute
input order and opaque IDs so lexical ordering cannot determine a winner.

## Falsifiers

The design fails if a hidden/future value reaches an observation, two layers
own one field, an emitted intent lacks a handler, a message lacks a terminal
route, effects depend on actor names, an annotation mutates state, replay
cannot reapply deltas, or termination ignores pending transport.

## Failure routing and handoff

Return observation, intent, or authority gaps to Agent/Population work. Return
selected values to configuration and decision logic to backend realization.
Framework-level schema or reducer gaps require a synthetic failing case before
a shared change.

Publish the ten-module Scenario Definition, machine interface, machine
mechanism, Interface Closure, manifest, and checksum inventory. Record parent
hashes, field/handler/route/lifecycle counts, adversarial cases, limitations,
successor trigger, verdict, and next legal action.
