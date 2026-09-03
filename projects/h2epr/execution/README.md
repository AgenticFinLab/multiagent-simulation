# Backend realization

This directory owns reviewed executable projections of admitted semantic
assets. A realization maps every configured decision unit and intent to one
implemented backend without changing roster, scenario, observation,
authority, or environment meaning.

Current releases live at `<event>/<backend>/`. Run identities and evidence
live under [releases/](../releases/).

Rule realization records deterministic policy and exact implementation
sources. A future LLM realization must record prompt projection, parser, model
controls, retries, and typed failures. RuleLLM additionally owns constraint,
repair, rejection, and fallback semantics.

| Event | Current realization |
|---|---|
| H2EPR-0288 Panic of 1907 | [Rule](panic_1907/rule/) |
| H2EPR-0616 SingHealth Data Breach | [Rule](singhealth_data_breach/rule/) |
| H2EPR-0481 Galaxy Note7 Recall | [Rule](samsung_note7_battery_recall/rule/) |

All three bind the same registered `DeclarativeRuleBackend`. Event behavior
resides in admitted mechanism and Rule-configuration assets.
