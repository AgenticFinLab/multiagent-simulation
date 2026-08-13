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

## Authority flow

Agents emit intentions. The environment validates and adjudicates them. Only
the authoritative world reducer may commit state changes. Communication is a
transport process with append-only attempts and dispositions. The trace records
both accepted effects and rejected, delayed, duplicate, failed, prohibited, or
expired attempts. A deterministic compiler consumes only eligible sealed trace
records.
