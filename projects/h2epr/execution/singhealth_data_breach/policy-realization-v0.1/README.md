# SingHealth Data Breach Policy Realization v0.1

- Event: `H2EPR-0616`
- Realization: `h2epr.0616.policy-realization.v0_1@0.1.0`
- Status: `accepted_policy_realization`
- Purpose: deterministic, uncalibrated mechanism coverage

This release maps the accepted SingHealth Data Breach participant and
Scenario semantics to a closed set of deterministic Rule implementations. It
is the execution boundary between the non-executable Scenario Configuration
and the full-roster runtime package.

The [machine realization](policy-realization.json) binds every configured
actor-capability placement to a static participant policy, every selected
Scenario policy to one implementation, and every declared business-process
family to an authoritative lifecycle rule. The
[review](substantive-review.md) records the semantic, failure, and claim
assessment.

## Closed surface

| Surface | Accepted count |
|---|---:|
| semantic participant products | 9 |
| actor instances | 13 |
| actor-capability placements | 13 |
| decision commitments | 41 |
| observation placements | 82 |
| private-state placements | 60 |
| configuration-parameter bindings | 0 |
| intent placements | 74 |
| selected Scenario policies | 9 |
| lifecycle families | 11 |

The nine participant implementations are reused where multiple configured
responsibility units share one released Population Model. Each unit remains a
separate actor with its own observations, private state, institutional host,
assignment, access, capacity, and result history. Every commitment declares
its consumed observations, persistent state, possible intents, lifecycle
references, no-intent reasons, and reopening triggers.

No participant-policy parameter is read directly from the configuration. This
is deliberate: responsibility-unit membership, institutional capacity,
authority, access, resource ownership, and structural variants remain
Scenario-owned inputs to adjudication rather than participant preferences or
hidden defaults.

The Scenario layer supplies explicit rules for event ordering, information
version and delivery, technical prerequisites and results, communication
routes, coordination, authority, institutional incident processing,
idempotent result handling, and notification. The lifecycle layer supplies
the eleven state graphs declared by the accepted Event Scenario Definition.
Invalid transitions return typed failures without changing authoritative
state.

## Authority and result boundary

Participant policies choose only among their released intents. They do not
author technical effects, message delivery, meeting attendance, incident
classification, report acceptance, outreach approval, notification delivery,
or another participant's response. Scenario policies adjudicate those steps,
and reducer-owned lifecycle transitions and state deltas alone change
authoritative business state. A result becomes participant knowledge only
through a separately delivered observation.

Missing implementations, parent drift, unknown actors or capabilities,
unresolved semantic references, invalid lifecycle definitions, and
unsupported inputs fail closed. No dynamic import, silent intent repair,
implicit authority, transitive knowledge, selected technical outcome, or
participant-authored result is admitted.

## Scope

This release establishes implementation and admission closure. It does not
contain a runtime bundle, canonical run, trace, replay receipt, or generated
EPG; those belong to the separately versioned executable successor and run
packages.

The Rules were constructed with access to the event record and are intended
to exercise the declared mechanisms, not reproduce the historical sequence.
The release makes no claim of historical calibration, historical validation,
held-out performance, policy effectiveness, or scientific validity.
