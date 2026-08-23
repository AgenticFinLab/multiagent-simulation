# H2EPR evolution and compatibility

H2EPR evolves its research models and implementations while preserving stable
interfaces for accepted artifacts. This document defines the version,
identity, and migration rules used across the project.

## Stable interfaces

`contracts/v1/` is the current compatibility boundary for:

- construction identities and source-policy classes;
- participant artifacts and runtime scenario bundles;
- observations, actions, messages, and logical time;
- trace records, tick seals, run seals, and manifests;
- generated event process graphs and graph seals; and
- separation of construction, runtime, and evaluation.

Schema validation alone is not sufficient. Cross-object identities, hashes,
state transitions, record coverage, and replay invariants are also part of the
contract.

The internal construction snapshot uses `h2epr.construction_ir.v1`. A change
to its serialized meaning requires a new snapshot identity even when Contracts
V1 remains compatible.

## Identity and version conventions

JSON Schema identifiers use stable repository URLs. Contracts schemas begin
with:

```text
https://raw.githubusercontent.com/AgenticFinLab/multiagent-simulation/main/projects/h2epr/contracts/v1/schemas/
```

Configuration schemas use the corresponding
`projects/h2epr/configs/schemas/` namespace. The checked-in catalogs resolve
these identifiers without network access.

Version forms have distinct purposes:

- public `version` fields use semantic versions such as `0.1.0`;
- reviewed prereleases use forms such as `0.1.0-candidate.1`;
- release directories and release IDs may use `v0.1` for a maintained release
  line;
- serialized format identifiers use `v0_1`, and Python modules use `_v0_1`;
  and
- lifecycle status values use lowercase snake case.

These forms are not interchangeable. Development rounds, review batches, and
dates are not public versions.

## Compatible changes

Private Python modules, internal class names, test organization, documentation,
and developer tooling may change in place when their observable contracts are
preserved. Derived mapping formats without external consumers may also evolve
with their tests and manifests.

Current research templates and Skills are maintained in place. Accepted
releases remain associated with the method and identities under which they
were reviewed; they are not rewritten merely to match later editorial
conventions.

## Changes that require a successor

A new contract or artifact version is required when a supported consumer would
observe a change in meaning, required fields, identity, validation behavior,
or serialization. Examples include:

- rejecting data that is valid under the existing schema;
- changing canonical JSON or a hash preimage;
- changing the meaning of an intent, disposition, result, or trace record;
- changing seal, reduction, or replay semantics;
- weakening an information or authority boundary; or
- requiring a carrier that Contracts V1 cannot represent without loss.

A successor should include the new contract, a migration description,
deterministic old and new fixtures, compatibility tests for supported
consumers, and an explicit cutover point.

## Research artifact changes

Participant Definitions, population models, scenario definitions,
configurations, and their mappings are linked by identity. Before accepting a
semantic change, inspect every downstream binding, policy, state, trace,
fixture, manifest, and document that consumes it. A hash may be updated only
after the consumer is shown to conform to the changed meaning.

Tracked paths contain the current method and accepted products. Superseded
drafts and rejected alternatives do not remain beside the maintained file as
date-suffixed or `-old` copies. Git history preserves earlier tracked states;
intentional contract versions and supported release lines remain explicit
exceptions.

## Release integrity

A release manifest records the identity and role of upstream semantic inputs.
A `SHA256SUMS` file covers files owned by its release directory. This keeps
local package integrity separate from lineage validation.

Once an accepted release, receipt, or sealed run record is published, its
bytes are immutable. Corrections use an erratum or a successor record. This
rule applies to adopted source archives, accepted decisions, evidence
manifests, run manifests, sealed traces, replay data, and release receipts.

## Package boundary

H2EPR has one Python package rooted at `projects/h2epr/src/h2epr` and its own
`pyproject.toml`. It is installed independently from the root MASim package.
Semantic assets under `agents/`, `populations/`, `configs/`, `releases/`, and
`scenarios/` are package inputs and release records, not competing import
roots.

Moving the package or changing a path that participates in an identity is a
migration. Review construction identities, manifests, input inventories,
seals, and published locators before such a change.

## Promoting reusable code to MASim

Code belongs in `masim/` only when it has:

- a domain-neutral interface;
- no H2EPR event identity or institutional policy;
- explicit failure and replay behavior;
- a credible consumer beyond one event-specific implementation; and
- tests that preserve H2EPR information and authority boundaries.

The event-process transport, reducer, trace, and seal primitives meet this
boundary. Agent Definitions, historical evidence, institutional behavior,
event policies, and evaluation remain H2EPR responsibilities.

## Related documents

- [Project README](README.md)
- [Architecture](ARCHITECTURE.md)
- [Event modeling workflow](WORKFLOW.md)
- [Contracts V1](contracts/v1/README.md)
- [Architecture decisions](decisions/)
