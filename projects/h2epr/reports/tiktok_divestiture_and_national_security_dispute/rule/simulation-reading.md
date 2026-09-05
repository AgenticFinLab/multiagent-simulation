# TikTok Divestiture and National Security Dispute Rule simulation reading

## Run identity

This is a simulation-only reading of the current seed-0 Rule output for
H2EPR-0170. Construction used exactly the three admitted dataset files with the
complete Draft exposed; model and network access were denied. The
[compact release](../../../releases/tiktok_divestiture_and_national_security_dispute/rule/) contains independently derived
verification receipts and reproduction guidance. The
[event entry](../../../events/tiktok_divestiture_and_national_security_dispute/) links each semantic owner.

| Item | Exact identity |
| --- | --- |
| Package | h2epr.event-package.0170.v1; 667de386997afde4f415f0b6ea491138acce8bfa081150bcfb88f156f67aa7fd |
| Rule binding | 705273c8305f79d568c90b20875fdcbbea18fdc3ed055ddd10e4f7e24f6d9339 |
| Realization | h2epr.0170.rule-realization.v1; c98b489f32a1ab86b103a263ac8f1cc1298b8dfa3709cea407539584b9262ec1 |
| Shared configuration | h2epr.0170.comparison.v1; ca34426154af60a3286eebb69c64ba10cb0c78ff0a7411e235c3df142a803649 |
| Rule configuration | h2epr.0170.rule.v1; 3018e61f9fbdba01e5d945a7ebe37e8307afc3b48190f9504fbd300cb28e623c |
| Run | run.2cb97929423c768bbd0cf72d |
| Run manifest | 811ac05dce1d4f12420f3873421520a19b68ae688df5a2272492cdc6cd0bc055 |
| Trace | 075a63a6862cced760b2b360d2974a89269aa4ef8da98446772fab499b6adec7 |
| Terminal state | 0749d3f388ca92fd77275afde9c0e5075f614b561efed216c430e9b50eda0269 |
| Run seal | 96ca389b6b91857e50bcdd4cff63938c8c3c9f791d06f6c3e8c596f7777d30af |
| Generated EPG seal | 0da5c0b2c32ab760711e0ed2d7c7f848e26ab5e8bce8545992da2bc9431c4828 |
| Physical raw custody | .local-runtime/h2epr-simulation/runs/benchmark/tiktok_divestiture_and_national_security_dispute/rule/2026-09-05-stage-e/accepted/materialization-a |

Fresh accepted A/B materializations are byte-identical across all eight output
roles and the run receipt. The generated-ID probe changes opaque run and record
IDs while preserving semantic trace/graph structure and exact terminal state.
The publisher independently reconstructs the run manifest, current H2EPR/MASim
source inventories, observation/memory projections, trace chain, tick/run seals,
authoritative replay, counts, outcomes and graph; it also rematerializes from the
admitted package.

## Complete-output coverage

The complete machine scan traversed 1,101 trace
records, 1,142 graph nodes and
3,297 graph edges. Trace and graph IDs are unique,
every edge endpoint resolves, and the union of graph source-trace references is
exactly all 1,101 records. Semantic review
covered all 23 non-default actions, 23 deltas, 40 messages, seven annotations,
every coordinate and all 23 terminal expectations. Repeated no-op, observation
and provenance rows were verified by complete-family traversal and independent
reconstruction rather than copied into the report.

| Trace family | Count | Coverage meaning |
| --- | --- | --- |
| observation / participant_decision / action_intent / action_disposition | 220 each | Ten complete actor paths at each of 22 coordinates |
| Non-default / no-op actions | 23 / 197 | All admitted; zero rejected non-default actions in the canonical baseline |
| message_intent / message_disposition | 40 / 80 | Every message queued and delivered; zero unresolved transport |
| state_delta | 23 | One actor-authorized record transition per non-default action |
| tick_open / tick_commit / tick_seal | 22 each | Full horizon and sealed authoritative replay |
| stage_entry / generated_annotation | 4 / 7 | Draft navigation entries and declared state summaries |
| run_seal | 1 | Complete evidence and terminal accounting |

The graph contains one generated event, 22 coordinates, ten participants,
1,101 trace-record nodes and eight state-entity
nodes. Its complete edge-family ledger is:

| Edge family | Count |
| --- | --- |
| addressed_to | 40 |
| aggregates | 22 |
| based_on | 220 |
| caused_by | 63 |
| changes | 23 |
| commits | 23 |
| decided_by | 220 |
| disposes | 300 |
| emitted_by | 220 |
| involves | 18 |
| learns_result_from | 210 |
| observes_for | 220 |
| occurs_at | 1101 |
| part_of | 30 |
| participates_in | 10 |
| projects | 220 |
| received_from | 40 |
| retains_memory_from | 210 |
| seals | 23 |
| sent_by | 40 |
| stage_of | 4 |
| succeeds | 40 |

`received_from` proves actual delivery. `learns_result_from` and
`retains_memory_from` capture runtime memory. `caused_by` and annotation
provenance describe implementation ancestry, not historical causality or a
minimal explanation of the dispute.

## Generated trajectory

An opening `unrecorded` value means that no modeled record has yet been accepted;
it does not say that an underlying historical proposition was false. The table
lists every coordinate, all non-default dispositions and every reducer delta.
Trace suffixes abbreviate `trace.run.2cb97929423c768bbd0cf72d.`.

| Coordinate | Accepted participant choices | Reducer effects and delivery count |
| --- | --- | --- |
| c01 | `donald_trump_executive_interface` → `issue_initial_divestment_order` | `regulation.initial_divestment_order=issued_45_day_divestment_or_restriction_record` (`…00000043`); 0 delivered |
| c02 | `bytedance_platform_governance_interface` → `file_initial_ban_challenge` | `litigation.initial_challenge=filed_first_amendment_challenge_record` (`…00000093`); 1 delivered |
| c03 | `donald_trump_executive_interface` → `record_initial_order_defense` | `litigation.executive_defense=defense_recorded` (`…00000141`); 2 delivered |
| c04 | `us_federal_judiciary_record_gate` → `record_initial_ban_suspension` | `judiciary.initial_ban_suspension=implementation_suspension_recorded` (`…00000190`); 1 delivered |
| c05 | `joe_biden_executive_interface` → `replace_order_with_review_framework` | `regulation.review_framework=revocation_and_review_framework_recorded` (`…00000241`); 2 delivered |
| c06 | `state_and_legislative_restriction_population` → `record_state_device_restrictions` | `restrictions.state_device_bans=aggregate_state_and_campus_restrictions_recorded` (`…00000292`); 2 delivered |
| c07 | `joe_biden_executive_interface` → `issue_federal_device_removal_directive`; `state_and_legislative_restriction_population` → `record_anti_tiktok_legislative_proposal` | `restrictions.federal_device_directive=issued_30_day_removal_record` (`…00000344`); `restrictions.anti_tiktok_legislative_proposal=federal_restriction_proposal_recorded` (`…00000345`); 2 delivered |
| c08 | `house_energy_and_commerce_committee` → `convene_tiktok_hearing` | `oversight.house_hearing=convened_recorded` (`…00000397`); 3 delivered |
| c09 | `bytedance_platform_governance_interface` → `designate_ceo_for_house_hearing` | `oversight.bytedance_ceo_designation=ceo_designation_recorded` (`…00000445`); 2 delivered |
| c10 | `shouzi_chew_testimony_interface` → `deliver_house_testimony` | `oversight.ceo_testimony=qualified_testimony_recorded` (`…00000494`); 1 delivered |
| c11 | `united_states_congress` → `pass_pafaca` | `legislation.pafaca_passage=passed_recorded` (`…00000543`); 2 delivered |
| c12 | `joe_biden_executive_interface` → `sign_pafaca` | `legislation.pafaca_enactment=signed_recorded` (`…00000593`); 1 delivered |
| c13 | `us_federal_judiciary_record_gate` → `issue_appeals_court_pafaca_ruling` | `judiciary.appeals_court_ruling=constitutionality_upheld_recorded` (`…00000642`); 2 delivered |
| c14 | `bytedance_platform_governance_interface` → `announce_supreme_court_appeal` | `litigation.supreme_court_appeal=announced_recorded` (`…00000689`); 1 delivered |
| c15 | `us_federal_judiciary_record_gate` → `issue_supreme_court_pafaca_ruling` | `judiciary.supreme_court_ruling=constitutionality_upheld_recorded` (`…00000736`); 1 delivered |
| c16 | `bytedance_platform_governance_interface` → `record_temporary_us_service_suspension` | `platform.us_service_status=temporarily_suspended_12_hour_record` (`…00000784`); 1 delivered |
| c17 | `donald_trump_executive_interface` → `issue_negotiation_grace_extensions` | `negotiation.ban_extensions=multiple_grace_extensions_recorded` (`…00000835`); 1 delivered |
| c18 | `bytedance_platform_governance_interface` → `record_resolution_negotiation_engagement` | `negotiation.bytedance_engagement=engagement_recorded` (`…00000888`); 3 delivered |
| c19 | `china_trade_negotiation_delegation_gate` → `record_china_consensus_position`; `us_trade_negotiation_delegation_gate` → `record_us_consensus_position` | `negotiation.china_delegation_position=qualified_consensus_position_recorded` (`…00000946`); `negotiation.us_delegation_position=qualified_consensus_position_recorded` (`…00000947`); 2 delivered |
| c20 | `bytedance_platform_governance_interface` → `record_qualified_resolution_position` | `negotiation.bytedance_resolution=qualified_data_operation_and_algorithm_authorization_recorded` (`…00000999`); 6 delivered |
| c21 | `donald_trump_executive_interface` → `issue_implementation_grace_extension` | `negotiation.implementation_extension=implementation_grace_extension_recorded` (`…00001050`); 1 delivered |
| c22 | All ten actors wait | No state delta; 3 delivered |

The early chain preserves separate authority. Trump records an initial mandate;
ByteDance files a challenge; Trump records a defence; and the judiciary gate
waits for both delivered party records before recording the suspension. Biden's
replacement review then enables an aggregate state/campus restriction record.
The state/proposal Population and Biden independently publish proposal and
federal-device records before the House committee can convene its hearing.

The hearing chain keeps convening, corporate witness designation and Chew's
testimony as three choices. Congress receives the proposal and testimony before
passing PAFACA; Biden receives the bill before signing. The judiciary gate then
records a court-of-appeals result, ByteDance announces a Supreme Court appeal,
and the same aggregate gate records the later court result. Aggregation is
explicit: the model does not treat distinct courts as one historical institution
or infer doctrine from their recorded outputs.

The final chain remains qualified. ByteDance records a temporary service
suspension only after the Supreme Court notice. Trump then publishes grace;
ByteDance records negotiation engagement; Chinese and US delegation gates
publish separate positions; ByteDance records its own position after both are
delivered; and Trump publishes an implementation extension. Two positions do
not form a binding agreement, and no state field transfers ownership, data or
algorithm authority. Coordinate 22 only drains the last three messages.

Every descriptive expectation is assessed below. These are bounded records:
challenge is not success, passage is not signature, a ruling is not enforcement,
service suspension is not an impact estimate, and a qualified position is not
implemented settlement.

| Expectation suffix | Observed value | Met |
| --- | --- | --- |
| regulation.initial_divestment_order | issued_45_day_divestment_or_restriction_record | True |
| litigation.initial_challenge | filed_first_amendment_challenge_record | True |
| litigation.executive_defense | defense_recorded | True |
| judiciary.initial_ban_suspension | implementation_suspension_recorded | True |
| regulation.review_framework | revocation_and_review_framework_recorded | True |
| restrictions.state_device_bans | aggregate_state_and_campus_restrictions_recorded | True |
| restrictions.anti_tiktok_legislative_proposal | federal_restriction_proposal_recorded | True |
| restrictions.federal_device_directive | issued_30_day_removal_record | True |
| oversight.house_hearing | convened_recorded | True |
| oversight.bytedance_ceo_designation | ceo_designation_recorded | True |
| oversight.ceo_testimony | qualified_testimony_recorded | True |
| legislation.pafaca_passage | passed_recorded | True |
| legislation.pafaca_enactment | signed_recorded | True |
| judiciary.appeals_court_ruling | constitutionality_upheld_recorded | True |
| litigation.supreme_court_appeal | announced_recorded | True |
| judiciary.supreme_court_ruling | constitutionality_upheld_recorded | True |
| platform.us_service_status | temporarily_suspended_12_hour_record | True |
| negotiation.ban_extensions | multiple_grace_extensions_recorded | True |
| negotiation.bytedance_engagement | engagement_recorded | True |
| negotiation.china_delegation_position | qualified_consensus_position_recorded | True |
| negotiation.us_delegation_position | qualified_consensus_position_recorded | True |
| negotiation.bytedance_resolution | qualified_data_operation_and_algorithm_authorization_recorded | True |
| negotiation.implementation_extension | implementation_grace_extension_recorded | True |

## Mechanism reading

### Direct run evidence

Ten participants use one declarative Rule implementation and one authoritative
environment. Single-writer handlers preserve executive, corporate, witness,
committee, legislative, judiciary, population and delegation authority. The
reducer, not Rule, owns effects. Public prestate, actual delivery and retained
runtime memory activate later rows; Draft stage labels, Reference content and
future negotiation facts are absent from earlier observations. No common-code
TikTok branch supplies the choices.

The canonical run accepts all 23 selected records and meets all 23 descriptive
expectations. That agreement is expected from a full-Draft-conditioned baseline
and is not a historical score. The run contains no rejected non-default action,
so shared negative tests and the construction probes own failure evidence.

### Representation and construction probes

Seven passive ByteDance receipt/target rows from the Draft become delivered
information or public state, not ByteDance-authored choices. P_3 aggregates
distinct public court records behind a declared representation gate; P_5 is an
aggregate Population; P_9 and P_10 retain separate negotiation authority. No
participant can use the malformed Draft relationship directions to claim another
participant's action.

Two freshly admitted local probes test the behavioral reading without becoming
current releases or historical counterfactuals:

| Changed owner/input | Observed response | Evidence boundary |
|---|---|---|
| ByteDance's hearing-designation choice sends no designation message to Chew | Ten early records remain accepted, including hearing and designation. Testimony and the dependent legislation, judiciary, service and negotiation chain remain open: 1,008 records, 1,049 nodes and 2,977 edges. | Fresh A/B, ID perturbation, replay, graph and independent publication pass with zero unresolved transport. This tests missing information, not historical non-occurrence. |
| ByteDance→judiciary route latency changes from one to four ticks | The initial chain shifts but stays inside its windows. The Supreme appeal is accepted at c16 and delivered after the c17 ruling window; the ruling and dependent service/negotiation choices remain open: 1,039 records, 1,080 nodes and 3,084 edges. | The appeal message reaches terminal delivery. Four ticks are an adversarial route setting, not estimated legal latency or a policy counterfactual. |

The probe run IDs are `run.eb4c66d5f8d3e738e733e37c` and `run.8cd7823db9d052599fabfd45`. Each
variant received new configuration, realization, assembly, package and release
identities before execution; neither was created by editing an admitted package
or generated output. An earlier attempt to add an ineligible future-message
guard was rejected before package admission with the typed
`rule_guard_recipient_ineligible` failure, confirming recipient closure.

## Limitations

The frozen evidence is uneven, mostly secondary and frequently truncated or
scraper-heavy; two records repeat substantially the same material. One later
account supplies the final 2025 negotiation description, while another record
conflicts on litigation timing and outcome details. The Source Profile preserves
these identities and the Scenario qualifies their use. No external historical
reconciliation was attempted.

The Draft contains misdirected relationship endpoints and omits delegation rows
from its final relationship. Actor-local rows and coherent descriptions govern
the current authority map. Court and state aggregation hide internal variation.
There is no national-security evidence model, legal reasoning, vote, enforcement,
ownership ledger, data flow, algorithm control, user population, market impact,
agreement implementation or compliance measure. Twenty-two coordinates and
one-tick baseline routes are authored ordering choices across five years.

This output supports dataset-conditioned construction, state/information-aware
deterministic execution, integrity/replay evidence and trace-derived Generated
EPG description. It does not establish legal or security truth, historical fit,
parameter calibration, held-out evaluation, platform or policy effects,
causality, scientific validity or universal generality. LLM and RuleLLM remain
planned; no model decision or cross-backend evidence appears here.
