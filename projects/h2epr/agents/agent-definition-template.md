# H2EPR Agent Definition Template

> Status: `MUTABLE_PILOT_HYPOTHESIS / NON_SCHEMA / EVENT_BOUND`

Use this template to create the smallest auditable behavioral contract for one
participant in one bounded event situation. It is not a fixed section schema,
cross-event archetype, runtime interface, or implementation authorization.

## 1. Event and representation boundary

State the event, decision time, and question. Identify the institutional
decision interface represented by the Agent, who is aggregated or excluded,
what the Agent does not explain, and what observation would require a finer
Agent granularity.

Deletion test: without this boundary, can a reviewer still tell who is
authorized to form an intent? If not, it is mandatory.

## 2. Institutional position, authority, and resources

Record only behaviorally material semantics:

- mandate or obligation affecting the current choice;
- authority to propose, request, review, refer, decline, or abstain;
- non-overridable procedure or eligibility constraints;
- whether each resource is observed, controlled, requested, recommended, or
  committed;
- unresolved authority or procedure as explicit structural uncertainty.

Actual membership, relationships, resource values, and feasibility belong to
the scenario/environment.

## 3. Epistemic and persistent-state boundary

For each material observation, specify its meaning, visibility, delivery or
availability time, freshness, missing/stale behavior, and claim or scenario
reference. List forbidden information, especially future outcomes, hidden
world state, another institution's private procedure, and undelivered messages.

At an executable pilot boundary, every bound observation field must appear
with either a value or an explicit missing/stale/unknown/not-delivered marker.
An absent key must not be silently interpreted as a known value or backend
default.

List only persistent state that changes a later decision. Distinguish:

- environment-owned business or institutional truth observed by the Agent;
- decision state whose semantics are declared here but whose updates must use
  an authoritative, sealed, replayable path;
- one-call ephemeral reasoning, which may remain backend-private.

No behaviorally material memory may exist only inside a Rule object or future
LLM context. Numeric beliefs are optional and require evidence or a specific
research need.

## 4. Decision Commitments

Start with two or three high-information decision situations. Each commitment
must be a meaningful, falsifiable behavioral claim, not a line-by-line copy of
code.

### `DC-<ROLE>-<N>` — `<decision situation>`

| Item | Required question |
|---|---|
| activation | What situation is covered, and when is it not applicable? |
| claim basis | Which claim IDs support, bound, motivate, or contradict it? |
| legal observations | Which delivered inputs may influence this decision? |
| relevant state | Which persistent state is read, and who owns its truth? |
| hard conformance obligations | What must every backend obey? |
| falsifiable behavioral hypothesis | Which provisional mechanism may be wrong? |
| precedence | Which information, authority, or procedure constraint wins conflicts? |
| intent envelope | Which semantic intents are permitted? |
| fallback / abstention | What happens when information or authority is missing? |
| trace implication | What must or must never appear in an auditable run? |
| falsifier | Which evidence, perturbation, or trace pattern would overturn it? |
| consumer / deletion test | Who uses it, and what breaks if it is removed? |

Separate hard obligations from behavioral hypotheses. A hard-obligation
failure means a backend or adapter is non-conformant; a hypothesis failure
means the candidate scientific model needs revision. Permit multiple compliant
intents unless evidence genuinely fixes one.

## 5. Intent and environment boundary

Define only the minimum semantic intents needed by the commitments, including
their target, lifecycle, prerequisites, and prohibited self-realized outcome.
The environment/reducer decides whether an intent is admissible, scheduled,
executed, partial, delayed, ineffective, failed, or prohibited, and is the only
authority that commits world or business-process state.

Invalid, unauthorized, duplicate, and out-of-envelope attempts must remain
auditable; an adapter must not silently repair them.

## 6. Evidence, assumptions, limitations, and withdrawal

Reference the evidence ledger instead of copying it. Distinguish event fact,
general theory, estimate, analogy, modeling assumption, structural uncertainty,
and exposed outcome. State which commitment changes if a claim is withdrawn.
Previously exposed material cannot become held-out evidence again.

## 7. Minimal review

Before promoting a candidate, perform at least:

1. actor-name erasure;
2. role/authority swap;
3. future-fact injection;
4. missing/stale information;
5. persistent-state replay;
6. invalid-intent visibility;
7. commitment-to-runtime mapping;
8. deletion of every mandatory capability.

Success means an independent reviewer can identify legal information,
authority, permitted intent, fallback, uncertainty, and violations without
reading backend-private logic. It does not establish historical validity or
cross-event reuse.

Any derived executable binding must fail closed when the canonical Markdown
hash, Definition identity/version, Decision Commitment inventory, observation
envelope, or commitment-specific intent mapping drifts.
