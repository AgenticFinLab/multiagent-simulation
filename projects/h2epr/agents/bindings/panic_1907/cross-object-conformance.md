# Fail-closed cross-object conformance rules

> Rule-set ID: `h2epr.agent-binding.conformance.v0_2_2`
>
> Status: `ACCEPTED_SPECIFICATION / PARTIAL_EXECUTABLE_CONFORMANCE`

V1 JSON Schema validates individual record shape. These rules validate meaning across Definition, evidence,
scenario, participant artifact, observation, decision, intent, communication, reducer state, trace, and seals.
A missing or ambiguous reference fails closed; validators do not repair the object or choose a scientific value.

The current machine mapping implements exact source identity, actor-specific observation domains, intent
projection, selected lifecycles, owner/capability/scope/time authority resolution, carrier correlation, trace
closure, and replay checks for the conservative first slice. The Cycle 4 behavior matrix exercises selected
policy-and-binding cases without starting a simulator. Rules outside that bounded coverage remain specifications;
partial execution is not historical or scientific validation.

## 1. Identity and inventory

### `CO-01` — Definition content identity

- Recompute Definition SHA-256 from exact bytes.
- Require ID, version, SHA, mapping-profile ID, and registry version in the participant binding.
- Require the ParticipantArtifact hash in RuntimeScenarioBundle and RunManifest.
- Fail on same version/different SHA, unknown Definition ID, or path-only identity.

### `CO-02` — evidence and use identity

- Every claim/source ref used by a Definition projection resolves to the frozen evidence ledger/source register.
- Provenance preserves event time, participant availability, exposure, and construction/calibration status.
- A construction-only or exposed claim does not become an actor observation merely because the Definition cites it.
- Fail on missing claim, changed source hash, future/held-out use, or duplicated evidence authority.

### `CO-03` — Commitment and intent parity

- Definition inventory must equal exactly four KT and five NYCH Decision Commitments.
- Registry inventory must equal exactly eleven KT and ten NYCH unique semantic intents.
- Each registry intent is declared by its Definition and names at least one declaring commitment.
- Each commitment's permitted intent is present in the registry; abstention remains a DecisionRecord state, not a
  twenty-second intent.
- Fail on orphan commitment, undeclared intent, duplicate semantic ID, or actor mismatch.

### `CO-04` — structural scenario identity

- Exactly one NYCH variant is present before the first observation.
- Conservative baseline requires null alternative route/forum refs; sensitivity requires both to resolve.
- Both variants require a stable construction/model-choice basis ref. Variant/basis fields are system-only,
  included in the RuntimeScenarioBundle SHA, and immutable in-run.
- Fail on missing/mixed value, invalid route/forum combination, Agent-visible variant label, runtime mutation, or
  outcome-conditioned selection.

## 2. Observation and information boundaries

### `CO-05` — declared observation path

For each external value used by a decision:

```text
Definition permits concept
  AND scenario owns/produces source state
  AND ObservationAccessRule permits actor/field
  AND ObservationPayload contains field/version
  AND DecisionRecord.observation_refs cites payload
```

Fail if any link is absent or if policy reads `WorldState` directly.

The machine observation domain for a concept must also match the exact observation row in that actor's bound
Definition. A value appearing elsewhere in a shared source or in the other participant's Definition does not
establish parity.

### `CO-06` — time and freshness

- Every dated observation includes source/effective time and delivery/logical time.
- Freshness is evaluated by the declared event-relative rule or a separately reviewed field rule.
- For `DC-KT-02`, each assessment is superseded by a later delivered observation of the same construct, or by a
  later event whose frozen dependency rule explicitly invalidates it. Channel change does not silently stale
  liquidity, and asset change does so only when the assessment records that dependency. No hidden tick count is
  allowed.
- Fail on missing time, future timestamp, silent stale-to-fresh conversion, or backend-specific freshness.

### `CO-07` — missing, disputed, and unknown values

- Missing/stale/disputed/unknown/not-authorized are explicit semantic values or companion fields.
- Each required missing state selects the Definition's verification, clarification, narrowed response, or scoped
  abstention branch.
- Fail if a default number/category, actor name, outcome, or model prior fills the value.

### `CO-08` — forbidden information and isolation

- Reject observations or policy inputs containing future suspension, later recovery, hidden counterpart balance,
  uncommunicated deliberation, later certificate program, Reference EPG, evaluation material, or any field denied
  by the Definition.
- Record the failed field identity and safe payload hash as an invariant violation; do not deliver it.
- A receiving Agent may classify requester authorization only from delivered request/dossier material. It may not
  read the requester's internal authorization state merely because both states exist in the same world model.
- Before a request is delivered, requester-authorization evidence is `absent` or `unknown`; request and dossier
  delivery may advance that evidence through explicit, traceable states but cannot pre-populate it.

## 3. State, lifecycle, and ownership

### `CO-09` — one state property, one authority

- Each request/case/review/authorization/proposal/communication/result property has one environment-owned path.
- Participant decision posture may cite the authoritative record/version but cannot duplicate its editable value.
- Fail on conflicting copies, backend-private authoritative state, or Agent-emitted `StateDelta`.

### `CO-10` — legal lifecycle transition

- Every requested transition exists in `SCENARIO_IDENTITY_AND_BUSINESS_LIFECYCLES.md`.
- Reducer validates current version/state, authority, triggering intent/event, and causal parents.
- StateDelta records before/after, versions, operation, invariant checks, and causal parents.
- Fail on skipped prerequisite, illegal terminal exit, in-place history rewrite, or transition without disposition.

### `CO-11` — request/case identity and idempotency

- One business-equivalent unresolved KT request and at most one active NYCH case per request.
- Action and MessageIntent idempotency keys use the registry's stable identity fields.
- Revision/retry creates a linked successor act/message, not a duplicate or overwrite.
- Fail on equivalent duplicate, case without delivered request, unlinked message retry, or changed request identity.

### `CO-12` — behaviorally material participant state

- `last_verified_condition_time`, `operational_posture`, request strategy posture, NYCH procedural assessment,
  and consumed record versions are declared, private-scoped, reducer-updated, sealed, and replayable.
- Backend-transient computation may disappear only if it cannot influence a later decision.
- Fail on hidden cooldown, memory, pending ref, prior plan, or belief that changes future behavior.

## 4. Decision and intent conformance

### `CO-13` — Decision Commitment basis and minimum response

- Every DecisionRecord cites at least one applicable `h2epr.dc.*`/hard-obligation ID plus any executable rule ID.
- Reason codes identify activation, precedence, missing/open gate, response class, and abstention blocker/revisit.
- The selected intents satisfy the commitment's minimum response; an always-wait/always-abstain policy fails.
- Fail on actor-ID-only rule, orphan executable branch, no legal observation, or unscoped abstention.

### `CO-14` — intent parameter contract

- Semantic ID, actor, action type/version, required/conditional parameters, primitive types, enum domains, units,
  targets, time, and references match `INTENT_REGISTRY.md`.
- Every semantic value maps to exactly one canonical ActionIntent slot. Any repeated value in a correlated
  MessageIntent is a delivery projection with exact equality and lineage, not a competing authority.
- Extra parameter names fail; missing conditional data remains a rejected attempt, not a default.
- `submit_support_request` requires exactly one numeric amount+unit or an explicit qualitative bound.

### `CO-15` — authority, route, and resource

- Every claimed authority ref resolves to an effective record whose owner actor, semantic capability, parameter
  scope, target scope, and effective interval all cover the attempted act.
- The attempted target set must equal the grant's target set. An empty grant means that the act has no external
  target; it is not a wildcard.
- Communication route, institutional eligibility, issuing authority, and resource ownership are checked separately.
- The member-facility gate applies only to its named facility.
- A conditioned NYCH proposal requires the sensitivity variant, explicit route/forum, and scoped authority.
- Fail on missing, expired, wrong-actor, wrong-capability, wrong-scope, or wrong-target authority; invented
  alternative route; or Agent-owned member resource.

### `CO-16` — action/message correlation

- Every domain intent creates one primary ActionIntent.
- Outward message content is created only after accepted/partial business admission and matches the admitted
  parameters and authoritative disposition.
- A staged decision may reserve deterministic message IDs, but its final sealed `message_intent_ids` must equal
  the MessageIntents actually materialized. Rejected/delayed source actions cannot leave orphan IDs or
  undisposed MessageIntents.
- One MessageIntent has one recipient; fanout has an explicit plan and separate messages.
- Decision/action/message/case/request refs and idempotency keys close.
- Fail on message-before-admission, content drift, unlinked message, or one message with multiple recipients.

### `CO-17` — disposition, delivery, and result separation

- ActionDisposition records business-act admission, accepted/rejected params, reason, state versions, and deltas or
  explicit no-effect.
- CommunicationDisposition and sent/delivered/expired records describe transport only.
- `case_disposition_status`, `case_communication_status`, and `delivered_case_result` have distinct records.
- Under the conservative structural variant, a conditioned proposal, non-neutral resource-proposal state, or
  proposal execution result is unreachable and fails before policy selection. Result-follow-up cases belong to a
  separately bound sensitivity variant.
- Fail if accepted means success, issued means delivered, delivered means counterparty agreement, or proposal means
  execution/effect.

### `CO-18` — invalid attempts remain visible

- Schema-valid but unauthorized/infeasible/duplicate attempts receive a rejected/failed disposition with typed
  reason and no effect.
- Schema-invalid attempts receive a safe `invariant_violation` or `runtime_error` record with payload hash, actor,
  failure layer, and reason; raw sensitive content need not be retained.
- Fail on adapter clamp, silent drop, conversion to another legal intent, or missing diagnostic linkage.

## 5. Trace, replay, and closure

### `CO-19` — causal trace chain

For each decision path, require resolvable order and references:

```text
observation_delivered
  -> decision_recorded
  -> action_intent_created
  -> action_disposition_recorded
  -> state_transition_applied or explicit no-effect
  -> message_intent_created when applicable
  -> communication_disposition / sent / delivered / expired
  -> later business disposition/result
  -> later actor observation
```

Optional stages may be absent only when the registry says they are inapplicable. Fail on dangling refs, causal
cycles, wrong actor, nonmonotone state version, or missing result delivery.

### `CO-20` — manifest, replay, and seals

- RunManifest binds runtime bundle, configuration, participant artifacts, code/component versions, contracts, and
  Definition mapping identity.
- Replaying identical sealed inputs reproduces record order, dispositions, state versions/hashes, and seals.
- Tick/run closure checks include the mapping conformance result.
- Fail on manifest drift, mismatched participant hash, mutable structural variant, replay divergence, or invalid
  seal closure.

### `CO-21` — causal-scope claim

- Trace/report metadata declares `focal_two_role_request_response_only`.
- NBC channel/relationship changes are labeled scenario-owned exogenous events.
- No report attributes NBC credit/routing/withdrawal, depositor run, Morgan coordination, full panic dynamics, or
  historical validation to this two-role binding.
- Fail on an endogenous/full-event claim outside Cycle 0 coverage.

## 6. Minimum conformance cases

| Case ID | Perturbation | Required outcome |
|---|---|---|
| `CC-01` | stale KT liquidity assessment | verification/blocker response; submission prohibited |
| `CC-02` | withdrawal ordinary with liquidity strained | material-pressure gate open; no submission |
| `CC-03` | withdrawal severe with liquidity unknown | return to `DC-KT-01`; no hidden default |
| `CC-04` | all five KT gates closed | exactly one bounded request is submitted |
| `CC-05` | equivalent request unresolved | duplicate rejected/absent; original identity preserved |
| `CC-06` | request message accepted but not delivered | NYCH has no delivered request or case |
| `CC-07` | delivered NYCH request has missing route/mandate | case/classification plus named procedural response |
| `CC-08` | nonmember requests member facility | facility-scoped decline/clarification; no universal ban |
| `CC-09` | decline disposition issued but message fails | business decline remains; counterparty has not observed it; failure visible |
| `CC-10` | decline message delivered | KT may adapt only after delivery; no automatic suspension |
| `CC-11` | conservative variant with no alternative route | `DC-NYCH-04` disabled for focal request |
| `CC-12` | sensitivity variant without route/forum refs | bundle/binding rejected before execution |
| `CC-13` | sensitivity variant with route/forum and valid authority | conditioned-proposal path enabled; effect still external |
| `CC-14` | proposal admitted then execution failed | disposition/message/proposal/result remain distinct; NYCH follows failure |
| `CC-15` | expired or mismatched authority ref | intent rejected with typed reason; no adapter repair |
| `CC-16` | prohibited future/Reference field | observation rejected and invariant violation recorded |
| `CC-17` | hidden persistent backend memory | conformance failure before historical validity review |
| `CC-18` | same logical inputs, actor names changed | behavior depends on role/authority, not historical name |
| `CC-19` | attempted direct StateDelta by Agent | rejected and traced |
| `CC-20` | exact replay of frozen binding | identical trace/state/seal identity |

## 7. Completion criterion

This rule set is complete as an accepted design specification when all `CO-01..21` have named inputs, a
deterministic pass/fail condition, and a diagnostic failure class; all 21 intents and seven lifecycles are
consumed; and no rule requires a new V1 field. Executable coverage is reported per validator, policy case, and
reducer path. Unexercised rules remain explicit gaps rather than inheriting a pass from the first slice.
