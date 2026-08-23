# H2EPR-0288 consolidated mapping specification v0.1

> `ACCEPTED_DESIGN_SPECIFICATION / NON_EXECUTABLE / NO_IMPLEMENTATION_AUTHORITY`

## 1. Accepted decision

This specification maps all semantics released in
`H2EPR-0288-ROSTER-DEFINITION-RELEASE-v0.1` into one H2EPR runtime model. It
does not amend a Definition, add a role, choose a Rule policy or authorize a
run.

The specification uses four distinct layers:

```text
historical/legal entity
  -> runtime actor and ParticipantArtifact
    -> one or more released capabilities
      -> capability-scoped observations, state and intents
```

The principal decision is:

> A released Agent Definition or population model is a capability authority,
> not automatically a separate runtime actor. One historical/legal entity has
> one canonical actor interface, one authority graph and one resource owner.

This permits the full Roster to use V1 without duplicating institutions or
collapsing distinct institutional processes.

## 2. Specification identity

| Item | Accepted value |
|---|---|
| mapping specification ID | `H2EPR-0288-CONSOLIDATED-MAPPING-v0.1` |
| mapping profile family | `h2epr.roster-consolidated-mapping.v0_1` |
| source release | `H2EPR-0288-ROSTER-DEFINITION-RELEASE-v0.1` |
| release commit | `e0cb20724db7c8f15cf344a161ab2f2b2721c1f0` |
| release manifest SHA-256 | `d14bca5ef4486031d2c87ba3f20a2a2fe5fb3221f5c6a305c95a02dc585ea0b1` |
| event semantic skeleton | `H2EPR-0288 event semantic skeleton`, version `0.1` |
| carrier target | H2EPR Contracts V1 |
| current status | accepted design specification; no executable binding |

This specification is hash-pinned by its release manifest. A later authorized
run must pin the mapping hash through `config_sha256`, pin the assembled
semantic state through `runtime_bundle_sha256`, record each ParticipantArtifact hash,
and identifies release, mapping and scenario component versions in the V1
RunManifest.

## 3. Identity model

### 3.1 Stable identities

| Identity | Required meaning | Owner |
|---|---|---|
| `entity_id` | one historical/legal person, institution, association, committee, population unit or scenario process | entity registry/scenario |
| `runtime_actor_id` | one endogenous decision interface and ParticipantArtifact | actor assembly |
| `unit_id` | one scenario-declared population choice unit, host/institution and weight | population assembly |
| `capability_id` | one released Definition or population-model behavior surface | mapping capability catalog |
| `definition_ref` | released semantic product ID, version, path and SHA-256 | release manifest |
| `machine_commitment_id` | capability-qualified reference to one released Decision/Population Commitment | derived commitment catalog |
| `business_object_id` | request, case, proposal, offer, loan, obligation, message, commitment, result or relationship | scenario/reducer lifecycle registry |
| `observation_key` | `(capability_id, reader_observation_id)` | observation catalog |
| `intent_key` | `(capability_id, reader_intent_id)` | intent registry |
| `machine_action_type` | unique V1 `ActionIntent.action_type` | derived intent registry |

### 3.2 Machine action identity

For each of the 107 released intent placements:

```text
reader_intent_id = <released label, unchanged>
intent_key       = (<capability_id>, <reader_intent_id>)
machine_action_type
  = h2epr.action.0288.<capability_id>.<reader_intent_id>
```

Example:

```text
h2epr.action.0288.new_york_clearing_house.request_case_information
h2epr.action.0288.j_pierpont_morgan.request_case_information
h2epr.action.0288.trust_presidents_committee.request_case_information
```

The three reader-facing names remain readable and traceable to their
Definitions, while the V1 action registry receives three unambiguous machine
types. The same rule applies to every repeated observation and intent label.

The action schema version is capability- and intent-specific:

```text
h2epr.intent.0288.<capability_id>.<reader_intent_id>.v0_1
```

This is an internal mapping-profile successor, not a Contracts successor.

Released commitments use the parallel identity rule:

```text
h2epr.commitment.0288.<capability_id>.<released_commitment_id>
```

These stable IDs populate the semantic basis of `DecisionRecord.rule_ids`.
They identify the Definition commitment being applied; they are not Rule v2
code or a claim that an implementation policy has already been approved.

## 4. Actor assembly

### 4.1 Assembly rules

1. The scenario declares the actor assembly; file-name matching or historical
   name similarity may not create an actor.
2. Every endogenous actor resolves to exactly one `entity_id` and one
   ParticipantArtifact.
3. One actor may contain several capabilities. Its action space is the union
   of their capability-qualified machine action types.
4. A capability cannot create a second balance sheet, authority record,
   relationship or private observation envelope for the same entity.
5. A named Agent Definition takes precedence for the actor's V1
   `representation_class`; a population-derived capability composes into that
   actor rather than replacing it.
6. A standalone unit instantiated only from a population model uses
   `aggregate_population_agent` and retains unit, host/institution, profile and
   weight identity.
7. Two choice units may share a population profile but never share private
   state, authority, resources, observation scope or lifecycle records.
8. Splitting one released institutional interface into internal sub-actors is
   outside this release and fails closed.

### 4.2 Representation projection

| Runtime object | V1 projection |
|---|---|
| named endogenous institution, Morgan or committee | `autonomous_participant_agent` |
| standalone population choice unit/cohort | `aggregate_population_agent` |
| scenario-owned venue or institutional mechanic, if materialized as an environment participant | `institutional_environment_agent` |

`autonomous_participant_agent` denotes endogenous choice; it does not assert
that an institution is a natural person. The Definition's representation and
governance limits remain in the ParticipantArtifact profile and constraints.

### 4.3 Required assembly patterns

| Pattern | Required result |
|---|---|
| Knickerbocker, NYCH, NBC, Morgan, TCA, Lincoln and the presidents committee | one named actor for each accepted decision interface |
| depositor populations | host-scoped weighted units; no cross-host depositor actor or wallet |
| member/correspondent bank resource decisions | one weight-one unit per included institution unless explicit aggregation and information loss are declared |
| call-money lender population | one institution-preserving lender unit per included lender |
| broker-borrower population | one institution-preserving borrowing unit per included broker/borrower interface |
| institution assigned both bank-resource and lender capabilities | one actor with both capabilities and one resource/exposure owner |
| named actor also assigned a population capability | capability is composed into the named actor; no second ParticipantArtifact |

The release does not specify the final number of population units. That number,
their weights and capability composition are scenario configuration and must be
run-pinned.

## 5. ParticipantArtifact projection

Every actor artifact carries the following namespaced semantic projections:

| V1 field | Consolidated projection |
|---|---|
| `runtime_actor_id` | actor assembly ID |
| `source_participant_ids` | historical entity/unit plus every composed release product ID |
| `representation_class` | rule in §4.2 |
| `participant_profile` | entity, unit/weight, host, capability list, Definition IDs/versions/hashes and representation limits |
| `behavior_profile` | commitment IDs, hard obligations, behavioral hypotheses, scenario-conditional commitments and private-state declarations per capability |
| `skill_set` | only formally released future Skill references; none inferred by this mapping |
| `goal_set` | reviewed role priorities projected from the Definition without adding utility weights |
| `constraint_set` | forbidden information, authority, resource, aggregation and intent/result boundaries |
| `information_boundary` | capability-scoped observation catalog and visibility/freshness rules |
| `action_space_refs` | exact union of capability-qualified machine action types |
| `communication_policy_ref` | scenario communication policy and allowed route/performative classes |
| `initial_resource_state` | checked projection of the entity's canonical initial resources, not a second resource authority |
| `rule_policy_ref` | deliberately unassigned by this non-executable specification; a later valid ParticipantArtifact must bind a stable, versioned and reviewed policy reference |

No V1 ParticipantArtifact is generated by this specification because the required
policy reference has not been authorized. Once implementation is separately
authorized, the artifact hash changes if its capability composition, source Definition
hash, information boundary, action space, initial resource projection or
structural configuration changes.

## 6. Observation mapping

### 6.1 Catalog and actor envelope

Each of the 115 released observation placements becomes one catalog entry
keyed by `(capability_id, observation_id)`. A catalog entry contains:

- Definition ID, version, content hash and consuming commitment IDs;
- semantic domain and allowed value representation;
- authoritative source object/state family;
- visibility and permitted actor/unit scopes;
- participant-available event-time rule;
- freshness, missing, stale, disputed and unavailable behavior;
- required provenance and authoritative record/version references; and
- whether the value is initial, delivered, private or derived.

An actor with several capabilities receives the union of their catalog entries
under namespaced field names:

```text
obs.<capability_id>.<observation_id>
```

Identical reader labels are not automatically merged. Two entries may project
the same authoritative source record only when their domain, time and scope
checks agree.

### 6.2 Canonical RuntimeField family

An observation is carried as a value plus explicit companions where materially
required:

```text
obs.<capability>.<id>.value
obs.<capability>.<id>.authoritative_record_ref
obs.<capability>.<id>.record_version
obs.<capability>.<id>.as_of
obs.<capability>.<id>.effective_interval
obs.<capability>.<id>.freshness
obs.<capability>.<id>.availability
obs.<capability>.<id>.scope_ids
obs.<capability>.<id>.uncertainty_or_dispute
```

V1 `RuntimeValue` supplies provenance, availability-at-t0, visibility,
visibility scopes, consumers and review state. The observation record ID used
by a DecisionRecord and ActionIntent identifies the frozen projection actually
seen by the actor.

### 6.3 Compound records

Compound concepts such as NBC exposure, an assistance dossier, a call-loan
offer or a coordination proposal are not stored as an opaque nested object in
one field. They use:

1. a stable business-object and version reference;
2. separate atomic RuntimeFields for every behaviorally material component;
3. common provenance, event-time and scope linkage; and
4. a validator that rejects missing, contradictory or cross-version
   components.

A stable reference cannot authorize the backend to dereference current hidden
WorldState. The actor receives only the explicitly frozen projection.

### 6.4 Observation admission

An observation is legal only if all four gates pass:

```text
Definition permits it
AND scenario can produce it
AND evidence/time policy permits it at the decision time
AND V1 mapping can carry its frozen typed projection
```

Failure at any gate produces the released missing/stale/unknown behavior; it
does not produce a hidden default.

## 7. Private decision-state mapping

### 7.1 Authoritative replay paths

Every behaviorally material actor-private state has one of two authoritative,
replayable carriers.

State that is explicitly transitioned by an admitted action or must be checked
atomically with current world/process state uses a reducer-owned V1 state path:

```text
actor.<runtime_actor_id>.capability.<capability_id>.private.<state_id>
```

It appears in `WorldState.process_states` as `runtime_private`, scoped to the
actor, and is updated only by a StateDelta with before/after value, state
versions, invariant checks and causal parents.

A consumption cursor or bounded abstention posture that is completely defined
by the ordered DecisionRecord, its observation refs, commitment IDs, structured
reason codes and named revisit observation is instead a deterministic
trace-derived private view. It is projected into the next legal observation;
it does not require an invented Agent intent merely to record that a decision
occurred.

An abstention therefore remains a DecisionRecord with no action/message intent,
a scoped blocker and revisit condition. It may advance only trace-derived
decision state. It cannot change business truth, resources or a mutable
world/process path.

A backend may hold transient reasoning during one decision but may not retain
behavior-changing memory outside these two authoritative paths.

### 7.2 Ownership split

| State kind | Canonical owner |
|---|---|
| posture or assessment explicitly transitioned by an admitted action | actor-private reducer path |
| last-consumed record versions and no-intent abstention posture completely derivable from DecisionRecords | sealed trace-derived private view |
| request, case, review, authorization, offer, message, relationship, loan and result truth | scenario/reducer business-process path |
| resources, exposure, collateral control, claim and settlement balance | V1 resource/world-state path |

Actor-private state stores references and assessments, not a second copy of
business truth. A reducer update caused by a delivered result points to that
result/version as a causal parent. A trace-derived view cites the exact prior
DecisionRecord and observations from which it is reconstructed.

## 8. Intent and parameter mapping

### 8.1 Complete coverage rule

The intent registry is generated from every released intent row. A registry is
valid only when it contains exactly 107 `(capability_id, reader_intent_id)`
placements and no extra action. Each entry records:

- machine action type and schema version;
- Definition/hash and consuming commitment IDs;
- allowed representation classes;
- required observations and private-state versions;
- target, authority, resource, time and business-object requirements;
- parameter names, scalar/flat-array types, domains and required/optional
  status;
- lifecycle owner and permitted source states;
- whether an admitted action may materialize one or more MessageIntents;
- idempotency scope, expiry and duplicate rule;
- permitted disposition and result families; and
- cross-object validators.

No intent can be synthesized from an action verb that is absent from the
release.

### 8.2 Canonical V1 carrier precedence

| Semantic item | Canonical V1 carrier |
|---|---|
| acting participant | `ActionIntent.actor_id` |
| real target participants | `target_entity_ids` |
| scoped authority records | `claimed_authority_refs` |
| offered/requested owned resource | `resource_offer_or_request` |
| earliest effect and expiry | `earliest_effect_time`, `expiry_time` |
| business-object IDs, versions, classifications, reasons, terms, scopes and stable record refs | flat typed `parameters` |
| actually consumed observations | `observation_refs` |
| responsible decision | `decision_ref` |
| duplicate identity | `idempotency_key` |

A semantic property has one canonical carrier. Duplicating the same amount,
authority, target or expiry in both a top-level field and `parameters` is an
error. A checked descriptive projection may appear in a profile or trace view,
but it is not a second authority.

### 8.3 Parameter families

The released intent content reduces to the following versioned parameter
families. Each intent selects the necessary members; it does not receive every
field.

| Family | Canonical members |
|---|---|
| business identity | `case_id`, `request_id`, `proposal_id`, `offer_id`, `application_id`, `loan_id`, `obligation_id`, `relationship_id`, `statement_id`, `message_ref`, `result_ref`, object version |
| represented parties | represented entity, sender, recipient, counterparty, host, forum, facility, route and resource-owner IDs |
| classification | route, eligibility, matter/case type, posture, response class, reason code and uncertainty/dispute status |
| information | requested information class IDs, record refs, `as_of`, freshness requirement, scope and purpose |
| authority | claimed authority top-level plus requested/competent forum, scope and authorization question parameters |
| proposal and terms | proposal/offer version, conditions, term fields, amount method, collateral refs, requested roles and unresolved items |
| resource | canonical top-level resource carrier plus resource type, owner/control refs, unit, valuation/as-of and condition refs |
| time | earliest effect, expiry, deadline, effective interval and revisit-event ref |
| communication | audience/recipient, performative, claim/scope, route/channel, correction/supersession ref and uncertainty |
| lifecycle | current object state/version, predecessor, superseded object, correlation and requested transition |

Free-form nested dictionaries, silent backend defaults and unversioned enum
extensions are not allowed. A list of compound objects is represented by stable
object IDs plus separately validated records.

### 8.4 Intent-family projection

| Released intent family | Required carrier behavior |
|---|---|
| verify, classify and assess | references the exact observed records; emits a proposed classification/posture transition, never hidden truth |
| request information or examination | target, object, information classes, scope, authority, deadline/expiry and correlation are explicit |
| seek authority | competent forum, scoped question, object/proposal and current authority record are explicit; result remains external |
| create or revise request/proposal/offer | one stable object/version, target, conditions, authority, resource and expiry; revision links predecessor |
| communicate, issue notice or statement | admitted action precedes message materialization; claim, authority, audience, route and `as_of` are explicit |
| accept, decline, refer or withdraw | typed scope/reason and exact object/version; a scoped decline cannot imply universal impossibility |
| commit or authorize controlled resource | actor/resource owner/control and amount/term/collateral are validated before disposition |
| wait, retain or continue | explicit pending object plus deadline/revisit event; never an unbounded default no-op |
| close, reopen, revise or cancel | terminal/supersession rule and causal new event are explicit; prior record remains in trace |

This family mapping covers all intent lists in `semantic-inventory.md`; exact
required semantic content remains the released intent row, not a new generic
policy.

## 9. Message mapping

1. An externally communicative released intent first produces an ActionIntent.
2. Only an ActionDisposition that permits communication materialization can
   create the correlated MessageIntent.
3. `MessageIntent.structured_content` is an exact projection of admitted
   action parameters and may not introduce a new claim, target or authority.
4. V1 permits one recipient per MessageIntent. A scenario fanout plan creates
   one correlated message per recipient and preserves the parent action.
5. Message creation, route admission, transport, delivery, receipt and business
   response use distinct IDs and records.
6. An internal classification, posture or preparation action creates no
   MessageIntent.
7. Failed, prohibited, delayed, expired and duplicate attempts remain visible;
   an adapter may not silently repair them.

## 10. Business lifecycle mapping

### 10.1 Canonical object state

Each lifecycle object has:

```text
object_id
object_type and schema version
owner/controller IDs
party and correlation IDs
current state and state version
created/effective/expiry times
predecessor/supersession refs
authority and resource refs where applicable
terminal flag and terminal reason
causal parent IDs
```

These are carried as stable references and flat RuntimeFields in
`WorldState.process_states`, `relations`, `commitments` or resources as
appropriate. State changes are reducer-owned StateDeltas.

### 10.2 Lifecycle families and owners

| Family | Primary authoritative owner | Required cross-links |
|---|---|---|
| governance/authority | relevant institution/scenario governance process | actor, scope, forum, proposal/case, predecessor |
| information/examination | producer/examiner plus scenario delivery process | request, scope, report, provenance, delivery, case |
| request/case review | recipient institutional process | requester, intermediaries, route, authority, review, disposition |
| proposal/plan | proposing coordination process | version, recipients, solicitations, replies, authority, expiry |
| solicitation/reply | each recipient's independent decision process | proposal, recipient, reply, resource owner, expiry |
| resource commitment/execution | resource owner and reducer | offer, reservation, commitment, transfer/result, release |
| credit and clearing relationship | relevant institutions plus scenario ledger | exposure, relationship, notice, effective interval, result |
| institutional communication | issuing authority plus transport | statement/version, recipient, message, delivery, correction |
| withdrawal/service/payment | depositor unit and host service/reducer | claim, request, queue/service, payment/result, remaining claim |
| facility/collateral | applicant, facility authority and reducer | application, collateral owner/control, review, issue/result |
| call-loan contract | lender, borrower and reducer | loan, term/call, notice, repayment/default, collateral |
| replacement funding | borrower, candidate lender and venue/reducer | request, offer, acceptance, match, booking, transfer, repayment |
| position reduction/venue | authorized borrower and scenario-owned NYSE process | authorization, request/order, match/trade, settlement/result |

### 10.3 Cross-hop lineage

The Knickerbocker → NBC → NYCH route requires distinct objects and events:

```text
KT request and authorization
  -> KT-to-NBC message and delivery
    -> NBC role classification
      -> NBC forward/sponsor/decline intent
        -> NBC-to-NYCH message and delivery
          -> NYCH case and disposition
            -> communicated disposition
              -> later delivered business/resource result
```

No hop inherits delivery, authorization or acceptance from the preceding hop.
NBC may be a courier, sponsor, representative, joint participant, unresolved
intermediary or decliner only as its released Definition permits.

## 11. Result mapping

| Layer | V1 or scenario carrier | Meaning |
|---|---|---|
| action admission | ActionDisposition | `accepted`, `rejected`, `partial`, `delayed`, `superseded` or `failed` for one intent |
| communication route | CommunicationDisposition | route admission, delay, prohibition, duplicate, expiry or failure |
| delivery | communication/delivery record | whether a message reached a recipient at a time |
| business disposition | authoritative process-state record | case, request, proposal, offer, application or obligation response |
| execution/result | result record plus StateDeltas | realized, partial, delayed, no-effect, failed, withdrawn or other typed outcome |
| later Agent knowledge | delivered result observation | only the result version actually delivered to that actor |

Business-specific states such as `unavailable`, `cancelled`, `paid`, `booked`,
`called`, `closed` or `facility_declined` are process states/reason codes; they
do not expand transport-status enums. `accepted` never proves that resources
were transferred, a message was delivered or a historical objective was met.

## 12. Authority and resource mapping

### 12.1 Authority

Authority is a versioned, scoped record. A valid action must establish:

- who or what granted the authority;
- which actor, object, route, resource and intent class it covers;
- effective and expiry time;
- current state (`authorized`, `pending`, `denied`, `disputed`, `unknown` or a
  more specific scenario-defined value); and
- the authoritative record/version reference.

An actor's identity, officer title, committee membership or relationship never
substitutes for a missing scoped authority record.

### 12.2 Resources

Resources use one canonical V1 ResourceState owner. A proposed resource action
must bind:

- resource and owner/controller identity;
- requested/offered amount or disclosed qualitative envelope;
- unit, valuation/as-of and uncertainty where material;
- collateral/condition and commitment references;
- current resource state version; and
- authority to offer, reserve, commit, transfer, repay or release it.

NYCH, the presidents committee and Morgan may coordinate independent
commitments; they do not acquire ownership of member, contributor or firm
resources. Partial, failed and released commitments update only the canonical
resource and lifecycle records through the reducer.

## 13. Scenario semantic extensions required

The specification requires scenario-side semantic design, not a V1 contract
change, for:

1. actor assembly and population-unit composition;
2. capability-scoped observation production and information-time filters;
3. the reusable business-object and lifecycle registry;
4. authority, relationship, resource-control and collateral rules;
5. request, review, proposal, commitment, notice and result adjudication;
6. withdrawal service, payment form and host-account effects;
7. NYSE venue, route, matching, call-money, collateral, trade and settlement
   mechanics;
8. exogenous Treasury deposits and initial affiliated-bank history;
9. structural variant configuration and run identity; and
10. the two-hop KT–NBC–NYCH lineage.

The structural variant set is immutable during a run and included in the
scenario config and runtime-bundle hashes. At minimum it records the selected
NYCH route interpretation, NBC termination provenance and every enabled
committee/resource-pool or venue policy. A participant never receives a
variant label; it receives only admissible observations produced under it.

## 14. Cross-object conformance rules

### Release and definition integrity

- `C01` — release ID, commit, manifest hash and every product hash match the
  accepted release.
- `C02` — every capability references exactly one released product and every
  released product has a mapping disposition.
- `C03` — the mapping contains exactly the released commitment, observation
  and intent placements; no behavior is added or omitted.

### Identity and assembly

- `C04` — every actor, unit, capability and entity ID is unique in its
  namespace and resolves.
- `C05` — one endogenous actor has exactly one ParticipantArtifact.
- `C06` — capabilities assigned to the same entity share one authority graph,
  resource owner and relationship state.
- `C07` — every population unit records profile, host/institution and weight;
  private state and resources are unit-scoped.
- `C08` — aggregate weight is used only for outcome aggregation, never to
  multiply an unvalidated individual resource or action.

### Observation and information boundary

- `C09` — the actor envelope equals the union of its capability catalogs and
  contains no unregistered observation.
- `C10` — each observation has provenance, event time/as-of, freshness,
  visibility, actor scope and authoritative record/version where required.
- `C11` — an observation cannot reference a future, undelivered, hidden or
  held-out value.
- `C12` — compound records are version-coherent and contain every material
  component; live hidden-state dereference is forbidden.
- `C13` — missing, stale, disputed and unknown values follow the released
  fallback/abstention rule; no backend default fills them.

### Private state and lifecycle

- `C14` — every behavior-changing persistent state is declared and has exactly
  one authoritative replay path: reducer state or a deterministic
  DecisionRecord-derived private view.
- `C15` — actor-private state updates or derivations cite the DecisionRecord
  and delivered authoritative inputs/results that caused them; a no-intent
  DecisionRecord cannot mutate world/process state.
- `C16` — business truth has one owner; actor memory may store only a reference,
  version and declared assessment.
- `C17` — lifecycle transitions are valid for the object type/current version,
  preserve predecessor/supersession lineage and cannot skip required authority
  or delivery stages.
- `C18` — one business-equivalent object cannot be recreated while an
  unresolved object exists unless the release explicitly permits a versioned
  replacement.

### Intent, message and authority

- `C19` — every ActionIntent type resolves to exactly one capability-qualified
  registry entry and belongs to the actor's action space.
- `C20` — required observations, state versions, targets, authority, resource,
  time and object parameters are present and type-valid.
- `C21` — a semantic item occupies one canonical carrier; conflicting duplicate
  projections fail closed.
- `C22` — authority record scope, actor, target, object, resource and time cover
  the proposed action.
- `C23` — idempotency scope includes actor, machine action type, business
  object/version, target and material parameters.
- `C24` — a MessageIntent is materialized only from a permitted admitted action,
  carries no new semantics and retains action correlation.
- `C25` — fanout creates one message per recipient; issue, delivery and response
  are not inferred from one another.

### Resource, result and trace

- `C26` — offered, committed or repaid resources resolve to the canonical
  owner/control record and prestate version.
- `C27` — only the authoritative reducer emits StateDeltas and increments state
  versions; every delta cites a disposition and causal parents.
- `C28` — ActionDisposition, CommunicationDisposition, business disposition,
  execution result and delivered observation remain distinct.
- `C29` — partial, delayed, failed, no-effect, withdrawn and superseded paths
  preserve attempted parameters and reasons in the trace.
- `C30` — DecisionRecord, observations, intents, messages, dispositions,
  deliveries, lifecycles and deltas form a closed causal chain.

### Run identity

- `C31` — runtime bundle and config hashes cover actor assembly, population
  units/weights, capability composition, mapping profile, scenario variants,
  initial state, routes and lifecycle policies.
- `C32` — ParticipantArtifact hashes cover source Definition hashes,
  observations, state, constraints and action-space projections.
- `C33` — release, mapping, scenario, contract and component versions are
  recoverable from the RunManifest and hashed inputs.
- `C34` — Rule, future LLM and any other backend receive the same frozen
  external semantic envelope; backend-specific hidden information or actions
  are forbidden.

## 15. Specification closure

This mapping covers:

- all 12 released semantic products;
- all 115 observation placements;
- all declared behaviorally material private state;
- all 107 intent placements and their message/result boundaries;
- the full set of shared lifecycle, identity, authority and resource families;
  and
- scenario-owned processes and structural variants.

It requires a consolidated internal mapping profile and scenario semantic
extensions. It does not expose a concrete V1 carrier failure and therefore
does not propose a Contracts successor. That carrier conclusion is audited
separately in `v1-carrier-review.md`.
