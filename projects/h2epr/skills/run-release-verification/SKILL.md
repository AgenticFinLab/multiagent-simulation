---
name: run-release-verification
description: Materialize an admitted H2EPR backend, verify trace/seals/replay/Generated EPG, and publish a compact reproducibility release.
---

# Run release verification

Read [references/guide.md](references/guide.md) for custody layout, trace and
seal invariants, replay/graph verification, deterministic and model evidence,
tamper cases, and release disposition.

## Procedure

1. Record clean Git state, exact package/binding/realization/configuration,
   seed/model settings, runtime/kernel identities, and fresh custody paths.
2. Materialize without mutating tracked inputs.
3. Validate one sealed pre-state per tick, actor decision coverage, typed
   intents, transport, dispositions, authoritative deltas, trace chain, tick
   seals, and run seal.
4. Replay from opening state and require exact terminal state.
5. Compile Generated EPG from trace only; require one first-class node per
   trace record, exact trace-ID coverage, source-trace hash, endpoint closure,
   and graph seal.
6. For deterministic backends, run a second fresh materialization and compare
   all eight scientific outputs plus the run receipt byte for byte. Perturb
   only run identity, derive generated-ID invariance independently, and
   hash-link that receipt into the determinism receipt.
7. For model backends, pin model/prompt/decoding provenance and report
   variation; do not assert determinism without evidence.
8. Require zero unresolved transport. Publish the compact release, checksums,
   exact command, counts, formal ignored-custody locator and inventory hash,
   and claim limits.
9. Treat producer receipts and seals as claims. At publication, rederive
   decision-to-intent and disposition-to-delta lineage, recompile Generated EPG
   from package, manifest, and trace, and rematerialize deterministic Rule
   candidates in temporary custody. Require byte equality before promotion.

Do not promote on trace/seal/replay/graph failure, custody reuse, unexplained
variation, unpinned model inputs, a failed checksum, or a fully resealed result
that cannot be independently reproduced.
