# H2EPR evolution and compatibility

H2EPR is still developing its Agent and scenario model, while Contracts V1
already provides a stable interface for existing artifacts and tools. This
document explains which parts can change in place and which changes require a
new version.

## Stable interfaces

`contracts/v1/` defines the current compatibility boundary for:

- construction identities and source-policy classes;
- ParticipantArtifact and RuntimeScenarioBundle;
- information access, actions, messages and logical time;
- trace records, TickSeal and RunSeal;
- RunManifest and SimulationTrace;
- Generated EPG and GraphSeal;
- separation of construction, runtime and evaluation.

An object may satisfy JSON Schema and still fail a cross-object invariant.
Schema validation and semantic validation are both part of V1 compatibility.

The internal Construction IR snapshot currently uses
`h2epr.construction_ir.v1`. A change to its meaning or serialized shape needs
a new snapshot version even when Contracts V1 remains unchanged.

## What can change in place

The following are implementation details and can evolve with tests and review:

- private Python modules and class names;
- scenario and config layout inside `projects/h2epr/`;
- runtime adapters and orchestration;
- compiler internals;
- Agent Definition sections and wording;
- derived binding formats that have no external consumer;
- test organization and developer tooling;
- repository-local packaging.

Compatible changes update the current files. They do not create public
versions named after audit rounds or development attempts.

## When a new contract version is required

A successor contract is needed when a supported consumer would observe a
change in meaning, required fields, identity, validation behavior or
serialization.

Examples include:

- changing a V1 schema in a way that rejects valid existing data;
- changing a hash preimage or canonical JSON rule;
- changing the meaning of an action, disposition or trace record;
- changing seal or replay semantics;
- weakening the construction/runtime/evaluation boundary;
- adding a required first-class carrier that cannot be represented compatibly
  in V1.

A successor should include:

1. the new contract and schema;
2. a migration description;
3. old and new deterministic fixtures;
4. compatibility tests for supported consumers;
5. a clear cutover point.

The current full-Roster carrier review finds that all twelve released semantic
products fit V1 through a consolidated internal mapping profile and Panic of
1907 scenario semantic extension. No concrete carrier loss currently
justifies a successor contract.

## Agent Definition changes

Agent Definitions, the template and the research/authoring/review Skills are
active research assets. The tracked paths contain the current methods and
accepted versions:

```text
agents/agent-definition-template.md
agents/defines/<event>/<participant>.md
agents/bindings/<event>/
skills/historical-evidence-research/
skills/participant-behavior-research/
skills/agent-definition/
skills/agent-definition-review/
```

Update these files in place as the study produces feedback. Before promoting a
Definition change, inspect every binding, implementation, state, trace, test,
and documentation consumer. A mapping may be updated only when it actually
conforms to the new Definition; otherwise retire it or isolate it as an
explicit engineering fixture instead of updating only its hash.

Git history keeps accepted versions. Working drafts, comparisons and rejected
alternatives belong under:

```text
.local-runtime/h2epr-simulation/working/
```

Date-suffixed and `-old` copies are not kept beside the current Definition.
Contract versions and intentionally supported release lines are the exception.

The two current Panic of 1907 reference-pilot Definitions are version `0.2.1`.
Their accepted V1 mapping under `agents/bindings/panic_1907/` now has strict
machine projections and a conservative first conformance slice under
`scenarios/panic_1907/`. NBC, Morgan, TCA, Lincoln, and the trust-company
presidents' committee are accepted `0.1.0` Roster-production Definitions.
Knickerbocker depositors, later-trust depositors, member/correspondent-bank
resource decisions, call-money lenders and broker-borrowers are accepted
`0.1.0` population products. Their hashes are pinned by Roster Definition
release v0.1. The accepted consolidated mapping under
`agents/bindings/panic_1907/consolidated/` covers all twelve products but is
not executable. It does not replace the G3 runtime or establish historical
validity.
The earlier `0.1.0-dev` three-tick unit is retained under
`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/` as a frozen regression
fixture. It is not an editable Definition line and does not claim conformance
with the current files.

## Evidence and run history

Research working files are editable until they are accepted or archived as
evidence. The following assets keep their original bytes once recorded:

- adopted source archives;
- accepted project decisions;
- evidence manifests and checksums;
- formal run manifests;
- sealed traces and replay data;
- release receipts.

Corrections to those records use a small erratum or successor record rather
than overwriting the original.

## Repository placement

The current Python package lives under `projects/h2epr/src/h2epr` and is not
distributed by the root `setup.py`. This placement supports fast project-local
iteration without turning event-specific behavior into MASim defaults.

A move to a root-level package becomes useful when one of the following is
true:

- another repository needs H2EPR as an installable dependency;
- H2EPR needs its own release and dependency cycle;
- repository-local imports repeatedly block reproducible use;
- the framework/event boundary has been demonstrated by more than one
  consumer.

If the package moves, the project keeps one `h2epr` namespace and one contract
source. The old and new locations are not maintained as parallel
implementations.

Before a move, review path-sensitive identities in ConstructionIdentity,
RunManifest, input inventories, seals and published locators. A path that
participates in identity turns relocation into a migration rather than a
simple file move.

## Moving reusable code into MASim

Code belongs in `masim/` when it has:

- a domain-neutral interface;
- no H2EPR event identity or policy;
- clear failure and replay behavior;
- at least one credible consumer beyond a single event-specific use;
- tests that preserve the H2EPR information and authority boundaries.

The phased simulator and event-process primitives are the current examples.
Agent Definitions, evidence ledgers, institutional actions and historical
evaluation remain H2EPR responsibilities.

## Current implementation names

`H2EPRSimulationRunner` and `H2EPRSimulator` identify the accepted G3 canary.
They are useful integration points, not permanent public class names.

The same applies to the current split between `artifacts/`, `policies/`,
`world/`, `bundles/`, `agents/`, `runtime/` and `compiler/`. Responsibilities
should stay clear even if the module layout changes.

Architecture decisions record why the current boundaries were chosen:

- [ADR-0001](decisions/ADR-0001-g1-project-local-incubator.md)
- [ADR-0002](decisions/ADR-0002-g2-artifacts-event-bundle-canary.md)
- [ADR-0003](decisions/ADR-0003-g3-phased-runtime-placement.md)

## Development direction

G1–G4 remain the engineering baseline. Current development proceeds through
small Agent Definition and scenario feedback loops. Rule v2, scientific
simulation, evaluation, LLM/RAG and multi-event work each begin when their
inputs and research purpose are ready.

H2EPR-0616 remains the V1 cross-domain check required before a future
shared-core claim. It does not set the order of the current Agent work.

## Related documents

- [Project guide](../H2EPR.md)
- [Project README](README.md)
- [Architecture](ARCHITECTURE.md)
- [Contracts V1](contracts/v1/README.md)
