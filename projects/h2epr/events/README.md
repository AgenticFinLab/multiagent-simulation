# Event packages

Each event directory publishes one backend-neutral package. It owns source
identity, participants, actorization, scenario semantics, shared
configuration, and the claim boundary used by every backend.

| Event | Package | Rule | LLM | RuleLLM |
|---|---|---|---|---|
| H2EPR-0288 Panic of 1907 | [package](panic_1907/package/) | implemented | planned | planned |
| H2EPR-0616 SingHealth Data Breach | [package](singhealth_data_breach/package/) | implemented | planned | planned |
| H2EPR-0481 Galaxy Note7 Recall | [package](samsung_note7_battery_recall/package/) | implemented | planned | planned |

The packages share one compiler, loader, Rule backend, environment, runtime,
replay adapter, Generated EPG compiler, publisher, and conformance contract.
Participant, state, mechanism, route, timeline, and Rule vocabulary remain
event-local declarative assets.

[current-events.json](current-events.json) is the machine discovery registry.
Add a row only after every referenced current path exists and validates; no
common Python event tuple should change.

Run traces, model outputs, external research notes, and backend-specific
outcomes do not belong here.
