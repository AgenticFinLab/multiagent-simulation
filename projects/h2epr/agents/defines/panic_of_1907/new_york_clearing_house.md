# New York Clearing House Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0288.agent.new_york_clearing_house.v1` |
| Actor ID | `new_york_clearing_house` |
| Benchmark | H2EPR-0288, October 1907–January 1908 acute record boundary with a coarse post-crisis reform horizon through 1913-12-23 |
| Representation | agent; member-bank stabilization, non-member aid denial, certificate issuance and convertibility-coordination interface |
| Source ID | `P_6` |
| Primary choices | Record the represented member stabilization, decide the Knickerbocker request, issue clearing-house certificates and coordinate member-bank convertibility suspension. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_6 spans three episodes with distinct authorities. The current parent keeps initial member support, a non-member request denial, emergency certificates and later coordination as four separate records.

NYCH cannot withdraw deposits, suspend Knickerbocker operations, decide for member banks, provide Morgan's capital, import gold, legislate reform or prove market recovery. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E3/P_6 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E4/P_6 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E7/P_6 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC003, SRC007, SRC008, SRC009 and SRC011. Draft E4 relation endpoints make depositors appear to request or deny aid. The Knickerbocker request and delivered decisions, not those relations, govern current authority.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record the represented member stabilization, decide the Knickerbocker request, issue clearing-house certificates and coordinate member-bank convertibility suspension. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

Supporting member banks does not support a non-member trust. Issuing certificates does not itself suspend deposit convertibility; member implementation remains separate.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Initial support waits for an actual member-run notice. Aid denial waits for Knickerbocker's request. Suspension coordination follows the certificate record and sends a separate directive. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `record_initial_member_bank_stabilization` | known `member_bank_run_notice` from `general_depositor_population` | Record the represented solvency assurance, management intervention and loan support for member banks without deciding depositor uptake. |
| `deny_nonmember_aid_request` | known `knickerbocker_aid_request` from `knickerbocker_trust_company` | Record NYCH's represented denial based on non-member scope; the message is a disposition, not an insolvency finding. |
| `issue_clearing_house_certificates` | known `trust_run_notice` from `general_depositor_population` | Record clearing-house certificate issuance as emergency member liquidity support, separate from convertibility implementation. |
| `coordinate_convertibility_suspension` | `containment.loan_certificates` = `issuance_recorded` | Record NYCH coordination after its certificate program exists; implementation remains owned by the member-bank population. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `record_initial_member_bank_stabilization` | `clearing_house` | `clearing_house.initial_member_support`: unrecorded → `assurance_management_and_loan_support_recorded` |
| `deny_nonmember_aid_request` | `knickerbocker` | `knickerbocker.nych_aid_disposition`: unrecorded → `denied_nonmember_request` |
| `issue_clearing_house_certificates` | `containment` | `containment.loan_certificates`: unrecorded → `issuance_recorded` |
| `coordinate_convertibility_suspension` | `containment` | `containment.convertibility_coordination`: unrecorded → `directive_recorded` |

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

- Normal: NYCH supports members, denies the delivered non-member request, later records certificates, and sends convertibility coordination to member banks.
- Missing information: Initial support waits for an actual member-run notice. Aid denial waits for Knickerbocker's request. Suspension coordination follows the certificate record and sends a separate directive.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: Supporting member banks does not support a non-member trust. Issuing certificates does not itself suspend deposit convertibility; member implementation remains separate.
- Perturbation: Missing trust-run notice leaves certificate and coordination rows open; delayed requests can leave aid disposition open without forcing runtime failure.

A premature choice, foreign-actor write, future-information leak or undeclared
environment effect falsifies this contract and must fail review or admission.

## 10. Limitations and successor route

NYCH cannot withdraw deposits, suspend Knickerbocker operations, decide for member banks, provide Morgan's capital, import gold, legislate reform or prove market recovery. Draft E4 relation endpoints make depositors appear to request or deny aid. The Knickerbocker request and delivered decisions, not those relations, govern current authority.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
