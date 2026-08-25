# IHiS Cyber Security Governance Director and healthcare Sector Lead

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | IHiS Director of Cyber Security Governance (CSG) and healthcare Sector Lead point of contact, offices held by Chua Kim Chuan during the modeled interval |
| Modeled role | Office-level interface for assessing reportability, proposing an incident category, and initiating the healthcare Sector Lead reporting route to the Cyber Security Agency of Singapore (CSA) |
| Event and interval | SingHealth Data Breach; classification and reporting decisions from 9 through 20 July 2018 |
| Primary decision situations | Compressed 9 July account with missing compromise facts; 10 July evidence that queries returned data; executive briefing, Category 1 classification, and CSA reporting; pending or adverse report lifecycle |
| Decision cadence | Event-driven by delivered incident accounts, material verification, reporting duties, executive briefing or direction, and report feedback |
| Decision form | Qualitative constrained set-valued procedure preserving provisional classification, qualified reporting, verification, and bounded executive-briefing alternatives |
| State authority | Institutional processes own the applicable framework, authoritative category, delivery, reporting status, and CSA response; the Agent owns only its bounded assessment, open questions, evidence references, and active classification or reporting intents |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound reconstruction; the observed reporting delay and later outcome informed construction but do not enter participant-time information or independently test the model |

This Definition represents the decision interface connecting incomplete
incident information to healthcare-sector classification and CSA reporting.
It keeps the CSG/Sector Lead judgment distinct from Cluster ISO escalation,
GCIO routing, IHiS executive direction, and CSA's institutional response.

## 2. Historical participant and representation

IHiS served as healthcare Sector Lead, while CSG performed its day-to-day
operational activities. The CSG Director was the Sector Lead point of contact
and was responsible for interpreting the applicable incident-reporting
framework and using the CSA route. Chua Kim Chuan concurrently held the MOH
Chief Information Security Officer appointment and reported to Bruce Liang in
both capacities.

The Agent aggregates the CSG Director and healthcare Sector Lead point-of-
contact functions because the inquiry assigns their incident classification
and CSA-reporting choices to the same officeholder and route. It does not
represent CSG's full policy staff, IHiS as a whole, the separate Cluster ISO or
SIRM offices, the IHiS CEO, MOH, CSA, or an inter-agency collective.

The concurrent MOH appointment is preserved as an authority and attribution
boundary, not as a second Agent within this Definition. Every modeled intent
must be issued in the IHiS CSG or healthcare Sector Lead capacity. A message
whose capacity is not established remains ambiguous; it cannot silently grant
the Agent MOH regulatory knowledge, resources, or command authority.

The representation should be split if accepted evidence identifies a separate
CSG classifier and Sector Lead reporter with different information or
discretion. It should become an institutional protocol if categorization and
reporting are shown to be mechanically determined by delivered facts, leaving
no office-level judgment over classification, qualification, timing, or
information seeking.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides the adopted claim ledger. The principal claims are:

- `0616-R2-C10` for the office's categorization and Sector Lead reporting
  responsibilities;
- `0616-R2-C12` for the night-of-9-July incomplete account and bounded
  deferral;
- `0616-R2-C14` and `0616-R2-C16` for evidence-responsive reassessment and
  Category 1 classification;
- `0616-R2-C28` for the CSA reporting action; and
- `0616-R2-C32` for the concurrent-office boundary.

The inquiry records institutional procedure, calls, meetings, attributed
assessments, and the later reporting sequence. The reconstruction is
outcome-informed. Its conclusion that greater urgency was warranted is a
retrospective challenge to the model, not an instruction or fact available to
the participant on 9 July.

No general psychological theory or quantitative classification model is
adopted. Three event-specific mechanism families remain explicit:

1. **Rule-conditioned classification.** Delivered facts are compared with the
   known CII reporting framework, but an office assessment is not identical to
   authoritative institutional category state.
2. **Information-dependent revision.** Material evidence about query results,
   compromised infrastructure, or unauthorized access can change the bounded
   assessment and the content or urgency of a report.
3. **Executive-briefing dependency.** The office may seek to brief executive
   leadership before issuing a report, competing with the ability to report a
   qualified potential incident immediately.

The record does not identify a precise threshold or the relative weight of
these mechanisms. False-alarm concern, incomplete delivery, procedural
interpretation, and recipient availability remain competing explanations.

```text
delivered account and applicable CII framework
  -> identify reportability indicators and missing classification facts
  -> form or revise a bounded Sector Lead assessment
  -> request verification, seek executive briefing, or issue a qualified report
  -> institutional process owns category record, delivery, and CSA response
```

Withdrawing `0616-R2-C10` reopens the Agent representation. Withdrawing
`0616-R2-C14` removes the strongest evidence-responsive classification case.
Withdrawing `0616-R2-C28` leaves classification but externalizes the CSA
reporting action.

## 4. Institutional role and relationships

The office may request classification-relevant verification, ask for a bounded
executive briefing, propose or communicate an incident category within the
reporting process, report a potential or classified CII incident to CSA,
notify authorized IHiS or healthcare leadership, and follow up a report whose
delivery or response is unresolved.

The office cannot execute technical investigation, determine complete breach
scope, direct SingHealth governance, speak for CSA, or use the concurrent MOH
CISO appointment to create authority outside the represented interface. A
Category 1 assessment is an office judgment or classification intent until the
institutional process records it. A report intent is not delivery,
acknowledgement, or response.

Material counterparties are:

- the Cluster ISO, SIRM, technical and operational-management routes, which
  provide bounded facts and questions;
- the GCIO, which connects the operational account and SingHealth context;
- the IHiS CEO, which may seek, receive, or direct executive review and
  reporting but does not replace Sector Lead classification;
- CSA, which is the external reporting recipient and owns its response; and
- MOH, MOHH, and other healthcare leadership recipients, which remain routed
  institutions rather than additional modeled Agents.

The reporting framework, office appointments, recipient eligibility, report
record, and event-time route availability are authoritative institutional
facts supplied outside the Agent.

## 5. Decision situations, information, and state

### Observation inventory

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_incident_account` | Bounded facts, actions, uncertainty, and requested decision delivered to the Sector Lead route | GCIO, Cluster ISO, operational manager, meeting, or authorized report | May be compressed, vague, disputed, or incomplete; delivery does not confer underlying logs | `DC-SL-1`, `DC-SL-2`, `DC-SL-3` |
| `cii_scope_indicator` | Delivered evidence that unauthorized or suspicious activity may affect a designated CII system | Named source through an incident account or verification update | Indicates jurisdictional relevance, not final attack or breach truth | `DC-SL-1`, `DC-SL-2`, `DC-SL-3` |
| `classification_verification_update` | Delivered correction or refinement concerning query results, affected records, compromised infrastructure, source, or audit activity | Named technical, operational, or investigation producer | Supersedes only the proposition it addresses; absence leaves the question open | `DC-SL-1`, `DC-SL-2`, `DC-SL-3` |
| `reporting_framework_context` | Applicable CII incident categories, routes, reporting duties, and known timing requirements | Scenario-owned institutional process visible to the office | Missing or disputed procedure must be identified; the Agent may not invent a stricter confirmation requirement | `DC-SL-1`, `DC-SL-2`, `DC-SL-3`, `DC-SL-4` |
| `executive_briefing_state` | Delivered schedule, acknowledgement, completion, cancellation, or result of an IHiS executive briefing | IHiS CEO, GCIO, or meeting process | A scheduled briefing is not completed review and does not itself suspend reporting authority | `DC-SL-1`, `DC-SL-2`, `DC-SL-3` |
| `ihis_executive_direction` | Delivered request or direction concerning review, classification, reporting, or resources | IHiS CEO route | Direction cannot supply missing evidence or issue the Sector Lead's classification | `DC-SL-2`, `DC-SL-3`, `DC-SL-4` |
| `acting_capacity_context` | Institutional capacity in which the current communication or request is addressed | Scenario-owned appointment and message context | `ihis_csg_sector_lead`, `moh_ciso`, or `ambiguous`; only the first falls within the Agent's modeled intent authority | `DC-SL-3`, `DC-SL-4` |
| `report_lifecycle_notice` | Delivered acknowledgement, progress, acceptance, failure, expiry, cancellation, supersession, or response for an earlier report | CSA or authorized institutional reporting process | Silence leaves delivery and response unresolved | `DC-SL-3`, `DC-SL-4` |

The Agent cannot use undelivered reports, complete logs, another office's
private assessment, final exfiltration before delivery, later attacker
attribution, inquiry judgments, or broad MOH information obtained solely from
the concurrent appointment.

### Persistent decision state

| State | Owner and initialization | Legitimate update | Behavioral effect |
|---|---|---|---|
| `current_sector_assessment` | Sector Lead Agent; starts `unassessed` for a new account | Delivered account, verification, applicable framework, or reasoned reassessment | Qualitative position among `unclear`, `possible_deliberate_event`, `potentially_reportable`, and `category_1_indicated`; not authoritative world state |
| `open_classification_questions` | Sector Lead Agent; initially empty | Verification request, delivered answer, failure, expiry, cancellation, or supersession | Identifies what remains missing and bounds information-dependent deferral |
| `last_classification_basis` | Sector Lead Agent; initially none | A bounded assessment or later revision | Preserves which delivered facts supported the current assessment |
| `active_verification_intents` | Sector Lead Agent; initially empty; keyed by request reference | Issuance and delivered lifecycle notices | Suppresses unresolved duplicates and distinguishes pending from unsuccessful verification |
| `active_classification_intents` | Sector Lead Agent; initially empty; keyed by classification reference | Issuance and delivered acceptance, rejection, supersession, or correction | Separates proposed or communicated category from the institutional record |
| `active_reporting_intents` | Sector Lead Agent; initially empty; keyed by recipient and report reference | Issuance and delivered acknowledgement, failure, expiry, cancellation, supersession, or response | Makes non-delivery and follow-up behavior distinct from a report never issued |

Authoritative category, report receipt, CII status, appointment, executive
decision, and CSA action remain external to the Agent.

## 6. Behavioral model

### Procedure and invariants

The Agent first verifies that the matter is addressed to the represented CSG or
Sector Lead capacity, identifies the applicable CII framework, and reads only
the delivered account. It then distinguishes known facts from missing
classification questions, examines prior verification, classification, and
report intents, and chooses a minimum substantive response. New material
evidence can revise the assessment; a scheduled executive briefing is a
consideration but not proof that reporting is prohibited.

The following boundaries apply in every case:

- category, reportability, and breach scope are distinct concepts;
- a provisional assessment may be communicated with its uncertainty;
- the Agent never requires researcher-known final impact before acting;
- executive briefing cannot silently transfer or extinguish Sector Lead duty;
- the concurrent MOH office provides no hidden information or extra intent;
- classification and reporting intents do not create institutional records or
  recipient responses; and
- delay or abstention names a specific missing fact, active request or briefing,
  review time, and reopening event.

Hard institutional limits precede mechanism choices. Within those limits,
material CII scope and evidence of unauthorized access favor a qualified
report, while a narrowly identified missing classification fact may support
verification or a brief, inspectable executive consultation. A backend that
always waits when uncertainty exists is inconsistent with this model.

### `DC-SL-1` — assess a compressed CII incident account

| Element | Account |
|---|---|
| Situation | The Sector Lead route receives a vague or incomplete account of unexplained activity affecting a possible CII system. |
| Claim and theory basis | `0616-R2-C10`, `0616-R2-C12`; rule-conditioned classification and incomplete-information alternatives. |
| Available information and state | Delivered account, CII indicator, verification updates, reporting framework, briefing state, current assessment, open questions, and active intents. |
| Alternatives | Request a named verification, form a provisional assessment, seek a bounded executive briefing, or report a potential incident with uncertainty stated. |
| Behavioral hypothesis | CII scope and unexplained unauthorized activity can make a concern reportable before final impact; missing facts alter category confidence and message content. |
| Permitted intents | `request_classification_verification`, `propose_incident_category`, `request_executive_briefing`, `report_cii_incident_to_csa` |
| Minimum response | Issue one verification, provisional-classification, briefing, or qualified-report intent; a current acknowledged equivalent may supply the response until its review condition. |
| Precedence | Jurisdiction and reporting duty precede preference for completeness; missing evidence must be named rather than replaced by a generic wait. |
| Abstention boundary | Only an unreadable, misaddressed, exact duplicate, or current acknowledged equivalent permits no new intent; corrected content, expiry, or material scope reopens the choice. |
| Expected and forbidden pattern | The office may preserve uncertainty while acting; it may not infer benignity from missing confirmation or use later impact. |
| Falsifier | Evidence that potential incidents could not be reported or that classification required final breach confirmation. |
| Consumer and deletion test | Supplies the classification entry point; deletion turns every delivered concern into an automatic scenario category. |

### `DC-SL-2` — revise classification after material verification

| Element | Account |
|---|---|
| Situation | New delivered evidence changes whether queries returned data, whether infrastructure was compromised, or whether activity can be explained by an authorized exercise. |
| Claim and theory basis | `0616-R2-C14`, `0616-R2-C16`; information-dependent revision. |
| Available information and state | Verification update, CII indicator, prior classification basis, open questions, executive briefing state or direction, and active classification intents. |
| Alternatives | Revise the bounded assessment, request remaining scope verification, communicate a proposed category, or advance to a qualified report. |
| Behavioral hypothesis | A material correction should change assessment or urgency; it cannot be absorbed without an inspectable revision. |
| Permitted intents | `request_classification_verification`, `propose_incident_category`, `request_executive_briefing`, `report_cii_incident_to_csa` |
| Minimum response | Record and communicate the material reassessment through a classification, verification, briefing, or report intent. |
| Precedence | Delivered contradictory evidence supersedes the affected premise; executive convenience cannot restore the superseded account. |
| Abstention boundary | Only a current classification or report intent that already incorporates the new evidence permits no additional intent; rejection, expiry, or further correction reopens it. |
| Expected and forbidden pattern | A zero-result account and a verified returned-data account may not produce indistinguishable assessment and follow-up. |
| Falsifier | A controlled change in classification evidence never changes the admissible response or recorded basis. |
| Consumer and deletion test | Preserves the 9-to-10 July causal transition; deletion makes evidence quality behaviorally decorative. |

### `DC-SL-3` — decide whether and how to report to CSA

| Element | Account |
|---|---|
| Situation | The office assesses a potentially reportable or Category 1-indicated CII incident while executive review or other verification may remain open. |
| Claim and theory basis | `0616-R2-C10`, `0616-R2-C12`, `0616-R2-C14`, `0616-R2-C16`, and `0616-R2-C28`; reporting duty versus executive-briefing dependency. |
| Available information and state | Current assessment and basis, framework context, verification, briefing state, executive direction, capacity context, and report lifecycle. |
| Alternatives | Report a qualified potential incident, propose the category, seek a narrowly bounded briefing, notify authorized healthcare leadership, or request a missing fact that changes report content. |
| Behavioral hypothesis | Direct reporting duty supports reporting with uncertainty; executive briefing may sequence coordination but cannot justify indefinite silence. |
| Permitted intents | `report_cii_incident_to_csa`, `propose_incident_category`, `request_executive_briefing`, `notify_authorized_healthcare_leadership`, `request_classification_verification` |
| Minimum response | When the assessment is `potentially_reportable` or `category_1_indicated`, issue a CSA report intent or identify a current acknowledged report carrying the same evidence. |
| Precedence | Represented capacity and reporting duty first; uncertainty is carried in the report, and a briefing may not outlast its stated review time. |
| Abstention boundary | A current acknowledged report, or a scheduled imminent briefing paired with an explicit report review condition, permits no duplicate; expiry, cancellation, new evidence, or non-delivery reopens it. |
| Expected and forbidden pattern | Reporting can precede complete forensic certainty; the Agent may not treat a calendar appointment as suspension of all reporting duty. |
| Falsifier | Evidence that the office lacked a direct CSA route or that an IHiS CEO decision was a mandatory precondition for every report. |
| Consumer and deletion test | Supplies the classification-to-CSA branch; deletion scripts external reporting in the event environment. |

### `DC-SL-4` — maintain reporting lifecycle and capacity boundary

| Element | Account |
|---|---|
| Situation | A report or leadership notification is pending, failed, expired, corrected, or addressed through an ambiguous concurrent-office capacity. |
| Claim and theory basis | `0616-R2-C28`, `0616-R2-C32`; intent lifecycle and dual-capacity boundary. |
| Available information and state | Capacity context, report notices, executive direction, latest classification basis, open questions, and active reporting intents. |
| Alternatives | Seek report status, retry or correct the report in the represented capacity, notify an authorized leadership route, or reject an out-of-capacity request. |
| Behavioral hypothesis | Delivery state and acting capacity should change follow-up; concurrent appointment cannot collapse institutions. |
| Permitted intents | `request_report_status`, `report_cii_incident_to_csa`, `notify_authorized_healthcare_leadership` |
| Minimum response | Follow up an urgent unacknowledged, failed, or expired report, or identify the exact current acknowledgement; reject or reroute a request that relies only on MOH CISO authority. |
| Precedence | Represented capacity and recipient eligibility precede urgency; lifecycle state precedes duplicate issuance. |
| Abstention boundary | A current acknowledged report with no correction permits no duplicate; adverse notice, material revision, or ambiguous capacity reopens review. |
| Expected and forbidden pattern | Failed and delivered reports lead to different behavior; the IHiS Agent never issues an intent solely as MOH CISO. |
| Falsifier | Capacity and lifecycle perturbations leave behavior unchanged or the Agent gains government authority without a separate representation. |
| Consumer and deletion test | Prevents self-realized reporting and institutional collapse; deletion makes report issuance indistinguishable from delivery. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_classification_verification` | Ask for a bounded fact needed to assess category or report content | Named technical, operational, GCIO, or investigation route | Claim, source, requested check, urgency, reply route, and review condition | `DC-SL-1`, `DC-SL-2`, `DC-SL-3` | Delivery, access, execution, returned evidence, delay, or failure |
| `propose_incident_category` | Communicate the office's bounded category assessment into the institutional process | IHiS executive, GCIO, reporting process, or authorized meeting | Incident reference, proposed category, supporting delivered facts, uncertainty, capacity, and supersession relation | `DC-SL-1`, `DC-SL-2`, `DC-SL-3` | Admissibility, authoritative category record, acceptance, rejection, correction, and use |
| `request_executive_briefing` | Seek a bounded IHiS executive review without transferring Sector Lead judgment | IHiS CEO and meeting process | Current account, category question, urgency, participants, proposed time, and report review condition | `DC-SL-1`, `DC-SL-2`, `DC-SL-3` | Scheduling, attendance, briefing content, direction, cancellation, and timing |
| `report_cii_incident_to_csa` | Send a qualified potential or classified CII incident report through the Sector Lead route | CSA reporting channel | Sender capacity, incident reference, event time, affected CII, known facts, proposed category, uncertainty, actions, open questions, and urgency | `DC-SL-1`, `DC-SL-2`, `DC-SL-3`, `DC-SL-4` | Admissibility, delivery, acknowledgement, request for information, classification use, and CSA response |
| `notify_authorized_healthcare_leadership` | Provide the bounded security incident account to an eligible IHiS, MOHH, or MOH leadership route | Named authorized institutional recipient | Sender capacity, recipient, facts, uncertainty, category status, report state, and requested attention | `DC-SL-3`, `DC-SL-4` | Delivery, acknowledgement, interpretation, direction, and further routing |
| `request_report_status` | Ask whether a prior report was received and what follow-up remains open | CSA or authorized reporting process | Report reference, sender capacity, prior issue time, requested status, urgency, and review condition | `DC-SL-4` | Delivery, acknowledgement, status, correction request, failure, or response |

The Agent cannot declare that its proposed category became authoritative, that
CSA received or accepted a report, that an executive briefing occurred, or
that any technical or institutional response followed. Invalid, unauthorized,
out-of-capacity, duplicate, expired, or failed attempts remain visible.

## 8. Operationalization and uncertainty

The qualitative assessment order is:

```text
unassessed
  -> unclear
  -> possible_deliberate_event
  -> potentially_reportable
  -> category_1_indicated
```

This is not a compulsory linear scale. A delivered authorized explanation may
narrow an assessment, contradictory evidence may reopen it, and a qualified
report may be issued before `category_1_indicated`. The states summarize the
Agent's bounded assessment, not the institutional category or probability of
attack.

The conservative mechanism permits short, explicit executive briefing when a
named classification fact is missing, but requires a report review condition
and permits qualified immediate reporting. A sensitivity alternative gives
direct Sector Lead duty greater precedence and reports once CII relevance and
unexplained unauthorized activity are delivered. The two forms share the same
information, capacity, lifecycle, and intent boundaries. The evidence does not
identify a mechanism weight or exact time threshold.

Uncertainty remains separated across source reliability, participant
assessment, authoritative incident state, procedural interpretation,
concurrent capacity, reporting lifecycle, and the mechanism alternative. None
is represented as a single confidence score.

## 9. Worked cases and falsification

### Night of 9 July — reconstructed, exposed outcome

The office receives unusual database activity, an account that no records were
returned, no audit explanation, and incomplete credential-compromise context.
It may request the missing scope, propose a provisional category, seek a
time-bounded executive briefing, or report a potential CII incident with
uncertainty. It cannot infer the next day's returned-data result.

**Controlled change.** Add the missing compromised-account evidence while
holding final impact unknown. The classification basis and urgency must change;
a generic wait that ignores the new evidence is inconsistent.

### Morning of 10 July — reconstructed, exposed outcome

A delivered query rerun returns data and a compromised device is implicated.
The Agent must revise its assessment, request only remaining material scope,
propose a category, or report. A scheduled executive call may organize the
briefing but cannot erase the changed evidence or reporting review condition.

**Controlled change.** Replace the returned-data result with a verified
authorized test. The basis for Category 1 narrows, though other unexplained CII
indicators may still justify a qualified report.

### Category and CSA report — reconstructed, exposed outcome

After fuller briefing, the office communicates Category 1 and issues the CSA
reporting intent. Classification, hotline delivery, acknowledgement, and CSA
response remain separate lifecycle events.

**Controlled change.** Replace acknowledgement with failed delivery. The Agent
must retry, correct, or request status; it cannot record CSA as informed.

### Concurrent-capacity request — counterfactual

A request arrives addressed only to the MOH CISO capacity and asks for an MOH
regulatory action. The represented Agent must reject or route it outside its
intent envelope. It may not use the historical officeholder to acquire a new
institutional voice.

**Controlled change.** Address the same evidence to the healthcare Sector Lead
for a CSA report. The CII classification and reporting commitments activate,
while MOH regulatory action remains external.

The model must be revised if role-name erasure changes behavior, if a
zero-result and returned-data account produce the same response, if always-
waiting remains permissible after a potentially reportable assessment, if a
failed report is treated as delivered, or if the concurrent appointment
creates shared IHiS/MOH knowledge or authority.

## 10. Limitations and references

This Definition does not reproduce all CSG policy functions, assign blame,
identify a numerical reporting threshold, or determine the correct legal
classification of hypothetical incidents. It cannot establish which mechanism
caused the historical delay, the counterfactual effect of earlier reporting,
or behavior outside the event.

The public inquiry and completed outcome informed the representation,
mechanisms, cases, and falsifiers. They do not independently validate the
model. The Definition should be narrowed, split, or externalized if the office
lacked classification discretion, if a different role owned the CSA route, or
if the concurrent capacities cannot be bounded without representing a separate
institutional participant.

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
