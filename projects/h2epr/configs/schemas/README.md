# Scenario Configuration admission schemas

This directory contains project-local, versioned schemas used by the bounded
H2EPR configuration-admission surface.

Two explicit profiles are available:

| Schema | Configuration family |
|---|---|
| `event-scenario-configuration-v0.1.schema.json` | the accepted original v0.1 shape used by the Panic of 1907 |
| `event-scenario-configuration-semantic-v0.1.schema.json` | the closed semantic shape for configurations with explicit institutions, processes, assets, materialization, and bounded lineage |

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
