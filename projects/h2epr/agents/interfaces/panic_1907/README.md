# Panic of 1907 participant interfaces

This is the publication-facing guide to the interfaces among the seven Agent
Definitions and five Population Models in the accepted H2EPR-0288 roster. It
brings the shared information, authority, lifecycle, and result boundaries
into one reading path without replacing the participant models or the Event
Scenario Definition.

The roster was produced in several batches. Their exact integration preflights
remain pinned by the Roster Definition release and preserve the mapping
questions that existed at the time. Those records are listed separately below;
their carrier classifications are project history, not participant traits.

## Reading map

| Interface | Participants | Main distinction |
|---|---|---|
| Focal clearing and support route | [Knickerbocker Trust](../../defines/panic_1907/knickerbocker-trust.md), [National Bank of Commerce](../../defines/panic_1907/national-bank-of-commerce.md), and [New York Clearing House](../../defines/panic_1907/new-york-clearing-house.md) | A request, each delivery hop, intermediation, recipient review, disposition, notice, and relationship effect remain separate. |
| Private coordination and named trusts | [J. Pierpont Morgan](../../defines/panic_1907/j-pierpont-morgan.md), [Trust Company of America](../../defines/panic_1907/trust-company-of-america.md), and [Lincoln Trust Company](../../defines/panic_1907/lincoln-trust-company.md) | Coordination proposals, examination, company choices, support routes, communication authority, and delivery retain distinct owners. |
| Collective trust support | [Trust-company presidents' committee](../../defines/panic_1907/trust-company-presidents-committee.md) and [member/correspondent-bank resource decisions](../../../populations/defines/panic_1907/member-and-correspondent-bank-resource-decisions.md) | Committee advice and plan assembly cannot create an institution's commitment or transfer its resources. |
| Depositor and market-liquidity processes | [Knickerbocker depositors](../../../populations/defines/panic_1907/knickerbocker-depositors.md), [later trust-company depositors](../../../populations/defines/panic_1907/later-trust-company-depositors.md), [call-money lenders](../../../populations/defines/panic_1907/call-money-lenders.md), and [broker-borrowers](../../../populations/defines/panic_1907/call-money-broker-borrowers.md) | Requests, host service, loan calls, offers, matching, booking, transfer, repayment, and market effects remain participant- and object-specific. |

## Shared causal structure

The focal institutional route is a sequence of bounded acts rather than a
single support decision:

```text
Knickerbocker forms and issues a scoped request
  -> National Bank of Commerce receives that request
  -> the bank chooses whether and how to forward, sponsor, or decline it
  -> the Clearing House receives only the delivered bank message
  -> the competent Clearing House process reviews and returns a disposition
  -> each response reaches an earlier participant only through its own route
```

The wider support process has the same separation. Morgan or a committee may
request information, form a proposal, solicit an institution, and assemble
delivered replies. Each contributor still decides under its own authority and
resource envelope. The environment validates any commitment, transfer,
clearing change, facility decision, or market effect.

Depositor and call-money populations interact through institution- and
contract-scoped objects. A depositor request does not reveal another account or
another trust's service state. A loan call does not create replacement funding;
an offer does not become a booked loan; a position-reduction request does not
become a trade or settled proceeds.

## Information and state boundaries

- Participants observe only dated records, publications, messages, and results
  delivered through an allowed route. Researcher knowledge and later outcomes
  never become participant observations merely because they are documented.
- Knickerbocker, NBC, and the Clearing House retain separate assessments and
  request histories. Delivery to NBC is not delivery to the Clearing House.
- Morgan, the trust-company committee, named trusts, and contributors retain
  separate proposal, advice, authority, commitment, and result state.
- Population units preserve host, institution, account, claim, contract,
  collateral, position, and resource ownership. Aggregation may summarize
  demand or supply but cannot create a collective wallet or shared belief.
- Pending, acknowledged, partial, failed, expired, cancelled, and superseded
  matters remain distinguishable from an intent that was never issued.

## Authority and result ownership

| Surface | Participant contribution | Owner outside participant policy |
|---|---|---|
| Support request | Form, authorize, issue, forward, sponsor, revise, or withdraw an intent within the participant's mandate | Transport, delivery, recipient case creation, review result, execution, and realized effect |
| Examination and advice | Request information or examination; provide scoped information; issue a qualified finding or recommendation | Examiner work, competent-forum procedure, authoritative condition, and recipient action |
| Coordination plan | Form and revise a versioned proposal from information and replies actually received | Independent contributor choice, admissibility, scheduling, transfer, allocation, and effect |
| Clearing relationship | Review credit or clearing posture and issue a scoped notice where authorized | Notice delivery, effective relationship change, settlement, repayment, and loss |
| Company communication | Propose, authorize, narrow, withhold, issue, or correct a statement | Transport, public availability, audience interpretation, and behavioral response |
| Depositor service | Submit, revise, withdraw, or await an account-scoped request | Queueing, capacity, payment form, partial payment, suspension, and remaining claim |
| Call-money response | Call a loan, seek terms, make or revise an offer, or request controlled position action | Matching, booking, transfer, trade, settlement, repayment, default, and market effect |

No coordinator, committee, institution, or population can produce a result by
naming it as an intent. Shared institutional procedures and resource effects
remain in the Scenario and authoritative reducer.

## Lifecycle expectations

The interface preserves a stable object and version across every material
transition. A request may be drafted, authorized, issued, delivered by one or
more hops, reviewed, conditioned, declined, withdrawn, executed, failed, or
closed. Proposals and statements retain predecessor and correction links.
Commitments retain their institution and resource owner. Loan and funding
objects retain borrower, lender, terms, collateral or position scope, booking,
transfer, repayment, and terminal result.

These distinctions prevent three common shortcuts: treating message issue as
delivery, treating a recommendation as a resource commitment, and treating an
accepted intent as its realized effect.

## Informative perturbations

The interface account would be contradicted if these controlled changes did
not alter behavior as stated:

- removing delivery of the Knickerbocker request to NBC must remove NBC's
  request-based forwarding choice;
- delivering the request to NBC but not the sponsored message to the Clearing
  House must create no Clearing House observation or case;
- removing a contributor's authority or controlled resource must prevent its
  commitment without preventing other institutions from deciding;
- replacing a delivered examination result with a pending or failed result
  must keep the relevant support question open;
- replacing successful statement delivery with transport failure must create
  no public observation;
- moving a depositor record to another host must not transfer the first host's
  service state or remaining claim; and
- replacing a booked funding result with a conditional offer must leave the
  borrower's funding gap unresolved.

## Evidence and limits

The interfaces are qualitative and event-bound. They distinguish mechanisms,
information routes, and ownership; they do not recover private deliberation,
participant thresholds, population weights, exact resource quantities, or a
unique historical path. The completed 1907 outcome was known during
construction. Worked situations therefore test semantic consequences and
falsifiers rather than provide held-out validation.

## Release relationship

The following files are exact inputs to the accepted
[Roster Definition release](../../../releases/panic_1907/roster-definition-v0.1/):

- [Knickerbocker depositor integration preflight](../../../populations/interfaces/panic_1907/knickerbocker-depositors.md);
- [National Bank of Commerce integration preflight](national-bank-of-commerce.md);
- [private coordination and named-trust preflight](r2-private-and-named-trusts.md);
- [collective trust-support preflight](r3-collective-trust-support.md); and
- [trust-contagion and call-money preflight](../../../populations/interfaces/panic_1907/r4-trust-contagion-and-call-money.md).

They preserve the carrier and mapping questions considered during roster
production. The accepted [consolidated mapping](../../bindings/panic_1907/consolidated/)
later resolves the full release against Contracts V1. Neither those records nor
this guide changes the participant behavior declared in the Definitions and
Population Models.
