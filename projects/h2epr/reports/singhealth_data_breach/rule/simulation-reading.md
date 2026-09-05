# SingHealth Data Breach Rule simulation reading

## Run identity

This is a simulation-only reading of the current seed-0 Rule output for
H2EPR-0616. Construction used exactly the three admitted dataset files with the
complete Draft exposed; model and network access were denied. The
[compact release](../../../releases/singhealth_data_breach/rule/) contains independently derived
verification receipts and reproduction guidance. The
[event entry](../../../events/singhealth_data_breach/) links each semantic owner.

| Item | Exact identity |
| --- | --- |
| Package | h2epr.event-package.0616.v1; 9d17581f17e994b2aba4252c8a7457c7b03ecd8f3e9003c83268bf954664a16c |
| Rule binding | f304a0fd41650859f626ebc89f7541062ba7e0f7166a141870b68ce519da2d4f |
| Realization | h2epr.0616.rule-realization.v1; c537c33a4eaabfe94c09f86ce0eabb20500f918e70c73421e0e6c23d6cb54e72 |
| Shared configuration | h2epr.0616.comparison.v1; 9086a428bdafd3060dd6c8eceebeedcdf2fe8171977808ebec6b42cead5c8ee0 |
| Rule configuration | h2epr.0616.rule.v1; 7be960405c4409028441c4f2c97efd22e26fa995900fbafa804f7198ce2c2200 |
| Run | run.5db9a323beb010817c521f46 |
| Run manifest | 847b59da4f08b2583796511417ff9051ef10378b2452a61b0e1a5f19d8d1fef5 |
| Trace | 3e20d90bc3ad4a15972286ac80c3acb3e5f7c029fecf37a6c9e46a34e3ebb5f8 |
| Terminal state | e27b32d9df9e035e2e7ad89a073f82397d4491db6ee597cd9b9efc82c649b07d |
| Run seal | e8393967e403da8ad215b1c81186fa6952ca324328332d0423bd25ca646d4fe0 |
| Generated EPG seal | 04429d76666f687d61eb9ad220675f348a07833390986b63611d448b20d5d8ae |
| Physical raw custody | .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-05-stage-d/materialization-a |

Fresh A/B materializations are byte-identical across all eight output roles and
the run receipt. The generated-ID probe changes opaque run and record IDs while
preserving semantic trace/graph structure and exact terminal state. The
publisher independently reconstructs the run manifest, H2EPR/MASim source
inventories, observation/memory projections, trace chain, tick/run seals,
authoritative replay, counts, outcomes and graph; it also rematerializes from the
admitted package.

## Complete-output coverage

The complete machine scan traversed 782 trace
records, 819 graph nodes and
2,317 graph edges. Trace and graph IDs are unique,
every edge endpoint resolves, and the union of graph source-trace references
equals all 782 records. Semantic review covered
all 17 non-default actions, 17 deltas, 18 messages, six annotations, every
coordinate and every terminal expectation. Repeated no-op, observation and
provenance rows were verified by complete-family traversal and independent
reconstruction rather than reproduced as a raw transcript.

| Trace family | Count | Coverage meaning |
| --- | --- | --- |
| observation / participant_decision / action_intent / action_disposition | 160 each | Eight complete actor paths at each of 20 coordinates |
| Non-default / no-op actions | 17 / 143 | All admitted; zero rejected actions in the canonical baseline |
| message_intent / message_disposition | 18 / 36 | Every item queued and delivered; zero unresolved transport |
| state_delta | 17 | One actor-authorized record transition per non-default action |
| tick_open / tick_commit / tick_seal | 20 each | Full horizon and sealed authoritative replay |
| stage_entry / generated_annotation | 4 / 6 | Navigation entries and declared state summaries |
| run_seal | 1 | Complete evidence and terminal accounting |

The graph contains one generated event, 20 coordinates, eight participants,
782 trace-record nodes and eight state-entity
nodes. Its complete edge-family ledger is:

| Edge family | Count |
| --- | --- |
| addressed_to | 18 |
| aggregates | 20 |
| based_on | 160 |
| caused_by | 35 |
| changes | 17 |
| commits | 17 |
| decided_by | 160 |
| disposes | 196 |
| emitted_by | 160 |
| involves | 13 |
| learns_result_from | 152 |
| observes_for | 160 |
| occurs_at | 782 |
| part_of | 28 |
| participates_in | 8 |
| projects | 160 |
| received_from | 18 |
| retains_memory_from | 152 |
| seals | 21 |
| sent_by | 18 |
| stage_of | 4 |
| succeeds | 18 |

`received_from` proves actual delivery. `learns_result_from` and
`retains_memory_from` capture runtime decision memory. `caused_by` and annotation
provenance describe implementation ancestry, not historical causality or a
minimal set of influential decisions.

## Generated trajectory

An opening `unrecorded` value means no modeled record has yet been accepted; it
does not assert that an underlying historical fact was false. This table lists
every coordinate, every non-default disposition and all reducer deltas. Trace
suffixes abbreviate `trace.run.5db9a323beb010817c521f46.`.

| Coordinate | Accepted participant choices | Reducer effects and delivery count |
| --- | --- | --- |
| c01 | `attributed_whitefly_activity_gate` → `record_retrospectively_attributed_access` | `incident.attributed_access=qualified_recorded` (`…00000033`); 0 delivered |
| c02 | `attributed_whitefly_activity_gate` → `record_concentrated_exfiltration_account` | `incident.concentrated_exfiltration=reported_1_5m_identity_and_160k_medication_records` (`…00000070`); 0 delivered |
| c03 | `singhealth_data_owner` → `record_organizational_breach_detection` | `response.detection=recorded_2018_07_04` (`…00000109`); 0 delivered |
| c04 | `ihis_system_operator` → `verify_breach_scope` | `response.scope_verification=qualified_scope_recorded` (`…00000151`); 1 delivered |
| c05 | `singapore_ministry_of_health` → `issue_public_breach_disclosure` | `disclosure.ministry_notice=issued` (`…00000191`); 2 delivered |
| c06 | `prime_minister_response_interface` → `publish_leadership_response` | `disclosure.leadership_response=published` (`…00000231`); 1 delivered |
| c07 | `singapore_ministry_of_health` → `direct_public_health_security_review` | `review.ministry_direction=issued` (`…00000270`); 1 delivered |
| c08 | `ihis_system_operator` → `initiate_directed_security_review`; `singapore_ministry_of_health` → `establish_committee_inquiry_path` | `review.ihis_review=initiated` (`…00000311`); `inquiry.ministry_mandate=issued` (`…00000312`); 1 delivered |
| c09 | `singhealth_committee_of_inquiry` → `conduct_breach_inquiry` | `inquiry.committee_process=recorded` (`…00000351`); 2 delivered |
| c10 | `singhealth_committee_of_inquiry` → `publish_findings_and_recommendations` | `inquiry.public_findings=qualified_findings_and_16_recommendations_published` (`…00000395`); 0 delivered |
| c11 | `personal_data_protection_commission` → `issue_ihis_penalty_order` | `enforcement.ihis_penalty=sgd_750000_order_recorded` (`…00000438`); 4 delivered |
| c12 | `personal_data_protection_commission` → `issue_singhealth_penalty_order` | `enforcement.singhealth_penalty=sgd_250000_order_recorded` (`…00000477`); 1 delivered |
| c13 | `ihis_system_operator` → `announce_security_improvement_program`; `singhealth_data_owner` → `accept_penalty_and_announce_governance_program` | `remediation.ihis_program=announced` (`…00000519`); `remediation.singhealth_program=acceptance_apology_and_program_announced` (`…00000520`); 1 delivered |
| c14 | `singapore_ministry_of_health` → `record_reform_oversight_program` | `remediation.ministry_oversight=recorded` (`…00000558`); 2 delivered |
| c15 | `symantec_attribution_publisher` → `publish_whitefly_attribution_report` | `attribution.public_report=whitefly_claim_recorded` (`…00000600`); 0 delivered |
| c16 | All eight actors wait | No state delta; 2 delivered |
| c17 | All eight actors wait | No state delta; 0 delivered |
| c18 | All eight actors wait | No state delta; 0 delivered |
| c19 | All eight actors wait | No state delta; 0 delivered |
| c20 | All eight actors wait | No state delta; 0 delivered |

The information chain is explicit. SingHealth records detection at c03 and its
notice arrives at IHiS before c04 verification. IHiS sends separate scope
summaries; the ministry receives one before c05 disclosure. The public notice
reaches the leadership interface before c06, and the resulting direction enables
distinct c07 review and c08 inquiry paths. The committee receives the mandate at
c09, publishes findings at c10, and PDPC receives them before its two separate
orders at c11 and c12. Recipient-specific penalty notices arrive before the c13
organizational program records; ministry oversight waits for both program
messages and occurs at c14.

Symantec's c15 attribution publication is independent of the inquiry/enforcement
chain. It is delivered at c16 and never appears in earlier actor memory. The P_1
representation gate emits no message at all, so its structural identity cannot
serve as an early public attribution. Coordinates 17–20 contain only waiting and
terminal accounting; all 18 messages reach a final delivered state.

Every descriptive expectation is assessed below. The values are records and
qualified claims: penalty order is not payment, program announcement is not
implementation, and attribution publication is not attacker-identity truth.

| Expectation suffix | Observed value | Met |
| --- | --- | --- |
| incident.attributed_access | qualified_recorded | True |
| incident.concentrated_exfiltration | reported_1_5m_identity_and_160k_medication_records | True |
| response.detection | recorded_2018_07_04 | True |
| response.scope_verification | qualified_scope_recorded | True |
| disclosure.ministry_notice | issued | True |
| disclosure.leadership_response | published | True |
| review.ministry_direction | issued | True |
| review.ihis_review | initiated | True |
| inquiry.ministry_mandate | issued | True |
| inquiry.committee_process | recorded | True |
| inquiry.public_findings | qualified_findings_and_16_recommendations_published | True |
| enforcement.ihis_penalty | sgd_750000_order_recorded | True |
| enforcement.singhealth_penalty | sgd_250000_order_recorded | True |
| remediation.singhealth_program | acceptance_apology_and_program_announced | True |
| remediation.ihis_program | announced | True |
| remediation.ministry_oversight | recorded | True |
| attribution.public_report | whitefly_claim_recorded | True |

## Mechanism reading

### Direct run evidence

Eight actors use one declarative Rule implementation and one authoritative
environment. Single-writer handlers preserve the authority of SingHealth, IHiS,
the leadership interface, ministry, inquiry committee, PDPC, Symantec and the
retrospective attack representation. The reducer, not the backend, owns record
effects. Public prestate, actual delivery and retained runtime memory jointly
activate later rows; Draft stage labels, Reference content and future findings
are absent from observations. No common-code SingHealth branch supplies the
choices.

The canonical run accepts all 17 selected records and meets all 17 descriptive
expectations. It contains no rejected non-default action, so the run alone does
not prove foreign-authority rejection or retry after changed information; those
are shared negative contracts. Its direct contribution is a fully sealed example
of multi-hop information activation and actor-specific result boundaries.

### Interpretation and construction probes

The representation separates conditions/results from choices more sharply than
the Draft. Affected patients are context because no response choice is exposed.
Database theft and inadequate controls are not choices by their victims. COI
findings, PDPC orders and organization responses are distinct transitions. The
Draft's claim of implemented reforms is reduced to announced programs and
oversight because no executable completion or effectiveness mechanism exists.

Two freshly admitted local probes test this reading without becoming current
event releases or scientific counterfactuals:

| Changed owner/input | Observed response | Evidence boundary |
|---|---|---|
| Rule scope-verification row additionally requires the later attribution report, which cannot arrive in its c04–c07 window | Only the two qualified incident records, detection and later Symantec publication occur. 720 trace records, 757 nodes, 2,100 edges; 13 downstream expectations remain open. | Fresh A/B, ID perturbation, replay, graph and independent publication pass with zero unresolved transport. This is a missing-information construction test. |
| Shared COI→PDPC findings latency changes from 1 to 7 ticks | Inquiry findings still publish at c10 and deliver at c17, after both penalty windows. Two penalties, two organizational programs and ministry oversight remain open. 763 records, 800 nodes, 2,249 edges. | The message reaches terminal delivery. Seven ticks are a routing perturbation, not an estimated historical delay or policy counterfactual. |

The probe run IDs are `run.5fc1d86747694ec2df5eeeb9` and
`run.7ba987891680155e0f1c69d6`. Each variant received a new configuration,
realization, assembly, package and release identity before execution; neither was
created by editing an admitted package or generated output.

## Limitations

The frozen set is uneven and secondary. The May 2015 date is an affected-record
cohort boundary, not direct proof that intrusion began then. Two breach extracts
are duplicated/truncated; several records are tangential or retrospective. The
current Source Profile and Scenario disclose these weaknesses rather than
reconciling them with external material.

Whitefly remains a later published attribution claim. P_1 is an explicit
representation gate, not a technical adversary simulation, and its structural
presence cannot leak identity into 2018 observations. There is no malware,
network topology, patient-level behavior, private medical data, payment ledger,
implemented-control state, breach probability or security-effectiveness metric.
Logical coordinates and one-tick routes are authored ordering choices.

This output supports dataset-conditioned construction, state/information-aware
deterministic execution, integrity/replay evidence and trace-derived Generated
EPG description. It does not establish intrusion timing, attacker truth,
historical fit, parameter calibration, held-out evaluation, cybersecurity or
regulatory effectiveness, policy effects, causality, scientific validity or
universal generality. LLM and RuleLLM remain planned; no model decision or
cross-backend evidence appears here.
