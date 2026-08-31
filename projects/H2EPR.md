# H2EPR project guide

H2EPR is a research project for building auditable multi-agent models of real
event processes. It keeps event evidence, participant semantics, scenario
rules, runtime records, and generated process graphs connected through explicit
interfaces and provenance.

The project is developed under [`projects/h2epr/`](h2epr/). MASim supplies
general multi-agent execution infrastructure; H2EPR owns event-specific
research and interpretation together with the execution logic shared by its
events.

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
| `projects/h2epr/execution/` | Policy Realizations, executable successors, compact run records, and cross-event conformance |
| `projects/h2epr/skills/` | Evidence-to-execution authoring methods and proportionate review routes |
| `projects/h2epr/src/h2epr/` | Installable construction, runtime, and compiler code |
| `projects/h2epr/tests/` | Contract, boundary, runtime, and conformance tests |
| `data/h2epr/` | Versioned source and development input packages |

Domain-neutral event-process primitives live in
`masim.integrations.event_process`. Event identities, historical assumptions,
institutional policies, and interpretation remain inside H2EPR.

## Cross-event baseline

The current baseline covers three events in different domains. The Panic of
1907 establishes the first complete standardization baseline with seven Agent
Definitions, five population models, and one bounded Knickerbocker
Trust--National Bank of Commerce--New York Clearing House lineage. The
SingHealth Data Breach applies the same handoff to a healthcare cybersecurity
event with seven Agent Definitions, two population models, and one bounded
technical--operations--GCIO lineage. The Samsung Galaxy Note7 Battery Recall
Crisis adds a product-safety and transport event with four Agent Definitions,
four Population Models, and a bounded
Samsung--regional-unit--outlet--consumer remedy lineage.

All three events connect accepted evidence and participant semantics to a
fixed roster, consolidated mapping, Event Scenario Definition, non-executable
Scenario Configuration, and fail-closed static admission. Separately
versioned executable successors then operate each complete configured roster,
produce repeatable sealed traces, replay authoritative state, and compile a
trace-derived generated event graph.

The accepted
[three-event conformance successor](h2epr/execution/cross-event-conformance-v0.2/)
shows that all three event paths close under the same run-document and
verification contract while retaining different participants, policies,
schedules, state, and graph inventories. The accepted v0.1 release remains an
immutable two-event record. This is an uncalibrated engineering result, not a
historical reconstruction, cross-domain validity result, or claim of
scientific validity. Calibration or evaluation requires a separate research
question and scope.

## Reading order

1. [Project README](h2epr/README.md) for installation, layout, and validation.
2. [Event entries](h2epr/events/README.md) for the research-facing path through
   each accepted baseline and the separate reproducibility records.
3. [Three-event execution conformance](h2epr/execution/cross-event-conformance-v0.2/)
   for the compact comparison of the three completed Rule paths.
4. [Event modeling workflow](h2epr/WORKFLOW.md) for artifact handoffs and
   stopping boundaries.
5. [H2EPR Skills](h2epr/skills/README.md) for the specialist methods used by
   each authorized stage, including the optional full-roster execution tail.
6. [Architecture](h2epr/ARCHITECTURE.md) for responsibility and information
   boundaries.
7. [Evolution policy](h2epr/EVOLUTION.md) for compatibility and release rules.
8. [Contracts V1](h2epr/contracts/v1/README.md) for machine-readable
   interfaces.
