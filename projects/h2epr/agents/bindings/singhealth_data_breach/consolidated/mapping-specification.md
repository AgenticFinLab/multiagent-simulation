# H2EPR-0616 consolidated mapping specification v0.1

> `ACCEPTED_DESIGN_SPECIFICATION / NON_EXECUTABLE / NO_IMPLEMENTATION_AUTHORITY`

## 1. Accepted decision

This specification maps every semantic placement in
`H2EPR-0616-ROSTER-DEFINITION-RELEASE-v0.1` into one event model. It does not
amend a Definition, add a participant, choose a behavioral policy, create a
runtime artifact, or authorize a run.

The mapping uses five distinct layers:

```text
canonical institution
  -> office actor or responsibility-unit actor
    -> released capability
      -> capability-scoped observations, private state, and intents
        -> Scenario-owned objects, lifecycles, delivery, and results
```

The principal accepted decision is:

> A released Agent Definition or Population Model is a capability authority.
> Office actors and responsibility units preserve their own decision and
> information boundaries while institutional identity, systems, resources,
> relationships, and realized results remain canonical Scenario truth.

This keeps IHiS and SingHealth from becoming unitary minds without creating a
second IHiS, SingHealth, SCM, authority graph, or result ledger for each
office.

## 2. Specification identity

| Item | Accepted value |
|---|---|
| mapping specification ID | `H2EPR-0616-CONSOLIDATED-MAPPING-v0.1` |
| mapping profile ID | `h2epr.roster-consolidated-mapping.0616.v0_1` |
| source release | `H2EPR-0616-ROSTER-DEFINITION-RELEASE-v0.1` |
| source manifest SHA-256 | `188f5117f02958997f8e1140d3d19fcbada296b1750223d8b3025e1cf537625e` |
| event semantic skeleton | `H2EPR-0616 event semantic skeleton`, version `0.2` |
| Scenario Definition | accepted `H2EPR-0616-EVENT-SCENARIO-DEFINITION-v0.1` |
| carrier target | H2EPR Contracts V1 |
| current status | accepted design specification; no executable binding |

The profile ID is event-qualified so it cannot collide with another event's
mapping. The generic loader schema may remain
`h2epr.roster-mapping-profile.v0_1`; this is an internal profile identity, not
a new Contracts version.

## 3. Identity model

### 3.1 Stable identities

| Identity | Required meaning | Owner |
|---|---|---|
| `institution_entity_id` | one canonical legal or organizational institution such as IHiS, SingHealth, MOH, MCI, or CSA | Scenario entity registry |
| `actor_entity_id` | one bounded office/officeholder or responsibility-unit decision interface | actor assembly |
| `runtime_actor_id` | one endogenous decision interface and later ParticipantArtifact | actor assembly |
| `unit_id` | one Scenario-declared technical or operational responsibility unit | population assembly |
| `capacity_id` | one office or concurrent appointment under which an authority claim or message is made | authority registry |
| `capability_id` | one released Agent Definition or Population Model behavior surface | mapping catalog |
| `definition_ref` | released product ID, version, path, and SHA-256 | release manifest |
| `machine_commitment_id` | capability-qualified reference to one released decision situation | derived commitment catalog |
| `business_object_id` | stable request, finding, message, meeting, control, report, plan, notification, or result identity | Scenario lifecycle registry |
| `observation_key` | `(event_id, capability_id, reader_observation_id)` | observation catalog |
| `intent_key` | `(event_id, capability_id, reader_intent_id)` | intent registry |
| `machine_action_type` | unique V1 `ActionIntent.action_type` | derived intent registry |

An office actor is a scoped sub-entity hosted by an institution; it is not a
duplicate legal institution. A responsibility unit additionally has a
function, assignment, access scope, availability interval, and composition.
The host relation grants neither institutional omniscience nor unscoped
authority.

### 3.2 Machine semantic identity

For each of the 54 intent placements:

```text
reader_intent_id = <released label, unchanged>
intent_key       = (H2EPR-0616, <capability_id>, <reader_intent_id>)
machine_action_type
  = h2epr.action.0616.<capability_id>.<reader_intent_id>
action_schema_version
  = h2epr.intent.0616.<capability_id>.<reader_intent_id>.v0_1
```

The same capability qualification applies to the 62 observation placements
and 29 decision situations:

```text
obs.<capability_id>.<reader_observation_id>
h2epr.commitment.0616.<capability_id>.<released_decision_id>
```

`request_incident_clarification` therefore remains readable in both products
but produces distinct Cluster ISO and Deputy GCEO machine identities. Reused
observation labels likewise remain distinct unless their independently checked
source, scope, recipient, time, and value-domain projections coincide.

## 4. Actor and capability assembly

### 4.1 Assembly rules

1. Scenario assembly, never filename matching, creates a runtime actor or
   responsibility unit.
2. Each office actor resolves to one actor entity, host-institution relation,
   authority/capacity record, and ParticipantArtifact.
3. Each population unit resolves to one unit identity, host, functional type,
   assignment, access scope, availability, and independent private state.
4. A capability can be instantiated only from its exact released product.
5. Several office actors may share an institutional host while retaining
   separate observations, private state, decisions, intents, and recipient
   histories.
6. Shared hosting never duplicates institutional state, system/data state,
   resources, relationships, category truth, delivery truth, or results.
7. A population model may instantiate several units, but units never share
   private state merely because they share a profile.
8. A unit or office cannot acquire another capability, authority, route, or
   information envelope through role-name similarity.
9. A concurrent appointment is a capacity-qualified authority and routing
   fact, not a merged actor or institution.
10. Splitting, merging, or adding a released decision interface requires a
    reviewed roster successor rather than an assembly shortcut.

### 4.2 Required assembly patterns

| Released capability | Required assembly pattern |
|---|---|
| `technical_administration_and_line_security_staff` | one or more institution-preserving, function-specific responsibility units; exact count and assignments are configuration choices |
| `security_incident_response_manager` | one SIRM office actor with explicit availability and coverage state |
| `cluster_information_security_officer` | one Cluster ISO office actor distinct from SIRM |
| `ihis_operational_and_scm_management` | one or more function-specific operational/SCM responsibility units; no collective IHiS-management mind |
| `singhealth_group_chief_information_officer` | one GCIO office actor with separately addressed IHiS and SingHealth routes |
| `cyber_security_governance_director_and_healthcare_sector_lead` | one office actor whose intent/message capacity is explicit; concurrent MOH appointment grants no implicit route or knowledge |
| `ihis_chief_executive_officer` | one IHiS CEO office actor; concurrent MOH CIO appointment remains a capacity boundary |
| `singhealth_deputy_group_chief_executive_officer` | one Deputy GCEO office actor with proposal/preparation authority but no implicit notification approval |
| `singhealth_group_chief_executive_officer` | one GCEO office actor whose direction/recommendation remains distinct from collective adoption and delivery |

External threat pressure, endpoint context, government recipients,
institutional notification, patients, and later aftermath retain their released
non-participant dispositions.

### 4.3 Representation projection

| Runtime interface | V1 representation |
|---|---|
| office-level endogenous decision interface | `autonomous_participant_agent` |
| responsibility unit instantiated from a Population Model | `aggregate_population_agent` |
| materialized Scenario-owned institutional process, if needed | `institutional_environment_agent` |

These values describe runtime decision interfaces, not natural-person status,
institutional personality, or a behavioral ontology. The released
representation and governance boundaries remain authoritative.

## 5. ParticipantArtifact projection

Every later actor artifact must carry:

| V1 field | Consolidated projection |
|---|---|
| `runtime_actor_id` | assembly identity |
| `source_participant_ids` | actor/unit identity and exact released product ID |
| `representation_class` | §4.3 rule |
| `participant_profile` | host, office/unit, capacity, capability, Definition version/hash, and representation limits |
| `behavior_profile` | released decision situations, obligations/hypotheses, and declared private state |
| `goal_set` | released role priorities without invented utility weights |
| `constraint_set` | information, authority, access, routing, result, and aggregation boundaries |
| `information_boundary` | exact capability-scoped observation catalog and delivery/freshness rules |
| `action_space_refs` | exact capability-qualified action types |
| `communication_policy_ref` | later reviewed route/performative policy reference |
| `initial_resource_state` | checked view of canonical resources; never a second resource authority |
| `rule_policy_ref` | deliberately unassigned by this non-executable design |

No ParticipantArtifact is generated at this stage. A later artifact is invalid
unless it binds a stable reviewed policy reference and changes hash whenever
its source product, capability, assembly, information boundary, action space,
capacity, or initial projection changes.

## 6. Observation mapping

### 6.1 Complete catalog

The mapping catalog contains exactly 62 entries, keyed by
`(event_id, capability_id, reader_observation_id)`. Each entry records:

- released product ID, version, hash, and consuming decision situations;
- semantic domain and permitted typed projection;
- authoritative source object and version;
- producer, route, recipient, visibility, and scope;
- event/as-of/effective and delivery time;
- freshness, missing, stale, disputed, corrected, and unavailable behavior;
- uncertainty and provenance; and
- whether the field is initial, delivered, private, or derived.

An observation is admitted only when the Definition permits it, the Scenario
can produce it, the event-time/evidence rule permits it, and V1 can carry a
frozen typed projection. Failure produces the released missing/unknown
behavior, never a hidden default.

### 6.2 RuntimeField projection

A materially complete projection uses one value plus explicit companions:

```text
obs.<capability>.<id>.value
obs.<capability>.<id>.authoritative_record_ref
obs.<capability>.<id>.record_version
obs.<capability>.<id>.event_time
obs.<capability>.<id>.as_of
obs.<capability>.<id>.effective_interval
obs.<capability>.<id>.delivery_time
obs.<capability>.<id>.freshness
obs.<capability>.<id>.availability
obs.<capability>.<id>.scope_ids
obs.<capability>.<id>.uncertainty_or_dispute
```

V1 supplies typed value, provenance, visibility, scopes, consumers, and review
state. A DecisionRecord cites the exact frozen observation record. A reference
cannot be used to dereference current hidden WorldState.

### 6.3 Compound and corrected records

Technical accounts, meeting records, executive briefs, classification bases,
scope updates, and outreach plans use:

1. one stable business-object/version reference;
2. separate atomic RuntimeFields for every behaviorally material component;
3. common source, time, delivery, and scope linkage; and
4. version-coherence validation.

A correction creates and routes a new version. It does not mutate a prior
delivery or a decision that consumed the prior version.

## 7. Private decision-state mapping

All 44 private-state placements use capability-scoped reducer paths:

```text
actor.<runtime_actor_id>.capability.<capability_id>.private.<state_id>
```

They are initialized from the released product and updated only by a declared
decision, admitted intent, or delivered observation/lifecycle notice permitted
by that product. Each transition records before/after values, state versions,
causal parents, and the consuming later decisions.

Assessments, open questions, last-consumed/shared records, and active intent
references never become a competing copy of technical, institutional,
category, report, notification, delivery, or result truth. Pending-reference
state distinguishes never issued, pending, acknowledged, partial, failed,
expired, cancelled, superseded, and completed work. Backend-local persistent
memory is not an admissible carrier.

## 8. Intent and parameter mapping

### 8.1 Complete registry

The intent registry must contain exactly 54 capability-qualified placements
and no additional action. Every entry records:

- machine action type and schema version;
- released product/hash and consuming decision situation;
- required observations and private-state versions;
- target, capacity, authority, relationship, access, object/prestate,
  resource, time, and expiry requirements;
- flat typed parameters with required/optional status;
- lifecycle owner, admissible source states, and idempotency scope;
- whether an admitted action may materialize messages; and
- permitted disposition, result, delta, and later-observation families.

No mapping may manufacture an intent from prose that is absent from the
release.

### 8.2 Canonical V1 carrier precedence

| Semantic item | Canonical V1 carrier |
|---|---|
| acting actor | `ActionIntent.actor_id` |
| real target actors or processes | `target_entity_ids` |
| claimed scoped authority | `claimed_authority_refs` |
| owned resource request or offer | `resource_offer_or_request` |
| earliest effect and expiry | `earliest_effect_time`, `expiry_time` |
| business object/version, capacity, route, reason, scope, uncertainty, and stable record refs | flat typed `parameters` |
| actually consumed observations | `observation_refs` |
| responsible decision | `decision_ref` |
| duplicate identity | `idempotency_key` |

One property has one authoritative carrier. Duplicate amount, target,
authority, capacity, expiry, or version values that disagree fail closed.

### 8.3 Parameter and intent families

| Family | Required semantic separation |
|---|---|
| inspect/verify/request | request, access, assignment, execution, returned evidence, failure/expiry, and interpretation |
| communicate/escalate/report | issue, transport, delivery, acknowledgement, institutional acceptance, further routing, and response |
| coordinate/convene/activate | request, authority, invitation, attendance/staffing, presented content, decision, assignment, and result |
| classify/direct/assign | participant proposal/direction, authoritative institutional transition, recipient action, and completed result |
| control/contain | target/prestate, authority, feasibility, execution, partial/no/adverse effect, recurrence, and observation |
| prepare/notify | preparation, proposal, consultation, authorization, issue, fanout delivery, correction, and recipient result |
| lifecycle clarification | a status request, delivered status, and actual underlying result remain distinct |

Parameters are scalar or flat-array V1 values plus stable object/version
references. Lists of compound objects use referenced records and checked
atomic fields rather than an unversioned nested payload.

## 9. Message mapping

1. A communicative released intent first creates an ActionIntent.
2. Only a permitting ActionDisposition may materialize correlated
   MessageIntents.
3. Message content is an exact projection of admitted parameters and cannot
   introduce a new source, claim, target, capacity, or authority.
4. Multi-recipient communication creates one correlated message and delivery
   history per recipient.
5. Issue, route admission, transport, delivery, receipt, acknowledgement,
   institutional acceptance, and business result remain separate.
6. Internal assessment, proposal, or preparation creates no message unless the
   released intent explicitly communicates it.
7. Correction and supersession cite the prior message/product version; neither
   erases the earlier recipient history.

## 10. Business lifecycle mapping

### 10.1 Canonical object state

Each request, finding, message, meeting, investigation, control, response-team
activation, category, report, direction, assignment, outreach plan,
notification, attack attempt, and result has:

- stable event-scoped object ID and kind;
- state/version, predecessor, correction, and supersession references;
- owner, issuer/producer, target/recipient, institution/capacity, and related
  objects;
- issue, event, effective, expiry, and delivery times;
- authority, relation, access, resource/capacity, and source references;
- lifecycle state, idempotency/correlation key, and disposition; and
- result, StateDelta, later-observation, and causal-parent references.

The lifecycle families and owners are those closed in the Scenario interface
record. A duplicate returns or rejects against the prior disposition. New
evidence, changed scope, expiry, failure, cancellation, or supersession may
create a new lineage-linked intent.

### 10.2 Cross-hop lineage

A forwarded finding, account, report, or direction creates a new hop. It
preserves the source object/version without changing the original issuer,
recipient, content, or prior delivery:

```text
technical source/result
  -> delivered finding
    -> technical/security/operational decision and intent
      -> qualified account or escalation
        -> GCIO or senior-office delivery and decision
          -> category/report/direction
            -> institutional delivery or execution result
              -> later status observation and private-state update
```

Every hop has its own decision, intent, message, disposition, delivery,
acknowledgement, result, delta, and version identities as applicable.

## 11. Result mapping

| Layer | Required record |
|---|---|
| semantic admission | accepted/rejected ActionDisposition with reason and checked versions |
| communication | route/transport/delivery disposition per recipient |
| institutional processing | accepted, pending, partial, declined, failed, expired, cancelled, or superseded process state |
| technical execution | blocked, failed, delayed, partial, effective, no-effect, adverse, reversed, or recurrent result |
| authoritative effect | reducer-owned StateDelta with invariant and causal parents |
| participant feedback | separately produced, routed, delivered, and frozen observation |

An admitted intent is never proof of execution, effect, delivery,
acknowledgement, institutional acceptance, containment, reporting, or
notification.

## 12. Authority, relationships, and resources

### 12.1 Authority and relationships

- authority is scoped by actor/unit, office/capacity, action/message, target,
  object, institution, and effective interval;
- unknown or ambiguous authority grants nothing;
- IHiS operation and SingHealth ownership remain separate institutional facts;
- host, employment, accountability, or concurrent appointment does not imply
  transitive access, knowledge, delivery, or command;
- GCIO IHiS and SingHealth routes have separate recipient and delivery state;
- MOH, MCI, and CSA remain distinct routes and institutional processes; and
- meeting attendance conveys only material presented or subsequently
  delivered.

### 12.2 Resources

The event requires canonical qualitative or bounded resources for system/data
access, credential/session control, investigation/response capacity,
meeting/communication capacity, reporting/notification routes, and outreach
readiness. A request, assignment, coordination instruction, or proposal does
not create capacity or completed work. Reservations, conflicts, execution,
release, and effects are reducer-owned and versioned.

## 13. Scenario semantic requirements

The Scenario must supply, without redefining participant behavior:

1. canonical institution, office/unit, capacity, assignment, access, system,
   database, and route identities;
2. bounded attack inputs and access/query/copying/disclosure mechanics;
3. source-preserving products, production, routing, delivery, meeting,
   correction, freshness, and dispute;
4. the lifecycle families fixed in the semantic inventory and interface
   closure;
5. authority, relationship, target, prestate, access, capacity, concurrency,
   expiry, duplicate, and feasibility adjudication;
6. typed dispositions, results, deltas, later observations, and causal trace;
7. system-only structural variants and exogenous inputs; and
8. normal/incomplete termination, pending-object treatment, invariant failure,
   trace closure, and reproducibility identity.

These are event semantics carried and hashed by V1, not generic Agent behavior
or a new exchange contract.

## 14. Cross-object conformance rules

### Release and identity

1. The exact release manifest and every source product hash must resolve.
2. The derived catalog must contain 9 products, 29 decision situations, 62
   observation placements, 44 private-state placements, and 54 intent
   placements, with no extra semantic item.
3. Every actor/unit/capability and machine placement ID must be injective and
   event-qualified.
4. Every office/unit must resolve to one host relation, authority/capacity
   record, and released product.
5. Canonical institution, system, resource, relationship, and result state may
   not be duplicated by actor assembly.

### Information and private state

6. Every observation resolves to a permitted source/version, producer, route,
   recipient, event/as-of/delivery time, freshness rule, and consumer.
7. No projection reads hidden live or future state through a reference.
8. Missing, stale, disputed, corrected, and undelivered values remain explicit.
9. Every private-state transition is released, reducer-versioned,
   capability-scoped, and causally linked.
10. Active-intent references distinguish pending and unsuccessful work from
    never-issued work.

### Intent, lifecycle, authority, and result

11. Every ActionIntent resolves to one released intent row and responsible
    DecisionRecord.
12. Target, capacity, authority, relation, access, object/prestate, resources,
    time, expiry, and idempotency are checked before execution.
13. Message materialization cannot add meaning absent from the admitted action.
14. Issue, delivery, acknowledgement, institutional acceptance, execution,
    result, delta, and observation remain distinct.
15. Only the reducer changes authoritative state; actors retain references and
    assessments only.
16. Partial, failed, expired, cancelled, superseded, no-effect, and adverse
    outcomes remain in the deterministic trace.
17. A correction versions only the propositions it addresses and never rewrites
    an earlier decision basis.
18. Cross-hop forwarding preserves source and recipient histories with exact
    correlation and causal references.

### Configuration and run boundary

19. Population units, assignments, capacities, structural variants, exact
    times, qualitative initial state, enabled lineage, and policies remain
    separately pinned configuration choices.
20. System-only configuration cannot enter participant knowledge without an
    eligible delivered observation.
21. Any later runtime bundle pins release, Scenario, mapping, configuration,
    assembly, policy, Contract, exogenous-input, code, time, and RNG identity.
22. Any unresolved required identity, hash, semantic placement, authority,
    version, route, or lifecycle rule fails closed.

## 15. Specification closure

The specification gives all nine released products one coherent identity,
information, private-state, intent, message, lifecycle, authority, resource,
result, and trace model. It finds no missing autonomous participant and no
concrete Contracts V1 loss.

The project owner accepted:

- `OD-CM-05`: canonical institution plus office/unit sub-entity identity;
- `OD-CM-06`: capability-qualified full-placement mapping and private-state
  model;
- `OD-CM-07`: retain Contracts V1 with an event-qualified internal profile and
  Scenario semantics; and
- `OD-CM-08`: if later authorized, implement only a fail-closed release loader
  and one bounded cross-hop lineage before broader participant policies.

These decisions authorize design promotion only. They do not authorize
configuration, binding, policy implementation, runtime,
simulation, calibration, evaluation, or validity claims.
