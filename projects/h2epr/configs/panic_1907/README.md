# Panic of 1907 configurations

This directory separates the accepted versioned research configuration from
the earlier engineering canaries.

| Asset | Status | Role |
|---|---|---|
| [Scenario Configuration v0.1](scenario-configuration-v0.1/) | accepted, non-executable | sole versioned H2EPR-0288 mechanism-coverage configuration authority |
| [Bounded configuration admission v0.1](configuration-admission-v0.1/) | static admission passed | exact schema, source/canonical identity, reference, assembly, failure-class and receipt evidence; no execution authority |
| [rule_canary_v1.json](rule_canary_v1.json) | frozen engineering reference | G3 Rule runtime canary input |
| [compiler_canary_v1.json](compiler_canary_v1.json) | frozen engineering reference | G4 compiler canary input |

The canaries do not supply actors, dates, quantities, policies, or defaults
to Scenario Configuration v0.1. The bounded loader admits the exact
configuration as a non-executable semantic input. A separately versioned
[KT--NBC--NYCH E6 binding](../../agents/bindings/panic_1907/kt-nbc-nych-v0.1/)
now projects and binds only that lineage. It does not edit this configuration,
clear its `execution_eligible=false` boundary, or bind the other 13 actors.
The separate [E7 closeout](../../scenarios/panic_1907/lineage-conformance-v0.1/)
revalidates that boundary while adding only negative conformance and a fixed
trace/replay receipt.
