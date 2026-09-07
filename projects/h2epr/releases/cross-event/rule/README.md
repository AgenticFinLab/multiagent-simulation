# Cross-event Rule conformance

This release verifies 8 distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
| [H2EPR-0196](../../east_palestine_train_derailment/rule/) | `e30a8f3ee5455fb0e18b1c29d3bc76e2baee22c2159e0b568e191cbf37031b10` | `run.1e712ffee7592ef9081ae7b0` | 405 | 432 | 1210 |
| [H2EPR-0551](../../angola_yellow_fever_outbreak/rule/) | `6912a3ad8c7c37cffd31d545a9ace24f07ae94d76eab73e61b4d66996b3af9a3` | `run.0eb5b7a94ef55fc1bdddf756` | 826 | 866 | 2481 |
| [H2EPR-1031](../../baoneng_vanke_takeover_battle/rule/) | `06cdd22424efcb091e4b9850f38b5965ea222e652e3e7cec31ecf2282a7bb976` | `run.f53d0be85dbb76fc46dcdde4` | 823 | 861 | 2465 |
| [H2EPR-0481](../../samsung_galaxy_note7_battery_recall_crisis/rule/) | `9a34a37f7267f47c8b07b6b37c596968d6ecf8b38a83630c00fa940dcbb6479c` | `run.9eedae94989891d2df7519e8` | 1101 | 1152 | 3262 |
| [H2EPR-0616](../../singhealth_data_breach/rule/) | `52dbf7578a745e66cf8066f8743ac91f129deafb849b9fc92d6802fa32b0b5a5` | `run.26b57124e29d077af3150e02` | 782 | 820 | 2318 |
| [H2EPR-0288](../../panic_of_1907/rule/) | `ddde21973e04ea8d9757c54db7ac1fe96069f55af23dafa8536aad1400f03b98` | `run.7abdebdad001e59c7d01db71` | 1043 | 1084 | 3111 |
| [H2EPR-0170](../../tiktok_divestiture_and_national_security_dispute/rule/) | `f2f4e3262bf1612a01a89e30548aead483d620ee34cebb3a98010312fd908391` | `run.62bbe5fca5c9ff9df58411c1` | 1101 | 1142 | 3297 |
| [H2EPR-0892](../../lebanese_civil_war/rule/) | `3c47bb0d6f91b5c5d716c2fb509c44d6cb543b5ef83c8e38333dd3e4533bfac4` | `run.391644c9adfa091e6d2109e9` | 922 | 963 | 2789 |

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these 8 practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
