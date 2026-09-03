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
[events/current-events.json](../events/current-events.json). H2EPR-0196 uses
the [East Palestine residents](models/east_palestine_train_derailment/east_palestine_residents.md)
Population Model. H2EPR-0551 uses the [Angola-DRC affected
residents](models/angola_yellow_fever_outbreak/angola_drc_affected_residents.md)
Population Model, which records the Draft's changing P_3 geographic scope.
