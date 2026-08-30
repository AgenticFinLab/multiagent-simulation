# H2EPR event modeling workflow

This workflow defines how an H2EPR event moves from a research question to a
reviewed engineering baseline. Specialist methods under `skills/` describe
how to produce individual artifacts; this document defines their order,
authority, and stopping boundaries.

## Working principles

- Every phase consumes named, versioned, or hash-identified inputs.
- Evidence, participant semantics, scenario rules, configuration, machine
  projection, runtime behavior, and evaluation have separate owners.
- An accepted artifact is changed through a reviewed successor, not by silently
  repairing downstream copies.
- A configuration is non-executable until admission and binding have been
  accepted for its exact identity.
- Implement the smallest lineage that can test a new interface. Move to a
  complete roster only after that interface is closed and a full-event
  integration question is separately authorized.
- Route defects to the layer that owns the meaning instead of adding hidden
  defaults or implementation-only exceptions.

## Event phases

| Phase | Required result | Stopping boundary |
|---|---|---|
| Frame the event | Accepted [Event Build Brief](event-build-brief-template.md) covering the research question, interval, evidence boundary, causal role map, roster, and semantic skeleton | Does not authorize participant production or code |
| Define participants | Reviewed Agent Definitions and Population Models with evidence, a lightweight semantic interface review, and shared publication-facing interface coverage | Does not determine release membership or implementation |
| Release the semantic roster | Hash-pinned inventory of the accepted participant products | Remains non-executable and makes no validity claim |
| Close scenario and mapping | Event Scenario Definition, interface closure, and consolidated carrier mapping | Mapping cannot add scenario meaning; scenario cannot supply participant behavior |
| Configure a purpose | Versioned actor/unit assembly, opening records, selections, sensitivities, and completion criteria | Configuration remains non-executable |
| Admit the configuration | Schema, canonical identity, references, failure classes, fail-closed loading, and a static receipt | Admission supplies neither policy behavior nor a runtime carrier |
| Bind a minimal lineage | Exact carrier projection and only the participant/environment policies needed for the selected lineage | Unselected roles and policies remain unbound |
| Review conformance | Focused negative cases, deterministic trace/replay evidence, implementation review, and reusable method findings | Stops before broad simulation or scientific evaluation |
| Realize complete Rule behavior | Independent Policy Realization covering every configured actor capability, decision commitment, intent, selected policy, required lifecycle, and declared failure behavior | Does not alter the accepted semantic configuration or authorize a run by itself |
| Assemble full-roster execution | An executable successor package with exact semantic parents, complete carrier projection, participant policies, environment/reducer ownership, clock, routes, exogenous inputs, and fail-closed admission | Starts no run until the exact package and output boundary pass preflight |
| Close a generated event graph | Repeated same-input Rule runs with identical trace and seals, successful replay, a trace-derived generated EPG, and compact integrity evidence | Establishes engineering mechanism coverage only, not calibration, historical fit, or scientific validity |

Some early H2EPR release records identify these phases as E0 through E7. The
names above are the maintained workflow vocabulary; the older identifiers
remain useful for interpreting those records.

The final three phases are optional extensions of a conformance-complete
event, not new requirements for every event build. They may be combined into
one release cycle when policy, assembly, run, and graph evidence remain
separately identifiable.

When that extension is authorized, use the
[full-roster Rule-execution Skill](skills/full-roster-rule-execution/SKILL.md)
and its compact
[execution-cycle template](execution/execution-cycle-closeout-template.md).
They preserve the three product boundaries without requiring three parallel
plans, approval records, or status documents.

Scenario design and carrier mapping may inform one another, but both retain
their own authority. Configuration admission and lineage binding may be
reviewed in one bounded engineering change only when their outputs and
acceptance questions remain separate.

## Opening and closing phases

Open a new event with the
[Event Build Brief template](event-build-brief-template.md), instantiated as
the event's single coordination entry under [`events/`](events/README.md). A
small event may keep its role map, roster, and semantic skeleton in the brief;
a larger event may link separate versioned artifacts. In either case the brief
remains the authority for the primary question, evidence and exposure boundary,
current authorization, and scope-change policy. It is not a full Scenario
Definition or an authorization for every phase on the roadmap. Complete its
minimum profile and use conditional extensions only when the event triggers
them.

Apply the [phase closeout checklist](phase-closeout-checklist.md) before
declaring any maintained phase complete, not after every edit, artifact, role,
or production batch. Record the result in the existing artifact that owns
closure whenever possible. The checklist provides common mainline,
minimality, authority, evidence, integrity, and handoff questions while
preserving the more specific verdicts of scholarly, semantic, carrier,
configuration, or implementation reviews. Its core is intentionally short;
the checks do not require separate reports or sign-offs, and phase- and
risk-specific questions apply only to surfaces changed by the work.

## Protected inputs and construction exposure

Choose the construction and claim mode before reading target material. Unless
post-seal evaluation is explicitly authorized, repository searches, file
inventories, retrieval indexes, prompts, and working sets exclude
`reference_epg.json`, held-out suffixes, and evaluation-only directories. A
Reference filename appearing in a checksum inventory may be verified as an
identity without opening its content.

If a human, tool context, or builder sees protected target content, record the
exposure and treat its target-specific descendants as full-draft-exposed. Do
not relabel that context as clean. This operational rule applies to ordinary
repository audits as well as event construction; it does not require a
held-out experiment for routine architecture or method work.

Strict continuation, clean-builder, domain-transfer, and post-seal evaluation
gates apply only when the corresponding claim or phase is separately
authorized. They are not prerequisites for closing an ordinary event-framing,
participant, scenario, or bounded engineering phase.

## Phase record

Each completed phase must leave a discoverable record in an existing brief,
manifest, release README, review, decision, or receipt. Together, the records
must identify:

1. the event and phase;
2. exact inputs and their identities;
3. purpose, authorized endpoint, and excluded work;
4. outputs and acceptance status;
5. verification and unresolved findings; and
6. the next legal action and its entry conditions.

At closeout, use the project checklist to confirm that the work still answers
the event question and is no deeper than necessary to test the intended
interface. Avoid creating a second tracker when a brief, release manifest,
review, decision, or receipt already carries this information.

## Failure routing

| Finding | Owning layer |
|---|---|
| Source, chronology, participant availability, or historical claim error | Evidence research |
| Representation, mechanism, decision, parameter, or falsifier error | Participant research or Definition |
| Institution, world state, routing, delivery, lifecycle, resource, adjudication, or termination gap | Event Scenario Definition |
| Actor assembly, structural selection, opening record, sensitivity, or declared-purpose error | Scenario Configuration |
| Semantic loss, ambiguous released identity, or carrier mismatch | Consolidated mapping |
| Schema, canonicalization, hash, reference, or admission error | Configuration admission |
| Hidden default, policy mismatch, or implementation-only state | Binding or policy implementation |
| Missing actor, commitment, intent, selected-policy, lifecycle, or failure coverage | Policy Realization or executable-package admission |
| Nondeterministic transition, trace, seal, or replay failure | Runtime and event-process implementation |
| Graph item without trace provenance, unresolved graph identity, or nondeterministic compilation | H2EPR graph compiler |
| Empirical or historical comparison problem | Separately authorized evaluation |

## Runtime preflight boundary

Static configuration admission verifies the exact semantic identities,
configuration shape, references, binding requirements, and deterministic
receipt. Runtime credentials, distributed resources, output locations,
timeouts, and post-run quality intake belong to a later experiment preflight
and are required only when a run is authorized.

## Completed cross-event baseline

The Panic of 1907 and SingHealth Data Breach events have each completed all
phases through one bounded lineage-conformance case. Both include an accepted
roster release, consolidated mapping, Event Scenario Definition,
non-executable Scenario Configuration, static admission, minimal
three-participant binding, and deterministic trace and replay evidence.

Together they exercise the same stage responsibilities across a financial
crisis and a healthcare cybersecurity event while retaining event-specific
participants, semantics, policies, identifiers, and causal checks. A separate
executable successor for each event closes full-roster Rule execution, replay,
and a generated event graph. The second event consumes the same event-neutral
H2EPR closure and custody kernel while retaining its own participant,
institutional, time, and graph semantics.
Neither event includes calibration, held-out evaluation, or a
historical-validity claim.

The separately authorized full-roster Rule-execution program built executable
successors from the frozen semantic parents, first for Panic and then for
SingHealth, without changing what either earlier release established. The
[cross-event conformance release](execution/cross-event-conformance-v0.1/)
now closes the shared run-document, replay, generated-graph, framework, and
claim boundaries. This is the completed engineering endpoint for the two-event
baseline, not an authorization for deeper modeling, calibration, or scientific
evaluation.
