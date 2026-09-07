# Annotated Agent Definition failure example

This document is deliberately nonconforming. Its fictional excerpts collect
shortcuts that can look plausible in prose while breaking H2EPR authority,
provenance, or backend neutrality. Never copy it as an event asset.

## Failed draft

> **Agent:** Harbor Authority
>
> The Harbor Authority represents management, legal counsel, inspectors,
> cleanup teams, communications staff, and all other relevant stakeholders. It
> knows the severity of the spill, which routes are safe, whether its request
> will be approved, and how the public will respond.
>
> The Agent has risk tolerance 0.72, trust 0.64, urgency 0.91, and a three-tick
> patience window. These values are based on normal emergency-management
> behavior. When severity exceeds 0.6, it immediately closes the harbor,
> allocates two cleanup teams, and announces that the spill is contained.
> Otherwise it waits. The LLM should reason carefully and choose the historically
> accurate outcome.
>
> The Agent can send any message to any participant. A successful closure action
> sets `harbor_closed=true`, delivers the notice to all port users, and reduces
> spill severity. If information is missing, it may do nothing until the
> simulation ends.
>
> Sources: the Draft EPG and public knowledge. Limitations: the model may not
> capture every detail. Future versions can improve realism.

## Finding 1: the represented interface is unbounded

The draft collapses management, legal authorization, inspection, resource
allocation, physical execution, and communication. These units can hold
different observations and powers. “All relevant stakeholders” also has no
membership rule.

Impact:

- one Agent receives organizational omniscience;
- independent vetoes and failures disappear;
- resource and legal authority move out of the environment; and
- another event cannot reuse the contract without copying this organization.

Correction:

Name one accountable decision interface and one choice family. List included
and excluded units, aggregation loss, and a split trigger. Route cleanup teams
to the scenario or a separately justified participant.

## Finding 2: world and future state appear as observations

The Agent “knows” true severity, safe routes, future approval, and public
response. The draft names no producer, delivery route, freshness rule, or
visibility boundary.

Impact:

- the backend is omniscient;
- pending, rejected, and adverse paths cannot occur;
- Rule and LLM contexts cannot be compared fairly; and
- later Draft or evaluator knowledge can leak into early decisions.

Correction:

Define typed delivered observations, explicit unknown states, and persistent
participant memory. Keep route safety and public response in world state until
a scenario process exposes them.

## Finding 3: invented parameters become participant truth

The numerical traits and window have no admitted anchor, unit, domain
justification, or downstream owner. “Normal behavior” relies on external
generalization.

Impact:

- arbitrary precision looks like evidence;
- the Definition fixes one backend's parameterization;
- sensitivity requires rewriting semantic identity; and
- values copied across events become hidden defaults.

Correction:

Delete unused personality traits. If a construct materially affects an
admissible choice, declare its meaning and domain in module 8, label its
provenance, and let configuration select the value.

## Finding 4: Rule policy is embedded in semantics

The severity threshold, immediate timing, fixed resource count, and binary
branch are a Rule implementation. The instruction to reproduce history is an
outcome target.

Impact:

- no meaningful option remains for LLM or RuleLLM;
- exact timing cannot vary without a semantic successor;
- policy assumptions become indistinguishable from dataset constraints; and
- a run can pass only by following a preferred trajectory.

Correction:

Write decision commitments with activation, admissible alternatives, duties,
prohibitions, delay, reopening, and environment boundaries. Put thresholds,
timing, and selection logic in configuration/backend realization.

## Finding 5: intent directly asserts environment results

The “closure action” changes navigation state, delivers a message, allocates
resources, and reduces physical severity in one participant operation.

Impact:

- authority and feasibility cannot reject the request;
- transport and reducer traces lose causal separation;
- replay cannot distinguish choice from outcome; and
- failure cases are structurally impossible.

Correction:

Emit a typed action and, if needed, attached messages. The shared handler and
reducer admit the action and apply its declared effects. Transport separately
handles messages from accepted source actions. A recorded request can coexist
with an undelivered message; a recipient's later authorization or execution is
another owned action. Expose each result through the appropriate state or
receipt instead of treating these steps as one successful participant act.

## Finding 6: communication scope is unlimited

“Any message to any participant” bypasses registered targets, content schemas,
privacy, route availability, and lifecycle.

Impact:

- private information can spread without evidence;
- invalid targets cannot fail closed;
- event vocabularies become unreviewable; and
- backends may invent protocols during execution.

Correction:

List each scenario `message_type`, eligible target class, required semantic
content, lifecycle, visible receipts, and environment-owned delivery result.

## Finding 7: no-op hides an active duty

The draft permits indefinite waiting whenever information is missing. It does
not distinguish non-applicable, delay, abstention, failure to respond, or a
meaningful reopening event.

Impact:

- a backend can avoid every difficult decision;
- missing-data handling cannot be falsified;
- a pending lifecycle never resolves; and
- Rule success may come from silent inactivity.

Correction:

Name mandatory information, admissible missing-data responses, minimum response
classes, bounded delay semantics, and events that permit reconsideration.
Leave the exact retry cadence downstream.

## Finding 8: provenance and limitations are not reviewable

“The Draft EPG and public knowledge” provides no stable anchors and mixes
admitted data with prohibited external material. “May not capture every
detail” identifies no modeling loss or successor condition.

Impact:

- claims cannot be withdrawn or challenged;
- protected-input exposure cannot be audited;
- an assumption can masquerade as a dataset fact; and
- future authors do not know whether to revise roster, scenario, or backend.

Correction:

Create claim and assumption ledgers with stable locators, owners, alternatives,
and withdrawal consequences. State concrete omitted distinctions and the
exact observation that would require narrowing, splitting, or a successor.

## Failure-routing summary

| Failed content | Correct owner |
|---|---|
| organization-wide aggregation | roster and representation review |
| safe route, legal status, cleanup resources, physical effects | scenario/mechanism |
| observation and action-intent IDs | participant registries |
| message types and delivery routes | scenario mechanism and shared configuration |
| risk threshold, patience window, resource count | configuration |
| binary selection and historical-outcome instruction | backend realization |
| delivery, closure, allocation, severity mutation | transport/environment/reducer |
| historical accuracy | later scientific evaluation |

## What a corrected review must demonstrate

A correction is not complete merely because the prose is longer. Independent
review must find:

- one bounded interface;
- resolvable dataset and assumption ledgers;
- no prohibited exposure;
- observations with producers and delivery routes;
- participant state with named update owners;
- stable decision commitments, registry action types, and scenario message
  types;
- meaningful backend choice;
- explicit environment rejection and adverse-result paths;
- worked falsifiers; and
- concrete limitations and successor conditions.

This failed draft has no completion evidence and must not advance to registry
projection or backend realization.
