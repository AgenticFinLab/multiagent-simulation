# H2EPR-0616 V1 carrier review

> `ACCEPTED_CARRIER_DECISION / NON_EXECUTABLE`

## 1. Decision

```text
carrier_verdict=
  V1_COMPATIBLE_VIA_EVENT_QUALIFIED_INTERNAL_MAPPING_AND_SCENARIO_SEMANTICS

contracts_v1_successor_required=NO
event_qualified_mapping_profile_required=YES
scenario_semantics_required=YES
implementation_authorized=NO
```

All nine released products can be represented with existing V1 entity,
ParticipantArtifact, RuntimeField/RuntimeValue, WorldState, ActionIntent,
MessageIntent, disposition, StateDelta, trace, bundle, and manifest carriers.
The event requires a new internal mapping profile and Scenario semantic layer;
neither is a Contracts successor.

## 2. Audited surfaces

The review used:

- the exact H2EPR-0616 Roster Definition release v0.1;
- the H2EPR-0616 semantic inventory, mapping specification, Scenario candidate,
  and complete interface closure;
- H2EPR Contracts V1 specifications and core/runtime schemas;
- the accepted Panic 1907 consolidated mapping and carrier review as a method
  reference only;
- the existing roster mapping loader/profile and its conformance tests; and
- the current action, communication, trace, bundle, and manifest carriers.

This is a semantic review. No schema, loader, Contract, test, policy, runtime,
or tracked release file is changed by it.

## 3. Existing V1 capacity

| V1 surface | H2EPR-0616 use |
|---|---|
| EntityRegistryEntry | canonical institutions, office/unit sub-entities, Scenario processes, and excluded boundaries |
| ParticipantArtifact | exact released capability, role/unit profile, constraints, information boundary, actions, and later policy identity |
| RuntimeField/RuntimeValue | observations, private state, process records, typed parameters, provenance, visibility, and scopes |
| WorldState | canonical institutions, technical state, relationships, access, resources, process state, and capability-scoped private state |
| ObservationPayload | frozen recipient-visible projection with stable references |
| DecisionRecord | exact observations, released decision basis, reasons, and emitted intent/message refs |
| ActionDefinition/ActionIntent | all 54 event- and capability-qualified intent placements |
| MessageIntent/fanout | recipient-specific request, report, direction, status, consultation, and correction messages |
| action and communication dispositions | semantic admission and communication handling distinct from institutional or technical result |
| StateDelta | reducer-owned private, process, technical, relationship, and result transitions |
| trace and seals | ordered decisions, intents, messages, deliveries, results, deltas, versions, hashes, and unresolved objects |
| RuntimeScenarioBundle/RunManifest | release, mapping, Scenario, configuration, assembly, variant, policy, Contract, code, time, RNG, and exogenous-input identity |

V1 TypedValue supports scalars and flat scalar arrays. Current compound
technical, meeting, classification, report, and outreach semantics can be
normalized as stable object/version references plus checked atomic fields.

## 4. Requirement disposition

The review classifications are:

- `V1_DIRECT`: an existing Contract surface directly carries the item;
- `V1_INTERNAL_MAPPING`: an explicit event registry/projection/validator is
  required;
- `SCENARIO_SEMANTICS`: the event must define the process or authoritative
  state outside Agents and the Contract; and
- `SUCCESSOR_WATCHPOINT`: stop only if implementation proves the stated
  irreducible loss.

| Released requirement | Existing carrier | Disposition | Finding |
|---|---|---|---|
| canonical institutions and office/unit actors | entity registry, ParticipantArtifact, relations | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | separate sub-entity and host records preserve identity without duplicating institutional truth |
| office and concurrent appointment capacity | authority refs and process/relation fields | `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTICS` | action/message capacity must be explicit; ambiguity fails closed |
| population-unit identity and assignment | entity/artifact profiles and world relations | `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTICS` | configuration declares units; V1 carries them |
| exact release identity | artifact hashes, bundle/config hashes, manifest components | `V1_INTERNAL_MAPPING` | release and product hash closure is sufficient |
| 62 observation placements | ObservationPayload and RuntimeFields | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | capability-qualified catalog removes label collisions |
| participant-time delivery and correction | RuntimeValue metadata, delivery records, versions | `V1_DIRECT` + `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTICS` | production/routing policy is event-owned |
| compound technical and organizational records | stable refs and atomic RuntimeFields | `V1_INTERNAL_MAPPING` | no current nested object is irreducible |
| 44 behaviorally material private-state placements | process-state RuntimeFields and StateDelta | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | reducer paths preserve visibility and replay |
| 54 intent placements | ActionDefinition and ActionIntent | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | event/capability qualification is injective |
| typed parameters and object versions | ActionDefinition, flat parameters, stable refs | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | one canonical carrier per property |
| internal versus communicative intents | ActionIntent, MessageIntent, correlation | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | materialization remains conditional and separate |
| multi-recipient reporting/notification | deterministic fanout and recipient delivery records | `V1_DIRECT` + `SCENARIO_SEMANTICS` | each recipient keeps a separate history |
| investigation, control, meeting, category, report, assignment, and outreach lifecycles | process state, versions, dispositions, StateDelta | `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTICS` | event lifecycle registry supplies business meaning |
| authority, route, access, and capacity checks | authority refs, relations, access and state versions | `V1_DIRECT` + `SCENARIO_SEMANTICS` | adjudication rules are event-specific |
| partial, failed, expired, no-effect, adverse, and corrected outcomes | dispositions, reason codes, process state, deltas | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | exact result vocabulary remains event-owned |
| technical-to-institutional multi-hop lineage | decision/action/message/result refs and trace parents | `V1_DIRECT` + `SCENARIO_SEMANTICS` | each hop is a separate business object and delivery |
| attack, access, query, copy, containment, and notification mechanics | exogenous manifest, WorldState, actions/results/deltas | `SCENARIO_SEMANTICS` | these are not Agent or generic Contract responsibilities |
| structural variants and termination | config/bundle identity, trace closure | `V1_INTERNAL_MAPPING` + `SCENARIO_SEMANTICS` | system-only choices can be pinned without leaking into policy |
| deterministic causal closure | versions, refs, dispositions, deltas, trace/seal | `V1_DIRECT` + `V1_INTERNAL_MAPPING` | validators must enforce the declared graph |

No row currently has a concrete carrier counterexample.

## 5. Internal profile work required

The accepted Panic 1907 profile is an event-specific implementation reference,
not a reusable H2EPR-0616 profile. H2EPR-0616 requires the following internal
work when separately authorized:

| Current limitation | H2EPR-0616 requirement | Internal change |
|---|---|---|
| source product count is fixed to 12 in the current release loader | exact nine-product release | derive and validate the count from the event release/profile rather than accepting another event's constant |
| accepted profile identity is not event-qualified | independent event mappings must not collide | use `h2epr.roster-consolidated-mapping.0616.v0_1` |
| first-event capability/fixture semantics are financial and institution-centered | office actors, responsibility units, technical state, delivery, classification, and notification | define an event-specific catalog and bounded fixture |
| one event's structural variants and causal cases are embedded in its fixture | attack pressure, route/delivery, office capacity, technical result, and notification variants | declare H2EPR-0616 variant identities and validators |
| existing conformance path proves a financial request carrier | H2EPR-0616 needs a technical-to-institutional delivery lineage | add one bounded event-specific lineage fixture and negative cases |

These changes are to the internal loader/profile surface. They do not justify
editing Contracts V1 or reusing Panic 1907 semantics under a new label.

## 6. Identifier and flat-field feasibility

The proposed complete intent catalog fits the current V1 StableId bound:

| Check | Maximum | V1 limit | Result |
|---|---:|---:|---|
| `machine_action_type` | 119 characters | 128 | PASS |
| `action_schema_version` | 124 characters | 128 | PASS |
| proposed observation companion field | 125 characters | 128 | PASS |

The longest cases arise from the Sector Lead capability and
`notify_authorized_healthcare_leadership`. These margins are acceptable for
the fixed v0.1 release but are a loader assertion, not a convention to extend
with additional suffixes. Companion observation fields must receive the same
mechanical length assertion during implementation.

Flat fields preserve current compound semantics because the released products
require bounded named components, stable source/version links, and delivery
metadata rather than arbitrary recursive objects. No participant requires a
free-form hidden document or live world-state dereference.

## 7. Scenario semantic boundary

The Scenario, not the mapping or Contracts V1, must define:

- canonical institution, office/unit, assignment, capacity, relationship,
  access, and route state;
- attack attempts and access/query/copying/disclosure results;
- information-product production, routing, delivery, correction, freshness,
  and dispute;
- investigation, control, meeting, SIRT, category, reporting, assignment,
  outreach, notification, and affected-cohort lifecycles;
- authority, access, target, prestate, capacity, concurrency, duplicate,
  expiry, and feasibility adjudication;
- technical and institutional result vocabularies and reducer invariants;
- structural variants, exogenous inputs, termination, and unresolved work; and
- causal lineage, replay, and run identity.

The Scenario cannot add participant behavior, private knowledge, or authority
absent from the released products.

## 8. Successor watchpoints

| Watchpoint | Evidence required before a successor is justified | Current finding |
|---|---|---|
| multi-office institutional identity | office actors cannot share a canonical institutional record without merging their information or duplicating institutional truth | no counterexample; sub-entity/host relations preserve both |
| capacity-qualified authority | one actor's concurrent capacity cannot be represented or checked without conflating IHiS and MOH authority | no counterexample; capacity/object refs and validators are sufficient |
| compound technical record | a required ordered or repeated record cannot be reconstructed from stable refs and atomic fields without ambiguity | no counterexample in released semantics |
| partial multi-target control | one admitted control affecting several targets cannot preserve component results using one disposition and correlated deltas | no counterexample; component refs/deltas can preserve partial effects |
| notification fanout scale | recipient/cohort delivery cannot be represented without erasing recipient-specific result identity | no counterexample; fanout plus cohort/result records are sufficient |
| private-state confidentiality | visibility scopes and projection cannot prevent cross-actor or backend exposure | no counterexample; V1 has scoped values and actor projection |
| deterministic correction | earlier decision basis cannot coexist with a corrected later product under stable versions | no counterexample; versioned observation refs preserve both |
| identifier capacity | an exact released machine ID cannot fit the StableId grammar without lossy aliasing | no counterexample; current maxima are 119/124 |
| atomic causal transition | required all-or-none/partial semantics cannot be recovered from one disposition, multiple delta refs, invariants, and causal parents | no counterexample in current design |

Convenience, shorter code, a preference for nested JSON, or dislike of long
event-qualified identifiers is not a carrier failure. A watchpoint failure
must present the smallest reproducible semantic loss before any successor
proposal.

## 9. First implementation-slice recommendation

After design promotion and a separate implementation authorization, the first
slice should be a fail-closed release/mapping loader plus one high-information
lineage fixture. It should prove:

1. exact hash-checked derivation of 9 products, 29 decisions, 62 observations,
   44 private-state placements, and 54 intents with event/capability-qualified
   identities;
2. assembly of distinct technical/security/operational/office interfaces that
   share canonical IHiS or SingHealth institutional truth without shared
   private state;
3. one bounded source/version-preserving path from technical finding through
   security or operational escalation to a senior/institutional delivery and
   later lifecycle observation; and
4. negative checks for wrong capacity, wrong recipient, undelivered evidence,
   stale/corrected versions, duplicate intent, result-as-intent, and
   cross-office private-state access.

The slice stops at deterministic mapping and lineage conformance. It need not
implement all 54 behavioral intents or run a full event simulation.

## 10. Carrier-review conclusion

```text
Contracts V1                           KEEP
Panic 1907 mapping profile             RETAIN AS EVENT-SPECIFIC REFERENCE
H2EPR-0616 event-qualified profile     REQUIRED INTERNALLY
H2EPR-0616 Scenario semantics          REQUIRED
Contracts successor                    NOT JUSTIFIED
```

The project owner accepted this carrier decision under `OD-CM-07`. It
authorizes design use only; implementation remains separately governed.
