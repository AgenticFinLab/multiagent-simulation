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
Lightweight event-interface preflight
        ↓
Roster Definition release
        ├── Event Scenario Definition + interface closure
        └── Consolidated mapping and carrier review
                    └── Bounded mapping-loader conformance

Accepted Scenario Definition + accepted mapping
        ↓
Versioned Scenario Configuration + review
        ↓
Separately authorized bounded configuration admission
        ↓
Exact carrier projection + minimal policy/environment binding
        ↓
Conformance closeout
```

The first four stages produce publication-facing research artifacts. Normal
Roster batches then record a lightweight interface preflight. Roster
Definition release v0.1 provides the stable semantic input for mapping and
scenario convergence. Configuration remains a separate, normally non-
executable stage; loader, binding, conformance, simulation, and evaluation each
retain their own authorization boundary. A small reference pilot may reach
mapping earlier only when that engineering feedback is the purpose of the
pilot.

## Available skills

| Skill | Use |
|---|---|
| [`event-agent-batch`](event-agent-batch/SKILL.md) | Coordinate an approved role batch in reference-pilot or Roster-production mode, route work through the specialist Skills, and stop at the correct integration boundary. |
| [`historical-evidence-research`](historical-evidence-research/SKILL.md) | Find, read, classify, and adjudicate evidence for a participant, institution, or decision situation. |
| [`participant-behavior-research`](participant-behavior-research/SKILL.md) | Build a publication-facing participant behavior model from adjudicated evidence, theory, institutional analysis, and high-information decision situations. |
| [`agent-definition`](agent-definition/SKILL.md) | Turn reviewed participant research into a canonical, publication-facing, backend-neutral Agent Definition. |
| [`agent-definition-review`](agent-definition-review/SKILL.md) | Independently review a Definition's historical grounding, institutional model, behavior, falsifiability, consistency, and publication quality. |
| [`event-scenario-design`](event-scenario-design/SKILL.md) | Turn an accepted event roster, semantic release, evidence boundary, and participant models into a publication-facing Scenario Definition without writing policy or running a simulation. |
| [`roster-mapping-conformance`](roster-mapping-conformance/SKILL.md) | Derive a release-wide mapping and carrier decision, then implement only an explicitly authorized loader/conformance slice. |
| [`scenario-configuration`](scenario-configuration/SKILL.md) | Design, review, and atomically promote one declared-purpose Scenario Configuration, then delimit its later bounded engineering admission without defining schema, policy, or runtime. |

The scenario, mapping/conformance, and configuration Skills are working
candidates. The mapping/conformance Skill now includes the bounded multi-hop
E6--E7 method demonstrated by the completed KT--NBC--NYCH closeout. The
configuration method is extracted retrospectively from the accepted
H2EPR-0288 configuration. Both additions should be forward-tested on the next
event that reaches their stage. Revise them only where real use exposes a
reusable gap. They do not form a general simulation pipeline or authorize
policy, simulation, contract, or evaluation work.

The project-level stage order, authorization boundaries, and current event
position are documented in the [Event modeling workflow](../WORKFLOW.md). The
detailed roster, batching, promotion, and participant test process remains in
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
