# East Palestine Train Derailment Rule simulation reading

## Run identity

This reading covers the complete canonical seed-0 Rule output for H2EPR-0196. Construction used the fully exposed Draft and the three dataset inputs sealed by the Source Profile. The run is a deterministic, dataset-conditioned construction baseline.

| Item | Identity |
|---|---|
| package | `h2epr.event-package.0196.v1`; `f1f30080e857417ed06cb45b3cbb25b37ea5a7fac72339978185f37dd657e297` |
| Rule binding | `9588486a9e93f5a46a94b3e1f4e9a3bb1f000ab3b61332f4437a5af611a4b17d` |
| Rule configuration | `h2epr.0196.rule.v1`; `0249e88e66453b3355994287f1982a981c0d773e04f0bd1512851465a1030031` |
| canonical run | `run.4cc6658590d5447313ff426b`; seed `0`; model and network access denied |
| run manifest | `2e9b537403377fc0d8f8f5f17e12c71239a0b1611161cc2070dcf501ea97f399` |
| trace | `a90e4b657e6f46c137e5d847a1e77da378f9309614e72be0fb1e66551cd7438a` |
| terminal state | `1b7dbf7b8e8e85bd7ff1fa172fd544d6d57a434d572fa1f446ade7d4333d5599` |
| run seal | `33d3a6f4471e29f12c33e6f44e84fbd1dc25380d108b97c052f4c35643a3b7b2` |
| Generated EPG | semantic seal `b36314507aa0b70878f8346ccec20df418cb804401fe91ffc63ca3754ec0eab2`; source trace as above |
| replay | pass; 405 records and 11 ticks replayed to the exact terminal-state hash |
| raw custody | `.local-runtime/h2epr-simulation/runs/benchmark/east_palestine_train_derailment/rule/current/materialization-a` |

Canonical materializations A and B are byte-identical across all nine output files. The determinism receipt is `b3bdfc7cf282c552b2db0913f778b1cf962b9aa2a30df874f4dcf34b3e228558`. A generated-ID probe changed run and opaque record identities while preserving the semantic trace, semantic graph, and terminal state. Its identity-conformance receipt is `9911c8229f1d8d6d50315a2009c1141ef65678182e50a319af4f342d7404b390`.

## Complete-output coverage

The reading traversed all 405 JSONL records, all 432 graph nodes, and all 1,056 graph edges. It checked every edge endpoint, every node and edge source-trace reference, and the full trace-ID set. The graph contains 432 unique node IDs and 1,056 unique edge IDs; all endpoints resolve, all 405 trace IDs are represented, no unknown trace ID is cited, and no trace record is uncovered.

The trace contains:

| Record family | Count | Reading result |
|---|---:|---|
| observations, participant decisions, action intents, action dispositions | 77 each | one complete path for each of 7 actors at each of 11 coordinates |
| non-`no_op` / `no_op` actions | 14 / 63 | all 77 dispositions accepted; no rejected or partial action |
| message intents | 14 | each has one queued and one delivered disposition |
| message dispositions | 28 | 14 queued, 14 delivered; none unresolved at run seal |
| state deltas | 14 | all link to an accepted source intent and a declared state entity |
| stage entries | 4 | one entry for S1, S2, S3, and S4 |
| generated annotations | 3 | response closure, formal-action opening, and settlement recording |
| tick opens, commits, and seals | 11 each | every coordinate closes against its poststate |
| run seals | 1 | zero unresolved intent IDs and recipient IDs |

The Generated EPG adds one generated-event node, 11 coordinate nodes, 7 participant nodes, 8 state-entity nodes, and one node for every trace record. Its edge families cover temporal placement, participant decisions, action and message provenance, state changes, stage membership, annotations, and seal relationships. Representative examples include `edge.45d1a3c54dfe6009fb786bc7f677158`, which links the first incident delta to the incident state entity, and `edge.cc8576b5766da5f957777ab9cbe9f19`, which links the final delivered settlement notice to its queued predecessor.

## Generated trajectory

The opening world has an operating incident state; inactive evacuation; pending hazard control; no preliminary investigation, community report, cleanup, legal filing, or settlement announcement. The Rule backend then produces this generated sequence:

| Coordinate | Generated transition | Direct trace evidence |
|---|---|---|
| c01, S1/E1 | Norfolk Southern reports the derailment and routes three incident alerts; `incident.status` becomes `derailed`. | decision `…00000016`; delta `…00000035`; stage entry `…00000037` |
| c02, S1/E1 | Local response activates evacuation and NTSB opens the preliminary investigation after incident-alert delivery. | deliveries `…00000040`–`42`; deltas `…00000075`–`76` |
| c03, S1/E2 | Residents acknowledge the routed evacuation order and local response completes the represented controlled-release operation. | decision records `…00000088`, `…00000092`; deltas `…00000113`–`114` |
| c04, S2/E3 | Ohio authorities receive the response update, lift evacuation, and route a return advisory. | decision `…00000136`; delta `…00000149`; response annotation `…00000152` |
| c05, S2/E4 | The resident Population reports concerns after receiving the return advisory and sends them to EPA and Ohio. | delivery `…00000155`; decision `…00000163`; delta `…00000188` |
| c06, S3/E5 | EPA receives both the delayed response update and the resident report, starts cleanup oversight, and routes a directive to Norfolk Southern. | deliveries `…00000192`–`194`; decision `…00000204`; delta `…00000225` |
| c07, S3/E6 | Norfolk Southern advances cleanup to characterization while Ohio and DOJ record separate state and federal filings. | decisions `…00000247`, `…00000249`, `…00000251`; deltas `…00000260`–`262`; annotation `…00000264` |
| c08, S4/E7 | The resident Population changes the concern state from `reported` to `persistent` and routes an impact update. | decision `…00000274`; delta `…00000297`; stage entry `…00000299` |
| c09, S4/E8 | Norfolk Southern announces the represented class-settlement step after both legal fields are filed and sends a settlement offer to Ohio. | decision `…00000318`; delta `…00000333` |
| c10, S4/E8 | Ohio records the represented municipal settlement after offer delivery and sends a notice to residents. | delivery `…00000337`; decision `…00000355`; delta `…00000368`; annotation `…00000370` |
| c11, S4/E8 | The final barrier delivers the settlement notice and makes no state change. | delivery `…00000373`; terminal tick seal `114734f2…c6136` |

The ellipses abbreviate the common prefix `trace.run.4cc6658590d5447313ff426b.`. The corresponding Generated EPG nodes use the same suffix under `record.trace.run.4cc6658590d5447313ff426b.*`. For example, `record.…00000260`, `record.…00000261`, and `record.…00000262` are three distinct c07 state-delta nodes connected to the cleanup and legal entities.

The terminal state records completed process statuses, not verified real-world outcomes: incident `derailed`; evacuation `lifted`; controlled release `completed`; investigation `preliminary_active`; resident evacuation response `acknowledged`; concerns `persistent`; cleanup `characterization`; federal and state actions `filed`; and class and municipal settlements `announced`. Investigation, concern, and cleanup values deliberately remain open or ongoing labels. The terminal condition requires their configured values, not semantic closure of those real-world processes.

## Mechanism reading

Direct run facts show a message-gated process rather than a hidden event-specific runner. The common Rule backend chose rows by actor and coordinate. Three early incident alerts activated evacuation and investigation; a three-tick local-response route aligned the response update with EPA's c06 decision, while a five-tick NTSB route aligned the preliminary notice with DOJ's c07 filing. EPA's cleanup directive and Norfolk Southern's settlement offer each enabled a next-coordinate action. The last notice required the explicit c11 delivery barrier.

The declarative environment admitted all 77 action intents against one sealed prestate per coordinate. Fourteen matched event rows and produced fourteen deltas; the other 63 produced accepted, zero-effect `no_op` dispositions. At c07, cleanup, state filing, and federal filing changed different fields in one batch, so deterministic concurrency produced no conflict. MASim transport produced all queued and delivered message lifecycles, and the reducer and trace writer produced the state, hash chain, tick seals, and run seal.

The Generated EPG is a projection of those records. A state-delta node such as `record.…00000149` connects to its source action, c04 coordinate, and evacuation entity; it does not add an independent historical claim. The graph's complete trace coverage establishes provenance of the simulated process only.

### Interpretation

Within this configuration, the main coordination bottlenecks are visible at three handoffs: incident notice to immediate authorities, combined response-and-resident signals to EPA, and investigation notice to federal enforcement. The model also keeps resident reporting separate from institutional findings and keeps state and federal legal action in separate fields. Those separations make the generated trajectory inspectable and provide clear perturbation points for future controlled variants.

This interpretation is conditional on the selected Rule rows and logical latencies. It does not establish that the real actors used these information paths, that a delay had the modeled causal role, or that the Draft chronology is complete. The simulation demonstrates that the new event-neutral assets can express and execute a multi-stage environmental-response event without adding an event branch to common Python.

## Limitations

- Construction saw the full Draft, so Draft-facing resemblance is expected and cannot be reported as held-out predictive performance.
- The frozen evidence is heterogeneous and was not externally reconciled. Draft relation-direction defects were excluded from authority construction rather than silently repaired as history.
- Six organizations or command groups are represented as single decision interfaces, and residents are one aggregate Population. Internal disagreement, individual behavior, exposure, and medical outcomes are absent.
- Logical ticks preserve process order but do not calibrate calendar time. Route latencies are structural coordination choices, not historical delay estimates.
- `controlled_release_completed`, `characterization`, `filed`, and `announced` describe modeled process states. They do not prove safety, remediation effectiveness, legal merit, payment, policy effect, or causal health impact.
- This one Rule run supports package, execution, integrity, replay, graph-provenance, and bounded descriptive claims. It does not support historical fit, parameter calibration, held-out evaluation, causal or scientific validity, policy conclusions, or universal generality.

The next eligible work after release acceptance is a separately admitted perturbation or backend comparison. This reading does not authorize LLM/RuleLLM implementation, scientific evaluation, or a second real event.
