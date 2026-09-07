# Observations and state

## Purpose

This reference defines the participant-side information boundary. It separates
world truth, delivered observations, persistent participant state, transient
backend context, and author knowledge so that a backend cannot become
omniscient by accident.

## Five information layers

| Layer | Owner | May the Agent use it? |
|---|---|---|
| world state | scenario/environment | only after an admitted observation route exposes it |
| delivered observation | participant interface | yes, subject to freshness and scope |
| persistent participant state | participant interface/runtime | yes after a named update event |
| transient decision context | backend invocation | yes for the current decision; not persistent by default |
| author or evaluator knowledge | construction/evaluation process | no |

The same proposition can appear in more than one layer at different times.
For example, a resource shortage may first be world state, later a delivered
notice, and then a remembered participant fact. Record each transition.

## Observation inventory

Every material observation uses the exact `observation_id` from the accepted
event-wide registry. The maintained convention is a dotted `obs.<name>`
namespace. Give the following account.

| Field | Required meaning |
|---|---|
| observation ID | exact registry identity |
| content | what proposition or value is exposed |
| producer | Agent, Population, scenario process, environment, or admitted input |
| delivery route | interface or lifecycle transition that makes it visible |
| availability | conditions under which it exists |
| freshness | current, retained, superseded, stale, or unknown |
| missing behavior | what the interface receives when it is absent |
| visibility | public, addressed, role-scoped, or own-private |
| consumers | document-local `decision.*` labels allowed to use it |
| provenance | dataset claim, structural assumption, or generated material |

Do not use “all relevant information” or “current state” as an observation.
Those phrases erase delivery and visibility boundaries.

## Availability is not truth

Distinguish:

- the proposition is true in world state;
- a message carrying the proposition was sent;
- transport admitted and delivered the message;
- the Agent observed the message;
- the Agent retained it in persistent state; and
- the proposition remains current.

Each step may fail independently. A sender's trace does not prove receipt, and
receipt does not prove the proposition.

## Missing and stale information

For every observation used by a commitment, define:

- whether absence makes the situation non-applicable;
- whether a bounded wait, query, or conservative response remains admissible;
- whether an explicit `unknown` value is delivered;
- which event makes the observation stale;
- whether a replacement supersedes or merely supplements it; and
- whether prior information may still be retained.

Never fill a missing observation with a later Draft fact, another participant's
private state, or a backend guess presented as data. A backend may reason under
uncertainty only within the declared choice contract.

## Persistent state

Persistent state records participant-relevant event history that may affect a
later decision. It is not a transcript of model reasoning.

| Field | Required account |
|---|---|
| state-field path | exact dotted path projected by `persistent_state_fields` |
| initial condition | absent, unknown, or admitted initial value |
| update event | delivered message, own admitted intent, environment result, or scenario transition |
| update rule owner | shared handler, reducer, or participant runtime |
| visibility | own-private, shared, or public |
| retention/supersession | how long and by what event it changes |
| consuming commitments | where it can affect later choice |

Examples of appropriate persistent state include an Agent's own outstanding
request, its last delivered disposition, or a notice it has received.
Unobserved world truth and another Agent's private choice are not appropriate.

## Own intent versus admitted intent

Keep action disposition, transport disposition, and domain result separate.
The backend selects an action; the environment admits or rejects it and the
reducer applies its effects at the current coordinate. The next observation
can expose that actor's own action disposition and the resulting public or
own-private state. This does not require a message addressed back to the actor.

Attached messages enter transport only after their source action is accepted.
Their pending, rejected, delivered, or expired states do not retroactively
change that action disposition. A recipient's later response or a domain result
such as authorization is a separate event with its own owner. Own accepted
request, delivered request, and effective requested outcome are different facts.

## Reconsideration

A Definition should explain why a decision can reopen, while leaving exact
retry policy downstream.

Meaningful reopening events include:

- a previously missing mandatory observation arrives;
- a pending request receives a disposition;
- an observation is superseded;
- an environment result changes feasibility;
- a new decision situation activates; or
- an outgoing message expires, or an explicit business-withdrawal action
  receives its own disposition.

“Retry every tick” is backend policy, not semantic reopening. “Never reconsider”
is invalid when the interface declares later observations that materially
change the choice set.

## Mandatory information, feasibility, and policy

Classify every apparent prerequisite.

### World feasibility

The environment decides whether a route, target, authority, or resource exists.
The Agent may request an infeasible act; the environment rejects or records it
according to the scenario contract.

### Mandatory actor information

The shared interface rejects or withholds a decision if a named observation is
required for semantic validity. This must project consistently across Rule,
LLM, and RuleLLM.

### Policy selection

The backend chooses whether an available observation is persuasive, which
admissible alternative to select, or whether a permitted delay is worthwhile.
Do not promote a Rule threshold to mandatory information merely because the
current Rule implementation uses it.

## Visibility matrix

Use a matrix when several actors exchange related information.

| Observation | Producer | Public | Addressed target | Other Agents | Environment |
|---|---|---:|---:|---:|---:|
| `<ID>` | | yes/no | yes/no | conditions | source of truth |

If visibility cannot be stated without inventing a route, stop and return to
scenario or registry design.

## Backend context projection

The participant interface provides a backend-neutral context containing:

- actor identity and logical coordinate;
- allowed observation values and missing markers;
- permitted persistent state;
- admissible intent schema;
- configuration values explicitly owned downstream; and
- identity/provenance needed for traceability.

Rule code, prompts, and hybrid admission may serialize this differently. They
must receive equivalent semantics. Hidden access to the full reducer state,
Draft future, or another Agent's memory invalidates comparison.

Document-local decision labels explain how to interpret this context; they are
not fields in the current observation schema. The maintained menu lists the
actor's registered action types, not only those whose shared preconditions
currently pass. Backend activation and environment admission therefore remain
separate. General active-duty enforcement or recurring decision instances
require a reviewed projection; prose alone does not provide them.

## Information-related falsifiers

The contract fails if:

- a worked case requires a value absent from the observation inventory;
- a decision uses a message before delivery;
- stale data is treated as current without an explicit rule;
- a pending message is represented as recipient receipt or authorization,
  or an action without an accepted disposition is treated as applied;
- another participant's private state appears in context;
- a backend can access more event information than another without declaration;
- transient reasoning silently persists; or
- an observation has no producer or delivery route.

Route missing vocabulary to participant registries, missing delivery to the
scenario mechanism, persistence implementation to runtime, and selection
behavior to backend realization.

## Completion evidence

Completion requires a closed observation inventory, state ledger, visibility
matrix where needed, missing/stale behavior, reopening events, forbidden
information list, and at least one case where information is absent or
delayed. Every observation ID and exact state-field path must have an owner and
at least one declared producer or updater.
