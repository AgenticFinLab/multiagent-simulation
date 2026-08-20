# Behavioral contract and interfaces

The Agent Definition must be precise enough to constrain independent backends
without freezing one implementation algorithm.

## Common behavioral framework

State the participant's recurring decision logic in domain terms:

1. identify the relevant decision situation;
2. determine which information is available to the participant and sufficiently fresh;
3. inspect legitimate persistent state;
4. enforce jurisdiction, authority, duties, and procedural preconditions;
5. identify institutionally permitted alternatives;
6. apply mechanism-specific precedence or choice logic;
7. seek information, delay, escalate, abstain, or emit an intent;
8. update behavior only after legitimate observations or delivered results.

The Definition need not impose one cognitive architecture, utility function,
or exact policy on all backends. It must establish a shared conformance
envelope and the provisional behavior hypotheses being tested.

## Hard obligations and behavioral hypotheses

### Hard conformance obligation

A boundary every backend must obey, such as:

- no future or hidden information;
- no action outside the represented authority;
- no self-declared result;
- no invisible persistent state;
- declared missing-information behavior;
- only the documented intent repertoire;
- invalid or unauthorized attempts remain auditable.

A violation means the implementation is nonconformant; it does not test the
historical behavioral hypothesis.

### Falsifiable behavioral hypothesis

A provisional scientific claim, such as:

- an unresolved request suppresses an equivalent duplicate request;
- institutional eligibility changes the response category;
- incomplete authorization produces information seeking, procedural delay, or
  abstention;
- a delivered adverse result changes subsequent operating posture.

A failed hypothesis means the participant model may need revision even when
the backend obeyed every hard boundary.

## Decision Commitment content

Each Decision Commitment should cover:

| Element | Required meaning |
|---|---|
| Decision situation | Historical or modeled condition and its scope. |
| Claim and theory basis | Evidence, mechanism, assumption, and competing proposition. |
| Participant-available observations | Information the participant may use, including missing/freshness semantics. |
| Relevant private state | Persistent participant state and legitimate update source. |
| Authority and procedure | Jurisdiction, duties, approval, and prohibition. |
| Alternatives | Institutionally permitted actions, communications, information requests, delay, escalation, and abstention. |
| Precedence | How hard constraints, duties, commitments, resources, and goals resolve conflict. |
| Intent envelope | Domain-level outputs permitted in this situation. |
| Minimum response | The response class required once the situation is activated. |
| Abstention boundary | Specific blockers that justify no substantive intent and the event that reopens the decision. |
| Process prediction | Expected and forbidden sequence or behavior. |
| Falsifier | Evidence or perturbation that rejects or narrows the claim. |

Write commitments at the level of meaningful behavioral propositions. Avoid
one commitment per code branch, enum value, or test.

## Selection sufficiency

A bounded intent set is not yet a behavioral policy. For every activated
Decision Commitment, state:

1. the minimum response class that must occur;
2. the constraints and precedence that remove alternatives;
3. the basis on which a conforming implementation may choose among remaining
   alternatives;
4. the exact blockers that justify delay or abstention; and
5. the information, state, or delivered result that must change the response
   class.

Use a constrained set-valued policy when the evidence does not identify one
historical action. This preserves legitimate underdetermination while ruling
out a degenerate implementation that waits or abstains in every case. If the
evidence supports no choice rule beyond the hard boundary, label that limit
instead of inventing a threshold or random gate.

## Exposed calibration hypotheses

A strong response rule may be useful when reconstructing an action already
known to have occurred. Label it as an exposed, event-specific calibration
hypothesis and record:

- the complete gate conditions;
- which conditions are observed facts, estimates, or construction assumptions;
- the different response required when a gate is removed;
- the scope in which the rule applies; and
- the validation and generalization claims it cannot support.

The known action can anchor construction and lifecycle analysis. It cannot
independently validate the behavior that was calibrated to reproduce it.

## Structural alternatives

When evidence leaves a mechanism or authority unresolved:

1. state the shared evidence-backed boundary outside the fork;
2. identify the unresolved structural dimension;
3. choose and label a conservative baseline;
4. retain a second variant only when it produces a meaningful sensitivity
   comparison;
5. select one variant before behavior begins; and
6. identify evidence that would narrow or retire each variant.

A conservative baseline may refuse to invent an unsupported route or capacity.
Describe that as `no evidenced route` rather than as a proven prohibition unless
direct evidence establishes the prohibition.

## Observation semantics

For each behaviorally material observation, state:

- domain concept;
- source or sender;
- historical availability and participant visibility;
- granularity and uncertainty;
- type, unit, ordering, or category where useful;
- permitted domain and impossible combinations;
- freshness, delay, and missing behavior;
- mechanisms and commitments that consume it;
- whether the participant observes world truth or a fallible projection.

Context that influences no current behavior can remain scenario description.
Do not bind decorative inputs merely to make the interface look complete.

## Private state semantics

Persistent private state is justified when a later choice depends on prior
information or action, such as:

- pending or previously attempted request;
- review or authorization stage;
- previously delivered result;
- commitment or resource reservation;
- last verified information time;
- operating posture;
- qualitative assessment formed from participant-available observations.

State the initial condition, legitimate transition trigger, persistence, owner,
visibility, and behavioral consequence. A Rule object or LLM memory cannot
silently invent or retain additional behaviorally material state.

## Intent semantics

For each domain-level action or message intent, explain:

- name and meaning in historical/institutional terms;
- actor authority and decision situations that permit it;
- recipient or target;
- required content, amount, category, or relation;
- units, range, ordering, or controlled vocabulary where meaningful;
- request/message lifecycle, expiry, cancellation, and duplication semantics;
- environment-owned admissibility, feasibility, and possible results;
- effects the Agent is prohibited from declaring.

Do not reduce institutional requests, examinations, authorizations,
communications, refusals, or coordination to `buy`, `sell`, or `hold` merely
because the carrier framework originated in financial-market simulation.

## Backend-neutral conformance

Rule and future LLM backends should share:

- the same Definition and scenario identity;
- the same information content and forbidden knowledge;
- the same persistent-state semantics;
- the same authority and hard obligations;
- the same domain intent repertoire;
- the same environment and result semantics;
- the same evidence-use and exposure boundary;
- traceable links from decisions to commitments and observations.

They may differ in internal search, reasoning, heuristics, representation,
controlled randomness, and selection among multiple permitted intents. Optional
rationale may aid audit but is not evidence of historical cognition.

## Boundary checks

- **Information completeness:** every behaviorally material external input is
  declared.
- **No hidden state:** every persistent behavioral state is declared.
- **Authority:** goals cannot override jurisdiction or procedure.
- **Intent/result:** attempts cannot submit or announce world effects.
- **Missing information:** unknown and stale values invoke declared behavior.
- **Lifecycle:** sent, delivered, pending, resolved, partial, failed, expired,
  and cancelled are not collapsed where the distinction affects behavior.
- **Invalid attempts:** adapters must not silently clamp or repair violations.
- **Backend parity:** no backend receives extra history, knowledge, memory, or
  actions.
