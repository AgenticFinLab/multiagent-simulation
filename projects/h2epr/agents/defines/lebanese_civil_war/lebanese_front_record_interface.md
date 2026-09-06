# Lebanese Front Record Interface Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0892.agent.lebanese_front_record_interface.v1` |
| Actor ID | `lebanese_front_record_interface` |
| Benchmark | H2EPR-0892, 1975-04-13 through the Draft's qualified 1990-10-13 post-war boundary |
| Representation | agent; six separately typed Lebanese Front coalition records |
| Source ID | `P_1` |
| Primary choices | Record initial and territorial participation, continued conflict, support for the 1982 siege, a qualified camp operation and its Taif position. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_1 persists across six episodes under two closely related names. One organizational interface preserves the source ID while separating conflict, alliance, camp-operation and negotiation records; it is not a stable militia personality or command model.

It cannot speak for every Christian faction, generate violence or casualties, control territory, request or command a foreign deployment, prove responsibility, implement Taif, or decide another faction's position. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E1/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S1/E2/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E3/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E5/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E6/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E8/P_1 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC005, SRC006, SRC008 and SRC011. The frozen set and Draft compress a changing coalition across fifteen years. E2 transactions and E6 relations use wrong endpoints, so actor-local P_1 rows and qualified narrative records own the current capability.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record initial and territorial participation, continued conflict, support for the 1982 siege, a qualified camp operation and its Taif position. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

A conflict or camp-operation record is not a tactical order, observed attack outcome, casualty attribution or legal finding. Support for a siege does not write Israel's action.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Later rows wait for delivered counterparty, invasion, facilitation or mediation notices. Missing information leaves that row open without manufacturing a substitute coalition outcome. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_initial_front_participation` | source-bounded availability and own record not yet made | Record the Lebanese Front's qualified initial conflict participation without generating combat, territory or casualty effects. |
| `record_front_beirut_campaign` | known `lnm_initial_record` from `lebanese_national_movement`; known `plo_initial_record` from `palestine_liberation_organization` | Record the represented Front territorial campaign; no control, displacement or Green Line effect is created. |
| `record_continued_front_conflict` | known `syrian_deployment_notice` from `syrian_state_intervention_interface` | Record continued Front conflict after the Syrian deployment notice, not its outcome. |
| `record_front_siege_support` | known `full_invasion_notice` from `israeli_state_intervention_interface` | Record qualified Front support for the siege without writing Israeli or PLO outcomes. |
| `record_sabra_shatila_camp_operation` | known `camp_entry_facilitation_record` from `israeli_state_intervention_interface` | Record the Front's represented camp operation after facilitation; no casualty or legal-responsibility state is created. |
| `record_front_taif_position` | known `taif_mediation_notice` from `syrian_state_intervention_interface` | Record the Front's qualified Taif representation position, not parliamentary implementation. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_initial_front_participation` | `initial_conflict` | `initial_conflict.front_participation`: unrecorded → `qualified_front_participation_recorded` |
| `record_front_beirut_campaign` | `beirut_territorial_records` | `beirut_territorial_records.front_campaign`: unrecorded → `east_beirut_campaign_recorded` |
| `record_continued_front_conflict` | `continued_conflict` | `continued_conflict.front_record`: unrecorded → `continued_front_conflict_recorded` |
| `record_front_siege_support` | `lebanese_front_records` | `lebanese_front_records.siege_support`: unrecorded → `qualified_siege_support_recorded` |
| `record_sabra_shatila_camp_operation` | `lebanese_front_records` | `lebanese_front_records.camp_operation`: unrecorded → `qualified_sabra_shatila_operation_recorded` |
| `record_front_taif_position` | `taif_process` | `taif_process.front_position`: unrecorded → `qualified_revised_representation_position_recorded` |

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

- Normal: The interface records its early participation, later receives the invasion and facilitation notices, and publishes a separate Taif position only after mediation is delivered.
- Missing information: Later rows wait for delivered counterparty, invasion, facilitation or mediation notices. Missing information leaves that row open without manufacturing a substitute coalition outcome.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: A conflict or camp-operation record is not a tactical order, observed attack outcome, casualty attribution or legal finding. Support for a siege does not write Israel's action.
- Perturbation: Withholding camp-entry facilitation leaves the P_1 camp-operation record open; omitting mediation preserves all earlier conflict records while leaving its Taif position open.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and successor route

It cannot speak for every Christian faction, generate violence or casualties, control territory, request or command a foreign deployment, prove responsibility, implement Taif, or decide another faction's position. The frozen set and Draft compress a changing coalition across fifteen years. E2 transactions and E6 relations use wrong endpoints, so actor-local P_1 rows and qualified narrative records own the current capability.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
