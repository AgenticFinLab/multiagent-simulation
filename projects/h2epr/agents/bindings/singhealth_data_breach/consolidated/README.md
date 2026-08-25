# SingHealth Data Breach consolidated mapping

This directory contains the accepted design specification that maps
H2EPR-0616 Roster Definition release v0.1 onto H2EPR Contracts V1. It covers
all seven Agent Definitions and two Population Models in the release.

The specification is not executable. It does not choose a behavioral policy,
create ParticipantArtifacts, implement all participant intents, run a
simulation, or change Contracts V1. The Panic of 1907 mapping remains a
separate event-specific reference.

## Files

| File | Purpose |
|---|---|
| [semantic-inventory.md](semantic-inventory.md) | fixed release inventory and complete observation, decision, state, intent, authority, resource, and lifecycle surface |
| [mapping-specification.md](mapping-specification.md) | accepted institution, actor/unit, capability, observation, private-state, intent, lifecycle, authority, and result mapping |
| [v1-carrier-review.md](v1-carrier-review.md) | accepted carrier decision and narrow-successor watchpoints |
| [substantive-review.md](substantive-review.md) | adversarial review, implementation conditions, and owner-resolution record |
| [manifest.json](manifest.json) | release identity, source-release identity, artifact hashes, decisions, and authorization boundary |
| [SHA256SUMS](SHA256SUMS) | integrity record for files owned by this release directory |

[ADR-0007](../../../../decisions/ADR-0007-singhealth-consolidated-mapping-boundary.md)
owns `OD-CM-05` through `OD-CM-08`. Roster Definition release v0.1 remains the
participant-semantic authority; this directory owns only its accepted mapping
onto the carrier and Scenario boundaries.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
(cd ../../../../releases/singhealth_data_breach/roster-definition-v0.1 && sha256sum -c SHA256SUMS)
```

After a Scenario Configuration is accepted and admitted, the first eligible
implementation scope is an exact fail-closed loader and one bounded
technical-to-institutional lineage. That work requires separate authorization.
