# Israeli State-Intervention Record Interface Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0892.agent.israeli_state_intervention_interface.v1` |
| Actor ID | `israeli_state_intervention_interface` |
| Benchmark | H2EPR-0892, 1975-04-13 through the Draft's qualified 1990-10-13 post-war boundary |
| Representation | agent; three separately typed Israeli intervention and facilitation records |
| Source ID | `P_8` |
| Primary choices | Record Operation Litani, the 1982 full invasion/siege and qualified camp-entry facilitation. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_8 appears in four episodes. The duplicated Litani wording is consolidated into one current choice, while the later full invasion and camp-entry facilitation remain separate public-record transitions.

It cannot act for the Lebanese Front, determine PLO withdrawal, generate combat or civilian harm, establish occupation control, transfer aid, prove motive or legal responsibility, or write a massacre outcome. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S2/E3/P_8 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E4/P_8 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E5/P_8 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E6/P_8 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC004, SRC005, SRC008 and SRC011. The E4 relations omit or mispoint Israel and the E6 relation description names P_1 while its endpoint is P_8. Current authority follows P_8 actor-local rows and keeps direct camp action with P_1.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record Operation Litani, the 1982 full invasion/siege and qualified camp-entry facilitation. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

An intervention or facilitation record is not a tactical simulation, a casualty effect, victory, occupation measure or responsibility judgment.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Litani waits for the delivered PLO cross-border record; the later invasion waits for resistance; camp-entry facilitation waits for the Front's separate support record. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_operation_litani` | known `plo_cross_border_operations_record` from `palestine_liberation_organization` | Consolidate the duplicated Litani rows into one qualified intervention record without territorial or casualty effects. |
| `record_full_invasion_and_siege` | known `plo_litani_resistance_record` from `palestine_liberation_organization` | Record the 1982 invasion and siege account without simulating combat, casualties, territorial advance or success. |
| `record_camp_entry_facilitation` | known `front_siege_support_record` from `lebanese_front_record_interface` | Record the represented camp-entry facilitation separately from the Lebanese Front operation and all civilian harm. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_operation_litani` | `israeli_intervention` | `israeli_intervention.operation_litani`: unrecorded → `operation_litani_recorded` |
| `record_full_invasion_and_siege` | `israeli_intervention` | `israeli_intervention.full_invasion_siege`: unrecorded → `full_invasion_and_siege_recorded` |
| `record_camp_entry_facilitation` | `israeli_intervention` | `israeli_intervention.camp_entry_facilitation`: unrecorded → `qualified_camp_entry_facilitation_recorded` |

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

- Normal: The interface publishes three bounded records in order, each leaving the PLO or Lebanese Front to decide its own response.
- Missing information: Litani waits for the delivered PLO cross-border record; the later invasion waits for resistance; camp-entry facilitation waits for the Front's separate support record.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: An intervention or facilitation record is not a tactical simulation, a casualty effect, victory, occupation measure or responsibility judgment.
- Perturbation: Withholding the Front support notice leaves facilitation and the dependent camp-operation record open without altering the invasion record.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and successor route

It cannot act for the Lebanese Front, determine PLO withdrawal, generate combat or civilian harm, establish occupation control, transfer aid, prove motive or legal responsibility, or write a massacre outcome. The E4 relations omit or mispoint Israel and the E6 relation description names P_1 while its endpoint is P_8. Current authority follows P_8 actor-local rows and keeps direct camp action with P_1.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
