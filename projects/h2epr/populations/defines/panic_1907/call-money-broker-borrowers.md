# Call-Money Broker-Borrower Population Model

## 1. Model overview

| Item | Definition |
|---|---|
| Event | Panic of 1907, acute New York phase |
| Focal interval | approximately 22–26 October 1907 |
| Representation | event-bound population of broker-borrower funding choice units |
| Focal choices | clarify a call, authorize controlled repayment, seek renewal/replacement funds, submit controlled collateral, respond to terms, request authorized position reduction or record inability |
| Evidence use and explanatory scope | Contemporary and retrospective sources informed an event-bound reconstruction; named-broker policies, leverage targets, rate tolerances, liquidation thresholds, and funding demand are not calibrated |

The model represents broker-borrowers facing demand-call obligations and
funding disruption in the New York call-money market. It retains a bounded
borrower response after a loan call: verify the obligation, use controlled
repayment resources, seek continuation or replacement funding, offer
controlled collateral, respond to delivered terms and, where separately
authorized, request a bounded position-reduction route.

The model does not represent a broker's customers, infer a portfolio strategy
or turn funding pressure into an automatic securities sale. Loan matching,
collateral valuation, booking, repayment, trade execution, settlement,
default, insolvency and price effects remain environmental results.

The population is distinct from the NYSE venue. A loan stand or money-pool
route can create a decision situation; it cannot decide for the borrower.

## 2. Historical population and representation

### Historical population

Sprague identifies stock brokers as principal call-loan borrowers and reports
that, when outside banks and trust companies called loans, brokers sought
accommodation from the banks carrying their regular accounts (`CMB-C01`). His
account also states that widespread calls could not be met without replacement
loans and could otherwise force insolvency or liquidation pressure (`CMB-C04`).

The Pujo Committee's later report describes an exchange loan stand and direct
bank–broker lending, generally on demand against listed collateral
(`CMB-C02`). Moen and Rodgers describe the 24 October pool as lending to floor
brokers to aid trade settlement (`CMB-C03`).

The record does not recover each broker's customer mandates, proprietary
positions, controlled resources, private funding policy or trade-selection
rule (`CMB-C05`).

### Modeled choice unit

A unit represents the authorized funding interface of a broker firm or
exchange member, or an explicitly synthetic interface included by a declared
scenario. It aggregates only officers and routines covered by the stated
borrowing, repayment, collateral and position mandate. A unit without that
representation statement is invalid. Customers, beneficial owners and their
independent choices remain excluded. The unit owns:

- one borrower and authority/mandate identity;
- only its own call obligations, funding routes and delivered results;
- controlled resource and collateral/position projections;
- settlement obligations explicitly assigned to it;
- one funding-response posture fixed before behavior; and
- separate funding, repayment and position-response lifecycles.

A historical name may identify a sourced obligation or outcome, but it cannot
select the unit's policy. Synthetic weighted compression must be labeled and
cannot own a historical firm's obligation.

### Why a population rather than named Agents or a demand process

A scenario-only funding-demand series would reproduce market pressure but
remove the borrower response documented by Sprague. Separate named Agent
Definitions would invent private mandates and policies from outcome
attribution. The population retains funding choices while exposing policy and
composition as sensitivity assumptions.

### Aggregation and split boundary

The unit aggregates the firm's authorized funding interface. It does not
aggregate customers, beneficial owners, lenders, exchange governance or the
venue. Split a customer or position owner only when direct evidence and a
revised research question require its independent information and choice.

## 3. Evidence and theoretical foundation

### Event and institutional evidence

Sprague supplies the central borrower-response claim and the distinction
between called loans, replacement accommodation and resulting distress. The
Pujo report supplies a later official description of market routes, demand
character and listed collateral. Moen and Rodgers connect the October 24 pool
to floor brokers and settlement (`CMB-C01`–`CMB-C04`).

These records support a bounded funding interface. They do not establish a
universal borrower sequence, customer authority, collateral choice, rate
tolerance or liquidation rule.

### Behavioral basis

Simon's bounded-choice framework motivates a limited-information response in
which authority, obligations, available routes and controlled resources
precede discretionary choice. The model uses exposed posture alternatives
rather than an inferred global objective or optimization function.

### Evidence-to-model translation

| Evidence or uncertainty | Translation | Consequence if withdrawn |
|---|---|---|
| brokers seek regular-bank accommodation after calls (`CMB-C01`) | valid call plus delivered route activates replacement-funding response | remove regular-bank case; retain bounded response to an obligation |
| demand and collateral structure (`CMB-C02`) | scenario supplies contract, deadline, route and collateral/control semantics | narrow if focal records establish different terms |
| pool lends to floor brokers for settlement (`CMB-C03`) | pool/venue route and settlement obligation remain separate observations | remove route/case if unsupported; no booked funding follows from announcement |
| possible insolvency/liquidation pressure (`CMB-C04`) | typed inability and authorized reduction route can follow a funding gap | never inject future failure or automatic sale into policy |
| missing mandates/policies (`CMB-C05`) | exposed postures and explicit authority/control gates | withdraw named policy, customer action and fitted threshold |
| borrower/venue separation (`CMB-C06`–`CMB-C08`) | funding intents remain separate from matching, valuation, trades and results | revisit only under an evidence-backed roster revision |

### Exposure

The authors know the loan calls, replacement-lending response, pool and later
market outcomes. They may guide construction and falsification design but do
not independently validate this behavior model.

## 4. Institutional role and relationships

### Authority and control

A unit may act only within a declared borrowing mandate and over resources,
collateral or positions it is authorized to use. It cannot pledge a customer
asset without mandate, accept a loan for another firm, order an exchange
allocation, value collateral or declare repayment.

| Capability | Unit-owned choice | External authority/result |
|---|---|---|
| call obligation | request clarification, authorize controlled repayment or form a funding response | obligation validity, delivery, transfer, closure/default |
| regular-bank/direct/venue funding route | request renewal/replacement and respond to delivered terms | lender offer, match, booking and funds |
| collateral proposal | submit or revise a package the unit controls | control truth, value, acceptance, custody and encumbrance |
| position-response route | request/authorize reduction only within a demonstrated mandate | order admission, execution, settlement and price effect |

### Relationships

| Relationship | Borrower-side meaning | Other owner |
|---|---|---|
| borrower ↔ existing lender | receive a call/term state, request clarification and deliver repayment/funding response | lender owns call/offer; scenario owns contract and result |
| borrower ↔ regular bank | delivered relationship may enable a replacement request | bank owns offer; relationship truth/effect are scenario-owned |
| borrower ↔ market/pool route | receive an eligible route or offer after delivery | Morgan assembles pool; lenders offer; venue matches/allocates |
| borrower ↔ customer/position owner | no authority by default | customer choice is outside v0.1 unless separately represented |
| borrower ↔ NYSE | use venue route and receive matching/settlement observations | venue mechanics and governance are scenario-owned |

## 5. Decision situations, information and state

### Decision situations

1. receipt of a new call or term-change notice;
2. a valid call creates a projected funding gap;
3. a regular-bank, direct, loan-stand or pool route becomes available;
4. collateral information or control is missing, stale or disputed;
5. a funding offer is delivered with terms or conditions;
6. an equivalent funding/repayment/reduction process is pending; and
7. a partial, failed, expired, cancelled, booked, repaid or settlement result
   is delivered.

### Observation boundary

| Observation | Domain | Freshness and uncertainty | Use |
|---|---|---|---|
| `borrower_profile` | identity, capability, accounts, relationships and mandates | fixed/versioned by scenario | authority and routes |
| `decision_authority` | borrowing, collateral, repayment and position-reduction scope | explicit; missing blocks the relevant firm intent | hard gate |
| `call_obligation` | loan, lender, called amount/range, deadline, terms, contract basis and lifecycle | authoritative delivered own record | call classification and gap |
| `controlled_resource_projection` | `none`, `partial`, `sufficient`, `unknown`, with dated amount/band when permitted | own delivered projection; not global truth | repayment capacity |
| `funding_route` | regular-bank/direct/loan-stand/pool route, eligibility and expiry | delivered; announcement alone may be context-only | replacement request |
| `collateral_package` | controlled assets, encumbrance, class and nonauthoritative value band | control/availability may be stale or disputed | proposal and term response |
| `settlement_obligation` | bounded own obligation, time and priority | explicit and scenario-supplied | funding purpose/precedence |
| `funding_offer` | lender, route, amount/band, rate/terms, collateral conditions, expiry and provenance | delivered/versioned | accept/request revision/decline |
| `own_business_lifecycles` | clarification, funding request, offer, booking, repayment and reduction states | authoritative own delivered state | duplication/adaptation |
| `market_observation` | dated rate band, route availability and coarse price/collateral condition | fallible and delivered; future values forbidden | context and terms, not automatic action |

Forbidden information includes lender private resources or postures, other
brokers' obligations/positions, customer instructions not delivered,
authoritative collateral value, future prices, future pool allocation, later
insolvency and exact global market state.

### Persistent state

| State | Initialization/update | Duration |
|---|---|---|
| capability, mandate and response posture | pre-run disclosed configuration | fixed in v0.1 |
| call case and information inventory | opened by delivered call; updated by delivered records | obligation lifetime |
| funding request/offer state | created by own request or delivered offer; advanced by result | terminal/superseded state |
| controlled collateral submission | created/revised under authority; advanced by result | matter lifetime |
| repayment/reduction request | created under authority; advanced by result | terminal/superseded state |
| remaining funding gap | scenario supplied and updated only by delivered realized components | until obligation closes |

No hidden backend memory may influence later decisions.

## 6. Behavioral model

### Funding-response postures

| Posture | Minimum response after hard gates |
|---|---|
| `renewal_or_replacement_first` | seek continuation/replacement through a delivered permitted route before position reduction, unless controlled repayment resources are sufficient |
| `parallel_funding_and_reduction` | when separately authorized, issue nonduplicate replacement-funding and bounded position-reduction intents under distinct lifecycles |
| `controlled_repayment_first` | authorize repayment from a delivered sufficient controlled resource; seek funding only for a remaining gap |

Postures are exposed structural sensitivities, not recovered broker classes.
They cannot override an obligation, authority, resource/collateral control or a
pending lifecycle. No hidden rate tolerance, leverage target or liquidation
threshold is permitted.

### Population commitments

#### `PC-CMB-01` — classify a delivered call or term change

A new call must be checked against loan identity, lender, amount/range,
deadline, contract basis, delivery and borrower authority. Missing or disputed
content requires a clarification request or a typed blocker with a reopening
event; it cannot become a guessed obligation.

A valid call opens or updates one call case. Receipt does not constitute
repayment, default or liquidation.

#### `PC-CMB-02` — address a valid funding gap

When a valid call leaves a positive delivered funding gap, the unit must
authorize controlled repayment, request renewal/replacement funding, request
an authorized bounded position reduction or record a typed inability. Generic
waiting is not conforming unless a named clarification, offer, booking,
repayment or reduction result is pending.

`record_funding_inability` is conforming only when no legal repayment,
replacement-funding or authorized position-reduction response is presently
available, and it must name the missing resource, route or authority together
with a reopening event. Declining one offer while a positive gap remains must
therefore be paired with another active response, a named pending process or
that typed inability record.

The response posture orders the remaining legal alternatives after authority,
obligation and resource gates. Under the exposed historical reconstruction, a
delivered regular-bank route activates replacement seeking for
`renewal_or_replacement_first`; this is an event-specific, outcome-exposed
mechanism hypothesis, not an independently validated law.

#### `PC-CMB-03` — form and manage a replacement-funding request

A funding request identifies the call case, needed amount/range, route,
purpose, authority, expiry and any proposed collateral. One active business-
equivalent request per route/case blocks duplication. A public pool
announcement does not create an eligible route, offer or booking until the
relevant information is delivered.

#### `PC-CMB-04` — submit collateral and respond to terms

The unit may submit only a controlled, nonduplicated collateral package. For a
delivered offer it must accept the stated terms, request a bounded revision or
decline; acceptance and revision are different intents and lifecycles. It
cannot self-value collateral, infer lender capacity, book the loan or declare
funds. Missing control or stale information yields correction, another route
or typed inability.

#### `PC-CMB-05` — preserve repayment and position-response authority

Repayment may be authorized only from a delivered controlled resource.
Position reduction may be requested only for a controlled or explicitly
mandated position and must identify scope, purpose, authority and limit. A
funding gap does not create customer authority. Trade admission, execution,
settlement and proceeds are external.

#### `PC-CMB-06` — adapt to delivered results

Clarification, request, offer, acceptance, matching, booking, transfer,
repayment, position reduction, settlement, failure and expiry remain distinct.
Only delivered realized components change the remaining gap, resource,
collateral or obligation state. Partial results retain their unresolved
remainder and causal lineage.

### Choice precedence

```text
borrower identity, mandate and authoritative obligation
→ duplicate call/request lifecycle
→ required information and deadline
→ controlled repayment resource and collateral/position authority
→ delivered funding routes and terms
→ disclosed funding-response posture
→ clarify, repay, seek funding, submit/respond to terms, request reduction or record inability
```

Every activated case receives a response class. Awaiting is justified only by
a named pending process and ends on delivery, expiry, cancellation or
reopening.

## 7. Intent and result boundary

| Intent or decision | Minimum semantic content | Result owned elsewhere |
|---|---|---|
| `request_call_or_term_clarification` | call/loan identity, missing/disputed element, lender/recipient, authority and deadline | correction and delivery |
| `request_call_loan_renewal_or_replacement` | call case, amount/range, route, purpose, authority, collateral proposal and expiry | lender response, match, booking and funds |
| `submit_controlled_collateral_proposal` | owner/control basis, package identity, assets/classes, encumbrance projection, request and authority | acceptance, valuation, custody and encumbrance |
| `accept_call_loan_offer` | offer, accepted terms, authority and expiry | contract formation, booking and transfer |
| `request_call_loan_offer_revision` | offer, requested bounded term changes, reason, authority and expiry | lender revision/decline, contract formation and booking |
| `decline_call_loan_offer` | offer and typed authority/term/route/collateral reason | delivery and later route availability |
| `authorize_controlled_repayment` | call/obligation, controlled resource, amount/range, authority and deadline | transfer, receipt and obligation closure |
| `request_authorized_position_reduction` | controlled position, mandate, bounded scope, purpose, limit and expiry | order admission, execution, settlement and proceeds |
| `record_funding_inability` | decision record with call case, missing resource/route/authority, time and reopening condition; creates no action or message | default, insolvency or market effect |
| `await_funding_or_repayment_result` | named pending clarification/request/offer/booking/repayment/reduction reference | delivered disposition/result |

No unit may output “loan renewed,” “funds received,” “collateral accepted,”
“repayment completed,” “position sold,” “settlement completed,” “firm
insolvent” or “market stabilized.”

## 8. Operationalization and uncertainty

### Funding-gap identity

When commensurate amount-and-unit records exist, let `O_u(t)` be borrower unit
`u`'s authoritative called obligation due in the modeled interval and `R_u(t)`
its delivered controlled repayment capacity. The model may then form a
non-negative decision-time gap projection:

```text
G_u(t) = max(0, O_u(t) - R_u(t))
```

If commensurate amounts do not exist, no subtraction is performed. The
scenario supplies a qualitative gap state in `{none, partial, positive,
unknown}` with its source and as-of time. Either representation activates a
response; neither establishes default or required liquidation. Only realized
repayment or funding changes the authoritative gap.

### Scenario-declared composition

A configuration identifies borrower units, authority/mandate, obligations,
relationships, controlled resources/collateral/positions, settlement duties
and response postures. Historical names may anchor sourced obligations but not
policy. Weighted synthetic units must remain explicitly synthetic.

### Structural uncertainty

| Item | Status | Treatment |
|---|---|---|
| broker identity and decision forum | incomplete | declared unit and explicit authority/mandate |
| obligations and deadlines | transaction record incomplete | scenario-supplied with source/synthetic status |
| controlled cash and positions | unavailable | qualitative/bounded projection; arithmetic only for commensurate amounts and no assumption of customer control |
| regular-bank and market routes | supported generally, incomplete per unit | explicit delivered relationship/route |
| collateral value/haircut | unknown | environment-owned; proposal carries uncertainty |
| response posture | unidentified | pre-run structural sensitivity |
| rate tolerance and funding amount rule | unidentified | no hidden threshold; explicit terms and bounded request method |
| liquidation/insolvency path | outcome-dependent | environment result, never policy input |

Unknown is not zero and a high rate is not automatic inability.

## 9. Worked cases and falsification

### Case A — called loan and regular-bank route (reconstructed from outcome-known evidence)

A valid call creates a positive gap and a regular-account bank route is
delivered. Under `renewal_or_replacement_first`, the unit requests replacement
funding. The bank may ask for information, condition, decline or offer; the
environment owns booking and funds. Removing the relationship requires
another route, controlled repayment, authorized reduction or typed inability.

### Case B — sufficient controlled repayment (illustrative)

A valid call is matched by sufficient delivered controlled cash. Under
`controlled_repayment_first`, the unit authorizes repayment. Transfer and
closure remain external. Replacing `sufficient` with `partial` leaves a
positive gap and activates another response.

### Case C — pool announcement without borrower offer (reconstructed from outcome-known evidence)

The public knows that a pool is being assembled, but the unit has no delivered
eligible route or offer. It cannot record funding or accept terms. Once a
route/offer is delivered, the relevant request and term-response commitments
activate.

### Case D — stale or uncontrolled collateral (illustrative)

A lender requests collateral, but the package is stale or owned by a customer
without mandate. The unit corrects information, proposes only controlled
assets, seeks another route or records inability. It may not pledge or value
the customer asset.

### Case E — parallel response under authority (counterfactual)

A unit with explicit position-reduction authority and a positive gap uses
`parallel_funding_and_reduction`. It sends separate nonduplicate funding and
bounded reduction intents. A funding result may cancel or narrow the still-
pending reduction only through a supported lifecycle.

### Case F — partial replacement (illustrative)

Only part of a funding offer is booked and transferred. The realized part
reduces the gap; the remainder remains open. Match or acceptance alone does
not change resources.

### Falsification matrix

| Perturbation or pattern | Expected implication | Failure meaning |
|---|---|---|
| erase broker name, preserve semantics | response unchanged | name-based scripting if changed |
| remove regular-bank route | replacement request moves to another legal route or typed inability | hidden route if unchanged |
| remove repayment authority | repayment intent unavailable | obligation is creating authority if unchanged |
| remove position mandate | reduction intent unavailable | customer/owner boundary violated if unchanged |
| announcement without offer | no booking or funding state | pool result leakage if funded |
| partial instead of full funding | only realized component changes gap | lifecycle collapse if gap closes |
| pending equivalent request | no duplicate request | missing persistent state if duplicated |
| future price or insolvency injected | observation rejected | temporal leakage if behavior uses it |

The model also fails if all postures respond identically to controlled cash
and route changes, if collateral submission self-validates, or if a scenario
funding-demand path is described as borrower choice.

## 10. Limitations and references

### Limitations and withdrawal conditions

The model does not reconstruct named broker firms, customers, beneficial
owners, private mandates, complete obligations, portfolios, collateral
control, funding policies, rate tolerances, leverage or liquidation rules. It
cannot explain securities selection, market prices, settlement architecture or
firm insolvency. Its regular-bank response and money-pool cases are exposed
reconstructions.

Promote a named broker only with direct evidence and an indispensable causal
distinction. Split customers or position owners only under a revised roster
question. Externalize the population if borrower funding response ceases to be
an endogenous research claim.

### References

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
