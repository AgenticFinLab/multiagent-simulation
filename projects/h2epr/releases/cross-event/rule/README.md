# Cross-event Rule conformance

This release verifies 8 distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
| [H2EPR-0196](../../east_palestine_train_derailment/rule/) | `2dfca76550db4a9d68db3cb7e03336e39bbddafe15f575ec9109d1096014330e` | `run.293a2a817e42f1ea0578dc45` | 405 | 432 | 1210 |
| [H2EPR-0551](../../angola_yellow_fever_outbreak/rule/) | `938f441d834a8c928fb64ec12eb6e3692ef6e00c91d06016ba681f8d6f540e3d` | `run.b21a925f5048915d999d5433` | 826 | 866 | 2481 |
| [H2EPR-1031](../../baoneng_vanke_takeover_battle/rule/) | `f1b68baa1d90045eb87a8309eb4a2ad606a00ee1d00bb2b53709abe82062b83f` | `run.6f6408d11b70b472f33444ae` | 823 | 861 | 2465 |
| [H2EPR-0481](../../samsung_galaxy_note7_battery_recall_crisis/rule/) | `cbcb8e37e6b3cfa8c9ffe83055dced7ed948146c60bb35046070c157f3733d5c` | `run.88051af3adbca475637d35ec` | 1101 | 1152 | 3262 |
| [H2EPR-0616](../../singhealth_data_breach/rule/) | `9d17581f17e994b2aba4252c8a7457c7b03ecd8f3e9003c83268bf954664a16c` | `run.5db9a323beb010817c521f46` | 782 | 819 | 2317 |
| [H2EPR-0288](../../panic_of_1907/rule/) | `cc5229cd7f77b93305450a50a068817e7d8ac786c2f2d2cde9a132749808e030` | `run.1b16d1949b2a609181e1d06d` | 1043 | 1084 | 3111 |
| [H2EPR-0170](../../tiktok_divestiture_and_national_security_dispute/rule/) | `667de386997afde4f415f0b6ea491138acce8bfa081150bcfb88f156f67aa7fd` | `run.2cb97929423c768bbd0cf72d` | 1101 | 1142 | 3297 |
| [H2EPR-0892](../../lebanese_civil_war/rule/) | `c806337186f2d7b51c5d1183b4ece5f28b2b2282b12f3521d5c2c86a9ecd475e` | `run.108a8c5193199df3dc7e5fa8` | 922 | 963 | 2789 |

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these 8 practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
