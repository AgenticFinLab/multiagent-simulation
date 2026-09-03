# Participant assets

This directory owns the source roster, actorization decision, named Agent
Definitions, and backend-neutral participant interfaces.

| Path | Responsibility |
|---|---|
| `rosters/<event>/` | Every Draft participant occurrence and its disposition |
| `defines/<event>/` | One semantic parent for each named decision unit |
| `interfaces/<event>/` | Observation, intent, lifecycle, and actor capability registries |
| [agent-definition-template.md](agent-definition-template.md) | Required human-readable Definition modules |
| [WORKFLOW.md](WORKFLOW.md) | Participant-stage handoffs and review |

A Definition owns identity, information, authority, admissible choices,
uncertainty, and limitations. Exact Rule rows, model prompts, decoding
settings, runtime IDs, and successful outcomes belong elsewhere. Population
choice units live under [populations/](../populations/).

Current event assets are discoverable only through
[events/current-events.json](../events/current-events.json). Current
participant releases are [H2EPR-0196 East Palestine Train
Derailment](rosters/east_palestine_train_derailment/) and [H2EPR-0551 Angola
Yellow Fever Outbreak of 2016](rosters/angola_yellow_fever_outbreak/). Empty
directories are not evidence of an accepted participant release.
