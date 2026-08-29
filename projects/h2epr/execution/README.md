# H2EPR Rule execution

This directory owns the reviewed assets that turn an accepted, non-executable
Scenario Configuration into a deterministic Rule execution. It sits between
semantic configuration and generated run output; it does not replace either
one.

## Responsibilities

| Asset | Responsibility |
|---|---|
| Policy Realization | Maps every configured actor capability and selected Scenario policy to explicit, versioned Rule behavior, including configuration inputs, replayable private state, no-intent reasons, revisit triggers, lifecycle implementations, and failure behavior |
| executable successor package | Pins the accepted semantic parents and closes actor, carrier, policy, lifecycle, component, and completion coverage |
| runtime bundle | Materializes the exact actor registry, participant artifacts, initial state, routes, exogenous inputs, policy registry, clock, environment, reducer, and compiler inputs used by a run |
| run and graph record | Preserves deterministic trace, seals, replay, generated-EPG identity, and compact verification evidence |

The accepted Scenario Configuration remains the authority for actor assembly,
opening records, selections, sensitivities, and completion meaning. Agent
Definitions and Population Models remain the authorities for participant
semantics. Policy Realization supplies implementation behavior but cannot add
an observation, intent, authority, route, lifecycle, or result absent from
those parents.

## Event layout

Execution assets are event-qualified and use the same event directory names as
the rest of H2EPR:

```text
execution/
  panic_1907/
    policy-realization-v0.1/
    full-roster-rule-v0.1/
    run-and-graph-v0.1/
  singhealth_data_breach/
    policy-realization-v0.1/
    full-roster-rule-v0.1/
    run-and-graph-v0.1/
```

Create a directory only when its artifact exists. A release package may keep a
machine document, concise guide, review, manifest, and checksum inventory
together; the workflow does not require a separate report for every policy or
actor.

## Current releases

The [Panic of 1907 Policy Realization v0.1](panic_1907/policy-realization-v0.1/)
closes the first event's 12 participant implementations, nine selected
Scenario policies, and thirteen lifecycle families.

The accepted
[Panic of 1907 full-roster Rule package v0.1](panic_1907/full-roster-rule-v0.1/)
then binds all sixteen actor carriers, seventeen capability projections, 127
actor-qualified actions, eighty-eight decision rules, thirteen lifecycle
families, and nine concrete runtime components to one deterministic bundle.
It is execution-eligible but is not itself a canonical run or generated EPG.

The accepted
[Panic of 1907 run and generated graph v0.1](panic_1907/run-and-graph-v0.1/)
records two byte-identical full-roster materializations, successful
authoritative replay, and a trace-closed generated EPG. Full traces and graphs
remain in ignored event custody; the tracked release retains their exact
identities and compact closure evidence.

## Admission boundary

An executable successor is admitted only when:

1. its configuration, release, mapping, roster, and Scenario parents resolve
   by exact identity and content hash;
2. every configured actor capability, population unit, structural selection,
   exogenous input, decision commitment, intent placement, selected policy,
   and required lifecycle has exactly one declared realization or an explicit
   non-emitting disposition;
3. actor-specific profiles, postures, and other fixed policy parameters resolve
   through explicit pointers into the hash-pinned configuration;
4. implementation IDs resolve through the H2EPR code registry without dynamic
   imports or event-local defaults;
5. participant intent, environment adjudication, authoritative reduction, and
   later observation remain separate;
6. unsupported or incomplete inputs are rejected before a run;
7. the same package and seed are materialized twice and must yield identical
   runtime bundles, traces, seals, replay receipts, and generated EPGs; and
8. the output claim remains limited to uncalibrated mechanism coverage.

These are cross-object checks, not eight independent approval steps.
The closed structural profiles are documented under [`schemas/`](schemas/).

Coverage is counted at the configured actor-capability placement. A shared
population capability instantiated for several actors is checked once for each
actor's information, state, parameters, and lifecycle scope, while its released
semantic identity remains singular. Branch tests close every declared intent
or non-emitting response; a canonical event run follows one predeclared policy
path and is not shaped to emit every alternative.

## Framework boundary

All H2EPR execution code lives under `projects/h2epr/src/h2epr`. MASim is a
read-only base framework. H2EPR may consume its public event-process values,
transport, reducer, trace, seal, and phased-runner interfaces, but cross-event
H2EPR code remains part of H2EPR even after reuse has been demonstrated.

## Output custody

Large traces, state snapshots, replay materializations, and generated graphs
are written to an event-qualified ignored run directory. The tracked release
surface contains the code and inputs needed to reproduce them together with a
compact manifest, receipt, checksum inventory, tests, and explanatory
documentation. A larger generated artifact enters Git only through a separate
release decision.
