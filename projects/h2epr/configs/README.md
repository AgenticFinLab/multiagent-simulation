# H2EPR Scenario Configurations

This directory holds versioned, declared-purpose instantiations of accepted
H2EPR Event Scenario Definitions and consolidated mappings.

A Scenario Configuration selects a clock, structural baseline, actor and unit
assembly, opening records, exogenous inputs, policy semantics, sensitivities,
completion rules, and validation expectations. It does not redefine
participant behavior or event-world semantics.

Use the public
[Scenario Configuration semantic design template](scenario-configuration-template.md)
with the
[Scenario Configuration Skill](../skills/scenario-configuration/SKILL.md).

## Artifact classes

| Class | Purpose | Authority boundary |
|---|---|---|
| versioned Scenario Configuration | one reviewed instantiation for one declared purpose | normally non-executable until separately admitted, projected, and bound |
| bounded configuration admission | exact schema/canonical/hash/reference validation plus a static receipt | proves configuration-surface admission only; never supplies projection, policy, or execution |
| frozen engineering canary | regression input for an older bounded engineering path | never supplies semantic defaults or release authority to a new configuration |

## Current configurations

| Event | Scenario Configuration | Admission status |
|---|---|---|
| Panic of 1907 (`H2EPR-0288`) | [v0.1](panic_1907/scenario-configuration-v0.1/) | [bounded static admission v0.1](panic_1907/configuration-admission-v0.1/) |
| SingHealth Data Breach (`H2EPR-0616`) | [v0.1](singhealth_data_breach/scenario-configuration-v0.1/) | [bounded static admission v0.1](singhealth_data_breach/configuration-admission-v0.1/) |

Event-specific packages live under their event directory. A promoted package
normally contains the machine document, publication-facing design, Definition
closure, substantive review, README, manifest, and checksum inventory.

Project-local admission schemas live under [`schemas/`](schemas/). Each bounded
admission record pins its accepted source, canonical, schema, release, and
semantic-input identities without changing the accepted configuration release.

Schema/canonical admission, carrier projection, policy binding, runtime, and
evaluation are separately governed stages. Successful parsing or static
admission does not make a configuration executable.
