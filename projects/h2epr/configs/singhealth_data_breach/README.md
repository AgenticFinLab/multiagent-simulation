# SingHealth Data Breach configurations

This directory contains versioned Scenario Configurations and any later,
separately governed admission records for H2EPR-0616.

| Asset | Status | Role |
|---|---|---|
| [Scenario Configuration v0.1](scenario-configuration-v0.1/) | accepted, non-executable | sole H2EPR-0616 mechanism-coverage configuration authority |
| [Bounded configuration admission v0.1](configuration-admission-v0.1/) | static admission passed | exact format, source/canonical identity, release, semantic-reference, assembly, execution-boundary, and receipt evidence |

Scenario Configuration v0.1 assembles the complete semantic roster while
keeping every policy implementation unbound and execution eligibility false.
It is not a historical baseline, runtime bundle, simulation, calibration, or
validity result.

The bounded loader admits the exact release without changing its semantics or
execution eligibility. A separate
[SCM technical--operations--GCIO binding](../../agents/bindings/singhealth_data_breach/scm-technical-operations-gcio-v0.1/)
now projects only the selected lineage, and its
[lineage-conformance package](../../scenarios/singhealth_data_breach/lineage-conformance-v0.1/)
checks deterministic trace, seals, and replay. Neither package makes the full
configuration executable or supplies a full-roster runtime, simulation,
calibration, evaluation, or validity result.
