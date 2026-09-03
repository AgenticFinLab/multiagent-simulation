# SingHealth data breach Rule simulation reading

## Run identity and reading boundary

| Item | Identity |
|---|---|
| Event | `H2EPR-0616` |
| Run | `run.9ee80f5e54b70d8b041b96b2` |
| Package | `96ab8667be1a283a0bb2488aadeea27335453bc07a11b98c6c0283e2d72c3e3f` |
| Rule binding | `0a386a726de655e4596d6f38651129a2dfd40b9141d05d0b502bfe2e747ca7fe` |
| Trace | `e8b084280da5a790960b78774e63f3a5bf7cd1d57702437eb0a6cdbaf99a42d8` |
| Final state | `29f4b5df4d8e046723a6e8a9ea21fcb6b5812c52f66eed2870a79c420a618b8a` |
| Generated EPG | `fcc6ecf944ab2dfac812d3d63ddad4b9e7c6bc2e38276ac2122224c74d318e62` |
| Compact release | [`releases/singhealth_data_breach/rule`](../../../releases/singhealth_data_breach/rule/) |

Construction used only the event's declared `event_spec`, `frozen_evidence`,
and fully exposed `draft_epg`. The report reads the generated Rule process; it
does not compare that process with external history or a hidden target.

## Complete-output coverage

The reading traversed all 438 trace records, 466 graph nodes, and 1,131 graph
edges. Every endpoint and source-trace reference resolves, all 438 trace IDs
are represented in the Generated EPG, every action and message disposition is
accounted for, and terminal transport custody is empty.

The graph contains one generated event, 11 logical coordinates, eight
participants, eight state entities, and 438 trace-record nodes. Principal edge
classes include 438 `occurs_at`, 106 `disposes`, 88 each of `based_on`,
`decided_by`, `emitted_by`, `observes_for`, and `projects`, plus 15 state
changes, nine message-successor chains, four stage entries, and 12 seals.

## Direct generated facts

The opening state has no recorded intrusion, exfiltration, detection, public
disclosure, inquiry, penalty, reform completion, or attribution. The table
covers every coordinate. Trace suffixes refer to
`trace.run.9ee80f5e54b70d8b041b96b2.*`.

| Tick and trace range | Generated action and resulting transition |
|---|---|
| 01, `00000000–00000037` | Whitefly establishes persistent access; intrusion status becomes `persistent`. |
| 02, `00000038–00000074` | Whitefly exfiltrates patient data; theft status becomes `exfiltrated`. |
| 03, `00000075–00000113` | SingHealth detects suspected intrusion and queues an incident alert to IHiS. |
| 04, `00000114–00000156` | IHiS verifies the incident and contains access, receives the alert, and queues verified-scope messages to SingHealth and MOH. |
| 05, `00000157–00000197` | Lee Hsien Loong publishes a leadership statement, MOH announces the breach, and SingHealth notifies affected patients. Both verified-scope messages arrive. |
| 06, `00000198–00000236` | MOH establishes the inquiry and queues its mandate to the Committee of Inquiry. |
| 07, `00000237–00000277` | The Committee produces root-cause findings, receives its mandate, and queues findings to MOH and PDPC. |
| 08, `00000278–00000320` | PDPC issues penalties, receives the findings, and queues penalty notices to SingHealth and IHiS. |
| 09, `00000321–00000361` | IHiS implements operator improvements, MOH activates oversight, and SingHealth implements owner reforms after both penalty notices arrive. |
| 10, `00000362–00000400` | Symantec publishes Whitefly attribution and queues the attribution report to SingHealth. |
| 11, `00000401–00000437` | The terminal barrier delivers the attribution report; all eight actors choose `no_op`. |

All 14 non-`no_op` actions are accepted and apply their declared effects. The
remaining 74 decisions are `no_op`. Nine message intents each receive a queued
and a delivered disposition. Six generated annotations mark intrusion,
exfiltration, verified containment, public response, enforcement, and
attribution; `S1` through `S4` each receive one stage-entry record.

The terminal state distinguishes persistent outcomes from closed response
lifecycles. Patient-data theft remains `exfiltrated`, while intrusion access is
`contained` and detection is `verified`. Disclosure, patient notification,
and the leadership statement are complete. Inquiry findings are ready,
penalties are issued, owner and operator reforms are implemented, oversight is
active, and attribution is `whitefly`. None of these values is silently reset
at termination.

## Mechanism attribution

The event package supplies 14 declarative Rule rows over 11 coordinates. The
Rule backend chooses actions from the sealed public prestate; it has no model
or network access. The H2EPR environment validates actor and intent authority,
applies typed deltas, and derives annotations. The MASim kernel provides the
message envelopes, one-tick append-only transport, authoritative reducer, and
trace/replay substrate.

Ticks 5 and 9 show atomic multi-actor updates to distinct fields of one state
entity. All actors decide from the same prestate, then the environment commits
the compatible writes together. This prevents an earlier actor in a logical
coordinate from leaking its update into a later actor's observation.

## Verification and limits

The complete output was scanned under the current coverage rule. Action types,
state deltas, message lifecycles, annotations, graph counts, and terminal-state
bytes are checked from the sealed run. Participant observations expose
semantic message content and lifecycle state while excluding opaque transport
identifiers from decision production. These are runtime-contract checks, not a
comparison with historical evidence.

## Interpretation

The generated process separates intrusion, detection and containment, public
response, institutional review, enforcement and reform, and attribution. Its
message chain makes the handoffs observable: detection reaches the operator,
verified scope reaches owner and ministry, findings reach regulator, and
penalties reach the organizations that implement reforms.

This is a coherent executable rendering of the exposed dataset structure. It
does not demonstrate autonomous attacker behavior, organizational decision
quality, or independent recovery of the event chronology. The fixed Rule rows
and logical coordinates deliberately realize the full-Draft-conditioned
baseline.

## Limitations

The model has no patient-level records, technical telemetry, exploit or
defense mechanics, system topology, monetary penalty values, organizational
deliberation, uncertainty, or reform-effectiveness measure. Patient victims
remain world state rather than action-bearing agents. One-tick communication
latency is structural and does not estimate elapsed historical time.

The run supports formal package integrity, deterministic execution, replay,
trace-complete graph publication, message closure, and common-contract tests.
It does not support historical fit, attribution validity, parameter
calibration, held-out performance, policy effectiveness, causality,
scientific validity, or universal generality.
