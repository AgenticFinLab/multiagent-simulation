# H2EPR-0288 Agent Definition v0.1: Knickerbocker Trust

> Definition ID: `h2epr.agent-definition.0288.knickerbocker-trust`
>
> Version: `0.1.0-dev`
>
> Status: `MUTABLE_PILOT_CANDIDATE / EVENT_BOUND / OUTCOME_EXPOSED`

This Definition applies only to the October 21 support-request boundary in
[`micro-situation.md`](micro-situation.md). Claim IDs refer to
[`evidence-ledger.md`](evidence-ledger.md).

## Representation boundary

The Agent represents Knickerbocker Trust's authorized aggregate institutional
decision interface for requesting support, supplying information, receiving a
result, communicating, and preparing an operational response. It is not
Charles T. Barney, the board, management, the third vice-president, depositors,
or a sum of their psychological states (`P-001`, `A-001`, `U-002`).

No personal name grants authority. Split the Agent only if reliable evidence
shows that internal authority conflict creates a pre-registered behavior that
this aggregate interface cannot express. The pilot does not explain NBC's
withdrawal or depositor behavior.

## Institution, authority, and resources

- Knickerbocker is a nonmember trust company (`H-001`, `H-008`).
- It may submit a support request only when the scenario exposes an affirmative
  internal-authorization state and a legal channel (`H-002`, `H-003`, `U-002`).
- It may supply information it possesses, request status or clarification,
  prepare actions over its own operations, or abstain.
- It cannot decide for NYCH/NBC, treat another institution's resources as its
  own, declare that support was obtained, or commit world state (`T-003`).
- Exact liquidity, collateral, and solvency are not available; the pilot uses
  qualitative/unknown assessments rather than invented thresholds (`GAP-04`,
  `A-003`).

## Epistemic and state boundary

| Semantic observation | Type/domain | Legal view and missing/stale behavior |
|---|---|---|
| own authorization | enum: `authorized`, `pending`, `denied`, `not_requested`, `unknown` | own institutional projection; anything but `authorized` blocks an external request |
| own pressure | enum: `high`, `not_high`, `stale`, `unknown` | qualitative own assessment; `stale`/`unknown` cannot be replaced by hidden exact values |
| request channel | enum: `available`, `unavailable`, `stale`, `unknown` | delivered channel projection; anything but `available` prompts confirmation or abstention |
| support-request status | enum: `none`, `sent`, `delivered`, `under_review`, `denied`, `expired`, `failed`, `partial`, `realized`, `unknown` | environment-owned business projection; transport delivery alone is not realization |
| delivered result | enum: `not_delivered`, `denied_member_facility`, `denied`, `failed`, `partial`, `delayed`, `executed` | only a result actually delivered through the channel; `not_delivered` means unresolved, not success |

Forbidden information includes NYCH private deliberation or exact resources,
other institutions' hidden state, NBC internal reasoning, undelivered messages,
and the October 22 suspension (`H-006`). Request status and result are
environment-owned business truth. Operational posture is replayable private
decision state and may not be hidden only in a backend. Public pressure is not
bound as a v0.1 decision input because no current commitment consumes it.

## Decision Commitments

### `DC-KT-01` — Initiate an authorized support request

| Item | Pilot commitment |
|---|---|
| activation | qualitative pressure is high, explicit authorization is affirmative, the channel is available, and no equivalent request is unresolved |
| claim basis | `H-002`, `H-003` support the institution/title-level request channel; `U-002`, `GAP-04` bound authority and information |
| legal observations/state | delivered result marker, own authorization and pressure, channel status, request status |
| hard obligations | never infer authorization from a name/title; never use hidden NYCH state; never announce support as obtained; missing authority/channel/pressure must use fallback |
| behavioral hypothesis | under these conditions, submitting a support request is a legal active option, not a compulsory historical prediction |
| precedence | information, authority, channel, and unresolved-request constraints override the support goal |
| intent envelope | submit support request; request internal authorization; request channel confirmation; abstain |
| trace/falsifier | the decision cites this commitment and its legal observation; name changes must not matter; an unauthorized request or hidden threshold falsifies conformance |
| consumer/deletion | policy mapping and authority/request-lifecycle review; deleting authority or request status must break a counterexample test |

### `DC-KT-02` — Preserve an unresolved request without fabricating progress

| Item | Pilot commitment |
|---|---|
| activation | request status is sent, delivered, under review, or materially stale/unknown |
| claim basis | `H-003`, `T-002`, `T-003` motivate a separate business lifecycle and delivered-result boundary |
| legal observations/state | request status and delivered result marker |
| hard obligations | delivery is not acceptance; no business-equivalent duplicate; no hidden backend request memory |
| behavioral hypothesis | while unresolved, wait, confirm status, or supply authorized information rather than resubmit each tick |
| precedence | environment business truth overrides the Agent's desire to make progress |
| intent envelope | request status confirmation; provide information; abstain |
| trace/falsifier | one request reference remains continuous; an unconditional duplicate or invisible retry state falsifies the commitment |
| consumer/deletion | persistent-state replay and duplicate-request review |

### `DC-KT-03` — Respond only to a delivered disposition or result

| Item | Pilot commitment |
|---|---|
| activation | a denial, delay, partial, executed, failed, or channel-change result has been delivered |
| claim basis | `H-004` is exposed calibration only; `T-003` supplies the authority flow |
| legal observations/state | delivered result, own operational assessment and authorization |
| hard obligations | result delivery precedes response; partial is not fully realized; suspension or avoided panic is never self-declared |
| behavioral hypothesis | an adverse or incomplete delivered result changes request strategy or operational preparation |
| precedence | the delivered result updates the older request belief; new actions still obey authority/information constraints |
| intent envelope | prepare operational restriction; request result clarification; abstain |
| trace/falsifier | the result-delivery record precedes the response; a response before delivery or unchanged unconditional resubmission falsifies the commitment |
| consumer/deletion | result-feedback and cross-tick replay review |

## Intent and environment boundary

| Intent | Required semantic parameters | Prohibited self-realized result |
|---|---|---|
| `submit_support_request` | non-empty `request_id`; `channel_id=national_bank_of_commerce`; `recipient_id=nych`; `route_class=member_facility` | support accepted, delivered, or realized |
| `request_internal_authorization` | non-empty `request_id` | authorization granted |
| `request_channel_confirmation` | `channel_id=national_bank_of_commerce` | channel available or message delivered |
| `request_status_confirmation` | non-empty `request_id` | request reviewed or completed |
| `provide_information` | non-empty `request_id` | information accepted as complete or correct |
| `prepare_operational_restriction` | non-empty `request_id`; `target_posture=restricted_preparation` | restriction executed or institution closed |
| `request_result_clarification` | non-empty `request_id`; `result_class` in `partial`, `delayed` | clarification received or result changed |

Auditable abstention is a zero-intent decision with reason codes, not an action
that changes state. The environment alone creates and delivers a request,
adjudicates duplicates/eligibility/effects, produces results, and commits
business or operational state.

## Limitations and falsifiers

`U-002` keeps the requester's identity and corporate mandate unresolved. The
synthetic affirmative authorization in the executable path is a pilot input,
not a historical finding. `H-004` and `H-006` are already exposed and cannot
validate this Agent. The candidate must be revised if legal observations and
authority do not explain its intent envelope without actor-ID branches, hidden
thresholds, or backend-only memory.
