# Population models

A Population Model represents an aggregate or heterogeneous choice unit when
the benchmark does not support, or the simulation does not require, one named
Agent per member. It must not assign an invented personality, balance, belief,
weight, or authority to an entire historical group.

Models live at `models/<event>/`. Runtime actor count, sampling, distributions,
and selected values belong to configuration. The roster records whether a
population is one aggregate runtime unit or several instantiated units.

Use [population-model-template.md](population-model-template.md). Agent and
Population products share the same observation, intent, lifecycle, authority,
and environment-result boundaries.

| Event | Current Population Models |
|---|---|
| H2EPR-0288 Panic of 1907 | [five aggregate cohorts](models/panic_1907/) |
| H2EPR-0616 SingHealth Data Breach | None; affected patients remain world state because the exposed process assigns them no autonomous decision |
| H2EPR-0481 Galaxy Note7 Recall | [global and China consumer cohorts](models/samsung_note7_battery_recall/) |
