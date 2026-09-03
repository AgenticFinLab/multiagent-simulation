---
name: event-agent-batch
description: Produce and review all Agent Definitions and Population Models for one accepted event roster as a coherent batch.
---

# Event participant batch

Read [references/guide.md](references/guide.md) for batching strategy,
event-wide ledgers, cross-participant checks, review independence, and the
release-ready handoff.

## Procedure

1. Freeze the Source Profile, simulation window, roster candidate, actor IDs,
   and semantic template revision.
2. Partition active decision units into named Agents and populations; keep
   context, world state, processes, and outside-window entities visible.
3. Produce Definitions/Models in bounded groups while maintaining one shared
   observation, intent, lifecycle, authority, and resource vocabulary.
4. Review each product, then review the batch for duplicated state, conflicting
   authority, missing counterparties, incompatible intent names, and hidden
   assumptions.
5. Publish exact human semantic-parent paths, hashes, source IDs, and Draft
   anchors in the participant semantic index; then seal the interface release.

The batch has no minimum number of files or review rounds. It closes when every
active runtime decision unit has one accepted semantic parent and all
cross-participant interfaces agree.
