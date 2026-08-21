# Observation semantic registry

> Registry ID: `h2epr.observation-registry.0288.two-role`
>
> Status: `DERIVED_MAPPING / DEFINITION_0.2.1`

This registry is the machine-facing projection of the two Agent Definitions'
epistemic-interface tables. The Definitions remain authoritative for meaning;
this file fixes only the value representation that an implementation may
deliver to a policy.

Every observation also carries the existing authoritative-record reference,
as-of time, freshness, availability, and actor scope. Those metadata fields do
not relax the value contract below.

## Value forms

| Form | Runtime representation | Rule |
|---|---|---|
| `enum` | one string from the listed domain | invented synonyms and lifecycle labels fail closed |
| `stable_id` | one non-empty stable identifier | the referenced record remains the authority for its content |
| `nullable_stable_id` | a stable identifier or `null` | `null` is required while the delivered object is unavailable |
| `status_reason_pair` | `[status, reason_code_or_null]` | status uses the listed domain; `none` requires a null reason; any other status requires a typed reason code |

The pair form keeps status and reason distinct without adding a new V1 field.
The observation's authoritative-record reference still identifies the source
record. It must not be replaced with a case lifecycle state or a narrative
summary.

## Knickerbocker Trust

| Observation | Form | Domain or projection |
|---|---|---|
| `asset_liquidity_assessment` | `enum` | `readily_available`, `conditionally_liquid`, `illiquid`, `disputed`, `unknown` |
| `clearing_channel_status` | `enum` | `active`, `termination_notice_delivered`, `ending_at_time`, `inactive`, `disputed`, `unknown` |
| `collateral_package_status` | `enum` | `not_prepared`, `preparing`, `available`, `submitted`, `disputed`, `unknown` |
| `corporate_authorization` | `enum` | `not_requested`, `pending`, `authorized`, `denied`, `unknown` |
| `delivered_disposition` | `status_reason_pair` | `none`, `pending`, `need_information`, `referred`, `refused`, `prohibited`, `delayed`, `partial`, `failed`, `executed` |
| `internal_liquidity_assessment` | `enum` | `adequate`, `strained`, `critical`, `unknown` |
| `received_information_request` | `nullable_stable_id` | delivered information-request identity |
| `support_request_status` | `enum` | `none`, `prepared`, `sent`, `delivered`, `awaiting_information`, `under_review`, `refused`, `expired`, `withdrawn`, `partial`, `failed`, `executed`, `unknown` |
| `withdrawal_pressure` | `enum` | `ordinary`, `elevated`, `severe`, `unknown` |

## New York Clearing House

| Observation | Form | Domain or projection |
|---|---|---|
| `authority_state` | `enum` | `no_competent_authority_identified`, `committee_scope`, `membership_scope_required`, `authorized`, `denied`, `disputed`, `unknown` |
| `case_communication_status` | `enum` | `not_issued`, `issued`, `transport_pending`, `delivered`, `expired`, `failed`, `unknown` |
| `case_disposition_status` | `status_reason_pair` | `none`, `pending`, `information_needed`, `referred`, `facility_declined`, `other_scoped_decline`, `conditioned_proposal`, `closed` |
| `delivered_case_result` | `status_reason_pair` | `none`, `delayed`, `partial`, `failed`, `executed`, `withdrawn` |
| `delivered_request` | `nullable_stable_id` | delivered request identity |
| `facility_eligibility` | `enum` | `eligible`, `ineligible`, `not_applicable`, `disputed`, `unknown` |
| `financial_information_status` | `enum` | `not_received`, `incomplete`, `stale`, `adequate_for_scope`, `disputed`, `unknown` |
| `relationship_status` | `stable_id` | stable relationship-class identity; the referenced relationship record owns membership, clearing-agent, effective-time, and notice details |
| `request_authorization_evidence` | `enum` | `sufficient`, `incomplete`, `disputed`, `absent`, `unknown` |
| `resource_proposal_status` | `enum` | `none`, `information_needed`, `collateral_review`, `member_consultation`, `conditionally_authorized`, `scheduled`, `partial`, `failed`, `executed`, `withdrawn` |
| `review_state` | `enum` | `not_open`, `collecting_information`, `examining`, `awaiting_forum`, `decision_ready`, `complete`, `closed` |
| `route_classification` | `enum` | `member_facility`, `nonmember_clearing_matter`, `other_identified_route`, `unresolved` |

## Cross-object rules

1. A runtime value outside the declared form or domain is rejected before the
   policy receives it.
2. An unavailable enum uses `unknown` only when that value is declared in its
   domain. An unavailable `nullable_stable_id` is `null`. An unavailable
   `status_reason_pair` uses `["none", null]`; other unavailable forms fail.
3. Case lifecycle (`received`, `classified`, `under_review`, and similar) is
   environment-owned process state. It is never projected as
   `case_disposition_status`.
4. Request-authority evidence is a dossier assessment (`sufficient`,
   `incomplete`, and related values), not the corporate authorization result.
5. Knickerbocker receives a decline as `refused` plus its typed reason; NYCH
   retains the narrower `facility_declined` case disposition. Neither value
   implies message delivery or resource effect.
6. A mapping change cannot add a synonym merely to preserve an implementation.
   If the Definition lacks a scientifically necessary concept, that gap is
   reviewed before the Definition changes.
