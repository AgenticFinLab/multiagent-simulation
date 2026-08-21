# Agent development workflow

This guide defines how H2EPR develops event-bound Agent Definitions in small,
repeatable batches. It connects historical research to reviewed Definitions,
derived mappings, conformance tests, and later scenario work without turning
every named historical entity into an Agent.

## From event question to tested batch

```text
research question and event horizon
  -> causal role map and approved roster
  -> batch scope and permissions
  -> evidence research
  -> participant behavior research
  -> Agent Definition
  -> independent review and owner acceptance
  -> atomic promotion
  -> batch mapping and carrier review
  -> conformance, interaction, and replay tests
  -> feedback and next-batch decision
```

Simulation follows a separate decision. A batch first has to show that its
Definitions, information boundaries, authority, intents, results, and
interactions can be implemented without adding hidden semantics.

## Build the roster around causal responsibility

The roster starts from the research question, modeled interval, and causal
transitions that the project intends to explain. Each relevant entity or
process receives one disposition:

| Disposition | Use |
|---|---|
| Agent | an autonomous choice must be explained and has a defensible decision interface |
| population or cohort | heterogeneous actors matter collectively and individual reconstruction is neither necessary nor supported |
| scenario or institutional process | rules, timing, routing, delivery, adjudication, market mechanics, or resource effects |
| initial or exogenous context | establishes the selected starting boundary without claiming endogenous explanation |
| excluded | outside the approved question or evidence boundary |

For every proposed Agent, record its focal choices, representation boundary,
evidence maturity, cost of externalization, and promotion trigger. Historical
prominence alone is not an admission criterion.

Approve the roster before opening a production batch. A later role is added
only when the research question changes, new evidence reveals an autonomous
choice, or an existing externalization prevents a stated causal claim.

## Open a small batch

A normal batch contains two or three roles from one causal segment. A single
role is appropriate when it introduces a materially different representation,
such as an institution versus a population, or when its evidence boundary is
unusually difficult.

Use one concise batch brief to record:

- event identity, modeled interval, and research question;
- admitted roles and the decisions assigned to each;
- interactions and scenario-owned processes in scope;
- local evidence inputs and exposed outcomes;
- authorized network, archive, private, and held-out boundaries;
- whether the batch includes Definition work only, mapping, implementation,
  or a separately approved run;
- stopping conditions and owner decision points.

Use the existing mutable working root and keep one directory per batch:

```text
batches/<batch-id>/
├── BATCH.md
├── roles/<role-id>/
│   ├── RESEARCH.md
│   ├── BEHAVIOR.md
│   ├── DEFINITION.md
│   └── REVIEW.md
└── CLOSE.md
```

Small roles may combine research notes when ownership remains clear. Raw
source bytes belong in the evidence area rather than the batch directory.

Permissions are batch-specific. Research permission for one role does not
authorize a different participant or source boundary, and mapping permission
does not authorize implementation or simulation.

## Develop each role

Each role follows the same four research stages. The stages may share sources
and decision situations, but they keep separate participant boundaries and
review verdicts.

| Stage | Project Skill | Required result |
|---|---|---|
| Evidence | [historical-evidence-research](../skills/historical-evidence-research/SKILL.md) | adopted source records, atomic claims, participant-time and use boundaries, conflicts, and a scoped closure verdict |
| Behavior | [participant-behavior-research](../skills/participant-behavior-research/SKILL.md) | representation, governance, information, mechanisms, high-information situations, worked cases, and falsifiers |
| Definition | [agent-definition](../skills/agent-definition/SKILL.md) | one canonical, publication-facing, event-bound Definition candidate |
| Review | [agent-definition-review](../skills/agent-definition-review/SKILL.md) | independent findings, revision routing, and an acceptance or return verdict |

Local sources and existing event claims are reviewed before new research.
External research uses the approved scope and archives only sources that enter
claim adjudication. Search results and unused downloads remain working notes.

The ten-module Definition template provides a common reading order. It does
not force different institutions, individuals, or populations to use the same
mechanism, variables, or number of commitments. Every behaviorally material
observation, state, parameter, and intent needs an actual explanatory or review
consumer.

## Review and promote a role

Review a stable candidate independently of backend code and simulation output.
Resolve blocking and major findings in the layer that owns the problem:
evidence, representation, behavior, Definition, or scenario boundary.

Before promotion:

1. confirm the Definition identity, version, claim references, and source
   records;
2. check cross-section and cross-role consistency;
3. review the impact on current bindings and shared source/evidence snapshots;
4. obtain owner acceptance;
5. promote the Definition, adopted claims, sources, and concise public guide
   updates as one coherent commit.

Choose the promotion unit in the batch brief: one role or the complete small
batch. Never split one role's Definition, adopted claims, source records, and
required binding-hash update across inconsistent commits.

The tracked tree contains the latest accepted research artifacts. Drafts,
search notes, rejected alternatives, source bytes, and detailed review history
remain in the ignored working and evidence areas. Git records accepted public
history.

Promotion does not silently add the role to an executable roster. A binding
names its participant set explicitly.

## Integrate and test a batch

Mapping begins after every Definition in the batch is independently readable
and accepted. The mapping is derived: it may connect semantic concepts to
machine carriers, but it cannot introduce a new behavioral rule, observation,
authority, state, intent, or result meaning.

Use the following test ladder:

| Level | Question |
|---|---|
| Definition integrity | Do claims, sources, sections, IDs, links, and semantic inventories close? |
| Mapping and carrier | Can every material observation, state, commitment, intent, and lifecycle be carried without loss or hidden defaults? |
| Role conformance | Do missing information, authority, lifecycle, alternative mechanisms, and adverse results change behavior as declared? |
| Cross-role interaction | Do sender, receiver, route, message, authorization, disposition, and result references close across participants? |
| Replay | Are state transitions, invalid attempts, results, and trace identity deterministic and inspectable? |
| Bounded run | Does a separately approved scenario answer a stated scientific question without using its known outcome as policy input? |

Start with high-information cases rather than broad scenario coverage. Include
future-information injection, missing or stale observations, invalid authority,
duplicate requests, delayed or partial results, role/authority perturbations,
and an always-wait or always-abstain challenge where applicable.

A batch close record contains only the information needed to reproduce and
review it:

- batch scope and participant versions;
- adopted source-archive identities and Definition hashes;
- binding, scenario variant, contract, and code identity;
- test commands and results;
- unresolved evidence, unimplemented paths, and permitted claims.

## Route feedback to the owning layer

| Finding | Return to |
|---|---|
| source, event time, participant availability, or exposure error | evidence research |
| weak representation, mechanism, selection rule, or falsifier | behavior research or Definition |
| world fact, institution, routing, delivery, resource, or adjudication gap | scenario/environment |
| semantic loss between Definition and carrier | mapping |
| hidden branch, default, memory, or silent repair | implementation |
| demonstrated inability of the accepted semantics to fit the current carrier | narrow contract-successor review |

A role-specific correction stays with that role. Update the shared template or
Skills only when a completed use case reveals a reusable method gap. Review the
change against existing accepted Definitions before using it in the next batch.

## Completion criteria

A role is complete for Definition work when its evidence question is closed
for the stated use, its behavior dossier is review-ready, its Definition has
passed independent substantive review, and the owner has accepted its atomic
promotion.

A batch is complete for conformance work when all admitted Definitions are
hash-pinned, every required semantic element is mapped, cross-role lifecycles
close, the agreed test ladder passes, and residual limitations are explicit.

The event roster is complete for the selected research question when every
target causal transition has an explicit Agent, population, scenario, context,
or exclusion owner; every admitted Agent has an accepted Definition; and every
interaction needed by the intended run has passed mapping and conformance
review.

## Current H2EPR-0288 application

National Bank of Commerce is the third accepted Panic of 1907 Definition. Its
next cycle is a read-only mapping and carrier-impact review followed by a
separate decision on three-role conformance work. After that review, the event
role map will be refreshed and the remaining roster divided into small batches.
The existing map suggests run formation, private and trust-company rescue, and
collective bank/market response as distinct causal segments; their exact role
membership remains an owner decision tied to the event horizon.
