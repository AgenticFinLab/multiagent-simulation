# SingHealth Data Breach Scenario Configuration v0.1

- Status: accepted non-executable configuration
- Event: `H2EPR-0616`
- Configuration: `h2epr.0616.scenario.mechanism-coverage.v0_1@0.1.0`
- Purpose: mechanism coverage
- Accepted: 25 August 2026

This release instantiates the accepted SingHealth Data Breach Event Scenario
Definition through seven office actors and six function-specific
responsibility-unit actors. It pins the accepted clock, six structural
baselines, 33 opening records, eight exact routes, six bounded exogenous
inputs, nine unbound policy meanings, six exact sensitivity overlays,
completion rules, and one illustrative technical-to-institutional lineage.

The configuration is qualitative and non-executable. It is not a historical
baseline, replay, calibration, prediction, policy-effectiveness result, or
historical or scientific-validity claim. Its machine representation remains a
provisional semantic format until a separately governed admission stage
accepts a compatible machine surface. Parsing does not change execution
eligibility.

## Files

| File | Purpose |
|---|---|
| [scenario-configuration.json](scenario-configuration.json) | accepted machine-readable configuration semantics and fail-closed execution boundary |
| [configuration-design.md](configuration-design.md) | publication-facing purpose, assembly, opening-state, policy, sensitivity, completion, and closure account |
| [definition-closure.md](definition-closure.md) | closure against the accepted Event Scenario Definition and consolidated mapping |
| [substantive-review.md](substantive-review.md) | post-revision review, finding resolutions, limitations, and owner disposition |
| [manifest.json](manifest.json) | release identity, candidate provenance, pinned semantic inputs, artifact hashes, decisions, and claim boundary |
| [SHA256SUMS](SHA256SUMS) | integrity record for files owned by this release directory |

[ADR-0009](../../../decisions/ADR-0009-singhealth-scenario-configuration-boundary.md)
records `OD-CFG-05` through `OD-CFG-08`. The manifest preserves the exact
hashes of the four reviewed `candidate.2` files and separately identifies the
promotion-only metadata and publication-template alignment.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
```

The next legal stage is a separately authorized bounded configuration-
admission preflight. This release does not authorize schema evolution, exact
loading, carrier projection, participant binding, policy implementation,
runtime execution, simulation, calibration, or evaluation.
