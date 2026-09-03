# Samsung Galaxy Note7 Battery Recall Rule realization

`DeclarativeRuleBackendV4` is selected through the typed backend registry and
reads the admitted decision table without branching on `H2EPR-0481` or
`samsung_note7_battery_recall`. The authoritative environment validates a coordinate against one prestate,
removes opaque transport identity from decision observations, rejects every
distinct concurrent writer, and serializes idempotent writes semantically.

MASim remains the append-only transport, reducer, seal, and trace kernel. Model
and network access are denied. Event behavior belongs to configuration and the
Scenario Mechanism, not the generic runner.
