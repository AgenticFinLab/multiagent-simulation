# H2EPR-0616 event semantic skeleton

- Version: `0.2`
- Status: accepted design boundary
- Event roster: [`agents/rosters/singhealth_data_breach.md`](../../agents/rosters/singhealth_data_breach.md)

This document fixes the shared event language used by the released participant
models. It is deliberately non-executable: it supplies no machine fields,
schedule, policy, parameter, numerical threshold, or historical outcome rule.

## Event frame

The modeled interval runs from the earliest evidenced compromise around
23 August 2017 through the public announcement on 20 July 2018, with
patient-notification delivery observed through 23 July. Event-specific
participant response begins on 18 January 2018, and the acute response window
begins on 11 June.

The causal opportunity sequence is:

| ID | Pre-state or opportunity | Transition to explain | Candidate decision or process owner | Authoritative result owner | Current status |
|---|---|---|---|---|---|
| `CT-1` | Exposed organizational or technical opportunity | Initial access becomes a persistent foothold | Threat actor; pre-existing security responsibilities remain institutional context | Scenario-owned access and system state | Supported outer boundary; exact initial action unresolved |
| `CT-2` | Foothold with bounded access | Access expands across credentials, hosts, and privileges toward SCM | Threat actor and IHiS operational interfaces | Scenario-owned authorization and network state | Supported for framing |
| `CT-3` | Access to SCM through compromised infrastructure | Queries, returned records, copying, and transfer produce material data exposure | Threat actor; IHiS access, database, and monitoring interfaces | Scenario-owned request, access, and disclosure results | Supported for framing |
| `CT-4` | Role-local alerts, unauthorized access findings, or anomalous activity | Signals are interpreted, communicated, classified, deferred, or escalated | Accepted R1 technical role set, SIRM, and Cluster ISO; accepted R2 operational role set, GCIO, Sector Lead, and IHiS CEO | Institutional communication, category, reporting, investigation, and incident-lifecycle processes | Supported from 18 January through the 10 July classification and reporting transition |
| `CT-5` | Suspected or confirmed incident | Local and inter-agency containment changes continued access and observed malicious activity | IHiS operational and management roles with SingHealth, MOH, and CSA response interfaces | Scenario-owned containment result and system state | Supported for framing |
| `CT-6` | Material breach and bounded organizational knowledge | Public announcement and patient notification are authorized and delivered | Accepted SingHealth Deputy GCEO and GCEO interfaces in routed coordination with IHiS, MOH, MCI, and CSA | Institutional notification approval, execution, and delivery process | Supported for planning choices through 20 July; external authorization and delivery remain outside the participant models |

These transitions organize causal opportunities. They are not a replay script,
and later breach scope or inquiry findings may not enter an earlier
participant observation.

## Sources of authority

| Question | Owner |
|---|---|
| event question, temporal boundary, exposure, and accepted scope | event coordination entry |
| roster membership and non-participant dispositions | research roster and Roster Definition release |
| participant knowledge, memory, decisions, and intents | Agent Definition or Population Model |
| source identity, claim support, conflicts, and participant-time admissibility | event-frame and participant-evidence records |
| access, system state, institutional relationships, routing, delivery, lifecycle truth, adjudication, and realized results | Scenario and authoritative reducer |
| representation, serialization, and version | machine contracts |
| projection of released meaning into the carrier | consolidated semantic mapping |

A participant emits an intent. The environment decides whether the request is
admissible and feasible and records its disposition, result, and authoritative
state effect. Message issue, transport, delivery, receipt, institutional
acceptance, execution, and observed result remain distinct.

## Shared event concepts

| Concept | Event-bound meaning | Owner | Required boundary |
|---|---|---|---|
| Event time | Ordered incident, detection, response, and notification intervals with uncertainty preserved | Evidence and scenario | Do not substitute publication or investigation dates for event time. |
| Information signal | A bounded observation available through a named technical or organizational channel | Participant Definition or population model; delivery by scenario | Researcher knowledge and full system state are not participant knowledge. |
| Authority | Permission to access a system, interpret or escalate an incident, order containment, or authorize notification | Institution and participant product | Technical capability, formal authority, and realized result remain distinct. |
| Access request and result | An attempted operation and its separately adjudicated authorization and system effect | Intent by participant; result by scenario | Requested, allowed, executed, observed, and copied are not synonyms. |
| Incident escalation | Communication that changes who can know, classify, or act on a suspected incident | Participant intent and institutional routing | Preserve sender, recipient, timing, content, and acknowledgement. |
| Containment | An authorized intervention intended to limit continued compromise or exposure | Participant intent; scenario result | Intention does not script success or immediate effect. |
| Notification | An authorized disclosure to an internal, governmental, affected, or public audience | Participant intent and institutional delivery | Separate decision, delivery time, audience, and information content. |
| Organization and unit | A real institutional boundary with defined information, authority, and accountability | Evidence and roster | Do not give a whole organization one mind when units differ materially. |

These concepts are semantic families, not a machine schema. Reused
reader-facing labels remain capability-scoped until consolidated mapping.

## Interaction routes

| Route | Required boundary |
|---|---|
| technical responsibility unit → SIRM or Cluster ISO | a local finding or review request is not delivered, understood, classified, or acted on until the corresponding institutional events occur |
| SIRM ↔ Cluster ISO | response coordination and independent accountability remain distinct; neither office automatically inherits the other's assessment or intent lifecycle |
| operational and SCM management → GCIO | a source-preserving operational account remains distinct from technical truth, delivery, recipient interpretation, and upward routing |
| GCIO → IHiS and SingHealth routes | dual accountability does not merge the two recipient histories, authorities, or responses |
| Sector Lead → CSA | proposed category, reporting direction, report creation, delivery, acknowledgement, and CSA response remain separate |
| IHiS CEO → Sector Lead and investigation route | executive direction and assignment do not perform classification, reporting, investigation, or containment |
| SingHealth Deputy GCEO and GCEO → MOH/MCI/CSA coordination | reporting, consultation, outreach proposal, notification approval, execution, and delivery remain separate |
| institutional notification → affected patients | audience selection and message delivery do not imply receipt, comprehension, or a patient decision interface |

MOH, MCI, and CSA are distinct institutional routes. Information delivered to
one does not become available to another without an explicit route and
delivery event.

## Event-owned state and lifecycles

The Scenario owns authoritative state for:

- identities, institutional roles, office availability, acting capacity, and
  responsibility assignments;
- accounts, credentials, hosts, sessions, network routes, applications,
  databases, monitoring, access grants, and technical control state;
- attack attempts, access adjudication, execution, queries, copying,
  disclosure, containment, and technical results;
- meetings, information products, delivery, acknowledgement, correction,
  freshness, and dispute;
- investigation requests, response-team activation, incident accounts,
  category proposals and decisions, reports, executive directions, and
  assignments;
- outreach proposals, consultation, notification approval, delivery, and
  affected-cohort consequences; and
- intent admission, progress, partial result, failure, expiry, cancellation,
  supersession, completion, and later observation.

Participant models retain only their declared assessments, open questions,
consumed references, and observed intent lifecycles. Those records must not
become competing copies of institutional or technical truth.

At minimum, later Scenario design must distinguish:

- signal production, projection, routing, delivery, freshness, correction,
  and acknowledgement;
- request issue, admissibility, assignment, execution, partial or failed
  result, expiry, and closure;
- incident suspicion, investigation, provisional assessment, institutional
  category, escalation, reporting, and reopening;
- local-control request, authority check, execution, technical effect, adverse
  effect, and observation;
- meeting request, invitation, attendance, presented material, decision,
  action ownership, and delivered record; and
- outreach preparation, audience and channel proposal, consultation,
  authorization, execution, delivery, and status feedback.

## Fixed structural boundaries

- The threat actor remains a bounded adversarial process with exogenous attack
  attempts. The baseline does not fix the historical attempt sequence or give
  the process participant-time policy.
- Technical administration and operational management remain
  responsibility-unit populations rather than collective organizational
  Agents. Units retain distinct observations, private state, access, and
  intents.
- IHiS and SingHealth office interfaces remain separate participants where the
  released roster establishes distinct information and authority choices.
  Institutional state and shared resources remain canonical Scenario truth.
- MOH, MCI, and CSA remain distinct routed processes rather than one government
  Agent or an automatically shared knowledge state.
- Endpoint users remain initial or exogenous context, and affected patients
  remain a consequence cohort for this question.
- Later investigation, attribution, liability, penalties, and reform are
  retrospective evidence or excluded aftermath.

Structural alternatives may vary attack pressure, route availability,
delivery delay, acting capacity, technical-result timing, and notification
delivery only within the accepted evidence boundary. The selected alternative
must enter configuration and run identity rather than participant policy.

## Lightweight interface preflight

The released products and their two shared interface accounts establish:

- 9 participant products: 7 Agent Definitions and 2 Population Models;
- 62 observation placements with 50 reader-facing labels;
- 44 replayable private-state placements;
- 29 decision situations; and
- 54 intent placements with 53 reader-facing labels.

Counts are derived from the release. Repeated labels do not imply common
identity, source, target, content, or authority. Scenario interface closure
must reconcile every placement to a source, route, time rule, lifecycle,
adjudication, result owner, and carrier disposition.

## Consolidated mapping entry

Consolidated mapping begins from the exact Roster Definition release. It may
introduce capability-scoped machine identities, actor assembly, registries,
validators, and event-specific Scenario meanings, but it may not add behavior,
historical knowledge, authority, or results absent from the release.

Contracts V1 remains the candidate carrier. A successor is justified only by
a concrete semantic loss that cannot be resolved through existing carriers,
internal mapping, or Scenario semantics. Mapping and Scenario Definition
remain non-executable until later configuration, admission, and binding stages
are separately completed.
