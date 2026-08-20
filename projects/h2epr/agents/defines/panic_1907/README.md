# Panic of 1907 Agent Definitions

This directory contains the current H2EPR-0288 reference Definitions for two institutionally different
participants:

- [Knickerbocker Trust Company](knickerbocker-trust.md), version `0.2.0`;
- [New York Clearing House Association](new-york-clearing-house.md), version `0.2.0`.

The Definitions are event-bound scholarly behavior models. They use the same ten-module structure but retain
different representation, information, authority, resource, decision, and intent semantics. Both are based on
fully exposed research material and remain exploratory; neither is historically calibrated or independently
validated.

## Supporting research assets

| File | Purpose |
|---|---|
| [source-register.md](source-register.md) | adopted public sources, stable source identities, public locators, byte hashes, adopted passages, and limitations |
| [evidence-ledger.md](evidence-ledger.md) | claim-level status, participant availability, allowed use, model consequence, and withdrawal consequence |
| [decision-situations.md](decision-situations.md) | shared situations and perturbations used to compare the two roles |

The evidence ledger owns claim status. The source register owns source identity and custody metadata. The
Definitions own participant behavior semantics. Scenario/environment assets will own instantiated world facts,
delivery, institutional process, adjudication, and results.

## Implementation status

There is no active executable binding for the `0.2.0` Definitions. Their observation, state, commitment, intent,
and trace mapping is the next separately reviewed step. Until that mapping is accepted, code and traces must not
claim conformance with these Definitions.

The earlier `0.1.0-dev` three-tick path is preserved only as a frozen engineering fixture under
[`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`](../../../tests/fixtures/agents/panic_1907/minimal_binding_v0_1/).
It checks the existing binding and trace seams; it is not an older editable Definition line and does not bind
the current files.

## Structural choice retained for NYCH

The member-facility restriction is common to both NYCH structures. The current conservative baseline is
`NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`; `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` is retained only as a
structural sensitivity variant. Neither is presented as historically validated.
