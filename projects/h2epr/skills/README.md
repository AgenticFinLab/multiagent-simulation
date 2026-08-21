# H2EPR Skills

This directory contains the research and modeling methods used to build H2EPR
event models. The skills connect historical sources to participant behavior,
Agent Definitions, scenario semantics, and eventually executable backends.

H2EPR draws on the mature handbooks in `masim/skills/` and the research
workflow in `docs/create-related-work-skill/`. Its methods add requirements
specific to real-event modeling: participant-time information boundaries,
institutional governance, evidence-use separation, competing historical
interpretations, and a strict distinction between an Agent's intent and the
environment's result.

## Workflow

```text
Event question, role map, and batch scope
        ↓
Historical evidence research
        ↓
Participant behavior research
        ↓
Agent Definition authoring
        ↓
Scholarly and modeling review
        ↓
Scenario binding and implementation conformance
        ↓
Batch feedback and next-roster decision
```

The first four stages produce publication-facing research artifacts. Runtime
mapping follows only after the behavioral model is stable enough to review on
its own terms.

## Available skills

| Skill | Use |
|---|---|
| [`event-agent-batch`](event-agent-batch/SKILL.md) | Coordinate an approved role batch, route work through the specialized Skills, and close promotion, mapping, testing, and feedback without expanding the roster or permissions. |
| [`historical-evidence-research`](historical-evidence-research/SKILL.md) | Find, read, classify, and adjudicate evidence for a participant, institution, or decision situation. |
| [`participant-behavior-research`](participant-behavior-research/SKILL.md) | Build a publication-facing participant behavior model from adjudicated evidence, theory, institutional analysis, and high-information decision situations. |
| [`agent-definition`](agent-definition/SKILL.md) | Turn reviewed participant research into a canonical, publication-facing, backend-neutral Agent Definition. |
| [`agent-definition-review`](agent-definition-review/SKILL.md) | Independently review a Definition's historical grounding, institutional model, behavior, falsifiability, consistency, and publication quality. |

Dedicated scenario-design and runtime-conformance Skills will be added from
completed use cases. Each addition must have a real consumer and reviewed
content before it becomes part of this catalog.

The detailed roster, batching, promotion, and test process is documented in
the [Agent development workflow](../agents/WORKFLOW.md).

## Method principles

- Read and adjudicate evidence before writing behavior.
- Treat historical claims, theoretical mechanisms, estimates, analogies, and
  modeling assumptions as different kinds of support.
- Record what a participant could know at the modeled decision time, not only
  what a researcher knows afterward.
- Keep the evidence ledger, Agent Definition, scenario, machine contracts, and
  authoritative state transition as complementary sources of truth.
- Write Agent Definitions as scholarly model specifications. Keep file hashes,
  runtime bindings, code identifiers, and test mechanics in derived
  conformance artifacts.
- Use small numbers of deeply researched participants and decision situations
  to improve the method before proposing cross-event archetypes.

## Source adaptation

H2EPR adopts research discipline rather than copying whole handbooks. In
particular:

- MASim contributes evidence-grounded theory, explicit information sets,
  behavioral mechanisms, parameters, worked cases, calibration, ablation, and
  cross-section consistency.
- The repository related-work guide contributes proactive and reactive search,
  relevance-based reading depth, structured extraction, source chaining, and
  manual verification.
- H2EPR changes scenario-portable archetypes into event-bound participant
  models, replaces venue-based evidence filters with claim-appropriate source
  hierarchies, and preserves unresolved historical structure instead of
  filling it with unsupported defaults.
