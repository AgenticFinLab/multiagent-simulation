# NYCH Member and Large Correspondent Bank Resource-Decision Population

## 1. Model overview

| Field | Description |
|---|---|
| Model name | NYCH member and large correspondent bank resource-decision units |
| Event and interval | Panic of 1907, acute New York phase, approximately 23–26 October 1907 |
| Choice unit | One institution with its own authority, resource envelope, relationship role, and request or commitment lifecycles |
| Population scope | NYCH member banks and large correspondent banks participating in, declining, or using collective-support and resource mechanisms |
| Primary decision situations | Request information, make a conditional offer or commitment, decline, revise a commitment, or apply for member certificates |
| Aggregation boundary | Historical institutions remain weight-one units and retain independent resources and commitments; weighted synthetic compression requires a separate representation review |
| State authority | Resource, collateral, certificate, transfer, settlement, and realized support truth remains scenario- or facility-owned; each unit retains only its decision posture and observed lifecycles |
| Evidence use and explanatory scope | Contemporary and retrospective sources informed an event-bound reconstruction; named-bank policies, response probabilities, commitment rules, and posture distributions are not recovered or calibrated |

The population represents independent institutional decisions that lie between
a coordinator's solicitation and an environment's realized resource effect.
It preserves the fact that institutions could participate, condition, defer,
decline or seek an institutional facility without giving all banks one voice
or inventing separate biographies from reported outcomes.

The product is not a general banking-sector Agent and not a call-money market
model. It addresses only the collective-support and closely related NYCH
member-resource interfaces needed by H2EPR-0288.

## 2. Population scope and representation

### Historical population

The event record names some large banks or firms in loans and coordinated
pools, reports that others held back, and describes resource mechanisms in
which member banks retained their own applications and collateral
(`CBC-C01`–`CBC-C05`). Attribution and amounts vary, while complete authority,
private information and decision rules are absent (`CBC-C06`–`CBC-C07`).

### Modeled choice unit

A choice unit represents one institution included by a declared scenario
configuration. It retains:

- institution and membership identity;
- a bounded capability/relationship role;
- its own decision authority;
- a delivered projection of its own resource and commitment envelope;
- request, offer, commitment and certificate-application lifecycles; and
- one exposed structural participation posture.

The unit is not an anonymous share of a common wallet. Each unit has weight one
in an event-bound reconstruction. Population aggregation summarizes delivered
responses and realized results while preserving their institutional origin.
Weighted synthetic compression would require a new representation review and
cannot own historical commitments in this version.

### Why not one Agent or many named Agent Definitions

One Agent would invent a shared observation, preference, authority and balance
sheet. Separate named Agent Definitions would require private policies that
the current sources do not recover. The population is the least complex
representation that retains independent commitment and facility-demand
choices without converting outcome attribution into policy.

A named institution is promoted to its own Agent only when direct evidence
establishes a distinct decision interface and its aggregation removes a
predeclared causal prediction.

## 3. Evidence and theoretical foundation

### Event-specific evidence

| Claim | What it supports | What it does not support |
|---|---|---|
| `CBC-C01` | participation/nonparticipation and institution heterogeneity | exact private motive or probability |
| `CBC-C02` | coordinator/contributor/resource separation | command by Morgan, committee or NYCH over independent bank resources |
| `CBC-C03` | multi-party collateral/resource route | universal route, fungible pooled ownership or automatic transfer |
| `CBC-C04`–`CBC-C05` | member choice to apply and variable certificate use under a governed facility | back-projection before October 26 or automatic approval |
| `CBC-C06`–`CBC-C07` | conflicting attribution and missing named policies | historical calibration or name-based behavior |
| `CBC-C08` | lifecycle separation | executable business state machine already exists |
| `CBC-C09` | institution-preserving population identity | need for a full named biography |
| `CBC-C10` | R3 scope limit | call-money/NYSE behavior |

### Behavioral lens

Simon's bounded-choice framework supports institution-specific decisions made
from limited information under a problem-specific environment
(`TH-C01`–`TH-C03`). The model uses explicit authority, information adequacy,
resource bounds and simple participation postures rather than global optimization.
It does not claim that historical banks used the posture labels or a common
utility function.

### Evidence-to-mechanism translation

| Evidence or uncertainty | Translation | Withdrawal consequence |
|---|---|---|
| some institutions participated and others held back | separate choice units and non-universal response | remove endogenous choice only if a binding collective rule is recovered |
| contributors retain resource identity | own authority/resource envelope and institution-linked commitments | reject any common pooled wallet |
| member certificate applications | optional member capability and application decision | remove or narrow if facility demand is outside the final event question |
| incomplete named-bank records | exposed postures and scenario assignments | withdraw named historical policy claims |
| conflicting amounts/attribution | cases and sensitivity, not fitted totals | withdraw exact reconstruction claims |
| known outcomes | future-information exclusion | any fitted participation/output invalidates the model |

## 4. Event role and relationships

### Role and capability boundary

A unit may act only through capabilities declared before a decision:

| Capability | Choice owned by unit | External authority/result |
|---|---|---|
| direct support contributor | request information, condition, commit or decline own cash/credit | transfer/admission/effect |
| collateralized intermediary | accept for review, condition or decline a route involving controlled services | collateral truth/value, government deposit and transfer |
| NYCH certificate applicant | apply or decline using own eligible collateral | eligibility enforcement, valuation, issuance and clearing effect |
| correspondent relationship participant | act within own delivered relationship and mandate | counterparty behavior and relationship effect |

Capability does not imply historical participation, obligation or available
capacity.

### Authority and resource control

Each unit controls only the decision rights and resources assigned to its
institution. It cannot pledge another institution's asset, spend an NYCH
association resource, issue a certificate, commit a target pool, or create a
government deposit. A coordinator, committee or NYCH rule can create a
decision situation but not the bank's commitment.

### Relationships

| Relationship | Unit-side meaning | Other owner |
|---|---|---|
| unit ↔ Morgan | receive a proposal/solicitation and send an independent response | Morgan owns proposal and assembly |
| unit ↔ trust-company committee | receive a bounded request, conditions or information; return own response | committee owns case/advice/coordination |
| unit ↔ applicant institution | review delivered information and make a bounded offer/decline | applicant owns request/disclosure; scenario owns truth and delivery |
| unit ↔ NYCH | receive facility/rule/eligibility information and submit an application | NYCH owns governance/committee action; scenario owns rule execution |
| unit ↔ other contributors | no direct shared state by default | delivery of public or authorized aggregate information is scenario-owned |

## 5. Decision situations, information, and state

### Activation

A unit acts only after a solicitation/request, facility opportunity, material
authority/resource update or lifecycle result is delivered. Inclusion in the
population alone does not activate a decision.

### Observation interface

| Observation | Meaning and domain | Freshness/uncertainty | Consumer |
|---|---|---|---|
| `institution_profile` | identity, membership, capability roles and relationships | fixed/versioned by scenario | all choices |
| `decision_authority` | competent forum and permitted exposure/route | explicit; missing means no firm commitment | hard gate |
| `own_resource_envelope` | qualitative or bounded available capacity under existing commitments | delivered projection; not exact global truth | contribution and revision |
| `solicitation_or_request` | origin, applicant, route, purpose, terms/amount, authority, expiry and provenance | delivered and versioned | review |
| `applicant_information` | scoped delivered package with as-of time and limitations | may be incomplete/conflicting | information gate |
| `facility_state` | availability, membership/eligibility and delivered rules | only after rule/effect is active and delivered | certificate decision |
| `own_collateral_projection` | controlled collateral class and encumbrance/eligibility projection | no self-valuation as authoritative truth | certificate application |
| `commitment_or_application_state` | own lifecycle and last delivered disposition/result | authoritative and request-specific | duplication/adaptation |
| `relationship_or_exposure_observation` | own modeled connection to applicant/coordinator | dated and explicitly included | optional sensitivity |

### Forbidden information

The unit cannot observe other institutions' exact resources, private replies,
postures or collateral; hidden applicant truth; future facility demand;
complete pool results before delivery; later survival; evaluator evidence; or
the coordinator's private knowledge.

### Persistent state

| State | Initialization/update | Duration |
|---|---|---|
| participation posture | disclosed scenario configuration | fixed during the run in v0.1 |
| review state | opened by own choice and environment disposition | request lifetime |
| information inventory | updated only by delivered records | request lifetime |
| offer/commitment state | created by own intent, advanced by authoritative lifecycle | through terminal/superseded state |
| certificate application | created by own intent, advanced by NYCH/environment result | through terminal state |
| own resource/collateral projection version | scenario supplied, later updated only from delivered result | until superseded |

No hidden backend memory may affect later action.

## 6. Behavioral model

### Participation postures

Postures are explicit structural sensitivities, not empirical bank categories:

| Posture | Behavior after hard gates |
|---|---|
| `obligation_only` | honors a demonstrated binding obligation within the available authority/resource envelope and declines nonbinding collective-support requests |
| `relationship_conditioned` | makes at most a conditional offer when a qualifying modeled relationship/exposure is delivered; otherwise declines a nonbinding request |
| `collective_support_permissive` | makes at least a conditional offer when authority, information, route and nonzero capacity are adequate; final terms are additionally required for a firm commitment |

A run declares posture assignment, any modeled obligation/relationship
predicate and a separate resource posture (`unavailable`, `constrained`, or
`bounded_available`). `relationship_conditioned` is an exposed sensitivity,
not a recovered named-bank policy. No historical frequency or name-based
mapping is claimed. `obligation_only` is the conservative non-invention
baseline; the other postures are structural sensitivities and do not become
historically validated when they reproduce a known participant list.

Certificate demand uses a separate exposed posture:

| Certificate-use posture | Decision boundary after hard gates |
|---|---|
| `no_certificate_use` | declines the facility; retained as an ablation |
| `material_need_conditioned` | applies only when delivered own operational need is `material` and eligible controlled collateral is nonzero |
| `early_access_permissive` | applies at `emerging` or `material` need when eligible controlled collateral is nonzero |

Own operational need is a qualitative scenario projection (`none`,
`emerging`, `material`), not a fitted numerical threshold.

### Decision procedure and determinacy

```text
validate institution/capability and trigger
→ identify request/facility and duplicate lifecycle
→ verify decision authority and route compatibility
→ check declared information/term sufficiency
→ inspect own delivered resource/collateral envelope
→ apply disclosed participation/certificate-use posture and amount method
→ emit information request, condition, commitment, decline or application
→ update only from delivered disposition/result
```

Hard gates are deterministic. After they pass, more than one response may be
allowed only where the declared posture, resource band or unfinished terms
preserve a bounded alternative. A valid decision situation must receive a
response class; `abstain` cannot mask an unspecified policy.

### Invariants

1. Choice units retain separate identity, authority and resources.
2. Solicitation is not commitment.
3. Commitment is not transfer or realized aid.
4. Facility availability does not force application.
5. A member application does not issue a certificate.
6. Postures and amount methods are declared before behavior and never inferred
   from names or outcomes.
7. Missing authority, route or information has an explicit consequence.
8. Another unit's private state is forbidden.
9. Partial, declined, pending and failed states remain visible.
10. Call-money and NYSE actions are outside this vocabulary.

### Mechanisms

#### `M-CBC-01` — independent authority and resource gate

Each unit can respond only within its own demonstrated mandate and resource
envelope, preserving distributed agency under a shared proposal.

#### `M-CBC-02` — information-conditioned contribution

Delivered applicant and route information can produce a request, condition,
commitment or decline. Missing information remains explicit rather than being
replaced by a hidden credit score.

#### `M-CBC-03` — exposed contribution posture

A declared posture selects among permitted choices after hard gates. A binding
obligation is honored within the available envelope or yields a typed
inability/partial response. `obligation_only` declines a nonbinding request;
`relationship_conditioned` requires a delivered qualifying relationship;
`collective_support_permissive` yields at least a conditional offer when
capacity is nonzero. This makes heterogeneity testable without attributing a
private historical motive.

#### `M-CBC-04` — optional facility demand

An eligible member decides whether to apply; NYCH separately reviews and
issues. This preserves the difference between facility supply, bank demand and
realized use.

#### `M-CBC-05` — lifecycle-aware revision

Offers, commitments, applications and transfers retain identity and version.
New information or partial results can revise a response without erasing its
prior state.

### Population Commitments

#### `PC-CBC-01` — classify a delivered request or solicitation

A new nonduplicate matter must produce review opening, information/authority
correction request, referral, decline, conditional offer or firm commitment.
Awaiting is valid only for an identified pending process.

#### `PC-CBC-02` — enforce authority, route and information gates

A firm commitment requires demonstrated authority, compatible route, declared
information classes and own resource capacity. Missing elements yield a
request, condition, referral or typed decline; urgency cannot create them.

#### `PC-CBC-03` — choose an independent contribution response

After hard gates, the disclosed posture selects commit, condition or decline
under the rules above. A binding obligation, qualifying relationship and
collective-support posture are distinct predicates. Any amount/band is
produced by a named pre-run method within the current authority/resource
envelope. Desired aggregate totals and hidden thresholds are forbidden.

#### `PC-CBC-04` — preserve commitment lifecycle

Conditional offer, commitment, scheduling and execution remain separate. A
pending equivalent blocks duplication. Revision/cancellation requires a valid
route and creates a linked version. Failure, expiry and partial execution
remain observable.

#### `PC-CBC-05` — decide whether to seek a member certificate

Only an eligible, authorized member with a delivered facility and controlled
collateral projection can apply. Application is optional and governed by a
separately disclosed certificate-use posture and own operational need. Review,
valuation, issuance and effect are external.

#### `PC-CBC-06` — adapt only to delivered results

Later capacity, collateral and choice state update only from delivered
dispositions/results. An announcement, accepted case or target pool does not
equal realized funding.

## 7. Intent and result boundary

| Unit intent/message | Minimum semantic content | Result owned elsewhere |
|---|---|---|
| `request_proposal_information` | matter, missing class/term, source/target, authority and expiry | disclosure and delivery |
| `refer_or_decline_proposal` | matter, typed authority/route/information/resource reason | recipient delivery and downstream response |
| `make_conditional_contribution_offer` | resource owner, route, amount/band method, terms, expiry and authority | acceptance, scheduling, transfer and effect |
| `commit_owned_resource` | commitment identity, owned resource, bounded amount/terms, authority and expiry | validation, encumbrance, transfer and realized aid |
| `revise_or_cancel_commitment` | prior identity, changed terms/reason and authority | admissibility and new lifecycle state |
| `apply_for_member_certificate` | member, facility, controlled collateral package, requested range and authority | collateral review, valuation, issue and clearing effect |
| `submit_controlled_collateral` | asset owner, package identity and control evidence | acceptance, custody, valuation and encumbrance |
| `await_commitment_or_application_result` | outstanding lifecycle reference | delivered disposition/result |

No unit may output “pool funded,” “certificate issued,” “collateral accepted,”
“market stabilized” or “applicant saved.”

## 8. Operationalization and uncertainty

### Scenario-declared composition

A configuration identifies weight-one institution units, capability roles, memberships,
relationships, qualitative authority/resource envelopes, participation
postures and certificate-use postures.
Weighted unit compression is not permitted in the event-bound reconstruction.
A historical reconstruction may use a
named institution to anchor a sourced relationship or outcome, but the policy
remains exposed and uncalibrated.

### Amount methods

Permitted methods are declared before behavior, for example a scenario-given
authorized band, a fixed sensitivity amount within capacity, or a qualitative
small/medium/large band resolved later by the environment. No method may fit a
known pool total, use an undisclosed balance-sheet threshold or allocate a
coordinator's target automatically.

### Structural uncertainty

- contributor set and exact amounts;
- deciding forum and decision-time information for each institution;
- distinction between bank cash, credit, trust-company bonds, Treasury
  deposits and certificate capacity;
- contributor priorities and reasons for holding back; and
- when a named institution deserves its own policy rather than a population
  unit.

These remain exposed variants, not probability estimates.

## 9. Worked cases and falsification

### Case A — heterogeneous response to one proposal (illustrative)

Two units receive identical terms. One has authority and available capacity;
one has a constrained own projection. They may respond differently without a
name-based rule. The coordinator receives separate replies.

### Case B — target pool and incomplete replies (reconstructed from outcome-known evidence)

A proposal names a target total. Some units commit, others decline or remain
pending. Only delivered commitments enter the current plan; target and realized
funds remain separate.

### Case C — collateralized route (reconstructed)

A bank considers a route involving another institution's collateral. It may
request information, condition or decline within its mandate. Collateral
acceptance, public-deposit availability and transfer are external outcomes.

### Case D — optional certificate demand (later contextual case)

Two eligible members receive the same facility terms. One applies and the
other declines under disclosed postures. The NYCH process separately reviews
the application; eligibility alone predicts neither use nor issuance.

### Case E — partial execution (illustrative)

A firm commitment is only partly executed. The unit's delivered state and
available-capacity projection change by the realized portion. Aggregation does
not count the remainder as aid.

### Falsification matrix

| Perturbation or observation | Expected implication | Failure meaning |
|---|---|---|
| swap names while retaining posture/state | behavior remains unchanged | name-based historical scripting if it changes |
| hold proposal fixed, constrain one unit's capacity | that unit may condition/decline; others unaffected | shared wallet or missing resource ownership if all change |
| coordinator raises target total | no unit obligation changes without a new delivered request/terms | target is being treated as commitment |
| remove facility eligibility | certificate application becomes unavailable, direct-support choices remain separately governed | capability conflation if all behavior disappears |
| partial execution replaces full execution | only realized amount affects state and aggregate | lifecycle/result collapse if unchanged |
| hide another unit's reply | focal unit behavior does not use it unless an authorized aggregate is delivered | illegal information sharing if it changes |

## 10. Limitations and references

### Limitations and withdrawal conditions

The model does not recover named-bank private policies, exact resources,
decision forums, information sets, posture weights, amount rules or complete
pool attribution. It cannot validate a historical funding total or explain the
call-money market.

Promote a named bank only when direct evidence and the research question
require a distinct policy. Reduce behavior to scenario input when contribution
choice is no longer part of the question. Revise the capability set if a
resource route is shown to have a different owner or institutional mechanism.

### References

- *Commercial and Financial Chronicle*, 26 October 1907 (`BASE-S03`).
- O. M. W. Sprague, *History of Crises Under the National Banking System*,
  1910, printed pp. 253–254 and Appendix Note J (`P4-S01`).
- James G. Cannon, *Clearing-House Methods and Practices*, 1910, printed
  pp. 159–180 (`P4-S02`).
- U.S. House Committee on Investigation of United States Steel Corporation,
  hearings, 1911, Oakleigh Thorne testimony (`R2-S01`).
- *Congressional Record*, 26 February 1908, contemporary press extracts
  (`R2-S02`).
- Jon R. Moen and Mary Tone Rodgers, “How J. P. Morgan Picked the Winners and
  Losers in the Panic of 1907,” 2022 (`R2-S03`).
- Herbert A. Simon, “Rational Choice and the Structure of the Environment,”
  1956 (`P4-S05`).
