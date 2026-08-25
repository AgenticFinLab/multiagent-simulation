# H2EPR-0616 Event Scenario Definition

> Accepted `0.1.0` · event-bound scholarly specification · not an
> executable configuration

## 1. Model overview

| Field | Description |
|---|---|
| Historical event | SingHealth Data Breach, `H2EPR-0616` |
| Modeled interval | Analytic interval from about 23 August 2017 through the 20 July 2018 public announcement; patient-notification observation through 23 July |
| Temporal form | Event-driven causal clock with calendar-time bounds and explicit within-time ordering |
| Research question | Which interactions across information, authority, and response chains turned an initial intrusion into a large-scale healthcare data breach, and how did detection, escalation, containment, and notification timing alter the event's evolution? |
| Semantic inputs | Roster Definition release v0.1; accepted consolidated mapping v0.1; research roster v0.2; event semantic skeleton v0.2; seven Agent Definitions; two Population Models; two interface accounts |
| Scenario form | Phased opportunity process with endogenous participant choices and Scenario-owned delivery, adjudication, execution, and results |
| Structural baseline | `BOUNDED_ADVERSARIAL_OPPORTUNITY_PROCESS`; institution-preserving responsibility units; distinct IHiS, SingHealth, MOH, MCI, and CSA routes |
| Sensitivity variants | attack-pressure envelope; route availability and delivery delay; acting capacity; technical-result timing; institutional notification authorization and delivery |
| State authority | Scenario and reducer own institutional, technical, delivery, lifecycle, adjudication, result, and affected-cohort truth |
| Evidence and model status | Official-source, outcome-exposed, qualitative, uncalibrated, non-held-out construction |
| Scenario identity | `h2epr.scenario.0616.singhealth_data_breach`, semantic version `0.1.0` |

The Scenario exposes how fragmented technical evidence can remain local or move
through security, operational, executive, governmental, and patient-
communication routes. It does not replay the known chronology. Historical
dates bound opportunities and evidence availability; access, detection,
escalation, containment, classification, reporting, and notification outcomes
must still arise from admitted intents, institutional inputs, and reducer-
owned results.

The design can support process and conformance questions. It cannot establish
historical reconstruction, calibrated mechanism weights, prediction, policy
effectiveness, independent-construction claims, or scientific validity.

## 2. Event boundary and causal question

### Historical setting

SingHealth owned SCM and its data-governance boundary, while IHiS operated the
system and distributed cybersecurity, incident-response, service-management,
and reporting responsibilities across deployed offices and units. The selected
episode begins with an exposed technical opportunity before authoritative
initial access and follows possible persistence, access expansion, SCM
querying, signal production, organizational response, containment, reporting,
and notification.

### Endogenous processes

The Scenario explains interactions among:

- bounded attack attempts and Scenario adjudication of access, execution,
  persistence, queries, copying, and disclosure;
- technical-unit investigation, local-control, evidence-sharing, and security-
  review choices;
- SIRM and Cluster ISO clarification, coordination, response-team, containment,
  and escalation choices;
- operational-management gathering, verification, convening, follow-up, and
  qualified escalation;
- GCIO routing across distinct IHiS and SingHealth recipient histories;
- Sector Lead classification and CSA-reporting judgement;
- IHiS CEO executive review, reporting direction, and investigation assignment;
- SingHealth Deputy GCEO and GCEO reporting and outreach-planning choices; and
- institutional delivery, meeting, incident, reporting, containment, outreach,
  notification, and feedback processes.

### Initial conditions

The initial state contains:

- canonical IHiS, SingHealth, MOH, MCI, and CSA identities and their effective
  institutional relationships;
- office and responsibility-unit assignments, reporting routes, authority
  scopes, availability, and technical access known at the boundary;
- SCM, supporting hosts, accounts, credentials, applications, databases,
  monitoring, network routes, and controls at evidence-bounded qualitative
  states;
- an exposed opportunity and a bounded adversarial input process, but no
  authoritative assumption that an attack attempt succeeds;
- participant private state at each released initialization; and
- no undelivered future finding, completed breach scope, inquiry judgement,
  notification decision, or known historical result in participant state.

### Exogenous and deliberately external choices

External threat strategy remains outside the participant roster. The Scenario
receives bounded attack-attempt inputs and adjudicates their technical effects.
Endpoint-user choices are initial or exogenous context. MOH, MCI, and CSA
remain distinct institutional routes; decisions not assigned to a released
participant enter only as identified institutional inputs. Collective
notification authorization and patient delivery are institutional processes,
not hidden participant policies.

### Exclusions

The Scenario excludes:

- general pre-event preparedness except as an initial institutional or
  technical condition;
- attacker biography, objective learning, or strategic Agent behavior;
- endpoint-user or patient decision models;
- later attribution, liability, penalties, and reform as endogenous processes;
- a full national or public-healthcare cybersecurity system;
- fixed historical policies, calibrated parameters, or an all-roster runtime;
- retrospective or evaluation-only material outside the admitted
  participant-time evidence boundary; and
- claims of historical fit, prediction, policy effectiveness, or validity.

### Causal transitions

The accepted CT-1 through CT-6 sequence remains authoritative:

1. an exposed opportunity may become a persistent foothold;
2. access may expand across credentials, hosts, privileges, and SCM routes;
3. queries, returned records, copying, and transfer may create material
   exposure;
4. role-local signals may be interpreted, communicated, classified, deferred,
   or escalated;
5. local and inter-agency containment may change continued access and observed
   malicious activity; and
6. bounded organizational knowledge may support public announcement and
   patient-notification planning, authorization, and delivery.

A run may diverge at every transition. No phase entry or success condition
requires the historical result.

### Claim boundary

A completed run can demonstrate that the declared participant semantics,
Scenario processes, and machine carrier form a causally inspectable system. It
can compare structural or qualitative response paths when later configuration
authorizes them. It cannot show that one path was historically true, probable,
optimal, transferable, or causally identified.

## 3. Evidence, theory, and temporal boundary

### Scenario mechanism ledger

| Mechanism | Claim or theory basis | Scenario use | Participant-time rule | Withdrawal consequence |
|---|---|---|---|---|
| outer interval and compromise uncertainty | `0616-FR-C01` | analytic boundary and attack-opportunity envelope | completed chronology never enters earlier observations | move or narrow the boundary; do not choose a precise hidden access time |
| query, copying, and exposure separation | `0616-FR-C02` | technical lifecycle and result types | roles receive only routed queries, alerts, logs, and results | collapse no states; remove unsupported transition/detail instead |
| containment as a sequence | `0616-FR-C03`, `C12`, `R1-C06`, `R1-C16`–`C17` | local-control, execution, partial/adverse result, recurrence, and observation | later absence of activity is unavailable in advance | remove the affected control case or result assumption |
| notification horizon | `0616-FR-C04` | core and observation horizons; delivery process | public or patient-visible only after issue and delivery | shorten the observation horizon |
| SingHealth/IHiS responsibility split | `0616-FR-C05`–`C08` | institution, authority, assignment, and result ownership | legal findings constrain design but are not participant beliefs | reopen authority graph and roster fit |
| January participant response | `0616-FR-C17`–`C18`, `0616-R1-C03`, `R1-C15` | early signal, investigation, control, sharing, and escalation opportunities | later attacker attribution is prohibited | remove January opportunity/case without shifting later facts earlier |
| June fragmented information | `0616-FR-C09`–`C11`, `0616-R1-C04`–`C05`, `R1-C08`–`C10` | separate local products, routes, delivery, clarification, deferral, and escalation | each office sees only its delivered content | narrow routes or remove the fragmentation mechanism |
| July detection and cross-team integration | `0616-FR-C12`–`C14`, `0616-R1-C06`, `R1-C11`, `0616-R2-C03`–`C07`, `R2-C25` | technical response, meetings, source-preserving accounts, correction, and escalation | later query-result verification arrives only through its own update | remove unsupported meeting or account transition |
| classification and executive reporting | `0616-R2-C08`–`C17`, `R2-C26`–`C29`, `R2-C31`–`C32` | GCIO bridge, Sector Lead assessment/report, CEO direction/assignment, capacity boundary | office-specific deliveries and capacities never merge | reopen the affected office interface or institutional route |
| routed inter-agency response | `0616-FR-C14`–`C15` | distinct MOH, MCI, CSA delivery and coordination processes | delivery to one body does not inform another | remove or narrow the affected route |
| SingHealth outreach planning | `0616-R2-C18`–`C24`, `R2-C30` | reporting, preparation, consultation, audience, plan, channel, readiness, and update lifecycles | scope/integrity facts arrive only at their delivery times | remove the unsupported planning mechanism or case |
| representation and falsification | `0616-FR-C16`, `0616-R1-C12` | later review only; warns against a fixed failure policy | retrospective judgement is never an event-time observation | remove the falsifier, not participant authority |

The mechanism ledger uses evidence to constrain possible structures. It does
not convert reconstructed action or later criticism into a mandatory policy.

### Temporal admissibility

Event time and evidence-record time remain distinct. Each record carries:

- occurrence or effective interval;
- production and as-of time;
- delivery time per recipient;
- version, correction, and supersession relation;
- freshness or expiry rule; and
- evidence-use and participant-availability class.

Dates stated only retrospectively may bound Scenario truth without becoming
participant observations. Conflicts remain disputed versions or explicit
unknowns. Missing evidence is not replaced with a numerical default.

## 4. Temporal structure and exogenous inputs

### Clock and within-time order

The clock is event-driven with ordered calendar timestamps. When several
events share a timestamp, the authoritative order is:

1. exogenous input admission;
2. Scenario process or technical event;
3. information-product production;
4. route admission, transport, and delivery;
5. observation projection and freeze;
6. participant decision and intent/message issue;
7. authority, relationship, prestate, duplicate, expiry, and feasibility
   adjudication;
8. execution and typed result;
9. reducer-owned state delta; and
10. later information production or observation.

An actor decision freezes its observation versions. A later correction cannot
retroactively alter that decision basis.

### Causal opportunity phases

| Phase | Entry condition | Active processes | Exit condition |
|---|---|---|---|
| `P0_EXPOSED_OPPORTUNITY` | analytic boundary and institutional/technical initial state admitted | bounded attack attempts, access adjudication, monitoring | access succeeds, opportunity closes, or horizon advances |
| `P1_PERSISTENCE_AND_EXPANSION` | authoritative foothold or access result | access expansion, credentials, hosts, routes, monitoring | loss of access, material signal production, or SCM opportunity |
| `P2_EARLY_RESPONSE` | event-specific malware/callback or equivalent signal delivered from 18 January onward | technical investigation, local controls, sharing, security review, clarification/escalation | matter closes with recorded basis, remains open, or new scope appears |
| `P3_ACUTE_UNAUTHORIZED_ACTIVITY` | unauthorized credential/access evidence from 11 June onward | cross-unit investigation, security coordination, local controls, escalation | access contained, uncertainty persists, or SCM-query opportunity appears |
| `P4_DATA_ACCESS_AND_RESPONSE` | admitted SCM access/query attempt or material query signal | query execution, copying/disclosure, monitoring, controls, response coordination | activity blocked/fails, continues, or cross-team account is convened |
| `P5_INSTITUTIONAL_ESCALATION` | qualified cross-team account reaches an authorized senior route | meetings, verification, GCIO routing, classification, executive direction, reporting | report/notification routes proceed, concern closes, or remains unresolved |
| `P6_INTERAGENCY_AND_OUTREACH` | institutional incident/report input reaches SingHealth or government routes | containment coordination, investigation, impact updates, outreach planning and authorization | core horizon reached or response remains incomplete |
| `P7_NOTIFICATION_OBSERVATION` | authorized public or patient notice is issued, or 20 July horizon is reached | message delivery, correction, status feedback, affected-cohort recording | 23 July observation horizon or earlier explicit closure |

Calendar dates enable opportunities; they do not force phase transitions.
Reopening is permitted after new material evidence, failed/expired intent,
recurrent activity, correction, or changed authority/capacity.

### Exogenous input register

| Input | Basis and event time | Visibility | Authoritative effect | Boundary reason | Sensitivity |
|---|---|---|---|---|---|
| bounded attack attempt | `0616-FR-C01`–`C03`; within the analytic interval | none until a technical product is produced and delivered | creates an adjudicated access/execution attempt, not guaranteed success | attacker strategy is outside the roster | vary opportunity type, target envelope, ordering, and pressure without replaying the historical sequence |
| endpoint/account context | `0616-FR-C09`, `C17` | assigned technical units only when locally observable | establishes account, workstation, credential, or route preconditions | endpoint-user choice is not endogenous | omit or vary bounded opportunity context |
| institutional framework and appointments | `0616-FR-C05`–`C08`, `0616-R2-C10`–`C11`, `R2-C31`–`C32` | offices see only their effective duties and capacities | establishes relationships and authority scopes | pre-existing institutional state | vary only evidence-supported capacity interpretation |
| office availability or capacity | `0616-R1-C07`, `0616-R2-C31`–`C32` | affected office and routed recipients after delivery | changes availability or required capacity qualification | staffing and appointment events are outside participant policy | present, absent, delayed coverage, or capacity-qualified route |
| government/institutional response input | `0616-FR-C14`–`C15` | named recipient routes after delivery | supplies distinct MOH/MCI/CSA acknowledgement, coordination, or authorization event | those bodies are routed processes, not Agents | vary delay, no response, partial response, or route failure |
| notification authorization and delivery opportunity | `0616-FR-C04`, `0616-R2-C20`–`C24` | planning offices see authorization; public/patients only after delivery | admits or rejects execution and creates recipient-specific delivery results | collective authorization and patient behavior are outside the roster | vary authorization time, audience acceptance, channel capacity, delay, partial delivery, and correction |

## 5. Participant assembly and causal ownership

### Assembly

| Entity or unit | Released capability | Decision interface | Institutional host | Authority owner | Scenario-owned dependencies |
|---|---|---|---|---|---|
| technical responsibility unit | `technical_administration_and_line_security_staff` | one scenario-instantiated function-specific population unit | IHiS or deployed cluster assignment | unit role/access record | assigned systems, access, signals, delivery, controls, and results |
| SIRM office | `security_incident_response_manager` | one office actor | IHiS Security Management | SIRM office authority record | delivery, SIRT, technical state, capacity, containment and escalation results |
| Cluster ISO office | `cluster_information_security_officer` | one office actor | IHiS / SingHealth cluster interface | Cluster ISO authority record | delivery, response-team/report state, meetings, capacity and results |
| operational-management unit | `ihis_operational_and_scm_management` | one scenario-instantiated function-specific population unit | IHiS | unit responsibility record | meetings, routes, assignments, verification and results |
| GCIO office | `singhealth_group_chief_information_officer` | one office actor with dual accountability routes | IHiS and SingHealth interface | capacity-scoped office authority | delivery, senior routes, patient-impact products and recipient responses |
| Sector Lead office | `cyber_security_governance_director_and_healthcare_sector_lead` | one capacity-qualified office actor | IHiS with evidenced healthcare/MOH interface | Sector Lead capacity record | framework, category record, report lifecycle, CSA route and feedback |
| IHiS CEO office | `ihis_chief_executive_officer` | one capacity-qualified office actor | IHiS | IHiS CEO capacity record | brief delivery, reporting/investigation routes, assignment and results |
| SingHealth Deputy GCEO office | `singhealth_deputy_group_chief_executive_officer` | one office actor | SingHealth | Deputy GCEO authority record | GCIO/GCEO delivery, consultation, outreach process and results |
| SingHealth GCEO office | `singhealth_group_chief_executive_officer` | one office actor | SingHealth | GCEO authority record | delivered account, MOH route, consultation, authorization and delivery |

Office actors are scoped institutional units, not duplicate legal
organizations. IHiS and SingHealth retain one canonical institutional identity,
relationship graph, system/data ownership, and authoritative process state.
No actor inherits another unit's observations or private state.

### Causal ownership map

| Material choice or transition | Owner |
|---|---|
| investigate, request context, share finding, request review, or request local control | technical responsibility-unit Population Model |
| assess, coordinate, activate team, direct containment, seek assistance, escalate, or delegate coverage | SIRM Agent Definition |
| clarify, exercise independent accountability, coordinate reporting, or escalate | Cluster ISO Agent Definition |
| gather, verify, convene, assign follow-up, or escalate a qualified operational account | operational-management Population Model |
| route an account across IHiS/SingHealth or maintain patient-impact updates | GCIO Agent Definition |
| seek verification, propose category, brief, report to CSA, or maintain report lifecycle | Sector Lead Agent Definition |
| seek evidence, direct reporting, assign investigation lead, or issue executive update | IHiS CEO Agent Definition |
| route internally, prepare/revise outreach, propose audience/plan, or report readiness | Deputy GCEO Agent Definition |
| direct MOH reporting, supervise consultation, advise audience, or recommend channel | GCEO Agent Definition |
| access, execution, delivery, meeting, authority, category, report, assignment, containment, notification, and affected-cohort results | Scenario/institutional process and reducer |
| evidence support and participant-time admissibility | event evidence authorities |
| representation and serialization | Contracts V1 and accepted mapping |

## 6. World, institutions, relationships, and resources

### Authoritative state families

| State family | Owner and initial basis | Valid transition causes | Visibility | Invariant |
|---|---|---|---|---|
| institution and unit registry | Scenario; roster and institutional evidence | reviewed structural/configuration input only | public identity; scoped role detail | one canonical identity per institution/unit |
| relationship and assignment graph | Scenario; evidence-backed effective records | admitted appointment, assignment, coverage, or route event | scoped to affected offices/routes | no implicit transitive knowledge or authority |
| system, host, account, credential, route, application, and database state | Scenario/reducer; evidence-bounded initial state | admitted technical event or result delta | access- and delivery-scoped | actor belief never changes authoritative technical state |
| access and control grants | Scenario/reducer; role and system authority | authority change, expiry, revocation, or admitted control result | holder and authorized process | empty/unknown scope grants nothing |
| monitoring and information products | producing process | technical/system event, investigation, meeting, report, correction | only after eligible projection and delivery | stable ID/version/provenance |
| incident and response process | institutional process | admitted investigation, activation, assessment, category, report, containment, or closure event | recipient-specific delivered projections | participant proposal is not authoritative process truth |
| outreach and notification process | SingHealth/institutional process | admitted preparation, consultation, authorization, issue, delivery, correction | planning offices, named routes, public/cohort after delivery | approval and delivery are distinct |
| affected-cohort record | Scenario | authoritative exposure and notification-delivery result | cohort/public rules | no patient decision state is inferred |
| participant private state | reducer, capability-scoped initialization | declared decision, issued intent, or delivered notice/update | owning actor/unit only | no competing business truth |

### Institutional and relationship rules

- IHiS operation of SCM does not erase SingHealth ownership and supervisory
  responsibility.
- Deploying a unit into a cluster does not make all IHiS or SingHealth
  information available to it.
- GCIO dual accountability creates two explicit routes, not one shared
  recipient state.
- Sector Lead and IHiS CEO concurrent MOH appointments require a capacity
  reference on each authority claim or message; appointment alone grants no
  access to all MOH information.
- MOH, MCI, and CSA have distinct identities, routes, deliveries,
  acknowledgements, and process states.
- Meeting attendance conveys only presented material and the delivered record.
- A responsibility unit can act only on its assigned systems, relationships,
  and authority interval.

### Resource and conservation rules

The event uses qualitative or bounded technical and organizational resources:

| Resource | Owner/controller | Rule |
|---|---|---|
| system and data access | system owner; access-control process | an intent cannot grant itself access; execution requires an effective grant and target/version |
| credential/session control | account/system process; scoped technical controller | control requests may fail, be partial, expire, or create adverse effects |
| investigation and response capacity | institutional unit/office | assignment or coordination intent does not create staffing or completed work |
| meeting and communication capacity | institutional route/process | a request does not guarantee invitation, attendance, delivery, or acknowledgement |
| reporting and notification route capacity | responsible institutional process | issue, transport, delivery, and correction remain separately recorded |
| outreach readiness | SingHealth outreach process | mobilization/proposal does not equal authorization, delivery, or patient response |

No resource is duplicated across office actors. Reservations, competing
requests, execution, release, and effects are reducer-owned and versioned.

## 7. Information production, routing, and observation

### Information-product families

| Family | Source object | Produced fields | Eligible routes | Freshness/correction |
|---|---|---|---|---|
| technical signal | monitoring, host, account, session, query, control, or investigation result | source, target, event/as-of time, bounded value, uncertainty, access scope | assigned technical unit; later named recipients only through communication | superseding signal/result creates a new version |
| technical finding/account | unit-issued source-preserving product | observations, interpretation, uncertainty, local actions, open questions | peer, SIRM, Cluster ISO, operational unit, or meeting | correction never rewrites the delivered prior version |
| response or coordination status | SIRM/SIRT/institutional process | owner, activation, work, pending items, time, uncertainty | addressed security/management route | silence remains unresolved |
| meeting/consultation record | institutional meeting process | attendees, presented versions, questions, decisions, action owners | attendees and named recipients | later minutes/correction are separate versions |
| operational consolidated account | operational-management unit | source refs, known facts, uncertainty, actions, open questions, requested decision | GCIO or authorized senior route | compressed account retains sources and omissions |
| executive brief/direction | GCIO, Sector Lead, CEO, or institutional process | content, sources, capacity, requested decision/direction | named office routes | delivery and acknowledgement are separate |
| category/report product | Sector Lead/institutional incident process | basis, proposed/authoritative category, uncertainty, report content and lifecycle | IHiS, SingHealth, MOH, CSA as explicitly routed | revision/supersession preserves prior report |
| patient-impact/outreach product | investigation or SingHealth outreach process | scope, integrity, readiness, proposal, audience, channel, uncertainty | named SingHealth offices and authorized routes | each update has its own as-of and delivery time |
| lifecycle notice | reducer/institutional process | object/ref, lifecycle, reason, result refs, time | original issuer and named recipients | missing notice means unresolved, never success |

### Production and delivery chain

Every behaviorally material observation follows:

```text
authoritative source/version
  -> information-product production
    -> route and recipient admissibility
      -> transport and delivery event
        -> capability-scoped frozen projection
          -> decision record
```

Projection cannot dereference live world state. It records source/reference,
value/domain, event and as-of time, effective interval, delivery time,
freshness, uncertainty/dispute, provenance, visibility/scope, and consuming
decision situations. Compound records use one object/version reference plus
separately checked material fields.

### Missing, stale, and disputed information

- missing delivery means unavailable, not false or safe;
- delivered content does not imply comprehension, agreement, acceptance, or
  action;
- stale information remains visible with its as-of time and may trigger
  verification;
- disputed accounts coexist as source-qualified versions;
- a correction does not mutate the earlier delivered observation or decision;
- an office never sees another actor's private assessment or undelivered
  intent/result; and
- later breach scope, attacker attribution, inquiry conclusions, and
  evaluation facts are prohibited before their admissible time and route.

## 8. Interaction, lifecycle, adjudication, and results

### Canonical business objects

Each request, finding, message, meeting, investigation, control, incident
account, category proposal, report, direction, assignment, outreach plan,
notification, and result has:

- stable event-scoped object ID and kind;
- version and prior/superseding reference;
- issuer/producer, target/recipient, institution/capacity, and related object;
- event, issue, effective, expiry, and delivery times as applicable;
- authority, relationship, target, resource/capacity, and source refs;
- lifecycle state and idempotency/correlation key; and
- disposition, result, delta, and later-observation refs.

### Lifecycle registry

The authoritative lifecycle families and states are those fixed in the
consolidated semantic inventory: participant intent; information product;
investigation/verification; local control; meeting/consultation; SIRT
activation; incident assessment/category; report/notification; investigation
assignment; outreach plan; and attack/technical effect.

A duplicate with the same issuer, capability, semantic intent, target, object
version, and idempotency key is rejected or returns the prior disposition.
Materially changed evidence, expiry, failure, cancellation, supersession, or
new scope may create a new intent and correlation lineage.

### Adjudication ladder

For every intent or message, the Scenario checks in order:

1. exact actor, capability, Definition, observation, and decision identity;
2. intent type, parameters, target/object version, time, and expiry;
3. institutional capacity and authority scope;
4. required relationship, route, access, and recipient eligibility;
5. object lifecycle prestate and version;
6. resource/capacity ownership, availability, reservations, and conflicts;
7. duplicate/idempotency and concurrent-claim rules;
8. event-phase and structural-variant admissibility; and
9. execution feasibility.

Typed rejection remains in trace. Admission does not guarantee transport,
execution, effect, acknowledgement, institutional acceptance, or later
observation.

### Result families

| Intent family | Possible typed results |
|---|---|
| inspect/verify/request information | access denied; unavailable; delayed; partial; disputed; verified; failed; expired |
| communicate/escalate/report | route rejected; staged; transported; delivered; acknowledged; misaddressed; delayed; failed; corrected |
| convene/coordinate/activate | unauthorized; invitation partial; no attendance; activated; partially staffed; declined; failed; expired |
| classify/direct/assign | unauthorized capacity; accepted; rejected; superseded; partial compliance; no effect; reassigned |
| control/contain | infeasible; rejected; scheduled; executed; partial; effective; no effect; adverse; reversed |
| prepare/notify | preparation active; not ready; proposal accepted/revised/declined; authorization absent/granted; delivery partial/failed/completed/corrected |
| attack/technical attempt | inadmissible input; blocked; failed; executed; partial; persisted; detected; contained; later observed |

Only reducer-owned state deltas alter authoritative state. A later observation
may report a result but cannot create it retroactively.

### Cross-hop lineage

A forwarded account or report creates a new business object/hop linked to its
source object and version. It does not change the source issuer, original
recipient, prior delivery, or content. The minimum lineage is:

```text
technical source/result
  -> delivered technical finding
    -> security or operational decision
      -> qualified escalation/account
        -> GCIO/senior delivery and decision
          -> category/report or executive direction
            -> institutional delivery/result
              -> later status observation
```

Each hop retains separate intent, message, delivery, acknowledgement,
adjudication, result, and state-delta identities.

## 9. Operationalization, variants, termination, and identity

### Configuration boundary

A later non-executable configuration may select:

- modeled start/end and notification-observation horizon within the accepted
  interval;
- responsibility-unit instances, functional types, assignments, access,
  availability, and office-capacity records;
- qualitative initial technical and institutional states;
- one declared attack-pressure, route/delivery, capacity, technical-result,
  and notification variant;
- bounded sensitivity values or intervals;
- enabled participant capabilities and one later lineage slice; and
- normal/incomplete termination and pending-object treatment.

It may not define participant policy, invent source claims, set hidden success
outcomes, or make the full roster executable.

### Structural variants

| Variant family | Baseline | Allowed alternatives | Identity consequence |
|---|---|---|---|
| attack pressure | `BOUNDED_ADVERSARIAL_OPPORTUNITY_PROCESS` | lower/delayed/different source-bounded opportunity envelope; no fixed historical replay | pin family and selection |
| route and delivery | distinct named routes with explicit delay/failure | route unavailable, delayed, partial, misaddressed, corrected | pin route graph and timing policy |
| responsibility units | institution-preserving function-specific units | narrower set or changed composition with declared information loss | pin unit roster and assignments |
| office capacity | IHiS capacity unless a message/authority claim states otherwise | absent/covered office or evidence-supported concurrent capacity | pin capacity records and effective intervals |
| technical result | authority/prestate/feasibility adjudication | delay, partial, no-effect, adverse, recurrence | pin result-policy family, not the realized result |
| notification | separate planning, institutional authorization, issue, and delivery | delayed/declined authorization, partial delivery, correction | pin process variant, not historical success |

A structural choice is system-only. It becomes participant information only
through an eligible delivered product.

### Termination and unresolved work

- `CORE_HORIZON_REACHED`: 20 July boundary reached after processing all
  eligible same-time events; announcement is recorded only if it occurred.
- `NOTIFICATION_OBSERVATION_HORIZON_REACHED`: 23 July reached after
  processing eligible delivery/correction events.
- `EARLY_PROCESS_CLOSURE`: all attack, incident, response, and notification
  objects close before the horizon with no scheduled eligible event.
- `INCOMPLETE_WITH_PENDING_OBJECTS`: horizon reached with unresolved intents,
  messages, investigations, controls, reports, assignments, or notifications;
  every pending object is preserved.
- `INVARIANT_FAILURE`: identity, authority, lifecycle, resource, trace, or
  reducer invariant fails; no valid seal is produced.

No termination condition requires the historical breach, classification,
containment, announcement, or patient-notification outcome.

### Reproducibility identity

A later admitted run must pin exact release, roster, skeleton, Scenario,
mapping, configuration, assembly, structural variant, Contract, code, policy,
exogenous-input, time, and RNG identities. ParticipantArtifact and runtime
bundle hashes must change when capability composition, information boundary,
authority/resource projection, structural selection, or policy reference
changes.

This Definition creates none of those executable objects.

## 10. Worked cases, falsification, limitations, and provenance

### Case 1 — January signal without retrospective attribution

A security-engineering unit receives a malware/callback signal. Its projection
contains the then-visible address, host, time, uncertainty, and assigned
access, not the later command-and-control attribution. An investigation or
control may be admitted, fail, return partial evidence, or close with open
questions. Any escalation requires a separate issued and delivered intent.

Forbidden: giving the unit or SIRM the completed attack linkage because it is
known to the researcher.

### Case 2 — fragmented June findings

A database unit and a Citrix unit hold separate signals. Sharing one finding
does not deliver the other's evidence or make Security Management understand
their connection. The SIRM and Cluster ISO receive only their addressed
versions and may clarify, coordinate, escalate, or defer with a finite
reopening condition.

Perturbation: deliver a source-preserving cross-system connection earlier.
Expected change: the admissible escalation/coordination set may expand; no
particular action or success is forced.

### Case 3 — urgent local control with adverse or partial result

A technical unit issues a bounded control intent outside the ordinary
procedure. Authority, target version, scope, and conflict checks precede
execution. The result may be effective, partial, no-effect, adverse, delayed,
or failed. Later recurrence creates a new observation rather than rewriting
the earlier result.

Forbidden: treating intent admission as containment success.

### Case 4 — compressed account and later correction

Operational units convene and produce an account stating that query results
are unverified or believed empty. GCIO, Sector Lead, and IHiS CEO decisions
freeze that version. A later verification product that returned data is a new
version delivered on its own route. Earlier decisions remain traceable to the
compressed account.

Perturbation: delay or withhold the correction. Expected change: later
classification/reporting options and reasons change, but no actor receives the
future fact.

### Case 5 — cross-institution escalation lineage

A technical finding reaches security or operational management; a qualified
account reaches the GCIO; separate messages reach IHiS executive/Sector Lead
and SingHealth management routes; the Sector Lead may propose category and
report to CSA; the IHiS CEO may direct reporting or assign investigation.
Every hop retains source, capacity, delivery, acknowledgement, and result
identity.

Forbidden: delivery to GCIO becoming delivery to CSA, MOH, or SingHealth.

### Case 6 — concurrent office capacity

A Sector Lead or IHiS CEO officeholder also has an evidenced MOH appointment.
An intent lacking an explicit capacity and authority scope is rejected. A
capacity-qualified message uses only the corresponding route and cannot read
the other institution's undisclosed state.

Perturbation: remove the concurrent appointment. Expected change: capacity-
dependent routes close; ordinary IHiS authority remains.

### Case 7 — outreach preparation and notification

The Deputy GCEO may mobilize preparation and revise a proposal as scope and
integrity products arrive; the GCEO may direct reporting, consult, advise an
audience, or recommend a channel. Institutional authorization remains
separate. Delivery may be delayed, partial, failed, or corrected and creates
recipient-specific results.

Forbidden: a proposal or recommended SMS channel authorizing or completing
patient notification.

### Case 8 — duplicate, expiry, and replay

Reissuing the same intent with the same idempotency key returns or rejects
against the prior disposition. Failure, expiry, cancellation, supersession, or
material new evidence permits a new lineage-linked intent. Deterministic replay
reconstructs the same observations, decisions, dispositions, deltas, pending
objects, and seals.

### Event-level falsification plan

The Scenario design is contradicted or must be revised if evidence or
implementation demonstrates that:

- a material autonomous choice belongs to no released participant or accepted
  institutional process;
- office/unit information was automatically shared despite distinct delivery
  records;
- a participant legally owned authoritative technical, category, delivery, or
  result state that the Scenario assigns elsewhere;
- a required observation cannot be produced without revealing hidden current
  or future state;
- participant behavior requires a historical outcome as an input;
- no capability-scoped identity can distinguish reused semantic labels;
- Contracts V1 cannot preserve a required object/version, lifecycle,
  authority, result, or causal link after reasonable internal mapping; or
- deterministic replay cannot recover the same frozen decision basis and
  authoritative deltas.

### Limitations

The design is based principally on retrospective official inquiry material.
It is outcome-exposed and does not identify quantitative mechanism weights,
population composition, technical exploit mechanics, complete institutional
procedures, or counterfactual probabilities. Government and notification
processes are bounded institutional interfaces rather than Agent models.
Population-unit instantiation and every executable policy remain future,
separately reviewed work.

### References and provenance

Semantic and evidence authorities:

- H2EPR-0616 Roster Definition release v0.1;
- research roster v0.2 and event semantic skeleton v0.2;
- event-frame evidence v0.1 and participant evidence v0.1;
- seven Agent Definitions, two Population Models, and two interface accounts;
- H2EPR Event Scenario Definition and interface-closure templates;
- H2EPR Contracts V1; and
- the accepted H2EPR-0288 Scenario Definition as a method reference, not a
  source of SingHealth historical meaning.

`0.1.0` is the first accepted event-level Scenario Definition for H2EPR-0616.
It was accepted after complete release-interface closure, separate substantive
review, and owner resolution of `OD-SC-05` through `OD-SC-08`.

The accepted Definition adds no participant behavior. It assigns event-world
ownership, defines information and shared-process semantics, and identifies
the configuration choices required before implementation. Exact executable
values remain the responsibility of a separately reviewed, versioned Scenario
Configuration.
