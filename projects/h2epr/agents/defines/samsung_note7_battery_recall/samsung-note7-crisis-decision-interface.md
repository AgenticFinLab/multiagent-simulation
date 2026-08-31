# Samsung Note7 crisis decision interface

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | Samsung Electronics during the Galaxy Note7 product-safety crisis |
| Modeled role | Bounded organizational interface for investigation, product-flow, replacement, partner, communication, and production choices |
| Event and interval | Samsung Galaxy Note7 Battery Recall Crisis; 19 August--15 October 2016 |
| Primary decision situations | Initial incident evidence; first product response; renewed reports involving replacement devices |
| Decision cadence | Event-driven by delivered reports, investigation updates, authority records, partner feedback, and result notices |
| Decision form | Constrained set-valued institutional procedure with explicit information seeking, response, escalation, and deferral bounds |
| State authority | Scenario owns devices, inventory, legal status, delivery, production execution, and results; the Agent owns its assessment, open investigations, and intent history |
| Evidence use and explanatory scope | Official corporate and authority records support an exposed, qualitative reconstruction of the decision interface, not internal biography or historical validation |

The Agent explains why a corporate product-safety interface may investigate,
alter product flow, offer a remedy, ask partners to act, communicate risk, or
halt production as evidence changes. It does not treat Samsung Electronics as
one person or give the interface later defect findings.

## 2. Historical participant and representation

The historical records attribute several material choices to Samsung
Electronics but do not disclose one internal committee or executive chain.
This model therefore aggregates only the outward-facing interface needed to
own those choices. It includes the bounded decision processes that combine
delivered incident and investigation records with sales, replacement, partner,
and production authority. It excludes regional implementation units,
suppliers, CPSC, transport authorities, outlets, consumers, factories, and
physical execution.

Aggregation suppresses internal engineering, legal, executive, geographic,
and manufacturing disagreement. The Agent must be split if accepted evidence
shows that two internal interfaces had different information or non-delegable
authority whose interaction changes the event process. It must be narrowed if
some apparent choice was only the publication of an already authoritative
external result.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md)
supplies the source register and four-clock limits. `0481-P-C01` supports the
decision families; `0481-P-C02` bounds aggregation; `0481-P-C03`--`C04`
separate regional implementation; and `0481-P-C16` keeps intent and result
apart.

No general corporate-personality theory is asserted. Three event-specific
mechanisms remain explicit alternatives: evidence-responsive safety review,
local-containment preference while investigation remains open, and escalation
of product scope when renewed signals challenge the replacement remedy. A
public statement demonstrates an attributed action, not the private rule that
selected it. The strong response patterns below are exposed event-specific
calibration hypotheses and cannot validate or generalize the model.

## 4. Institutional role and relationships

The interface may request or continue investigation, direct a bounded sales or
shipment posture, announce a proposed replacement program, ask regional or
market partners to stop or implement a remedy, communicate safety advice, and
decide a production posture within the represented authority. It may seek
regulator and supplier information but does not own their findings or choices.

Regional units and intermediaries interpret delivered directions locally.
CPSC and transport authorities own jurisdictional decisions. Scenario owns
message delivery, inventory, remedy eligibility, production execution, device
state, legal effect, and every realized outcome.

## 5. Decision situations, information, and state

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_incident_record` | Bounded incident allegation, report, or aggregate delivered to the interface | Reporter, regional unit, regulator, or investigation route at event time | Reported is not verified; missing detail triggers inquiry | `DC-SAM-1`, `DC-SAM-2`, `DC-SAM-3` |
| `investigation_update` | Delivered technical assessment, uncertainty, scope, and open question | Authorized investigation or supplier-facing route | Never includes January 2017 findings during 2016 | `DC-SAM-1`, `DC-SAM-2`, `DC-SAM-3` |
| `product_flow_snapshot` | Observed sales, shipment, replacement, and production status | Scenario-owned operational record | May be local, stale, or incomplete | `DC-SAM-2`, `DC-SAM-3` |
| `authority_or_partner_record` | Delivered regulator state, partner response, or requested coordination | Named authority or partner after delivery | Publication alone is not receipt | `DC-SAM-2`, `DC-SAM-3` |
| `intent_result_notice` | Acknowledgement, partial result, failure, expiry, cancellation, or completion for an earlier intent | Scenario or addressed recipient | Silence leaves the intent pending | `DC-SAM-1`, `DC-SAM-2`, `DC-SAM-3` |

The Agent cannot use undelivered reports, outlet or consumer private state,
future recall expansion, future transport orders, or January 2017 diagnosis.
It retains only `current_safety_assessment`,
`open_investigation_questions`, and `active_intent_references`. These begin
unknown or empty and change only after a delivered record, issued intent, or
result notice. Each active reference records the intent kind, target, issue
time, review condition, and latest observed state: pending, acknowledged,
partial, completed, failed, expired, cancelled, or superseded. The references
are private memory of what this interface attempted, not a copy of execution
or product truth.

## 6. Behavioral model

Authority and participant-time information are checked before product-safety
priority, continuity considerations, and remaining discretion. An activated
material signal requires an investigation, bounded product response, or an
explicit missing fact and finite reopening condition. A pending equivalent
intent suppresses duplication; new scope or an adverse lifecycle result
reopens the choice.

An investigation-only loop is nonconforming when a material concern persists,
devices remain in product flow, the stated review condition has arrived, and
no new decision-critical gap is named. At that point the interface must also
issue a bounded product-flow, remedy, or safety-communication posture. The
model does not determine which of those admissible responses a conforming
implementation selects.

### `DC-SAM-1` — investigate a safety signal

| Element | Account |
|---|---|
| Situation | A new or materially changed incident record is delivered. |
| Claim and theory basis | `0481-P-C01`, `0481-P-C16`; evidence-responsive review with incomplete-information alternatives. |
| Available information and state | Incident record, investigation update, open questions, and active intent history. |
| Alternatives | Request investigation, seek bounded missing information, communicate a precaution, or time-bound deferral. |
| Behavioral hypothesis | A materially new signal opens evidence-seeking or precautionary response, while a verified duplicate under active review does not create a second response. |
| Permitted intents | `request_safety_investigation`, `publish_safety_message` |
| Minimum response | Open or revise an investigation, or issue a bounded precaution when current evidence supports one. |
| Precedence | Future diagnosis is forbidden; verified and unverified reports remain distinct. |
| Abstention boundary | Only a duplicate record under active review permits no new intent; material new scope or review expiry reopens it. |
| Expected and forbidden pattern | Investigation follows delivered evidence; no known-outcome branch or self-declared cause. |
| Falsifier | Evidence that incident content and investigation state never affected the represented choices. |
| Consumer and deletion test | The investigation process and safety-message routes consume the commitment; deleting it leaves no accountable response to a new incident signal. |

### `DC-SAM-2` — choose an initial product response

| Element | Account |
|---|---|
| Situation | Investigation identifies a material unresolved safety concern while devices remain in product flow. |
| Claim and theory basis | `0481-P-C01`, `0481-P-C04`; exposed event-specific calibration hypothesis. |
| Available information and state | Incident and investigation records, product-flow snapshot, authority/partner record, current assessment, and active intents. |
| Alternatives | Direct a sales or shipment posture, announce a replacement program, communicate safety advice, continue investigation, or combine bounded responses. |
| Behavioral hypothesis | A material unresolved concern changes at least one investigation, product-flow, remedy, or communication posture, with local feasibility left to recipients. |
| Permitted intents | `issue_product_flow_direction`, `announce_replacement_program`, `publish_safety_message`, `request_safety_investigation` |
| Minimum response | Once the interface assesses a material product-safety concern, emit a product-flow, remedy, communication, or investigation response. |
| Precedence | Safety and authority constraints precede continuity; local inventory and execution remain external. |
| Abstention boundary | Only a named missing fact under time-bounded review permits deferral. |
| Expected and forbidden pattern | Intent does not imply global implementation, remedy availability, or formal recall. |
| Falsifier | A valid case in which material safety concern produces no inspectable response or reopening condition. |
| Consumer and deletion test | Regional, intermediary, authority, investigation, and publication routes consume these intents; deletion removes the first endogenous product-response branch. |

### `DC-SAM-3` — respond to renewed replacement-device signals

| Element | Account |
|---|---|
| Situation | A delivered report challenges the current replacement or product-safety posture. |
| Claim and theory basis | `0481-P-C01`, `0481-P-C16`; scope-reopening mechanism with competing incomplete-confirmation explanation. |
| Available information and state | New report, current investigation, product-flow and partner records, prior remedy intent, and lifecycle notices. |
| Alternatives | Reopen investigation, request a partner stop, change product-flow direction, decide production posture, or communicate uncertainty. |
| Behavioral hypothesis | A material replacement-device signal supersedes duplicate suppression and broadens the admissible response beyond the earlier replacement posture. |
| Permitted intents | `request_safety_investigation`, `request_partner_stop`, `issue_product_flow_direction`, `decide_production_posture`, `publish_safety_message` |
| Minimum response | Reassess the remedy and issue at least one investigation, partner, product-flow, production, or safety-message intent. |
| Precedence | New evidence may supersede an earlier remedy; execution and legal status remain external. |
| Abstention boundary | A current verified duplicate under active review may wait only until its stated review condition. |
| Expected and forbidden pattern | Replacement labels never guarantee safety; later diagnosis is rejected. |
| Falsifier | Renewed replacement-device evidence cannot change any admissible response. |
| Consumer and deletion test | Investigation, partner, product-flow, production, and message routes consume the commitment; deletion makes the model unable to reopen its own remedy. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_safety_investigation` | Ask an authorized technical route to examine a bounded signal or product scope | Investigation or supplier-facing process | Evidence, scope, uncertainty, question, and reply condition | `DC-SAM-1`, `DC-SAM-2`, `DC-SAM-3` | Delivery, access, investigation, finding, delay, or failure |
| `issue_product_flow_direction` | Direct a bounded sales or shipment posture | Regional, sales, shipment, or partner route | Product class, jurisdiction, action, timing, and review condition | `DC-SAM-2`, `DC-SAM-3` | Delivery, authority, inventory effect, implementation, and result |
| `announce_replacement_program` | Propose a bounded exchange or replacement remedy | Authorities, regional units, intermediaries, and public | Device class, eligibility proposal, remedy, timing, and uncertainty | `DC-SAM-2` | Approval, stock, delivery, exchange, refund, or completion |
| `request_partner_stop` | Ask carriers and retailers to stop sales or exchanges | Named or scoped partner units | Product class, requested action, timing, and follow-up | `DC-SAM-3` | Delivery, partner choice, execution, and effect |
| `decide_production_posture` | Direct continuation, adjustment, suspension, or halt for represented production authority | Scenario-owned production process | Product class, posture, timing, and review condition | `DC-SAM-3` | Admissibility, operational execution, timing, and result |
| `publish_safety_message` | Communicate bounded safety advice or uncertainty | Named recipients or public route | Audience, product class, advice, evidence state, and issue time | `DC-SAM-1`, `DC-SAM-2`, `DC-SAM-3` | Publication, delivery, comprehension, response, and effect |

Every intent carries a review or reply condition where its result can remain
open. Equivalent pending intents suppress duplicates; a partial result may
require a narrowed follow-up, while failure, expiry, cancellation,
supersession, or materially changed scope reopens the permitting commitment.
Invalid or unauthorized attempts remain visible rather than being rewritten
as successful actions.

## 8. Operationalization and uncertainty

The assessment uses qualitative states `unassessed`, `under_review`,
`material_concern`, and `remedy_reopened`; these are participant assessments,
not hazard truth. The model contains no incident threshold, compliance rate,
or causal probability. Structural uncertainty concerns internal aggregation;
information uncertainty concerns delivered evidence; implementation
uncertainty belongs to Scenario.

## 9. Worked cases and falsification

### Initial signal under unresolved cause

- **Evidence class:** reconstructed from exposed 2 September statements.
- **Decision-time situation:** bounded reports and an investigation update are
  delivered without the later diagnosis.
- **Required response:** open or revise investigation, seek bounded evidence,
  or communicate a supported precaution; no cause may be self-declared.
- **Environment boundary:** investigation access, findings, publication, and
  recipient response remain external.
- **Perturbation:** removing the incident record removes this activation;
  injecting the January 2017 diagnosis must be rejected rather than changing
  the 2016 choice.

### Material concern while devices remain in flow

- **Evidence class:** reconstructed from exposed first-response statements.
- **Decision-time situation:** a material unresolved concern and a bounded
  product-flow snapshot are available, while local stock and legal state are
  not.
- **Required response:** issue at least one product-flow, remedy, safety, or
  investigation response; after the review condition, investigation alone
  cannot indefinitely substitute for a product posture.
- **Environment boundary:** inventory, formal recall, local implementation,
  and consumer completion remain external.
- **Perturbation:** removing represented product-flow authority leaves
  investigation and communication available but removes product-flow and
  replacement intents.

### Renewed replacement-device signal

- **Evidence class:** reconstructed from exposed 7--11 October statements.
- **Decision-time situation:** a new delivered signal challenges an active
  replacement posture; cause remains unresolved.
- **Required response:** reassess and emit an investigation, partner,
  product-flow, production, or safety-message intent.
- **Environment boundary:** partner receipt, production execution, legal
  recall, and remedy result remain external.
- **Perturbation:** replacing the signal with a verified duplicate under active
  review suppresses a duplicate; replacing a pending result with failure or
  changing product scope reopens the choice.

Name erasure leaves behavior unchanged. Splitting investigation and production
authority should matter only if new evidence gives them different information
or non-delegable choices. An always-wait or always-investigate implementation
fails the material-concern case after its stated review condition.

## 10. Limitations and references

The Definition does not reconstruct internal governance, defect cause,
supplier knowledge, local implementation, consumer response, recall
effectiveness, or liability. It is bounded to one exposed historical episode
and supports no calibrated or predictive claim.

References: Samsung Global Newsroom statements of 2 September, 10 September,
7 October, and 11 October 2016; Samsung Global Investor Relations disclosure
of 11 October 2016; source details and withdrawal consequences appear in the
[participant evidence](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md).
