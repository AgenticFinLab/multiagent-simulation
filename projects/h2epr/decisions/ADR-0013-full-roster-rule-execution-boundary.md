# ADR-0013: adopt the full-roster Rule-execution boundary

- Status: accepted
- Date: 29 August 2026
- Scope: H2EPR-0288 and H2EPR-0616 deterministic Rule execution and generated EPG closure
- Resolved decisions: OD-EXE-01 through OD-EXE-06

## Context

Panic of 1907 and the SingHealth Data Breach each have an accepted semantic
roster, consolidated mapping, Event Scenario Definition, non-executable
Scenario Configuration, static admission, and one bounded lineage-conformance
case. Those assets establish semantic and carrier compatibility but do not
supply complete participant policies, a full-roster runtime assembly, or a
simulation-generated event graph.

The existing Contracts V1 runtime lineage was designed for an earlier
draft/prefix continuation protocol. Its runtime bundle and run manifest require
construction-state parents and source classifications that do not describe the
two accepted Scenario Configuration releases. Recasting those releases as old
construction bundles would obscure rather than preserve lineage.

MASim already provides useful event-process values, deterministic reduction,
message transport, trace chaining, seals, replay, and phased-runner interfaces.
H2EPR needs a project-owned execution layer that uses those interfaces without
changing the base framework or moving H2EPR policy into it.

## Decision

### `OD-EXE-01` — immutable semantic parents and executable successors

Accepted Definitions, Population Models, mappings, Scenario Definitions,
Scenario Configurations, admissions, bounded bindings, and conformance records
remain unchanged. A full execution is a separately identified successor that
pins its semantic parents and admission evidence by path, stable identity, and
content hash. Earlier bounded bindings and conformance records remain immutable
reference implementations, not implicit full-run parents.

### `OD-EXE-02` — independent Policy Realization

Policy Realization is the only layer that turns reviewed participant and
Scenario semantics into Rule behavior. It must close the exact configured
actor-capability, decision-commitment, intent, selected-policy, lifecycle, and
failure inventories. A valid no-intent decision is represented explicitly; it
names both its blocker and revisit trigger and is not filled by a default
action. Actor-specific profiles and postures resolve through explicit pointers
into the pinned configuration; system-only structural variants are not direct
participant inputs. Environment result logic remains separate from participant
choice.

### `OD-EXE-03` — H2EPR-owned execution architecture

Shared kernel, registry, admission, adapter, runtime, and compiler code remain
under `projects/h2epr/src/h2epr`. Event-owned policies and reducers remain under
their H2EPR scenario modules. `masim/` is read-only: H2EPR consumes existing
public interfaces and adds project-local adapters when a narrower interface is
needed. Cross-event reuse never implies promotion into MASim.

### `OD-EXE-04` — contract evolution

Contracts V1 serialized interfaces and schemas remain unchanged. The
executable successor first uses a project-local H2EPR Rule-execution profile
whose lineage begins at the accepted Scenario Configuration and its semantic
releases. V1 value and carrier semantics are reused where they remain accurate.
A shared Contracts successor is considered only if both complete event
implementations require the same field or invariant and a project-local
profile cannot express it without semantic loss.

### `OD-EXE-05` — run and graph closure

Each event receives one canonical full-roster Rule run and one independent
same-input, same-seed materialization. The runtime bundle, trace, tick and run
seals, replay receipt, and generated EPG must be byte-identical. The run must
also close authoritative replay and produce an EPG whose nodes and edges
resolve to sealed trace records. Focused perturbations are added only for
high-information mechanisms or failure paths; there is no mandatory parameter
grid.

Large materialized outputs remain in an indexed ignored run directory. Git
tracks reproducible code and inputs plus compact manifests, receipts,
checksums, tests, and reader-facing documentation.

### `OD-EXE-06` — order and claim boundary

Panic is implemented first. Only behavior that becomes genuinely shared while
closing Panic is extracted into the H2EPR execution layer. SingHealth then acts
as the second consumer and supplies the cross-event test. The final claim is
limited to deterministic, uncalibrated mechanism-coverage engineering on two
real-event assets. It does not establish historical reconstruction, parameter
fit, policy effectiveness, held-out performance, or scientific validity.

## Consequences

The project gains an end-to-end path without weakening its existing semantic
or authority boundaries. Full coverage is measured against released
inventories rather than file counts or a hand-selected positive branch.
Unsupported semantics fail before execution, and a successful run remains
distinguishable from a historically validated model.

The new execution profile and code are H2EPR assets. The experiment may reveal
that some V1 carriers or existing compiler rules can be reused directly, but
it cannot change MASim or a frozen release as a convenience repair.
