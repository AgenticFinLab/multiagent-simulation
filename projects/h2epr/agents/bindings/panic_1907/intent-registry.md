# H2EPR-0288 two-role intent registry

> Registry ID: `h2epr.intent-registry.0288.two-role`
>
> Version: `0.2.1`
>
> Status: `ACCEPTED_SPECIFICATION / NON_EXECUTABLE`
>
> Carrier: H2EPR contracts V1 through mapping profile
> `h2epr.agent-definition.mapping.0288.two-role.v0_2_1`

## 1. Definition bindings

| Definition | Version | Content SHA-256 |
|---|---|---|
| `h2epr.agent-definition.0288.knickerbocker-trust` | `0.2.1` | `d844a7a10c11bfee29c6ec2260a31ddd70748eb290e624f88dc81883d587754d` |
| `h2epr.agent-definition.0288.new-york-clearing-house` | `0.2.1` | `e5cdc9e3f440d6243bf3407cc27e46b2dc280ffd68178d8f66511f6b9bd6996b` |

If either Definition changes, this registry becomes stale until its binding and content identity are updated.

## 2. Shared representation rules

1. Every semantic intent has one primary `ActionIntent` using action type
   `h2epr.action.<semantic_id>` and schema version `h2epr.intent.v0_2_1`.
2. An outward institutional act creates at most one correlated `MessageIntent` per recipient, after the primary
   action is admitted as `accepted` or `partial`. A delayed or rejected action does not send its message.
   If message IDs are deterministically reserved while the decision is staged, the final sealed
   `DecisionRecord.message_intent_ids` must still equal the MessageIntents actually materialized; a rejected or
   delayed source act cannot leave an orphan declared message ID.
3. The parameter lists below are semantic contracts, not an instruction to duplicate every value inside
   `ActionIntent.parameters`. A binding projection assigns each semantic value to exactly one canonical V1 slot:
   business payload in `parameters`, actor targets in `target_entity_ids`, authority records in
   `claimed_authority_refs`, offered/requested quantities in `resource_offer_or_request`, and action validity in
   `earliest_effect_time`/`expiry_time`. If a correlated message repeats admitted content for delivery, exact
   equality and lineage to the action are required; the message is not a second business authority.
4. `claimed_authority_refs` must resolve to scoped environment-owned authority records but never grant authority.
5. Only the reducer emits `StateDelta`. An Agent or adapter cannot declare its requested transition realized.
6. Every used external value must resolve to an actor-visible delivered `ObservationPayload` field.
7. Invalid, unauthorized, duplicate, expired, or out-of-envelope attempts are rejected and traced; no adapter
   silently clamps or repairs them.
8. Action admission, message transport/delivery, institutional disposition, execution, and business result remain
   distinct.
9. `ActionIntent.idempotency_key` is derived from the registry version, actor, semantic intent, primary business
   object or act ID, operation/scope, and relevant authoritative object version. Where an intent has no separate
   act ID (for example an information response), the key uses the request/case IDs, disclosed item IDs, `as_of`,
   and disclosure scope. A retry or revision changes only a named retry/revision component and links to the prior
   attempt; random IDs cannot bypass business equivalence.

### Type vocabulary

| Type | Meaning |
|---|---|
| `stable_id` | V1 `StableId` resolving within the frozen bundle/run |
| `stable_id[]` | flat, unique array of stable IDs |
| `enum{...}` | string restricted to the listed domain |
| `time_value` | dated string or stable time-record reference validated against the scenario time policy |
| `time_value?` | a valid time value or explicit null when the named policy permits no fixed expiry |
| `number` | finite V1 number; a unit is mandatory whenever the value represents a quantity |
| `string` | bounded V1 string used only when an enumerated/stable-ID representation is inappropriate |

`required` below means the semantic value must be represented in its canonical carrier slot on every instance.
`conditional` means a named rule decides whether it must appear; `optional` means it may be absent without a
default. Neither permits the adapter to invent a value. A future executable registry must record the canonical
slot for every listed value and reject duplicate conflicting projections.

### Canonical V1 projection

| Semantic value class | Canonical ActionIntent location | Cross-object requirement |
|---|---|---|
| action/intent identity and version | `action_type`, `action_schema_version` | must match this registry and the actor's ActionDefinition/action-space entry |
| actor or institutional target | `target_entity_ids` | any recipient/audience field used for business correlation must resolve to the same target set |
| scoped authority record | `claimed_authority_refs` | a business parameter may name the scope/question, but cannot duplicate or replace the authority record |
| offered/requested resource or quantity | `resource_offer_or_request` | amount, unit, resource category, and qualitative bound form one validated field family |
| action validity window | `earliest_effect_time`, `expiry_time` | any human-readable validity statement must resolve to the same interval; null expiry remains explicit |
| request/case/proposal IDs, operation, reason, scope, route/channel refs, content categories, and conditions | `parameters` | exact allowed-name/type/domain rules are intent-specific below |
| legal decision input | `observation_refs` | all behaviorally used values resolve through the cited actor-visible ObservationPayload |
| delivery projection | correlated `MessageIntent` | recipient, channel, content, expiry, decision, and business-object refs must be derived from the admitted action without drift |

The executable binding may store a correlation reference in a business parameter even when the referenced
object is also represented by a top-level field, but it must not store a second independently chosen value. The
mapping manifest must say which occurrence is canonical and which is a checked projection.

## 3. Knickerbocker Trust registry

### `verify_internal_condition`

- Commitments: `DC-KT-01`.
- Required parameters: `verification_request_id:stable_id`, `information_category_ids:stable_id[]`,
  `required_as_of:time_value`, `responsible_interface_id:stable_id`.
- Observations: `internal_liquidity_assessment` and `withdrawal_pressure`.
- Persistent participant state: `last_verified_condition_time`.
- Authority: ordinary or scoped authority to request internal information.
- Lifecycle request: `verification:none_or_terminal -> pending`; an equivalent pending verification is not
  duplicated.
- Adjudication/result: the act may be admitted, delayed, rejected, failed, or superseded; a multi-category request
  may be partial. Any later assessment is a separately delivered observation.
- Message: none; the internal process is environment-owned in this two-role model.
- The Agent may not declare information obtained or accurate.

### `seek_institutional_authorization`

- Commitments: `DC-KT-01`, `DC-KT-02`.
- Required parameters: `authorization_request_id:stable_id`, `scope_id:stable_id`,
  `supporting_information_status:enum{missing,incomplete,adequate_for_scope,disputed,unknown}`.
- Optional parameter: `proposal_id:stable_id`.
- Observations: `corporate_authorization`, `internal_liquidity_assessment`, `withdrawal_pressure`.
- Authority: ordinary authority to request a governance decision; not authority for the material act itself.
- Lifecycle request: `corporate_authorization:not_requested_or_unknown -> pending`.
- Adjudication/result: admission opens or continues the scoped request only; authorization, denial, expiry, or
  supersession is a later governance result.
- Message: none while governance remains an environment-owned internal process.
- The Agent may not declare authorization granted.

### `prepare_information_package`

- Commitments: `DC-KT-01`, `DC-KT-02`.
- Required parameters: `package_id:stable_id`, `information_category_ids:stable_id[]`,
  `disclosure_scope_id:stable_id`, `as_of:time_value`.
- Optional parameter: `request_id:stable_id`.
- Observations: `collateral_package_status`, `corporate_authorization`,
  `internal_liquidity_assessment`, `asset_liquidity_assessment`.
- Authority: ordinary preparation authority or scoped disclosure authority, according to content.
- Lifecycle request: `information_package:not_prepared_or_unknown -> preparing`.
- Adjudication/result: admission creates/advances preparation; partial may identify accepted categories. Available,
  disputed, failed, or withdrawn package status is a later authoritative process result.
- Message: none; preparation is distinct from disclosure/submission.
- The Agent may not declare the package complete, submitted, accepted, or collateral accepted.

### `submit_support_request`

- Commitment: `DC-KT-02`.
- Required parameters: `request_id:stable_id`, `recipient_id:stable_id`, `channel_id:stable_id`,
  `route_id:stable_id`, `resource_category_id:stable_id`, `withdrawal_condition_ids:stable_id[]`,
  `expiry_time:time_value?`.
- Conditional parameters: either `requested_amount_value:number` plus `requested_amount_unit:stable_id`, or
  `qualitative_bound:enum{amount_unknown,bounded_minimum,bounded_maximum,bounded_range,nonquantified_category_request}`;
  `package_ref_ids:stable_id[]` when prepared/route-required material exists.
- Observations: `internal_liquidity_assessment`, `withdrawal_pressure`, `asset_liquidity_assessment`,
  `collateral_package_status`, `corporate_authorization`, `clearing_channel_status`,
  and `support_request_status`; route-content requirements are carried by the delivered
  `clearing_channel_status` field family rather than an undeclared extra input.
- Authority: scoped corporate authorization is mandatory.
- Lifecycle request: `support_request:none -> prepared`; all five qualitative gates must be closed and no
  business-equivalent request may be unresolved.
- Adjudication/result: accepted/partial may create the bounded request state and admitted content; delayed,
  rejected, failed, or superseded creates no delivery. Delivery, case creation, disposition, and resource result
  are separate later events.
- Message: correlated `request` to `recipient_id`, using `request_id` and `route_id` as correlation fields.
- The Agent may not declare delivery, recipient admissibility, approval, funding, or rescue.

### `request_channel_confirmation`

- Commitments: `DC-KT-02`, `DC-KT-04`.
- Required parameters: `confirmation_request_id:stable_id`, `channel_id:stable_id`,
  `relationship_ref:stable_id`, `relevant_time:time_value`, `recipient_id:stable_id`.
- Observations: `clearing_channel_status`, `delivered_disposition`.
- Authority: ordinary or scoped authority to inquire about the channel.
- Lifecycle request: `channel_confirmation:none_or_terminal -> pending`; no duplicate pending inquiry.
- Adjudication/result: action admission permits the inquiry only; transport and a later authoritative channel
  observation may be delayed, failed, expired, disputed, or delivered independently.
- Message: correlated `query` to the scenario-owned channel endpoint.
- The Agent may not declare the channel active, unchanged, or the message delivered.

### `provide_requested_information`

- Commitment: `DC-KT-03`.
- Required parameters: `request_id:stable_id`, `case_id:stable_id`, `information_item_ids:stable_id[]`,
  `as_of:time_value`, `provenance_ref_ids:stable_id[]`, `disclosure_scope_id:stable_id`,
  `recipient_id:stable_id`.
- Observations: `received_information_request`, `collateral_package_status`, `corporate_authorization`,
  `support_request_status`.
- Authority: scoped disclosure authorization is mandatory; only a delivered information request activates it.
- Lifecycle request: create one response linked to the existing request/case.
- Adjudication/result: accepted/partial identifies material admitted for disclosure; delayed/rejected/failed leaves
  the case request unresolved. Delivery and recipient classification are later events.
- Message: correlated `inform` using request and case IDs.
- The Agent may not declare the material complete/favorable, review complete, or support approved.

### `request_status_clarification`

- Commitment: `DC-KT-03`.
- Required parameters: `clarification_request_id:stable_id`, `request_id:stable_id`,
  `status_question_id:stable_id`, `as_of:time_value`, `recipient_id:stable_id`.
- Observations: `support_request_status`, `delivered_disposition`.
- Authority: ordinary or scoped case-inquiry authority.
- Lifecycle request: `status_clarification:none_or_terminal -> pending`, only after a declared interval or
  material ambiguity; no duplicate pending clarification.
- Adjudication/result: admission permits the inquiry; transport and any later status/disposition response remain
  separate and may fail, expire, be delayed, or be disputed.
- Message: correlated `query`.
- The Agent may not declare review completion or a changed result.

### `revise_or_withdraw_request`

- Commitment: `DC-KT-03`.
- Required parameters: `request_id:stable_id`, `operation:enum{revise,withdraw}`, `scope_id:stable_id`,
  `reason_code:stable_id`, `recipient_id:stable_id`.
- Observations: `support_request_status`, `corporate_authorization`, `delivered_disposition`.
- Authority: scoped corporate authorization is mandatory.
- Lifecycle request: `withdraw` requests transition of the current nonterminal request to `withdrawn`; `revise`
  requests an incremented successor request version in `prepared`, linked to the prior version. Request identity
  and history remain, and acknowledgement/transport are separate.
- Adjudication/result: accepted/partial applies only the identified revision or withdrawal scope; rejection,
  delay, failure, or supersession preserves the prior authoritative request version. Downstream acknowledgement
  and case handling are later events.
- Message: correlated `notify`.
- The Agent may not declare downstream cancellation, acknowledgement, or that the request already changed.

### `issue_institutional_communication`

- Commitment: `DC-KT-04`.
- Required parameters: `communication_act_id:stable_id`, `audience_id:stable_id`,
  `bounded_claim_id:stable_id`, `basis_ref_ids:stable_id[]`, `effective_time:time_value`.
- Observations: `delivered_disposition`, `clearing_channel_status`, `corporate_authorization`,
  `operational_posture`.
- Authority: scoped communication authority; claim must match delivered basis.
- Lifecycle request: an institutional communication act is issued; public/fanout communication requires a
  separate fanout plan with one MessageIntent per recipient.
- Adjudication/result: action admission establishes only the bounded issuing act; transport may be accepted,
  delayed, expired, prohibited, duplicate, or failed. Audience response and operational effects remain external.
- Message: correlated `inform`.
- The Agent may not declare delivery, restored confidence, stopped withdrawals, or an operational result.

### `prepare_operational_contingency`

- Commitments: `DC-KT-01`, `DC-KT-03`, `DC-KT-04`.
- Required parameters: `contingency_id:stable_id`, `preparation_class_id:stable_id`, `scope_id:stable_id`,
  `revisit_trigger_id:stable_id`.
- Observations: `withdrawal_pressure`, `internal_liquidity_assessment`, `clearing_channel_status`,
  `delivered_disposition`, and `corporate_authorization`.
- Persistent participant state: `operational_posture`.
- Authority: scoped preparation authority.
- Lifecycle request: `operational_posture:ordinary_or_prior -> contingency_prepared`.
- Adjudication/result: admission/partial may update only the named preparation posture; delay, rejection, failure,
  or supersession has no execution effect. Any restriction, suspension, or closure requires a later authoritative
  result.
- Message: none unless a separate communication intent is emitted.
- The Agent may not declare restriction, suspension, closure, or contingency execution.

### `request_result_clarification`

- Commitment: `DC-KT-04`.
- Required parameters: `clarification_request_id:stable_id`, `request_id:stable_id`, `result_ref:stable_id`,
  `ambiguity_code:stable_id`, `question_id:stable_id`, `recipient_id:stable_id`.
- Observations: `delivered_disposition`, `support_request_status`, `clearing_channel_status`.
- Authority: ordinary or scoped result-inquiry authority.
- Lifecycle request: `result_clarification:none_or_terminal -> pending`.
- Adjudication/result: admission permits an inquiry only; transport and any later clarification/correction result
  are separate. The prior result remains authoritative until a successor result is delivered.
- Message: correlated `query`.
- The Agent may not reverse the prior result or declare a new one delivered.

## 4. New York Clearing House registry

### `record_and_classify_request`

- Commitment: `DC-NYCH-01`.
- Required parameters: `case_id:stable_id`, `source_request_id:stable_id`, `sender_id:stable_id`,
  `channel_id:stable_id`, `represented_institution_id:stable_id`, `relationship_ref:stable_id`,
  `route_class:enum{member_facility,nonmember_clearing_matter,other_identified_route,unresolved}`,
  `unresolved_field_ids:stable_id[]`.
- Conditional parameter: `facility_id:stable_id` when the route names a facility.
- Observations: `delivered_request`, `relationship_status`, `route_classification`, `facility_eligibility`,
  `request_authorization_evidence`.
- Authority: competent intake/classification interface.
- Lifecycle request: `case:received -> classified`; one case per business-equivalent request.
- Adjudication/result: accepted/partial records only supported classification fields and preserves unresolved
  ones; delayed/rejected/failed/superseded does not establish eligibility, authority, or support.
- Message: none.
- The Agent may not declare request acceptance, support availability, or resource effect.

### `request_case_information`

- Commitments: `DC-NYCH-01`, `DC-NYCH-02`, `DC-NYCH-04`, `DC-NYCH-05`.
- Required parameters: `information_request_id:stable_id`, `case_id:stable_id`,
  `information_category_ids:stable_id[]`, `required_as_of:time_value`, `recipient_id:stable_id`,
  `scope_id:stable_id`.
- Observations: `delivered_request`, `request_authorization_evidence`, `financial_information_status`,
  `review_state`, and `case_disposition_status`.
- Authority: competent case interface.
- Lifecycle request: `case:classified_or_reviewing -> awaiting_information`; name the missing item and prevent a
  duplicate pending request.
- Adjudication/result: admission records the information-needed process; transport and later supplied material
  are separate and may be delayed, failed, expired, incomplete, stale, or disputed.
- Message: correlated `request`.
- The Agent may not declare information delivered, complete, favorable, or review complete.

### `open_or_continue_review`

- Commitment: `DC-NYCH-02`.
- Required parameters: `review_act_id:stable_id`, `case_id:stable_id`, `reviewing_interface_id:stable_id`,
  `scope_id:stable_id`,
  `current_information_status:enum{not_received,incomplete,stale,adequate_for_scope,disputed,unknown}`,
  `desired_transition:enum{collecting_information,examining,awaiting_forum,decision_ready,complete}`.
- Observations: `financial_information_status`, `review_state`, `authority_state`.
- Authority: competent review interface.
- Lifecycle request: only a legal transition from the current review state; time/randomness alone cannot advance it.
- Adjudication/result: accepted/partial applies only the validated review transition/scope; delay, rejection,
  failure, or supersession cannot be read as review completion or case disposition.
- Message: none.
- The Agent may not declare review complete or a decision made merely by emitting the intent.

### `seek_procedural_authority`

- Commitments: `DC-NYCH-01`, `DC-NYCH-02`, `DC-NYCH-03`.
- Required parameters: `authority_request_id:stable_id`, `case_or_proposal_id:stable_id`, `route_id:stable_id`,
  `authority_question_id:stable_id`, `proposed_forum_id:stable_id`.
- Observations: `route_classification`, `facility_eligibility`, `review_state`, and `authority_state`.
- Authority: ordinary authority to request a scoped forum decision; the proposed forum must be evidenced or bound
  by the selected structural scenario.
- Lifecycle request: unresolved/disputed authority enters forum pending.
- Adjudication/result: admission opens/continues the scoped authority question; later authorization, denial,
  dispute, or absence of a competent forum is an authoritative governance result.
- Message: none while the forum is environment-owned.
- The Agent may not grant authority or establish universal prohibition.

### `seek_member_or_association_authorization`

- Commitment: `DC-NYCH-04`.
- Required parameters: `authorization_request_id:stable_id`, `proposal_id:stable_id`, `forum_id:stable_id`,
  `commitment_class_id:stable_id`, `condition_ids:stable_id[]`.
- Observations: `authority_state`, `review_state`, `financial_information_status`, and
  `resource_proposal_status`.
- Authority: the sensitivity variant and a competent collective forum are mandatory.
- Lifecycle request: collective authorization enters pending; no duplicate vote/commitment process.
- Adjudication/result: admission opens/continues the scoped collective process; later authorization, denial,
  failed formation, or supersession does not itself commit member resources.
- Message: none while members/association remain environment-owned processes.
- The Agent may not declare member agreement, resource commitment, or proposal execution.

### `refer_request`

- Commitments: `DC-NYCH-01`, `DC-NYCH-02`, `DC-NYCH-03`, `DC-NYCH-05`.
- Required parameters: `referral_id:stable_id`, `case_id:stable_id`, `referral_basis_id:stable_id`,
  `recipient_id:stable_id`, `receiving_route_id:stable_id`.
- Observations: `route_classification`, `authority_state`, `case_disposition_status`, and
  `case_communication_status`.
- Authority: competent issuing interface plus an evidenced receiving route.
- Lifecycle request: case disposition becomes scoped referral without automatically closing the original case.
- Adjudication/result: accepted/partial records the supported referral scope; transport, recipient acceptance,
  assistance, and original-case closure remain later independent events.
- Message: correlated `refer`.
- The Agent may not declare recipient acceptance or assistance.

### `issue_typed_decline`

- Commitments: `DC-NYCH-03`, `DC-NYCH-05`.
- Required parameters: `decline_act_id:stable_id`, `case_id:stable_id`,
  `reason_code:enum{facility_ineligible,no_competent_authority,insufficient_information,not_approved,other_supported_reason}`,
  `facility_or_route_scope_id:stable_id`, `issuing_authority_ref:stable_id`, `recipient_id:stable_id`.
- Observations: `facility_eligibility`, `route_classification`, `authority_state`, and
  `case_disposition_status`.
- Authority: competent scoped issuing authority.
- Lifecycle request: case disposition becomes a scoped decline.
- Adjudication/result: accepted/partial records only the validated facility/route scope and reason; delay,
  rejection, failure, or supersession creates no communicated decline. Delivery and closure remain separate.
- Message: correlated `decline`.
- The Agent may not declare all routes prohibited, requester failure, message delivery, or automatic case closure.

### `propose_conditioned_measure`

- Commitment: `DC-NYCH-04`.
- Required parameters: `proposal_id:stable_id`, `case_id:stable_id`, `authorized_route_id:stable_id`,
  `scope_id:stable_id`, `condition_ids:stable_id[]`,
  `collateral_or_information_requirement_ids:stable_id[]`, `requested_commitment_ids:stable_id[]`,
  `expiry_time:time_value`, `recipient_id:stable_id`.
- Observations: `financial_information_status`, `review_state`, `authority_state`,
  `resource_proposal_status`, and `route_classification`.
- Authority: sensitivity variant, competent alternative route, and scoped authorization are mandatory.
- Lifecycle request: create/advance a conditioned proposal; proposal remains separate from commitment/execution.
- Adjudication/result: accepted/partial records only admitted proposal terms; delay, rejection, failure, or
  supersession creates no commitment. Member/collateral decisions, scheduling, execution, and resource results
  are separate later events.
- Message: correlated `propose`.
- The Agent may not declare member commitment, accepted collateral, scheduled execution, transferred resources, or
  system stabilization.

### `communicate_case_status`

- Commitments: all five NYCH commitments.
- Required parameters: `communication_act_id:stable_id`, `case_id:stable_id`,
  `case_disposition_ref:stable_id`, `procedural_state:stable_id`, `issuing_authority_ref:stable_id`,
  `audience_id:stable_id`, `effective_time:time_value`.
- Observations: `case_disposition_status`, `case_communication_status`, `review_state`, `authority_state`, and
  `delivered_case_result` as relevant.
- Authority: competent scoped issuing authority; communicated content must match the authoritative disposition.
- Lifecycle request: `case_communication:not_issued_or_terminal_failure -> issued`.
- Adjudication/result: action admission validates the truthful bounded issuing act; transport may be accepted,
  delayed, expired, prohibited, duplicate, or failed. Delivery cannot alter the case disposition or result.
- Message: correlated `inform`, one recipient per V1 MessageIntent.
- The Agent may not declare delivery, counterparty acceptance, changed case result, or resource effect.

### `close_or_reopen_review`

- Commitment: `DC-NYCH-05`.
- Required parameters: `review_act_id:stable_id`, `case_id:stable_id`,
  `operation:enum{close,reopen}`, `reason_code:stable_id`, `authority_ref:stable_id`.
- Conditional parameter: `new_event_ref:stable_id`, mandatory for reopening.
- Observations: `case_disposition_status`, `case_communication_status`, `delivered_case_result`,
  `review_state`, and `authority_state`.
- Authority: scoped review-transition authority.
- Lifecycle request: complete/closed review becomes closed or reopens through a successor version.
- Adjudication/result: accepted/partial applies only the validated close/reopen scope; delay, rejection, failure,
  or supersession leaves the current review/case version authoritative. External processes and outcomes remain
  unchanged.
- Message: none; outward notice requires a separate `communicate_case_status` intent.
- The Agent may not cancel an external process, erase history, or change an outcome.

## 5. Registry-level completeness

```text
Knickerbocker intents=11
NYCH intents=10
total unique semantic intents=21
unregistered Definition intents=0
registry-only invented intents=0
```

All twenty-one entries have a Definition consumer, parameter contract, observation/authority boundary,
lifecycle request, message rule, and forbidden self-result. The registry does not select policy among multiple
conforming intents; Decision Commitments retain that authority.
