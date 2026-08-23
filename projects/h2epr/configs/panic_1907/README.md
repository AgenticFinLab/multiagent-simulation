# Panic of 1907 configurations

This directory separates the accepted versioned research configuration from
the earlier engineering canaries.

| Asset | Status | Role |
|---|---|---|
| [Scenario Configuration v0.1](scenario-configuration-v0.1/) | accepted, non-executable | sole versioned H2EPR-0288 mechanism-coverage configuration authority |
| [rule_canary_v1.json](rule_canary_v1.json) | frozen engineering reference | G3 Rule runtime canary input |
| [compiler_canary_v1.json](compiler_canary_v1.json) | frozen engineering reference | G4 compiler canary input |

The canaries do not supply actors, dates, quantities, policies, or defaults
to Scenario Configuration v0.1. The accepted configuration remains
fail-closed until a separately reviewed and authorized loader, policy binding,
and exact carrier projection exist.
