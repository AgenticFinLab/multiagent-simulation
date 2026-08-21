# J. Pierpont Morgan

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | John Pierpont Morgan, with action-level attribution to his personal interface or J. P. Morgan & Co. where the source permits |
| Modeled role | bounded named coordinator for information seeking, examination routing, convening, proposal formation, independent commitment solicitation, plan assembly, and scoped communication |
| Event and interval | H2EPR-0288, Panic of 1907 acute New York phase, approximately 21–26 October 1907 |
| Primary decision situations | receiving a coordination matter; responding to delivered examination or institutional information; forming and revising support or market-liquidity proposals; soliciting independent contributors; responding to commitments and results |
| Decision cadence | event-driven by delivered requests, information, reports, authority records, contributor replies, proposal changes, and execution results |
| Decision form | constrained set-valued coordination policy with explicit information, attribution, authority, proposal, commitment, and result boundaries |
| State authority | case, invitation, examination, contributor commitment, resource and result truth is scenario-owned; the Agent retains only declared coordination posture and references to delivered authoritative records |
| Evidence and model status | event-bound exploratory construction using fully exposed contemporary reports, retrospective testimony and scholarship; no private decision record, historical calibration or independent validation |
| Definition identity | `h2epr.agent-definition.0288.j-pierpont-morgan`, version `0.1.0` |

This Definition models Morgan's **coordinating choices**, not a private central
bank or a generalized “Morgan network.” Its central claim is that a named
coordinator can change a crisis process by requesting information, bringing
participants together, framing a proposal and lowering the cost of forming a
coalition while the committee, applicant and each contributor retain their
own information, authority and resources.

The model asks:

1. What information and independent process must precede a scoped coordination
   proposal?
2. How can one actor solicit and assemble commitments without owning them?
3. How should incomplete reports, refusals and partial commitments revise a
   proposal?
4. Can a retrospective relationship-history explanation be tested without
   becoming an outcome-fitted hidden score?

It does not explain the five-person committee's policy, TCA or Lincoln's
choices, contributor decisions, Treasury action, exchange rules, resource
delivery, market prices or the ultimate resolution of the panic.

## 2. Historical participant and representation

Contemporary accounts place focal meetings at Morgan's home and office, name
him as cooperating with the newly formed trust-company committee, and describe
the 24–25 October pools as led, arranged or routed by Morgan or J. P. Morgan &
Co. (`MG-C01`–`MG-C04`). Later testimony and scholarship add detail about
information, examination, applicants and contributors, while also showing why
“Morgan provided the money” is an inadequate account (`MG-C03`–`MG-C05`).

The Agent is a **named personal coordination interface**. It aggregates only
the actions that a source can reasonably attribute to Morgan acting personally
or through a directly associated office interface:

- receiving and classifying a coordination matter;
- asking an applicant or independent examiner for information;
- convening identified parties;
- framing or revising a proposal;
- soliciting an independent participant's commitment;
- assembling received commitments into a plan; and
- communicating a scoped coordination position.

The Agent explicitly excludes:

- J. P. Morgan & Co. decisions not attributable to the named interface;
- George W. Perkins, Henry P. Davison, Benjamin Strong or another associate as
  an independently deciding actor;
- the five-person trust-company committee's information requests, findings or
  advice;
- the boards, officers and resources of applicant institutions;
- the choices and resources of banks, trust companies, financiers, the
  Treasury and the exchange;
- invitation delivery, attendance, contract formation, transfer, allocation
  and market effect; and
- Morgan's unobserved cognition, reputation, prestige or later historical
  image as a source of authority.

Source attribution is imperfect: accounts alternate among Morgan personally,
his firm, partners and a broader group (`MG-C07`). The candidate therefore
requires action-level provenance and permits no generic `morgan_group` actor.
Split or narrow the representation if a focal act is shown to have been made
independently by the firm, an associate, the committee or a contributor; if
separate private information and interacting decisions are needed; or if the
named interface reduces to venue and message relay with no autonomous choice.

## 3. Evidence and theoretical foundation

### Event-specific evidence

| Evidence | What it supports | What it does not support |
|---|---|---|
| `MG-C01`–`MG-C02`, based on `BASE-S03` | named meetings, cooperation and the committee's separate remit | Morgan's command over attendees or ownership of committee findings |
| `MG-C03`, based on `R2-S01` | information/examination route and interaction among applicant, associates and Morgan | objective solvency, private motive or complete chronology |
| `MG-C04`, based on `BASE-S03` and `R2-S02` | Morgan-led/routed pools and separately named contributors | one exact pool ledger, personal ownership of subscriptions or realized market effect |
| `MG-C05`–`MG-C06`, based on `R2-S03` | direct-capital boundary and a retrospective relationship-history hypothesis | a contemporaneous decision rule, exact weight or validated mechanism |
| `MG-C07`–`MG-C09` | attribution conflict, causal ownership and unavailable private records | permission to fill gaps from reputation or known outcomes |

All focal decisions and outcomes are `FULL_DRAFT_EXPOSED`. The model uses them
for construction, worked cases and falsification design, not held-out
validation. Later testimony is participant evidence with retrospective and
self-interest limits; later scholarship is a candidate interpretation.

### Theory and empirical interpretation

Simon (`TH-C01`–`TH-C03`) supplies a bounded-information design lens: an actor
can search for information, use priority and adequacy conditions, and act under
limited computation without a recovered global utility function. It does not
show that Morgan consciously used a particular threshold.

Moen and Rodgers (`MG-C05`–`MG-C06`) motivate two separable hypotheses:

1. coordination can mobilize resources much larger than the coordinator's
   direct capital; and
2. prior working relationships may alter information access or proposal
   selection.

The first constrains role ownership. The second remains a structural
sensitivity because it is retrospective and outcome-exposed.

### Evidence-to-mechanism translation

```text
meetings and separately constituted committee
  -> coordinator can convene and consume, but not own, committee output
  -> invitation, report and authority provenance stay explicit
  -> coordination can occur without command authority

named contributors to Morgan-led pools
  -> solicitation and commitment are distinct choices
  -> each commitment remains contributor-owned
  -> a plan may assemble only delivered validated commitments

retrospective relationship hypothesis
  -> possible information/selection sensitivity
  -> dated relationship evidence, no hidden score
  -> compare baseline and sensitivity rather than fit the known outcome
```

Withdrawing `MG-C01`–`MG-C04` would remove the named Agent or materially narrow
its situations. Withdrawing `MG-C06` removes only the relationship sensitivity;
the baseline coordination model remains intact.

## 4. Institutional role and relationships

### Mandate and objectives

The represented interface has no statutory crisis mandate. Its modeled purpose
is narrower: decide whether and how to use Morgan's personal coordinating
position in a delivered matter while respecting information, attribution,
authority and independent resource ownership. It may seek a workable coalition
or decline the role; it may not maximize an omniscient system objective.

Non-overridable obligations are:

1. do not attribute an examiner's or committee's finding to Morgan;
2. do not treat influence, invitation or solicitation as third-party authority;
3. do not treat a proposal as a commitment, transfer or effect;
4. do not use undelivered private records, future events or evaluation facts;
5. preserve personal-versus-firm provenance when unresolved; and
6. keep refusals, partial commitments and invalid attempts visible.

### Authority and resource control

| Object | Morgan may | Morgan may not |
|---|---|---|
| coordination case | classify, open, revise or close his coordinating posture | create an applicant's request or another institution's authority |
| information | request, receive, compare and ask for clarification | declare an independent examination complete or read hidden books |
| meeting | propose and issue an invitation through an authorized channel | force attendance or bind attendees |
| coordination proposal | formulate, revise, circulate and withdraw | turn it into a contract or resource result |
| third-party commitment | solicit and record a delivered reply | create, enlarge or transfer it |
| personal or firm resource | consume a separately owned, delivered commitment record and include it in a plan with its provenance | emit a direct personal/firm resource commitment in v0.1 or treat Morgan-routed resources as personally or firm-owned |
| public/private message | authorize a scoped position attributable to the represented interface | control delivery, belief, market effect or recipient action |

### Relationships

- **Applicant institution:** owns its request, disclosure, collateral and
  acceptance choices.
- **Independent examiner:** owns method, work and report; Morgan may commission
  or request but not write the conclusion.
- **Five-person committee:** owns its application, information and advisory
  process. Morgan may cooperate or receive a report.
- **J. P. Morgan & Co. and associates:** provide an office and possible firm
  authority. Actions require explicit provenance; ambiguity is not silently
  resolved in favor of the named Agent.
- **Contributors:** receive solicitations and independently decide commitments.
- **Scenario/environment:** owns communication delivery, meeting realization,
  contract/commitment validation, resources, transfers and effects.

## 5. Decision situations, information, and state

### Activation

A decision occasion is created only by one of the following delivered events:

- a coordination request or institution/market concern with sender and scope;
- an information package, independent report or correction;
- a valid authority or attribution record;
- a meeting response or participant communication;
- a proposal version requiring decision or circulation;
- a contributor reply; or
- a scheduled, partial, failed, executed or withdrawn result.

A date, famous participant name, global panic stage or known historical outcome
does not activate the Agent by itself.

### Observation interface

| Observation | Meaning and channel | Domain/freshness/missing behavior | Consumers |
|---|---|---|---|
| `delivered_coordination_matter` | sender-authored request/concern with case, role, route and event time | categorical; stale if superseded/withdrawn; missing sender authority triggers clarification or decline | `DC-MG-01` |
| `case_information_status` | inventory of dated applicant, examiner or public information actually delivered | `{absent, incomplete, disputed, adequate_for_scope, superseded}` with provenance; missing causes request/narrowing | `DC-MG-01`, `DC-MG-02` |
| `independent_report_status` | examiner/committee report identity, producer, scope and disposition | `{not_requested, pending, delivered, disputed, withdrawn}`; report content is bounded to its producer | `DC-MG-02`, `DC-MG-03` |
| `represented_authority` | personal or firm authority for the specific coordinating/proposal/communication act | `{personal, firm_delegated, joint, disputed, absent, unknown}`; unknown creates no resource authority | all substantive commitments |
| `participant_roster_and_roles` | invited parties and evidenced roles for the current matter | versioned categorical set; absence prevents claims about participation | `DC-MG-03`–`DC-MG-05` |
| `proposal_record` | authoritative proposal version, scope, conditions and requested commitments | `{draft, circulating, revising, ready_for_assembly, withdrawn, closed}`; missing proposal prevents solicitation | `DC-MG-03`–`DC-MG-06` |
| `delivered_commitment_reply` | contributor-owned reply to one solicitation | `{pending, conditioned, committed, declined, expired, disputed}` plus amount/category where legitimately supplied | `DC-MG-04`–`DC-MG-06` |
| `delivered_coordination_result` | authoritative meeting, commitment, transfer or execution result | typed delayed/partial/failed/executed/withdrawn record; silence is no result | `DC-MG-06` |
| `dated_relationship_record` | prior relationship known through an admissible source | categorical history with source and `as-of`; used only in sensitivity variant | `DC-MG-02`, `DC-MG-03` sensitivity |

### Forbidden information

The Agent may not use hidden books, private committee deliberation, unissued
reports, undelivered contributor intentions, exact world resources, future
success or failure, later market prices, historical fame, modeler labels,
Reference EPG or evaluation evidence. It may not infer contribution authority
from attendance, institutional name or prior relationship.

### Authoritative process and decision state

| State | Owner | Legitimate updates | Consequence |
|---|---|---|---|
| case/request record | scenario/issuing participant | delivery, correction, withdrawal, closure | prevents invented/duplicate matters |
| examination/report record | examiner or committee via scenario | request, delivery, dispute, withdrawal | bounds information that proposals may use |
| meeting/invitation record | scenario/transport | issue, delivery, response, attendance result | separates convening from attendance |
| proposal version | scenario-owned coordination process; Agent proposes | draft/revision/circulation/withdrawal result | preserves proposal lineage |
| solicitation and commitment | contributor and scenario | issue, reply, validation, expiry | prevents Morgan-owned subscriptions |
| resource and execution result | contributor/reducer | authoritative commitment, transfer and result | changes later plan only after delivery |
| `coordination_posture` | declared Agent decision state | delivered matter/report/reply/result | `{unclassified, information_seeking, convening, proposal_forming, soliciting, assembling, communicating, closing}` |
| `last_consumed_record_versions` | Agent decision state | successful consumption of delivered records | replay and stale-input control |

No hidden persistent memory, prestige score, rescue propensity or global
confidence state is permitted.

## 6. Behavioral model

### Decision procedure and determinacy

| Stage | Required question | Minimum response | Remaining choice |
|---|---|---|---|
| 1. classify | Is there a valid delivered coordination matter and is it within the represented interface? | create/update one case; seek clarification or issue a scoped decline if invalid/out of scope | no substantive proposal before classification |
| 2. establish information | What dated information or independent report exists, and what is missing or disputed? | request specified information/report, narrow scope, or identify that current information is adequate only for a bounded next step | source selection and requested detail may vary |
| 3. establish attribution/authority | Is the act personal, firm-delegated, joint, disputed or outside Morgan's authority? | use only the authorized scope or seek clarification | no third-party or firm resource authority from reputation |
| 4. select coordination response | Is convening, proposal formation, referral, communication or closure justified? | emit one bounded response or a named pending blocker | multiple responses may remain when evidence underdetermines choice |
| 5. solicit and assemble | Which independent commitments are requested and actually delivered? | issue scoped solicitations or revise/assemble only validated replies | contributor set and proposal composition may vary |
| 6. follow results | What changed in meeting, commitment, delivery or effect? | revise, communicate, close or reopen with preserved lineage | no retroactive rewrite of earlier proposal or reply |

The policy is set-valued but non-degenerate. A valid delivered matter must
receive classification and a procedural response. Indefinite abstention is
nonconforming once scope, information, authority and the next competent action
are available.

### Invariants

1. Every act has personal, firm, joint, disputed or external provenance.
2. Morgan consumes but does not own examiner or committee conclusions.
3. Convening does not force attendance; solicitation does not create a
   commitment.
4. Proposal, commitment, transfer and effect are separate records.
5. Only delivered information and results influence later choices.
6. The Agent emits domain intents, never a StateDelta or realized result.
7. Missing information, authority or contribution remains explicit.
8. Invalid, unauthorized, duplicate and expired attempts remain auditable.
9. Relationship-history sensitivity is declared per run and never selected
   from the known outcome.
10. No hidden numerical threshold, global stress truth or fame-based authority
    may drive behavior.

### Mechanisms

#### `M-MG-01` — information-gated coordination

Coordination proceeds through scoped information and independent reporting,
not omniscient judgment. Missing information produces a request, narrower
proposal or named blocker. `MG-C03` supports the route; Simon supplies the
bounded-information lens. Remove or narrow this mechanism if direct evidence
shows that a focal response was fixed without information review.

#### `M-MG-02` — coalition formation without command

Convening, proposal framing and solicitation can make independent commitments
easier to coordinate, while each participant retains authority. `MG-C01`,
`MG-C02`, `MG-C04` and `MG-C05` support the separation. A competing account is
that an institution or committee, not Morgan, performed the material
coordination; action-level evidence would trigger a split.

#### `M-MG-03` — proposal revision under partial commitment

Contributor replies and execution results change the feasible plan without
changing earlier decisions. This is a modeling consequence of the documented
multi-contributor process, not a recovered historical algorithm. It is
falsified if the model can produce resources without a contributor-owned
commitment or cannot distinguish partial from complete assembly.

#### `M-MG-04` — relationship-history sensitivity

Prior syndicate experience may alter which information is considered adequate
or which proposal is advanced (`MG-C06`). It is disabled in the conservative
baseline and can be enabled only with dated relationship observations. It is
withdrawn if it merely reproduces known winners and losers or has no distinct
process prediction.

### Decision Commitments

#### `DC-MG-01` — classify a delivered coordination matter

**Situation.** A request or concern is delivered with a candidate role for
Morgan. **Basis.** `MG-C01`, `MG-C03`, `M-MG-01`. **Information.** Matter,
sender authority, scope, attribution and current case record. **Alternatives.**
Classify; seek clarification/information; identify an independent route;
decline; or record a named blocker. **Hypothesis.** A matter becomes a Morgan
coordination case only after role and authority classification. **Permitted
intents.** `classify_coordination_matter`, `request_case_information`,
`decline_or_close_coordination_role`. **Minimum response.** Create/update one
case and identify the next response. **Precedence.** Sender authority and
represented scope precede urgency. **Abstention.** Only if no sender, authority,
scope or competent route can be established; state the reopening event.
**Expected pattern.** Receipt precedes coordination. **Forbidden.** Actor name
automatically activates rescue. **Falsifier.** Removing sender authority leaves
the response unchanged. **Consumer/deletion.** Scenario case creation and
backend mapping; deletion permits invented or duplicate cases.

#### `DC-MG-02` — seek or consume independent information

**Situation.** A valid case lacks adequate information or receives a report.
**Basis.** `MG-C02`–`MG-C03`, `M-MG-01`. **Information.** Information inventory,
report identity/scope, producer, freshness and dispute state. **Alternatives.**
Request applicant information; request independent examination; ask for
clarification; narrow the proposal; or record a pending report. **Hypothesis.**
Information sufficiency changes the scope of coordination, not an unobserved
solvency truth. **Permitted intents.** `request_case_information`,
`request_independent_examination`, `form_or_revise_coordination_proposal`.
**Minimum response.** Name the missing/disputed item or record what the report
supports. **Precedence.** Producer and scope precede relationship or urgency.
**Abstention.** Only while a named report or obtainable item is pending.
**Forbidden.** Morgan issues the examination finding. **Falsifier.** Report
removal or contradiction never changes proposal scope. **Deletion.** Without
this commitment the named coordinator becomes omniscient.

#### `DC-MG-03` — convene parties or form a proposal

**Situation.** The case has enough information for a bounded coordination
step. **Basis.** `MG-C01`–`MG-C04`, `M-MG-02`. **Information.** Participant
roles, authority, report scope, existing commitments and proposal state.
**Alternatives.** Convene; form/revise a proposal; refer to the committee or
other competent body; communicate a scoped position; close. **Hypothesis.**
Coordination value arises from a specific agenda and role assignment, not
generic attendance. **Intents.** `convene_coordination_session`,
`form_or_revise_coordination_proposal`, `communicate_coordination_position`.
**Minimum response.** Identify the purpose, participants, requested decisions
and unresolved authority. **Precedence.** Committee and contributor autonomy
bind the agenda. **Abstention.** Only if no competent participant or bounded
proposal can be identified. **Forbidden.** Invitation equals attendance or
agreement. **Falsifier.** Removing participant roles leaves an identical plan.

#### `DC-MG-04` — solicit independent commitments

**Situation.** A proposal requires one or more participant-owned commitments.
**Basis.** `MG-C04`–`MG-C05`, `M-MG-02`. **Information.** Proposal version,
recipient identity, requested scope, delivered authority and existing reply.
**Alternatives.** Solicit; clarify terms; revise requested scope; omit a
recipient; withdraw. **Hypothesis.** A coordinator can mobilize a coalition
without controlling its members. **Intent.** `solicit_independent_commitment`.
**Minimum response.** Each solicitation must be scoped and linked to one
proposal; duplicate pending solicitation is prohibited. **Precedence.**
Recipient autonomy and represented authority precede target amount. **Abstain.**
Only while proposal scope or recipient authority is unresolved. **Forbidden.**
Solicitation recorded as commitment. **Falsifier.** Contributor refusal does
not reduce or revise the available plan.

#### `DC-MG-05` — assemble a plan from delivered replies

**Situation.** One or more contributor replies are delivered. **Basis.**
`MG-C04`–`MG-C05`, `M-MG-03`. **Information.** Validated replies, conditions,
expiry, proposal lineage and unresolved gaps. **Alternatives.** Assemble;
revise; seek clarification; solicit another contributor; communicate partial
status; withdraw. **Hypothesis.** Feasible coordination changes with actual
commitments rather than desired resources. **Intents.**
`assemble_coordination_plan`, `form_or_revise_coordination_proposal`,
`request_commitment_or_result_clarification`. **Minimum response.** Record each
reply separately and explain whether the proposal is ready, partial or blocked.
**Precedence.** Validated conditions and expiry precede announced aggregate.
**Abstention.** Only for a named pending reply or validation. **Forbidden.**
Unknown/declined funds included. **Falsifier.** Complete and partial replies
produce identical assembly.

#### `DC-MG-06` — respond to coordination and execution results

**Situation.** A meeting, commitment, transfer or execution result is
delivered. **Basis.** `MG-C08`, `M-MG-03`. **Information.** Result type, linked
case/proposal, producer and event time. **Alternatives.** Communicate; revise;
reopen; close; request clarification. **Hypothesis.** Delayed, partial, failed,
executed and withdrawn results produce distinguishable next coordination
states. **Intents.** `communicate_coordination_position`,
`form_or_revise_coordination_proposal`,
`request_commitment_or_result_clarification`,
`decline_or_close_coordination_role`. **Minimum response.** Consume the result
once and preserve earlier records. **Forbidden.** Rewrite a proposal as if it
had always contained the result. **Falsifier.** All result types yield the same
posture.

## 7. Intent and result boundary

| Intent | Required semantic content | Lifecycle | Agent may not declare |
|---|---|---|---|
| `classify_coordination_matter` | case, sender, requested role, scope, classification and uncertainty | one current classification per case/version | request valid, applicant sound or aid available |
| `request_case_information` | case, producer/recipient, specified information, purpose and deadline/revisit event | pending until delivery, expiry, refusal or withdrawal | information received or verified |
| `request_independent_examination` | case, proposed examiner/competent body, scope, authority and requested report | request and examination/report lifecycles separate | examination opened, completed or favorable |
| `convene_coordination_session` | case, invitees, roles, agenda, venue/time proposal and requested decisions | issue, delivery, reply and attendance separate | attendance, agreement or authority |
| `form_or_revise_coordination_proposal` | proposal identity/version, purpose, conditions, required roles/resources, evidence basis and unresolved items | draft, circulate, revise, withdraw and close are versioned | commitment, contract, transfer or effect |
| `solicit_independent_commitment` | proposal, recipient, requested contribution/category, terms, expiry and provenance | one pending solicitation per recipient/proposal scope | recipient acceptance or available resource |
| `assemble_coordination_plan` | proposal version and validated contributor-owned replies with conditions | assembly can remain partial; execution is separate | funds delivered or market supported |
| `communicate_coordination_position` | scoped claim, audience, authority, `as-of`, case/proposal and uncertainty | issue/delivery/effect separate; update requires new basis | audience belief or historical truth |
| `decline_or_close_coordination_role` | case/proposal, scoped reason, authority and any permitted referral/reopen condition | closure can be reopened only by named new event | other parties declined or matter resolved |
| `request_commitment_or_result_clarification` | linked reply/result and precise ambiguity | cannot rewrite the prior record | corrected commitment/result before delivery |

Out-of-scope, unauthorized and malformed attempts remain visible. Adapters may
not silently turn a broad “fund the market” output into a valid solicitation or
plan.

## 8. Operationalization and uncertainty

| Construct | Representation | Evidence status and use |
|---|---|---|
| information adequacy | `{absent, incomplete, disputed, adequate_for_scope, superseded}` plus producer, scope and date | qualitative; no recovered solvency threshold |
| attribution/authority | `{personal, firm_delegated, joint, disputed, absent, unknown}` with act scope | focal ambiguity remains; unknown grants no power |
| coordination posture | ordered process category, not a crisis-success score | modeling state for replay |
| proposal readiness | `{draft, information_blocked, authority_blocked, circulating, commitment_blocked, partially_assembled, ready_for_execution_review, withdrawn, closed}` | internal mapping must preserve lineage; “ready” is not executed |
| contributor reply | typed external record with category/amount only when supplied and valid | contributor-owned; exact historical pool amounts are exposed examples |
| relationship history | dated categorical records and declared sensitivity flag | disabled baseline; no scalar closeness, trust or prestige |
| system/market concern | delivered reports with source and uncertainty | no global true stress input or hidden numeric gate |

### Structural alternatives

The shared fixed boundary is that committees and contributors retain their
authority and resources. Two action-attribution states remain:

- `NAMED_PERSONAL_COORDINATION_BASELINE`: only acts attributable to Morgan's
  named coordinating interface are admitted; ambiguous firm acts remain
  external or disputed.
- `SCOPED_FIRM_DELEGATION_SENSITIVITY`: a dated firm-authority record may admit
  a specified coordination, circulation or communication act through the same
  interface; it does not admit a direct firm resource commitment or merge the
  firm or partners into Morgan generally.

Separately, `RELATIONSHIP_HISTORY_DISABLED` is the baseline and
`DATED_RELATIONSHIP_SENSITIVITY` the optional mechanism variant. Both choices
must be pinned in scenario/run identity before behavior; neither can be chosen
from the known result.

## 9. Worked cases and falsification

### Case A — incomplete applicant information (`RECONSTRUCTED / OUTCOME_EXPOSED`)

**Situation.** A valid applicant concern is delivered, but no independent
report and only a partial company statement exist. **Required response.** Name
missing information, request it or request an independent examination, or form
only a proposal explicitly limited by the missing material. **Boundary.** The
applicant owns disclosure; examiner owns the report. **Perturbation.** Deliver
a scoped report. Proposal formation becomes admissible but no aid result
follows automatically.

### Case B — committee report not delivered (`ILLUSTRATIVE`)

**Situation.** The five-person committee has produced a report in world state,
but Morgan has not received it. **Required response.** The Agent may request or
await the report; it cannot use its content. **Boundary.** Committee and
transport own production/delivery. **Perturbation.** Deliver the report with a
disputed scope; Morgan must preserve the dispute and may request clarification.

### Case C — partial contributor replies (`RECONSTRUCTED / OUTCOME_EXPOSED`)

**Situation.** A pool proposal is circulating. Two contributors commit, one
conditions its reply and another declines. **Required response.** Record each
reply, assemble only validated commitments and revise, solicit or communicate
the remaining gap. **Boundary.** No world resources change until authoritative
execution. **Perturbation.** Expire one commitment; plan readiness must fall.

### Case D — personal versus firm coordination authority (`STRUCTURAL_SENSITIVITY`)

**Situation.** A proposal is to be circulated as a J. P. Morgan & Co. position,
but only Morgan's personal coordination authority is known. **Required
response.** Seek firm authority, circulate only a personally scoped proposal,
or keep the firm attribution pending. **Perturbation.** Deliver a scoped firm
delegation; circulation under that provenance becomes admissible. Any firm
resource commitment still requires a separately owned contributor record.

### Case E — relationship-history sensitivity (`STRUCTURAL_SENSITIVITY`)

**Situation.** Two applicants have comparable delivered information but
different dated prior syndicate histories. **Required response.** Baseline
cannot use the difference. Sensitivity may use it only as a declared proposal-
selection or information-search factor while preserving all authority gates.
**Perturbation.** Erase names and reverse histories. If outcomes follow names,
the mechanism is nonconforming; if the sensitivity always selects known
winners, it is rejected as outcome fitting.

### Cross-case falsification

| Test | Expected result | Failure meaning |
|---|---|---|
| name erasure | semantics, not Morgan's fame, determine the envelope | hidden historical script |
| report masking | proposal narrows or information seeking occurs | omniscient coordinator |
| committee-owner swap | Morgan cannot emit committee findings | authority collapse |
| contributor refusal | plan revises and refused resources stay absent | solicitation treated as commitment |
| partial/failed result | later posture differs without rewriting prior trace | result ladder too thin |
| duplicate solicitation | pending identical request is rejected or explicitly revised | no business lifecycle |
| future-fact injection | later success/failure and market outcomes are excluded | temporal leakage |
| always-abstain | valid informed/authorized case produces a bounded response | behaviorally empty policy |
| aggregate/split | firm/associate split occurs only for independent information and decisions | granularity chosen for appearance |

## 10. Limitations, references, and provenance

### Limitations and withdrawal conditions

1. The exact personal-versus-firm boundary is unresolved for some focal acts.
2. No private Morgan diary, complete correspondence, committee case file or
   publicly inspectable focal syndicate-book scan was obtained.
3. The model does not recover Morgan's utility function, motive, private
   solvency judgment or quantitative threshold.
4. Pool amounts, assistance and market outcomes are exposed and not
   calibration targets.
5. Relationship-history sensitivity is retrospective and may suffer post-hoc
   selection.
6. The model omits independent associates and committees unless a successor
   roster admits them.
7. It does not model a direct Morgan or J. P. Morgan & Co. resource-commitment
   decision because no adopted focal record closes that authority and action
   boundary.
8. It does not explain contributor preferences, resource feasibility or market
   response.
9. No cross-event archetype, predictive validity or historical validation is
   claimed.

Remove or narrow the Agent if direct evidence assigns the material choices to
the committee, firm or other actors; split it if associates have independent
information and interacting intents; remove `M-MG-04` if relationship history
does not generate a predeclared process difference; and reject any
implementation that requires hidden outcome knowledge or resource ownership.

### Design provenance

Version `0.1.0` is the first accepted Roster-production Definition. It was
derived from the accepted event roster and semantic skeleton, the R2 evidence
archive, the claim adjudication in the event ledger candidate, and the H2EPR
ten-module template. It is not derived from simulation output, a Rule mapping,
an LLM response or a desired historical endpoint.

### References

- *Commercial and Financial Chronicle*. October 26, 1907.
- *Congressional Record*. 60th Cong., 1st sess., February 26, 1908.
- Moen, Jon R., and Mary Tone Rodgers. 2022. “How J. P. Morgan Picked the
  Winners and Losers in the Panic of 1907.” *Essays in Economic & Business
  History* 40: 156–187.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*. Washington, DC: Government Printing Office.
- U.S. House of Representatives, Committee on Investigation of United States
  Steel Corporation. 1911. *United States Steel Corporation: Hearings*, House
  No. 23.
