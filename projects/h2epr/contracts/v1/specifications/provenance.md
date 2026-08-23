# Contract provenance

Contracts V1 combines the accepted construction identity, runtime lineage,
communication closure, tick/run sealing, generated-graph, and run-global
stable-ID semantics in one public interface. Earlier review records remain
historical evidence; they are not public schema versions or compatibility
layers.

Contract content has four derivation classes:

- **semantically retained:** behavior and rejection vectors preserved from
  accepted validation evidence;
- **normalized:** stable V1 identifiers, paths, schema names, and fixture
  names;
- **synthesized:** self-contained documentation and responsibility boundaries;
  and
- **test-structure refactored:** aggregate cases divided among schema,
  construction, communication, trace/identity, repository, and boundary
  regression builders.

Canonical JSON and offline schema resolution remain independent support
surfaces. The case registry combines responsibility-owned builders without
import-time cumulative mutation, and the receipt layer only serializes the
resulting stable registry.

Synthetic construction-anchor fixtures are test-only. They are not approved
production roots and support no clean-build projection, historical fit, or
scientific simulation claim.

`projects/h2epr/` is the authoritative root for H2EPR contracts, semantic
assets, configurations, event code, and tests. Standard MASim scenarios remain
under `examples/` and top-level `configs/`. Domain-neutral framework
capabilities may be shared through `masim/`, but event identity and policy may
not be duplicated there.

The repository boundary preserves frozen-input/generated-output separation,
evaluation-only reference isolation, and V1 trace/seal semantics. Compatible
implementation movement follows `projects/h2epr/EVOLUTION.md`; it does not
create an audit-round version or imply runtime or scientific readiness.
