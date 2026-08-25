# H2EPR-0616 consolidated semantic inventory

> `ACCEPTED_SEMANTIC_INVENTORY / NON_EXECUTABLE`

## 1. Fixed input and counting rule

- Release: `H2EPR-0616-ROSTER-DEFINITION-RELEASE-v0.1`
- Release manifest SHA-256:
  `188f5117f02958997f8e1140d3d19fcbada296b1750223d8b3025e1cf537625e`
- Release `SHA256SUMS` SHA-256:
  `fa92cc4d61dfbfafff97b12506deeb820ef51743b0ce315dcb470d98dec693f2`
- Carrier under review: H2EPR Contracts V1
- Construction exposure: full outcome exposed; no clean-builder, held-out,
  calibration, historical-validity, or scientific-validity claim

The release contains nine semantic products: seven Agent Definitions and two
Population Models. A product is a semantic authority, not automatically a
runtime actor. Counts below are placements in the exact released products;
reused labels remain separate until capability-qualified mapping is applied.

| Measure | Count |
|---|---:|
| semantic products and proposed capabilities | 9 |
| Agent Definitions | 7 |
| Population Models | 2 |
| decision situations | 29 |
| observation placements | 62 |
| distinct reader-facing observation IDs | 50 |
| private-state placements | 44 |
| intent placements | 54 |
| distinct reader-facing intent IDs | 53 |

## 2. Product inventory and runtime disposition

| Product | Proposed capability ID | Observations | Private state | Decisions | Intents | Runtime disposition |
|---|---|---:|---:|---:|---:|---|
| Technical administration and line security staff | `technical_administration_and_line_security_staff` | 5 | 4 | 3 | 5 | scenario-instantiated responsibility units |
| Security Incident Response Manager | `security_incident_response_manager` | 8 | 5 | 4 | 8 | one office-scoped actor |
| Cluster Information Security Officer | `cluster_information_security_officer` | 9 | 5 | 3 | 6 | one office-scoped actor |
| IHiS operational and SCM management | `ihis_operational_and_scm_management` | 5 | 4 | 3 | 5 | scenario-instantiated responsibility units |
| SingHealth Group Chief Information Officer | `singhealth_group_chief_information_officer` | 7 | 5 | 3 | 6 | one office-scoped actor |
| Cyber Security Governance Director and Healthcare Sector Lead | `cyber_security_governance_director_and_healthcare_sector_lead` | 8 | 6 | 4 | 6 | one office-scoped actor |
| IHiS Chief Executive Officer | `ihis_chief_executive_officer` | 7 | 5 | 3 | 5 | one office-scoped actor |
| SingHealth Deputy Group Chief Executive Officer | `singhealth_deputy_group_chief_executive_officer` | 7 | 5 | 3 | 7 | one office-scoped actor |
| SingHealth Group Chief Executive Officer | `singhealth_group_chief_executive_officer` | 6 | 5 | 3 | 6 | one office-scoped actor |

IHiS and SingHealth are canonical institutional entities. Office actors and
responsibility units are scoped sub-entities hosted by those institutions;
they do not create additional legal organizations, institutional resource
ledgers, or automatically shared knowledge. Population-unit count, functional
type, assignment, access, availability, and composition remain Scenario or
later configuration choices.

## 3. Observation inventory

### 3.1 Released observations by capability

| Capability | Reader-facing observation IDs |
|---|---|
| `technical_administration_and_line_security_staff` | `local_technical_signal`; `delivered_peer_finding`; `local_control_state`; `security_response_request`; `action_result_notice` |
| `security_incident_response_manager` | `delivered_security_signal`; `technical_investigation_update`; `delivered_response_request`; `incident_scope_indicator`; `response_capacity_status`; `control_result_notice`; `reporting_framework_context`; `escalation_feedback` |
| `cluster_information_security_officer` | `delivered_incident_signal`; `sirm_response_update`; `cii_scope_indicator`; `technical_finding_summary`; `response_team_status`; `reporting_framework_context`; `coordination_meeting_record`; `office_availability_status`; `intent_lifecycle_notice` |
| `ihis_operational_and_scm_management` | `delivered_role_local_account`; `coordination_meeting_record`; `verification_result_notice`; `management_route_context`; `intent_lifecycle_notice` |
| `singhealth_group_chief_information_officer` | `delivered_operational_account`; `technical_verification_update`; `ihis_executive_direction`; `sector_lead_update`; `singhealth_management_response`; `patient_impact_update`; `intent_lifecycle_notice` |
| `cyber_security_governance_director_and_healthcare_sector_lead` | `delivered_incident_account`; `cii_scope_indicator`; `classification_verification_update`; `reporting_framework_context`; `executive_briefing_state`; `ihis_executive_direction`; `acting_capacity_context`; `report_lifecycle_notice` |
| `ihis_chief_executive_officer` | `delivered_executive_incident_brief`; `supporting_evidence_summary`; `sector_lead_assessment`; `gcio_update`; `investigation_capacity_status`; `acting_capacity_context`; `intent_lifecycle_notice` |
| `singhealth_deputy_group_chief_executive_officer` | `delivered_gcio_incident_update`; `singhealth_gceo_direction`; `investigation_scope_update`; `data_integrity_update`; `interagency_consultation_record`; `outreach_readiness_status`; `intent_lifecycle_notice` |
| `singhealth_group_chief_executive_officer` | `delivered_incident_update`; `unauthorized_access_indicator`; `deputy_gceo_outreach_proposal`; `interagency_consultation_record`; `notification_readiness_summary`; `intent_lifecycle_notice` |

### 3.2 Label reuse and interface families

Seven reader-facing observation labels are reused across products. Their
placements remain distinct:

| Reused label | Placements | Required distinction |
|---|---:|---|
| `intent_lifecycle_notice` | 6 | issuer, recipient, intent reference, lifecycle, and delivered time remain capability-scoped |
| `reporting_framework_context` | 3 | office duty, route, category, and effective institutional context remain scoped |
| `acting_capacity_context` | 2 | Sector Lead and IHiS CEO office/capacity records remain distinct |
| `cii_scope_indicator` | 2 | Cluster ISO and Sector Lead receive independently routed projections |
| `coordination_meeting_record` | 2 | attending responsibility unit and Cluster ISO see only presented or delivered content |
| `ihis_executive_direction` | 2 | Sector Lead and GCIO receive separately addressed direction |
| `interagency_consultation_record` | 2 | Deputy GCEO and GCEO receive their own delivered consultation record |

| Observation family | Material concepts | Mapping requirement |
|---|---|---|
| technical signal and control | alert, log, query, callback, credential, session, host, control, result | stable source object/version, assigned access, event time, delivery, freshness, and no hidden current state |
| incident account and assessment | finding, summary, scope indicator, operational account, executive brief, category basis | source-preserving information product with uncertainty and separately delivered revisions |
| relationship and authority context | institutional route, reporting framework, office capacity, assignment | authoritative relation/authority record with effective interval; unknown grants nothing |
| meeting and consultation | agenda, presented evidence, decisions, action owners, consultation record | attendance and delivery do not reveal undisclosed participant knowledge |
| lifecycle and feedback | intent, report, investigation, outreach, control, and response notices | stable object/reference, typed lifecycle, producer, delivery time, and version |
| patient-impact and outreach | scope, integrity, readiness, proposal, audience, channel | authoritative update remains distinct from a participant recommendation and notification result |

## 4. Private state and authoritative state

### 4.1 Replayable participant state

| Capability | Behaviorally material private state |
|---|---|
| `technical_administration_and_line_security_staff` | `local_assessment`; `open_questions`; `last_shared_finding`; `active_intent_references` |
| `security_incident_response_manager` | `current_incident_assessment`; `open_information_requests`; `active_coordination_intents`; `last_escalation_intent`; `coverage_assessment` |
| `cluster_information_security_officer` | `current_iso_assessment`; `open_clarifications`; `last_response_status`; `active_coordination_intents`; `active_reporting_intents` |
| `ihis_operational_and_scm_management` | `current_cross_team_assessment`; `open_verification_items`; `last_consolidated_account`; `active_management_intents` |
| `singhealth_group_chief_information_officer` | `current_gcio_assessment`; `open_information_requests`; `last_routed_account`; `active_review_intents`; `active_reporting_intents` |
| `cyber_security_governance_director_and_healthcare_sector_lead` | `current_sector_assessment`; `open_classification_questions`; `last_classification_basis`; `active_verification_intents`; `active_classification_intents`; `active_reporting_intents` |
| `ihis_chief_executive_officer` | `current_executive_assessment`; `open_evidence_questions`; `last_investigation_assignment`; `active_direction_intents`; `active_reporting_intents` |
| `singhealth_deputy_group_chief_executive_officer` | `current_supervisory_assessment`; `open_information_needs`; `last_scope_update`; `active_reporting_intents`; `active_outreach_intents` |
| `singhealth_group_chief_executive_officer` | `current_gceo_assessment`; `open_governance_questions`; `last_consultation_record`; `active_reporting_directions`; `active_notification_directions` |

Every state placement has one capability-scoped owner, an explicit
initialization, legitimate update event, version, visibility boundary, and
decision consumer. Pending-intent references distinguish never issued,
pending, acknowledged, partial, failed, expired, cancelled, superseded, and
completed attempts. Backend-local undeclared memory is not an admissible
carrier.

### 4.2 Environment-owned business truth

The Scenario and reducer retain authoritative truth for:

- institution, office, responsibility-unit, role, assignment, capacity, and
  reporting relationships;
- accounts, credentials, hosts, sessions, network routes, applications,
  databases, access grants, monitoring, and technical controls;
- attack attempts, access, execution, query, copying, disclosure,
  investigation, containment, and technical results;
- information-product production, message issue, transport, delivery,
  acknowledgement, correction, freshness, and dispute;
- meetings, response-team activation, incident category, reports, executive
  directions, investigation assignments, consultation, outreach plans,
  notification approval, execution, delivery, and affected-cohort results; and
- action/message admission, progress, partial effect, failure, expiry,
  cancellation, supersession, completion, and later observation.

A participant may retain a delivered reference or bounded assessment. It may
not maintain a competing copy of any state above.

## 5. Intent inventory

### 5.1 Released intents by capability

| Capability | Reader-facing semantic intent IDs |
|---|---|
| `technical_administration_and_line_security_staff` | `investigate_local_signal`; `request_peer_context`; `share_technical_finding`; `request_security_review`; `apply_local_control` |
| `security_incident_response_manager` | `request_security_investigation`; `coordinate_incident_response`; `activate_incident_response_team`; `provide_incident_response_status`; `direct_local_containment`; `request_external_assistance`; `escalate_suspected_incident`; `delegate_sirm_coverage` |
| `cluster_information_security_officer` | `request_incident_clarification`; `request_response_status`; `issue_security_coordination_direction`; `request_sirt_activation`; `coordinate_incident_reporting`; `escalate_potential_cii_incident` |
| `ihis_operational_and_scm_management` | `request_operational_account`; `convene_cross_functional_review`; `request_fact_verification`; `assign_operational_follow_up`; `escalate_operational_concern` |
| `singhealth_group_chief_information_officer` | `request_operational_clarification`; `convene_management_review`; `escalate_to_ihis_leadership`; `notify_singhealth_management`; `request_singhealth_reporting_advice`; `provide_patient_impact_update` |
| `cyber_security_governance_director_and_healthcare_sector_lead` | `request_classification_verification`; `propose_incident_category`; `request_executive_briefing`; `report_cii_incident_to_csa`; `notify_authorized_healthcare_leadership`; `request_report_status` |
| `ihis_chief_executive_officer` | `request_executive_incident_briefing`; `request_supporting_evidence`; `direct_sector_lead_reporting`; `assign_investigation_lead`; `issue_ihis_executive_update` |
| `singhealth_deputy_group_chief_executive_officer` | `request_incident_clarification`; `notify_singhealth_gceo`; `request_moh_reporting`; `mobilize_outreach_preparation`; `propose_notification_audience`; `propose_notification_plan`; `provide_outreach_status` |
| `singhealth_group_chief_executive_officer` | `request_incident_detail`; `direct_moh_reporting`; `request_outreach_plan`; `consult_on_outreach_plan`; `advise_notification_audience`; `recommend_primary_notification_channel` |

`request_incident_clarification` is the only reused reader-facing intent
label. Its Cluster ISO and Deputy GCEO placements differ in evidence,
recipient set, institutional purpose, and downstream lifecycle. Every machine
identity therefore uses `(event_id, capability_id, semantic_intent_id)`.

### 5.2 Intent interface families

| Family | Examples | Required separation |
|---|---|---|
| inspect and verify | investigate signal; request logs, evidence, scope, category, or operational account | request, access, execution, returned evidence, interpretation, and later use remain separate |
| coordinate and convene | response coordination, SIRT activation, cross-functional review, consultation | proposal, route admission, invitation, attendance, presented content, decision, and action ownership remain separate |
| communicate and escalate | share finding, report status, escalate concern, notify leadership or management | issue, transport, delivery, acknowledgement, recipient interpretation, and further routing remain separate |
| classify and direct | propose category, direct reporting, assign investigation, direct local control | participant judgement or direction is not authoritative institutional state or completed execution |
| contain and control | apply local control, direct containment, request assistance | authority, target, prestate, feasibility, execution, partial/adverse effect, and observation remain separate |
| prepare and notify | mobilize outreach, propose audience/plan, recommend channel, provide patient-impact update | preparation, consultation, approval, delivery, and patient result remain separate |
| clarify lifecycle | request response, report, delivery, or result status | a status request cannot manufacture an acknowledgement or successful result |

## 6. Lifecycle inventory

| Lifecycle family | Minimum states and transitions | Authoritative owner |
|---|---|---|
| participant intent | issued, admitted/rejected, pending, acknowledged, partial, completed, failed, expired, cancelled, superseded | reducer and referenced institutional process; participant observes delivered notices |
| information product | drafted/produced, versioned, routed, delivered, acknowledged, corrected/superseded, stale/expired | producing and delivery processes |
| investigation or verification request | requested, authority/access checked, assigned, executing, partial, completed, failed/declined, expired/closed | technical or institutional process |
| local-control request | proposed, authority checked, scheduled, executing, partial, effective/no-effect/adverse, reversed/released | technical process and reducer |
| meeting or consultation | requested, admitted, invited, attended, material presented, decision recorded, action assigned, record delivered, closed | institutional meeting process |
| response-team activation | requested, authority checked, activated/declined, staffed, operating, stood down | institutional incident-response process |
| incident assessment and category | suspected, under review, provisionally assessed, category proposed, institutionally classified, revised/reopened, closed | institutional incident process; participants own only proposals/assessments |
| report and notification | proposed, drafted, authorized, issued, transported, delivered, acknowledged, corrected/superseded, closed | reporting or notification process |
| investigation assignment | proposed, authority checked, accepted/declined, active, partial, completed, failed/reassigned, closed | institutional assignment process |
| outreach plan | preparation requested, drafting, consultation, revised, readiness assessed, approved/declined, executing, completed/cancelled | SingHealth/institutional outreach process |
| attack and technical effect | attempt, access adjudication, executed/blocked/failed, persisted, detected, contained, later observed | bounded adversarial input plus Scenario/reducer |

No valid no-intent decision is converted into an invented action. A decision
record may instead retain its bounded reason and reopening condition.

## 7. Identity, authority, and resource inventory

| Layer | Stable requirement |
|---|---|
| institution | one canonical `entity_id` for IHiS, SingHealth, MOH, MCI, CSA, and each technical/system process represented in the Scenario |
| office or responsibility unit | one `unit_id`, host institution, effective role, assignment, access scope, availability, and capacity context |
| runtime participant | one `runtime_actor_id` or population-unit identity per instantiated decision interface |
| capability | exact released product ID, version, SHA-256, and proposed capability ID |
| semantic placement | capability-qualified observation, private-state, decision, intent, message, and result reference |
| business object | stable object ID, kind, version, owner/process, lifecycle state, and causal parents |
| run component | exact release, mapping, Scenario, configuration, assembly, structural-variant, Contract, and code identities |

Authority is scoped to office/unit, capability, intent, target, relationship,
system or process, effective interval, and source record. Unknown or empty
scope grants nothing. Concurrent IHiS/MOH appointments do not merge capacity,
information, or institutional authority.

The event has no financial ledger requirement. Material resources are
technical access and control scopes, investigation/response capacity, meeting
and communication capacity, and outreach readiness. Proposals and assignments
do not change those resources; only the reducer records reservations,
execution, release, and realized effects.

## 8. Scenario-owned semantic requirements

The Event Scenario Definition must supply without redefining participant
behavior:

1. institution, office/unit, assignment, reporting, capacity, access, system,
   database, and route identities;
2. attack-pressure inputs and access/query/copying/disclosure mechanics;
3. source-preserving information products, delivery, meeting, consultation,
   correction, freshness, and dispute;
4. investigation, verification, local-control, SIRT, incident-category,
   reporting, executive-direction, assignment, outreach, and notification
   lifecycles;
5. authority, target, relationship, prestate, capacity, concurrency, expiry,
   duplicate, and feasibility adjudication;
6. typed dispositions, results, state deltas, later observations, and
   deterministic causal lineage;
7. structural variants and exogenous inputs that never enter participant
   knowledge unless delivered; and
8. normal/incomplete termination, pending-object treatment, invariant failure,
   trace closure, and reproducibility identity.

## 9. Inventory findings

- The accepted nine-product roster covers every autonomous choice needed by
  the research question; no participant or behavior gap is open.
- Capability-scoped IDs resolve all observation and intent label reuse without
  changing reader-facing semantics.
- Several office actors may be hosted by one institution without duplicating
  the institutional entity, system state, authority records, or results.
- The 44 private-state placements can be reducer-versioned and replayed using
  Contracts V1 fields, decision records, and state deltas.
- The 62 observations and 54 intents require an event Scenario semantic layer
  and a consolidated internal mapping, but no current requirement demonstrates
  an irreducible Contracts V1 loss.
- The likely high-information lineage crosses a technical finding, security
  escalation, operational consolidation, GCIO routing, Sector Lead
  classification/reporting, executive direction, and institutional delivery.
  Exact binding selection remains a later configuration decision.
