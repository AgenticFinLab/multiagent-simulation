# Panic of 1907 consolidated mapping

This directory contains the accepted design specification that maps H2EPR-0288
Roster Definition release v0.1 onto Contracts V1. It covers all seven Agent
Definitions and five population models in the release.

The specification is not executable. It does not select a Rule policy, create
ParticipantArtifacts, run a simulation or change Contracts V1. The existing
two-role binding in the parent directory remains the frozen engineering
reference.

## Files

| File | Purpose |
|---|---|
| [semantic-inventory.md](semantic-inventory.md) | fixed release inventory and complete observation, commitment, state, intent, authority, resource and lifecycle surface |
| [mapping-specification.md](mapping-specification.md) | accepted entity, actor, capability, observation, private-state, intent, lifecycle and result mapping |
| [v1-carrier-review.md](v1-carrier-review.md) | accepted carrier decision and narrow-successor watchpoints |
| [substantive-review.md](substantive-review.md) | adversarial review, implementation conditions and owner-resolution record |
| [manifest.json](manifest.json) | release identity, source-release identity, artifact hashes, decisions and authorization boundary |
| [SHA256SUMS](SHA256SUMS) | integrity record for files owned by this release directory |

[ADR-0004](../../../../decisions/ADR-0004-roster-consolidated-mapping-boundary.md)
owns OD-CM-01 through OD-CM-04. Roster Definition release v0.1 remains the
semantic source authority; this directory owns only its accepted mapping onto
the carrier and scenario boundaries.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
(cd ../../../../releases/panic_1907/roster-definition-v0.1 && sha256sum -c SHA256SUMS)
```

A mapping-loader/conformance slice is the next eligible implementation scope,
but it requires separate authorization.
