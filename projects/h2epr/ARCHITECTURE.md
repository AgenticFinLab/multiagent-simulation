# H2EPR architecture

H2EPR turns bounded event evidence into participant artifacts, executes
participant interaction and compiles the resulting trace into a Generated EPG.
This document describes the responsibilities between those stages.

## Design principles

### Separate construction, runtime and evaluation

H2EPR uses three information views:

1. **Construction** prepares participants, policies, world inputs and event
   bundles from the evidence available to the builder.
2. **Runtime** gives each participant only its legal observation and records
   the generated interaction.
3. **Evaluation** compares sealed generated artifacts with held-out event
   material after a run.

Evaluation data does not enter construction, runtime state, prompts, memory or
retrieval. A builder who has seen the target continuation cannot restore a
clean held-out status by rebuilding the same event.

### Keep Agent decisions separate from environment results

Agents emit intents and messages. The environment checks institutional rules,
authority, resources and concurrent state. The authoritative reducer is the
only component that commits state changes.

This keeps the following events distinct:

- an Agent requests an action;
- the request is accepted for processing;
- the action is executed;
- the action has a partial, delayed, failed or zero effect.

### Make every run auditable

Runtime records use logical coordinates and deterministic ordering. Trace
records are hash chained, sealed by tick and sealed again for the full run.
Replay reconstructs state from the same trace before the compiler accepts it.

### Keep event semantics in H2EPR

MASim supplies reusable execution infrastructure. H2EPR owns event evidence,
participant behavior, institutional rules, observation policy, business
results and Generated EPG semantics.

## System flow

```text
explicit source manifest
  -> typed Construction IR
  -> EntityRegistry and ParticipantArtifacts
  -> world inputs and RuntimeScenarioBundle
  -> participant-specific observations
  -> Agent decisions, intents and messages
  -> environment adjudication
  -> authoritative state reduction
  -> trace, tick seals, run seal and replay
  -> Generated EPG and GraphSeal
  -> post-seal evaluation
```

## Construction

### Source loading

`src/h2epr/construction/` receives an explicit list of
`SourceDescriptor` objects and approved roots. The source adapter:

- normalizes and checks paths;
- verifies source hashes;
- reads supported JSON and CSV inputs;
- preserves raw JSON-compatible values and exact source pointers;
- records bounded diagnostics and provenance;
- exports a deterministic Construction IR snapshot.

It does not discover sibling files or walk input directories. Reference and
evaluation locations are rejected by the construction policy.

The current internal snapshot identity is
`h2epr.construction_ir.v1`. Its meaning and serialized shape are versioned
independently from the private Python module layout.

### Artifact and bundle assembly

```text
Construction IR
  -> EntityRegistry
  -> roster and reversible loss report
  -> ParticipantArtifacts
  -> policy and world inputs
  -> construction seal
  -> RuntimeScenarioBundle
```

The artifact layer separates:

- `artifacts/` for entity resolution, participant envelopes and provenance;
- `policies/` for declarative Rule policy inputs;
- `world/` for normalized world values and pure calculations;
- `bundles/` for source profiles, canonical hashes, seals and bundle
  validation.

The Panic of 1907 architecture canary has three sensitivity profiles. Seeds
remain execution inputs rather than part of EventBundle identity, producing a
three-profile by three-seed runtime matrix over three bundle hashes.

Target-specific descendants are marked `full_draft_exposed` and
`architecture_demo_only` because the builder had access to the complete draft.
The normalized world values are sensitivity assumptions rather than historical
measurements.

## Agent and scenario semantics

The current `0.2.1` Agent Definitions specify the behavior layer that will sit
above the existing ParticipantArtifact shell. Their V1 mapping specification
has been accepted under `agents/bindings/panic_1907/`, but it is not yet
executable.

| Responsibility | Owner |
|---|---|
| Role, legal information, decision commitments, intent meaning and limits | Agent Definition Markdown |
| Source identity, locator, adopted scope and file hash | Source register |
| Claim status, event time, availability and use | Evidence ledger |
| Institutions, relationships, observation delivery, authority and results | Scenario/environment |
| Field types, serialization and versioning | Contracts V1 |
| Executable mapping from Definition to code | Binding and backend adapter |
| State transition and action result | Authoritative reducer |

An accepted binding must store exact Definition hashes and a complete mapping
of the commitments, observations, state and intents it implements. A changed
Definition invalidates the old mapping; updating a hash without semantic
remapping is not conformance.

### Observation boundary

The environment produces an actor-specific observation from authoritative
world state. Each observation declares the fields available to that actor and
uses explicit markers for missing or unresolved values.

Persistent state that affects future behavior must be visible to replay. The
current Definitions identify request/case status, authorization, information,
review, channel, proposal and posture states that the next mapping must place
under an authoritative, replayable path.

### Current Definitions and frozen engineering baseline

The current Knickerbocker Trust and NYCH Definitions have an accepted,
non-executable mapping specification. `src/h2epr/agents/panic_1907_baseline.py` preserves a
small non-Ray path for the old `0.1.0-dev` fixture. It validates:

- Definition identity and content hashes;
- observation allowlists;
- missing-value handling;
- request and response lifecycle;
- procedural authority;
- commitment-to-intent mapping;
- environment-owned results;
- deterministic trace and replay.

This fixture is separate from both the current Definitions and the older G3
Rule policy. It proves engineering seams only. Current integration begins with
a new Definition-to-implementation mapping rather than relabeling this path.

## Runtime and MASim integration

Standard MASim scenarios use:

```text
GeneralSimulationRunner
  -> GeneralSimulator
  -> PlayerPersona
  -> GeneralPlayer
```

The H2EPR G3 canary uses an opt-in pair:

```text
H2EPRSimulationRunner
  -> H2EPRSimulator
  -> ten phased barriers
  -> H2EPR policy and world effects
  -> event-process reducer, transport and trace
```

The paired runtime keeps the MASim setup/run/shutdown lifecycle while replacing
level dispatch with explicit barriers. All participant decisions for a tick use
the same prestate. Participant completion order is canonicalized before
reduction.

Domain-neutral event-process values, transport, reducer mechanics, trace and
seals live under `masim.integrations.event_process`. H2EPR event identity,
policy, world effects, detectors and orchestration remain under this project.
The default `GeneralSimulator` path is unchanged.

The current code predates a fully consolidated adapter boundary. Direct MASim
imports appear in the G3 runtime modules, the G4 compiler adapter and the
frozen Agent baseline. Before the new Agent semantics join the formal runtime,
these imports should be reviewed capability by capability and routed through a
clear H2EPR integration surface.

## Runtime authority and trace

Each logical tick follows the same responsibility order:

1. construct participant observations from one prestate;
2. collect decisions and intents;
3. validate intent identity and prestate binding;
4. adjudicate actions and messages;
5. apply state deltas through the reducer;
6. advance delayed-message transport;
7. write generated detector annotations;
8. seal the tick.

The transport records queued, delayed, sent, delivered, expired, rejected,
duplicate and failed dispositions. A delivered message proves transport
delivery, not completion of the business request it carries.

The accepted architecture canary covers nine profile/seed rows and 41 logical
ticks. It is deterministic and Rule-only.

## Generated EPG compiler

`src/h2epr/compiler/` consumes an explicitly inventoried G3 trace package.
The compiler:

1. verifies each input path and SHA-256;
2. validates the record chain, TickSeals and RunSeal;
3. replays the trace;
4. materializes V1 RunManifest and SimulationTrace wrappers;
5. derives events, episodes, stages and temporal/causal relations;
6. writes a deterministic Generated EPG and GraphSeal.

The compiler uses only simulation records and generated detector annotations.
The seven original G3 scientific files remain unchanged.

Private compiler modules may be reorganized as the project grows. V1 output
shape, identity and deterministic behavior remain the compatibility boundary.

## Evaluation

Historical evaluation is a post-seal responsibility. It receives:

- a sealed SimulationTrace;
- a Generated EPG and GraphSeal;
- an approved held-out evidence set.

Evaluation findings belong to a successor Agent/scenario version. The same
run is not modified after its historical outcome has been inspected.

No evaluation package is currently part of the active implementation. Its
placement will be chosen together with the first approved evaluation method.

## Repository and package boundaries

`projects/h2epr/src/h2epr` is repository-local and is not installed by the
root `setup.py`. This keeps H2EPR-specific code separate from the distributed
MASim package while the framework boundary is still evolving.

The current placement rules are:

- H2EPR event assets and configs stay under `projects/h2epr/`;
- standard MASim scenarios stay under root `examples/` and `configs/`;
- reusable MASim code contains no H2EPR event identity or policy;
- frozen inputs stay under `data/h2epr/`;
- generated runs stay under `EXPERIMENT/H2EPR/`.

A future package move must preserve contract identity, trace hashes and path
semantics. The project will audit those identities before changing the
repository location.

## Current limitations

- The current G1–G4 canary is based on full-draft-exposed construction.
- Rule v1 reads broader state and uses more actor-specific code than the new
  Agent Definition design permits.
- The current `0.2.1` two-role Definitions and mapping specification have not
  been implemented or integrated into the G3/G4 path; the old three-tick unit
  is only a frozen engineering fixture.
- NYCH authority outside the member facility remains unresolved.
- Exact Knickerbocker requester identity and corporate authorization remain
  unresolved.
- H2EPR-0616 is still required before a future cross-domain shared-core claim.

These constraints define the next review work; they do not prevent continued
iteration on the two Agent Definitions.

## Related documents

- [Project guide](../H2EPR.md)
- [Project README](README.md)
- [Evolution policy](EVOLUTION.md)
- [Contracts V1](contracts/v1/README.md)
- [Agent guide](agents/README.md)
