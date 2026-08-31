# CAAC Note7 warning decision interface

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | Civil Aviation Administration of China during the Note7 transport-safety episode |
| Modeled role | Bounded civil-aviation safety interface that may seek information and issue or qualify a jurisdictional warning |
| Event and interval | Samsung Galaxy Note7 Battery Recall Crisis; 2 September--15 October 2016 |
| Primary decision situations | Available device-safety predicates before warning; materially changed recall or transport information after warning |
| Decision cadence | Event-driven by delivered safety, recall, dangerous-goods, and operator records |
| Decision form | Authority-constrained qualitative procedure with information seeking, warning, qualification, and bounded deferral |
| State authority | Scenario owns publication, delivery, legal or institutional effect, operator action, enforcement, and results; the Agent owns assessment and intent history |
| Evidence use and explanatory scope | One official warning supports an exposed event-bound issuance interface with explicit aggregation uncertainty |

The model preserves the autonomous choice to issue a warning without assigning
the downstream warning lifecycle to the participant.

## 2. Historical participant and representation

The official record names CAAC as issuer but does not identify an internal
person or committee. The Agent therefore represents only the narrow interface
that evaluates delivered aviation-safety predicates and selects a warning
intent within CAAC authority. It excludes airlines, airports, cargo operators,
Samsung, passengers, publication, routing, enforcement, and results.

The representation must narrow or split if an internal carrier with distinct
information or veto power is evidenced. It should become an institutional
process only if issuance is shown to be mechanically compelled and no
discretionary information, timing, scope, or qualification choice remains.

## 3. Evidence and theoretical foundation

`0481-P-C09` establishes issuance, operator duties, and stricter-measure scope;
`0481-P-C10` records the unresolved internal boundary; `0481-P-C13` separates
operator choices; and `0481-P-C16` separates issuance from lifecycle and
result.

The event-specific mechanism is precautionary aviation-safety authority under
incomplete device and operator information. Competing explanations are direct
application of dangerous-goods rules, international regulatory signaling, and
new incident evidence. The historical warning is an exposed calibration case,
not proof of a reusable regulator policy.

## 4. Institutional role and relationships

The interface may request bounded safety or operator information, issue a
warning, and qualify its scope or review condition. Samsung and consumer-safety
authorities own their statements. Operators own local measures. Scenario owns
publication, routing, receipt, institutional effect, enforcement, physical
carriage, and result.

## 5. Decision situations, information, and state

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_device_safety_record` | Bounded incident, defect allegation, or product-safety statement | Samsung, authority, or authorized safety route after delivery | Reported is not independently verified cause | `DC-CAAC-1`, `DC-CAAC-2` |
| `delivered_recall_record` | Jurisdictional or corporate recall and product-scope record | Named authority or firm after delivery | Scope and authority remain explicit | `DC-CAAC-1`, `DC-CAAC-2` |
| `dangerous_goods_context` | Applicable dangerous-goods rule or technical instruction available to the interface | Institutional legal or technical route | Does not by itself prove a unique action | `DC-CAAC-1`, `DC-CAAC-2` |
| `operator_risk_record` | Delivered operator assessment, question, or implementation feedback | Named airline, airport, or cargo route | Local and potentially incomplete | `DC-CAAC-1`, `DC-CAAC-2` |
| `intent_result_notice` | Lifecycle notice for an earlier information or warning intent | Scenario or addressed route | Missing notice leaves the item unresolved | `DC-CAAC-1`, `DC-CAAC-2` |

The Agent cannot use undelivered operator information, other authorities'
private reasoning, the later U.S. order before delivery, or January 2017
findings. It retains `current_transport_assessment`,
`open_information_requests`, and `active_warning_references`. They begin
`insufficient_record` or empty and update only after lawful delivery, intent
issuance, or a delivered result. Each reference records kind, target, issue
time, review condition, and the latest pending, acknowledged, partial,
completed, failed, expired, cancelled, or superseded state; it does not copy
warning publication, effect, or compliance truth.

## 6. Behavioral model

The interface checks jurisdiction and dangerous-goods context, then delivered
safety evidence, product scope, operator information, and active intents. A
material aviation concern requires an information request, warning-family
intent, or a named blocker with a finite review condition.

### `DC-CAAC-1` — assess whether to issue a transport warning

| Element | Account |
|---|---|
| Situation | Delivered device-safety and recall predicates create a possible aviation risk before an active warning exists. |
| Claim and theory basis | `0481-P-C09`--`C10`; precautionary authority with direct-rule and information-gap alternatives. |
| Available information and state | Safety and recall records, dangerous-goods context, operator record, assessment, and open requests. |
| Alternatives | Request risk information, issue a warning, issue a qualified warning, or time-bound deferral. |
| Behavioral hypothesis | A material aviation concern makes precautionary warning or targeted inquiry admissible, while jurisdiction and evidence scope constrain content. |
| Permitted intents | `request_transport_risk_information`, `issue_transport_warning`, `qualify_transport_warning` |
| Minimum response | For a material in-scope concern, issue a warning-family or targeted information intent. |
| Precedence | Jurisdiction and safety constraints precede convenience; uncertainty remains in content. |
| Abstention boundary | Only a duplicate record or a named missing predicate under finite review permits waiting. |
| Expected and forbidden pattern | Issuance does not imply publication, operator receipt, enforcement, or result. |
| Falsifier | Scope, evidence, and dangerous-goods context cannot alter the warning decision. |
| Consumer and deletion test | Information and institutional warning routes consume the commitment; deletion removes the authority-specific issuance choice. |

### `DC-CAAC-2` — reconsider warning scope

| Element | Account |
|---|---|
| Situation | New product, recall, or operator information materially changes an active warning's basis or scope. |
| Claim and theory basis | `0481-P-C09`, `0481-P-C13`, `0481-P-C16`; evidence-responsive scope review. |
| Available information and state | New delivered record, current warning reference, operator feedback, and result notices. |
| Alternatives | Qualify warning scope, request information, issue a superseding warning, or retain current scope with review condition. |
| Behavioral hypothesis | Materially changed product or operator information reopens scope, while an immaterial duplicate preserves the active warning reference. |
| Permitted intents | `qualify_transport_warning`, `request_transport_risk_information`, `issue_transport_warning` |
| Minimum response | Record a scope review and issue a changed warning or information request when new information is material. |
| Precedence | Product identity and jurisdiction remain explicit; no global rule is inferred. |
| Abstention boundary | An immaterial duplicate under current review may wait until the stated review event. |
| Expected and forbidden pattern | Operator discretion and lifecycle remain outside the Agent. |
| Falsifier | Material new product scope never changes warning content or inquiry. |
| Consumer and deletion test | Warning-supersession and information routes consume the commitment; deletion makes an issued warning insensitive to new scope. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `request_transport_risk_information` | Seek bounded safety, product, or operator evidence | Samsung, authority, operator, or technical route | Question, product scope, jurisdiction, due condition, and uncertainty | `DC-CAAC-1`, `DC-CAAC-2` | Delivery, access, response, delay, or failure |
| `issue_transport_warning` | Issue a jurisdictional aviation-safety warning intent | Institutional publication and operator routes | Product class, scope, restrictions, duties, issue time, and review condition | `DC-CAAC-1`, `DC-CAAC-2` | Publication, delivery, effect, compliance, enforcement, and result |
| `qualify_transport_warning` | Narrow, clarify, or supersede warning content | Institutional publication and operator routes | Prior warning, changed scope, reason, timing, and review condition | `DC-CAAC-1`, `DC-CAAC-2` | Supersession, delivery, operator interpretation, enforcement, and result |

All intents carry a due or review condition. Equivalent pending intents
suppress duplicates; partial results permit bounded follow-up, and failure,
expiry, cancellation, supersession, or material new scope reopens review. A
request-only loop after all named decision predicates are present is
nonconforming.

## 8. Operationalization and uncertainty

Assessment categories are `insufficient_record`, `risk_review`,
`warning_warranted`, and `scope_review`. They are qualitative and contain no
probability or incident threshold. The unresolved internal carrier is a
structural uncertainty, not a hidden policy parameter.

## 9. Worked cases and falsification

- **Pre-warning review, reconstructed and exposed:** a delivered recall and
  dangerous-goods predicate require inquiry or warning; removing jurisdiction
  removes the warning intent envelope.
- **New scope after issuance, illustrative:** a material product-class change
  reopens scope review. A pending publication result remains external and
  cannot be treated as operator receipt.

The model fails if a future U.S. order drives the earlier CAAC choice, if
issuing a warning creates its own compliance, or if an always-wait response is
permitted after a material in-scope concern.

## 10. Limitations and references

The Definition does not reconstruct CAAC governance, quantify aviation risk,
model enforcement, or generalize across jurisdictions. It preserves one
exposed issuance choice and its uncertainty.

Reference: Civil Aviation Administration of China, “Safety warning on air
transport of Samsung Note7 phones,” 14 September 2016. Full source details
appear in the [participant evidence](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md).
