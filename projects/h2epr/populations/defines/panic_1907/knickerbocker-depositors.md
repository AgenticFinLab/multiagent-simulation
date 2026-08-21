# Knickerbocker Depositor Population Model

## 1. Model overview

| Item | Definition |
|---|---|
| Model identity | `H2EPR-0288-KNICKERBOCKER-DEPOSITOR-POPULATION` |
| Semantic version | `0.1.0` |
| Event | Panic of 1907, acute New York phase |
| Focal interval | approximately 18–22 October 1907 |
| Representation | event-bound population of weighted depositor choice units |
| Focal choices | request withdrawal, retain for the current interval, await a pending result, and respond to a delivered result |
| Evidence status | exploratory construction with fully exposed focal outcomes |
| Calibration status | no individual or cohort calibration; population composition and response profiles are sensitivity assumptions |

The model represents heterogeneous holders of deposit claims against the
Knickerbocker Trust Company. It connects private withdrawal needs, delivered
institution-related information, observed access conditions, and own request
results to depositor withdrawal or retention choices. These choices produce
requested demand. They do not produce cash payment or institutional failure.

The model addresses a central causal boundary of H2EPR-0288: population
response must be capable of amplifying or attenuating institution-specific
signals, but it may not be replaced by one collective depositor personality or
by a demand path fitted to the known run.

It does not explain Knickerbocker management decisions, NBC's credit or
clearing decisions, NYCH support policy, the operating queue, cash allocation,
suspension, or later trust-company runs.

## 2. Historical population and representation

### Historical population

The historical population consists of holders of deposit claims against
Knickerbocker during the focal interval. Adopted sources establish a large
deposit base and an aggregate run in which about $8 million was reportedly
paid before suspension (`KT-C01`, `KT-C02`, `KDP-C01`). They do not provide a
depositor roster, account-level balances, private cash needs, information
receipt, network position, queue order, or individual choice times
(`KDP-C03`).

### Modeled choice unit

A choice unit represents either one account or a weighted set of accounts that
a scenario treats as exchangeable for a declared configuration. It owns one
bounded decision interface:

- the claim and request result it has actually been told about;
- the institution-related information delivered to it;
- an explicit private withdrawal-need state;
- an explicit response-profile assumption; and
- a choice to request withdrawal, retain, or await a result.

A weighted choice is an approximation over similar modeled conditions. It is
not evidence that the represented depositors coordinated, shared information,
or acted through one authorized voice.

### Why the model is a population rather than an Agent

A unitary Agent would give all depositors one observation, memory, and action.
That would erase the simultaneous existence of withdrawal and waiting and
would personify the population. A purely scenario-owned demand process would
preserve aggregate pressure but could not examine how delivered signals and
access feedback affect demand. The population model is the least complex
representation that retains the causal choice required by the event question.

### Included and excluded heterogeneity

The model may vary units by private need, delivered information, observed
access, own request status, remaining claim, and a declared response profile.
It does not infer demographic, occupational, geographic, relational, insured,
or wealth classes from the current record.

A future revision should add a historical segmentation only when adopted
microdata identify the class, its event-time meaning, and a behavioral
difference that cannot be represented by the current variables.

## 3. Evidence and theoretical foundation

### Event evidence

Sprague's retrospective narrative and the contemporary *Commercial and
Financial Chronicle* report the aggregate payment episode and suspension,
while the 22 October *New-York Tribune* shows a public information environment
containing both adverse and reassuring claims (`KDP-C01`, `KDP-C02`). These
records establish the event context and the need to model information and
realized payment separately. They do not establish an individual decision
rule.

Moen and Tallman's institution-level study associates liquidity position and
clearinghouse access with deposit contraction and discusses access as a bundle
of liquidity, monitoring, guarantee, and depositor-signaling channels
(`KDP-C04`, `TH-C04`). The study motivates separate model concepts; it cannot
identify the Knickerbocker population's micro-level response or a causal
coefficient for this event.

### Behavioral lens

Simon provides a general basis for bounded choice under limited information
and for choosing a representation jointly with the structure of the
environment (`TH-C01`–`TH-C03`). R1 applies that lens by limiting units to
delivered observations and declaring simple response profiles. It does not
attribute Simon's illustrative mechanisms to historical depositors.

### Evidence-to-model translation

| Evidence or assumption | Translation | Behavioral consequence | Withdrawal consequence |
|---|---|---|---|
| mixed public reporting (`KDP-C02`) | signals retain content, time, provenance, and contradiction | units may respond differently according to a declared profile | remove signal-driven choices if no signal was delivered |
| aggregate paid run (`KDP-C01`) | demand, admission, and payment are separate | choices emit requests rather than cash effects | removing the figure changes historical context, not the response rule |
| institution-level access and liquidity relation (`KDP-C04`) | access observation and hidden institution state remain separate | own delivered access evidence may change later choice | remove access-sensitivity hypothesis if evidence or tests show it is decorative |
| no microdata (`KDP-C03`, `KDP-C07`) | cohort shares and thresholds remain unidentified | use explicit profile mixtures and sensitivity rather than fitted probabilities | any precise calibrated mix must be withdrawn |
| private cash need | explicit modeling assumption, not a historical claim | permits ordinary withdrawal without labeling it panic | ablate the mechanism to measure how much demand comes from signal response |

### Exposure

The research team knows the run and suspension. They are used for
construction, explanatory cases, and falsification design. No part of this
model has an independent held-out historical outcome.

## 4. Institutional role and relationships

Depositors hold claims against Knickerbocker and may request payment according
to the account and operational conditions represented by the scenario. They do
not control Knickerbocker cash, the clearing relationship, outside support,
opening or suspension, or other depositors' accounts.

| Relationship | Population-side meaning | Other owner |
|---|---|---|
| depositor ↔ Knickerbocker | claim, request, delivered account information, and result feedback | Knickerbocker owns its communication choices; the scenario owns account truth, service, payment, and resource effects |
| depositor ↔ public information | a dated report may become an observation after delivery | source publication and delivery are scenario events |
| depositor ↔ other depositors | only a coarse local or public projection may be observed | population composition, local visibility, and aggregate activity are scenario-owned |
| depositor ↔ NBC/NYCH/private financiers | no direct institutional authority is assumed | any public statement or delivered consequence arrives through an explicit scenario channel |

The model has no collective mandate, committee, or authority. Its constraints
come from individual claim ownership, the request lifecycle, available access,
and the prohibition against treating a request as a realized result.

## 5. Decision situations, information, and state

### Decision situations

1. ordinary operation with or without an immediate private need;
2. receipt of mixed adverse and reassuring institution-related information;
3. observed local activity or access deterioration;
4. an equivalent request already pending; and
5. receipt of a paid, partial, failed, expired, cancelled, or unavailable
   result.

### Observation boundary

| Observation | Domain | Freshness and uncertainty | Used by |
|---|---|---|---|
| `remaining_claim` | non-negative amount or normalized share | last delivered account state; may be coarse | request sizing and closure |
| `private_withdrawal_need` | `none`, `deferrable`, `immediate`, `unknown` | current private state; sensitivity assumption | ordinary need response |
| `institution_signal` | dated adverse, reassuring, mixed, neutral, or unknown content with provenance | content may be disputed; delivery is required | signal-response profile |
| `service_access_observation` | `normal`, `delayed`, `restricted`, `unavailable`, `unknown` | own result or authorized local observation only | access response and feasibility expectation |
| `peer_activity_observation` | `none_observed`, `limited`, `substantial`, `unknown` | coarse and channel-specific; exact global fraction prohibited | optional signal/access sensitivity |
| `own_request_status` | `none`, `created`, `delivered`, `pending`, `partial`, `paid`, `failed`, `expired`, `cancelled` | last delivered lifecycle state persists | duplicate suppression and reopening |
| `own_request_result` | paid amount or fraction, remaining claim, delay/failure category where delivered | result only after delivery | claim and response update |

The population may not observe the authoritative institutional cash position,
asset value, support deliberations, exact global queue, other accounts,
undelivered messages, future suspension, or later historical interpretation.

### Persistent private state

| State | Initialization | Legitimate update | Duration |
|---|---|---|---|
| remaining claim | scenario-supplied account or cohort claim | delivered paid or account result | until exhausted or replaced by a later account result |
| withdrawal need | declared population configuration | explicit private need event, if the scenario models one | until the private event changes it |
| request state | `none` | own submitted choice followed by delivered lifecycle/result | until the next legitimate transition |
| last information set | empty or scenario-declared prehistory | delivered dated signal | historical information remains with its date |
| response profile | declared before behavior begins | no within-run learning in v0.1 | entire run |

No hidden backend memory may affect later choices. Momentary reasoning does not
become a historical belief unless the model declares and records a persistent
state transition.

## 6. Behavioral model

### Response profiles

The response profile is a fully exposed, uncalibrated structural assumption
used to compare plausible responses under the same evidence boundary.

| Profile | Decision role | Response boundary |
|---|---|---|
| `need_only` | isolates ordinary liquidity demand | institution signals alone do not trigger withdrawal; immediate private need does |
| `signal_responsive` | tests protective response to delivered institution information | a materially adverse delivered signal triggers a positive request unless an equivalent request is pending; mixed signals use a declared, pre-run qualitative tie rule |
| `access_responsive` | tests response to own access/result deterioration | worsening delivered access evidence cannot reduce withdrawal orientation while need, claim, and lifecycle remain fixed |

No profile denotes a historical social class, personality, insurance status, or
belief in insolvency. A scenario must disclose profile weights and tie rules.

Mixed adverse and reassuring signals use one predeclared qualitative rule:
`adverse_dominant` requests withdrawal, `reassurance_dominant` retains for the
interval, and `need_only_under_conflict` falls back to private need. No backend
may substitute an undisclosed numerical score, probability, or fitted
threshold.

### Population commitments

#### `PC-KDP-01` — ordinary need and retention

When no equivalent request is pending and service is not known unavailable, an
immediate private need requires a positive withdrawal request. With no need and
no materially adverse delivered signal, the unit retains for the current
interval. A deferrable or unknown need cannot be silently promoted to
immediate.

This is partly an explicit modeling assumption. It prevents all withdrawals
from being interpreted as panic and prevents a model from withdrawing everyone
without a causal input.

#### `PC-KDP-02` — delivered institution information

A newly delivered institution signal must update the dated information set and
produce a recorded choice: withdrawal request, retention, or awaiting an
existing request. Lifecycle constraints take precedence over signal response;
immediate need then takes precedence; the declared response profile selects
among the remaining permitted choices.

Mixed reporting remains mixed. A reassuring item does not erase an adverse
item, and neither becomes authoritative world truth.

#### `PC-KDP-03` — access and peer observation

A new own-result, local-access observation, or authorized peer-activity
projection may change choice only after delivery. A pending equivalent request
blocks duplication. Service known unavailable informs the choice but does not
silently prohibit an attempted request: the environment may leave it
undelivered or return an inadmissible or unavailable result. Unavailability
does not create payment or erase the claim.

For the `access_responsive` profile, worsening delivered access evidence may
hold or increase withdrawal orientation, but may not reduce it unless another
delivered signal, result, or blocker changes. This is a sensitivity hypothesis,
not a measured 1907 law.

#### `PC-KDP-04` — pending request discipline

A created, delivered, or pending equivalent request requires awaiting its
result rather than submitting a duplicate. A materially different request is
permitted only when its amount or scope changes and the scenario's lifecycle
admits revision. Cancellation is unavailable unless a supported route exists.

#### `PC-KDP-05` — delivered-result adaptation

A delivered result updates request state and remaining claim before a later
choice. Full payment closes the paid portion. Partial payment may reopen the
remainder. Failure or expiry may permit retry only after the lifecycle reopens
and access is not known unavailable. A failed request never reduces the claim
as though it had been paid.

### Choice precedence

```text
valid delivered account and lifecycle state
  -> no duplicate pending request
  -> known service or access condition
  -> immediate private need
  -> newly delivered institution and access information
  -> declared response profile and mixed-signal tie rule
  -> request, retain, or await
```

An active situation must produce one recorded response class. Indefinite,
unrecorded abstention is not permitted. Awaiting is justified only by a pending
request or a known access/lifecycle blocker and ends when a relevant result or
reopening event is delivered. A known operational problem changes expectation;
it does not authorize the population model to erase an attempted request.

## 7. Withdrawal choice and result boundary

### Population outputs

| Output | Meaning | Required content | Prohibited interpretation |
|---|---|---|---|
| `request_withdrawal` | asks Knickerbocker's service process to pay part of the remaining claim | choice-unit identity or weight, request identity, positive requested amount or fraction, claim reference, and decision time | cash has been paid, the request is admissible, or the institution has failed |
| `retain_for_interval` | records that no new withdrawal request is made in the current decision interval | choice-unit identity or weight, decision time, and basis category | permanent commitment, confidence in solvency, or redeposit |
| `await_request_result` | records that an existing request or access process remains unresolved | request reference and last delivered lifecycle state | delivery, acceptance, payment, or cancellation |

`retain_for_interval` and `await_request_result` are traceable population
choices; only `request_withdrawal` creates new demand for the environment.

### Environment-owned outcomes

The scenario and authoritative state path own:

- request admission, ordering, and duplicate detection;
- access restrictions and service availability;
- paid, partially paid, delayed, failed, expired, cancelled, or unavailable
  results;
- the reduction of depositor claim and Knickerbocker cash;
- aggregate realized withdrawals; and
- operational restriction or suspension.

Invalid, excessive, duplicate, or unavailable requests remain observable. An
adapter may not silently clamp them into a different legitimate choice.

Redeposit is not a v0.1 output. The adopted local evidence does not establish
an acute-period return-of-funds decision or reopening route for this
population. A later event scope may add it with its own evidence and result
lifecycle.

## 8. Operationalization and uncertainty

### Population aggregation

For choice unit `u`, let:

- `w_u` be its scenario-declared population weight;
- `B_u(t)` be its remaining claim; and
- `q_u(t)` be the requested fraction of that claim, with `0 <= q_u(t) <= 1`.

The population's requested demand is:

```text
D_requested(t) = sum_u w_u * B_u(t) * q_u(t)
```

The environment determines admission and payment:

```text
0 <= D_realized(t) <= D_admitted(t) <= D_requested(t)
```

These relations preserve causal ownership. They are not an estimate of the
historical run and do not require a particular clock or population sampler.

### Uncertainty register

| Item | Status | v0.1 treatment |
|---|---|---|
| individual identities and balances | unavailable in adopted sources | scenario-supplied synthetic units or weights; no historical label |
| private withdrawal needs | unobserved | explicit sensitivity classes |
| public-information receipt | unobserved individually | scenario-delivered observations with coverage assumptions disclosed |
| peer and queue visibility | unobserved individually | absent by default; coarse local projection only when declared |
| response-profile weights | unidentified | pre-run sensitivity configurations, never fitted silently |
| signal-response threshold | unidentified | qualitative profile rule; no numeric threshold |
| intraday request and service sequence | insufficiently reconstructed | scenario lifecycle question for consolidated design |
| reported $8 million paid | exposed aggregate report | worked-case scale and falsification context only |

Numerical population size, account distribution, request fraction, and profile
weights must be labeled synthetic, bounded, or sensitivity-only. Unknown is not
encoded as zero.

## 9. Worked cases and falsification

### Case 1 — ordinary private need

An illustrative unit observes normal access, has no adverse delivered signal,
has an immediate private need, a positive remaining claim, and no pending
request. `PC-KDP-01` requires a positive withdrawal request. The environment
may pay, delay, partially pay, fail, or reject it. With need changed to `none`
and all else fixed, the same unit retains for the interval.

### Case 2 — mixed morning information

In a reconstructed, fully exposed situation, a unit receives both an adverse
leadership/clearing signal and a reassuring public claim. A `need_only` unit
without immediate need retains. A `signal_responsive` unit follows the
declared mixed-signal tie rule and may request or retain. Neither unit sees the
later suspension. The case demonstrates structural sensitivity rather than
historical validation.

### Case 3 — visible stress with a pending request

An illustrative unit has a pending equivalent request and receives a coarse
authorized observation of substantial local activity. `PC-KDP-04` requires
awaiting; it cannot add a duplicate request merely because perceived stress
rose. The observation may influence the next choice only after a result
reopens the lifecycle.

### Case 4 — partial result and restricted access

An illustrative unit receives a partial payment and a positive remaining
claim, followed by restricted access. It updates the claim and request state
first. When the process reopens, an `access_responsive` profile may request an
eligible remainder. If service is unavailable, the unit records awaiting or
failure rather than declaring payment.

### Case 5 — supplied-demand ablation

The population response is removed and replaced by an exogenous demand class
under the same institutional scenario. The run pressure may remain, but claims
about information-to-choice response no longer follow. This distinguishes a
population mechanism from a scenario trajectory.

### Falsifiers and forbidden patterns

- all units receive one global exact observation or make one collective
  action;
- behavior changes when only the historical name or internal identifier
  changes;
- an undelivered public report, exact bank cash, future suspension, or later
  historical interpretation affects choice;
- the model calls all withdrawals panic behavior or ignores immediate private
  need after declaring it material;
- pending requests are duplicated or forgotten;
- partial, paid, failed, expired, and unavailable results produce the same
  later state;
- requested demand directly reduces Knickerbocker cash;
- a response profile or population weight is selected after inspecting a run
  merely to match the known $8 million report;
- removing profile heterogeneity has no predeclared effect while the model
  claims heterogeneity is explanatory; or
- a scenario-owned demand path is described as endogenous depositor behavior.

## 10. Limitations, references, and provenance

### Limits

This model does not identify real individual depositors, empirical social
networks, account contracts, precise queue discipline, or a calibrated
withdrawal function. It does not determine whether contemporaneous reports
were believed, whether observed activity conveyed private information, or how
many withdrawals reflected ordinary liquidity needs. It cannot independently
validate the historical run because the focal outcome shaped construction.

The three response profiles are explicit sensitivity structures. They should
be narrowed, replaced, or empirically weighted if appropriate microdata become
available. If individual attributes or networks create a necessary and
supported event-process distinction, the choice-unit representation should be
revised. If endogenous response proves unnecessary for the selected research
question, the population may be externalized as a scenario demand process,
with the corresponding explanatory claim withdrawn.

### References

- Moen, Jon R., and Ellis W. Tallman. 1995. “Clearinghouse Access and Bank
  Runs: Comparing New York and Chicago During the Panic of 1907.” Federal
  Reserve Bank of Atlanta Working Paper 95-9.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*. National Monetary Commission, Senate Document No. 538.
- *The Commercial and Financial Chronicle*. 1907. “New York Banking Affairs.”
  October 26, pp. 999–1001.
- *New-York Tribune*. 1907. “C. T. Barney Out of Knickerbocker Trust.” October
  22, p. 1.

### Provenance

Version `0.1.0` resolves the roster representation gate as an
event-bound population model. It rejects a unitary cohort Agent and limits a
scenario-owned demand process to an ablation or alternative research boundary.
The model introduces five population commitments, three sensitivity profiles,
three qualitative mixed-signal tie rules, explicit request/result separation,
and a bounded aggregation identity. It keeps known access infeasibility as an
observation rather than allowing the model to suppress an auditable attempted
request. No executable mapping, population generator, or historical
calibration is included.
