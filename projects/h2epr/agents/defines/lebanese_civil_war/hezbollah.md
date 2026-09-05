# Hezbollah Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0892.agent.hezbollah.v1` |
| Actor ID | `hezbollah` |
| Benchmark | H2EPR-0892, 1975-04-13 through the Draft's qualified 1990-10-13 post-war boundary |
| Representation | agent; camp-support, Taif-position and post-war exemption-status records |
| Source ID | `P_11` |
| Primary choices | Record represented support for PLO camp defence, a qualified Taif position and a later exemption-status record. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_11 appears in E7–E9 under changing militia, negotiating and post-war roles. One organizational parent separates the three records and does not back-project later prominence into the earlier event.

It cannot act for Amal, the PLO, Syria or all Shia actors, generate combat outcomes, guarantee an exemption, implement Taif, prove disarmament status, or establish later political power. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S3/E7/P_11 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E8/P_11 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E9/P_11 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC001, SRC002, SRC008 and SRC010. Post-war and 2008 material is retrospective context only. E7 relationship endpoints swap Syria/PLO/Hezbollah meanings; actor-local P_11 rows govern current authority.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record represented support for PLO camp defence, a qualified Taif position and a later exemption-status record. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

Support is a qualified record without tactical or casualty effects. A negotiation position does not secure an exemption; the later status row requires delivered enforcement context.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Camp support waits for PLO defence information; Taif position waits for mediation; exemption status waits for the enforcement notice. Any may remain open. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_hezbollah_camp_support` | known `plo_camp_defence_record` from `palestine_liberation_organization` | Record represented Hezbollah support after receiving PLO camp-defence information; no tactical or casualty effect follows. |
| `record_hezbollah_taif_position` | known `taif_mediation_notice` from `syrian_state_intervention_interface` | Record Hezbollah's qualified exemption position without granting or implementing an exemption. |
| `record_postwar_exemption_status` | known `taif_enforcement_notice` from `syrian_state_intervention_interface` | Record the represented post-war exemption status only after enforcement notice; no legal validity or future capability is inferred. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_hezbollah_camp_support` | `war_of_camps` | `war_of_camps.hezbollah_support`: unrecorded → `qualified_hezbollah_support_recorded` |
| `record_hezbollah_taif_position` | `taif_process` | `taif_process.hezbollah_position`: unrecorded → `qualified_exemption_position_recorded` |
| `record_postwar_exemption_status` | `postwar_records` | `postwar_records.hezbollah_exemption_status`: unrecorded → `qualified_exemption_status_recorded` |

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

- Normal: The interface reacts to the delivered PLO camp-defence record, later publishes its own Taif position, and records a distinct post-war status after enforcement notice.
- Missing information: Camp support waits for PLO defence information; Taif position waits for mediation; exemption status waits for the enforcement notice. Any may remain open.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: Support is a qualified record without tactical or casualty effects. A negotiation position does not secure an exemption; the later status row requires delivered enforcement context.
- Perturbation: Delaying PLO-to-Hezbollah delivery beyond the support window suppresses the camp-support and mediation-dependent resolution chain while closing transport normally.

A premature choice, foreign-actor write, future-information leak or undeclared
environment effect falsifies this contract and must fail review or admission.

## 10. Limitations and successor route

It cannot act for Amal, the PLO, Syria or all Shia actors, generate combat outcomes, guarantee an exemption, implement Taif, prove disarmament status, or establish later political power. Post-war and 2008 material is retrospective context only. E7 relationship endpoints swap Syria/PLO/Hezbollah meanings; actor-local P_11 rows govern current authority.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
