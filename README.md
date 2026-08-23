# MASim: Multiagent Simulation Framework

MASim is a research framework for building auditable multi-agent simulations.
It provides reusable player/persona lifecycles, topology-aware communication,
simulation runners, persistence, and analysis support for financial-market and
broader computational-social-science scenarios.

## Getting started

1. Read [the development-environment guide](docs/development-environment.md)
   and install the environment appropriate to your task.
2. Review [the repository structure](docs/structure.md),
   [framework contract](docs/framework-contract.md), and
   [simulation guide](docs/run-simulation.md).
3. Explore the standard scenarios in [`examples/`](examples/) and their
   matching configurations in [`configs/`](configs/). Each scenario runner
   documents its exact command; deterministic `Rule` variants do not require
   a model API.

The full MASim runtime also requires the separately sourced `lmbase`
dependency described in `requirements.txt`. Contract-only work can use a
smaller validation environment.

## Repository map

- `masim/`: reusable framework, agents, runners, communication, storage, and
  evaluation components.
- `examples/` and `configs/`: standard MASim scenario implementations and run
  configurations.
- `projects/`: cross-scenario research projects with their own explicit
  contracts and development boundaries.
- `docs/`: architecture, configuration, scenario, and workflow guidance.
- `EXPERIMENT/` and `simulation-results/`: local run output and curated result
  packages; neither is source input.

## H2EPR research project

[`projects/h2epr/`](projects/h2epr/) is a repository-local research surface for
draft-EPG-driven participant simulation and the current single authority root
for H2EPR-owned contracts, Agent/Scenario semantics, runtime adapters and
compiler responsibilities. Its G1–G4 engineering chain reaches deterministic
Rule execution, sealed trace/replay and Generated EPG compilation. The first
standardized event cycle, H2EPR-0288, now also reaches an accepted Scenario
Configuration, fail-closed static admission, a bounded KT--NBC--NYCH binding,
and focused E7 conformance/trace/replay closeout. These remain engineering and
method baselines: neither line establishes historical fidelity or scientific
readiness, and the accepted full configuration is not an executable event.

Start with the repository-level
[H2EPR project guide](projects/H2EPR.md), then use the
[project README](projects/h2epr/README.md) for implementation details and the
[event modeling workflow](projects/h2epr/WORKFLOW.md) for stage gates, stopping
boundaries and the current event position.
