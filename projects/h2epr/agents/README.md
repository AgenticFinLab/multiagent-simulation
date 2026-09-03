# Participant definitions

This directory owns the backend-neutral account of who may decide in an H2EPR
event. Named organizational or individual decision interfaces are separated
from aggregate Population Models and scenario-owned processes.

An Agent Definition states identity, representation loss, observable
information, authority, admissible intents, parameter domains, worked cases,
and limitations. It does not choose Rule rows, model settings, or realized
outcomes.

## Publication surfaces

| Path | Responsibility |
|---|---|
| [agent-definition-template.md](agent-definition-template.md) | Stable reading order for a named decision unit |
| `defines/<event>/` | Current Agent Definitions |
| `rosters/<event>/` | Complete Draft roster and actorization map |
| `interfaces/<event>/` | Observation, intent, lifecycle, and participant registries |

Population choice units live under [populations/](../populations/). The event
package compiles these products into a portable projection without becoming a
second behavioral authority.

## Current events

| Event | Definitions | Roster | Interface |
|---|---|---|---|
| H2EPR-0288 Panic of 1907 | [definitions](defines/panic_1907/) | [roster](rosters/panic_1907/) | [interface](interfaces/panic_1907/) |
| H2EPR-0616 SingHealth Data Breach | [definitions](defines/singhealth_data_breach/) | [roster](rosters/singhealth_data_breach/) | [interface](interfaces/singhealth_data_breach/) |
| H2EPR-0481 Galaxy Note7 Recall | [definitions](defines/samsung_note7_battery_recall/) | [roster](rosters/samsung_note7_battery_recall/) | [interface](interfaces/samsung_note7_battery_recall/) |

Definitions may name a construct, unit, category, range, and behavioral
consequence. Exact values belong to shared configuration or backend
realization so Rule, LLM, and RuleLLM can share participant semantics without
being forced to make the same decisions.
