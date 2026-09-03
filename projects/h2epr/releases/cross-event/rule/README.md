# Cross-event Rule conformance

This release verifies 3 distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
| [H2EPR-0288](../../panic_1907/rule/) | `185797e8e4987b3f485a246569039514a415114ac5d05dc4005b696ea8f115ee` | `run.e37134e71ff5370299ec8f78` | 813 | 851 | 2074 |
| [H2EPR-0616](../../singhealth_data_breach/rule/) | `96ab8667be1a283a0bb2488aadeea27335453bc07a11b98c6c0283e2d72c3e3f` | `run.9ee80f5e54b70d8b041b96b2` | 438 | 466 | 1131 |
| [H2EPR-0481](../../samsung_note7_battery_recall/rule/) | `30e615792ef9f1b035e2d3c6f20c1b88cfd21f13ed0ff796d3c6c4f5c47b3b2e` | `run.9493ae39f4127dc9e84172f3` | 729 | 772 | 1872 |

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these 3 practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
