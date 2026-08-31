# H2EPR-0481 consolidated mapping specification

## 1. Identity and source authority

| Field | Value |
|---|---|
| Mapping profile | `h2epr.roster-consolidated-mapping.0481.v0_1` |
| Event | `H2EPR-0481` |
| Source release | `H2EPR-0481-ROSTER-DEFINITION-RELEASE-v0.1` |
| Carrier | H2EPR Contracts V1 |
| Mapping scope | complete release-wide semantic design |
| Execution status | design specification only |

The roster release remains authoritative for participant behavior. This
mapping qualifies identities and assigns Scenario ownership; it does not add
an observation, state variable, intent, authority, result, or policy.

## 2. Entity, actor, and capability assembly

| Released capability | Required assembly pattern |
|---|---|
| `samsung_crisis_decision_interface` | one institution-preserving Samsung corporate decision-interface actor with product-safety and represented production capacities kept explicit |
| `cpsc_recall_decision_interface` | one CPSC recall-interface actor; warning, information request, initial recall, and expansion authority remain intent-specific |
| `caac_warning_decision_interface` | one CAAC warning-issuance actor; post-issuance warning lifecycle remains Scenario-owned |
| `us_dot_emergency_order_decision_interface` | one Secretary-level U.S. DOT issuance actor with bounded FAA/PHMSA inputs; post-issuance lifecycle remains Scenario-owned |
| `samsung_regional_implementation_units` | one or more jurisdiction-scoped, evidence-gated units; no unit inherits another region's knowledge, stock, route history, or policy |
| `carrier_and_retail_remedy_outlets` | one or more channel-local units with exact host, outlet scope, inventory context, route, and result history |
| `note7_owners_and_prospective_consumers` | one or more individual or household-level choice units; aggregation never creates shared private state or a representative collective policy |
| `air_transport_operators` | one or more operator-function units with jurisdiction, rule, procedure, encounter, and handling scope kept explicit |

Stable carrier identity is event-qualified:

```text
event_id + entity_id + actor_id + capability_id + product_id + version
```

Population reuse produces distinct actors. Unit count, composition, host or
resource domain, jurisdiction, weight, initial state, and active status are
configuration choices.

## 3. Observation mapping

Every released observation is carried as a capability-qualified projection:

```text
Observation(
  observation_id,
  capability_id,
  producer_id,
  source_object_id,
  source_version,
  produced_or_as_of_time,
  route_id,
  recipient_actor_id,
  delivery_time,
  freshness,
  correction_or_supersession_ref,
  payload_projection
)
```

| Observation family | Carrier source | Scenario obligation |
|---|---|---|
| incident, defect, hazard, and replacement-device signal | observation payload plus source/version metadata | retain allegation, verification, aggregation, uncertainty, product class, and delivery boundaries |
| investigation, authority, recall, legal, or dangerous-goods context | versioned information product | expose only records validly available to the recipient at the decision time |
| product flow, inventory, remedy, offer, and purchase opportunity | scoped object projection | preserve locality, staleness, availability uncertainty, and separation from completion |
| partner, operator, peer, consumer, and institutional message | communication plus explicit route/delivery record | forbid transitive delivery and set broadcast; retain sender and recipient histories |
| device experience or encounter | local observation projection | preserve reported identity and condition without promoting it to global device truth |
| intent-result notice | lifecycle result projection | expose only a delivered notice and never infer success from silence |

`intent_result_notice` and `local_inventory_observation` are qualified by
capability and actor. A common reader-facing label is not a common object.

## 4. Private-state mapping

Each of the 28 placements maps to actor-local, reducer-versioned state. The
carrier stores the capability-qualified state key, prior version, causal input
references, new value, and decision trace reference. Only the participant
policy may propose its update; only the reducer commits it after a lawful
observation, issued intent, or delivered result.

Private assessments and open-question sets never duplicate product, incident,
inventory, recall, remedy, order, legal-effect, transport, or compliance
truth. Active-reference state records what the actor attempted and the latest
notice it received; it is not an execution ledger.

## 5. Intent mapping and adjudication

Every intent uses:

```text
Intent(
  intent_id,
  event_id,
  actor_id,
  capability_id,
  intent_type,
  target_id,
  object_refs,
  parameters,
  authority_scope,
  issue_time,
  idempotency_key,
  review_or_expiry_condition,
  causal_observation_refs
)
```

The Scenario checks, in order: identity and schema; target and parameter
closure; actor/capability ownership; capacity and authority; institutional or
resource relationship; object prestate; route and delivery eligibility;
resource availability; duplicate or concurrent intent; temporal phase; and
physical or institutional feasibility. Rejection is typed and trace-visible.

| Intent class | Adjudication owner | Result boundary |
|---|---|---|
| investigation or information request | investigation, intake, or addressed institutional process | request, delivery, access, work, and answer remain distinct |
| product-flow, inventory, production, purchase, or use posture | product, inventory, production, market, or device process | direction or choice does not guarantee admission, implementation, transfer, use, or effect |
| remedy proposal or request | remedy and fulfillment process | proposal, eligibility, stock, selection, handoff, refund/exchange, and completion remain distinct |
| public or partner communication | information and delivery process | intent, message, publication, delivery, comprehension, response, and effect remain distinct |
| recall, warning, or emergency order | jurisdiction-qualified institutional process | valid issuance, effect, delivery, implementation, enforcement, and outcome remain distinct |
| incident report or transport response | intake or transport process | allegation, identification, authority, physical action, and result remain distinct |

## 6. Lifecycle and result mapping

The twelve lifecycle families listed in the semantic inventory are Scenario-
owned business objects. Each has stable identity, version, owner, state,
predecessor and supersession links, idempotency relation, valid transition
cause, result or failure, and deterministic replay lineage.

All participant intents share the released lifecycle vocabulary: pending,
acknowledged, partial, completed, failed, expired, cancelled, and superseded.
Business lifecycles may use more specific states, but every result returns a
typed disposition and zero or more StateDeltas. Only reducers mutate
authoritative state.

## 7. Institutions, authority, relationships, and resources

| Semantic requirement | Carrier treatment | Scenario extension |
|---|---|---|
| canonical Samsung, CPSC, CAAC, and U.S. DOT identities | entity and relationship records | event-time capacity, jurisdiction, and route availability |
| corporate, recall, warning, order, regional, outlet, consumer, and operator authority | capability-scoped authority graph | intent-specific target, object, effective interval, and prestate checks |
| regional, outlet, consumer, and operator unit scope | event-qualified actor/unit mapping | host or resource domain, jurisdiction, composition, and active interval |
| device, product class, inventory, remedy stock, production, and transport encounter | resource and business-object references | canonical ownership, availability, conservation, and physical-result rules |
| public, partner, regulator, regional, outlet, consumer, and operator routes | communication and observation fields | route eligibility, transport, delivery, correction, and recipient visibility |
| recall and transport legal effect | institution and business lifecycle | issuance predicate, effective time, scope, supersession, enforcement and result |

Requesting information or action grants no authority, access, stock, delivery
capacity, production control, legal effect, enforcement capacity, or physical
result.

## 8. Cross-object conformance rules

1. Exact roster release and every component hash must match.
2. Every actor references exactly one released participant product.
3. Every released capability appears in the assembly and no extra capability appears.
4. A Population Model may be reused only through distinct actor and unit identities.
5. Entity, actor, unit, capacity, authority, resource-owner, and relationship identities are non-interchangeable.
6. Capability-qualified observation and intent identities are immutable.
7. Observation production, transport, delivery, projection, and decision-time freeze are distinct.
8. Missing delivery conveys no knowledge; publication is not universal receipt.
9. Correction or supersession preserves the prior version and prior decision basis.
10. Private state changes only from permitted delivered observations, issued intents, or delivered notices.
11. An active reference never substitutes for authoritative execution state.
12. Every intent has a stable idempotency key, review or expiry rule, and causal inputs.
13. Intent issue, route admission, institutional acceptance, execution, result, StateDelta, and later observation remain distinct.
14. Authority is capacity-, jurisdiction-, target-, object-, and time-scoped.
15. Regional or channel hosting creates no shared knowledge or transitive authority.
16. Consumer aggregation creates no collective actor, memory, or policy.
17. Inventory, stock, transfer, exchange, refund, and device custody obey conservation rules.
18. Recall, warning, and order proposal, issuance, effect, delivery, implementation, and enforcement are separate.
19. Incident reports remain allegations until an authoritative process versions a finding.
20. January 2017 diagnosis cannot enter a 2016 observation, policy input, opening state, or result.
21. Every rejection, partial effect, failure, expiry, cancellation, and supersession remains trace-visible.
22. Structural variants and policy selections are immutable run inputs and are not participant observations unless delivered.
23. Completion retains unresolved objects with owner, state, reason, and next eligible event.
24. Replay must reproduce canonical state, dispositions, deliveries, results, and trace identity from the same admitted bundle.

## 9. Carrier disposition

The complete released surface is representable in H2EPR Contracts V1 through
direct fields, event-qualified internal mapping, and Scenario semantics. No
concrete information, identity, authority, lifecycle, resource, or result loss
requires a Contracts successor. Configuration representation remains a later
machine-surface question and does not alter this carrier verdict.

```text
carrier_verdict=V1_COMPATIBLE_VIA_EVENT_QUALIFIED_INTERNAL_MAPPING_AND_SCENARIO_SEMANTICS
contracts_successor_required=NO
released_products=8/8
observation_placements=40/40
private_state_placements=28/28
intent_placements=37/37
```

This verdict is an engineering compatibility claim only.
