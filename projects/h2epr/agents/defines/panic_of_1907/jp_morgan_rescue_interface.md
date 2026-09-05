# J.P. Morgan Rescue Interface Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0288.agent.jp_morgan_rescue_interface.v1` |
| Actor ID | `jp_morgan_rescue_interface` |
| Benchmark | H2EPR-0288, October 1907–January 1908 acute record boundary with a coarse post-crisis reform horizon through 1913-12-23 |
| Representation | agent; private aid disposition and bounded trust/NYSE liquidity-support records |
| Source ID | `P_9` |
| Primary choices | Decide the Knickerbocker request and record separate private support for distressed trusts and the NYSE call-loan market. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_9 appears across four episodes. The parent preserves one denied request and two later support interfaces without treating Morgan as a central bank or owner of market recovery.

Morgan cannot act for NYCH, withdraw deposits, suspend institutions, create a gold flow, resolve every trust run, legislate reform or prove a counterfactual avoided collapse. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S2/E4/P_9 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E5/P_9 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E6/P_9 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E8/P_9 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC007, SRC009 and SRC011. Draft E6 relationships reverse creditor/funder directions and E8 sends bailout funds to depositors. Actor-local rescue descriptions, not those endpoints, define the qualified records.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may decide the Knickerbocker request and record separate private support for distressed trusts and the NYSE call-loan market. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

A denial has no state effect beyond its record/message. Trust support and NYSE support are distinct; neither creates cash conservation or a recovery outcome.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

The denial waits for the request, trust support waits for an actual trust-run notice, and NYSE support waits for a delivered call-loan liquidity notice. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `decline_knickerbocker_aid_request` | known `knickerbocker_aid_request` from `knickerbocker_trust_company` | Record Morgan's represented declined request after the bounded review failed to resolve financial condition; no insolvency truth is asserted. |
| `coordinate_private_trust_support` | known `trust_run_notice` from `general_depositor_population` | Record the bounded private support continuum for distressed trusts without conserved funds, guaranteed stabilization or counterfactual collapse claims. |
| `record_nyse_liquidity_support` | known `call_loan_liquidity_notice` from `new_york_trust_company_population` | Record the separately triggered NYSE liquidity support account without simulating lending balances, brokers, rates or exchange closure. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `decline_knickerbocker_aid_request` | `knickerbocker` | `knickerbocker.morgan_aid_disposition`: unrecorded → `declined_unresolved_request` |
| `coordinate_private_trust_support` | `private_rescue` | `private_rescue.trust_support`: unrecorded → `qualified_support_recorded` |
| `record_nyse_liquidity_support` | `private_rescue` | `private_rescue.nyse_support`: unrecorded → `qualified_support_recorded` |

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

- Normal: Morgan denies the unresolved Knickerbocker request, then records trust support and a separately triggered NYSE liquidity intervention.
- Missing information: The denial waits for the request, trust support waits for an actual trust-run notice, and NYSE support waits for a delivered call-loan liquidity notice.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: A denial has no state effect beyond its record/message. Trust support and NYSE support are distinct; neither creates cash conservation or a recovery outcome.
- Perturbation: Without trust contagion, later support rows remain open even though the earlier request disposition can still close.

A premature choice, foreign-actor write, future-information leak or undeclared
environment effect falsifies this contract and must fail review or admission.

## 10. Limitations and successor route

Morgan cannot act for NYCH, withdraw deposits, suspend institutions, create a gold flow, resolve every trust run, legislate reform or prove a counterfactual avoided collapse. Draft E6 relationships reverse creditor/funder directions and E8 sends bailout funds to depositors. Actor-local rescue descriptions, not those endpoints, define the qualified records.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
