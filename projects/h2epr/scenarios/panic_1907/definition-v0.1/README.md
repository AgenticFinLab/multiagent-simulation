# Panic of 1907 Event Scenario Definition v0.1

- Status: accepted semantic specification
- Event: `H2EPR-0288`
- Scenario: `h2epr.scenario.0288.panic_1907@0.1.0`
- Accepted: 22 August 2026

This release describes the event world shared by Panic of 1907 participant
models. It fixes the research interval, causal ownership, institutions,
relationships, resources, information delivery, business lifecycles,
adjudication, structural variants, termination, and reproducibility boundary.

The release closes the complete interface of Roster Definition release v0.1:
12 semantic products, 115 observation placements, 107 intent placements,
13 lifecycle families, and 34 cross-object rules. Exact actors, population
weights, opening values, route policies, and other executable choices belong
to a later versioned scenario configuration.

## Files

| File | Purpose |
|---|---|
| [scenario-definition.md](scenario-definition.md) | accepted publication-facing event and environment semantics |
| [interface-closure.md](interface-closure.md) | release-wide reconciliation of participant observations, intents, lifecycles, authority, and resources |
| [substantive-review.md](substantive-review.md) | semantic review and owner-resolution record |
| [manifest.json](manifest.json) | release identity, source identities, artifact hashes, accepted decisions, and authorization boundary |
| [SHA256SUMS](SHA256SUMS) | integrity record for files owned by this release directory |

[ADR-0005](../../../decisions/ADR-0005-panic-1907-event-scenario-definition-boundary.md)
records `OD-SC-01` through `OD-SC-04`. The conservative structural baseline
is the design default; alternative interpretations remain unvalidated
sensitivity variants and must be pinned in scenario and run identity.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
```

The next design stage is a minimal versioned scenario configuration. Policy
implementation and simulation require separate authorization.
