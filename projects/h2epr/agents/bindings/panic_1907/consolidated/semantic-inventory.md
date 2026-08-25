# H2EPR-0288 consolidated semantic inventory

> `ACCEPTED_SEMANTIC_INVENTORY / NON_EXECUTABLE`

## 1. Fixed input and counting rule

- Release: `H2EPR-0288-ROSTER-DEFINITION-RELEASE-v0.1`
- Release commit: `e0cb20724db7c8f15cf344a161ab2f2b2721c1f0`
- Release tree: `74d16ad177ff486eb5966c070c835f8c42de37ab`
- Release manifest SHA-256:
  `a03188f8a3ef45c500fa49ddd4230b99999c9b6759bf3cae73bf8040e0e73ec6`
- Release `SHA256SUMS` SHA-256:
  `5249a21d04d57e275bea83b32bd0e2fb6aef58c8fd9bc36bf47a07ace90b9899`

The release manifest, the 26 recorded assets and their hashes passed at Goal
entry. All inventory content below is resolved from the fixed Git tree rather
than from a mutable working-tree path.

The release contains twelve semantic products: seven Agent Definitions and
five population models. A product is a semantic authority, not necessarily a
runtime actor. Counts below are placements in released products; repeated
semantic labels remain separate placements until capability-qualified mapping
is applied.

| Measure | Count |
|---|---:|
| semantic products | 12 |
| Agent Definitions | 7 |
| population models | 5 |
| Decision/Population Commitments | 62 |
| observation placements | 115 |
| distinct reader-facing observation IDs | 103 |
| intent placements | 107 |
| distinct reader-facing intent IDs | 98 |

`communication_posture` in the Lincoln Definition is private decision state,
not a seventh observation; the Lincoln observation count is therefore six.

## 2. Product inventory and runtime disposition

The capability identifiers below are proposed mapping identifiers. They do not
rename or amend the released semantic products.

| Product | Version | Proposed capability ID | Observations | Commitments | Intents | Runtime disposition |
|---|---|---|---:|---:|---:|---|
| Knickerbocker Trust | 0.2.1 | `knickerbocker_trust` | 9 | 4 | 11 | one named endogenous actor |
| New York Clearing House | 0.2.1 | `new_york_clearing_house` | 12 | 5 | 10 | one named endogenous procedural actor |
| National Bank of Commerce | 0.1.0 | `national_bank_of_commerce` | 12 | 4 | 15 | one named endogenous actor with credit, intermediation and clearing capabilities |
| J. Pierpont Morgan | 0.1.0 | `j_pierpont_morgan` | 9 | 6 | 10 | one natural-person actor; authority and controlled resources remain scoped |
| Trust Company of America | 0.1.0 | `trust_company_of_america` | 9 | 6 | 14 | one named endogenous actor |
| Lincoln Trust Company | 0.1.0 | `lincoln_trust_company` | 6 | 4 | 7 | one named endogenous actor for the bounded communication interface |
| Trust Company Presidents Committee | 0.1.0 | `trust_presidents_committee` | 10 | 6 | 8 | one aggregate procedural actor; no ownership of contributors' resources |
| Knickerbocker depositor population | 0.1.0 | `knickerbocker_depositor` | 7 | 5 | 3 | one or more scenario-declared weighted choice units hosted by Knickerbocker |
| Member/correspondent bank resource decisions | 0.1.0 | `bank_resource_decision` | 9 | 6 | 8 | institution-preserving weight-one units; compose with an existing institution actor when identities coincide |
| Later trust depositor populations | 0.1.0 | `later_trust_depositor` | 9 | 5 | 3 | host-scoped weighted choice units, never one cross-host wallet |
| Call-money lenders | 0.1.0 | `call_money_lender` | 13 | 5 | 8 | institution-preserving lender units; capability may compose with a bank actor |
| Call-money broker-borrowers | 0.1.0 | `call_money_broker_borrower` | 10 | 6 | 10 | institution-preserving borrowing units with controlled collateral and repayment authority |

Runtime materialization therefore cannot use `one product = one
ParticipantArtifact`. One historical/legal entity has one resource owner and
one endogenous actor identity. Multiple released capabilities may be composed
under that actor without duplicating its balance sheet, authority or
relationships.

## 3. Observation inventory

### 3.1 Released observations by capability

| Capability | Reader-facing observation IDs |
|---|---|
| `knickerbocker_trust` | `internal_liquidity_assessment`; `withdrawal_pressure`; `asset_liquidity_assessment`; `collateral_package_status`; `corporate_authorization`; `clearing_channel_status`; `support_request_status`; `received_information_request`; `delivered_disposition` |
| `new_york_clearing_house` | `delivered_request`; `relationship_status`; `route_classification`; `facility_eligibility`; `request_authorization_evidence`; `financial_information_status`; `review_state`; `authority_state`; `resource_proposal_status`; `case_disposition_status`; `case_communication_status`; `delivered_case_result` |
| `national_bank_of_commerce` | `clearing_relationship_status`; `clearing_exposure_record`; `credit_exposure_record`; `participant_review_notice`; `counterparty_condition_information`; `counterparty_request`; `nbc_corporate_authority`; `nych_clearing_direction`; `nych_request_disposition`; `incremental_recovery_assessment`; `message_and_notice_status`; `delivered_credit_or_relationship_result` |
| `j_pierpont_morgan` | `delivered_coordination_matter`; `case_information_status`; `independent_report_status`; `represented_authority`; `participant_roster_and_roles`; `proposal_record`; `delivered_commitment_reply`; `delivered_coordination_result`; `dated_relationship_record` |
| `trust_company_of_america` | `participant_condition_notice`; `company_condition_information`; `governance_authority`; `examination_request_or_result`; `support_route_state`; `collateral_control_information`; `service_condition`; `communication_matter`; `delivered_case_result` |
| `lincoln_trust_company` | `condition_statement_proposal`; `lincoln_condition_information`; `communication_decision_authority`; `statement_authorization_state`; `message_lifecycle`; `material_information_update` |
| `trust_presidents_committee` | `committee_mandate`; `case_type_review_standard`; `assistance_application`; `case_information_package`; `examination_status_or_report`; `reporting_opportunity`; `delivered_continuity_assessment`; `coordination_authority`; `contributor_reply`; `process_disposition_or_result` |
| `knickerbocker_depositor` | `remaining_claim`; `private_withdrawal_need`; `institution_signal`; `service_access_observation`; `peer_activity_observation`; `own_request_status`; `own_request_result` |
| `bank_resource_decision` | `institution_profile`; `decision_authority`; `own_resource_envelope`; `solicitation_or_request`; `applicant_information`; `facility_state`; `own_collateral_projection`; `commitment_or_application_state`; `relationship_or_exposure_observation` |
| `later_trust_depositor` | `host_institution`; `remaining_claim`; `private_withdrawal_need`; `host_signal`; `public_contagion_signal`; `service_access_observation`; `peer_activity_observation`; `own_request_status`; `own_request_result` |
| `call_money_lender` | `institution_profile`; `decision_authority`; `own_resource_envelope`; `own_liquidity_need`; `existing_call_loan`; `contractual_status`; `borrower_request`; `borrower_information`; `collateral_projection`; `term_assessment_basis`; `market_or_pool_route`; `market_observation`; `own_loan_lifecycle` |
| `call_money_broker_borrower` | `borrower_profile`; `decision_authority`; `call_obligation`; `controlled_resource_projection`; `funding_route`; `collateral_package`; `settlement_obligation`; `funding_offer`; `own_business_lifecycles`; `market_observation` |

### 3.2 Interface-family consolidation

| Family | Material concepts | Mapping requirement |
|---|---|---|
| identity and institutional position | participant, host, membership, roster, role, relationship | stable entity and relationship references with effective time |
| authority and governance | corporate, committee, association, contribution, communication and repayment authority | authoritative record reference, scope, state and version; `unknown` grants nothing |
| resources and exposures | liquidity, claim, credit, collateral, controlled resource, call loan, settlement obligation | owner, controller, quantity/unit or qualitative envelope, `as-of`, uncertainty and state version |
| requests, cases and proposals | support request, examination, solicitation, application, offer and coordination plan | stable business-object reference plus lifecycle state; delivery never implies acceptance |
| information and assessment | condition, dossier, report, eligibility, term basis and recovery assessment | provenance, participant-available time, freshness, scope and missing/disputed state |
| relationship and service | clearing, host, support route, market route, service access | relationship object, parties, effective interval and authoritative status |
| message and delivery | notice, statement, request, reply, case status | issue, transport, delivery, receipt and business consequence remain separate |
| result and feedback | disposition, execution, payment, booking, failure and partial effect | typed disposition/result reference, reason and state version |
| population-only private input | withdrawal need, response profile, liquidity need and disclosed posture | pre-run configuration or delivered private event; never public world truth |

Eleven reader-facing observation IDs are reused across products. Reuse does
not establish an identical domain. For example, `decision_authority` is scoped
separately to bank-resource, lender and broker-borrower capabilities. The
mapping catalog must therefore key observations by `(capability_id,
observation_id)` before projecting them into an actor's combined envelope.

## 4. Private state and authoritative state

### 4.1 Actor-owned, replayable decision state

| Capability | Behaviorally material private state |
|---|---|
| `knickerbocker_trust` | last verified condition time; `operational_posture`; request-strategy posture; last consumed authoritative references |
| `new_york_clearing_house` | procedural-assessment posture; last consumed record versions |
| `national_bank_of_commerce` | exposure-review posture; intermediation posture; communication posture; last consumed record versions |
| `j_pierpont_morgan` | `coordination_posture`; `last_consumed_record_versions` |
| `trust_company_of_america` | `institutional_response_posture`; last-consumed versions |
| `lincoln_trust_company` | `communication_posture`; last-consumed versions |
| `trust_presidents_committee` | declared information inventory and bounded decision posture over authoritative case, report, plan and reply references |
| `knickerbocker_depositor` | withdrawal need; response profile; dated information inventory; last-consumed request/result references |
| `bank_resource_decision` | participation posture; information inventory; last-consumed offer, application and resource-projection versions |
| `later_trust_depositor` | private need; response profile/conflict rule; dated information inventory; last-consumed request/result references |
| `call_money_lender` | lender and accommodation postures; term-compatibility assessment; information inventory; last-consumed lifecycle/resource versions |
| `call_money_broker_borrower` | response posture; information inventory; last-consumed obligation, request, offer, collateral and result versions |

Every state that can alter a later choice must be declared, reducer-committed,
versioned and replayable. Backend-local persistent memory is not an admissible
carrier.

### 4.2 Environment-owned business truth

The following remain authoritative scenario/reducer state even when an actor
retains a private reference or assessment:

- case/request, proposal, offer, application and solicitation identity;
- corporate, committee, association and contributor authorization;
- relationship, membership, clearing and service status;
- balances, claims, exposure, collateral control, commitments and resources;
- review, examination, matching, booking, payment and settlement state;
- message issue, transport, delivery and receipt;
- action disposition, business result and world-state effect.

An actor may remember the last delivered version and may form a declared
assessment. It may not maintain a competing copy of business truth.

## 5. Intent inventory

### 5.1 Released intent placements by capability

| Capability | Reader-facing semantic intent IDs |
|---|---|
| `knickerbocker_trust` | `verify_internal_condition`; `seek_institutional_authorization`; `prepare_information_package`; `submit_support_request`; `request_channel_confirmation`; `provide_requested_information`; `request_status_clarification`; `revise_or_withdraw_request`; `issue_institutional_communication`; `prepare_operational_contingency`; `request_result_clarification` |
| `new_york_clearing_house` | `record_and_classify_request`; `request_case_information`; `open_or_continue_review`; `seek_procedural_authority`; `seek_member_or_association_authorization`; `refer_request`; `issue_typed_decline`; `propose_conditioned_measure`; `communicate_case_status`; `close_or_reopen_review` |
| `national_bank_of_commerce` | `verify_nbc_exposure`; `request_counterparty_information`; `seek_nbc_authority`; `propose_credit_posture`; `limit_or_decline_additional_credit`; `seek_intermediation_clarification`; `forward_request_with_provenance`; `sponsor_or_represent_request`; `decline_intermediation`; `request_nych_direction_clarification`; `confirm_clearing_continuation`; `propose_relationship_condition`; `issue_clearing_termination_notice`; `communicate_nbc_position`; `request_delivery_or_result_clarification` |
| `j_pierpont_morgan` | `classify_coordination_matter`; `request_case_information`; `request_independent_examination`; `convene_coordination_session`; `form_or_revise_coordination_proposal`; `solicit_independent_commitment`; `assemble_coordination_plan`; `communicate_coordination_position`; `decline_or_close_coordination_role`; `request_commitment_or_result_clarification` |
| `trust_company_of_america` | `verify_institutional_condition`; `consent_to_scoped_examination`; `provide_scoped_case_information`; `request_information_or_terms`; `open_or_update_support_request`; `propose_collateral_package`; `withdraw_or_close_support_route`; `propose_operational_capacity_change`; `authorize_operational_posture`; `authorize_condition_statement`; `issue_authorized_condition_statement`; `narrow_or_withhold_condition_statement`; `authorize_correction_or_update`; `close_or_pause_institutional_matter` |
| `lincoln_trust_company` | `request_condition_information`; `authorize_condition_statement`; `narrow_or_withhold_condition_statement`; `issue_authorized_condition_statement`; `authorize_correction_or_update`; `request_message_delivery_clarification`; `close_communication_matter` |
| `trust_presidents_committee` | `open_or_refer_assistance_case`; `request_case_information`; `request_scoped_examination`; `issue_case_recommendation`; `report_case_status`; `solicit_independent_contribution`; `assemble_or_revise_support_plan`; `await_case_or_plan_result` |
| `knickerbocker_depositor` | `request_withdrawal`; `retain_for_interval`; `await_request_result` |
| `bank_resource_decision` | `request_proposal_information`; `refer_or_decline_proposal`; `make_conditional_contribution_offer`; `commit_owned_resource`; `revise_or_cancel_commitment`; `apply_for_member_certificate`; `submit_controlled_collateral`; `await_commitment_or_application_result` |
| `later_trust_depositor` | `request_withdrawal`; `retain_for_interval`; `await_request_result` |
| `call_money_lender` | `request_call_loan_information`; `continue_call_loan_for_interval`; `propose_call_loan_term_change`; `issue_call_or_reduction_notice`; `make_conditional_call_loan_offer`; `decline_call_loan_request`; `revise_or_cancel_call_loan_offer`; `await_call_loan_result` |
| `call_money_broker_borrower` | `request_call_or_term_clarification`; `request_call_loan_renewal_or_replacement`; `submit_controlled_collateral_proposal`; `accept_call_loan_offer`; `request_call_loan_offer_revision`; `decline_call_loan_offer`; `authorize_controlled_repayment`; `request_authorized_position_reduction`; `record_funding_inability`; `await_funding_or_repayment_result` |

### 5.2 Intent-name collisions

| Reader-facing ID | Placements |
|---|---:|
| `request_case_information` | 3 |
| `authorize_condition_statement` | 2 |
| `authorize_correction_or_update` | 2 |
| `issue_authorized_condition_statement` | 2 |
| `narrow_or_withhold_condition_statement` | 2 |
| `request_withdrawal` | 2 |
| `retain_for_interval` | 2 |
| `await_request_result` | 2 |

These are not errors in the release. They show that reader-facing semantic IDs
are local to a capability. A machine action identifier must be
capability-qualified; a global registry keyed only by the reader-facing ID
would silently assign several distinct definitions to one action.

### 5.3 Intent interface families

| Family | Examples | Required separation |
|---|---|---|
| inspect/classify | verify condition or exposure; classify request, case or route | classification record is not later authorization |
| request information/examination | request case, counterparty, condition, loan or examination information | request, delivery, freshness and finding are separate |
| seek authority | corporate, committee, member or association authority | Agent request is not authority granted |
| form request/proposal/offer | support request, collateral package, coordination plan, contribution or loan offer | proposal is not commitment, match, booking or transfer |
| communicate/notify | position, statement, status, call, termination or correction | issue, delivery, receipt and business effect are separate |
| accept/decline/refer/withdraw | typed decision over one scoped object/version | scoped decision cannot assert every alternative is unavailable |
| commit/authorize controlled resources | contribution, repayment or position reduction | actor must own or control the offered resource; reducer realizes effect |
| wait/retain/continue | pending result, retained claim or continuing loan | explicit bounded choice with revisit event, not indefinite no-op |
| close/reopen/revise | case, request, proposal, offer or communication matter | lineage is preserved; closure does not erase prior records |

## 6. Consolidated lifecycle inventory

The 107 placements reduce to reusable business-process families. Each object
has a stable identity, owner, version, current state, predecessor/supersession
links and terminal conditions.

| Lifecycle family | Minimum stages or tracks | Principal capabilities |
|---|---|---|
| governance and authority | identify forum; request; pending; authorized/denied/disputed; superseded/expired | all named institutions, Morgan, committee, bank/lender/borrower units |
| information and examination | request; delivery; receipt; scope/freshness review; examination; report; dispute/correction; closure | NYCH, NBC, Morgan, TCA, Lincoln, committee, resource/lending units |
| support/request case | form; authorize; transmit; receive; classify; review; disposition; communicate; close/reopen | Knickerbocker, NBC, NYCH, TCA, committee |
| proposal/plan | draft; version; circulate; revise; withdraw; authorize; solicit; assemble; expire/close | Morgan, NYCH, committee, TCA |
| solicitation and independent reply | issue per recipient; delivery; reply; validate; revise/cancel; expire | Morgan, committee, bank resource units |
| resource commitment and execution | offer; reserve; commit; schedule; execute; partial/no-effect/fail; release | banks, trusts, NYCH/member route, Morgan plans |
| credit exposure | existing exposure; review; proposed posture; booking/adjustment; repayment; close | NBC and counterparty |
| clearing relationship and notice | active/restricted; condition proposed; notice issue/delivery; effective termination/correction | NBC, Knickerbocker, NYCH/scenario |
| institutional communication | proposal; authorization; issue; transport; delivery; correction; expiry/close | Lincoln, TCA, NBC, NYCH, Morgan |
| withdrawal/service/payment | choice; request; queue/service; partial/full payment; alternate form; failure/expiry; claim update | depositor units and host trusts |
| collateral and facility application | package/application; submission; review; decision; booking/issue; release | banks, lenders, borrowers, trusts, NYCH facilities |
| call-loan contract | active loan; review; term proposal/call; notice; borrower response; repayment/default/close | lender and broker-borrower units |
| replacement funding | request; offer; revision; acceptance; matching; booking; transfer; repayment; close | lenders, broker-borrowers and scenario venue |
| position reduction and venue execution | authorization; order/request; venue adjudication; trade; settlement; realized proceeds | broker-borrowers and scenario-owned NYSE process |

Action admission, message transport, business disposition, execution result and
state delta are orthogonal tracks. One generic `accepted` value cannot replace
these lifecycle states.

## 7. Identity, authority and resource inventory

### 7.1 Required identity layers

| Identity | Meaning |
|---|---|
| historical/legal entity | owns relationships, resources, obligations and institutional history |
| runtime actor | one endogenous decision interface and one ParticipantArtifact |
| capability | one released Definition/population policy surface composed into an actor |
| population unit | scenario-declared choice unit, host/institution identity and weight |
| business object | request, case, proposal, message, loan, obligation, offer, commitment or result |

One entity may have several capabilities but may not receive duplicate resource
accounts or competing authority records. Population models are semantic
factories: they do not authorize a single shared wallet or a common private
observation.

### 7.2 V1 representation projection

- Named endogenous institutions, Morgan and the committee project to
  `autonomous_participant_agent` because they make endogenous choices; the
  enum does not imply a natural-person model.
- A standalone unit instantiated from a population model projects to
  `aggregate_population_agent`, with its unit identity and weight retained.
- If a named endogenous actor also receives a population-derived capability,
  the capability is composed into its existing ParticipantArtifact; the
  existing actor representation remains authoritative.
- The NYSE and other scenario-owned institutional mechanics are not promoted
  to an Agent merely to obtain a carrier. Where an environment participant is
  needed, V1 already provides `institutional_environment_agent`.

### 7.3 Authority and resource invariants

1. An intent's actor, claimed authority, target and resource owner must resolve
   to compatible entity and process versions.
2. A committee, NYCH or Morgan coordination plan never becomes ownership of
   member, firm or contributor resources.
3. A population capability can offer only resources controlled by its
   instantiated unit.
4. Collateral proposal, validation, acceptance, encumbrance and release are
   distinct.
5. A result updates one canonical resource/exposure state through the reducer;
   actors consume the delivered version later.

## 8. Scenario-owned semantic requirements

The release requires the scenario/environment to own:

- the event clock, phase transitions and participant-time information filter;
- historical identities, membership, host and relationship intervals;
- authoritative resources, exposures, collateral, commitments and access;
- message routes, fanout, delay, delivery and failure;
- requests, reviews, authority processes, proposal and result lifecycles;
- withdrawal service, payment form and host-institution account effects;
- NYSE venue, matching, rate, collateral, trading and settlement mechanics;
- the Knickerbocker → NBC → NYCH two-hop lineage;
- explicit exogenous Treasury public deposits;
- United Copper and affiliated-bank distress as initial/exogenous history;
- structural variants, including the selected NYCH alternative-route model,
  NBC termination provenance and any committee/resource-pool policy.

The selected structural variants are system-only run inputs. Agents receive
only their resulting, legally and temporally admissible observations.

## 9. Inventory findings

1. The release is semantically complete enough to enter consolidated mapping:
   all twelve products expose observation, state, intent, authority, resource
   and result boundaries.
2. Product count is not actor count. Identity composition is mandatory before
   any ParticipantArtifact can be generated.
3. Reader-facing intent and observation IDs are capability-local. The current
   two-role mapping's global one-ID/one-actor assumption cannot be extended
   unchanged.
4. Compound records must be projected as canonical atomic RuntimeFields plus
   stable object/version references; a reference may not hide a live WorldState
   dereference.
5. The event requires richer internal registries and scenario semantics, but
   the inventory exposes no concrete requirement that V1 cannot carry.
6. No behavior, role or historical fact has been added by this inventory.
