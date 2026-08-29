# Repository and experiment layout

The repository separates reusable MASim code, H2EPR research assets, frozen
inputs, generated workspaces, and curated outputs:

```text
masim/                    reusable framework and event-process primitives
examples/                 standard MASim scenario implementations
configs/                  standard MASim run configurations
projects/h2epr/           H2EPR contracts, research assets, package, and tests
data/h2epr/               frozen read-only development fixtures
EXPERIMENT/H2EPR/         generated run workspaces
simulation-results/H2EPR/ curated release artifacts
```

Within `projects/h2epr/`, semantic and executable responsibilities are also
separate:

```text
contracts/v1/             stable serialized interfaces
agents/ populations/      participant research and releases
scenarios/ configs/       event semantics and declared-purpose assemblies
src/h2epr/                independently installed Python package
tests/                    contract, boundary, runtime, and conformance checks
```

Research projects may combine contracts, event configurations, compilers, and
evaluation protocols that would not fit one standard example. Event identity,
participant choices, institutional policies, and H2EPR's cross-event execution
layer remain inside H2EPR. `masim/` is the read-only base framework: H2EPR may
reuse its public execution primitives, but does not promote project code back
into that directory.

Evaluation-only reference material must not flow into construction or runtime.
Frozen inputs are never overwritten by generated state, and generated
workspaces are not treated as curated releases. Tracked test fixtures remain
small and synthetic unless a separately reviewed data package records their
provenance and use.

Path changes that affect serialized identities, manifests, or published
locators are migrations. Other internal package movement is compatible when it
preserves the V1 interfaces and leaves one authoritative implementation.

This layout defines ownership; it does not by itself authorize an event run or
establish runtime, historical, or scientific validity.
