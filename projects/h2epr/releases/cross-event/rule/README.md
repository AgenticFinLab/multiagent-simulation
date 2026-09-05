# Cross-event Rule conformance

This release verifies 2 distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
| [H2EPR-0196](../../east_palestine_train_derailment/rule/README.md) | `2dfca76550db4a9d68db3cb7e03336e39bbddafe15f575ec9109d1096014330e` | `run.af195d6305dad7006bc55759` | 405 | 432 | 1210 |
| [H2EPR-0551](../../angola_yellow_fever_outbreak/rule/README.md) | `938f441d834a8c928fb64ec12eb6e3692ef6e00c91d06016ba681f8d6f540e3d` | `run.c8e90196fadcf5a18b9b9f9a` | 826 | 866 | 2481 |

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these 2 practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
