# Angola Yellow Fever Outbreak of 2016 Rule simulation reading

## Run identity

This reading covers the canonical seed-0 output for `H2EPR-0551`,
built from the three allowed dataset inputs with the full Draft exposed.
The [compact release](../../../releases/angola_yellow_fever_outbreak/rule/) records independent
verification and reproduction instructions. Model and network access are denied.

| Item | Identity |
|---|---|
| Package | `h2epr.event-package.0551.v2`; `938f441d834a8c928fb64ec12eb6e3692ef6e00c91d06016ba681f8d6f540e3d` |
| Rule binding | `530e0f3316aa7af6275cc5a58cf2f9e254de00de9999cdf4c6c0f28025e7890c` |
| Rule configuration | `h2epr.0551.rule.v2`; `e3954abe461770d5872fe53ec381e28f05dff678c6ab8b270ab9b4c0b2e13ddc` |
| Run | `run.c8e90196fadcf5a18b9b9f9a` |
| Run manifest | `6072990591323910c30efdeecce60c44835b46a5d829cf39ea81a707c9a786ee` |
| Trace | `a08dd89d287d2e7d12061c6fec04584f954aaaa5306d037efd957a54320fff08` |
| Terminal state | `6e43cbba3847a1df9b6dd5c5395932c964d8baf6f086717e7c04f375da0ea26e` |
| Run seal | `57121ec6e9c26a3f7207d2e08098c79cf0a1725d0a5a302d3e86aae2ece4c8b6` |
| Generated EPG seal | `b177447f3ba8ba8af9320599ae1e924fa2c0453897056e1b95bf85fb6be0a4c4` |
| Raw physical custody | `.local-runtime/h2epr-simulation/runs/benchmark/angola_yellow_fever_outbreak/rule/2026-09-05-behavior/a` |

Fresh A/B materializations are byte-identical across the eight output roles and
run receipt. A generated-ID probe changes opaque identities while preserving
semantic trace/graph and exact terminal state. The publisher independently
reconstructs the manifest, source inventory, observations and memory, trace,
seals, replay, counts, outcomes, and graph, and rematerializes the package.

## Complete-output coverage

The complete machine scan visits all 826 trace records,
866 graph nodes, and 2,481 graph edges. All IDs
are unique, every edge endpoint resolves, and every source-trace reference
resolves to the exact 826-record set with no uncovered record.
The semantic review covers every non-no-op action, delta, message, annotation,
and coordinate below; repeated observation, no-op, provenance, and seal
scaffolding is checked by family and exact reconstruction rather than reproduced
as a raw transcript in this report.

| Record family | Count | Result |
|---|---:|---|
| Observation / decision / intent / disposition | 160 each | One complete actor path per coordinate |
| Non-no-op / no-op | 26 / 134 | All dispositions accepted in this canonical run |
| Message intents / dispositions | 30 / 60 | Every message queued and delivered; zero unresolved |
| State deltas | 26 | Every effect traces to an accepted source intent |
| Stage entries / annotations | 4 / 5 | Clock navigation and configured state-condition labels |
| Tick opens / commits / seals | 20 each | Exact authoritative replay of every actual state |
| Run seal | 1 | Complete horizon and terminal transport accounting |

The graph includes one event node, 20 coordinate nodes, 8
participant nodes, 11
state-entity nodes, and one node per trace record. Its 22 edge
families cover placement, decisions, dispositions, effects, messages, memory,
annotations, and seals. In particular, `30`
`received_from` edges identify actual delivery; `152`
`learns_result_from` and `152` `retains_memory_from`
edges form each actor's linear information-history chain. These are provenance
links, not proof that every available fact caused a decision. Annotation
provenance includes the contributing coordinate batch, not a minimal causal set.

## Generated trajectory

The table lists every coordinate and every non-default action and state change.
Trace suffixes abbreviate `trace.run.c8e90196fadcf5a18b9b9f9a.`; corresponding graph
record nodes use `record.trace.run.c8e90196fadcf5a18b9b9f9a.` with the same suffix.

| Coordinate | Accepted choices | Recorded effects and delivery |
|---|---|---|
| c01 | `angola_ministry_of_health` → `detect_outbreak` | `outbreak.detection_status=detected` `…00000039`; 0 delivered |
| c02 | `institut_pasteur_dakar` → `confirm_ipd_cases`; `nicd_south_africa` → `confirm_nicd_cases` | `laboratory.ipd_status=confirmed` `…00000083`; `laboratory.nicd_status=confirmed` `…00000084`; 3 delivered |
| c03 | `world_health_organization` → `record_initial_confirmation` | `outbreak.confirmation_status=recorded` `…00000122`; 2 delivered |
| c04 | `angola_ministry_of_health` → `report_case_surge` | `epidemiology.case_status=surge_reported` `…00000161`; 0 delivered |
| c05 | `angola_ministry_of_health` → `launch_local_vaccination` | `vaccination.local_campaign=active` `…00000201`; 1 delivered |
| c06 | `angola_drc_affected_residents` → `participate_local_vaccination` | `population_response.local_status=participating` `…00000242`; 1 delivered |
| c07 | `drc_ministry_of_health` → `report_imported_cases` | `regional_risk.imported_case_status=reported` `…00000282`; 2 delivered |
| c08 | `world_health_organization` → `document_cross_border_risk` | `regional_risk.risk_status=documented` `…00000321`; 1 delivered |
| c09 | `world_health_organization` → `convene_first_emergency_committee` | `governance.first_meeting=convened` `…00000364`; 1 delivered |
| c10 | `angola_ministry_of_health` → `submit_angola_briefing`; `drc_ministry_of_health` → `submit_drc_briefing` | `governance.angola_briefing=submitted` `…00000408`; `governance.drc_briefing=submitted` `…00000409`; 3 delivered |
| c11 | `who_yellow_fever_emergency_committee` → `issue_first_risk_assessment` | `governance.first_assessment=serious_event_not_pheic` `…00000449`; 2 delivered |
| c12 | `world_health_organization` → `coordinate_scaled_response` | `scaled_response.coordination=scaled` `…00000493`; 1 delivered |
| c13 | `angola_ministry_of_health` → `record_angola_scaled_response`; `drc_ministry_of_health` → `record_drc_scaled_response` | `scaled_response.angola_status=response_recorded` `…00000532`; `scaled_response.drc_status=fractional_response_recorded` `…00000533`; 3 delivered |
| c14 | `angola_drc_affected_residents` → `participate_scaled_vaccination` | `population_response.regional_status=participating` `…00000573`; 0 delivered |
| c15 | `angola_ministry_of_health` → `submit_angola_progress`; `drc_ministry_of_health` → `submit_drc_progress` | `progress.angola_status=no_recent_confirmed_cases_reported` `…00000616`; `progress.drc_status=no_recent_confirmed_cases_reported` `…00000617`; 2 delivered |
| c16 | `world_health_organization` → `convene_second_emergency_committee` | `governance.second_meeting=convened` `…00000657`; 2 delivered |
| c17 | `who_yellow_fever_emergency_committee` → `issue_second_risk_assessment` | `governance.second_assessment=serious_event_not_pheic_continued` `…00000696`; 1 delivered |
| c18 | `uganda_ministry_of_health` → `declare_uganda_outbreak_end` | `uganda_outbreak.status=declared_ended` `…00000736`; 1 delivered |
| c19 | `angola_ministry_of_health` → `activate_angola_surveillance`; `drc_ministry_of_health` → `activate_drc_surveillance`; `uganda_ministry_of_health` → `activate_uganda_surveillance`; `world_health_organization` → `activate_regional_surveillance` | `surveillance.angola_status=ongoing` `…00000780`; `surveillance.drc_status=ongoing` `…00000781`; `surveillance.uganda_status=ongoing` `…00000782`; `surveillance.who_status=ongoing` `…00000783`; 1 delivered |
| c20 | All actors wait; no state effect | No delta; 3 delivered |

## Mechanism reading

The opening is a set of institutional records: no recorded detection,
pending lab statements and committee assessments, inactive campaigns and
surveillance, and no Uganda end declaration. It is not a simulated infection
state. `detect_outbreak` records detection, while each laboratory separately
submits its exposed confirmation statement. WHO then records the paired reports.

The response handoffs distinguish WHO convening, country briefings, committee
assessment, WHO guidance, national response records, and aggregate Population
participation. At c13, regional guidance is already delivered to the Population;
it remains known until the c14 opportunity, after both country response records
become visible. No two-tick transport alignment is needed. Country progress
statements feed the later review, without a model estimating why case reports fell.

Uganda's c18 declaration is independently owned and no longer requires the
WHO assessment. Its `not_declared`/`declared_ended` field is an announcement
record. The second assessment and the Uganda declaration have separate paths
into the modeled surveillance choices; the latter does not authorize every
jurisdiction's surveillance. The c20 barrier delivers all three country updates.

All 26 descriptive expectations are met in this selected run. The terminal
local campaign remains `active`, Population responses remain `participating`,
and four surveillance records remain `ongoing`. `response_recorded` and
`fractional_response_recorded` describe national action records. Laboratory
confirmation, progress reports, assessments, and the end declaration are
represented statements, not independently established epidemiological truth.

### Interpretation

Paired reports can be accumulated across ticks, countries keep their own
response authority, and later choices can wait inside bounded windows.
These mechanisms support an inspectable coordination process without a
public-health-specific runner. The current committee choice surface remains
narrow: the baseline supplies the exposed non-PHEIC statements and permits
waiting, but does not implement a classifier over alternative assessments.

The full Draft, authored dependencies, interval compression, and selected
statement contents shape this trajectory. This run does not demonstrate
counterfactual clinical behavior, intervention effectiveness, or historical
causality. Those questions would need different information and contracts.

## Limitations

- Construction is full-Draft-exposed and the frozen evidence is heterogeneous, including later page material. No independent historical reconciliation or held-out prediction is established.
- P_3 changes from Luanda to Angola to Angola/DRC while keeping one source ID. Its aggregate participation intent is a structural assumption without microdata or a stable individual panel.
- P_7 travel and P_10 affected status remain deliberately unmodeled as individual decisions. The current scope does not test voluntary mobility, dose receipt, stock allocation, or subgroup uptake.
- Clock opportunities and routes are uncalibrated. Two laboratories share a compressed 19–20 January interval; a complete graph does not recover that finer chronology.
- The modeled confirmation, national response records, no-recent-cases reports, assessments, and Uganda declaration do not prove diagnostic accuracy, infection counts, interrupted transmission, or public-health effectiveness.
- The Draft ends openly. Ongoing surveillance is a finite-run record, and the Uganda milestone establishes no Angola-specific causal transmission path.
- The result supports engineering integrity and bounded descriptive simulation. Historical fit, parameter calibration, held-out evaluation, causal or scientific validity, policy effectiveness, and universal generality remain unsupported.
