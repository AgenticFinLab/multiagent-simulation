# H2EPR generated-process analysis

This directory owns human-readable analysis of sealed H2EPR simulation
outputs. It begins after run, replay, and generated-graph closure and keeps the
interpretation of a generated process separate from the release that produced
it. Event evidence remains under [`events/`](../events/), executable and run
identities remain under [`execution/`](../execution/), and automated metrics
or held-out evaluation require a separately authorized evaluation surface.

## Current reading packages

| Event | Package | Current scope |
|---|---|---|
| `H2EPR-0288`, Panic of 1907 | [historical-process-comparison v0.1](panic_1907/historical-process-comparison-v0.1/) | Complete simulation-only reading of the accepted Generated EPG and its sealed run context |
| `H2EPR-0616`, SingHealth Data Breach | [historical-process-comparison v0.1](singhealth_data_breach/historical-process-comparison-v0.1/) | Complete simulation-only reading of the accepted Generated EPG and its sealed run context |
| `H2EPR-0481`, Samsung Galaxy Note7 Battery Recall Crisis | [historical-process-comparison v0.1](samsung_note7_battery_recall/historical-process-comparison-v0.1/) | Complete simulation-only reading of the accepted Generated EPG and its sealed run context |

The package name states the intended research destination. The present
documents stop before graph-to-Draft or graph-to-history comparison. Later
stages will be added only when their evidence, exposure, and claim boundary
are authorized; empty placeholders are not retained.

## Reading method

Each current report uses the complete canonical `generated-epg.json`, not a
node sample or visualization. The reading procedure:

1. verifies the graph identity against its tracked run release;
2. traverses every node and edge, checks unique identities, endpoints, and
   source-trace references, and inventories all node and relation types;
3. reconstructs the action waves, policy applications, message routes, state
   deltas, and carry-forward objects;
4. reads the corresponding accepted run manifest, trace, and final state when
   the graph alone does not expose dates, observation delivery, or terminal
   state; and
5. separates artifact facts from analytical interpretation.

The canonical and independent-repeat graphs are byte-identical for all three
events. The canonical copy is therefore the reading object; the repeat is a
determinism witness rather than a second simulated case.

## Shared structural finding

All three graphs use the same nine node types and five directed relations.
Their edges connect an action intent to its disposition, policy applications,
state deltas, and message intents, then connect each message intent to its
queue and delivery dispositions. Exogenous releases, participant decisions,
and carry-forward records are source-trace-resolved nodes but have no graph
edges in these releases.

This makes the current Generated EPG a precise execution-provenance
projection. It is well suited to auditing what governed and followed each
action. A reader must also use logical ticks and, where needed, the sealed
trace to recover observation-to-decision succession across actions. The
reports treat this as a property of the accepted compiler projection, not as
evidence that the simulated process lacked temporal interaction.

## Authority and claim boundary

The reports may explain the generated trajectory, internal mechanism
coverage, information routing, state memory, and visible limitations of the
simulation. They do not rewrite an accepted event, Scenario, configuration,
runtime, or graph release.

No Draft EPG or Reference EPG was used in the current readings. Historical
event material was not used as comparison evidence, although the project and
its supervisor are not historically blind to the event topics. The present
layer establishes no calibration, historical fit, held-out result, causal
identification, policy effectiveness, scientific validity, or universal
generality.
