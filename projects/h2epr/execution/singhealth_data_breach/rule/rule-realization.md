# SingHealth Data Breach Rule realization

`DeclarativeRuleBackendV4` is selected through the typed backend registry and
reads the admitted decision table without branching on `H2EPR-0616` or
`singhealth_data_breach`. The authoritative environment validates a coordinate against one prestate,
removes opaque transport identity from decision observations, rejects every
distinct concurrent writer, and serializes idempotent writes semantically.

MASim remains the append-only transport, reducer, seal, and trace kernel. Model
and network access are denied. Event behavior belongs to configuration and the
Scenario Mechanism, not the generic runner.
