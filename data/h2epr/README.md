# H2EPR Integration Data

This directory contains small, versioned fixtures for developing the H2EPR
event-simulation integration. It is not the complete H2EPR-Bench release and
must not become a second authoritative copy of Unified-3000.

## Boundary

- `development_samples_v1/` contains eight cross-domain events selected from
  authentic FinMycelium `FinalEventCascade` outputs.
- Frozen upstream files are copied byte-for-byte and are never edited in this
  repository.
- `draft_epg.json` is the process seed available to scenario construction.
- `reference_epg.json` is evaluation-only. It must never be included in an
  agent prompt, observation, memory, retrieval index, or simulation state.
- `projects/h2epr/` owns the H2EPR contracts, research assets, configurations,
  event scenarios, Python package, and tests.
- `examples/{Scenario}/` and top-level `configs/{Scenario}/` remain the
  standard MASim convention and do not contain a second H2EPR assembly.
- No layout decision may weaken frozen-input/generated-output separation,
  evaluation-only Reference isolation, or the accepted V1 trace and seal
  behavior. The public evolution policy is `projects/h2epr/EVOLUTION.md`.

## Intended Full-Scale Contract

The sample layout is deliberately event-local so the same contract can later
be materialized outside Git for any subset of Unified-3000:

```text
events/H2EPR-XXXX/
  event_spec.json
  frozen_evidence.json
  draft_epg.json
  reference_epg.json
```

Large-scale exports, simulation outputs, provider credentials, caches, and
runtime logs must remain outside this tracked fixture directory.
