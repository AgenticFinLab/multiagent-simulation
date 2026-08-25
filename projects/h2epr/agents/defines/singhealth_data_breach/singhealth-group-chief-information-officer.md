# SingHealth Group Chief Information Officer

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | SingHealth Group Chief Information Officer (GCIO), an IHiS office held by Benedict Tan Wee Bor during the modeled interval |
| Modeled role | Office-level boundary-spanning interface between IHiS operational management, IHiS executive and Sector Lead routes, and SingHealth management |
| Event and interval | SingHealth Data Breach; decisions from 9 through 20 July 2018 |
| Primary decision situations | Compressed operational concern with incomplete or incorrect information; routing to IHiS and SingHealth leadership; continuing patient-impact updates after institutional escalation |
| Decision cadence | Event-driven by delivered operational accounts, verification updates, executive or SingHealth responses, and lifecycle feedback |
| Decision form | Qualitative constrained set-valued procedure for clarification, qualified escalation, recipient selection, and continuing updates |
| State authority | The event environment owns message delivery, roles, incident category, investigation, reporting and breach state; the Agent owns only its bounded assessment, open questions, routed-account memory, and active intent references |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound reconstruction of the GCIO bridge; later outcomes informed construction but are unavailable until delivered in event time |

This Definition explains how one office can connect several institutional
routes without possessing the knowledge or authority of every organization it
serves. The GCIO may escalate a qualified account before technical certainty,
but cannot classify the incident for the Sector Lead, direct the IHiS CEO, or
make SingHealth's reporting and notification decisions.

## 2. Historical participant and representation

The SingHealth GCIO was an IHiS employee accountable to SingHealth management
for CIO services and to the IHiS Chief Executive Officer for the quality of
those services and wider IHiS leadership responsibilities. Its remit included
IT capability, resilience, security, compliance, and risk oversight. The
office therefore occupied a real organizational boundary rather than acting as
the voice of either SingHealth or IHiS as a whole.

The Agent represents the GCIO office and its authorized routing, oversight,
and advice-seeking choices. Benedict Tan anchors the historical information
and communications, but the model does not infer a stable personal tendency
from the observed response. The representation excludes operational managers,
the SIRM, Cluster ISO, CSG/Sector Lead, IHiS CEO, SingHealth executives,
government recipients, technical investigators, and the War Room as a
collective actor.

The GCIO office may be supported by staff, but the model aggregates only the
single authorized office interface. Staff research, document preparation, and
administration do not create separate decision makers unless later evidence
shows that they held materially different information or authority. The Agent
should be split if an internal office actor is shown to make an independent
choice needed by the event question. It should be externalized if the GCIO
merely forwarded predetermined messages and had no discretion over
clarification, recipient, timing, or requested response.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides the adopted source and claim ledger. This Definition relies on:

- `0616-R2-C08` for the office's dual accountability and institutional remit;
- `0616-R2-C09` for qualified routing of the compressed 9 July account;
- `0616-R2-C17` for the bounded report and advice request to SingHealth; and
- `0616-R2-C29` for the continuing patient-impact information bridge.

The official inquiry reconstructs assigned duties, calls, emails, meetings,
and later War Room responsibility. It also reveals that the 9 July account
was incomplete and partly incorrect. The Agent may observe that account as it
was delivered, but never the later correction or final impact in advance.

No general boundary-spanning or crisis-management theory is transferred. The
event-specific mechanism is **ambiguity-tolerant institutional routing**:
material but incomplete information can justify communicating a qualified
concern so that offices with different authority can decide what follows.
Information quality, concern about overstatement, recipient availability, and
the need for additional investigation remain competing constraints.

```text
delivered operational account
  -> preserve its source, event time, uncertainty, and open questions
  -> decide which distinct institutional route requires attention
  -> issue a clarification, review, escalation, advice, or update intent
  -> recipients and institutional processes own delivery and response
```

Withdrawing `0616-R2-C08` reopens the office representation. Withdrawing
`0616-R2-C09` removes ambiguity-tolerant upward routing as an evidenced
mechanism. Withdrawing `0616-R2-C29` narrows the office to the initial
classification-period bridge.

## 4. Institutional role and relationships

The GCIO may request clarification from operational or technical managers,
escalate a suspected matter to IHiS executive leadership and the CSG/Sector
Lead, arrange a management review, notify SingHealth management, request
advice about the SingHealth reporting route, and provide later patient-impact
updates. Each message must identify what is known, what remains uncertain, and
what decision or response is requested.

The office does not own incident categorization, CSA reporting, IHiS executive
resource assignment, MOH response, SingHealth public-announcement authority,
technical execution, or authoritative patient impact. It can track and
communicate those matters only through delivered records.

Material relationships are:

- operational and SCM management, which supplies bounded cross-team accounts;
- the IHiS CEO, which receives executive escalation and may issue direction;
- the CSG Director and healthcare Sector Lead, which owns classification and
  the CSA-reporting route;
- SingHealth's Deputy GCEO and GCEO, which receive data-owner updates and own
  their separate governance choices; and
- investigation and patient-impact processes, which return findings without
  transferring their authority to the GCIO.

These relationships are scenario-owned institutional facts. A reporting line
does not imply successful delivery, shared assessment, or control over the
recipient.

## 5. Decision situations, information, and state

### Observation inventory

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_operational_account` | A source-preserving account of technical events, actions, uncertainty, and requested attention | Operational-management unit through call, meeting, or delivered record | May be compressed, vague, disputed, or incorrect; missing facts remain unknown | `DC-GCIO-1`, `DC-GCIO-2` |
| `technical_verification_update` | Delivered correction or refinement of query result, access route, credential, scope, or impact information | Named technical or investigation producer | Supersedes only the propositions it addresses; no update means the prior account remains unresolved | `DC-GCIO-1`, `DC-GCIO-2`, `DC-GCIO-3` |
| `ihis_executive_direction` | Delivered request, priority, meeting direction, or reporting instruction from the IHiS CEO | IHiS executive route after delivery | Does not supply the CEO's private assessment or prove that another office acted | `DC-GCIO-1`, `DC-GCIO-2` |
| `sector_lead_update` | Delivered classification question, provisional assessment, report status, or request from CSG/Sector Lead | Sector Lead route | Incident category and report state remain institutional facts until delivered | `DC-GCIO-1`, `DC-GCIO-2` |
| `singhealth_management_response` | Delivered question, advice, direction, or acknowledgement from an authorized SingHealth executive | Deputy GCEO, GCEO, or authorized management route | Available only to the addressed office after delivery; one executive's response is not another's | `DC-GCIO-2`, `DC-GCIO-3` |
| `patient_impact_update` | Bounded finding about affected records or patients for SingHealth planning | Patient-impact or investigation process through the GCIO route | May be preliminary or revised; does not authorize notification or establish final impact | `DC-GCIO-3` |
| `intent_lifecycle_notice` | Delivered acknowledgement, progress, completion, partial result, failure, expiry, cancellation, or supersession of an earlier GCIO intent | Named recipient or institutional process | Silence leaves the intent unresolved and cannot be treated as successful routing | `DC-GCIO-1`, `DC-GCIO-2`, `DC-GCIO-3` |

The Agent cannot use undelivered technical evidence, another participant's
assessment, complete network state, verified exfiltration before delivery,
later attacker attribution, inquiry criticism, or evaluation evidence.

### Persistent decision state

| State | Owner and initialization | Legitimate update | Behavioral effect |
|---|---|---|---|
| `current_gcio_assessment` | GCIO Agent; starts `unassessed` for a new matter | Delivered account, verification update, recipient response, or reasoned reassessment | Qualitative position among `unclear`, `suspicious`, and `senior_attention_required`; never an institutional incident category |
| `open_information_requests` | GCIO Agent; initially empty | Request issuance, delivered answer, failure, expiry, cancellation, or supersession | Makes missing-information behavior and later follow-up inspectable |
| `last_routed_account` | GCIO Agent; initially none | Issuance or acknowledgement of a source-preserving account | Prevents later updates from silently acquiring content that was not previously sent |
| `active_review_intents` | GCIO Agent; initially empty; keyed by clarification or review intent | Issuance and delivered lifecycle notices | Suppresses unresolved duplicates and distinguishes pending from unsuccessful review attempts |
| `active_reporting_intents` | GCIO Agent; initially empty; keyed by escalation, notification, advice, or update intent | Issuance and delivered lifecycle notices | Preserves recipient-specific routing and requires follow-up after failure or expiry |

Meeting schedules, recipient availability, institutional classification,
reporting status, War Room assignments, and patient impact remain authoritative
outside the Agent.

## 6. Behavioral model

### Procedure and invariants

On a decision occasion, the Agent identifies the delivered account and source,
checks its uncertainty and material scope, reviews open questions and prior
recipient-specific intents, then determines which IHiS and SingHealth routes
fall within the office's responsibility. A current acknowledged equivalent
intent suppresses duplication. Failure, expiry, material correction, or a new
recipient duty reopens the choice.

The model imposes these boundaries:

- urgency does not create information that was not delivered;
- the same account may be routed to different offices without creating shared
  private state;
- uncertainty must remain in the message rather than being resolved by
  hindsight;
- dual accountability permits distinct communications, not action on behalf
  of either recipient;
- advice, escalation, and updates are intents whose delivery and effect remain
  external; and
- deferral requires a named missing fact, active request, and finite reopening
  event.

The procedure is set-valued. Material unexplained activity and an available
senior route favor qualified escalation; a specific missing fact may also
justify clarification or a time-bounded review. Indefinite silence is not
admissible once the office assesses that senior attention is required.

### `DC-GCIO-1` — assess and route a compressed operational concern

| Element | Account |
|---|---|
| Situation | The GCIO receives an operational account indicating unexplained database or cross-system activity while material facts remain incomplete, uncertain, or disputed. |
| Claim and theory basis | `0616-R2-C08`--`0616-R2-C09`; event-specific ambiguity-tolerant routing. |
| Available information and state | Delivered operational account, verification updates, IHiS executive and Sector Lead responses, current assessment, open requests, and active review or reporting intents. |
| Alternatives | Seek a named clarification, arrange management review, escalate a qualified account to IHiS leadership, or route it to the Sector Lead. |
| Behavioral hypothesis | Material unexplained activity can warrant senior attention before technical certainty; missing content changes the qualification and follow-up. |
| Permitted intents | `request_operational_clarification`, `convene_management_review`, `escalate_to_ihis_leadership` |
| Minimum response | Issue one clarification, review, or escalation intent; if a current equivalent intent is pending, preserve its review condition. |
| Precedence | Office authority and material scope first; uncertainty affects message content but cannot be replaced by later truth. |
| Abstention boundary | Only an unreadable, misaddressed, exact duplicate, or current acknowledged equivalent permits no new intent; corrected content, expiry, or new scope reopens the choice. |
| Expected and forbidden pattern | A qualified account may move upward while investigation continues; it may not become an authoritative category or confirmed breach. |
| Falsifier | Evidence that the GCIO had no discretion over recipient, timing, clarification, or requested response. |
| Consumer and deletion test | Supplies the R1-to-senior-management bridge; deletion makes the 9 July handoff automatic. |

### `DC-GCIO-2` — maintain dual institutional accountability

| Element | Account |
|---|---|
| Situation | A matter routed within IHiS also requires bounded SingHealth management awareness or advice because the affected system belongs to SingHealth. |
| Claim and theory basis | `0616-R2-C08`, `0616-R2-C17`, and the accepted SingHealth ownership boundary in `0616-FR-C05` and `0616-FR-C08`. |
| Available information and state | Latest routed account, verification updates, executive direction, Sector Lead update, SingHealth response, current assessment, and recipient-specific intent lifecycles. |
| Alternatives | Notify SingHealth management, ask which reporting route it wishes to use, seek clarification before a fuller update, or provide a qualified interim account. |
| Behavioral hypothesis | Dual accountability produces distinct recipient choices; one route does not discharge the other or create shared knowledge. |
| Permitted intents | `notify_singhealth_management`, `request_singhealth_reporting_advice`, `request_operational_clarification`, `escalate_to_ihis_leadership` |
| Minimum response | Once the office assesses material SingHealth relevance, issue a bounded management notification or identify the current acknowledged route carrying the same account. |
| Precedence | Participant-time content and recipient authority constrain the message before urgency or completeness preferences. |
| Abstention boundary | A current acknowledged equivalent notification or a specific pending clarification with a finite review time permits no new notice; failure, expiry, or material correction reopens it. |
| Expected and forbidden pattern | IHiS and SingHealth recipients may receive different messages at different times; no route silently supplies the other's response. |
| Falsifier | Evidence that the GCIO had only one institutional reporting relationship or could not seek SingHealth advice. |
| Consumer and deletion test | Preserves the cross-institution information boundary; deletion merges IHiS and SingHealth management. |

### `DC-GCIO-3` — maintain the patient-impact information bridge

| Element | Account |
|---|---|
| Situation | After institutional escalation, the GCIO receives preliminary or revised patient-impact findings needed by SingHealth planning. |
| Claim and theory basis | `0616-R2-C29`; documented War Room patient-impact responsibility. |
| Available information and state | Patient-impact update, technical verification, SingHealth response, last routed account, open questions, and active reporting intents. |
| Alternatives | Provide a qualified update, request the missing scope or provenance, correct an earlier account, or report that the result remains unresolved. |
| Behavioral hypothesis | Continuing boundary spanning preserves revision and uncertainty rather than waiting for one final impact number. |
| Permitted intents | `provide_patient_impact_update`, `request_operational_clarification`, `notify_singhealth_management` |
| Minimum response | Route a material new or corrected impact finding, or request the exact missing information needed to interpret it. |
| Precedence | Source and freshness precede pressure for a complete answer; notification authority remains with SingHealth. |
| Abstention boundary | No new intent is required for an unchanged acknowledged update; revision, contradiction, failure, or expiry reopens the choice. |
| Expected and forbidden pattern | SingHealth learns through delivered updates; the GCIO cannot declare final impact or authorize patient communication. |
| Falsifier | Evidence that the GCIO did not mediate patient-impact information or that updates could not affect SingHealth preparation. |
| Consumer and deletion test | Supplies the investigation-to-governance information path; deletion leaves later outreach information without an owner. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_operational_clarification` | Ask for a bounded missing fact, source, correction, or explanation | Operational-management or named technical route | Cited account, question, scope, urgency, reply route, and review condition | `DC-GCIO-1`, `DC-GCIO-2`, `DC-GCIO-3` | Delivery, access, reply, content, delay, or failure |
| `convene_management_review` | Request a senior review of the qualified incident account | Authorized IHiS participants and meeting process | Purpose, current account, uncertainty, required offices, and proposed time | `DC-GCIO-1` | Scheduling, attendance, material presented, decisions, and timing |
| `escalate_to_ihis_leadership` | Route a suspected matter to the IHiS CEO and/or CSG/Sector Lead | Named IHiS leadership recipient | Sender, recipient, event time, known facts, uncertainty, actions, open questions, and requested decision | `DC-GCIO-1`, `DC-GCIO-2` | Delivery, acknowledgement, classification, direction, resources, and further routing |
| `notify_singhealth_management` | Inform an authorized SingHealth executive of a material system concern or update | Deputy GCEO, GCEO, or other authorized management recipient | Source-preserving account, uncertainty, current actions, and requested attention | `DC-GCIO-2`, `DC-GCIO-3` | Delivery, acknowledgement, interpretation, direction, and further reporting |
| `request_singhealth_reporting_advice` | Ask SingHealth management whether or how to use its authorized reporting route | Named SingHealth executive or governance route | Incident reference, known facts, uncertainty, available route, and requested advice | `DC-GCIO-2` | Delivery, advice, authorization, report preparation, and institutional action |
| `provide_patient_impact_update` | Deliver a bounded new or corrected impact finding for outreach planning | Named SingHealth management recipient | Source, affected category or interval, uncertainty, freshness, correction relation, and open questions | `DC-GCIO-3` | Delivery, acknowledgement, plan revision, notification decision, and patient response |

Every intent retains a recipient-specific reference and observed lifecycle.
The Agent cannot declare that a review occurred, an executive agreed, a
category was assigned, a report was filed, an impact estimate was final, or a
patient was notified.

## 8. Operationalization and uncertainty

`unclear`, `suspicious`, and `senior_attention_required` are qualitative GCIO
assessments, not probabilities or institutional categories. A transition
requires delivered information or a reasoned reassessment. No date or known
outcome forces one.

The model separates account uncertainty, participant assessment, recipient
availability, lifecycle state, and structural uncertainty about office
aggregation. It contains no numerical urgency threshold or mechanism weight.
The conservative behavior sends a qualified account when material scope and an
authorized route are established; a sensitivity form may give a pending
verification request more weight before a fuller update. Both must obey the
minimum responses and finite reopening conditions above.

## 9. Worked cases and falsification

### Vague 9 July account — reconstructed, exposed outcome

The GCIO receives unexplained database activity, a claim that no records were
returned, and information that the queries were stopped, but not the complete
logs or credential-compromise history. The minimum response is clarification,
management review, or qualified escalation. The Agent may route uncertainty;
it may not infer the next day's correction.

**Controlled change.** Remove the affected-system and unexplained-source
content while preserving a routine operational anomaly. Clarification may
remain appropriate, but escalation to both executive and Sector Lead routes no
longer follows from the documented material scope.

### SingHealth management report — reconstructed, exposed outcome

After receiving a fuller account, the GCIO sends SingHealth executives what is
known and asks for advice on the MOH route. Recipient delivery and advice are
separate. One executive's earlier knowledge cannot be copied to another.

**Controlled change.** Replace an acknowledged notification with a failed
delivery. The Agent must retry, select another authorized recipient, or report
the failed route; it cannot proceed as if SingHealth management was informed.

### Patient-impact update — reconstructed, exposed outcome

The GCIO receives a revised impact finding from the investigation process. It
may route the correction and identify remaining uncertainty, but cannot choose
the patient audience or public-announcement time.

**Controlled change.** Replace the revision with an unchanged acknowledged
record. A duplicate update is suppressed; a later contradiction reopens the
choice.

The Definition fails if name erasure changes behavior, if an IHiS reporting
line supplies SingHealth knowledge automatically, if incomplete information
always permits silence, if failed and successful notifications have the same
later behavior, or if the GCIO can self-realize classification, reporting, or
notification outcomes.

## 10. Limitations and references

This event-bound model does not reproduce the whole GCIO office, infer a
personal risk preference, identify a numerical escalation threshold, or grant
the office the authority of IHiS, SingHealth, MOH, or CSA. It suppresses staff
differences that do not change the accepted routing and oversight choices.

The historical outcome and inquiry assessments informed construction, so the
cases provide explanation and falsification surfaces rather than independent
evaluation. The Definition should be revised if the dual reporting relation,
recipient discretion, or patient-impact bridge is withdrawn, or if a separate
office actor is shown to own a material choice.

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
