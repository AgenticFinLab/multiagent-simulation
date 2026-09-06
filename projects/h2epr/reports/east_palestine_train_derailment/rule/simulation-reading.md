# East Palestine Train Derailment Rule simulation reading

## Run identity

This reading covers the canonical seed-0 output for `H2EPR-0196`,
built from the three allowed dataset inputs with the full Draft exposed.
The [compact release](../../../releases/east_palestine_train_derailment/rule/) records independent
verification and reproduction instructions. Model and network access are denied.

| Item | Identity |
|---|---|
| Package | `h2epr.event-package.0196.v2`; `897f82abe5197dab4e32c6de9e477d77ff74b6709292d096c83c8eebe6534684` |
| Rule binding | `3071f54542ee566dff373276abac87e832d1b756a0f280fe55a55fb2a8f0cd2c` |
| Rule configuration | `h2epr.0196.rule.v2`; `98dffac626cbe4900aff1852e498641a35f3421ba6dadb4cc6e5119982655ff5` |
| Run | `run.c81b945d591680e9f1fbaf03` |
| Run manifest | `d19e1dec7b58e76427cf62ca6db7533d0584fd6982ee26f29158dc39e4297d72` |
| Trace | `bed17c556d05b24d37317f58838fe28d601574b890166e00d3d4af4c9e137c45` |
| Terminal state | `79ed8e7961b316ff111e8add369f9de2cbfedd10f47cb45682343c27bc8cb140` |
| Run seal | `a427eaae17e9505faab43fdcd53e62ff478f0330040e49346d046f3af62c98e4` |
| Generated EPG seal | `a4eae255bc5b9924c12915dc5c4fec687ca791331ffd3219da14cb3b761f9be1` |
| Raw physical custody | `.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/2026-09-06-semantic-contracts/materialization-a` |

Fresh A/B materializations are byte-identical across the eight output roles and
run receipt. A generated-ID probe changes opaque identities while preserving
semantic trace/graph and exact terminal state. The publisher independently
reconstructs the manifest, source inventory, observations and memory, trace,
seals, replay, counts, outcomes, and graph, and rematerializes the package.

## Complete-output coverage

The complete machine scan visits all 405 trace records,
432 graph nodes, and 1,210 graph edges. All IDs
are unique, every edge endpoint resolves, and every source-trace reference
resolves to the exact 405-record set with no uncovered record.
The semantic review covers every non-no-op action, delta, message, annotation,
and coordinate below; repeated observation, no-op, provenance, and seal
scaffolding is checked by family and exact reconstruction rather than reproduced
as a raw transcript in this report.

| Record family | Count | Result |
|---|---:|---|
| Observation / decision / intent / disposition | 77 each | One complete actor path per coordinate |
| Non-no-op / no-op | 14 / 63 | All dispositions accepted in this canonical run |
| Message intents / dispositions | 14 / 28 | Every message queued and delivered; zero unresolved |
| State deltas | 14 | Every effect traces to an accepted source intent |
| Stage entries / annotations | 4 / 3 | Clock navigation and configured state-condition labels |
| Tick opens / commits / seals | 11 each | Exact authoritative replay of every actual state |
| Run seal | 1 | Complete horizon and terminal transport accounting |

The graph includes one event node, 11 coordinate nodes, 7
participant nodes, 8
state-entity nodes, and one node per trace record. Its 22 edge
families cover placement, decisions, dispositions, effects, messages, memory,
annotations, and seals. In particular, `14`
`received_from` edges identify actual delivery; `70`
`learns_result_from` and `70` `retains_memory_from`
edges form each actor's linear information-history chain. These are provenance
links, not proof that every available fact caused a decision. Annotation
provenance includes the contributing coordinate batch, not a minimal causal set.

## Generated trajectory

The table lists every coordinate and every non-default action and state change.
Trace suffixes abbreviate `trace.run.c81b945d591680e9f1fbaf03.`; corresponding graph
record nodes use `record.trace.run.c81b945d591680e9f1fbaf03.` with the same suffix.

| Coordinate | Accepted choices | Recorded effects and delivery |
|---|---|---|
| c01 | `norfolk_southern` → `report_derailment` | `incident.notification_status=reported` `…00000035`; 0 delivered |
| c02 | `local_emergency_response` → `order_evacuation`; `national_transportation_safety_board` → `open_investigation` | `evacuation.status=active` `…00000075`; `investigation.status=preliminary_active` `…00000076`; 3 delivered |
| c03 | `east_palestine_residents` → `acknowledge_evacuation`; `local_emergency_response` → `issue_controlled_release_instruction` | `community.evacuation_response=acknowledged` `…00000114`; `hazard_control.status=instruction_recorded` `…00000115`; 2 delivered |
| c04 | `ohio_response_authorities` → `lift_evacuation` | `evacuation.status=lifted` `…00000151`; 2 delivered |
| c05 | `east_palestine_residents` → `report_health_concerns` | `community.health_concerns=reported` `…00000190`; 1 delivered |
| c06 | `environmental_protection_agency` → `start_cleanup_oversight` | `cleanup.status=active` `…00000226`; 2 delivered |
| c07 | `norfolk_southern` → `advance_cleanup`; `ohio_response_authorities` → `file_state_civil_action`; `us_department_of_justice` → `file_federal_civil_action` | `cleanup.status=characterization` `…00000260`; `legal.state_status=filed` `…00000261`; `legal.federal_status=filed` `…00000262`; 1 delivered |
| c08 | `east_palestine_residents` → `report_persistent_impacts` | `community.health_concerns=persistent` `…00000297`; 0 delivered |
| c09 | `norfolk_southern` → `announce_class_settlement` | `settlement.class_status=announced` `…00000333`; 1 delivered |
| c10 | `ohio_response_authorities` → `record_municipal_settlement` | `settlement.municipal_status=announced` `…00000368`; 1 delivered |
| c11 | All actors wait; no state effect | No delta; 1 delivered |

Each declared expectation is assessed below; these are descriptive endpoints, not release gates.

| Expectation suffix | Observed terminal value | Met |
|---|---|---|
| `incident.status` | `derailed` | True |
| `evacuation.status` | `lifted` | True |
| `hazard_control.status` | `instruction_recorded` | True |
| `investigation.status` | `preliminary_active` | True |
| `community.evacuation_response` | `acknowledged` | True |
| `community.health_concerns` | `persistent` | True |
| `cleanup.status` | `characterization` | True |
| `legal.federal_status` | `filed` | True |
| `legal.state_status` | `filed` | True |
| `settlement.class_status` | `announced` | True |
| `settlement.municipal_status` | `announced` | True |
| `incident.notification_status` | `reported` | True |

## Mechanism reading

The opening derailment is an exogenous fact. The first operator intent
changes `incident.notification_status` from `unreported` to `reported`; it does
not cause an accident. At c03 the command records a controlled-release
instruction. The later return advisory is a separate authority decision and
establishes no physical safety result.

Two retained-information handoffs are directly visible. DOJ receives the NTSB
notice at c03 and keeps it while the federal-filing window remains closed until
c07. EPA receives the response instruction at c04 and the health report at c06;
both are known at c06 without artificially aligning route delays. Cleanup
oversight, railroad response, resident reporting, and federal/state filings
remain separate intents. The final settlement notice is delivered at c11.

The terminal record contains an already-derailed incident with notification
recorded, lifted evacuation, a recorded controlled-release instruction,
preliminary investigation, acknowledged resident evacuation, persistent
concerns, cleanup characterization, two filings, and two settlement
announcements. The investigation, concerns, and cleanup remain substantive
open processes. Neither payment nor verified remediation occurs in this world.

### Interpretation

The selected policy uses bounded windows and received information while
preserving exposed earliest intervals. One action per actor per coordinate
and explicit priority make competing eligible tasks observable modeling
choices. Waiting, an expired opportunity, or an unmade filing can be a valid
outcome; the publisher checks actual evidence rather than requiring those
choices to succeed. In this canonical run every descriptive expectation is
met, so this run alone does not establish the behavior of every alternative.

The operator notification chain, EPA's paired-report requirement, DOJ's
notice requirement, and the links from filings to settlement are authored
dependencies. They are inspectable and falsifiable within this simulation,
but are not recovered institutional protocols or historical causal claims.

## Limitations

The current observation profile exposes declared event vocabulary, including
names associated with later events. It does not provide historically
prefix-clean information. Rule windows and receipt guards are selected
policy assumptions except where explicit shared handler requirements apply.
Configured decision reasons are rationale; hash-linked observations, actual
message content, dispositions and deltas provide generated evidence.

- Construction uses the full exposed Draft; resemblance cannot be held-out prediction evidence.
- Frozen evidence was read as the sealed dataset context, without external reconciliation. Defective Draft relations and transaction directions do not define authority.
- Six organizational/command interfaces and one aggregate resident Population omit internal disagreement, heterogeneous behavior, exposure, and medical trajectories.
- The finite clock and one-tick routes are structural choices, not historical delay estimates. Windows allow delayed decisions but do not guarantee that all later opportunities remain available.
- `instruction_recorded`, `characterization`, `filed`, and `announced` establish no physical safety, remediation effectiveness, legal merit, executed compensation, or policy effect.
- The supported conclusions are dataset-conditioned construction, execution integrity, replay, graph provenance, and bounded descriptive reading. Historical fit, parameter calibration, held-out performance, causal validity, scientific validity, and universal generality remain unsupported.
