# H2EPR project guide

H2EPR is a research project for building auditable multi-agent models of real
event processes. It keeps event evidence, participant semantics, scenario
rules, runtime records, and generated process graphs connected through explicit
interfaces and provenance.

The project is developed under [`projects/h2epr/`](h2epr/). MASim supplies
general multi-agent execution infrastructure; H2EPR owns the event-specific
research and interpretation.

## Engineering flow

```text
bounded sources and evidence
  -> participant and population definitions
  -> event scenario and configuration
  -> admitted, explicitly bound runtime inputs
  -> deterministic trace, seals, and replay
  -> generated event process graph
```

The boundaries in this flow are deliberate. A configuration is not executable
until it passes admission and has an explicit carrier and policy binding.
Agent outputs describe intents; the environment adjudicates outcomes; the
reducer alone commits authoritative state. Scientific evaluation is a separate
activity performed only when an experiment is specifically authorized.

## Repository boundary

| Location | Responsibility |
|---|---|
| `projects/h2epr/contracts/` | Stable serialized interfaces and JSON Schemas |
| `projects/h2epr/agents/` | Participant definitions, rosters, reviews, and bindings |
| `projects/h2epr/populations/` | Event-bound heterogeneous population models |
| `projects/h2epr/scenarios/` | Scenario semantics and versioned event releases |
| `projects/h2epr/configs/` | Declared-purpose configurations and admission records |
| `projects/h2epr/src/h2epr/` | Installable construction, runtime, and compiler code |
| `projects/h2epr/tests/` | Contract, boundary, runtime, and conformance tests |
| `data/h2epr/` | Versioned source and development input packages |

Domain-neutral event-process primitives live in
`masim.integrations.event_process`. Event identities, historical assumptions,
institutional policies, and interpretation remain inside H2EPR.

## First event baseline

The Panic of 1907 assets provide the first complete standardization baseline.
They include:

- seven institutional Agent Definitions and five population models;
- a hash-pinned roster release and consolidated semantic mapping;
- an Event Scenario Definition and a non-executable Scenario Configuration;
- fail-closed static configuration admission; and
- a bounded Knickerbocker Trust--National Bank of Commerce--New York Clearing
  House binding with deterministic conformance, trace, and replay evidence.

This baseline tests the repository interfaces and modeling method. It is not a
full-event simulation, a calibrated historical reconstruction, or a claim of
scientific validity. Broader runtime integration or evaluation requires a
separate research question and authorization. The next normal method check is
to apply the same workflow to another event.

## Reading order

1. [Project README](h2epr/README.md) for installation, layout, and validation.
2. [Event modeling workflow](h2epr/WORKFLOW.md) for artifact handoffs and
   stopping boundaries.
3. [Architecture](h2epr/ARCHITECTURE.md) for responsibility and information
   boundaries.
4. [Evolution policy](h2epr/EVOLUTION.md) for compatibility and release rules.
5. [Contracts V1](h2epr/contracts/v1/README.md) for machine-readable
   interfaces.
