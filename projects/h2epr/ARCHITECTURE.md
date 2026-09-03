# Architecture

## Execution path

```text
three allowed files for one benchmark event
        │
        ▼
Source Profile
        │
        ▼
roster + actor map
  Agent Definitions + Population Models
  observation + intent + lifecycle registries
        │
        ▼
Scenario Definition + Scenario Mechanism
        │
        ▼
shared configuration
        │
        ▼
backend-neutral event package
        │
        ├──────── Rule binding      implemented
        ├──────── LLM binding       planned
        └──────── RuleLLM binding   planned
        │
        ▼
common participant-decision interface
        │
        ▼
authoritative environment + MASim reducer
        │
        ▼
hash-chained trace ──► seals ──► replay
        │
        ▼
trace-derived Generated EPG
        │
        ▼
compact release + simulation-only reading
```

An optional experiment control plane sits above this path. It admits a matrix
of package, backend, seed, custody, failure, and analysis selections. It does
not change event semantics, decision behavior, runtime state, or graph
construction.

## Authority by layer

### Benchmark input

`data/h2epr` owns event identity and benchmark-authored records. H2EPR resolves
one event ID to exactly `event_spec.json`, `frozen_evidence.json`, and
`draft_epg.json`. The loader neither inventories sibling files nor searches
for fallback data.

### Source Profile

The Source Profile owns input paths, byte hashes, exposure mode, prohibited
inputs, transformations, and claim exclusions. A path, hash, event identity,
or exposure mismatch stops construction.

### Participant products

The roster preserves every Draft participant occurrence. The actor map assigns
each occurrence to an Agent, Population, world-state object, institutional
process, outside-window record, or explicit source defect. Agent Definitions
and Population Models then own identity, information, authority, admissible
intents, parameter domains, and limitations for active decision units.

The participant interface registries own observations, intents, lifecycle
states, routes, and handler references. They do not choose an action for any
backend and do not commit world state.

### Scenario products

The Scenario Definition owns the event window, institutions, clock,
communication meaning, environment authority, failure routing, and terminal
conditions. `scenario-mechanism.json` is its executable projection: typed
state fields, handlers, preconditions, effects, message kinds, annotation
rules, and conflict policy.

Shared configuration selects the exact opening state, timeline, routes, and
other backend-neutral values. Every top-level setting is either linked to a
dataset anchor or recorded as an explicit construction choice.

### Event package

The compiler validates and seals portable participant and scenario
projections. `package_sha256` identifies the backend-neutral core and excludes
the backend catalog and attachments. A backend attachment changes the full
manifest and binding identities without changing that core hash.

The package contains no credential, generated decision, or successful outcome.
It is the parity boundary for backend comparisons.

### Backend

A backend receives one observation for each active decision unit and returns
one typed action intent plus zero or more typed message intents. It owns
decision production only. Rule tables or model settings belong to backend
configuration and realization, not Agent Definitions or the event package.

Rule, LLM, and RuleLLM must share the package's actors, observations, action
schema, clock, environment, and output contracts. An unavailable or
identity-mismatched backend fails before setup; it is never silently replaced.

### Runtime and environment

For each logical coordinate, the runtime:

1. delivers due messages;
2. seals one pre-state;
3. constructs all participant observations from that state;
4. collects and canonicalizes decisions;
5. invokes the environment once;
6. commits one authoritative reduction;
7. derives annotations; and
8. seals the coordinate.

The environment owns admission, authority checks, concurrent effects, and
typed dispositions. All intents at one coordinate are checked against the same
pre-state. Distinct concurrent writers to the same field are rejected as a
batch; identical writes are idempotent and ordered by semantic content.
Opaque generated IDs and input ordering do not decide outcomes.

### MASim boundary

H2EPR uses the tracked MASim event-process implementation for action and
message values, append-only transport, authoritative reduction, trace, tick
and run seals, and replay. H2EPR owns the benchmark-specific package,
participant loop, declarative environment, and Generated EPG compiler.

When optional MASim top-level dependencies are unavailable, H2EPR loads the
same tracked event-process subpackage through a private import path. This
changes import mechanics only; no MASim code or scientific value is copied.
Every run records the exact H2EPR and MASim source inventories.

### Trace, replay, and Generated EPG

The trace is append-only and hash chained. Tick and run seals close the state,
transport, and record sequence. Authoritative replay starts from the package's
opening state and must reproduce the exact terminal bytes.

The Generated EPG compiler accepts only the admitted package, sealed run
manifest, and trace. Every trace record becomes a first-class graph node;
navigation nodes for the event, coordinates, participants, and state entities
do not replace trace provenance. Validation requires exact trace coverage,
valid edge endpoints, matching source-trace identity, and a deterministic
graph seal.

### Release and report

Raw runs stay in ignored custody. A compact tracked release records package,
binding, runtime, MASim kernel, seed, output hashes, counts, replay, graph,
determinism, and custody identity. Publication independently reconstructs
these claims from the raw bytes and rematerializes deterministic Rule runs.

A simulation reading cites the compact release, traverses the complete trace
and graph, describes generated facts, attributes mechanisms, and states open
or persistent terminal fields. It remains separate from historical or
held-out evaluation.

## Single-current publication surface

The tracked tree exposes one current directory, template, Skill, schema file,
and Python import path for each responsibility. Machine-level
`schema_version`, artifact IDs, and content hashes remain explicit because
they are validation inputs. Replaced development generations and construction
history remain recoverable from Git rather than appearing beside current
assets.

`events/current-events.json` is the discovery registry. Adding an event adds a
registry row and declarative assets; it must not add an event ID, slug,
participant, or domain branch to common Python.

## Backend parity and change routing

A backend revision may change decision production only. Changes to actorization,
observations, action schemas, environment behavior, clock, trace semantics, or
analysis definitions create a new shared comparison boundary and require all
compared backends to be rematerialized.

Each defect returns to its owning layer. Participant mistakes are not repaired
in the environment; scenario mistakes are not hidden in Rule rows; runtime or
publication failures do not authorize a semantic change. [EVOLUTION.md](EVOLUTION.md)
defines how a reviewed replacement becomes current without publishing parallel
working generations.

## Current boundary

The common Rule implementation, compiler, runtime, replay, graph, publication,
and experiment-admission contracts are implemented. Current event results are
declared only by `events/current-events.json`. LLM and RuleLLM remain planned
and fail closed. The experiment layer admits plans but does not execute a
matrix.
