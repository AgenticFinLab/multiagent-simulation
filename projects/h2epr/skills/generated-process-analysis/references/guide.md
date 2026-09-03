# Generated process analysis guide

## Evidence gate

Begin only from a release whose package, trace chain, seals, replay, graph,
source inventories, and custody identity have independently passed. Analysis
must not repair missing records or infer a path from a compact receipt alone.

## Complete-output ledger

Read in sequence and record coverage for:

1. opening state and run manifest;
2. every observation, decision, action intent, message intent, disposition,
   state delta, delivery transition, annotation, stage entry, tick seal, and
   run seal;
3. terminal state and replay receipt;
4. every Generated EPG node and edge, including source-trace references;
5. coordinate summaries and count maps, checked against the trace.

Maintain a trajectory table with coordinate, active observations, decisions,
accepted/rejected/partial effects, messages, lifecycle transitions, state
before/after, annotation, and cited trace IDs. Maintain a graph-class ledger
with node/edge class, count, endpoints checked, and anomalies.

## Evidence labels

| Label | Meaning | Required citation |
|---|---|---|
| direct generated fact | exact content present in trace/graph/state | trace or graph record ID |
| mechanism attribution | declared handler/backend/environment explains a transition | package mechanism plus generated disposition/delta |
| interpretation | analyst account of pattern or significance | generated evidence plus explicit reasoning |
| dataset-facing description | relation to an exposed Draft input | Draft anchor and exposure caveat |
| unsupported | calibration, historical fit, causality, policy effect, scientific validity, generality | exclude or reserve for another protocol |

Classify terminal domain values as closed lifecycle, persistent outcome, or
deliberately open state. Do not infer closure from a field name.

## Comparison gates

Backend comparison requires identical package core, shared configuration,
runtime/environment/trace contract, source exposure, seed grouping, and an
accepted analysis contract. Cross-event comparison uses only event-neutral
definitions and reports missing/non-comparable values. Full-Draft construction
may support a transparent descriptive comparison but not an unbiased score.

## Falsifiers and routing

Stop on incomplete trace or graph coverage, invalid endpoint, unexplained
count mismatch, unresolved transport, package/runtime drift, uncited direct
claim, or mixed evidence labels. Route behavior gaps to participant semantics,
value gaps to configuration, selection gaps to backend, effect gaps to
Scenario/environment, integrity gaps to runtime/publication, and analysis
definition gaps to the report/template layer.

## Handoff

Publish run identities, exact coverage counts, trajectory and graph ledgers,
direct findings, mechanism attributions, interpretations, anomalies, exposure,
limitations, routed findings, and next legal action. The report is
simulation-only unless a separately accepted evaluation protocol says more.

The formal simulation reading keeps exactly the five level-two headings in
`templates/simulation-reading.md`. Separate interpretation with an evidence
label or a level-three subsection under `Mechanism reading`; “separate” does
not mean adding a sixth level-two chapter.
