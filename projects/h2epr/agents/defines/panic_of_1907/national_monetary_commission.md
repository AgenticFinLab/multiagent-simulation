# National Monetary Commission Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0288.agent.national_monetary_commission.v1` |
| Actor ID | `national_monetary_commission` |
| Benchmark | H2EPR-0288, October 1907–January 1908 acute record boundary with a coarse post-crisis reform horizon through 1913-12-23 |
| Representation | agent; commission inquiry-process and recommendation-publication interface |
| Source ID | `P_16` |
| Primary choices | Record the represented banking-system inquiry and publish bounded recommendations after receiving its congressional mandate. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_16 is a distinct government commission. Process and recommendations are separated so mandate receipt, work and publication cannot collapse into one forced outcome.

The commission cannot create its own mandate, pass legislation, operate a central bank, determine the exact reform design, or prove that its work caused later stability. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S3/E10/P_16 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC005, SRC007, SRC009 and SRC011. The frozen set describes the commission and eventual Act only coarsely. Current records do not invent hearings, members, report contents or dates beyond the exposed interval.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record the represented banking-system inquiry and publish bounded recommendations after receiving its congressional mandate. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

Conducting an inquiry does not publish recommendations; recommendations do not enact a statute.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Both rows require the delivered congressional mandate or the prior commission-process state. Without them, no reform default is synthesized. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `conduct_banking_system_inquiry` | known `commission_mandate` from `united_states_congress` | Record the represented commission process without inventing hearings, members, evidence or report details. |
| `publish_banking_reform_recommendations` | `reform.commission_process` = `bounded_inquiry_recorded` | Record a bounded recommendation publication after the inquiry process and deliver it to Congress; it does not enact policy. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `conduct_banking_system_inquiry` | `reform` | `reform.commission_process`: unrecorded → `bounded_inquiry_recorded` |
| `publish_banking_reform_recommendations` | `reform` | `reform.commission_recommendations`: unrecorded → `qualified_recommendations_recorded` |

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

- Normal: The commission receives its mandate, records a bounded inquiry process, then publishes a qualified recommendation record to Congress.
- Missing information: Both rows require the delivered congressional mandate or the prior commission-process state. Without them, no reform default is synthesized.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: Conducting an inquiry does not publish recommendations; recommendations do not enact a statute.
- Perturbation: Increasing recommendation-route latency can leave the Act open despite an accepted publication, directly exercising information-sensitive closure.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and successor route

The commission cannot create its own mandate, pass legislation, operate a central bank, determine the exact reform design, or prove that its work caused later stability. The frozen set describes the commission and eventual Act only coarsely. Current records do not invent hearings, members, report contents or dates beyond the exposed interval.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
