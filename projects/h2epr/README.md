# H2EPR benchmark simulation

H2EPR turns one benchmark event into an auditable multi-agent simulation
package. The package fixes the participant universe, observations, action
vocabulary, event world, logical clock, and authoritative environment shared
by every decision backend.

```text
benchmark event package
├── Rule     deterministic participant baseline         implemented
├── LLM      direct model-decision baseline              planned
└── RuleLLM  model decisions under declared constraints  planned
```

The framework is event-neutral. Event IDs, actor names, state fields,
mechanisms, routes, timelines, and policies belong to declarative event
assets, never to common Python. The machine authority for published events is
[events/current-events.json](events/current-events.json); only rows in that
registry are current results.

The current publication registry contains six completed Rule events:
[H2EPR-0196 East Palestine Train Derailment](events/east_palestine_train_derailment/),
[H2EPR-0551 Angola Yellow Fever Outbreak of
2016](events/angola_yellow_fever_outbreak/),
[H2EPR-1031 Baoneng–Vanke Takeover Battle](events/baoneng_vanke_takeover_battle/),
[H2EPR-0481 Samsung Galaxy Note7 Battery Recall Crisis](events/samsung_galaxy_note7_battery_recall_crisis/),
[H2EPR-0616 SingHealth Data Breach](events/singhealth_data_breach/), and
[H2EPR-0288 Panic of 1907](events/panic_of_1907/). Their
[cross-event release](releases/cross-event/rule/) verifies the shared package,
runtime, output, replay, graph, transport, and claim-boundary contracts.

## Method boundary

Construction admits exactly three files for a selected event:
`event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`. Reference
EPG, held-out material, evaluation-only content, external research, and
network retrieval are excluded from construction.

The maintained Rule path establishes package admission, deterministic
execution, trace integrity, replay, Generated EPG provenance, and compact
release verification. It does not establish historical fit, parameter
calibration, held-out performance, policy effects, causality, scientific
validity, or universal generality.

## End-to-end path

```text
three admitted dataset files
  → Source Profile
  → complete roster and actor map
  → Agent Definitions / Population Models
  → observation, intent, and lifecycle registries
  → Scenario Definition, interface, and mechanism
  → shared configuration
  → backend configuration and realization
  → backend-neutral package plus explicit binding
  → participant decisions
  → authoritative environment and MASim reducer
  → hash-chained trace, tick/run seals, and replay
  → trace-derived Generated EPG
  → compact release and simulation-only reading
```

Each arrow is an ownership boundary. A later layer may select or project an
accepted parent; it may not silently repair or redefine it.

## Repository map

| Path | Responsibility |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Runtime layers and authority boundaries |
| [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md) | Input exposure, comparison, and claim rules |
| [WORKFLOW.md](WORKFLOW.md) | Maintained event-to-release sequence |
| [PUBLICATION_STANDARD.md](PUBLICATION_STANDARD.md) | Evidence, identity, documentation, and Git quality |
| [EVOLUTION.md](EVOLUTION.md) | Replacement, correction, and current-version policy |
| [EXPERIMENT_STANDARD.md](EXPERIMENT_STANDARD.md) | Optional run-matrix admission |
| [docs/](docs/) | Contributor guides and artifact reference |
| [agents/](agents/) | Named units, source rosters, actor maps, and interfaces |
| [populations/](populations/) | Aggregate choice-unit models |
| [scenarios/](scenarios/) | Event-world, authority, transition, and termination semantics |
| [configs/](configs/) | Shared and backend-specific selected values |
| [execution/](execution/) | Backend realizations and implementation identities |
| [events/](events/) | Source Profiles, assemblies, packages, and current registry |
| [backends/](backends/) | Shared decision contract and backend availability |
| [schemas/](schemas/) | Current machine-contract catalog |
| [templates/](templates/) | Maintained authoring surfaces |
| [skills/](skills/) | Task-oriented build and review procedures |
| [src/h2epr/](src/h2epr/) | Admission, compilation, runtime, replay, graph, and publication |
| [tests/](tests/) | Synthetic contracts, negative boundaries, and current-event checks |
| [releases/](releases/) | Compact verified run evidence |
| [reports/](reports/) | Generated-process readings |
| [experiments/](experiments/) | Admitted comparison plans and closeouts |

Large materializations and development records remain below ignored
`.local-runtime/h2epr-simulation/`. They are not an alternate publication
surface.

## Start here

For a new event, read [NEW_EVENT_PLAYBOOK.md](NEW_EVENT_PLAYBOOK.md), then
[docs/EVENT_AUTHORING_GUIDE.md](docs/EVENT_AUTHORING_GUIDE.md). Use the Skills
linked by those documents at the point where their product is owned.

Run the dependency-light suite from the repository root:

```bash
PYTHONPATH=projects/h2epr/src python -B -m unittest discover \
  -s projects/h2epr/tests -t projects/h2epr/tests -p 'test_*.py' -v
```

Inspect command contracts without writing output:

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli --help
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli validate-registry
```

Commands that build, materialize, or publish require explicit output paths and
refuse to overwrite existing custody or release roots.
