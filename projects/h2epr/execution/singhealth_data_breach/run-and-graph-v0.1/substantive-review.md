# Substantive review: SingHealth run and generated graph v0.1

## Review question

Does the accepted full-roster package produce a complete, independently
repeatable, replayable, and trace-derived event graph while preserving its
participant, institutional, technical, time, custody, and claim boundaries?

## Executable lineage

The run manifest names the accepted executable package and runtime bundle by
identity, version, serialized hash, and canonical hash. Compact release
admission reloads that package through its fail-closed admission boundary and
requires the run manifest to resolve to the admitted parent. Earlier semantic
and Policy Realization releases remain unchanged and continue to resolve
through the executable parent.

Finding: **pass**.

## Independent materialization

The canonical and repeat materializations start in distinct fresh operational
directories. They share only the admitted package, runtime bundle, run profile,
and seed. Operational paths are excluded from the reproducibility documents.
All eight serialized documents—run manifest, trace, final state, tick seals,
run seal, replay receipt, generated EPG, and execution receipt—have equal bytes
and equal canonical hashes across the two executions.

Finding: **pass**.

## Full-roster and policy coverage

All thirteen configured actors operate on every coordinate, and all thirteen
actor-capability projections retain separate authority, capacity, assignment,
access, and private state. The run evaluates all 41 commitments and emits 41
actions on the declared canonical path. The environment records concrete
applications of all nine selected Scenario policies against their originating
actor, capability, commitment, and action. The authoritative state contains
objects from all eleven lifecycle families.

This is coverage of one declared mechanism path, not exhaustive emission of 74
alternative intent placements. Alternative, no-intent, and failure branches
remain covered by the accepted Policy Realization and executable-package
tests.

Finding: **pass for the declared mechanism-coverage profile**.

## Authority and bounded institutional endpoints

Participant policies propose intents but do not author their admission,
technical effect, institutional classification, message delivery, or another
participant's choice. The environment checks each intent against its admitted
actor, commitment, branch, execution coordinate, lifecycle, authority,
capacity, access, ownership, and private-state update. The reducer alone
changes authoritative state.

Results and directed notices enter append-only transport and become available
no earlier than the following logical coordinate. MOH, CSA, and the
notification process consume only admitted deliveries at their accepted
bounded endpoints. They receive neither Agent observations nor autonomous
decision state and therefore do not silently expand the roster.

Finding: **pass**.

## Time, lifecycle completion, and replay

The fifty logical coordinates preserve ten accepted same-time barriers at five
event anchors without adding intraday precision. All submitted messages reach
terminal transport disposition before completion. Open lifecycle records keep
their object, owner, state, version, reason, and causal context in typed
carry-forward records at the analytic horizon.

The trace closes with fifty tick seals and one run seal. Replay begins from the
admitted initial state, checks every delta prestate, and reproduces the sealed
final-state hash.

Finding: **pass**.

## Shared H2EPR kernel

Pair materialization, complete-artifact validation, byte and canonical
comparison, graph receipt construction, compact closure, strict JSON and path
handling, and ignored custody use the event-neutral `h2epr.execution` kernel.
The release pins those shared sources together with the thin SingHealth release
adapter. Actor IDs, event counts, policies, state, time, reduction, and graph
semantics do not enter the shared kernel.

The same kernel had already reproduced the accepted Panic comparison and graph
receipt. SingHealth is its independent second event consumer; no H2EPR code is
receipt. SingHealth is its separate second event consumer; no H2EPR code is
moved into MASim and no MASim source is modified.

Finding: **pass**.

## Generated graph

Graph compilation begins only after trace validation and run sealing. Each of
the 752 nodes carries an exact trace record identity and record hash. Each of
the 623 edges resolves its source and target nodes and its source trace
references. The graph names the exact source trace and run seal and has a seal
over its complete preimage. The compact graph receipt reproduces these parent,
inventory, and closure facts without treating the summary as the graph.

Finding: **pass**.

## Custody and reproducibility

The repository tracks the executable code and inputs, compact run records,
large-artifact hashes, reader documentation, review, and checksum inventory.
The two full traces and graphs remain in event-qualified ignored custody. This
keeps the publication surface readable while retaining exact byte identities
for later inspection or regeneration. No machine-specific absolute path is a
run identity.

Finding: **pass**.

## Claim boundary

The run uses evidence-exposed, synthetic mechanism-coverage projections. Its
determinism, replay, and graph closure are engineering properties of the
declared model. They do not show that its trajectory is historically fitted or
independently predictive, and they do not evaluate policy effectiveness or
scientific validity.

Finding: **pass**.

## Verdict

**Accept as the SingHealth Data Breach deterministic run and generated-graph
closure v0.1.**

This closes the second event's end-to-end Rule path. The next task is a narrow
cross-event conformance and publication-surface closeout over the two accepted
event releases and their shared H2EPR kernel.
