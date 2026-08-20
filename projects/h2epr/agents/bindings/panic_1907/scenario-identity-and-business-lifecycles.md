# Scenario identity and business lifecycles

> Specification ID: `h2epr.scenario-binding.0288.two-role`
>
> Version: `0.2.1`
>
> Status: `ACCEPTED_SPECIFICATION / NON_EXECUTABLE`

## 1. NYCH structural identity

### 1.1 Authority and placement

The unresolved alternative-route interpretation is a scenario/construction choice, not an NYCH preference,
belief, random draw, or outcome-conditioned policy branch.

Provisional V1 field family in `RuntimeScenarioBundle.initial_world_state.process_states`:

```text
h2epr.scenario.0288.nych_alternative_route_variant
h2epr.scenario.0288.nych_alternative_route_ref
h2epr.scenario.0288.nych_alternative_forum_ref
h2epr.scenario.0288.nych_variant_basis_ref
```

All four values are `runtime_system_only`. The variant field has exactly two values:

- `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`;
- `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION`.

The field family is part of the initial world-state preimage and therefore of the RuntimeScenarioBundle SHA.
The `RunManifest.runtime_bundle_sha256` binds that choice to every trace and seal.

### 1.2 Valid combinations

| Variant | Alternative route ref | Competent forum ref | Variant basis ref | Binding interpretation |
|---|---|---|---|---|
| `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` | null | null | one stable model-choice record documenting the unresolved evidence and conservative non-invention rule | no competent alternative NYCH route is introduced; this is absence of adopted evidence, not proof of historical prohibition |
| `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` | one explicit scenario-owned route ID | one explicit scoped forum/authority interface ID | one stable structural-assumption record identifying the bounded sensitivity interpretation | the named route may enter review subject to information, authority, proposal, and resource constraints; the selection does not guarantee approval or effect |

Any other combination fails closed. The sensitivity variant cannot be selected without a route and forum; the
conservative baseline cannot quietly carry a hidden alternative route. The basis ref is mandatory in both
variants and identifies a construction/modeling decision, not a historical actor belief or validation result.

### 1.3 Agent-visible derivation

The Agent does not observe the variant label. The scenario derives dated, scoped observations:

```text
route_classification
facility_eligibility
authority_state
review_state
```

Under the conservative baseline, other-route authority remains
`no_competent_authority_identified` or `unknown`, and `DC-NYCH-04` is not applicable. Under the sensitivity
variant, the explicit route can be `other_identified_route`; authority still remains a separate environment-owned
process and may be pending, denied, disputed, or authorized.

### 1.4 Immutability and comparison

The variant fields are immutable after run creation. No `StateDelta` may target them. A controlled structural
sensitivity comparison uses two separately identified bundles/runs with otherwise matched construction inputs.
Reports must label both as exposed, unvalidated structural interpretations.

## 2. Lifecycle conventions

Each business object has:

- one stable ID and object kind;
- one environment-owned authoritative status/version;
- explicit causal parent and event time;
- actor-visible projections only after permitted delivery;
- legal transitions requested by an Agent intent but committed only by the reducer;
- a separate communication state when an external message is required;
- terminal or reopen rules that never erase earlier records.

An Agent may keep a reference and its last delivered version. It may not keep a second editable business truth.

## 3. Support-request lifecycle

**Authority:** environment-owned request process. Knickerbocker owns only its request-strategy posture.

```text
none
  -> prepared
  -> sent
  -> delivered
  -> awaiting_information <-> under_review
  -> refused | expired | withdrawn | partial | failed | executed
```

| Transition | Permitted trigger | Reducer checks | Result/observation |
|---|---|---|---|
| `none -> prepared` | admitted `submit_support_request` business act | five `DC-KT-02` gates, stable ID, no equivalent unresolved request | request exists; no message or recipient case implied |
| `prepared -> sent` | correlated message is actually sent | permitted route, sender/recipient, correlation, nonduplicate transport | transport event; not delivery |
| `sent -> delivered` | message delivery event | latency/expiry/recipient and exact message correlation | NYCH may receive `delivered_request`; no acceptance implied |
| `delivered -> awaiting_information` | authoritative information-needed disposition | case/request correlation and competent issuing interface | KT receives the information request only after delivery |
| `delivered/awaiting_information -> under_review` | authoritative case/review event | correct case, route, information state | review is active; no approval implied |
| nonterminal `-> refused` | scoped authoritative decline is delivered | issuing authority, reason/scope, message delivery | adverse disposition activates `DC-KT-04`; no automatic suspension |
| nonterminal `-> expired` | expiry rule/event | time and unresolved status | request ceases to be pending; history remains |
| nonterminal `-> withdrawn` | admitted authorized withdrawal | request/version/scope and authority | downstream acknowledgement/closure remains separate |
| nonterminal `-> prepared` successor version | admitted authorized revision | same stable request object, incremented version, changed scope/content, and link to the prior version | revision does not overwrite history or imply recipient acknowledgement |
| nonterminal `-> partial/failed/executed` | delivered authoritative result | result/process reference and state delta closure | result class becomes behaviorally consequential |

`prepared`, `sent`, `delivered`, `awaiting_information`, and `under_review` are unresolved for business-equivalence
and idempotency. A new request with the same actor, target, route, scope, resource category, and material purpose is
a duplicate unless explicitly linked as an authorized revision. `partial`, `failed`, and `executed` on the request
are derived projections of the linked authoritative result record, not a second independently editable result.

## 4. NYCH case lifecycle

**Authority:** environment-owned case process. NYCH owns only procedural assessment posture and consumed record
versions.

```text
none
  -> received
  -> classified
  -> awaiting_information | under_review | awaiting_authority
  -> disposition_ready
  -> disposition_issued
  -> closed
```

| Transition | Permitted trigger | Reducer checks | Constraint |
|---|---|---|---|
| `none -> received` | delivered support-request message | one case per business-equivalent request; sender/channel/request refs | message acceptance without delivery creates no case |
| `received -> classified` | `record_and_classify_request` | membership, relationship, route, facility, requester mandate; unresolved fields preserved | classification has no resource effect |
| `classified -> awaiting_information` | `request_case_information` admitted | named missing item, recipient, scope, nonduplicate request | later material must be delivered and freshness-checked |
| `classified/awaiting_information -> under_review` | `open_or_continue_review` admitted | competent interface and applicable route | not a random timer |
| any pre-disposition `-> awaiting_authority` | procedural/member authorization request admitted | named question, forum, route/proposal scope | request does not confer authority |
| review/authority state `-> disposition_ready` | environment process establishes sufficient basis and competent issuing interface | frozen variant, information, authority, case version | does not issue or deliver a message |
| `disposition_ready -> disposition_issued` | admitted scoped disposition/proposal/status act | truthfulness, authority, reason/scope | updates `case_disposition_status`; communication is separate |
| nonterminal `-> closed` | admitted `close_or_reopen_review` closure or terminal case rule | authority, reason, outstanding obligations | never erases request, review, messages, or results |
| `closed -> under_review/awaiting_authority` | admitted reopening with an authoritative new-event ref | reopening authority and new material event | creates a new case version linked to prior closure |

## 5. Review lifecycle

**Authority:** environment-owned NYCH institutional process.

Allowed states match the Definition:

```text
not_open
  -> collecting_information
  -> examining
  -> awaiting_forum
  -> decision_ready
  -> complete
  -> closed
```

- steps may remain at the same state only with a named pending event and no duplicate act;
- an evidenced route may skip an inapplicable stage, but the reason and competent interface are recorded;
- no state is advanced by elapsed time or a random gate alone;
- `complete` means the scoped review is complete, not that the case, communication, or execution succeeded;
- reopening a closed review requires a new event and new state version.

## 6. Authorization lifecycles

### 6.1 Knickerbocker corporate authorization

```text
not_requested -> pending -> authorized | denied
unknown -> pending | denied
```

The record contains scope, competent governance interface, effective time, and source event. `authorized` opens
only the named request/disclosure/contingency scope. Expiry, supersession, or scope mismatch means the intent does
not have valid authority even if the Agent cites the old record.

### 6.2 NYCH procedural/collective authority

```text
no_competent_authority_identified | unknown | disputed
  -> committee_scope | membership_scope_required
  -> authorized | denied
```

The state is route/proposal scoped. The conservative variant cannot transition to an alternative-route forum
without a new construction identity. Under the sensitivity variant, an identified forum may still deny authority.
Member/association authorization is distinct from member commitment and resource execution.

## 7. Proposal and resource-commitment lifecycle

**Authority:** environment-owned institutional/member process. NYCH may propose transitions but owns no member
resource scalar.

```text
none
  -> information_needed | collateral_review | member_consultation
  -> conditionally_authorized
  -> scheduled
  -> partial | failed | executed | withdrawn
```

- `propose_conditioned_measure` may create a proposal only under the sensitivity variant with competent route,
  adequate scoped information, and valid authority;
- conditions, collateral/information requirements, requested commitments, scope, and expiry are explicit;
- `conditionally_authorized` is neither member agreement nor collateral acceptance;
- `scheduled` is not execution;
- only reducer-applied resource/member process events produce `partial`, `failed`, or `executed`;
- `withdrawn` requires an authoritative withdrawal/cancellation event and does not erase prior commitments.

## 8. Communication lifecycle

**Authority:** environment-owned issue and transport process. Business admissibility and transport are separate.

```text
not_issued
  -> issued
  -> transport_pending
  -> delivered | expired | failed
```

| State/event | Meaning | Explicit non-meaning |
|---|---|---|
| `issued` | competent interface authorized the bounded message content | message accepted by transport or seen by recipient |
| `transport_pending` | MessageIntent admitted/queued/delayed under the route policy | delivered or business outcome pending approval |
| `delivered` | recipient may receive the message at the recorded time | recipient agrees, acts, or produces an effect |
| `expired` | message reached its expiry without delivery | underlying disposition is reversed |
| `failed` | transport failed with typed reason | business disposition or case history disappears |

A permitted retry has a new message-intent ID and idempotency key linked to the same case disposition. It cannot
silently reuse or overwrite the failed attempt.

## 9. Result lifecycle

**Authority:** authoritative environment/reducer process.

```text
none -> delayed | partial | failed | executed | withdrawn
delayed -> partial | failed | executed | withdrawn
partial -> partial | failed | executed | withdrawn
```

- `delayed` is nonterminal and creates no current effect delta;
- `partial` records accepted/rejected scope and remaining obligation; it is nonterminal while remaining scope is
  explicit and may be terminal only when `remaining_scope=none`;
- `failed`, `executed`, and `withdrawn` are terminal for the identified result version;
- correction or reopening creates a successor result/event linked to the prior one; it does not mutate history;
- result delivery to each actor is a separate observation event.

## 10. Cross-lifecycle invariants

1. One request can create at most one active NYCH case unless an explicit split/merge record explains otherwise.
2. Request, case, review, authorization, proposal, communication, and result IDs are distinct and linked by refs.
3. Business disposition cannot be derived from message transport status.
4. Message delivery cannot be derived from business disposition.
5. Resource result cannot be derived from proposal or authorization.
6. Agent-private posture updates only after its legal observation or its own admitted preparation decision.
7. Every transition records old/new status, state versions, causal parents, authority/reason refs, and time.
8. No Agent emits a `StateDelta`; only the reducer commits transitions.
9. Duplicate, expired, unauthorized, invalid, and failed attempts remain in the trace.
10. NBC delivery/relationship events may change channel state, but this pilot does not generate NBC's underlying
    credit, routing, or withdrawal decision.
11. A closed case or terminal result can be revisited only through a new authorized event and successor version.
12. The NYCH structural variant is immutable and cannot be a transition target.

## 11. V1 fit

The seven lifecycles can be carried by stable flat field families in `WorldState.commitments` and
`WorldState.process_states`, plus `ActionDisposition`, `CommunicationDisposition`, `StateDelta`, and trace refs.
The bounded first slice has one focal request/case, so a first-class nested process object is not yet necessary.

This remains a successor watchpoint: if a real binding cannot make multi-object transitions atomic, cannot retain
unambiguous refs across concurrent cases, or cannot close partial-result semantics with flat fields, a narrow
first-class business-process carrier should be reconsidered. No such implementation counterexample exists yet.
