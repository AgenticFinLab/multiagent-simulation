# H2EPR-0481 Scenario Configuration design

## 1. Identity, purpose, and claims

| Field | Value |
|---|---|
| Configuration | `h2epr.0481.scenario.mechanism-coverage.v0_1@0.1.0` |
| Purpose | mechanism coverage |
| Modeled interval | 19 August--15 October 2016 |
| Machine format | `h2epr.scenario-configuration-semantic-candidate.v0_2` |
| Execution eligibility | false |
| Historical calibration / validation / fitting | false / false / false |

The configuration assembles the accepted Note7 participant and Scenario
semantics around safety-signal delivery, product and remedy flow, authority-
specific public action, and transport response. It fixes configuration-owned
choices without changing a participant or requiring the historical outcome.

It is not a replay, calibration, prediction, policy-effectiveness result,
defect-cause finding, historical correspondence test, held-out evaluation, or
scientific-validity claim.

## 2. Pinned semantic inputs

| Authority | Stable identity | Consumed scope |
|---|---|---|
| Event Scenario Definition release | `H2EPR-0481-EVENT-SCENARIO-DEFINITION-v0.1` | release and closure identity |
| Scenario Definition | `h2epr.scenario.0481.samsung_note7_battery_recall@0.1.0` | world, time, information, lifecycle, authority, resource, and result semantics |
| Roster Definition release | `H2EPR-0481-ROSTER-DEFINITION-RELEASE-v0.1` | four Agent Definitions and four Population Models |
| consolidated mapping | `H2EPR-0481-CONSOLIDATED-MAPPING-v0.1` | complete placement counts and carrier obligations |
| mapping profile | `h2epr.roster-consolidated-mapping.0481.v0_1` | capability and unit assembly |
| semantic skeleton and evidence | exact SHA-256 identities in the machine document | question, roles, claims, clocks, and future-information limits |

No mutable note, implementation, runtime trace, Reference content, or
simulation result supplies a default.

## 3. Clock and causal order

The configuration uses UTC as a neutral cross-jurisdiction clock. Event dates
retain their source precision; UTC does not manufacture an intraday order. The
modeled start is 19 August, participant response begins on 2 September, and
the acute and core horizon close on 15 October 2016.

At equal modeled times: admit exogenous input; process physical or
institutional events; produce information; transport and deliver it; freeze
observations; permit participant decisions; adjudicate; execute and produce a
typed result; apply reducer deltas; then expose later observations. Stable
event identity breaks residual ties.

January 2017 diagnosis cannot enter any 2016 opening record, policy input,
observation, intent adjudication, or result.

## 4. Structural baseline and sensitivities

| Family | Baseline | Coupled sensitivity | Outcome limit |
|---|---|---|---|
| exogenous pressure | bounded device-local hazard or report opportunities | lower or delayed opportunities | selects no failure, report, receipt, response, or diagnosis |
| route and delivery | distinct exact-addressed routes | delayed or failed delivery | eligibility is not receipt or action |
| population assembly | four evidence- and scope-preserving units | retain only regional and outlet units | inactive endpoints remain referentially present but ineligible |
| authority capacity | jurisdiction- and capacity-qualified | delayed CPSC capacity | creates no substitute authority |
| operational result | authority, prestate, resource, and feasibility adjudicated | delayed or partial result | selects no product, remedy, custody, or handling outcome |
| public-action delivery | proposal, issuance, effect, delivery, and implementation separated | partial or failed delivery/implementation | selects no recall, warning, order, or message success |

The six slot names use the domain-neutral vocabulary introduced by the v0.2
semantic admission schema. SingHealth's v0.1 vocabulary and schema identity
remain valid and unchanged. Each format permits one complete vocabulary, not
a merged semantic surface.

## 5. Actor, unit, and resource-domain assembly

### Named actors

| Actor | Capability | Primary authority scope |
|---|---|---|
| `actor.0481.interface.samsung-crisis` | `samsung_crisis_decision_interface` | Samsung product-safety and represented production capacities |
| `actor.0481.interface.cpsc-recall` | `cpsc_recall_decision_interface` | U.S. recall authority |
| `actor.0481.interface.caac-warning` | `caac_warning_decision_interface` | CAAC warning issuance |
| `actor.0481.interface.us-dot-order` | `us_dot_emergency_order_decision_interface` | Secretary-level emergency-order issuance |

### Population units

| Unit | Capability | Scope |
|---|---|---|
| `unit.0481.samsung-regional-singapore` | `samsung_regional_implementation_units` | evidence-supported Singapore regional product, remedy, and route context |
| `unit.0481.outlet-singapore-channel` | `carrier_and_retail_remedy_outlets` | one modeled carrier/retail channel unit |
| `unit.0481.consumer-primary` | `note7_owners_and_prospective_consumers` | one individual or household-level semantic choice unit |
| `unit.0481.air-operator-primary` | `air_transport_operators` | one operator-function semantic unit |

The singular units are mechanism-coverage constructions, not claims that the
historical populations were homogeneous or contained one member. Reusing a
Population Model creates no shared policy, observation, private state, intent,
or result.

The retained carrier field `canonical_institutions` also registers three explicitly
typed resource domains: a Singapore market channel, consumer decision-unit
domain, and air-operator function domain. `semantic_kind` and
`participant_disposition` prevent those registries from being mistaken for
single legal institutions.

### Resource objects

Eight stable objects cover original and replacement product classes,
associated-device context, incident context, product flow, production,
inventory/remedy, and transport encounter. Context envelopes are not device,
stock, incident, or operator inventories; exact instances and prestates remain
unknown until admitted input supplies them.

## 6. Opening records and routes

The 34 opening records comprise four authority/capacity records, four unit
assignments, four institutional or resource-domain relationships, eight exact-
addressed routes, eight resource-state records, and six business-process
records.

| Route | Endpoints | Boundary |
|---|---|---|
| consumer intake | consumer ↔ exact Samsung, CPSC, or outlet recipient | one request or report per sender/recipient pair |
| Samsung--CPSC | corporate interface ↔ recall interface | firm report and authority response remain distinct |
| Samsung--regional | corporate interface ↔ Singapore regional unit | global publication is not regional receipt |
| regional--outlet | regional unit ↔ one channel unit | partner choice and inventory effect remain external |
| outlet--consumer | outlet unit ↔ one consumer unit | offer, request, eligibility, stock, and handoff separated |
| safety--CAAC | exact Samsung or CPSC sender ↔ CAAC | no merged safety knowledge or guaranteed warning |
| safety--U.S. DOT | exact Samsung or CPSC sender ↔ DOT | no merged FAA/PHMSA/CPSC/Samsung mind or guaranteed order |
| transport--operator | exact CAAC or DOT sender ↔ operator unit | issuer, jurisdiction, delivery, procedure, and handling remain scoped |

Every record carries a non-empty evidence or accepted-decision basis. Effective
intervals describe this configuration, not complete historical tenure,
staffing, population size, or route availability.

## 7. Exogenous inputs and policy meanings

Six inputs cover bounded hazard/report opportunity; device/product context;
institutional authority; product-flow and resource opportunity; recall/remedy
process opportunity; and post-issuance transport/encounter opportunity. Each
has exact typed targets, visibility, evidence basis, causal limit, and
`outcome_forcing = false`.

Nine selected policy meanings cover time, information, hazard/intake, routes,
authority, product/production/inventory, remedy, public action, and twelve
shared lifecycles. Every implementation remains `unbound`; every execution
consequence is `fail_closed`. The selections contain no algorithm, prompt,
backend, parameter, calibrated value, or realized outcome.

## 8. Bounded lineage

The illustrative lineage is:

```text
Samsung crisis interface
  -> Singapore regional implementation unit
  -> Singapore outlet/channel unit
  -> owner or prospective-consumer unit
```

It uses three exact routes and seven released intents spanning product-flow
direction, replacement-program proposal, partner coordination, local remedy,
outlet posture, outlet remedy response, and consumer exchange/refund request.
Intent and message, issue and delivery, direction and partner choice, offer
and stock, request and eligibility, handoff and completion, and result and
later observation remain distinct.

The lineage contains no implementation and implies nothing about full-roster
behavior.

## 9. Completion and validation expectations

Normal closure occurs at the core horizon or an early process closure.
Pending objects produce bounded-incomplete closure with owner, state, version,
reason, and next eligible event. Invariant failure closes fail-safe. Historical
outcome is not required.

| Expected inventory | Count |
|---|---:|
| products / situations | 8 / 22 |
| observation / private-state / intent placements | 40 / 28 / 37 |
| lifecycle families | 12 |
| named / Population actors | 4 / 4 |
| resource objects / registry entries | 8 / 7 |
| opening records / routes | 34 / 8 |
| structural selections / exogenous inputs | 6 / 6 |
| policy meanings / sensitivity overlays | 9 / 6 |

These are integrity expectations, not behavioral or scientific results.

## 10. Execution boundary and limitations

The configuration is non-executable. Parsing and static admission confer no
carrier projection, ParticipantArtifact, policy implementation, binding,
runtime bundle, trace, replay, simulation, evaluation, or scientific claim.

Exact incident realization, internal investigation, product-flow result,
production result, inventory and remedy availability, consumer decision,
authority issuance, delivery, operator handling, enforcement, and completion
remain unresolved until separately admitted inputs and implemented policies
produce typed results.

The next legal responsibility is fail-closed static configuration admission,
followed by separately identified carrier projection and bounded binding.
