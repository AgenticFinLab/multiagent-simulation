# Decision situations and behavior

A decision situation is a bounded historical or counterfactual configuration
used to examine what the participant can know, decide, and request. It is not a
code branch and does not predetermine the environment's result.

## Select high-information situations

Start with situations that expose different parts of the proposed model, such
as:

- ordinary operation before visible stress;
- worsening conditions with incomplete information;
- a pending request or unresolved institutional process;
- receipt of new but partial or stale information;
- authority or eligibility not yet established;
- competing duties or scarce resources;
- denial, delay, partial realization, or failed action;
- a role, relationship, or information perturbation.

Use the smallest set that exposes the material mechanisms and boundaries. Add
another situation only when it introduces a distinct mechanism, authority
boundary, information problem, or behavioral prediction.

## Situation record

For each situation, explain:

| Element | Content |
|---|---|
| Historical location | Event interval and whether the situation is observed, reconstructed, illustrative, or counterfactual. |
| Research purpose | Mechanism or boundary the situation is designed to expose. |
| World conditions | Scenario facts relevant to the decision, without treating all of them as participant knowledge. |
| Legal observations | Information received by the participant, with source, time, channel, granularity, uncertainty, and freshness. |
| Hidden information | Material world facts or later outcomes the participant cannot use. |
| Prior private state | Pending requests, authorization, review stage, commitments, memory, or qualitative belief. |
| Authority and procedure | Preconditions, prohibitions, duties, and decision process in force. |
| Available alternatives | Legal intents, information requests, communications, delay, escalation, and abstention. |
| Decision commitments | Mechanisms and precedence that constrain the choice. |
| Participant output | Action or message intent, not a realized outcome. |
| Environment responsibility | Delivery, admissibility, feasibility, execution, partial effect, delay, failure, and world-state change. |
| Expected process pattern | Trace-visible sequence or absence predicted by the model. |
| Counterexample | A changed input, role, authority, or outcome that should alter or falsify the behavior. |

## Observation, state, and belief

Keep these concepts separate:

### Authoritative world state

The event model's current facts: resources, membership, relationships,
institutional status, messages in transit, and other participants' state. The
participant does not see this state by default.

### Legal observation

The information delivered through an allowed channel by the decision time.
Record whether it is exact, aggregated, qualitative, estimated, rumored,
delayed, or missing.

### Modeled private state

Persistent information needed to explain later behavior, including a pending
request, review stage, authorization status, previous commitment, last verified
information time, or operating posture. Define how it is initialized and what
legitimate event updates it.

### Belief or qualitative assessment

An interpretation of unknown world state formed from legal observations.
Represent it only if it changes decisions. Prefer explicit unknown, ordering,
interval, or qualitative categories when historical evidence cannot identify a
probability.

### Ephemeral reasoning

Momentary calculation or deliberation that does not persist and is not treated
as historical fact. Do not use an imagined inner monologue as evidence.

## Decision commitment

A decision commitment is a falsifiable behavior claim. It should identify:

1. its scope and decision situation;
2. supporting theory, event claims, or explicit assumptions;
3. required and prohibited information;
4. relevant private state;
5. authority and procedural conditions;
6. available alternatives;
7. duties, goals, precedence, and conflict handling;
8. intended action, message, request for information, delay, escalation, or
   abstention;
9. expected and forbidden process patterns;
10. evidence or perturbation that would weaken or reject it.

Do not create one commitment for every implementation conditional. One
commitment should express a behaviorally meaningful proposition with an
alternative explanation or a way to fail.

## Precedence and conflict

Explain choices in an institutionally meaningful order:

```text
jurisdiction and prohibitions
    -> required information and authorization
    -> procedural duties and existing commitments
    -> resource and feasibility beliefs
    -> role-specific priorities among legal alternatives
    -> fallback, escalation, delay, or abstention
```

This does not require every Agent to share one utility function or cognitive
architecture. It requires enough clarity that two readers can identify the
same legal choice set and the same hard constraints.

## Intent and result

Participant outputs describe what the participant attempts, requests,
communicates, offers, authorizes, refuses, schedules, or cancels. They must not
self-certify effects.

Distinguish at least:

- intent created;
- message or request delivered;
- institutionally admissible or prohibited;
- scheduled or pending;
- executed, partially realized, no effect, failed, delayed, expired, or
  cancelled;
- result delivered back to the participant;
- later participant response.

A historical statement such as “support was obtained,” “the institution was
stabilized,” or “the market recovered” is a result or interpretation, not an
Agent action.

## Worked cases

Ensure every major mechanism appears in a worked case or explicit
falsification check; one case may cover several mechanisms. A useful case in
prose or a compact table shows:

- exactly what the participant knows;
- what remains unknown;
- which authority and mechanism matter;
- the plausible alternatives;
- why the proposed intent falls within the model;
- what the environment must still determine;
- how the behavior changes under one meaningful perturbation.

Label observed historical cases, reconstructed cases, illustrative cases, and
counterfactual cases. A worked historical outcome is explanatory material, not
independent validation of a model built from the same outcome.

## Behavioral adequacy checks

- **Name erasure:** behavior should not change merely because the actor ID or
  historical name changes while all semantic properties remain fixed.
- **Role or authority swap:** exchanging authority should change the legal
  intent envelope where the model claims role differences matter.
- **Information masking:** missing or stale required information should produce
  the declared information request, fallback, delay, or abstention.
- **Future-fact exclusion:** later outcomes must not enter the decision.
- **Lifecycle check:** pending, denied, expired, partial, and completed states
  should produce distinguishable later behavior where relevant.
- **Intent-result check:** a valid request may still fail or have no effect.
- **Mechanism ablation:** removing a claimed mechanism should change a
  predeclared process pattern or reveal that the mechanism was decorative.
- **Representation check:** finer internal actors should be added only when
  they produce a necessary and testable distinction.
