# Adversarial and minimality review

Adversarial review asks how the Definition could be wrong, underdetermined, or
decorative. Perform these checks on paper before relying on runtime tests.

## Strongest counterargument

Write the strongest evidence-based objection to:

- the participant boundary;
- the chosen institutional mechanism;
- the information available to the participant;
- the central behavioral mechanism;
- any precise parameter or threshold;
- the claim that the Definition is publication-ready.

State what observation would make the objection stronger and what would answer
it. Avoid a weak straw objection that the current draft can dismiss easily.

## Role and identity perturbations

### Name erasure

Remove historical names and internal IDs while preserving the semantic role,
information, authority, state, and resources. The Definition should imply the
same behavior. A change indicates name-based scripting or narrative anchoring.

### Role or authority swap

Exchange authority, membership, institutional duty, or resource control while
holding other conditions fixed. The institutionally permitted intent envelope and process should
change where the model claims those distinctions matter.

### Representation split and collapse

Test whether splitting an aggregate Agent into internal actors produces a
necessary, evidence-grounded process distinction. Also test whether collapsing
the participant into a scenario protocol loses any real discretionary
behavior. Retain the least complex adequate representation.

## Information perturbations

- remove a required observation;
- make it stale, delayed, coarser, uncertain, or contradictory;
- replace an exact value with the historically supported range;
- inject hidden world state or a future outcome;
- give one backend richer background than another;
- delay message or result delivery.

The Definition should specify changed behavior, fallback, or abstention. It
should reject forbidden information rather than silently use it.

## Degenerate-policy test

Construct an implementation that always waits or abstains whenever more than
one intent is permitted. Then ask, for every activated Decision Commitment:

- which minimum response makes that implementation nonconforming;
- which blocker would make abstention legitimate;
- which reopening event or changed input ends the abstention;
- which precedence rule narrows the remaining alternatives; and
- whether a new information or result class must produce a different response.

If the always-abstain implementation remains conforming, the Definition has an
action catalogue but not a sufficient behavioral policy. Strengthen the
minimum response and selection boundary without inventing a unique action,
historical threshold, or random gate unsupported by evidence.

## State and lifecycle perturbations

Place requests, reviews, commitments, or results in different states:

- absent;
- initiated but not delivered;
- delivered and pending;
- waiting for information or authorization;
- denied or prohibited;
- scheduled or delayed;
- partial or no effect;
- failed, expired, cancelled, or realized.

Check whether later behavior distinguishes the states when it should. Repeated
requests and unexplained forgetting often reveal missing persistent state.

## Mechanism alternatives and ablation

- remove one central mechanism;
- replace it with the strongest competing explanation;
- remove a claimed parameter;
- turn a hard rule into discretion or vice versa;
- remove a procedure and leave only a generic preference;
- reverse a precedence relation;
- withdraw one supporting evidence claim.

Prestate the process pattern expected to change. If nothing changes, the
mechanism may be decorative or the falsification surface may be inadequate.

## Intent and result adversaries

Construct cases in which:

- an authorized intent is institutionally inadmissible;
- an admissible intent is infeasible;
- execution is partial, delayed, failed, or without effect;
- a duplicate or expired request is submitted;
- a participant attempts an unauthorized action;
- an action parameter is missing or outside its meaningful domain;
- a message is created but not delivered.

The participant must not claim a realized outcome, and the model should make
the later delivered result behaviorally meaningful.

## Minimality and consumer checks

For each major observation, state, mechanism, parameter, intent, table, or
mandatory section, ask:

1. Which behavioral decision, prediction, scholarly argument, or review uses
   it?
2. What becomes ambiguous or wrong if it is removed?
3. Does another authority already own the same fact?
4. Is it substantive or included only to resemble a mature template?

Remove decorative semantics, but do not confuse minimality with brevity. A
long historical explanation can be necessary when it establishes governance,
institutional meaning, or a contested mechanism. A compact parameter table can
be decorative when no decision uses it.

## Quantitative checks

- independently recompute all worked examples;
- verify inequality directions and boundary inclusion;
- check units and dimensional consistency;
- distinguish input range from behaviorally plausible range;
- inspect sensitivity near thresholds;
- confirm that missing and unknown are not encoded as zero;
- ensure stochasticity is declared and not used to imitate unmodeled
  institutional procedure.

## Review outcome

For every failed adversarial test, identify whether the revision belongs to:

- evidence research;
- participant representation;
- behavior mechanism research;
- Agent Definition authoring;
- scenario/environment semantics;
- later implementation conformance.

Do not repair a Definition failure by silently moving the behavior into an
adapter or scenario.
