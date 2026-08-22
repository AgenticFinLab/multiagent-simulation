# H2EPR Agent Definition Template

> Status: working research template · event-bound · versioned

An H2EPR Agent Definition is the canonical account of how one historical participant is represented as a
decision-making actor in a bounded event model. It serves two audiences: readers evaluating the historical and
behavioral model, and implementers translating that model into Rule-based or future model-based Agents.

The ten modules below provide a stable reading order across participants. Their contents remain proportional to
the role: equations, numerical parameters, internal-actor decompositions, and structural alternatives are used
when they clarify a material mechanism. Evidence records, scenario facts, machine interfaces, and realized
results retain their own authorities and are referenced rather than duplicated here.

## 1. Model overview

Begin with a compact table that lets a reader understand the model before reading its details.

| Field | Description |
|---|---|
| Historical participant | Named person, organization, group, or institutional body. |
| Modeled role | The decision interface represented by the Agent. |
| Event and interval | Event identity and the bounded period in which the model applies. |
| Primary decision situations | Two or more high-information situations covered by the Definition. |
| Decision cadence | Event-driven, scheduled, or mixed; identify what creates a decision occasion. |
| Decision form | Decision table, state machine, constrained set-valued policy, equation, or another justified form. |
| State authority | Where institutional truth and behaviorally material participant state are recorded. |
| Evidence and model status | Construction status, exposure boundary, calibration status, and appropriate claims. |
| Definition identity | Stable identifier and semantic version. |

Follow the table with a short account of the participant's modeled purpose, central mechanism, and principal
research questions. State the situations the Definition explains and the adjacent processes it leaves to other
participants or the event environment.

## 2. Historical participant and representation

Describe the historical entity before introducing the model abstraction.

Cover:

- the participant's identity and event-specific position;
- the person, office, committee, organization, or coalition represented by the Agent;
- internal actors aggregated into the interface and actors explicitly excluded;
- the difference between the historical participant and the modeled role;
- known losses introduced by aggregation; and
- observations that would require the participant to be split, narrowed, or represented as an institutional
  protocol rather than a discretionary Agent.

For an organization, identify the decision interface instead of attributing a single personality to the whole
institution. Personal traits belong here only when they have a documented behavioral meaning in the focal
situation.

## 3. Evidence and theoretical foundation

Explain why the proposed behavior is a defensible model.

### Event-specific evidence

Summarize the sources that establish the participant's role, relationships, information, authority, resources,
and observed decisions. Link each material statement to evidence-ledger claim identifiers. Preserve conflicts,
missing records, retrospective bias, participant-availability time, and exposed outcomes.

### Theory and empirical research

Identify the original theoretical or empirical work used to interpret behavior. Explain the mechanism that is
being transferred, its population and institutional scope, and why it is relevant to this participant. A
citation alone does not establish that a mechanism applies.

### Evidence-to-mechanism translation

Show how evidence and theory constrain the behavioral model:

```text
claim or theoretical mechanism
    -> modeled institutional or cognitive implication
    -> information, state, authority, or choice constraint
    -> observable decision or process implication
```

Distinguish event fact, general theory, estimate, analogy, modeling assumption, structural uncertainty, and
known outcome. State which part of the Definition would change if a claim were withdrawn or reclassified.

## 4. Institutional role and relationships

Describe the participant's position in the event system.

Include:

- mandate, duties, objectives, and non-overridable obligations;
- governance and authorization interfaces;
- actions the participant may initiate, recommend, approve, communicate, or refuse;
- material prohibitions and jurisdiction limits;
- resources the participant owns, controls, observes, requests, recommends, or can only influence;
- formal and informal relationships with other participants; and
- communication, representation, delegation, and intermediation channels.

Keep actual membership, relationship state, resource quantities, and event-time feasibility in the
scenario/environment. This module explains how those facts matter to the participant's choices.

## 5. Decision situations, information, and state

### Activation and decision situations

List the events or state changes that create a decision occasion. A historical date or a global crisis label is
insufficient unless it becomes available to the participant through a specified observation.

### Information available to the participant

Begin with one compact inventory row for every behaviorally material
observation. Use stable reader-facing semantic identifiers; detailed historical
or institutional explanation may follow in prose or role-specific subsections.

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `<observation_id>` | `<historical and institutional meaning>` | `<producer, route, event time, delivery and visibility>` | `<type/category/unit, uncertainty, stale/disputed/missing rule>` | `<Decision Commitment IDs or explicit contextual label>` |

The inventory is a semantic index, not a wire schema. It should make clear who
produced the information, how and when the participant obtained it, its
permissible users, relevant granularity or uncertainty, and the response to
absent, delayed, disputed, incomplete, or superseded information.

List information that the Agent is explicitly forbidden to use, especially hidden world state, undelivered
messages, other participants' private processes, future outcomes, and evaluation evidence.

### Institutional process state and participant decision state

Separate:

- authoritative world, relationship, request, review, authorization, commitment, and result state;
- declared participant decision state, such as a qualitative assessment or last-consumed record reference; and
- transient reasoning that does not persist across decision occasions.

For each persistent item, identify its owner, initial condition, legitimate update event, duration, visibility,
and behavioral consequence. A persistent state that influences later choices must be versioned and replayable.
The Agent may observe or propose changes to institutional process state; it does not create a second private
copy of that truth.

## 6. Behavioral model

### Decision procedure and determinacy

Describe how the Agent moves from a decision situation to an intent. Make the order of checks visible: receipt,
information, authority, duties, existing commitments, feasible alternatives, precedence, response, and later
result handling as applicable.

State how tightly behavior is determined. A historically underdetermined Definition may permit several
responses, but it must still define:

- the minimum response class for each activated situation;
- how competing duties or mechanisms are ordered;
- when a response must change after new information or state;
- the conditions under which delay or abstention is justified; and
- the remaining choice available to different conforming implementations.

A policy is non-degenerate only when an Agent cannot remain conforming by indefinitely waiting or abstaining in
every activated situation. Where the evidence supports multiple choices, constrain the admissible set and its
selection basis rather than inventing a precise historical threshold.

When a strong response rule is calibrated to an already known event action, label it as an **exposed,
event-specific calibration hypothesis**. Explain what the rule helps reconstruct, which inputs change its
response, and why reproducing the exposed action is not independent validation or a reusable participant law.

### Model invariants

List the information, authority, state, intent, and result boundaries that every implementation must obey.
Keep these invariants distinct from behavioral hypotheses: violating an invariant indicates an inconsistent
implementation; falsifying a behavioral hypothesis calls for revising the participant model.

### Behavioral mechanisms

For each central mechanism, explain:

- the historical or theoretical basis;
- the causal pathway from information and institutional position to choice;
- interaction with other mechanisms and precedence;
- an important competing explanation; and
- an observation that would narrow or remove the mechanism.

Mechanisms should express substantive behavioral claims rather than paraphrase implementation branches.

### Decision Commitments

Use Decision Commitments as the smallest auditable units of the behavioral model.

#### `DC-<ROLE>-<N>` — `<decision situation>`

| Element | Required account |
|---|---|
| Situation | Activation conditions, scope, and non-applicable cases. |
| Claim and theory basis | Supporting, bounding, motivating, and contradicting claims. |
| Available information and state | The observations and persistent state that may influence this decision. |
| Alternatives | Institutionally permitted actions, messages, information requests, escalation, delay, and abstention. |
| Behavioral hypothesis | The provisional mechanism and the difference it predicts. |
| Permitted intents | The bounded output set for this situation. |
| Minimum response | The response class required once the situation is activated. |
| Precedence | How prohibitions, duties, prior commitments, resources, and goals resolve conflicts. |
| Abstention boundary | The specific blockers that justify no substantive intent and the event that reopens the decision. |
| Expected and forbidden pattern | What should and should not appear in the modeled process. |
| Falsifier | Evidence, perturbation, or process pattern that would overturn or narrow the commitment. |
| Consumer and deletion test | Who uses the commitment and what becomes ambiguous if it is removed. |

Decision Commitments may permit more than one intent. They must still exclude irrelevant responses, prescribe a
minimum action where the model claims one is required, and make repeated abstention inspectable.

## 7. Intent and result boundary

Define the participant's domain-level action and communication repertoire. Use
reader-facing labels and stable semantic identifiers. Begin with a compact
inventory that closes the link from Decision Commitments to the event
environment.

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `<intent_id>` | `<what the participant is trying to do>` | `<eligible target/scope>` | `<content, quantity/category, duplicate/expiry/cancellation semantics>` | `<Decision Commitment IDs>` | `<delivery, admissibility, execution or effect the Agent cannot declare>` |

The inventory is a semantic index, not a serialization contract. For every
intent, the surrounding text should describe:

- historical and institutional meaning;
- target or recipient;
- required content, quantities, categories, or relations;
- authority and decision situations that permit it;
- lifecycle, duplication, expiry, cancellation, and follow-up semantics; and
- the realized outcome the Agent is not entitled to declare.

The event environment determines delivery, admissibility, feasibility, scheduling, execution, partial effect,
failure, and result. Invalid, unauthorized, duplicate, and out-of-domain attempts remain visible for review
rather than being silently rewritten into valid actions.

## 8. Operationalization and uncertainty

Explain how qualitative concepts become inspectable model variables or procedures. Use equations, thresholds,
state transitions, decision tables, ordered categories, intervals, or alternative structures when they add
behavioral meaning.

For each parameter or construct, record its definition, unit or category, admissible range, source class,
identification status, behavioral role, and sensitivity interpretation. Preserve distinctions among:

- evidence uncertainty;
- uncertain event state or parameter values;
- the participant's own uncertain assessment;
- uncertainty about the behavioral mechanism; and
- uncertainty about the participant's organizational granularity.

Unknown, qualitative, and interval-valued representations are valid outcomes of historical research. Numerical
precision should reflect evidence rather than formatting convention.

For structural alternatives, state their shared evidence-backed boundaries once, then isolate the unresolved
dimension. Identify one conservative baseline and any sensitivity variant explicitly. A baseline that declines
to invent an unsupported authority or capacity must be described as absence of an evidenced route—not as proof
of categorical prohibition. Neither baseline nor sensitivity variant is historically validated merely by
matching an exposed outcome.

## 9. Worked cases and falsification

Include enough contrasting cases to exercise normal operation, stress, missing information, pending state,
authority limits, and adverse results where relevant. Use a consistent case format:

- **Evidence class:** observed, reconstructed, illustrative, counterfactual, or structural sensitivity;
- **Decision-time situation:** only information available within the stated boundary;
- **Required response:** minimum response, remaining admissible choices, and prohibited behavior;
- **Environment boundary:** delivery, authority, feasibility, execution, and result facts outside the Agent; and
- **Perturbation:** one controlled change and the process difference it should produce.

Add cross-case tests for name erasure, role or authority swaps, information removal, future-fact injection,
persistent-state replay, invalid intents, intent/result separation, mechanism ablation, aggregation changes, and
the always-abstain policy. Recompute all quantitative examples independently.

## 10. Limitations, references, and provenance

State the model's unresolved evidence, aggregation losses, unmodeled actors and procedures, exposed outcomes,
parameter limits, external-validity boundary, and structural alternatives. Give concrete withdrawal or revision
conditions for the participant boundary and central mechanisms.

Provide a conventional bibliography and a concise version history. Record what changed in the behavioral model
and why. Project records may separately maintain file identities, derived implementation mappings, review
results, and release status.

### Promotion review

Before treating a Definition as the current scholarly candidate, confirm that:

1. an independent reader can identify the participant, represented decision interface, and aggregation losses;
2. each material behavioral claim has an evidence, theory, estimate, analogy, or explicit-assumption basis;
3. each activated Decision Commitment has a minimum response and a bounded abstention rule;
4. every material observation and persistent state has a single owner and a behavioral consumer;
5. institutional authority and resource control, rather than historical names or generic traits, explain role
   differences;
6. all outputs are intents or messages, while delivery and realized results remain environment-owned;
7. worked cases exercise the actual model and produce different paths under meaningful perturbations;
8. structural unknowns remain visible instead of being converted into arbitrary probabilities;
9. strong rules fitted to exposed actions are labeled as event-specific calibration hypotheses;
10. structural variants distinguish shared fixed boundaries, conservative baseline, and sensitivity use;
11. the Definition contains no hidden future outcome or evaluation evidence; and
12. the document's scope claims match what the evidence and participant set can support.

Executable mappings are derived from a reviewed Definition. They should preserve its identity, information
boundary, state ownership, Decision Commitment inventory, intent semantics, and uncertainty choices without
becoming a competing account of participant behavior.
