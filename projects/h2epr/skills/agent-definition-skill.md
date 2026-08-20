---
name: agent-definition-skill
purpose: Design or review an evidence-linked, event-bound H2EPR Agent Definition without turning the profile into runtime code or a premature cross-event archetype.
status: provisional
audience: H2EPR researchers, Agent authors, implementers, and reviewers.
---

# H2EPR Agent Definition

This is an H2EPR framework method asset, analogous to the handbooks under
`masim/skills/`. It is not an automatically installed Codex Skill package.

Create the smallest useful behavioral contract for the current event and
participant. Preserve uncertainty and project authorization. Do not infer
permission to browse, inspect held-out material, run simulation, change
contracts, or generalize across events.

## Establish the research boundary

Confirm the event, decision time, participant, authorized evidence, exposure
status, and question. Work claim by claim. Keep source, time, epistemic status,
allowed use, dispute, and withdrawal consequence in the evidence ledger; the
Definition only references those claims.

When an unresolved historical fact changes the mechanism, retain explicit
structural uncertainty. Do not resolve it by preference or invented
probability.

## Model high-information decisions

Choose a few decision situations that expose role differences or can invalidate
the model. State the represented decision interface, aggregated/excluded
actors, and a trigger for finer granularity.

For each decision situation make reviewable:

- legal and forbidden observations, freshness, and missing/stale behavior;
- behaviorally material state and its authoritative replay path;
- authority, procedure, resource-control relation, and hard constraints;
- hard conformance obligations, separately from behavioral hypotheses;
- precedence, permitted intent envelope, fallback, and abstention;
- trace implication, falsifier, downstream consumer, and deletion consequence.

Do not translate every code branch into a commitment. Allow multiple compliant
actions unless evidence rules them out.

## Preserve orthogonal authority

- Agent Definition owns representation, information semantics, decision
  commitments, intent meaning, assumptions, and falsifiers.
- Evidence ledger owns source, time, status, exposure, and use.
- Scenario/environment owns actual world values, institutions, delivery,
  feasibility, and adjudication.
- Machine contracts own identifiers, encoding, shape, serialization, and
  versioning.
- Authoritative state/reducer owns committed state and results.

An Agent emits intent, never a self-realized outcome. Invalid or unauthorized
attempts remain visible rather than being silently repaired.

## Iterate before abstracting

Draft the Definition with a shared micro-situation and at least one contrasting
role. Let observed duplication or ambiguity—not anticipated reuse—decide
whether a theory prototype or Participant Card should later be extracted.

Map the draft to the current runtime and distinguish retained engineering seam,
available-but-unused carrier, missing capability, and semantic conflict. Remove
decorative content and surface hidden inputs, actor-ID branches, thresholds,
state, and outcome semantics.

If a pilot uses a derived machine binding, verify the canonical Markdown hash,
identity/version, commitment inventory, explicit missing-value observations,
and commitment-specific intent envelope. Treat any drift as a fail-closed
conformance error; never let the binding become an independent behavior source.

Review actor-name erasure, role/authority swap, future-fact injection,
missing/stale input, state replay, invalid-intent visibility, runtime mapping,
and deletion of mandatory content. Stop before unauthorized evidence access,
contract changes, additional events, or unsupported validity claims.

For the tracked H2EPR pilot, read:

- `../agents/agent-definition-template.md`
- `../agents/defines/panic_1907/evidence-ledger.md`
- `../agents/defines/panic_1907/micro-situation.md`

These are mutable pilot assets, not universal installed-skill dependencies.
