# Panic of 1907 Agent Definitions

This directory contains the current H2EPR-0288 reference Definitions for seven institutionally different
participants:

- [Knickerbocker Trust Company](knickerbocker-trust.md), version `0.2.1`;
- [New York Clearing House Association](new-york-clearing-house.md), version `0.2.1`;
- [National Bank of Commerce in New York](national-bank-of-commerce.md), version `0.1.0`;
- [J. Pierpont Morgan](j-pierpont-morgan.md), version `0.1.0`;
- [Trust Company of America](trust-company-of-america.md), version `0.1.0`;
- [Lincoln Trust Company](lincoln-trust-company.md), version `0.1.0`; and
- [trust-company presidents' five-person committee](trust-company-presidents-committee.md), version `0.1.0`.

The Definitions are event-bound scholarly behavior models. They use the same ten-module structure but retain
different representation, information, authority, resource, decision, and intent semantics. All are based on
fully exposed research material and remain exploratory; none is historically calibrated or independently
validated.

Five non-Agent Roster products sit in the adjacent population collection: the
[Knickerbocker depositor model](../../../populations/defines/panic_1907/knickerbocker-depositors.md),
[member/correspondent-bank resource-decision model](../../../populations/defines/panic_1907/member-and-correspondent-bank-resource-decisions.md),
[later trust-company depositor model](../../../populations/defines/panic_1907/later-trust-company-depositors.md),
[call-money lender model](../../../populations/defines/panic_1907/call-money-lenders.md),
and [broker-borrower model](../../../populations/defines/panic_1907/call-money-broker-borrowers.md).
They reuse this event's source register and evidence ledger while keeping their
distributed behavior semantics under `populations/`.

The accepted event scope and every participant disposition are in the
[H2EPR-0288 research roster](../../rosters/panic_1907.md). The event
[semantic skeleton](../../../scenarios/panic_1907/semantic-skeleton.md) and the
[Roster Definition release v0.1](../../../releases/panic_1907/roster-definition-v0.1/)
provide the fixed participant-semantic input. The accepted
[consolidated mapping](../../bindings/panic_1907/consolidated/),
[Event Scenario Definition v0.1](../../../scenarios/panic_1907/definition-v0.1/),
and [Scenario Configuration v0.1](../../../configs/panic_1907/scenario-configuration-v0.1/)
now carry the event-level downstream authorities without changing these
Definitions.

## Supporting research assets

| File | Purpose |
|---|---|
| [source-register.md](source-register.md) | adopted public sources, stable source identities, public locators, byte hashes, adopted passages, and limitations |
| [evidence-ledger.md](evidence-ledger.md) | claim-level status, participant or population availability, allowed use, model consequence, and withdrawal consequence |
| [decision-situations.md](decision-situations.md) | shared situations and perturbations used to compare Knickerbocker and NYCH |
| [NBC interface preflight](../../interfaces/panic_1907/national-bank-of-commerce.md) | accepted compound-observation, route-hop and lifecycle impact for NBC |
| [R2 interface preflight](../../interfaces/panic_1907/r2-private-and-named-trusts.md) | accepted semantic fit and deferred-mapping note for Morgan, TCA, and Lincoln |
| [R3 interface preflight](../../interfaces/panic_1907/r3-collective-trust-support.md) | accepted semantic fit and deferred-mapping note for the committee and bank resource-decision population |
| [R4 interface preflight](../../../populations/interfaces/panic_1907/r4-trust-contagion-and-call-money.md) | accepted host-contagion, call-lender, broker-borrower and NYSE scenario boundary |
| [Roster Definition release v0.1](../../../releases/panic_1907/roster-definition-v0.1/) | exact semantic input inventory for consolidated mapping |
| [binding specification](../../bindings/panic_1907/) | accepted mapping of the Knickerbocker and NYCH Definitions into Contracts V1, business lifecycles, intent registry, and cross-object checks |
| [consolidated mapping](../../bindings/panic_1907/consolidated/) | accepted release-wide identity, observation, intent, lifecycle, authority, resource, result, and carrier design |
| [Scenario Configuration v0.1](../../../configs/panic_1907/scenario-configuration-v0.1/) | accepted non-executable mechanism-coverage instantiation |
| [KT--NBC--NYCH E6 binding](../../bindings/panic_1907/kt-nbc-nych-v0.1/) | exact four-action, three-route positive projection with NBC as pure courier |
| [E7 conformance closeout](../../../scenarios/panic_1907/lineage-conformance-v0.1/) | cross-hop negatives, deterministic trace/replay receipt, implementation review, and method closeout |

The evidence ledger owns claim status. The source register owns source identity and custody metadata. The
Definitions own participant behavior semantics. Scenario/environment assets will own instantiated world facts,
delivery, institutional process, adjudication, and results.

## Implementation status

The Knickerbocker and NYCH `0.2.1` Definitions have an exact-hash machine mapping and a conservative first
conformance slice under [`scenarios/panic_1907/`](../../../scenarios/panic_1907/). The machine registry covers
their 21 intents; the first slice exercises eight decisions from support request through delivered
facility-scoped decline and subsequent contingency preparation.

The NBC, Morgan, TCA, Lincoln, and trust-company committee `0.1.0` Definitions
and all five population models are accepted scholarly products in Roster
Definition release v0.1. NBC alone now has a separate bounded E6 courier
projection in the KT--NBC--NYCH lineage; it is still absent from the frozen
two-role registry. The other four Definitions and all populations have no
participant policy implementation. Their semantics remain covered by the
consolidated mapping profile rather than separate role-by-role engineering.
E5--E7 have passed for the bounded lineage, but the accepted Scenario
Configuration remains explicitly non-executable and its nine top-level policy
selections remain unbound.

The R2 Definitions are intentionally non-symmetrical. Morgan is a bounded named coordinator; TCA is an
aggregate institutional response interface; Lincoln is a thin board-authorized communication interface because
the bounded evidence did not support a focal Lincoln assistance, collateral, or operating policy.

The earlier `0.1.0-dev` three-tick path is preserved only as a frozen engineering fixture under
[`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`](../../../tests/fixtures/agents/panic_1907/minimal_binding_v0_1/).
It checks the existing binding and trace seams; it is not an older editable Definition line and does not bind
the current files.

## Structural choice retained for NYCH

The member-facility restriction is common to both NYCH structures. The current conservative baseline is
`NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`; `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` is retained only as a
structural sensitivity variant. Neither is presented as historically validated.
