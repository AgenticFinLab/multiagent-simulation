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
not compatibility commitments. The required pre-G3 placement review was
completed by ADR-0003 using G1/G2 evidence. A compatible relocation or refactor
through a reviewed successor decision does not create a new V1 contract
version. A change to snapshot meaning or shape does require a new explicit
snapshot version and migration tests.

ADR-0002 applies the same incubation rule to the G2 `artifacts/`, `policies/`,
`world/`, and `bundles/` modules. Their present responsibility split is useful
evidence, not a permanent namespace guarantee. The accepted V1 construction,
participant, and runtime-bundle schemas remain authoritative; canary-specific
assembly, profile values, policy thresholds, file layout, and future packaging
may be replaced through reviewed compatible successors.

The focused placement/readiness review retained event identity, roster,
calibration assumptions and target-specific policy under the H2EPR project,
while extracting only domain-neutral phased runtime, event-process values,
transport, reduction, trace and seal mechanics into MASim. Future movement
must preserve this three-view boundary and requires implementation evidence.

`H2EPRSimulationRunner` and `H2EPRSimulator` are the adopted G3 paired-runner
canary classes, not permanent compatibility commitments. The phased lifecycle,
H2EPR world reducer, trace recorder, G4 compiler and future offline evaluator
remain separate responsibilities even if their eventual module layout changes.

## Repository boundaries

The H2EPR project implementation remains repository-only and is not installed
by `setup.py`; the domain-neutral G3 integration modules under `masim/` are
discovered normally. Its repository-local namespace is organized by
responsibility, not as a permanently fixed G1–G4 package range. Construction,
artifact assembly, runtime and compiler keep their current reviewed ownership,
while an evaluator namespace is added only with separately authorized G5 work.
Runtime, compiler and later evaluator surfaces remain explicit opt-in
imports rather than eager top-level package effects.

Standard MASim scenarios and configurations remain in `examples/` and top-level
`configs/`, while the bounded H2EPR canary configuration stays under
`projects/h2epr/configs/`. A later reviewed decision may revise these locations
without weakening the stable V1 contract or allowing evaluation data to flow
into construction or runtime.

Phase-0 validation proves only the accepted contract surface. The bounded G1
construction and G2 EventBundle layers remain non-runtime. G3 now runs a
deterministic Rule-only architecture canary, but it does not establish strict
continuation eligibility, historical calibration or scientific readiness. G4
now performs an explicit inventory, contract-wrapper and eligibility check on
the immutable G3 scientific files, then deterministically produces a sealed V1
Generated EPG. This remains Reference-blind architecture/demo evidence rather
than a fidelity result. G5 post-seal evaluation and later Gates remain
separately authorized.
