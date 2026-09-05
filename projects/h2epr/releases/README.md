# Run releases

A tracked run release is a compact, independently verified index into ignored
raw custody. It pins the package, binding, backend, seed or model controls,
runtime and MASim source inventories, trace, seals, terminal state, replay,
Generated EPG, determinism or variation evidence, and custody inventory.

Only releases referenced by
[events/current-events.json](../events/current-events.json) are current.
Cross-event evidence is published only when at least two independently
accepted event runs share the declared contract.

Raw traces and graphs remain under ignored custody. A producer's success flag,
self-hash, or outer checksum is never sufficient for publication; the
publisher rederives semantic lineage, replay, graph coverage, and deterministic
Rule output.

Current run releases are [H2EPR-0196 East Palestine Train Derailment,
Rule](east_palestine_train_derailment/rule/), [H2EPR-0551 Angola Yellow
Fever Outbreak of 2016, Rule](angola_yellow_fever_outbreak/rule/), and
[H2EPR-1031 Baoneng–Vanke Takeover Battle, Rule](baoneng_vanke_takeover_battle/rule/).
The [three-event Rule conformance release](cross-event/rule/) covers the complete
current registry.
