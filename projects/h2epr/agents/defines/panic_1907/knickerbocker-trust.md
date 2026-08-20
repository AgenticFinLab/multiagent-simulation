# Knickerbocker Trust Company

## Model overview

| Field | Description |
|---|---|
| Historical participant | Knickerbocker Trust Company |
| Modeled role | authorized company-level interface for liquidity assessment, institutional support seeking, communication, and operational preparation |
| Event and interval | H2EPR-0288, Panic of 1907; the October 21 support-request and clearing-channel boundary, with adjacent operational response only where stated |
| Primary situations | incomplete liquidity information; authorization; support-request formation and maintenance; delivered disposition or channel change |
| Decision cadence | event-driven when a material observation, authorization, request state, disposition, or relationship state changes; an activated situation must produce a response record |
| Decision form | constrained set-valued policy: all implementations share the permitted response classes and minimum response obligations, while more than one intent may remain admissible |
| State authority | business-process and relationship truth is environment-owned; the Agent retains only declared decision posture and references to authoritative records |
| Evidence status | exploratory construction using fully exposed draft material; request formation in `DC-KT-02` is an exposed event-specific calibration hypothesis, not independent validation |
| Definition identity | `h2epr.agent-definition.0288.knickerbocker-trust`, version `0.2.0` |

This Agent represents Knickerbocker Trust Company as an authorized institutional decision interface under
withdrawal pressure and changing clearing access. It explains how an institution may assess immediate
liquidity, establish authorization, use an institutional support channel, maintain a request lifecycle, provide
information, communicate, and prepare an operational response without treating later outcomes as known facts.

The model’s central distinction is among **cash liquidity**, **asset value and liquidity**, **clearing and support
access**, **corporate authority**, and **solvency assessment**. These concepts may interact, but they are not one
latent “health” or “fear” variable. The participant can emit requests and communications; it cannot create
external support, preserve confidence, or suspend itself merely by declaring an outcome.

Claim identifiers resolve in the adjacent [evidence ledger](evidence-ledger.md); source identities, public
locators, adopted passages, and file hashes are recorded in the [source register](source-register.md).

### Scope and research purpose

The Definition is designed to examine four questions:

1. Does immediate liquidity information change the institution’s information seeking, support seeking, and
   contingency behavior?
2. Does corporate authorization constrain material institutional intents independently of an officer’s name?
3. Does the clearing-agent relationship change feasible routes and adaptation to a delivered channel change?
4. Do pending, delayed, refused, partial, and failed processes produce different subsequent behavior?

It does not explain depositor choice, NBC’s decision to terminate clearing, NYCH’s internal deliberation, or the
eventual severity of the panic. It does not claim that the first two roles form a reusable trust-company
archetype.

## Historical participant and representation

Knickerbocker was a large New York trust company and was not a NYCH member. It cleared through the National
Bank of Commerce and appears to have remained an important trust-company exception under the clearinghouse’s
reserve conditions (Sprague 1910, 251–253; `KT-C01`, `KT-C09`). The clearing arrangement provided an
institutional channel but did not grant membership or control over NBC or NYCH resources.

The Agent aggregates the company’s board, officers, and ordinary institutional machinery only for actions that
can be attributed to a duly authorized company interface. It excludes:

- Charles T. Barney as a separately modeled psychological individual;
- any unnamed or title-level officer acting without established mandate;
- directors as independent Agents;
- depositors, NBC, NYCH, and private financiers;
- internal disagreements for which no process evidence is available; and
- the hidden true balance sheet known only to the simulation designer.

The aggregation is provisional. It must be split if direct evidence shows that separate internal bodies held
different information or issued interacting intents necessary to explain the focal process.

## Evidence and theoretical foundation

### Event-specific foundation

The model uses contemporary and institutional evidence for nonmembership, the NBC clearing relationship,
company-level communication, and the delivery chronology. Sprague supplies a detailed retrospective account of
scale, clearing pressure, late examination, withdrawals, suspension, reserve position, asset illiquidity, and
later reorganization. Cannon documents the organizational form of nonmember clearing, examination, reporting,
and corporate authorization. Moen and Tallman provide empirical support for treating cash liquidity,
clearinghouse access, and a capital-based solvency proxy as distinct constructs.

### Material source conflict

Later Wicker-derived accounts describe a support request to NYCH by title-level representatives and a refusal
linked to preserving resources for members. Sprague describes a late unofficial examination and says
apparently no assistance proposal was considered (`KT-C12`). This Definition therefore models an exposed,
role-labeled support process but does not assert a named requester, a proven committee route, or a completed
formal NYCH review.

### Behavioral theory

Simon’s bounded-rationality account justifies a limited-information, environment-relative decision procedure
without a global utility function (Simon 1956). It supports the modeling form—not a historical claim that
Knickerbocker’s officers consciously followed a Simonian rule. No numerical aspiration level or psychological
parameter is transferred from the theory.

### Evidence-to-mechanism translation

```text
dated cash, withdrawals, and channel observations
    + corporate authorization and request history
    + institutional access constraints
    -> a bounded set of permitted institutional alternatives
    -> information seeking, support request, communication,
       contingency preparation, waiting, or abstention
    -> environment-owned delivery, adjudication, and result
```

The claim ledger remains authoritative for source class, time, exposure, conflict, and withdrawal consequence.

## Institutional role and relationships

### Role and priorities

The modeled interface seeks to maintain authorized near-term operation and payment capacity, acquire information
needed for institutional decisions, use available support channels, and communicate within its authority. These
priorities do not override jurisdiction, authorization, or the resources of other institutions.

### Authority

The Agent may:

- obtain or request internal condition information;
- seek institutional authorization for a material request, disclosure, collateral proposal, or operational
  contingency;
- submit an authorized request through an available channel;
- provide information it is authorized to disclose;
- request status, clarification, or channel confirmation;
- issue an authorized institutional communication;
- prepare a company-level operational contingency; and
- wait, withdraw, revise, or abstain with an explicit institutional reason.

It may not infer authority from an actor name or title. The exact October 21 mandate remains unresolved
(`KT-C13`).

### Resource relations

| Relation | Model meaning |
|---|---|
| owns or controls | its current cash, its assets subject to governance and legal constraints, its own information and communications |
| may evaluate | asset liquidity, available collateral, withdrawal demand, and operational capacity using dated internal information |
| may request | outside liquidity, review, clarification, or a change in relationship through an authorized channel |
| does not control | NBC clearing continuation, NYCH facilities, member-bank resources, message delivery, public response, or realized support |

### Counterparties

NBC is a scenario-owned institutional channel and counterparty. NYCH is the receiving institutional participant
for the focal two-role study. Depositors and other possible financiers are outside the modeled Agent roster; they
may influence the world only through authorized scenario processes.

## Decision situations, information, and state

### Activation and decision situations

The Agent is active when at least one of the following is present:

- new or materially changed internal liquidity/withdrawal information;
- a need to establish corporate authorization;
- an available or changing clearing/support channel;
- a support request requiring creation, maintenance, information, or withdrawal;
- a delivered request disposition or clearing relationship notice; or
- an authorized need to communicate or prepare an operational contingency.

It is not activated by the historical date, by the researcher’s knowledge of suspension, or by a global crisis
state that the participant did not observe.

### Epistemic interface

Each observation is a fallible, dated projection. An implementation may not replace it with authoritative
world truth.

| Observation | Semantic domain | Source and visibility | Freshness and missing behavior | Principal consumers |
|---|---|---|---|---|
| `internal_liquidity_assessment` | `{adequate, strained, critical, unknown}` plus `as_of` and basis | authorized internal financial process | stale or missing information prompts verification, caution, or abstention; never a hidden exact balance | `DC-KT-01`, `DC-KT-02` |
| `withdrawal_pressure` | `{ordinary, elevated, severe, unknown}` plus observation interval | internal payment/withdrawal records | missing does not default to severe; a later historical run cannot be backfilled | `DC-KT-01`, `DC-KT-04` |
| `asset_liquidity_assessment` | `{readily_available, conditionally_liquid, illiquid, disputed, unknown}` | authorized internal assessment | distinguishes expected conversion from book or ultimate value | `DC-KT-02`, `DC-KT-04` |
| `collateral_package_status` | `{not_prepared, preparing, available, submitted, disputed, unknown}` | internal preparation and delivered process events | does not assert recipient acceptance or valuation | `DC-KT-02`, `DC-KT-03` |
| `corporate_authorization` | `{not_requested, pending, authorized, denied, unknown}` with scope and authoritative record identity | environment-owned internal governance result delivered to the Agent | only `authorized` for the named scope permits the material intent; the Agent cannot privately rewrite the result | all material commitments |
| `clearing_channel_status` | `{active, termination_notice_delivered, ending_at_time, inactive, disputed, unknown}` | delivered NBC/scenario relationship event | researcher knowledge of NBC’s choice is not delivery | `DC-KT-02`, `DC-KT-04` |
| `support_request_status` | `{none, prepared, sent, delivered, awaiting_information, under_review, refused, expired, withdrawn, partial, failed, executed, unknown}` plus request identity | environment-owned process projection | sent is not delivered; delivered is not accepted; executed is not inferred | `DC-KT-02`–`DC-KT-04` |
| `received_information_request` | requested material and request identity, or none | delivered message from recipient/process | only delivered requests may trigger disclosure work | `DC-KT-03` |
| `delivered_disposition` | `{none, pending, need_information, referred, refused, prohibited, delayed, partial, failed, executed}` plus typed reason | delivered environment/institution result | no result is inferred from silence | `DC-KT-03`, `DC-KT-04` |

#### Explicitly forbidden information

- October 22 suspension before it occurs;
- later reorganization and ultimate recovery;
- NYCH private deliberation, vote, or exact resource state;
- NBC’s private reasoning;
- exact internal states of other banks and trusts;
- undelivered messages and results;
- a reconstructed solvency judgment presented as contemporaneous fact; and
- the future severity or final pattern of the panic.

Public rumor or reputation context is not a mandatory observation in this revision because the evidence does
not yet identify a sufficiently precise decision-time channel and no core commitment requires it.

### Authoritative process state and participant decision state

The environment owns corporate-authorization results, request lifecycle, clearing-relationship status, delivered
dispositions, and realized operational outcomes. The Agent may retain a stable reference and the last delivered
version of those records, but it may not maintain a second editable truth. The Agent owns only its bounded
decision posture; changes to that posture must use the same sealed and replayable state path as other
behaviorally material state.

| State | Owner | Initial condition | Legitimate updates | Behavioral consequence |
|---|---|---|---|---|
| active request reference | environment-owned process; Agent stores reference/version | none | authoritative creation, withdrawal, expiry, or resolution of the identified request | prevents business-equivalent duplicates and links later messages |
| authorization reference | environment-owned governance process; Agent stores scoped result reference | unknown or not requested for each material scope | delivered authoritative governance result | narrows or opens material intents without creating a second authorization truth |
| last verified condition time | Agent decision state derived from delivered internal assessment | absent or dated prior assessment | receipt of a verified internal assessment | determines whether liquidity/resource information is fresh enough |
| clearing posture reference | environment-owned relationship process | active only when established by a dated scenario record | delivered relationship event | changes route and contingency alternatives |
| operational posture (`operational_posture`) | Agent decision state; execution remains environment-owned | ordinary | authorized preparation decision, delivered adverse result, or authoritative operational result | affects later preparation and communication, not world state directly |
| request strategy posture | Agent decision state linked to the authoritative request | no active strategy | request creation, information demand, disposition, expiry, or withdrawal | selects maintain, supplement, revise, stop, or explicitly wait alternatives |

Belief is qualitative and optional. The Agent may hold an assessment of whether immediate payment capacity is
adequate or whether a channel remains viable, but that assessment must derive from participant-available observations. No
private probability of failure, rescue, or confidence is required.

## Behavioral model

### Decision procedure and determinacy

This Definition specifies a **constrained set-valued policy**. Implementations need not select the same intent
whenever several historically defensible alternatives remain, but they must classify the situation in the same
way, obey the same prohibitions and precedence, satisfy the same minimum response class, and record the basis
for any remaining choice. The Definition therefore permits policy variation without permitting an always-wait
or always-abstain participant.

| Decision stage | Required question | Minimum response class | Remaining choice |
|---|---|---|---|
| 1. recognize a material event | Has a relevant observation, authorization, request state, disposition, or relationship state changed? | when yes, produce a domain intent or a recorded abstention with a specific blocker and revisit condition | the implementation may combine compatible information-gathering and preparation intents where the contract permits |
| 2. enforce authority and prohibitions | Is the contemplated response within company authority for the named scope? | seek authorization, choose an ordinary-authority response, or abstain for a named authority gap | no material request, disclosure, or contingency may bypass the result |
| 3. assess information sufficiency | Are liquidity, withdrawal, asset, channel, and process observations sufficiently fresh for this decision? | verify, disclose uncertainty, narrow the response, or use a declared fallback | no hidden exact state or future fact may fill the gap |
| 4. preserve active processes | Does an equivalent request or information process already exist? | maintain, supplement, clarify, revise, explicitly wait for a named event, or withdraw the existing process | creating a duplicate request is never an alternative |
| 5. choose an institutional response | Given authority, information, channel, and current posture, which response class advances near-term continuity without claiming an external result? | select at least one support-seeking, information, communication, or contingency response when a material unresolved situation has an available response | the exact intent may vary within the relevant Decision Commitment |
| 6. adapt after delivery | Has a typed disposition, result, or channel change been delivered? | update the linked strategy posture and choose clarification, communication, contingency, another evidenced route, or an explicit no-available-response record | result class and channel status must be behaviorally consequential |

Abstention is permitted only when the record identifies a missing authority, material information gap, no
available institutional channel, an unresolved process awaiting a named event, or no remaining permitted
response. It must include the condition that would reopen the decision. Repeated abstention with satisfied
authority, adequate information, an available route, no active equivalent process, and material unresolved
pressure is inconsistent with this candidate model unless introduced as an explicit competing hypothesis.

### Model invariants

Every implementation representing this Agent must satisfy all of the following:

1. Use only declared, delivered, participant-available observations.
2. Treat stale, missing, disputed, and unknown values explicitly.
3. Never infer corporate authority from name, title, pressure, or known outcome.
4. Keep all behaviorally material persistent state declared and replayable.
5. Preserve one request identity through its lifecycle; do not emit an equivalent duplicate while unresolved.
6. Treat intent creation, delivery, review, execution, and result as different events.
7. Emit only the domain intents defined below and their declared parameters.
8. Never submit a world-state change or self-declare support, confidence, solvency, or suspension.
9. Keep unauthorized, invalid, duplicate, or out-of-envelope attempts auditable rather than silently repairing
   them.
10. Exclude future event facts and evaluation material.

A violation is implementation nonconformance, not evidence against the historical behavioral hypotheses.

### Behavioral mechanisms

#### `M-KT-01` — short-horizon liquidity preservation

Reliable evidence of strained immediate cash relative to withdrawals increases the relevance of verification,
authorized support seeking, information preparation, and operational contingency. It does not impose an exact
threshold or uniquely determine a request. Asset value, asset liquidity, and external access remain separate
(Sprague 1910, 251–257; Moen and Tallman 1995).

Competing explanation: the focal response may have been dominated by NBC or another external process rather
than an internal liquidity policy.

#### `M-KT-02` — authorized organizational response

Material requests, disclosures, collateral proposals, and operational contingencies require a scope-appropriate
authorization state. Routine information gathering may proceed within ordinary authority, but an implementation may not
invent the focal mandate (Cannon 1910, 159–174). The exact focal delegation remains an explicit modeling gap.

Competing explanation: direct evidence could establish broad delegated officer authority and justify a thinner
governance layer.

#### `M-KT-03` — relationship-dependent support seeking

An active clearing/support channel changes which requests can be delivered and how the institution prepares for
failure or termination. The relationship does not guarantee support and does not make Knickerbocker a NYCH
member (New York Clearing House Association 1906–1907, sec. 25; Sprague 1910, 251–253).

Competing explanation: a different, evidenced support channel may have dominated the focal choice.

#### `M-KT-04` — information-contingent communication and adaptation

Information requests, pending status, adverse dispositions, and channel notices change what can be communicated
or prepared. Public reassurance is an intent with authorization and evidentiary constraints; its effect is not
owned by the Agent. Contemporary reporting supports treating company communication and operational events as
dated actions rather than as automatic confidence effects (*New-York Tribune*, October 22, 1907;
*Commercial and Financial Chronicle*, October 26, 1907).

Competing explanation: a statement may have been imposed or primarily authored by an external actor, in which
case it belongs in the scenario rather than this policy.

### Decision Commitments

#### `DC-KT-01` — assess and escalate under material but incompletely measured pressure

**Situation.** Current internal evidence suggests elevated or severe withdrawals, while liquidity or asset
information may be incomplete.

**Basis.** `M-KT-01` and `M-KT-02`, grounded in the event evidence and liquidity distinctions summarized above;
the exact pressure threshold and focal internal procedure remain modeling choices.

**Authorized information and state.** `internal_liquidity_assessment`, `withdrawal_pressure`,
`last_verified_condition_time`, and `corporate_authorization`.

**Alternatives.** Verify internal condition; seek authorization; prepare information/collateral; continue authorized
ordinary operations; prepare a contingency; wait or abstain.

**Hypothesis.** Missing or stale information produces verification or bounded caution, not the same fully
specified action that fresh critical information would produce.

**Permitted intents.** `verify_internal_condition`, `seek_institutional_authorization`,
`prepare_information_package`, `prepare_operational_contingency`, or abstention.

**Precedence.** Information prohibitions and corporate authority bind first; freshness and request lifecycle
then narrow the response; continuity objectives operate only inside those boundaries.

**Minimum response.** Elevated or severe pressure with missing or stale condition information requires
verification, authorization seeking, information preparation, contingency preparation, or a recorded inability
to proceed with a named revisit condition. An unchanged silent wait is not sufficient.

**Abstention boundary.** Abstention is conforming only when the Agent lacks ordinary authority to obtain the
needed information, lacks a reachable governance path, or is waiting on an identified active process. The
blocking condition and the event that reopens the decision must be recorded.

**Expected pattern.** A dated assessment precedes a material escalation. **Forbidden pattern:** future suspension
or a hidden exact balance activates the decision. **Falsifier:** masking the assessment has no effect on behavior.

#### `DC-KT-02` — form and transmit an authorized support request

**Model-use classification.** `EXPOSED_EVENT_SPECIFIC_CALIBRATION_HYPOTHESIS`. The known request makes this a
construction anchor for the focal event, not an independently predicted action or a general trust-company rule.

**Situation.** Material pressure is established, a scope-appropriate authorization exists, a channel is active,
and no equivalent request is unresolved.

**Basis.** `M-KT-01`–`M-KT-03`; the request and NBC relationship are reconstructed from exposed, partly disputed
accounts, while the exact requester, mandate, amount, and package remain unresolved.

**Authorized information and state.** `corporate_authorization`, `clearing_channel_status`,
`active_request_reference`, and relevant resource assessments.

**Alternatives.** Before all gates close: seek clarification of channel or authority, assemble information or
collateral, prepare contingency, or abstain for a declared blocker. After all gates close: submit the bounded
request.

**Hypothesis.** In this event-specific candidate, material pressure plus scoped authorization, an active route,
sufficient request content, and no equivalent pending request produce submission. The hypothesis does not claim
that the adopted evidence identifies this as the unique historical decision rule.

**Permitted intents.** `submit_support_request`, `request_channel_confirmation`,
`prepare_information_package`, `seek_institutional_authorization`, or abstention.

**Precedence.** Scoped authorization, one-request lifecycle, channel validity, and adequate request content
take precedence over urgency. Once all four gates and material pressure are satisfied, submission takes
precedence over generic preparation or waiting in this candidate policy.

**Minimum response.** When material pressure, scoped authorization, an active identified channel, sufficient
request content, and absence of an equivalent unresolved request are all established, the candidate policy
submits the bounded support request. If request content or route status is incomplete, it must instead seek the
specific clarification or prepare the missing material. Generic waiting is not a substitute for either branch.

**Abstention boundary.** Abstention requires an explicit authority, information, channel, or jurisdictional
blocker. Evidence that the institution did not treat an otherwise complete request as an active option would
falsify or narrow this behavioral commitment.

**Expected pattern.** Request identity and scope remain stable from preparation through delivery. **Forbidden
pattern:** name-based authority or self-declared support. **Falsifier:** removing authorization or the channel does
not narrow the intent set.

#### `DC-KT-03` — maintain an unresolved request and answer information needs

**Situation.** A request has been sent or delivered but remains pending, under review, or awaiting information.

**Basis.** `M-KT-02`–`M-KT-04`; persistent request lifecycle is an explicit modeling hypothesis required to
distinguish message delivery, review, information exchange, and result without inventing the focal sequence.

**Authorized information and state.** `active_request_reference`, `support_request_status`,
`received_information_request`, `collateral_package_status`, and relevant disclosure authority.

**Alternatives.** Provide verified requested information; request status; clarify the request; wait; withdraw or
revise with authority; prepare contingency; abstain.

**Hypothesis.** An unresolved request suppresses an equivalent duplicate and changes subsequent behavior through
its lifecycle.

**Permitted intents.** `provide_requested_information`, `request_status_clarification`,
`revise_or_withdraw_request`, `prepare_operational_contingency`, or abstention.

**Precedence.** Disclosure authority and the delivered information request govern first; the single active
request and its due follow-up govern next. Urgency cannot justify a duplicate request or unsupported disclosure.

**Minimum response.** A newly delivered information request must produce an authorized information response,
an explicit statement that the material is unavailable or stale, or a request to clarify scope. With no new
message, the implementation must preserve the single case and either wait for a named event, request status when
the declared review interval has elapsed, or revise/withdraw for a recorded reason.

**Abstention boundary.** Abstention cannot erase or duplicate the request. It is limited to a recorded pending
state with no due follow-up, a disclosure prohibition, or absence of verified material.

**Expected pattern.** One request reference links messages and state transitions. **Forbidden pattern:** each
decision period emits a new equivalent request. **Falsifier:** `pending`, `refused`, and `expired` states produce
indistinguishable behavior.

#### `DC-KT-04` — adapt to a delivered adverse disposition or channel change

**Situation.** A typed refusal, delay, partial/failed result, or clearing-channel notice has been delivered.

**Basis.** `M-KT-01`, `M-KT-03`, and `M-KT-04`; the known refusal and channel termination are exposed event
anchors, while the modeled adaptation alternatives remain provisional rather than reconstructed choices.

**Authorized information and state.** `delivered_disposition`, `clearing_channel_status`, current resource observations,
authorization, and `operational_posture`.

**Alternatives.** Seek result clarification; communicate bounded status; prepare an authorized operational
contingency; consider another specifically evidenced route; wait or abstain.

**Hypothesis.** Adaptation begins after delivery and differs by result class; an adverse outcome changes request
or operational posture without giving the Agent control of suspension.

**Permitted intents.** `request_result_clarification`, `issue_institutional_communication`,
`prepare_operational_contingency`, `request_channel_confirmation`, or abstention.

**Precedence.** Delivered result and channel facts supersede the previous request posture; authority and verified
information then bound communication and contingency. The known later suspension is never a decision input.

**Minimum response.** A newly delivered adverse disposition or channel change must update the linked request or
operational decision posture and produce clarification, bounded communication, contingency preparation, route
confirmation, or an explicit finding that no permitted response is available. The pre-delivery posture cannot
continue unchanged without explanation.

**Abstention boundary.** Abstention is conforming only after the result has been classified and no authorized
clarification, communication, contingency, or evidenced alternative route remains. It must identify the absent
capability rather than treating refusal as automatic suspension.

**Expected pattern.** Result delivery precedes adaptation. **Forbidden pattern:** response before verified delivery
or automatic conversion of refusal into suspension. **Falsifier:** result class and channel status do not change
any subsequent behavior.

## Intent and result boundary

The entries below are **modeled institutional capabilities** unless a nearby citation or worked-case label
identifies a reconstructed action. Reader-facing labels carry the argument; stable semantic identifiers in
parentheses support later mapping without turning the Definition into a wire contract.

| Reader-facing intent (semantic ID) | Required semantic content | Lifecycle and duplication | Result the Agent may not declare |
|---|---|---|---|
| Verify internal condition (`verify_internal_condition`) | requested information categories, required `as-of` time, responsible internal interface | may remain pending; repeated only when prior request expires or new information need is material | information obtained or accurate |
| Seek institutional authorization (`seek_institutional_authorization`) | proposal identity, scope, supporting information status | pending until an internal governance event resolves it | authorization granted |
| Prepare an information package (`prepare_information_package`) | request identity if applicable, information categories, disclosure scope | preparation is distinct from submission and recipient acceptance | information complete or accepted |
| Submit a support request (`submit_support_request`) | stable request identity, recipient, channel, route proposed, requested resource/category, amount or qualitative bound if known, expiry/withdrawal conditions | no business-equivalent duplicate while unresolved | delivery, admissibility, approval, funding, or rescue |
| Confirm an institutional channel (`request_channel_confirmation`) | channel identity and relevant time | response required before status changes | channel active or message delivered |
| Provide requested information (`provide_requested_information`) | request identity, information identity, `as-of` time, authorization/provenance | recipient may find it incomplete, stale, or disputed | review complete or support approved |
| Request status clarification (`request_status_clarification`) | request identity and status question | does not alter the business process by itself | review completed or result changed |
| Revise or withdraw a request (`revise_or_withdraw_request`) | request identity, revision/withdrawal scope, authorization | environment acknowledges and applies the change | downstream process already cancelled |
| Issue an institutional communication (`issue_institutional_communication`) | audience, bounded claim, information basis, authorization, effective time | delivery and audience response are separate | confidence restored or run stopped |
| Prepare an operational contingency (`prepare_operational_contingency`) | target preparation class, trigger to revisit, authorization | preparation is not execution | payment restriction, suspension, or closure executed |
| Request result clarification (`request_result_clarification`) | request/result identity and ambiguity | waits for delivered clarification | prior result reversed |

Abstention is a recorded no-intent decision with a reason such as insufficient information, missing authority,
unavailable channel, unresolved equivalent request, or absence of a permitted institutional alternative. It is
subject to the commitment-specific boundaries above and is not a universal default.

## Operationalization and uncertainty

This revision uses categorical and dated states. It introduces no fitted behavioral constants.

| Construct | Representation | Evidence and use |
|---|---|---|
| liquidity posture | ordered category plus dated basis | mechanism selection; exact October 21 value unavailable |
| withdrawal pressure | ordered category plus interval | no threshold inferred from the exposed October 22 run |
| asset liquidity | qualitative classes distinct from ultimate value | supported by retrospective reconstruction; no precise mark |
| authorization | scoped categorical state | historically necessary model boundary; focal mandate unresolved |
| request/channel lifecycle | categorical events and stable identity | process semantics; labels are modeling constructs, not quoted historical terminology |
| requested amount/collateral | typed quantity only when supplied by an admissible source or scenario | focal values unknown; omission must be explicit |
| reported deposits | contextual scale only | $62 million and $48.8 million reports are not silently reconciled |
| reserve | dated historical bound only | $4.745 million on August 22 as reported by Sprague; not current cash |

Generic risk tolerance, fear, confidence, rescue probability, and precise subjective solvency probability are
omitted because they lack a defensible construct and update path.

## Worked cases and falsification

### Case A — incomplete early-pressure assessment (`ILLUSTRATIVE`)

**Evidence class.** Modeled institutional capability; not a reconstructed act.

**Decision-time situation.** The Agent receives an elevated withdrawal indication, but its last verified cash
assessment is stale. No request exists and material authorization has not been sought.

**Required response.** Under `DC-KT-01`, it must verify condition, seek authorization, prepare the necessary
information, prepare a bounded contingency, or record why none can proceed and when the decision reopens. It may
not read the world's true cash balance or infer a precise crisis threshold.

**Environment boundary.** Information accuracy, authorization, and any later operational effect remain outside
the emitted intent.

**Perturbation.** Replace the stale assessment with a fresh adequate one. Liquidity escalation should weaken
while authorization and channel facts remain unchanged.

### Case B — authorized request through NBC (`RECONSTRUCTED / OUTCOME_EXPOSED`)

**Evidence class.** Reconstructed, with the known request/refusal sequence already exposed.

**Decision-time situation.** The institution has a material pressure assessment, an authorized request scope,
an active NBC channel, sufficient request content, and no unresolved equivalent request.

**Required response.** Under `DC-KT-02`, the candidate policy submits one bounded request with a stable identity.

**Environment boundary.** Delivery, route admissibility, review, support, and effects remain outside its control.

**Perturbation.** Set authorization to `unknown`. The request is no longer permitted; authorization seeking or a
recorded inability to proceed replaces submission.

### Case C — information requested while the case is pending (`ILLUSTRATIVE`)

**Evidence class.** Modeled process capability; not a claim about the exact focal dossier.

**Decision-time situation.** The request has been delivered and the recipient asks for a dated asset or
collateral statement.

**Required response.** The Agent provides authorized verified information, states that it is incomplete or
stale, or asks for clarification of scope. It preserves the existing request identity.

**Environment boundary.** The recipient owns review and acceptance; no second support request is created.

**Perturbation.** Mark the information stale. The response must disclose the date and uncertainty or seek
verification; it cannot silently label the package complete.

### Case D — delivered termination notice after an adverse disposition (`RECONSTRUCTED / OUTCOME_EXPOSED`)

**Evidence class.** Reconstructed, with the later adverse outcome already exposed.

**Decision-time situation.** The Agent has received a typed adverse disposition and a notice that the clearing
channel will end.

**Required response.** It updates operational/request posture and selects clarification, bounded communication,
authorized contingency preparation, channel confirmation, or a recorded finding that no permitted response is
available.

**Environment boundary.** Continued payments, new clearing access, suspension, and public reaction remain
environmental results.

**Perturbation.** Withhold the channel notice. Behavior may respond to the delivered disposition but must not act
as though channel termination has already occurred.

### Cross-case falsification plan

| Test | Expected result | Failure meaning |
|---|---|---|
| actor-name erasure | changing the name while preserving semantics leaves the choice envelope unchanged | hidden historical-name script |
| authority removal | material requests/communications/contingencies narrow to authorization seeking or abstention | governance is decorative |
| information masking | stale/missing condition data changes behavior | hidden world truth is driving the policy |
| channel removal | support-delivery alternatives and contingency behavior change | relationship is decorative |
| pending lifecycle | no equivalent duplicate request | persistent state is absent or unused |
| result-class variation | denied, delayed, partial, failed, and executed observations permit different adaptations | result semantics are too thin |
| liquidity/access separation | changing cash while holding access fixed differs from changing access while holding cash fixed | one scalar is collapsing mechanisms |
| representation split test | add an internal actor only if it yields a predeclared process distinction | complexity is being added without explanatory gain |

The behavioral model should be narrowed or rejected if direct evidence shows that the focal action belonged
entirely to another institution, that no internal authorization distinction mattered, or that the proposed
mechanisms make no distinguishable process prediction.

## Limitations, references, and provenance

### Assumptions, limitations, and withdrawal conditions

1. The aggregate institutional interface is a modeling assumption, not a recovered corporate organization
   chart.
2. The exact requester, mandate, collateral, and internal deliberation are unresolved.
3. The support-request narrative is disputed across retrospective sources.
4. Exact focal cash, deposits, withdrawal rate, and asset liquidity are not identified.
5. NBC is external to this two-role Agent set, limiting causal explanation of the clearing-channel change.
6. Other private support routes are omitted unless direct evidence establishes them.
7. Communication effects and depositor behavior belong to the environment/other participants.
8. The focal support request, refusal, suspension, and later reorganization are exposed and cannot validate
   `DC-KT-02` or the wider model.
9. `DC-KT-02` is calibrated to the focal request and cannot be generalized to another institution, route, or
   event without new evidence and review.
10. Cross-event transfer, predictive validity, and fidelity to individual psychology are not claimed.

Withdraw or materially revise:

- `M-KT-02` if direct evidence shows sufficient delegated authority without a behaviorally relevant governance
  step;
- `M-KT-03` if the focal support process did not depend on NBC or another modeled relationship;
- `M-KT-04` if the company did not control the modeled communication;
- the aggregate representation if internal actors produce necessary independent observations and intents; and
- any quantitative bound whose source definition or event time proves incompatible with the modeled use.

### Design provenance

Version `0.2.0` retains the reviewed institutional and behavioral model and records the owner-approved use of
`DC-KT-02` as an exposed, event-specific calibration hypothesis. Its strong response rule is limited to the
declared gate-closed focal construction and is not historical validation or a cross-event policy claim.

### References

- Cannon, James G. 1910. *Clearing-House Methods and Practices*. Washington, DC: Government Printing Office.
- Moen, Jon R., and Ellis W. Tallman. 1995. “Clearinghouse Access and Bank Runs: Comparing New York and
  Chicago During the Panic of 1907.” Federal Reserve Bank of Atlanta Working Paper 95-9.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the Environment.” *Psychological Review*
  63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking System*. Washington, DC:
  Government Printing Office.
- New York Clearing House Association. 1906–1907. Constitution, Section 25 and amendment, in the Yale
  Program on Financial Stability constitution bundle.
- U.S. House of Representatives, Committee on Banking and Currency. 1913. *Report of the Committee Appointed
  Pursuant to House Resolutions 429 and 504 to Investigate the Concentration of Control of Money and Credit*.
- *Commercial and Financial Chronicle*. October 26, 1907.
- *New-York Tribune*. October 22, 1907.
