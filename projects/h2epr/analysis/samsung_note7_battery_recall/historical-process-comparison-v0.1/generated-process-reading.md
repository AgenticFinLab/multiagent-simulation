# H2EPR-0481 generated-process reading

The accepted Note7 run generates a compact, four-wave account of product
safety, recall, remedy, regional implementation, and transport action. The
graph demonstrates broad mechanism coverage across eight participants and
four authority settings. Its canonical trajectory remains a positive-path
execution: every scheduled decision emits an action, every action is
accepted, and all resulting lifecycle objects remain open at the analytic
horizon.

This report is a reading of simulated output. The inventory, chronology,
routes, and state counts below are direct artifact facts. The section headed
“Analytical reading” states interpretations drawn from those facts. No Draft
EPG, Reference EPG, or historical comparison evidence is used.

## Reading scope

The primary object is the complete canonical Generated EPG identified by the
[accepted run release](../../../execution/samsung_note7_battery_recall/run-and-graph-v0.1/).
The run manifest supplies the civil-date meaning of logical ticks. The sealed
trace and final state are used to check observation delivery and the state at
completion, because those records are not fully projected as graph nodes.

| Coverage item | Complete reading result |
|---|---:|
| Generated EPG nodes | 374 of 374 |
| Generated EPG edges | 302 of 302 |
| Unique node-to-trace references | 374 |
| Sealed trace records traversed as context | 926 of 926 |
| Participants | 8 |
| Participant decisions / action intents | 22 / 22 |
| Canonical and repeat graph | byte-identical |

The graph declares `simulation_generated_mechanism_coverage` as its output
interpretation. Its own claim boundary sets historical calibration,
historical validation, and scientific validity to false.

## Graph form

The 374 nodes use nine types:

| Node type | Count | Reading responsibility |
|---|---:|---|
| exogenous input release | 6 | Bounded opportunities and context admitted by the Scenario |
| participant decision | 22 | Commitment, branch, declared observations, and selected semantic intent |
| action intent | 22 | Participant request submitted to the environment |
| action disposition | 22 | Environment admission result |
| Scenario-policy application | 117 | Rule applications governing each action |
| state delta | 52 | Authoritative lifecycle, idempotency, and private-state changes |
| message intent | 37 | Participant communication or typed action result |
| message disposition | 74 | Queue and delivery records for those messages |
| carry-forward | 22 | Nonterminal lifecycle state at the analytic horizon |

The 302 edges use five relations: 22 `adjudicates`, 52 `causes`, 37 `emits`,
117 `governs`, and 74 `routes`. Every edge belongs to one of these forms:

```text
action intent -> disposition / policy application / state delta / message
message intent -> queue disposition / delivery disposition
```

The graph has 72 weakly connected components. Twenty-two are
action-centered subgraphs; the other 50 are the six exogenous releases, 22
participant decisions, and 22 carry-forward records, each represented as an
edge-isolated node. The graph contains no explicit edge between different
actions, from an observation to a decision, or from a lifecycle object to its
carry-forward record. Logical ticks and source-trace identities preserve the
records needed to recover that order outside the edge topology.

## Simulated process

The clock uses five event anchors, each expanded into ten partial-order slots.
Two pairs of anchors share a civil date. Their ordering is a declared
simulation barrier and does not claim an unobserved intraday chronology.

| Logical position | Simulated actions |
|---|---|
| 19 August 2016, modeled start | Three context inputs admit a bounded hazard signal, device and product context, and institutional authority. No participant acts. |
| 2 September, response wave | CPSC issues a consumer warning; Samsung requests a safety investigation; a consumer selects a device-use posture. |
| 2 September, acute-start wave | CAAC issues a transport warning; CPSC issues a recall action; Samsung directs product flow; the U.S. transport interface qualifies an emergency order; an air operator publishes a notice; a consumer submits an incident report; an outlet requests inventory action; and the Singapore regional unit coordinates a partner response. |
| 15 October, core-horizon wave | CAAC qualifies the warning; CPSC expands the recall action; Samsung decides a production posture; the U.S. transport interface issues an emergency order; the operator proposes carriage handling; the consumer requests exchange or refund; the outlet responds; and the regional unit proposes a local remedy. |
| 15 October, observation-horizon wave | The operator adopts a stricter local measure; the outlet sets a local product posture; and the regional unit publishes a local safety message. |

All six exogenous inputs carry `outcome_forcing: false`. They admit hazard,
product-flow, remedy, and transport opportunities without directly supplying
the participant disposition.

## Authority and communication

The actor set preserves four authority-bearing interfaces—Samsung, CPSC,
CAAC, and the U.S. transport order—and four implementation or affected
units—a Singapore regional unit, an outlet, a consumer, and an air operator.
The run does not collapse these roles into a single crisis manager.

Every action produces one typed result from the environment to its originator.
Fifteen actions also produce a declared participant communication. The main
routed chains are:

- CPSC to consumers and Samsung;
- Samsung to its Singapore regional unit;
- the regional unit and outlet in both directions, with an outlet-to-consumer
  remedy response;
- the consumer to Samsung and the outlet; and
- CAAC and the U.S. transport interface separately to the air operator.

All 37 message intents have latency one. Each has one queued and one delivered
disposition, and each is visible in exactly one recipient observation. No
message intent or recipient is unresolved at the run seal.

Delivery alone does not establish downstream causal use. In this run, message
delivery occurs at the next logical tick, while the later action waves occur
at subsequent anchors. The Generated EPG has no observation node or
observation-to-decision edge, and later decision records do not identify a
specific delivered message as their causal parent.

## Policy, state, and completion

All 117 Scenario-policy applications pass:

| Policy family | Applications | Visible result |
|---|---:|---|
| authority | 22 | authority scope admitted |
| time | 22 | intent admitted at its declared coordinate |
| lifecycle | 22 | typed result completed |
| information and route | 15 each | information product created and route admitted |
| public action | 9 | preparation requested to drafting |
| product | 7 | canonical mechanism-coverage execution |
| hazard | 2 | suspected to under review |
| remedy coordination | 3 | requested to admitted |

All 22 action dispositions are accepted. The 52 authoritative state deltas
comprise 22 lifecycle additions, 22 idempotency records, and eight
participant-private updates. Each private update sets one actor’s active
reference from an empty value to `pending`; assessment fields such as current
safety, authority, transport, remedy, or local-resolution assessment remain
`unknown` in the final state.

The run closes normally with all messages resolved. Its 22 lifecycle objects
are nonterminal and all become carry-forward records. Fifteen end in
`admitted`; the remaining seven are distributed across `acknowledged`,
`identified`, `issued`, `qualified`, `reviewed`, `routed`, and `submitted`.
The completion record therefore closes the analytic window, not the recall,
remedy, transport, or hazard process itself.

## Analytical reading

### Institutional breadth is the main strength

The generated process keeps corporate direction, formal recall authority,
regional implementation, consumer remedy, and two transport authorities
separate. That separation is visible in actor identity, action ownership,
routes, and lifecycle types. It is a useful test of whether the framework can
carry several overlapping jurisdictions and implementation layers through one
run without assigning their choices to the environment.

### The trajectory exercises coverage more than deliberation

All 22 commitments select an intent; no decision consumes a configuration
parameter; every action passes every applicable policy. The run therefore
shows that the declared mechanisms compose, while offering little evidence
about behavioral variation, refusal, delay, supersession, or competition
between branches. Negative cases exist elsewhere in conformance tests, but
they are not part of this canonical generated process.

### Internal assessment memory is shallow

The run creates typed lifecycle and policy objects, yet participant-private
state changes only once per actor and retains broad assessments as unknown.
This limits the extent to which the generated trajectory can be read as
participants revising beliefs from incident, recall, remedy, or transport
information. The visible progression is primarily commitment scheduling and
environment-owned mechanism realization.

### The graph is an audit projection, not a self-contained story graph

Action provenance is unusually clear: each intent leads to the exact rules,
messages, deltas, and disposition that followed it. Cross-action process
reading is less direct because decisions, exogenous triggers, observations,
and final carry-forward states are not connected by graph edges. Historical
comparison should therefore retain the sealed trace and clock alongside the
Generated EPG rather than treating connectivity alone as the simulated causal
story.

## Questions reserved for later comparison

A later, separately scoped study can test:

- which simulated action and authority transitions are retained from the
  configured Draft EPG and which are introduced by participant or Scenario
  mechanisms;
- whether the two declared same-date partial orders agree with evidence or
  merely provide deterministic execution order;
- whether routed warnings, recall actions, remedy exchanges, and transport
  orders occur in historically supportable order and at supportable
  granularity;
- which of the 22 open lifecycle objects have historical outcomes that can be
  evidenced, and which should remain unresolved; and
- whether actor assessment state needs a successor model before claims about
  learning, response, or policy effects are considered.

Those questions are not answered by the present simulation-only reading.
