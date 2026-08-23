# Scenario Configuration admission schemas

This directory contains project-local, versioned schemas used by the bounded
H2EPR configuration-admission surface.

`event-scenario-configuration-v0.1.schema.json` closes the serialized shape of
the accepted v0.1 Scenario Configuration family. Cross-object identity,
assembly, input-integrity, overlay-target, coverage, and execution-boundary
checks remain in the fail-closed loader because JSON Schema alone cannot
derive them from the accepted roster mapping.

These schemas are not members of `contracts/v1/` and do not add or change a V1
runtime carrier. A second event that needs a new field must produce an explicit
schema evolution and compatibility review; it must not receive an unvalidated
event-local extension or a loader default.
