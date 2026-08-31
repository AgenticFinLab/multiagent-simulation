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

The current [`panic_1907/`](panic_1907/) directory contains the accepted
[Event Scenario Definition v0.1](panic_1907/definition-v0.1/), the frozen
two-role reference path, and the completed
[KT--NBC--NYCH conformance closeout](panic_1907/lineage-conformance-v0.1/).
Its accepted Scenario Configuration is kept separately under
[`configs/panic_1907/`](../configs/panic_1907/) so event-world meaning and one
declared-purpose instantiation remain distinct.
The earlier semantic skeleton remains the Roster-production precursor recorded
by the accepted Definition; it is not a competing scenario authority.

The [`singhealth_data_breach/`](singhealth_data_breach/) directory contains the
accepted
[Event Scenario Definition v0.1](singhealth_data_breach/definition-v0.1/),
the completed
[SCM technical--operations--GCIO conformance closeout](singhealth_data_breach/lineage-conformance-v0.1/),
and its stable Roster-production precursor, the
[event semantic skeleton v0.2](singhealth_data_breach/semantic-skeleton.md).
The conformance path exercises only four selected intents from the accepted
binding. The complete nine-product Scenario Configuration remains
non-executable.

The [`samsung_note7_battery_recall/`](samsung_note7_battery_recall/) directory
contains the accepted authoring-window
[Event Scenario Definition v0.1](samsung_note7_battery_recall/definition-v0.1/)
and its stable participant-production precursor, the
[event semantic skeleton](samsung_note7_battery_recall/semantic-skeleton.md).
The Definition closes four Agent and four Population products across product,
remedy, recall, transport, and consumer decision boundaries. Its qualitative
configuration remains non-executable after static admission.
