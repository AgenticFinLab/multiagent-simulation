# Scenario and backend configuration

Configuration selects exact executable values from admitted semantic domains.
It does not redefine participants or scenario meaning.

| Path | Identity boundary | Typical contents |
|---|---|---|
| `<event>/shared/` | Included in the backend-neutral package | timeline, opening state, routes, observation and termination settings |
| `<event>/backends/<backend>/` | Sealed by that backend binding | Rule rows, model controls, prompt or constraint settings |

Each release includes a design account, machine configuration, exhaustive
top-level provenance coverage or typed exemptions, an independently derived
admission receipt, a manifest, and checksums. Credentials and mutable service
endpoints are never tracked.

Use [scenario-configuration-template.md](scenario-configuration-template.md).
Current configurations are listed indirectly by
[events/current-events.json](../events/current-events.json).
