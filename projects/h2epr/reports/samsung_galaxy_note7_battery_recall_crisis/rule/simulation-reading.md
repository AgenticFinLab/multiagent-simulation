# Samsung Galaxy Note7 Battery Recall Crisis Rule simulation reading

## Run identity

This is a simulation-only reading of the current seed-0 Rule output for
H2EPR-0481. Construction used exactly the three admitted dataset files with the
complete Draft exposed; model and network access were denied. The
[compact release](../../../releases/samsung_galaxy_note7_battery_recall_crisis/rule/)
contains independently derived verification receipts and reproduction guidance.
The event entry links every semantic owner.

| Item | Exact identity |
|---|---|
| Package | `h2epr.event-package.0481.v1`; `6b37fcffdb633d9696cc757d71e0fe60d62c7cd6e9ac074862f8281f346a48fe` |
| Rule binding | `34f80fc27a8ce458777a94234f4178fbb8cd7ab7a44adec06462d7ed010c5419` |
| Realization | `h2epr.0481.rule-realization.v1`; `3efb0abe46003efa1af672b5d9e78290b6ee2f4187c6788349d93e24ebce3754` |
| Shared configuration | `h2epr.0481.comparison.v1`; `1c2bbf2cb1b4e65253c65b1b3c4a5d987b1acc2d934dcdf84aefb0279c92bc33` |
| Rule configuration | `h2epr.0481.rule.v1`; `5328bbdbfe8e1fc073e87535ca43fa4783c71bd187e42f72882ab7efd03bafaf` |
| Run | `run.9120d67d5fe0c22266400e21` |
| Run manifest | `2a5ee513c4271b40510b501cb3d3e46509c1f983e8f546f79ef8c1aa97181d14` |
| Trace | `8696796a7002226e83c62272d8f078ddbe9d8d8b181b75809180f7611f301825` |
| Terminal state | `ed367bf27f6c59a047b0ac40b07957dbc8f7a3d5a17752b4be522eb829970c32` |
| Run seal | `797a72f31f2415c7a9b56e4098fb21c9f33141915bbb07f91737f4c3e3f5adc4` |
| Generated EPG seal | `daf947cb36ba655f70e76577f0b6d3801be46c63d2166733a0e28abfb818600a` |
| Physical raw custody | `.local-runtime/h2epr-simulation/runs/benchmark/samsung_galaxy_note7_battery_recall_crisis/rule/2026-09-06-semantic-contracts/materialization-a` |

Fresh A/B output is byte-identical across all eight output roles and the run
receipt. The generated-ID probe changes opaque run/record identities while
preserving semantic trace and graph structure and exact terminal state. The
publisher independently reconstructs the manifest and H2EPR/MASim source
inventories, observations and memory, trace chain, seals, replay, counts,
outcomes and graph; it also rematerializes the admitted package.

## Complete-output coverage

The full machine scan traversed all 1,101 trace records, 1,152 graph nodes and
3,262 graph edges. Trace IDs and graph IDs are unique, every edge endpoint
resolves, and the union of node/edge source-trace references equals all 1,101
trace records exactly. Semantic review inspected all 28 non-default actions,
28 deltas, 16 messages, five annotations and every coordinate. Repeated no-op,
observation and provenance records were verified by complete family traversal
and independent reconstruction rather than copied as a raw transcript.

| Trace family | Count | Coverage meaning |
|---|---:|---|
| observation / participant_decision / action_intent / action_disposition | 232 each | Eight complete actor paths at each of 29 coordinates |
| Non-default / no-op actions | 28 / 204 | All admitted; zero rejected actions in the canonical baseline |
| message_intent / message_disposition | 16 / 32 | Every message queued and delivered; zero unresolved transport |
| state_delta | 28 | One actor-owned record transition per non-default action |
| tick_open / tick_commit / tick_seal | 29 each | Full horizon and sealed authoritative replay |
| stage_entry / generated_annotation | 4 / 5 | Navigation entries and configured state summaries |
| run_seal | 1 | Complete evidence and terminal accounting |

The graph contains one generated event, 29 coordinates, eight participants,
1,101 trace-record nodes and 13 state-entity nodes. Its complete edge ledger is:

| Edge family | Count |
|---|---:|
| addressed_to | 16 |
| aggregates | 29 |
| based_on | 232 |
| caused_by | 44 |
| changes | 28 |
| commits | 28 |
| decided_by | 232 |
| disposes | 264 |
| emitted_by | 232 |
| involves | 12 |
| learns_result_from | 224 |
| observes_for | 232 |
| occurs_at | 1,101 |
| part_of | 42 |
| participates_in | 8 |
| projects | 232 |
| received_from | 16 |
| retains_memory_from | 224 |
| seals | 30 |
| sent_by | 16 |
| stage_of | 4 |
| succeeds | 16 |

`received_from` identifies actual delivery. `learns_result_from` and
`retains_memory_from` are runtime memory provenance. `caused_by` and annotation
provenance describe implementation ancestry; they are not identified historical
causes or a minimal set of influential decisions.

## Generated trajectory

Opening `unrecorded` values mean that the simulation has not yet admitted a
modeled record. They do not deny the underlying history or set physical facts to
zero. Trace suffixes abbreviate `trace.run.9120d67d5fe0c22266400e21.`.

| Coordinate | Accepted participant choices | Reducer effects and delivery count |
|---|---|---|
| c01 | `samsung_electronics` → `record_note7_launch` | `product.launch=recorded` (`…00000033`); 0 delivered |
| c02 | `samsung_electronics` → `record_global_sales_start` | `product.sales_start=recorded` (`…00000070`); 0 delivered |
| c03 | `global_note7_purchasers` → `report_early_battery_incidents` | `early_incidents.consumer_report=recorded` (`…00000108`); 0 delivered |
| c04 | `samsung_electronics` → `issue_initial_cause_statement` | `early_response.initial_statement=isolated_charging_account_recorded` (`…00000145`); 1 delivered |
| c05 | `samsung_electronics` → `announce_additional_quality_testing` | `early_response.quality_testing=announced` (`…00000181`); 0 delivered |
| c06 | `samsung_electronics` → `delay_global_shipments` | `early_response.shipment_delay=announced` (`…00000217`); 0 delivered |
| c07 | `samsung_electronics` → `announce_initial_global_recall` | `recall.initial_global=announced_excluding_mainland_china` (`…00000256`); 0 delivered |
| c08 | regulator → `require_test_unit_recall_plan`; Samsung → `issue_initial_safety_guidance` | two deltas (`…00000298–299`); 1 delivered |
| c09 | Samsung → `announce_test_unit_recall` | `recall.china_test_units=announced_1858_units` (`…00000339`); 2 delivered |
| c10 | test-unit owners → `request_test_unit_return` | `consumer_requests.test_unit_return=aggregate_request_recorded` (`…00000378`); 1 delivered |
| c11 | regular purchasers → `report_mainland_battery_incident` | `domestic_incidents.consumer_report=recorded` (`…00000420`); 1 delivered |
| c12 | ATL → `issue_battery_nonconnection_statement`; Samsung → `issue_external_heating_statement` | two qualified account records (`…00000462–463`); 2 delivered |
| c13 | regular purchasers → `record_public_safety_dispute` | `domestic_dispute.consumer_position=dispute_recorded` (`…00000503`); 2 delivered |
| c14 | Samsung → `issue_china_recall_handling_apology` | `domestic_dispute.samsung_apology=recorded` (`…00000541`); 1 delivered |
| c15 | airline gate → `record_aircraft_note7_incident` | `aircraft_incident.report=recorded` (`…00000579`); 0 delivered |
| c16 | Samsung → `conduct_production_safety_review` | `product_exit.internal_review=recorded` (`…00000617`); 1 delivered |
| c17 | Samsung → `announce_production_suspension` | `product_exit.production_suspension=announced` (`…00000653`); 0 delivered |
| c18 | Samsung → `announce_permanent_product_stop` | `product_exit.permanent_stop=announced` (`…00000689`); 0 delivered |
| c19 | Samsung → `announce_full_china_recall` | `recall.china_full=announced_190984_units` (`…00000727`); 0 delivered |
| c20 | regular purchasers → `file_represented_consumer_litigation` | `post_recall.consumer_litigation=filed_recorded` (`…00000767`); 1 delivered |
| c21 | Samsung → `conduct_internal_root_cause_investigation` | `post_recall.internal_investigation=recorded` (`…00000805`); 1 delivered |
| c22 | Samsung → `commission_independent_investigation` | `post_recall.third_party_commission=recorded` (`…00000843`); 0 delivered |
| c23 | consortium → `conduct_independent_investigation`; Samsung → `respond_to_consumer_litigation` | two deltas (`…00000880–881`); 1 delivered |
| c24 | consortium → `publish_independent_findings` | `investigation.third_party_findings=published_claim_recorded` (`…00000919`); 0 delivered |
| c25 | Samsung → `publish_final_investigation_report` | `investigation.samsung_final_report=published_claim_recorded` (`…00000956`); 1 delivered |
| c26–c29 | All eight actors wait | no delta and no delivery; c29 is the terminal barrier |

The early chain is information-dependent: P_3's c03 report reaches Samsung at
c04 before the selected initial account. Testing and shipment delay are separate
manufacturer choices; neither is a hidden environment update. The regulator's
c08 requirement arrives before Samsung records the limited recall at c09. The
test-owner Population then records a request, not a refund or return completion.

The domestic chain keeps disagreement rather than resolving it. P_7's c11 report
reaches Samsung and ATL at c12. Their two accepted actions are records of
contested accounts. Only after both statements are delivered at c13 does P_7
record its dispute; Samsung's c14 apology concerns handling and is not transformed
into an admission of defect.

P_8's c15 action is explicitly an incident-notification representation gate.
The physical fire is not caused by its decision. Samsung receives the record at
c16, then separately records internal review, suspension, permanent stop and
full mainland recall. The release contains no production volume, aviation ban,
completed return or recall-effectiveness state.

The post-recall chain also separates process from finding. P_9 can begin only
after receiving Samsung's commission. Its investigation record at c23 does not
publish a finding. Publication at c24 sends a qualified account, delivered at
c25 before Samsung's own final-report record. No 2017 finding appears in a 2016
observation or message.

All 28 descriptive expectations are met in this selected baseline. That is a
property of this exposed-Draft Rule configuration, not a historical score and
not a condition for evidence validity.

## Mechanism reading

### Direct run evidence

The runtime uses one common declarative Rule implementation across eight actors.
Each domain field has one authorized handler. Multiple actors can act on the
same coordinate because their state writes are separate. The reducer validates
effects; the backend cannot complete payments, change production quantities,
resolve litigation or declare physical causation.

Actual delivery and retained participant memory determine the guarded decisions.
The canonical trace has no rejected non-default action, so it does not alone
demonstrate the common rejection/retry contract; synthetic runtime tests and
foreign-authority checks retain that responsibility.

### Interpretation and probe evidence

The useful modeled structure is the separation among incident report, public
account, dispute, corporate response, recall notice, consumer request, aircraft
notification, production decision, investigation process, independent finding
and manufacturer report. This avoids treating Draft relation endpoints or a
headline chronology as one automatic causal chain.

Two freshly admitted local construction probes test the information boundary.
They are not formal current releases or scientific comparisons:

| Changed configuration | Observed response | Evidence boundary |
|---|---|---|
| P_7's domestic-report row waits on a notice unavailable in its c11–c13 window | Domestic report, both accounts, dispute and apology remain open; full-China recall and later investigation continue. 1,080 trace records, 1,131 nodes, 3,188 edges; five unmet expectations. | Fresh A/B, generated-ID invariance, replay and independent publication pass with zero unresolved transport. |
| P_9→Samsung findings route latency changes from 1 to 5 ticks | P_9 publishes at c24; delivery occurs at c29 after Samsung's c25–c28 window, so only the Samsung final report remains open. 1,099 trace records, 1,150 nodes, 3,255 edges. | The information delay is structural, not an estimated historical delay or intervention effect. All integrity checks pass. |

Probe run IDs are `run.dd36be7b954c4893e4120959` and
`run.65e0134d3e0ef5d6493d813b`. Each probe was re-admitted and compiled from a
configuration successor before execution; no sealed package or output was
patched. The initial attempt to delete a declared-intent Rule row failed closed
with `rule_intent_coverage_mismatch` and is retained in ignored custody.

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

The source set is noisy and internally inconsistent. Draft relation/transaction
endpoints misidentify consumers, suppliers and the regulator. The current
scenario resolves runtime authority from actor-local actions and qualified
narrative, and records every disposition; it does not claim to settle the
historical disputes. Full Draft exposure informs every selected action and
window, so apparent sequence alignment is not predictive evidence.

P_2 has no exposed autonomous choice and remains context. P_8 and P_5 use
explicitly disclosed representation choices: notification of an experienced
incident and a qualified return request after eligibility. Three Populations
represent aggregate records, not unanimous individual behavior. There is no
device, battery, money, inventory, production, injury, aviation-enforcement,
court or public-trust mechanism.

This output supports dataset-conditioned construction, bounded participant
behavior, deterministic integrity/replay and trace-derived process description.
It does not support historical fit, parameter calibration, held-out evaluation,
recall or policy effectiveness, causal attribution, scientific validity or
universal generality. LLM and RuleLLM remain planned; no model decision or
cross-backend evidence is present.
