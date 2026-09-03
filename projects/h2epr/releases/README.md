# Run releases

A run release is a compact index into ignored custody. It pins one event
package, binding, backend, seed, H2EPR runtime, MASim kernel, manifest, trace,
terminal state, replay, Generated EPG, and deterministic comparison.

| Event | Backend | Current release |
|---|---|---|
| H2EPR-0288 Panic of 1907 | Rule | [release](panic_1907/rule/) |
| H2EPR-0616 SingHealth Data Breach | Rule | [release](singhealth_data_breach/rule/) |
| H2EPR-0481 Galaxy Note7 Recall | Rule | [release](samsung_note7_battery_recall/rule/) |

The shared [cross-event Rule receipt](cross-event/rule/) verifies identity
isolation, common contracts, deterministic closure, replay, graph coverage,
and terminal transport across all three events.

Raw traces and graphs are reproducible custody outputs, not tracked release
payloads.
