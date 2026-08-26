---
name: h2epr-event-agent-batch
description: Coordinate a risk-proportionate H2EPR participant batch in reference-pilot or Roster-production mode. Use when event rows need shared scope, evidence and behavior routing, coherent promotion, and either an authorized conformance pilot or a lightweight semantic interface review with publication-facing coverage.
---

# Event participant batch

Use this Skill to coordinate repeated role work without merging the roles'
evidence, policy, or review boundaries. It routes work through the specialist
Skills; it does not replace them.

Read the canonical [Agent development workflow](../../agents/WORKFLOW.md), the
accepted event roster, and the event semantic skeleton before opening a batch.

## Choose the mode

Record one mode in `BATCH.md`:

- **Reference pilot:** use only when a new representation, semantic method,
  carrier boundary, or interaction pattern needs end-to-end testing. Mapping
  and conformance require explicit authorization.
- **Roster production:** use for normal event-roster completion. It ends at
  accepted research products, a lightweight semantic interface review, and
  publication-facing coverage in a shared account. Do not map or implement
  each batch.

When the request does not explicitly authorize the reference-pilot engineering
tail, use Roster-production mode.

## Required inputs

Confirm:

- event identity, horizon, research question, roster version, and skeleton
  version;
- admitted roster rows and their causal choices;
- batch mode, production profile per row, and promotion unit;
- local evidence, exposed outcomes, and source permissions;
- the selected template and specialist Skill paths, with any repository commit
  retained only in the local batch record;
- working, evidence, and tracked output locations; and
- the exact stopping point and unresolved owner decisions.

If the question, roster, or skeleton is unresolved, stop at that owner-level
boundary rather than filling it inside a role Definition.

## Run the batch

### 1. Open one brief

Write a concise `BATCH.md` covering roles, interactions, permissions, mode,
promotion unit, stopping conditions, and outputs. Reuse the current mutable
plan and status rather than creating parallel trackers. Keep raw source bytes
in the evidence area.

### 2. Select the route and depth

Use the accepted roster disposition and production profile:

- `disposition-only` closes with an explicit scenario, exogenous, excluded, or
  deferred owner; do not create a participant product;
- a `standard` Agent uses the evidence, behavior, Agent Definition, and review
  methods, but its supporting working records and routine review may be
  combined;
- a `standard` population uses the evidence and behavior methods, the
  [Population model template](../../populations/population-model-template.md),
  its exact ten-module publication structure, and a concise
  profile-proportionate review; and
- `deep` uses the same representation route with fuller separate research or
  review records only where the declared risk requires them.

Evidence and behavior are semantic responsibilities for every admitted Agent
or population, not mandatory filenames. Apply
[`h2epr-historical-evidence-research`](../historical-evidence-research/SKILL.md)
and
[`h2epr-participant-behavior-research`](../participant-behavior-research/SKILL.md)
to the depth required by the row. Invoke
[`h2epr-agent-definition`](../agent-definition/SKILL.md) and
[`h2epr-agent-definition-review`](../agent-definition-review/SKILL.md) only for
an Agent route. A population uses its own ten-module profile rather than the
Agent profile; production depth never changes either public module order.

Share adopted source identity and event claims through the event-owned source
register and participant-evidence record. Keep these shared authorities under
`events/<event>/`; `agents/defines/<event>/` contains only its index and Agent
Definitions. Do not share participant policy, private state, or authority
merely because roles belong to one batch.

A representation-gate row may close as an Agent Definition, a reviewed
population/cohort interface, or an explicit scenario disposition. Do not force
it into an Agent-shaped document.

### 3. Review shared boundaries

Check that:

- every autonomous choice belongs to an admitted Agent or population model;
- rules, delivery, adjudication, and realized effects remain scenario-owned;
- populations are not disguised as institutional personalities;
- cross-role messages, relationships, and time boundaries are compatible;
- no role relies on another role's hidden state or a later outcome; and
- shared Template or Skill changes answer a demonstrated reusable gap.

### 4. Complete the semantic interface review

The working `INTERFACE.md` records only what later integration needs to know:

- representation and causal choices;
- observations and participant-time limits;
- behaviorally material private state;
- intents, counterparties, and routes;
- authority, resource, lifecycle, result, and scenario dependencies;
- skeleton compatibility; and
- `KNOWN_FIT`, `MAPPING_EXTENSION_EXPECTED`, or
  `CONCRETE_CARRIER_COUNTEREXAMPLE` for each material interface family.

In Roster-production mode, stop here. Do not select wire fields, build a
registry, update binding hashes, implement policy, or run replay tests.

This is a working or release-time integration review, not the scholarly
interface account. It may retain exact carrier classifications when a release
needs to pin them.

### 5. Promote accepted products

Promote the accepted Definition or population product with adopted claim and
source updates and corresponding coverage in a publication-facing interface
account. Normally extend one shared batch- or event-level account rather than
creating a public file for each participant. If a release deliberately pins
the working `INTERFACE.md`, retain it unchanged as a release-time review and
identify that role from the current guide. Record the review verdict under the
batch's declared promotion authority; seek a separate owner decision only for
a material scope, representation, or claim change. Keep candidates, search
history, raw sources, and detailed reviews in ignored local areas.

Before promotion, apply the repository
[publication standard](../../PUBLICATION_STANDARD.md). Do not copy batch status,
production profile, owner decisions, semantic versions, Git identities, local
paths, or mapping-readiness labels into the public participant product or
scholarly interface account.

Promotion does not add the role to an executable participant set.

### 6. Run an authorized reference-pilot tail

Only in reference-pilot mode, and only when explicitly authorized:

- derive the mapping without adding semantics;
- repeat carrier review against the pilot set;
- test role behavior, cross-role interaction, invalid attempts, and replay;
- record exact identities, commands, results, and limitations; and
- keep simulation behind a separate authorization.

### 7. Close and learn

Route findings to evidence, behavior, Definition, skeleton/scenario, mapping,
implementation, or contracts. Fix role-specific problems locally. Change a
shared method only for a reusable gap and check it against accepted products.

Update the mutable plan, concise status, and batch close record. State what the
batch permits the project to claim and what remains external.

## Normal outputs

Roster-production mode produces:

1. one batch brief and roster slice;
2. reviewed research and an accepted product for each admitted participant;
3. adopted event source and claim updates;
4. profile-proportionate review verdicts;
5. one lightweight semantic interface review plus corresponding coverage in a
   shared publication-facing account, without requiring a separate public file
   per participant;
6. coherent promotion; and
7. one concise close record.

Reference-pilot mode may additionally produce a derived mapping and bounded
conformance evidence when those actions are authorized.

## Stop conditions

Stop and request direction when:

- a role is admitted for prominence rather than a required causal choice;
- the event question, horizon, or roster expands beyond the brief;
- evidence needs an unapproved source boundary;
- a role lacks a defensible decision interface or material evidence;
- a product conflicts with the frozen skeleton or another accepted role;
- interface review exposes a concrete carrier counterexample;
- mapping would invent behavior or historical knowledge; or
- implementation, simulation, or contract work is not separately authorized.
