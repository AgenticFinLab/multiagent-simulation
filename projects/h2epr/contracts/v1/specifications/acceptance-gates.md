# Acceptance gates

Contract acceptance is layered:

1. JSON Schema validates each closed object shape.
2. Cross-object validators close identity, parent cardinality, foreign keys,
   time, provenance, hashes, trace references, and seal sets.
3. Static checks enforce offline schema resolution and repository boundaries.
4. Deterministic replay proves the same case IDs and outcomes in fresh runs.

Phase-0 synthetic acceptance does not substitute for later execution evidence.
Before a runtime entry can be exercised, the canonical environment and direct
dependencies must pass readiness checks. Before a strict scientific run, the
external anchor, time split, roster, clean builder, prefix projection, and
suffix-absence receipts must be frozen independently.

Later gates must separately prove scheduler/barrier behavior, authoritative
world reduction, trace writing, compiler closure, offline evaluator isolation,
H2EPR-0288 deterministic replay, clean-build strict rerun, and H2EPR-0616
domain transfer. The additive H2EPR-0481 successor must independently close
the same execution, replay, graph, custody, and claim contracts without
rewriting either accepted predecessor. A waiver may document a noncritical
limitation but cannot waive Reference isolation, future-information leakage,
trace integrity, or scientific lineage.
