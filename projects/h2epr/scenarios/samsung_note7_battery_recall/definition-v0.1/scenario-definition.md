# H2EPR-0481 Event Scenario Definition

## 1. Purpose, identity, and claim boundary

| Field | Value |
|---|---|
| Event | `H2EPR-0481` |
| Scenario | `h2epr.scenario.0481.samsung_note7_battery_recall@0.1.0` |
| Modeled interval | 19 August through 15 October 2016 |
| Acute interval | 2 September through 15 October 2016 |
| Outcome exposure | full public outcome exposed during construction |
| Purpose | engineering and method mechanism coverage |

The Scenario asks how incident and defect signals, participant choices,
institutional authority, product and remedy resources, communication routes,
and transport restrictions changed the reachable product-safety process. It
does not require the historical sequence or outcome to occur.

The design supports no claim of defect-cause proof, liability, recall
effectiveness, historical replay or fit, parameter calibration, prediction,
held-out performance, policy effectiveness, scientific validity, or universal
generality. A source-attributed report remains a report unless an
authoritative modeled process versions a finding.

## 2. Boundary, clocks, and causal opportunities

Four clocks remain distinct: occurrence or effective time, participant-time
availability, source publication time, and research-access time. Message
production, issue, transport, delivery, correction, review, and expiry times
are also distinct. Unsupported intraday order is never invented.

| Opportunity | Entry condition | Reachable changes | Non-guarantee |
|---|---|---|---|
| `CT-1` launch and safety-signal arrival | a launched device population and bounded incident opportunity exist | local experience, report, intake, investigation request, or product-flow review | no incident, defect, receipt, or response is forced |
| `CT-2` initial corporate response | a Samsung interface receives an eligible signal or investigation update | information request, safety message, product-flow direction, or replacement proposal | no investigation finding, stop, partner action, or remedy completion is forced |
| `CT-3` recall and remedy interaction | CPSC receives eligible firm, incident, or remedy information | warning, further inquiry, initial recall intent, or continued review | no legal action, effect, stock, exchange, or consumer response is forced |
| `CT-4` replacement-device reopening | a replacement-device signal or adverse result is produced and delivered | reassessment, partner stop request, product-flow change, renewed authority review | no finding, global stop, or expansion is forced |
| `CT-5` production and expanded-recall opportunity | relevant signals, flow records, or authority predicates are available | production posture, recall expansion, revised remedy or communication | no halt, expansion, delivery, or return is forced |
| `CT-6` transport issuance and downstream action | an authority interface receives eligible safety, recall, legal, or feasibility records | CAAC warning or U.S. order inquiry, qualification, issuance, publication, effect, operator action | neither issuance nor post-issuance success is forced |
| `CT-7` bounded closure | horizon, early closure, or invariant failure occurs | normal, bounded-incomplete, or fail-safe terminal record | historical outcome is not a completion predicate |

The calendar bounds opportunity eligibility. They do not script transitions.
January 2017 diagnosis and remediation are categorically unavailable to every
2016 actor and process input.

## 3. Event-driven process and phase model

| Phase | Entry condition | Permitted work | Exit or reopening |
|---|---|---|---|
| `P0` opening product context | modeled start reached | establish device classes, scoped flow context, institutions, routes, and unknowns | first eligible signal or horizon |
| `P1` signal and investigation | eligible incident or safety record exists | intake, delivery, inquiry, investigation, local reporting, and provisional assessment | response proposal, unresolved carry-forward, correction, or new signal |
| `P2` initial product response | Samsung receives sufficient eligible context for a decision | product-flow, replacement, partner, safety-message, or continued-investigation intents | typed result, expiry, supersession, or renewed evidence |
| `P3` recall and remedy | CPSC or remedy routes receive eligible records | warning, information/remedy review, recall intent, local offer, inventory and consumer choice | typed legal/remedy results, correction, or replacement signal |
| `P4` replacement reopening | replacement-device signal or adverse result is delivered | corporate, authority, regional, outlet, and consumer reassessment | revised posture, expansion opportunity, unresolved state, or horizon |
| `P5` production and expanded action | relevant participant intents are admitted | production, partner, recall-expansion, remedy, and message processes | typed results, supersession, or transport predicate |
| `P6` transport restriction | CAAC or DOT issuance predicate becomes eligible | inquiry, qualification, issuance, post-issuance lifecycle, operator encounter and handling | effective/expired/superseded restriction, unresolved action, or horizon |
| `P7` closure | terminal rule activates | retain final canonical state and unresolved objects | deterministic terminal record |

At the same modeled time the Scenario admits exogenous input, processes
physical or institutional events, produces information, transports and
delivers it, freezes recipient observations, permits participant decisions,
adjudicates intents, executes admitted work, applies reducer deltas, and only
then exposes later observations. Stable event identity breaks remaining ties.

## 4. Institutions, participants, and non-participant processes

| Entity or process | Modeled responsibility | Boundary |
|---|---|---|
| Samsung corporate product-safety interface | investigation, product-flow, replacement, partner, production, and safety-message intents | not a whole-company mind; supplier knowledge and January 2017 findings excluded |
| CPSC recall interface | warning, inquiry, initial recall, and recall-expansion intents | legal state, delivery, implementation, and effectiveness remain Scenario truth |
| CAAC warning interface | warning inquiry, issuance, and qualification intents | publication, effect, delivery, duties, enforcement, and results start after valid issuance |
| U.S. DOT emergency-order interface | Secretary-level inquiry, qualification, and issuance intents with bounded FAA/PHMSA inputs | no merged agency mind; post-issuance lifecycle remains external |
| Samsung regional units | jurisdiction-local partner, remedy, and message choices | only evidence-supported units may be configured; Singapore does not imply all regions |
| carrier and retail outlets | channel-local sales, notice, inventory, and remedy choices | no shared outlet knowledge, stock, policy, or result |
| owners and prospective consumers | unit-local purchase, use, report, information, exchange, and refund choices | no representative collective intent or access to aggregate truth |
| air-transport operators | operator/function-local communication, identification, handling, denial, stricter-measure, and escalation choices | jurisdiction, procedure, encounter, authority, and physical results remain scoped |
| suppliers and supplier-facing investigation | bounded investigation context | no autonomous supplier participant or fault attribution |
| device and incident process | device identities, classes, reports, and physical hazard opportunities | never generated to force the known outcome |
| product, production, inventory, remedy, and custody processes | authoritative object state and conservation | participant directions or requests do not guarantee changes |
| recall and transport institutional processes | valid issuance consequences, legal effect, routing, duties, enforcement, and results | may not impersonate an unresolved issuance Agent |

Institutions, scoped units, resource domains, capacities, relationships, and
effective intervals are canonical and versioned. Hosting or affiliation does
not imply shared knowledge, transitive authority, or delivery.

## 5. World state, resources, and invariants

| State or resource family | Owner | Invariant |
|---|---|---|
| device and product class | device/product registry | original, replacement, and green-icon labels remain explicit; label is not safety truth |
| incident and safety record | intake/investigation process | reported, delivered, investigated, aggregated, and verified are distinct |
| product-flow state | product-flow process | sales, shipments, exchanges, production, returns, and custody are separate variables |
| production posture | production process | direction, admission, operational change, and result remain distinct |
| inventory and remedy stock | inventory/remedy process | local observation may be stale; allocation, transfer, handoff, exchange, and refund conserve objects |
| recall state | jurisdictional recall process | corporate program, warning, initial formal recall, and expansion are different objects or versions |
| transport action | issuer plus post-issuance process | CAAC and U.S. records never merge; proposal, issue, effect, delivery, duty, enforcement, and result differ |
| route and delivery capacity | information process | route eligibility is not issue, transport, receipt, acknowledgement, interpretation, or action |
| investigation and information capacity | responsible process | request is not access, assignment, work, finding, or answer |
| participant private state | each actor capability | never authoritative business truth and never visible to another actor |

Only reducers mutate authoritative truth. Each accepted transition records the
object and version read, authority and resource checks, typed result,
StateDeltas, causal references, and resulting version. Negative, partial,
no-effect, adverse, corrected, and reversed results remain visible.

## 6. Information production, routing, and observation

An information product records producer, source object/version, proposition or
payload, uncertainty, production/as-of time, correction or supersession link,
and visibility class. A message records sender, exact recipient, route,
capacity, issue time, delivery disposition and time, and content version.

Participant observations are immutable, capability-scoped projections frozen
at a decision. Public posting does not prove receipt. Meeting, affiliation,
market participation, or common jurisdiction creates no transitive delivery.
Missing information remains missing; stale or disputed information remains
marked; a correction changes only the propositions it addresses and preserves
the earlier decision basis.

The Scenario rejects any observation containing an undelivered future recall,
production halt, transport order, enforcement result, later participant
choice, other actor's private state, Reference or evaluation fact, or January
2017 diagnosis.

## 7. Exogenous and institutional input boundary

| Input family | Permitted effect | Forbidden effect |
|---|---|---|
| bounded incident opportunity | create a device-local hazard or report opportunity subject to adjudication | force a failure, causal diagnosis, report, receipt, or response |
| device and product context | provide stable identity, class, jurisdiction, or scoped prestate | reveal future findings or another device's state |
| institutional framework and authority | version jurisdiction, capacity, route, and legal context | select a participant intent or valid issuance |
| product-flow and inventory opportunity | make bounded stock, production, shipment, or handoff state eligible for observation or action | force availability, transfer, exchange, refund, or return |
| recall-process opportunity | admit review, issue, effect, delivery, correction, or expansion transitions after prerequisites | create authority, guarantee action, or establish effectiveness |
| transport-process opportunity | admit publication, effective-time, delivery, duty, encounter, enforcement, or result after valid issuance | replace the CAAC or DOT issuance choice |

All inputs are versioned, independently identified, non-outcome-forcing, and
immutable within a run unless their admitted event explicitly versions them.

## 8. Intents, adjudication, lifecycles, and results

The Scenario accepts only the 37 capability-qualified intent types in the
released mapping. It validates actor and capability identity, parameters,
target, causal observations, capacity, authority, jurisdiction, relationship,
object prestate, route, resources, duplicate/concurrency status, phase, and
feasibility before execution.

The twelve authoritative lifecycle families are participant intent;
information product and message; investigation and information request;
incident report and intake; product-flow posture; production posture;
inventory and partner action; remedy offer and fulfillment; recall authority
action; warning or emergency-order action; device use and purchase posture;
and transport encounter and handling.

Every object has stable identity, version, owner, state, predecessor and
supersession relation, idempotency key where applicable, valid transition
cause, review/expiry rule, and replay path. Invalid work returns a typed
disposition; it is never silently dropped or converted to success.

Participant intent, message materialization, issue, route admission,
delivery, acknowledgement, institutional acceptance, execution, physical or
legal effect, result, StateDelta, and later observation are distinct events.

## 9. Structural variants, termination, and reproducibility

| Structural family | Baseline | Bounded alternatives |
|---|---|---|
| exogenous hazard-signal pressure | bounded device-local opportunities with adjudicated results | lower or delayed opportunity; different bounded source mix |
| route and delivery | distinct named routes and recipient histories | delay/failure; partial or corrected delivery |
| population assembly | evidence-gated, scope-preserving units | narrower active unit set with disclosed information loss |
| authority capacity | capacity- and jurisdiction-qualified authority | delayed/unavailable capacity; narrower route availability |
| operational result | authority, prestate, resource, and feasibility adjudicated | partial/no-effect/adverse result; delayed resource availability |
| public-action delivery | proposal, valid issuance, publication, effect, delivery, and implementation separated | delayed effect; partial/failed delivery; supersession |

A configuration selects one baseline per family, exact units, opening records,
inputs, policy meanings, overlays, and a bounded lineage. Selections are
system inputs, not actor knowledge or policy.

Normal completion occurs at the core horizon or a declared early process
closure. Pending objects cause bounded-incomplete closure while retaining
owner, state, version, reason, and next eligible event. Invariant failure
closes fail-safe. The same admitted configuration, binding, policies,
exogenous sequence, seed, and code identity must reproduce canonical state,
dispositions, deliveries, results, and trace identity.

## 10. Falsification, gaps, and limitations

Representative falsifiers include an observation without a source/version or
delivery; a regional unit inferred from another jurisdiction; a consumer
cohort with shared private state; a remedy completed by offer alone; a recall
or order effective before valid issuance; a post-issuance process that chooses
issuance; an inventory or custody delta that violates conservation; an
undelivered message treated as knowledge; a 2017 diagnosis available in 2016;
or replay that drops negative or unresolved results.

A contradiction routes to evidence if the historical premise fails; to the
Roster or Definition if autonomous choice or behavior is wrong; to mapping if
qualification is lossy; to Scenario if world, time, authority, lifecycle,
resource, or result semantics are absent; to configuration if a selected unit
or baseline is unsupported; to implementation if admitted semantics are not
preserved; and to Contracts only after a concrete carrier loss is shown.

Open empirical questions include Samsung internal decision boundaries,
supplier knowledge and autonomy, incident-level reconciliation, carrier- and
jurisdiction-specific timing, physical failure mechanism during the modeled
interval, remedy availability, consumer and operator heterogeneity, and
recall effectiveness. The Scenario records these limits and supplies no
answer through a default parameter.

This Definition closes the released semantic interface. It remains a
qualitative engineering specification, not an executable model or a
scientific result.
