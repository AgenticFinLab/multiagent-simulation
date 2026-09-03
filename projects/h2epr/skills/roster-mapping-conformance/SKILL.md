---
name: roster-mapping-conformance
description: Close the full Draft roster, actorization losses, and observation/intent/lifecycle registries before package compilation.
---

# Roster mapping conformance

Read [references/guide.md](references/guide.md) for extraction rules,
disposition choices, cardinality accounting, registry closure, negative cases,
and the release evidence record.

## Procedure

1. Extract every source participant occurrence, exact observed name, type,
   role, appearance anchor, count, and identifier gap from the allowed Draft.
2. Give each participant one disposition and one rationale. Record many-to-one
   aggregation and source-to-runtime cardinality explicitly.
3. Require every active actor to resolve to one Agent Definition or Population
   Model and one participant-interface row. Publish a semantic index that pins
   the human parent path, hash, source IDs, and exact Draft anchors.
4. Close observation producers/consumers, intent targets/handlers, lifecycle
   transitions, routes, state owners, and authority.
5. Verify that the portable package projection is loss-accounted and adds no
   behavior absent from the semantic parents.
6. Seal roster, actor map, registries, manifest, and checksums.

## Negative checks

Reject missing/duplicate participants, changed source names/types/roles,
fabricated IDs, unknown actors,
unresolved semantic parents, action-space widening, hidden aggregation,
orphan observations/intents, and actor names used as authority checks.
