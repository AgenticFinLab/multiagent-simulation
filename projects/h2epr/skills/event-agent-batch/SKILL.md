---
name: h2epr-event-agent-batch
description: Coordinate an approved H2EPR event-role batch in either reference-pilot or Roster-production mode. Use when several event roles need a shared scope, specialist evidence/behavior/Definition/review routing, atomic promotion, and either an explicitly authorized conformance pilot or a lightweight interface preflight.
---

# Event Agent batch

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
  accepted research products and a lightweight interface preflight. Do not map
  or implement each batch.

When the request does not explicitly authorize the reference-pilot engineering
tail, use Roster-production mode.

## Required inputs

Confirm:

- event identity, horizon, research question, roster version, and skeleton
  version;
- admitted roster rows and their causal choices;
- batch mode and promotion unit;
- local evidence, exposed outcomes, and source permissions;
- the current template and specialist Skill identities;
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

### 2. Research each role

For each role, apply:

1. [`h2epr-historical-evidence-research`](../historical-evidence-research/SKILL.md);
2. [`h2epr-participant-behavior-research`](../participant-behavior-research/SKILL.md);
3. [`h2epr-agent-definition`](../agent-definition/SKILL.md); and
4. [`h2epr-agent-definition-review`](../agent-definition-review/SKILL.md).

Share adopted source identity and event claims through the event source
register and evidence ledger. Do not share participant policy, private state,
or authority merely because roles belong to one batch.

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

### 4. Complete `INTERFACE.md`

Record only what later integration needs to know:

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

### 5. Promote accepted products

Promote the accepted Definition or population product with adopted claim and
source updates, `INTERFACE.md`, and concise guide changes. Keep candidates,
search history, raw sources, and detailed reviews in ignored local areas.

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
2. reviewed research and an accepted product per row;
3. adopted event source and claim updates;
4. independent review verdicts;
5. one lightweight `INTERFACE.md`;
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
- preflight exposes a concrete carrier counterexample;
- mapping would invent behavior or historical knowledge; or
- implementation, simulation, or contract work is not separately authorized.
