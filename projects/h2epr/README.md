# H2EPR

H2EPR is a repository-local research project for auditable simulation of real
event processes. It builds participant Agents from bounded evidence, records
their interaction as a sealed trace and compiles the generated process into an
EPG.

For the repository-level overview and the relationship with MASim, see the
[H2EPR project guide](../H2EPR.md).

## Current focus

The current research loop is an Agent Definition pilot for the Panic of 1907.
It compares two institutionally different participants:

- Knickerbocker Trust;
- New York Clearing House (NYCH).

Each participant has an event-specific Markdown Definition. A small non-Ray
pilot checks whether those Definitions constrain legal observations,
request lifecycle, procedural authority, intents and response to results.

The earlier G1–G4 work remains the engineering foundation: construction,
participant artifacts, deterministic Rule execution, trace/seal/replay and
Generated EPG compilation.

## Implemented components

| Component | Location | Current role |
|---|---|---|
| Contracts V1 | `contracts/v1/` | Stable construction, runtime, trace, seal and Generated EPG interfaces |
| Construction IR | `src/h2epr/construction/` | Explicit source loading and typed, lossless construction data |
| Participant artifacts | `src/h2epr/artifacts/` | Entity registry, provenance and ParticipantArtifact assembly |
| Event bundles | `src/h2epr/bundles/` | Construction seals, RuntimeScenarioBundle generation and validation |
| Canary policy and world | `src/h2epr/policies/`, `src/h2epr/world/` | Rule policy inputs and normalized sensitivity state |
| Runtime | `src/h2epr/runtime/` | H2EPR adapter, phased Rule runtime, detectors and orchestration |
| Compiler | `src/h2epr/compiler/` | Sealed-trace validation and deterministic EPG/GraphSeal compilation |
| Agent Definitions | `agents/` | Event-specific behavior definitions, evidence ledger and bindings |
| Agent pilot | `src/h2epr/agents/` | Definition enforcement and the current two-role feedback loop |

## Repository layout

```text
projects/h2epr/
├── contracts/v1/
├── decisions/
├── configs/panic_1907/
├── agents/
│   ├── README.md
│   ├── agent-definition-template.md
│   └── defines/panic_1907/
├── skills/
│   └── agent-definition-skill.md
├── src/h2epr/
│   ├── construction/
│   ├── artifacts/
│   ├── policies/
│   ├── world/
│   ├── bundles/
│   ├── agents/
│   ├── runtime/
│   └── compiler/
└── tests/
```

The project is organized by responsibility rather than by audit round. New
directories are added when a real implementation needs them; the tree is not
a permanent package API.

## Agent Definition pilot

The current event assets are under `agents/defines/panic_1907/`:

| File | Purpose |
|---|---|
| `knickerbocker-trust.md` | Knickerbocker role, information, authority and decision commitments |
| `new-york-clearing-house.md` | NYCH governance, eligibility and procedural commitments |
| `evidence-ledger.md` | Adopted claims, source identity, exposure and unresolved questions |
| `micro-situation.md` | Shared October 21 support-request situation |
| `binding-catalog.json` | Derived mapping from Definition hashes to executable commitments |

The three-tick pilot follows one narrow path:

1. Knickerbocker submits a support request.
2. NYCH issues a typed member-facility decline.
3. Knickerbocker receives the result and prepares an operational restriction.

This path exercises Definition hashes, observation allowlists, explicit
unknown values, request state, authority checks, intent/result separation,
deterministic trace and replay.

Two historical questions remain open: NYCH authority over other possible
support routes, and the exact Knickerbocker representatives and corporate
authorization behind the request. The pilot keeps both as bounded unknowns.

## Architecture

```text
evidence
  -> Agent Definition + scenario/environment
  -> ParticipantArtifact / EventBundle
  -> filtered observation
  -> Agent intent or message
  -> environment adjudication
  -> authoritative state update
  -> sealed trace and replay
  -> Generated EPG
```

Agents propose actions; the environment determines admissibility and effects.
Only the reducer commits world state. The runtime records accepted, rejected,
delayed, duplicate, failed and expired attempts.

The full architecture and integration boundaries are described in
[ARCHITECTURE.md](ARCHITECTURE.md).

## Evidence and generated data

- `data/h2epr/` contains frozen input assets.
- `.local-runtime/h2epr-simulation/` contains local working material,
  research history and archived evidence.
- `EXPERIMENT/H2EPR/` is used for generated local run data.
- `simulation-results/H2EPR/` is reserved for separately curated releases.

Construction, runtime and post-seal evaluation use separate information
boundaries. The current Panic of 1907 canary was built after exposure to the
full draft and is classified as an architecture demo. Its outputs support
engineering review rather than historical calibration.

## Packaging

The `h2epr` package is not installed by the root `setup.py`. Run project tests
from the repository root with `projects/h2epr/src` on `PYTHONPATH`:

```bash
PYTHONPATH=projects/h2epr/src python -c "import h2epr"
```

Domain-neutral phased execution and event-process primitives currently live in
`masim/`. Event identity, Agent behavior, scenario policy and compiler logic
remain in H2EPR.

## Tests

Contracts and the Agent pilot run offline and do not start Ray:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=projects/h2epr/src \
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/contracts \
  projects/h2epr/tests/agents
```

Additional suites cover construction, bundles, runtime and compilation:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=projects/h2epr/src \
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/construction \
  projects/h2epr/tests/g2 \
  projects/h2epr/tests/g3 \
  projects/h2epr/tests/g4
```

The G3 suite requires the project runtime environment. See
[tests/README.md](tests/README.md) for details.

## Project status

G1–G4 provide a deterministic engineering chain with recorded limitations.
The current Agent work is the first event-specific semantic iteration and has
not yet been integrated into the G3/G4 path. Scientific evaluation remains a
later post-seal activity.

H2EPR-0616 SingHealth is retained by Contracts V1 as the cross-domain check
required before a future shared-core claim. It is not scheduled as the next
development task.

## Further reading

- [Research projects index](../README.md)
- [Project guide](../H2EPR.md)
- [Architecture](ARCHITECTURE.md)
- [Evolution policy](EVOLUTION.md)
- [Agent guide](agents/README.md)
- [Contracts V1](contracts/v1/README.md)
- [Architecture decisions](decisions/)
