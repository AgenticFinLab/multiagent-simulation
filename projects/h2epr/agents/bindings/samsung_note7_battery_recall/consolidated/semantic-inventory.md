# H2EPR-0481 released semantic inventory

## 1. Fixed source boundary

This inventory is derived only from
`H2EPR-0481-ROSTER-DEFINITION-RELEASE-v0.1`. It does not add behavior,
participants, authority, or historical facts. Repeated reader-facing labels
remain capability-qualified placements.

| Derived measure | Count |
|---|---:|
| semantic products | 8 |
| Agent Definitions | 4 |
| Population Models | 4 |
| decision and population situations | 22 |
| observation placements | 40 |
| distinct observation labels | 32 |
| private-state placements | 28 |
| intent placements | 37 |
| distinct intent labels | 37 |

## 2. Products and decision commitments

| Capability | Product kind | Released situations | Count |
|---|---|---|---:|
| `samsung_crisis_decision_interface` | Agent Definition | `DC-SAM-1`, `DC-SAM-2`, `DC-SAM-3` | 3 |
| `cpsc_recall_decision_interface` | Agent Definition | `DC-CPSC-1`, `DC-CPSC-2`, `DC-CPSC-3` | 3 |
| `caac_warning_decision_interface` | Agent Definition | `DC-CAAC-1`, `DC-CAAC-2` | 2 |
| `us_dot_emergency_order_decision_interface` | Agent Definition | `DC-DOT-1`, `DC-DOT-2` | 2 |
| `samsung_regional_implementation_units` | Population Model | delivered central posture; local remedy under constraints; renewed stop or adverse result | 3 |
| `carrier_and_retail_remedy_outlets` | Population Model | new safety, partner, or authority record; consumer remedy request; supersession or adverse result | 3 |
| `note7_owners_and_prospective_consumers` | Population Model | purchase or ordinary use; delivered safety concern; remedy and replacement reopening | 3 |
| `air_transport_operators` | Population Model | authority record before or after effect; device encounter; changed rule or adverse result | 3 |

The four Population Models define reusable unit-level choice semantics. They do
not establish the number, weight, composition, jurisdiction, or identity of
units instantiated by a later configuration.

## 3. Observation inventory

### 3.1 Released observations by capability

| Capability | Released observation labels |
|---|---|
| `samsung_crisis_decision_interface` | `delivered_incident_record`, `investigation_update`, `product_flow_snapshot`, `authority_or_partner_record`, `intent_result_notice` |
| `cpsc_recall_decision_interface` | `delivered_firm_safety_report`, `incident_summary`, `remedy_proposal`, `replacement_device_signal`, `intent_result_notice` |
| `caac_warning_decision_interface` | `delivered_device_safety_record`, `delivered_recall_record`, `dangerous_goods_context`, `operator_risk_record`, `intent_result_notice` |
| `us_dot_emergency_order_decision_interface` | `delivered_safety_predicate`, `delivered_recall_scope`, `transport_feasibility_record`, `authority_context`, `intent_result_notice` |
| `samsung_regional_implementation_units` | `delivered_central_direction`, `local_authority_record`, `partner_response`, `local_inventory_observation`, `intent_result_notice` |
| `carrier_and_retail_remedy_outlets` | `delivered_product_direction`, `delivered_authority_notice`, `local_inventory_observation`, `consumer_request`, `intent_result_notice` |
| `note7_owners_and_prospective_consumers` | `local_device_experience`, `delivered_safety_message`, `local_remedy_offer`, `purchase_opportunity`, `intent_result_notice` |
| `air_transport_operators` | `delivered_transport_record`, `local_procedure_record`, `device_encounter`, `peer_or_authority_message`, `intent_result_notice` |

### 3.2 Label reuse and qualification

`intent_result_notice` occurs in all eight products, and
`local_inventory_observation` occurs in two. Neither is a shared object or
broadcast surface. The stable identity is
`<capability>.<observation>`, and every delivered projection retains producer,
source object and version, route, recipient, delivery time, correction or
supersession relation, and freshness status.

## 4. Private decision state

### 4.1 Replayable participant state

| Capability | Released private-state labels |
|---|---|
| `samsung_crisis_decision_interface` | `current_safety_assessment`, `open_investigation_questions`, `active_intent_references` |
| `cpsc_recall_decision_interface` | `current_authority_assessment`, `open_information_requests`, `active_action_references` |
| `caac_warning_decision_interface` | `current_transport_assessment`, `open_information_requests`, `active_warning_references` |
| `us_dot_emergency_order_decision_interface` | `current_hazard_assessment`, `open_authority_questions`, `active_order_references` |
| `samsung_regional_implementation_units` | `local_resolution_assessment`, `open_partner_questions`, `active_offer_reference`, `active_intent_references` |
| `carrier_and_retail_remedy_outlets` | `local_action_assessment`, `open_instruction_questions`, `observed_inventory_reference`, `active_intent_references` |
| `note7_owners_and_prospective_consumers` | `current_safety_assessment`, `current_remedy_assessment`, `associated_device_reference`, `active_intent_references` |
| `air_transport_operators` | `current_rule_assessment`, `open_scope_questions`, `active_encounter_reference`, `active_intent_references` |

Each placement is participant-private and reducer-versioned. Initialization is
the released unknown, empty, or dated-prehistory default. Valid updates are an
issued intent, a lawful delivered observation, or a delivered lifecycle
notice. No placement is authoritative incident, inventory, recall, remedy,
legal-effect, device, transport, compliance, or enforcement truth.

### 4.2 Environment-owned business truth

The Scenario owns product identity and flow, device and incident state,
investigation objects, inventory and remedy availability, recall and warning
records, order issuance and effect, routes and delivery, consumer handoff,
transport encounters, institutional relationships, resources, typed results,
and their version histories.

## 5. Intent inventory

### 5.1 Released intents by capability

| Capability | Released intent labels |
|---|---|
| `samsung_crisis_decision_interface` | `request_safety_investigation`, `issue_product_flow_direction`, `announce_replacement_program`, `request_partner_stop`, `decide_production_posture`, `publish_safety_message` |
| `cpsc_recall_decision_interface` | `issue_consumer_warning`, `request_incident_information`, `request_remedy_information`, `issue_recall_action`, `expand_recall_action` |
| `caac_warning_decision_interface` | `request_transport_risk_information`, `issue_transport_warning`, `qualify_transport_warning` |
| `us_dot_emergency_order_decision_interface` | `request_hazard_information`, `qualify_emergency_order`, `issue_emergency_order` |
| `samsung_regional_implementation_units` | `request_regional_clarification`, `coordinate_local_partner_response`, `propose_local_remedy`, `publish_local_safety_message` |
| `carrier_and_retail_remedy_outlets` | `request_channel_clarification`, `set_local_product_posture`, `publish_outlet_notice`, `request_inventory_action`, `respond_to_remedy_request` |
| `note7_owners_and_prospective_consumers` | `choose_device_use_posture`, `submit_incident_report`, `request_safety_information`, `choose_purchase_posture`, `request_exchange_or_refund` |
| `air_transport_operators` | `request_transport_clarification`, `publish_operator_notice`, `request_device_identification`, `propose_carriage_denial_or_handling`, `adopt_stricter_local_measure`, `escalate_transport_ambiguity` |

### 5.2 Intent interface families

| Family | Included intent meanings | Required separation |
|---|---|---|
| information and investigation request | safety, incident, remedy, hazard, transport, regional, channel, inventory, or identity inquiry | request, delivery, access, work, answer, and later observation |
| product-flow and production posture | sales, shipment, exchange, inventory, purchase, use, production, or partner-stop proposal | issue, authority, admission, implementation, physical effect, and result |
| remedy | program announcement, local offer, outlet response, exchange or refund request | proposal, eligibility, stock, selection, handoff, payment, and completion |
| public communication | safety, warning, outlet, operator, or regional message | authorship, issue, publication, delivery, comprehension, response, and effect |
| authority action | recall, recall expansion, transport warning, warning qualification, emergency order, or order qualification | proposal, valid issuance, publication, legal effect, delivery, implementation, and enforcement |
| incident and transport response | incident report, device identification, carriage response, stricter measure, or ambiguity escalation | allegation, delivery, verification, authority, action, and physical result |

## 6. Shared lifecycle inventory

| Lifecycle family | Authoritative owner | Required states or transitions |
|---|---|---|
| participant intent | Scenario reducer with participant-visible notices | pending, acknowledged, partial, completed, failed, expired, cancelled, superseded |
| information product and message | producing and delivery processes | produced, routed, delivered, corrected, superseded, stale, failed |
| investigation and information request | investigation or institutional process | requested, admitted, assigned, active, partial, completed, failed, declined, expired |
| incident report and intake | safety-intake process | alleged, submitted, delivered, admitted, aggregated, corrected, closed |
| product-flow posture | product-flow process | proposed, admitted, active, partial, completed, failed, reversed, superseded |
| production posture | production process | proposed, admitted, active, suspended, halted, resumed, failed, superseded |
| inventory and partner action | inventory/partner process | requested, acknowledged, allocated, moved, unavailable, refused, completed |
| remedy offer and fulfillment | remedy process | proposed, reviewed, available, selected, accepted, handed off, refunded, exchanged, failed |
| recall authority action | jurisdictional recall process | proposed, issued, effective, expanded, corrected, superseded, closed |
| warning or emergency-order action | issuing institution and post-issuance process | proposed, qualified, issued, published, effective, delivered, superseded, expired |
| device use and purchase posture | device/market process | proposed, admitted, transferred, used, ceased, retained, failed, superseded |
| transport encounter and handling | transport process | encountered, identified, admitted, denied, unloaded, isolated, returned, escalated, closed |

## 7. Authority, resource, and temporal inventory

The release requires distinct authority scopes for Samsung corporate product
and production directions, CPSC recall actions, CAAC warning issuance, the
U.S. Secretary-level emergency-order decision, regional implementation,
outlet-local action, consumer choice, and operator-local action. A request does
not manufacture the target's authority or resources.

Material resource classes are device populations, production and product-flow
capacity, partner and publication routes, jurisdiction-specific inventory and
remedy stock, consumer-associated devices and handoff capacity, transport
encounters and handling capacity, institutional legal records, and
investigation or information capacity.

Event time, production/as-of time, issue time, effective time, delivery time,
correction time, review time, and expiry time remain distinct. January 2017
diagnosis is future-only for every 2016 participant.

## 8. Inventory verdict

The eight released products reconcile without adding a participant or changing
a Definition. Their complete carrier-facing surface is 22 situations, 40
observation placements, 28 private-state placements, 37 intent placements,
and twelve shared lifecycle families. These are structural counts, not a claim
about behavior, historical fit, calibration, policy effectiveness, or
scientific validity.
