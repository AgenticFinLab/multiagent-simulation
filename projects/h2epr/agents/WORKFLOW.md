# Agent development workflow

H2EPR develops event-bound participant models in two modes. Reference pilots
take a few roles through the whole semantic and engineering path to test the
method. Roster production then builds the remaining scholarly participant
products against a shared event skeleton before the event is mapped as one
system.

This is the participant-production sub-process of the project-level
[Event modeling workflow](../WORKFLOW.md). That workflow owns the later
Scenario Configuration, bounded admission, policy/environment binding, and
conformance-closeout stages.

Participant production starts from an accepted
[Event Build Brief](../event-build-brief-template.md), whether its roster and
semantic skeleton are embedded or linked as separate versioned artifacts.
The brief's event question, evidence permissions, current authorization, and
scope-change policy remain binding on every batch.

## Two operating modes

| Mode | Use | Normal endpoint |
|---|---|---|
| reference pilot | test a new representation, participant-product method, carrier boundary, or interaction pattern with a small number of roles | accepted products plus an explicitly authorized mapping and conformance slice |
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
       evidence -> behavior -> representation product -> review -> promotion
       -> lightweight interface preflight
  -> Roster Definition release
  -> consolidated mapping and Event Scenario Definition convergence
  -> accepted non-executable Scenario Configuration
  -> separately authorized bounded admission, binding, and conformance
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

## Choose participant production depth

Assign one production profile when a roster row is accepted. The profile
controls working-document and review depth; it does not relax evidence,
participant-time, causal-ownership, or claim standards.

| Profile | Use | Normal product |
|---|---|---|
| `disposition-only` | scenario, exogenous, excluded, or deferred rows that do not require a participant model | accepted roster disposition and owner |
| `standard` | a causally necessary Agent or population whose representation and evidence boundary are established | one accepted participant product, concise review, and interface preflight |
| `deep` | a new or disputed representation, a central causal choice, high evidence or claim risk, or a proposed reusable abstraction | fuller separate research and review records as the risk requires |

A standard profile still closes the evidence and behavior questions needed for
its use. Its working records may be combined, and routine findings may be
reviewed at batch level. A deep profile separates evidence, behavior,
authoring, and review when that separation makes a material judgment easier to
audit. Do not promote a row to `deep` merely because a detailed template is
available.

The production profile is independent of the batch mode. A `deep` participant
does not authorize mapping or implementation, and a reference pilot still
requires explicit authorization for its engineering tail.

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

Use the smallest coherent batch that shares a causal segment and evidence
boundary; two or three rows will often be enough. A single-row batch is
appropriate for a materially different representation, such as the first
population/cohort model, or an unusually difficult evidence boundary. Do not
split a routine batch only to create extra review or closeout records.

Use one concise batch brief to record:

- mode, event identity, modeled interval, and research question;
- roster rows and causal choices assigned to the batch;
- interactions and scenario-owned processes in scope;
- local evidence, exposed outcomes, and source permissions;
- the production profile for each row;
- whether promotion is per role or per batch;
- the authorized endpoint; and
- stopping conditions and owner decisions.

When a batch needs a working directory, use a compact structure such as:

```text
batches/<batch-id>/
├── BATCH.md
├── roles/<role-id>/
│   └── <working records needed for the selected profile>
├── INTERFACE.md
└── CLOSE.md
```

These filenames describe responsibilities, not mandatory public artifacts.
Standard rows may combine research and review notes when claim and participant
ownership remains clear. Raw source bytes belong in the evidence area rather
than the batch directory.

Permissions are batch-specific. Research permission for one role does not
authorize another participant or source boundary. Participant-product
promotion does not authorize mapping, implementation, simulation, or contract
changes.

## Develop each participant

Every admitted Agent or population closes the evidence and behavior questions
needed for its stated use. Rows may share adopted sources and decision
situations, but never participant policy, private state, or authority.

| Route | Methods | Required result |
|---|---|---|
| Agent | [historical evidence](../skills/historical-evidence-research/SKILL.md), [participant behavior](../skills/participant-behavior-research/SKILL.md), [Agent Definition](../skills/agent-definition/SKILL.md), and [Definition review](../skills/agent-definition-review/SKILL.md) | one canonical, publication-facing, event-bound Agent Definition and a profile-proportionate verdict |
| population or cohort | historical evidence, participant behavior, the [Population model template](../populations/population-model-template.md), and profile-proportionate review | one heterogeneous population model and interface without a collective personality |
| disposition-only | roster adjudication | an explicit scenario, exogenous, excluded, or deferred owner; no participant product |

The stages name semantic responsibilities, not a required file sequence. A
standard Agent may combine its supporting working records, but its accepted
Definition remains canonical. A population does not use the Agent Definition
profile unless the roster decision actually admits an Agent.

Review local sources and event claims before opening new research. External
research uses the approved scope and archives only sources that enter claim
adjudication. Search results and unused downloads remain working notes.

The ten-module template provides a common reading order for Agent Definitions.
It does not govern population products or force institutions and individuals
to share mechanisms, variables, or commitment counts. Every material
observation, state, parameter, and intent still needs an explanatory or review
consumer.

## Review and promote

Review a stable candidate independently of backend code and simulation output.
Use a fresh, authoring-independent reviewing context where practical. A
standard row may close with a concise batch-level review; a deep row uses a
separate report when its novelty, centrality, or claim risk requires one.
Review independence is a judgment boundary, not a clean-builder claim,
mandatory external signoff, or extra public file.

Resolve blocking and major findings in the layer that owns the problem:
evidence, representation, behavior, Definition, population model, or scenario
boundary.

Before promotion:

1. confirm product identity, version, claim references, and source records;
2. for a new Agent Definition, pass the lightweight ten-module and
   inventory-profile check without applying it retroactively to frozen
   releases;
3. check cross-section, cross-role, roster, and skeleton consistency;
4. complete the batch interface preflight;
5. record the review verdict and any triggered owner decision under the
   declared promotion authority; and
6. promote the participant product, adopted claims, sources, interface note,
   and concise guide updates as one coherent change.

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

The accepted Scenario Definition and accepted mapping converge before Scenario
Configuration. Configuration then fixes one declared-purpose assembly,
structural selection, policy semantics, sensitivities, and completion boundary
without silently becoming executable. A mapping-loader conformance slice may
be completed earlier because it tests carrier and assembly properties rather
than participant behavior or event dynamics; a configuration loader or policy
binding remains a later, separately authorized stage.

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

A participant is complete for semantic production when its evidence question
is closed for the stated use, its accepted product and interface preflight
close, and it has a review appropriate to the selected profile. Promotion uses
the authority declared in the batch brief; a separate owner decision is needed
only when a material scope, representation, or claim boundary changes.

A production batch is complete when every admitted row reaches its declared
endpoint and the close record names any roster, skeleton, evidence, or
later-mapping issue.

Apply the project [phase closeout checklist](../phase-closeout-checklist.md) to
the participant-production phase. A batch `CLOSE.md` may carry supporting
detail, but it does not replace the phase-level acceptance record or create a
second project status authority. Do not repeat the project checklist for every
role; aggregate accepted batch and role reviews at the maintained phase
boundary.

The Roster Definition release is complete when all roster dispositions and
semantic products meet the release gate. Consolidated conformance is complete
only after the released system is mapped and the agreed test ladder passes.

## Current H2EPR-0288 application

Knickerbocker Trust and NYCH form the completed reference pilot. The accepted
[Roster v0.4](rosters/panic_1907.md), event
[semantic skeleton](../scenarios/panic_1907/semantic-skeleton.md), seven Agent
Definitions and five population models form
[Roster Definition release v0.1](../releases/panic_1907/roster-definition-v0.1/).
The accepted
[consolidated mapping](bindings/panic_1907/consolidated/) provides the
full-Roster identity, observation, state, intent, lifecycle, authority,
resource and V1 carrier design. Its bounded
[mapping-loader/conformance profile](bindings/panic_1907/roster-v0.1/)
checks the release-wide carrier and assembly risks without selecting policy or
running a scenario; no individual production role triggers a standalone
mapping or implementation cycle. The accepted
[Event Scenario Definition v0.1](../scenarios/panic_1907/definition-v0.1/) and
[Scenario Configuration v0.1](../configs/panic_1907/scenario-configuration-v0.1/)
close the event-world and first mechanism-coverage configuration stages.
Configuration admission, the KT--NBC--NYCH bounded binding, and its
[lineage conformance closeout](../scenarios/panic_1907/lineage-conformance-v0.1/)
are also complete. The configuration remains non-executable; the next normal
method task is a second-event forward test, not another participant-production
batch or deeper first-event runtime.
