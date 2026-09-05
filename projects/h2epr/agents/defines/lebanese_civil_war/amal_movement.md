# Amal Movement Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0892.agent.amal_movement.v1` |
| Actor ID | `amal_movement` |
| Benchmark | H2EPR-0892, 1975-04-13 through the Draft's qualified 1990-10-13 post-war boundary |
| Representation | agent; one camp-campaign record and one Taif-position record |
| Source ID | `P_10` |
| Primary choices | Record its represented War-of-the-Camps campaign and later its qualified Taif disarmament position. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_10 appears in E7 and E8 as an organizational militia/political interface. The two records are separated by role and time; neither models members, tactics, uniform preferences or later political evolution.

It cannot act for Syria or all Shia actors, generate siege harm or supplies, determine camp control, bind Hezbollah, implement disarmament, or establish a peace outcome. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S3/E7/P_10 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E8/P_10 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002 and SRC008, with retrospective SRC009/SRC010 context. E7 relations misname P_3 as Amal and use incorrect endpoints for Syrian or alleged Israeli support. Current P_10 capability comes from its actor-local rows, not those edges.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record its represented War-of-the-Camps campaign and later its qualified Taif disarmament position. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

A camp-campaign record has no casualty, aid, territory or humanitarian effect. A Taif position is not actual disarmament or agreement implementation.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

The Taif row waits for Syrian mediation delivery. Missing invitation leaves only the earlier campaign record. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_war_of_camps_campaign` | source-bounded availability and own record not yet made | Record Amal's represented camp campaign without siege mechanics, supplies, casualties or territorial outcomes. |
| `record_amal_taif_position` | known `taif_mediation_notice` from `syrian_state_intervention_interface` | Record Amal's qualified disarmament position, not actual disarmament or compliance. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_war_of_camps_campaign` | `war_of_camps` | `war_of_camps.amal_campaign`: unrecorded → `qualified_amal_campaign_recorded` |
| `record_amal_taif_position` | `taif_process` | `taif_process.amal_position`: unrecorded → `qualified_disarmament_position_recorded` |

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

- Normal: Amal publishes a qualified camp campaign, later receives mediation and records its own disarmament position.
- Missing information: The Taif row waits for Syrian mediation delivery. Missing invitation leaves only the earlier campaign record.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: A camp-campaign record has no casualty, aid, territory or humanitarian effect. A Taif position is not actual disarmament or agreement implementation.
- Perturbation: Removing the mediation notice to Amal leaves its position and Syria's all-position enforcement row open.

A premature choice, foreign-actor write, future-information leak or undeclared
environment effect falsifies this contract and must fail review or admission.

## 10. Limitations and successor route

It cannot act for Syria or all Shia actors, generate siege harm or supplies, determine camp control, bind Hezbollah, implement disarmament, or establish a peace outcome. E7 relations misname P_3 as Amal and use incorrect endpoints for Syrian or alleged Israeli support. Current P_10 capability comes from its actor-local rows, not those edges.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
