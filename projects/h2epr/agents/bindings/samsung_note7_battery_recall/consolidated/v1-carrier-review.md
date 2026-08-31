# H2EPR-0481 Contracts V1 carrier review

## 1. Review question

Can Contracts V1 preserve all eight released participant products without
changing behavior or losing identity, information, state, intent, authority,
resource, lifecycle, result, or replay meaning?

## 2. Classification

| Requirement | Classification | Reason |
|---|---|---|
| event, entity, actor, capability, policy, intent, observation, result, and trace identity | `V1_DIRECT` | the carrier already provides stable identity and payload surfaces |
| capability-qualified reused labels | `V1_INTERNAL_MAPPING` | event-qualified keys prevent `intent_result_notice` and inventory-label collisions |
| Population Model reuse across regional, outlet, consumer, and operator units | `V1_INTERNAL_MAPPING` | distinct actor/unit identity preserves local state and results |
| source/version, as-of, issue, effective, delivery, correction, and expiry distinctions | `V1_DIRECT` plus validation | existing time and causal metadata carry the distinctions |
| institutional and resource relationships | `V1_DIRECT` plus event-qualified graphs | scope and effective interval are Scenario records |
| business lifecycle registries | `SCENARIO_SEMANTIC_EXTENSION` | Contracts carries object/result data; the Scenario owns allowed transitions |
| recall, warning, and order legal effect | `SCENARIO_SEMANTIC_EXTENSION` | issuance predicates, jurisdiction, effect, and supersession are domain semantics |
| inventory, remedy, custody, and transport conservation | `SCENARIO_SEMANTIC_EXTENSION` | object ownership and conservation are reducer rules, not new carrier fields |
| January 2017 firewall | `SCENARIO_SEMANTIC_EXTENSION` plus admission validation | event-time visibility and future-fact rejection are Scenario obligations |

## 3. Adversarial cases

| Case | Required preservation | Finding |
|---|---|---|
| the same result-notice label reaches all eight capability types | capability and recipient qualification | no collision after event/capability/actor qualification |
| one Singapore regional record is available but another jurisdiction is not evidenced | unit-local instantiation and no transitive knowledge | preserved by evidence-gated unit identity and exact delivery |
| a corporate stop request reaches one outlet but not another | per-message addressing and delivery | supported without broadcast inference |
| an owner requests exchange while stock is unavailable | intent/result and inventory separation | typed partial, failed, or pending outcome preserved |
| CPSC recall scope later expands to replacement devices | versioned authority lifecycle | prior scope and decision bases remain replayable |
| CAAC warning and U.S. emergency order have different issuers and post-issuance owners | capacity, jurisdiction, and lifecycle separation | distinct actors and Scenario processes preserve both |
| an operator sees a suspected device encounter | allegation, identification, authority, and physical action separation | no carrier loss found |
| future January 2017 diagnosis is supplied to a 2016 observation | temporal visibility rejection | validation can reject the projection deterministically |

## 4. Successor threshold

A Contracts successor would be required only if a concrete released case could
not preserve a stable identity, exact recipient delivery, temporal version,
authority/capacity relation, object/result lineage, typed failure, or replay
reference without overloading a field. No such case was found.

The need for event-specific lifecycle registries, authority rules, or a more
general configuration schema is not itself a Contracts counterexample. Those
responsibilities belong to Scenario semantics or the configuration admission
surface.

## 5. Verdict and watchpoints

`V1_COMPATIBLE_VIA_EVENT_QUALIFIED_INTERNAL_MAPPING_AND_SCENARIO_SEMANTICS`

Contracts V1 remains unchanged. Later implementation must still prove:

- all eight capability placements project without collision;
- consumer and other Population actors retain unit-local memory and policy;
- issuance, publication, effect, delivery, implementation, and enforcement do
  not collapse;
- inventory, remedy, custody, and transport results conserve objects; and
- replay preserves negative, partial, corrected, superseded, and unresolved
  outcomes.

This review establishes engineering representability, not runtime readiness or
scientific validity.
