---
name: generated-process-analysis
description: Read a sealed H2EPR Generated EPG and trace, then make bounded simulation-only or backend-comparison claims.
---

# Generated process analysis

## Procedure

1. Pin release, package, backend, realization, configuration, run, trace,
   replay, graph, exposure, and analysis scope.
2. Read the generated trajectory before any target comparison: opening state,
   action/message sequence, rejected/partial intents, state transitions,
   lifecycles, turning points, generated stages, and terminal state.
3. Confirm graph trace coverage first. Traverse every trace record, graph node,
   and graph edge; validate endpoints and source-trace references. Record exact
   counts by class. Read observation, decision, disposition, delta, annotation,
   stage-entry, tick-seal, and run-seal nodes rather than sampling actions.
4. Classify terminal values as closed lifecycles, persistent outcomes, or
   deliberately open states. Never synthesize a closure absent from the
   admitted input and mechanism.
5. Cite trace/graph record IDs for direct facts. Label mechanism attribution
   and interpretation separately.
6. If comparing backends, first prove package/runtime parity and then compare
   decision and process differences.
7. If making a Draft-facing description, state full-Draft exposure and avoid an
   unbiased score claim.
8. Route findings to participant semantics, configuration, backend,
   environment, runtime, compiler, or report. Change shared assets only after a
   reusable gap is demonstrated.

The analysis cannot establish historical fit, calibration, causality, policy
effectiveness, scientific validity, or generality without a separate protocol.
