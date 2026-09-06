# Lebanese Civil War Rule simulation reading

## Run identity

This is a simulation-only reading of the current seed-0 Rule output for
H2EPR-0892. Construction used exactly the three admitted dataset files with the
complete Draft exposed; model and network access were denied. The
[compact release](../../../releases/lebanese_civil_war/rule/) contains independently derived
verification receipts and reproduction guidance. The
[event entry](../../../events/lebanese_civil_war/) links each semantic owner.

| Item | Exact identity |
| --- | --- |
| Package | h2epr.event-package.0892.v1; 3c47bb0d6f91b5c5d716c2fb509c44d6cb543b5ef83c8e38333dd3e4533bfac4 |
| Rule binding | e85d9ea15786c3d954fb4be081c63663b7d0e453ced104154fc4ef82d2fef45a |
| Realization | h2epr.0892.rule-realization.v1; 697ea2f709c55e2c94a1358a054c636d5796951be0f988ad070a43786faa6d32 |
| Shared configuration | h2epr.0892.comparison.v1; 4c44629bc39c37e621dd7a8b016e820a9fe951ef823d946aac8065b5ceda34be |
| Rule configuration | h2epr.0892.rule.v1; 9cf54ce1096e4d891f1f66a5893a2b6886ccaa4bcf4b4352886f8bd04cb7fff6 |
| Run | run.391644c9adfa091e6d2109e9 |
| Run manifest | 3980f0b5d0e063b24d0e631ed66d4be4613fc76123c038a8dd71e02cb2caffaa |
| Trace | 29fb302aa459662f3aaeb40696c7af45df2eb224b5d7d20ea9152910feeb565b |
| Terminal state | 3aff7c57db691e4088eea06b88cb8179c1f21b78d108d437998c2fe68f5cde25 |
| Run seal | 537ff58de661c7abf5926fd15a4046a0619893a15e3cab8af3b714b04805f250 |
| Generated EPG seal | ed5c47ee5094f03c87a8f8d8898fcaf6a449e676294917decbd055626adccf19 |
| Physical raw custody | .local-runtime/h2epr-simulation/runs/benchmark/lebanese_civil_war/rule/2026-09-06-semantic-contracts/materialization-a |

Fresh accepted A/B materializations are byte-identical across all eight output
roles and the run receipt. The generated-ID probe changes opaque run and record
IDs while preserving semantic trace/graph structure and exact terminal state.
The publisher independently reconstructs the run manifest, current H2EPR/MASim
source inventories, observation/memory projections, trace chain, tick/run seals,
authoritative replay, counts, outcomes and graph; it also rematerializes from the
admitted package.

## Complete-output coverage

The complete machine scan traversed 922 trace
records, 963 graph nodes and
2,789 graph edges. Trace and graph IDs are unique,
every edge endpoint resolves, and the union of graph source-trace references is
exactly all 922 records. Semantic review
covered all 33 non-default actions, 33 deltas, 47 messages, eight annotations,
every coordinate and all 33 terminal expectations. Repeated no-op, observation
and provenance rows were checked through complete-family traversal and
independent reconstruction rather than reproduced verbatim below.

| Trace family | Count | Coverage meaning |
| --- | --- | --- |
| observation / participant_decision / action_intent / action_disposition | 168 each | Eight complete actor paths at each of 21 coordinates |
| Non-default / no-op actions | 33 / 135 | All admitted; zero rejected non-default actions in the canonical baseline |
| message_intent / message_disposition | 47 / 94 | Every message queued and delivered; zero unresolved transport |
| state_delta | 33 | One actor-authorized record transition per non-default action |
| tick_open / tick_commit / tick_seal | 21 each | Full horizon and sealed authoritative replay |
| stage_entry / generated_annotation | 4 / 8 | Draft navigation entries and declared state summaries |
| run_seal | 1 | Complete evidence and terminal accounting |

The graph contains one generated event, 21 coordinates, eight participants,
922 trace-record nodes and eleven state-entity
nodes. Its complete edge-family ledger is:

| Edge family | Count |
| --- | --- |
| addressed_to | 47 |
| aggregates | 21 |
| based_on | 168 |
| caused_by | 80 |
| changes | 33 |
| commits | 33 |
| decided_by | 168 |
| disposes | 262 |
| emitted_by | 168 |
| involves | 24 |
| learns_result_from | 160 |
| observes_for | 168 |
| occurs_at | 922 |
| part_of | 32 |
| participates_in | 8 |
| projects | 168 |
| received_from | 47 |
| retains_memory_from | 160 |
| seals | 22 |
| sent_by | 47 |
| stage_of | 4 |
| succeeds | 47 |

`received_from` proves actual delivery. `learns_result_from` and
`retains_memory_from` capture runtime memory. `caused_by` and annotation
provenance describe implementation ancestry, not historical causality,
responsibility or a minimal explanation of the war.

## Generated trajectory

An opening `unrecorded` value means that no modeled record has yet been accepted;
it does not say that an underlying historical proposition was false. The table
lists every coordinate, all non-default dispositions and every reducer delta.
Trace suffixes abbreviate `trace.run.391644c9adfa091e6d2109e9.`.

| Coordinate | Accepted participant choices | Reducer effects and delivery count |
| --- | --- | --- |
| c01 | `lebanese_front_record_interface` → `record_initial_front_participation`; `lebanese_national_movement` → `record_initial_lnm_participation`; `palestine_liberation_organization` → `record_initial_plo_participation` | `initial_conflict.front_participation=qualified_front_participation_recorded` (`…00000051`); `initial_conflict.lnm_participation=qualified_lnm_participation_recorded` (`…00000052`); `initial_conflict.plo_participation=qualified_plo_participation_recorded` (`…00000053`); 0 delivered |
| c02 | `lebanese_front_record_interface` → `record_front_beirut_campaign`; `lebanese_national_movement` → `record_lnm_beirut_campaign`; `palestine_liberation_organization` → `record_plo_west_beirut_position` | `beirut_territorial_records.front_campaign=east_beirut_campaign_recorded` (`…00000106`); `beirut_territorial_records.lnm_campaign=beirut_campaign_recorded` (`…00000107`); `beirut_territorial_records.plo_position=west_beirut_position_recorded` (`…00000108`); 9 delivered |
| c03 | `lebanese_joint_government_interface` → `record_syrian_intervention_request` | `state_authority.intervention_request=qualified_syrian_intervention_request_recorded` (`…00000150`); 3 delivered |
| c04 | `syrian_state_intervention_interface` → `record_initial_syrian_deployment` | `syrian_intervention.initial_deployment=deployment_recorded` (`…00000193`); 1 delivered |
| c05 | `lebanese_front_record_interface` → `record_continued_front_conflict`; `lebanese_national_movement` → `record_continued_lnm_conflict`; `palestine_liberation_organization` → `record_continued_plo_conflict`; `syrian_state_intervention_interface` → `record_syrian_territorial_consolidation` | `continued_conflict.front_record=continued_front_conflict_recorded` (`…00000237`); `continued_conflict.lnm_record=continued_lnm_conflict_recorded` (`…00000238`); `continued_conflict.plo_record=continued_plo_conflict_recorded` (`…00000239`); `syrian_intervention.territorial_consolidation=northern_eastern_presence_recorded` (`…00000240`); 3 delivered |
| c06 | `palestine_liberation_organization` → `record_cross_border_operations`; `syrian_state_intervention_interface` → `record_syrian_alignment_change` | `plo_operations.cross_border_record=qualified_cross_border_operations_recorded` (`…00000286`); `syrian_intervention.alignment_change=lnm_plo_support_recorded` (`…00000287`); 2 delivered |
| c07 | `israeli_state_intervention_interface` → `record_operation_litani` | `israeli_intervention.operation_litani=operation_litani_recorded` (`…00000331`); 4 delivered |
| c08 | `palestine_liberation_organization` → `record_litani_resistance`; `syrian_state_intervention_interface` → `record_continued_syrian_presence` | `plo_operations.litani_resistance=qualified_litani_resistance_recorded` (`…00000372`); `syrian_intervention.continued_presence=continued_presence_recorded` (`…00000373`); 2 delivered |
| c09 | All eight actors wait | No state delta; 1 delivered |
| c10 | `israeli_state_intervention_interface` → `record_full_invasion_and_siege` | `israeli_intervention.full_invasion_siege=full_invasion_and_siege_recorded` (`…00000449`); 0 delivered |
| c11 | `lebanese_front_record_interface` → `record_front_siege_support`; `palestine_liberation_organization` → `record_beirut_defence_and_withdrawal` | `lebanese_front_records.siege_support=qualified_siege_support_recorded` (`…00000490`); `plo_operations.beirut_defence_withdrawal=defence_and_withdrawal_recorded` (`…00000491`); 2 delivered |
| c12 | `israeli_state_intervention_interface` → `record_camp_entry_facilitation` | `israeli_intervention.camp_entry_facilitation=qualified_camp_entry_facilitation_recorded` (`…00000531`); 1 delivered |
| c13 | `lebanese_front_record_interface` → `record_sabra_shatila_camp_operation` | `lebanese_front_records.camp_operation=qualified_sabra_shatila_operation_recorded` (`…00000568`); 1 delivered |
| c14 | `amal_movement` → `record_war_of_camps_campaign` | `war_of_camps.amal_campaign=qualified_amal_campaign_recorded` (`…00000611`); 0 delivered |
| c15 | `palestine_liberation_organization` → `record_camp_defence`; `syrian_state_intervention_interface` → `record_syrian_support_for_amal` | `war_of_camps.plo_defence=qualified_plo_camp_defence_recorded` (`…00000654`); `war_of_camps.syrian_amal_support=qualified_syrian_support_recorded` (`…00000655`); 3 delivered |
| c16 | `hezbollah` → `record_hezbollah_camp_support` | `war_of_camps.hezbollah_support=qualified_hezbollah_support_recorded` (`…00000695`); 2 delivered |
| c17 | `syrian_state_intervention_interface` → `record_taif_mediation` | `taif_process.mediation=qualified_taif_mediation_recorded` (`…00000739`); 1 delivered |
| c18 | `amal_movement` → `record_amal_taif_position`; `hezbollah` → `record_hezbollah_taif_position`; `lebanese_front_record_interface` → `record_front_taif_position` | `taif_process.amal_position=qualified_disarmament_position_recorded` (`…00000785`); `taif_process.hezbollah_position=qualified_exemption_position_recorded` (`…00000786`); `taif_process.front_position=qualified_revised_representation_position_recorded` (`…00000787`); 3 delivered |
| c19 | `syrian_state_intervention_interface` → `record_taif_enforcement` | `taif_process.enforcement=qualified_enforcement_recorded` (`…00000833`); 3 delivered |
| c20 | `hezbollah` → `record_postwar_exemption_status`; `syrian_state_intervention_interface` → `record_postwar_syrian_presence` | `postwar_records.hezbollah_exemption_status=qualified_exemption_status_recorded` (`…00000878`); `postwar_records.syrian_presence=postwar_presence_recorded` (`…00000879`); 3 delivered |
| c21 | All eight actors wait | No state delta; 3 delivered |

The opening path keeps three faction participation records and three Beirut
records separately owned. The joint-government gate waits for delivered faction
records before issuing a qualified intervention request. Syria then records its
own deployment, territorial-presence and alignment choices; a request does not
cause deployment without that separate choice.

The next section preserves distinct PLO, Syrian and Israeli records. PLO's
cross-border record becomes delivered information before Israel records
Operation Litani. PLO separately records resistance, and Syria records continued
presence. Coordinate 9 is a delivery barrier. Israel later records the 1982
invasion/siege and camp-entry facilitation; the PLO and Lebanese Front own their
separate defence, support and camp-operation records. No state field represents
casualties, territory, weapons, tactics, responsibility or military success.

The War-of-the-Camps sequence uses actual information receipt. Amal records its
campaign; PLO and Syria then record defence and support; Hezbollah waits for the
delivered PLO record before recording support. Syria records a qualified Taif
mediation framework only after all three relevant camp records arrive. The
Lebanese Front, Amal and Hezbollah publish separate positions, after which Syria
records qualified enforcement. Syria and Hezbollah finally own their separate
post-war records. These fields do not model agreement formation, constitutional
implementation, disarmament, durable peace or policy effectiveness.

Every descriptive expectation is assessed below. Endpoint agreement follows
from a full-Draft-conditioned deterministic baseline and is not a historical
fit score.

| Expectation suffix | Observed value | Met |
| --- | --- | --- |
| initial_conflict.front_participation | qualified_front_participation_recorded | True |
| initial_conflict.lnm_participation | qualified_lnm_participation_recorded | True |
| initial_conflict.plo_participation | qualified_plo_participation_recorded | True |
| beirut_territorial_records.front_campaign | east_beirut_campaign_recorded | True |
| beirut_territorial_records.lnm_campaign | beirut_campaign_recorded | True |
| beirut_territorial_records.plo_position | west_beirut_position_recorded | True |
| state_authority.intervention_request | qualified_syrian_intervention_request_recorded | True |
| syrian_intervention.initial_deployment | deployment_recorded | True |
| continued_conflict.front_record | continued_front_conflict_recorded | True |
| continued_conflict.lnm_record | continued_lnm_conflict_recorded | True |
| continued_conflict.plo_record | continued_plo_conflict_recorded | True |
| syrian_intervention.territorial_consolidation | northern_eastern_presence_recorded | True |
| syrian_intervention.alignment_change | lnm_plo_support_recorded | True |
| plo_operations.cross_border_record | qualified_cross_border_operations_recorded | True |
| israeli_intervention.operation_litani | operation_litani_recorded | True |
| plo_operations.litani_resistance | qualified_litani_resistance_recorded | True |
| syrian_intervention.continued_presence | continued_presence_recorded | True |
| israeli_intervention.full_invasion_siege | full_invasion_and_siege_recorded | True |
| plo_operations.beirut_defence_withdrawal | defence_and_withdrawal_recorded | True |
| lebanese_front_records.siege_support | qualified_siege_support_recorded | True |
| israeli_intervention.camp_entry_facilitation | qualified_camp_entry_facilitation_recorded | True |
| lebanese_front_records.camp_operation | qualified_sabra_shatila_operation_recorded | True |
| war_of_camps.amal_campaign | qualified_amal_campaign_recorded | True |
| war_of_camps.plo_defence | qualified_plo_camp_defence_recorded | True |
| war_of_camps.syrian_amal_support | qualified_syrian_support_recorded | True |
| war_of_camps.hezbollah_support | qualified_hezbollah_support_recorded | True |
| taif_process.mediation | qualified_taif_mediation_recorded | True |
| taif_process.front_position | qualified_revised_representation_position_recorded | True |
| taif_process.amal_position | qualified_disarmament_position_recorded | True |
| taif_process.hezbollah_position | qualified_exemption_position_recorded | True |
| taif_process.enforcement | qualified_enforcement_recorded | True |
| postwar_records.syrian_presence | postwar_presence_recorded | True |
| postwar_records.hezbollah_exemption_status | qualified_exemption_status_recorded | True |

## Mechanism reading

### Direct run evidence

Eight organizational participants use one declarative Rule implementation and
one authoritative environment. Single-writer handlers preserve coalition,
government, Syrian, Israeli, Amal and Hezbollah authority. Rule chooses; the
environment admits and applies effects. Public prestate, actual delivery and
retained runtime memory activate later rows. Draft stage labels, Reference
content are absent from observations. Taif/post-war field and capability names
are visible before their generated result values, so this is a vocabulary-exposed
baseline. No common-code Lebanon branch supplies the choices.

The canonical run accepts all 33 selected records and meets all 33 descriptive
expectations. The run contains no rejected non-default action, so shared
negative tests and the two construction probes own failure evidence.

### Representation and construction probes

Four Draft sources remain non-acting context: Lebanese civilians, unidentified
church attackers, Sabra/Shatila refugees and Palestinian camp residents. Five
victim-harm rows never become victim-authored intents. Malformed Draft
relationships and transactions create no authority, route or resource flow.
Repeated Litani and exemption language is consolidated while retaining its
source anchors.

Two previously verified local probes, retained as historical construction evidence, test the information-dependent mechanism.
They are not current releases or historical counterfactual claims:

| Changed owner/input | Observed response | Evidence boundary |
|---|---|---|
| Syria's mediation record sends no invitation to Amal | Earlier records and mediation remain accepted. The Front and Hezbollah publish their positions; Amal's position, enforcement and both post-war records remain open: 892 records, 933 nodes and 2,685 edges. | Fresh A/B, ID perturbation, replay, graph and independent publication pass with zero unresolved transport. This tests missing information, not historical exclusion or peace effects. |
| PLO→Hezbollah camp-defence latency changes from one to four ticks | The defence message arrives after Hezbollah's support window. Hezbollah support, mediation, all three Taif positions, enforcement and both post-war records remain open: 872 records, 913 nodes and 2,614 edges. | The delayed message reaches terminal delivery. Four ticks are an adversarial route setting, not estimated wartime communication latency or a conflict counterfactual. |

The probe run IDs are `run.249b34483d81d2cce4ffdd00` and `run.c23ea6cd6e5708e5d77bac6e`. Each
variant received new configuration, realization, assembly, package and release
identities before execution. Neither was created by editing an admitted package
or generated output.

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

The frozen evidence is weak for a fifteen-year event: it is mostly secondary,
frequently truncated and includes later retrospectives and pages about the 2008
clashes. Records conflict on whether the opening is April or September 1975.
The Source Profile preserves the supplied identities and the Scenario qualifies
their use; no external reconciliation was attempted.

The Draft contains malformed participant IDs in five E2 transactions and
misdirected E4–E7 relationships. Actor-local rows and coherent descriptions own
the current authority map. Organizational interfaces aggregate internal
variation. Twenty-one coordinates and one-tick baseline routes are authored
logical ordering choices across fifteen years.

This output supports dataset-conditioned construction, state/information-aware
deterministic execution, integrity/replay evidence and trace-derived Generated
EPG description. It does not establish historical fit, calibrated conflict
behavior, casualty or responsibility claims, military or peace effects,
held-out performance, causality, scientific validity or universal generality.
LLM and RuleLLM remain planned; no model decision or cross-backend evidence
appears here.
