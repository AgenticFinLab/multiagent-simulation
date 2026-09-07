# Mainland China Regular Note7 Purchasers Population Model

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0481.population.china_regular_note7_purchasers.v1` |
| Choice unit | one aggregate interface for P_7, with separate incident-report, dispute and filing records |
| Runtime representation | one aggregate Population actor; no individual agents or weighted samples |
| Actor ID | `china_regular_note7_purchasers` |
| Benchmark | H2EPR-0481, August 2016–January 2017 represented boundary |
| Representation | population; aggregate incident-report, public-dispute and litigation-filing interface |
| Source ID | `P_7` |
| Primary choices | Record a domestic incident report, dispute the represented supplier/manufacturer explanation, and file the later represented civil claim. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Population scope and representation

P_7 consolidates the same regular-purchaser cohort across incident, full-recall and litigation appearances. Separate fields preserve reporting, public disagreement and legal filing; no individual claimant is synthesized.

The Population does not establish physical cause, injury, damages, judicial acceptance, case outcome, recall participation or public-opinion prevalence. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

The regular-purchaser cohort excludes P_5 test-unit owners and P_3 global purchasers. Repeated appearances are the same aggregate interface, not additional independent respondents.

Aggregation is categorical: an accepted intent records one bounded group-level
choice. No weights, shares, representative individual, or unanimity are inferred.
An independently attributable unit with its own observations or veto requires
roster and semantic review; a purely passive group belongs in scenario/context.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S2/E5/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E7/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E8/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC004, SRC005, SRC006, SRC007, SRC008, SRC009 and SRC011. The Draft attaches consumer-dispute and litigation prose to wrong endpoints in several relation rows. P_7's actor-local actions own only the three qualified records.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role and relationships

This population may record a domestic incident report, dispute the represented supplier/manufacturer explanation, and file the later represented civil claim. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

A disputed Samsung statement remains a recorded manufacturer position; the Population cannot erase it or compel an apology, recall or judgment.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Without both delivered September statements, the selected dispute row waits. The later lawsuit row is separately available and does not prove liability. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

No individual persistent state is instantiated. The fields in module 7 are
aggregate world records owned by shared handlers/reducer; received and own-action
memory belongs to this single runtime interface.

## 6. Choice model and heterogeneity

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `report_mainland_battery_incident` | source-bounded availability and own record not yet made | Record aggregate mainland incident reporting without resolving physical cause. |
| `record_public_safety_dispute` | known `samsung_incident_account` from `samsung_electronics`; known `atl_incident_account` from `atl_battery_supplier` | Record the aggregate public dispute after both represented accounts are received. |
| `file_represented_consumer_litigation` | `recall.china_full` = `announced_190984_units` | Record the represented civil filing without court acceptance, liability or judgment. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

Heterogeneity is unmodeled, not assumed absent. There is no distribution,
independence, perfect-correlation, or representative-agent claim. The aggregate
rows can differ through their own observations and prerequisites; adaptation
is the bounded retry behavior described above, not learning or calibrated
preference change. No general eventual-response duty is machine-enforced.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `report_mainland_battery_incident` | `domestic_incidents` | `domestic_incidents.consumer_report`: unrecorded → `recorded` |
| `record_public_safety_dispute` | `domestic_dispute` | `domestic_dispute.consumer_position`: unrecorded → `dispute_recorded` |
| `file_represented_consumer_litigation` | `post_recall` | `post_recall.consumer_litigation`: unrecorded → `filed_recorded` |

The environment checks actor, target, parameters and preconditions against the
same sealed state. Rejection yields no delta. Coupled messages have independent
transport dispositions and do not prove action acceptance or recipient uptake.

## 8. Configuration and uncertainty

| Construct | Owner | Behavioral use |
|---|---|---|
| Availability window | Rule configuration | Bounded waiting for supported information. |
| Priority | Rule configuration | Orders overlapping rows under one action per actor/tick. |
| Route latency | Shared configuration | Determines actual information availability. |
| Message payload | Backend configuration within this parent | Reports qualified content without granting effects. |

All are structural choices, not calibrated probabilities or historical timings.

Only the aggregate instantiation above is supported. Changing population size,
weights or distributions is not a current configuration option. Sensitivity
within this model concerns admitted information and Rule selection windows;
changing aggregation routes to the parent and roster owners.

## 9. Worked cases and falsification

- Normal: A domestic report informs Samsung and ATL; their delivered statements can enable the aggregate dispute, which informs but does not force Samsung's apology.
- Missing information: Without both delivered September statements, the selected dispute row waits. The later lawsuit row is separately available and does not prove liability.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: A disputed Samsung statement remains a recorded manufacturer position; the Population cannot erase it or compel an apology, recall or judgment.
- Perturbation: Removing the domestic report blocks the explanation/dispute chain while later product-exit and investigation chains remain independently possible.

- Aggregate alternatives: Withholding one manufacturer/supplier account may leave dispute unrecorded while the separately enabled incident report remains recorded; disagreement and litigation are distinct choices.
- Aggregation change: A named claimant or independent information set would require a separate reviewed representation. Splitting this cohort without new data would invent claimant counts and correlations.
- Rejected request: a stale or unauthorized intent produces no aggregate state
  delta and no accepted-source message; a later retry requires changed visible
  information, not an invented additional population member.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and source anchors

The Population does not establish physical cause, injury, damages, judicial acceptance, case outcome, recall participation or public-opinion prevalence. The Draft attaches consumer-dispute and litigation prose to wrong endpoints in several relation rows. P_7's actor-local actions own only the three qualified records.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
