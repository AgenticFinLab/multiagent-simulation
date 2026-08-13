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

[`projects/h2epr/`](projects/h2epr/) contains the repository-only Phase-0
contract and synthetic validation surface for draft-EPG-driven participant
simulation. It does not yet contain a runnable H2EPR simulator or claim
scientific readiness. Its stable V1 contract, evolution policy, and strict
Reference-information boundary are documented within that project root.
