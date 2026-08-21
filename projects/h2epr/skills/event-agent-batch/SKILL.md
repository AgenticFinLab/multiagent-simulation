---
name: h2epr-event-agent-batch
description: Coordinate a small approved batch of H2EPR event roles from roster admission through evidence and behavior research, Agent Definition review, atomic promotion, derived mapping, conformance testing, and feedback. Use for multi-role or event-roster work; use the specialized H2EPR Skills for each role's evidence, behavior, Definition, and review content.
---

# Event Agent batch

Use this skill to keep repeated Agent development consistent, bounded, and
reproducible across one event. It coordinates the work; it does not replace the
specialized research and authoring Skills.

Read the canonical [Agent development workflow](../../agents/WORKFLOW.md)
before opening or closing a batch.

## Required inputs

Confirm:

- event identity, modeled interval, research question, and causal transitions;
- current role map and owner-approved Agent roster;
- a batch of normally two or three admitted roles;
- each role's focal choices, representation boundary, and externalization cost;
- local evidence inventory and known exposed outcomes;
- network, archive, private, Reference, and held-out permissions;
- whether the authorization ends at research, Definition promotion, mapping,
  implementation, or a bounded run;
- current template, Skill, contract, binding, and scenario identities;
- working, evidence, and tracked output locations.

If the roster or scientific question is unresolved, complete the role-map gate
before starting role research.

## Workflow

### 1. Open the batch

Write one concise batch brief covering scope, roles, interactions, permissions,
stopping conditions, owner decisions, and whether promotion occurs per role or
for the complete small batch. Reuse the current mutable plan and status files
rather than creating parallel trackers. Use the workflow's compact batch
layout; keep source bytes in the evidence area.

### 2. Complete role research independently

For each role, apply in order:

1. [`h2epr-historical-evidence-research`](../historical-evidence-research/SKILL.md);
2. [`h2epr-participant-behavior-research`](../participant-behavior-research/SKILL.md);
3. [`h2epr-agent-definition`](../agent-definition/SKILL.md);
4. [`h2epr-agent-definition-review`](../agent-definition-review/SKILL.md).

Share adopted source identities and event facts through the event source
register and evidence ledger. Do not share participant policy, private state,
or authority merely because roles appear in the same batch.

### 3. Review the batch boundary

Before promotion, check:

- every autonomous choice belongs to an admitted Agent;
- rules, delivery, adjudication, and realized effects remain scenario-owned;
- population behavior is not disguised as one institutional personality;
- cross-role messages and relationships use compatible semantics;
- no role relies on another role's hidden state or a later event outcome;
- shared Template or Skill changes are supported by a reusable method gap.

### 4. Promote accepted Definitions

Use the promotion unit fixed in the batch brief. Include each accepted
Definition with its adopted claim/source updates, required binding-hash update,
and concise guide changes. Perform a binding-impact check whenever a pinned
shared asset changes. Keep candidates, search history, raw sources, and
detailed reviews in the ignored local areas.

### 5. Map and test the completed batch

After the batch's Definitions are accepted:

- map every material observation, persistent state, commitment, intent,
  authority, lifecycle, and result boundary;
- repeat carrier-fit review instead of assuming the earlier role result;
- use explicit participant and scenario identities;
- test role behavior, cross-role interaction, invalid attempts, and replay;
- record exact versions, hashes, commands, results, and remaining gaps.

Treat simulation as a separate gate with its own research question and
authorization.

### 6. Close and learn

Route findings to evidence, behavior, Definition, scenario, mapping,
implementation, or contracts. Make a narrow local fix for a role-specific
problem. Revise shared methods only for a demonstrated reusable gap, then check
the change against accepted Definitions before opening the next batch.

Update the role map, mutable plan, and concise status at batch close. Record
what the batch permits the project to claim and what remains external.

## Outputs

A completed batch normally has:

1. one batch brief and approved roster slice;
2. reviewed research and one accepted Definition per role;
3. event-level adopted source and claim updates;
4. an independent review verdict per Definition;
5. atomic promotion commits;
6. a derived batch binding and carrier verdict when authorized;
7. conformance, interaction, and replay results when authorized;
8. one concise close record and an updated role map/status.

## Stop conditions

Stop and request direction when:

- a role is being admitted for prominence rather than a required causal choice;
- the research question or event horizon expands beyond the batch brief;
- useful evidence requires unapproved network, archive, private, Reference, or
  held-out access;
- a role lacks a defensible decision interface or material evidence;
- mapping would need to invent behavior or silently change an accepted
  Definition;
- implementation, simulation, or contract work has not been separately
  authorized;
- one batch is growing into a full-event rewrite rather than a reviewable
  increment.
