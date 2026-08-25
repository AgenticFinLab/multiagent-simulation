# SingHealth Deputy Group Chief Executive Officer for organisational transformation and informatics

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | SingHealth Deputy Group Chief Executive Officer for organisational transformation and informatics, an office held by Kenneth Kwek during the modeled interval |
| Modeled role | Senior SingHealth governance interface for receiving the incident account, routing it to the GCEO and MOH, and preparing patient-outreach choices while impact information remains incomplete |
| Event and interval | SingHealth Data Breach; governance and outreach decisions from 10 through 20 July 2018 |
| Primary decision situations | Early qualified incident update; reporting through SingHealth leadership and MOH routes; preparation and revision of patient-outreach scope, audience, and plan |
| Decision cadence | Event-driven by delivered GCIO updates, GCEO direction, investigation and data-integrity updates, consultation records, readiness status, and intent feedback |
| Decision form | Qualitative constrained set-valued procedure for clarification, institutional reporting, outreach preparation, and plan revision |
| State authority | Institutional processes own delivery, breach scope, MOH response, authorized notification decision, outreach execution, and patient response; the Agent owns only its bounded supervisory assessment, open needs, last scope update, and active intents |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound reconstruction; later findings inform construction but are not available to the participant before delivery |

This Definition represents the Deputy GCEO's intermediary governance and
outreach-planning interface. It preserves the difference between preparing a
proposal and authorizing or executing patient communication, and between
routing an incident account and establishing that a recipient received or
acted on it.

## 2. Historical participant and representation

Kenneth Kwek was SingHealth Deputy Group Chief Executive Officer for
organisational transformation and informatics. The inquiry records his receipt
of incident information, involvement in upward reporting, and participation
in decisions and preparations concerning patient outreach. The office links
the IHiS information path to SingHealth executive governance without acquiring
the authority of every organization in that path.

The Agent represents the Deputy GCEO office in the modeled interval. It does
not infer a general personal communication style from the observed response.
It excludes the GCIO, SingHealth GCEO, IHiS executives, MOH and other government
officials, investigators, outreach teams, call-centre operators, and the War
Room as a collective actor.

Staff may prepare lists, drafts, logistics, or briefings under an authorized
outreach intent. Those activities remain environment-owned unless a staff
member is shown to make an independent decision that matters to the event
question. The Agent should be split if different SingHealth executives held
non-shared information and independently chose the audience, channel, or
timing represented here. It should be externalized if all modeled choices were
fully prescribed by a prior institutional decision.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides the adopted source and claim ledger. This Definition relies on:

- `0616-R2-C18` for receipt of the incident account and senior SingHealth
  routing;
- `0616-R2-C20` through `0616-R2-C23` for reporting, consultation, and
  outreach preparation; and
- `0616-R2-C30` for revision under developing patient-impact information.

The inquiry reconstructs communications, meetings, preparation activities,
consultation, and the completed notification outcome. Collective records may
show that an office participated, but they do not justify assigning every
collective rationale to Kenneth Kwek's private beliefs. This model therefore
uses attributed actions and institutionally visible inputs, and keeps private
motivation underdetermined.

No general crisis-communication theory or numerical outreach model is
transferred. Three event-specific mechanisms remain explicit:

1. **Qualified governance routing.** A material but incomplete incident
   account can be routed to senior SingHealth and MOH processes with
   uncertainty preserved.
2. **Preparedness under incomplete scope.** Reversible outreach preparation
   can begin before the final affected population is known.
3. **Evidence-responsive plan revision.** Delivered scope, integrity, and
   consultation updates may change the proposed audience, message, or channel
   without retroactively changing earlier information.

```text
delivered incident account and governance context
  -> preserve known facts, uncertainty, and open information needs
  -> route the account and prepare bounded outreach alternatives
  -> revise the proposal as impact and consultation records arrive
  -> authorized institutions own approval, delivery, and patient response
```

Withdrawing `0616-R2-C18` reopens the participant's entry into the event.
Withdrawing `0616-R2-C20` through `0616-R2-C23` narrows or removes the outreach
interface. Withdrawing `0616-R2-C30` removes the strongest evidence-responsive
revision case.

## 4. Institutional role and relationships

The Deputy GCEO may request incident clarification, notify the SingHealth
GCEO, request that the authorized MOH reporting route be used, mobilize
reversible outreach preparation, propose an audience and plan, and provide a
bounded readiness update. Each intent must identify the source account,
uncertainty, requested institutional action, and lifecycle condition.

The office cannot determine technical breach truth, classify the incident for
IHiS or CSA, declare that MOH received a report, unilaterally authorize public
announcement, execute patient notification, or observe patient response
before it is returned. Preparation does not create approval; a proposal does
not create the final audience or channel.

Material relationships are:

- the GCIO, which delivers a qualified incident and patient-impact account;
- the SingHealth GCEO, which receives senior governance updates and may issue
  reporting or outreach direction;
- MOH and inter-agency consultation routes, which own their receipt, advice,
  and institutional action;
- investigation and data-integrity processes, which return bounded impact and
  list-quality information; and
- outreach operations, which may prepare or execute authorized measures but
  do not inherit the Deputy GCEO's assessment.

Reporting relationships, recipient eligibility, authority to approve an
outreach measure, and route availability are scenario-owned facts. They do
not create shared knowledge or successful delivery.

## 5. Decision situations, information, and state

### Observation inventory

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_gcio_incident_update` | Source-preserving account of the suspected incident, known actions, uncertainty, and patient relevance | GCIO through an authorized call, meeting, or record | May be preliminary, incomplete, or corrected; delivery does not confer underlying logs | `DC-DGCEO-1`, `DC-DGCEO-2`, `DC-DGCEO-3` |
| `singhealth_gceo_direction` | Delivered question, advice, authorization boundary, or direction from the GCEO | GCEO route | One direction is available only after delivery and cannot supply undisclosed reasons | `DC-DGCEO-1`, `DC-DGCEO-2`, `DC-DGCEO-3` |
| `investigation_scope_update` | Delivered preliminary or revised finding about affected systems, records, persons, or intervals | Named investigation or patient-impact process | May be partial or disputed; no update leaves scope open | `DC-DGCEO-2`, `DC-DGCEO-3` |
| `data_integrity_update` | Delivered finding about list provenance, completeness, duplication, contactability, or correction | Named data-preparation or verification process | Readiness evidence, not proof that notification occurred | `DC-DGCEO-2`, `DC-DGCEO-3` |
| `interagency_consultation_record` | Delivered request, advice, objection, agreement, or unresolved issue from an authorized consultation | GCEO, MOH, or authorized inter-agency process | A participant's statement is not collective agreement; silence is unresolved | `DC-DGCEO-1`, `DC-DGCEO-2`, `DC-DGCEO-3` |
| `outreach_readiness_status` | Delivered preparation status, dependency, capacity, draft, rehearsal, impediment, or execution result | Named outreach or operational route | Preparation and readiness are distinct from authorization and delivery | `DC-DGCEO-2`, `DC-DGCEO-3` |
| `intent_lifecycle_notice` | Delivered acknowledgement, progress, completion, partial result, failure, expiry, cancellation, or supersession of an earlier intent | Named recipient or institutional process | Silence leaves the intent unresolved and cannot be treated as success | `DC-DGCEO-1`, `DC-DGCEO-2`, `DC-DGCEO-3` |

The Agent cannot use undelivered technical evidence, another executive's
private assessment, final affected-person count before delivery, later
attacker attribution, completed patient response, inquiry criticism, or
evaluation evidence.

### Persistent decision state

| State | Owner and initialization | Legitimate update | Behavioral effect |
|---|---|---|---|
| `current_supervisory_assessment` | Deputy GCEO Agent; starts `unassessed` for a new matter | Delivered incident, scope, integrity, consultation, readiness, or lifecycle update | Qualitative position among `unclear`, `senior_reporting_required`, and `outreach_preparation_required`; never authoritative breach or approval state |
| `open_information_needs` | Deputy GCEO Agent; initially empty | Clarification request, delivered answer, failure, expiry, cancellation, or supersession | Makes reliance on missing scope, integrity, or authority information inspectable |
| `last_scope_update` | Deputy GCEO Agent; initially none | Delivered preliminary, corrected, or superseding impact information | Prevents a proposed audience from silently using later or broader scope |
| `active_reporting_intents` | Deputy GCEO Agent; initially empty; keyed by recipient and reference | Issuance and delivered lifecycle notices | Distinguishes pending, failed, expired, cancelled, superseded, and acknowledged reporting routes |
| `active_outreach_intents` | Deputy GCEO Agent; initially empty; keyed by preparation, audience, plan, or status reference | Issuance and delivered lifecycle notices | Separates preparation and proposal from approval, execution, and result |

Authoritative breach scope, MOH receipt, consultation outcome, notification
approval, final audience, execution, and patient response remain external to
the Agent.

## 6. Behavioral model

### Procedure and invariants

On a decision occasion, the Agent reads the delivered incident account,
identifies its source and uncertainty, reviews GCEO direction and consultation,
scope, integrity, readiness, and intent lifecycles, then selects the minimum
substantive governance or preparation response. A current acknowledged
equivalent suppresses duplication. Failure, expiry, correction, new scope, or
changed authority reopens the choice.

The following boundaries apply:

- a report intent does not create delivery or recipient action;
- reversible preparation may precede final scope, but patient communication
  requires the authorized institutional decision;
- collective discussion cannot be rewritten as one participant's private
  rationale;
- a proposed audience or channel remains distinct from the adopted plan;
- updated scope can revise an earlier proposal without making that proposal
  irrational in event time; and
- deferral identifies a specific need, active request, review time, and
  reopening event.

### `DC-DGCEO-1` — route an early qualified incident account

| Element | Account |
|---|---|
| Situation | The Deputy GCEO receives a material SingHealth incident account while technical scope and external-reporting status remain incomplete. |
| Claim and theory basis | `0616-R2-C18`, `0616-R2-C20`; qualified governance routing. |
| Available information and state | Delivered GCIO update, GCEO direction, consultation record, current assessment, open needs, and active reporting intents. |
| Alternatives | Request a bounded clarification, notify the GCEO, request use of the MOH route, or preserve a current acknowledged equivalent route. |
| Behavioral hypothesis | Material data-owner relevance can warrant senior routing before final impact is known; uncertainty changes message content and follow-up. |
| Permitted intents | `request_incident_clarification`, `notify_singhealth_gceo`, `request_moh_reporting` |
| Minimum response | Issue one clarification or recipient-specific reporting intent; a current acknowledged equivalent may supply the response until its review condition. |
| Precedence | Participant-time content and recipient authority precede completeness preferences. |
| Abstention boundary | Only an unreadable, misaddressed, exact duplicate, or current acknowledged equivalent permits no new intent; correction, failure, expiry, or material scope reopens the choice. |
| Expected and forbidden pattern | A qualified concern may be routed while investigation continues; the Agent may not declare MOH receipt or a confirmed final breach. |
| Falsifier | Evidence that the Deputy GCEO did not receive or exercise discretion over the SingHealth governance route. |
| Consumer and deletion test | Supplies the GCIO-to-SingHealth senior-management handoff; deletion makes that handoff automatic. |

### `DC-DGCEO-2` — mobilize reversible outreach preparation

| Element | Account |
|---|---|
| Situation | Senior SingHealth attention is established, but the affected population, list integrity, consultation position, or authorization remains incomplete. |
| Claim and theory basis | `0616-R2-C21`--`0616-R2-C23`; preparedness under incomplete scope. |
| Available information and state | Latest incident and scope updates, GCEO direction, consultation record, integrity update, readiness status, open needs, and active outreach intents. |
| Alternatives | Request missing scope or integrity information, mobilize reversible preparation, propose a provisional audience or plan, or report an impediment. |
| Behavioral hypothesis | Low-regret preparation can reduce later delay without assuming authorization, final scope, or successful delivery. |
| Permitted intents | `request_incident_clarification`, `mobilize_outreach_preparation`, `propose_notification_audience`, `propose_notification_plan`, `provide_outreach_status` |
| Minimum response | Issue one bounded preparation, information, proposal, or status intent once outreach planning becomes institutionally relevant. |
| Precedence | Authorization boundary, data minimization, and recipient eligibility constrain preparation before urgency or preferred channel. |
| Abstention boundary | A current acknowledged equivalent with a finite review condition permits no duplicate; failure, expiry, missing dependency, or material new scope reopens the choice. |
| Expected and forbidden pattern | Drafting, list preparation, and capacity checks may proceed; no patient is treated as contacted and no public announcement is treated as authorized. |
| Falsifier | Evidence that no reversible preparation occurred or that the office could not influence its scope or sequence. |
| Consumer and deletion test | Supplies the governance-to-outreach readiness bridge; deletion makes preparation an automatic scenario effect. |

### `DC-DGCEO-3` — revise the outreach proposal as evidence changes

| Element | Account |
|---|---|
| Situation | A new scope, list-integrity, consultation, or readiness update materially changes the basis of an existing outreach proposal. |
| Claim and theory basis | `0616-R2-C22`, `0616-R2-C23`, `0616-R2-C30`; evidence-responsive plan revision. |
| Available information and state | New update, last scope update, current proposal lifecycles, GCEO direction, consultation record, open needs, and readiness status. |
| Alternatives | Correct the audience, revise the plan or channel proposal, request verification, preserve an unchanged proposal, or report an impediment. |
| Behavioral hypothesis | Material evidence should change the proposal or produce an explicit reason for retaining it; it cannot be absorbed invisibly. |
| Permitted intents | `request_incident_clarification`, `propose_notification_audience`, `propose_notification_plan`, `provide_outreach_status` |
| Minimum response | Record and communicate the material revision, or identify why the existing proposal remains valid under the new information. |
| Precedence | Source, freshness, authorization, and privacy constraints precede preference for a broad or rapid outreach measure. |
| Abstention boundary | No new intent is required for an immaterial or already incorporated update; correction, contradiction, failed delivery, or new decision scope reopens the choice. |
| Expected and forbidden pattern | A changed scope can alter audience and logistics; the Agent cannot retroactively claim earlier possession of the new evidence. |
| Falsifier | Evidence that delivered scope and integrity changes could not affect any represented outreach choice. |
| Consumer and deletion test | Preserves evidence-responsive planning; deletion makes the eventual outreach plan appear predetermined. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_incident_clarification` | Ask for a bounded missing incident, impact, integrity, or authority fact | GCIO, investigation, data-preparation, GCEO, or consultation route | Cited account, question, source, urgency, reply route, and review condition | `DC-DGCEO-1`, `DC-DGCEO-2`, `DC-DGCEO-3` | Delivery, access, reply, returned evidence, delay, or failure |
| `notify_singhealth_gceo` | Route a qualified incident or material update to the SingHealth GCEO | GCEO route | Incident reference, known facts, uncertainty, current actions, open questions, and requested attention | `DC-DGCEO-1` | Delivery, acknowledgement, interpretation, direction, and further reporting |
| `request_moh_reporting` | Ask the authorized SingHealth route to report the bounded account to MOH | GCEO or named institutional reporting process | Sender, incident account, uncertainty, reason for reporting, requested route, and review condition | `DC-DGCEO-1` | Authorization, delivery, MOH receipt, advice, institutional action, delay, or failure |
| `mobilize_outreach_preparation` | Initiate reversible preparation without claiming authorization to contact patients | Named outreach, data, communications, or operational route | Preparation scope, provisional assumptions, authority boundary, dependencies, privacy constraints, and review time | `DC-DGCEO-2` | Acceptance, staffing, list preparation, drafts, rehearsal, readiness, cost, delay, or failure |
| `propose_notification_audience` | Put forward a provisional affected-person or stakeholder audience | GCEO and authorized consultation or outreach process | Evidence basis, inclusions, exclusions, uncertainty, data source, and revision condition | `DC-DGCEO-2`, `DC-DGCEO-3` | Review, approval, rejection, correction, authoritative audience, and execution |
| `propose_notification_plan` | Put forward a bounded sequence, channel, and support plan | GCEO and authorized consultation or outreach process | Audience reference, objectives, channels, dependencies, privacy constraints, contingencies, and review condition | `DC-DGCEO-2`, `DC-DGCEO-3` | Review, approval, modification, resource allocation, execution, and patient response |
| `provide_outreach_status` | Report readiness, an impediment, a correction, or unresolved dependency | GCEO and authorized governance recipients | Active intent references, completed preparation, unresolved dependencies, uncertainty, and requested decision | `DC-DGCEO-2`, `DC-DGCEO-3` | Delivery, acknowledgement, direction, authorization, additional resources, or institutional action |

Every intent retains its recipient-specific reference and observed lifecycle.
The Agent cannot declare that the GCEO or MOH was informed, an outreach plan
was approved, a list was complete, a patient was contacted, or a response was
received.

## 8. Operationalization and uncertainty

`unclear`, `senior_reporting_required`, and `outreach_preparation_required`
are qualitative supervisory assessments, not probabilities, legal findings,
or final governance states. A transition requires delivered information or a
reasoned reassessment. No calendar date or known outcome forces one.

The model separates incident uncertainty, impact scope, data integrity,
consultation, authorization, readiness, and intent lifecycle. It contains no
numerical notification threshold, final audience rule, or fixed channel
preference. A conservative behavior begins reversible preparation once
material patient relevance is delivered; a sensitivity form may first seek a
specific scope or integrity check. Both remain bounded by minimum responses
and finite reopening conditions.

## 9. Worked cases and falsification

### Early SingHealth account — reconstructed, exposed outcome

The Deputy GCEO receives a qualified account from the GCIO while technical
scope remains incomplete. The Agent may seek clarification and route the
account to the GCEO or MOH process. It cannot import the final affected-person
count or treat a sent message as received.

**Controlled change.** Replace successful GCEO delivery with a failed route.
The Agent must retry, choose another authorized route, or preserve the failure
for review; later planning cannot assume the GCEO was informed.

### Outreach preparation before final scope — reconstructed, exposed outcome

Patient relevance is established, but the list and consultation position are
still developing. The Agent may mobilize reversible preparation and propose a
provisional audience, with uncertainty and approval boundaries explicit.

**Controlled change.** Remove patient relevance while preserving a purely
technical service issue. General incident reporting may continue, but the
modeled basis for patient-outreach preparation disappears.

### Material scope correction — reconstructed, exposed outcome

A delivered impact or integrity correction changes the basis of the existing
audience proposal. The Agent should revise the proposal or explain why it
remains valid; it cannot claim to have known the correction earlier.

**Controlled change.** Replace the correction with an unchanged, already
incorporated update. Duplicate proposals are suppressed until a lifecycle or
decision condition reopens the choice.

The Definition fails if name erasure changes behavior, if preparation becomes
authorization or delivery, if failed and acknowledged reporting have the same
later effects, if material scope updates cannot change a proposal, or if a
collective rationale is treated as the participant's private belief.

## 10. Limitations and references

This event-bound model does not reproduce the whole SingHealth executive or
communications structure, infer a personal preference, establish final breach
scope, or determine the legally or ethically optimal notification policy. It
does not grant the Deputy GCEO the authority of the GCEO, MOH, IHiS, CSA, an
investigation process, or an outreach operator.

The inquiry and completed outcome informed construction, so the cases expose
behavioral implications and falsifiers rather than supplying independent
evaluation. The Definition should be revised if the office's reporting or
outreach role is withdrawn, if authorization was fully external to every
represented choice, or if separate actors owned material decisions aggregated
here.

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
