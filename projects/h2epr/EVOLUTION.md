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
boundary must be decided by a Phase-1 ADR rather than inferred from provisional
documentation.

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

Phase-0 validation proves only the accepted contract surface. It does not
authorize Phase 1, run a simulator, or establish a scientific fidelity claim.
