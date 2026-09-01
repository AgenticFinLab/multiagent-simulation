# H2EPR Roster Definition releases

This directory contains the accepted, event-qualified Roster Definition
releases. A roster release fixes the participant-product inventory and
non-participant dispositions consumed by consolidated mapping and later
semantic stages. Scenario, configuration, binding, execution, and run releases
remain under their owning responsibility directories.

## Current releases

| Event | Stable event slug | Accepted roster release |
|---|---|---|
| Panic of 1907 (`H2EPR-0288`) | `panic_1907` | [Roster Definition v0.1](panic_1907/roster-definition-v0.1/) |
| SingHealth Data Breach (`H2EPR-0616`) | `singhealth_data_breach` | [Roster Definition v0.1](singhealth_data_breach/roster-definition-v0.1/) |
| Samsung Galaxy Note7 Battery Recall Crisis (`H2EPR-0481`) | `samsung_note7_battery_recall` | [Roster Definition v0.1](samsung_note7_battery_recall/roster-definition-v0.1/) |

Each package contains a release `README.md`, `manifest.json`, and
`SHA256SUMS`. The manifest records the exact roster, evidence authorities,
participant models, interface records, semantic skeleton, dispositions, and
next-stage boundary accepted for that event. The checksum inventory covers
files owned by the release directory; downstream consumers separately pin the
manifest and semantic inputs they admit.

## Authority and evolution

Accepted roster releases are immutable as-of-release records. Current event
position and the recommended reading path belong to the
[event coordination entries](../events/README.md). A changed participant
identity, membership decision, semantic input, or disposition requires a
reviewed successor rather than an in-place rewrite. Editorial updates to
current guides do not alter an accepted roster release.

Event directories use lowercase snake-case slugs, release directories use
forms such as `v0.1`, public versions use semantic versions such as `0.1.0`,
and serialized format identities use forms such as `v0_1`.
