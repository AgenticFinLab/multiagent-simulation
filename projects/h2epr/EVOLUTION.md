# Maintenance and evolution

H2EPR publishes one current surface while preserving prior states in Git. A
change begins as a review candidate, is validated with all affected
dependents, and replaces the current path only when accepted. The tracked tree
does not keep parallel working generations.

## Change ownership

| Change | Owning product | Required downstream work |
|---|---|---|
| Participant identity, aggregation, or representation | Roster and actor map | Semantic parents, interfaces, package, runs, releases, reading |
| Observation, intent, lifecycle, authority, or parameter domain | Participant semantic products and registries | Scenario closure, package, runs, releases, reading |
| World field, route, institution, environment semantics, or clock | Scenario products | Configuration, package, every compared backend run and release |
| Backend-neutral selected value | Shared configuration | Package, every backend run and release |
| Decision rule, prompt, model setting, or constraint policy | Backend configuration and realization | Binding, affected backend runs and releases |
| Trace, replay, seal, or graph semantics | Runtime or graph contract | Every event and backend run, release, and conformance receipt |
| Experiment rows, seeds, model controls, scheduling, or analysis | Experiment plan | Admission receipt and all planned attempts |
| Incorrect release evidence | Publisher or release | Reject and regenerate; never edit evidence into consistency |

Changing participant, scenario, environment, or shared configuration meaning
creates a new package identity. That package begins a new comparison group
unless every compared backend is rematerialized against it. A backend-only
change must leave the backend-neutral package identity unchanged.

## Replacement procedure

1. Identify the owning layer and state the falsified contract.
2. Modify only that layer and its declared dependents.
3. Recompute semantic manifests, checksums, assembly identities, package core,
   backend catalog, and bindings in dependency order.
4. Rematerialize every affected deterministic baseline in fresh custody.
5. Compare normalized decisions, dispositions, deltas, messages, annotations,
   and terminal state with the accepted baseline; explain every intended
   difference.
6. Rebuild compact releases, simulation readings, and cross-event
   conformance.
7. Run the complete suite from a clean archive or clone.
8. Update current pointers and commit the replacement as one coherent change.

Do not overwrite raw custody, reuse a failed output directory, repair a hash
without rebuilding its source, or retain an obsolete working directory under
the current event tree.

## Stable paths and machine identity

Human-facing paths and public Python imports are stable. Machine contracts
retain schema versions, semantic IDs, and content hashes because those values
make admission and replay falsifiable. A semantic identity change propagates
through its manifests and dependents even though the path remains current.

`events/current-events.json` is the only current-event discovery pointer. It
may reference an event only after all declared paths, package identities,
individual release checks, and reading close. Once the registry contains two
or more events, the current cross-event conformance release must cover every
row. A zero- or one-event registry has no cross-event claim.

## Experiment immutability

An admitted experiment plan is immutable after an attempt begins. A changed
row, seed set, custody location, retry policy, model control, or analysis
definition requires a new plan identity. Failed custody remains evidence and
is never replaced by a retry.

## Historical recovery

Prior repository states remain accessible from Git commits and the designated
local history branch. Supervisor notes, build diaries, audits, migration
records, and commit-to-asset maps belong under ignored `.local-runtime/`
project memory. They may inform maintenance but are not formal runtime or
publication inputs.
