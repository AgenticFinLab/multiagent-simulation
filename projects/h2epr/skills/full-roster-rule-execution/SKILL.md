---
name: h2epr-full-roster-rule-execution
description: Realize and close an accepted H2EPR Scenario Configuration as deterministic full-roster Rule execution. Use after configuration admission and bounded lineage conformance are accepted, when work is authorized to build Policy Realization, an executable successor, repeated runs, replay, and a trace-derived generated EPG; do not use for semantic revision, model-backed policy, calibration, or scientific evaluation.
---

# Full-roster Rule execution

Use this Skill to extend a conformance-complete H2EPR event into one
deterministic, replayable full-roster Rule execution. The method was derived
from the accepted Panic of 1907 and SingHealth Data Breach implementations.
It preserves the same engineering responsibilities without copying either
event's participants, policies, clock, state, or graph semantics.

This is an optional event phase. It is not required for ordinary event
framing, participant production, configuration, or bounded conformance.

Read the project [Rule-execution guide](../../execution/README.md), the exact
accepted event entry and semantic parents, and the
[execution-cycle template](../../execution/execution-cycle-closeout-template.md)
before implementation. Apply the project
[phase closeout checklist](../../phase-closeout-checklist.md) only at the
maintained product boundaries. If a run uses remote machines, paid APIs, or
model-backed policies, apply the repository
[experiment-preflight method](../../../../docs/experiment-preflight-skill/00-overview.md)
separately; its operational gates are not requirements for a local
deterministic Rule materialization.

## Choose the endpoint

Name the last product authorized for the cycle:

| Endpoint | Required result | Stop before |
|---|---|---|
| Policy Realization | Complete, admitted Rule behavior for the configured semantic inventory | Runtime assembly or execution |
| Executable successor | Exact parent binding, complete carrier and component assembly, and fail-closed admission | Materializing a run |
| Run and generated graph | Two independent same-input materializations, replay closure, and a trace-derived generated EPG | Calibration or evaluation |
| Cross-event method review | Comparison of already accepted releases under one shared closure contract | Changing either event or claiming domain validity |

Several endpoints may be completed in one work cycle when their artifacts and
verdicts remain separately identifiable. Do not create an approval or status
file for each row merely because the work is sequential.

## Required inputs

Confirm:

- the event identity, research purpose, modeled interval, claim boundary, and
  authorized endpoint;
- exact accepted identities and hashes for the Event Scenario Definition,
  roster, consolidated mapping, Scenario Configuration, configuration
  admission, and bounded binding/conformance records;
- the complete configured inventory of actors, capability placements,
  commitments, intents and non-emitting branches, selected Scenario policies,
  lifecycle families, structural selections, exogenous inputs, routes,
  completion conditions, and declared failures;
- the intended Rule implementation roots, public MASim interfaces, output
  custody root, seed, and run identity policy; and
- excluded work, especially semantic revision, model-backed policy,
  calibration, known-outcome fitting, evaluation-only targets, and external
  claims.

Stop before implementation if an accepted parent is mutable, drifted, or not
byte-identifiable. An execution layer cannot repair a semantic gap.

## Build the execution chain

### 1. Derive the coverage inventory

Load the admitted configuration and derive coverage from its pinned parents.
Count configured placements, not only distinct reader-facing labels. Give
every required item exactly one implementation or an explicit non-emitting or
external disposition.

Use the bounded lineage implementation as an interface precedent, not as a
source of missing full-roster behavior. Reject hand-copied counts, event-local
defaults, ambiguous identifiers, and policies that resolve only because a
similarly named implementation exists.

### 2. Realize Rule behavior

Implement participant decisions, selected Scenario policies, and lifecycle
transitions as separate, versioned objects. Preserve these boundaries:

- observations are limited to the participant's declared information set;
- persistent participant state distinguishes never-issued, pending, failed,
  expired, superseded, and completed intents when later behavior depends on
  that distinction;
- a participant may emit an intent or message but cannot declare its delivery,
  acceptance, execution, or effect;
- the environment adjudicates attempts, and the reducer alone changes
  authoritative state; and
- no-intent, invalid, delayed, duplicate, failed, expired, and other declared
  branches remain observable rather than collapsing into a default success.

Test every declared intent or non-emitting response through focused branch
cases. A canonical run may follow one predeclared path; it need not force all
alternatives into one history.

### 3. Assemble and admit the executable successor

Preserve one canonical actor interface, authority graph, relationship set,
and resource owner per entity while projecting every configured capability
and population unit. Build one exact runtime bundle containing the actor
registry, participant implementations, opening state, routes, exogenous
inputs, policy registry, clock, environment, reducer, completion rule, and
graph inputs.

Admission must verify exact semantic parents and complete actor, capability,
commitment, intent, policy, lifecycle, route, component, and failure coverage.
Resolve implementations through an explicit registry. Reject dynamic imports,
implicit fallbacks, unsupported inputs, path escape, duplicate identity, and
partial assembly before a run begins.

H2EPR code remains under `projects/h2epr/src/h2epr`. Consume only public MASim
interfaces; do not place H2EPR event or cross-event logic in `masim/`.

### 4. Materialize twice

Preflight the exact package, seed, output boundary, and empty event-qualified
custody locations. Never overwrite an accepted or prior materialization.
Produce two fresh runs from the same admitted input and compare the complete
run-document surface using the shared `h2epr.execution` closure contract.

The trace must preserve the causal chain needed by the event: observation,
decision, intent or message, transport and disposition, authoritative result,
state delta, and later observation. Record unsuccessful attempts when they
are part of the declared behavior. Determinism applies to the declared
reproducibility outputs and their seals, not to unrelated host metadata.

### 5. Replay and compile the graph

Replay from the sealed trace without consulting participant policies or
repairing state from the final snapshot. Require replayed terminal state and
seal closure to match the materialized run.

Compile the generated EPG only from admitted trace records. Every graph node
and edge must resolve to trace provenance, event identity, and deterministic
graph identity. Reject unresolved references, orphan graph items, unsealed
parents, and compilation that changes across the two materializations.

### 6. Publish compact closure evidence

Keep full traces, state snapshots, replay materializations, and generated
graphs in event-qualified ignored custody. Track only the code and semantic
inputs needed to reproduce them plus compact manifests, receipts, comparison,
review, and checksum evidence. Do not add a large artifact to Git without a
separate release decision.

Use the execution-cycle template as a compact authoring and review aid. Put
its fields into the manifest, README, receipt, or substantive review that
already owns them; instantiate a separate copy only when no existing record
can carry the closeout without ambiguity.

### 7. Review and learn

Run focused admission, branch, runtime, replay, graph, and negative checks
first. At an executable or run-release boundary, run the affected regression
suites, repository release checksums, strict formal-JSON parsing, publication
links, package checks, and the full H2EPR suite.

Extract shared code only after independent event use demonstrates the same
responsibility and interface. Shared code must accept event identity and
coverage as inputs and contain no event-specific actors, policies, clock,
state, reducer, or graph semantics. Similar filenames or object shapes alone
do not justify a framework abstraction.

## Failure routing

| Failure | Return to |
|---|---|
| Missing or contradictory participant choice | Agent Definition or Population Model |
| Missing route, lifecycle meaning, adjudication, resource, or result owner | Event Scenario Definition |
| Incorrect actor assembly, selected alternative, opening record, or completion rule | Scenario Configuration |
| Parent identity, schema, canonicalization, or static-reference failure | Configuration admission |
| Semantic loss or ambiguous carrier identity | Consolidated mapping or binding |
| Missing behavior or coverage, hidden default, or implementation-only state | Policy Realization or executable successor |
| Nondeterministic transition, trace, seal, or replay | Runtime or event-process implementation |
| Graph item without sealed trace provenance | Graph compiler |
| Historical comparison or empirical-quality question | Separately authorized evaluation |

Fix a defect at its owning layer through the appropriate successor. Do not
edit a frozen parent merely to make downstream admission pass.

## Stop conditions

Stop and request a scope decision when:

- the event question, interval, roster, structural interpretation, or claim
  class would change;
- a required semantic parent is missing, mutable, or fails integrity;
- full-roster implementation would invent an observation, intent, authority,
  route, lifecycle, result, or historical fact;
- a new shared contract is proposed without a concrete representation loss;
- execution would require an unapproved model, API, remote resource, protected
  evaluation target, or destructive output operation; or
- deterministic engineering evidence is being presented as calibration,
  historical reconstruction, policy effectiveness, or scientific validity.
