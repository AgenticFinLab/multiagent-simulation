# H2EPR evolution policy

## Stable now

`contracts/v1/` is the stable Phase-0 consumer contract. Compatible
implementations must preserve its construction identities, information
boundaries, communication and trace semantics, seal rules, Generated EPG
shape, and evaluation isolation. Breaking those interfaces requires an
explicit successor contract version and reviewed migration plan.

## Deliberately adjustable

Phase 0 does not freeze the complete `projects/h2epr/` tree. Scenario
assemblies, configurations, internal modules, runtime adapters, test
organization, and operational tooling may change as implementation evidence
arrives. Compatible adjustments do not receive audit-round public version
names. The permanent ownership of reusable runtime code and its packaging
boundary must be decided by reviewed integration evidence rather than inferred
from provisional documentation.

ADR-0001 approves `src/h2epr/construction/` only as a repository-local G1
incubator. Its public responsibility boundary is explicit-manifest construction
and deterministic IR export; private module names and internal class layout are
not compatibility commitments. Before G3, the project must review whether to
retain, package, relocate or split this code using G1/G2 evidence. A compatible
relocation or refactor through a reviewed successor decision does not create a
new V1 contract version. A change to snapshot meaning or shape does require a
new explicit snapshot version and migration tests.

ADR-0002 applies the same incubation rule to the G2 `artifacts/`, `policies/`,
`world/`, and `bundles/` modules. Their present responsibility split is useful
evidence, not a permanent namespace guarantee. The accepted V1 construction,
participant, and runtime-bundle schemas remain authoritative; canary-specific
assembly, profile values, policy thresholds, file layout, and future packaging
may be replaced through reviewed compatible successors.

Before G3, a focused placement/readiness review must decide whether these
modules remain project-local, move behind a reusable integration boundary, or
split between project and framework ownership. That review must preserve the
three-view boundary and may not move event identity, roster, calibration, or
target-specific policy into generic MASim core.

Likewise, `H2EPRSimulationRunner` and `H2EPRSimulator` are useful candidate
names for exploring the current paired-runner pattern, not mandatory classes.
The scheduler, world reducer, trace recorder, compiler, and offline evaluator
remain separate responsibilities even if their eventual module layout changes.

## Repository boundaries

The current project root is repository-only and is not installed by
`setup.py`. Standard MASim scenarios and configurations remain in `examples/`
and top-level `configs/`. A later reviewed decision may choose H2EPR-specific
locations without weakening the stable V1 contract or allowing evaluation data
to flow into construction or runtime.

Phase-0 validation proves only the accepted contract surface. The bounded G1
construction and G2 EventBundle candidates neither run a simulator nor
establish runtime or scientific readiness; later Gate and phase transitions
remain separately authorized.
