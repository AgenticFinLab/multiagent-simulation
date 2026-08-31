# Samsung Galaxy Note7 battery recall full-roster Rule package v0.1

- Event: `H2EPR-0481`
- Package: `h2epr.0481.full-roster-rule.v0_1@0.1.0`
- Runtime bundle: `h2epr.0481.rule-runtime-bundle.v0_1@0.1.0`
- Status: `accepted_executable_package`
- Purpose: deterministic, uncalibrated mechanism coverage

This is the executable successor to the accepted Note7 Scenario
Configuration and Policy Realization. The semantic parents remain unchanged;
this release adds the exact carriers, initial state, decision inputs, action
bindings, routes, lifecycle graphs, clock, runtime components, completion
policy, and compiler input required for a full-roster Rule run.

The [executable package](executable-package.json) records lineage, component
bindings, run requirements, and custody rules. The
[runtime bundle](runtime-bundle.json) is the complete reproducible runtime
input. The [substantive review](substantive-review.md) examines assembly,
authority, time, failure, and claim boundaries.

## Closed assembly

| Surface | Accepted count |
|---|---:|
| actor instances and carriers | 8 |
| actor-capability projections | 8 |
| participant artifacts | 8 |
| decision observation rules | 22 |
| actor-qualified action bindings | 37 |
| communication routes | 24 |
| configured institutional route records | 8 |
| selected Scenario policies | 9 |
| lifecycle families | 12 |
| runtime components | 9 |
| logical coordinates | 50 |

One carrier belongs to each configured named or Population actor. Population
actors retain their own assignment, capacity, asset access, institution,
private state, and action namespace. No carrier is added for a cohort,
institutional process, airline passenger set, regulator as an undifferentiated
organization, or a 2017 investigator.

Each commitment has one actor-qualified observation rule. All 22 rules select
a declared branch in this canonical mechanism-coverage profile; alternative
branches and explicit no-intent behavior remain part of the policy contract
rather than being combined into one run. The selected primary lifecycles cover
all twelve families while preserving every commitment's full lifecycle set.

## Authority, routing, and results

An intent is bound to its actor, capability, commitment, branch, lifecycle,
private-state proposal, capacity, authority graph, access record, relationship,
resource owner, and exact result route. Product, remedy, hazard, recall,
warning, and emergency-order mechanisms remain separately adjudicated.

The 24 routes consist of eight environment-to-actor typed-result channels and
sixteen participant channels. Every participant channel resolves to one of the
eight accepted configuration route records. Each route has one sender and one
recipient; there is no all-to-all fallback. Messages arrive after one logical
tick, so issuance, transport, delivery, observation, and later choice remain
distinct.

## Event time and custody

Five accepted event anchors and ten same-time precedence barriers yield 50
logical coordinates. The timezone is UTC. A coordinate imposes causal order
but does not invent an intraday time. Six exogenous opportunities are released
at declared anchors without selecting their historical result.

Admission reconstructs the runtime bundle and requires exact canonical
identity. The package requires two fresh runs with the same bundle and seed,
sealed ticks and run, authoritative replay, and a generated graph closed over
the sealed trace. Large run products belong in the ignored local custody
directory; the tracked run release contains compact receipts and identities.

## Scope

This package establishes executable engineering closure for a full-roster
mechanism-coverage run. It does not establish historical reconstruction,
parameter calibration, historical fit, held-out evaluation, recall
effectiveness, causal identification, scientific validity, or universal
generality.
