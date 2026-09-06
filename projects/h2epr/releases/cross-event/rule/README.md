# Cross-event Rule conformance

This release verifies 8 distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
| [H2EPR-0196](../../east_palestine_train_derailment/rule/) | `897f82abe5197dab4e32c6de9e477d77ff74b6709292d096c83c8eebe6534684` | `run.c81b945d591680e9f1fbaf03` | 405 | 432 | 1210 |
| [H2EPR-0551](../../angola_yellow_fever_outbreak/rule/) | `40dd6cf24ad8c162f861e476cc5665ab8260738a11d4d4dd2157bac46b9e22e7` | `run.8fca27c569b81c55eab3a256` | 826 | 866 | 2481 |
| [H2EPR-1031](../../baoneng_vanke_takeover_battle/rule/) | `06cdd22424efcb091e4b9850f38b5965ea222e652e3e7cec31ecf2282a7bb976` | `run.f53d0be85dbb76fc46dcdde4` | 823 | 861 | 2465 |
| [H2EPR-0481](../../samsung_galaxy_note7_battery_recall_crisis/rule/) | `6b37fcffdb633d9696cc757d71e0fe60d62c7cd6e9ac074862f8281f346a48fe` | `run.9120d67d5fe0c22266400e21` | 1101 | 1152 | 3262 |
| [H2EPR-0616](../../singhealth_data_breach/rule/) | `52dbf7578a745e66cf8066f8743ac91f129deafb849b9fc92d6802fa32b0b5a5` | `run.26b57124e29d077af3150e02` | 782 | 820 | 2318 |
| [H2EPR-0288](../../panic_of_1907/rule/) | `f657f2857d9e4d56cc18b882990f98f0fe12dccbd609252dd3d6858bf87c648f` | `run.ae8aa2842bfd4d33c481fc78` | 1043 | 1084 | 3111 |
| [H2EPR-0170](../../tiktok_divestiture_and_national_security_dispute/rule/) | `13ea21a15889014555de7f3c8c6603325a3fb42525fd538492f2e996fc768a05` | `run.2a983fc27557518b15624c54` | 1101 | 1142 | 3297 |
| [H2EPR-0892](../../lebanese_civil_war/rule/) | `3c47bb0d6f91b5c5d716c2fb509c44d6cb543b5ef83c8e38333dd3e4533bfac4` | `run.391644c9adfa091e6d2109e9` | 922 | 963 | 2789 |

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these 8 practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
