# Scenario definitions

Scenario assets own the benchmark event world: time, institutions, public and
private state, observation production, communication routes, authority,
concurrent effects, failure routing, termination, and generated annotations.
They do not choose participant intents.

Each current event directory contains:

- `scenario-definition.md`, the reader-facing semantic account;
- `interface-closure.md`, the assembly proof;
- `scenario-interface.json`, the actor/state/route boundary;
- `scenario-mechanism.json`, typed handlers, messages, effects, annotations,
  conflict policy, and termination;
- `manifest.json`; and
- `SHA256SUMS`.

| Event | Scenario |
|---|---|
| H2EPR-0288 Panic of 1907 | [current definition](panic_1907/) |
| H2EPR-0616 SingHealth Data Breach | [current definition](singhealth_data_breach/) |
| H2EPR-0481 Galaxy Note7 Recall | [current definition](samsung_note7_battery_recall/) |

Use [scenario-definition-template.md](scenario-definition-template.md),
[scenario-interface-closure-template.md](scenario-interface-closure-template.md),
and [scenario-mechanism-template.md](scenario-mechanism-template.md).
