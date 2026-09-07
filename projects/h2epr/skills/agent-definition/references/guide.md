# Agent Definition method guide

## Purpose

An Agent Definition is the accepted, human-readable semantic authority for one
named decision interface. It explains who is represented, what the interface
may know and remember, what it may request or communicate, and what evidence
would show that the representation is wrong.

It is upstream of registries, backend realization, and run artifacts. Those
products may project or select within the Definition; they may not widen it.
The Definition does not select thresholds, prompts, decoding settings,
priorities, timing constants, successful trajectories, or world outcomes.

## Required product

Use the maintained ten-module
[Agent Definition template](../../../agents/agent-definition-template.md)
without renaming or reordering its modules. Replace every prompt with
event-specific content. Empty prose such as “not applicable” is acceptable
only when it explains why the field is structurally inapplicable.

The product must be:

- bounded to one accepted roster disposition and one event;
- traceable to the admitted benchmark package;
- explicit enough to project into the selected implemented backend and to
  review future backend equivalence without implying those backends exist;
- explicit about environment and configuration ownership;
- falsifiable through concrete cases; and
- publishable as the sole current Definition for that Agent.

## Reading routes

| Authoring question | Required reference |
|---|---|
| Is this participant really an Agent, and what does it represent? | [Representation and authority](representation-and-authority.md) |
| Is this statement supported, assumed, generated, or selected later? | [Dataset provenance and exposure](dataset-provenance-and-exposure.md) |
| What can the Agent see, retain, forget, or use on reconsideration? | [Observations and state](observations-and-state.md) |
| How do I constrain choices without encoding Rule or LLM policy? | [Decision commitments and intents](decision-commitments-and-intents.md) |
| Which cases are needed, and what counts as a falsifier? | [Worked cases and falsification](worked-cases-and-falsification.md) |
| What must be checked and recorded before acceptance? | [Publication and completion](publication-and-completion.md) |
| What does a filled, event-neutral Definition look like? | [Complete synthetic example](complete-synthetic-example.md) |
| Which attractive shortcuts make a Definition invalid? | [Annotated failure example](annotated-failure-example.md) |

## Authority stack

Resolve conflicts by ownership. Admitted bytes, exposure rules, Source Profile,
and roster constrain the candidate. The Definition owns participant meaning;
registries project that meaning and own exact executable identifiers. Scenario
owns world state, routes, feasibility, and effects. Configuration selects
values and backend realization selects options. Run observations describe what
happened under those parents.

An existing registry does not override a conflicting participant contract, and
prose cannot silently add a new identifier or world capability. Return the
mismatch to the affected owners and review their candidates together. During
initial authoring, a proposed vocabulary can be coordinated with the Scenario
candidate; executable acceptance waits for the final parent set and projection.
Pin that set in the external review record after the candidate bytes settle.

## Core ownership test

For each sentence, ask who could change it:

- If changing benchmark input changes the statement, it is dataset-bound.
- If changing the modeled world changes it, scenario owns it.
- If changing an allowed value changes it, configuration owns it.
- If changing how an admissible option is selected changes it, backend owns it.
- If changing a delivered result changes it, runtime or generated evidence
  owns it.
- If it defines the participant's stable choice boundary across those changes,
  the Agent Definition owns it.

This test is stronger than choosing ownership by document convenience.

## Minimal authoring sequence

1. Establish identity and representation before describing behavior.
2. Build the provenance ledger before turning claims into prose.
3. Define observable information and persistent state before choice sets.
4. Write one decision commitment at a time.
5. Project commitments into typed intents and environment-owned results.
6. Separate open configuration dimensions from semantic invariants.
7. Try to break the Definition with worked cases.
8. Complete the publication record and hand off to independent review.

## Failure routing

Do not patch a Definition around an upstream defect.

| Finding | Destination |
|---|---|
| missing or duplicate participant disposition | roster |
| population or aggregate response unit | Population Model |
| missing world state, route, feasibility, or effect | Scenario Definition or Mechanism |
| undefined shared observation or intent vocabulary | participant semantic registry |
| exact threshold, window, priority, or retry count | configuration |
| option selection, prompt, or fallback algorithm | backend realization |
| delivery, admission, execution, or result | runtime/environment |
| protected input or future information | exposure failure; stop |

## Completion evidence

Completion requires the current template revision, semantic parent and Agent
IDs, source participant IDs, anchor and assumption ledgers, named decision
commitments, intent/result mappings, adversarial cases, limitations, successor
conditions, validation results, reviewer disposition, and content identity.
Acceptance means the event-wide interface can project the Definition without
loss or widening. It does not mean that a backend or run succeeds.
