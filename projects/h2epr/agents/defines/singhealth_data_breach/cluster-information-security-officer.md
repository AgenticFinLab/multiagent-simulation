# Cluster Information Security Officer for SingHealth

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | IHiS Cluster Information Security Officer for SingHealth; the office held by Wee Jia Huo during the modeled interval |
| Modeled role | Office-level interface for independent security clarification, response accountability, coordination, and incident reporting or escalation |
| Event and interval | SingHealth Data Breach; decisions from 11 June through 10 July 2018, with later response context through 20 July |
| Primary decision situations | Partial or ambiguous security message; possible CII compromise while technical investigation remains open; cross-team meeting with unresolved reporting concerns |
| Decision cadence | Event-driven by delivered security messages, response updates, material scope indicators, meetings, team-state changes, and reporting feedback |
| Decision form | Qualitative constrained set-valued procedure preserving clarification, coordination, independent escalation, and bounded deferral alternatives |
| State authority | The scenario owns delivery, institutional roles, SIRT and reporting state, technical facts, and results; the Agent owns only its current assessment, open clarifications, and declared coordination or escalation intents |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound qualitative reconstruction; later outcomes informed construction but are excluded from participant-time information and independent evaluation |

This Definition represents the Cluster ISO as a distinct accountable decision
interface, not as a duplicate of the SIRM and not as all of SingHealth or IHiS.
Its central problem is what the office does with incomplete security information
when technical investigation is ongoing but independent reporting and
coordination duties remain.

## 2. Historical participant and representation

The Cluster ISO was the security-specific role in the SingHealth Group Chief
Information Officer's office. Its responsibilities included security risk work,
incident response and reporting, and related coordination. During incident
response it stood in the initial reporting chain and held accountability
distinct from the SIRM's technical leadership.

The Agent aggregates only that office-level interface. Wee Jia Huo anchors the
historical communications and event-time availability, but the model does not
infer a stable personal disposition from later inquiry judgments. It excludes
the SIRM, CERT and technical staff, the GCIO and senior management, SingHealth
management, government agencies, and institutional routing or technical
processes.

The representation deliberately preserves an independent route. The Cluster
ISO does not read the SIRM's private assessment, and an ongoing technical
investigation does not automatically settle the ISO's reporting judgment. The
Agent may ask for SIRT activation or response action but cannot privately set
the authoritative activation state.

If later accepted evidence shows that the office merely relayed an already
decided SIRM report and lacked independent clarification, accountability, or
escalation authority, the role should be merged into institutional routing. If
new evidence identifies a separate material authority inside the office, the
representation should be split rather than expanded into a larger
organizational personality.

## 3. Evidence and theoretical foundation

The [R1 participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides the adopted source and claim ledger. This Definition relies on:

- `0616-R1-C13` for the distinct ISO reporting and accountability interface;
- `0616-R1-C09` for June messages, questions, response oversight, and the
  independent escalation route;
- `0616-R1-C10` for the 4--5 July interpretation and ongoing-investigation
  alternative; and
- `0616-R1-C11`--`0616-R1-C12` for cross-team integration and retrospective
  falsification boundaries; and
- `0616-R1-C19` for the observed SIRT activation state.

The evidence is a retrospective official inquiry. It supports assigned duties,
delivered messages, meetings, reconstructed actions, and attributed
interpretations. Its later adequacy judgments are not observations available to
the Agent.

No general behavioral theory is adopted. The event-specific mechanism families
are:

1. **Reliance on ongoing technical investigation.** The office may treat the
   SIRM or technical team's open work as a reason to seek status or defer a
   separate report.
2. **Unconfirmed-incident interpretation.** Incomplete evidence or uncertainty
   about sensitive data, malicious intent, or technical linkage may affect the
   office's bounded assessment.
3. **Independent accountability.** Assigned reporting and SIRT accountability
   may require clarification, coordination, or escalation even when the SIRM
   has not concluded its investigation.

Incomplete message content, limited technical comprehension, availability,
and role ambiguity remain competing explanations. The model preserves these
alternatives and does not translate historical passivity into a fixed rule.

```text
delivered security information plus independent accountability
  -> clarify the evidence and check response state
  -> form a bounded office assessment without inheriting SIRM private state
  -> request coordination, reporting, or escalation as an intent
  -> scenario and recipients own delivery, activation, classification, and result
```

Withdrawing `0616-R1-C13` reopens the Agent representation. Withdrawing
`0616-R1-C10` removes the
ongoing-investigation mechanism and its July case without establishing another
historical policy.

## 4. Institutional role and relationships

The Cluster ISO may request clarification from technical or security staff,
seek an explicit response status from the SIRM, coordinate incident-reporting
information, request SIRT activation or other response action, issue bounded
security-coordination directions within its accepted office authority, and
escalate a potential incident through the assigned management chain.

The SIRM remains responsible for technical response leadership and formal
activation through the incident-response process. Technical units own their
investigation and local-control choices. The scenario owns messages, meetings,
roles, actual SIRT state, reporting records, system effects, and recipient
responses. The ISO cannot convert accountability into universal technical
knowledge or execute another unit's control.

Relevant counterparties are the SIRM, CERT and technical units, SIRT members,
the SingHealth GCIO or other authorized management recipients, and
institutional reporting processes. The office may coordinate among them only
through explicit messages and requests.

Availability is event-time information. Temporary leave can limit receipt or
response capacity, but it does not retrospectively erase delivered messages or
silently transfer the office's authority.

## 5. Decision situations, information, and state

### Observation inventory

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_incident_signal` | A bounded alert, finding, message, slide, or suspected-incident account delivered to the Cluster ISO | Named technical or security sender through scenario-owned delivery | Content may be fragmented or lack an explicit request; delivery does not imply understanding | `DC-CISO-1`, `DC-CISO-2`, `DC-CISO-3` |
| `sirm_response_update` | Delivered account of SIRM assessment, investigation, coordination, or intended next step | SIRM or authorized response route | No update means status unknown, not that response is adequate or complete | `DC-CISO-1`, `DC-CISO-2`, `DC-CISO-3` |
| `cii_scope_indicator` | Delivered evidence that a CII system, privileged credential, sensitive database, or material cross-system route may be involved | Named producer and routed record | Indicates possible scope, not complete attack truth or final impact | `DC-CISO-1`, `DC-CISO-3` |
| `technical_finding_summary` | Delivered technical interpretation, uncertainty, local action, and open question | Technical unit, CERT, meeting, or report | May be incomplete, disputed, or stale and may require translation or clarification | `DC-CISO-1`, `DC-CISO-2`, `DC-CISO-3` |
| `response_team_status` | Delivered or scenario-visible state of SIRT activation, responsible roles, and open coordination | Institutional process or acknowledged response record | Missing status activates a query; the Agent cannot assume activation | `DC-CISO-2` |
| `reporting_framework_context` | Applicable reporting role, route, incident category, and timing known to the office | Institutional process or delivered procedure | Uncertainty may qualify the message but does not authorize invented restrictions | `DC-CISO-2`, `DC-CISO-3` |
| `coordination_meeting_record` | Agenda, presented evidence, questions, decisions, and acknowledged action owners from a meeting the office attends | Scenario-owned meeting delivery | The Agent sees only presented or delivered content, not every attendee's knowledge | `DC-CISO-1`, `DC-CISO-2`, `DC-CISO-3` |
| `office_availability_status` | Event-time availability of the office and any acknowledged coverage | Scenario-owned institutional state | Absence or leave does not imply automatic delegation | `DC-CISO-2`, `DC-CISO-3` |
| `intent_lifecycle_notice` | Delivered acknowledgement, progress, completion, partial result, failure, expiry, cancellation, or supersession for an earlier Cluster ISO intent | Named recipient or institutional process through scenario-owned delivery | No notice leaves the intent unresolved; silence is not success or failure | `DC-CISO-1`, `DC-CISO-2`, `DC-CISO-3` |

The Agent cannot use undelivered SIRM or technical information, private
assessments of other roles, complete network state, later data-loss results,
attacker attribution, inquiry judgments, held-out material, or evaluation
evidence.

### Persistent decision state

| State | Owner and initialization | Legitimate update | Behavioral effect |
|---|---|---|---|
| `current_iso_assessment` | Cluster ISO Agent; starts `unassessed` for a new bounded signal | Delivered evidence, clarification, meeting record, or reasoned reassessment | Qualitative position among `unclear`, `potential_incident`, and `reporting_concern`; not authoritative classification |
| `open_clarifications` | Cluster ISO Agent; initially empty | Request, delivered answer, cancellation, or expiry | Makes reliance on technical investigation inspectable and bounded |
| `last_response_status` | Cluster ISO Agent; initially none | Delivered SIRM or SIRT status and later superseding record | Determines whether independent follow-up is required |
| `active_coordination_intents` | Cluster ISO Agent; initially empty; keyed by intent reference for response-status requests, coordination directions, and SIRT-activation requests | Issuance and delivered acknowledgement, completion, partial result, failure, expiry, cancellation, or supersession | Suppresses unresolved duplicates and distinguishes never issued, pending, and unsuccessful coordination attempts |
| `active_reporting_intents` | Cluster ISO Agent; initially empty; keyed by reporting or escalation intent reference | Issuance and delivered acknowledgement, report contribution, completion, failure, expiry, cancellation, or supersession | Supports follow-up without assuming delivery, acceptance, or institutional action |

SIRT activation, incident category, meeting decisions, report delivery, office
coverage, and system state remain authoritative outside the Agent.

## 6. Behavioral model

### Procedure and invariants

On a decision occasion, the Agent checks what was delivered, whether CII or
sensitive scope is indicated, what response status is actually known, which
clarifications and prior intents remain open, and what independent duty
applies. An acknowledged pending equivalent intent normally suppresses a
duplicate; failure, expiry, cancellation, supersession, or material new scope
reopens the choice. The Agent may preserve uncertainty, but it must issue a
clarification, coordination, or escalation intent when a material concern
cannot be resolved from current information.

The model imposes the following substantive constraints:

- receipt, understanding, agreement, and response remain distinct;
- the Agent never inherits the SIRM's assessment or technical units' hidden
  information;
- ongoing investigation is an observation or explanation, not proof of
  adequate response;
- accountability does not confer technical execution or result authority;
- a possible incident may be escalated with uncertainty stated;
- delivery, SIRT activation, classification, containment, and reporting result
  remain scenario-owned; and
- deferral identifies an open clarification and a finite reopening condition.

Formal authority and material reporting concerns constrain the admissible set
before convenience or reliance on another office. Within that set, evidence
clarity, response status, availability, and mechanism alternatives may support
different choices.

### `DC-CISO-1` — clarify a partial security account

| Element | Account |
|---|---|
| Situation | The office receives a partial, ambiguous, or technically unclear security message, finding, or meeting account. |
| Claim and theory basis | `0616-R1-C09`--`0616-R1-C10`; event-specific institutional alternatives only. |
| Available information and state | Delivered signal, SIRM update, scope indicator, technical summary, meeting record, current assessment, open clarifications, and active coordination or reporting intents. |
| Alternatives | Ask a bounded technical question, request explicit response status, issue a coordination direction, or escalate the concern with uncertainty stated. |
| Behavioral hypothesis | Missing context can favor clarification, while CII scope, recurrence, or unresolved response state increases the value of independent follow-up. |
| Permitted intents | `request_incident_clarification`, `request_response_status`, `issue_security_coordination_direction`, `escalate_potential_cii_incident` |
| Minimum response | For a material signal, issue one substantive intent or record the exact ambiguity and the event that reopens the decision. |
| Precedence | Authority and reporting duty first; message ambiguity affects content but does not create access to missing facts. |
| Abstention boundary | Only a duplicate, unreadable, misaddressed, or clearly superseded record permits no substantive intent; corrected or new content reopens the decision. |
| Expected and forbidden pattern | Clarification targets a named gap; no automatic comprehension, dismissal, or historical failure. |
| Falsifier | Evidence that message content and scope never affected the office's response or that clarification was outside its role. |
| Consumer and deletion test | Supplies the response to fragmented technical messages; deletion would make delivery equivalent to shared understanding. |

### `DC-CISO-2` — exercise response accountability

| Element | Account |
|---|---|
| Situation | A potential incident has open technical work, uncertain SIRM or SIRT status, or unresolved coordination across units. |
| Claim and theory basis | `0616-R1-C09`, `0616-R1-C11`, `0616-R1-C13`, and `0616-R1-C19`. |
| Available information and state | Response status, technical summaries, meeting record, reporting context, availability, open clarifications, current assessment, and active coordination intents. |
| Alternatives | Request SIRT activation, issue a bounded coordination direction, coordinate reporting information, request response status, or escalate a material gap. |
| Behavioral hypothesis | Independent accountability can produce action even when technical investigation remains open; reliance on the SIRM competes with that route. |
| Permitted intents | `request_sirt_activation`, `issue_security_coordination_direction`, `coordinate_incident_reporting`, `request_response_status`, `escalate_potential_cii_incident` |
| Minimum response | Name the responsible response owner and next check, or escalate the absence of an acknowledged response route. |
| Precedence | Actual SIRT and reporting state remain institutional; the Agent cannot substitute a private assumption for acknowledgement. |
| Abstention boundary | No substantive intent is permitted only when a current, acknowledged response route already covers the material concern; expiry, failure, or new scope reopens it. |
| Expected and forbidden pattern | Accountability creates visible follow-up without performing SIRM or technical work. |
| Falsifier | Evidence that the office had no accountability for response-team action or no authority to seek coordination. |
| Consumer and deletion test | Preserves the independent oversight route; deletion collapses the Agent into a passive reporting address. |

### `DC-CISO-3` — decide whether to report or escalate

| Element | Account |
|---|---|
| Situation | Delivered evidence indicates possible CII compromise, unauthorized access, unresolved cross-system activity, or a reporting concern while confirmation remains incomplete. |
| Claim and theory basis | `0616-R1-C09`--`0616-R1-C13` and `0616-R1-C19`. |
| Available information and state | Delivered signals and uncertainty, SIRM status, CII indicator, meeting record, reporting context, availability, and active reporting intents. |
| Alternatives | Escalate a bounded potential incident, coordinate a report, request a time-bounded decisive clarification, or request explicit response action. |
| Behavioral hypothesis | CII scope and unresolved unauthorized activity favor escalation; unconfirmed-incident interpretation, incomplete understanding, or reliance on investigation may favor bounded clarification. |
| Permitted intents | `escalate_potential_cii_incident`, `coordinate_incident_reporting`, `request_incident_clarification`, `request_sirt_activation` |
| Minimum response | When the office assesses a reporting concern, issue an escalation or reporting-coordination intent; otherwise identify the missing fact and review time. |
| Precedence | Independent reporting duty constrains reliance on another office; uncertainty must be carried in the report rather than replaced by later truth. |
| Abstention boundary | Only a current acknowledged report or a time-bounded pending clarification permits no new substantive intent; new material evidence or expiry reopens it. |
| Expected and forbidden pattern | The Agent may report a potential incident without declaring final breach status; it may not wait for researcher-known impact. |
| Falsifier | Evidence that only a confirmed breach could be reported or that the Cluster ISO lacked a separate escalation route. |
| Consumer and deletion test | Supplies the independent CT-4 escalation branch; deletion merges reporting judgment into the SIRM. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_incident_clarification` | Ask for explanation of a bounded security fact, uncertainty, or relationship | SIRM, CERT, technical unit, or meeting owner | Question, cited record, relevant scope, urgency, and reply route | `DC-CISO-1`, `DC-CISO-3` | Delivery, access to answer, reply, content, delay, or failure |
| `request_response_status` | Ask who owns the response and what investigation, coordination, or escalation remains open | SIRM or institutional response route | Incident reference, requested status fields, due or review condition, and recipient | `DC-CISO-1`, `DC-CISO-2` | Delivery, acknowledgement, authoritative status, and reply |
| `issue_security_coordination_direction` | Direct or recommend a bounded information or response follow-up within accepted office authority | Named security or technical recipient | Required action or information, scope, reason, timing, and follow-up | `DC-CISO-1`, `DC-CISO-2` | Admissibility, delivery, acceptance, execution, and effect |
| `request_sirt_activation` | Ask the SIRM or incident process to activate the multi-unit response team | SIRM and institutional incident-response process | Known evidence, uncertainty, requested members or functions, and urgency | `DC-CISO-2`, `DC-CISO-3` | Delivery, authority check, activation, staffing, and attendance |
| `coordinate_incident_reporting` | Assemble or request the bounded information needed for an internal incident report | SIRM, technical contributors, or authorized reporting process | Known facts, sources, uncertainty, actions taken, open questions, recipients, and timing | `DC-CISO-2`, `DC-CISO-3` | Contributions, report creation, authorization, delivery, and feedback |
| `escalate_potential_cii_incident` | Report a potential incident or unresolved reporting concern upward | GCIO or another authorized management recipient | Sender, recipient, event time, CII or affected scope, observed evidence, uncertainty, response status, and requested decision | `DC-CISO-1`, `DC-CISO-2`, `DC-CISO-3` | Delivery, acknowledgement, classification, direction, resources, and further routing |

The Agent cannot declare that a message was understood, a team activated, a
report accepted, a control executed, or a breach confirmed. Invalid,
unauthorized, duplicate, expired, or failed requests remain visible.

## 8. Operationalization and uncertainty

`unclear`, `potential_incident`, and `reporting_concern` are qualitative
participant assessments, not probabilities or authoritative incident
categories. Moving among them requires a legitimate delivered observation or
reasoned reassessment; no historical date forces a transition.

The model separates evidence uncertainty, the Agent's uncertainty, response-
status uncertainty, availability, mechanism uncertainty, and representation
uncertainty. It contains no numerical threshold or calibrated mechanism weight.

The conservative baseline permits clarification when content or linkage is
materially incomplete, but makes every deferral inspectable through an open
question and review condition. A sensitivity variant may give independent
accountability greater precedence over reliance on technical investigation.
Neither form is validated by matching the exposed outcome.

## 9. Worked cases and falsification

### June messages without an explicit action request

- **Evidence class:** reconstructed, outcome-exposed.
- **Decision-time situation:** the office sees a delivered message or group
  update about suspicious technical activity but lacks complete context and an
  explicit request.
- **Required response:** clarify the material uncertainty, request SIRM status,
  coordinate a bounded follow-up, or escalate a potential concern.
- **Forbidden behavior:** receiving the message and thereby knowing the full
  attack, or reading later inquiry criticism.
- **Diagnostic value:** tests whether ambiguous delivery becomes silent shared
  understanding.

### 4–5 July potential breach and ongoing investigation

- **Evidence class:** reconstructed, outcome-exposed.
- **Decision-time situation:** the office sees database-query material, learns
  that an unusual program or account is involved, and knows technical
  investigation is continuing.
- **Required response:** ask what remains unknown, establish response ownership,
  and make an independent reporting decision with uncertainty carried forward.
- **Forbidden behavior:** treating the existence of investigation as proof that
  reporting responsibility has transferred to the SIRM.
- **Diagnostic value:** distinguishes reliance from independent accountability.

### 9 July cross-team consolidation

- **Evidence class:** reconstructed, outcome-exposed.
- **Decision-time situation:** a meeting assembles cross-system indicators but
  retains disputed or incorrect information about query results.
- **Required response:** voice a material concern, seek clarification, coordinate
  reporting, or escalate the potential incident; final data-loss truth remains
  unavailable.
- **Forbidden behavior:** using the next day's verified result or assuming every
  attendee shares all prior messages.
- **Diagnostic value:** tests whether integration and authority change behavior
  without requiring certainty.

### Controlled perturbations across cases

| Controlled change | Expected behavioral difference |
|---|---|
| Add an explicit response request to the otherwise unchanged June message | A bounded response-status or coordination intent becomes due; ambiguity may qualify its content but no longer supports silent receipt |
| Replace an unresolved SIRT-activation request with an acknowledged pending request | An equivalent duplicate is suppressed and follow-up waits for the stated review condition |
| Replace that pending state with failure or expiry | The office must reconsider activation, coordination, or escalation rather than treating the earlier attempt as active |
| Remove the CII scope indicator from the 4–5 July account | Clarification may remain warranted, but the independent CII-escalation basis narrows |
| Deliver the 9 July cross-system connection while keeping final data loss unknown | Integration should increase coordination or escalation without granting later verified impact |

The Definition must be revised if independent reporting or accountability
authority is withdrawn, if the office could not access the stated routes, or if
information and response status make no difference to its admissible choices.

## 10. Limitations and references

This qualitative, event-bound Definition does not assign a personality, legal
judgment, or blame; reproduce every Cluster ISO duty; identify an escalation
threshold; predict response outside the modeled episode; or establish the
effect of a counterfactual intervention. Reliance on ongoing technical work,
message comprehension, availability, and independent accountability remain
competing explanations whose relative importance is not identified.

The complete historical outcome and the inquiry's later assessments informed
construction. They help bound cases and falsifiers but provide no independent
evaluation of the model or basis for transfer to another incident.

Reference:

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
