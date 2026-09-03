# H2EPR project guide

H2EPR is the repository's benchmark-event simulation project. For each event,
it turns three exposed H2EPR dataset files into an admitted event package, runs
that package through a declared decision backend, and preserves enough evidence
to replay the authoritative state and reconstruct the generated event graph.

The project lives under [`projects/h2epr/`](h2epr/). MASim provides the
domain-neutral event-process transport, reducer, trace, and seal primitives.
H2EPR owns benchmark admission, participant and scenario semantics, backend
bindings, orchestration, publication, and interpretation.

## Current flow

```text
event_spec.json + frozen_evidence.json + draft_epg.json
  -> Source Profile
  -> roster, actor map, Agent Definitions, and Population Models
  -> participant interface and Scenario Mechanism
  -> shared and backend configurations
  -> backend-neutral event package plus explicit backend binding
  -> participant decisions and authoritative environment transitions
  -> hash-chained trace, seals, replay, and Generated EPG
  -> compact run release and simulation-only reading
```

Rule is the implemented deterministic baseline. LLM and RuleLLM are declared
future backends and fail closed. Every backend must use the same event package,
clock, environment, transport, observation boundary, and publication contract;
only participant decision production may differ.

## Repository responsibilities

| Location | Responsibility |
|---|---|
| `data/h2epr/` | The three allowed dataset inputs for each event |
| `projects/h2epr/events/` | Source Profiles, package assemblies, compiled packages, and the current-event registry |
| `projects/h2epr/agents/` | Named choice units, rosters, actor maps, and participant interfaces |
| `projects/h2epr/populations/` | Aggregate heterogeneous choice units |
| `projects/h2epr/scenarios/` | Event-world, institutional, authority, and transition semantics |
| `projects/h2epr/configs/` | Shared selections and backend-specific settings with provenance |
| `projects/h2epr/backends/` | Backend contract and availability catalog |
| `projects/h2epr/execution/` | Backend realizations and implementation identity |
| `projects/h2epr/src/h2epr/` | Admission, compilation, execution, replay, graph, and publication code |
| `projects/h2epr/schemas/` | Current serialized contract catalog |
| `projects/h2epr/releases/` | Compact run and cross-event verification evidence |
| `projects/h2epr/reports/` | Full-output simulation readings |
| `projects/h2epr/templates/` and `skills/` | Maintained authoring and review procedures |
| `projects/h2epr/tests/` | Contract, boundary, execution, and publication validation |

Large materializations remain in the ignored
`.local-runtime/h2epr-simulation/runs/` custody tree. Reference EPG,
held-out, and evaluation-only content is outside construction authority.

## Three-event baseline

The current Rule baseline covers the Panic of 1907, SingHealth Data Breach,
and Samsung Galaxy Note7 Battery Recall Crisis. All three packages use the
same compiler, package loader, backend interface, declarative environment,
runtime, replay path, graph compiler, publisher, and cross-event verifier.
Event vocabulary and policy tables stay in admitted assets rather than common
Python.

The [cross-event release](h2epr/releases/cross-event/rule/) records the common
closure contract. Individual [event entries](h2epr/events/README.md) lead to
each package, run release, and simulation reading.

This baseline establishes dataset-conditioned engineering and method closure.
It does not establish historical fit, calibration, held-out performance,
policy effects, causality, scientific validity, or universal generality.

## Reading order

1. [Project README](h2epr/README.md) for the baseline, commands, and repository map.
2. [New-event playbook](h2epr/NEW_EVENT_PLAYBOOK.md) for the maintained event-building sequence.
3. [Workflow](h2epr/WORKFLOW.md) for handoffs, authority, and failure routing.
4. [Architecture](h2epr/ARCHITECTURE.md) for runtime and information boundaries.
5. [Benchmark protocol](h2epr/BENCHMARK_PROTOCOL.md) for allowed inputs and claim limits.
6. [Publication standard](h2epr/PUBLICATION_STANDARD.md) for identity and release quality.
7. [Event index](h2epr/events/README.md) and [cross-event release](h2epr/releases/cross-event/rule/) for current evidence.
8. [Experiment standard](h2epr/EXPERIMENT_STANDARD.md) only when a comparison plan is authorized.
