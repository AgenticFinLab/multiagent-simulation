# H2EPR Event Scenario Definition Template

> Status: working research template · event-bound · versioned

An H2EPR Scenario Definition describes the event world in which released
participant models interact. It is the scholarly authority for event time,
institutions, relationships, resources, information delivery, business
processes, adjudication, results, structural variants, and termination.

The Scenario Definition references the event roster, evidence ledger, Agent
Definitions, population models, and machine contracts. It does not restate
their participant behavior, source custody, or wire schemas. Exact executable
values belong to a versioned scenario configuration derived from the reviewed
Definition.

Use the ten modules below as the stable reading order. Add role- or
event-specific subsections only where they clarify a material mechanism.

## 1. Model overview

Begin with a compact table.

| Field | Description |
|---|---|
| Historical event | Event name and stable project identity. |
| Modeled interval | Start, end, temporal resolution, and any deliberately excluded periods. |
| Research questions | The event-process questions this scenario can address. |
| Semantic inputs | Roster Definition release, evidence boundary, and Agent/population versions. |
| Scenario form | Event-driven, phased, scheduled, or mixed. |
| Structural baseline | Conservative interpretation used by the baseline scenario. |
| Sensitivity variants | Evidence-bounded structural alternatives, if any. |
| State authority | Event-world processes that own institutional truth and authoritative transitions. |
| Evidence and model status | Exposure, calibration, validation, and appropriate claim boundary. |
| Scenario identity | Stable identifier and semantic version. |

Follow the table with a short account of the modeled phenomenon, the causal
process the scenario is intended to expose, and the most important limitation
on interpretation.

## 2. Event boundary and causal question

Begin with a concise account of the historical setting, focal episode, and
critical transition the model studies. Then state the event-process question
before describing operational choices.
Separate:

- processes the scenario explains endogenously;
- initial conditions that establish the selected boundary;
- exogenous events whose effects are modeled but whose decisions are not;
- adjacent actors or mechanisms deliberately excluded; and
- known outcomes that may be used only as exposed construction context or
  later evaluation material.

Describe the causal transitions of interest. Historical chronology may bound
the model, but it must not become a script that forces later outcomes.

Define what a successful run can demonstrate. Engineering closure, process
plausibility, calibration, historical reconstruction, and independent
validation are different claims.

## 3. Evidence, theory, and temporal boundary

Identify the claim sets and theoretical mechanisms used to construct the
world, institutions, relationships, exogenous inputs, and adjudication rules.
Reference ledger claim identifiers rather than copying source records.

For each material scenario mechanism, record:

| Element | Required account |
|---|---|
| Claim or theory basis | Supporting, bounding, competing, or contradicting claim references. |
| Scenario use | Initial condition, institutional rule, event input, state transition, parameter bound, or sensitivity alternative. |
| Event time | When the modeled fact or process applies. |
| Participant availability | Which participants may learn it, through which channel, and when. |
| Exposure and evaluation use | Construction, calibration, sensitivity, or reserved evaluation status. |
| Withdrawal consequence | What changes if the basis is reclassified or removed. |

Preserve disagreements and unavailable evidence as structural alternatives,
unknown values, or bounded assumptions. Do not replace an unresolved mechanism
with an arbitrary probability merely to make the scenario executable.

## 4. Temporal structure and exogenous inputs

Describe the clock, event ordering, phase structure, and decision cadence.
Phases organize causal opportunities; they do not prescribe historical
outcomes.

For each phase, state:

- entry conditions based on authoritative state or delivered events;
- participants and processes that may become active;
- information and resources that can change;
- permissible transitions, including persistence or reversal; and
- exit conditions.

List exogenous inputs in a separate table.

| Input | Source and event time | Delivery/visibility | State effect | Why exogenous | Sensitivity treatment |
|---|---|---|---|---|---|
| `<event input>` | `<claim or approved assumption>` | `<recipients and delay>` | `<authoritative effect>` | `<boundary reason>` | `<fixed, varied, or omitted>` |

An exogenous input may alter the world. It may not silently tell an Agent why
the input occurred or reveal a later result.

## 5. Participant assembly and causal ownership

Reference the accepted roster and semantic release. Do not rewrite participant
behavior inside the scenario.

Record the assembly needed by this event:

| Entity or unit | Released capability/Definition | Modeled decision interface | Authority owner | Resource owner | Scenario-owned dependencies |
|---|---|---|---|---|---|
| `<entity/unit>` | `<release identity>` | `<one actor or scoped population unit>` | `<authority record owner>` | `<resource ledger owner>` | `<routes, institutions, venue, or process>` |

Maintain these boundaries:

- one historical or legal entity has one canonical identity and resource
  owner, even when it composes several capabilities;
- population units retain host, institution, weight, private state, and
  observation scope;
- a coordinator, committee, intermediary, venue, and contributor do not own
  one another's choices or resources; and
- environment processes handle rules, routing, delivery, matching,
  adjudication, and effects rather than becoming hidden Agents.

If the scenario requires a new autonomous choice not present in the released
roster, stop and return to the roster/Definition process.

## 6. World, institutions, relationships, and resources

Define the minimum authoritative world needed to answer the research question.
Use one state owner for every fact.

| State family | Meaning and owner | Initial basis | Valid update events | Visibility | Invariants |
|---|---|---|---|---|---|
| `<state>` | `<institutional meaning and authority>` | `<claim/configuration source>` | `<adjudicated transitions>` | `<public/private/scoped>` | `<conditions that must always hold>` |

Cover, where material:

- institutional membership, mandate, jurisdiction, governance, and
  authorization;
- contractual, clearing, correspondent, committee, communication, market, and
  support relationships;
- resources, balances, collateral, capacity, control rights, reservations,
  commitments, transfers, and releases;
- operational access and service conditions; and
- venue, matching, settlement, and institutional procedures.

An Agent may observe, request, propose, authorize, or refuse a change. Only the
authoritative event-state process changes world, relationship, resource, or
business state.

## 7. Information production, routing, and observation

Separate world truth from information products and delivered observations.

| Information product | Producer and source state | Eligible recipients | Event/as-of time | Route and delay | Missing, stale, or disputed behavior | Provenance |
|---|---|---|---|---|---|---|
| `<information>` | `<producer/record>` | `<scoped recipients>` | `<time rule>` | `<delivery path>` | `<projection rule>` | `<required lineage>` |

Specify:

- public, private, institutional, relationship-scoped, and role-scoped
  visibility;
- production, issue, transport, delivery, receipt, acknowledgement, and
  business acceptance as distinct events;
- freshness, supersession, correction, dispute, and unavailability;
- participant-time admissibility and forbidden future information;
- compound-record version consistency; and
- the frozen observation identity recorded for each decision.

The scenario may project an authoritative record into a legal observation. It
must not expose current hidden state through a reference that a backend can
dereference.

## 8. Interaction, lifecycle, adjudication, and results

Define the shared business objects and processes through which participants
interact.

| Lifecycle family | Object identity and owner | Valid states | Transition causes | Idempotency/expiry | Result and later observation |
|---|---|---|---|---|---|
| `<request/case/...>` | `<stable identity/authority>` | `<ordered or branching states>` | `<intent, message, time, or exogenous event>` | `<duplicate and closure rule>` | `<typed result and delivery>` |

For every material intent family, distinguish:

```text
Agent decision
  -> action or message intent
  -> validation and institutional admissibility
  -> scheduling and feasibility
  -> execution, partial effect, delay, no effect, or failure
  -> authoritative result and state delta
  -> later delivered observation
```

Record authority, target, resource, relationship, precondition, concurrency,
and causal-lineage checks. Invalid, unauthorized, duplicate, expired, and
infeasible attempts remain visible in the auditable execution record; derived
implementations may not silently repair them.

## 9. Operationalization, variants, termination, and identity

Explain how scenario concepts become inspectable state, transitions, and
configuration choices without duplicating machine schemas.

For every scenario or environment parameter, record its meaning, unit or
category, admissible range, source class, identification status, owning
mechanism, and sensitivity use. Exact run values belong to a versioned
configuration.

Define structural variants by the one unresolved mechanism they change. State
their shared fixed boundaries, conservative baseline, sensitivity purpose,
and evidence that would retire either interpretation. The selected variant
must enter scenario and run identity.

Define termination and failure separately:

- normal completion conditions;
- time or phase horizon;
- unresolved pending-object treatment;
- invariant violation and fail-closed behavior;
- incomplete-run status; and
- conditions that make a run incomplete or ineligible for downstream analysis
  or evaluation.

The associated reproducibility record should pin the accepted participant
release, Scenario Definition, configuration, structural interpretation, actor
assembly, implementation policy, random seed, and applicable interface
versions. Exact interface placements and carrier decisions belong in the
derived interface-closure record; paths and hashes belong in promotion or run
manifests, not in this scholarly document.

## 10. Worked cases, falsification, limitations, and provenance

Use a small set of high-information cases before broad coverage. Include
ordinary interaction, missing information, stale or disputed input, authority
failure, duplicate intent, partial result, adverse result, competing resource
claims, and a structural-variant difference where relevant.

For each case record:

- evidence class and decision-time boundary;
- authoritative prestate;
- observations actually delivered to each participant;
- permitted intents and invalid attempts;
- adjudication and result owner;
- expected causal record and state transition; and
- the controlled perturbation and predicted difference.

Add event-level falsifiers for causal ownership, information leakage,
relationship and resource conservation, lifecycle closure, phase transitions,
result separation, replay, and scenario minimality. State which findings would
revise the scenario, a participant Definition, the mapping, or the research
question.

Close with unresolved evidence, exogenous choices, aggregation losses,
unmodeled processes, exposed outcomes, calibration limits, evaluation limits,
conventional references, and a concise semantic version history.

Complete the derived
[Scenario interface closure](scenario-interface-closure-template.md) alongside
this document. It reconciles the released participant interface with the event
world without expanding the publication-facing narrative into a machine
mapping.
