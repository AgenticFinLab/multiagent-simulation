# United States Congress Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0170.agent.united_states_congress.v1` |
| Actor ID | `united_states_congress` |
| Benchmark | H2EPR-0170, 2020-08-06 through the Draft's qualified 2025-09-15 negotiation and grace-extension endpoint |
| Representation | agent; the represented PAFACA passage record |
| Source ID | `P_8` |
| Primary choices | Record passage of PAFACA and submit the qualified bill record to the President. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_8 appears once as the full legislature. The interface records the exposed passage outcome without simulating chambers, members, votes, amendments or procedure.

Congress cannot sign its own bill, issue court rulings, enforce divestment, suspend TikTok service, determine security risk, or model individual legislators. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S3/E6/P_8 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC004, SRC008, SRC009, SRC010 and SRC011. E6 relations swap bill-submission and regulatory-target endpoints. Current passage sends a bill notice to P_4 and qualified law context to P_2/P_3 only after signature.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may record passage of PAFACA and submit the qualified bill record to the President. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

Passage is not enactment, constitutional validity, enforcement, ownership transfer or platform shutdown.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

The current Rule waits for the represented oversight testimony and proposal record. If either is unavailable, passage remains a descriptive open endpoint. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `pass_pafaca` | known `anti_tiktok_proposal_record` from `state_and_legislative_restriction_population`; known `hearing_testimony_record` from `shouzi_chew_testimony_interface` | Record the exposed PAFACA passage after the proposal and hearing record are actually known; votes and legal effect remain outside this field. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `pass_pafaca` | `legislation` | `legislation.pafaca_passage`: unrecorded → `passed_recorded` |

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

- Normal: Congress records passage after the bounded public oversight chain and sends the bill to Biden for a separate signature decision.
- Missing information: The current Rule waits for the represented oversight testimony and proposal record. If either is unavailable, passage remains a descriptive open endpoint.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: Passage is not enactment, constitutional validity, enforcement, ownership transfer or platform shutdown.
- Perturbation: Missing testimony preserves earlier restrictions but leaves passage and its dependent chain open.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and successor route

Congress cannot sign its own bill, issue court rulings, enforce divestment, suspend TikTok service, determine security risk, or model individual legislators. E6 relations swap bill-submission and regulatory-target endpoints. Current passage sends a bill notice to P_4 and qualified law context to P_2/P_3 only after signature.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
