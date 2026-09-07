# New York Trust Company Population Model

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0288.population.new_york_trust_company_population.v1` |
| Choice unit | one aggregate liquidation-record interface for the other New York trusts grouped under P_10 |
| Runtime representation | one aggregate Population actor; no individual agents or weighted samples |
| Actor ID | `new_york_trust_company_population` |
| Benchmark | H2EPR-0288, October 1907–January 1908 acute record boundary with a coarse post-crisis reform horizon through 1913-12-23 |
| Representation | population; aggregate trust-company balance-liquidation record under delivered run pressure |
| Source ID | `P_10` |
| Primary choices | Record the represented liquidation of cash balances at national banks after trust-company run pressure is delivered. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Population scope and representation

P_10 groups other New York trusts, including Trust Company of America. The Population Model retains one aggregate balance-liquidation record and treats being run on or supported as results.

It cannot represent every trust, choose depositor withdrawals, quantify balances, seize the call-loan market, receive conserved bailout funds or certify stabilization. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

The source group includes Trust Company of America; it excludes the separately represented Knickerbocker interface. Passive run-target and rescue-recipient roles do not create additional population decisions.

Aggregation is categorical: an accepted intent records one bounded group-level
choice. No weights, shares, representative individual, or unanimity are inferred.
An independently attributable unit with its own observations or veto requires
roster and semantic review; a purely passive group belongs in scenario/context.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S2/E5/P_10 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E6/P_10 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E8/P_10 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC003, SRC007, SRC009 and SRC011. The Draft mixes passive run-target/rescue-recipient roles with the active liquidation row and reverses later transaction endpoints. Only the bounded aggregate liquidation is selectable.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role and relationships

This population may record the represented liquidation of cash balances at national banks after trust-company run pressure is delivered. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

The record sends a qualified liquidity notice; it does not directly close the NYSE or determine interest rates.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Without delivered trust-run information, the population waits and the call-loan-dependent Morgan row remains open. Memory persists across this bounded event without a
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
| `record_national_bank_balance_liquidation` | known `trust_run_notice` from `general_depositor_population` | Record the represented aggregate liquidation of national-bank balances under trust run pressure; no amount or bank-level path is fabricated. |

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
| `record_national_bank_balance_liquidation` | `trust_liquidity` | `trust_liquidity.national_bank_balances`: unrecorded → `aggregate_liquidation_recorded` |

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

- Normal: After receiving the trust-run notice, the population records balance liquidation and informs Morgan of the qualified call-loan liquidity stress.
- Missing information: Without delivered trust-run information, the population waits and the call-loan-dependent Morgan row remains open.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: The record sends a qualified liquidity notice; it does not directly close the NYSE or determine interest rates.
- Perturbation: Suppressing the trust-run notice leaves both liquidation and downstream NYSE support open while terminal evidence can remain valid.

- Aggregate alternatives: No delivered trust-run notice leaves liquidation unrecorded; its receipt may enable the bounded liquidation record without specifying how much any trust liquidates.
- Aggregation change: Trust-specific liquidity, constraints or vetoes require separately justified units. Splitting the group cannot conserve or allocate balances because no cash ledger exists.
- Rejected request: a stale or unauthorized intent produces no aggregate state
  delta and no accepted-source message; a later retry requires changed visible
  information, not an invented additional population member.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and source anchors

It cannot represent every trust, choose depositor withdrawals, quantify balances, seize the call-loan market, receive conserved bailout funds or certify stabilization. The Draft mixes passive run-target/rescue-recipient roles with the active liquidation row and reverses later transaction endpoints. Only the bounded aggregate liquidation is selectable.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
