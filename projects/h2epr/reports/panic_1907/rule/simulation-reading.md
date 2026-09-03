# Panic of 1907 Rule simulation reading

## Run identity and reading boundary

| Item | Identity |
|---|---|
| Event | `H2EPR-0288` |
| Run | `run.e37134e71ff5370299ec8f78` |
| Package | `185797e8e4987b3f485a246569039514a415114ac5d05dc4005b696ea8f115ee` |
| Rule binding | `5c02b8087844740e2c86cbeb172a16231f519a7010002a0b608871cfcb50fb22` |
| Trace | `f3d9eb95d35daef823e1914f3e623905753b46547cf2fb32de82a8b08264be48` |
| Final state | `2db6c38a541b4356c045c1f33abf821f1d3023ed484b46aecae124d71bb49dc5` |
| Generated EPG | `850c1d87a1bbe32c2faaf35e2a1df1de7e328e0846d4877b1f8b789154e94f6a` |
| Compact release | [`releases/panic_1907/rule`](../../../releases/panic_1907/rule/) |

Construction used the event's declared `event_spec`, `frozen_evidence`, and
fully exposed `draft_epg`. This is a simulation-only reading of the sealed Rule
output. It is not a comparison with external history or an evaluation target.

## Complete-output coverage

The reading traversed all 813 trace records, 851 graph nodes, and 2,074 graph
edges. It checked every node and edge endpoint, every embedded source-trace
reference, all 813 trace-to-graph coverage entries, every action and message
disposition, the terminal state, and the run seal. No trace record is omitted
from the graph and no transport intent remains unresolved.

The graph contains one generated event, 15 logical coordinates, 12
participants, ten state entities, and one node for each trace record. Its edge
inventory includes 813 `occurs_at`, 192 `disposes`, 180 each of `based_on`,
`decided_by`, `emitted_by`, `observes_for`, and `projects`, plus state,
message, stage, seal, and containment relations.

## Direct generated facts

The opening state records stable affiliated banks and trusts, an open
Knickerbocker Trust, normal call-market liquidity, no emergency support, a
strained monetary system, and no reform institutions. The table reads every
logical coordinate. Trace suffixes refer to
`trace.run.e37134e71ff5370299ec8f78.*`.

| Tick and trace range | Generated action and resulting transition |
|---|---|
| 01, `00000000–00000053` | Heinze's market-corner action changes `united_copper.corner_status` to `failed`; Morse's same-value action is accepted with no additional effect. |
| 02, `00000054–00000105` | Depositors initiate an affiliated-bank run, changing its status from `stable` to `active`. |
| 03, `00000106–00000159` | NYCH stabilizes the affiliated banks and completes member-bank stabilization. |
| 04, `00000160–00000216` | Knickerbocker requests support; requests to NYCH and J. P. Morgan enter one-tick routes. |
| 05, `00000217–00000274` | J. P. Morgan applies the support denial; NYCH's identical denial is accepted without a second state change. Both denial messages are queued after the two requests arrive. |
| 06, `00000275–00000331` | Depositors start the trust run, J. P. Morgan begins private rescue, and Knickerbocker suspends operations. Both denial messages are delivered. |
| 07, `00000332–00000383` | Other trusts liquidate call balances, changing call-market liquidity to `seized`. |
| 08, `00000384–00000436` | J. P. Morgan supports exchange liquidity; NYSE support becomes `provided` and the call market becomes `supported`. |
| 09, `00000437–00000490` | Member banks suspend deposit convertibility while NYCH issues emergency liquidity. |
| 10, `00000491–00000544` | J. P. Morgan completes the private bailout and the active trust run becomes `contained`. |
| 11, `00000545–00000597` | European money centers export gold; gold is marked `arrived` and monetary system status becomes `restored`. |
| 12, `00000598–00000649` | Congress establishes the National Monetary Commission. |
| 13, `00000650–00000703` | The Commission issues recommendations and queues its report to Congress. |
| 14, `00000704–00000759` | Congress establishes the Federal Reserve, receives the recommendation report, and queues a reform notice to the Commission. |
| 15, `00000760–00000812` | The terminal barrier delivers the reform notice; all 12 actors choose `no_op`. |

All 19 non-`no_op` action intents are accepted. Seventeen apply a transition;
the second market-corner attempt and second support denial are typed
`admitted_no_effect` because the simultaneous or same-coordinate write already
set the identical value. The other 161 decisions are declared `no_op`
decisions. Six message intents produce six queued and six delivered
dispositions.

Five generated annotations mark the failed corner, affiliated-bank
stabilization, Knickerbocker suspension, private containment, and monetary
reform. Stage entries occur once for each of `S1`, `S2`, and `S3`.

The terminal state retains the failed corner, suspended Knickerbocker
operations, denied support, suspended deposit convertibility, and issued
emergency liquidity. It also records stabilized affiliated banks, contained
trust-sector pressure, completed private rescue, supported call-market
liquidity, restored monetary status, and established reform institutions.
These are concurrent categorical state fields; the run does not synthesize an
unrecorded reopening or convertibility-restoration action.

## Mechanism attribution

The exact trajectory follows 19 event-local declarative Rule rows over 15
published coordinates. H2EPR owns the roster, observation and intent
interfaces, state domains, action preconditions and effects, route table,
configuration, and generated annotations. The generic Rule backend selects a
row from the sealed prestate. The H2EPR environment validates authority and
applies typed deltas atomically. The unchanged MASim kernel owns envelopes,
append-only communication, authoritative reduction, and trace/replay
primitives.

The two accepted no-effect actions demonstrate the declared conflict policy:
idempotent same-value writes remain observable without applying a second
delta. The final delivery-only coordinate demonstrates that scenario closure
must include message lifecycle, not only the last substantive action.

## Verification and limits

The complete output was scanned under the current coverage rule. Action types,
state deltas, message lifecycles, annotations, graph counts, and terminal-state
bytes are checked from the sealed run. Participant observations expose
semantic message content and lifecycle state while excluding opaque transport
identifiers from decision production. These are runtime-contract checks, not a
comparison with historical evidence.

## Interpretation

The output forms a coherent categorical cascade from market-corner failure to
bank and trust stress, private and clearing-house responses, monetary relief,
and institutional reform. This coherence is an implementation result: all
declared actions are admitted, state changes are ordered, messages reach their
recipients, and the graph preserves the complete trace.

It is not evidence that the simulator independently discovered the historical
sequence. Full Draft exposure supplied the participant set and ordered process
outline, while the Rule rows deliberately realize that dataset-conditioned
construction.

## Limitations

The state has no money amounts, prices, bank-level balance sheets, beliefs,
failure probabilities, or heterogeneous depositor behavior. Source-time
ranges label logical coordinates; one tick and one-tick message latency are
execution choices rather than historical durations. Persistent terminal
states such as suspended convertibility are not automatically unwound.

The run supports package integrity, deterministic execution, replay,
trace-complete graph publication, message closure, and cross-event engineering
tests. It does not support historical fit, parameter calibration, held-out
performance, policy effectiveness, causality, scientific validity, or
universal generality.
