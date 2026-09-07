# New York Clearing House Member-Bank Population Model

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0288.population.ny_clearing_house_member_bank_population.v1` |
| Choice unit | one collective implementation-record interface for member banks grouped under P_12 |
| Runtime representation | one aggregate Population actor; no individual agents or weighted samples |
| Actor ID | `ny_clearing_house_member_bank_population` |
| Benchmark | H2EPR-0288, October 1907–January 1908 acute record boundary with a coarse post-crisis reform horizon through 1913-12-23 |
| Representation | population; represented collective implementation of deposit-convertibility suspension |
| Source ID | `P_12` |
| Primary choices | Record member-bank implementation after both certificate support and the clearing-house coordination directive are delivered. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Population scope and representation

P_12 appears once as a group-level policy implementer and liquidity recipient. The current Population Model retains only the collective suspension record.

It cannot issue certificates, coordinate itself, model individual banks, quantify withdrawals, create the currency premium, import gold or establish recovery. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

Membership is the represented group boundary; no individual bank is sampled or weighted. The clearing house is a separate Agent that issues certificates and coordination, not a population member decision merged into this interface.

Aggregation is categorical: an accepted intent records one bounded group-level
choice. No weights, shares, representative individual, or unanimity are inferred.
An independently attributable unit with its own observations or veto requires
roster and semantic review; a purely passive group belongs in scenario/context.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S3/E7/P_12 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC002, SRC003, SRC007, SRC008, SRC009 and SRC011. The Draft combines receipt of certificates with implementation in one action. Current semantics make receipt a message and suspension the population-owned decision record.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role and relationships

This population may record member-bank implementation after both certificate support and the clearing-house coordination directive are delivered. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

Certificate receipt alone does not suspend convertibility, and a group record does not imply identical bank-level timing or behavior.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Both NYCH messages must be actually delivered. A missing directive leaves suspension open rather than being filled from the stage description. Memory persists across this bounded event without a
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
| `implement_deposit_convertibility_suspension` | known `certificate_support_notice` from `new_york_clearing_house`; known `convertibility_suspension_coordination` from `new_york_clearing_house` | Record the represented collective implementation after both distinct NYCH messages; no bank-level uniformity or cash balance is implied. |

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
| `implement_deposit_convertibility_suspension` | `containment` | `containment.member_convertibility`: unrecorded → `aggregate_suspension_recorded` |

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

- Normal: The population receives certificate support and coordination, then records the represented collective suspension and emits a public premium signal.
- Missing information: Both NYCH messages must be actually delivered. A missing directive leaves suspension open rather than being filled from the stage description.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: Certificate receipt alone does not suspend convertibility, and a group record does not imply identical bank-level timing or behavior.
- Perturbation: Withholding coordination preserves certificate evidence but leaves suspension, gold-flow and dependent reform rows open.

- Aggregate alternatives: A certificate notice alone is insufficient in the selected policy; both distinct messages enable collective suspension recording without establishing uniform bank compliance.
- Aggregation change: Bank-specific refusal or separate information would require a successor representation. Multiplying group actors cannot establish a compliance fraction or create additional certificates.
- Rejected request: a stale or unauthorized intent produces no aggregate state
  delta and no accepted-source message; a later retry requires changed visible
  information, not an invented additional population member.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and source anchors

It cannot issue certificates, coordinate itself, model individual banks, quantify withdrawals, create the currency premium, import gold or establish recovery. The Draft combines receipt of certificates with implementation in one action. Current semantics make receipt a message and suspension the population-owned decision record.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
