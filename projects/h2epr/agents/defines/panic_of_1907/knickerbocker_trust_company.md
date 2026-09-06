# Knickerbocker Trust Company Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0288.agent.knickerbocker_trust_company.v1` |
| Actor ID | `knickerbocker_trust_company` |
| Benchmark | H2EPR-0288, October 1907–January 1908 acute record boundary with a coarse post-crisis reform horizon through 1913-12-23 |
| Representation | agent; Knickerbocker aid-request, leadership-dismissal and operations-suspension interface |
| Source ID | `P_7` |
| Primary choices | Request emergency assistance, record the represented chairman dismissal, and suspend operations after the bounded run and delivered aid denials. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_7 is a non-NYCH trust company across E4/E5. Three records separate seeking support, its board-level dismissal and the later operating suspension.

Knickerbocker cannot issue its own aid decision, write depositor withdrawals, make other trusts run, determine its solvency, or establish systemic contagion. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S2/E4/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E5/P_7 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC007, SRC009 and SRC011, with the same records byte-duplicated. The Draft's E4 relationship endpoints are malformed and omit the clearing agent identity. The current model does not synthesize missing P_8 or National Bank of Commerce authority.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may request emergency assistance, record the represented chairman dismissal, and suspend operations after the bounded run and delivered aid denials. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

An aid request has no liquidity effect. A chairman dismissal neither resolves the run nor authorizes the two requested rescuers.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Suspension requires its own earlier request/dismissal records, the public run record, and delivered denials from NYCH and Morgan. Any missing item leaves suspension open. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `request_emergency_assistance` | known `failed_copper_scheme_report` from `augustus_heinze_scheme_interface`; known `failed_copper_scheme_report` from `charles_morse_scheme_interface` | Record the represented aid request and route it separately to NYCH and Morgan; requesting creates no liquidity. |
| `record_chairman_dismissal` | `knickerbocker.aid_request` = `submitted_to_nych_and_morgan` | Record the represented board dismissal separately from aid decisions and operations suspension. |
| `suspend_knickerbocker_operations` | known `knickerbocker_aid_denial` from `new_york_clearing_house`; known `knickerbocker_aid_denial` from `jp_morgan_rescue_interface`; `knickerbocker.aid_request` = `submitted_to_nych_and_morgan`; `knickerbocker.chairman_dismissal` = `charles_barney_dismissal_recorded`; `withdrawals.knickerbocker_run` = `aggregate_run_recorded` | Record the represented operations suspension only after its internal records, aggregate run and both delivered aid dispositions exist. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `request_emergency_assistance` | `knickerbocker` | `knickerbocker.aid_request`: unrecorded → `submitted_to_nych_and_morgan` |
| `record_chairman_dismissal` | `knickerbocker` | `knickerbocker.chairman_dismissal`: unrecorded → `charles_barney_dismissal_recorded` |
| `suspend_knickerbocker_operations` | `knickerbocker` | `knickerbocker.operations`: unrecorded → `suspended_recorded` |

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

- Normal: The company requests aid, records the dismissal, receives both denials, then records suspension and publishes a qualified suspension notice.
- Missing information: Suspension requires its own earlier request/dismissal records, the public run record, and delivered denials from NYCH and Morgan. Any missing item leaves suspension open.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: An aid request has no liquidity effect. A chairman dismissal neither resolves the run nor authorizes the two requested rescuers.
- Perturbation: Suppressing the aid request blocks both decisions and suspension, testing downstream trust-run dependence without inventing an alternative rescue.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and successor route

Knickerbocker cannot issue its own aid decision, write depositor withdrawals, make other trusts run, determine its solvency, or establish systemic contagion. The Draft's E4 relationship endpoints are malformed and omit the clearing agent identity. The current model does not synthesize missing P_8 or National Bank of Commerce authority.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
