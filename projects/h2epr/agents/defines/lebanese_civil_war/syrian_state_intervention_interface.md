# Syrian State-Intervention Record Interface Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0892.agent.syrian_state_intervention_interface.v1` |
| Actor ID | `syrian_state_intervention_interface` |
| Benchmark | H2EPR-0892, 1975-04-13 through the Draft's qualified 1990-10-13 post-war boundary |
| Representation | agent; eight separately typed Syrian intervention, support, mediation and post-war records |
| Source ID | `P_7` |
| Primary choices | Record deployment, territorial consolidation, alignment change, continued presence, Amal support, Taif mediation and enforcement, and post-war presence. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_7 appears across six episodes in changing intervention, belligerent, mediator and post-war roles. A representation gate preserves those public records without treating a state and armed forces as one timeless preference or tactical controller.

It cannot decide Lebanese faction positions, generate territorial or casualty outcomes, transfer weapons, prove motives or legality, write Israel's intervention, implement constitutional reform, or establish peace effectiveness. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E2/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E3/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E4/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E7/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E8/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E9/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC001, SRC002, SRC004, SRC005, SRC008 and SRC011. E2 and E7 edges repeatedly assign Syrian descriptions to other IDs. The current parent uses actor-local P_7 rows and qualified narrative only; alleged material transfers have no resource effect.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record deployment, territorial consolidation, alignment change, continued presence, Amal support, Taif mediation and enforcement, and post-war presence. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

Deployment does not follow automatically from a request. Alignment, support, mediation, enforcement and post-war presence are separate records; none establishes control, compliance or war termination.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Reactive rows wait for delivered government, LNM/PLO, Litani, camp and faction-position messages. Missing information permits open endpoints. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_initial_syrian_deployment` | known `syrian_intervention_request` from `lebanese_joint_government_interface` | Record Syrian deployment after the qualified request arrives; no control or battlefield outcome follows. |
| `record_syrian_territorial_consolidation` | `syrian_intervention.initial_deployment` = `deployment_recorded` | Record a qualified northern/eastern presence account without a territory ledger. |
| `record_syrian_alignment_change` | known `lnm_continued_conflict_record` from `lebanese_national_movement`; known `plo_continued_conflict_record` from `palestine_liberation_organization` | Record the Draft's represented alignment change after relevant continued-conflict records arrive. |
| `record_continued_syrian_presence` | known `operation_litani_notice` from `israeli_state_intervention_interface` | Record continued Syrian presence after Litani notice without producing occupation control or aid effects. |
| `record_syrian_support_for_amal` | known `amal_camp_campaign_record` from `amal_movement` | Record represented Syrian support for Amal without a weapons, finance or battlefield-effect transfer. |
| `record_taif_mediation` | known `amal_camp_campaign_record` from `amal_movement`; known `plo_camp_defence_record` from `palestine_liberation_organization`; known `hezbollah_camp_support_record` from `hezbollah` | Record the represented mediation framework after three camp-conflict records arrive; this does not itself form agreement. |
| `record_taif_enforcement` | known `front_taif_position` from `lebanese_front_record_interface`; known `amal_taif_position` from `amal_movement`; known `hezbollah_taif_position` from `hezbollah` | Record the represented enforcement/end-of-war framework after all three faction positions arrive; peace and implementation are not produced. |
| `record_postwar_syrian_presence` | `taif_process.enforcement` = `qualified_enforcement_recorded` | Record the Draft's post-war Syrian-presence boundary without a territory, sovereignty or effectiveness claim. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_initial_syrian_deployment` | `syrian_intervention` | `syrian_intervention.initial_deployment`: unrecorded → `deployment_recorded` |
| `record_syrian_territorial_consolidation` | `syrian_intervention` | `syrian_intervention.territorial_consolidation`: unrecorded → `northern_eastern_presence_recorded` |
| `record_syrian_alignment_change` | `syrian_intervention` | `syrian_intervention.alignment_change`: unrecorded → `lnm_plo_support_recorded` |
| `record_continued_syrian_presence` | `syrian_intervention` | `syrian_intervention.continued_presence`: unrecorded → `continued_presence_recorded` |
| `record_syrian_support_for_amal` | `war_of_camps` | `war_of_camps.syrian_amal_support`: unrecorded → `qualified_syrian_support_recorded` |
| `record_taif_mediation` | `taif_process` | `taif_process.mediation`: unrecorded → `qualified_taif_mediation_recorded` |
| `record_taif_enforcement` | `taif_process` | `taif_process.enforcement`: unrecorded → `qualified_enforcement_recorded` |
| `record_postwar_syrian_presence` | `postwar_records` | `postwar_records.syrian_presence`: unrecorded → `postwar_presence_recorded` |

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

- Normal: The interface records an ordered series of qualified roles, culminating in mediation, three-position receipt, enforcement and a separate post-war presence record.
- Missing information: Reactive rows wait for delivered government, LNM/PLO, Litani, camp and faction-position messages. Missing information permits open endpoints.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: Deployment does not follow automatically from a request. Alignment, support, mediation, enforcement and post-war presence are separate records; none establishes control, compliance or war termination.
- Perturbation: Omitting the Amal mediation invitation prevents the complete three-position bundle and therefore enforcement/post-war records while earlier Syrian records persist.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and successor route

It cannot decide Lebanese faction positions, generate territorial or casualty outcomes, transfer weapons, prove motives or legality, write Israel's intervention, implement constitutional reform, or establish peace effectiveness. E2 and E7 edges repeatedly assign Syrian descriptions to other IDs. The current parent uses actor-local P_7 rows and qualified narrative only; alleged material transfers have no resource effect.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
