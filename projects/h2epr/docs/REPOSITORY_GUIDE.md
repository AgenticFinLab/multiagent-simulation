# Repository guide

## Scope

H2EPR is a project-local simulation framework layered on MASim. It admits a
bounded H2EPR benchmark event, expresses participant and world semantics as
reviewable assets, attaches a decision backend, executes through an
authoritative reducer, and publishes replayable generated-process evidence.

The tracked tree is a publication surface. It contains standards, current
contracts, current event assets, tests, and compact evidence. Raw runs,
construction notes, supervisor reviews, migration maps, and replaced local
experiments stay under ignored `.local-runtime/h2epr-simulation/` or in Git
history.

## Responsibility tree

```text
projects/h2epr/
├── standards and guides          method, lifecycle, publication
├── schemas/                      machine shape
├── templates/                    human authoring surfaces
├── skills/                       task-time procedures
├── agents/ and populations/      participant semantics
├── scenarios/                    world and environment semantics
├── configs/                      selected executable values
├── execution/                    backend projection
├── events/                       source admission, assembly, package
├── src/h2epr/                    generic implementation
├── tests/                        synthetic and current-event proof
├── releases/                     compact verified evidence
├── reports/                      generated-process interpretation
└── experiments/                  optional comparison control plane
```

The dataset remains under `data/h2epr/`. H2EPR does not copy those source
records into the project tree. MASim remains under `masim/` and is changed only
by separately scoped base-framework work.

## Authority and projections

An upstream asset owns meaning; a downstream asset may select, project, or
seal it.

| Owner | Owns | Must not own |
|---|---|---|
| Source Profile | input identity, exposure, prohibitions, claim boundary | participant or mechanism design |
| roster and actor map | complete Draft coverage and representation disposition | behavior or success |
| Definition / Population Model | decision-unit semantics and uncertainty | exact backend values |
| registries | shared observations, intents, lifecycles, capabilities | selected decisions |
| Scenario Definition / Mechanism | world state, authority, effects, routes, termination | backend choice |
| shared configuration | exact backend-neutral selections | model-only or Rule-only controls |
| backend configuration | decision-production settings | world-state authority |
| realization and binding | executable projection and source identity | semantic repair |
| runtime and environment | observation cycle, admission, reduction, transport | historical truth |
| release | independently verified evidence index | raw custody or interpretation |
| report | bounded interpretation of generated output | new runtime facts |

When two artifacts appear to own the same fact, resolve ownership before
adding another field. Duplication without an explicit projection rule creates
drift.

## Currentness and discovery

`events/current-events.json` is the machine authority for current event
results. Its rows pin all reader-facing and machine paths. The registry may be
empty or contain one event; cross-event conformance independently requires at
least two distinct events.

Schema protocol versions and content hashes are validation data. They do not
justify parallel `v0.1`, `v0.2`, or `old` directories. A replacement becomes
the one current path after all descendants are rebuilt and verified. Git
preserves earlier tracked bytes.

## Local and tracked boundaries

Tracked:

- standards, guides, templates, Skills, schemas, and generic code;
- accepted event assets and compiled packages;
- compact release receipts and simulation readings;
- tests that reproduce or falsify published claims.

Ignored local custody:

- full traces, Generated EPG bytes, terminal states, and materialization A/B;
- identity probes, failed attempts, and temporary compilation output;
- build diaries, review notes, historical identity maps, and migration plans.

An ignored file may be required by a compact release. Its locator and inventory
hash then form part of the release, but the file does not become a second
tracked publication surface.

## Failure routing

Correct the layer that owns the failed claim:

| Failure | Owner |
|---|---|
| wrong or unavailable source byte | Source Profile or dataset authority |
| missing Draft participant | roster |
| invented actor behavior | Definition / Population Model |
| unknown observation or intent | registry |
| invalid target, effect, or concurrent write | Scenario Mechanism |
| uncovered selected value | configuration |
| missing implementation or fallback | backend realization |
| trace, seal, transport, or replay failure | runtime / MASim boundary |
| graph coverage mismatch | Generated EPG compiler |
| self-consistent but forged receipt | publication verifier |
| unsupported interpretation | report or evaluation protocol |

A failure in a later layer does not authorize changing an accepted parent to
make the run pass.

## Verification levels

1. JSON/schema and text hygiene.
2. Cross-file semantic and identity closure.
3. Synthetic positive and negative contract tests.
4. Current-event compilation and runtime checks.
5. Fresh A/B, identity perturbation, replay, graph, and publication checks.
6. Optional cross-event or experiment evidence.

The synthetic fixtures are deliberately nonhistorical and use two different
vocabularies. They prove that common code is not tied to a published event;
they do not validate the semantic quality of a real event package.
