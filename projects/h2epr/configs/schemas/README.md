# Scenario Configuration admission schemas

This directory contains project-local, versioned schemas used by the bounded
H2EPR configuration-admission surface.

Two explicit profiles are available:

| Schema | Configuration family |
|---|---|
| `event-scenario-configuration-v0.1.schema.json` | the accepted original v0.1 shape used by the Panic of 1907 |
| `event-scenario-configuration-semantic-v0.1.schema.json` | the frozen cyber-oriented semantic shape accepted for SingHealth |
| `event-scenario-configuration-semantic-v0.2.schema.json` | the closed domain-neutral semantic shape for configurations with explicit institutions or scoped resource domains, processes, assets, materialization, and bounded lineage |

The semantic loader accepts two versioned six-slot structural vocabularies.
The v0.1 schema retains the original cyber-oriented names and hash for
byte-stable SingHealth descendants. New domains use the v0.2 neutral names
`exogenous_pressure`, `route_and_delivery`, `population_assembly`,
`authority_capacity`, `operational_result`, and
`public_action_delivery`, with matching materialization profiles. A package
must use the complete vocabulary selected by its format identity.
Registry entries may also declare `semantic_kind` so a scoped market,
consumer, or operator resource domain is not misrepresented as a legal
institution merely because the v0.1 carrier field retains its historical
name.

Cross-object identity, assembly, input-integrity, overlay-target, coverage, and
execution-boundary checks remain in the fail-closed loader because JSON Schema
alone cannot derive them from accepted Roster and mapping releases.

Each schema's `$id` is its stable repository URL. The loader selects a profile
only from the document's explicit format identity; it does not infer a profile
from an event ID or accept unvalidated extensions.

These schemas are not members of `contracts/v1/` and do not add or change a V1
runtime carrier. A configuration that needs a field outside an accepted shape
requires an explicit schema evolution and compatibility review; it must not
receive an unvalidated event-local extension or a loader default.
