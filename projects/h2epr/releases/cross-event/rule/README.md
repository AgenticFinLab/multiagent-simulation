# Cross-event Rule conformance

This release verifies 4 distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
| [H2EPR-0196](../../east_palestine_train_derailment/rule/) | `2dfca76550db4a9d68db3cb7e03336e39bbddafe15f575ec9109d1096014330e` | `run.293a2a817e42f1ea0578dc45` | 405 | 432 | 1210 |
| [H2EPR-0551](../../angola_yellow_fever_outbreak/rule/) | `938f441d834a8c928fb64ec12eb6e3692ef6e00c91d06016ba681f8d6f540e3d` | `run.b21a925f5048915d999d5433` | 826 | 866 | 2481 |
| [H2EPR-1031](../../baoneng_vanke_takeover_battle/rule/) | `f1b68baa1d90045eb87a8309eb4a2ad606a00ee1d00bb2b53709abe82062b83f` | `run.6f6408d11b70b472f33444ae` | 823 | 861 | 2465 |
| [H2EPR-0481](../../samsung_galaxy_note7_battery_recall_crisis/rule/) | `cbcb8e37e6b3cfa8c9ffe83055dced7ed948146c60bb35046070c157f3733d5c` | `run.88051af3adbca475637d35ec` | 1101 | 1152 | 3262 |

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these 4 practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
