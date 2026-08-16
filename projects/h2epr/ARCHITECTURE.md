# Architecture

## Scientific boundary

H2EPR simulation separates three views:

1. **Construction view** produces typed participant, policy, world, scheduler,
   and source-policy artifacts. A full-draft target demo is permanently
   contaminated. A strict build accepts only an approved prefix projection and
   must be performed by a clean builder.
2. **Runtime view** exposes only identity, capabilities, state, delivered
   information, public event progress, and prior trace-derived history. It does
   not expose future real actions or outcomes.
3. **Evaluation view** reads the sealed generated artifacts and the held-out
   real process only after a run. Its data cannot flow back into construction,
   runtime, memory, prompts, retrieval, or world state.

## G1 construction seam

The active G1 candidate is deliberately project-owned and Reference-blind:

```text
explicit SourceDescriptor manifest
  -> normalized path and hash guard
  -> tolerant JSON/CSV decoder
  -> immutable typed Construction IR
  -> minimized evidence/provenance
  -> versioned canonical snapshot export
```

Callers provide both approved roots and explicit descriptors. The adapter does
not walk directories, infer siblings, accept a Reference locator, or discover
schemas from the working directory. Accepted `contracts/v1/` schemas remain the
single contract source and are not duplicated under `src/`.

Architecture-generic parsing is implemented for the authorized non-Reference
development inputs. It preserves raw JSON-compatible values and exact pointers
while adding normalization proposals and bounded diagnostics. It does not
select participants, aggregate entities, define a world, or produce runtime
policy. Synthetic strict-prefix tests validate the closed policy boundary; an
actual clean strict artifact is not produced in G1.

This seam remains independent of MASim imports. G3 consumes its downstream G2
artifacts through a separate project-owned adapter; G1 itself remains
runtime-free.

## G2 artifact and EventBundle seam

The current project-owned G2 candidate remains upstream of runtime execution:

```text
typed Construction IR
  -> entity registry + reversible roster/loss report
  -> one data-driven ParticipantArtifact envelope
  -> declarative Rule skills and policy catalog
  -> normalized profile-specific world
  -> sealed target-demo construction bundle
  -> canonical RuntimeScenarioBundle (EventBundle)
```

Its `artifacts/`, `policies/`, `world/`, and `bundles/` modules are separated by
responsibility. The world helpers are pure calculations; they do not mutate
live state. The EventBundle compiler creates exactly one bundle per sensitivity
profile. Run seeds remain separate future execution inputs, so the nine-row
profile/seed matrix refers to three bundle hashes rather than creating nine
duplicate bundle identities.

The Panic-of-1907 instance is an architecture demo built from an explicit
26-file non-evaluation source profile. Only the two common authorization inputs
and three approved target files enter its source ancestry; the other seven
events are genericity-regression inputs only. Full-draft contamination is
irreversible, the historical post-cutoff scheduler is empty, and all normalized
world values are assumptions rather than historical measurements.

G2 exports declarative shell inputs only. It neither imports nor instantiates a
Player, Persona, Ray actor, runner, simulator, reducer, compiler, or evaluator.
ADR-0003 completed the pre-runtime placement review without changing that G2
boundary.

## G3 framework integration

MASim currently starts standard scenarios through:

```text
scenario entry
  -> masim.simulator.general.run
  -> GeneralSimulationRunner
  -> BaseSimulationRunner lifecycle/preflight
  -> GeneralSimulator
```

G3 adopts an opt-in `H2EPRSimulationRunner` paired with an `H2EPRSimulator`.
The pair preserves the MASim outer lifecycle while using ten explicit phased
barriers for same-prestate participant decisions, authoritative reduction,
delayed-message transport, generated-only detection, trace sealing and replay.
Domain-neutral values and mechanics live in
`masim.integrations.event_process` and `masim.simulator.phased`; fixed H2EPR
policy, world effects, adapters, detectors and orchestration remain under
`projects/h2epr/src/h2epr/runtime`. `GeneralSimulator` and its legacy dispatch
path remain unchanged.

The current runtime is a local CPU/private-loopback Ray Rule canary. It emits a
41-tick hash-chained trace, TickSeals, a RunSeal, deterministic replay and P007
annotations. Runtime remains separate from the downstream G4 compiler and the
future offline evaluator, and it does not establish historical calibration or
scientific validity.

## G4 deterministic compiler seam

The accepted G4 compiler consumes the seven immutable G3 scientific files
through an explicit path/hash inventory. It verifies the record chain, seals
and replay, materializes V1 `RunManifest` and `SimulationTrace` wrappers, and
only then assigns `compiler_evaluator_eligible`. It deterministically detects
and groups generated events into participant, action, outcome, transaction,
episode and stage nodes, closes temporal/causal edges, and seals the resulting
V1 Generated EPG with a GraphSeal. The original G3 bytes and the
`architecture_demo_only` / `full_draft_exposed` scope remain unchanged.

The implementation currently belongs under the project-owned
`h2epr.compiler` responsibility boundary; that private module layout may
evolve if later cross-domain evidence justifies a generic abstraction. The
compiler consumes only the validated trace and generated-only P007 evidence.
It neither imports Reference/evaluation material nor asks an agent to emit a
complete event graph. Its evidence is an architecture/demo canary, not
Reference-based fidelity evaluation or a historical-validity claim. G5 remains
a separately authorized, isolated post-seal evaluation stage.

## Evolvability boundary

Phase 0 freezes the behavior of `contracts/v1`, not the full project tree.
Scenario assemblies, run configurations, reusable modules, and later tests may
be added under locations selected by reviewed Phase-1 decisions. Existing
`examples/` and top-level `configs/` remain the standard MASim boundary today;
this document does not pre-allocate or reserve a permanent H2EPR alternative.
The project-local G1–G4 package remains an incubator rather than a permanent
distribution promise. ADR-0003 records the current generic/project split using
G1/G2 implementation evidence; later compatible refactoring remains allowed
with focused migration tests.

## Authority flow

Agents emit intentions. The environment validates and adjudicates them. Only
the authoritative world reducer may commit state changes. Communication is a
transport process with append-only attempts and dispositions. The trace records
both accepted effects and rejected, delayed, duplicate, failed, prohibited, or
expired attempts. A deterministic compiler consumes only eligible sealed trace
records.
