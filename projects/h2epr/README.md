# H2EPR benchmark simulation

H2EPR turns a benchmark event into a sealed multi-agent simulation package.
The package fixes the participants, observations, action vocabulary, event
world, logical clock, and authoritative environment shared by every decision
backend.

```text
benchmark event package
├── Rule     deterministic participant baseline        implemented
├── LLM      direct model-decision baseline             planned
└── RuleLLM  model decisions under declared constraints planned
```

Rule is implemented for three events from different domains. LLM and RuleLLM
remain unavailable and fail closed; the repository makes no result claim for
either backend.

## Current baseline

Construction reads exactly `event_spec.json`, `frozen_evidence.json`, and the
fully exposed `draft_epg.json` for each event. It does not use external
research, Reference EPG, held-out material, or evaluation-only inputs.

| Event | Active units | Coordinates | Trace records | Generated EPG | Evidence |
|---|---:|---:|---:|---:|---|
| H2EPR-0288 Panic of 1907 | 12 | 15 | 813 | 851 nodes / 2,074 edges | [Rule release](releases/panic_1907/rule/) |
| H2EPR-0616 SingHealth Data Breach | 8 | 11 | 438 | 466 nodes / 1,131 edges | [Rule release](releases/singhealth_data_breach/rule/) |
| H2EPR-0481 Galaxy Note7 Recall | 8 | 19 | 729 | 772 nodes / 1,872 edges | [Rule release](releases/samsung_note7_battery_recall/rule/) |

The three events use one compiler, package loader, Rule backend, declarative
environment, named-barrier runtime, MASim event-process kernel, replay path,
Generated EPG compiler, publisher, and conformance implementation. Event
vocabulary stays in admitted event assets rather than common Python.

Each current release records two byte-identical materializations, an
identity-perturbation run with the same trajectory semantics, exact replay,
complete trace-to-graph coverage, and zero unresolved transport. The shared
[cross-event receipt](releases/cross-event/rule/) verifies that the same
contract closes across all three packages.

These results establish dataset-conditioned engineering and method closure.
They do not establish historical fit, parameter calibration, held-out
performance, policy effects, causality, scientific validity, or universal
generality.

## Construction and execution path

```text
three admitted dataset files
  → Source Profile
  → roster and actor map
  → Agent Definitions / Population Models
  → participant interface registries
  → Scenario Definition and Scenario Mechanism
  → shared configuration
  → backend configuration and realization
  → backend-neutral event package plus binding
  → participant decisions
  → authoritative environment and MASim reducer
  → hash-chained trace, seals, and replay
  → trace-derived Generated EPG
  → compact release and simulation-only reading
```

The tracked tree exposes one current path for each responsibility. Machine
documents retain explicit schema, artifact, and content identities so that
admission and replay remain falsifiable; development generations and local
construction history are not parallel publication surfaces.

## Repository map

| Path | Responsibility |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layer ownership and execution boundaries |
| [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md) | Input exposure, comparison, and claim rules |
| [WORKFLOW.md](WORKFLOW.md) | Maintained event-to-release procedure |
| [PUBLICATION_STANDARD.md](PUBLICATION_STANDARD.md) | Documentation, identity, release, and Git quality |
| [EXPERIMENT_STANDARD.md](EXPERIMENT_STANDARD.md) | Future run-matrix admission and comparison parity |
| [agents/](agents/) | Named decision units, rosters, and participant registries |
| [populations/](populations/) | Aggregate choice-unit models |
| [scenarios/](scenarios/) | Event-world, institution, authority, and transition semantics |
| [configs/](configs/) | Shared selections and backend-specific decision settings |
| [execution/](execution/) | Backend realizations and implementation identities |
| [events/](events/) | Source Profiles, assemblies, and compiled event packages |
| [events/current-events.json](events/current-events.json) | Machine registry for complete current events |
| [backends/](backends/) | Backend availability and ownership |
| [schemas/](schemas/) | Current machine-contract catalog |
| [src/h2epr/](src/h2epr/) | Admission, compilation, execution, replay, graph, and publication code |
| [releases/](releases/) | Compact reproducibility evidence |
| [reports/](reports/) | Full-output simulation readings |
| [experiments/](experiments/) | Admitted future comparison plans |
| [templates/](templates/) | Current authoring surfaces |
| [skills/](skills/) | Build, review, execution, and verification procedures |
| [tests/](tests/) | Dependency-light contract and end-to-end validation |

Large run outputs remain in the ignored
`.local-runtime/h2epr-simulation/runs/` custody tree.

## Validate or reproduce one Rule event

From the repository root:

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli validate-package \
  --data-root data/h2epr \
  --package projects/h2epr/events/panic_1907/package \
  --backend rule

PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli materialize \
  --data-root data/h2epr \
  --package projects/h2epr/events/panic_1907/package \
  --backend rule \
  --seed 0 \
  --custody-locator .local-runtime/h2epr-simulation/runs/benchmark/panic_1907/rule/reproduction \
  --output .local-runtime/h2epr-simulation/runs/benchmark/panic_1907/rule/reproduction
```

Run the maintained suite without pytest:

```bash
PYTHONPATH=projects/h2epr/src python -B -m unittest discover \
  -s projects/h2epr/tests -t projects/h2epr/tests -p 'test_*.py' -v
```

Use [NEW_EVENT_PLAYBOOK.md](NEW_EVENT_PLAYBOOK.md) to add another event. For a
multi-seed or multi-backend matrix, admit a plan under [experiments/](experiments/)
before execution. Plan admission exists; a generic matrix executor and the two
model backends do not yet exist.
