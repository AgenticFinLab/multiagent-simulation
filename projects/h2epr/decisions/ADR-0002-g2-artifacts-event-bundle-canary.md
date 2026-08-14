# ADR-0002: Project-local G2 artifacts and EventBundle canary

- Status: accepted for the architecture-demo candidate; runtime placement pending
- Scope: declarative construction after Construction IR and before simulation

## Context

The project needs an auditable bridge from typed Construction IR to inputs that
a future participant runtime can consume. The bridge must prove identity,
roster, provenance, normalized-world, policy, and seal closure without making a
premature permanent package decision or starting a simulation.

The Panic-of-1907 canary uses a complete target draft for engineering speed.
Every target-specific descendant is therefore permanently
`full_draft_exposed` and `architecture_demo_only`. Its normalized basis-point
world is a sensitivity instrument, not a historical calibration.

## Decision

Incubate four responsibilities beneath `projects/h2epr/src/h2epr/`:

- `artifacts`: reviewed entity registry, reversible roster/loss accounting,
  provenance values, and one generic ParticipantArtifact envelope;
- `policies`: declarative Rule capabilities and policy catalogs, with no model
  or runtime call;
- `world`: normalized profiles and pure deterministic calculations, with no
  authoritative live-state mutation; and
- `bundles`: explicit source-profile binding, canonical construction seals,
  RuntimeScenarioBundle compilation, offline validation, and logical manifests.

Create one construction/EventBundle pair for each of three sensitivity
profiles. Keep seeds outside the EventBundle and bind the Cartesian product of
three profiles and three seeds in a nine-row future-execution matrix. Historical
post-cutoff exogenous items remain empty.

The target builder validates the complete explicit 26-file non-evaluation
development profile but isolates the 0288 ancestry to two common inputs and the
three approved target files. No directory discovery, evaluation input, hidden
configuration, absolute output path, or cross-event value may enter the bundle.

## Consequences

This establishes deterministic, schema-conforming future runtime inputs and a
bounded place for canary assumptions. It does not establish simulator
readiness, execute a Player, authorize a reducer or tick loop, or support a
scientific continuation claim. A clean-prefix rebuild remains mandatory before
strict continuation evidence is admissible.

The current module split, policy thresholds, profiles, and package location are
revisable. A focused pre-runtime review must decide retain/relocate/split
placement using G1/G2 evidence. Any successor must preserve the V1 identity,
three-view, provenance, seal, and evaluation-isolation contracts; event-specific
roster or world assumptions must not become generic MASim defaults.
