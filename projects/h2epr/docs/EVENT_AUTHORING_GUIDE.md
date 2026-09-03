# Event authoring guide

## Purpose

This guide turns a selected H2EPR event into reviewable semantic assets. It
does not authorize external research, protected inputs, simulation, or
scientific evaluation. The thin sequence is in
[NEW_EVENT_PLAYBOOK.md](../NEW_EVENT_PLAYBOOK.md); this document explains the
judgment required at each handoff.

## 1. Freeze the input boundary

Receive an exact event ID. Resolve the three permitted paths directly and
check public identity, JSON shape, size, and SHA-256. Record exposure before
reading for semantics. A full-Draft-exposed event is suitable for construction
and descriptive analysis; it is not a clean prediction task.

The Source Profile must state:

- what the dataset makes available;
- what is explicitly prohibited;
- shape defects or identifier gaps that remain source facts;
- transformations or aggregation that construction will perform; and
- the strongest permitted and prohibited claims.

Stop if the requested event cannot be identified without protected-directory
discovery, if any permitted byte drifts, or if a source conflict would need an
unrecorded repair.

## 2. Build a loss-accounted roster

Walk every Draft stage and episode. Preserve occurrence order, exact observed
names, types, roles, and stable anchors. Then choose one disposition per source
participant:

| Disposition | Use when |
|---|---|
| named Agent | a person, office, organization, or institution has an autonomous choice boundary |
| Population | a group has a meaningful aggregate or heterogeneous choice boundary |
| initial context | the item only establishes opening conditions |
| world state | the item carries state but no modeled choice |
| institutional process | the item is a rule-governed process after an initiating choice |
| outside window | the item is deliberately excluded by the simulation interval |
| unresolved defect | the dataset does not support a defensible mapping |

Historical importance does not by itself justify an Agent. A publication
decision can be an Agent boundary while the post-publication announcement,
delivery, enforcement, and observable effects remain scenario processes.
Record every many-to-one mapping and information loss.

## 3. Define decision units

Write one Definition or Population Model for every active runtime actor. Start
from decision situations: what activates a choice, what the unit can observe,
what it controls, which typed intents are admissible, and which results remain
environment-owned.

Keep constructs separate from selected values. For example, a Definition may
state that response delay is configurable and bounded; shared or backend
configuration selects a value. This avoids the MASim AgentDefinition pattern
in which large behavior and parameter bundles become permanent identity.

Each parent must include:

- exact Draft anchors and any frozen-evidence anchors used;
- included and excluded internal actors;
- persistent versus transient state;
- missing, stale, pending, rejected, and adverse-result behavior;
- meaningful perturbations and a falsification condition;
- representation losses and a successor trigger.

## 4. Close the shared participant language

Build registries from accepted semantic parents, not from Rule code. Every
active actor appears once in the participant interface and semantic index.
Every intent has matching eligible actors in the interface and one matching
mechanism handler. Every observation names its producer, consumers,
availability, visibility, and missing behavior. Every lifecycle names state,
owner, and trigger.

Useful review probes:

- erase display names and check whether authority still follows IDs and roles;
- swap two actor rows and confirm closure fails;
- inject a later Draft fact into an earlier observation and confirm review
  rejects it;
- remove one semantic-parent anchor and confirm compiler admission fails;
- add an intent to a backend only and confirm interface parity fails.

## 5. Define the event world

The Scenario Definition explains the endogenous window, opening context,
clock, institutions, resources, routes, state ownership, concurrency,
failures, annotations, and termination. Its mechanism projection must be
deterministic for a fixed admitted batch.

For every state field, define type, domain, visibility, and update authority.
For every intent handler, define parameter domains, target domain,
preconditions, and effects. Messages do not mutate state directly. A route
controls delivery; the recipient's later decision and the environment's
admission control effects.

All actors at one coordinate decide against the same sealed prestate. Distinct
concurrent values for one field are rejected without partial effects;
idempotent same-value writes are admitted under semantic ordering. Add a final
logical coordinate when needed to drain one-tick transport before termination.

## 6. Select executable values

Shared configuration covers the complete mechanism field universe and ordered
Draft stage/episode coordinates. Every route is explicit. Every top-level
setting has provenance or a reviewed bounded-unavailability exemption.

Rule configuration should be the smallest deterministic construction baseline
supported by the exposed Draft. A row states actor, coordinate, priority,
guards, typed action, messages, and reason. It must exercise every non-`no_op`
intent at least once. Missing rows produce a typed `no_op`; they must not invoke
hidden defaults.

## 7. Review before execution

Compilation must rederive roster semantics, source gaps, actor closure,
semantic-parent anchors, registry/mechanism closure, state domains, timeline,
routes, configuration receipts, implementation hashes, and backend parity.
Compile twice into fresh temporary directories and compare every byte.

Only after this passes may the event advance to
[RUN_AND_RELEASE_GUIDE.md](RUN_AND_RELEASE_GUIDE.md). Do not add a row to the
current-event registry at semantic completion alone.
