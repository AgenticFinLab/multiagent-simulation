# Agent development workflow

H2EPR develops event-bound participant models in two modes. Reference pilots
take a few roles through the whole semantic and engineering path to test the
method. Roster production then builds the remaining scholarly Definitions
against a shared event skeleton before the event is mapped as one system.

## Two operating modes

| Mode | Use | Normal endpoint |
|---|---|---|
| reference pilot | test a new representation, Definition method, carrier boundary, or interaction pattern with a small number of roles | accepted Definitions plus an explicitly authorized mapping and conformance slice |
| Roster batch production | complete the accepted event roster efficiently and consistently | accepted role or population products plus a lightweight interface preflight |

Choose the mode in the batch brief. Do not run the reference-pilot engineering
tail for every production role.

```text
event question and horizon
  -> causal role map
  -> accepted research roster
  -> event semantic skeleton
  -> reference pilot, when the method needs testing
  -> Roster production batches
       evidence -> behavior -> Definition -> review -> promotion
       -> lightweight interface preflight
  -> Roster Definition release
  -> consolidated mapping and carrier review
  -> conformance, interaction, and replay tests
  -> separately approved simulation
```

## Build and maintain the roster

The roster starts from the research question, modeled interval, and causal
transitions the project intends to explain. Each relevant entity or process
receives one disposition:

| Disposition | Use |
|---|---|
| Agent | an autonomous choice must be explained and has a defensible decision interface |
| population or cohort | heterogeneous actors matter collectively and individual reconstruction is neither necessary nor supported |
| representation gate | a required short study must choose Agent, population/cohort, or scenario ownership before production continues |
| scenario or institutional process | rules, timing, routing, delivery, adjudication, market mechanics, or resource effects |
| initial or exogenous context | establishes the selected boundary without claiming endogenous explanation |
| excluded | outside the approved question or evidence boundary |

For a proposed Agent, record its focal choices, representation boundary,
evidence maturity, cost of externalization, and promotion trigger. Historical
prominence alone is not an admission criterion.

Approve the roster before production. Freezing a roster prevents silent scope
drift; it does not make the model immutable. A change to the event question,
horizon, causal owner, or disposition requires an owner decision and a new
roster version. Evidence refinement within an accepted row does not.

## Establish the event semantic skeleton

Before Roster production, define a short event-level skeleton that names:

- the research boundary and working phases;
- shared institutional, information, relationship, resource, request, result,
  and time concepts;
- the main interaction routes and causal lineage requirements;
- what Agents, populations, scenario, contracts, mapping, and reducer each own;
- known structural variants and exogenous inputs; and
- the interface-preflight questions every batch must answer.

The skeleton aligns vocabulary and ownership. It is not a scenario
implementation, wire schema, parameter registry, or event script. A role batch
may propose a revision when evidence exposes a genuine conflict, but may not
silently redefine the shared event language.

## Open a small batch

A normal batch contains two or three roles from one causal segment. A
single-role batch is appropriate for a materially different representation,
such as the first population/cohort model, or an unusually difficult evidence
boundary.

Use one concise batch brief to record:

- mode, event identity, modeled interval, and research question;
- roster rows and causal choices assigned to the batch;
- interactions and scenario-owned processes in scope;
- local evidence, exposed outcomes, and source permissions;
- whether promotion is per role or per batch;
- the authorized endpoint; and
- stopping conditions and owner decisions.

Use the mutable working root and one directory per batch:

```text
batches/<batch-id>/
├── BATCH.md
├── roles/<role-id>/
│   ├── RESEARCH.md
│   ├── BEHAVIOR.md
│   ├── DEFINITION.md
│   └── REVIEW.md
├── INTERFACE.md
└── CLOSE.md
```

Small roles may share research notes when ownership remains clear. Raw source
bytes belong in the evidence area rather than the batch directory.

Permissions are batch-specific. Research permission for one role does not
authorize another participant or source boundary. Definition promotion does
not authorize mapping, implementation, simulation, or contract changes.

## Develop each role

Each role follows four research stages. They may share adopted sources and
decision situations, but retain separate participant boundaries and review
verdicts.

| Stage | Project Skill | Required result |
|---|---|---|
| Evidence | [historical-evidence-research](../skills/historical-evidence-research/SKILL.md) | adopted source records, atomic claims, participant-time and use boundaries, conflicts, and a scoped closure verdict |
| Behavior | [participant-behavior-research](../skills/participant-behavior-research/SKILL.md) | representation, governance, information, mechanisms, high-information situations, worked cases, and falsifiers |
| Definition | [agent-definition](../skills/agent-definition/SKILL.md) | one canonical, publication-facing, event-bound Definition candidate |
| Review | [agent-definition-review](../skills/agent-definition-review/SKILL.md) | independent findings, revision routing, and an acceptance or return verdict |

Review local sources and event claims before opening new research. External
research uses the approved scope and archives only sources that enter claim
adjudication. Search results and unused downloads remain working notes.

The ten-module template provides a common reading order. It does not force
institutions, individuals, and populations to share mechanisms, variables, or
commitment counts. Every material observation, state, parameter, and intent
needs an explanatory or review consumer.

## Review and promote

Review a stable candidate independently of backend code and simulation output.
Resolve blocking and major findings in the layer that owns the problem:
evidence, representation, behavior, Definition, or scenario boundary.

Before promotion:

1. confirm Definition identity, version, claim references, and source records;
2. for a new candidate, pass the lightweight ten-module and inventory-profile
   check without applying it retroactively to frozen releases;
3. check cross-section, cross-role, roster, and skeleton consistency;
4. complete the batch interface preflight;
5. obtain owner acceptance; and
6. promote the Definition, adopted claims, sources, interface note, and concise
   guide updates as one coherent change.

The tracked tree contains the current accepted research artifacts. Drafts,
search notes, rejected alternatives, raw sources, and detailed review history
remain in the ignored working and evidence areas. Git records accepted public
history.

Promotion adds an accepted research product. It does not silently add an
executable participant, update a binding hash, or authorize implementation.

## Lightweight preflight for production batches

Roster batches stop after a semantic interface check. `INTERFACE.md` records:

- representation and causal choices;
- observations, private state, intents, counterparties, and routes;
- authority, resource, lifecycle, result, and scenario dependencies;
- compatibility with the event skeleton and other accepted products; and
- whether each material interface is a known fit, expects an internal mapping
  extension, or presents a concrete carrier counterexample.

The preflight does not choose machine fields, build registries, bind hashes,
implement policy, or run replay tests. A suspected carrier issue is recorded
for consolidated review; only a concrete, irreducible counterexample pauses
production for an owner decision.

## Create the Roster Definition release

The release closes the semantic production phase. It requires:

- a reviewed disposition for every roster row;
- an accepted Definition for every admitted Agent;
- an accepted interface for every retained population/cohort;
- explicit scenario ownership for externalized processes;
- resolved blocking conflicts across Definitions and the skeleton; and
- a manifest pinning roster, skeleton, Definition, evidence, and preflight
  identities.

The release is a coherent semantic input, not an executable bundle and not a
scientific-validity claim.

## Define the released event world

After semantic release, use the
[`event-scenario-design`](../skills/event-scenario-design/SKILL.md) Skill and
the public Scenario Definition and interface-closure templates to specify event
time, institutions, relationships, resources, information delivery, business
lifecycles, adjudication, results, variants, and termination, then reconcile the
complete released observation and intent interface.

The Scenario Definition and consolidated mapping may expose requirements to
one another, but they retain separate authorities. The scenario cannot add
participant behavior; the mapping cannot add world or institutional meaning.
Resolve their interface before policy implementation. A semantic skeleton is
not by itself a complete executable scenario.

The accepted Scenario Definition and accepted mapping converge before any
policy/interaction implementation. A mapping-loader conformance slice may be
completed earlier because it tests carrier and assembly properties rather than
participant behavior or event dynamics.

## Map and test the released roster

Consolidated mapping starts only after the release and under separate
authorization. It derives implementation carriers for the released semantic
system; it cannot introduce a behavior, observation, authority, state, intent,
route, or result meaning.

Use the
[`roster-mapping-conformance`](../skills/roster-mapping-conformance/SKILL.md)
Skill in design mode for the inventory, mapping, carrier decision, rules, and
review. Enter its conformance mode only through a separate implementation
authorization.

Use the following test ladder:

| Level | Question |
|---|---|
| release integrity | Do roster, evidence, Definitions, population interfaces, skeleton, IDs, links, and inventories close? |
| mapping and carrier | Can every material semantic element be carried without loss or hidden defaults? |
| role conformance | Do information, authority, lifecycle, mechanism, and adverse-result changes affect behavior as declared? |
| cross-role interaction | Do sender, receiver, route, authorization, disposition, result, and causal lineage close? |
| replay | Are state transitions, invalid attempts, results, and trace identity deterministic and inspectable? |
| bounded run | Does a separately approved scenario answer a stated scientific question without using its known outcome as policy input? |

Start with high-information cases rather than broad scenario coverage.
Simulation remains a separate decision.

## Route feedback

| Finding | Return to |
|---|---|
| source, event time, participant availability, or exposure error | evidence research |
| weak representation, mechanism, selection rule, or falsifier | behavior research or Definition |
| world fact, institution, routing, delivery, resource, or adjudication gap | semantic skeleton or scenario/environment |
| semantic loss between release and carrier | consolidated mapping |
| hidden branch, default, memory, or silent repair | implementation |
| demonstrated inability of released semantics to fit the carrier | narrow contract-successor review |

A role-specific correction stays with that role. Revise the shared template or
Skills only when a completed use case reveals a reusable method gap. Review a
shared change against accepted Definitions before using it in the next batch.

## Completion criteria

A role is complete for Definition work when its evidence question is closed
for the stated use, its behavior model is review-ready, its Definition has
passed independent substantive review, its interface preflight closes, and the
owner accepts its promotion.

A production batch is complete when every admitted role reaches that state and
the close record names any roster, skeleton, evidence, or later-mapping issue.

The Roster Definition release is complete when all roster dispositions and
semantic products meet the release gate. Consolidated conformance is complete
only after the released system is mapped and the agreed test ladder passes.

## Current H2EPR-0288 application

Knickerbocker Trust and NYCH form the completed reference pilot. The accepted
[Roster v0.4](rosters/panic_1907.md), event
[semantic skeleton](../scenarios/panic_1907/semantic-skeleton.md), seven Agent
Definitions and five population models now form
[Roster Definition release v0.1](../releases/panic_1907/roster-definition-v0.1/).
The accepted
[consolidated mapping](bindings/panic_1907/consolidated/) now provides the
full-Roster identity, observation, state, intent, lifecycle, authority,
resource and V1 carrier design. Its bounded
[mapping-loader/conformance profile](bindings/panic_1907/roster-v0.1/) now
checks the release-wide carrier and assembly risks without selecting policy or
running a scenario; no individual production role triggers a standalone
mapping or implementation cycle.
