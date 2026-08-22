# H2EPR scenarios

This directory contains the public
[Event Scenario Definition template](scenario-definition-template.md),
its derived
[Scenario interface closure template](scenario-interface-closure-template.md),
event-owned scenario semantics and policies, and bounded integration paths.
The [`event-scenario-design`](../skills/event-scenario-design/SKILL.md) Skill
turns an accepted roster/release into a reviewed Scenario Definition before a
policy implementation or run is authorized. The interface-closure companion
reconciles every released observation, intent, lifecycle, authority, and
resource requirement without expanding the scholarly scenario into a machine
mapping.

Domain-neutral Definition loading and Contracts V1 carrier checks remain under
`src/h2epr/`; event identities and historical assumptions stay here.

The current [`panic_1907/`](panic_1907/) slice is a deterministic, non-Ray
conformance path for the first two Agent Definitions. Its semantic skeleton is
an accepted precursor, not yet the full Event Scenario Definition.
