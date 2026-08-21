# H2EPR-0288 V1 carrier review

> `ACCEPTED_CARRIER_DECISION / NON_EXECUTABLE`

## 1. Decision

```text
carrier_verdict=
  V1_COMPATIBLE_VIA_CONSOLIDATED_INTERNAL_MAPPING_AND_SCENARIO_SEMANTIC_EXTENSION

contracts_v1_successor_required=NO
internal_mapping_profile_successor_required=YES
scenario_semantic_extension_required=YES
implementation_authorized=NO
```

All 12 released semantic products can be represented using existing V1
ParticipantArtifact, RuntimeField/RuntimeValue, WorldState, ActionIntent,
MessageIntent, disposition, StateDelta, trace, bundle and manifest carriers.
The release does require a consolidated successor to the current internal
two-role mapping profile and an event scenario semantic layer. Neither is a
Contracts successor.

## 2. Audited sources

The review used the fixed release tree plus these current V1 and accepted
reference surfaces:

- `projects/h2epr/contracts/v1/README.md`
- `projects/h2epr/contracts/v1/specifications/entity-and-participant-contract.md`
- `projects/h2epr/contracts/v1/specifications/action-communication-and-time.md`
- `projects/h2epr/contracts/v1/specifications/run-trace-and-seals.md`
- `projects/h2epr/contracts/v1/schemas/core/h2epr_core.schema.json`
- `projects/h2epr/contracts/v1/schemas/runtime/runtime_scenario_bundle.schema.json`
- `projects/h2epr/contracts/v1/schemas/runtime/run_manifest.schema.json`
- `projects/h2epr/contracts/v1/schemas/runtime/simulation_trace.schema.json`
- `projects/h2epr/agents/bindings/panic_1907/two-role-binding.md`
- `projects/h2epr/agents/bindings/panic_1907/binding.json`
- the accepted two-role intent, observation, lifecycle and cross-object
  registries
- `projects/h2epr/src/h2epr/agents/mapping.py`
- `projects/h2epr/src/h2epr/agents/carrier.py`

This is a semantic carrier review. No schema, loader, test, contract or runtime
was changed.

## 3. What V1 already carries

| V1 surface | Relevant capacity | Full-Roster use |
|---|---|---|
| EntityRegistryEntry | stable identity, runtime disposition and aggregate-member links | entity, population-unit, scenario process and excluded boundary |
| ParticipantArtifact | actor identity, source IDs, representation, profiles, constraints, information boundary, actions and initial resources | one artifact with one or more capability projections |
| RuntimeField/RuntimeValue | scalar or flat-array value, provenance, availability, visibility, scopes, consumers and review state | observations, private state, process records and parameters |
| WorldState | versioned entities, resources, relations, commitments, risks, access grants, public signals and process states | canonical world, business lifecycle and actor-private state |
| ResourceState | owner, type, unit, bounds, quantity visibility, conservation rule and state version | one canonical resource ledger per owner/resource |
| ObservationPayload | stable observation ID and RuntimeFields | frozen actor-visible projection |
| DecisionRecord | actor, observation refs, rule/commitment refs, action/message refs and reason codes | replayable semantic decision basis |
| ActionDefinition/ActionIntent | versioned action type, targets, parameters, authority, resources, time, observation and decision refs | all 107 capability-qualified intent placements |
| MessageIntent and fanout | one recipient per intent, typed content, route/time, confidentiality, correlation and idempotency | request, notice, statement, reply and fanout |
| ActionDisposition | admission status, reasons, accepted/rejected parameters, conflicts, state versions, deltas and retry | intent admission distinct from result |
| CommunicationDisposition and delivery records | route admission/transport state and later delivery | issue, delivery and receipt separation |
| StateDelta | entity/path, transition, before/after, state versions, invariants and causal parents | reducer-owned private/business/resource transitions |
| trace and seals | ordered observations, decisions, intents, messages, dispositions, deliveries, deltas, hashes and closure | causal audit and replay |
| RuntimeScenarioBundle | entity registry, artifacts, world state, actions, routes, observation access, exogenous inputs and hash | complete assembled scenario identity |
| RunManifest | bundle/config/code/contract/participant hashes, component versions, time and RNG identity | release/mapping/scenario/run pinning |

V1 `TypedValue` permits string, number, boolean, null or a flat array of those
scalar types. The full Roster does not require arbitrary nested payloads when
compound objects are represented by stable object/version references and
separate atomic RuntimeFields.

## 4. Requirement-by-requirement disposition

The classification vocabulary is:

- `V1_DIRECT`: existing contract surface carries the requirement directly;
- `V1_INTERNAL_MAPPING`: explicit registry/projection/validation is required,
  but no V1 change is needed;
- `SCENARIO_SEMANTIC_EXTENSION`: event-owned state, process or policy must be
  designed outside the Agent and V1 contract;
- `NARROW_SUCCESSOR_WATCHPOINT`: no current failure, but implementation must
  stop if the stated concrete loss appears.

| Released requirement | Existing carrier | Disposition | Reason |
|---|---|---|---|
| historical entity and runtime actor identity | EntityRegistryEntry, ParticipantArtifact | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | V1 carries both; assembly decides identity equivalence |
| several capabilities on one institution | ParticipantArtifact profiles, action-space refs and source IDs | `V1_INTERNAL_MAPPING` | capability composition is a mapping concern, not a new participant type |
| population choice-unit identity and weight | entity/participant profile RuntimeFields | `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTIC_EXTENSION` | scenario declares units/weights; V1 carries them |
| one canonical resource owner across capabilities | ResourceState and entity refs | `V1_DIRECT` + `SCENARIO_SEMANTIC_EXTENSION` | ownership/adjudication policy is event semantics |
| Definition identity/version/hash | ParticipantArtifact profile/hash and RunManifest inputs | `V1_INTERNAL_MAPPING` | explicit projection and hash closure are sufficient |
| 115 observation placements | ObservationPayload and RuntimeFields | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | capability-scoped catalog prevents label collision |
| participant-time, freshness and provenance | RuntimeValue plus explicit companion fields | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | metadata is available; mapping makes event-time/freshness explicit |
| compound dossiers, proposals, loans and offers | stable refs plus flat RuntimeFields | `V1_INTERNAL_MAPPING` | lossless atomic projection is available for current semantics |
| behaviorally material private state | WorldState.process_states/StateDelta or a deterministic DecisionRecord-derived private view | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | explicit transition uses reducer state; consumption cursor/no-intent abstention is reconstructed from sealed decision records |
| governance and authority | claimed authority refs, process states and access/relationship fields | `V1_DIRECT` + `SCENARIO_SEMANTIC_EXTENSION` | scenario establishes scope and competent forum |
| 107 intent placements | ActionDefinition and ActionIntent | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | capability-qualified action type removes global-name collision |
| versioned, typed parameter contracts | ActionDefinition, action schema version and flat RuntimeFields | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | registry supplies per-intent semantics and cross-checks |
| resource request/offer | ActionIntent resource carrier and ResourceState | `V1_DIRECT` | owner/control and prestate validators are mapping/scenario work |
| internal versus communicative actions | ActionIntent, MessageIntent and correlation | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | message materialization is conditional and separate |
| multi-recipient communication | one-recipient MessageIntent plus fanout plan | `V1_DIRECT` | V1 already defines deterministic fanout |
| request/case/proposal/loan lifecycles | process-state RuntimeFields, state versions and StateDeltas | `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTIC_EXTENSION` | reusable event lifecycle registry supplies the business semantics |
| intent, transport, business disposition and result separation | action/communication dispositions, process state, result and delta trace | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | no new status layer is required |
| partial, delayed, failed and no-effect outcomes | ActionDisposition, reason codes, explicit-no-effect and process state | `V1_DIRECT` | event-specific business reason/state remains scenario-owned |
| two-hop KT–NBC–NYCH lineage | message/action correlations and trace causal refs | `V1_DIRECT` + `SCENARIO_SEMANTIC_EXTENSION` | scenario owns routes and separate business cases |
| withdrawal service and payment form | actions, process states, resources and results | `SCENARIO_SEMANTIC_EXTENSION` | not an Agent or generic contract responsibility |
| call-money matching, booking and settlement | actions, resources, state and trace | `SCENARIO_SEMANTIC_EXTENSION` | NYSE/venue rules are event semantics |
| structural variants | config hash, runtime bundle hash and component versions | `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTIC_EXTENSION` | immutable system-only variant set can be fully run-pinned |
| Treasury deposits and affiliated-bank history | exogenous manifest and initial state | `V1_DIRECT` + `SCENARIO_SEMANTIC_EXTENSION` | explicitly exogenous by release decision |
| cross-object causal closure | trace refs, versions, dispositions, deltas and seals | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | validators must enforce the semantic graph |

No row has a demonstrated `CONCRETE_CARRIER_COUNTEREXAMPLE`.

## 5. Why the current two-role mapping cannot be reused unchanged

The current mapping implementation is an accepted reference for Knickerbocker
and NYCH. It is not the Contracts V1 carrier itself. The following limitations
require an internal mapping-profile successor:

| Current assumption | Full-Roster conflict | Required internal change |
|---|---|---|
| intent registry is a dictionary keyed only by `semantic_id` | 107 placements contain repeated labels across capabilities | key by `(capability_id, semantic_id)` and generate capability-qualified action types |
| every IntentDefinition contains one `actor_id` | one semantic capability may be instantiated by several population units; one actor may compose several capabilities | separate capability definition from actor assembly |
| participant inventory equals the set of intent actors | product count and actor count differ | validate release capability coverage and scenario actor assembly separately |
| one participant maps to one Definition ID | a named institution can also receive a population-derived lending/resource capability | permit one artifact to reference several released capability products |
| observation contracts are actor/ID tables with a small fixed value-type set | the full Roster needs capability-scoped reusable domains, boolean/number/flat arrays and compound atomic projections | generalize the internal observation registry; V1 RuntimeField already supports the values |
| parameter types omit several V1 scalar forms and compound-record projection | full Roster uses richer typed terms, intervals and object/version refs | expand internal parameter types and canonical field-family rules |
| scenario coherence is hard-coded for `new_york_clearing_house` | all roles require generic lifecycle, identity, authority and resource cross-checks | replace actor-specific code with declarative cross-object validators |
| scenario identity recognizes only the NYCH structural fork | NBC, committee, venue, population and resource-pool choices must also be run-pinned | use one immutable structural-variant set in scenario configuration |
| machine action type is `h2epr.action.<semantic_id>` | repeated semantic labels collide | qualify with event and capability |

These are limitations of `h2epr.agent-definition-mapping.v0_2_2`, not evidence
that the stable V1 machine contract is too narrow.

## 6. Scenario semantic extension boundary

The event scenario must add semantic content for the following without
redefining Agent behavior:

- actor/capability/unit assembly and population weights;
- entity, host, membership, clearing, intermediary and venue relationships;
- participant-time observation projection and delivery;
- business-object IDs and state machines;
- governance, authority, collateral and resource-control adjudication;
- service, payment, clearing, credit, request, review and result mechanics;
- call-money route, venue, matching, trade, settlement and repayment;
- structural variants and exogenous inputs; and
- reducer invariants and reason-code vocabularies.

This extension produces an event-specific scenario definition/configuration
that is then carried and hashed by V1. It does not belong in a general Agent
Definition or in the stable exchange contract.

## 7. Narrow successor watchpoints

The following are stop conditions, not proposed seams:

| Watchpoint | Concrete evidence required before a successor is justified | Current finding |
|---|---|---|
| atomic multi-object transition | one admitted action must update several object/resource records atomically, but one disposition with multiple delta IDs and invariants cannot preserve all-or-none/partial semantics | no counterexample; V1 groups deltas under one disposition |
| concurrent business-object identity | two live cases/offers/loans cannot be distinguished or referentially validated using stable IDs, versions and flat process-state records | no counterexample in released semantics |
| lossless repeated structured observations | an ordered/repeated compound input required by behavior cannot be reconstructed from stable refs and atomic fields without ambiguity | no counterexample; current dossiers and offers can be normalized |
| partial-result closure | accepted/rejected parameters, deltas, reason codes and process states cannot identify which part of a resource/proposal was realized | no counterexample; explicit component refs are sufficient in design |
| first-class release/mapping identity | RunManifest hashes and component versions cannot recover the exact release, mapping, assembly and variant inputs | no counterexample; config/bundle/artifact hashes close the identity |
| private-state confidentiality | RuntimeValue visibility scopes and actor-private observation projection cannot prevent another actor/backend from seeing state | no counterexample; V1 has scoped visibility |
| decision-only private-state update | a released no-intent decision must change behaviorally material state that cannot be derived from DecisionRecord/observations and cannot legally use an existing admitted intent | no current counterexample; released abstention/cursor state can be trace-derived, while effectful posture changes accompany admitted actions/results |

If implementation produces one of these exact losses, work stops and presents
the smallest successor seam that repairs it. Convenience, shorter code, a
preference for nested JSON or an unattractive mapping is not a carrier failure.

## 8. First implementation-slice recommendation

After owner acceptance and formal promotion, the first implementation slice
should be a **mapping-loader and conformance slice**, not a simulation or Rule
policy.

It should prove three hard properties:

1. load and hash-check all 12 released products, deriving exactly 115
   observation and 107 intent placements with capability-qualified IDs;
2. assemble a bounded event fixture in which one institution has both
   `bank_resource_decision` and `call_money_lender` capabilities but only one
   actor, authority graph and resource ledger; and
3. connect one broker-borrower funding request/offer lifecycle and one
   host-scoped depositor unit, validating observation scope, object versions,
   idempotency, resource ownership and result separation.

The slice stops after deterministic mapping validation and artifact identity.
It emits no policy decision, runs no simulation and does not claim historical
validity. A later slice can map the named Agent policies only after this carrier
risk has been retired.

## 9. Carrier-review conclusion

The full Roster increases semantic breadth substantially, but it does not
invalidate V1. The correct next boundary is:

```text
Contracts V1                         KEEP
two-role mapping profile v0.2.2     RETAIN AS FROZEN REFERENCE
consolidated mapping profile        SUCCESSOR REQUIRED INTERNALLY
Panic 1907 scenario semantics       EXTENSION REQUIRED
Contracts successor seam            NOT JUSTIFIED
```

This verdict is accepted as a design decision. Implementation remains
unauthorized until a separate implementation authorization is issued.
