# H2EPR-0288 generated-process reading

The accepted Panic of 1907 run is the largest and most continuously
interactive of the three current H2EPR generated processes. It moves from a
call-money relationship into Knickerbocker support and clearing interactions,
differentiated depositor requests, wider trust-company coordination, and
conditional resource commitments. Its 16 actors make 88 decisions over 22
active logical ticks; 87 decisions emit accepted actions and one follows an
explicit no-intent branch.

This report is a reading of simulated output. The inventory, chronology,
routes, and state counts below are direct artifact facts. The section headed
“Analytical reading” states interpretations drawn from those facts. No Draft
EPG, Reference EPG, or historical comparison evidence is used.

## Reading scope

The primary object is the complete canonical Generated EPG identified by the
[accepted run release](../../../execution/panic_1907/run-and-graph-v0.1/).
The run manifest supplies the civil-date meaning of logical ticks. The sealed
trace and final state are used to read observation delivery, pre-existing
lifecycle state, and completion, because those records are not fully
projected as graph nodes.

| Coverage item | Complete reading result |
|---|---:|
| Generated EPG nodes | 1,392 of 1,392 |
| Generated EPG edges | 1,121 of 1,121 |
| Unique node-to-trace references | 1,392 |
| Sealed trace records traversed as context | 2,002 of 2,002 |
| Participants | 16 |
| Participant decisions / action intents | 88 / 87 |
| Canonical and repeat graph | byte-identical |

The graph declares `simulation_generated_mechanism_coverage` as its output
interpretation. Its own claim boundary sets historical calibration,
historical validation, and scientific validity to false.

## Graph form

The graph contains 88 participant decisions, 87 action intents, 87 action
dispositions, 443 policy applications, 141 state deltas, 150 message intents,
300 message dispositions, eight exogenous releases, and 88 carry-forward
nodes.

Its 1,121 edges comprise 87 `adjudicates`, 141 `causes`, 150 `emits`, 443
`governs`, and 300 `routes` relations. They connect each action intent to its
local disposition, rules, deltas, and messages, then each message to queue and
delivery dispositions.

The graph has 271 weakly connected components. Eighty-seven are
action-centered components; the other 184 are the eight exogenous releases,
88 decisions, and 88 carry-forward records, each represented as an isolated
node. The graph contains no explicit cross-action or
observation-to-decision edge. The logical clock and trace are therefore
necessary to see the interaction sequence between these local subgraphs.

## Simulated process

The clock spans 18 October through 2 November 1907 in America/New_York. Each
civil date has two deterministic partial-order slots; the slot is not an
inferred intraday timestamp. Actions occur from tick 0 through tick 21,
corresponding to 18–28 October. The final four messages are delivered on 29
October, and the run carries open state to the 2 November analytic horizon.

| Interval | Decisions and actions | Simulated process |
|---|---:|---|
| 18–20 October, ticks 0–5 | 11 / 11 | A broker and member bank exchange call-loan information, renewal or replacement requests, collateral proposals, a decline, offer revision, controlled repayment, and clarification. |
| 21–22 October, ticks 6–9 | 16 / 16 | Knickerbocker, National Bank of Commerce, and New York Clearing House verify and classify the case, exchange information, and issue or clarify a typed disposition; two Knickerbocker depositor profiles begin differentiated withdrawal or retention choices. |
| 23–25 October, ticks 10–15 | 46 / 45 | Later-trust depositors enter; Morgan and the trust presidents’ committee classify, investigate, coordinate, solicit, and assemble support; Trust Company of America and Lincoln issue or revise institutional positions; one TCA decision emits no action. |
| 26–28 October, ticks 16–21 | 14 / 14 | Two bank-resource actors request proposal information, make or refer conditional contributions, submit collateral or a member-certificate application, and revise commitments; Lincoln handles correction and delivery clarification. |

The eight exogenous inputs all carry `outcome_forcing: false`. They include
dated event and institutional opportunities, public signal and authority
records, a later certificate-facility context, an NYSE calendar with a
synthetic tie policy, and explicitly synthetic private-need activations. The
input labels therefore expose which parts of the canonical path are historical
context and which exist to exercise mechanisms.

## Heterogeneous decisions

Thirty-five decisions consume no configuration parameter, 36 consume two,
and 17 consume three. Parameter use is concentrated in the call-money,
depositor, and bank-resource populations; the institutional interfaces rely
on their declared observations and persistent state.

The depositor carriers demonstrate visible branch differences:

- both Knickerbocker profiles request withdrawal when the need and signal set
  first arrives; on the next slot the need-only profile retains while the
  signal-responsive profile requests again;
- on 23 October all four later-trust profiles request withdrawal; in the next
  slot the contagion- and host-signal-responsive profiles request again while
  both need-only profiles retain; and
- later slots include retention, awaiting a result, and renewed withdrawal,
  rather than one uniform run trajectory.

At tick 15 the Trust Company of America commitment records
`no_declared_activation_condition`. It produces a participant-decision node
with no action intent, disposition, policy application, delta, or message.
This is the only no-intent decision in the three current canonical runs.

## Communication and temporal interaction

Every accepted action produces one typed environment result. Sixty-three
actions also emit participant communication, creating 150 message intents in
total. All have latency one, one queued disposition, one delivered
disposition, and exactly one recipient observation. No message intent or
recipient is unresolved.

The declared communication network links:

- broker and member bank in both directions;
- Knickerbocker, NBC, and NYCH along the support and clearing route;
- depositor units to their host trust;
- Trust Company of America, Morgan, and the trust presidents’ committee;
- Lincoln and the committee; and
- later bank-resource actors to TCA, Morgan, or NYCH.

From tick 1 through tick 21, pending messages are delivered before the tick’s
actor observations and participant decisions. This gives later decisions a
real observation opportunity that is absent from the more widely spaced
action waves in the other two runs. The Generated EPG retains the relevant
ticks and message records but does not draw the corresponding
message-observation-decision edge.

## Policy, state, and completion

All 443 policy applications pass:

| Policy family | Applications | Visible responsibility |
|---|---:|---|
| lifecycle, result, and time | 87 each | typed transition, accepted reducer result, and logical-time admission |
| information | 63 | routed information product |
| review | 41 | evidence-item classification |
| amount | 39 | bounded requested and realized amount |
| service | 16 | withdrawal-service handling |
| facility | 12 | facility and resource constraint |
| venue | 11 | venue transition |

All 87 action dispositions are accepted. The 141 state deltas comprise 87
authoritative lifecycle transitions and 54 participant-private updates. The
final private state preserves differences such as reassuring versus adverse
dated information, need-only versus signal-responsive profiles, incomplete
resource information, institutional review or communication posture, and
consumed record versions.

The final state contains 88 nonterminal lifecycle objects: one opening
call-loan object plus one object created by each accepted action. All become
carry-forward records. Thirty withdrawal-service objects end in
`request_created`; the remainder occupy `active`, `admitted`, `authorized`, `circulating`,
`delivered_reviewing`, `issued`, `offered`, `pending_authority`, `requested`,
`review_due`, or `submitted`. The run closes normally at the analytic horizon
with transport resolved and business processes still open.

## Analytical reading

### This run shows the strongest interaction depth

The daily two-slot clock repeatedly delivers one action’s messages before the
next decisions. Participant profiles also consume explicit configuration
parameters and update persistent state. The resulting process is more than a
set of independent scheduled actions: it exposes repeated information,
request, and coordination opportunities across several actor chains.

### Heterogeneity is visible and inspectable

Parallel depositor carriers do not always choose the same branch. Their
different information inventories and response profiles are reflected in
withdraw, retain, and await choices. The one no-intent case also demonstrates
that the roster can remain active without forcing every scheduled commitment
to emit an action.

### The canonical path remains strongly coverage-oriented

Despite the richer interaction, all 87 emitted actions are accepted and every
policy application passes. No message is delayed beyond its fixed one-tick
latency, rejected, duplicated, or lost. Resource and facility policies return
typed values, but all business objects remain open at completion. The run
therefore exercises a broad mechanism vocabulary without estimating how often
alternative outcomes would occur.

### Synthetic triggers are materially important

The graph itself exposes synthetic private-need activations and a synthetic
tie policy among its exogenous inputs. Those inputs are legitimate for
mechanism coverage and are clearly labeled. A historical comparison must not
silently treat the resulting timing or withdrawal opportunities as recovered
historical facts.

### Provenance is clearer than global causal structure

For each action, the governing policies, state changes, messages, and reducer
result are exact. The global graph remains fragmented into local action
components, with decisions and exogenous triggers isolated. The trace shows
that messages are available before later choices, while the graph does not
state which message or state item caused a particular branch. Historical
causal interpretation will need an explicit comparison method rather than
visual graph matching alone.

## Questions reserved for later comparison

A later, separately scoped study can test:

- which call-money, trust-support, depositor, coordination, and facility
  transitions are retained from the configured Draft EPG;
- whether the continuous two-slot chronology adds simulated steps or ordering
  unsupported by event evidence;
- which branch differences are evidence-consistent consequences of the
  declared profiles and which are artifacts of synthetic need or tie inputs;
- whether accepted-only action and transport paths omit historically relevant
  refusal, delay, capacity, or authority outcomes;
- which of the 88 open lifecycle objects have supportable historical
  dispositions; and
- whether a future comparison should evaluate local causal motifs,
  actor-to-actor process chains, or event-level chronology rather than one
  monolithic graph distance.

Those questions are not answered by the present simulation-only reading.
