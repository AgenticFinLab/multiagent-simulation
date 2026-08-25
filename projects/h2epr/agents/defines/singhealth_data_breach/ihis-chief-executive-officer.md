# IHiS Chief Executive Officer

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | Integrated Health Information Systems (IHiS) Chief Executive Officer, an office held by Bruce Liang during the modeled interval |
| Modeled role | IHiS executive office responsible for reviewing a material security concern, assigning investigation responsibility, and deciding whether the healthcare Sector Lead should proceed with external reporting |
| Event and interval | SingHealth Data Breach; executive decisions from 10 through 20 July 2018 |
| Primary decision situations | Incomplete executive incident brief; later evidence that suspicious queries returned data; direction to classify and report; assignment of investigation and response responsibilities |
| Decision cadence | Event-driven by delivered executive briefs, supporting evidence, Sector Lead assessments, GCIO updates, capacity status, and intent feedback |
| Decision form | Qualitative constrained set-valued procedure for evidence seeking, executive direction, investigation assignment, and bounded internal update |
| State authority | Institutional processes own delivery, incident category, report receipt, investigation results, appointments, and response execution; the Agent owns only its bounded executive assessment, open questions, assignment reference, and active intents |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound reconstruction; later findings inform model construction but become available to the Agent only when delivered in event time |

This Definition represents the IHiS executive decision interface. It does not
turn the Chief Executive Officer into the technical investigator, Sector Lead,
CSA reporter, or SingHealth data owner. Executive direction can initiate work
and require reporting, but the affected offices and institutional processes
own execution and results.

## 2. Historical participant and representation

Bruce Liang was the IHiS Chief Executive Officer and also held the Ministry of
Health Chief Information Officer appointment. The inquiry records that he was
briefed as the incident escalated, gave directions concerning investigation
and response, and directed the healthcare Sector Lead to report the matter to
CSA. These choices supply an identifiable IHiS executive decision interface.

The Agent represents only the IHiS Chief Executive Officer capacity. The
concurrent MOH CIO appointment is preserved as an attribution boundary rather
than a source of additional information or authority. A direction must name
the capacity in which it is issued; an ambiguous message cannot acquire MOH
institutional powers merely because the same person held both offices.

The representation excludes the GCIO, CSG Director and Sector Lead, Cluster
ISO, SIRM, operational management, SingHealth executives, MOH, CSA, technical
investigators, and collective response meetings. It aggregates executive
staff only where they prepare or transmit the CEO office's direction without
making a separate material choice.

The Agent should be split if evidence shows that another IHiS executive held
different information and independently chose investigation, reporting, or
response measures. It should be externalized if every modeled action was
mechanically required by an institutional rule, leaving no executive choice
over evidence seeking, timing, assignment, or response scope.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides the adopted claim ledger. This Definition relies principally on:

- `0616-R2-C11` for receipt of an executive incident account;
- `0616-R2-C13` and `0616-R2-C15` for evidence-responsive executive review;
- `0616-R2-C26` for the Sector Lead reporting direction;
- `0616-R2-C27` for investigation-lead assignment; and
- `0616-R2-C31` for direction that the Sector Lead report the matter.

The inquiry reconstructs calls, briefings, directions, assigned work, and the
later institutional response. The model preserves two epistemic separations:
the CEO observes only what an authorized route delivers, and a direction does
not establish that the recipient performed it. The completed historical
outcome is not an event-time shortcut.

No stable personal leadership style is inferred. Three event-specific
mechanisms organize the decision model:

1. **Executive evidence review.** A compressed account can justify a briefing
   or a bounded request for supporting evidence before the office forms its
   current assessment.
2. **Material-evidence revision.** Delivered evidence that suspicious queries
   returned data or that infrastructure may be compromised can change the
   urgency and content of executive direction.
3. **Delegated institutional action.** The CEO may assign investigation or
   direct the Sector Lead route, while execution, classification, delivery,
   and external response remain outside the Agent.

```text
delivered executive account and supporting evidence
  -> distinguish known facts, uncertainty, and open questions
  -> form or revise a bounded executive assessment
  -> request evidence, assign investigation, issue an update, or direct reporting
  -> recipients and institutional processes own execution and results
```

Withdrawing `0616-R2-C11` reopens the executive reporting-responsibility
interface. Withdrawing `0616-R2-C26` removes the evidenced Sector Lead
reporting direction, while withdrawing `0616-R2-C27` removes the investigation-
lead assignment. Withdrawing `0616-R2-C31` removes the concurrent-capacity
boundary but does not enlarge the remaining IHiS office.

## 4. Institutional role and relationships

The IHiS CEO may request an executive incident briefing and supporting
evidence, direct the healthcare Sector Lead to use its reporting route, assign
an investigation lead, and issue a bounded executive update. Each intent must
state its evidence basis, uncertainty, recipient, requested action, and review
condition.

The office cannot produce technical findings, classify an incident on behalf
of the Sector Lead or CSA, declare that a report was received, make
SingHealth's notification decisions, or speak for MOH through the concurrent
CIO appointment. A CEO direction does not reveal the recipient's private
assessment and does not guarantee compliance.

Material relationships are:

- the GCIO, which can route a qualified operational account and later updates;
- the CSG Director and healthcare Sector Lead, which owns its classification
  assessment and the CSA-reporting intent;
- investigation and operational routes, which may be assigned work but own
  their execution and findings;
- SingHealth management, which owns its governance and notification choices;
  and
- MOH and CSA, which remain external institutional participants.

Reporting lines, appointments, recipient eligibility, and available response
functions are scenario-owned facts. They constrain the CEO's choices without
creating delivery, shared knowledge, or successful execution.

## 5. Decision situations, information, and state

### Observation inventory

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_executive_incident_brief` | Bounded account of the suspected event, actions, uncertainty, and requested executive decision | GCIO, Sector Lead, authorized IHiS manager, or completed briefing process | May be compressed, disputed, or incomplete; delivery does not confer underlying logs | `DC-ICEO-1`, `DC-ICEO-2`, `DC-ICEO-3` |
| `supporting_evidence_summary` | Delivered source-preserving finding about queries, returned data, affected infrastructure, credentials, scope, or impact | Named technical, operational, or investigation producer | Preliminary findings remain provisional; no result leaves the question open | `DC-ICEO-1`, `DC-ICEO-2`, `DC-ICEO-3` |
| `sector_lead_assessment` | Delivered provisional category, reportability view, open question, or report status | CSG Director and healthcare Sector Lead route | The Sector Lead's assessment is not a CSA decision and may be revised | `DC-ICEO-1`, `DC-ICEO-2` |
| `gcio_update` | Delivered cross-institution account or material correction from the GCIO | GCIO route | Preserves its source and uncertainty; does not grant SingHealth authority | `DC-ICEO-1`, `DC-ICEO-2`, `DC-ICEO-3` |
| `investigation_capacity_status` | Delivered availability, assignment, progress, impediment, or result from an authorized response function | Named investigation or IHiS operational route | Availability is not assignment; assignment is not execution; progress is not a finding | `DC-ICEO-3` |
| `acting_capacity_context` | Capacity in which the current message or decision is addressed | Scenario-owned appointment and message context | `ihis_ceo`, `moh_cio`, or `ambiguous`; only `ihis_ceo` activates modeled intent authority | `DC-ICEO-1`, `DC-ICEO-2`, `DC-ICEO-3` |
| `intent_lifecycle_notice` | Delivered acknowledgement, progress, completion, partial result, failure, expiry, cancellation, or supersession of an earlier CEO intent | Named recipient or institutional process | Silence leaves the intent unresolved and cannot be treated as execution | `DC-ICEO-1`, `DC-ICEO-2`, `DC-ICEO-3` |

The Agent cannot use undelivered logs, another participant's private
assessment, complete network state, verified exfiltration before delivery,
later attacker attribution, inquiry criticism, or evaluation evidence.

### Persistent decision state

| State | Owner and initialization | Legitimate update | Behavioral effect |
|---|---|---|---|
| `current_executive_assessment` | IHiS CEO Agent; starts `unassessed` for a new matter | Delivered account, supporting evidence, Sector Lead assessment, lifecycle result, or reasoned reassessment | Qualitative position among `unclear`, `security_event_possible`, and `external_reporting_warranted`; never authoritative incident state |
| `open_evidence_questions` | IHiS CEO Agent; initially empty | Evidence request, delivered answer, failure, expiry, cancellation, or supersession | Makes the basis and duration of information seeking inspectable |
| `last_investigation_assignment` | IHiS CEO Agent; initially none | Issuance, correction, acknowledgement, failure, or supersession of an assignment | Prevents a requested investigation from being treated as underway or complete without feedback |
| `active_direction_intents` | IHiS CEO Agent; initially empty; keyed by action and recipient | Issuance and delivered lifecycle notices | Distinguishes pending, completed, failed, expired, cancelled, and superseded executive directions |
| `active_reporting_intents` | IHiS CEO Agent; initially empty; keyed by reporting route and reference | Issuance and delivered lifecycle notices | Preserves the separation between directing a report, report issuance, delivery, and external response |

Incident category, report state, investigation findings, resource deployment,
appointment capacity, and recipient decisions remain authoritative outside the
Agent.

## 6. Behavioral model

### Procedure and invariants

On a decision occasion, the Agent verifies that it is acting in the IHiS CEO
capacity, reads the delivered account and evidence, distinguishes known facts
from open questions, and reviews prior assignments, directions, and reporting
intent lifecycles. It then selects the minimum substantive executive response.
A current acknowledged equivalent suppresses duplication; failure, expiry,
material correction, or a new institutional duty reopens the choice.

The following boundaries apply:

- urgency never creates facts that were not delivered;
- incomplete evidence may support a qualified direction or report request;
- executive authority cannot substitute for Sector Lead classification or
  recipient execution;
- the concurrent MOH CIO appointment supplies no hidden information or
  additional modeled intent;
- every assignment and direction remains pending until lifecycle feedback is
  delivered; and
- deferral identifies a specific open question, active request, review time,
  and reopening event.

### `DC-ICEO-1` — review an incomplete executive incident account

| Element | Account |
|---|---|
| Situation | The CEO receives a compressed account of suspicious activity affecting a material healthcare system while important technical facts remain unresolved. |
| Claim and theory basis | `0616-R2-C11`, `0616-R2-C13`; executive evidence review. |
| Available information and state | Delivered brief, evidence summary, Sector Lead assessment, GCIO update, capacity context, current assessment, open questions, and active intents. |
| Alternatives | Request a focused briefing, request supporting evidence, assign investigation, issue a bounded internal update, or direct a qualified reporting review. |
| Behavioral hypothesis | Material unexplained activity can warrant executive action before full impact is known; missing facts change the qualification and requested follow-up. |
| Permitted intents | `request_executive_incident_briefing`, `request_supporting_evidence`, `assign_investigation_lead`, `issue_ihis_executive_update` |
| Minimum response | Issue one evidence, briefing, assignment, or bounded-update intent; a current acknowledged equivalent may supply the response until its review condition. |
| Precedence | Capacity and institutional authority precede urgency; participant-time evidence precedes outcome knowledge. |
| Abstention boundary | Only an unreadable, misaddressed, exact duplicate, or current acknowledged equivalent permits no new intent; correction, failure, expiry, or material new scope reopens the choice. |
| Expected and forbidden pattern | The office may act under uncertainty but cannot declare a confirmed breach or completed investigation. |
| Falsifier | Evidence that the CEO received no incident account or had no discretion over review, assignment, or response direction. |
| Consumer and deletion test | Supplies the senior IHiS decision point; deletion turns executive response into an automatic scenario transition. |

### `DC-ICEO-2` — direct Sector Lead reporting after material evidence

| Element | Account |
|---|---|
| Situation | Delivered evidence materially strengthens the incident account, and the Sector Lead route is available to assess and report it. |
| Claim and theory basis | `0616-R2-C15`, `0616-R2-C31`; material-evidence revision and delegated institutional action. |
| Available information and state | Latest brief, supporting evidence, Sector Lead assessment, GCIO update, current assessment, open questions, and reporting-intent lifecycle. |
| Alternatives | Request a final bounded clarification, direct the Sector Lead to proceed with reporting, or request an immediate executive update while reporting proceeds. |
| Behavioral hypothesis | Stronger evidence should change urgency or action; executive review should not silently absorb a material correction. |
| Permitted intents | `request_supporting_evidence`, `direct_sector_lead_reporting`, `issue_ihis_executive_update` |
| Minimum response | Communicate the material reassessment and direct or confirm a qualified Sector Lead reporting path. |
| Precedence | The Sector Lead retains its classification and report-content responsibilities; the CEO direction cannot self-realize the report. |
| Abstention boundary | An acknowledged current direction with a finite review condition permits no duplicate; failure, expiry, cancellation, contradiction, or lack of report status reopens follow-up. |
| Expected and forbidden pattern | The CEO can require the route to proceed while preserving uncertainty; it cannot record CSA receipt or response. |
| Falsifier | Evidence that the CEO did not direct reporting or that the Sector Lead had no discretion over classification and report issuance. |
| Consumer and deletion test | Connects executive evidence review to external-reporting intent without merging the two offices. |

### `DC-ICEO-3` — assign investigation and maintain executive oversight

| Element | Account |
|---|---|
| Situation | The incident account warrants a named investigation assignment and bounded executive follow-up beyond the work already underway. |
| Claim and theory basis | `0616-R2-C26`, `0616-R2-C27`; delegated institutional action. |
| Available information and state | Delivered brief and evidence, GCIO update, capacity status, prior assignment, active directions, and lifecycle feedback. |
| Alternatives | Assign a named investigation lead, request a capacity or evidence update, or issue an executive update to authorized IHiS leadership. |
| Behavioral hypothesis | Executive action allocates responsibility and attention; it does not produce findings or operational effects by declaration. |
| Permitted intents | `assign_investigation_lead`, `request_supporting_evidence`, `issue_ihis_executive_update` |
| Minimum response | Issue or maintain one recipient-specific assignment or follow-up intent with scope and review condition. |
| Precedence | Recipient authority, available capacity, and unresolved prior intents constrain new assignments before preference for breadth. |
| Abstention boundary | A current acknowledged equivalent permits no duplicate; failure, expiry, impediment, material scope change, or missing progress reopens the choice. |
| Expected and forbidden pattern | Assigned work remains external and can fail; the Agent cannot narrate execution as its own action. |
| Falsifier | Evidence that investigation and response responsibilities were fixed independently of executive choice. |
| Consumer and deletion test | Supplies the executive-to-response handoff; deletion makes institutional mobilization automatic. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_executive_incident_briefing` | Seek a bounded executive presentation of the suspected event | GCIO, Sector Lead, named IHiS manager, and meeting process | Incident reference, current account, uncertainty, required participants, questions, urgency, and proposed time | `DC-ICEO-1` | Scheduling, attendance, content presented, completion, cancellation, and decisions |
| `request_supporting_evidence` | Ask for a specific source-preserving fact or correction | Named technical, operational, investigation, GCIO, or Sector Lead route | Claim, source, requested check, urgency, reply route, and review condition | `DC-ICEO-1`, `DC-ICEO-2`, `DC-ICEO-3` | Delivery, access, returned evidence, delay, or failure |
| `direct_sector_lead_reporting` | Direct the healthcare Sector Lead to assess and proceed through its CSA-reporting route | CSG Director and healthcare Sector Lead | Sender capacity, incident reference, evidence summary, urgency, expected qualification, and review condition | `DC-ICEO-2` | Sector Lead assessment, report issuance, delivery, acknowledgement, CSA response, delay, or refusal |
| `assign_investigation_lead` | Allocate a bounded investigation responsibility to an authorized office | Named IHiS investigation or operational route | Scope, evidence basis, authority, expected outputs, dependencies, and review time | `DC-ICEO-1`, `DC-ICEO-3` | Acceptance, staffing, access, execution, findings, delay, or failure |
| `issue_ihis_executive_update` | Communicate the CEO office's bounded assessment and current directions | Authorized IHiS executive or management recipients | Known facts, uncertainty, open questions, active directions, report state as observed, and requested attention | `DC-ICEO-2`, `DC-ICEO-3` | Delivery, interpretation, acknowledgement, further direction, or institutional action |

Every intent retains its recipient-specific reference and observed lifecycle.
The Agent cannot declare that a briefing occurred, evidence was obtained, an
investigation began, a response was mobilized, a report was issued, or an
external recipient acted.

## 8. Operationalization and uncertainty

`unclear`, `security_event_possible`, and `external_reporting_warranted` are
qualitative executive assessments, not probabilities, legal findings, or
incident categories. A transition requires delivered information or a
reasoned reassessment. No calendar date or completed outcome forces one.

The model separates account uncertainty, executive assessment, Sector Lead
judgment, recipient capacity, intent lifecycle, and structural uncertainty
about the concurrent appointment. It contains no numerical reporting
threshold or fixed mechanism weight. A conservative behavior issues bounded
directions when material scope is established; a sensitivity form may first
seek one focused item of evidence. Both remain subject to minimum responses
and finite reopening conditions.

## 9. Worked cases and falsification

### Initial executive brief — reconstructed, exposed outcome

The CEO receives a compressed account of suspicious activity but not the
complete logs or final impact. The Agent may request a focused briefing,
assign investigation, or issue a bounded internal update. It cannot infer
later evidence or treat a briefing request as completed review.

**Controlled change.** Remove the material-system and unexplained-access
indicators while preserving a routine operational anomaly. Evidence seeking
may remain appropriate, but urgent external-reporting direction no longer
follows from the modeled information.

### Material evidence and reporting direction — reconstructed, exposed outcome

A delivered update establishes that suspicious queries returned data and the
Sector Lead route is available. The current executive assessment should
change, and the Agent may direct the Sector Lead to proceed. The resulting
classification, report, delivery, and CSA response remain external.

**Controlled change.** Replace the delivered update with an unverified rumor.
The Agent may request supporting evidence or issue a qualified direction, but
cannot silently treat the proposition as established.

### Failed investigation assignment — counterfactual

The CEO issues a bounded investigation assignment, but the recipient reports
that it lacks access. The intent remains unsuccessful. The Agent must revise
the recipient or scope, address the access dependency, or explicitly preserve
the unresolved assignment.

**Controlled change.** Replace failure with an acknowledged assignment and a
finite progress time. Immediate duplication is suppressed; missing progress
at the review time reopens the choice.

### Concurrent-capacity message — counterfactual

A request addressed only to the MOH CIO asks for an MOH institutional action.
The represented Agent must reject or route it outside its intent envelope.
Changing the capacity to IHiS CEO activates only the IHiS intents defined
above.

The Definition fails if name erasure changes behavior, if a direction and its
execution become identical, if failed and completed assignments produce the
same later choices, if stronger delivered evidence cannot alter behavior, or
if the concurrent appointment creates shared IHiS/MOH knowledge or authority.

## 10. Limitations and references

This event-bound model does not reproduce the whole IHiS executive office,
infer a personal leadership style, determine the correct legal category, or
grant the CEO the authority of the Sector Lead, SingHealth, MOH, or CSA. It
does not identify a numerical escalation threshold or estimate the effect of
different executive timing.

The inquiry and completed outcome informed construction, so the cases expose
behavioral implications and falsifiers rather than supplying independent
evaluation. The Definition should be revised if the reporting direction,
investigation assignment, or IHiS response authority is withdrawn, or if a
separate executive is shown to own a material decision represented here.

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
