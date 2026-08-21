# H2EPR-0288 consolidated mapping substantive review

> `ACCEPTED_SUBSTANTIVE_REVIEW / NON_EXECUTABLE`

## 1. Review conclusion

```text
recommendation=ACCEPTED_BY_OWNER
owner_resolution_date=2026-08-22
owner_decisions=OD-CM-01,OD-CM-02,OD-CM-03,OD-CM-04
blocking_findings=0
unresolved_contract_counterexamples=0
implementation_conditions=6
scientific_validity_claim=NONE
```

The reviewed candidate was sufficiently complete and internally coherent for
owner acceptance and atomic formal promotion. It is now an accepted design
specification and must not be treated as an executable binding. This review
was performed by the current Supervisor; it is a substantive adversarial
review, not an independent external replication.

## 2. Review scope and tests

The review challenged the candidate on:

1. fixed-release coverage and absence of new behavior;
2. entity, actor, unit and capability identity;
3. observation loss, participant-time and hidden-state leakage;
4. private-state authority and no-intent decisions;
5. intent, message, lifecycle and result separation;
6. governance, authority and resource ownership;
7. population composition and aggregation loss;
8. V1 schema capacity versus current mapping-code limitations;
9. cross-object causal closure and deterministic replay; and
10. scope discipline and successor minimality.

Identifier checks against the fixed release produced:

| Check | Result |
|---|---|
| released intent placements | 107 |
| capability-qualified machine action types | 107 unique |
| longest proposed machine action type | 85 characters; V1 StableId limit is 128 |
| released observation placements | 115 |
| capability-qualified observation keys | 115 unique |
| longest proposed companion field name | 94 characters; V1 StableId limit is 128 |

## 3. Requirement audit

| Objective requirement | Evidence | Review verdict |
|---|---|---|
| release v0.1 is the only fixed semantic input | commit/tree/manifest hashes in inventory and candidate; all semantics resolve to release products | `PASS` |
| full-Roster observation mapping | all 115 placements inventoried; capability-scoped catalog, metadata and compound-field projection defined | `PASS` |
| private-state mapping | all declared state families inventoried; reducer and DecisionRecord-derived replay paths separated | `PASS_WITH_IMPLEMENTATION_CONDITION` |
| intent/message mapping | all 107 placements covered by an injective identity grammar, canonical carriers and message-materialization rules | `PASS` |
| lifecycle/result mapping | thirteen lifecycle families, ownership, cross-hop lineage and disposition/result ladder defined | `PASS_WITH_IMPLEMENTATION_CONDITION` |
| identity, authority and resources | entity/actor/unit/capability layers, one-resource-owner rule and scoped authority model defined | `PASS` |
| cross-object consistency | 34 deterministic conformance rules cover release through run identity | `PASS_AS_DESIGN` |
| carrier classification | each material family classified as V1, internal mapping or scenario extension; watchpoints have concrete triggers | `PASS` |
| narrow successor seam only if necessary | no concrete V1 loss found; no successor proposed | `PASS` |
| no new role or Definition rewrite | product inventory equals release; no tracked release file was edited by this Goal | `PASS` |
| no implementation/simulation/Rule v2/LLM/RAG | outputs are mutable Markdown design artifacts only | `PASS` |

## 4. Adversarial findings and resolutions

### `SR-01` — global semantic IDs would collide

**Challenge.** The release contains 107 intent placements but only 98 distinct
reader-facing labels. The current mapping uses a global dictionary keyed by
`semantic_id` and assigns each entry one actor.

**Resolution.** The candidate keys the registry by capability and reader ID,
then derives 107 unique V1 action types. Reader-facing labels and Definition
content remain unchanged.

**Status.** `RESOLVED_IN_CANDIDATE`.

### `SR-02` — one product per actor would duplicate institutions

**Challenge.** A member bank can be both an independent resource contributor
and a call-money lender; a named institution can also receive a
population-derived capability. Separate actors would duplicate balance sheets,
authority and relationships.

**Resolution.** Products are capability authorities. Actor assembly composes
capabilities under one entity and ParticipantArtifact. Population-unit weights
do not multiply resources or create a common wallet.

**Status.** `RESOLVED_IN_CANDIDATE`.

### `SR-03` — no-intent decisions cannot be forced into an invented action

**Challenge.** Released abstention is a DecisionRecord state, not an additional
intent. The first candidate draft placed all private state behind StateDelta,
which would tempt implementation to invent a no-op action merely to update a
consumption cursor or abstention posture.

**Resolution.** Effectful private posture uses reducer state. A consumption
cursor or bounded no-intent posture that is fully defined by DecisionRecord,
observation refs, commitment basis, blocker and revisit condition is a sealed,
deterministic trace-derived private view. It cannot alter world/process state.

**Status.** `RESOLVED_DURING_REVIEW`.

### `SR-04` — V1 flat values could hide compound-object loss

**Challenge.** Dossiers, proposals, offers and loans contain several related
properties; one stable ref alone could become a hidden live lookup.

**Resolution.** The candidate requires a stable object/version plus explicit
atomic RuntimeFields and version-coherence validation. A backend cannot
dereference current hidden WorldState. The current release exposes no object
that cannot be normalized this way.

**Status.** `RESOLVED_AS_DESIGN`; retained as a concrete successor watchpoint.

### `SR-05` — scenario variants could leak into policy

**Challenge.** NYCH route, NBC termination provenance, committee/resource-pool
and venue choices may become hidden actor branches or change mid-run.

**Resolution.** Variants are immutable, system-only configuration included in
config/bundle identity. Actors receive only resulting admissible observations.

**Status.** `RESOLVED_IN_CANDIDATE`.

### `SR-06` — accepted action could still be mistaken for business success

**Challenge.** The wider Roster introduces request, review, message,
commitment, booking, payment and settlement processes. A single accepted flag
would collapse their causal order.

**Resolution.** ActionDisposition, communication route, delivery, business
disposition, execution result, StateDelta and later delivered observation are
separate authoritative records.

**Status.** `RESOLVED_IN_CANDIDATE`.

### `SR-07` — representation enums could be read as behavioral ontology

**Challenge.** V1's `autonomous_participant_agent` label could be mistaken for
a claim that NYCH, TCA or a committee is a unitary person.

**Resolution.** The enum denotes an endogenous decision interface only.
ParticipantArtifact profiles retain each Definition's representation,
governance and aggregation limits. Scenario-owned NYSE mechanics remain an
environment capability.

**Status.** `RESOLVED_BY_EXPLICIT_INTERPRETATION`.

### `SR-08` — a design-only candidate cannot satisfy required policy refs

**Challenge.** V1 ParticipantArtifact requires a stable `rule_policy_ref`, but
this Goal does not authorize Rule implementation.

**Resolution.** The candidate explicitly generates no ParticipantArtifact.
The field remains unassigned until a separately authorized implementation
binds a reviewed policy. Mapping acceptance cannot be presented as a valid
runtime artifact.

**Status.** `RESOLVED_BY_NON_EXECUTABLE_BOUNDARY`.

## 5. Cross-object consistency review

### Identity and resource test

```text
one entity
  -> one endogenous actor
  -> one ParticipantArtifact
  -> capability union
  -> one authority graph and resource ledger
```

This passes for named actors, institution-preserving population units and
multi-capability institutions. Depositor units remain separate claim owners
hosted by a trust; they are not capabilities of the host institution.

### Information test

```text
released observation
  -> scenario-owned source/version
  -> participant-time and visibility filter
  -> frozen ObservationPayload
  -> DecisionRecord observation ref
```

No candidate path permits a policy to read WorldState directly, infer an
undelivered message or recover a future/held-out result.

### Intent and result test

```text
released commitment
  -> capability-qualified DecisionRecord basis
  -> capability-qualified ActionIntent
  -> authority/resource/lifecycle adjudication
  -> optional correlated MessageIntent
  -> independent transport/delivery
  -> business disposition/execution
  -> reducer StateDelta
  -> later actor-visible result
```

No Agent self-realizes a result. Invalid and partial attempts remain visible.

### Replay test

Runtime bundle/config/artifact hashes pin actor assembly, definitions,
observations, action spaces, scenario variants and initial state. Trace records
pin decisions, intents, messages, dispositions, deliveries and deltas.
Reducer-state and DecisionRecord-derived private state can both be reproduced
without backend-local memory.

## 6. Minimality review

The candidate adds only three design surfaces:

1. a capability-aware consolidated mapping profile;
2. a scenario actor/lifecycle/variant semantic layer; and
3. declarative cross-object validation.

It does not add a second H2EPR framework, new role, generic Agent archetype,
LLM interface, RAG/evidence service, evaluation framework, simulation policy or
Contracts version. A V1 successor would add cost without repairing a
demonstrated loss and is therefore rejected at this stage.

## 7. Conditions before implementation

Owner acceptance of this design does not satisfy these later implementation
conditions:

1. materialize an explicit machine entry for exactly 107 intent placements,
   with per-intent parameter types, carriers and validators;
2. materialize all 115 observation entries and prove Definition-domain parity;
3. declare a concrete actor/unit/capability assembly and preserve one resource
   owner across composed capabilities;
4. implement every required lifecycle transition and negative transition test;
5. prove reducer/trace closure for both reducer-state and trace-derived private
   state, including a no-intent abstention case; and
6. rerun the narrow-successor watchpoints before any contract-change request.

These conditions belong to the separately authorized implementation slice;
they are not missing semantic decisions in the current candidate.

## 8. Owner decision resolution

### `OD-CM-01` — consolidated identity model

Accept one entity/actor/resource owner with composed released capabilities,
including institution-preserving population units and host-scoped depositor
units.

**Resolution:** `ACCEPTED`.

### `OD-CM-02` — semantic mapping model

Accept capability-qualified observation/intent identities, two authoritative
private-state replay paths, canonical V1 carrier precedence and the separated
lifecycle/result ladder.

**Resolution:** `ACCEPTED`.

### `OD-CM-03` — carrier decision

Accept `Contracts V1 KEEP`, `internal consolidated mapping successor REQUIRED`
and `Panic 1907 scenario semantic extension REQUIRED`, with no Contracts
successor at this stage.

**Resolution:** `ACCEPTED`.

### `OD-CM-04` — later first implementation slice

After a separate formal-promotion and implementation authorization, begin with
the mapping-loader/conformance slice in `v1-carrier-review.md`, not a Rule
policy or simulation.

**Resolution:** `ACCEPTED_AS_FUTURE_SCOPE`; this decision does not authorize implementation.

## 9. Final review statement

The candidate preserves the released Agent/population semantics while giving
the full event a single identity, information, authority, resource, lifecycle
and result model. Its remaining work is deliberate executable materialization
and testing, not unresolved semantic architecture. The owner accepted OD-CM-01 through OD-CM-04. The specification is formally
accepted for design use and for no broader claim.
