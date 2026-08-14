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

This seam is independent of MASim imports. Runtime integration remains a later
Gate decision.

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
Placement and packaging must be reconsidered before runtime implementation.

## Framework integration target

MASim currently starts standard scenarios through:

```text
scenario entry
  -> masim.simulator.general.run
  -> GeneralSimulationRunner
  -> BaseSimulationRunner lifecycle/preflight
  -> GeneralSimulator
```

One provisional extension shape is an opt-in `H2EPRSimulationRunner` paired
with an `H2EPRSimulator`, following the current MASim runner pattern. In that
option the runner would own MASim lifecycle and tick orchestration while
domain-neutral scheduler, reducer, trace, and compiler responsibilities remain
separate. These names and source locations are candidates, not Phase-0
requirements; a Phase-1 ADR must test them against implementation evidence.
Any accepted design must preserve `GeneralSimulator` defaults and keep generic
participant runtime code out of the finance package.

`BaseSimulationRunner` does not itself supply an H2EPR tick barrier,
authoritative world reducer, stage controller, trace seal, trace-to-EPG
compiler, or offline evaluator. Those remain explicit future capabilities.

## Evolvability boundary

Phase 0 freezes the behavior of `contracts/v1`, not the full project tree.
Scenario assemblies, run configurations, reusable modules, and later tests may
be added under locations selected by reviewed Phase-1 decisions. Existing
`examples/` and top-level `configs/` remain the standard MASim boundary today;
this document does not pre-allocate or reserve a permanent H2EPR alternative.
The project-local G1/G2 package is likewise an incubator, not a permanent
package or runtime placement. Its ownership and packaging must be reconsidered
before G3 using implementation evidence, as specified by ADR-0001 and ADR-0002.

## Authority flow

Agents emit intentions. The environment validates and adjudicates them. Only
the authoritative world reducer may commit state changes. Communication is a
transport process with append-only attempts and dispositions. The trace records
both accepted effects and rejected, delayed, duplicate, failed, prohibited, or
expired attempts. A deterministic compiler consumes only eligible sealed trace
records.
