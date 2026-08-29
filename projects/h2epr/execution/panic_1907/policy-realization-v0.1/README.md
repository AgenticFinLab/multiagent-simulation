# Panic of 1907 Policy Realization v0.1

- Event: `H2EPR-0288`
- Realization: `h2epr.0288.policy-realization.v0_1@0.1.0`
- Status: `accepted_policy_realization`
- Purpose: deterministic, uncalibrated mechanism coverage

This release maps the accepted Panic of 1907 participant and Scenario
semantics to a closed set of deterministic Rule implementations. It is the
execution boundary between the non-executable Scenario Configuration and the
later full-roster runtime package.

The [machine realization](policy-realization.json) binds each configured
actor-capability placement to one static participant policy, each selected
Scenario policy to one implementation, and each business-process family to
one authoritative lifecycle rule. The [review](substantive-review.md) records
the semantic, failure, and claim-boundary assessment.

## Closed surface

| Surface | Accepted count |
|---|---:|
| actor instances | 16 |
| actor-capability placements | 17 |
| decision commitments | 88 |
| observation placements | 158 |
| private-state placements | 56 |
| configuration-parameter bindings | 23 |
| intent placements | 127 |
| selected Scenario policies | 9 |
| lifecycle families | 13 |

The twelve participant implementations are shared where several configured
actors use the same released capability, while actor state and configuration
pointers remain separate. Every commitment has an explicit set of consumed
observations, persistent state, emittable intents, lifecycle references,
no-intent reasons, and revisit triggers. Population profiles and postures are
read from the hash-pinned configuration rather than from implementation
defaults.

The Scenario layer supplies the selected partial-order, information,
host-service, review, qualitative-amount, dated-facility, explicit-venue,
lifecycle-revisit, and typed-result rules. The lifecycle layer supplies the
thirteen state graphs declared by the accepted Event Scenario Definition.
Invalid transitions return a typed failure without changing authoritative
state.

## Authority and result boundary

Participant policies may choose and emit declared intents. They do not author
message delivery, case disposition, resource transfer, payment, settlement,
or another participant's decision. Scenario policies adjudicate the relevant
environmental step, and lifecycle rules alone advance authoritative business
state. A result becomes participant knowledge only through a later delivery.

Missing implementations, unresolved configuration pointers, unknown
capabilities or semantics, invalid lifecycle definitions, and unsupported
inputs fail closed. No dynamic import, silent intent repair, hidden score, or
resource allocation is admitted.

## Scope

This release establishes implementation and admission closure, not a completed
simulation. It does not contain a runtime bundle, canonical run, trace, replay
receipt, or generated EPG. Those belong to the separately versioned executable
successor and run packages.

The policies are exposed to the historical outcome and use construction
choices where the record is underdetermined. The release therefore makes no
claim of historical calibration, historical reconstruction, held-out
performance, policy effectiveness, or scientific validity.
