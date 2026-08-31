# U.S. CPSC Note7 recall decision interface

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | U.S. Consumer Product Safety Commission in the Note7 recall episode |
| Modeled role | Bounded authority interface for warning, remedy review, formal recall, and recall expansion choices |
| Event and interval | Samsung Galaxy Note7 Battery Recall Crisis; 2 September--15 October 2016 |
| Primary decision situations | Pre-recall warning and remedy review; first formal recall; renewed reports and expansion |
| Decision cadence | Event-driven by delivered firm reports, incident summaries, remedy proposals, investigation updates, and lifecycle results |
| Decision form | Authority-constrained qualitative procedure with information seeking, warning, recall, expansion, and bounded deferral |
| State authority | Scenario owns legal recall state, publication, delivery, remedy execution, and results; the Agent owns review assessment and intent history |
| Evidence use and explanatory scope | Official CPSC records support an exposed event-bound authority model, not a generic regulator personality or effectiveness claim |

The Agent explains the separate choices visible in the 9 September warning,
15 September formal recall, and 13 October expansion while preserving firm
action, public notice, consumer receipt, and remedy results under their own
owners.

## 2. Historical participant and representation

The model represents the CPSC interface that evaluates the bounded safety and
remedy record and issues a public warning or recall action. It does not
represent the entire Commission as one mind, infer individual commissioner
psychology, or absorb Samsung's product decisions. Staff investigation and
institutional procedure are aggregated only insofar as they supply the
evidenced authority choice.

The interface should split if evidence establishes materially different
warning and recall decision bodies with different information or veto power.
It should return procedural steps to Scenario if they are shown to be
non-discretionary after another authority decision.

## 3. Evidence and theoretical foundation

`0481-P-C05` and `0481-P-C06` establish the warning, review, recall, and
expansion distinctions; `0481-P-C07`--`C08` bound intermediary and consumer
responses; `0481-P-C16` separates intent from legal and practical result. The
official pages are authority records, not internal deliberation transcripts.

The event-specific mechanism is staged precautionary authority under changing
evidence and remedy scope. Competing explanations include incomplete incident
information, remedy-feasibility review, cooperative firm action, and
institutional processing time. Strong historical response patterns are
exposed calibration hypotheses rather than regulator laws.

## 4. Institutional role and relationships

The interface may request incident or remedy information, issue a bounded
consumer warning, propose or issue a formal recall action within its authority,
and expand that action when new evidence changes product scope. Samsung owns
its submissions and corporate intents; intermediaries and consumers own their
responses. Scenario owns publication, legal status, notice delivery, remedy
availability, exchange or refund execution, and effectiveness.

## 5. Decision situations, information, and state

| Observation | Meaning | Source, channel, and availability | Domain, freshness, and missing behavior | Behavioral consumers |
|---|---|---|---|---|
| `delivered_firm_safety_report` | Firm-supplied defect, incident, investigation, and product-scope account | Samsung or authorized reporting route after delivery | Attributed and potentially incomplete | `DC-CPSC-1`, `DC-CPSC-2`, `DC-CPSC-3` |
| `incident_summary` | Delivered administrative incident and injury information | CPSC intake or bounded case aggregation | Categories may change and are not monotonic parameters | `DC-CPSC-1`, `DC-CPSC-2`, `DC-CPSC-3` |
| `remedy_proposal` | Delivered replacement, refund, exchange, notice, and implementation proposal | Samsung and compliance route | Proposal is not approval, availability, or completion | `DC-CPSC-1`, `DC-CPSC-2`, `DC-CPSC-3` |
| `replacement_device_signal` | Delivered report or summary concerning replacement devices | Intake, firm, or investigation route | Reported is not verified cause | `DC-CPSC-3` |
| `intent_result_notice` | Lifecycle notice for a request, warning, or recall intent | Scenario or named counterpart | Silence keeps the item unresolved | `DC-CPSC-1`, `DC-CPSC-2`, `DC-CPSC-3` |

Forbidden information includes undelivered firm records, consumer private
state, future expansion before its evidence, transport outcomes, and January
2017 diagnosis. Persistent state is limited to
`current_authority_assessment`, `open_information_requests`, and
`active_action_references`. They begin `review_open` or empty and update only
after lawful observations, an issued intent, or a delivered result. Each
reference records kind, target, issue time, review condition, and the latest
observed pending, acknowledged, partial, completed, failed, expired, cancelled,
or superseded state; it is not a copy of recall or remedy truth.

## 6. Behavioral model

The interface first checks jurisdiction and available evidence, then the
urgency of consumer communication, remedy completeness, product scope, and
active commitments. A material concern requires a warning, information
request, recall-family intent, or time-bounded recorded blocker. Pending
equivalent actions suppress duplication; adverse results or new device scope
reopen review.

### `DC-CPSC-1` — warn while recall and remedy remain under review

| Element | Account |
|---|---|
| Situation | Delivered safety information supports a material concern while formal recall scope or remedy remains unresolved. |
| Claim and theory basis | `0481-P-C05`--`C06`; staged precautionary authority. |
| Available information and state | Firm report, incident summary, remedy proposal, assessment, open requests, and action history. |
| Alternatives | Warn consumers, request incident information, request remedy information, or time-bound review. |
| Behavioral hypothesis | A material concern can justify precautionary communication before remedy and formal-action predicates are complete. |
| Permitted intents | `issue_consumer_warning`, `request_incident_information`, `request_remedy_information` |
| Minimum response | Issue a warning or a targeted information request with a review condition for a material unresolved concern. |
| Precedence | Jurisdiction and public-safety duty precede convenience; uncertainty must remain explicit. |
| Abstention boundary | Only a duplicate current request or non-material record permits no new substantive intent. |
| Expected and forbidden pattern | Warning does not create recall, delivery, or compliance. |
| Falsifier | Warning and information sufficiency never alter later authority action. |
| Consumer and deletion test | Public-warning and information routes consume the commitment; deletion collapses warning and pending formal review into one undated action. |

### `DC-CPSC-2` — decide a formal recall action

| Element | Account |
|---|---|
| Situation | Product scope, hazard record, and proposed remedy are sufficiently bounded for formal action review. |
| Claim and theory basis | `0481-P-C05`--`C06`; exposed event-specific calibration hypothesis. |
| Available information and state | Firm and incident records, remedy proposal, prior warning and requests, and lifecycle notices. |
| Alternatives | Issue a recall action, request further remedy or incident information, or record a bounded deferral. |
| Behavioral hypothesis | Product scope, hazard record, and remedy feasibility jointly constrain whether formal action can issue or a specific evidence gap must be closed. |
| Permitted intents | `issue_recall_action`, `request_incident_information`, `request_remedy_information` |
| Minimum response | Issue a recall-family or targeted information intent once the formal review situation is active. |
| Precedence | Legal scope and remedy review constrain action; no intent can assert uptake or effectiveness. |
| Abstention boundary | Only a named missing fact under a finite review period permits deferral. |
| Expected and forbidden pattern | Corporate replacement and formal recall remain different states. |
| Falsifier | Formal authority adds no process distinction beyond Samsung's announcement. |
| Consumer and deletion test | The recall process and information routes consume the commitment; deleting it removes the jurisdictional transition between warning and formal action. |

### `DC-CPSC-3` — reassess and expand product scope

| Element | Account |
|---|---|
| Situation | New replacement-device signals challenge the current recall or remedy scope. |
| Claim and theory basis | `0481-P-C05`--`C06`, `0481-P-C16`; scope-reopening mechanism. |
| Available information and state | Replacement signal, current recall and remedy observations, incident summary, open requests, and action results. |
| Alternatives | Expand recall action, request targeted evidence, revise remedy review, or time-bound deferral. |
| Behavioral hypothesis | A material signal concerning replacement devices reopens product and remedy scope even while the prior action remains active. |
| Permitted intents | `expand_recall_action`, `request_incident_information`, `request_remedy_information` |
| Minimum response | Reassess current scope and issue an expansion or evidence-request intent. |
| Precedence | New scope cannot be ignored because an earlier remedy is active; cause remains unproved. |
| Abstention boundary | Only a duplicate signal under active review permits waiting until its stated review event. |
| Expected and forbidden pattern | Replacement status never suppresses the delivered new signal or guarantees safety. |
| Falsifier | Replacement-device evidence cannot change recall scope or information seeking. |
| Consumer and deletion test | The expanded-recall and targeted-information routes consume the commitment; deletion makes the original action irrevisable. |

## 7. Intent and result boundary

| Intent | Historical and institutional meaning | Target or recipient | Required content and lifecycle | Permitting commitments | Environment-owned result |
|---|---|---|---|---|---|
| `issue_consumer_warning` | Communicate bounded safety advice before or apart from formal recall | Public, owners, firm, and intermediaries | Product class, advice, evidence state, issue time, and jurisdiction | `DC-CPSC-1` | Publication, delivery, comprehension, compliance, and effect |
| `request_incident_information` | Seek a bounded incident, product, or investigation account | Firm, intake, or authorized investigator | Question, scope, source, due condition, and uncertainty | `DC-CPSC-1`, `DC-CPSC-2`, `DC-CPSC-3` | Delivery, access, answer, delay, or failure |
| `request_remedy_information` | Seek remedy design, availability, testing, or implementation information | Firm or compliance route | Remedy class, question, evidence, due condition, and jurisdiction | `DC-CPSC-1`, `DC-CPSC-2`, `DC-CPSC-3` | Delivery, adequacy assessment, revision, delay, or failure |
| `issue_recall_action` | Issue a bounded formal recall intent | Firm and jurisdictional recall process | Product scope, hazard basis, remedy terms, issue time, and notice content | `DC-CPSC-2` | Legal state, publication, delivery, execution, and effectiveness |
| `expand_recall_action` | Extend formal action to additional devices or remedies | Firm and jurisdictional recall process | Prior action, new scope, evidence, remedy, and issue time | `DC-CPSC-3` | Supersession, publication, delivery, execution, and effectiveness |

Each request and authority intent has a due or review condition. Equivalent
pending intents suppress duplication. Partial results permit targeted
follow-up; failure, expiry, cancellation, supersession, or material new scope
reopens review. A request-only loop after all named decision-critical
predicates are available is nonconforming, and invalid or unauthorized intents
remain inspectable rather than becoming legal state.

## 8. Operationalization and uncertainty

Assessment categories are `review_open`, `warning_warranted`,
`formal_action_ready`, and `scope_reopened`. They are not legal truth outside
the represented interface. Incident counts remain attributed snapshots, not
calibrated thresholds. Structural uncertainty about staff, chair, and
commission roles remains visible through split triggers.

## 9. Worked cases and falsification

### Warning while remedy review remains open

- **Evidence class:** reconstructed from the exposed 9 September statement.
- **Decision-time situation:** a material concern is supported, while formal
  product and remedy predicates remain incomplete.
- **Required response:** warn, seek a named incident or remedy fact, or retain a
  finite review condition; warning cannot silently become formal recall.
- **Environment boundary:** publication, delivery, compliance, and remedy
  availability remain external.
- **Perturbation:** supplying the named missing remedy predicate reopens formal
  action review; removing the material concern removes the warning minimum.

### First formal-recall review

- **Evidence class:** reconstructed from the exposed 15 September notice.
- **Decision-time situation:** product scope, hazard record, and proposed
  remedy are sufficiently bounded for jurisdictional action review.
- **Required response:** issue a recall-family intent or request one specific
  unresolved predicate; repeated requests after all named predicates are
  available are nonconforming.
- **Environment boundary:** legal state, notice delivery, stock, exchange,
  refund, and effectiveness remain external.
- **Perturbation:** changing product scope or remedy completeness changes the
  required content without declaring a different consumer response.

### Replacement-device scope reopening

- **Evidence class:** reconstructed from the exposed 13 October notice.
- **Decision-time situation:** a delivered replacement-device signal conflicts
  with the current recall and remedy scope.
- **Required response:** expand review through an expansion or targeted
  evidence intent while preserving the signal's attributed uncertainty.
- **Environment boundary:** publication, supersession, outlet action, consumer
  receipt, and completed remedy remain external.
- **Perturbation:** masking the new signal preserves the earlier scope;
  delivering it reopens review without injecting defect cause.

The model fails if an always-wait policy remains conforming after a material
concern, if warning and recall are interchangeable, or if an issued action
declares remedy completion. Name erasure preserves behavior; splitting warning
and recall offices matters only if new evidence assigns different information
or non-transferable authority.

## 10. Limitations and references

The Definition does not reconstruct internal Commission voting or staff work,
prove hazard cause, estimate recall effectiveness, or claim optimal regulatory
action. It is an exposed qualitative account of one authority interface.

References: U.S. CPSC statements and recall notices of 9 September,
15 September, and 13 October 2016. Complete locators, limitations, and
withdrawal consequences appear in the [participant evidence](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md).
