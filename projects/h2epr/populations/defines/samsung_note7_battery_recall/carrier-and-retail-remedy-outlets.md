# Galaxy Note7 carrier and retail remedy outlets

## 1. Model overview

| Field | Value |
|---|---|
| Model name | Carrier and retail product-flow, notice, and remedy units |
| Event and interval | Samsung Galaxy Note7 Battery Recall Crisis; 2 September--15 October 2016 |
| Choice unit | One carrier or retail outlet responsibility unit able to act on local sales, notice, inventory, exchange, or refund matters |
| Population scope | Wireless-carrier and authorized retail channels reached by corporate, recall, or regional routes; each unit remains attached to its organization and location |
| Primary decision situations | Corporate or authority notice; local stock and eligibility; consumer request; renewed stop instruction; adverse lifecycle result |
| Aggregation boundary | Units may be counted by channel or jurisdiction, but information, inventory observation, authority, intent, and result remain unit-specific |
| State authority | Scenario owns legal and corporate product state, delivery, inventory truth, eligibility, handoff, payment, and completion; units retain local assessments and intent references |
| Evidence use and explanatory scope | Official corporate and CPSC records support distributed channel choices and constraints, not universal outlet receipt or compliance |

The population preserves the difference between a global partner request, a
formal recall, a local outlet's received instructions, and the action or
remedy a customer ultimately experiences.

## 2. Population scope and representation

One unit is the smallest carrier or retailer responsibility assignment that
can receive a bounded instruction or request and choose a permitted local
sales, notice, stock, exchange, or refund intent. A nationwide company may
contain many outlets, but the Scenario may aggregate them only when they share
the same delivered authority, inventory observation, and action owner. It may
not duplicate one inventory or commitment across units.

The population excludes Samsung regional units, CPSC, consumers, transport
operators, payment and logistics processes, and physical device handling.
Mandatory legal transitions and mechanical point-of-sale effects remain with
the Scenario. A named intermediary becomes an Agent only if unique authority
or a durable event-specific decision history materially changes the accepted
question. A behavior returns to Scenario ownership when accepted evidence
shows it was automatic after delivery and left no outlet-level alternative.

## 3. Evidence and theoretical foundation

The [participant-evidence record](../../../events/samsung_note7_battery_recall/participant-evidence-v0.1.md)
supplies the source and claim ledger. `0481-P-C07` establishes the channel
roles, `0481-P-C03`--`C04` bound regional relations, `0481-P-C08` separates
consumer choices, and `0481-P-C16` separates request, implementation, and
result.

CPSC and Samsung records identify carriers and retailers as sales, notice,
replacement, exchange, refund, and stop-action channels. Samsung's 11 October
statement is a request to partners, while the CPSC chairman's 13 October
statement is an aggregate assessment of response. Neither proves universal,
synchronous, or outlet-level action.

The model retains two competing mechanisms: prompt action on a delivered
safety or authority record, and constrained local action while inventory,
eligibility, or instruction remains incomplete. Channel type, local stock,
message route, customer demand, and authority scope may change the choice; no
fixed compliance propensity is inferred.

## 4. Event role and relationships

| Relationship | Unit-owned choice | Other owner |
|---|---|---|
| unit ↔ Samsung central or regional interface | acknowledge, question, or locally respond to a delivered partner request or remedy term | sender owns its intent; Scenario owns delivery and corporate state |
| unit ↔ CPSC or jurisdictional authority | interpret and act within a delivered warning or recall record | authority owns action; Scenario owns legal state, notice route, and admissibility |
| unit ↔ consumer | communicate local terms and accept, reject, or seek clarification on a bounded remedy request | consumer owns selection; Scenario owns eligibility, device handoff, payment, and completion |
| unit ↔ inventory or logistics process | request stock, quarantine, transfer, or disposition | Scenario owns stock truth, physical movement, and result |

No outlet observes another outlet's private assessment or stock merely because
both belong to one channel class.

## 5. Decision situations, information, and state

| Observation | Unit-specific meaning | Availability and missing behavior | Behavioral use |
|---|---|---|---|
| `delivered_product_direction` | Corporate or regional sales, exchange, or remedy request addressed to the unit | Available only after delivery; a global page is not receipt | stop and remedy review |
| `delivered_authority_notice` | Warning, formal recall, expansion, or jurisdictional instruction | Authority, product scope, and effective time remain explicit | authority-constrained action |
| `local_inventory_observation` | Dated observation of original, replacement, or alternative device stock accessible to the unit | May be stale, partial, or unavailable | remedy proposal and fulfillment request |
| `consumer_request` | A delivered purchase, report, exchange, refund, or information request | Request is not eligibility or completion | customer-facing choice |
| `intent_result_notice` | Lifecycle notice for a stop, message, stock, or remedy intent | Missing notice leaves the attempt unresolved | retry, revision, and suppression |

Each unit retains `local_action_assessment`, `open_instruction_questions`,
`observed_inventory_reference`, and `active_intent_references`. Initialization
is unknown or empty. Updates require lawful observation, intent issuance, or a
delivered result. The state cannot contain aggregate compliance, undisclosed
stock, another outlet's action, future authority state, or the 2017 diagnosis.

## 6. Behavioral model

### New safety, partner, or authority record

The unit checks sender authority, jurisdiction, product identity, effective
time, and local feasibility. It may request clarification, propose a local
sales or exchange posture, communicate bounded terms, or request inventory
action. If a material safety instruction is incomplete, a targeted question
with a finite review condition is required; indefinite silent continuation is
not admissible.

### Consumer remedy request

The unit checks the delivered remedy terms and observed local availability. It
may acknowledge and forward the request, propose an eligible local option,
request missing evidence, or explain a bounded inability. The unit cannot
create eligibility, stock, payment, device transfer, or completion.

### Supersession or adverse result

A renewed stop request, expanded recall, replacement-device signal, stock
failure, refused request, expiry, or superseding instruction reopens the local
choice. A current equivalent intent suppresses duplication until its review
condition. The model allows prompt precaution and feasibility-constrained
response as competing mechanisms; neither is a fixed historical replay.

## 7. Intent and result boundary

| Intent | Meaning and target | Required content | Scenario-owned result |
|---|---|---|---|
| `request_channel_clarification` | Seek bounded authority, product, remedy, or timing information | question, source, jurisdiction, product identity, due condition | delivery, answer, delay, or failure |
| `set_local_product_posture` | Propose stop, hold, resume, or exchange posture within unit authority | device class, action, basis, timing, review condition | admissibility, system update, inventory effect, implementation |
| `publish_outlet_notice` | Communicate bounded safety or remedy terms through the unit's channel | audience, source, product class, advice, offer terms, issue time | publication, delivery, comprehension, response |
| `request_inventory_action` | Seek stock verification, quarantine, allocation, or transfer | item identity, quantity class if observed, location, action, urgency | inventory truth, feasibility, movement, result |
| `respond_to_remedy_request` | Accept for adjudication, qualify, redirect, or refuse a consumer request | request reference, stated basis, proposed path, uncertainty | eligibility, handoff, payment, refund, exchange, completion |

Aggregated outlet intents may describe channel response patterns but never
constitute a collective carrier-retailer decision.

## 8. Operationalization and uncertainty

The Scenario instantiates units with channel type, jurisdiction, organization
and outlet identity, authorized routes, local inventory observation, and
event-time availability. Qualitative action states are `instruction_unknown`,
`review_open`, `local_action_proposed`, and `response_reopened`. Channel type
does not determine behavior by itself.

Structural uncertainty concerns company-versus-outlet granularity;
compositional uncertainty concerns which channels and locations are present;
measurement uncertainty concerns stock, receipt, and aggregate response.
Sensitivity varies delivery, authority scope, availability, and lifecycle
results without inventing a compliance rate or fitting historical uptake.

## 9. Worked cases and falsification

**Initial U.S. remedy channel, reconstructed and exposed.** A unit receives a
formal recall and a proposed replacement plan. It may communicate options and
request stock, but cannot claim the replacement is locally available. Removing
stock observation preserves the information response while replacing a local
offer with a clarification or inventory request.

**Global partner stop request, reconstructed and exposed.** Receipt of the
11 October request reopens any active sales or exchange posture. Before
delivery the unit cannot act as if it knew the request; after delivery it must
respond or name a bounded authority or implementation blocker.

**Remedy failure, illustrative.** A pending exchange request suppresses an
unchanged duplicate. A delivered stock failure permits a refund path,
clarification, or revised request. The model fails if a corporate request
becomes universal implementation, if a recall creates stock, or if outlet
intent proves consumer completion.

## 10. Limitations and references

This model does not reconstruct named companies or outlets, measure receipt,
stock, compliance, remedy completion, or return rates, estimate behavioral
weights, or support calibration, prediction, effectiveness, or universal
intermediary claims.

References: Samsung and U.S. CPSC statements and recall notices of
2 September through 13 October 2016 listed with exact locators and limitations
in the participant-evidence record.
