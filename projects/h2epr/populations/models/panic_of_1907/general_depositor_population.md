# General Public Depositor Population Population Model

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0288.population.general_depositor_population.v1` |
| Actor ID | `general_depositor_population` |
| Benchmark | H2EPR-0288, October 1907–January 1908 acute record boundary with a coarse post-crisis reform horizon through 1913-12-23 |
| Representation | population; aggregate withdrawal and cessation records exposed for public depositors |
| Source ID | `P_5` |
| Primary choices | Record bounded aggregate withdrawals from affiliated banks and trusts, and record cessation of the initial member-bank run after delivered assurance. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_5 appears in five episodes as an aggregate group. A Population Model retains the represented collective records without fabricating individual depositors, unanimity, cash amounts or a calibrated behavioral distribution.

The population cannot decide for banks, verify solvency, create a suspension, transfer conserved money, establish contagion causality, or prove that every depositor acted. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E2/P_5 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S1/E3/P_5 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E4/P_5 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E5/P_5 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E8/P_5 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC005, SRC007, SRC009 and SRC011. Draft transactions reverse or misidentify withdrawal endpoints, and later rescue transactions name P_5 as a funding recipient. Actor-local withdrawal rows control; monetary transfer and bailout receipt are not modeled.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This population may record bounded aggregate withdrawals from affiliated banks and trusts, and record cessation of the initial member-bank run after delivered assurance. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

One accepted aggregate withdrawal record neither moves a cash ledger nor forces another population's action. Cessation requires an actually delivered NYCH assurance.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Withdrawal rows wait for both separately delivered joint-scheme records or for a delivered Knickerbocker suspension. Missing information is a valid open endpoint. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_affiliated_bank_withdrawal_run` | known `failed_copper_scheme_report` from `augustus_heinze_scheme_interface`; known `failed_copper_scheme_report` from `charles_morse_scheme_interface` | Record the bounded aggregate run on affiliated banks after both scheme records are actually known; no cash ledger or universal depositor behavior follows. |
| `record_initial_run_cessation` | known `member_bank_stabilization_notice` from `new_york_clearing_house` | Record the Draft's bounded cessation account after delivered clearing-house assurance, not a calibrated response rate or causal estimate. |
| `record_knickerbocker_withdrawal_run` | known `failed_copper_scheme_report` from `augustus_heinze_scheme_interface`; known `failed_copper_scheme_report` from `charles_morse_scheme_interface` | Record aggregate Knickerbocker withdrawals after both public scheme records; association and confidence remain qualified narrative, not a probability model. |
| `record_trust_company_withdrawal_run` | known `knickerbocker_suspension_notice` from `knickerbocker_trust_company` | Record the bounded spread of aggregate withdrawals to other trusts after Knickerbocker suspension is delivered; no network coefficient is inferred. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_affiliated_bank_withdrawal_run` | `withdrawals` | `withdrawals.affiliated_bank_run`: unrecorded → `aggregate_run_recorded` |
| `record_initial_run_cessation` | `withdrawals` | `withdrawals.affiliated_bank_run_cessation`: unrecorded → `aggregate_cessation_recorded` |
| `record_knickerbocker_withdrawal_run` | `withdrawals` | `withdrawals.knickerbocker_run`: unrecorded → `aggregate_run_recorded` |
| `record_trust_company_withdrawal_run` | `withdrawals` | `withdrawals.trust_company_run`: unrecorded → `aggregate_contagion_run_recorded` |

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

- Normal: The population records the initial run, later cessation after assurance, the Knickerbocker run, and trust-company contagion after suspension becomes known.
- Missing information: Withdrawal rows wait for both separately delivered joint-scheme records or for a delivered Knickerbocker suspension. Missing information is a valid open endpoint.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: One accepted aggregate withdrawal record neither moves a cash ledger nor forces another population's action. Cessation requires an actually delivered NYCH assurance.
- Perturbation: Withholding a scheme record blocks early withdrawals; withholding the suspension leaves trust-company contagion open while other valid records may continue.

A premature choice, foreign-actor write, future-information leak or undeclared
environment effect falsifies this contract and must fail review or admission.

## 10. Limitations and successor route

The population cannot decide for banks, verify solvency, create a suspension, transfer conserved money, establish contagion causality, or prove that every depositor acted. Draft transactions reverse or misidentify withdrawal endpoints, and later rescue transactions name P_5 as a funding recipient. Actor-local withdrawal rows control; monetary transfer and bailout receipt are not modeled.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
