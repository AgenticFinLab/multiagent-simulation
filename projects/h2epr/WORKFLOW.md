# Workflow

## 1. Admit one event

Choose the H2EPR event ID and exposure mode. Resolve exactly
`event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`; record their
paths and hashes in a Source Profile. Stop on an identity, hash, shape, or
prohibited-input violation.

## 2. Close the source roster

Extract every Draft participant occurrence. Assign each one to a named Agent,
Population, initial context, world-state object, institutional process,
outside-window record, or explicit source defect. Record aggregation,
exclusion, and information loss before runtime work.

## 3. Define active decision units

Write one Agent Definition or Population Model for every active unit. Close
dataset provenance, observation limits, state visibility, authority,
admissible intents, parameter domains, environment-result boundaries, worked
cases, falsification conditions, and limitations. Keep exact Rule or model
settings out of these backend-neutral products.

## 4. Close participant interfaces

Publish the observation, intent, and lifecycle registries. Resolve every
active actor to one semantic parent and close producers, consumers, routes,
handlers, lifecycle states, and state owners. Any unresolved actor or intent
stops construction.

## 5. Define and configure the scenario

Define the event world, institutions, logical clock, observations,
communication, action admission, concurrent effects, failure routing,
termination, and annotations. Complete the Interface Closure.

Publish `scenario-mechanism.json` with executable state fields, handlers,
preconditions, effects, message kinds, annotation rules, conflict policy, and
safety invariants and descriptive outcome expectations. Desired event outcomes
must not be release preconditions. Put the exact timeline, opening state, routes, and other
shared selections in the shared configuration. Give every selected top-level
value a dataset provenance pointer or an explicit construction-choice
exemption.

## 6. Compile the backend-neutral package

Validate all paths, hashes, actor identities, semantic parents, interfaces,
routes, configuration provenance, and claim exclusions. Compile portable
participant and scenario projections, then seal the package core before
attaching a backend. `package_sha256` must exclude catalog and binding state.

## 7. Realize and bind a backend

Choose `rule`, `llm`, or `rulellm`. Publish its configuration and Backend
Realization, including exact implementation sources. Verify actor and action
space parity with the package.

Attach the backend through its registered factory. Recompute catalog,
manifest, and binding identities while proving that the backend-neutral
package hash did not change. A planned backend, unavailable factory, stale
source hash, or identity mismatch stops before setup; no fallback backend is
permitted.

## 8. Materialize into fresh custody

For event construction and synthetic contract verification, materialize
directly, including A/B and identity probes. Before a comparative multi-event,
multi-backend, or multi-seed study, publish and admit an experiment plan under
[EXPERIMENT_STANDARD.md](EXPERIMENT_STANDARD.md).

Write each run to a new ignored custody directory. At every coordinate the
runtime uses one sealed pre-state, collects all decisions, applies one
authoritative reduction, records transport, and seals the result. The run
writes its manifest, trace, terminal state, tick seals, run seal, replay
receipt, Generated EPG, and compact receipt. The horizon can end with an open
domain state or rejected request. Trace, replay and transport integrity must
still close; unmet outcome expectations remain visible results.

## 9. Verify determinism and publish

Validate package identity, implementation inventories, trace chaining, tick
and run seals, authoritative replay, graph provenance, endpoint closure, and
terminal transport. Materialize the same deterministic input twice in fresh
directories and require byte equality for every scientific output. Perturb
only the generated run identity and require the same normalized decisions,
dispositions, deltas, messages, annotations, and terminal state.

The publisher independently rederives observation-to-decision-to-intent
lineage, result counts, coordinate summaries, replay, graph construction, and
custody checksums. It rematerializes the Rule variants in temporary custody
before writing a compact release. Producer-supplied success flags are not
publication evidence.

Conflict tests also permute reducer input and opaque IDs. Distinct concurrent
writers must be rejected together; identical writes must retain one semantic
outcome independent of ordering.

## 10. Read the complete generated process

Describe the simulated trajectory before comparing it with a target. State
the event package, backend, seed, exposure, run, trace, terminal-state, and
graph identities. Traverse every trace record, graph node, and edge. Separate
direct generated facts, mechanism attribution, interpretation, and
limitations. Classify terminal fields as closed, persistent, or deliberately
open.

## 11. Register the current event

Add the event to `events/current-events.json` only after every declared path
exists, all package and release identities close, the reading is complete,
and the individual event passes the current repository checks. Adding an event
must not require editing a hard-coded event tuple in common Python.

When the registry contains at least two events, publish or refresh the
cross-event conformance release over every current row and require it to pass.
With zero or one current event, cross-event evidence is not applicable and must
not be fabricated as a promotion prerequisite.

## Failure routing

| Finding | Owning layer |
|---|---|
| Missing or inconsistent dataset record | Source Profile or recorded source limitation |
| Wrong participant aggregation | Roster or actor map |
| Wrong information, authority, or intent semantics | Agent Definition, Population Model, or participant registry |
| Wrong window, institution, or world meaning | Scenario Definition or Scenario Mechanism |
| Wrong exact value or hidden default | Shared or backend configuration |
| Poor Rule, LLM, or RuleLLM decision | Backend configuration or implementation |
| Invalid authority, resource effect, or outcome | Environment |
| Broken trace, seal, or replay | Runtime |
| Missing trace provenance in the graph | Generated EPG compiler |
| Incomparable rows, hidden retry, or seed drift | Experiment plan or closeout |
| Unverified release claim | Publisher |
| Overstated conclusion | Reading, report, or benchmark protocol |

Fix a finding at its owner. A downstream layer must not silently compensate
for an upstream semantic defect. If a current sealed identity changes, follow
[EVOLUTION.md](EVOLUTION.md), regenerate all dependent identities, and retain
the replaced state in Git history rather than beside the current tree.
