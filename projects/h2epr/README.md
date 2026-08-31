# H2EPR

H2EPR provides research and software components for auditable simulation of
real event processes. It turns bounded evidence and participant models into
explicit scenario inputs, records deterministic interaction traces, and
compiles validated traces into generated event process graphs.

H2EPR uses MASim's public interfaces as a read-only base for general
multi-agent infrastructure but is packaged and tested as a separate project.
Event evidence, participant behavior, institutional rules, shared H2EPR
execution logic, and generated-process semantics remain H2EPR concerns.

## Components

| Component | Location | Responsibility |
|---|---|---|
| Contracts | `contracts/v1/` | Stable construction, runtime, trace, seal, and graph interfaces |
| Construction | `src/h2epr/construction/` | Explicit source loading and typed construction records |
| Artifacts and bundles | `src/h2epr/artifacts/`, `src/h2epr/bundles/` | Participant artifacts, provenance, and validated runtime bundles |
| Policies and world | `src/h2epr/policies/`, `src/h2epr/world/` | Declarative policy inputs and normalized world calculations |
| Runtime and compiler | `src/h2epr/runtime/`, `src/h2epr/compiler/` | Deterministic execution, sealed traces, replay, and graph compilation |
| Shared execution closure | `src/h2epr/execution/` | Event-neutral run documents, closure validation, deterministic comparison, strict release input, and ignored custody |
| Agent research | `agents/` | Definitions, rosters, interface accounts, mappings, and bindings |
| Population research | `populations/` | Heterogeneous participant models and interface reviews |
| Event coordination | `events/` | One lightweight Build Brief and cross-directory index per event |
| Event scenarios | `scenarios/`, `src/h2epr/scenarios/` | Semantic releases, event-qualified implementations, and comparisons that name specific events |
| Configurations | `configs/`, `src/h2epr/configuration/` | Declared-purpose configurations and fail-closed admission |
| Rule execution releases | `execution/` | Policy Realizations, executable successors, runtime-bundle contracts, and compact run/graph records |
| Methods and templates | `skills/` and project templates | Evidence-to-execution authoring methods, proportionate review, and phase closeout |
| Tests | `tests/` | Contract, boundary, runtime, compiler, and conformance checks |

Importable Python code is contained in `src/h2epr`. The `scenarios` directory
holds reviewed semantic assets rather than a second Python package.

## First event baseline

The Panic of 1907 assets exercise the complete event-modeling handoff at a
bounded scale:

- seven Agent Definitions and five population models;
- a fixed roster release and consolidated mapping;
- an [Event Scenario Definition](scenarios/panic_1907/definition-v0.1/);
- a non-executable [Scenario Configuration](configs/panic_1907/scenario-configuration-v0.1/)
  with [static admission](configs/panic_1907/configuration-admission-v0.1/);
- a bounded [KT--NBC--NYCH binding](agents/bindings/panic_1907/kt-nbc-nych-v0.1/);
  and
- focused [lineage conformance](scenarios/panic_1907/lineage-conformance-v0.1/)
  with deterministic trace and replay evidence.

The binding implements only the selected three-role lineage. It does not make
the full configuration executable, supply behavior for every roster member,
or establish historical or scientific validity.

The separately accepted
[full-roster Policy Realization](execution/panic_1907/policy-realization-v0.1/)
now supplies Rule behavior for all twelve participant capabilities, all nine
selected Scenario policies, and all thirteen lifecycle families. Its accepted
[full-roster Rule package](execution/panic_1907/full-roster-rule-v0.1/) binds
those policies to all sixteen actor carriers, the closed runtime input, and
the deterministic MASim component boundary. Its separate
[run and generated-graph release](execution/panic_1907/run-and-graph-v0.1/)
records byte-identical canonical and repeat materializations, authoritative
replay, and a trace-closed generated EPG.

## Second event baseline

The SingHealth Data Breach assets apply the complete bounded handoff to a
healthcare cybersecurity event:

- seven Agent Definitions and two Population Models;
- a fixed
  [Roster Definition release](releases/singhealth_data_breach/roster-definition-v0.1/)
  and accepted
  [consolidated mapping](agents/bindings/singhealth_data_breach/consolidated/);
- an accepted
  [Event Scenario Definition](scenarios/singhealth_data_breach/definition-v0.1/);
- a non-executable
  [Scenario Configuration](configs/singhealth_data_breach/scenario-configuration-v0.1/)
  with
  [bounded static admission](configs/singhealth_data_breach/configuration-admission-v0.1/);
- an exact
  [SCM technical--operations--GCIO binding](agents/bindings/singhealth_data_breach/scm-technical-operations-gcio-v0.1/);
  and
- focused
  [lineage conformance](scenarios/singhealth_data_breach/lineage-conformance-v0.1/)
  with deterministic trace, seal, and replay evidence;
- an accepted
  [full-roster Policy Realization](execution/singhealth_data_breach/policy-realization-v0.1/)
  covering all configured actor placements, selected Scenario policies, and
  lifecycle families;
- an accepted
  [full-roster Rule package](execution/singhealth_data_breach/full-roster-rule-v0.1/)
  binding all thirteen carriers, 74 actor-qualified actions, 41 decision
  rules, eleven lifecycle families, and nine runtime components; and
- an accepted
  [run and generated-graph release](execution/singhealth_data_breach/run-and-graph-v0.1/)
  recording byte-identical materializations, authoritative replay, and a
  trace-closed generated EPG.

## Third event baseline

The Samsung Galaxy Note7 Battery Recall Crisis applies the same bounded
handoff to a product-safety and transport event. Its
[event entry](events/samsung_note7_battery_recall/README.md) links the accepted
evidence, six Agent Definitions, two Population Models, roster, mapping,
Scenario Definition, Scenario Configuration, admission, bounded binding, and
lineage conformance. Separately versioned
[Policy Realization](execution/samsung_note7_battery_recall/policy-realization-v0.1/),
[full-roster Rule package](execution/samsung_note7_battery_recall/full-roster-rule-v0.1/),
and [run and generated-graph release](execution/samsung_note7_battery_recall/run-and-graph-v0.1/)
close its eight carriers, 22 commitments, nine selected policies, twelve
lifecycle families, paired deterministic materializations, authoritative
replay, and trace-derived generated EPG.

The three bounded event baselines use the same stage responsibilities and
release structure while retaining event-specific participants, policies,
identifiers, and causal checks. Each has separately versioned end-to-end Rule
execution, authoritative replay, and generated-graph closure. Calibration and
evaluation remain outside all three baselines.

The accepted
[three-event Rule execution conformance successor](execution/cross-event-conformance-v0.2/)
compares their exact run releases. It verifies one shared document, replay,
and graph-closure contract while preserving event-specific coverage values
and semantics. The accepted [v0.1 release](execution/cross-event-conformance-v0.1/)
remains the immutable two-event record.

## Reading the event baselines

Use the [event coordination index](events/README.md) as the default entry to
the three baselines. Each completed event entry separates two tracked reading
paths without moving or duplicating the underlying assets:

- **Research-facing assets** lead from the event frame and evidence to
  participant models, cross-participant semantics, the Event Scenario
  Definition, and the configuration design.
- **Reproducibility and release records** retain exact roster, mapping,
  admission, binding, conformance, manifest, and checksum identities.

Both paths are part of the formal repository. Ignored source archives, working
notes, and local status records support construction but are not formal event
authorities and must not be required to follow a tracked research claim.

## Package layout

```text
projects/h2epr/
├── agents/
├── configs/
├── contracts/v1/
├── decisions/
├── events/
├── execution/
├── populations/
├── releases/
├── scenarios/
├── skills/
├── src/h2epr/
├── tests/
├── ARCHITECTURE.md
├── EVOLUTION.md
├── PUBLICATION_STANDARD.md
├── WORKFLOW.md
├── event-build-brief-template.md
├── phase-closeout-checklist.md
└── pyproject.toml
```

Research assets are organized by responsibility and event identity. Versioned
release directories contain manifests and local integrity records; upstream
lineage is recorded in manifests rather than copied into package checksums.
Each event has at most one lightweight coordination entry under `events/`;
accepted research and release assets remain in their responsibility-owned
directories rather than being copied into an event package.

## Installation

Install H2EPR from the repository root:

```bash
python -m pip install -e "projects/h2epr[test]"
```

Runtime integration also requires the MASim dependencies described in the
root [`requirements.txt`](../../requirements.txt). Contract, configuration,
and most research-asset checks run without starting a simulator.

## Validation

Run the project suites from the repository root after installation:

```bash
python -B -m pytest -p no:cacheprovider projects/h2epr/tests
```

Individual directories may be used for narrower checks:

```bash
python -B -m pytest -p no:cacheprovider projects/h2epr/tests/contracts
python -B -m pytest -p no:cacheprovider projects/h2epr/tests/configuration
python -B -m pytest -p no:cacheprovider projects/h2epr/tests/execution
python -B -m pytest -p no:cacheprovider projects/h2epr/tests/agents
```

See [the test guide](tests/README.md) for suite-specific dependencies and
commands. Release directories that contain a `SHA256SUMS` file can be checked
with `sha256sum --check SHA256SUMS` from that directory.

## Information and authority boundaries

- Construction reads only explicitly declared sources and records their
  provenance.
- Runtime observations expose only information available to the participant.
- Agents emit intents and messages; the environment owns adjudication and
  results.
- The reducer is the sole authority for state changes.
- Trace and seal validation precede replay and graph compilation.
- Evaluation material is not a runtime or construction input.

The accepted bounded baselines remain distinct from full-roster execution.
The three executable successors and run releases establish deterministic
runtime, replay, and graph closure for their declared mechanism-coverage
profiles. None of the events claims calibration, historical fitting, held-out
evaluation, policy effectiveness, or scientific validity.
The separately governed [Rule-execution layer](execution/) provides the
authorized engineering extension without changing the scope of those earlier
releases.

## Documentation

- [Project guide](../H2EPR.md)
- [Event modeling workflow](WORKFLOW.md)
- [Event coordination entries](events/README.md)
- [Event Build Brief template](event-build-brief-template.md)
- [Phase closeout checklist](phase-closeout-checklist.md)
- [Publication-facing research standard](PUBLICATION_STANDARD.md)
- [Architecture](ARCHITECTURE.md)
- [Rule execution](execution/README.md)
- [Full-roster Rule-execution Skill](skills/full-roster-rule-execution/SKILL.md)
- [Execution-cycle closeout template](execution/execution-cycle-closeout-template.md)
- [Three-event execution conformance](execution/cross-event-conformance-v0.2/)
- [Evolution and compatibility](EVOLUTION.md)
- [Agent guide](agents/README.md)
- [Contracts V1](contracts/v1/README.md)
