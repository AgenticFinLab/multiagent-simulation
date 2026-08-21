# R2 lightweight interface preflight

- Status: accepted Roster-production preflight
- Event: H2EPR-0288
- Roster: `panic_1907` v0.2
- Semantic skeleton: `panic_1907` v0.1
- Products: J. Pierpont Morgan, Trust Company of America, Lincoln Trust Company
- Scope: semantic fit only; no wire mapping, registry, executable binding, implementation or simulation

## Cross-role ownership

| Causal object | Owner in the R2 design |
|---|---|
| Morgan coordination classification, information request, invitation, proposal, solicitation and scoped position | Morgan Agent |
| examination work/report | examiner or committee process |
| five-person committee application, information call, finding and advice | future committee representation gate or scenario process |
| applicant information disclosure, request, collateral proposal, operating and communication intent | applicant Agent where admitted; TCA owns its evidenced forms |
| contributor decision and resource | each contributor or future cohort/Agent |
| Lincoln condition-statement verification, authorization, issue and correction | thin Lincoln Agent |
| request delivery, attendance, service operation, collateral admissibility/value, commitment validation, resource transfer, message delivery and effect | scenario/environment and authoritative reducer |

The ownership is compatible with the event skeleton. No R2 Agent absorbs the
committee, another institution, a contributor or an environment effect.

## Role preflight

### J. Pierpont Morgan

| Family | Candidate semantics | Participant-time/authority boundary | Fit |
|---|---|---|---|
| representation | named personal coordination interface with action-level personal/firm attribution | ambiguous firm/associate acts remain disputed or external | `MAPPING_EXTENSION_EXPECTED` |
| observation | delivered matter, scoped information/report, authority, participant roles, proposal, contributor reply, result, optional dated relationship record | no hidden books, committee deliberation, contributor intention, future result or fame-based authority | `MAPPING_EXTENSION_EXPECTED` |
| decision state | coordination posture and last-consumed authoritative versions | case/report/proposal/commitment/resource truth remains external | `KNOWN_FIT` |
| intents | classify, request information/examination, convene, form/revise proposal, solicit, assemble, communicate, close/clarify | solicitation cannot bind; proposal cannot transfer resources | `MAPPING_EXTENSION_EXPECTED` |
| lifecycle/result | case, examination/report, invitation/attendance, proposal version, solicitation/reply, commitment, transfer and result | each producer/owner remains identifiable | `MAPPING_EXTENSION_EXPECTED` |

### Trust Company of America

| Family | Candidate semantics | Participant-time/authority boundary | Fit |
|---|---|---|---|
| representation | authorized aggregate company interface | exact board/management delegation remains scoped and explicit | `KNOWN_FIT` |
| observation | participant-visible condition notice, dated company information, authority, examination request/result, route state, collateral control, service condition, communication matter, result | no hidden asset truth, future withdrawals, examiner deliberation or contributor state | `MAPPING_EXTENSION_EXPECTED` |
| decision state | institutional response posture and consumed record versions | condition, request, collateral, service, message and resource state stays authoritative externally | `KNOWN_FIT` |
| intents | verify, consent/disclose, request terms, open/update/withdraw support route, propose collateral, propose/authorize operating posture, separately authorize/issue/withhold/correct a statement, and close/pause a matter | no self-examination, self-valued collateral, self-payment or self-aid; result consumption is state update rather than a meta-intent | `MAPPING_EXTENSION_EXPECTED` |
| lifecycle/result | separate examination, route-specific request, collateral, operating, communication and result lifecycles | one route cannot overwrite another; partial/failed/executed remain distinct | `MAPPING_EXTENSION_EXPECTED` |

### Lincoln Trust Company

| Family | Candidate semantics | Participant-time/authority boundary | Fit |
|---|---|---|---|
| representation | board-authorized institutional communication interface | support, collateral, operations and resources explicitly excluded | `KNOWN_FIT` |
| observation | statement proposal, dated condition records, scoped authority, message lifecycle and material update | no hidden condition, future assistance/withdrawals or depositor belief | `MAPPING_EXTENSION_EXPECTED` |
| decision state | communication posture and consumed record versions | board and message truth remains external | `KNOWN_FIT` |
| intents | request information, authorize/narrow/withhold/issue/correct statement, seek delivery clarification, close communication matter | no support or operating intent; authorization is not delivery/effect | `MAPPING_EXTENSION_EXPECTED` |
| lifecycle/result | proposal, authorization, issue, transport, delivery, expiry/failure and correction | public availability begins only after delivery | `MAPPING_EXTENSION_EXPECTED` |

## Shared concepts required from the scenario

R2 uses semantic families already admitted by the skeleton:

- identity, role and scoped authority;
- dated delivered information with source, freshness and uncertainty;
- request/case, examination/review, proposal, disposition and result;
- collateral/resource control, contribution and execution;
- message issue, transport, delivery and public availability; and
- causal lineage across versioned proposals, requests and messages.

The candidate Definitions add role-specific vocabulary but no conflicting
owner. A consolidated mapping will need internal profiles and intent/lifecycle
entries for coordination proposals, contributor solicitations, multi-route
support, collateral packages, operating posture and governance-gated
communication. That is an expected mapping extension, not evidence of a
contract failure.

## Carrier verdict

| Interface family | Verdict | Reason |
|---|---|---|
| identities, provenance and scoped authority | `MAPPING_EXTENSION_EXPECTED` | personal-versus-firm attribution and board/company scope need new event profiles, but no semantic contradiction is known |
| observations and participant-time limits | `MAPPING_EXTENSION_EXPECTED` | new source/freshness categories fit the shared observation family |
| replayable participant decision state | `KNOWN_FIT` | finite postures and record references follow the accepted pattern |
| domain intents | `MAPPING_EXTENSION_EXPECTED` | new role vocabularies require later registry work, explicitly deferred |
| request/proposal/message lifecycles | `MAPPING_EXTENSION_EXPECTED` | skeleton already requires these families; R2 supplies additional route distinctions |
| intent/adjudication/result authority | `KNOWN_FIT` | every R2 output remains an intent and every effect remains reducer-owned |
| resource ownership | `KNOWN_FIT` | committee, contributor and company resources remain separated |

Aggregate verdict: `NO_CONCRETE_CARRIER_COUNTEREXAMPLE /
CONSOLIDATED_MAPPING_EXTENSION_EXPECTED`.

This preflight authorizes neither a binding nor implementation. If later
mapping demonstrates an actual semantic loss that cannot be represented by an
internal profile or registry extension, it must present the concrete example
before proposing a narrow successor seam.
