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

[`projects/h2epr/`](projects/h2epr/) is an independently packaged research
project for auditable event-process simulation. It owns its contracts,
participant and scenario semantics, configuration admission, runtime adapters,
and graph compiler. The Panic of 1907 and SingHealth Data Breach assets now
provide two deterministic full-roster Rule executions, authoritative replay,
generated event graphs, and a shared cross-event closure baseline. These are
uncalibrated mechanism-coverage models, not historical-validity claims.

Start with the repository-level
[H2EPR project guide](projects/H2EPR.md), then use the
[project README](projects/h2epr/README.md) for installation and validation, or
the [event index](projects/h2epr/events/README.md) for the research-facing and
reproducibility paths through each baseline. The
[event modeling workflow](projects/h2epr/WORKFLOW.md) defines artifact handoffs
and stopping boundaries; the
[cross-event conformance release](projects/h2epr/execution/cross-event-conformance-v0.1/)
summarizes the two completed execution paths.
