# Baoneng–Vanke Takeover Battle Rule simulation reading

## Run identity

This is a simulation-only reading of the current seed-0 Rule output for
H2EPR-1031. Construction used the three admitted dataset files with the complete
Draft exposed; model/network access are denied. The
[compact release](../../../releases/baoneng_vanke_takeover_battle/rule/) contains independent
verification receipts and reproduction instructions. The
[event entry](../../../events/baoneng_vanke_takeover_battle/) links every semantic owner.

| Item | Exact identity |
| --- | --- |
| Package | h2epr.event-package.1031.v1; 06cdd22424efcb091e4b9850f38b5965ea222e652e3e7cec31ecf2282a7bb976 |
| Rule binding | 89de3ff815ff6649a37df3191cf28fa0a3a191d490d47772dd75512c1a4e7452 |
| Realization | h2epr.1031.rule-realization.v1; dbd0e032b5089214dc5e740473668637400025916da443f1a8d3cbda6f0721b9 |
| Shared configuration | h2epr.1031.comparison.v1; 1fdd3ff487570175d387e406ff8c1fea6599548b8ce0646b7834b8ab6d4766a9 |
| Rule configuration | h2epr.1031.rule.v1; 36e94810565faaf3e656362b95b2ae359a66ff683bae2c7cbcb451fc6cd37636 |
| Run | run.f53d0be85dbb76fc46dcdde4 |
| Run manifest | 4816bcfacf04000bf3b1f5512eb387dd937d90d79c7b48b6df882fe4f09d42f2 |
| Trace | 3b6d399af0cf8247b2f284a375b1d69e347bf95ad3f10ce79390c0250423e475 |
| Terminal state | b5c58efa2c78ab645c4eac75ff0481a2c122576551084ab6227cfe2735c8ec32 |
| Run seal | 114604c982effaab1e166b1652745439eba0bb6f2d83582ae93058ad1e1fe0ae |
| Generated EPG seal | 06d315f500d23348b3c3a888d6f1f859ca872e7b254d1f1494ef3aadcd8ba1e2 |
| Physical raw custody | .local-runtime/h2epr-simulation/runs/benchmark/baoneng_vanke_takeover_battle/rule/2026-09-06-semantic-contracts/materialization-a |

Fresh A/B outputs are byte-identical across all eight output roles and the run
receipt. The generated-ID probe preserves semantic trace/graph structure and
exact terminal state. The publisher independently reconstructs the manifest and
H2EPR/MASim source inventories, trace and seals, observations and memory, replay,
counts, outcomes and graph; it also rematerializes from the admitted package.

## Complete-output coverage

The full machine scan traversed 823 trace records, 861 graph nodes and 2,465
graph edges. IDs are unique, all edge endpoints resolve and graph source-trace
references cover exactly all 823 trace records. Semantic review inspected all
27 non-default dispositions, 27 deltas, 29 messages, four annotations and every
coordinate. Repeated no-op, observation and provenance scaffolding was checked
by family and exact reconstruction, not presented as a verbatim raw transcript.

| Trace family | Count | Coverage meaning |
| --- | --- | --- |
| observation / participant_decision / action_intent / action_disposition | 160 each | Eight complete actor paths at each of 20 coordinates |
| Non-default / no-op actions | 27 / 133 | All admitted; zero rejected dispositions in this canonical baseline |
| message_intent / message_disposition | 29 / 58 | Each queued and delivered; zero unresolved transport |
| state_delta | 27 | One actor-owned record transition per non-default action |
| tick_open / tick_commit / tick_seal | 20 each | Full horizon; exact authoritative state replay |
| stage_entry / generated_annotation | 4 / 4 | Navigation entries and configured state-condition summaries |
| run_seal | 1 | Complete evidence and terminal accounting |

The graph adds one event, 20 coordinates, eight participants and nine state-entity
nodes to the 823 record nodes. Its complete edge-family ledger is:

| Edge family | Count |
| --- | --- |
| addressed_to | 29 |
| aggregates | 20 |
| based_on | 160 |
| caused_by | 56 |
| changes | 27 |
| commits | 27 |
| decided_by | 160 |
| disposes | 218 |
| emitted_by | 160 |
| involves | 12 |
| learns_result_from | 152 |
| observes_for | 160 |
| occurs_at | 823 |
| part_of | 29 |
| participates_in | 8 |
| projects | 160 |
| received_from | 29 |
| retains_memory_from | 152 |
| seals | 21 |
| sent_by | 29 |
| stage_of | 4 |
| succeeds | 29 |

`received_from` identifies actual information receipt; `learns_result_from` and
`retains_memory_from` form linear participant memory histories. `caused_by` and
annotation provenance name implementation-level ancestry, not identified
historical causes. Annotation provenance includes the coordinate batch and is
not a minimal set of causally influential actions.

## Generated trajectory

Opening fields mean unrecorded statements, not zero holdings. Election result
opens at unobserved and has no action writer. The table lists every coordinate,
all non-default actions and all state deltas. Trace suffixes abbreviate
`trace.run.f53d0be85dbb76fc46dcdde4.`; graph record nodes add `record.` to that exact ID.

| Coordinate | Accepted participant choices | Recorded effects and deliveries |
| --- | --- | --- |
| c01 | `baoneng_group` → `disclose_initial_stake` | `stake_disclosures.baoneng_initial=reported_22_45_percent` (`…00000039`); 0 delivered |
| c02 | `wang_shi` → `state_takeover_opposition`; `yu_liang` → `state_management_risk` | `management.wang_opposition=recorded` (`…00000085`); `management.yu_risk_statement=recorded` (`…00000086`); 3 delivered |
| c03 | `vanke_corporate_governance` → `issue_suspension_notice`; `wang_shi` → `publish_management_statement` | `corporate.suspension_notice=recorded` (`…00000125`); `management.wang_publication=recorded` (`…00000126`); 3 delivered |
| c04 | `baoneng_group` → `disclose_increased_stake`; `vanke_corporate_governance` → `record_conditional_loi` | `stake_disclosures.baoneng_increase=reported_24_3_percent` (`…00000162`); `corporate.conditional_loi=recorded` (`…00000163`); 0 delivered |
| c05 | `shenzhen_metro` → `submit_restructuring_terms` | `proposal.metro_terms=recorded` (`…00000202`); 0 delivered |
| c06 | `vanke_corporate_governance` → `announce_metro_proposal` | `proposal.corporate_announcement=recorded` (`…00000245`); 1 delivered |
| c07 | `baoneng_group` → `oppose_asset_proposal`; `china_resources` → `oppose_asset_proposal_cr`; `shenzhen_metro` → `confirm_proposal_participation` | `positions.baoneng_opposition=recorded` (`…00000284`); `positions.china_resources_opposition=recorded` (`…00000285`); `proposal.metro_agreement=recorded` (`…00000286`); 3 delivered |
| c08 | `baoneng_group` → `submit_removal_request`; `csrc` → `issue_governance_guidance`; `vanke_corporate_governance` → `issue_resumption_notice` | `governance.removal_request=submitted` (`…00000333`); `regulation.guidance=issued` (`…00000334`); `corporate.resumption_notice=recorded` (`…00000335`); 0 delivered |
| c09 | `vanke_corporate_governance` → `record_board_rejection` | `governance.board_response=rejection_recorded` (`…00000379`); 5 delivered |
| c10 | `evergrande_group` → `disclose_evergrande_stake` | `stake_disclosures.evergrande=reported_4_68_percent` (`…00000419`); 1 delivered |
| c11 | `vanke_corporate_governance` → `open_resolution_discussion` | `negotiation.invitation=issued` (`…00000462`); 1 delivered |
| c12 | `baoneng_group` → `reaffirm_opposition`; `evergrande_group` → `record_negotiation_participation`; `shenzhen_metro` → `submit_negotiation_position` | `negotiation.baoneng_position=opposition_reaffirmed` (`…00000501`); `negotiation.evergrande_position=recorded` (`…00000502`); `negotiation.metro_position=recorded` (`…00000503`); 3 delivered |
| c13 | `vanke_corporate_governance` → `report_operating_impacts` | `corporate.operating_report=recorded` (`…00000539`); 0 delivered |
| c14 | `shenzhen_metro` → `disclose_metro_acquisition` | `stake_disclosures.metro=reported_nearly_30_percent` (`…00000583`); 0 delivered |
| c15 | `shenzhen_metro` → `submit_board_nominees` | `nomination.metro_proposal=submitted` (`…00000631`); 4 delivered |
| c16 | `vanke_corporate_governance` → `register_board_nominees`; `wang_shi` → `decline_board_nomination` | `nomination.corporate_registration=recorded` (`…00000674`); `nomination.wang_choice=declined_recorded` (`…00000675`); 3 delivered |
| c17 | `vanke_corporate_governance` → `schedule_shareholder_meeting` | `nomination.meeting_notice=scheduled` (`…00000713`); 2 delivered |
| c18 | All eight actors wait | No state delta; 0 delivered |
| c19 | All eight actors wait | No state delta; 0 delivered |
| c20 | All eight actors wait | No state delta; 0 delivered |

The first communication chain is genuinely sequenced: Baoneng's initial report
reaches Wang/Yu at c02; Yu's statement reaches Wang at c03 before republication.
Metro terms arrive at Vanke at c06; separate investor responses occur at c07.
Baoneng's removal request at c08 is followed by a corporate board-response record
at c09. A rejected removal *request* is the content of that accepted corporate
statement, not a rejected simulator action. These are different lifecycle layers.

The later chain preserves independent meanings. Metro's acquisition disclosure
at c14 (`…00000575`) does not execute the old proposed asset swap. Its nominee
proposal at c15 (`…00000624`) is delivered at c16, when Vanke registers it and
Wang records his personal decline. The c17 meeting notice (`…00000710`) is a
scheduled vote, not an elected board. c18–c20 contain only no-op decisions and
integrity closure. All 29 transport lifecycles are closed; institutional records
persist and election_result deliberately remains unobserved.

Every declared expectation is assessed below. Meeting/nominee records are
persistent process states, and the election is deliberately open; none is an
independent historical success score or a complete-release requirement.

| Expectation suffix | Observed value | Met |
| --- | --- | --- |
| stake_disclosures.baoneng_initial | reported_22_45_percent | True |
| management.wang_opposition | recorded | True |
| management.yu_risk_statement | recorded | True |
| management.wang_publication | recorded | True |
| corporate.suspension_notice | recorded | True |
| corporate.conditional_loi | recorded | True |
| stake_disclosures.baoneng_increase | reported_24_3_percent | True |
| proposal.metro_terms | recorded | True |
| proposal.corporate_announcement | recorded | True |
| proposal.metro_agreement | recorded | True |
| positions.baoneng_opposition | recorded | True |
| positions.china_resources_opposition | recorded | True |
| governance.removal_request | submitted | True |
| corporate.resumption_notice | recorded | True |
| regulation.guidance | issued | True |
| governance.board_response | rejection_recorded | True |
| stake_disclosures.evergrande | reported_4_68_percent | True |
| negotiation.invitation | issued | True |
| negotiation.baoneng_position | opposition_reaffirmed | True |
| negotiation.metro_position | recorded | True |
| negotiation.evergrande_position | recorded | True |
| corporate.operating_report | recorded | True |
| stake_disclosures.metro | reported_nearly_30_percent | True |
| nomination.metro_proposal | submitted | True |
| nomination.corporate_registration | recorded | True |
| nomination.wang_choice | declined_recorded | True |
| nomination.meeting_notice | scheduled | True |
| nomination.election_result | unobserved | True |

## Mechanism reading

### Direct run evidence

Eight separate actors use one declarative Rule implementation. Single-writer
record handlers preserve corporate, personal, shareholder and regulator
authority. Concurrent opposition at c07 writes different shareholder fields.
The reducer validates effects; the backend does not grant removal, execute
transfers or elect directors. Public state, actual delivery and retained memory
jointly condition the selected policy; historical stage labels are absent from
decision-time observations. No common-code event branch supplies these choices.

The canonical run follows all 27 selected statement choices and meets all
28 descriptive expectations, including unobserved election. It contains no
rejected runtime action, so it alone does not demonstrate retry after rejection
or authority-denial behavior. Those remain independently tested common contracts.

### Interpretation

The model distinguishes a proposal from agreement, shareholder opposition from
a veto, a request from a board response, and nomination from election. That
separation is useful despite a narrow choice set. It exposes which transitions
depend on information and which later source statements remain independently
available. For example, the later Metro acquisition disclosure is not conditional
on fictitious completion of the rejected 2016 proposal.

This remains a sparse disclosure/decision-record simulation. Fixed statement
contents, earliest windows, one-tick routes and priority are authored structural
choices informed by the full Draft. Valid no-op and delayed alternatives make
the process responsive, but do not establish strategic autonomy, endogenous
market behavior or the quality of an acquisition decision.

Two separately admitted local construction probes support this limited behavior
claim. They are not additional current releases or scientific comparisons:

| Changed owner/input | Observed response | Evidence boundary |
|---|---|---|
| Rule configuration omits the nominee statement's three outgoing messages | Acquisition disclosure and nominee submission remain; registration, Wang decline and meeting notice are absent. 804 trace records, 842 nodes, 2,398 edges; three unmet expectations. | Open endpoint still passes fresh A/B, ID probe, replay and independent publication with zero unresolved transport. |
| Shared Metro→Vanke route latency changes from 1 to 3 ticks | Terms/proposal and dependent earlier choices shift; registration moves c16→c18 and meeting notice c17→c19. Counts remain 823 / 861 / 2,465. | This delays every message on that route, not only nominees. It is a routing-construction check, not an estimated historical delay. |

Their exact run identities are `run.d0ab1fa50cd31c66fdd2bc65` and
`run.23aed97aaa4c29dfc895562d`; local custody is under
`.local-runtime/h2epr-simulation/working/2026-09-05-behavior/probes/` in the
`baoneng-missing-nominees` and `baoneng-delayed-metro` directories. Each was
compiled before execution with new selected-configuration identity, never
created by mutating an admitted package or editing its outputs.

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

The frozen sources and Draft disagree about relationship/transaction endpoints,
the December investor, the board-response date and the strength of the final
election claim. These limitations belong to the Source Profile and Scenario;
the simulation chooses bounded records rather than declaring the disputes solved.
Any descriptive alignment with Draft is full-Draft-conditioned, not unbiased
historical validation. No Reference or external history was used.

The P_2 issuer/board-record composite omits internal votes and management-versus-
board disagreement. No source Population Model is needed, but outside investors,
exchange operators and election voters are not simulated. Monetary quantities
remain report content; there is no balance sheet, funding mechanism, price,
share conservation or securities settlement. The clock does not reconcile
overlapping dates. Later acquisition and succession remain strongly conditioned
by the exposed input and selected policy.

This output supports dataset-conditioned construction, executable process
semantics, deterministic integrity/replay and trace-derived graph description.
It does not support historical fit, parameter calibration, held-out evaluation,
policy effects, causal or scientific validity, universal generality, or a claim
that autonomous model agents rediscovered the historical outcome. LLM and RuleLLM
remain planned, with no model-decision or cross-backend evidence here.
