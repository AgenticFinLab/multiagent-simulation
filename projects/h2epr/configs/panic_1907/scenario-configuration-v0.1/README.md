# Panic of 1907 Scenario Configuration v0.1

- Status: accepted non-executable configuration
- Event: `H2EPR-0288`
- Configuration: `h2epr.0288.scenario.mechanism-coverage.v0_1@0.1.0`
- Purpose: mechanism coverage
- Accepted: 23 August 2026

This release is the first versioned instantiation of the accepted Panic of
1907 Event Scenario Definition. It pins the analytic clock, 16-actor and
10-unit assembly, categorical opening records, nine bounded exogenous inputs,
eight conservative structural selections, nine unbound policy semantics,
eight predeclared sensitivity overlays, completion rules, and fail-closed
execution expectations.

It is not a historical baseline and is not executable. Population quantities,
profiles, qualitative resource envelopes, and the 2 November horizon are
exposed mechanism-coverage constructions. No policy implementation, exact
runtime carrier projection, loader, simulation, calibration, validation, or
historical-validity claim is supplied by this release.

## Files

| File | Purpose |
|---|---|
| [scenario-configuration.json](scenario-configuration.json) | accepted machine-readable configuration semantics and execution boundary |
| [configuration-design.md](configuration-design.md) | explanatory design, construction choices, and accepted owner decisions |
| [definition-closure.md](definition-closure.md) | closure against Event Scenario Definition v0.1 and the full released interface |
| [substantive-review.md](substantive-review.md) | successor-window review, resolved findings, limitations, and owner resolution |
| [manifest.json](manifest.json) | release identity, candidate provenance, semantic-input hashes, artifact hashes, decisions, and authorization boundary |
| [SHA256SUMS](SHA256SUMS) | integrity record for this release and its fixed authorities |

[ADR-0006](../../../decisions/ADR-0006-panic-1907-scenario-configuration-boundary.md)
records `OD-CFG-01` through `OD-CFG-04`. The manifest also preserves the
exact hashes of the four owner-reviewed candidate files so the promotion
delta can be audited.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
```

The old `../rule_canary_v1.json` and `../compiler_canary_v1.json` remain
frozen engineering references; they are not semantic inputs to this release.
A minimal configuration loader and KT–NBC–NYCH carrier projection is the next
eligible engineering question, but it requires separate authorization.
