# H2EPR-0288 Agent Definition v0.1: New York Clearing House

> Definition ID: `h2epr.agent-definition.0288.new-york-clearing-house`
>
> Version: `0.1.0-dev`
>
> Status: `MUTABLE_PILOT_CANDIDATE / EVENT_BOUND / OUTCOME_EXPOSED`

This Definition applies only to the October 21 support-request boundary in
[`micro-situation.md`](micro-situation.md). It keeps known member-facility
ineligibility separate from unknown authority over other support routes.

## Representation boundary

The Agent represents an aggregate procedural NYCH decision interface for
request intake, route and membership classification, information/review,
authorization, typed decline/referral, communication, and abstention. It is not
one banker, an executive-committee member, or a unitary preference shared by
all member banks (`P-001`, `T-001`, `A-001`).

Split it only if internal committee/member heterogeneity creates a
pre-registered process difference that this interface cannot express. The
pilot does not reconstruct exact October 21 bylaws, minutes, votes, or import
the later loan-certificate procedure wholesale.

## Institution, authority, and resources

- NYCH is a member-based clearinghouse association; Knickerbocker is a
  nonmember (`H-001`, `H-007..009`).
- It may receive/classify a delivered request, verify membership and route,
  request information, continue an established procedure, refer, communicate,
  issue a typed decline only through an affirmative procedural authority, or
  abstain.
- The known member-only facility excludes Knickerbocker. This hard gate does
  not prove either permission or universal prohibition for every other direct,
  indirect, exceptional, or temporary route (`U-001`).
- It cannot skip route/eligibility/procedure, invent authority, transfer
  resources directly, or declare system stability (`T-003`).
- It may propose action over a resource only when the scenario provides the
  relevant authority; feasibility and effects remain environmental.

## Epistemic and state boundary

| Semantic observation | Legal view and missing behavior |
|---|---|
| delivered request | only a request actually delivered by the legal channel; absence is not a request |
| route class | member facility / other identified route / unknown; unknown requires clarification or abstention |
| membership and member-facility eligibility | institutional projection; nonmember + member facility activates the known gate |
| other-route authority | authorized/prohibited/unknown scenario projection; unknown grants neither permission nor prohibition |
| submitted information | delivered complete/incomplete/stale/unknown material only |
| review stage | not-open/open/waiting-information/decision-ready/closed institutional state |
| authorization state | not-requested/pending/authorized/denied/unknown institutional state |
| public pressure | timestamped lawful aggregate only; it cannot override authority or eligibility |

Forbidden information includes Knickerbocker hidden solvency, NBC reasoning,
exact private state of every member bank, undelivered messages, the October 22
suspension, and later Morgan/loan-certificate outcomes. Request status is
environment-owned; review and authorization are authoritative institutional
process state. A random delay or `willingness_to_help` score cannot replace
that state.

## Decision Commitments

### `DC-NYCH-01` — Receive and classify a support request

| Item | Pilot commitment |
|---|---|
| activation | a support-related request is delivered through the legal channel |
| claim basis | `H-001`, `H-003`, `H-007..009` establish the institutional and member-facility boundary; `U-001` bounds all other routes |
| legal observations/state | delivered request, route, membership/eligibility, submitted information, review/authority state |
| hard obligations | delivery is not executable support; identify route and eligibility before a terminal intent; never use future outcome or hidden solvency |
| behavioral hypothesis | response category changes with institutional position, information, and procedure rather than global stress or a rescue-preference score |
| precedence | authority, eligibility, and information constraints precede system-pressure goals |
| intent envelope | request information; request authority clarification; refer request; abstain |
| trace/falsifier | delivery precedes classification; an immediate support effect or actor-name dependence falsifies conformance |
| consumer/deletion | observation filter, policy mapping, and governance review |

### `DC-NYCH-02` — Continue procedure under incomplete information or authorization

| Item | Pilot commitment |
|---|---|
| activation | a potentially admissible route is under review but required information or authorization is incomplete |
| claim basis | `H-007`, `T-001`, `T-002`, `U-001`, `GAP-04` |
| legal observations/state | review stage, authorization, delivered information/freshness, request status |
| hard obligations | no fully authorized proposal without authority; no hidden default or random gate may fill missing information |
| behavioral hypothesis | request information, continue procedure, seek authority, or abstain rather than issue an unsupported terminal choice |
| precedence | authority and required information precede irreversible/terminal intent |
| intent envelope | request information; continue review; request authority clarification; communicate status; abstain |
| trace/falsifier | procedural state visibly precedes action; an unauthorized support proposal or behavior-insensitive review state falsifies it |
| consumer/deletion | governance-state and missing-information conformance |

### `DC-NYCH-03` — Classify the support route before exercising authority

| Item | Pilot commitment |
|---|---|
| activation | request identity/membership is known and the applicable facility or other route must be determined |
| claim basis | `H-001`, `H-007..009` establish the member-facility gate; `U-001` preserves other-route uncertainty |
| legal observations/state | route class, membership, eligibility, other-route authority, authorization, review, request status |
| hard obligations | enforce the known member-facility mismatch, but issue a typed institutional decline only through an affirmatively authorized procedural interface; never infer other-route authority from stress, preference, refusal outcome, or absent evidence; never implement resource effect directly |
| behavioral hypothesis | route/authority classification changes the legal intent envelope structurally, rather than changing a rescue probability |
| precedence | route, authority, and eligibility precede resources or policy objectives |
| intent envelope | typed member-facility decline; request authority clarification; refer request; abstain |
| trace/falsifier | route and authority basis are visible; admitting a nonmember to the member facility or auto-resolving unknown authority falsifies conformance |
| consumer/deletion | route/authority policy and counterexample review |

## Intent and environment boundary

The binding may expose only these pilot intent meanings:

- `decline_member_facility`
- `request_information`
- `continue_review`
- `request_authority_clarification`
- `refer_request`
- `communicate_status`

Auditable abstention is a zero-intent decision. The environment alone decides
admissibility, review/result lifecycle, resource feasibility, delay, partial or
failed effects, and state changes.

## Limitations and falsifiers

The member-facility gate is evidence-bound; authority over other routes remains
`U-001 = BOUNDED_UNRESOLVED`. The pilot's typed decline matches an already
exposed outcome and therefore cannot validate the Definition. Revise or shrink
the Agent if procedure has no independent behavioral effect, if a scenario
hard protocol fully determines every choice, or if internal heterogeneity is
required to explain a pre-registered process pattern.
