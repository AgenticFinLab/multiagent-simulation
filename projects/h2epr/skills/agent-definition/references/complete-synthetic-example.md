# Complete synthetic Agent Definition example

This document is an illustrative authoring example, not an accepted event
asset. The event, records, participant, identifiers, observations, and choices
are synthetic. Copy the method and degree of specificity; do not copy its
domain terms, values, or response structure into a real event.

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `harbor_response_office`; Harbor Response Office |
| Benchmark event and interval | `H2EPR-0000`; synthetic spill-response interval |
| Represented decision interface | the office interface that requests navigation restrictions and communicates operational notices after receiving incident information |
| Source participant IDs | `P_3`; Draft appearances `draft_epg:S1/E1/P_3`, `draft_epg:S2/E2/P_3`, and `draft_epg:S3/E3/P_3` |
| Primary decision situations | `decision.response_request` response request; `decision.operational_notice` operational notice |
| Decision cadence | event-triggered; exact scheduling belongs to backend configuration |
| State authority | trace-derived own dispositions, delivered messages, pending lifecycles, and the named persistent fields; the environment owns all updates |
| Dataset exposure and scope | admitted synthetic `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`; no Reference or later evaluation input |
| Definition semantic ID | `h2epr.0000.agent.harbor_response_office.v1` |

The Agent represents a bounded office choice: what restriction-related request
to make after a qualified incident report and what operational notice to issue
after a relevant disposition. It does not represent the harbor authority as a
whole. The environment owns navigation status, legal authorization, route
availability, message delivery, cleanup progress, and physical effects.

## 2. Benchmark participant and representation

The synthetic Draft attributes response requests and public operational
updates to `P_3`. The roster therefore admits one named Agent
instead of treating the office as a passive institutional process.

| Internal or related unit | Status | Included function | Excluded function | Reason |
|---|---|---|---|---|
| incident desk | included | receives and records qualified incident reports for this interface | independent investigation | the Draft routes reports through the office |
| duty coordinator | included | selects requests and notices within the two decision commitments | physical execution | the Draft attributes the requests to the office |
| harbor legal office | excluded | none | authorizes compulsory closure | authorization is not attributed to `P_3` |
| cleanup operator | excluded | none | allocates crews and reports progress | represented as an environment process |
| port users | excluded | none | individual compliance choices | represented as a Population in this synthetic design |

The aggregation hides disagreement between the incident desk and duty
coordinator. A successor must split them if an admitted package exposes
different observations, an independent veto, or separately attributable
choices. Narrow the Agent instead if later review shows that it only
communicates notices and never selects a restriction request.

Rejected dispositions:

- not context, because the participant makes attributable requests;
- not a Population, because this is one accountable office interface; and
- not an institutional process, because response selection remains open.

## 3. Dataset basis and provenance

### Claim ledger

| Claim label | Anchor | Class | Semantic use | Limitation or withdrawal consequence |
|---|---|---|---|---|
| `claim.event_identity` | `event_spec.json#/public_event_id` and `#/title` | dataset material | event identity only | removing it invalidates the example event binding |
| `claim.incident_report_role` | `draft_epg:S1/E1/P_3` | dataset material | participant receives an incident report | does not establish report truth or completeness |
| `claim.restriction_request_role` | `draft_epg:S2/E2/P_3` | dataset material | participant can request a navigation restriction | does not establish authorization or success |
| `claim.operational_notice_role` | `draft_epg:S3/E3/P_3` | dataset material | participant communicates an operational notice | does not prove delivery or compliance |
| `claim.disposition_semantics` | `frozen_evidence:source:SYN-F1` | dataset material | a restriction disposition can be represented | status and timing remain scenario-owned |
| `claim.draft_order` | `draft_epg:S1/E1` and `draft_epg:S2/E2` | dataset material | report appearance precedes the Draft request appearance | sequence is a Draft relation, not a causal finding |
| `assumption.structured_incident_report` | participant-interface design | executable structural assumption | incident reports carry an affected-area field | alternative is an explicit unknown area |
| `assumption.addressed_request_disposition` | scenario-interface design | executable structural assumption | the office receives typed request dispositions | alternative is public-status observation only |

### Assumption ledger

| Assumption | Missing dataset detail | Selected structure | Owner | Affected commitments | Alternative and successor condition |
|---|---|---|---|---|---|
| `assumption.structured_incident_report` | Draft does not enumerate report fields | report includes incident ID, observed condition class, and affected area or explicit unknown | shared participant interface | `decision.response_request` | use an unstructured report only if all backends receive an equivalent bounded projection |
| `assumption.addressed_request_disposition` | Draft does not specify private versus public disposition | addressed typed disposition is deliverable to the office | scenario route | `decision.response_request`, `decision.operational_notice` | replace with public status if the accepted scenario cannot justify addressed delivery |

The Definition does not treat the synthetic Draft as verified history. Later
Draft stages help identify possible semantics but are unavailable to the Agent
until a scenario transition produces and delivers the corresponding
observation.

Vocabulary exposure is limited to domain-neutral lifecycle values and the
synthetic response-scope categories declared below. The backend never receives
the Draft's later action or result text.

## 4. Event role, relationships, and authority

| Counterparty or process | Direction | Interface authority | Environment boundary |
|---|---|---|---|
| incident-reporting process | receive | observe delivered qualified reports | environment decides whether a report exists and is delivered |
| navigation authority | send | request a restriction or clarification | authority admits, rejects, or delays the request |
| port-user population | send | issue an operational notice to an eligible audience | transport owns delivery; users own response |
| cleanup process | receive | observe a delivered progress notice if routed | environment owns cleanup allocation and progress |

Authority dimensions:

| Dimension | Agent authority |
|---|---|
| decide | selects among response and notice alternatives in active commitments |
| authorize | no authority to make a navigation restriction effective |
| communicate | may emit the typed requests and notices listed in module 7 |
| allocate | no direct allocation of routes, crews, or equipment |
| execute | no direct navigation control or cleanup execution |
| verify | may not certify physical safety or completion |
| observe | only delivered observations in module 5 |

The Agent controls the content of its own admissible intents. It may request a
scope but does not control whether that scope exists, is legally available, or
becomes effective.

## 5. Decision situations, observations, and state

### Observation inventory

| Observation ID | Exposed content used here | Producer and route | Availability/freshness | Missing behavior | Visibility and consuming decisions |
|---|---|---|---|---|---|
| `obs.public_state` | sealed values of the persistent state fields listed below | H2EPR runtime from authoritative prestate | current at coordinate open; superseded by a later sealed version | malformed or absent required state fails admission | public or visibility-filtered; both decisions |
| `obs.delivered_messages` | typed `incident_report`, `request_disposition`, and `cleanup_progress_notice` messages actually delivered to this actor | MASim transport over `route.incident_reporting_interface.to.harbor_response_office`, `route.navigation_authority.to.harbor_response_office`, and `route.cleanup_operator.to.harbor_response_office` | current delivery batch; retained copies move into participant memory | empty list; absence supplies no report, disposition, or progress claim | addressed; both decisions according to message kind |
| `obs.pending_lifecycles` | this actor's outgoing nonterminal message lifecycle references | MASim transport | current at every coordinate | empty list | own lifecycle view; `decision.response_request` |
| `obs.participant_memory` | trace-derived received messages and this actor's prior action dispositions | H2EPR runtime | retained through the event and updated before decision collection | empty at the first coordinate; malformed memory fails | actor-private; both decisions |

The Agent cannot observe the navigation authority's private deliberation,
undelivered reports, future Draft stages, unreported cleanup world state,
population compliance, evaluator labels, or Reference structure.

### Persistent state surface

| Exact state-field path | Initial condition | Update event and owner | Visibility | Consuming decisions |
|---|---|---|---|---|
| `entities.navigation.restriction_status` | `unrecorded` | accepted environment handler records the admitted status | public | both decisions |
| `entities.communication.operational_notice_status` | `unrecorded` | accepted `issue_operational_notice` handler records issuance, not delivery | public | `decision.operational_notice` |
| `entities.cleanup.progress_status` | `unreported` | environment-owned cleanup process records a qualified update | public | `decision.operational_notice` |

The participant interface projects these exact paths without creating
document-only state aliases. Outstanding requests, received notices, and own
prior dispositions remain trace-derived through `obs.pending_lifecycles` and
`obs.participant_memory`. Selecting a request does not make it admitted,
delivered, authorized, or effective.

Reconsideration becomes meaningful when a missing affected area is supplied,
a report is superseded, an outstanding request receives a disposition, a
navigation status changes, or a new incident report activates a separate
instance. Exact polling or retry cadence is not defined here.

## 6. Admissible decision semantics

### `decision.response_request` — choose a response request

| Field | Contract |
|---|---|
| situation | response choice after a delivered qualified incident report |
| activation | `obs.delivered_messages` contains a current `incident_report` for an incident |
| non-applicable | no report has been delivered, or the report was withdrawn without replacement |
| usable information | `obs.delivered_messages`, `obs.public_state`, `obs.pending_lifecycles`, `obs.participant_memory`, and `entities.navigation.restriction_status` |
| alternatives | emit `request_navigation_restriction` restriction request; emit `request_report_clarification` clarification request when a mandatory report field is unknown; emit `withdraw_own_request` withdrawal for an outstanding own request when new information changes its basis; bounded delay only while a declared required field or disposition is pending |
| minimum response | once a report contains the mandatory fields and no equivalent request is pending, emit a request, explicitly withdraw an obsolete request, or record an admissible response choice; silent indefinite no-op is forbidden |
| prohibitions | assert effective closure; allocate routes; use future Draft results; request a target outside the registry |
| precedence | withdrawal of an obsolete own request precedes a replacement request for the same incident when both would otherwise conflict |
| reopening | superseding report, disposition, status change, or expiration/withdrawal of the outstanding request |
| environment boundary | request admission, authority, effective scope, timing, and navigation effect |
| falsifier | a trace records effective navigation status as a direct Agent state write |

World feasibility includes target eligibility and available restriction scope.
Mandatory actor information includes incident identity and a condition class;
affected area may be explicit unknown, in which case clarification remains
admissible. Preference among request scope, clarification, withdrawal, and
bounded delay is backend selection within this contract.

### `decision.operational_notice` — choose an operational notice

| Field | Contract |
|---|---|
| situation | communication choice after a new delivered request disposition, navigation status, or relevant cleanup notice |
| activation | a newer public restriction status, delivered `request_disposition` or `cleanup_progress_notice`, or delivery-failure receipt is visible relative to the last own notice in `obs.participant_memory` |
| non-applicable | no externally relevant delivered information is newer than the last own notice |
| usable information | all four registered observation IDs plus `entities.navigation.restriction_status`, `entities.communication.operational_notice_status`, and `entities.cleanup.progress_status` |
| alternatives | emit `issue_operational_notice` with only delivered status; withhold a notice when the new information is explicitly own-private and has no admissible public projection |
| minimum response | a newly effective public navigation-status change requires an operational notice attempt |
| prohibitions | announce cleanup completion without a delivered notice; announce a request as effective; expose private authority reasoning |
| precedence | current public status supersedes the requested scope when composing a notice |
| reopening | newer status, disposition, progress notice, or delivery failure receipt |
| environment boundary | message admission, delivery, audience receipt, compliance, and downstream effects |
| falsifier | notice content claims a restriction is effective when only a pending request exists |

Rule code, an LLM, or RuleLLM admission selects within these sets. All receive
the same commitment identity, observation boundary, prohibitions, intent
schemas, and environment-result boundary.

## 7. Intent and environment-result boundary

| Exact registry `intent_id` | Permitting decisions | Meaning | Eligible target | Required content and lifecycle | Environment-owned result |
|---|---|---|---|---|---|
| `request_navigation_restriction` | `decision.response_request` | asks the navigation authority to consider a bounded restriction | `navigation_authority` | incident ID, requested scope category, and basis observation IDs; submitted → accepted/rejected; may attach `navigation_restriction_request` | authorization, effective scope, start/end, and navigation state |
| `request_report_clarification` | `decision.response_request` | asks the registered report producer for a missing field | `incident_reporting_interface` | incident ID, report version, and missing field; submitted → accepted/rejected; may attach `report_clarification_request` | whether clarification is available, delivered, or true |
| `issue_operational_notice` | `decision.operational_notice` | requests publication of delivered operational status | `port_user_population` | incident ID, cited delivered observation versions, and bounded notice content; submitted → accepted/rejected; may attach `operational_notice` | audience receipt, interpretation, compliance, and physical effect |
| `withdraw_own_request` | `decision.response_request` | requests withdrawal of one outstanding own restriction request | `navigation_authority` | request ID and superseding basis; submitted → accepted/rejected; may attach `request_withdrawal_notice` | whether withdrawal is accepted or prevents later action |

### Message output surface

| Exact scenario `message_type` | Permitting action type | Eligible recipients | Payload semantics | Environment-owned result |
|---|---|---|---|---|
| `navigation_restriction_request` | `request_navigation_restriction` | `navigation_authority` | incident ID, requested scope category, and cited observation versions | admission, route availability, delivery, authority interpretation, and response |
| `report_clarification_request` | `request_report_clarification` | `incident_reporting_interface` | incident ID, report version, and missing field | admission, delivery, availability of clarification, and response |
| `operational_notice` | `issue_operational_notice` | `port_user_population` | incident ID, delivered status versions, and bounded notice content | admission, recipient delivery, interpretation, compliance, and physical effect |
| `request_withdrawal_notice` | `withdraw_own_request` | `navigation_authority` | outstanding request ID and superseding basis | admission, delivery, acceptance, and downstream cancellation |

These four values become participant-decision `action_type` values. Each
emission receives a separate generated `ActionIntent.intent_id`; the local
`decision.*` label is never used as a runtime instance identity. Duplicate
handling follows that runtime identity and the declared lifecycle. Each
attached message also receives a generated `message_intent_id` distinct from
its `message_type`. The Agent may emit a successor notice or request only after
a reopening event; it does not rewrite a prior trace record.

## 8. Configurable dimensions and uncertainty

| Construct | Meaning/unit | Admissible domain | Configuration owner | Behavioral use |
|---|---|---|---|---|
| `response_scope_category` | requested operational extent | `local_area`, `route_segment`, `harbor_wide`; synthetic categorical domain | shared event configuration | content available to `request_navigation_restriction` |
| `reconsideration_schedule` | when an active backend is invoked after a reopening event | event-triggered schedule choices admitted by runtime | backend configuration | invocation timing only; does not create new reopening events |
| `notice_audience_projection` | registered audience classes visible to the Agent | non-empty subsets of eligible registry targets | shared event configuration | targets available to `issue_operational_notice` |
| `pending_response_policy` | preference among clarification, bounded delay, or another admissible response | enumerated backend policy choices | backend realization/configuration | selection under missing or pending information |

The scope categories and addressed-disposition route are synthetic structural
choices, not historical measurements. The Definition supplies no personality
scores, calibrated probabilities, preferred outcome, or Rule threshold.

## 9. Worked cases and contract falsification

### `case.complete_report` — complete report, open choice

`obs.delivered_messages` contains a current `incident_report` with all
mandatory fields, and `obs.participant_memory` contains no equivalent prior
accepted request. `decision.response_request` is active. More than one request
scope may be admissible, and the backend may select among them. Claiming that a
request is already effective is forbidden. The environment may admit or reject
the selected intent. A direct navigation-state mutation by the Agent falsifies
the contract.

### `case.missing_affected_area` — missing affected area

The report carries an explicit unknown affected area. Clarification and any
semantically bounded response admitted for unknown scope remain possible;
indefinite silent no-op does not. Future Draft scope is unavailable. If backend
context contains that later scope, the exposure contract is falsified.

### `case.pending_request` — pending request

The Agent emitted `request_navigation_restriction`;
`obs.participant_memory` contains its accepted action disposition and
`obs.pending_lifecycles` contains the related outgoing message, but no delivered
`request_disposition` exists. The Agent may wait within the admitted pending
policy or act on a superseding report, but it may not issue a notice that calls
the requested restriction effective. Such a notice falsifies
`decision.operational_notice`.

### `case.authority_denial` — authority denial

The environment rejects an otherwise admissible
`request_navigation_restriction`. The rejection is a valid environment result
and does not retroactively make the participant choice invalid. A later
delivered rejection may reopen `decision.response_request`; automatic world
restriction would falsify the authority boundary.

### `case.partial_result` — partial or adverse result

The authority admits a narrower effective scope than requested. The Agent may
observe only the delivered current status and may issue a notice citing that
status. It may not publish the requested broader scope as fact. Equating
requested and effective scope falsifies the intent/result separation.

### `case.missing_condition_perturbation` — meaningful perturbation

Hold the backend and identity fixed, then replace a complete report with one
whose condition class is unknown. The admissible set loses restriction-request
alternatives that require that mandatory field and retains clarification or
other explicitly bounded responses. If the same hidden future information
restores the original set, the information boundary is falsified.

### `case.superseding_notice` — superseding notice

A newer public status conflicts with the Agent's last own notice.
`decision.operational_notice` reopens, and the older status becomes stale. The
backend may choose admissible wording, but cannot reuse the stale status as
current. A trace that does so falsifies freshness handling.

## 10. Limitations and source anchors

This example aggregates the incident desk and duty coordinator, omits internal
legal deliberation, treats port users as a Population, and assumes typed
addressed dispositions. It does not model physical spill dynamics, cleanup
allocation, legal validity, message interpretation, or compliance as Agent
choices.

A successor is required if admitted data exposes independent office vetoes,
different internal information sets, direct closure authority, or a report
format incompatible with `assumption.structured_incident_report`. Scenario
revision is required if addressed dispositions cannot be produced.
Configuration revision is sufficient for a different admitted schedule or
scope-domain selection.

Source anchors used by the synthetic example:

- `event_spec.json#/public_event_id`;
- `event_spec.json#/title`;
- `frozen_evidence:source:SYN-F1`;
- `draft_epg:S1/E1/P_3`;
- `draft_epg:S2/E2/P_3`;
- `draft_epg:S3/E3/P_3`.

Semantic parents are the synthetic accepted Source Profile, roster disposition,
shared observation/intent registry, and scenario vocabulary. This example has
no release disposition, backend, run, evaluation result, or scientific claim.
