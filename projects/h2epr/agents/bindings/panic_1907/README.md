# Panic of 1907 Agent binding

This directory contains the accepted mapping specification for the two
H2EPR-0288 Agent Definitions, version `0.2.1`. It maps their observations,
decision commitments, state, intents, institutional processes, and trace
requirements onto Contracts V1.

The specification is currently non-executable. Code and traces can claim
conformance only after the mapping, registry, and fail-closed checks have been
implemented and reviewed against the exact Definition identities recorded in
[two-role-binding.md](two-role-binding.md).

## Files

| File | Purpose |
|---|---|
| [two-role-binding.md](two-role-binding.md) | pinned Definition and evidence identities, V1 placement, causal chain, carrier judgment, and implementation entry conditions |
| [scenario-identity-and-business-lifecycles.md](scenario-identity-and-business-lifecycles.md) | NYCH structural scenario identity and the seven authoritative business lifecycles |
| [intent-registry.md](intent-registry.md) | versioned semantic contracts and V1 projections for the 21 two-role intents |
| [cross-object-conformance.md](cross-object-conformance.md) | fail-closed rules linking Definitions, scenario state, artifacts, observations, decisions, intents, messages, results, trace, and seals |

The Agent Definitions remain the authority for participant behavior. Scenario
state and lifecycle truth remain environment-owned, machine shape remains in
Contracts V1, and only the reducer may commit results. These documents record
the reviewed mapping between those authorities rather than duplicating them.

The baseline binding uses
`NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`. The
`BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` branch is retained as a separate
structural-sensitivity specification and is not part of the first
implementation slice.

The earlier `0.1.0-dev` path remains a frozen engineering fixture under
[`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`](../../../tests/fixtures/agents/panic_1907/minimal_binding_v0_1/).
It does not bind the current Definitions.
