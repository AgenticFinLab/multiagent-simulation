---
name: h2epr-event-scenario-design
description: Design or revise a publication-facing H2EPR Event Scenario Definition from an accepted event roster, semantic release, evidence boundary, and participant models. Use when event time, world state, institutions, relationships, resources, information delivery, lifecycles, adjudication, structural variants, or termination must be specified before policy implementation; do not use to write Agent behavior, machine schemas, or run a simulation.
---

# Event Scenario design

> Method status: working candidate. Revise it only from observed use in a real
> event scenario, not from speculative pipeline expansion.

Use this Skill after the event's research question and participant
dispositions are accepted. It turns the event semantic skeleton and released
participant semantics into one coherent Scenario Definition without writing
policy code or forcing the known historical outcome.

Read the public
[Scenario Definition Template](../../scenarios/scenario-definition-template.md),
the derived
[Scenario interface closure template](../../scenarios/scenario-interface-closure-template.md),
the accepted event roster and semantic skeleton, the evidence ledger, the
relevant Agent/population products, and any accepted consolidated mapping.
Read [scenario review](references/scenario-review.md) before issuing a review
verdict.

## Required inputs

Confirm:

- event identity, research questions, modeled interval, and roster version;
- the exact semantic release or accepted participant-product set;
- evidence ledger, exposure boundary, unresolved claims, and source
  permissions;
- semantic skeleton and accepted structural/exogenous decisions;
- participant observations, intents, authority, resource, and lifecycle
  requirements;
- applicable machine-contract and mapping versions, when they exist;
- candidate location, version policy, review audience, and stopping point; and
- whether the task permits evidence research, implementation, simulation, or
  only Scenario Definition work.

If a participant or causal owner is still undecided, return to the roster or
representation gate. Do not settle an autonomous-choice question by hiding it
inside the environment.

Use **create mode** when no Scenario Definition exists. Use **revise mode** for
an existing candidate: identify the semantic delta, affected evidence and
participant interfaces, version consequence, and downstream consumers before
editing. A revision must not silently replace a pinned release or accepted
mapping input.

## Workflow

### 1. Fix the event boundary

State the causal question, interval, temporal resolution, endogenous
processes, initial conditions, exogenous inputs, excluded processes, exposed
outcomes, and claims the scenario can and cannot support.

Use chronology to constrain opportunity and information. Do not use the known
sequence as an event script or success criterion.

### 2. Pin semantic inputs

Record the roster/release, Definition and population identities, skeleton,
evidence boundary, and accepted owner decisions consumed by the candidate.
Reference these authorities instead of copying them.

Derive the expected product, capability, observation, intent, and lifecycle
counts from the pinned release and mapping. These counts seed the interface
closure record; do not transcribe them into an unaudited narrative total.

When no formal release exists, state the exact reviewed input set and keep the
candidate mutable. Do not describe an unpinned collection as a released
scenario.

### 3. Build a causal-ownership map

For each material choice or transition, assign one owner:

- participant Definition or population model for decision semantics;
- scenario/environment for world facts, relationships, resources, routing,
  delivery, institutional procedures, feasibility, and effects;
- evidence ledger for claim status and participant-time admissibility;
- machine contracts for representation and serialization; and
- reducer for authoritative state transition.

Challenge any state or rule represented in two places. A coordinator does not
own contributors, a committee does not own member resources, and a venue does
not become an Agent merely because it changes results.

### 4. Specify time and exogenous inputs

Define event clock, phase entry/exit conditions, within-time ordering,
decision occasions, expiry, and the delivery time of exogenous inputs. Phase
changes must follow inspectable state or events rather than a hidden historical
date switch.

An exogenous input needs an evidence or approved-assumption basis, a state
effect, visibility rule, causal limit, and sensitivity disposition.

### 5. Specify authoritative world state

Inventory only state needed by the research questions and released behavior:
institutions, relationships, requests/cases, resources, operational access,
procedures, venue state, and results.

For each state family define owner, initial basis, valid transition causes,
visibility, invariants, and conservation or exclusivity rules. Keep
participant decision state separate from business truth.

### 6. Specify information production and delivery

Trace each behaviorally material observation from authoritative source record
through production, projection, route, delivery, freshness, dispute, and
participant scope. Define missing and stale behavior without inventing hidden
defaults.

Reject designs where an actor can dereference a current world object, see an
undelivered message, or consume a future/evaluation fact.

### 7. Specify interactions and business lifecycles

Define stable business-object identities and lifecycle states for requests,
cases, reviews, authorizations, messages, notices, proposals, commitments,
resources, market/funding objects, and results as needed.

Separate intent, transport, receipt, admissibility, scheduling, execution,
partial effect, failure, result, and later observation. Define duplicate,
expiry, cancellation, concurrency, cross-hop lineage, and reopening rules.

### 8. Specify adjudication and results

For each intent family, state the authority, target, relationship, resource,
prestate, feasibility, and competing-claim checks. Define typed dispositions
and results. Preserve invalid and unsuccessful attempts rather than repairing
them silently.

The environment may reject an Agent's believed-feasible intent. It may not
alter the intent to reproduce the historical outcome.

### 9. Define operationalization and variants

Use qualitative domains, intervals, procedures, equations, or parameters in
proportion to the evidence. Record source class and identification status for
every material scenario input.

Keep structural uncertainty separate from parameter uncertainty. Pin the
chosen structural variant in scenario/run identity and state the evidence that
would retire it.

Define normal termination, incomplete termination, invariant failure, pending
object treatment, and seal/evaluation eligibility.

### 10. Close the released interface, pressure-test, and review

Complete the derived Scenario interface closure after the scenario semantics
are stable. Reconcile every released observation placement with a source,
projection, route, time rule, and scenario concept; reconcile every released
intent placement with authority, target, lifecycle, adjudication, result, and
scenario concept. Close participant assembly, private/business state,
relationships, resources, structural identity, and replay at the same time.

A gap remains a gap even when a likely implementation carrier exists. Route it
to the owning Definition, scenario, mapping, evidence, or contract boundary
rather than filling it locally.

Write high-information cases spanning ordinary behavior, missing or stale
information, authority failure, duplicates, partial/adverse results,
cross-resource conflicts, and structural alternatives as relevant.

Apply the linked review rubric in a separate review pass that does not rely on
private authoring notes, policy code, or simulation output. Prefer a different
reviewer or a clean review context when available. Route findings to evidence,
roster, Definition, scenario, mapping, implementation, or contracts according
to ownership. Do not broaden the candidate to fix a problem outside its
research question.

## Outputs

A complete design run produces:

1. one versioned Event Scenario Definition candidate using the ten-module
   template;
2. one derived Scenario interface-closure record reconciled to the exact
   participant release and accepted mapping;
3. explicit causal-ownership, state, relationship/resource, information,
   lifecycle, adjudication, variant, termination, and reproducibility accounts;
4. high-information worked cases and event-level falsifiers;
5. a separate substantive scenario-review report and revision routing; and
6. a concise list of implementation prerequisites and unresolved owner or
   evidence decisions.

The candidate is a semantic design. It does not itself create a configuration,
ParticipantArtifact, policy, reducer, trace, or simulation result.

## Stop conditions

Stop and request direction when:

- the event question, horizon, roster, or causal owner would change;
- a required participant choice is absent from the accepted semantic input;
- a material event claim requires unauthorized source or held-out access;
- the scenario would need a known later outcome as an earlier input or rule;
- two authorities would own the same state, relationship, resource, or result;
- an unresolved structural mechanism is being replaced by an arbitrary number;
- the current carrier has a concrete irreducible loss requiring separate
  successor review; or
- implementation, simulation, contract change, or evaluation is outside the
  authorized task.
