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
| Package | h2epr.event-package.0616.v1; 52dbf7578a745e66cf8066f8743ac91f129deafb849b9fc92d6802fa32b0b5a5 |
| Rule binding | 5b7dcacd27eee069208fa777908807db91c831c0cd8b00e1fb9330b2a07646b4 |
| Realization | h2epr.0616.rule-realization.v1; 459360b6f9214ff7dd08bef5808d86d137adf828068a7bf278f2fc2f41396dae |
| Shared configuration | h2epr.0616.comparison.v1; 0bdb117b630e2cd6f2ff12f369a66a1185698d15bf63b1dd57c164598315c424 |
| Rule configuration | h2epr.0616.rule.v1; 20d445e58a239b63ec013b51833040b815d4a2a24c19edf8bea145708952e1ac |
| Run | run.26b57124e29d077af3150e02 |
| Run manifest | f0002f2c2161afd255134d062898cfa0672a191509334d80d13430d9abbe4b7a |
| Trace | c326760686ce7e9652546955bc7a2fddaa72ee5d1941af073796d1c7ed96234b |
| Terminal state | 5c8ecedefd2211d9f41636bdd47a144ec079ed9de97135f764e589ec5f745472 |
| Run seal | b4834493f4d893676e58f2a221376f9f6eec72ae06f3e7ec34fbd595c7a0c438 |
| Generated EPG seal | bf365f5d1306ead1ac0fd46f6feaddfe6e55d8b49546b3512a92f10bdf308dde |
| Physical raw custody | .local-runtime/h2epr-simulation/runs/benchmark/singhealth_data_breach/rule/2026-09-06-semantic-contracts-final/materialization-a |

Fresh A/B materializations are byte-identical across all eight output roles and
the run receipt. The generated-ID probe changes opaque run and record IDs while
preserving semantic trace/graph structure and exact terminal state. The
publisher independently reconstructs the run manifest, H2EPR/MASim source
inventories, observation/memory projections, trace chain, tick/run seals,
authoritative replay, counts, outcomes and graph; it also rematerializes from the
admitted package.

## Complete-output coverage

The complete machine scan traversed 782 trace
records, 820 graph nodes and
2,318 graph edges. Trace and graph IDs are unique,
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
782 trace-record nodes and nine state-entity
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
| part_of | 29 |
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
suffixes abbreviate `trace.run.26b57124e29d077af3150e02.`.

| Coordinate | Accepted participant choices | Reducer effects and delivery count |
| --- | --- | --- |
| c01 | `attributed_whitefly_activity_gate` → `record_retrospectively_attributed_access` | `incident.attributed_access=qualified_recorded` (`…00000033`); 0 delivered |
| c02 | `attributed_whitefly_activity_gate` → `record_concentrated_exfiltration_account` | `incident.concentrated_exfiltration=reported_1_5m_identity_and_160k_medication_records` (`…00000070`); 0 delivered |
| c03 | `singhealth_data_owner` → `record_organizational_breach_detection` | `response.detection=recorded_2018_07_04` (`…00000109`); 0 delivered |
| c04 | `ihis_system_operator` → `verify_breach_scope` | `ihis_system_operator.scope_verification=qualified_scope_recorded` (`…00000151`); 1 delivered |
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
| ihis_system_operator.scope_verification | qualified_scope_recorded | True |
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
effects. Public prestate, IHiS-private assessment, actual delivery and retained
runtime memory activate the selected rows. Stage descriptions and Reference
content are absent; event-specific vocabulary remains visible before its result.
No common-code SingHealth branch supplies the choices.

At c04, the `verify_breach_scope` disposition (`…00000142`) admits the qualified
report and writes `ihis_system_operator.scope_verification` (`…00000151`). The
ministry-bound summary (`…00000128`) carries typed status and scale. Its receipt
before c05 is required for disclosure (`…00000186`, delta `…00000191`). The
ministry never receives the private field in its state projection. Shared
admission checks that field independently; an eligible sender's positive message
cannot substitute for a qualified internal record. Neither record nor message
establishes that technical forensic verification occurred.

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

Eight fresh Rule probes exercise the scope/disclosure and findings-content contracts. Each used admitted
assets, A/B materialization, generated-ID perturbation and independent publication;
all sealed, replayed and closed transport. They are local contract evidence, not
current canonical event releases or historical counterfactuals.

| Changed owner/input | Observed response | Evidence boundary |
|---|---|---|
| Unresolved internal assessment and summary | No disclosure; 13 unmet expectations; 727 records / 765 nodes / 2,125 edges | `run.e25ddb70e5719796b3f84007`; a well-formed negative report permits a valid open run |
| Qualified internal record, withdrawn summary | No disclosure; 12 unmet; 727 / 765 / 2,125 | `run.e6bd38a63b109de8f5256db2`; world feasibility does not replace qualifying information |
| Ministry summary withheld | No disclosure; 12 unmet; 724 / 762 / 2,115 | `run.3725264d3efa8b81d99a6133`; IHiS can record assessment without making ministry receipt true |
| IHiS→ministry route latency 1→3 ticks | Disclosure shifts c05→c07; all 17 expectations met; 782 / 820 / 2,318 | `run.b6555b325cffe11157bf70b0`; every message on that directed route is delayed, not only the scope summary |
| Same route latency 1→9 ticks | Summary reaches c13 after the c05–c08 policy window; no disclosure; 12 unmet; 727 / 765 / 2,125 | `run.2af7299510db9f43159bb358`; window expiry is selected policy behavior, not a shared legal time lock |
| Summary withheld and Rule receipt guard removed | c05 attempt rejected: `information_requirement_not_met`; 12 unmet; 726 / 764 / 2,121 | `run.7d3bcba393d722b962a5cefb`; bypassing policy does not bypass shared receipt admission |
| Positive summary with unresolved internal record | c05 attempt rejected: `precondition_not_met`; 13 unmet; 729 / 767 / 2,131 | `run.6421b226f4fd6bf448c3ea34`; information and world feasibility have independent authority |
| COI findings marked withdrawn | Disclosure remains c05; neither PDPC penalty is selected; 5 unmet; 763 / 801 / 2,250 | `run.f421d679f1e85f1c289e57af`; a message type alone does not satisfy the positive-content Rule guards; this is policy selection, not shared penalty admission |

Physical probe custody is retained under
`.local-runtime/h2epr-simulation/working/2026-09-06-contracts/singhealth-probes-final/`,
with one named case directory per row. Malformed, empty and conflicting/latest
updates are additionally covered by the event-neutral
[information-contract tests](../../../tests/runtime/test_information_contracts.py).
The withdrawn case supplies a withdrawn summary as its first report; it does not
claim that the event ran a positive-then-withdrawn cycle. Latest-update precedence
is demonstrated by synthetic tests. The event's internal assessment is one-shot.

## Limitations

The current observation profile exposes declared event vocabulary, including
names associated with later events. It does not provide historically
prefix-clean information. Rule windows and receipt guards are selected
policy assumptions except where explicit shared handler requirements apply.
Configured decision reasons are rationale; hash-linked observations, actual
message content, dispositions and deltas provide generated evidence.

The frozen set is uneven and secondary. The May 2015 date is an affected-record
cohort boundary, not direct proof that intrusion began then. Two breach extracts
are duplicated/truncated; several records are tangential or retrospective. The
current Source Profile and Scenario disclose these weaknesses rather than
reconciling them with external material.

Whitefly remains a later published attribution claim. P_1 is an explicit
representation gate, not a technical adversary simulation, and its structural
presence and capability names expose attribution-related vocabulary earlier.
This limits information-clean participant experiments. There is no malware,
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
