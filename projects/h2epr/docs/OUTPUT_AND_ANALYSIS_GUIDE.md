# Output and analysis guide

## Analysis order

Always validate evidence before interpretation. The reading order is:

1. compact release identities and checksum inventory;
2. package, binding, configuration, runtime, and source exposure;
3. run manifest and opening state;
4. complete trace in sequence;
5. tick seals, run seal, replay receipt, and terminal state;
6. complete Generated EPG nodes and edges;
7. coordinate summaries and count maps;
8. interpretation and any authorized comparison.

Sampling only action records misses observations, no-ops, rejected intents,
message lifecycle, annotations, barriers, and evidence seals. A simulation-only
reading therefore accounts for every trace record and every graph edge class,
even when prose focuses on a smaller number of turning points.

## Evidence classes

Use four labels consistently:

| Class | Example | Citation basis |
|---|---|---|
| generated fact | an intent was accepted at tick 4 | trace record ID |
| mechanism attribution | the transition occurred because handler X admitted the intent | package mechanism plus trace disposition/delta |
| interpretation | the generated process concentrates authority in one actor | explicitly labeled analytic judgment |
| limitation | the Draft supplies no actor-level distinction | Source Profile or semantic parent |

Do not present a configuration choice as a dataset fact, a generated sequence
as verified history, or an interpretation as a runtime record.

## Trajectory account

Describe the opening state, actor and coordinate coverage, decisions,
messages, dispositions, deltas, annotations, stage transitions, and terminal
state. Include rejected, no-effect, and no-op paths when they explain causal
structure or missing behavior.

For each turning point, identify:

- decision-time observation and message state;
- actor and typed intent;
- authority, parameter, guard, and precondition result;
- environment-owned delta or rejection;
- downstream transport and later decision;
- trace and graph references.

Classify each terminal value as a closed lifecycle, persistent output, or
deliberately open field. Never narrate an absent closure into existence.

## Generated EPG reading

The graph is trace-derived evidence, not a second simulation. Navigation nodes
for event, coordinate, actor, and entity make the process traversable. Trace
record nodes remain the provenance backbone. Verify:

- source trace hash and record count;
- exact one-to-one trace record node coverage;
- edge endpoints and relation vocabulary;
- coordinate, actor, and entity linkage;
- deterministic graph seal.

Network measures may summarize this graph only after their definition,
normalization, missing-value behavior, and interpretation limits are accepted.
High degree or centrality is a property of the generated representation, not
automatically historical importance or causal power.

## Draft-facing description

When the full Draft was exposed during construction, comparison can identify
omitted Draft actions, reordered coordinates, representation changes, or
mechanism projections. It is a descriptive implementation/model audit. It is
not a held-out score and must not be used to tune and then evaluate on the same
records without disclosure.

Reference EPG, held-out content, external history, and scientific evaluation
remain outside this guide unless a separate protocol explicitly admits them.

## Backend and cross-event comparison

Compare backends only after package, clock, environment, runtime, seed, output,
and analysis parity closes. Attribute differences first to participant
decisions, then follow their admitted environment and transport consequences.

Across events, compare contract-level properties or metrics with valid common
meaning. Preserve event-specific vocabulary and unavailable measures. Two or
more events support evidence of reuse across those cases, not universal
generality.

## Report quality

A publishable reading names exact identities, coverage counts, scope,
trajectory, mechanisms, terminal state, limitations, and falsifiers. It uses
natural prose and compact tables where they clarify repeated mappings. Build
history, supervisor dialogue, and defensive process narration stay local.

Use exactly the five level-two sections in the maintained simulation-reading
template. Evidence-class labels and event-specific analysis belong within
those sections; interpretation may be a level-three subsection of `Mechanism
reading`.
