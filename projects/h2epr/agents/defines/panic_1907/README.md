# Panic of 1907 Agent Definitions

This directory contains the current H2EPR-0288 reference Definitions for three institutionally different
participants:

- [Knickerbocker Trust Company](knickerbocker-trust.md), version `0.2.1`;
- [New York Clearing House Association](new-york-clearing-house.md), version `0.2.1`;
- [National Bank of Commerce in New York](national-bank-of-commerce.md), version `0.1.0`.

The Definitions are event-bound scholarly behavior models. They use the same ten-module structure but retain
different representation, information, authority, resource, decision, and intent semantics. All are based on
fully exposed research material and remain exploratory; none is historically calibrated or independently
validated.

The first non-Agent Roster product is the adjacent
[Knickerbocker depositor population model](../../../populations/defines/panic_1907/knickerbocker-depositors.md).
It reuses this event's source register and evidence ledger while keeping its
distributed behavior semantics under `populations/`.

The accepted event scope and remaining participant dispositions are in the
[H2EPR-0288 research roster](../../rosters/panic_1907.md). New production
batches use the event [semantic skeleton](../../../scenarios/panic_1907/semantic-skeleton.md)
and stop at a lightweight interface preflight. A consolidated mapping is made
only after the Roster Definition release.

## Supporting research assets

| File | Purpose |
|---|---|
| [source-register.md](source-register.md) | adopted public sources, stable source identities, public locators, byte hashes, adopted passages, and limitations |
| [evidence-ledger.md](evidence-ledger.md) | claim-level status, participant or population availability, allowed use, model consequence, and withdrawal consequence |
| [decision-situations.md](decision-situations.md) | shared situations and perturbations used to compare Knickerbocker and NYCH |
| [binding specification](../../bindings/panic_1907/) | accepted mapping of the Knickerbocker and NYCH Definitions into Contracts V1, business lifecycles, intent registry, and cross-object checks |

The evidence ledger owns claim status. The source register owns source identity and custody metadata. The
Definitions own participant behavior semantics. Scenario/environment assets will own instantiated world facts,
delivery, institutional process, adjudication, and results.

## Implementation status

The Knickerbocker and NYCH `0.2.1` Definitions have an exact-hash machine mapping and a conservative first
conformance slice under [`scenarios/panic_1907/`](../../../scenarios/panic_1907/). The machine registry covers
their 21 intents; the first slice exercises eight decisions from support request through delivered
facility-scoped decline and subsequent contingency preparation.

The NBC `0.1.0` Definition is the accepted scholarly model for the third role. It is not included in the
two-role binding, executable mapping, intent registry, or scenario implementation. Its mapping is deferred to
the consolidated Roster Definition release rather than performed as a standalone three-role cycle.

The earlier `0.1.0-dev` three-tick path is preserved only as a frozen engineering fixture under
[`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`](../../../tests/fixtures/agents/panic_1907/minimal_binding_v0_1/).
It checks the existing binding and trace seams; it is not an older editable Definition line and does not bind
the current files.

## Structural choice retained for NYCH

The member-facility restriction is common to both NYCH structures. The current conservative baseline is
`NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`; `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` is retained only as a
structural sensitivity variant. Neither is presented as historically validated.
