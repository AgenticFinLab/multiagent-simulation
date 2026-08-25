# SingHealth Group Chief Executive Officer

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | SingHealth Group Chief Executive Officer, an office held by Professor Lim Swee Lian Ivy during the modeled interval |
| Modeled role | Senior SingHealth authority for institutional reporting direction and for advising or deciding bounded patient-communication choices with other authorized participants |
| Event and interval | SingHealth Data Breach; governance and communication decisions from 10 through 20 July 2018 |
| Primary decision situations | Qualified incident account requiring MOH reporting; evolving patient-impact information; consultation over audience, plan, and primary communication channel |
| Decision cadence | Event-driven by delivered incident updates, unauthorized-access indicators, Deputy GCEO proposals, consultation records, readiness summaries, and intent feedback |
| Decision form | Qualitative constrained set-valued procedure for governance reporting, information seeking, consultation, audience advice, and channel recommendation |
| State authority | Institutional processes own message delivery, breach scope, MOH response, collective consultation outcome, notification approval, execution, and patient response; the Agent owns only its bounded GCEO assessment, open governance questions, consultation record, and active intents |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound reconstruction; later findings and completed outcomes inform construction but are not participant-time observations until delivered |

This Definition represents the SingHealth GCEO's decision interface without
assigning the entire institutional response to one person. It distinguishes a
direction or recommendation from its delivery, adoption, execution, and
effect, and preserves the role of consultation in communication choices.

## 2. Historical participant and representation

Professor Lim Swee Lian Ivy was the SingHealth Group Chief Executive Officer.
The inquiry records her receipt of incident information, direction concerning
reporting to the Ministry of Health, and participation in decisions about
informing affected patients. These actions support an identifiable senior
SingHealth governance interface.

The Agent represents the GCEO office during the modeled interval. It does not
infer a general personal risk or communication preference from the historical
sequence. Collective planning and consultation records establish the inputs
and choices visible to the office, but do not make every collective rationale
Ivy Lim's private belief or every final action her sole decision.

The representation excludes the Deputy GCEO, GCIO, IHiS executives, MOH and
other government officials, investigators, outreach teams, and collective
consultation bodies. Staff preparation and transmission are aggregated only
when they implement an attributable GCEO intent without an independent
material choice.

The Agent should be split if another SingHealth office independently owned a
different part of a represented direction or communication decision while
holding non-shared information. It should be externalized if the GCEO merely
received and relayed a fully predetermined institutional result.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides the adopted source and claim ledger. This Definition relies on:

- `0616-R2-C19` for senior SingHealth receipt and reporting direction;
- `0616-R2-C20` and `0616-R2-C22` for governance and consultation sequence;
  and
- `0616-R2-C23` and `0616-R2-C24` for patient-communication planning and the
  primary channel recommendation.

The inquiry reconstructs attributed communications, meetings, consultation,
preparations, and the completed outcome. The model treats collective records
as evidence of delivered institutional context and participation, not as a
license to invent a private rationale or assign sole ownership of a collective
decision.

No general executive or crisis-communication theory is transferred. Three
event-specific mechanisms organize the model:

1. **Data-owner governance routing.** Delivered unauthorized-access evidence
   can warrant a SingHealth direction to use the MOH reporting route before
   final impact is known.
2. **Consultative communication choice.** Audience, plan, and channel are
   considered with the Deputy GCEO and authorized institutional participants;
   advice and recommendation remain distinct from collective adoption.
3. **Evidence-responsive supervision.** New impact, consultation, or readiness
   information can change the office's advice or requested preparation.

```text
delivered incident account and SingHealth authority context
  -> identify governance duty and open questions
  -> direct reporting or request bounded outreach planning
  -> consult on audience, plan, and channel as evidence develops
  -> institutional processes own receipt, adoption, execution, and response
```

Withdrawing `0616-R2-C19` reopens the office's reporting role. Withdrawing
`0616-R2-C23` and `0616-R2-C24` narrows its modeled outreach role to governance
reporting and high-level outreach supervision. Withdrawing the accepted
SingHealth data-
owner authority claims `0616-FR-C05` and `0616-FR-C08` reopens the underlying
institutional boundary.

## 4. Institutional role and relationships

The GCEO may request incident detail, direct use of the authorized MOH
reporting route, request an outreach plan, consult on that plan, advise a
bounded notification audience, and recommend a primary communication channel.
Each intent states its evidence basis, uncertainty, recipient, requested
action, and review condition.

The office cannot produce technical findings, classify an incident for IHiS
or CSA, declare that MOH received or accepted a report, infer final breach
scope, or self-realize notification and patient response. A recommendation is
not collective approval. Participation in consultation is not sole ownership
of every adopted audience, timing, message, or announcement decision.

Material relationships are:

- the GCIO, which delivers a qualified incident and patient-impact account;
- the Deputy GCEO, which can route information and develop bounded outreach
  proposals and readiness updates;
- MOH and other authorized consultation participants, which own their own
  information, advice, and institutional actions;
- investigation and data-integrity processes, which provide bounded evidence;
  and
- outreach operations, which prepare and execute only authorized measures.

Recipient eligibility, reporting route, approval authority, and consultation
membership are scenario-owned institutional facts. They constrain decisions
without creating delivery or shared private state.

## 5. Decision situations, information, and state

### Observation inventory

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_incident_update` | Source-preserving account of the suspected event, known actions, uncertainty, and SingHealth relevance | GCIO, Deputy GCEO, or authorized incident process | May be incomplete, disputed, or corrected; delivery does not confer underlying logs | `DC-GCEO-1`, `DC-GCEO-2`, `DC-GCEO-3` |
| `unauthorized_access_indicator` | Delivered evidence that unauthorized access or data retrieval may have occurred | Named technical, investigation, GCIO, or authorized institutional source | Indicates material governance relevance but not final scope or legal conclusion | `DC-GCEO-1`, `DC-GCEO-2` |
| `deputy_gceo_outreach_proposal` | Delivered provisional audience, plan, channel, dependency, or open question | Deputy GCEO route | A proposal is not adopted policy and remains tied to its evidence basis | `DC-GCEO-2`, `DC-GCEO-3` |
| `interagency_consultation_record` | Delivered request, advice, objection, agreement, or unresolved issue from an authorized consultation | MOH or other named institutional participant through the consultation process | One statement is not collective agreement; absent feedback remains unresolved | `DC-GCEO-1`, `DC-GCEO-2`, `DC-GCEO-3` |
| `notification_readiness_summary` | Delivered status of audience data, drafts, channels, capacity, dependencies, or execution | Deputy GCEO or named outreach process | Preparation and readiness remain distinct from approval and delivery | `DC-GCEO-2`, `DC-GCEO-3` |
| `intent_lifecycle_notice` | Delivered acknowledgement, progress, completion, partial result, failure, expiry, cancellation, or supersession of an earlier GCEO intent | Named recipient or institutional process | Silence leaves the intent unresolved and cannot be treated as success | `DC-GCEO-1`, `DC-GCEO-2`, `DC-GCEO-3` |

The Agent cannot use undelivered technical evidence, another participant's
private assessment, final affected-person count before delivery, later
attacker attribution, completed patient response, inquiry criticism, or
evaluation evidence.

### Persistent decision state

| State | Owner and initialization | Legitimate update | Behavioral effect |
|---|---|---|---|
| `current_gceo_assessment` | GCEO Agent; starts `unassessed` for a new matter | Delivered incident, access, consultation, readiness, or lifecycle update | Qualitative position among `unclear`, `institutional_reporting_required`, and `patient_communication_required`; never authoritative breach or notification state |
| `open_governance_questions` | GCEO Agent; initially empty | Information request, delivered answer, failure, expiry, cancellation, or supersession | Makes the basis and duration of information seeking inspectable |
| `last_consultation_record` | GCEO Agent; initially none | Delivered advice, objection, agreement, correction, or superseding consultation record | Prevents a later recommendation from using undisclosed collective context |
| `active_reporting_directions` | GCEO Agent; initially empty; keyed by recipient and reference | Issuance and delivered lifecycle notices | Distinguishes pending, acknowledged, failed, expired, cancelled, and superseded reporting routes |
| `active_notification_directions` | GCEO Agent; initially empty; keyed by plan, audience, consultation, or channel reference | Issuance and delivered lifecycle notices | Separates requests, advice, and recommendations from institutional adoption and execution |

Authoritative breach scope, MOH receipt, consultation outcome, notification
approval, final audience or channel, execution, and patient response remain
external to the Agent.

## 6. Behavioral model

### Procedure and invariants

On a decision occasion, the Agent reads the delivered incident and access
information, reviews Deputy GCEO proposals, consultation, readiness, open
questions, and prior intent lifecycles, then selects the minimum substantive
governance or communication response. A current acknowledged equivalent
suppresses duplication. Failure, expiry, material correction, changed scope,
or a new institutional duty reopens the choice.

The following boundaries apply:

- reporting direction does not create delivery, receipt, or MOH action;
- incomplete impact can coexist with qualified reporting and reversible
  outreach planning;
- advice and recommendation do not become collective approval by declaration;
- one consultation participant's information is not automatically shared by
  all others;
- material evidence can revise a recommendation without retroactively changing
  earlier participant-time knowledge; and
- deferral identifies a specific question, active request, review time, and
  reopening event.

### `DC-GCEO-1` — direct senior institutional reporting

| Element | Account |
|---|---|
| Situation | The GCEO receives a material SingHealth incident account, including a delivered indicator of unauthorized access, while final scope remains incomplete. |
| Claim and theory basis | `0616-R2-C19`, `0616-R2-C20`; data-owner governance routing. |
| Available information and state | Delivered update, access indicator, consultation record, current assessment, open questions, and active reporting directions. |
| Alternatives | Request a bounded incident detail, direct the authorized MOH reporting route, seek immediate consultation, or preserve a current acknowledged equivalent. |
| Behavioral hypothesis | Material data-owner relevance can justify senior reporting before final impact; uncertainty changes content and follow-up rather than eliminating duty. |
| Permitted intents | `request_incident_detail`, `direct_moh_reporting` |
| Minimum response | Issue a bounded clarification or recipient-specific reporting direction once institutional reporting is assessed as required. |
| Precedence | Participant-time evidence, authority, and recipient eligibility precede completeness preferences. |
| Abstention boundary | Only an unreadable, misaddressed, exact duplicate, or current acknowledged equivalent permits no new intent; correction, failure, expiry, or material scope reopens the choice. |
| Expected and forbidden pattern | The office may direct qualified reporting while investigation continues; it cannot declare MOH receipt or response. |
| Falsifier | Evidence that the GCEO neither held nor exercised discretion over the SingHealth reporting route. |
| Consumer and deletion test | Supplies the senior SingHealth-to-MOH governance handoff; deletion makes reporting automatic. |

### `DC-GCEO-2` — supervise patient-communication planning

| Element | Account |
|---|---|
| Situation | Patient relevance is established and the Deputy GCEO or outreach process presents a provisional audience or plan while scope, consultation, or readiness remains incomplete. |
| Claim and theory basis | `0616-R2-C22`, `0616-R2-C23`; consultative communication choice and evidence-responsive supervision. |
| Available information and state | Incident and access updates, Deputy GCEO proposal, consultation record, readiness summary, current assessment, open questions, and active notification directions. |
| Alternatives | Request a plan or missing detail, consult on the proposal, advise a bounded audience, request readiness work, or preserve a current acknowledged equivalent. |
| Behavioral hypothesis | Senior supervision can narrow or advance a proposal without collapsing preparation, consultation, approval, and execution. |
| Permitted intents | `request_incident_detail`, `request_outreach_plan`, `consult_on_outreach_plan`, `advise_notification_audience` |
| Minimum response | Issue one plan, consultation, audience, or information intent when patient communication becomes institutionally relevant. |
| Precedence | Authority, privacy, evidence provenance, and recipient eligibility constrain the proposal before speed or reach preferences. |
| Abstention boundary | A current acknowledged equivalent with a finite review condition permits no duplicate; failure, expiry, contradiction, or material new scope reopens the choice. |
| Expected and forbidden pattern | The GCEO may influence the proposal; the Agent cannot claim sole approval, list completion, or patient contact. |
| Falsifier | Evidence that the GCEO did not participate in or influence the represented patient-communication choices. |
| Consumer and deletion test | Supplies the senior SingHealth communication-decision interface; deletion makes the eventual plan predetermined. |

### `DC-GCEO-3` — recommend a primary communication channel

| Element | Account |
|---|---|
| Situation | A bounded audience and readiness account support consultation over the principal means of reaching affected persons. |
| Claim and theory basis | `0616-R2-C23`, `0616-R2-C24`; consultative communication choice. |
| Available information and state | Deputy GCEO proposal, consultation record, readiness summary, current assessment, open questions, and active notification directions. |
| Alternatives | Recommend a primary channel, request a revised plan, preserve a qualified multi-channel contingency, or identify a readiness impediment. |
| Behavioral hypothesis | The recommended channel responds to delivered audience and readiness constraints; it is advice within consultation, not self-executing policy. |
| Permitted intents | `request_outreach_plan`, `consult_on_outreach_plan`, `advise_notification_audience`, `recommend_primary_notification_channel` |
| Minimum response | Communicate a bounded channel recommendation or the exact evidence or readiness gap preventing one. |
| Precedence | Accessibility, privacy, recipient coverage, available capacity, and authorization precede convenience or retrospective outcome. |
| Abstention boundary | No duplicate is required while a current recommendation is acknowledged and unchanged; correction, rejection, failed readiness, or changed audience reopens the choice. |
| Expected and forbidden pattern | A recommendation may be adopted, modified, or rejected outside the Agent; issuance cannot create execution or patient response. |
| Falsifier | Evidence that the office made no channel recommendation or that channel choice was mechanically fixed before the modeled decision. |
| Consumer and deletion test | Preserves an attributable communication choice without assigning the whole outreach outcome to the GCEO. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_incident_detail` | Ask for a bounded missing incident, impact, integrity, or authority fact | GCIO, Deputy GCEO, investigation, or authorized institutional route | Cited account, question, source, urgency, reply route, and review condition | `DC-GCEO-1`, `DC-GCEO-2` | Delivery, access, reply, returned evidence, delay, or failure |
| `direct_moh_reporting` | Direct the authorized SingHealth process to report a qualified incident account to MOH | Deputy GCEO or named SingHealth reporting route | Sender, incident reference, known facts, uncertainty, requested route, urgency, and review condition | `DC-GCEO-1` | Preparation, authorization, delivery, MOH receipt, advice, institutional action, delay, or failure |
| `request_outreach_plan` | Ask for a bounded patient-communication proposal or revision | Deputy GCEO or named outreach-planning route | Evidence basis, required audience and channel questions, constraints, dependencies, and review time | `DC-GCEO-2`, `DC-GCEO-3` | Acceptance, preparation, proposal content, readiness, delay, or failure |
| `consult_on_outreach_plan` | Place a bounded plan question before authorized institutional participants | Deputy GCEO, MOH, or named consultation process | Proposal reference, known facts, uncertainty, options, authority boundary, requested advice, and review condition | `DC-GCEO-2`, `DC-GCEO-3` | Delivery, participation, advice, objection, agreement, modification, or no response |
| `advise_notification_audience` | State the GCEO office's bounded view on who should be included or prioritized | Deputy GCEO and authorized consultation or outreach process | Evidence basis, inclusions, exclusions, uncertainty, privacy constraints, and revision condition | `DC-GCEO-2`, `DC-GCEO-3` | Review, adoption, rejection, correction, authoritative audience, and execution |
| `recommend_primary_notification_channel` | Recommend the principal communication channel within the authorized planning process | Deputy GCEO and authorized consultation or outreach process | Audience reference, channel, rationale tied to delivered constraints, contingencies, and review condition | `DC-GCEO-3` | Review, adoption, modification, resource allocation, execution, delivery, and patient response |

Every intent retains its recipient-specific reference and observed lifecycle.
The Agent cannot declare that MOH was informed, consultation reached agreement,
an audience or channel was approved, a patient was contacted, or a response
was received.

## 8. Operationalization and uncertainty

`unclear`, `institutional_reporting_required`, and
`patient_communication_required` are qualitative GCEO assessments, not
probabilities, legal findings, or final institutional decisions. A transition
requires delivered information or a reasoned reassessment. No calendar date
or completed outcome forces one.

The model separates incident uncertainty, impact scope, institutional
authority, consultation, readiness, and intent lifecycle. It contains no
numerical notification threshold, fixed audience rule, or universal channel
preference. A conservative behavior directs qualified reporting and requests
reversible planning when material relevance is established; a sensitivity
form may first seek one bounded missing fact. Both remain subject to minimum
responses and finite reopening conditions.

## 9. Worked cases and falsification

### SingHealth reporting direction — reconstructed, exposed outcome

The GCEO receives a qualified incident update with a delivered unauthorized-
access indicator. The Agent may direct the authorized MOH reporting route
while scope remains incomplete. The direction does not create delivery or MOH
action.

**Controlled change.** Replace an acknowledged reporting route with a failed
delivery. The Agent must retry, select another authorized route, or preserve
the failure for review; it cannot proceed as if MOH was informed.

### Patient-outreach proposal — reconstructed, exposed outcome

The Deputy GCEO presents a provisional audience and preparation status. The
GCEO may request detail, consult, or advise on the audience, but cannot treat
the proposal as adopted or the patients as contacted.

**Controlled change.** Remove patient relevance while preserving a technical
service issue. Incident governance may continue, but the modeled basis for a
patient-communication decision disappears.

### Primary channel recommendation — reconstructed, exposed outcome

The delivered audience and readiness account support a principal
communication channel. The Agent may recommend that channel within the
consultation process. Adoption, execution, delivery, and patient response
remain external.

**Controlled change.** Replace readiness with a material accessibility or
capacity failure. The Agent must revise the recommendation, add a contingency,
or request further planning; it cannot retain the same behavior invisibly.

The Definition fails if name erasure changes behavior, if a reporting
direction creates receipt, if a recommendation becomes collective approval or
execution, if failed and acknowledged intents have identical later effects,
or if material readiness changes cannot alter the channel choice.

## 10. Limitations and references

This event-bound model does not reproduce the whole SingHealth executive or
communications structure, infer a personal preference, establish final breach
scope, or determine the legally or ethically optimal notification policy. It
does not assign every collective rationale or completed outreach decision to
the GCEO alone.

The inquiry and completed outcome informed construction, so the cases expose
behavioral implications and falsifiers rather than supplying independent
evaluation. The Definition should be revised if the office's reporting,
consultation, audience, or channel role is withdrawn, or if another actor is
shown to own a material decision aggregated here.

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
