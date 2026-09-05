# Palestine Liberation Organization Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0892.agent.palestine_liberation_organization.v1` |
| Actor ID | `palestine_liberation_organization` |
| Benchmark | H2EPR-0892, 1975-04-13 through the Draft's qualified 1990-10-13 post-war boundary |
| Representation | agent; seven PLO participation, operation, resistance and withdrawal records |
| Source ID | `P_3` |
| Primary choices | Record early alliance participation, West Beirut positioning, continued conflict, cross-border operations, Litani resistance, Beirut defence/withdrawal and camp defence. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_3 appears in six episodes and changes operational setting. One organizational parent retains the source identity but keeps every record separately typed; it does not model leadership, fighters, refugees or one continuous strategy.

It cannot act for LNM, civilians, refugee residents, Israel or Syria, create casualties or territory, transfer aid, prove cross-border attacks, or determine a battle or ceasefire result. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E1/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S1/E2/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E3/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E4/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E5/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E7/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC005, SRC007, SRC008 and SRC011. E2 and E7 transactions/relations repeatedly use P_3 where their descriptions name Israel, Amal or another actor. Those endpoints are rejected as authority. Current values remain qualified actor-local records.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record early alliance participation, West Beirut positioning, continued conflict, cross-border operations, Litani resistance, Beirut defence/withdrawal and camp defence. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

Resistance and withdrawal records do not imply military success, civilian protection, expulsion truth or the absence of later PLO activity.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Litani, invasion and camp-defence rows require actual delivered notices. A late notice may arrive after the bounded choice window and remain terminally delivered without forcing action. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_initial_plo_participation` | source-bounded availability and own record not yet made | Record the PLO's separate initial participation rather than merging it with the LNM. |
| `record_plo_west_beirut_position` | known `front_initial_record` from `lebanese_front_record_interface`; known `lnm_initial_record` from `lebanese_national_movement` | Record the qualified West Beirut position without treating it as measured control or a durable border. |
| `record_continued_plo_conflict` | known `syrian_deployment_notice` from `syrian_state_intervention_interface` | Record continued PLO conflict after deployment without merging it with the LNM. |
| `record_cross_border_operations` | `continued_conflict.plo_record` = `continued_plo_conflict_recorded` | Record the exposed cross-border operations account without simulating targets, attacks or effects. |
| `record_litani_resistance` | known `operation_litani_notice` from `israeli_state_intervention_interface` | Record PLO resistance after Litani notice; no battlefield result or continued control is inferred. |
| `record_beirut_defence_and_withdrawal` | known `full_invasion_notice` from `israeli_state_intervention_interface` | Record the represented defence and withdrawal account; neither success nor expulsion completeness is verified. |
| `record_camp_defence` | known `amal_camp_campaign_record` from `amal_movement` | Record PLO camp defence after receiving Amal's campaign record; civilian outcomes remain outside state. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_initial_plo_participation` | `initial_conflict` | `initial_conflict.plo_participation`: unrecorded → `qualified_plo_participation_recorded` |
| `record_plo_west_beirut_position` | `beirut_territorial_records` | `beirut_territorial_records.plo_position`: unrecorded → `west_beirut_position_recorded` |
| `record_continued_plo_conflict` | `continued_conflict` | `continued_conflict.plo_record`: unrecorded → `continued_plo_conflict_recorded` |
| `record_cross_border_operations` | `plo_operations` | `plo_operations.cross_border_record`: unrecorded → `qualified_cross_border_operations_recorded` |
| `record_litani_resistance` | `plo_operations` | `plo_operations.litani_resistance`: unrecorded → `qualified_litani_resistance_recorded` |
| `record_beirut_defence_and_withdrawal` | `plo_operations` | `plo_operations.beirut_defence_withdrawal`: unrecorded → `defence_and_withdrawal_recorded` |
| `record_camp_defence` | `war_of_camps` | `war_of_camps.plo_defence`: unrecorded → `qualified_plo_camp_defence_recorded` |

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

- Normal: The interface publishes distinct records across the early conflict, Israeli interventions and War of the Camps, with each reactive row gated by information from the relevant source actor.
- Missing information: Litani, invasion and camp-defence rows require actual delivered notices. A late notice may arrive after the bounded choice window and remain terminally delivered without forcing action.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: Resistance and withdrawal records do not imply military success, civilian protection, expulsion truth or the absence of later PLO activity.
- Perturbation: Delaying its camp-defence notice to Hezbollah can leave later support and the Taif chain open while earlier PLO records remain accepted.

A premature choice, foreign-actor write, future-information leak or undeclared
environment effect falsifies this contract and must fail review or admission.

## 10. Limitations and successor route

It cannot act for LNM, civilians, refugee residents, Israel or Syria, create casualties or territory, transfer aid, prove cross-border attacks, or determine a battle or ceasefire result. E2 and E7 transactions/relations repeatedly use P_3 where their descriptions name Israel, Amal or another actor. Those endpoints are rejected as authority. Current values remain qualified actor-local records.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
