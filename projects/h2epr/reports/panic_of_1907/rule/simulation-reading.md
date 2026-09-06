# Panic of 1907 Rule simulation reading

## Run identity

This is a simulation-only reading of the current seed-0 Rule output for
H2EPR-0288. Construction used exactly the three admitted dataset files with the
complete Draft exposed; model and network access were denied. The
[compact release](../../../releases/panic_of_1907/rule/) contains independently derived
verification receipts and reproduction guidance. The
[event entry](../../../events/panic_of_1907/) links each semantic owner.

| Item | Exact identity |
| --- | --- |
| Package | h2epr.event-package.0288.v1; f657f2857d9e4d56cc18b882990f98f0fe12dccbd609252dd3d6858bf87c648f |
| Rule binding | 4f46b295b13ad1d4c1e779ded1f9c0be4055e12ab84afbf46442d80f0fa60339 |
| Realization | h2epr.0288.rule-realization.v1; dcbe6430f21c496ad6c773ed61452f4ff8e95b3a3ab3dc1b5e24fe6122ce138e |
| Shared configuration | h2epr.0288.comparison.v1; 3d770548c9bdd7c84f6ef4d9b90110affaeee39b20fa8ee236b6f9f741b2ab7a |
| Rule configuration | h2epr.0288.rule.v1; 19626901b7939971b70d3668f55e51d466e2447c03463442165fd9d457d3d60d |
| Run | run.ae8aa2842bfd4d33c481fc78 |
| Run manifest | 5bd389e910586acc715a4a8cb13194a85ed2f03dc5f3414b399616d650db726b |
| Trace | c55af03ad713bd9426f7fa15e7c2f5bb4b2f3e677114fe3336d46cf066a7688b |
| Terminal state | 76ef0853824b1f9c6205d1ecccad42eec1a43759b7c607800d5fdd1e9a1a7515 |
| Run seal | 514b7bb4a2ced7374967d84a8aee43663bb7270735dfc0c629c2a8b0f0e18331 |
| Generated EPG seal | f34dc9527ead73cf341c65ff4b0d91e114ae5c2c168e18babe8ffda7be391700 |
| Physical raw custody | .local-runtime/h2epr-simulation/runs/benchmark/panic_of_1907/rule/2026-09-06-semantic-contracts/materialization-a |

Fresh A/B materializations are byte-identical across all eight output roles and
the run receipt. The generated-ID probe changes opaque run and record IDs while
preserving semantic trace/graph structure and exact terminal state. The
publisher independently reconstructs the run manifest, H2EPR/MASim source
inventories, observation/memory projections, trace chain, tick/run seals,
authoritative replay, counts, outcomes and graph; it also rematerializes from the
admitted package.

## Complete-output coverage

The complete machine scan traversed 1,043 trace
records, 1,084 graph nodes and
3,111 graph edges. Trace and graph IDs are unique,
every edge endpoint resolves, and the union of graph source-trace references
equals all 1,043 records. Semantic review covered
all 23 non-default actions, 23 deltas, 23 messages, seven annotations, every
coordinate and all 23 terminal expectations. Repeated no-op, observation and
provenance rows were verified by complete-family traversal and independent
reconstruction rather than copied as a raw transcript.

| Trace family | Count | Coverage meaning |
| --- | --- | --- |
| observation / participant_decision / action_intent / action_disposition | 220 each | Eleven complete actor paths at each of 20 coordinates |
| Non-default / no-op actions | 23 / 197 | All admitted; zero rejected non-default actions in the canonical baseline |
| message_intent / message_disposition | 23 / 46 | Every message queued and delivered; zero unresolved transport |
| state_delta | 23 | One actor-authorized record transition per non-default action |
| tick_open / tick_commit / tick_seal | 20 each | Full horizon and sealed authoritative replay |
| stage_entry / generated_annotation | 3 / 7 | Draft navigation entries and declared state summaries |
| run_seal | 1 | Complete evidence and terminal accounting |

The graph contains one generated event, 20 coordinates, eleven participants,
1,043 trace-record nodes and nine state-entity
nodes. Its complete edge-family ledger is:

| Edge family | Count |
| --- | --- |
| addressed_to | 23 |
| aggregates | 20 |
| based_on | 220 |
| caused_by | 46 |
| changes | 23 |
| commits | 23 |
| decided_by | 220 |
| disposes | 266 |
| emitted_by | 220 |
| involves | 16 |
| learns_result_from | 209 |
| observes_for | 220 |
| occurs_at | 1043 |
| part_of | 29 |
| participates_in | 11 |
| projects | 220 |
| received_from | 23 |
| retains_memory_from | 209 |
| seals | 21 |
| sent_by | 23 |
| stage_of | 3 |
| succeeds | 23 |

`received_from` proves actual delivery. `learns_result_from` and
`retains_memory_from` capture runtime memory. `caused_by` and annotation
provenance describe implementation ancestry, not historical causality or a
minimal causal explanation of the panic.

## Generated trajectory

An opening `unrecorded` value means no modeled record has yet been accepted; it
does not assert that an underlying historical fact was false. The table lists
every coordinate, all non-default dispositions and every reducer delta. Trace
suffixes abbreviate `trace.run.ae8aa2842bfd4d33c481fc78.`.

| Coordinate | Accepted participant choices | Reducer effects and delivery count |
| --- | --- | --- |
| c01 | `augustus_heinze_scheme_interface` → `record_heinze_scheme_participation`; `charles_morse_scheme_interface` → `record_morse_scheme_participation` | `scheme.heinze_participation=qualified_failed_scheme_recorded` (`…00000053`); `scheme.morse_participation=qualified_failed_scheme_recorded` (`…00000054`); 0 delivered |
| c02 | `general_depositor_population` → `record_affiliated_bank_withdrawal_run`; `knickerbocker_trust_company` → `request_emergency_assistance` | `withdrawals.affiliated_bank_run=aggregate_run_recorded` (`…00000114`); `knickerbocker.aid_request=submitted_to_nych_and_morgan` (`…00000115`); 4 delivered |
| c03 | `general_depositor_population` → `record_knickerbocker_withdrawal_run`; `jp_morgan_rescue_interface` → `decline_knickerbocker_aid_request`; `knickerbocker_trust_company` → `record_chairman_dismissal`; `new_york_clearing_house` → `record_initial_member_bank_stabilization` | `withdrawals.knickerbocker_run=aggregate_run_recorded` (`…00000170`); `knickerbocker.morgan_aid_disposition=declined_unresolved_request` (`…00000171`); `knickerbocker.chairman_dismissal=charles_barney_dismissal_recorded` (`…00000172`); `clearing_house.initial_member_support=assurance_management_and_loan_support_recorded` (`…00000173`); 3 delivered |
| c04 | `general_depositor_population` → `record_initial_run_cessation`; `new_york_clearing_house` → `deny_nonmember_aid_request` | `withdrawals.affiliated_bank_run_cessation=aggregate_cessation_recorded` (`…00000225`); `knickerbocker.nych_aid_disposition=denied_nonmember_request` (`…00000226`); 2 delivered |
| c05 | `knickerbocker_trust_company` → `suspend_knickerbocker_operations` | `knickerbocker.operations=suspended_recorded` (`…00000283`); 1 delivered |
| c06 | `general_depositor_population` → `record_trust_company_withdrawal_run` | `withdrawals.trust_company_run=aggregate_contagion_run_recorded` (`…00000341`); 3 delivered |
| c07 | `jp_morgan_rescue_interface` → `coordinate_private_trust_support`; `new_york_clearing_house` → `issue_clearing_house_certificates`; `new_york_trust_company_population` → `record_national_bank_balance_liquidation` | `private_rescue.trust_support=qualified_support_recorded` (`…00000398`); `containment.loan_certificates=issuance_recorded` (`…00000399`); `trust_liquidity.national_bank_balances=aggregate_liquidation_recorded` (`…00000400`); 3 delivered |
| c08 | `jp_morgan_rescue_interface` → `record_nyse_liquidity_support`; `new_york_clearing_house` → `coordinate_convertibility_suspension` | `private_rescue.nyse_support=qualified_support_recorded` (`…00000453`); `containment.convertibility_coordination=directive_recorded` (`…00000454`); 3 delivered |
| c09 | `ny_clearing_house_member_bank_population` → `implement_deposit_convertibility_suspension` | `containment.member_convertibility=aggregate_suspension_recorded` (`…00000506`); 1 delivered |
| c10 | `european_gold_flow_gate` → `record_aggregate_gold_inflow_account` | `gold_flow.european_imports=qualified_inflow_recorded` (`…00000557`); 1 delivered |
| c11 | All eleven actors wait | No state delta; 0 delivered |
| c12 | `united_states_congress` → `establish_national_monetary_commission` | `reform.commission_establishment=mandate_recorded` (`…00000655`); 0 delivered |
| c13 | `national_monetary_commission` → `conduct_banking_system_inquiry` | `reform.commission_process=bounded_inquiry_recorded` (`…00000704`); 1 delivered |
| c14 | `national_monetary_commission` → `publish_banking_reform_recommendations` | `reform.commission_recommendations=qualified_recommendations_recorded` (`…00000754`); 0 delivered |
| c15 | `united_states_congress` → `record_federal_reserve_act_passage` | `reform.federal_reserve_act=passed_1913_12_23_recorded` (`…00000803`); 1 delivered |
| c16 | All eleven actors wait | No state delta; 0 delivered |
| c17 | All eleven actors wait | No state delta; 0 delivered |
| c18 | All eleven actors wait | No state delta; 0 delivered |
| c19 | All eleven actors wait | No state delta; 0 delivered |
| c20 | All eleven actors wait | No state delta; 0 delivered |

The first information chain is separately attributable. Heinze and Morse record
their own scheme participation at c01; both reports arrive before c02 aggregate
affiliated-bank withdrawals and Knickerbocker's aid request. The member-run
notice reaches NYCH before c03 support. Morgan's c03 denial and NYCH's c04 denial
arrive separately. Knickerbocker cannot record its c05 suspension until its own
request/dismissal, the public run and both delivered dispositions are present.

Suspension delivery enables c06 trust-company withdrawals. That run notice
enables c07 trust balance liquidation, Morgan trust support and NYCH certificate
issuance. The liquidation notice reaches Morgan before c08 NYSE support. NYCH's
distinct coordination record also occurs at c08; member banks implement
convertibility suspension only after both certificate and coordination messages
are delivered. Their public signal reaches the aggregate gold-flow gate before
its c10 qualified record. Nothing in these records transfers money, sets a price
or writes a recovery state.

The reform chain begins at c12 after the disclosed structural crisis-response
conditions. Congress sends a mandate; the Commission records its inquiry at c13
and publishes recommendations at c14. Only delivery of those recommendations
enables Congress's c15 Act record. Later participants never appear in earlier
memory. Coordinates 16–20 contain waiting and terminal accounting.

Every descriptive expectation is assessed below. These are qualified records:
support is not a conserved transfer, aggregate action is not unanimity, gold
inflow is not proven recovery, and statute passage is not policy effectiveness.

| Expectation suffix | Observed value | Met |
| --- | --- | --- |
| scheme.heinze_participation | qualified_failed_scheme_recorded | True |
| scheme.morse_participation | qualified_failed_scheme_recorded | True |
| withdrawals.affiliated_bank_run | aggregate_run_recorded | True |
| clearing_house.initial_member_support | assurance_management_and_loan_support_recorded | True |
| withdrawals.affiliated_bank_run_cessation | aggregate_cessation_recorded | True |
| knickerbocker.aid_request | submitted_to_nych_and_morgan | True |
| knickerbocker.chairman_dismissal | charles_barney_dismissal_recorded | True |
| withdrawals.knickerbocker_run | aggregate_run_recorded | True |
| knickerbocker.nych_aid_disposition | denied_nonmember_request | True |
| knickerbocker.morgan_aid_disposition | declined_unresolved_request | True |
| knickerbocker.operations | suspended_recorded | True |
| withdrawals.trust_company_run | aggregate_contagion_run_recorded | True |
| trust_liquidity.national_bank_balances | aggregate_liquidation_recorded | True |
| private_rescue.trust_support | qualified_support_recorded | True |
| private_rescue.nyse_support | qualified_support_recorded | True |
| containment.loan_certificates | issuance_recorded | True |
| containment.convertibility_coordination | directive_recorded | True |
| containment.member_convertibility | aggregate_suspension_recorded | True |
| gold_flow.european_imports | qualified_inflow_recorded | True |
| reform.commission_establishment | mandate_recorded | True |
| reform.commission_process | bounded_inquiry_recorded | True |
| reform.commission_recommendations | qualified_recommendations_recorded | True |
| reform.federal_reserve_act | passed_1913_12_23_recorded | True |

## Mechanism reading

### Direct run evidence

Eleven participants use one declarative Rule implementation and one authoritative
environment. Single-writer handlers preserve separate speculator, depositor,
clearing-house, trust, private-rescue, member-bank, aggregate-flow, legislative
and commission authority. The reducer, not Rule, owns effects. Public prestate,
actual delivery and retained runtime memory activate later rows; Draft labels,
Reference content are absent from observations. Reform capability and field names
are visible before their generated result values. No common-code Panic branch
supplies choices.

Morgan's refusal is selected after the received aid request. The configured
rationale refers to source reporting about review; the simulation produces no
audit finding, balance sheet or solvency determination. Decision-record rationale
must not be read as evidence that an audit ran.

The canonical run accepts all 23 selected records and meets all 23 descriptive
expectations. It contains no rejected non-default action, so it does not alone
prove failed authority or changed-information retry; shared negative tests own
those contracts. Its direct contribution is a sealed multi-hop example spanning
individual interfaces, institutional Agents, Population Models and an aggregate
representation gate.

### Representation and construction probes

Five Draft participants remain context because being a stock target, run/support
recipient, exchange under stress, national system or institution created by law
does not expose a coherent choice. P_8 is absent from the Draft and no clearing-
agent authority is invented. The three depositor/trust/member-bank group parents
preserve aggregate records without individual probabilities or unanimity. The
gold-flow gate records a qualified source account rather than a market process.

Two previously verified local probes, retained as historical construction evidence, test this reading without becoming current
event releases or historical counterfactuals:

| Changed owner/input | Observed response | Evidence boundary |
|---|---|---|
| Knickerbocker's Rule request row receives a deliberate circular prerequisite: it must know an NYCH denial before requesting aid | Six early records remain accepted. Request, dismissal, denials, suspension and the suspension-dependent trust/containment/gold/reform chain stay open: 970 trace records, 1,011 nodes and 2,856 edges. | Fresh A/B, ID perturbation, replay, graph and independent publication pass with zero unresolved transport. This tests missing-choice propagation, not historical non-occurrence. |
| Commission-to-Congress recommendation latency changes from one to six ticks | Recommendations publish at c14 but reach Congress at terminal c20, after its decision window. The Act is the only open expectation: 1,041 trace records, 1,082 nodes and 3,104 edges. | The message reaches a terminal delivered state. Six ticks are an adversarial route setting, not estimated legislative latency or a policy counterfactual. |

The probe run IDs are `run.35a2b4ab1731bd2169a3edaf` and
`run.da9ddcf62f36612913100e65`. Each variant received new configuration,
realization, assembly, package and release identities before execution; neither
was created by editing an admitted package or generated output.

Previously recorded probe identities refer to their original source revision;
they were not rematerialized as part of this current canonical replacement.
Current shared-contract behavior is covered by the maintained synthetic tests.

## Limitations

The current observation profile exposes declared event vocabulary, including
names associated with later events. It does not provide historically
prefix-clean information. Rule windows and receipt guards are selected
policy assumptions except where explicit shared handler requirements apply.
Configured decision reasons are rationale; hash-linked observations, actual
message content, dispositions and deltas provide generated evidence.

The frozen evidence is uneven. Three records are byte-identical truncated copies,
two repeat a 2025 abstract, and several are scraper-heavy, tangential or only
partial. The current Source Profile retains all input identities while the
semantic parents avoid counting duplicate pages as independent corroboration.
No external historical reconciliation is attempted.

The Draft itself contains malformed or reversed relationship and transaction
endpoints. Actor-local rows and coherent descriptions govern the current
authority map. There is no price process, cash or gold ledger, balance sheet,
solvency state, bank-level population, vote, welfare measure or recovery metric.
Twenty coordinates and one-tick baseline routes are authored ordering choices;
the 1908–1913 interval is deliberately coarse.

This output supports dataset-conditioned construction, state/information-aware
deterministic execution, integrity/replay evidence and trace-derived Generated
EPG description. It does not establish historical fit, parameter calibration,
held-out evaluation, contagion causality, rescue effectiveness, policy effects,
scientific validity or universal generality. LLM and RuleLLM remain planned; no
model decision or cross-backend evidence appears here.
