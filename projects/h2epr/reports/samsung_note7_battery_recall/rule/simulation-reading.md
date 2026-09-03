# Samsung Galaxy Note7 recall Rule simulation reading

## Run identity and reading boundary

| Item | Identity |
|---|---|
| Event | `H2EPR-0481` |
| Run | `run.9493ae39f4127dc9e84172f3` |
| Package | `30e615792ef9f1b035e2d3c6f20c1b88cfd21f13ed0ff796d3c6c4f5c47b3b2e` |
| Rule binding | `584a18ec84c1af98e2523876c8dbaf8ea2c06c5c8981aff9c00af19c76f43739` |
| Trace | `f5c3acff8535e54424bbeba2392541d92047c8766f19a41e23fef88aaaa3987f` |
| Final state | `b95c4d0db0dd2bf4576db7ebdbddcc20bad34f9692f84839ae2cd2c5cdbc43ab` |
| Generated EPG | `52c0d0a6cb08f173de89d90cbcc1bfbda0de0880262b8f36026987beb43ced08` |
| Compact release | [`releases/samsung_note7_battery_recall/rule`](../../../releases/samsung_note7_battery_recall/rule/) |

Construction used the declared `event_spec`, `frozen_evidence`, and fully
exposed `draft_epg` for `H2EPR-0481`. The report describes the sealed generated
process only. No Reference EPG, held-out target, external source, or historical
score is used.

## Complete-output coverage

The reading traversed all 729 trace records, 772 graph nodes, and 1,872 graph
edges. Every node and edge endpoint resolves, all embedded trace references
belong to the sealed trace, all 729 trace records appear in the graph, and all
action, message, state, annotation, stage, tick-seal, and run-seal classes were
read. Terminal message custody is empty.

The graph contains one generated event, 19 logical coordinates, eight
participants, 15 state entities, and 729 trace-record nodes. Principal edge
classes include 729 `occurs_at`, 170 `disposes`, 152 each of `based_on`,
`decided_by`, `emitted_by`, `observes_for`, and `projects`, plus 26 state
changes, nine message-successor chains, four stage entries, and 20 seals.

## Direct generated facts

The opening state has no launch, sales, suppliers, incident reports, recall,
investigation, litigation, or cause report. Production and shipment are
available, and the corporate China position is neutral. The table covers all
19 coordinates. Trace suffixes refer to
`trace.run.9493ae39f4127dc9e84172f3.*`.

| Tick and trace range | Generated action and resulting transition |
|---|---|
| 01, `00000000–00000037` | Samsung launches the product. |
| 02, `00000038–00000074` | Samsung starts global sales while Samsung SDI becomes the initial battery supplier. |
| 03, `00000075–00000113` | Global consumers report initial incidents and queue the report to Samsung. |
| 04, `00000114–00000151` | Samsung receives the report, starts additional testing, and pauses shipments. |
| 05, `00000152–00000189` | Samsung announces a global recall scope that excludes China. |
| 06, `00000190–00000227` | AQSIQ issues a China test-unit recall requirement and queues the order to Samsung. |
| 07, `00000228–00000264` | Samsung receives the order and changes China recall scope to test units. |
| 08, `00000265–00000300` | ATL becomes the domestic battery supplier. |
| 09, `00000301–00000341` | ATL denies a battery link and China consumers report incidents; both messages are queued to Samsung. |
| 10, `00000342–00000382` | Samsung receives both messages, issues an external-heating claim, and queues that claim to China consumers. |
| 11, `00000383–00000419` | Samsung apologizes to China consumers after the claim is delivered. |
| 12, `00000420–00000458` | Southwest Airlines reports a flight fire and queues the report to Samsung. |
| 13, `00000459–00000495` | Samsung receives the report and suspends production. |
| 14, `00000496–00000536` | Samsung terminates production, sales, and shipments and expands global and China recall fields to all markets and all units. |
| 15, `00000537–00000573` | Global consumers file litigation. |
| 16, `00000574–00000611` | Samsung opens an internal investigation and commissions independent investigators. |
| 17, `00000612–00000650` | Independent investigators receive the commission, produce findings, and queue them to Samsung. |
| 18, `00000651–00000691` | Samsung receives the findings, publishes the cause report, completes the investigation, and queues a final report notice. |
| 19, `00000692–00000728` | The terminal barrier delivers the final notice; all eight actors choose `no_op`. |

All 20 non-`no_op` actions are accepted and apply their declared effects. The
remaining 132 decisions are `no_op`. Nine message intents each receive a
queued and a delivered disposition. Six annotations mark launch, the initial
safety signal, partial recall, the China-market dispute, permanent termination
with full recall, and the cause report. One stage-entry record marks each of
`S1` through `S4`.

The terminal state records both initial and domestic suppliers, reported
global, China, and flight incidents, all-market/all-unit recall, terminated
production, sales, and shipments, filed litigation, completed investigation,
and a published cause report. The product remains marked `launched` because
that field records occurrence, while separate fields record termination.
Likewise `testing_status=active` records that additional quality testing was
started at tick 4; the exposed package supplies no separate completion action
for that early testing field. The report does not infer one from the later
investigation closure.

## Mechanism attribution

The package provides 20 declarative Rule rows over 19 coordinates. Event-local
assets own the participant semantics, state vocabulary, preconditions,
effects, routes, and annotations. The common Rule backend selects the declared
row using one sealed prestate. The H2EPR environment validates and atomically
applies effects. MASim supplies message envelopes, append-only transport,
authoritative reduction, and trace/replay primitives.

Tick 14 shows one admitted action producing five coordinated deltas across
production, sales, shipment, and two recall-scope fields. Message delivery is
not treated as an actor-controlled success: each send is first queued, becomes
visible to its recipient only at the next coordinate, and receives a separate
delivery disposition.

## Verification and limits

The complete output was scanned under the current coverage rule. Action types,
state deltas, message lifecycles, annotations, graph counts, and terminal-state
bytes are checked from the sealed run. Participant observations expose
semantic message content and lifecycle state while excluding opaque transport
identifiers from decision production. These are runtime-contract checks, not a
comparison with historical evidence.

## Interpretation

The generated process forms a categorical product-safety cascade: launch and
sales, incident signal, testing and partial recall, China-specific response,
renewed incident pressure, permanent termination and full recall, litigation,
investigation, and report publication. Supplier, consumer, regulator,
airline, corporate, and investigator boundaries interact through the same
runtime contract used by the two other events.

This is an executable rendering of the exposed dataset structure, not an
independent reconstruction. The Rule rows determine actions at published
coordinates and do not model private corporate deliberation, consumer choice,
regulatory discretion, or probabilistic battery failures.

## Limitations

The model has no device-level hazard process, incident count, recall rate,
sales volume, cost, consumer heterogeneity, jurisdictional law, carrier
network, engineering test result, or causal defect mechanism. Test-unit owners
remain world state. Source-time ranges and one-tick communication latency are
structural labels, not estimated durations. The open testing field is reported
as a limitation rather than closed by an unsupported transition.

The run supports package integrity, deterministic execution, replay,
trace-complete graph publication, message closure, and cross-event engineering
tests. It does not support historical fit, parameter calibration, held-out
performance, recall effectiveness, policy effects, causality, scientific
validity, or universal generality.
