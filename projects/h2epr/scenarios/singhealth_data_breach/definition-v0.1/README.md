# SingHealth Data Breach Event Scenario Definition v0.1

- Status: accepted semantic specification
- Event: `H2EPR-0616`
- Scenario: `h2epr.scenario.0616.singhealth_data_breach@0.1.0`
- Accepted: 25 August 2026

This release describes the event world shared by the H2EPR-0616 participant
models. It fixes the event boundary, causal ownership, institutions,
relationships, technical and organizational resources, information delivery,
shared lifecycles, adjudication, structural variants, termination, and
reproducibility boundary.

The release closes the complete interface of Roster Definition release v0.1:
nine semantic products, 29 decision situations, 62 observation placements, 44
private-state placements, 54 intent placements, and eleven shared lifecycle
families. Exact responsibility units, opening values, structural selections,
exogenous sequences, policies, and the first conformance lineage belong to a
later versioned Scenario Configuration.

## Files

| File | Purpose |
|---|---|
| [scenario-definition.md](scenario-definition.md) | accepted publication-facing event and environment semantics |
| [interface-closure.md](interface-closure.md) | release-wide reconciliation of participant observations, private state, intents, lifecycles, authority, and resources |
| [substantive-review.md](substantive-review.md) | semantic review and owner-resolution record |
| [manifest.json](manifest.json) | release identity, source identities, artifact hashes, accepted decisions, and authorization boundary |
| [SHA256SUMS](SHA256SUMS) | integrity record for files owned by this release directory |

[ADR-0008](../../../decisions/ADR-0008-singhealth-event-scenario-definition-boundary.md)
records `OD-SC-05` through `OD-SC-08`. Structural alternatives remain
unvalidated sensitivities and must be pinned in configuration and run identity.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
```

The next eligible design stage is a small, non-executable Scenario
Configuration. Loader implementation, policy implementation, and simulation
require separate authorization.
