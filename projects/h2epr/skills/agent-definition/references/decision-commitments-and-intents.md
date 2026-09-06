# Decision commitments and intents

## Purpose

A decision commitment is the smallest reviewable contract for one participant
choice situation. It states when choice is required or permitted, what
information is usable, which response classes are admissible, and where the
Agent's authority stops.

It is not a decision tree, prompt, score function, historical script, or
expected trajectory.

## Commitment identity

Assign each commitment a stable document-local label such as
`decision.response_request`. Use it to cross-reference sections and worked
cases. Current registries and backend bindings project the Definition through
its semantic parent plus exact observation, intent, and state identifiers; do
not add a decision-label field to them unless a reviewed schema adopts one.

Each commitment must answer:

| Field | Required account |
|---|---|
| situation | the bounded choice being represented |
| activation | observable condition that opens the choice |
| non-applicable condition | when the interface has no choice to make |
| usable observations/state | exact IDs available to this commitment |
| alternatives | semantic response classes, not backend-specific actions |
| minimum response | any duty that rules out silent no-op |
| prohibitions | choices never admissible in this situation |
| precedence | conflicts with other commitments or duties |
| delay/abstention | when it is meaningful and what it must not imply |
| reopening | new information or lifecycle event that permits reconsideration |
| intents | typed action/message outputs that can express the response |
| environment boundary | admissions and results the Agent cannot assert |
| falsifier | a process pattern contradicting the contract |

## Preserve meaningful choice

A semantic contract should constrain invalid choices and leave meaningful
selection to the backend. Usually it should admit more than one response under
at least one executable case.

If the dataset genuinely exposes a mandatory act, distinguish:

- the duty to respond;
- alternative ways to satisfy the duty;
- conditions under which the duty is non-applicable;
- environment rejection or failure; and
- whether the backend still controls timing, target, content, or escalation.

If nothing remains for a backend to select, reconsider whether the behavior is
a scenario transition rather than an Agent decision.

## Alternatives and preferences

An alternative is admissible because it respects the semantic boundary.
Preference among alternatives belongs to Rule, LLM, or RuleLLM.

Bad:

> If severity is high, issue the strongest response immediately.

This fixes both a threshold and a policy.

Better:

> When a delivered assessment activates `decision.response_request`, the Agent
> may request a restrictive response, request a limited response, seek
> clarification, or delay only while a named mandatory observation is missing.
> Configuration defines any comparable severity domain; the backend selects
> among currently admissible alternatives.

## No-op, delay, and abstention

Treat these as different semantics:

- **non-applicable**: no decision situation is active;
- **no-op**: the situation is active and an explicit non-action is admissible;
- **delay**: the Agent defers while a declared reopening event may arrive;
- **abstention**: the Agent declines to select despite having authority;
- **failure to respond**: a duty exists and no admissible response was emitted.

An always-no-op interface is incomplete when an activated situation has a
minimum response class. A permitted delay needs a reason, observable pending
state, and reopening event. Exact retry cadence remains backend configuration.

## Precedence and concurrent commitments

When multiple commitments can activate together, state whether they:

- can emit independently;
- share a mutually exclusive intent;
- require one commitment to resolve first;
- are suppressed by a higher-order duty; or
- create a conflict that must be exposed to the backend.

Do not resolve concurrency by relying on implementation order. If order is
semantically required, the contract or scenario lifecycle must state it.

## Intent inventory

An event-wide registry intent is a typed participant action request. Copy its
canonical lowercase snake-case `intent_id`; that value is the participant
decision's `action_type`. The runtime creates a distinct
`ActionIntent.intent_id` for each emitted instance.

| Field | Meaning |
|---|---|
| exact registry `intent_id` | canonical backend-neutral action type |
| permitting commitments | which choice contracts may emit it |
| target class | eligible recipient or environment route |
| content schema | required semantic fields without prompt formatting |
| lifecycle | proposed, emitted, admitted/rejected, delivered, acted on, expired, or withdrawn as applicable |
| idempotency/duplication | whether repeated intent is distinct or duplicate |
| participant-visible receipts | which lifecycle changes can later be observed |
| environment-owned result | state or effect that is never asserted by emission |

Avoid intent names that encode success, such as `closure_completed` or
`resource_delivered`. Prefer requests such as `request_closure` and
`request_resource`.

## Message output inventory

A participant decision may attach zero or more messages. Copy each canonical
`message_type` from the scenario mechanism and define:

| Field | Meaning |
|---|---|
| exact message type | canonical scenario `message_type` |
| permitting decision/action | local `decision.*` label and registry `intent_id` |
| eligible recipients | exact participant IDs or closed recipient class |
| payload semantics | required fields and bounded meanings |
| source action | relationship to the generating `ActionIntent.intent_id` |
| lifecycle | pending, delivered, expired, rejected, duplicate, or failed |
| environment-owned result | admission, route, delivery, interpretation, and response |

The runtime gives each emission a generated `message_intent_id`. Do not use the
message type, action type, or document-local decision label as that instance
identity.

## Action and message boundary

Use the action for an attempt to change modeled state through an environment
handler. Use attached messages for addressed or public communication. A
message may influence later behavior, but delivery and interpretation are not
guaranteed by emission.

For every intent, name the full boundary:

> Agent selects → participant emits → transport admits or rejects →
> environment delivers or schedules → reducer applies an authorized effect →
> later observation may expose the result.

The Definition owns the first two semantics. Shared transport, scenario, and
runtime own the remainder.

## Environment-owned results

The environment owns:

- route existence and target eligibility at runtime;
- institutional authorization;
- resource feasibility and allocation;
- delivery order and timing;
- action execution;
- world-state mutation;
- causal or physical effects; and
- receipts that expose those results.

An Agent may form an intent that is denied, delayed, superseded, only partly
implemented, or produces an adverse result. Those paths are required test
cases, not anomalies to remove.

## Configuration boundary

The Definition declares constructs only when they are semantically meaningful
across backends.

| Definition owns | Configuration owns | Backend owns |
|---|---|---|
| construct meaning | selected value | option-selection logic |
| admissible domain | seed and backend parameters | prompt/rule/hybrid implementation |
| invariant prohibitions | timeouts and policy windows | tie-breaking and fallback within contract |
| reopening semantics | exact cadence or threshold | response wording within schema |

Do not force every Agent to have numerical traits. Do not copy MASim-style
parameters merely to make the document look complete. Include a construct only
if a worked case or planned comparison depends on it.

## Backend equivalence

Rule code, an LLM, or RuleLLM admission selects within the same semantic choice
set. Backend-specific representations may differ, but all must share:

- active commitment identity;
- admissible alternatives;
- observation and state boundary;
- mandatory information checks;
- intent schema;
- prohibitions; and
- environment-result ownership.

If an LLM needs contextual prose, it must be a projection of admitted semantics,
not a new source of authority. If Rule needs an exact threshold, the value and
provenance belong to configuration.

## Contradiction patterns

A Definition is contradicted when:

- an active duty can disappear through unrecorded no-op;
- an intent directly mutates environment state;
- a backend emits an intent outside the commitment's alternatives;
- a selected intent presupposes delivery or success;
- reconsideration occurs without a named reopening event;
- implementation order silently supplies semantic precedence;
- an exact policy value is embedded in prose; or
- one backend receives a wider choice or information set.

## Completion evidence

Completion requires stable document-local decision labels and exact registry
intent IDs, closed mappings from observations to commitments and commitments
to intents, explicit
non-applicable/delay/reopening semantics, concurrency treatment, environment
boundaries, open backend choice, and at least one executable rejection or
adverse-result path.
