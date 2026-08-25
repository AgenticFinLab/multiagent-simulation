# SingHealth classification-and-institutional-escalation participant interface

## Purpose

This account examines whether the six R2 participant models form a coherent
information, authority, action, and result structure between operational
integration, senior classification and reporting, and SingHealth governance.
It extends the accepted [R1 detection-and-escalation interface](r1-detection-and-escalation.md)
without transferring R1 private state or the completed historical outcome to
an R2 participant.

The reviewed products are:

- [IHiS operational and SCM management](../../../populations/defines/singhealth_data_breach/ihis-operational-and-scm-management.md);
- [SingHealth Group Chief Information Officer](../../defines/singhealth_data_breach/singhealth-group-chief-information-officer.md);
- [IHiS Cyber Security Governance Director and healthcare Sector Lead](../../defines/singhealth_data_breach/cyber-security-governance-director-and-healthcare-sector-lead.md);
- [IHiS Chief Executive Officer](../../defines/singhealth_data_breach/ihis-chief-executive-officer.md);
- [SingHealth Deputy Group Chief Executive Officer for organisational transformation and informatics](../../defines/singhealth_data_breach/singhealth-deputy-group-chief-executive-officer.md);
- [SingHealth Group Chief Executive Officer](../../defines/singhealth_data_breach/singhealth-group-chief-executive-officer.md); and
- the shared [participant evidence](../../../events/singhealth_data_breach/participant-evidence-v0.1.md).

## Cross-role causal chain

```text
R1 participant finding or escalation intent
  -> scenario delivers bounded content to an operational or senior route
  -> operational-management unit correlates role-local accounts and may seek
     verification, convene review, assign follow-up, or escalate
  -> GCIO receives a source-preserving account and selects distinct IHiS and
     SingHealth routes without merging their knowledge or authority
  -> Sector Lead assesses classification and may report through the CSA route;
     IHiS CEO reviews evidence, assigns response, and may direct that route
  -> SingHealth Deputy GCEO and GCEO receive their own delivered accounts and
     choose governance reporting, outreach preparation, consultation, audience,
     and channel intents
  -> institutional processes own delivery, authoritative category, reporting,
     investigation, notification approval, execution, and external response
  -> delivered results, failures, expiry, or material new evidence reopen the
     relevant participant choice
```

No participant owns the whole chain. Correlation is not classification;
classification is not report delivery; executive direction is not recipient
execution; preparation is not notification approval; and a communication
recommendation is not patient contact.

## Product surfaces

### Operational and SCM management role set

Each unit observes only delivered role-local accounts, meetings it attends,
verification results, available management routes, and intent feedback. It may
gather accounts, convene review, request verification, assign follow-up, or
escalate a qualified concern. Units retain distinct functional scope and
private memory. Composition, assignment, delivery, technical execution, and
senior response remain external.

### SingHealth GCIO office

The GCIO observes delivered operational accounts and later technical,
executive, Sector Lead, SingHealth, and patient-impact updates. It may clarify,
convene, route a concern to IHiS leadership, notify SingHealth management, seek
SingHealth reporting advice, or provide an impact update. It does not own the
recipient's classification, direction, governance decision, or response.

### CSG Director and healthcare Sector Lead office

The Sector Lead observes delivered incident accounts, CII indicators,
verification, applicable reporting context, executive briefing state and
direction, capacity context, and report feedback. It may seek verification,
form a bounded category proposal, request executive briefing, report through
the CSA route, notify authorized leadership, or follow up a report. It does not
own CSA receipt or response and cannot use its officeholder's concurrent MOH
appointment as unbounded authority.

### IHiS CEO office

The IHiS CEO observes delivered executive briefs, supporting evidence, Sector
Lead assessments, GCIO updates, investigation capacity, capacity context, and
intent feedback. It may request evidence, assign investigation, direct the
Sector Lead reporting route, or issue an executive update. It does not
self-realize classification, reporting, investigation, or response.

### SingHealth Deputy GCEO office

The Deputy GCEO observes delivered GCIO accounts, GCEO direction, impact and
integrity updates, consultation records, readiness status, and intent feedback.
It may route the incident, seek MOH reporting, mobilize reversible outreach
preparation, propose an audience or plan, and report readiness. It does not own
GCEO or MOH receipt, notification approval, execution, or patient response.

### SingHealth GCEO office

The GCEO observes only its delivered incident and unauthorized-access
information, Deputy GCEO proposals, consultation records, readiness summaries,
and intent feedback. It may direct the MOH reporting route, request and consult
on an outreach plan, advise an audience, or recommend a primary channel. It
does not assign every collective rationale to one person or make its
recommendations self-executing.

## Interaction closure

| Sender intent | Route and content | Recipient observation and possible response | Environment-owned result |
|---|---|---|---|
| R1 technical unit `share_technical_finding` or R1 office escalation | Named operational-management unit; source, event time, bounded finding, uncertainty, local action, and requested attention | `delivered_role_local_account`; the unit may gather another account, verify, convene, assign follow-up, or escalate | Admissibility, delivery, access to attachments, interpretation, technical state, and later response |
| Operational unit `request_operational_account`, `request_fact_verification`, or `assign_operational_follow_up` | Named R1 technical or operational unit; bounded question or task, scope, source, urgency, and reply route | R1 `peer_or_management_request` or `security_response_request` where assigned; the recipient chooses within its own authority | Delivery, authority check, access, work, returned evidence, delay, refusal, and technical effect |
| Operational unit `convene_cross_functional_review` | Named responsibility holders and meeting process; purpose, bounded evidence, open questions, required functions, urgency, and proposed time | Attending units receive only the delivered `coordination_meeting_record`; each retains its own interpretation and follow-up choice | Admissibility, invitations, attendance, presented material, decisions, cancellation, and timing |
| Operational unit `escalate_operational_concern` | Named GCIO route; sources, event time, known facts, uncertainty, actions, open questions, and requested decision | GCIO `delivered_operational_account`; clarify, convene, or escalate under `DC-GCIO-1` | Delivery, acknowledgement, interpretation, executive or Sector Lead response, and further routing |
| GCIO `request_operational_clarification` | Named operational-management unit; cited account, missing fact, scope, urgency, and review condition | Unit `delivered_role_local_account`; gather, verify, assign, or return a bounded account within its own authority | Delivery, access, returned content, delay, failure, and technical result |
| GCIO `convene_management_review` | Authorized IHiS participants and meeting process; current account, uncertainty, open questions, required offices, and proposed time | Each attending represented office receives only its delivered brief, meeting record, or lifecycle notice and applies its own procedure | Scheduling, attendance, material presented, completion, cancellation, decisions, and timing |
| GCIO `escalate_to_ihis_leadership` to the Sector Lead | Sector Lead route; qualified incident account, sources, uncertainty, actions, and requested classification attention | Sector Lead `delivered_incident_account`; assess, verify, brief, classify, or report under `DC-SL-1`--`DC-SL-3` | Delivery, acknowledgement, institutional category, report issuance, report delivery, and external response |
| GCIO `escalate_to_ihis_leadership` to the IHiS CEO | CEO route; qualified incident account, sources, uncertainty, actions, and requested executive decision | CEO `delivered_executive_incident_brief` or `gcio_update`; request evidence, assign investigation, issue a bounded update, or direct reporting | Delivery, acknowledgement, executive interpretation, recipient action, investigation, and response effect |
| Sector Lead `request_executive_briefing` | IHiS CEO and meeting process; account, category question, uncertainty, urgency, participants, and proposed time | CEO `delivered_executive_incident_brief` after delivery or completed briefing; review evidence and issue a bounded direction | Scheduling, attendance, presented content, completion, cancellation, and decisions |
| IHiS CEO `request_executive_incident_briefing` | GCIO, Sector Lead, named IHiS manager, and meeting process; account, questions, uncertainty, urgency, and proposed time | Addressed participants receive the bounded request; the CEO receives only material actually delivered through the completed brief or meeting | Scheduling, attendance, content presented, completion, cancellation, and decisions |
| IHiS CEO `request_supporting_evidence` or Sector Lead `request_classification_verification` | Named technical, operational, investigation, or GCIO route; exact claim, source, requested check, urgency, and review condition | Addressed participant observes only the delivered bounded request and may act within its own model or assigned process | Delivery, authority and access, execution, evidence, delay, expiry, or failure |
| IHiS CEO `direct_sector_lead_reporting` | Sector Lead route; sender capacity, evidence summary, urgency, expected qualification, and review condition | Sector Lead `ihis_executive_direction`; reassess and choose its own classification and reporting intent under `DC-SL-2`--`DC-SL-4` | Delivery, acknowledgement, Sector Lead decision, report issuance, CSA receipt, and response |
| Sector Lead `propose_incident_category` | IHiS executive, GCIO, or authorized reporting process; proposed category, evidence basis, uncertainty, and supersession relation | CEO `sector_lead_assessment` or GCIO `sector_lead_update` when addressed; recipients retain independent assessment and action | Delivery, institutional recording, acceptance, rejection, correction, and authoritative category |
| Sector Lead `report_cii_incident_to_csa` | CSA reporting route; sender capacity, incident account, proposed category, uncertainty, actions, and open questions | CSA remains an external institutional recipient; returned feedback may become `report_lifecycle_notice` | Admissibility, delivery, acknowledgement, requests, classification use, response, and further action |
| Sector Lead `notify_authorized_healthcare_leadership` | Named IHiS, MOHH, or MOH leadership route; sender capacity, facts, uncertainty, category and report status, and requested attention | An addressed CEO may receive a bounded brief or Sector Lead assessment; other recipients remain external and return only delivered feedback | Delivery, acknowledgement, interpretation, direction, further routing, and institutional action |
| Sector Lead `request_report_status` | CSA or authorized reporting process; report reference, sender capacity, issue time, urgency, and requested status | Returned acknowledgement, status, correction request, failure, or response becomes a delivered `report_lifecycle_notice` | Delivery, recipient search or review, authoritative status, response, delay, or failure |
| IHiS CEO `assign_investigation_lead` | Named investigation route; scope, authority, expected outputs, dependencies, and review condition | Assigned process observes the delivered direction; participants represented elsewhere receive only separately routed tasks | Acceptance, staffing, access, work, findings, operational effect, progress, delay, or failure |
| IHiS CEO `issue_ihis_executive_update` | Authorized IHiS executive or management route; known facts, uncertainty, open questions, active directions, and observed report state | GCIO `ihis_executive_direction` or Sector Lead `ihis_executive_direction` when addressed; each recipient retains independent assessment | Delivery, acknowledgement, interpretation, recipient action, further direction, and institutional use |
| GCIO `notify_singhealth_management` to the Deputy GCEO | Deputy GCEO route; source-preserving incident account, uncertainty, actions, and requested attention | `delivered_gcio_incident_update`; clarify, notify the GCEO, request MOH reporting, or begin bounded preparation | Delivery, acknowledgement, interpretation, institutional direction, and further reporting |
| GCIO `notify_singhealth_management` to the GCEO | GCEO route; source-preserving incident account, uncertainty, actions, and requested attention | `delivered_incident_update`; request detail or direct governance reporting under `DC-GCEO-1` | Delivery, acknowledgement, interpretation, reporting action, and further consultation |
| GCIO `request_singhealth_reporting_advice` | Named Deputy GCEO, GCEO, or SingHealth governance route; incident account, uncertainty, available route, and requested advice | Deputy `delivered_gcio_incident_update`, GCEO `delivered_incident_update`, or external governance observation; a reply returns only after delivery | Delivery, advice, authorization, report preparation, institutional action, delay, or failure |
| Deputy GCEO `notify_singhealth_gceo` | GCEO route; qualified account, known facts, uncertainty, open questions, and requested attention | GCEO `delivered_incident_update`; request detail, direct MOH reporting, or request planning | Delivery, acknowledgement, interpretation, direction, and institutional action |
| GCEO `direct_moh_reporting` or Deputy GCEO `request_moh_reporting` | Authorized SingHealth reporting route; qualified incident account, uncertainty, route, urgency, and review condition | MOH remains an external institutional recipient; any returned advice appears only through a delivered consultation or lifecycle record | Preparation, authorization, delivery, MOH receipt, advice, action, delay, or failure |
| GCIO `provide_patient_impact_update` | Deputy GCEO or GCEO route; source, affected category or interval, uncertainty, freshness, and correction relation | Deputy `investigation_scope_update` or GCEO `delivered_incident_update` when addressed; revise the relevant governance or outreach choice | Delivery, acknowledgement, plan revision, notification decision, execution, and patient response |
| Deputy GCEO `request_incident_clarification` or GCEO `request_incident_detail` | Named GCIO, investigation, data, consultation, or counterpart executive route; cited account, bounded question, source, urgency, and review condition | Addressed represented participant receives only a compatible delivered request or direction; returned content becomes the requester's source-specific update | Delivery, access, reply, evidence, correction, delay, expiry, or failure |
| Deputy GCEO `mobilize_outreach_preparation` | Named data, communications, outreach, or operational route; provisional scope, authority boundary, dependencies, privacy constraints, and review time | External preparation process returns `outreach_readiness_status` through delivery; no patient observation is created by preparation | Acceptance, staffing, list work, drafts, rehearsal, readiness, cost, delay, cancellation, or failure |
| GCEO `request_outreach_plan` | Deputy GCEO or named outreach-planning route; evidence basis, required questions, constraints, dependencies, and review time | Deputy `singhealth_gceo_direction`; clarify, prepare, propose, or report readiness under `DC-DGCEO-2`--`DC-DGCEO-3` | Delivery, preparation, proposal content, readiness, delay, or failure |
| Deputy GCEO `propose_notification_audience`, `propose_notification_plan`, or `provide_outreach_status` | GCEO and authorized consultation process; evidence basis, scope, uncertainty, dependencies, and requested decision | GCEO `deputy_gceo_outreach_proposal` or `notification_readiness_summary`; consult, advise, recommend, or request revision | Delivery, review, collective consultation, approval, modification, resource allocation, and execution |
| GCEO `consult_on_outreach_plan` | Deputy GCEO, MOH, or named consultation process; proposal, known facts, uncertainty, authority boundary, options, and requested advice | Deputy `interagency_consultation_record` when addressed; other participants remain external and return only their delivered statements | Delivery, participation, advice, objection, agreement, modification, delay, or no response |
| GCEO `advise_notification_audience` or `recommend_primary_notification_channel` | Deputy GCEO and authorized outreach process; bounded recommendation, evidence basis, constraints, contingency, and review condition | Deputy `singhealth_gceo_direction` or consultation record when delivered; revise plan, preparation, or status within its authority | Delivery, interpretation, collective adoption or rejection, execution, message delivery, and patient response |

Every represented route has a sender-owned intent, externally adjudicated
delivery, recipient-owned observation and interpretation, and externally owned
result. An undelivered message cannot update the recipient, and a sender may
learn failure or completion only through a delivered lifecycle record.

## Information and state boundaries

- Operational units retain separate role type, assignment, private assessment,
  open verification items, consolidated account, and intent lifecycles.
- The GCIO, Sector Lead, IHiS CEO, Deputy GCEO, and GCEO each retain a separate
  assessment and recipient-specific intent history. Reporting lines and
  meeting attendance do not merge those states.
- A delivered account preserves sender, recipient, event time, source,
  uncertainty, freshness, known action, open question, and requested response.
- Category proposal, authoritative category, reporting direction, report
  issuance, delivery, acknowledgement, and external response are distinct.
- Investigation assignment, acceptance, execution, finding, and technical or
  operational effect are distinct.
- Outreach preparation, proposal, consultation, approval, execution, message
  delivery, and patient response are distinct.
- Concurrent IHiS and MOH appointments require an explicit acting capacity.
  They never create hidden cross-institution knowledge, authority, or action.
- Final attacker attribution, complete forensic scope, later inquiry judgment,
  and the completed notification outcome remain unavailable unless a valid
  event-time route delivers the relevant information.

## Authority and result boundaries

| Surface | Operational role set | GCIO | Sector Lead | IHiS CEO | Deputy GCEO | GCEO | External owner |
|---|---|---|---|---|---|---|---|
| Cross-team account | Gather, verify, correlate, and escalate | Receive, clarify, and route | Receive for classification | Receive for executive review | Receive for SingHealth governance | Receive for senior governance | Delivery, attachments, and source records |
| Incident assessment | Unit-local operational assessment | GCIO bounded assessment | Sector Lead bounded category assessment | IHiS executive assessment | SingHealth supervisory assessment | SingHealth GCEO assessment | Authoritative incident and legal state |
| Category and CSA reporting | None | Route to responsible offices | Propose category and issue report intent | Review and direct route, not classify for Sector Lead | None | None | Institutional category record, delivery, CSA receipt and response |
| Investigation and IHiS response | Assign bounded operational follow-up | Request clarification and route updates | Request classification evidence | Assign lead and mobilize response | Consume delivered impact updates | Consume delivered governance updates | Access, staffing, execution, findings, effects, and failure |
| MOH reporting | None | Seek SingHealth advice | Notify only within authorized capacity | No modeled MOH action in IHiS capacity | Request authorized route | Direct authorized route | Preparation, authorization, delivery, MOH receipt, advice, and action |
| Outreach planning | None | Provide bounded impact updates | None | None | Prepare and propose | Request, consult, advise, and recommend | Approval, authoritative audience, resources, execution, delivery, and response |

The distinction between the GCIO bridge, Sector Lead classification, IHiS CEO
direction, and SingHealth data-owner governance is causal. Swapping only names
changes nothing, but swapping their authority or delivered information changes
which intents are admissible.

## Shared decision situations

### Compressed 9 July management account

Operational units correlate fragmentary technical findings and may continue a
bounded review, verify, convene, or escalate. The GCIO acts only on the account
delivered to it and may route qualified uncertainty to distinct IHiS and
SingHealth recipients. The Sector Lead and IHiS CEO each act only on the
content delivered to that office. A single shared incident belief at this
point is inconsistent with the models.

### Material 10 July correction

Delivered evidence that suspicious queries returned data can revise the
Sector Lead and CEO assessments, reporting direction, and investigation
assignment. It does not retroactively change the 9 July account or
automatically inform SingHealth. Category, report issuance, delivery, and CSA
response remain separate even when the direction and classification occur in
close succession.

### SingHealth governance and outreach

The Deputy GCEO and GCEO receive distinct delivered accounts and retain
separate authority. Qualified MOH reporting and reversible outreach preparation
may proceed while impact develops. Later impact, integrity, consultation, and
readiness updates may revise audience and channel advice. No proposal,
recommendation, or preparation activity becomes approval or patient contact by
itself.

### Missing, delayed, or adverse result

An undelivered escalation creates no recipient observation. A failed evidence
request leaves its question open; a failed assignment does not begin an
investigation; an unacknowledged report is not received; and a failed outreach
route does not inform a patient. Each product retains lifecycle references and
finite reopening conditions, so an always-wait policy is inconsistent after
material new evidence, failure, or expiry.

## Integration implications

| Interface family | Required semantic distinction |
|---|---|
| R1-to-R2 transition | Preserve the originating R1 participant, bounded content, uncertainty, requested response, recipient, delivery, and lifecycle |
| Operational role set | Preserve unit type, assignment, responsibility, and private memory without creating a collective management mind |
| IHiS senior offices | Preserve GCIO routing, Sector Lead classification and reporting, CEO executive direction, and their separate information histories |
| Concurrent offices | Require explicit acting capacity and prevent IHiS authority or information from becoming MOH state |
| Institutional reporting | Separate concern, assessment, direction, report intent, issuance, delivery, acknowledgement, response, and authoritative record |
| Investigation and response | Separate assignment, authority, access, execution, finding, operational effect, and returned observation |
| SingHealth governance | Preserve Deputy GCEO and GCEO recipient-specific knowledge and decisions |
| Patient communication | Separate preparation, proposal, consultation, advice, approval, execution, delivery, and response |
| Delayed or adverse results | Preserve pending, acknowledged, completed, partial, failed, expired, cancelled, and superseded lifecycle states with causal references |

The six R2 products therefore form a closed participant account for the
bounded classification-and-institutional-escalation process. Government
recipients, technical and institutional execution, authoritative incident
state, completed containment, and patient response remain separate event
processes.

## Falsification conditions

The account must be revised if an operational unit's undelivered finding
changes a senior office, if reporting lines create shared private assessment,
if a concurrent appointment supplies hidden cross-institution authority, if a
classification or direction creates its own report, if a failed assignment is
treated as executed, if preparation becomes notification approval, if a
recommendation creates patient contact, or if exchanging Sector Lead, IHiS CEO,
Deputy GCEO, and GCEO authority leaves the predicted process unchanged.
