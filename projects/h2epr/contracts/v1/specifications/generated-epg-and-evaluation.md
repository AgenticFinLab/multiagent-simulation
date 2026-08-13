# Generated EPG and evaluation

The primary runtime output is a sealed simulation trace. A deterministic or
otherwise separately controlled compiler performs:

```text
trace records -> event detection -> episode grouping -> stage induction
              -> participant/action/outcome nodes -> temporal/causal edges
              -> Generated EPG
```

Every Generated EPG node and edge has a unique ID. Edge endpoints and
participant references resolve exactly once. Every provenance-index row points
to exactly one source trace record and binds the source trace artifact/hash.
The graph seal omits only its own seal value and operational metadata.

Evaluation is a separate offline namespace. It binds the eligible trace and
Generated EPG, then compares against a held-out real process. The reference is
not copied into runtime objects and its evidence provenance is not conflated
with simulation-log provenance.

The evaluation contract covers structural process fidelity, temporal
evolution, causal/mechanistic paths, participant behavior, outcomes,
traceability, hallucinated/extraneous behavior, and run-to-run stability and
diversity. Missing or inapplicable dimensions remain explicit rather than
being silently scored as zero or perfect. Synthetic Phase-0 fixtures prove the
contract shape; they are not scientific evaluation results.

