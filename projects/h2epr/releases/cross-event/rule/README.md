# Cross-event Rule conformance

This release verifies 2 distinct H2EPR event packages on one Rule
contract, one runtime source inventory, and one read-only MASim kernel
inventory.

| Event release | Package SHA-256 | Run | Trace | Nodes | Edges |
|---|---|---|---:|---:|---:|
| [H2EPR-0196](../../east_palestine_train_derailment/rule/) | `f1f30080e857417ed06cb45b3cbb25b37ea5a7fac72339978185f37dd657e297` | `run.4cc6658590d5447313ff426b` | 405 | 432 | 1056 |
| [H2EPR-0551](../../angola_yellow_fever_outbreak/rule/) | `d6456af798b2593d264b18f7b1a4f0bf360682cfe36a26965ed3d29dbfe5c2b6` | `run.2c5f37a8e456f99bdb1eff02` | 826 | 866 | 2147 |

`conformance-receipt.json` records distinct event identities, the shared
package and backend-status contracts, equal H2EPR and MASim inventories, equal
output roles, replay/trace/transport closure, and common claim exclusions. It
establishes cross-event engineering closure for these 2 practices,
not historical fit, held-out performance, calibration, causality, scientific
validity, or universal generality.
