# Run and release guide

## Preconditions

Materialization begins from an admitted compiled package and an implemented
binding. Record the clean Git identity, package and binding hashes, source
exposure, backend, seed or model controls, H2EPR runtime inventory, MASim
kernel inventory, and fresh ignored custody paths.

The output root must not exist. Reusing or overwriting custody destroys the
attempt denominator and invalidates byte-comparison evidence.

## Coordinate cycle

At each logical coordinate the runner:

1. delivers messages whose declared routes are due;
2. seals one public prestate;
3. projects observations for every active actor;
4. obtains one participant decision per actor;
5. canonicalizes the batch without using opaque generated IDs as priority;
6. invokes the environment once against the sealed prestate;
7. commits the authoritative reduction;
8. emits annotations and transport transitions; and
9. closes the tick seal.

The next observation includes runtime-derived memory of prior own action
dispositions and messages actually received. Pending transport is visible to
its sender; a recipient does not learn of a private queued message before
delivery. Draft stage, episode and action labels remain trace navigation
metadata, outside the backend observation. A logical coordinate identifies
time availability without certifying that its associated Draft action occurred.

The environment owns intent admission, parameter and authority checks,
preconditions, conflict handling, effects, and disposition. The backend owns
decision production. MASim owns the event-process values, append-only
transport, reducer, trace writer, and seals used by H2EPR.

## Required raw outputs

One materialization writes coordinate results, final state, Generated EPG,
replay receipt, run manifest, run seal, trace, tick seals, and run receipt.
The receipt inventory must name the exact other outputs in stable order and
bind them to one formal `.local-runtime/h2epr-simulation/runs/...` locator.

Verify directly:

- one decision and disposition path per actor and coordinate;
- trace sequence and previous-record hash chain;
- tick and run seal recomputation;
- zero unresolved terminal transport;
- authoritative replay from package opening state to exact final bytes;
- one graph node per trace record, complete referenced trace IDs, valid edge
  endpoints, source-trace hash, and graph seal;
- independently derived record, action, and coordinate counts.

## Deterministic Rule evidence

Use three fresh roots:

| Root | Identity mode | Purpose |
|---|---|---|
| materialization A | canonical | candidate custody |
| materialization B | canonical | exact repeatability |
| identity probe | generated-ID perturbation | prove opaque IDs do not change trajectory semantics |

A and B share the same logical custody locator so all scientific outputs and
the run receipt can be byte-identical. The identity probe has a separate
locator and run identity. The determinism receipt must hash-link the
independently derived identity-conformance receipt.

## Independent publication

Treat every producer receipt as a claim. The publisher reloads the package,
rebuilds the expected seed-0 manifest and source inventories, validates trace
and seals, replays state, rebuilds coordinate summaries and counts, recompiles
the Generated EPG, checks terminal transport, and rematerializes all three
Rule variants in temporary custody.

This catches a forged payload even when an attacker recomputes the payload's
self-hash, run receipt, and outer checksum. Publication refuses an existing
release root and removes a partially created release after failure.

The tracked release contains only compact receipts, the run manifest, a
reader-facing README, and exact checksums. Full trace and graph bytes remain
in ignored custody.

## Promotion

After publication, read the complete generated process using
[OUTPUT_AND_ANALYSIS_GUIDE.md](OUTPUT_AND_ANALYSIS_GUIDE.md). Add the event to
`events/current-events.json` only when its semantic releases, package,
realization, run release, and reading all exist at their sole current paths.
Recompute the registry self-hash and run repository-surface tests.

Cross-event conformance is a separate release requiring at least two distinct
current packages. A single-event success must never be described as
cross-event evidence.

## Failure disposition

Preserve failed custody. Route package or semantic failures upstream,
decision-contract failures to the backend, effect/authority failures to the
scenario, trace/replay failures to runtime, graph failures to the graph
compiler, and evidence mismatch to publication. Do not patch generated output.

After package admission, materialization writes the manifest and checkpoints
each sealed coordinate. A caught setup, execution, finalization, or output
failure preserves the available trace, tick seals, coordinate results,
`partial_state.json`, and `failure-receipt.json`. The receipt records the
failure, sealed ticks and unresolved transport; it is ineligible for a complete
release. A process killed without cleanup may leave only the last checkpoint.
Disk failure can prevent even that checkpoint from being written.

These checkpoints support diagnosis, not exact resume. Restart in fresh
custody after correcting the owning cause. Unmet `outcome_expectations` are
instead recorded in an otherwise valid run receipt and independently
recomputed from replayed terminal state; they do not create a failed attempt.
