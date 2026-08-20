# H2EPR-0288 micro-situation: October 21 support request

> Status: `MUTABLE_PILOT_SCENARIO / EXPLORATORY_CONSTRUCTION_ONLY`

## Research question

Can two institutional Agents produce structurally different, auditable
behavior from legal information, authority, procedure, and request lifecycle—
without seeing the October 22 suspension, reading global state, or announcing
their own result?

This pilot tests carrier and behavioral-contract fit. It does not test whether
the generated path reproduces history.

## Boundary

```text
event = H2EPR-0288 Panic of 1907
date = 1907-10-21
exact clock time = not frozen
agents = Knickerbocker Trust, New York Clearing House
external channel = National Bank of Commerce
future cutoff = before the 1907-10-22 suspension
```

## Minimal institutional facts

| Concept | Pilot value | Basis / ownership |
|---|---|---|
| Knickerbocker role | aggregate trust-company decision interface | `A-001`; Definition-owned representation |
| NYCH role | aggregate procedural clearinghouse interface | `A-001`, `T-001`; Definition-owned representation |
| membership | Knickerbocker is a nonmember | `H-001`; scenario relation |
| request channel | NBC carries the request | `H-002`, `H-003`, `A-002`; scenario delivery |
| member facility | nonmember is ineligible | `H-001`, `H-007..009`; environment hard gate |
| other support route | authority unknown | `U-001`; no permission or prohibition inference |
| requester identity/mandate | title level / authorization explicit but historically unresolved | `U-002`; scenario process state |
| pilot procedural authority | affirmative synthetic authority for Knickerbocker to submit this request and for the NYCH interface to apply the known member-facility classification | implementation input only; not a historical finding |
| exact resources and solvency | unknown | `GAP-04`; no numerical thresholds |

## Legal observation matrix

| Observation | Knickerbocker | NYCH |
|---|---|---|
| own authorization/process state | own projection only | own projection only |
| own pressure/operational assessment | qualitative projection | not directly visible |
| request lifecycle | own request projection | after delivery |
| submitted information | knows what it sent | sees only delivered material |
| membership/route/eligibility | own relation can be known | institutional view after delivery |
| NYCH review/authorization | delivered updates only | private procedural projection |
| public pressure | only timestamped public signal | only timestamped public signal |
| global exact resources/hidden solvency | forbidden | forbidden |
| NBC internal reasoning | forbidden | forbidden |
| October 22 suspension/later outcome | forbidden | forbidden |

Missing or stale required information leads to clarification, procedure,
waiting, or auditable abstention—not a hidden default.

## Authoritative state used by the pilot

| State | Owner | Purpose |
|---|---|---|
| request status and result | environment business state | distinguish none/sent/delivered/denied/partial/realized |
| internal authorization | institutional process | prevent title or goal from granting authority |
| review stage | institutional process | prevent random delay from replacing procedure |
| support route and eligibility | scenario/environment | separate known member-facility gate from `U-001` |
| operational posture | replayable private decision state | record response to a delivered result |

## Three-step executable path

1. With a synthetic explicit authorization, high qualitative pressure, an
   available channel, and no unresolved request, Knickerbocker may submit a
   support-request intent. The environment creates the business request and
   queues its message.
2. After delivery, the synthetically authorized NYCH intake interface observes
   a nonmember request for the known member-only facility and emits a typed
   decline intent. The environment records the denial and queues a result
   message. Delivery alone never means support was accepted or realized.
3. Only after the denial is delivered does Knickerbocker emit an operational-
   restriction preparation intent. The environment commits that state change.

Both explicit procedural authorizations and the choice of the member-facility
route are synthetic pilot inputs, not newly discovered historical facts.

## Required counterexamples

- An undeclared or future observation must be rejected before policy use.
- An unresolved request must not be duplicated.
- Unknown other-route authority must produce clarification or abstention, not
  automatic permission or universal prohibition.
- Swapping role/authority must change the permitted intent envelope.
- An Agent intent must never update authoritative state directly.

Passing these checks proves only that the two Definitions can constrain a
minimal implementation and produce useful feedback.
