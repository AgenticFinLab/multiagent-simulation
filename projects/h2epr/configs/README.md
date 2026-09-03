# Scenario and backend configurations

Configuration selects exact executable values from admitted semantic assets.
It is not another participant or scenario definition.

| Path | Included in backend-neutral package identity | Examples |
|---|---:|---|
| `<event>/shared/` | yes | timeline, opening state, routes, environment selections |
| `<event>/backends/<backend>/` | no; sealed by the binding | Rule rows, model identity, decoding, prompt or admission policy |

Credentials and mutable service endpoints are never tracked. A current
configuration release contains a design note, machine configuration,
exhaustive provenance coverage, admission receipt, manifest, and checksums.
Coverage plus typed exemptions must exactly partition its top-level settings.

| Event | Shared | Rule |
|---|---|---|
| H2EPR-0288 Panic of 1907 | [configuration](panic_1907/shared/) | [Rule settings](panic_1907/backends/rule/) |
| H2EPR-0616 SingHealth Data Breach | [configuration](singhealth_data_breach/shared/) | [Rule settings](singhealth_data_breach/backends/rule/) |
| H2EPR-0481 Galaxy Note7 Recall | [configuration](samsung_note7_battery_recall/shared/) | [Rule settings](samsung_note7_battery_recall/backends/rule/) |

Admission receipts are independently rederived during package compilation; a
correct self-hash without matching semantic evidence is rejected.
