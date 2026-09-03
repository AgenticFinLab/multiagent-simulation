# Population models

A Population Model represents an aggregate or heterogeneous choice unit when
the dataset and simulation boundary do not support one named Agent per member.
It must state the unit of choice, inclusion and exclusion, aggregation,
weighting, supported heterogeneity, and the condition that would split or
promote a unit.

Models live at `models/<event>/` and use
[population-model-template.md](population-model-template.md). Counts,
distributions, weights, seeds, and selected values belong to configuration.
When the dataset exposes no microdata, the model records that limitation
instead of inventing individual trajectories.

Current models are reached through the event rows in
[events/current-events.json](../events/current-events.json).
