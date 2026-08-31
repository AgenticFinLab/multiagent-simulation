# ADR-0018: accept the Note7 bounded-lineage conformance boundary

- Status: accepted
- Date: 31 August 2026
- Scope: H2EPR-0481 Samsung--regional--outlet--consumer lineage conformance
- Resolved decisions: `OD-0481-CNF-01` through `OD-0481-CNF-04`

## Context

The accepted H2EPR-0481 carrier binding projects seven participant intents
across one Samsung crisis interface, one Singapore regional unit, one outlet
unit, and one consumer choice unit. Six intents use four directed message
carriers. The outlet product-posture intent instead targets an institutional
process, which separately produces a result before the Scenario can expose a
remedy offer to the consumer.

Carrier validity alone does not prove that a later action cites the exact
upstream object, message, delivery, or result. It also does not prove causal
record order, deterministic seals, authoritative replay, or preservation of
the still-open fulfillment boundary.

## Decision

### `OD-0481-CNF-01` — exact release and bounded horizon

Use only the binding release identified by raw manifest SHA-256
`368637163b3d6d18120f378f9dbe8277a67a69ee679c1d72e93df22a366d43c8`.
The conformance horizon is four actors, seven actions, four directed carriers,
one product-posture result, one Scenario-owned remedy-offer delivery, and
logical ticks zero through fourteen. Pinned identity drift returns to the
binding phase.

### `OD-0481-CNF-02` — result ownership and causal identity

Keep participant intent, participant message, communication disposition,
delivery, product-posture result, Scenario-owned offer delivery, state delta,
and later observation distinct. The consumer request must cite the exact offer
and delivery. The outlet response must cite the exact request, request message,
request delivery, and posture result. Neither response delivery nor a proposed
path establishes eligibility, stock, handoff, payment, exchange, refund, or
completion.

### `OD-0481-CNF-03` — deterministic trace and replay

Record one fully exposed synthetic branch with the existing domain-neutral
trace, canonical hash, tick-seal, run-seal, validation, and replay primitives.
The replay state contains only state version and eight lineage stages. Repeated
construction must be identical. No simulator, scheduler, distributed actor
system, model backend, or complete Scenario runtime is started.

### `OD-0481-CNF-04` — receipt and stopping boundary

Publish a reproducible expected-vector receipt and implementation review after
focused carrier, negative-conformance, trace, replay, integrity, link, and
publication checks. Preserve the consumer request as unresolved at the outlet
because the path contains a response but no fulfillment result. Stop at
`PASS_BOUNDED_LINEAGE_CONFORMANCE`.

## Consequences

The method now covers a third event domain and a lineage that combines
organizational direction, regional coordination, outlet action, Scenario-owned
result production, and a two-way consumer route. The conformance package adds
no historical behavior and does not execute the other four configured actors
or thirty unbound intent placements.

The 2017 investigation remains outside every runtime carrier. The branch is
engineering evidence only: it supports neither parameter calibration,
historical fit, held-out evaluation, policy effectiveness, scientific
validity, nor universal generality.
