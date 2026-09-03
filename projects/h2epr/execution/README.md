# Backend realizations

A realization maps every active decision unit and permitted intent to one
implemented backend. It pins the backend configuration, decision interface,
implementation sources, and typed failure routing without changing shared
event semantics.

Current releases live at `<event>/<backend>/`. Rule uses the registered
declarative implementation. LLM and RuleLLM remain unavailable until their
implementation, provenance, parser, retry, and failure contracts exist.

Use [backend-realization-template.md](backend-realization-template.md) and
[execution-cycle-closeout-template.md](execution-cycle-closeout-template.md).
Accepted realizations are reached through
[events/current-events.json](../events/current-events.json). The current Rule
realizations are [H2EPR-0196 East Palestine Train
Derailment](east_palestine_train_derailment/rule/) and [H2EPR-0551 Angola
Yellow Fever Outbreak of 2016](angola_yellow_fever_outbreak/rule/).
