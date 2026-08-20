# H2EPR-0288 two-role Definition binding

> Mapping profile ID: `h2epr.agent-definition.mapping.0288.two-role.v0_2_1`
>
> Status: `ACCEPTED_MAPPING_SPECIFICATION / NON_EXECUTABLE`
>
> Carrier target: H2EPR contracts V1

## 1. Bound inputs

| Input | Version or SHA-256 |
|---|---|
| Knickerbocker Definition | `0.2.1`; `df800bea6820eb5087c02fbcdb446b0f4ca558be143ed0d89d81074d75562758` |
| NYCH Definition | `0.2.1`; `8b4e66fc18c4c032cca2d3028d598a5ad4256303599e3d1a055cc9d83dd1a4df` |
| Source register | `9b4c44d3e7c5f48143e55c8235faa985712f74da01512eae47969c130740b2e9` |
| Evidence ledger | `e9f22d792a3a78f4bd23684edd09969ff433bcaae799df1db8316fb21ae60cd7` |
| Decision situations | `b9cd28a6b95481e75135ad91a3651ea9f286b757142e22189ce266423d8c0883` |
| Scenario identity/lifecycles | `8a60c1607cf1226bb8249d087f35b01c6d1a0b1ac5b16f68c1b383f6779837b7` |
| Intent registry | `63bb8c9d39d190c139a62b9dd14df9d95b3d19534e562516417aac462cccbe87` |
| Cross-object conformance rules | `9a9a9aae6908409450aa6831da5c5f011846474423bf5571171344fc40a1746f` |
| V1 core schema | `d6bea7e1094071c5187e16c2c52e989d8353e426da4d385206a11a189c5c5cf5` |

Any bound content change invalidates this mapping until the affected hash and dependent mapping are reviewed and updated.

## 2. Participant binding projection

Each future `ParticipantArtifact` must carry these namespaced values in its profile/behavior projection:

```text
h2epr.agent_definition.id
h2epr.agent_definition.version
h2epr.agent_definition.content_sha256
h2epr.agent_definition.mapping_profile_id
h2epr.agent_definition.decision_commitment_ids
h2epr.agent_definition.hard_obligation_ids
h2epr.agent_definition.behavioral_hypothesis_ids
h2epr.intent_registry.id
h2epr.intent_registry.version
h2epr.intent_registry.content_sha256
h2epr.evidence_ledger.snapshot_sha256
```

The fields contain IDs, versions, hashes, and flat ID arrays only. They do not embed the Definition, evidence
ledger, intent registry, or scenario state.

### Knickerbocker participant inventory

- representation: aggregate authorized company decision interface;
- commitments: `DC-KT-01..04`;
- observations: nine declared concepts;
- participant decision state: `last_verified_condition_time`, `operational_posture`, request-strategy posture;
- action space: eleven registry intents;
- structural behavioral hypothesis: `DC-KT-02` exposed five-gate submission rule.

### NYCH participant inventory

- representation: aggregate procedural institutional interface;
- commitments: `DC-NYCH-01..05`;
- observations: twelve declared concepts after separating disposition, communication, and result;
- participant decision state: procedural assessment posture and last-consumed record versions;
- action space: ten registry intents;
- scenario-conditional commitment: `DC-NYCH-04`, enabled only under the correctly bound sensitivity variant and
  explicit competent route/forum.

## 3. Observation binding inventory

All concepts map to actor-specific `ObservationPayload.fields`; none authorizes direct `WorldState` access.

### Knickerbocker Trust

```text
internal_liquidity_assessment
withdrawal_pressure
asset_liquidity_assessment
collateral_package_status
corporate_authorization
clearing_channel_status
support_request_status
received_information_request
delivered_disposition
```

### New York Clearing House

```text
delivered_request
relationship_status
route_classification
facility_eligibility
request_authorization_evidence
financial_information_status
review_state
authority_state
resource_proposal_status
case_disposition_status
case_communication_status
delivered_case_result
```

Each observation uses a flat field family for value, authoritative record ref, as-of/effective time, freshness,
availability, and relevant scope. The V1 information boundary and access rules must explicitly deny all forbidden
Definition fields.

## 4. World and process binding

| Semantic family | V1 placement | Single owner |
|---|---|---|
| entity and modeled representation | entity registry and participant artifact | construction/bundle |
| membership and clearing relationship | `WorldState.relations` | scenario/reducer |
| institutional authority and eligibility | `access_grants` plus scoped `process_states` | governance/environment process |
| request, case, dossier, proposal, commitment | `commitments` plus `process_states` | environment process |
| resources and realized effects | `resources` and reducer deltas | reducer/environment |
| public/exogenous signal | `public_signals` or exogenous event | scenario schedule |
| participant decision posture | actor-private scoped `process_states` | declared participant-state path, reducer committed |
| NYCH structural variant | system-only immutable initial `process_states` | construction/scenario identity |

The seven lifecycle specifications determine legal transitions. Flat fields are sufficient for the bounded
single-request/case slice; a nested successor carrier remains conditional on an actual atomicity/reference
failure.

## 5. Action and communication binding

- `RuntimeScenarioBundle.action_registry` contains exactly twenty-one action definitions corresponding to the
  registry semantic IDs.
- `ParticipantArtifact.action_space_refs` contains only the eleven or ten actions declared for that role.
- Each DecisionRecord cites its actual ObservationPayload and applicable Definition commitment(s).
- Each domain intent creates one ActionIntent; parameters, target, authority, resource request, time,
  idempotency, and visibility follow the registry's canonical-slot projection. A semantic value has one
  canonical carrier location; repeated delivery content is checked projection, not a second authority.
- An external institutional act creates its correlated MessageIntent only after accepted/partial action
  admission. If deterministic message IDs are reserved while the decision is staged, the final sealed
  DecisionRecord must list exactly the MessageIntents actually materialized. Internal scenario-owned
  governance/review/preparation processes require no synthetic message.
- Action and communication dispositions have separate reason/status namespaces and trace records.

### Focal mediated route

The first-slice request route is modeled as one explicit communication route from Knickerbocker to NYCH with an
`nbc_mediated` channel/relationship identity. NBC is a scenario-owned channel condition, not a policy-bearing
participant. Delivery can be released or blocked only by an explicit scenario relationship/channel event.

This abstraction supports the focal delivery question but cannot explain why NBC transmitted, shaped, or later
withdrew the channel. The causal-scope metadata and trace must state that limitation.

The return route carries NYCH case information/status/disposition messages to Knickerbocker through an authorized
case-delivery channel. Exact historical messenger identity or latency is not fixed by this specification; a future
synthetic conformance fixture may use explicit test timing without claiming it as history.

## 6. Decision and trace closure

Required trace closure:

```text
Definition + registry + scenario identity
  -> legal ObservationPayload
  -> DecisionRecord(commitment/rule basis)
  -> ActionIntent
  -> ActionDisposition
  -> StateDelta or explicit no-effect
  -> correlated MessageIntent when applicable
  -> CommunicationDisposition / sent / delivered / expired
  -> authoritative disposition/result
  -> later ObservationPayload
  -> TickSeal / RunSeal
```

Every skipped stage must be inapplicable under the registry rather than merely absent. Invalid attempts use the
safe diagnostic path defined by `CO-18`.

## 7. V1 carrier re-check

| Mapped issue | V1 carrier | Verdict |
|---|---|---|
| five qualitative KT gates | flat observation/process fields plus DecisionRecord/rule basis | `FIT_WITH_INTERNAL_MAPPING` |
| bounded request content | ActionIntent flat params, resource request, timing, registry validation | `FIT_WITH_INTERNAL_MAPPING` |
| NYCH case disposition | process/commitment field, ActionDisposition and StateDelta | `FIT_WITH_INTERNAL_MAPPING` |
| NYCH communication status | MessageIntent, CommunicationDisposition/history, process field | `FIT_EXISTING_V1` |
| later delivered case result | ActionDisposition/StateDelta plus later observation | `FIT_EXISTING_V1` |
| immutable structural variant | system-only initial process field, bundle/manifest hash | `FIT_WITH_INTERNAL_MAPPING` |
| seven business lifecycles | flat stable-ID field families and reducer deltas | `FIT_FOR_BOUNDED_SINGLE_CASE`; concurrency watchpoint retained |
| twenty-one parameter contracts | ActionDefinition names plus RuntimeFields and cross-object registry | `FIT_WITH_INTERNAL_MAPPING`; first-class parameter-schema watchpoint retained |
| canonical parameter-to-carrier projection | ActionIntent top-level slots plus flat RuntimeFields | `FIT_WITH_INTERNAL_MAPPING`; duplicate conflicting projections fail closed |
| decision/action/message staging | DecisionRecord arrays, deterministic IDs, ActionDisposition, MessageIntent | `FIT_WITH_ORCHESTRATION_CHANGE`; no rejected/delayed orphan message ID permitted |
| fail-closed semantic validation | project-level validator over V1 objects | `IMPLEMENTATION_REQUIRED`, not a V1 schema gap |

This mapping introduces no irreducible carrier counterexample and therefore retains:

```text
V1_COMPATIBLE_VIA_EXPLICIT_INTERNAL_MAPPING_AND_CROSS_OBJECT_VALIDATION
v1_successor_required=NO
```

## 8. Specification completeness and deliberate gaps

Specified here:

- 4+5 Commitment identity and semantics;
- 9+12 observation inventory;
- seven authoritative lifecycles;
- two immutable NYCH structural interpretations;
- 21 unique intent contracts;
- 21 cross-object rule designs and 20 minimum conformance cases;
- first-slice carrier and causal boundary.

Not produced:

- actual ParticipantArtifact or RuntimeScenarioBundle JSON;
- action/communication registry JSON;
- executable loader, mapper, validator, Rule policy, reducer extension, or tests;
- a historical route latency, request amount, exact mandate, or NYCH focal procedure;
- an active binding, simulation run, historical calibration, or validity claim.

## 9. Implementation entry conditions

This accepted mapping is non-executable by itself. Any separately authorized implementation slice must satisfy
all of the following:

1. use only `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`; the bounded-discretion proposal branch remains a
   separate structural-sensitivity slice;
2. materialize Definition identity, the executable intent registry, and fail-closed validators before adding role
   policy branches;
3. close DecisionRecord, ActionIntent, ActionDisposition, MessageIntent, and communication-disposition staging
   without orphan references or pre-admission delivery;
4. label synthetic inputs as conformance fixtures rather than historical measurements;
5. leave the frozen `0.1.0-dev` engineering fixture unchanged and never cite it as current Definition evidence;
6. begin with static, unit, binding, and conformance tests; simulation remains separately authorized; and
7. stop for a narrow successor review if implementation reveals a concrete V1 carrier counterexample rather than
   hiding it in adapter defaults.

This specification does not itself authorize implementation, Rule policy changes, contract changes, or simulation.
