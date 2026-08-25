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
Event Build Brief: question, boundary, role map, and current authorization
        ↓
Historical evidence research
        ↓
Participant behavior research
        ↓
Accepted representation route
        ├── Agent Definition + proportionate review
        ├── Population model + proportionate review
        └── Scenario, exogenous, excluded, or deferred disposition
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

Evidence and behavior research feed the representation chosen by the roster.
Normal Roster batches produce only the participant products required by that
route and one lightweight interface preflight. Roster Definition release v0.1
provides the stable semantic input for mapping and scenario convergence.
Configuration remains a separate, normally non-executable stage; loader,
binding, conformance, simulation, and evaluation each retain their own
authorization boundary. A small reference pilot may reach mapping earlier only
when that engineering feedback is the purpose of the pilot.

## Available skills

| Skill | Use |
|---|---|
| [`event-agent-batch`](event-agent-batch/SKILL.md) | Coordinate an approved participant batch with risk-proportionate Agent, population, or disposition routing and stop at the correct integration boundary. |
| [`historical-evidence-research`](historical-evidence-research/SKILL.md) | Find, read, classify, and adjudicate evidence for a participant, institution, or decision situation. |
| [`participant-behavior-research`](participant-behavior-research/SKILL.md) | Build a publication-facing participant behavior model from adjudicated evidence, theory, institutional analysis, and high-information decision situations. |
| [`agent-definition`](agent-definition/SKILL.md) | Turn reviewed participant research into a canonical, publication-facing, backend-neutral Agent Definition. |
| [`agent-definition-review`](agent-definition-review/SKILL.md) | Independently review a Definition's historical grounding, institutional model, behavior, falsifiability, consistency, and publication quality. |
| [`event-scenario-design`](event-scenario-design/SKILL.md) | Turn an accepted event roster, semantic release, evidence boundary, and participant models into a publication-facing Scenario Definition without writing policy or running a simulation. |
| [`roster-mapping-conformance`](roster-mapping-conformance/SKILL.md) | Derive a release-wide mapping and carrier decision, then implement only an explicitly authorized loader/conformance slice. |
| [`scenario-configuration`](scenario-configuration/SKILL.md) | Design, review, and atomically promote one declared-purpose Scenario Configuration, then delimit its later bounded engineering admission without defining schema, policy, or runtime. |

The scenario, mapping/conformance, and configuration Skills encode the methods
supported by the repository. The mapping/conformance Skill includes the
bounded multi-hop binding and conformance method demonstrated by the
KT--NBC--NYCH closeout. The configuration Skill defines the corresponding
configuration-design and admission boundaries. Re-evaluate both methods when
they are applied to another event, and revise them only where that use exposes
a reusable gap. They do not form a general simulation pipeline or authorize
policy, simulation, contract, or evaluation work.

The project-level stage order, authorization boundaries, and current event
position are documented in the [Event modeling workflow](../WORKFLOW.md). The
detailed roster, batching, promotion, and participant test process remains in
the [Agent development workflow](../agents/WORKFLOW.md).

## Workflow templates

| Template | Use |
|---|---|
| [Event Build Brief](../event-build-brief-template.md) | Open an event with one accepted question, temporal and evidence boundary, causal role map, roster dispositions, semantic skeleton, and current authorization. |
| [Population model](../populations/population-model-template.md) | Specify heterogeneous choice units, information, private state, behavior, uncertainty, and interface ownership in the canonical ten-module population structure. |
| [Phase closeout checklist](../phase-closeout-checklist.md) | Close any maintained event phase with common mainline, depth, authority, evidence, integrity, and handoff checks, recording a reusable method finding only when one emerged. |

These project-level templates route work into the specialist Skills; they do
not replace the Skills' artifact-specific inputs, outputs, reviews, or stop
conditions. Use the closeout checklist inside an existing authoritative record
when possible rather than creating a parallel status file. Complete only the
brief's minimum profile and the checklist's core gates by default; conditional
sections are triggered by the event and the surfaces actually changed.

## Method identity and loading

At event opening, record one method baseline: the repository commit plus the
Skill and template paths selected for the authorized work. That is sufficient
to reproduce the method; do not create a second version number for every Skill
or copy the full directory into an event record.

Read the coordinating Skill and only the specialist Skills and references used
by the selected representation and production profile. These repository paths
are the canonical method assets. Any execution integration should point to
them rather than maintain a divergent copy.

## Production profiles

Participant production uses `disposition-only`, `standard`, or `deep` depth.
The profile changes working-document and review depth, not evidence or semantic
standards. Standard is the default for an established Agent or population;
deep is triggered by a new or disputed representation, central causal choice,
or material evidence and claim risk. Reference-pilot engineering remains a
separate choice and is never implied by `deep`.

## Method principles

- Read and adjudicate evidence before writing behavior.
- Treat historical claims, theoretical mechanisms, estimates, analogies, and
  modeling assumptions as different kinds of support.
- Record what a participant could know at the modeled decision time, not only
  what a researcher knows afterward.
- Keep the participant-evidence record, Agent Definition, scenario, machine contracts, and
  authoritative state transition as complementary sources of truth.
- Write Agent Definitions as scholarly model specifications. Keep file hashes,
  runtime bindings, code identifiers, and test mechanics in derived
  conformance artifacts.
- Match research and review depth to causal and claim risk, and use a small
  number of high-information decision situations before proposing cross-event
  archetypes.

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
