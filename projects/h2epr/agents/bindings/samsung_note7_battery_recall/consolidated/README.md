# Samsung Galaxy Note7 consolidated mapping v0.1

This package maps the exact H2EPR-0481 Roster Definition release onto H2EPR
Contracts V1. It covers four Agent Definitions and four Population Models
without changing their behavior.

The package is a complete engineering design, not an executable binding. It
does not create ParticipantArtifacts, select policies, run a simulation, or
support calibration, historical fit, held-out performance, policy
effectiveness, scientific validity, or universal generality.

## Files

| File | Responsibility |
|---|---|
| [semantic-inventory.md](semantic-inventory.md) | exact products, situations, observations, private state, intents, lifecycles, authority, resources, and clocks |
| [mapping-specification.md](mapping-specification.md) | event-qualified entity, actor/unit, capability, observation, state, intent, lifecycle, authority, resource, result, and replay mapping |
| [v1-carrier-review.md](v1-carrier-review.md) | direct/internal/Scenario classification and Contracts successor test |
| [substantive-review.md](substantive-review.md) | authoring-exposed adversarial review, resolved findings, and limitations |
| [manifest.json](manifest.json) | release identity, pinned source, coverage, artifacts, decision, carrier verdict, and authorization boundary |
| [SHA256SUMS](SHA256SUMS) | release-directory integrity record |

[ADR-0014](../../../../decisions/ADR-0014-note7-consolidated-mapping-boundary.md)
records the mapping decisions. The roster release remains the participant-
semantic authority; this directory owns only carrier and Scenario mapping.

Verify this directory with `sha256sum -c SHA256SUMS`. The next semantic stage
is the Event Scenario Definition; later configuration, admission, binding,
runtime, execution, and evaluation remain separately identified products.
