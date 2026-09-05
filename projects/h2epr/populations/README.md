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
H2EPR-1031's [actor map](../agents/rosters/baoneng_vanke_takeover_battle/)
selects eight named Agents and no Population. That explicit zero is valid;
directory symmetry does not require inventing an unsupported aggregate choice.
H2EPR-0481 uses three aggregate choice units: [global purchasers, mainland test-unit
owners and mainland regular purchasers](models/samsung_galaxy_note7_battery_recall_crisis/).
H2EPR-0616 keeps its affected-patient cohort as explicit initial context because
the Draft exposes no patient-authored choice; it therefore has no current
Population Model.
H2EPR-0288 uses three aggregate choice units: [general public depositors, New
York trust companies and NYCH member banks](models/panic_of_1907/). Each model
owns a bounded group-level record without inventing individual trajectories,
unanimity, weights or financial quantities.
H2EPR-0170 uses one [state and legislative restriction
Population](models/tiktok_divestiture_and_national_security_dispute/state_and_legislative_restriction_population.md)
for the Draft's aggregate state, campus and proposal records. It does not imply
uniform members, counts, weights or individual policy trajectories.
