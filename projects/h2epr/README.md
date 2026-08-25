# H2EPR

H2EPR provides research and software components for auditable simulation of
real event processes. It turns bounded evidence and participant models into
explicit scenario inputs, records deterministic interaction traces, and
compiles validated traces into generated event process graphs.

H2EPR uses MASim for general multi-agent infrastructure but is packaged and
tested as a separate project. Event evidence, participant behavior,
institutional rules, and generated-process semantics remain H2EPR concerns.

## Components

| Component | Location | Responsibility |
|---|---|---|
| Contracts | `contracts/v1/` | Stable construction, runtime, trace, seal, and graph interfaces |
| Construction | `src/h2epr/construction/` | Explicit source loading and typed construction records |
| Artifacts and bundles | `src/h2epr/artifacts/`, `src/h2epr/bundles/` | Participant artifacts, provenance, and validated runtime bundles |
| Policies and world | `src/h2epr/policies/`, `src/h2epr/world/` | Declarative policy inputs and normalized world calculations |
| Runtime and compiler | `src/h2epr/runtime/`, `src/h2epr/compiler/` | Deterministic execution, sealed traces, replay, and graph compilation |
| Agent research | `agents/` | Definitions, rosters, interface accounts, mappings, and bindings |
| Population research | `populations/` | Heterogeneous participant models and interface reviews |
| Event coordination | `events/` | One lightweight Build Brief and cross-directory index per event |
| Event scenarios | `scenarios/`, `src/h2epr/scenarios/` | Semantic releases and their bounded implementation modules |
| Configurations | `configs/`, `src/h2epr/configuration/` | Declared-purpose configurations and fail-closed admission |
| Tests | `tests/` | Contract, boundary, runtime, compiler, and conformance checks |

Importable Python code is contained in `src/h2epr`. The `scenarios` directory
holds reviewed semantic assets rather than a second Python package.

## First event baseline

The Panic of 1907 assets exercise the complete event-modeling handoff at a
bounded scale:

- seven institutional Agent Definitions and five population models;
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

## Second event construction

The SingHealth Data Breach collection has reached the corresponding semantic
design boundary: seven Agent Definitions, two Population Models, a fixed
[Roster Definition release](releases/singhealth_data_breach/roster-definition-v0.1/),
an accepted
[consolidated mapping](agents/bindings/singhealth_data_breach/consolidated/),
and an accepted
[Event Scenario Definition](scenarios/singhealth_data_breach/definition-v0.1/),
followed by an accepted non-executable
[Scenario Configuration](configs/singhealth_data_breach/scenario-configuration-v0.1/).
These assets close the complete participant interface and one declared-purpose
semantic assembly while remaining qualitative and non-executable. Admission,
binding, runtime, simulation, calibration, and evaluation require later
bounded stages.

## Package layout

```text
projects/h2epr/
├── agents/
├── configs/
├── contracts/v1/
├── decisions/
├── events/
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

The current baseline stops before full-roster runtime integration, calibration,
historical fitting, held-out evaluation, and scientific claims. Extending one
of those surfaces requires a separate research purpose and review.

## Documentation

- [Project guide](../H2EPR.md)
- [Event modeling workflow](WORKFLOW.md)
- [Event coordination entries](events/README.md)
- [Event Build Brief template](event-build-brief-template.md)
- [Phase closeout checklist](phase-closeout-checklist.md)
- [Publication-facing research standard](PUBLICATION_STANDARD.md)
- [Architecture](ARCHITECTURE.md)
- [Evolution and compatibility](EVOLUTION.md)
- [Agent guide](agents/README.md)
- [Contracts V1](contracts/v1/README.md)
