# H2EPR-0288 Scenario interface closure

> Accepted companion `0.1.0` · complete semantic reconciliation ·
> no executable configuration or historical-validity claim

## 1. Closure identity and inputs

| Field | Value |
|---|---|
| Event and scenario | `H2EPR-0288`; `h2epr.scenario.0288.panic_1907@0.1.0` |
| Participant semantic input | `H2EPR-0288-ROSTER-DEFINITION-RELEASE-v0.1`; manifest SHA-256 `a03188f8a3ef45c500fa49ddd4230b99999c9b6759bf3cae73bf8040e0e73ec6` |
| Evidence/time boundary | event evidence ledger SHA-256 `5314f7cd526586be824ba330cba566170d725499a42a4635d475ad5186e4d933`; all focal outcomes `FULL_DRAFT_EXPOSED` |
| Consolidated mapping | `H2EPR-0288-CONSOLIDATED-MAPPING-v0.1`; manifest SHA-256 `d2aef35116df2df5f99cad7d0cdd69136e8c8e5b69261f387ea4cfd301eb72d5` |
| Mapping profile | `h2epr.roster-consolidated-mapping.v0_1`; SHA-256 `efa341364d12f8b1be8035ebd1cdde7b6ef2446f4015db3e28b6f2bdbaab25e7` |
| Carrier | H2EPR Contracts V1; accepted verdict `V1_COMPATIBLE_VIA_CONSOLIDATED_INTERNAL_MAPPING_AND_SCENARIO_SEMANTIC_EXTENSION` |
| Structural baseline | `SV-NYCH-ROUTE=NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`; `SV-NBC-DIRECTION=NO_NYCH_DIRECTION_DELIVERED`; `SV-TPC-RECOMMENDATION=PROCEDURE_CONSERVATIVE`; `SV-POOL-OWNERSHIP=INDEPENDENT_RESOURCE_OWNERS`; Morgan personal baseline and relationship sensitivity disabled |
| Review state | substantive review passed; `OD-SC-01` through `OD-SC-04` accepted by owner |

### Derived coverage

Counts below are validated by the accepted roster loader, not hand-entered
estimates.

| Measure | Expected | Derived | Status |
|---|---:|---:|---|
| semantic products/capabilities | 12 | 12 | `MATCH` |
| commitments | 62 | 62 | `MATCH` |
| observation placements | 115 | 115 | `MATCH` |
| distinct reader-facing observations | 103 | 103 | `MATCH` |
| intent placements | 107 | 107 | `MATCH` |
| distinct reader-facing intents | 98 | 98 | `MATCH` |
| shared lifecycle families | 13 | 13 | `MATCH` |
| accepted cross-object rules | 34 | 34 | `COVERED` |

## 2. Participant and capability assembly

| Entity or unit pattern | Capability/product | Decision interface | Host/institution | Authority owner | Resource owner | Status |
|---|---|---|---|---|---|---|
| Knickerbocker Trust | `knickerbocker_trust` | one named institutional actor | self | KT governance record | KT canonical ledger | `CLOSED` |
| New York Clearing House | `new_york_clearing_house` | one aggregate procedural actor | association | NYCH governance record | association/member resources stay distinct | `CLOSED` |
| National Bank of Commerce | `national_bank_of_commerce` | one named multi-capability actor | self/NYCH member | NBC governance record | NBC canonical ledger | `CLOSED` |
| J. Pierpont Morgan | `j_pierpont_morgan` | one named personal coordination actor | personal interface | act-level personal/firm record | no direct resource capability in release | `CLOSED` |
| Trust Company of America | `trust_company_of_america` | one named institutional actor | self | TCA governance record | TCA canonical ledger | `CLOSED` |
| Lincoln Trust Company | `lincoln_trust_company` | one narrow communication actor | self | competent forum/statement record | no resource action in capability | `CLOSED` |
| Presidents' committee | `trust_presidents_committee` | one aggregate procedural actor | committee | mandate/coordination record | contributors stay independent | `CLOSED` |
| KT depositor unit | `knickerbocker_depositor` | weighted host-scoped unit | KT | unit request/private-state scope | unit claim/KT account relation | `CLOSED; CONFIG_REQUIRED` |
| later depositor unit | `later_trust_depositor` | weighted host-scoped unit | exactly one trust | unit request/private-state scope | unit claim/host account relation | `CLOSED; CONFIG_REQUIRED` |
| bank resource unit | `bank_resource_decision` | institution-preserving weight-one unit or composed capability | declared institution | institution authority graph | same institution canonical ledger | `CLOSED; CONFIG_REQUIRED` |
| call lender unit | `call_money_lender` | institution-preserving or composed capability | declared institution | institution/loan authority | same institution canonical ledger | `CLOSED; CONFIG_REQUIRED` |
| broker-borrower unit | `call_money_broker_borrower` | authorized firm/member funding interface | declared broker | firm mandate/authority | firm-controlled resource/collateral scope | `CLOSED; CONFIG_REQUIRED` |

`CONFIG_REQUIRED` means that a later executable configuration must choose the
instances, weights, profiles, relationships, and initial projections. It is
not a semantic gap. A same-entity bank-resource/lender assignment composes into
one actor, authority graph, relationship state, and resource owner.

## 3. Observation production and delivery

### Closure codebook

The row catalog uses the following Scenario Definition references:

- `IP-IDENTITY`, `IP-AUTHORITY`, `IP-RELATIONSHIP`, `IP-RESOURCE`,
  `IP-CONDITION`, `IP-REQUEST`, `IP-CASE`, `IP-REPORT`, `IP-PROPOSAL`,
  `IP-REPLY`, `IP-FACILITY`, `IP-COMMUNICATION`, `IP-SERVICE`, `IP-ACCOUNT`,
  `IP-MARKET`, `IP-RESULT`, and `IP-PRIVATE` are the information-product
  families in Scenario Definition §7.
- `R-ACTOR` is actor/institution scoped; `R-PARTY` is one business object's
  parties; `R-HOST` is one host/account population; `R-UNIT` is one
  population unit; `R-PUBLIC` requires issue plus configured public delivery;
  `R-PRIVATE` is unit/actor private.
- `T-RECORD` requires source/as-of/version, delivery before decision, and the
  released missing/stale/disputed fallback. `T-EFFECTIVE` additionally
  enforces relationship/authority effective time. `T-RESULT` permits the
  value only after authoritative result delivery. `T-CONFIG` is a pre-run
  private/system assignment and never public. `T-PUBLIC` separates publication
  from recipient coverage.

Every row is capability-qualified; repeated reader-facing labels are not
merged. `CLOSED` means the scenario supplies an authoritative producer,
projection, route/scope, temporal rule, and accepted carrier path.

### Complete observation-placement catalog

| Capability | Observation | Product/source | Route | Time rule | Status |
|---|---|---|---|---|---|
| `bank_resource_decision` | `institution_profile` | `IP-IDENTITY` | `R-ACTOR` | `T-CONFIG` | `CLOSED` |
| `bank_resource_decision` | `decision_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `bank_resource_decision` | `own_resource_envelope` | `IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `bank_resource_decision` | `solicitation_or_request` | `IP-REQUEST` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `bank_resource_decision` | `applicant_information` | `IP-CONDITION` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `bank_resource_decision` | `facility_state` | `IP-FACILITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `bank_resource_decision` | `own_collateral_projection` | `IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `bank_resource_decision` | `commitment_or_application_state` | `IP-CASE`/`IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `bank_resource_decision` | `relationship_or_exposure_observation` | `IP-RELATIONSHIP`/`IP-RESOURCE` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `call_money_broker_borrower` | `borrower_profile` | `IP-IDENTITY` | `R-ACTOR` | `T-CONFIG` | `CLOSED` |
| `call_money_broker_borrower` | `decision_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `call_money_broker_borrower` | `call_obligation` | `IP-REQUEST`/`IP-ACCOUNT` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `call_money_broker_borrower` | `controlled_resource_projection` | `IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `call_money_broker_borrower` | `funding_route` | `IP-FACILITY`/`IP-RELATIONSHIP` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `call_money_broker_borrower` | `collateral_package` | `IP-PROPOSAL`/`IP-RESOURCE` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `call_money_broker_borrower` | `settlement_obligation` | `IP-ACCOUNT` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `call_money_broker_borrower` | `funding_offer` | `IP-PROPOSAL` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `call_money_broker_borrower` | `own_business_lifecycles` | `IP-CASE`/`IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `call_money_broker_borrower` | `market_observation` | `IP-MARKET` | `R-ACTOR` | `T-PUBLIC` | `CLOSED` |
| `call_money_lender` | `institution_profile` | `IP-IDENTITY` | `R-ACTOR` | `T-CONFIG` | `CLOSED` |
| `call_money_lender` | `decision_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `call_money_lender` | `own_resource_envelope` | `IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `call_money_lender` | `own_liquidity_need` | `IP-RESOURCE`/`IP-PRIVATE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `call_money_lender` | `existing_call_loan` | `IP-ACCOUNT` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `call_money_lender` | `contractual_status` | `IP-ACCOUNT` | `R-PARTY` | `T-EFFECTIVE` | `CLOSED` |
| `call_money_lender` | `borrower_request` | `IP-REQUEST` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `call_money_lender` | `borrower_information` | `IP-CONDITION` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `call_money_lender` | `collateral_projection` | `IP-RESOURCE` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `call_money_lender` | `term_assessment_basis` | `IP-CONDITION` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `call_money_lender` | `market_or_pool_route` | `IP-FACILITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `call_money_lender` | `market_observation` | `IP-MARKET` | `R-ACTOR` | `T-PUBLIC` | `CLOSED` |
| `call_money_lender` | `own_loan_lifecycle` | `IP-CASE`/`IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `j_pierpont_morgan` | `delivered_coordination_matter` | `IP-REQUEST` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `j_pierpont_morgan` | `case_information_status` | `IP-CONDITION` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `j_pierpont_morgan` | `independent_report_status` | `IP-REPORT` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `j_pierpont_morgan` | `represented_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `j_pierpont_morgan` | `participant_roster_and_roles` | `IP-IDENTITY` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `j_pierpont_morgan` | `proposal_record` | `IP-PROPOSAL` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `j_pierpont_morgan` | `delivered_commitment_reply` | `IP-REPLY` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `j_pierpont_morgan` | `delivered_coordination_result` | `IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `j_pierpont_morgan` | `dated_relationship_record` | `IP-RELATIONSHIP` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `knickerbocker_depositor` | `remaining_claim` | `IP-ACCOUNT` | `R-UNIT`/`R-HOST` | `T-RESULT` | `CLOSED` |
| `knickerbocker_depositor` | `private_withdrawal_need` | `IP-PRIVATE` | `R-PRIVATE` | `T-CONFIG` | `CLOSED` |
| `knickerbocker_depositor` | `institution_signal` | `IP-COMMUNICATION` | `R-UNIT` | `T-PUBLIC` | `CLOSED` |
| `knickerbocker_depositor` | `service_access_observation` | `IP-SERVICE` | `R-UNIT`/`R-HOST` | `T-RESULT` | `CLOSED` |
| `knickerbocker_depositor` | `peer_activity_observation` | `IP-SERVICE` | `R-UNIT`/`R-HOST` | `T-RECORD` | `CLOSED` |
| `knickerbocker_depositor` | `own_request_status` | `IP-CASE` | `R-UNIT` | `T-RESULT` | `CLOSED` |
| `knickerbocker_depositor` | `own_request_result` | `IP-RESULT` | `R-UNIT` | `T-RESULT` | `CLOSED` |
| `knickerbocker_trust` | `internal_liquidity_assessment` | `IP-RESOURCE`/`IP-PRIVATE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `knickerbocker_trust` | `withdrawal_pressure` | `IP-SERVICE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `knickerbocker_trust` | `asset_liquidity_assessment` | `IP-RESOURCE`/`IP-PRIVATE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `knickerbocker_trust` | `collateral_package_status` | `IP-PROPOSAL`/`IP-RESOURCE` | `R-ACTOR` | `T-RESULT` | `CLOSED` |
| `knickerbocker_trust` | `corporate_authorization` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `knickerbocker_trust` | `clearing_channel_status` | `IP-RELATIONSHIP` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `knickerbocker_trust` | `support_request_status` | `IP-CASE` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `knickerbocker_trust` | `received_information_request` | `IP-REQUEST` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `knickerbocker_trust` | `delivered_disposition` | `IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `later_trust_depositor` | `host_institution` | `IP-IDENTITY` | `R-UNIT`/`R-HOST` | `T-CONFIG` | `CLOSED` |
| `later_trust_depositor` | `remaining_claim` | `IP-ACCOUNT` | `R-UNIT`/`R-HOST` | `T-RESULT` | `CLOSED` |
| `later_trust_depositor` | `private_withdrawal_need` | `IP-PRIVATE` | `R-PRIVATE` | `T-CONFIG` | `CLOSED` |
| `later_trust_depositor` | `host_signal` | `IP-COMMUNICATION` | `R-UNIT`/`R-HOST` | `T-PUBLIC` | `CLOSED` |
| `later_trust_depositor` | `public_contagion_signal` | `IP-COMMUNICATION` | `R-UNIT` | `T-PUBLIC` | `CLOSED` |
| `later_trust_depositor` | `service_access_observation` | `IP-SERVICE` | `R-UNIT`/`R-HOST` | `T-RESULT` | `CLOSED` |
| `later_trust_depositor` | `peer_activity_observation` | `IP-SERVICE` | `R-UNIT`/`R-HOST` | `T-RECORD` | `CLOSED` |
| `later_trust_depositor` | `own_request_status` | `IP-CASE` | `R-UNIT` | `T-RESULT` | `CLOSED` |
| `later_trust_depositor` | `own_request_result` | `IP-RESULT` | `R-UNIT` | `T-RESULT` | `CLOSED` |
| `lincoln_trust_company` | `condition_statement_proposal` | `IP-PROPOSAL` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `lincoln_trust_company` | `lincoln_condition_information` | `IP-CONDITION` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `lincoln_trust_company` | `communication_decision_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `lincoln_trust_company` | `statement_authorization_state` | `IP-AUTHORITY`/`IP-CASE` | `R-ACTOR` | `T-RESULT` | `CLOSED` |
| `lincoln_trust_company` | `message_lifecycle` | `IP-COMMUNICATION` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `lincoln_trust_company` | `material_information_update` | `IP-CONDITION` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `national_bank_of_commerce` | `clearing_relationship_status` | `IP-RELATIONSHIP` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `national_bank_of_commerce` | `clearing_exposure_record` | `IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `national_bank_of_commerce` | `credit_exposure_record` | `IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `national_bank_of_commerce` | `participant_review_notice` | `IP-CONDITION`/`IP-COMMUNICATION` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `national_bank_of_commerce` | `counterparty_condition_information` | `IP-CONDITION` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `national_bank_of_commerce` | `counterparty_request` | `IP-REQUEST` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `national_bank_of_commerce` | `nbc_corporate_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `national_bank_of_commerce` | `nych_clearing_direction` | `IP-COMMUNICATION`/`IP-AUTHORITY` | `R-PARTY` | `T-EFFECTIVE` | `CLOSED` |
| `national_bank_of_commerce` | `nych_request_disposition` | `IP-CASE`/`IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `national_bank_of_commerce` | `incremental_recovery_assessment` | `IP-CONDITION` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `national_bank_of_commerce` | `message_and_notice_status` | `IP-COMMUNICATION` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `national_bank_of_commerce` | `delivered_credit_or_relationship_result` | `IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `new_york_clearing_house` | `delivered_request` | `IP-REQUEST` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `new_york_clearing_house` | `relationship_status` | `IP-RELATIONSHIP` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `new_york_clearing_house` | `route_classification` | `IP-CASE` | `R-ACTOR` | `T-RESULT` | `CLOSED` |
| `new_york_clearing_house` | `facility_eligibility` | `IP-FACILITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `new_york_clearing_house` | `request_authorization_evidence` | `IP-AUTHORITY` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `new_york_clearing_house` | `financial_information_status` | `IP-CONDITION`/`IP-REPORT` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `new_york_clearing_house` | `review_state` | `IP-CASE` | `R-ACTOR` | `T-RESULT` | `CLOSED` |
| `new_york_clearing_house` | `authority_state` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `new_york_clearing_house` | `resource_proposal_status` | `IP-PROPOSAL`/`IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `new_york_clearing_house` | `case_disposition_status` | `IP-CASE`/`IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `new_york_clearing_house` | `case_communication_status` | `IP-COMMUNICATION` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `new_york_clearing_house` | `delivered_case_result` | `IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `trust_company_of_america` | `participant_condition_notice` | `IP-CONDITION`/`IP-COMMUNICATION` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `trust_company_of_america` | `company_condition_information` | `IP-CONDITION`/`IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `trust_company_of_america` | `governance_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `trust_company_of_america` | `examination_request_or_result` | `IP-REQUEST`/`IP-REPORT`/`IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `trust_company_of_america` | `support_route_state` | `IP-CASE`/`IP-RELATIONSHIP` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `trust_company_of_america` | `collateral_control_information` | `IP-RESOURCE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `trust_company_of_america` | `service_condition` | `IP-SERVICE` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `trust_company_of_america` | `communication_matter` | `IP-PROPOSAL`/`IP-COMMUNICATION` | `R-ACTOR` | `T-RECORD` | `CLOSED` |
| `trust_company_of_america` | `delivered_case_result` | `IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `trust_presidents_committee` | `committee_mandate` | `IP-AUTHORITY`/`IP-IDENTITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `trust_presidents_committee` | `case_type_review_standard` | `IP-CONDITION`/`IP-PRIVATE` | `R-ACTOR` | `T-CONFIG` | `CLOSED` |
| `trust_presidents_committee` | `assistance_application` | `IP-REQUEST` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `trust_presidents_committee` | `case_information_package` | `IP-CONDITION` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `trust_presidents_committee` | `examination_status_or_report` | `IP-REPORT` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `trust_presidents_committee` | `reporting_opportunity` | `IP-CASE` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `trust_presidents_committee` | `delivered_continuity_assessment` | `IP-CONDITION` | `R-PARTY` | `T-RECORD` | `CLOSED` |
| `trust_presidents_committee` | `coordination_authority` | `IP-AUTHORITY` | `R-ACTOR` | `T-EFFECTIVE` | `CLOSED` |
| `trust_presidents_committee` | `contributor_reply` | `IP-REPLY` | `R-PARTY` | `T-RESULT` | `CLOSED` |
| `trust_presidents_committee` | `process_disposition_or_result` | `IP-RESULT` | `R-PARTY` | `T-RESULT` | `CLOSED` |

Catalog row count: **115**. Every row resolves to a released
`(capability_id, reader_observation_id)` placement. No global reader-facing
observation registry is assumed.

## 4. Intent, communication, adjudication, and result

### Closure codebook

- `AT-SELF`: actor plus scoped own institutional authority; `AT-PARTY`: exact
  counterparty/recipient and object; `AT-FORUM`: competent committee,
  governance, facility, or institutional forum; `AT-HOST`: exact host/claim;
  `AT-RESOURCE`: actor plus canonical resource/control owner; `AT-VENUE`:
  eligible venue/route and mandate; `AT-NONE`: a valid recorded no-intent
  decision.
- Lifecycle references `LF-AUTH`, `LF-INFO`, `LF-SUPPORT`, `LF-PROPOSAL`,
  `LF-SOLICIT`, `LF-RESOURCE`, `LF-CREDIT_CLEARING`, `LF-COMM`,
  `LF-WITHDRAWAL`, `LF-FACILITY`, `LF-CALL`, `LF-FUNDING`, and `LF-POSITION`
  resolve to Scenario Definition §8.
- `AJ-GOV`, `AJ-INFO`, `AJ-CASE`, `AJ-REL`, `AJ-COMM`, `AJ-RESOURCE`,
  `AJ-OPS`, `AJ-FACILITY`, `AJ-LOAN`, `AJ-FUNDING`, `AJ-VENUE`, and `AJ-TRACE`
  identify the authoritative adjudication/result owner. `AJ-TRACE` records a
  no-intent choice or pending state and cannot mutate business/world state.

Every placement additionally requires its capability-qualified action type,
released parameters, consumed observation/state versions, decision reference,
target, authority/resource refs where material, event/expiry times, and
idempotency identity. The row code names the primary lifecycle; cross-links to
other families remain mandatory where the released semantics require them.

### Complete intent-placement catalog

| Capability | Intent | Authority/target | Object/lifecycle | Adjudicator/result owner | Status |
|---|---|---|---|---|---|
| `bank_resource_decision` | `request_proposal_information` | `AT-PARTY` | `LF-INFO`/`LF-SOLICIT` | `AJ-INFO` | `CLOSED` |
| `bank_resource_decision` | `refer_or_decline_proposal` | `AT-PARTY` | `LF-SOLICIT` | `AJ-CASE` | `CLOSED` |
| `bank_resource_decision` | `make_conditional_contribution_offer` | `AT-RESOURCE` | `LF-SOLICIT`/`LF-RESOURCE` | `AJ-RESOURCE` | `CLOSED` |
| `bank_resource_decision` | `commit_owned_resource` | `AT-RESOURCE` | `LF-RESOURCE` | `AJ-RESOURCE` | `CLOSED` |
| `bank_resource_decision` | `revise_or_cancel_commitment` | `AT-RESOURCE` | `LF-SOLICIT`/`LF-RESOURCE` | `AJ-RESOURCE` | `CLOSED` |
| `bank_resource_decision` | `apply_for_member_certificate` | `AT-FORUM`/`AT-RESOURCE` | `LF-FACILITY` | `AJ-FACILITY` | `CLOSED` |
| `bank_resource_decision` | `submit_controlled_collateral` | `AT-FORUM`/`AT-RESOURCE` | `LF-FACILITY` | `AJ-FACILITY` | `CLOSED` |
| `bank_resource_decision` | `await_commitment_or_application_result` | `AT-NONE` | `LF-SOLICIT`/`LF-FACILITY` | `AJ-TRACE` | `CLOSED` |
| `call_money_broker_borrower` | `request_call_or_term_clarification` | `AT-PARTY` | `LF-INFO`/`LF-CALL` | `AJ-INFO` | `CLOSED` |
| `call_money_broker_borrower` | `request_call_loan_renewal_or_replacement` | `AT-PARTY` | `LF-FUNDING` | `AJ-FUNDING` | `CLOSED` |
| `call_money_broker_borrower` | `submit_controlled_collateral_proposal` | `AT-RESOURCE`/`AT-PARTY` | `LF-FACILITY`/`LF-FUNDING` | `AJ-FACILITY` | `CLOSED` |
| `call_money_broker_borrower` | `accept_call_loan_offer` | `AT-PARTY` | `LF-FUNDING` | `AJ-FUNDING` | `CLOSED` |
| `call_money_broker_borrower` | `request_call_loan_offer_revision` | `AT-PARTY` | `LF-FUNDING` | `AJ-FUNDING` | `CLOSED` |
| `call_money_broker_borrower` | `decline_call_loan_offer` | `AT-PARTY` | `LF-FUNDING` | `AJ-FUNDING` | `CLOSED` |
| `call_money_broker_borrower` | `authorize_controlled_repayment` | `AT-RESOURCE`/`AT-PARTY` | `LF-CALL`/`LF-RESOURCE` | `AJ-LOAN` | `CLOSED` |
| `call_money_broker_borrower` | `request_authorized_position_reduction` | `AT-VENUE`/`AT-RESOURCE` | `LF-POSITION` | `AJ-VENUE` | `CLOSED` |
| `call_money_broker_borrower` | `record_funding_inability` | `AT-NONE` | `LF-FUNDING` decision record | `AJ-TRACE` | `CLOSED` |
| `call_money_broker_borrower` | `await_funding_or_repayment_result` | `AT-NONE` | `LF-FUNDING`/`LF-CALL` | `AJ-TRACE` | `CLOSED` |
| `call_money_lender` | `request_call_loan_information` | `AT-PARTY` | `LF-INFO`/`LF-CALL` | `AJ-INFO` | `CLOSED` |
| `call_money_lender` | `continue_call_loan_for_interval` | `AT-PARTY` | `LF-CALL` | `AJ-LOAN` | `CLOSED` |
| `call_money_lender` | `propose_call_loan_term_change` | `AT-PARTY` | `LF-CALL` | `AJ-LOAN` | `CLOSED` |
| `call_money_lender` | `issue_call_or_reduction_notice` | `AT-PARTY` | `LF-CALL`/`LF-COMM` | `AJ-LOAN` | `CLOSED` |
| `call_money_lender` | `make_conditional_call_loan_offer` | `AT-RESOURCE`/`AT-PARTY` | `LF-FUNDING`/`LF-RESOURCE` | `AJ-FUNDING` | `CLOSED` |
| `call_money_lender` | `decline_call_loan_request` | `AT-PARTY` | `LF-FUNDING` | `AJ-FUNDING` | `CLOSED` |
| `call_money_lender` | `revise_or_cancel_call_loan_offer` | `AT-PARTY` | `LF-FUNDING` | `AJ-FUNDING` | `CLOSED` |
| `call_money_lender` | `await_call_loan_result` | `AT-NONE` | `LF-CALL`/`LF-FUNDING` | `AJ-TRACE` | `CLOSED` |
| `j_pierpont_morgan` | `classify_coordination_matter` | `AT-SELF`/`AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `j_pierpont_morgan` | `request_case_information` | `AT-PARTY` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `j_pierpont_morgan` | `request_independent_examination` | `AT-FORUM`/`AT-PARTY` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `j_pierpont_morgan` | `convene_coordination_session` | `AT-PARTY` | `LF-COMM`/`LF-PROPOSAL` | `AJ-COMM` | `CLOSED` |
| `j_pierpont_morgan` | `form_or_revise_coordination_proposal` | `AT-SELF`/`AT-PARTY` | `LF-PROPOSAL` | `AJ-CASE` | `CLOSED` |
| `j_pierpont_morgan` | `solicit_independent_commitment` | `AT-PARTY` | `LF-SOLICIT` | `AJ-COMM` | `CLOSED` |
| `j_pierpont_morgan` | `assemble_coordination_plan` | `AT-SELF` | `LF-PROPOSAL`/`LF-SOLICIT` | `AJ-CASE` | `CLOSED` |
| `j_pierpont_morgan` | `communicate_coordination_position` | `AT-PARTY` | `LF-COMM` | `AJ-COMM` | `CLOSED` |
| `j_pierpont_morgan` | `decline_or_close_coordination_role` | `AT-SELF`/`AT-PARTY` | `LF-SUPPORT`/`LF-PROPOSAL` | `AJ-CASE` | `CLOSED` |
| `j_pierpont_morgan` | `request_commitment_or_result_clarification` | `AT-PARTY` | `LF-INFO`/`LF-SOLICIT` | `AJ-INFO` | `CLOSED` |
| `knickerbocker_depositor` | `request_withdrawal` | `AT-HOST` | `LF-WITHDRAWAL` | `AJ-OPS` | `CLOSED` |
| `knickerbocker_depositor` | `retain_for_interval` | `AT-NONE` | `LF-WITHDRAWAL` decision record | `AJ-TRACE` | `CLOSED` |
| `knickerbocker_depositor` | `await_request_result` | `AT-NONE` | `LF-WITHDRAWAL` | `AJ-TRACE` | `CLOSED` |
| `knickerbocker_trust` | `verify_internal_condition` | `AT-SELF` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `knickerbocker_trust` | `seek_institutional_authorization` | `AT-FORUM` | `LF-AUTH` | `AJ-GOV` | `CLOSED` |
| `knickerbocker_trust` | `prepare_information_package` | `AT-SELF` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `knickerbocker_trust` | `submit_support_request` | `AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `knickerbocker_trust` | `request_channel_confirmation` | `AT-PARTY` | `LF-INFO`/`LF-CREDIT_CLEARING` | `AJ-REL` | `CLOSED` |
| `knickerbocker_trust` | `provide_requested_information` | `AT-PARTY` | `LF-INFO`/`LF-COMM` | `AJ-INFO` | `CLOSED` |
| `knickerbocker_trust` | `request_status_clarification` | `AT-PARTY` | `LF-INFO`/`LF-SUPPORT` | `AJ-INFO` | `CLOSED` |
| `knickerbocker_trust` | `revise_or_withdraw_request` | `AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `knickerbocker_trust` | `issue_institutional_communication` | `AT-PARTY` | `LF-COMM` | `AJ-COMM` | `CLOSED` |
| `knickerbocker_trust` | `prepare_operational_contingency` | `AT-SELF`/`AT-HOST` | `LF-WITHDRAWAL` | `AJ-OPS` | `CLOSED` |
| `knickerbocker_trust` | `request_result_clarification` | `AT-PARTY` | `LF-INFO`/`LF-SUPPORT` | `AJ-INFO` | `CLOSED` |
| `later_trust_depositor` | `request_withdrawal` | `AT-HOST` | `LF-WITHDRAWAL` | `AJ-OPS` | `CLOSED` |
| `later_trust_depositor` | `retain_for_interval` | `AT-NONE` | `LF-WITHDRAWAL` decision record | `AJ-TRACE` | `CLOSED` |
| `later_trust_depositor` | `await_request_result` | `AT-NONE` | `LF-WITHDRAWAL` | `AJ-TRACE` | `CLOSED` |
| `lincoln_trust_company` | `request_condition_information` | `AT-PARTY`/`AT-SELF` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `lincoln_trust_company` | `authorize_condition_statement` | `AT-SELF` | `LF-AUTH`/`LF-COMM` | `AJ-GOV` | `CLOSED` |
| `lincoln_trust_company` | `narrow_or_withhold_condition_statement` | `AT-SELF` | `LF-COMM` | `AJ-GOV` | `CLOSED` |
| `lincoln_trust_company` | `issue_authorized_condition_statement` | `AT-PARTY` | `LF-COMM` | `AJ-COMM` | `CLOSED` |
| `lincoln_trust_company` | `authorize_correction_or_update` | `AT-SELF` | `LF-AUTH`/`LF-COMM` | `AJ-GOV` | `CLOSED` |
| `lincoln_trust_company` | `request_message_delivery_clarification` | `AT-PARTY` | `LF-INFO`/`LF-COMM` | `AJ-COMM` | `CLOSED` |
| `lincoln_trust_company` | `close_communication_matter` | `AT-SELF` | `LF-COMM` | `AJ-CASE` | `CLOSED` |
| `national_bank_of_commerce` | `verify_nbc_exposure` | `AT-SELF` | `LF-INFO`/`LF-CREDIT_CLEARING` | `AJ-INFO` | `CLOSED` |
| `national_bank_of_commerce` | `request_counterparty_information` | `AT-PARTY` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `national_bank_of_commerce` | `seek_nbc_authority` | `AT-FORUM` | `LF-AUTH` | `AJ-GOV` | `CLOSED` |
| `national_bank_of_commerce` | `propose_credit_posture` | `AT-SELF`/`AT-PARTY` | `LF-CREDIT_CLEARING` | `AJ-RESOURCE` | `CLOSED` |
| `national_bank_of_commerce` | `limit_or_decline_additional_credit` | `AT-SELF`/`AT-PARTY` | `LF-CREDIT_CLEARING` | `AJ-RESOURCE` | `CLOSED` |
| `national_bank_of_commerce` | `seek_intermediation_clarification` | `AT-PARTY` | `LF-INFO`/`LF-SUPPORT` | `AJ-INFO` | `CLOSED` |
| `national_bank_of_commerce` | `forward_request_with_provenance` | `AT-PARTY` | `LF-SUPPORT`/`LF-COMM` | `AJ-COMM` | `CLOSED` |
| `national_bank_of_commerce` | `sponsor_or_represent_request` | `AT-PARTY` | `LF-SUPPORT`/`LF-COMM` | `AJ-CASE` | `CLOSED` |
| `national_bank_of_commerce` | `decline_intermediation` | `AT-PARTY` | `LF-SUPPORT`/`LF-COMM` | `AJ-CASE` | `CLOSED` |
| `national_bank_of_commerce` | `request_nych_direction_clarification` | `AT-FORUM` | `LF-INFO`/`LF-CREDIT_CLEARING` | `AJ-INFO` | `CLOSED` |
| `national_bank_of_commerce` | `confirm_clearing_continuation` | `AT-SELF`/`AT-PARTY` | `LF-CREDIT_CLEARING` | `AJ-REL` | `CLOSED` |
| `national_bank_of_commerce` | `propose_relationship_condition` | `AT-PARTY` | `LF-CREDIT_CLEARING` | `AJ-REL` | `CLOSED` |
| `national_bank_of_commerce` | `issue_clearing_termination_notice` | `AT-PARTY` | `LF-CREDIT_CLEARING`/`LF-COMM` | `AJ-REL` | `CLOSED` |
| `national_bank_of_commerce` | `communicate_nbc_position` | `AT-PARTY` | `LF-COMM` | `AJ-COMM` | `CLOSED` |
| `national_bank_of_commerce` | `request_delivery_or_result_clarification` | `AT-PARTY` | `LF-INFO`/`LF-COMM` | `AJ-INFO` | `CLOSED` |
| `new_york_clearing_house` | `record_and_classify_request` | `AT-SELF`/`AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `new_york_clearing_house` | `request_case_information` | `AT-PARTY` | `LF-INFO`/`LF-SUPPORT` | `AJ-INFO` | `CLOSED` |
| `new_york_clearing_house` | `open_or_continue_review` | `AT-SELF` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `new_york_clearing_house` | `seek_procedural_authority` | `AT-FORUM` | `LF-AUTH` | `AJ-GOV` | `CLOSED` |
| `new_york_clearing_house` | `seek_member_or_association_authorization` | `AT-FORUM` | `LF-AUTH` | `AJ-GOV` | `CLOSED` |
| `new_york_clearing_house` | `refer_request` | `AT-PARTY` | `LF-SUPPORT`/`LF-COMM` | `AJ-CASE` | `CLOSED` |
| `new_york_clearing_house` | `issue_typed_decline` | `AT-PARTY` | `LF-SUPPORT`/`LF-COMM` | `AJ-CASE` | `CLOSED` |
| `new_york_clearing_house` | `propose_conditioned_measure` | `AT-RESOURCE`/`AT-PARTY` | `LF-PROPOSAL`/`LF-RESOURCE` | `AJ-RESOURCE` | `CLOSED` |
| `new_york_clearing_house` | `communicate_case_status` | `AT-PARTY` | `LF-COMM` | `AJ-COMM` | `CLOSED` |
| `new_york_clearing_house` | `close_or_reopen_review` | `AT-SELF`/`AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `trust_company_of_america` | `verify_institutional_condition` | `AT-SELF` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `trust_company_of_america` | `consent_to_scoped_examination` | `AT-PARTY` | `LF-INFO` | `AJ-GOV` | `CLOSED` |
| `trust_company_of_america` | `provide_scoped_case_information` | `AT-PARTY` | `LF-INFO`/`LF-COMM` | `AJ-INFO` | `CLOSED` |
| `trust_company_of_america` | `request_information_or_terms` | `AT-PARTY` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `trust_company_of_america` | `open_or_update_support_request` | `AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `trust_company_of_america` | `propose_collateral_package` | `AT-RESOURCE`/`AT-PARTY` | `LF-FACILITY`/`LF-SUPPORT` | `AJ-FACILITY` | `CLOSED` |
| `trust_company_of_america` | `withdraw_or_close_support_route` | `AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `trust_company_of_america` | `propose_operational_capacity_change` | `AT-SELF` | `LF-WITHDRAWAL` | `AJ-OPS` | `CLOSED` |
| `trust_company_of_america` | `authorize_operational_posture` | `AT-SELF` | `LF-AUTH`/`LF-WITHDRAWAL` | `AJ-OPS` | `CLOSED` |
| `trust_company_of_america` | `authorize_condition_statement` | `AT-SELF` | `LF-AUTH`/`LF-COMM` | `AJ-GOV` | `CLOSED` |
| `trust_company_of_america` | `issue_authorized_condition_statement` | `AT-PARTY` | `LF-COMM` | `AJ-COMM` | `CLOSED` |
| `trust_company_of_america` | `narrow_or_withhold_condition_statement` | `AT-SELF` | `LF-COMM` | `AJ-GOV` | `CLOSED` |
| `trust_company_of_america` | `authorize_correction_or_update` | `AT-SELF` | `LF-AUTH`/`LF-COMM` | `AJ-GOV` | `CLOSED` |
| `trust_company_of_america` | `close_or_pause_institutional_matter` | `AT-SELF`/`AT-PARTY` | `LF-SUPPORT`/`LF-COMM` | `AJ-CASE` | `CLOSED` |
| `trust_presidents_committee` | `open_or_refer_assistance_case` | `AT-SELF`/`AT-PARTY` | `LF-SUPPORT` | `AJ-CASE` | `CLOSED` |
| `trust_presidents_committee` | `request_case_information` | `AT-PARTY` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `trust_presidents_committee` | `request_scoped_examination` | `AT-FORUM`/`AT-PARTY` | `LF-INFO` | `AJ-INFO` | `CLOSED` |
| `trust_presidents_committee` | `issue_case_recommendation` | `AT-FORUM` | `LF-SUPPORT`/`LF-COMM` | `AJ-CASE` | `CLOSED` |
| `trust_presidents_committee` | `report_case_status` | `AT-FORUM` | `LF-COMM` | `AJ-COMM` | `CLOSED` |
| `trust_presidents_committee` | `solicit_independent_contribution` | `AT-PARTY` | `LF-SOLICIT` | `AJ-COMM` | `CLOSED` |
| `trust_presidents_committee` | `assemble_or_revise_support_plan` | `AT-SELF` | `LF-PROPOSAL`/`LF-SOLICIT` | `AJ-CASE` | `CLOSED` |
| `trust_presidents_committee` | `await_case_or_plan_result` | `AT-NONE` | `LF-SUPPORT`/`LF-PROPOSAL` | `AJ-TRACE` | `CLOSED` |

Catalog row count: **107**. Every row resolves to a released
`(capability_id, reader_intent_id)` placement. A message can be materialized
only after the corresponding action is admitted and may add no semantic
content.

## 5. Private state and business lifecycles

### Private decision state

| Capability | Released state family | Authoritative replay path | Business truth retained elsewhere | Status |
|---|---|---|---|---|
| `knickerbocker_trust` | last verified condition time; operational and request-strategy posture; consumed refs | reducer-committed private posture or deterministic DecisionRecord view, linked to delivered inputs/results | condition, authority, request, relationship, operations, resources | `CLOSED` |
| `new_york_clearing_house` | procedural-assessment posture; consumed versions | reducer/private or deterministic DecisionRecord view | case, review, authority, resource proposal, disposition/result | `CLOSED` |
| `national_bank_of_commerce` | exposure-review, intermediation, communication postures; consumed versions | reducer/private or deterministic DecisionRecord view | credit, relationship, request, direction, notice, result | `CLOSED` |
| `j_pierpont_morgan` | coordination posture; consumed versions | reducer/private or deterministic DecisionRecord view | case, report, proposal, reply, resource, result | `CLOSED` |
| `trust_company_of_america` | institutional-response posture; consumed versions | reducer/private or deterministic DecisionRecord view | condition, examination, route, collateral, service, message, result | `CLOSED` |
| `lincoln_trust_company` | communication posture; consumed versions | reducer/private or deterministic DecisionRecord view | condition, competent forum, statement authorization, message/result | `CLOSED` |
| `trust_presidents_committee` | information inventory and bounded case/plan posture | reducer/private or deterministic DecisionRecord view | mandate, application, examination, recommendation delivery, replies, plan/result | `CLOSED` |
| `knickerbocker_depositor` | private need, response profile, dated information inventory, consumed request/result refs | unit-scoped private configuration/events plus DecisionRecord-derived state | host claim, request, service, payment/result | `CLOSED` |
| `bank_resource_decision` | participation/certificate posture, information inventory, consumed offer/application/resource versions | actor/unit private configuration plus DecisionRecord/reducer path | authority, facility, collateral, commitment, canonical resource | `CLOSED` |
| `later_trust_depositor` | private need, profile/conflict rule, dated information inventory, consumed refs | host/unit-scoped private configuration/events plus DecisionRecord-derived state | host claim, request, service, payment/result | `CLOSED` |
| `call_money_lender` | existing/new lending postures, term assessment, information inventory, consumed lifecycle/resource versions | actor/unit private configuration and declared assessment transitions | contract, call, offer, resource, booking/repayment | `CLOSED` |
| `call_money_broker_borrower` | response posture, information inventory, consumed obligation/request/offer/collateral/result versions | actor/unit private configuration plus DecisionRecord/reducer path | obligation, route, collateral control, funding, repayment/settlement | `CLOSED` |

A behavior-changing state cannot remain backend-local. A no-intent decision may
update only its declared/derived private view; it cannot change a request,
resource, relationship, service, loan, or world record.

### Lifecycle closure

| Family | Scenario owner and replay record | Released capability coverage | Status |
|---|---|---|---|
| `LF-AUTH` | competent governance/forum object plus versioned result | all institutional and resource/funding authority requests | `CLOSED` |
| `LF-INFO` | producer/examiner, information request/report, transport and delivery | all information, condition, examination and clarification intents | `CLOSED` |
| `LF-SUPPORT` | sender/recipient case process with each intermediary hop | KT, NBC, NYCH, TCA, committee, Morgan case roles | `CLOSED` |
| `LF-PROPOSAL` | one proposal/plan owner and immutable version lineage | Morgan, committee, NYCH, TCA proposal/plan semantics | `CLOSED` |
| `LF-SOLICIT` | one target decision process per proposal/version | Morgan, committee and bank-resource replies | `CLOSED` |
| `LF-RESOURCE` | canonical resource owner, reservation/commitment/execution ledger | bank resources, support measures, credit/funding and repayment | `CLOSED` |
| `LF-CREDIT_CLEARING` | financial exposure and relationship/notice ledgers | NBC credit/clearing, KT channel and linked results | `CLOSED` |
| `LF-COMM` | issuing authority, message, transport, delivery and correction | all statements, notices, status, invitations and request hops | `CLOSED` |
| `LF-WITHDRAWAL` | unit request, host service, payment and claim ledger | KT/later depositors and host operating response | `CLOSED` |
| `LF-FACILITY` | applicant, facility, collateral and reducer | TCA/bank/lender/borrower collateral and certificate semantics | `CLOSED` |
| `LF-CALL` | lender/borrower contract and repayment process | call lender and broker-borrower | `CLOSED` |
| `LF-FUNDING` | borrower/lender/venue funding process | replacement requests, offers, acceptance, match, booking, transfer | `CLOSED` |
| `LF-POSITION` | authorized position owner and NYSE venue/settlement | broker-borrower bounded reduction | `CLOSED` |

## 6. Institutions, relationships, authority, and resources

| Requirement | Authoritative owner | Invariant/competing-claim rule | Status |
|---|---|---|---|
| entity/actor/capability identity | `WS-ENTITY` | one entity/actor/artifact; capability union cannot duplicate entity | `CLOSED` |
| host/population identity | `WS-ENTITY`/`WS-CLAIM` | unit, host, claim, weight, profile and private state resolve together | `CLOSED; CONFIG_REQUIRED` |
| governance/authority | `WS-AUTH` | exact actor/intent/object/target/resource/time scope; unknown grants nothing | `CLOSED` |
| KT–NBC clearing relation | `WS-REL` | notice issue/delivery/effective change separate; focal terms remain explicit/unknown | `CLOSED` |
| NYCH membership/focal route | membership/case process | member-facility restriction fixed; alternative-route mechanism run-pinned | `CLOSED` |
| committee/presidents/Morgan ownership | mandate, case and proposal registries | distinct owners; cooperation cannot create shared plan or resource authority | `CLOSED` |
| support/request routes | `LF-SUPPORT` | one object and per-hop lineage; route result cannot overwrite other route | `CLOSED` |
| resource ownership/conservation | `WS-RESOURCE`/reducer | one owner/prestate; offers, commitments, transfers and effects distinct | `CLOSED` |
| collateral | `WS-COLLATERAL`/facility/venue | owner/control, eligibility, valuation, encumbrance and realization distinct | `CLOSED` |
| depositor claim/service | `WS-CLAIM`/`WS-OPS` | only realized payment changes claim/cash; host/private scope conserved | `CLOSED` |
| call loan/funding | `WS-LOAN` | contract, call, request, offer, match, booking, transfer, repayment distinct | `CLOSED` |
| NYSE venue | `WS-VENUE` | route/matching/settlement only; venue supplies no participant policy | `CLOSED; POLICY_CONFIG_REQUIRED` |
| Treasury/later facility inputs | exogenous input registry | dated, sourced, not visible before delivery and not back-projected | `CLOSED; CONFIG_REQUIRED` |

## 7. Structural identity, representative cases, and conformance rules

The Scenario Definition's eight structural identities and every participant
profile/posture assignment enter system-only run identity. Agents receive only
their admissible projected consequences. The ten worked cases in Scenario
Definition §10 exercise multi-hop request lineage, compound records,
host-scoped populations, NYCH route variants, multi-capability resources, TCA
process separation, coordinator/contributor ownership, broker funding,
Lincoln communication, and deterministic duplicate/replay behavior.

### Accepted rule coverage

| Rule | Closure evidence | Status |
|---|---|---|
| `C01` | fixed release ID/commit/manifest/product hashes in input identity | `COVERED` |
| `C02` | twelve-row capability assembly and exact loader inventory | `COVERED` |
| `C03` | exact 62/115/107 derivation and complete catalogs | `COVERED` |
| `C04` | `WS-ENTITY` namespace/resolve rule | `COVERED` |
| `C05` | named and population assembly rules | `COVERED` |
| `C06` | one entity authority/resource/relationship owner across capabilities | `COVERED` |
| `C07` | host/institution/weight/private-state population assembly | `COVERED` |
| `C08` | weights limited to outcome aggregation; no resource/action multiplication | `COVERED` |
| `C09` | capability-qualified observation catalog equals loader-derived union | `COVERED` |
| `C10` | information-product source/time/freshness/visibility/version rules | `COVERED` |
| `C11` | temporal admissibility and forbidden-knowledge rules | `COVERED` |
| `C12` | compound-record coherence and Case 2 | `COVERED` |
| `C13` | missing/stale/disputed/unknown fail-closed projection | `COVERED` |
| `C14` | twelve-row private-state replay table | `COVERED` |
| `C15` | DecisionRecord/input/result causal refs; no-intent cannot change world | `COVERED` |
| `C16` | participant memory limited to refs/version/assessment | `COVERED` |
| `C17` | thirteen lifecycle state/lineage registries | `COVERED` |
| `C18` | family-specific duplicate, revision and expiry rules; Case 10 | `COVERED` |
| `C19` | exact capability-qualified 107-row intent catalog | `COVERED` |
| `C20` | catalog codebook plus accepted mapping parameter/observation requirements | `COVERED` |
| `C21` | one semantic item/one canonical carrier; conflicting projection fails | `COVERED` |
| `C22` | `WS-AUTH` scope and adjudication ladder | `COVERED` |
| `C23` | object/version/target/material-parameter idempotency; Case 10 | `COVERED` |
| `C24` | action admission before message materialization; no new semantics | `COVERED` |
| `C25` | one message/delivery lifecycle per recipient/hop | `COVERED` |
| `C26` | canonical resource/control prestate and conservation rules | `COVERED` |
| `C27` | reducer-only state deltas/version increments | `COVERED` |
| `C28` | admission, communication, delivery, business and execution results separated | `COVERED` |
| `C29` | adverse/partial paths retain attempted parameters/reasons | `COVERED` |
| `C30` | decision-to-observation closed chain and replay case | `COVERED` |
| `C31` | reproducibility identity covers assembly/config/variants/routes/policies | `COVERED` |
| `C32` | artifact identity covers Definition hashes/envelopes/action union | `COVERED` |
| `C33` | release/mapping/scenario/contract/component recoverability | `COVERED` |
| `C34` | shared frozen backend-neutral semantic envelope | `COVERED` |

## 8. Gaps, routing, owner decisions, and verdict

### Remaining work and gaps

| Item | Owning layer | Required next action | Blocks accepted semantics? | Blocks implementation? |
|---|---|---|---|---|
| exact historical intraday order and several focal authority/procedure facts unavailable | evidence/scientific interpretation | preserve unknowns and structural alternatives; research only if later question justifies it | no | no, if configuration labels assumptions |
| exact actor composition, population units/weights, opening resources/claims/loans not selected | scenario configuration | produce a small versioned configuration after owner accepts this Definition | no | yes |
| service/queue, venue, matching, amount and timing policies are semantic families but not executable values | scenario configuration/implementation | choose minimal predeclared policies and test them against worked cases | no | yes |
| structural baseline and exogenous ownership boundary | owner decision | `OD-SC-01` through `OD-SC-03` accepted and fixed for v0.1 | no | no |
| no Rule policy, runtime adapter, or simulation exists for the full release | implementation | later bounded implementation slices after scenario/config acceptance | no | yes |
| historical calibration/held-out validation absent | future research/evaluation | do not make validity claims; design successor evidence/evaluation separately | no | no for engineering; yes for scientific-validity claims |

No released observation or intent lacks a scenario producer, route,
adjudicator, lifecycle, or result owner. No concrete V1 carrier counterexample
was found. Exact runtime values and executable transition code are deliberately
outside this accepted closure.

### Owner decision resolution

The project owner accepted `OD-SC-01` through `OD-SC-04` on 22 August 2026.

1. **`OD-SC-01` — event boundary.** Accept an 18 October start, a primary
   21–26 October window, a configuration-pinned early-November horizon, and the
   partially ordered event-time policy. The exact final date/time belongs to
   the later configuration because the fixed evidence supplies only the
   broader follow-through interval.
2. **`OD-SC-02` — exogenous ownership.** Accept pre-boundary affiliated-bank
   distress, committee constitution by the wider presidents' forum, Treasury
   deposits, later certificate-facility supply/rules, and NYSE governance as
   explicit scenario inputs because their autonomous decision makers are not
   in Roster release v0.1.
3. **`OD-SC-03` — structural baseline.** Accept the conservative NYCH route,
   no-presumed-NYCH-direction NBC baseline, conservative committee procedure,
   independent resource owners, Morgan personal attribution, and disabled
   relationship-history mechanism, with the listed sensitivities unvalidated.
4. **`OD-SC-04` — next-stage boundary.** Accept semantic closure now and defer
   exact actor/population/resource/venue configuration and implementation to a
   separate bounded cycle; do not reopen Definitions or Contracts absent a
   reproducible closure failure.

### Formal disposition

`OWNER_ACCEPTED_SEMANTIC_CLOSURE`

The accepted Event Scenario Definition supplies the complete semantic world
required by all 12 released products, all 115 observation placements, all 107
intent placements, declared private state, 13 lifecycle families, and 34
accepted cross-object rules. The remaining items are later configuration or
implementation work, not hidden semantic gaps. This disposition authorizes
neither implementation nor simulation and makes no historical-validity claim.
