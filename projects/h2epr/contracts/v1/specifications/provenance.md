# Contract provenance

This effective V1 synthesizes the accepted Phase-0 construction identity,
runtime lineage, communication closure, tick/run sealing, generated-graph, and
run-global stable-ID semantics into one public surface. Earlier review rounds
remain historical evidence; they are not public schema versions or runtime
compatibility layers.

Content has four derivation classes:

- **semantically retained:** behavior and rejection vectors preserved from the
  sealed validation history;
- **normalized:** stable V1 identifiers, paths, schema names, and fixture names;
- **synthesized:** self-contained project documentation and responsibility
  boundaries; and
- **test-structure refactored:** the former aggregate case surface divided into
  responsibility-owned schema, construction, communication, trace/identity,
  repository, and boundary-regression builders. `case_registry.py` combines
  them without import-time cumulative mutation; `receipt.py` only serializes
  the resulting stable registry. Canonical JSON and offline schema resolution
  remain separate unchanged support modules.

The public suite retains 345 canonical behavior cases: 225 base cases, 53
additional closure cases, 8 communication corrections, 11 run-global identity
cases, and 48 independent/boundary probes. A separate promotion evidence
package maps every legacy case ID to one stable test node and records byte
hashes for the exact public candidate.

Synthetic construction-anchor fixtures are explicitly test-only. No public
file represents them as an approved production root, and no clean-build
projection or scientific simulation run is claimed here.

The earlier public candidate selected `projects/h2epr/` as the stable current
root for the Phase-0 V1 contract and offline tests, and proposed
`projects/h2epr/scenarios/` plus `projects/h2epr/configs/` as default future
assembly locations. This record preserves that derivation history while
clarifying that the two subdirectories are provisional planning defaults, not
reserved paths or consumer compatibility promises. Neither directory exists
in this candidate.

`examples/` and top-level `configs/` remain the current standard MASim
convention, and the present candidate places no H2EPR assembly there. A
reviewed Phase-1 ADR, informed by implementation and tests, may retain, refine,
or replace the proposed locations and decide runtime, package, scenario,
configuration, and future-test ownership. It must prevent duplicate source
ownership and ambiguous run configuration, keep domain-neutral framework
capability separate from event-specific identity and policy, and preserve
frozen-input/generated-output separation, evaluation-only Reference isolation,
and accepted V1 trace/seal semantics.

This clarification follows `projects/h2epr/EVOLUTION.md`. It neither changes
V1 behavior nor creates an audit-round public version, and it does not claim
Phase-1 authorization, a runnable scenario, runtime readiness, or scientific
readiness.
