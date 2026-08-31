# Galaxy Note7 air-transport operators

## 1. Model overview

| Field | Value |
|---|---|
| Model name | Airline, airport, and air-cargo operational response units |
| Event and interval | Samsung Galaxy Note7 Battery Recall Crisis; 14 September--15 October 2016 |
| Choice unit | One jurisdiction- and function-bounded operator responsibility unit able to communicate, handle, deny, escalate, or adopt a permitted stricter measure |
| Population scope | Passenger airlines, airport operating units, and cargo operators reached by CAAC or U.S. transport-authority routes |
| Primary decision situations | Delivered warning or order; pre-effective preparation; passenger or cargo encounter; ambiguity, exception, or adverse result |
| Aggregation boundary | Units may be summarized by jurisdiction and function, but authority, procedure, encounter, intent, and result remain unit-local |
| State authority | Scenario owns publication, delivery, legal effect, institutional duties, enforcement, physical carriage, and results; units retain local assessments and intent references |
| Evidence use and explanatory scope | Official CAAC and U.S. order records support bounded operational choices and duties, not universal receipt, compliance, or effectiveness |

This population connects two separate transport-authority lifecycles to local
operations without merging jurisdictions or treating airlines, airports, and
cargo operators as one actor.

## 2. Population scope and representation

One unit is the smallest operational responsibility assignment that receives
a jurisdiction-specific authority record or encounters a device and can
choose among permitted communication, handling, denial, escalation, or
stricter-measure intents. Passenger, airport, and cargo functions remain typed
because their information, obligations, and feasible actions differ. A real
organization may host several types; the Scenario must preserve their shared
institutional identity without copying one encounter, authority, or resource
state across them.

The population excludes CAAC and U.S. DOT issuance choices, post-issuance
publication and legal-effect processes, passengers, Samsung, CPSC, physical
device state, enforcement, and petition adjudication. A named operator becomes
an Agent only if unique authority or durable event-specific information is
causally necessary. A behavior returns to Scenario when the delivered rule
mechanically determines it and no local interpretation or procedural choice
remains.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md)
provides the evidence ledger. `0481-P-C09` establishes CAAC warning scope and
stricter-measure room, `0481-P-C11`--`C12` establish the U.S. issuance and
lifecycle distinction, `0481-P-C13` supports heterogeneous operator surfaces,
and `0481-P-C16` separates issuance, delivery, implementation, and result.

CAAC's warning set passenger restrictions, airline communication duties, and
scope for stricter measures. The U.S. emergency order set product, carriage,
effective-time, notification, and denial obligations. These authority records
do not prove when each unit received them or how each encounter was handled.

The model retains precautionary local handling and rule-constrained
implementation as competing mechanisms. Jurisdiction, function, delivered
scope, effective time, device identity, local procedure, and encounter
information may change the action. It adopts no generic operator personality
or compliance probability.

## 4. Event role and relationships

| Relationship | Unit-owned choice | Other owner |
|---|---|---|
| unit ↔ CAAC or U.S. order lifecycle | acknowledge, seek clarification, prepare, or act within a delivered authority record | issuer owns issuance; Scenario owns publication, delivery, effect, duties, enforcement |
| unit ↔ traveler or shipper | communicate rules, request device information, deny or qualify acceptance within authority | traveler or shipper owns its response; Scenario owns delivery and physical result |
| unit ↔ airport, airline, or cargo peer | route bounded encounter or handling information and request coordination | each peer owns its response; Scenario owns routing and shared operational state |
| unit ↔ enforcement or authority route | escalate ambiguity, suspected violation, or exception | authority owns adjudication; Scenario owns delivery, enforcement, and result |

No unit receives the other jurisdiction's rule or another operator's private
assessment without a valid route.

## 5. Decision situations, information, and state

| Observation | Unit-specific meaning | Availability and missing behavior | Behavioral use |
|---|---|---|---|
| `delivered_transport_record` | CAAC warning, U.S. order, or bounded authority clarification delivered to the unit | Jurisdiction, issue time, effective time, scope, and source remain explicit | preparation and action |
| `local_procedure_record` | Current operator procedure available to the unit | May be incomplete, superseded, or more restrictive only when authority permits | communication and handling |
| `device_encounter` | A passenger, baggage, cargo, or shipment encounter involving a reported device identity and condition | Allegation is not verified device truth | encounter response |
| `peer_or_authority_message` | Delivered coordination, exception, or clarification record | Other messages remain unknown | ambiguity resolution |
| `intent_result_notice` | Lifecycle notice for communication, denial, handling, or escalation intent | Missing notice keeps the action unresolved | retry, revision, suppression |

Each unit retains `current_rule_assessment`, `open_scope_questions`,
`active_encounter_reference`, and `active_intent_references`. They begin empty
or from dated Scenario prehistory and update only through legitimate delivery,
the unit's own intent, or a delivered result. They cannot contain future legal
effect, another unit's private procedure, enforcement outcome, petition result,
January 2017 diagnosis, or later retrospective findings.

## 6. Behavioral model

### Authority record before or after effect

On delivery, the unit checks jurisdiction, function, product scope, and issue
and effective times. Before legal effect it may prepare or communicate only as
permitted; it cannot treat the U.S. prohibition as already effective. After
effect it may communicate, request device information, adopt a permitted
procedure, or seek clarification. A named scope ambiguity may support a finite
review, not indefinite inaction.

### Device encounter

The unit checks the delivered rule and local procedure against the encounter.
It may communicate, request identifying information, deny or qualify carriage,
route the item for authorized handling, or escalate an ambiguity. It cannot
declare physical removal, enforcement, passenger compliance, or safe carriage.

### Changed rule or adverse result

A superseding authority record, stricter permitted measure, failed delivery,
refusal, repeated encounter, or enforcement notice reopens the response. A
pending equivalent intent normally suppresses duplication. Failure, expiry,
cancellation, supersession, or material new scope permits revision.

## 7. Intent and result boundary

| Intent | Meaning and target | Required content | Scenario-owned result |
|---|---|---|---|
| `request_transport_clarification` | Seek bounded scope, timing, identity, or handling information | authority, jurisdiction, question, encounter or product reference, due condition | delivery, answer, delay, or failure |
| `publish_operator_notice` | Communicate delivered restrictions or local procedure to travelers, shippers, or staff | source, jurisdiction, product scope, effective time, audience | publication, receipt, comprehension, compliance |
| `request_device_identification` | Ask a traveler, shipper, or peer for bounded device information | encounter, requested attributes, authority basis, response route | delivery, answer, verified identity, refusal |
| `propose_carriage_denial_or_handling` | Request denial, unloading, isolation, return, or another permitted response | encounter, rule, product identity, function, timing | admissibility, physical action, enforcement, carriage result |
| `adopt_stricter_local_measure` | Propose a stricter CAAC-permitted local operating measure | jurisdiction, scope, reason, duration, review condition | authority check, institutional adoption, publication, effect |
| `escalate_transport_ambiguity` | Route an exception, suspected violation, or unresolved hazard to an authorized recipient | encounter, known facts, uncertainty, rule, urgency | delivery, adjudication, enforcement, response |

Aggregate operator responses remain analysis outputs, not an additional
authority or collective choice.

## 8. Operationalization and uncertainty

The Scenario instantiates units by jurisdiction, function (`passenger_airline`,
`airport_operations`, or `cargo_operations`), institutional host, authorized
route, event-time availability, and delivered authority. Qualitative states
are `record_unreceived`, `scope_review`, `procedure_ready`, and
`encounter_reopened`.

Structural uncertainty concerns function and host granularity; compositional
uncertainty concerns which operators receive a route; measurement uncertainty
concerns device identity, delivery, and encounter records. Sensitivity varies
jurisdiction, effective time, function, scope, and lifecycle result without
fitting a compliance or enforcement rate.

## 9. Worked cases and falsification

**CAAC warning and stricter measure, reconstructed and exposed.** An airline
unit that receives the warning may publish a bounded notice and, if its
authority permits, propose a stricter measure. Removing that permission leaves
communication and ordinary handling available but removes the stricter-measure
intent.

**Signed U.S. order before effect, reconstructed and exposed.** A unit may
prepare and communicate after delivery on 14 October but cannot treat the ban
as legally effective before noon Eastern on 15 October. Advancing only the
clock changes the lifecycle constraint, not the issuing Agent's decision.

**Ambiguous device encounter, illustrative.** A reported device identity may
trigger information seeking or bounded handling; it is not self-verifying. A
failed identification request reopens escalation or handling review. The model
fails if CAAC and U.S. authority merge, if issuance gives every operator
instant knowledge, or if an intent creates its own denial or enforcement.

## 10. Limitations and references

The model does not reconstruct named operators, internal procedures, delivery,
compliance, enforcement, petition outcomes, carriage results, or aviation risk.
It supplies no calibrated rate, policy-effectiveness result, prediction, or
cross-jurisdictional generality claim.

References: Civil Aviation Administration of China, “Safety warning on air
transport of Samsung Note7 phones,” 14 September 2016; U.S. DOT/FAA/PHMSA,
*Emergency Restriction/Prohibition Order*, 14 October 2016; U.S. DOT, “DOT
Bans All Samsung Galaxy Note7 Phones from Airplanes,” 14 October 2016.
