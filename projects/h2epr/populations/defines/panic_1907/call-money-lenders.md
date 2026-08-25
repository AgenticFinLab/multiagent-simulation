# Call-Money Lender Population Model

## 1. Model overview

| Field | Description |
|---|---|
| Model name | Institution-preserving call-money lender choice units |
| Event and interval | Panic of 1907, acute New York phase, approximately 22–26 October 1907 |
| Choice unit | One lending institution with its own authority, controlled resource envelope, loan exposure, and delivered information |
| Population scope | Banks, trust companies, and other institutions assigned a call-lending capability; borrowers, collective coordinators, the market, and the venue remain separate |
| Primary decision situations | Review, continue, condition, or call an existing loan; review, offer, revise, or decline new or replacement call credit |
| Aggregation boundary | Historical institutions remain weight-one units; any synthetic sensitivity units are explicit and cannot own a named institution's resources, contracts, or commitments |
| State authority | Contracts, collateral, matching, transfer, repayment, liquidation, resource effects, and market outcomes remain scenario-owned; the unit retains only its own decision and observed lifecycle state |
| Evidence use and explanatory scope | Contemporary and retrospective sources informed an event-bound reconstruction; named-lender policies, response probabilities, amount rules, rate tolerances, and haircuts are not calibrated |

The model represents banks, trust companies and other financial institutions
that a scenario assigns a call-lending capability. It preserves their
independent decisions over existing exposures and new call-credit offers while
keeping loan contracts, collateral, matching, transfer, repayment and market
effects outside the population.

One institution may also participate in collective support or another H2EPR
interface. It nevertheless has one identity, authority and resource truth.
This product defines a call-lending capability; it does not create a duplicate
institution or balance sheet.

The population is not a unitary money market, a modern central bank or a
general finance Agent. It does not control Morgan, NYCH, broker-borrowers or
the New York Stock Exchange.

## 2. Population scope and representation

### Historical population

The event record describes outside banks and New York trust companies calling
loans, brokers seeking accommodation from their regular banks, and clearing-
house banks taking on replacement credit (`CML-C03`). It also describes
special money pools assembled on 24 and 25 October (`CML-C04`).

Those accounts demonstrate heterogeneity in lender role and response. They do
not recover each named institution's competent forum, decision-time resource
assessment, contract inventory, relationship value, amount method or private
policy (`CML-C07`).

### Modeled choice unit

An event-bound historical configuration uses one weight-one unit for each
included institution. A declared sensitivity configuration may use synthetic
units, but they may not be given historical names or commitments.

Each unit retains:

- one authoritative institution and capability identity;
- its own decision authority and controlled resource envelope;
- its own existing loan and call/offer lifecycles;
- delivered borrower, relationship, route and collateral information;
- one existing-exposure posture and one new-lending posture; and
- only its own delivered results.

There is no common lender wallet, observation or action.

### Why a population rather than named Agents or one market Agent

A unitary Agent would merge distinct resources and convert market liquidity
into a collective preference. Separate named Definitions would infer policies
from known calls, loans or pool participation. The institution-preserving
population is the least complex representation that retains independent
choice without claiming private historical knowledge.

A named lender is promoted only when direct evidence recovers a distinct
decision interface and population treatment removes a predeclared causal
prediction.

### Capability composition

The same institution may carry the accepted collective-support resource
capability and this call-lending capability. Their proposal, commitment, loan
and result lifecycles remain distinct, but all read one authoritative resource
projection. A later mapping must prevent resource or participant duplication
(`CML-C09`).

## 3. Evidence and theoretical foundation

### Event and institutional evidence

Sprague describes correspondent and trust-company loan calls, broker recourse
to regular banks and replacement lending by clearing-house banks. His account
also distinguishes ordinary call-market response from the two emergency money
pools. The contemporary *Commercial and Financial Chronicle* reports extreme
call rates and the 24 October pool. The Cleveland Fed synthesis places call
loans in the correspondent/trust liquidity structure, and Moen and Rodgers
describe the pool's floor-broker and settlement purpose (`CML-C01`–`CML-C05`).

The Pujo Committee's later official report describes an exchange loan stand,
direct bank–broker negotiation and loans generally payable on demand against
listed collateral (`CML-C06`). It supports the institutional vocabulary, not
uniform focal contracts or policy.

### Behavioral basis

Simon's bounded-choice framework motivates a representation in which
institutional decisions depend on limited information, declared authority and
the structure of available routes. The model uses simple, exposed postures to
preserve structural alternatives. It does not attribute Simon's illustrative
decision rules or a common utility function to historical lenders.

### Evidence-to-model translation

| Evidence or uncertainty | Translation | Consequence if withdrawn |
|---|---|---|
| banks/trusts called loans and banks replaced some credit (`CML-C03`) | separate call, continuation and replacement-offer choices | remove the event case if contradicted; retain independent loan ownership |
| crisis rate/collateral pressure (`CML-C02`, `CML-C05`) | delivered market/collateral observations, never a hidden composite threshold | remove exact rate cases rather than fit policy |
| money pools (`CML-C04`) | pool proposal, contribution, lender offer, match and funding remain separate | remove the route if unsupported; no institution becomes Morgan-controlled |
| demand/collateral structure (`CML-C06`) | contract callability and collateral class are scenario-supplied gates | narrow to focal contract evidence if later recovered |
| missing named policy (`CML-C07`) | exposed postures and qualitative resource states | withdraw historical policy or calibrated name assignment |
| shared institutional identity (`CML-C09`) | capability composition under one resource owner | stop before mapping if composition would duplicate resources |

### Exposure

Loan calls, replacement lending, rate spikes, pool amounts and later market
outcomes are known. They support construction and diagnostic cases, not
independent validation or target fitting.

## 4. Event role and relationships

### Authority and resource control

A lender unit may act only over a controlled existing exposure or authorized
new-lending envelope. It cannot call another institution's loan, spend a pool
target, promise another contributor's funds, value a borrower's collateral or
create a market rate.

| Capability | Unit-owned choice | External authority/result |
|---|---|---|
| existing call loan | request information, continue, condition or issue a valid call/reduction notice | contract validity, delivery, repayment, default and effect |
| direct/regular-bank replacement route | review, condition, offer or decline own credit | borrower acceptance, collateral validation, booking and transfer |
| exchange or pool route | offer under delivered terms or decline | venue matching, allocation, booking and rate effect |
| collateralized lending | request or review a package and state conditions | ownership/control truth, valuation, custody and enforcement |

### Relationships

| Relationship | Lender-side meaning | Other owner |
|---|---|---|
| lender ↔ broker-borrower | delivered loan/request, information, terms and own lifecycle | borrower owns request/acceptance; environment owns obligations/results |
| lender ↔ regular-account customer | scenario-declared relationship may enable a route or sensitivity | relationship truth and service effects are scenario-owned |
| lender ↔ Morgan/pool coordinator | receive a proposal or authorized route and return an independent offer/decline | Morgan owns proposal/assembly; contributors own commitments |
| lender ↔ NYSE | use a delivered venue route/market observation | NYSE mechanics, matching, rates and settlement are scenario-owned |
| lender ↔ other lenders | no private shared state by default | only delivered public/authorized aggregate information is visible |

## 5. Decision situations, information, and state

### Decision situations

1. scheduled or event-triggered review of an existing call exposure;
2. a delivered own-liquidity/resource change;
3. a borrower request for continuation, renewal or replacement funding;
4. a delivered direct, exchange or pool lending route;
5. incomplete, stale or conflicting borrower/collateral information;
6. a pending call, offer, match, booking or repayment; and
7. a delivered partial, failed, expired, cancelled, repaid or default result.

### Observation boundary

| Observation | Domain | Freshness and uncertainty | Use |
|---|---|---|---|
| `institution_profile` | identity, capabilities, memberships and relationships | fixed/versioned by scenario | authority and composition |
| `decision_authority` | permitted existing-loan and new-lending scope | explicit; missing blocks firm action | hard gate |
| `own_resource_envelope` | `unavailable`, `constrained`, `bounded_available`, with dated limits | delivered projection, not exact global truth | call/offer capacity |
| `own_liquidity_need` | `stable`, `constrained`, `material_recovery_need`, `unknown` | dated qualitative projection | existing-exposure response |
| `existing_call_loan` | lender, borrower, identity, callable/term state, amount/band, deadline, terms and lifecycle | authoritative delivered own record | continuation/call review |
| `contractual_status` | `current`, `review_due`, `call_right_available`, `call_required`, `unknown`, with contract/provenance reference | delivered per-loan interpretation; unknown requires clarification | distinguishes mandatory, discretionary and unavailable call routes |
| `borrower_request` | identity, route, requested range, purpose, authority, expiry and provenance | delivered/versioned | new/replacement review |
| `borrower_information` | scoped dated information package | may be incomplete/conflicting | information gate |
| `collateral_projection` | package identity, class, control evidence, encumbrance and nonauthoritative value band | no lender self-valuation as world truth | condition/offer |
| `term_assessment_basis` | delivered current/requested terms, relevant contract clauses and the current own-resource envelope reference | dated/versioned; missing or incomparable inputs block a firm assessment | input to the unit's declared qualitative term assessment |
| `market_or_pool_route` | direct/regular-bank/loan-stand/pool route and delivered terms | announcement alone is not an offer/match | route gate |
| `market_observation` | dated rate band, route availability and coarse condition | fallible, delivered and nonpredictive | context for a separately declared term assessment; never an independent trigger |
| `own_loan_lifecycle` | call/offer/match/booking/repayment state and last result | authoritative and loan-specific | duplicate/adaptation |

Forbidden information includes other lenders' private resources, replies,
postures or exposures; hidden borrower truth; future collateral prices;
future pool total or allocation; future repayment/default; Morgan's private
knowledge; and an exact global market state not delivered to the unit.

### Persistent state

| State | Initialization/update | Duration |
|---|---|---|
| capabilities and two postures | pre-run disclosed configuration | fixed in v0.1 |
| existing-loan review and information inventory | opened by review event; updated by delivered records | loan/review lifetime |
| term-compatibility assessment | `within_current_envelope`, `bounded_change_required`, `outside_current_envelope` or `unknown`; updated only from the delivered assessment basis under the predeclared classifier | review/request lifetime or until the basis changes |
| call/term-change state | created by own intent; advanced by delivered lifecycle/result | terminal or superseded state |
| new offer state | created by own intent; advanced by match/booking/result | terminal or superseded state |
| resource/exposure projection version | scenario supplied; updated by delivered authoritative result | until superseded |

No hidden backend memory may alter later choices.

## 6. Behavioral model

### Structural postures

Existing-exposure posture:

| Posture | Response after hard gates |
|---|---|
| `contractual_continuation_baseline` | issue a call only when `call_required`; at `review_due`, classify the delivered terms against the current envelope, then continue, condition, call under an available right or record a typed blocker; otherwise continue when terms are within the current envelope, condition when a bounded change is required, and request clarification when status/compatibility is unknown |
| `liquidity_recovery` | issue a valid call/reduction when own recovery need is material and `call_right_available` or `call_required`; otherwise follow the explicit term-compatibility response |
| `relationship_accommodation` | for a qualifying delivered relationship, continue when terms are within the envelope, condition when a bounded change is required, and use a permitted call or typed blocker when outside; no relationship is inferred from a name |

New-lending posture:

| Posture | Response after hard gates |
|---|---|
| `no_new_call_credit` | decline a nonbinding new request |
| `relationship_conditioned` | make at least a conditional offer when a qualifying delivered relationship, authority, information, compatible or conditionable terms and nonzero capacity pass; otherwise decline, request information or state the explicit blocking condition |
| `market_support_permissive` | make at least a conditional offer when route, authority, information and nonzero capacity are adequate |

Postures are explicit construction sensitivities, not empirical institution
types. Their assignments cannot be fitted to the known call or pool record.

### Population commitments

#### `PC-CML-01` — classify and review an existing exposure

A new review event, borrower information, own resource change, term state or
loan result requires opening or updating an identified review. The unit must
continue, request missing information/authority, condition, call/reduce or
await a named pending process. Generic abstention is not permitted.

An exact contract/loan identity, authority and delivered `contractual_status`
are hard gates. `unknown` status requires clarification or a named blocker.
`call_required` is distinct from `call_right_available`; market stress alone
cannot create either.

#### `PC-CML-02` — choose continuation, condition or call

After hard gates, the unit uses its delivered own need, exposure state,
relationship, contractual status, term compatibility and existing-exposure
posture. `call_required` requires a valid bounded call notice under every
posture. A material recovery need under `liquidity_recovery` requires a call
when a call right is available. The baseline continues when the contract is
current and terms are within the envelope; it conditions when a bounded change
is required. `relationship_accommodation` follows the same compatibility
distinction while retaining the delivered relationship as the reason to offer
bounded accommodation. `outside_current_envelope` yields a permitted call, a
proposed bounded term change when one exists, or a named authority blocker
according to contract and authority; it cannot be treated as silent
continuation or as a new-request decline.

If information or authority is missing, the unit requests it or records the
specific blocker/reopening event. A call is an intent; repayment and effect
remain external.

#### `PC-CML-03` — classify a new or replacement request

A delivered nonduplicate borrower request or market/pool route must receive
an information/authority correction request, referral, conditional offer,
typed decline or awaiting of an identified pending matter. An announcement,
target pool or high rate cannot create a loan or oblige the unit.

An `unknown` term-compatibility assessment requires information or explicit
conditions. The assessment is a modeled lender judgment, not a scenario-
supplied policy answer. `within_current_envelope` requires every declared hard
term to fit the current own envelope; `bounded_change_required` requires an
explicit permitted condition capable of bringing the request within that
envelope; `outside_current_envelope` means no permitted bounded change does
so. The classifier may not use an undisclosed rate, relationship or market
score.
`outside_current_envelope` cannot produce an unconditional offer.

#### `PC-CML-04` — form an independent new-loan response

Authority, route compatibility, declared information and nonzero own capacity
are required for any offer. `no_new_call_credit` requires a typed decline.
`relationship_conditioned` requires at least a conditional offer when a
qualifying delivered relationship and compatible or conditionable terms pass
those gates; a nonqualifying relationship requires a typed decline.
`market_support_permissive` requires at least a conditional offer when the
same nonrelationship gates pass. Terms or amounts use a predeclared method
within the current resource envelope; known pool totals, hidden reserves,
unverified collateral values and undisclosed rate thresholds are forbidden.

For the two offer-capable postures, a compatible request within the envelope
receives a conditional offer; a bounded change requires those conditions to be
explicit; outside or unknown compatibility requires decline, information or
revised terms. The lender may not choose between these classes by an
undisclosed score.

#### `PC-CML-05` — preserve and adapt to loan lifecycles

Continue, call, offer, match, booking, transfer, repayment, default and effect
remain distinct. A pending business-equivalent call or offer blocks duplicate
creation. Revision/cancellation creates a linked version under authority.
Only delivered booked/realized amounts update exposure or resources.

### Choice precedence

```text
institution, authority and contract
→ own loan identity and duplicate lifecycle
→ delivered contractual status, information, collateral, route and term compatibility
→ own delivered resource need/capacity
→ disclosed existing-exposure or new-lending posture
→ request, continue, condition, call, offer, decline or await
```

Every activated matter receives a response. Awaiting requires a named pending
information, authority, match, booking or repayment state and ends when the
state changes.

## 7. Intent and result boundary

| Intent or decision | Minimum semantic content | Result owned elsewhere |
|---|---|---|
| `request_call_loan_information` | loan/request identity, missing class/term, source/target, authority, as-of and expiry | disclosure and delivery |
| `continue_call_loan_for_interval` | loan, interval, unchanged/condition basis and authority | borrower capacity, future continuation and repayment |
| `propose_call_loan_term_change` | loan, proposed terms/range, effective/review event, authority and expiry | acceptance, contract modification and effect |
| `issue_call_or_reduction_notice` | loan, called amount/range, contract basis, deadline, authority and notice route | delivery, admissibility, repayment, default or liquidation |
| `make_conditional_call_loan_offer` | lender/resource owner, borrower/request, route, amount method, terms, collateral conditions, authority and expiry | matching, acceptance, booking, transfer and effect |
| `decline_call_loan_request` | request, typed authority/information/resource/route reason and any permitted referral | delivery and borrower response |
| `revise_or_cancel_call_loan_offer` | prior offer, changed terms/reason and authority | admissibility and new lifecycle state |
| `await_call_loan_result` | pending information/call/offer/match/booking/repayment identity | delivered disposition/result |

No unit may output “loan repaid,” “collateral accepted,” “funds transferred,”
“pool funded,” “market stabilized,” “borrower liquidated” or a realized rate.

## 8. Operationalization and uncertainty

### Scenario-declared composition

An event configuration identifies weight-one historical institution units,
capabilities, relationships, authority, existing loans, qualitative resource
envelopes and the two posture assignments. A synthetic sensitivity
configuration labels synthetic units explicitly.

### Amount and term methods

Permitted offer/call methods are declared before behavior: a scenario-given
authorized band, a fixed sensitivity amount within capacity or a qualitative
small/medium/large band later adjudicated. No method may fit a known pool
total, use another institution's resources or hide a rate/haircut threshold.

### Structural uncertainty

| Item | Status | Treatment |
|---|---|---|
| lender set and exact loan book | incomplete | scenario-declared with source/synthetic identity |
| deciding forum and authority | generally unavailable | explicit authority observation; missing blocks firm action |
| own liquidity/capacity | unobserved | qualitative delivered projection |
| focal contract, call status and terms | incomplete | explicit delivered per-loan status and term-compatibility assessment; no universal term or hidden classifier |
| relationship importance | unresolved | declared sensitivity predicate |
| existing/new posture assignment | unidentified | pre-run structural sensitivity |
| collateral value and haircut | unknown | environment-owned valuation; lender may condition only |
| amount and rate response | unidentified | bounded predeclared method; no fitted function |

## 9. Worked cases and falsification

### Case A — valid call under recovery need (reconstructed from outcome-known evidence)

A trust-company lender receives a material own recovery need and holds a loan
with `call_right_available` under valid authority. Under
`liquidity_recovery`, it issues a bounded call/reduction notice. The borrower
may seek replacement funds; the
environment determines delivery, repayment and effects. Removing callability
or authority changes the response to information request, condition or typed
inability.

### Case B — regular-bank accommodation (reconstructed from outcome-known evidence)

A bank receives a replacement request from a broker whose regular-account
relationship is delivered. With nonzero capacity and
`relationship_conditioned`, it may make a conditional offer. The relation
does not force lending; removing it yields decline or another supported route.

### Case C — money-pool route (reconstructed from outcome-known evidence)

An authorized market/pool route and request are delivered. A
`market_support_permissive` unit makes at least a conditional offer within its
capacity; `no_new_call_credit` declines. Morgan's target, reported market rate
and eventual allocation do not determine amount or booking.

### Case D — stale collateral information (illustrative)

A borrower request cites collateral whose control/value projection is stale.
The lender requests a fresh package or conditions an offer. It cannot silently
apply an invented haircut or declare collateral acceptable.

### Case E — partial booking and repayment (illustrative)

Only part of an accepted offer is booked and later only part is repaid. The
unit updates exposure/resource state by delivered realized components. Offer,
match and the unpaid remainder remain visible.

### Falsification matrix

| Perturbation or pattern | Expected implication | Failure meaning |
|---|---|---|
| erase lender name, preserve semantics | response unchanged | name-based scripting if changed |
| remove contract call right | call intent unavailable | market stress is overriding contract if unchanged |
| constrain one lender's own capacity | its offer narrows; other units unchanged | shared wallet if all change |
| raise Morgan/pool target | no unit obligation changes without delivered terms | target treated as commitment |
| hide another lender's reply | no effect absent authorized aggregate | illegal information sharing |
| partial replaces full booking | only realized component updates state | lifecycle collapse if unchanged |
| duplicate institution capability | rejected or composed under one resource owner | double-counted identity/resources otherwise |

Forbidden patterns include a self-repaying call, an offer that books itself,
a rate spike that creates authority, an undelivered pool announcement used as
capacity, future prices in observation and a policy selected from the known
lender list.

## 10. Limitations and references

### Limitations and withdrawal conditions

The model does not recover the complete lender set, private loan books,
decision forums, resource states, contract terms, relationship priorities,
posture assignments, amount rules, rate tolerances or haircuts. It cannot
validate a pool total or explain market prices. The 1913 institutional
description may not apply uniformly to every 1907 contract.

Promote a named lender only with direct evidence and an indispensable causal
distinction. Move a behavior to the scenario if a fixed contract uniquely
determines it. Withdraw a route or term class if focal evidence contradicts
the current institutional description.

### References

- *Commercial and Financial Chronicle*. 1907. “New York Banking Affairs.”
  October 26, pp. 999–1001.
- Moen, Jon R., and Mary Tone Rodgers. 2022. “How J. P. Morgan Picked the
  Winners and Losers in the Panic of 1907.” *Essays in Economic & Business
  History* 40: 153–178.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*. National Monetary Commission, Senate Document No. 538.
- U.S. House of Representatives, Committee on Banking and Currency. 1913.
  *Report of the Committee Appointed Pursuant to House Resolutions 429 and
  504 to Investigate the Concentration of Control of Money and Credit*,
  report pp. 33–34.
