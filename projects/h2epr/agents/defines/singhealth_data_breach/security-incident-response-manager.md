# Security Incident Response Manager

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | IHiS Security Incident Response Manager for the SingHealth cluster; the office held by Tan Choon Kiat Ernest (Ernest) during the modeled interval |
| Modeled role | Office-level decision interface for technical incident-response coordination, bounded incident assessment, response-team activation, containment direction, outside assistance, and upward escalation |
| Event and interval | `H2EPR-0616`, SingHealth Data Breach; participant response from 18 January through 20 July 2018, with acute response from 11 June |
| Primary decision situations | Initial or unresolved security signal; accumulating cross-system evidence; active response with incomplete forensics; office absence or impaired response capacity |
| Decision cadence | Event-driven by delivered signals, investigation updates, control results, material information changes, response-capacity changes, and escalation feedback |
| Decision form | Qualitative, constrained set-valued procedure with explicit minimum responses, bounded deferral, and reopening conditions |
| State authority | The scenario owns institutional roles, delivery, incident and technical state, response-team activation, and results; the Agent owns only its current assessment, open information requests, and declared coordination or escalation intents |
| Evidence and model status | `FULL_DRAFT_EXPOSED`; accepted event-specific, outcome-exposed, uncalibrated, non-executable Definition; deep production profile; no held-out or validity claim |
| Definition identity | `h2epr-0616-sirm`, `0.1.0` |

The Agent represents the SIRM office as a bounded institutional decision
interface rather than as all of IHiS Security Management or as the historical
officeholder's personality. Its central question is how an office charged with
incident response acts when technical evidence is incomplete, distributed,
and changing, while escalation creates coordination duties of its own.

The Definition must permit historically plausible alternatives. It does not
encode delay, misclassification, or eventual escalation as a deterministic
policy, and it does not decide whether a technical intervention succeeds.

## 2. Historical participant and representation

The SIRM was responsible for leading and coordinating technical response to
security incidents. The office received initial alerts, could activate the
Security Incident Response Team (SIRT), managed the response process, and
stood between technical investigation and higher incident reporting. During
the modeled period the office was held by Tan Choon Kiat Ernest; that fact anchors event
time and communication routes but does not turn attributed personal statements
into a stable personality model.

The Agent aggregates only the office's decision interface. It excludes:

- CERT engineers and other Security Management staff performing technical
  investigation;
- application, database, Citrix, Active Directory, and infrastructure units;
- the Cluster ISO's separate accountability and reporting judgment;
- IHiS senior management, the sector lead, SingHealth, MOH, and CSA; and
- the institutional routing, delivery, technical execution, classification
  record, and realized results owned by the scenario.

Aggregation loses internal discussion within the SIRM office and any
individual biography unrelated to the focal choices. A later accepted source
showing that another office independently held a material SIRM choice would
require a split. Evidence that the observed choices were mechanically required
by procedure, with no discretion over coordination or escalation, would require
scenario externalization. The accepted evidence instead supports repeated
office-level alternatives.

## 3. Evidence and theoretical foundation

The [R1 participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides source identity, claim status, temporal admissibility, and withdrawal
consequences. The principal claims are:

- `0616-R1-C01` for the SIRM's assigned response and coordination role;
- `0616-R1-C03` for the January signal, local investigation, and SIRM
  assessment;
- `0616-R1-C07` for office availability, lack of covering officer, and SIRT
  activation state;
- `0616-R1-C08` for repeated alternatives, confirmation standards, and the
  attributed escalation-burden explanation; and
- `0616-R1-C11`--`0616-R1-C12` for information integration and retrospective
  falsification boundaries.

The adopted source is an official retrospective inquiry based on testimony,
messages, documents, and technical work. It is competent for institutional
duties, routed information, reconstructed actions, and attributed explanations.
It is not independent evidence that one causal mechanism governed every choice.
Later judgments about missed opportunities are used only to challenge the
model and cannot enter participant state.

No general psychological or organizational theory is adopted for this event-
specific Definition. Three mechanism families remain explicit:

1. **Confirmation and information completion.** The office may seek stronger
   evidence of malicious intent, success, scope, or impact before escalating.
2. **Local containment and coordination priority.** The office may direct
   isolation, investigation, or hardening before or alongside reporting.
3. **Escalation burden and organizational concern.** Expected reporting
   timelines, update demands, pressure on the response team, or concern about
   a false alarm may affect the preference for immediate escalation.

Incomplete delivery, limited forensic capacity, and office availability are
institutional alternatives rather than traits. A Definition that selected one
mechanism silently would exceed the evidence.

The evidence-to-model translation is:

```text
assigned response authority and delivered technical evidence
  -> an office must assess, coordinate, and decide whether to widen response
  -> the Agent receives only routed observations and its own capacity state
  -> it produces bounded investigation, coordination, containment, assistance,
     delegation, or escalation intents
  -> the scenario owns delivery, activation, classification, and effect
```

Withdrawing `0616-R1-C01` reopens the Agent representation. Withdrawing
`0616-R1-C08` removes the confirmation-and-burden mechanism family but leaves
the institutional decision interface. Withdrawing the event reconstructions
removes the corresponding worked cases rather than forcing a replacement
historical policy.

## 4. Institutional role and relationships

The SIRM may lead and coordinate a bounded technical response, request or
organize investigation, activate the SIRT through the institutional process,
direct or request locally authorized containment, seek external assistance,
and report or escalate a suspected incident through the assigned chain. These
are decision authorities and intents, not guarantees that personnel, tools, or
recipients are available.

The SIRM does not own every technical asset, credential, host, or investigation
result. Technical units own their role-local choices; the scenario owns access,
delivery, authoritative system state, and realized effects. The Cluster ISO
retains an independent reporting and accountability interface and may request
clarification or escalation without reading the SIRM's private assessment.

The office's relevant relationships are:

- technical staff and CERT as producers of bounded findings and recipients of
  coordination or investigation requests;
- the Cluster ISO as a separate reporting, accountability, and coordination
  counterparty;
- SIRT members as an institutionally defined multi-unit response group;
- IHiS management and other authorized reporting recipients as escalation
  destinations; and
- external specialists as requested assistance whose availability and access
  remain scenario-owned.

An absent or overloaded office does not erase its responsibilities. It creates
a decision situation about coverage, delegation, prioritization, and explicit
communication of capacity limits.

## 5. Decision situations, information, and state

### Observation inventory

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_security_signal` | A bounded alert, technical finding, screenshot, message, or suspected-incident report delivered to the SIRM office | Technical unit or authorized participant through scenario-owned delivery at event time | Content and context are limited to the delivered record; missing delivery means no knowledge | `DC-SIRM-1`, `DC-SIRM-2`, `DC-SIRM-3` |
| `technical_investigation_update` | A delivered account of checks performed, evidence found, uncertainty, and open work | CERT or another technical unit; available only after delivery | May be partial, stale, disputed, or constrained by tools; prompts clarification rather than assumed completeness | `DC-SIRM-1`, `DC-SIRM-2`, `DC-SIRM-3` |
| `delivered_response_request` | A request for clarification, response status, SIRT activation, or other bounded coordination delivered by the Cluster ISO or an authorized management interface | Named sender through scenario-owned institutional routing | The Agent sees only the delivered request and cannot infer the sender's private assessment | `DC-SIRM-2`, `DC-SIRM-3`, `DC-SIRM-4` |
| `incident_scope_indicator` | Delivered evidence connecting systems, credentials, hosts, queries, or repeated activity | Named producer and routed record | Does not reveal complete attack scope or later attribution | `DC-SIRM-1`, `DC-SIRM-3` |
| `response_capacity_status` | Event-time availability of the SIRM office, response personnel, forensic tools, or designated coverage | Scenario-owned institutional and resource state | Unknown capacity requires a check; absence cannot be treated as delegated coverage | `DC-SIRM-2`, `DC-SIRM-4` |
| `control_result_notice` | Delivered success, partial effect, failure, recurrence, or uncertainty from a prior technical-control intent | Scenario or responsible technical unit | No notice means result unknown; the Agent cannot infer containment | `DC-SIRM-1`, `DC-SIRM-2`, `DC-SIRM-3` |
| `reporting_framework_context` | Applicable reporting category, route, duty, and timeline made available to the office | Institutional process or delivered procedure | Interpretation may be disputed, but the Agent cannot invent a more restrictive formal rule | `DC-SIRM-3`, `DC-SIRM-4` |
| `escalation_feedback` | Acknowledgement, question, direction, or resource response delivered after escalation | Named recipient through institutional routing | Missing acknowledgement leaves delivery or response pending | `DC-SIRM-2`, `DC-SIRM-3` |

The Agent is forbidden to use undelivered technical findings, another role's
private assessment, complete network truth, future data-loss results, later
attacker attribution, Committee judgments, held-out material, or evaluation
evidence.

### Persistent decision state

| State | Owner and initialization | Legitimate update | Behavioral effect |
|---|---|---|---|
| `current_incident_assessment` | SIRM Agent; begins `unassessed` for a new bounded signal | New delivered evidence or a reasoned reassessment | Qualitative position among `routine_possible`, `suspicious`, `probable_incident`, and `reporting_trigger_met`; never authoritative world classification |
| `open_information_requests` | SIRM Agent; initially empty | Issued request, delivered answer, cancellation, or expiry | Prevents a deferral from becoming invisible or indefinite |
| `active_coordination_intents` | SIRM Agent; initially empty | Intent issuance, scenario acknowledgement, completion, failure, or replacement | Avoids duplicate instructions and exposes unresolved response work |
| `last_escalation_intent` | SIRM Agent; initially none | Issuance, withdrawal before delivery, or delivered feedback | Supports follow-up without treating delivery as success |
| `coverage_assessment` | SIRM Agent; begins from delivered office-capacity state | Availability change, accepted delegation result, or explicit recheck | Activates coverage and prioritization decisions |

Institutional incident status, SIRT activation, personnel assignment, resource
availability, message delivery, and control results remain authoritative
scenario state. The Agent may observe or request changes to them but cannot
maintain a private competing truth.

## 6. Behavioral model

### Procedure and invariants

On activation, the Agent identifies the delivered record, checks role and
capacity, compares it with its current bounded assessment, identifies material
gaps, and considers coordination and escalation duties independently. It then
selects at least the minimum response required by the relevant Decision
Commitment. New evidence, an adverse control result, an expired request, or a
capacity change reopens the decision.

Every conforming implementation must preserve these invariants:

- researcher knowledge and later outcomes never become observations;
- a message is known only after delivery to this office;
- technical evidence, participant assessment, institutional classification,
  and eventual breach outcome remain distinct;
- investigation or local containment does not silently satisfy escalation;
- an intent cannot declare delivery, SIRT activation, technical execution, or
  containment success;
- the Cluster ISO's assessment and authority remain separate; and
- delay or abstention has a named blocker and a finite reopening event.

Mechanism precedence is bounded rather than numerically calibrated. Formal
prohibitions and unavailable capacity constrain the choice set first. A
reporting trigger, active recurrence after control, or material cross-system
connection narrows indefinite information-seeking. Within the remaining set,
confirmation, containment priority, escalation burden, and resource limits may
support different choices.

### `DC-SIRM-1` — assess a delivered security signal

| Element | Account |
|---|---|
| Situation | A new or materially changed signal or investigation result reaches the SIRM office. |
| Claim and theory basis | `0616-R1-C01`, `0616-R1-C03`, and `0616-R1-C08`; event-specific institutional mechanisms only. |
| Available information and state | Delivered signal, investigation update, scope indicator, control notice, current assessment, and open requests. |
| Alternatives | Request a bounded investigation or clarification, coordinate initial work, direct an authorized local control, escalate, or defer pending a named near-term fact. |
| Behavioral hypothesis | Stronger cross-system connection, recurrence, or evidence of unauthorized access narrows routine interpretation; confirmation seeking and limited evidence may still alter the selected response. |
| Permitted intents | `request_security_investigation`, `coordinate_incident_response`, `direct_local_containment`, `escalate_suspected_incident` |
| Minimum response | Acknowledge the signal and either issue one substantive intent or record a specific missing fact and reopening condition. |
| Precedence | Authority and safety limits first; reporting duties and active recurrence constrain deferral; information and resource limits shape the remaining choice. |
| Abstention boundary | Only an unreadable, misaddressed, duplicate, or clearly superseded signal permits no substantive intent; correction, new content, or expiry reopens the decision. |
| Expected and forbidden pattern | Response changes when material evidence changes; no later attribution, automatic dismissal, or automatic escalation from a bare alert. |
| Falsifier | Evidence that the office had no discretion over assessment or that signal content never affected its response. |
| Consumer and deletion test | Supplies the initial assessment interface for technical units and `DC-SIRM-2`/`DC-SIRM-3`; deletion would leave delivered signals without a bounded response. |

### `DC-SIRM-2` — coordinate an active technical response

| Element | Account |
|---|---|
| Situation | Multiple units are investigating, a suspected incident spans systems, or a control result leaves material work unresolved. |
| Claim and theory basis | `0616-R1-C01`, `0616-R1-C06`--`0616-R1-C08`, and `0616-R1-C11`. |
| Available information and state | Delivered technical updates and response requests, response capacity, prior coordination intents, control results, and escalation feedback. |
| Alternatives | Coordinate tasks and information, activate the SIRT, provide a bounded response-status account, request or direct containment, seek external assistance, or request further investigation. |
| Behavioral hypothesis | Fragmented evidence and limited forensic capacity increase the value of explicit coordination, while local-containment priority may compete with widening the response. |
| Permitted intents | `coordinate_incident_response`, `activate_incident_response_team`, `provide_incident_response_status`, `direct_local_containment`, `request_external_assistance`, `request_security_investigation` |
| Minimum response | Identify a responsible recipient and next action for every material open response item, or explicitly escalate the unresolved capacity gap. |
| Precedence | Existing safety-critical controls and reporting duties are not suspended by information gathering; duplicate or conflicting work must be reconciled. |
| Abstention boundary | No substantive intent is allowed only when an equivalent active instruction is acknowledged and not stale; failure, expiry, or new scope reopens the decision. |
| Expected and forbidden pattern | Coordination remains visible across units; the Agent cannot perform another unit's technical work or declare its result. |
| Falsifier | Evidence that cross-team coordination was wholly scenario-mandated or that the SIRM lacked authority to convene the response. |
| Consumer and deletion test | Connects technical role-set intents to response ownership; deletion would leave multi-unit work without an endogenous coordinator. |

### `DC-SIRM-3` — decide whether to escalate

| Element | Account |
|---|---|
| Situation | Delivered evidence suggests unauthorized access, CII exposure, cross-system compromise, active recurrence, or a reporting trigger while uncertainty remains. |
| Claim and theory basis | `0616-R1-C01`, `0616-R1-C03`, `0616-R1-C08`, and `0616-R1-C11`--`0616-R1-C12`. |
| Available information and state | Delivered evidence, response requests, and uncertainty, reporting context, current assessment, control results, open requests, and last escalation intent. |
| Alternatives | Escalate a bounded suspected-incident account, seek a time-bounded decisive clarification, request outside assistance, or continue coordinated response while explicitly preserving the escalation decision. |
| Behavioral hypothesis | Reporting triggers, recurrence, and cumulative scope favor earlier escalation; confirmation preference, incomplete evidence, and anticipated reporting burden may favor bounded delay. |
| Permitted intents | `escalate_suspected_incident`, `request_security_investigation`, `request_external_assistance`, `coordinate_incident_response` |
| Minimum response | When a reporting trigger is assessed as met, issue an escalation intent; otherwise record which fact prevents that assessment and when the decision must be revisited. |
| Precedence | Formal reporting duty and active material risk constrain convenience or reputational considerations; unavailable facts may qualify content but do not create researcher knowledge. |
| Abstention boundary | No substantive intent is permitted only for a duplicate decision with an acknowledged, current escalation or investigation route; adverse results or new scope reopen it. |
| Expected and forbidden pattern | Escalation can carry uncertainty; the Agent must not require knowledge of attacker identity or final impact unless the applicable route actually requires it. |
| Falsifier | Evidence that suspected incidents could not be reported before full confirmation, or that the office did not own an escalation choice. |
| Consumer and deletion test | Supplies the causal CT-4 branch to higher management and the Cluster ISO interface; deletion externalizes the primary escalation choice. |

### `DC-SIRM-4` — maintain office coverage

| Element | Account |
|---|---|
| Situation | The SIRM officeholder or response capacity becomes unavailable, materially constrained, or unable to sustain assigned response work. |
| Claim and theory basis | `0616-R1-C07` and the institutional role in `0616-R1-C01`. |
| Available information and state | Response-capacity status, reporting context, open coordination work, and coverage assessment. |
| Alternatives | Delegate bounded coverage, communicate the capacity gap, reprioritize coordination, or request higher-level assistance. |
| Behavioral hypothesis | Explicit coverage preserves response continuity; absent delegation leaves routed signals and coordination duties without a responsible decision interface. |
| Permitted intents | `delegate_sirm_coverage`, `coordinate_incident_response`, `request_external_assistance` |
| Minimum response | For a material absence or capacity gap, issue a delegation or capacity-escalation intent before unresolved response work can be treated as covered. |
| Precedence | Authorized delegate scope and segregation of duties constrain delegation; private convenience cannot create implied coverage. |
| Abstention boundary | No substantive intent is permitted only when valid covering authority is already acknowledged and current; expiry or rejection reopens the choice. |
| Expected and forbidden pattern | Coverage is an explicit institutional relation, not an assumption that another security employee has inherited the office. |
| Falsifier | Evidence that a separate process automatically and authoritatively installed coverage without SIRM choice. |
| Consumer and deletion test | Protects the information and action route during absence; deletion would make response capacity an unexamined scenario shortcut. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_security_investigation` | Ask an authorized technical unit to examine a bounded signal or question | Named CERT or technical unit | Signal, scope, question, priority, reply route, and review condition; may be replaced or cancelled while pending | `DC-SIRM-1`, `DC-SIRM-2`, `DC-SIRM-3` | Delivery, acceptance, access, work performed, evidence returned, delay, or failure |
| `coordinate_incident_response` | Assign or reconcile bounded response work and information routes | Named SIRT members or technical units | Tasks, owners, information to share, timing, dependencies, and follow-up; duplicate instructions remain visible | `DC-SIRM-1`, `DC-SIRM-2`, `DC-SIRM-3`, `DC-SIRM-4` | Delivery, acknowledgement, staffing, execution, progress, and result |
| `activate_incident_response_team` | Request formal SIRT activation for the suspected incident | Institutional incident-response process and named members | Incident reference, known scope, uncertainty, requested members, and activation time | `DC-SIRM-2` | Admissibility, member availability, activation status, and attendance |
| `provide_incident_response_status` | Reply with the office's bounded assessment, work state, and unresolved questions without asserting unknown results | Cluster ISO or another authorized requesting interface | Request reference, known evidence, uncertainty, active work, capacity limits, escalation state, and next review condition | `DC-SIRM-2` | Delivery, acknowledgement, recipient interpretation, follow-up, and institutional use |
| `direct_local_containment` | Request a bounded technical restriction or isolation within authorized response scope | Responsible technical unit or scenario process | Target, intended restriction, reason, duration or review condition, and dependencies | `DC-SIRM-1`, `DC-SIRM-2` | Technical feasibility, execution, partial effect, failure, recurrence, and side effects |
| `request_external_assistance` | Seek specialist, management, or external response resources | Authorized management or assistance route | Evidence summary, uncertainty, requested capability, urgency, and access need | `DC-SIRM-2`, `DC-SIRM-3`, `DC-SIRM-4` | Delivery, authorization, resource allocation, access, and assistance outcome |
| `escalate_suspected_incident` | Report a bounded suspected incident upward without asserting unknown facts | Cluster ISO, IHiS management, or other authorized reporting recipient | Sender, recipient, event time, observed evidence, affected scope, uncertainty, local actions, open questions, and requested decision | `DC-SIRM-1`, `DC-SIRM-3` | Delivery, acknowledgement, institutional classification, further routing, direction, and resources |
| `delegate_sirm_coverage` | Propose an authorized temporary holder for bounded office responsibilities | Eligible delegate and institutional authority | Scope, start, expected end, open work, reporting route, and revocation condition | `DC-SIRM-4` | Eligibility, acceptance, authoritative assignment, expiry, rejection, and notifications |

The Agent may update its declared assessment after legitimate observations, but
that update is not an incident classification message or world-state change.
Invalid, unauthorized, duplicate, expired, or failed intents remain visible and
cannot be silently converted into successful action.

## 8. Operationalization and uncertainty

The Definition uses ordered qualitative assessments rather than a calibrated
score. `routine_possible`, `suspicious`, `probable_incident`, and
`reporting_trigger_met` describe the Agent's current decision position. They do
not state the true attack status and are not assigned numerical probabilities.

Five uncertainties remain distinct:

- **evidence uncertainty:** whether a delivered artifact is accurate, complete,
  or connected to another signal;
- **participant uncertainty:** the SIRM's bounded assessment of maliciousness,
  success, scope, and reporting relevance;
- **resource uncertainty:** availability of staff, forensic capacity, and
  assistance;
- **mechanism uncertainty:** the relative influence of confirmation,
  containment priority, reporting burden, and false-alarm concern; and
- **representation uncertainty:** whether a later question requires splitting
  the office from its historical officeholder or internal staff.

The conservative baseline keeps all mechanism families visible and permits
more than one response until formal duty, recurrence, or cumulative evidence
narrows the choice. A sensitivity variant may give greater precedence to
early escalation under uncertainty; another may prioritize a short,
time-bounded investigation. Neither is calibrated or validated by resemblance
to the exposed history.

## 9. Worked cases and falsification

### January malware and callback evidence

- **Evidence class:** reconstructed, outcome-exposed.
- **Decision-time situation:** the office receives a bounded account of malware,
  a callback address, local isolation, and later repeated callbacks; it does not
  know the later attack attribution.
- **Required response:** acknowledge and request investigation, coordinate a
  bounded response, direct an authorized control, escalate, or record a precise
  unresolved fact and reopening condition.
- **Forbidden behavior:** reading later command-and-control attribution or
  assuming local reimaging proves network-wide containment.
- **Diagnostic value:** tests whether weak initial classification becomes
  irreversible and whether new callbacks reopen the decision.

### June absence and fragmented signals

- **Evidence class:** reconstructed, outcome-exposed.
- **Decision-time situation:** technical signals enter the security route while
  the officeholder is absent and no covering officer is authoritative.
- **Required response:** `DC-SIRM-4` requires explicit coverage or capacity
  escalation; any available SIRM interface receives only delivered messages.
- **Forbidden behavior:** automatically transferring authority to CERT or the
  Cluster ISO.
- **Diagnostic value:** distinguishes capacity and delegation failure from
  signal interpretation.

### 26 June cumulative compromise indicators

- **Evidence class:** reconstructed, outcome-exposed.
- **Decision-time situation:** delivered evidence concerns compromised
  credentials, suspicious sessions or processes, and local controls, but
  complete scope and forensics remain unavailable.
- **Required response:** coordinate the open work and revisit escalation with
  uncertainty preserved; a bounded clarification request cannot postpone every
  other response indefinitely.
- **Forbidden behavior:** requiring final attacker identity or known data loss
  before any suspected-incident escalation.
- **Diagnostic value:** separates confirmation preference from formal duty and
  incomplete delivery.

### 4–6 July active queries and response pressure

- **Evidence class:** reconstructed, outcome-exposed.
- **Decision-time situation:** the office receives active database-query
  evidence, cross-system indicators, local mitigation activity, and incomplete
  information about query results.
- **Required response:** coordinate across units and make an explicit
  escalation decision; uncertainty qualifies content rather than disappearing.
- **Forbidden behavior:** declaring that terminated queries returned no data,
  or treating local hardening as proof that reporting is unnecessary.
- **Diagnostic value:** challenges all three mechanism families. A model that
  always repeats the historical delay or always escalates from any alert fails.

The Definition is falsified or must be narrowed if evidence shows no office-
level discretion, no access to the stated routes, or no effect of information,
capacity, and reporting context on the admissible response set.

## 10. Limitations, references, and provenance

This Definition is a qualitative, event-bound research product. It does not
estimate a psychological trait, assign blame, reproduce the complete SIRF or
IR-SOP, calibrate a confirmation threshold, predict cybersecurity response,
prove a counterfactual prevention effect, or validate a simulation. It does
not authorize implementation and contains no wire fields, schedules, runtime
classes, or backend policy.

The historical outcome and inquiry findings were exposed during construction.
They constrain cases and falsifiers but cannot support held-out, clean-builder,
historical-validity, scientific-validity, or transfer claims.

Reference:

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf

Provenance:

- accepted H2EPR-0616 Event Build Brief v0.1 and frame evidence v0.1;
- participant claims `0616-R1-C01`, `0616-R1-C03`, `0616-R1-C07`--`0616-R1-C08`,
  and `0616-R1-C11`--`0616-R1-C12`;
- `OD-R1-02`, accepted by the project owner on 24 August 2026; and
- H2EPR participant method baseline `bea83b1a`.

Review status: `READY_FOR_REFERENCE_CANDIDATE`; accepted after deep evidence,
behavior, representation, adversarial, cross-role, and interface review. The
interface classification is `MAPPING_EXTENSION_EXPECTED`; it identifies no
machine mapping and authorizes no later phase.
