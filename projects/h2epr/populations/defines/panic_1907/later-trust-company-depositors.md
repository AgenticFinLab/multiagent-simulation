# Later Trust-Company Depositor Population Model

## 1. Model overview

| Item | Definition |
|---|---|
| Event | Panic of 1907, acute New York phase |
| Focal interval | approximately 22–26 October 1907 |
| Representation | event-bound, institution-indexed populations of weighted depositor choice units |
| Focal choices | request withdrawal, retain for the current interval, await a pending result and adapt to a delivered result |
| Evidence use and explanatory scope | Contemporary and retrospective sources informed an event-bound reconstruction; individual, host-cohort, and cross-host responses are not calibrated |

The model represents heterogeneous holders of deposit claims against Trust
Company of America, Lincoln Trust Company and other later New York trust
companies included by a declared event configuration. It studies how private
liquidity needs, delivered host-specific information, public contagion signals,
observed access and own request results can produce different withdrawal or
retention choices after the Knickerbocker suspension.

The host institution is part of every choice unit's identity. Depositors at
different trusts do not share one observation, memory, claim or action. This
preserves contagion through delivered information while preventing one
institution's private condition or result from becoming global depositor
knowledge.

The population produces requested demand. It does not operate paying windows,
choose a trust company's communication, allocate cash, issue certified checks,
move funds to another bank or suspend an institution.

## 2. Historical population and representation

### Historical population

Contemporary and retrospective sources report that withdrawals spread from
Knickerbocker to TCA, Lincoln and other trust companies, with episodes of
different severity (`LDP-C01`). TCA evidence includes large daily withdrawals,
a visible line and expanded paying windows (`LDP-C02`). Lincoln evidence is
thinner and supports a distinct institution and public communication, not a
TCA-like operating policy (`LDP-C03`).

The adopted record does not provide an individual depositor roster, account
balances, private cash needs, information receipt, network position, queue
order or choice times for these later institutions (`LDP-C06`). The model
therefore does not reconstruct named depositors or demographic classes.

### Modeled choice unit

A choice unit represents one account or a weighted set of accounts that a
scenario declares exchangeable for a specified host and behavioral
configuration. It owns:

- one host trust-company identity and claim reference;
- its own remaining claim and private withdrawal-need state;
- only signals and access observations delivered to it;
- its own request and result history; and
- one response profile fixed before behavior begins.

A weight is a transparent compression of modeled conditions, not evidence
that historical depositors coordinated or acted through a common voice.

### Why one institution-indexed model

A separate full Definition for every host would imply institution-specific
depositor policies that the evidence does not recover. One cross-host
population without host identity would create the opposite error: it would
allow a TCA statement, Lincoln result or other trust's access condition to
affect every unit automatically.

The institution-indexed model reuses one bounded choice method while requiring
host-specific claims, signals, access and results. A host may use a different
declared population mix only as a disclosed sensitivity, never because its
known historical outcome was worse or better.

### Included and excluded heterogeneity

Units may vary by host, private need, delivered information, observed access,
own request state, remaining claim, response profile and qualitative conflict
rule. The current model does not infer demographic, occupational, geographic,
wealth, relationship or account-contract classes.

A new historical cohort requires direct microdata, a meaningful event-time
classification and a behavioral prediction not expressible through current
variables. A host institution becomes irrelevant only if the research
question ceases to study institution-specific contagion.

## 3. Evidence and theoretical foundation

### Event evidence

The *Commercial and Financial Chronicle* distinguishes withdrawals at TCA,
Lincoln and other institutions and reports TCA's continued payments.
Thorne's testimony supplies a retrospective TCA account of withdrawals, a
visible line and the expansion of paying windows. Sprague describes runs of
varying severity across trusts and certified-check payment through clearing-
house banks. A later Cleveland Fed synthesis records broad trust deposit
contraction and transactions in which trust depositors moved toward national
banks (`LDP-C01`–`LDP-C05`).

These sources establish a contagion and service context. They do not identify
an individual decision rule, a response coefficient or a shared belief. The
movement-to-banks result does not authorize a depositor transfer action in
this version.

### Behavioral basis

Simon's bounded-choice framework supplies a general lens for choice under
limited information and for fitting a decision representation to its
environment. Moen and Tallman's institution-level study motivates separating
liquidity, clearing-house access, monitoring and depositor signaling. Neither
source establishes that later-trust depositors followed a particular profile
or threshold.

### Evidence-to-model translation

| Evidence or assumption | Model translation | Consequence if withdrawn |
|---|---|---|
| distinct host withdrawal episodes (`LDP-C01`–`LDP-C03`) | host identity remains in every unit and observation | retain the generic method but remove unsupported host-specific case claims |
| TCA line and service response (`LDP-C02`) | depositor access observation and institution service action remain separate | remove the seven-window case, not the choice/service distinction |
| certified-check payment (`LDP-C04`) | payment form is a delivered result attribute, not equivalent cash or confidence | remove that result branch if contradicted |
| aggregate movement to banks (`LDP-C05`) | later context and falsification boundary only | no acute transfer policy is lost |
| no microdata (`LDP-C06`, `LDP-C09`) | profiles and composition are explicit sensitivities | withdraw any calibrated share or hidden numerical response rule |
| private cash need | explicit modeling assumption | ablate it to measure how much demand is signal-driven |

### Exposure

The authors know the runs, public statements, service responses and later
outcomes. They are used for construction, worked cases and falsification
design. None supplies independent held-out validation for this version.

## 4. Institutional role and relationships

Depositors hold claims against one host trust company and may request payment
through its service process. They do not control host cash, support, operating
capacity, communications or suspension.

| Relationship | Choice-unit meaning | Other owner |
|---|---|---|
| depositor ↔ host trust | claim, request, delivered account information and result | host owns communication choices; scenario owns account truth, service, payment and resource effects |
| depositor ↔ public information | dated host-specific or sector information may become an observation after delivery | publication and delivery are scenario events |
| depositor ↔ local activity | a coarse local/access projection may be observed through a declared channel | composition, queue and aggregate activity are scenario-owned |
| depositor ↔ other trust | no private relation by default | only a delivered public or explicit account relation can transmit information |
| depositor ↔ bank receiving later funds | outside v0.1 decision interface | any later transfer route and result require a separate model |

The populations possess no collective mandate, committee, shared resource or
authority. Claim ownership, request lifecycle and access constrain each unit.

## 5. Decision situations, information and state

### Decision situations

1. ordinary operation with or without an immediate private need;
2. receipt of a host-specific statement or adverse report;
3. receipt of a public contagion signal concerning another trust or the trust
   sector;
4. observation of own/local access deterioration;
5. an equivalent withdrawal request already pending; and
6. receipt of a paid, certified-check, partial, delayed, failed, expired,
   cancelled or unavailable result.

### Observation boundary

| Observation | Domain and granularity | Freshness and missing behavior | Behavioral use |
|---|---|---|---|
| `host_institution` | stable trust-company identity | fixed by scenario; missing invalidates the unit | scopes every claim, signal, request and result |
| `remaining_claim` | non-negative amount or normalized share | last delivered account state; unknown prevents amount selection | request sizing and closure |
| `private_withdrawal_need` | `none`, `deferrable`, `immediate`, `unknown` | current sensitivity state; unknown is not immediate | ordinary-need response |
| `host_signal` | dated adverse, reassuring, mixed, neutral or unknown content with provenance | delivery required; conflict retained | host-signal profile |
| `public_contagion_signal` | dated host/sector scope and adverse, reassuring, mixed or neutral content | delivery required; never private result | contagion-responsive profile |
| `service_access_observation` | `normal`, `delayed`, `restricted`, `unavailable`, `unknown`, with host scope | own result or authorized local observation only | access response and expected feasibility |
| `peer_activity_observation` | `none_observed`, `limited`, `substantial`, `unknown` | coarse, local and host-scoped | optional access/contagion response |
| `own_request_status` | `none`, `created`, `delivered`, `pending`, `partial`, `paid`, `failed`, `expired`, `cancelled`, `unavailable` | authoritative last delivered state | duplicate suppression and reopening |
| `own_request_result` | paid form/amount or fraction, remaining claim and typed delay/failure | only after delivery | claim and later-choice update |

The unit cannot observe authoritative host cash, asset value, support
deliberations, exact global queue, other accounts, other hosts' private
results, undelivered communications, future suspension or later historical
interpretation.

### Persistent private state

| State | Initialization | Legitimate update | Duration |
|---|---|---|---|
| host and claim identity | scenario-supplied | host cannot change; claim changes only by delivered account result | unit lifetime |
| withdrawal need | declared configuration | explicit private-need event | until changed |
| request state | `none` | submitted choice and delivered lifecycle/result | through terminal/reopened state |
| dated information inventory | empty or declared prehistory | delivered signal/access observation | retains provenance and time |
| response profile and conflict rule | pre-run assignment | fixed in v0.1 | entire run |

No hidden backend memory may affect later choices.

## 6. Behavioral model

### Response profiles

| Profile | Behavioral boundary |
|---|---|
| `need_only` | immediate private need triggers a request; signals alone do not |
| `host_signal_responsive` | a materially adverse delivered host signal triggers a request after hard gates; mixed signals use the declared conflict rule |
| `contagion_and_access_responsive` | after hard claim/lifecycle gates, a materially adverse delivered host/public signal, newly substantial host-local peer activity or newly worsened own access observation requires a positive request; mixed signals use the declared conflict rule |

Mixed information uses one predeclared qualitative rule:
`adverse_dominant`, `reassurance_dominant` or
`need_only_under_conflict`. These labels are sensitivity structures, not
historical social classes, confidence scores or empirical frequencies.

### Population commitments

#### `PC-LDP-01` — ordinary need and host-scoped retention

With a positive known claim and no equivalent pending request, immediate
private need requires a positive withdrawal request. A report that service is
unavailable changes expected disposition but does not suppress the auditable
attempt; the environment may return an unavailable result. With no need and no
profile-activating delivered signal or access change, the unit records
retention for the current interval. A deferrable or unknown need may not be
promoted silently.

The host scopes the request; the same need cannot create a request against a
different trust.

#### `PC-LDP-02` — delivered host and contagion information

A newly delivered host or public contagion signal updates the dated
information inventory and requires a recorded response: request, retain or
await an existing request. Lifecycle constraints take precedence, immediate
need follows, and the declared profile/conflict rule selects among remaining
responses.

After the hard claim and duplicate gates, a materially adverse host signal
requires a positive request for `host_signal_responsive`; a materially adverse
host or public signal requires a positive request for
`contagion_and_access_responsive`. A mixed signal follows the declared
qualitative conflict rule. `need_only` does not convert a signal into a
request.

A report about another institution may affect only a profile that admits a
public contagion signal. It never imports the other institution's account,
access or result state.

#### `PC-LDP-03` — access and payment-form feedback

A new own/local access observation, host-local peer-activity observation or
delivered request result may change a later response only after delivery.
Worsening access cannot reduce withdrawal orientation for the access-
responsive profile while other inputs are fixed. After the hard claim and
duplicate gates, a newly worsened observation from `normal` or `unknown` to
`delayed`, `restricted` or `unavailable`, or a newly `substantial` host-local
peer-activity observation, requires a positive request for
`contagion_and_access_responsive`. Known unavailability informs expectation
but does not let the population erase that attempted request; the environment
may return an unavailable result.

A certified-check result reduces the claim only by the authoritative paid
amount. It does not establish equivalent cash access, redeposit, solvency or
confidence.

#### `PC-LDP-04` — pending request discipline

A created, delivered or pending equivalent host/claim request requires
awaiting its result rather than submitting a duplicate. Revision is permitted
only when amount or scope changes and the request lifecycle admits it.
Cancellation requires a supported route.

#### `PC-LDP-05` — delivered-result adaptation

A delivered result updates request state and remaining claim before the next
choice. Full payment closes the paid portion. Partial or certified-check
payment may reopen a remainder after the lifecycle permits. Failure or expiry
may permit retry after reopening. Unavailable service does not reduce the
claim as though payment occurred.

### Choice precedence and determinacy

```text
valid host, claim and delivered lifecycle
→ no duplicate pending request
→ immediate private need
→ newly delivered host/public/access information, including reported unavailability
→ declared response profile and conflict rule
→ request, retain or await
```

Every activated situation records one response. Awaiting is justified only by
an identified pending request or access/lifecycle blocker and ends when a
relevant result or reopening event is delivered. Generic abstention is not a
population output.

## 7. Withdrawal choice and result boundary

| Output | Required semantic content | Lifecycle | Result the population may not declare |
|---|---|---|---|
| `request_withdrawal` | unit/weight, host, request and claim identities, positive amount/fraction, decision time and basis category | one active business-equivalent request per host/claim scope | admission, payment, cash availability, transfer or suspension |
| `retain_for_interval` | unit/weight, host, interval and basis category | applies only to current decision interval | permanent confidence, future retention or redeposit |
| `await_request_result` | unit/weight, host, request reference and last delivered state | ends on delivery, expiry, cancellation or reopening | delivery, payment or cancellation |

The scenario and authoritative state path own request admission, queueing,
service availability, payment form, partial/full payment, delay, failure,
expiry, cancellation, claim/cash effects, operational restriction and
suspension. Invalid, excessive, duplicate and unavailable attempts remain
visible rather than being silently repaired.

## 8. Operationalization and uncertainty

For unit `u` at host `h`, let `w_u` be its declared weight, `B_u(t)` its
remaining claim and `q_u(t)` the requested fraction with
`0 <= q_u(t) <= 1`. Requested demand at host `h` is:

```text
D_requested,h(t) = sum_{u: host(u)=h} w_u * B_u(t) * q_u(t)
```

The environment determines admission and realized payment by host:

```text
0 <= D_realized,h(t) <= D_admitted,h(t) <= D_requested,h(t)
```

Aggregation across hosts is an analysis view, not a shared claim or resource.
The equations do not estimate the historical withdrawal path.

| Uncertain item | Status | v0.1 treatment |
|---|---|---|
| identities, balances and account contracts | unavailable | synthetic units/weights with no historical label |
| private needs | unobserved | explicit sensitivity states |
| signal receipt and local visibility | unobserved individually | scenario delivery/coverage assumptions |
| response-profile and conflict-rule shares | unidentified | pre-run sensitivity configurations |
| numerical signal or access response | unidentified | qualitative profiles; no hidden threshold |
| certified-check usability | not recovered at unit level | delivered result attribute; downstream use outside v0.1 |
| host-specific intraday queue | insufficiently reconstructed | scenario lifecycle question after roster release |

Unknown is never encoded as zero. A known host outcome cannot determine its
profile mixture.

## 9. Worked cases and falsification

### Case A — TCA signal, line and service (reconstructed from outcome-known evidence)

A TCA unit receives a dated materially adverse host signal and observes local
delay. The applicable responsive profiles request; a need-only unit without
immediate need retains. TCA's
decision to expand paying windows and the actual payment remain external. If
the access observation is removed, only the delivered signal and private need
can affect the choice.

### Case B — Lincoln board statement (reconstructed from outcome-known evidence)

A Lincoln unit receives a board-authorized reassuring statement after issue.
The unit records it as a fallible host signal. A host-responsive profile
follows its declared conflict rule if earlier adverse information remains.
The statement does not reveal authoritative condition or future withdrawal.

### Case C — public contagion without private leakage (illustrative)

A TCA unit receives a materially adverse public report about Knickerbocker. A
contagion-responsive profile requests after the hard claim and lifecycle gates;
the other profiles do not acquire a signal-based request duty. The unit does
not acquire Knickerbocker claim, queue, access or payment information. Removing
the public delivery eliminates the signal effect.

### Case D — pending request under new stress (illustrative)

A unit has an equivalent pending request when a new adverse host signal
arrives. It updates the information inventory and awaits. When a partial result
is delivered and the lifecycle reopens, it may request the remaining eligible
claim.

### Case E — certified-check payment (reconstructed)

A delivered result reports partial payment by certified check. The paid claim
changes; the remainder persists. The population cannot infer cash usability,
successful deposit elsewhere or host stability.

### Falsifiers and forbidden patterns

- removing host identity leaves cross-host information and result use
  unchanged;
- all units receive one exact global trust-company state;
- a TCA or Lincoln private result becomes another host's depositor input;
- an undelivered report or future suspension changes choice;
- pending requests duplicate or failed requests reduce the claim;
- service access or certified-check issue directly realizes cash effects;
- profile composition is assigned from known host withdrawals;
- all profiles respond identically to information/access perturbations while
  heterogeneity remains an explanatory claim; or
- an exogenous demand series is described as endogenous depositor behavior.

## 10. Limitations and references

### Limitations and withdrawal conditions

The model does not recover individuals, balances, private needs, social
networks, account contracts, information receipt, queue discipline, response
coefficients or host-specific population weights. Evidence is richer for TCA
than Lincoln and sparse for unnamed later trusts. The model cannot validate a
historical run because those outcomes shaped construction.

Add a historical cohort only when direct microdata produce a necessary
behavioral distinction. Remove a host-specific case when its source is
withdrawn. Externalize the whole population if endogenous depositor response
is no longer part of the research question.

### References

- *Commercial and Financial Chronicle*. 1907. “New York Banking Affairs.”
  October 26, pp. 999–1001.
- Moen, Jon R., and Ellis W. Tallman. 1995. “Clearinghouse Access and Bank
  Runs: Comparing New York and Chicago During the Panic of 1907.” Federal
  Reserve Bank of Atlanta Working Paper 95-9.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*. National Monetary Commission, Senate Document No. 538.
- U.S. House Committee on Investigation of United States Steel Corporation.
  1911. *Hearings*, testimony of Oakleigh Thorne, printed pp. 1661–1669.
