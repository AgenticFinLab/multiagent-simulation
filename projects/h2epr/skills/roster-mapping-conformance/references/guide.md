# Roster mapping and conformance guide

## Source roster extraction

Traverse the admitted Draft deterministically by stage, episode, participant,
and action. Preserve exact observed names, types, roles, appearance anchors,
occurrence counts, and identifier defects. Normalize only for comparison; do
not overwrite source spellings or invent missing IDs.

Every unique source participant receives exactly one disposition:

| Disposition | Criterion |
|---|---|
| named Agent | autonomous named decision interface is simulated |
| population | repeated or aggregate choice unit is simulated |
| context | opening fact with no simulated choice |
| world state | environment-owned entity or condition |
| process | automatic or institutional transition |
| outside window | real source appearance intentionally excluded by time boundary |
| source defect | unresolved malformed, missing, or contradictory record |

The actor map records source-to-runtime cardinality and all many-to-one
aggregation. One source participant may not silently feed two active actors.

## Registry closure

For each active actor, resolve one semantic parent and one interface row. Then
check the shared registries as a graph:

- every observation has one producer, declared consumers, availability,
  visibility, and missing behavior;
- every intent has eligible actors/targets, payload meaning, authority owner,
  environment handler, and lifecycle;
- every lifecycle has one initial state, reachable terminal states, transition
  owners, and triggers;
- every actor capability is present in the appropriate registry, and no
  registry row widens its human parent;
- every source anchor in the semantic index exists in the admitted Draft.

`no_op` is typed behavior, not a way to hide an uncovered decision occasion.

## Adversarial checks

Reject duplicate source rows, duplicate actor IDs, fabricated source IDs,
unknown semantic parents, unsafe parent paths, hash drift, unknown
observations/intents/lifecycles, orphan producers or consumers, missing
targets, name-based authority, hidden aggregation, and changed source
names/types/roles. Test an opaque actor-ID perturbation: semantic results must
follow declared roles and interfaces rather than lexical names.

## Release construction

Publish the roster/actor-map release separately from participant interfaces.
Each release has a reader-facing README, exact artifacts, self-hashed manifest,
and SHA-256 inventory. The participant semantic index pins human parent bytes;
the portable package later projects those parents but cannot replace them.

## Failure routing

Source extraction and disposition defects remain here. Representation defects
go to Agent/Population work. Missing world handler or route semantics go to
Scenario work. Machine schema or validator gaps supported by a reduced
synthetic case go to the common framework.

## Completion evidence

Record source participant and occurrence counts, disposition totals, active
actor total, aggregation rows, identifier defects, registry row counts,
semantic-parent hashes, negative checks, manifest and inventory identities,
validation result, limitations, and next legal action.
