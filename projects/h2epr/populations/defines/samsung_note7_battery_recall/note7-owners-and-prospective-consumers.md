# Galaxy Note7 owners and prospective consumers

## 1. Model overview

| Field | Value |
|---|---|
| Model name | Note7 owner and prospective-consumer safety and remedy choice units |
| Event and interval | Samsung Galaxy Note7 Battery Recall Crisis; 19 August--15 October 2016 |
| Choice unit | One person or household decision unit controlling one bounded purchase, use, report, power-down, exchange, or refund choice |
| Population scope | Current owners, replacement-device recipients, and prospective purchasers reached through local product, safety, recall, or remedy channels |
| Primary decision situations | Purchase opportunity; device experience; delivered warning or recall; remedy availability; replacement-device reopening |
| Aggregation boundary | Units may be summarized by device and remedy state, but observation, interpretation, device relation, intent, and result remain unit-specific |
| State authority | Scenario owns device identity and physical state, message delivery, legal and product state, eligibility, handoff, refund, exchange, and aggregate outcomes |
| Evidence use and explanatory scope | Official instructions and remedy records expose a bounded choice set; they do not reveal individual beliefs, receipt, compliance, or response rates |

The model represents heterogeneous individual choices that affect incident
signals and product/remedy flows. It does not create a collective “consumer”
mind or infer a risk preference from the historical outcome.

## 2. Population scope and representation

One unit controls a bounded decision involving a particular device relation
and local information. A household may be the choice unit when its members
share control of the same device and remedy request; the Scenario must then
avoid duplicating the device, claim, or request across people. Current owners,
replacement-device recipients, and prospective purchasers may face different
choices, but these are states or role types rather than personalities.

The population excludes Samsung, authorities, outlets, transport operators,
physical battery failure, notice delivery, and remedy execution. It has no
shared incident count, inventory view, or legal interpretation. A named person
would require unique causal authority absent from the accepted question. A
choice family should return to Scenario ownership if removing heterogeneity
does not alter any material signal, use, purchase, or remedy route.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md)
supplies source roles and temporal boundaries. `0481-P-C08` supports the
individual choice families, `0481-P-C07` bounds intermediary relations,
`0481-P-C13` bounds transport relations, and `0481-P-C16` separates advice,
selection, implementation, completion, and effect.

Samsung, CPSC, and transport records advised owners to power down or refrain
from use and exposed replacement, exchange, and refund paths. Those records
demonstrate offered choices, not individual receipt, comprehension, belief,
device condition, eligibility, or action. Reports and administrative counts
are attributed snapshots, not a distribution of consumer hazard experience.

Three mechanisms remain alternatives: precaution after a credible delivered
warning; continued use or delayed remedy under incomplete delivery,
availability, or feasibility; and renewed action when replacement-device
signals revise the perceived option set. The model adopts no utility
function, risk coefficient, compliance type, or population rate.

## 4. Event role and relationships

| Relationship | Unit-owned choice | Other owner |
|---|---|---|
| unit ↔ device | use, power down, retain, or present the associated device | Scenario owns identity, battery state, failure, damage, and physical transition |
| unit ↔ Samsung or outlet | request information, exchange, refund, or another offered remedy | recipient owns its response; Scenario owns delivery, eligibility, stock, payment, handoff, completion |
| unit ↔ CPSC or reporting route | submit a bounded incident report or seek authority information | authority owns review; Scenario owns routing, admissibility, aggregation, and result |
| unit ↔ transport operator | communicate device status or respond to a delivered carriage instruction | operator owns its local action; Scenario owns delivery, physical carriage, enforcement, and result |

A unit cannot observe another consumer's private experience or infer aggregate
truth from a public count.

## 5. Decision situations, information, and state

| Observation | Unit-specific meaning | Availability and missing behavior | Behavioral use |
|---|---|---|---|
| `local_device_experience` | Direct observation concerning the unit's associated original or replacement device | Does not establish cause or another device's state | use and reporting choices |
| `delivered_safety_message` | Samsung, authority, outlet, or operator content actually delivered to the unit | Sender, jurisdiction, device scope, and event time are preserved | safety interpretation |
| `local_remedy_offer` | Delivered exchange, refund, replacement, or information terms at an accessible route | Offer is not eligibility, stock, handoff, or completion | remedy selection |
| `purchase_opportunity` | A locally available offer to obtain a device | Product state may be stale or constrained | purchase or refrain choice |
| `intent_result_notice` | Lifecycle notice for a report, information, purchase, or remedy intent | Missing notice keeps the attempt unresolved | retry and revision |

Each unit retains `current_safety_assessment`, `current_remedy_assessment`,
`associated_device_reference`, and `active_intent_references`. Initial values
are unknown or supplied as dated prehistory. Updates require direct local
experience, delivered content, the unit's own intent, or a delivered result.
The unit cannot use aggregate incident truth, undelivered warnings, future
recall or order states, other consumers' choices, or January 2017 diagnosis.

## 6. Behavioral model

### Purchase or ordinary use under incomplete information

A prospective purchaser or owner checks the locally delivered product and
safety state. It may purchase, refrain, continue bounded use, seek information,
or record a finite wait for a named missing fact. Device identity and current
authority scope constrain the choice; the historical sale or stop is not a
target policy.

### Delivered safety concern

After a material warning, recall, incident experience, or operator instruction,
the unit may power down, stop use, report the experience, seek information, or
request a remedy. If it continues use or waits, the model requires an explicit
missing route, feasibility constraint, or review condition; it cannot encode
permanent inaction as an unexplained type.

### Remedy and replacement reopening

Given a delivered local offer, the unit may request exchange, refund, or
information, or defer under a stated access constraint. A replacement device
does not guarantee safety. A delivered renewed signal, superseding recall,
failed request, or changed availability reopens both safety and remedy choice.
A pending equivalent request normally suppresses duplication.

## 7. Intent and result boundary

| Intent | Meaning and target | Required content | Scenario-owned result |
|---|---|---|---|
| `choose_device_use_posture` | Propose use, power-down, retain, or cease-use posture for an associated device | device identity, observed basis, timing, review condition | physical use state, failure, damage, enforcement, effect |
| `submit_incident_report` | Communicate a bounded local experience to Samsung, authority, or outlet route | device identity, event time, observation, uncertainty, sender | delivery, admissibility, investigation, aggregation, response |
| `request_safety_information` | Seek current product, authority, transport, or remedy information | question, device scope, recipient, reason, reply condition | delivery, answer, delay, or failure |
| `choose_purchase_posture` | Purchase, refrain, or defer at a local opportunity | product identity, offer reference, timing, reason or review condition | admissibility, payment, transfer, inventory effect |
| `request_exchange_or_refund` | Select and request one delivered remedy path | device and offer references, selected remedy, channel, event time | eligibility, stock, acceptance, handoff, payment, completion |

Counts, proportions, or sequences of intents are derived analysis. They do not
become a population decision or prove compliance and effectiveness.

## 8. Operationalization and uncertainty

The Scenario instantiates units with a device relation (`prospective`,
`original_owner`, or `replacement_owner`), jurisdiction, available routes,
and dated observations. Device relation constrains admissible choices but does
not assign belief or policy. Qualitative assessments are `information_open`,
`concern_present`, `remedy_open`, and `choice_reopened`.

Composition, delivery, feasibility, and interpretation are explicit
uncertainties. Population size, device allocation, receipt, and response rates
are not supplied by this model. Sensitivity varies message delivery, device
relation, remedy availability, and lifecycle results without fitting a
historical compliance distribution.

## 9. Worked cases and falsification

**Initial replacement offer, reconstructed and exposed.** An original-device
owner who receives a local offer may request exchange, refund, or more
information. Removing the delivered offer preserves safety choices but removes
the remedy request until another route becomes available.

**Undelivered warning, illustrative.** A public warning that has not reached a
unit cannot directly change its private assessment. Delivering the same
warning makes power-down, report, information, and remedy responses available;
it does not force one historical response.

**Replacement-device reopening, reconstructed and exposed.** A replacement
owner receives a renewed warning or recall and must reconsider use and remedy.
Changing the device label without delivering the new record does not provide
future knowledge. The model fails if all consumers share a warning
automatically, if a request completes its own refund, or if aggregate incident
counts become personal experience.

## 10. Limitations and references

The model does not estimate beliefs, risk tolerance, message receipt,
compliance, incident propensity, remedy uptake, return rates, or welfare. It
does not identify causal effects, calibrate a population, predict behavior, or
generalize beyond the event-bound choice surfaces.

References: Samsung, U.S. CPSC, CAAC, and U.S. DOT records listed with exact
locators, participant-time limits, and withdrawal consequences in the shared
participant-evidence record.
