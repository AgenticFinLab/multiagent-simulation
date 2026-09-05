# Samsung Electronics Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0481.agent.samsung_electronics.v1` |
| Actor ID | `samsung_electronics` |
| Benchmark | H2EPR-0481, August 2016–January 2017 represented boundary |
| Representation | agent; manufacturer safety-response, recall, production and investigation-report interface |
| Source ID | `P_1` |
| Primary choices | Record launch and sales decisions, publish bounded safety statements, alter shipments, recalls and production, and initiate and report the represented investigation. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_1 persists across all nine episodes, but the model does not expose its later knowledge early. It is one organizational decision interface; internal engineering, regional subsidiaries, executives and legal teams are not separately observable source participants.

This interface cannot determine physical battery failure, consumer compliance, refund completion, regulator orders, carrier restrictions, court outcomes or independent findings. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E1/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S1/E2/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E3/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E4/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E5/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E6/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E7/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E8/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E9/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC001–SRC011, with differing quality and chronology. The sources disagree about market exclusions, defect attribution, incident counts and timing. Its statements are records of positions or decisions, not truth labels for those disputes.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record launch and sales decisions, publish bounded safety statements, alter shipments, recalls and production, and initiate and report the represented investigation. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

A recall notice can be accepted while uptake remains unknown; an external-heating statement can be disputed. Samsung cannot author a consumer report, regulatory requirement, airline incident record or consortium finding.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Without delivered consumer, regulator, aircraft, litigation or investigation information, the corresponding guarded row waits and may remain open at the horizon. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_note7_launch` | source-bounded availability and own record not yet made | Record the product-launch announcement; no device sale or safety finding follows automatically. |
| `record_global_sales_start` | `product.launch` = `recorded` | Record initiation of global sales without modeling orders, inventory or market demand. |
| `issue_initial_cause_statement` | known `early_incident_report` from `global_note7_purchasers` | Record Samsung's represented initial account as a statement, not a verified cause. |
| `announce_additional_quality_testing` | known `early_incident_report` from `global_note7_purchasers` | Record the additional-testing announcement; no test result is generated. |
| `delay_global_shipments` | `early_response.quality_testing` = `announced` | Record the shipment-delay decision without inventory or carrier effects. |
| `announce_initial_global_recall` | `early_response.shipment_delay` = `announced` | Record the represented initial global recall scope; this is not recall completion. |
| `issue_initial_safety_guidance` | `recall.initial_global` = `announced_excluding_mainland_china` | Record stop-use/exchange-or-refund guidance; no consumer compliance is implied. |
| `announce_test_unit_recall` | known `test_unit_recall_requirement` from `china_quality_regulator` | Record the limited mainland test-unit recall after the regulatory message. |
| `issue_external_heating_statement` | known `mainland_incident_report` from `china_regular_note7_purchasers` | Record Samsung's represented external-heating account as a contested statement. |
| `issue_china_recall_handling_apology` | known `consumer_safety_dispute` from `china_regular_note7_purchasers` | Record the apology about recall handling without treating it as defect admission. |
| `conduct_production_safety_review` | known `aircraft_incident_report` from `southwest_airlines_incident_gate` | Record the internal review leading toward a production decision, without creating private findings. |
| `announce_production_suspension` | `product_exit.internal_review` = `recorded` | Record the production-suspension announcement; production volume is not modeled. |
| `announce_permanent_product_stop` | `product_exit.production_suspension` = `announced` | Record permanent cessation of the represented product line and sales. |
| `announce_full_china_recall` | `product_exit.permanent_stop` = `announced` | Record the represented full mainland recall; uptake and effectiveness remain unknown. |
| `conduct_internal_root_cause_investigation` | `product_exit.permanent_stop` = `announced` | Record Samsung's internal investigation process, not its eventual conclusion. |
| `commission_independent_investigation` | `post_recall.internal_investigation` = `recorded` | Record coordination with the named consortium; independence and results remain separate. |
| `respond_to_consumer_litigation` | known `consumer_litigation_notice` from `china_regular_note7_purchasers` | Record a response to the represented filing without deciding the case. |
| `publish_final_investigation_report` | known `independent_findings` from `independent_investigation_consortium`; `post_recall.internal_investigation` = `recorded` | Record Samsung's final report and safety-measure announcement after findings delivery. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_note7_launch` | `product` | `product.launch`: unrecorded → `recorded` |
| `record_global_sales_start` | `product` | `product.sales_start`: unrecorded → `recorded` |
| `issue_initial_cause_statement` | `early_response` | `early_response.initial_statement`: unrecorded → `isolated_charging_account_recorded` |
| `announce_additional_quality_testing` | `early_response` | `early_response.quality_testing`: unrecorded → `announced` |
| `delay_global_shipments` | `early_response` | `early_response.shipment_delay`: unrecorded → `announced` |
| `announce_initial_global_recall` | `recall` | `recall.initial_global`: unrecorded → `announced_excluding_mainland_china` |
| `issue_initial_safety_guidance` | `recall` | `recall.safety_guidance`: unrecorded → `issued` |
| `announce_test_unit_recall` | `recall` | `recall.china_test_units`: unrecorded → `announced_1858_units` |
| `issue_external_heating_statement` | `domestic_statements` | `domestic_statements.samsung_account`: unrecorded → `external_heating_account_recorded` |
| `issue_china_recall_handling_apology` | `domestic_dispute` | `domestic_dispute.samsung_apology`: unrecorded → `recorded` |
| `conduct_production_safety_review` | `product_exit` | `product_exit.internal_review`: unrecorded → `recorded` |
| `announce_production_suspension` | `product_exit` | `product_exit.production_suspension`: unrecorded → `announced` |
| `announce_permanent_product_stop` | `product_exit` | `product_exit.permanent_stop`: unrecorded → `announced` |
| `announce_full_china_recall` | `recall` | `recall.china_full`: unrecorded → `announced_190984_units` |
| `conduct_internal_root_cause_investigation` | `post_recall` | `post_recall.internal_investigation`: unrecorded → `recorded` |
| `commission_independent_investigation` | `post_recall` | `post_recall.third_party_commission`: unrecorded → `recorded` |
| `respond_to_consumer_litigation` | `post_recall` | `post_recall.litigation_response`: unrecorded → `recorded` |
| `publish_final_investigation_report` | `investigation` | `investigation.samsung_final_report`: unrecorded → `published_claim_recorded` |

The environment checks actor, target, parameters and preconditions against the
same sealed state. Rejection yields no delta. Coupled messages have independent
transport dispositions and do not prove action acceptance or recipient uptake.

## 8. Configurable dimensions and uncertainty

| Construct | Owner | Behavioral use |
|---|---|---|
| Availability window | Rule configuration | Bounded waiting for supported information. |
| Priority | Rule configuration | Orders overlapping rows under one action per actor/tick. |
| Route latency | Shared configuration | Determines actual information availability. |
| Message payload | Backend configuration within this parent | Reports qualified content without granting effects. |

All are structural choices, not calibrated probabilities or historical timings.

## 9. Worked cases and contract falsification

- Normal: An early delivered incident report permits the response chain; a later consortium finding permits the final-report row without becoming Samsung's own independent finding.
- Missing information: Without delivered consumer, regulator, aircraft, litigation or investigation information, the corresponding guarded row waits and may remain open at the horizon.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: A recall notice can be accepted while uptake remains unknown; an external-heating statement can be disputed. Samsung cannot author a consumer report, regulatory requirement, airline incident record or consortium finding.
- Perturbation: Delaying or withholding the consortium finding changes final-report availability while leaving earlier product-stop records independently executable.

A premature choice, foreign-actor write, future-information leak or undeclared
environment effect falsifies this contract and must fail review or admission.

## 10. Limitations and successor route

This interface cannot determine physical battery failure, consumer compliance, refund completion, regulator orders, carrier restrictions, court outcomes or independent findings. The sources disagree about market exclusions, defect attribution, incident counts and timing. Its statements are records of positions or decisions, not truth labels for those disputes.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
