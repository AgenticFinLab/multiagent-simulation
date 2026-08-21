# H2EPR

H2EPR is a repository-local research project for auditable simulation of real
event processes. It builds participant Agents from bounded evidence, records
their interaction as a sealed trace and compiles the generated process into an
EPG.

For the repository-level overview and the relationship with MASim, see the
[H2EPR project guide](../H2EPR.md).

## Current focus

The Knickerbocker Trust–New York Clearing House work is the completed reference
pilot for Panic of 1907 Agent Definitions. Its `0.2.1` Definitions have an
accepted V1 mapping, machine-readable intent and lifecycle registries,
fail-closed carrier checks, and a deterministic non-Ray request-to-feedback
conformance slice. The earlier `0.1.0-dev` fixture remains frozen as an
engineering baseline.

National Bank of Commerce is the third accepted scholarly Definition. The
first Roster-production batch has also resolved Knickerbocker depositors as an
event-bound population model rather than a collective Agent or an entirely
external demand path. The project is completing the remaining H2EPR-0288
roster in small production batches. Each batch stops at a lightweight
event-interface preflight; consolidated mapping waits for the Roster
Definition release.

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
| Agent research | `agents/` | Event roster, institutional behavior Definitions, source register, evidence ledger, decision situations, and derived bindings |
| Population research | `populations/` | Reviewed heterogeneous-participant models and lightweight interface preflights |
| Agent binding support | `src/h2epr/agents/` | Strict Definition mapping, semantic-intent validation and Contracts V1 carrier checks |
| Event conformance slices | `scenarios/` | Event-owned policies, authoritative process state and bounded non-Ray integration paths |

## Repository layout

```text
projects/h2epr/
├── contracts/v1/
├── decisions/
├── configs/panic_1907/
├── agents/
│   ├── README.md
│   ├── agent-definition-template.md
│   ├── defines/panic_1907/
│   ├── rosters/panic_1907.md
│   └── bindings/panic_1907/
├── populations/
│   ├── defines/panic_1907/
│   └── interfaces/panic_1907/
├── skills/
│   ├── event-agent-batch/
│   ├── historical-evidence-research/
│   ├── participant-behavior-research/
│   ├── agent-definition/
│   └── agent-definition-review/
├── scenarios/panic_1907/
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

## Agent Definitions and roster production

The current event assets are under `agents/defines/panic_1907/`:

| File | Purpose |
|---|---|
| `knickerbocker-trust.md` | Knickerbocker role, information, authority and decision commitments |
| `new-york-clearing-house.md` | NYCH governance, eligibility and procedural commitments |
| `national-bank-of-commerce.md` | NBC credit, request-intermediation and clearing-relationship decisions |
| `source-register.md` | Adopted source identities, public locators, hashes, cited passages and limitations |
| `evidence-ledger.md` | Claim status, participant availability, exposure and unresolved questions |
| `decision-situations.md` | Shared role-comparison situations and falsification perturbations |

The reference Definitions provide four Knickerbocker and five NYCH Decision
Commitments. They cover information and authorization work, request/case
lifecycle, route and facility classification, conditional proposals,
communication, results, uncertainty and falsification. The member-facility
restriction is common to both NYCH structures; the conservative baseline uses
no evidenced competent alternative route, while bounded alternative-route
discretion is retained only for structural sensitivity.

The accepted mapping under `agents/bindings/panic_1907/` pins the two
Definition hashes, seven business lifecycles, 21 semantic intents, and 21
cross-object conformance rules to Contracts V1. Its machine projections reject
stale hashes, undeclared parameters, carrier drift, illegal lifecycle changes,
and action/message mismatches.

The conservative first slice under `scenarios/panic_1907/` exercises eight
decisions across request formation, case classification, information exchange,
review, a facility-scoped decline, delivery, and Knickerbocker's subsequent
contingency preparation. All 21 intents are registered and validated, but the
remaining intent policies are not implemented by this slice. It does not start
Ray or the G3/G4 simulation path and makes no historical-validity claim.

The NBC `0.1.0` Definition is the third accepted scholarly role model. It is
not part of the two-role binding, intent registry, or implementation slice. Its
mapping is deferred to the consolidated Roster Definition release.

The accepted [Knickerbocker depositor population model](populations/defines/panic_1907/knickerbocker-depositors.md)
is the first Roster-production product with a non-Agent representation. It
preserves heterogeneous withdrawal and retention choices, pending-request
discipline, and delivered-result response. Population composition and response
profiles remain uncalibrated sensitivity inputs. Its
[interface preflight](populations/interfaces/panic_1907/knickerbocker-depositors.md)
found no concrete Contracts V1 counterexample and deliberately created no
mapping or implementation.

The accepted [research roster](agents/rosters/panic_1907.md) fixes the v0.1
question, horizon, causal ownership, and role dispositions. The non-executable
[event semantic skeleton](scenarios/panic_1907/semantic-skeleton.md) aligns
shared concepts and interaction routes while new role products are developed.

The earlier three-tick path is frozen under
`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`; it exercises
Definition hashes, observation allowlists, request state, intent/result
separation, deterministic trace and replay only for the old `0.1.0-dev`
fixture.

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

Contracts and the frozen Agent engineering baseline run offline and do not
start Ray:

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
The current Agent work has reached an accepted three-role Definition set; two
roles have an accepted semantic binding and a tested first implementation
slice. Roster v0.2 and the event semantic skeleton now govern the remaining
Definition batches. The slice is not yet integrated into the G3/G4 runtime,
and it does not establish historical or scientific validity. Scientific
evaluation remains a later post-seal activity.

H2EPR-0616 SingHealth is retained by Contracts V1 as the cross-domain check
required before a future shared-core claim. It is not scheduled as the next
development task.

## Further reading

- [Research projects index](../README.md)
- [Project guide](../H2EPR.md)
- [Architecture](ARCHITECTURE.md)
- [Evolution policy](EVOLUTION.md)
- [Agent guide](agents/README.md)
- [Agent development workflow](agents/WORKFLOW.md)
- [Panic of 1907 research roster](agents/rosters/panic_1907.md)
- [Panic of 1907 semantic skeleton](scenarios/panic_1907/semantic-skeleton.md)
- [Contracts V1](contracts/v1/README.md)
- [Architecture decisions](decisions/)
