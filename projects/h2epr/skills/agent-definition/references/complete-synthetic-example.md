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
| Decision cadence | runtime invokes every active actor at every logical coordinate; backend rules select an action or `no_op` from the bounded situations below |
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
| cleanup operator | excluded context | none | allocates crews and produces physical progress | no active actor or transport sender in this design |
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

The Definition does not treat the synthetic Draft as verified history. Full
Draft stages inform the designed vocabulary, including later restriction,
withdrawal and notice terms. This design follows the current runtime's declared
event-vocabulary-exposed boundary; it makes no historically prefix-clean claim.

| Surface | Content available | Availability and evidential limit |
|---|---|---|
| Observation packet metadata | own `actor_id`, logical coordinate and state-version/identity metadata | available at each coordinate, including the first; identifiers and time do not prove an event result |
| Public state vocabulary | public entity and field names, including navigation, office request and operational notice fields in module 5 | names are visible from the first coordinate even while values remain `unrecorded` |
| Actor capability menu | the office's complete `permitted_action_types`: the four module-7 action types plus `no_op` | visible from the first coordinate; membership does not establish current eligibility or shared admission |
| Rule configuration | configured action rows, targets, message types, payload/guard constants, response-scope categories and selection windows | available at backend setup, including possible later status values; a configured value is not evidence that it has been observed or realized |
| Generated public values and own dispositions | sealed public prestate and trace-derived own action results | initial values are declared at start; public values change through accepted shared effects, while own memory records both acceptance and rejection; an accepted request does not prove navigation authorization |
| Received report and disposition content | delivered `incident_report` and `request_disposition` messages, including retained copies | usable as received information only after actual delivery; outgoing pending metadata supplies no recipient receipt |

The runtime does not supply raw Draft stage descriptions as participant
observations. Undelivered reports and unrealized results cannot be used as
received information or achieved facts. Their field/action names and possible
configured values can already be known; vocabulary alone cannot fill a missing
report field or satisfy a mandatory receipt requirement. A real projection
must audit both the observation packet and backend configuration against this
inventory, rather than inferring exposure solely from delivered messages.

## 4. Event role, relationships, and authority

| Counterparty or process | Direction | Interface authority | Environment boundary |
|---|---|---|---|
| `incident_reporting_interface` (separate active Agent) | receive/send | receive typed reports; request missing fields | producer chooses report content; shared handlers and transport control admission and delivery |
| `navigation_authority` (separate active Agent) | send/receive | request a restriction or withdraw the office request; receive authority dispositions | authority chooses its response; shared handlers control effective navigation state |
| port-user population | send | issue an operational notice to an eligible audience | transport owns delivery; users own response |
| cleanup process (context only) | none | no report or message interface | physical cleanup is outside this model |

Authority dimensions:

| Dimension | Agent authority |
|---|---|
| decide | selects among response and notice alternatives in active commitments |
| authorize | no authority to make a navigation restriction effective |
| communicate | may emit the typed requests and notices listed in module 7 |
| allocate | no direct allocation of routes, crews, or equipment |
| execute | no direct navigation control or cleanup execution |
| verify | may not certify physical safety or completion |
| observe | current runtime state, actually received messages and trace-derived own memory/lifecycles in module 5, with the vocabulary exposure declared in module 3 |

The Agent controls the content of its own admissible intents. It may request a
scope but does not control whether that scope exists, is legally available, or
becomes effective.

## 5. Decision situations, observations, and state

### Observation inventory

| Observation ID | Exposed content used here | Producer and route | Availability/freshness | Missing behavior | Visibility and consuming decisions |
|---|---|---|---|---|---|
| `obs.public_state` | sealed values of the persistent state fields listed below | H2EPR runtime from authoritative prestate | current at coordinate open; superseded by a later sealed version | malformed or absent required state fails admission | public or visibility-filtered; both decisions |
| `obs.delivered_messages` | typed `incident_report` and `request_disposition` messages actually delivered to this actor | MASim transport from active `incident_reporting_interface` and `navigation_authority` to `harbor_response_office` | current delivery batch; retained copies move into participant memory | empty list; absence supplies no report or authority disposition | addressed; both decisions according to message kind |
| `obs.pending_lifecycles` | this actor's outgoing nonterminal message lifecycle references | MASim transport | current at every coordinate | empty list | own lifecycle view; `decision.response_request` |
| `obs.participant_memory` | trace-derived received messages and this actor's prior action dispositions | H2EPR runtime | retained through the event and updated before decision collection | empty at the first coordinate; malformed memory fails | actor-private; both decisions |

The four registered observation IDs describe state, receipt and memory
surfaces; they do not exhaust the packet's metadata or capability menu. Own
`actor_id` and `permitted_action_types` are also exposed as declared in module 3;
no fifth observation ID is invented for them. This design declares no private
persistent world fields. The Agent cannot observe the navigation authority's
private deliberation, undelivered report content, raw Draft stage descriptions,
unreported cleanup world state, population compliance, evaluator labels, or
Reference structure. Knowing a future field or action name does not reveal a
future generated result.

### Persistent state surface

| Exact state-field path | Initial condition | Update event and owner | Visibility | Consuming decisions |
|---|---|---|---|---|
| `entities.navigation.restriction_status` | `unrecorded` | shared handler of the separate active navigation authority's admitted status action | public | both decisions |
| `entities.communication.operational_notice_status` | `unrecorded` | accepted `issue_operational_notice` handler records issuance, not delivery | public | `decision.operational_notice` |
| `entities.office.request_status` | `unrecorded` | shared handlers of this office's accepted request and withdrawal record `requested` or `withdrawn`; neither changes navigation state | public | `decision.response_request` |

The participant interface projects these exact paths without creating
document-only state aliases. Outstanding requests, received notices, and own
prior dispositions remain trace-derived through `obs.pending_lifecycles` and
`obs.participant_memory`. Selecting a request does not make it admitted,
delivered, authorized, or effective.

This is a finite, single-incident design. Each of the four office action rows
can be accepted once. A rejected row can be reconsidered when visible report,
state, or transport information changes. Acceptance completes that Rule row;
a later incident does not create a new runtime commitment instance. Additional
requests or successor notices need distinct, reviewed rows and are outside
this example. `entities.office.request_status` records business status, not
the transport lifecycle of an already emitted request message.

## 6. Admissible decision semantics

### `decision.response_request` — choose a response request

| Field | Contract |
|---|---|
| situation | initial request or clarification after a delivered incident report, or withdrawal of a current own request after a delivered withdrawal of its basis |
| activation | the latest actually received `incident_report` in current messages or retained memory and the own request state meet an uncompleted intent's conditions in the table below; backend guards select and shared information requirements admit the action |
| non-applicable | no non-`no_op` intent satisfies its own information, request-state and row-completion conditions; withdrawal of a basis alone does not disable withdrawal of a current own request |
| usable information | `obs.delivered_messages`, `obs.public_state`, `obs.pending_lifecycles`, `obs.participant_memory`, and `entities.navigation.restriction_status` |
| alternatives | before any accepted own request, emit `request_navigation_restriction` on a complete non-withdrawn report or `request_report_clarification` on a non-withdrawn report with known incident identity and an explicitly unknown required field; emit `withdraw_own_request` only for an accepted, still-current own request whose basis the latest received report withdraws; `no_op` remains admissible in every situation |
| minimum response | no general machine-enforced duty or eventual-response guarantee; a Rule realization may prefer an enabled action over `no_op`, and review must disclose that selection policy |
| prohibitions | assert effective closure; allocate routes; use future Draft results; request a target outside the registry |
| precedence | a withdrawn basis disables new requests and clarification; for a current accepted own request only withdrawal or `no_op` remains admissible; this is not a machine-enforced withdrawal duty and there is no replacement-request row |
| reopening | a rejected, not yet accepted row may retry after visible information changes; a completed row never rearms |
| environment boundary | request admission, authority, effective scope, timing, and navigation effect |
| falsifier | a trace records effective navigation status as a direct Agent state write |

The following table specifies the information and business-state alternatives
for `decision.response_request`, not the independent notice decision. A current
own request requires both a trace-derived accepted request disposition and
`entities.office.request_status == requested`. Every non-`no_op` alternative
also requires its own Rule row to remain unaccepted and its selection window
to be open. Remove completed or out-of-window alternatives; `no_op` remains.

| Latest actually received report | Own request state | Alternatives before shared admission |
|---|---|---|
| No report, or no usable incident identity | any otherwise valid own state | `no_op` |
| Non-withdrawn; identity, condition and affected area known | no accepted own request; status `unrecorded` | `request_navigation_restriction`, `no_op` |
| Non-withdrawn; identity known; condition or affected area explicitly unknown | no accepted own request; status `unrecorded` | `request_report_clarification`, `no_op` |
| Basis withdrawn for the identified incident | no accepted own request; status `unrecorded` | `no_op` |
| Non-withdrawn report, including a later incomplete report | accepted current own request; status `requested` | `no_op` |
| Basis withdrawn for the same incident as the current request | accepted current own request; status `requested` | `withdraw_own_request`, `no_op` |
| Any report, including withdrawn basis or a replacement complete report | prior own request already withdrawn; status `withdrawn` | `no_op` |

World feasibility still includes target eligibility and available restriction
scope. A new restriction request requires a non-withdrawn basis with known
incident identity, condition class and affected area. Clarification requires
identity and an explicitly unknown field; it does not require that field's
missing value. Withdrawal requires the identified withdrawn basis and current
own request, not a newly qualified condition or affected area. It remains
admissible whether the original outgoing message is pending or already
delivered. A real projection must reject inconsistent required state/memory
rather than derive permission from it. The request-state and received-basis
checks remain part of the unclosed handler/information projections in module
10. Preference between an enabled action and `no_op` belongs to backend
selection, and denial of an action remains possible.

### `decision.operational_notice` — choose an operational notice

| Field | Contract |
|---|---|
| situation | one public operational notice after an authority disposition has actually arrived |
| activation | latest received `request_disposition` carries a publishable status, agrees with current public navigation state, and no office notice action has been accepted |
| non-applicable | absent, unresolved, private-only, or stale disposition; or the one notice row already completed |
| usable information | all four registered observation IDs plus `entities.navigation.restriction_status` and `entities.communication.operational_notice_status` |
| alternatives | emit `issue_operational_notice` citing the received and currently consistent status; otherwise `no_op` |
| minimum response | no general eventual-publication or delivery guarantee; selection preference belongs to the reviewed Rule policy |
| prohibitions | announce cleanup completion without a delivered notice; announce a request as effective; expose private authority reasoning |
| precedence | current public status supersedes the requested scope when composing a notice |
| reopening | an unaccepted row may retry after a newer received disposition; accepted notice issuance does not rearm on message failure |
| environment boundary | message admission, delivery, audience receipt, compliance, and downstream effects |
| falsifier | notice content claims a restriction is effective when only a pending request exists |

The current Rule backend consumes registered observations and action rows.
The `decision.*` labels organize this human contract; they are not observation
fields or invocation instances. Future backend comparisons must preserve the
same observation and shared admission boundaries; this example implements no
LLM or RuleLLM backend.

## 7. Intent and environment-result boundary

| Exact registry `intent_id` | Permitting decisions | Meaning | Eligible target | Required content and lifecycle | Environment-owned result |
|---|---|---|---|---|---|
| `request_navigation_restriction` | `decision.response_request` | asks the navigation authority to consider a bounded restriction | `navigation_authority` | no prior accepted own request; incident ID, known condition and affected area from a non-withdrawn report, requested scope category, and basis observation IDs; submitted → accepted/rejected; may attach `navigation_restriction_request` | authorization, effective scope, start/end, and navigation state |
| `request_report_clarification` | `decision.response_request` | asks the registered report producer for a missing field | `incident_reporting_interface` | no prior accepted own request; incident ID, non-withdrawn report version, and explicitly unknown required field; submitted → accepted/rejected; may attach `report_clarification_request` | whether clarification is available, delivered, or true |
| `issue_operational_notice` | `decision.operational_notice` | requests publication of delivered operational status | `port_user_population` | incident ID, cited delivered observation versions, and bounded notice content; submitted → accepted/rejected; may attach `operational_notice` | audience receipt, interpretation, compliance, and physical effect |
| `withdraw_own_request` | `decision.response_request` | records withdrawal of the office's current business request | `navigation_authority` | own accepted request still has status `requested`; incident ID and latest received withdrawn basis refer to that same request; submitted → accepted/rejected; accepted handler sets office request status to withdrawn and may attach `request_withdrawal_notice` | authority response and navigation effect; no cancellation of the earlier transport message |

### Message output surface

| Exact scenario `message_type` | Permitting action type | Eligible recipients | Payload semantics | Environment-owned result |
|---|---|---|---|---|
| `navigation_restriction_request` | `request_navigation_restriction` | `navigation_authority` | incident ID, requested scope category, and cited observation versions | admission, route availability, delivery, authority interpretation, and response |
| `report_clarification_request` | `request_report_clarification` | `incident_reporting_interface` | incident ID, report version, and missing field | admission, delivery, availability of clarification, and response |
| `operational_notice` | `issue_operational_notice` | `port_user_population` | incident ID, delivered status versions, and bounded notice content | admission, recipient delivery, interpretation, compliance, and physical effect |
| `request_withdrawal_notice` | `withdraw_own_request` | `navigation_authority` | incident ID and superseding basis | delivery and later authority response; authority must check current business status before acting on an older request |

The four registry intent IDs in the first table become participant-decision
`action_type` values; the second table lists distinct message types. Each
emission receives a separate generated `ActionIntent.intent_id`; the local
`decision.*` label is never used as a runtime instance identity. Duplicate
handling follows that runtime identity and the declared lifecycle. Each
attached message also receives a generated `message_intent_id` distinct from
its `message_type`. Shared admission and reducer application occur before
transport submission of attached messages. Thus accepted request status or
notice issuance can coexist with a pending or failed message; subsequent
authority action or audience response is separate. No prior trace is rewritten.

## 8. Configurable dimensions and uncertainty

| Construct | Meaning/unit | Admissible domain | Configuration owner | Behavioral use |
|---|---|---|---|---|
| `response_scope_category` | requested operational extent | `local_area`, `route_segment`, `harbor_wide`; synthetic categorical domain | shared event configuration | content available to `request_navigation_restriction` |
| `selection_windows` | logical coordinates where each finite Rule row is selectable | coordinate subsets within the scenario timeline | Rule configuration | selection eligibility; runtime still invokes every actor each coordinate |
| `notice_audience_projection` | registered audience classes visible to the Agent | non-empty subsets of eligible registry targets | shared event configuration | targets available to `issue_operational_notice` |
| `pending_response_policy` | preference among clarification, bounded delay, or another admissible response | enumerated backend policy choices | backend realization/configuration | selection under missing or pending information |

The scope categories and addressed-disposition route are synthetic structural
choices, not historical measurements. The Definition supplies no personality
scores, calibrated probabilities, preferred outcome, or Rule threshold.

## 9. Worked cases and contract falsification

### `case.complete_report` — complete report, open choice

`obs.delivered_messages` contains a current non-withdrawn `incident_report` with all
mandatory fields, and `obs.participant_memory` contains no equivalent prior
accepted request. `decision.response_request` is active. More than one request
scope may be admissible for `request_navigation_restriction`, and the backend
may select among them. Claiming that a
request is already effective is forbidden. The environment may admit or reject
the selected intent. A direct navigation-state mutation by the Agent falsifies
the contract.

### `case.missing_affected_area` — missing affected area

The received non-withdrawn report carries an explicit unknown affected area,
and neither an own request nor the clarification row has been accepted. In
`decision.response_request`, `request_report_clarification` and `no_op` remain
admissible; `request_navigation_restriction` is not. Accepted clarification
does not supply the missing area: its message can fail, and the producer may
reply with another unknown. A later received qualified report may enable the
unaccepted request row. Configured response-scope categories are already known,
but they cannot supply the report's missing affected area. If configuration
vocabulary restores request eligibility without a qualifying received report,
the information contract is falsified.

### `case.pending_request` — pending request

For `decision.response_request`, the Agent emitted `request_navigation_restriction`;
`obs.participant_memory` contains its accepted action disposition and
`obs.pending_lifecycles` contains the related outgoing message, but no delivered
`request_disposition` exists. The Agent may select `no_op` or withdraw on a
received withdrawn basis, but it may not issue a notice that calls
the requested restriction effective. Such a notice falsifies
`decision.operational_notice`.

### `case.authority_denial` — authority denial

The office's `request_navigation_restriction` action was accepted, but the
separate navigation authority later sends a denied `request_disposition`.
`decision.operational_notice` may select `issue_operational_notice` reporting
denial if it agrees with public state. The authority's denial neither changes
the earlier action disposition nor rearms its completed Rule row. Automatic
world restriction would falsify the authority boundary. Shared admission
rejection of the office action is different: it produces no accepted state
effect or attached message and may retry after visible information changes.

### `case.partial_result` — partial or adverse result

The authority's accepted status action records a narrower scope than requested.
After its disposition arrives, `decision.operational_notice` may select
`issue_operational_notice` citing that current status. Accepted issuance
updates `entities.communication.operational_notice_status` before attached
message delivery; failed delivery does not undo issuance. It may not publish
the requested broader scope as fact. Equating
requested and effective scope falsifies the intent/result separation.

### `case.missing_condition_perturbation` — meaningful perturbation

In `decision.response_request`, hold the backend and identity fixed, then
replace a complete report with one
whose condition class is unknown. The admissible set loses restriction-request
`request_navigation_restriction` alternatives requiring that field and retains clarification or
other explicitly bounded responses. If the same hidden future information
restores the original set, the information boundary is falsified.

### `case.withdrawal` — withdrawn basis with a request in transport

`decision.response_request` observes an accepted current own request with
`entities.office.request_status == requested`, a pending outgoing message and
a newer received report withdrawing the basis for the same incident. The
withdrawal row is still unaccepted and within its selection window.
`withdraw_own_request` and `no_op` are admissible; a new restriction request
and clarification are not. No replacement qualified report is required to
permit withdrawal. If selected and accepted, the withdrawal handler sets
`entities.office.request_status` to `withdrawn`. The original message can still
arrive, and the withdrawal notice can fail. The authority must observe current
business status before acting; claiming that withdrawal cancelled transport
falsifies this contract. Denied withdrawal leaves business status unchanged.

Hold the withdrawn report fixed and remove the prior accepted own request:
with status `unrecorded`, only `no_op` is admissible. After an accepted
withdrawal, status `withdrawn` also permits only `no_op`, even if a replacement
complete report later arrives; neither accepted row rearms. These adjacent
cases falsify any projection that permits withdrawal without a current own
request or creates a second request from this finite row. Whether the original
message is pending or already delivered does not change these business-state
conditions. Selecting `no_op` does not violate a mandatory withdrawal duty,
because this example declares none.

### `case.stale_notice` — stale disposition before first notice

A newer public status conflicts with the last received disposition, before
the first notice action has been accepted. `decision.operational_notice`
cannot select `issue_operational_notice` using the old disposition. It can
select `no_op` until a matching newer disposition arrives. After one accepted
notice, this bounded design has no successor notice row. A stale notice being
admitted or a completed row firing again falsifies the respective contract.

### Case coverage matrix

This matrix is a review index, not a substitute for the cases above or an
executable harbor fixture. Tests check references and missing-case mutations.
Existing synthetic runtime fixtures separately exercise lifecycle, typed
receipt and producer admission invariants; they do not validate this
uncompiled domain design.

| Case | Decision | Selected or withheld intent | Information condition | Environment branch |
|---|---|---|---|---|
| `case.complete_report` | `decision.response_request` | `request_navigation_restriction` | complete received report | accepted or rejected action |
| `case.missing_affected_area` | `decision.response_request` | `request_report_clarification` | received explicit unknown area | accepted action; reply absent or still unknown |
| `case.pending_request` | `decision.response_request` | `request_navigation_restriction` | accepted own request; authority disposition absent | outgoing message pending; no repeated accepted row |
| `case.authority_denial` | `decision.operational_notice` | `issue_operational_notice` | received denial consistent with public state | authority denial distinct from office action rejection |
| `case.partial_result` | `decision.operational_notice` | `issue_operational_notice` | received narrower status consistent with public state | accepted issuance; delivery may fail |
| `case.missing_condition_perturbation` | `decision.response_request` | `request_navigation_restriction` | condition changed to unknown | request admission must fail |
| `case.withdrawal` | `decision.response_request` | `withdraw_own_request` | withdrawn basis crossed with no request, current request and withdrawn request | only current own request permits withdrawal; old transport survives |
| `case.stale_notice` | `decision.operational_notice` | `issue_operational_notice` | public state conflicts with received disposition | notice admission must fail |

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
Configuration revision is sufficient for a different admitted selection window or
scope-domain selection.

Source anchors used by the synthetic example:

- `event_spec.json#/public_event_id`;
- `event_spec.json#/title`;
- `frozen_evidence:source:SYN-F1`;
- `draft_epg:S1/E1/P_3`;
- `draft_epg:S2/E2/P_3`;
- `draft_epg:S3/E3/P_3`.

This document has no release disposition, backend, run, evaluation result, or
scientific claim. Its illustrative status is not `ACCEPTED`: the synthetic
source anchors and peer Definitions are explanatory, not existing sealed
assets. A real handoff must supply the source profile, roster (four active
actors, cleanup context), shared observation/intent registry, typed report and
disposition declarations, handlers and finite selection rules. It must project
two commitments, four observations, three state fields, four office intents
and four attached message types, then exercise all eight cases.

Module-10 handoff uses `agents/agent-definition-template.md` and this semantic
ID. No exact parent hashes are invented here. A separate review record must
pin the final Definition, template and parent bytes, list these unclosed
projections, and record reviewer/verdict/next owner. Closed semantic-index
fields remain unchanged. Completion requires those projections and their
tests; this human example alone cannot supply executable acceptance.
