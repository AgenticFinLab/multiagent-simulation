# National Bank of Commerce in New York

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | National Bank of Commerce in New York |
| Modeled role | authorized bank-level interface for exposure review, relationship credit, request intermediation, clearing-continuation review, and institutional communication |
| Event and interval | H2EPR-0288, Panic of 1907; from the reported Knickerbocker run and NBC credit accommodation on or before 18 October through the reported next-day relationship boundary on 22 October 1907; exact contract terms remain unresolved |
| Primary decision situations | rising but incompletely measured exposure; received request requiring an intermediation role; clearing-continuation review; issued notice and later delivery/effect |
| Decision cadence | event-driven when a participant-visible review notice, counterparty-information change, authority result, request, direction, notice, or result record arrives; the notice's research provenance remains outside Agent input, and routine per-item clearing does not create a fresh Agent decision |
| Decision form | constrained set-valued institutional policy with explicit authority, information, obligation, lifecycle, and minimum-response boundaries |
| State authority | credit, clearing, request, authorization, communication, and relationship truth is environment-owned; NBC retains only declared decision posture and references to delivered authoritative records |
| Evidence and model status | reviewed event-bound construction using outcome-exposed local sources plus three adopted public sources; the legal rule's identity and narrow effect are resolved, while focal internal authority, information, credit terms, exact ordering, and termination provenance remain explicitly unresolved; no historical calibration or held-out validation is claimed |
| Definition identity | `h2epr.agent-definition.0288.national-bank-of-commerce`, version `0.1.0` |

This Agent represents NBC as a large member bank with its own resources,
clearing obligations, counterparty exposure, and authority constraints. It
explains how the bank may evaluate additional credit, decide whether it will
merely carry or actively stand behind a request, review continuation of a
nonmember clearing relationship, and issue bounded communications.

The model's central distinction is between **NBC's autonomous institutional
choices** and **the channel mechanics in which NBC participated**. Credit
selection, request sponsorship, and the choice to initiate a clearing notice
belong to the participant when they require NBC judgment and authority.
Settlement, transport, delivery, effective termination, and realized loss
belong to the event environment.

Claim identifiers `NBC-C01`–`NBC-C16` resolve in the adjacent
[evidence ledger](evidence-ledger.md); source identities, public locators,
adopted passages, and file hashes are recorded in the
[source register](source-register.md).

### Scope and research purpose

The Definition examines four questions:

1. How do NBC's own dated credit and clearing exposures change information,
   authority, credit, and relationship-review behavior?
2. When does NBC act as a pure forwarding channel, an institutional sponsor, a
   representative, or a participant that declines to intermediate?
3. How do bank-selected and NYCH-directed clearing changes differ in authority,
   decision basis, notice provenance, and traceable process?
4. Can notice issue, delivery, remaining clearing obligations, effective
   termination, and later loss remain analytically distinct?

The model does not explain Knickerbocker's internal request formation, NYCH's
disposition, depositor withdrawals, private-financier coordination, or the
subsequent panic. It does not claim a reusable correspondent-bank archetype or
a historically identified NBC utility function.

## 2. Historical participant and representation

NBC was a large national bank in New York, a prominent correspondent bank, an
NYCH member, and Knickerbocker's clearing agent (`NBC-C01`). Contemporary and
retrospective accounts record NBC's notice and a next-day boundary for the
relationship (`NBC-C02`, `NBC-C04`). The exact focal contract and the direct
application of NYCH Section 25 are not established (`NBC-C16`). The relationship
nevertheless joined operational service to NBC's own credit and settlement
exposure.

Later institutional accounts report that NBC extended credit while
Knickerbocker faced withdrawals, participated through a vice-president in a
support request, and later announced that it would cease clearing
(`NBC-C04`–`NBC-C06`). These accounts establish meaningful decision classes,
but not the exact NBC officer, internal forum, credit terms, information set,
or decision rule.

The Agent is an **aggregate procedural institutional interface**. It includes
only the authorized NBC functions necessary to:

- assess the bank's own exposure and current obligations;
- seek or exercise scoped authority over additional credit;
- classify and act on a request-intermediation role;
- review continuation of the clearing relation and initiate a notice; and
- communicate the bank's verified institutional position.

It excludes:

- Thomas F. Ryan, Henry A. Smith, or another officer as a named psychological
  actor;
- Knickerbocker's board, officers, depositors, assets, and private state;
- NYCH committees and member-bank choices;
- clearing clerks and automatic exchange mechanics as autonomous policies;
- unobserved disagreement inside NBC; and
- the hidden true financial state known to the model designer.

The January 1907 directory lists two NBC vice-presidents, so “the vice
president” cannot identify the focal representative (`NBC-C07`). Split this
Agent if direct evidence shows that request intermediation, credit selection,
and clearing termination belonged to independent NBC bodies with different
information and interacting intents. Narrow it to a protocol where a rule or
external order uniquely determines the relevant response.

## 3. Evidence and theoretical foundation

### Institutional foundation

The 1906 NYCH constitution and Cannon's institutional account support a general
regime for formally recognized nonmember-clearing arrangements: committee
consent, negotiated security terms, member responsibility for exchanges,
reporting and examination, and a notice-governed exit. They do not establish
that Knickerbocker's focal relation was formally governed by Section 25. A
contemporary August 1907 article states that no trust company was then among the
nonmembers for which NYCH members cleared, in tension with focal accounts that
describe NBC as Knickerbocker's clearing agent (`NBC-C16`).

The Pujo Committee's official retrospective report states that a clearing
member could terminate at its own election or be compelled by the
clearing-house committee (`NBC-C03`). Later official hearing testimony confirms
the member's general termination power but records that the witness lacked
first-hand knowledge of NBC's focal consideration (`NBC-C15`). These sources
establish structural authority paths, not the focal contract, exact tail duties,
or the path that produced NBC's action.

### Event-specific foundation

Contemporary financial press, Sprague, and later institutional histories agree
that NBC announced the end of the clearing relationship on 21 October. The
*New-York Tribune* reports that the notice was delivered and that an NBC
officer declined to elaborate publicly (`NBC-C04`, `NBC-C08`). Later sources
report prior credit extension and NBC participation in the request
(`NBC-C05`, `NBC-C06`).

The source accounts are not fully consistent. Sprague emphasizes a late
unofficial examination and says apparently no assistance proposal was
considered, while Wicker-derived accounts describe an NBC/Knickerbocker request
to NYCH. The Section 25 applicability conflict remains separate. The exact
intraday ordering, request form, contractual notice basis, and remaining duties
after notice remain open.

### Exposure mechanism

Tallman's later synthesis interprets the clearing relation as creating
material exposure and a possible incentive to contain additional exposure
(`NBC-C09`). Contemporary post-action reporting corroborates material clearing
exposure while also recording an unnamed NBC officer's assertion that the bank
was covered (`NBC-C14`). Neither source identifies the bank's focal reasoning.

Chapter 522, effective 17 June 1907, supplies the narrower legal mechanism. Once
a bank had knowledge or notice that the Superintendent had taken possession of
an institution, a later payment, advance, clearance, or liability did not
create a lien or charge against that institution's assets (`NBC-C13`). This
does not establish that NBC's pre-possession claims or collateral were
unprotected, and it does not select a termination policy. The Definition uses
the rule only as a dated prospective tail-exposure assessment and introduces no
exact loss, credit limit, or termination threshold. The contemporaneous
reproduction of the enacted text also supersedes the *Tribune*'s shorthand
statement that the change occurred “last February.”

### Behavioral theory

Simon (1956) supports a bounded-information, environment-relative decision
form in which priorities, adequacy, and limited search can organize choice
without global optimization. The theory justifies the modeling form. It is not
evidence that NBC officers consciously followed a Simonian algorithm, and no
parameter is transferred from the paper.

### Evidence-to-mechanism translation

```text
active relationship and current obligations
    + dated NBC credit and clearing exposure
    + delivered counterparty information and request
    + scoped NBC authority and any NYCH direction
    -> bounded credit, intermediation, and relationship alternatives
    -> typed NBC intent or communication
    -> environment-owned booking, transport, settlement, and result
```

Withdrawing the exposure interpretation would narrow `M-NBC-01` but would not
remove the observed relationship, request role, notice process, or the need to
separate participant choice from transport.

## 4. Institutional role and relationships

### Duties and priorities represented

The modeled interface must satisfy clearing and notice duties actually present
in the authoritative focal relationship record,
act only through a competent NBC authority, use current participant-available
information, preserve request and message provenance, and avoid unsupported
commitments. Within those constraints it may protect NBC's own resources,
continue an authorized relationship, seek information or external resolution,
limit additional exposure, or initiate a relationship change.

The Definition does not assign NBC a general public-rescue mandate, a duty to
fund Knickerbocker, or a preference to maximize system confidence.

### Authority interfaces

| Decision scope | NBC authority required | External constraint |
|---|---|---|
| routine clearing under an active arrangement | operational authority under the actual recorded terms | relationship validity, focal contract, NYCH consent, and settlement rules remain authoritative; Section 25 may not be assumed to supply missing terms |
| new or changed credit exposure | scoped credit/financial authority | actual resources, terms, collateral, booking, and result are environmental |
| pure forwarding | authority to transmit the sender's request and provenance through the identified route | sender mandate, content integrity, delivery, and NYCH intake remain external |
| sponsorship or representation | separate authority to add an NBC institutional position or commitment | cannot replace missing Knickerbocker authority or create NYCH admissibility |
| relationship condition or termination notice | scoped NBC relationship/communication authority unless a delivered NYCH direction governs | notice validity, required timing, remaining obligations, delivery, and effect are authoritative process facts |
| public or counterparty statement | scoped communication authority and verified content | audience receipt and reaction remain external |

The exact NBC body holding each authority is not established. An officer title
does not supply authority.

### Resource and exposure relations

| Relation | Model meaning |
|---|---|
| owns or controls | NBC cash and claims, decisions over new NBC credit, its records, and authorized communications, subject to governance and law |
| is responsible for | exchanges carried for Knickerbocker while the clearing arrangement and notice obligations remain in force |
| may evaluate | current NBC exposure, counterparty information actually received, recovery position, relationship terms, and operational capacity |
| may request or propose | information, security/conditions, authority, route clarification, credit posture, or relationship change |
| does not control | Knickerbocker assets or withdrawals, NYCH facilities or member resources, message delivery, settlement, receiver recovery, or public response |

### Counterparties

Knickerbocker is the represented nonmember counterparty. NYCH is the member
association that governs relevant clearing permission and receives or
classifies the focal support-related request. Neither institution's private
state is NBC information without a dated delivery channel.

## 5. Decision situations, information, and state

### Activation and decision situations

The Agent is activated by:

- a valid participant-visible review notice tied to named NBC credit, clearing,
  relationship, legal, or information records;
- new, corrected, stale, or disputed counterparty information;
- a request requiring NBC forwarding, sponsorship, representation, or refusal;
- a scoped NBC authorization result;
- a delivered NYCH clearing direction or request disposition;
- a due clearing-continuation or termination decision; or
- a notice, message, settlement, credit, or relationship result requiring
  adaptation.

The Agent is not activated by the calendar alone, by every routine clearing
item, by a global crisis label, or by knowledge of Knickerbocker's future
suspension.

### Epistemic interface

| Observation | Semantic domain | Source and visibility | Freshness and missing behavior | Principal consumers |
|---|---|---|---|---|
| `clearing_relationship_status` | `{active, notice_pending, ending_at_time, inactive, disputed, unknown}` plus relationship and notice references | authoritative relationship and delivered notice records | seek confirmation; never infer from date or later closure | `DC-NBC-01`, `DC-NBC-03`, `DC-NBC-04` |
| `clearing_exposure_record` | dated NBC clearing items, balances, obligations, stated uncertainty, and optional sourced amounts; no inferred severity class | authoritative NBC clearing/settlement record actually available to the participant | stale or missing triggers verification or narrower action; the later debit report is not backfilled | `DC-NBC-01`, `DC-NBC-03` |
| `credit_exposure_record` | dated outstanding or proposed credit, current terms, stated uncertainty, and any record-backed authorized capacity; no inferred `at_limit` state | authorized NBC credit record actually available to the participant | missing is not zero, unlimited, or at a limit; seek current position or use a scoped conservative response | `DC-NBC-01` |
| `participant_review_notice` | `{none, due, disputed, unknown}` plus review subject, `as_of`, cited delivered record references, and the NBC-legible institutional instruction or due-review basis | an NBC review calendar/instruction, delivered governance record, or participant-visible projection of a changed source record | missing subject, record reference, or participant-legible basis yields `unknown` or `disputed`; researcher classifier/version and construction/sensitivity labels are forbidden | `DC-NBC-01`, `DC-NBC-03` |
| `counterparty_condition_information` | typed dated categories for submitted liquidity, withdrawals, assets, collateral, or uncertainty | Knickerbocker submission, clearing pattern, or authorized examination material actually received | request specified information; no hidden solvency truth | `DC-NBC-01`, `DC-NBC-02`, `DC-NBC-03` |
| `counterparty_request` | request ID, represented sender, content, mandate evidence, route, time, and provenance | delivered Knickerbocker request record | missing mandate/content triggers clarification or narrower role | `DC-NBC-02` |
| `nbc_corporate_authority` | `{not_requested, pending, authorized, denied, disputed, unknown}` with scope and authoritative reference | NBC governance result delivered to the Agent | seek authority or stay within recorded operational authority | every commitment whose proposed act exceeds that authority |
| `nych_clearing_direction` | `{none_delivered, direction_delivered, clarification_pending, disputed, unknown}` plus scope and provenance | delivered NYCH institutional record | no direction inferred from NBC's historical notice | `DC-NBC-03` |
| `nych_request_disposition` | `{none, pending, information_needed, referred, scoped_decline, conditioned_proposal, delayed, partial, failed, executed, unknown}` | delivered NYCH case/result record | silence is no result; private deliberation is forbidden | `DC-NBC-02`, `DC-NBC-04` |
| `incremental_recovery_assessment` | `{protected, no_post_possession_lien, uncertain, disputed, unknown}` plus possession-notice state, affected activity interval, source, and date | authorized legal or institutional assessment | do not generalize the rule to all pre-possession exposure; later scholarship is not participant knowledge unless represented by a dated admissible input | `DC-NBC-01`, `DC-NBC-03` |
| `message_and_notice_status` | `{prepared, issued, transport_pending, delivered, expired, failed, unknown}` plus message, recipient, route, and times | authoritative communication lifecycle | issued is not delivered; delivered is not accepted or effective | `DC-NBC-02`–`DC-NBC-04` |
| `delivered_credit_or_relationship_result` | `{none, no_change, conditioned, partial, failed, effective, reversed, disputed}` plus authoritative result reference | environment-owned financial/relationship result delivered to NBC | never inferred from NBC intent | `DC-NBC-01`, `DC-NBC-03`, `DC-NBC-04` |

#### Explicitly forbidden information

- Knickerbocker's future suspension, later reorganization, and ultimate asset
  recovery;
- the hidden true Knickerbocker balance sheet or private management judgment;
- NYCH private deliberation, vote, resource position, or undelivered direction;
- the identity or mandate of an unnamed NBC vice-president inferred from title;
- the later reported October 22 NBC debit used as an earlier exact input;
- future withdrawals, depositor intentions, and panic severity;
- eventual NBC recovery or loss; and
- a global confidence, fear, solvency, or rescue-probability scalar.

#### Researcher-only review-trigger audit

The scenario/run identity and trace, not the Agent observation, record the
review-trigger classifier authority, classifier identity/version, rule basis,
input-source mapping, and epistemic status
`{historical_record, construction_assumption, sensitivity_assignment}`. These
fields make a modeler-created trigger auditable without telling NBC that it is
inside an experimental branch. Rule and future LLM policies must receive the
same participant projection and may not inspect or branch on these audit labels.

### Authoritative process state and participant decision state

The environment owns the clearing relationship, credit/advance records,
counterparty request, NBC authorization results, NYCH directions and
dispositions, message/notice lifecycle, settlement, and realized outcomes. NBC
may retain the last delivered identity and version but cannot edit a competing
copy.

| State | Owner | Initial condition | Legitimate updates | Behavioral consequence |
|---|---|---|---|---|
| clearing relationship reference | environment relationship process | active only if established by a dated record | consented relation, notice, expiry/effective event, correction | determines current duties and relationship alternatives |
| credit and advance reference | environment financial process | current authoritative book state | adjudicated booking, repayment, failure, correction | changes NBC's exposure observation without self-booking |
| counterparty request reference | environment request process; NBC stores reference/version | none | receipt, clarification, forwarding, withdrawal, expiry, closure | prevents duplicate forwarding and links later disposition |
| NBC authority reference | environment-owned NBC governance process | unknown/not requested by scope | delivered scoped result | opens or closes credit, sponsorship, notice, and communication intents |
| NYCH direction reference | NYCH institutional process; NBC stores delivered reference | none delivered or unknown | delivered direction, withdrawal, clarification, expiry | distinguishes bank-selected from externally directed action |
| exposure-review posture | NBC decision state linked to a valid participant review notice and its cited records | routine monitoring | delivered notice, verification result, information, legal, authority, or result observation | selects verification, continuation, containment, or exit review without becoming balance-sheet truth or receiving researcher-only audit metadata |
| intermediation posture | NBC decision state linked to one request | none | request receipt, role classification, forwarding/sponsorship choice, delivery result, closure | distinguishes courier, sponsor, representative, joint, unresolved, and declined roles |
| communication posture | NBC decision state linked to authoritative message records | none | issue, delivery, failure, expiry, follow-up | prevents unsupported repetition and preserves bounded public restraint as a choice |

Any persistent item that changes a later choice must remain declared,
versioned, and replayable. Transient reasoning may not become hidden memory.

## 6. Behavioral model

### Decision procedure and determinacy

The model is a **constrained set-valued institutional policy**. Evidence does
not identify one exact NBC response for every state. Conforming
implementations may choose among the remaining institutionally defensible
alternatives, but they must apply the same information, authority, obligation,
lifecycle, minimum-response, and result boundaries.

| Stage | Required question | Minimum response class | Remaining choice |
|---|---|---|---|
| 1. distinguish choice from mechanics | Has a valid participant review notice or a request, authority, direction, notice, or result event with its own declared activation rule occurred? | if no, allow routine environment mechanics without inventing an NBC decision; if yes, create a bounded decision response | compatible verification and communication may accompany the substantive response; researcher audit labels are not policy inputs |
| 2. enforce existing obligations | What clearing, notice, and delivered NYCH obligations are currently authoritative? | comply, seek scoped clarification, or record a genuine conflict | urgency cannot erase an active duty or create an undelivered instruction |
| 3. establish information sufficiency | Are exposure, counterparty, request, legal, and relationship observations current enough for the contemplated scope? | verify, request specified information, narrow the action, or use a declared fallback | no hidden exact state may fill the gap |
| 4. establish NBC authority | Is the chosen credit, sponsorship, notice, or communication within a delivered scoped authority? | seek authority, use an ordinary-authority alternative, or abstain for the named blocker | title, historical action, and urgency do not confer authority |
| 5. preserve process identity | Is there an unresolved equivalent request, notice, or credit/relationship process? | maintain, clarify, revise, or await the named due event | no duplicate business process or new ID to bypass state |
| 6. select bounded response | Which permitted credit, intermediation, relationship, or communication response fits the current evidence? | choose at least one substantive or information/authority response after a valid activated event with an available response | the exact choice may vary where the Definition leaves a defensible set |
| 7. adapt after delivery | Has a message, credit, settlement, or relationship result been delivered? | update the linked posture and choose follow-up, clarification, communication, closure, or renewed review | intent cannot be treated as its result |

Abstention is permitted only for a named information, authority, jurisdiction,
obligation conflict, unresolved process, or absence-of-permitted-response
condition. It must identify the event that reopens the decision. An always-wait
or always-abstain policy is not conforming.

### Model invariants

1. Use only declared, delivered, participant-available observations.
2. Treat missing, stale, disputed, and unknown values explicitly.
3. Do not infer NBC authority or a representative's identity from title.
4. Do not infer an NYCH direction from NBC's observed historical notice.
5. Keep routine exchange/transport mechanics outside NBC behavioral policy.
6. Preserve one identity through each request, notice, credit, and relationship
   lifecycle.
7. Keep pure forwarding distinguishable from NBC sponsorship or representation.
8. Keep credit or notice intent, environment adjudication, booking/delivery,
   effective result, and later observation distinct.
9. Do not silently repair invalid, unauthorized, duplicate, or out-of-envelope
   attempts.
10. Do not submit world-state changes or declare support, solvency, delivery,
    effective termination, avoided loss, or restored confidence.
11. Keep all behaviorally material persistent state declared and replayable.
12. Exclude future event facts and evaluation evidence.
13. Do not infer `material`, `elevated`, or `at_limit` from an undocumented
    classifier. The participant review notice must expose only its NBC-legible
    subject, date, cited records, and institutional basis. Its classifier,
    version, source mapping, and historical/construction/sensitivity status must
    remain auditable in scenario/run identity and trace but invisible to policy.

Violating an invariant is implementation nonconformance. Falsifying a
mechanism below is evidence to revise the participant model.

### Behavioral mechanisms

#### `M-NBC-01` — exposure-bounded relationship credit

The clearing relation made NBC's own credit and settlement records relevant to
additional discretionary exposure. A dated change in those records, limited
protection for incremental post-possession activity, stale counterparty
information, or a record-backed change in NBC authority can lead to a
participant-visible review notice and activate
verification, conditions, authority review, and limitation of new discretionary
credit. Where no historical NBC review record survives, the run audit must
identify the activation as a construction assumption or sensitivity assignment
without exposing that label to NBC. It does not
uniquely imply relationship termination and does not retroactively erase
protection for earlier balances or collateral.

Competing explanations include routine service under existing terms,
temporary accommodation while an external solution is pursued, and an
externally directed clearing change. Remove or narrow the mechanism if focal
records show that NBC had no meaningful discretion or performed no exposure
assessment.

#### `M-NBC-02` — mandate-sensitive request intermediation

The clearing relationship provided a channel and an NBC stake in the outcome,
but did not automatically authorize NBC to speak for Knickerbocker. NBC must
distinguish pure forwarding from sponsorship, representation, or a joint
request. Missing sender mandate or NBC authority narrows the role rather than
being filled by an officer title.

Competing explanation: the focal NBC role was mechanical carriage. If evidence
shows no participant choice over transmission, forwarding moves to the
scenario while any separately evidenced sponsorship remains an Agent action.

#### `M-NBC-03` — notice-governed clearing continuation and exit

An active clearing relation could not be ended by a private state change. NBC
had to act within its own authority or a delivered committee direction and
issue or process a notice. The environment owned delivery, the focal contract,
any duties that remained in force, and effective change. Section 25 supplies a
general comparison, not a frozen focal contract (`NBC-C16`).

The known 21 October notice establishes the action repertoire, not a universal
rule that an exposure label forces exit.

#### `M-NBC-04` — information-contingent institutional communication

NBC may communicate verified request, credit, notice, or procedural facts to a
permitted audience. It may also decline to elaborate beyond an authorized
notice when information or authority is insufficient. The contemporary report
of an NBC officer declining further comment supports this response as a focal
capability, not a stable personality trait.

Communication cannot obtain NYCH support, change the relationship, or restore
confidence by declaration.

### Decision Commitments

#### `DC-NBC-01` — review exposure and bound additional credit while preserving current obligations

**Situation.** A valid `participant_review_notice` identifies a new or due NBC
credit/clearing record, counterparty-information change, recovery assessment,
or credit result for review under an active relationship.

**Basis.** `NBC-C02`, `NBC-C05`, `NBC-C09`, `NBC-C11`, `NBC-C13`, `NBC-C14`;
`M-NBC-01`. The focal credit extension, reported debit, coverage assertion,
and termination are exposed or post-action evidence; the internal selection
rule is not known.

**Available information and state.** `credit_exposure_record`,
`clearing_exposure_record`, `participant_review_notice`,
`counterparty_condition_information`, `incremental_recovery_assessment`,
`nbc_corporate_authority`, current relationship/credit references, and
exposure-review posture.

**Alternatives.** Verify exposure; request counterparty information; seek NBC
authority; propose continued credit under existing or bounded conditions;
limit or decline new discretionary credit; continue existing mandatory duties;
seek result clarification; abstain for a named blocker.

**Behavioral hypothesis.** Changing a cited NBC exposure record, its declared
uncertainty, or the legal/authority record changes credit-review and containment
behavior when Knickerbocker's name, the calendar, and the clearing route are
held fixed. The hypothesis concerns traceable input contrasts, not an inferred
severity threshold.

**Permitted intents.** `verify_nbc_exposure`,
`request_counterparty_information`, `seek_nbc_authority`,
`propose_credit_posture`, `limit_or_decline_additional_credit`,
`request_delivery_or_result_clarification`, or abstention.

**Minimum response.** A newly delivered, valid participant review notice must produce
current verification, a scoped authority request, a bounded credit-posture
proposal, limitation of new discretionary exposure, result clarification, or a
recorded blocker with a due revisit event. Existing clearing obligations remain
as recorded until an authoritative change. The pre-event posture cannot persist
without an explicit basis. A notice with a missing participant-visible subject,
cited record, or institutional basis is `unknown` or `disputed` and can require
verification, but cannot by itself justify a credit or relationship restriction.
Researcher-only trigger provenance is audited externally and cannot affect the
choice.

**Precedence.** Existing legal/clearing duties and delivered authority govern
first; current participant information governs next; preserving NBC resources
cannot justify hidden insolvency inference or retroactive termination.

**Abstention boundary.** Abstention requires missing current exposure,
counterparty information, legal assessment, or authority, or a pending process
with no due action. It may not stand in for a credit decision when all declared
prerequisites are satisfied.

**Expected and forbidden pattern.** Exposure and information perturbations
change the credit-review path. Forbidden: a date-triggered termination, an
undocumented numeric limit, or NBC directly booking a result.

**Falsifier and deletion test.** The mechanism is falsified or narrowed if
exposure changes produce no process difference, or direct records show a
mechanically fixed response. Removing this commitment would make NBC's reported
credit extension and exposure containment an unexplained environment choice.

#### `DC-NBC-02` — classify and act on a request-intermediation role

**Situation.** NBC receives a Knickerbocker request or request-related message
that may be carried, sponsored, represented, clarified, or declined.

**Basis.** `NBC-C06`, `NBC-C07`, `NBC-C11`, `NBC-C12`; `M-NBC-02`. Later
accounts support title-level NBC participation but do not establish the exact
person, mandate, content, or role.

**Available information and state.** `counterparty_request`, sender mandate,
route/content provenance, `nbc_corporate_authority`, current relationship,
intermediation posture, message status, and any delivered NYCH clarification.

**Alternatives.** Seek mandate/content clarification; forward one request with
unaltered provenance; seek or exercise NBC sponsorship authority; add an
authorized NBC representation; decline sponsorship or intermediation for a
typed reason; request route clarification; abstain for a named blocker.

**Behavioral hypothesis.** Sender mandate, NBC authority, and NBC's declared
role alter the content and permitted form of the request path. Pure carriage
and institutional sponsorship are not interchangeable.

**Permitted intents.** `seek_intermediation_clarification`,
`forward_request_with_provenance`, `sponsor_or_represent_request`,
`decline_intermediation`, `request_nych_direction_clarification`, or abstention.

**Minimum response.** A newly delivered request that contains a stable request
identity, represented sender, requested content, mandate status, proposed
route, event time, and provenance must be classified and receive one of: a
single linked forwarding act, a scoped sponsorship/representation act, a
request for specified missing information or authority, a typed decline, or an
explicit absence-of-competent-route record. If any required element is missing,
the minimum response is a named clarification, narrower role, or typed blocker.
The request cannot remain indefinitely unclassified.

**Precedence.** Sender authority and content integrity precede NBC's own role;
NBC sponsorship authority precedes adding any endorsement; one request identity
precedes all follow-up messages.

**Abstention boundary.** Abstention requires a named missing request element,
NBC authority, competent route, or a pending equivalent process with no due
follow-up. It cannot transform pure forwarding into silent refusal.

**Expected and forbidden pattern.** Forwarding preserves original provenance;
sponsorship adds a separate NBC basis. Forbidden: title-based mandate, duplicate
request, rewritten sender content, or self-declared NYCH receipt/acceptance.

**Falsifier and deletion test.** If sender mandate and NBC sponsorship authority
never alter message content or choice, the mechanism is decorative. Removing
the commitment collapses NBC into transport and prevents the model from asking
why the observed request took this institutional route.

#### `DC-NBC-03` — govern clearing continuation or an authorized termination notice

**Situation.** A valid participant review notice tied to the relationship, exposure,
authority, or applicable legal record arrives; a separately recorded clearing
review becomes due; or an NYCH clearing direction is delivered.

**Basis.** `NBC-C02`, `NBC-C03`, `NBC-C04`, `NBC-C09`, `NBC-C10`, `NBC-C11`,
`NBC-C13`, `NBC-C14`, `NBC-C15`, `NBC-C16`; `M-NBC-01` and `M-NBC-03`. General and
official-testimony evidence supports bank-elected and committee-compelled
paths; the focal witness was not present for NBC's consideration, so focal
provenance remains unresolved. Section 25's direct focal applicability is also
disputed and cannot supply an otherwise missing contract term.

**Available information and state.** `clearing_relationship_status`,
`clearing_exposure_record`, `credit_exposure_record`, `participant_review_notice`,
counterparty information, `incremental_recovery_assessment`,
`nbc_corporate_authority`, `nych_clearing_direction`, notice status, and
relationship/exposure-review posture.

**Alternatives.** Confirm continuation after review; propose a bounded
condition; verify information; seek NBC authority; seek NYCH direction or scope
clarification; issue an authorized termination notice; comply with a valid
delivered direction; abstain for a named blocker.

**Behavioral hypothesis.** Relationship posture responds to NBC's own exposure,
information, authority, and any delivered NYCH direction, while notice and
effective termination remain distinct. The same historical date does not fix
the choice.

**Permitted intents.** `confirm_clearing_continuation`,
`propose_relationship_condition`, `verify_nbc_exposure`,
`request_counterparty_information`, `seek_nbc_authority`,
`request_nych_direction_clarification`, `issue_clearing_termination_notice`, or
abstention.

**Minimum response.** A valid review event must produce a reviewed
continuation/condition, verification or authority step, direction
clarification/compliance response, termination-notice intent, or a recorded
blocker with a revisit event. A valid delivered committee direction must be
processed; without such a direction, NBC-selected notice requires its own
scope, authority, and basis.

**Precedence.** Valid external institutional direction and current obligations
govern first; NBC authority and current information govern the bank-selected
path; a known future suspension never governs.

**Abstention boundary.** Abstention requires unresolved direction provenance,
authority, a named required information item, or a genuine conflict of
obligations. It
cannot preserve an unchanged relationship posture indefinitely after all
declared blockers close.

**Expected and forbidden pattern.** Bank-selected and committee-directed paths
remain distinguishable, and notice issue precedes delivery/effect. Forbidden:
automatic termination from date/name, private relation mutation, or using the
known notice to prove its own decision rule.

**Falsifier and deletion test.** A focal record showing unique committee
control would narrow NBC to compliance/communication for that path; a unique
contractual rule could narrow it further to protocol. Removing the commitment
would hide the clearing-channel withdrawal inside the environment.

#### `DC-NBC-04` — communicate and adapt across request, notice, and result lifecycles

**Situation.** NBC has formed a credit, request, or relationship posture; a
message/notice has been issued, delivered, failed, or expired; or a later
credit, NYCH, settlement, or relationship result has been delivered.

**Basis.** `NBC-C04`, `NBC-C08`, `NBC-C12`; `M-NBC-04`. The focal notice and
limited public comment are exposed examples, while the lifecycle separation is
a modeling necessity.

**Available information and state.** current request, credit, relationship,
authority, direction, message/notice, and delivered-result records plus NBC's
intermediation and communication posture.

**Alternatives.** Issue a bounded request, notice, or status communication;
request delivery/result clarification; retry through a permitted route; update
credit/intermediation/relationship posture; close or reopen review through a
new authorized event; decline additional comment; abstain when no response is
due.

**Behavioral hypothesis.** NBC behavior differs among prepared, issued,
delivered, failed, expired, partial, and effective states. Public restraint is
permitted when information or authority does not support further claims.

**Permitted intents.** `communicate_nbc_position`,
`request_delivery_or_result_clarification`, any still-applicable linked intent
from `DC-NBC-01`–`DC-NBC-03`, or abstention.

**Minimum response.** A new message failure, delivered NYCH disposition,
credit result, or effective relationship result must update the linked posture
and produce a truthful communication, clarification, retry, renewed review,
closure, or explicit no-further-action record. An issued intent cannot remain
the visible terminal state after a contradictory result.

**Precedence.** Authoritative business and relationship state determine what
may be said; communication status determines delivery-dependent follow-up but
cannot rewrite the decision or result; the newest delivered result governs
later adaptation without erasing history.

**Abstention boundary.** Abstention is conforming only when no new
communication/follow-up is due or authority/information forbids a substantive
statement. The current state and reopening event must remain visible.

**Expected and forbidden pattern.** Decision, issue, transport, delivery,
effective result, and later observation remain linked and distinct. Forbidden:
declaring delivery, termination, avoided loss, or restored confidence.

**Falsifier and deletion test.** If message/result classes produce identical
later behavior, the lifecycle is too thin. Removing this commitment would let
NBC intent masquerade as delivered and realized outcome.

## 7. Intent and result boundary

The capabilities below are modeled institutional intents unless a worked case
explicitly labels an exposed reconstruction. Stable semantic identifiers aid
comparison; they do not prescribe a wire schema.

| Reader-facing intent (semantic ID) | Required semantic content | Lifecycle and duplication | Result NBC may not declare |
|---|---|---|---|
| Verify NBC exposure (`verify_nbc_exposure`) | requested clearing/credit record scope, input-record references, required `as-of`, responsible NBC interface, and current process reference | remains pending until an authoritative dated record or assessment result | record complete, exposure acceptable, or loss avoided |
| Request counterparty information (`request_counterparty_information`) | request/relationship identity, specified information, `as-of`, recipient, disclosure route | may be clarified, delivered, stale, disputed, or unanswered | information received, complete, or favorable |
| Seek NBC authority (`seek_nbc_authority`) | proposal identity, scope `{credit, sponsorship, representation, relationship, notice, communication}`, basis | pending until authoritative governance result | authority granted |
| Propose a credit posture (`propose_credit_posture`) | credit/relationship reference, posture `{continue, condition, pause_new_credit}`, bounded terms or unknowns, expiry/review event | booking and later exposure result separate | credit advanced, collateral accepted, or counterparty supported |
| Limit or decline additional credit (`limit_or_decline_additional_credit`) | affected credit scope, typed reason, authority, effective/review condition | does not erase outstanding obligations or authoritative balances | exposure reduced, loss avoided, or relationship ended |
| Seek intermediation clarification (`seek_intermediation_clarification`) | request identity, missing sender mandate/content/route/NBC role | one active clarification thread per request and issue | mandate established or route accepted |
| Forward a request with provenance (`forward_request_with_provenance`) | request identity, unaltered sender/content, mandate evidence, NBC role=`courier`, recipient/route | no business-equivalent duplicate; transport and receipt separate | delivered, accepted, reviewed, or approved |
| Sponsor or represent a request (`sponsor_or_represent_request`) | request identity, NBC role and claim, scoped NBC authority, sender provenance, recipient/route | sponsorship is linked to but distinct from sender request and delivery | NYCH accepted, support available, or funds committed |
| Decline intermediation (`decline_intermediation`) | request identity, scoped reason, NBC authority, any permitted alternative/referral | delivery and sender adaptation separate | request withdrawn or all routes unavailable |
| Request NYCH direction clarification (`request_nych_direction_clarification`) | relationship/case identity, direction/route question, competent NYCH interface | pending until a delivered institutional response | committee direction or permission established |
| Confirm reviewed clearing continuation (`confirm_clearing_continuation`) | relationship identity, participant-visible review-notice/reference, reviewed scope, current terms, authority, next review event | used after a valid review, not for each routine item | future clearing completed or counterparty viable |
| Propose a relationship condition (`propose_relationship_condition`) | relationship identity, condition, authority, proposed effective/review event | environment validates and applies any condition | relationship changed or condition satisfied |
| Issue a clearing-termination notice (`issue_clearing_termination_notice`) | relationship identity, provenance `{bank_initiated, committee_directed, combined, disputed}`, scope, authority, proposed effective time, recipients | issue, delivery, remaining obligation, and effect are separate | notice delivered, relationship inactive, loss avoided, or institution closed |
| Communicate NBC position (`communicate_nbc_position`) | verified bounded claim, subject, audience, authority, `as-of`, linked process | delivery and audience response separate; repeated only for a new authoritative or explicitly classified update | confidence restored, withdrawals stopped, or outcome changed |
| Request delivery or result clarification (`request_delivery_or_result_clarification`) | linked message/process/result identity and specified ambiguity | cannot rewrite the prior record | delivery occurred or result reversed |

Abstention is a recorded no-intent decision with a specific information,
authority, direction, process, or jurisdiction blocker and a revisit event. It
is not a universal fallback.

## 8. Operationalization and uncertainty

The Definition uses dated, provenance-bearing observations and process records.
No exact or qualitative severity threshold is introduced merely to reproduce
the historical notice. A modeler-created review activation is disclosed in the
run audit as a construction assumption or sensitivity assignment, not presented
as a recovered NBC judgment and not exposed to the Agent.

| Construct | Representation | Evidence and use |
|---|---|---|
| credit and clearing exposure | dated source records, stated uncertainty, and optional sourced amount; no inferred severity or limit state | exact focal terms and balances unavailable; later $7 million report is not an earlier input |
| participant review notice | `{none, due, disputed, unknown}` with subject, cited delivered records, NBC-legible instruction/basis, and `as-of` | no focal NBC review procedure survives; this is the only trigger projection visible to policy |
| review-trigger audit | classifier authority and identity/version, rule basis, input-source mapping, `as-of`, and epistemic status | scenario/run/trace-only; modeled activations must be labeled construction assumptions or structural sensitivities unless a historical record is later found; policy access is prohibited |
| counterparty information | typed dated categories with provenance, scope, and uncertainty | exact focal dossier unavailable |
| NBC authority | scoped categorical governance result | focal deciding interface unavailable |
| incremental recovery position | categorical legal assessment tied to possession notice, activity timing, source, and date | Chapter 522 verified; focal NBC understanding and the quality of pre-possession coverage remain unresolved |
| request role | `{courier, sponsor, representative, joint, unresolved, unauthorized}` | focal role unresolved; title does not decide it |
| termination provenance | `{bank_initiated, committee_directed, combined, disputed, unknown}` | general authority paths supported; focal provenance unresolved |
| notice lifecycle | `{prepared, issued, transport_pending, delivered, effective, failed, disputed}` | general notice boundary supported; exact focal timing needs refinement |
| credit result | typed no-change/conditioned/partial/failed/booked/repaid/loss state | environment-owned; no Agent self-booking |

### Request-role decision table

| Sender mandate/content | NBC sponsorship authority | Minimum admissible response | Prohibited shortcut |
|---|---|---|---|
| incomplete or disputed | any | request specified clarification, decline the unsupported role, or record no competent path | infer sender authority from the clearing relation |
| sufficient; sponsorship unknown/denied | pure forwarding permitted | forward once as courier, seek sponsorship authority, or decline sponsorship with a typed reason | add an NBC endorsement silently |
| sufficient; sponsorship authorized | route and content adequate | pure forwarding or scoped sponsorship/representation, with distinct provenance | call message issue NYCH acceptance |
| sufficient; no competent route identified | any | seek route clarification, make an evidenced referral if permitted, or record the route blocker | invent a recipient or duplicate the request |

### Clearing-direction decision table

| Delivered NYCH direction | NBC information/authority | Minimum admissible response | Historical claim boundary |
|---|---|---|---|
| valid direction within scope | sufficient to comply | process the direction under notice/current-duty rules or seek clarification of a genuine ambiguity | does not prove this was the focal path |
| none delivered | sufficient NBC review authority | continue, condition, seek more information, or issue an NBC-initiated notice | known notice does not validate one selection rule |
| disputed or unclear | any | verify provenance/scope while preserving obligations still in force | cannot treat later narration as delivered direction |
| no NBC authority and no valid direction | any | seek authority or record a scoped inability to change the relationship | urgency and exposure do not create authority |

Generic risk tolerance, fear, confidence, benevolence, solvency probability,
rescue propensity, and an undocumented exposure limit are omitted.

## 9. Worked cases and falsification

### Case A — routine clearing without a new NBC choice (`HISTORICALLY_GROUNDED_BASELINE`)

**Evidence class.** Historically grounded institutional baseline, not a
reconstruction of one focal credit decision.

**Decision-time situation.** The clearing relationship is active; no valid
participant review notice or information, authority, direction, notice, or due-review
event has arrived. Valid exchange items arrive under current recorded terms.

**Required response.** The environment carries and settles the items under the
authoritative relationship. NBC need not emit a high-level continuation intent
for every item.

**Environment boundary.** Item validation, routing, settlement, balances, and
results are authoritative mechanics.

**Perturbation.** Deliver a due review notice citing changed exposure records
and an NBC-legible basis. The run audit, invisible to NBC, identifies the
classifier/version and labels this perturbation `sensitivity_assignment`. NBC
now owes a bounded response under `DC-NBC-01`; the notice does not predetermine
termination and is not represented as an observed NBC threshold.

### Case B — exposure rises while counterparty information is stale (`ILLUSTRATIVE`)

**Evidence class.** Illustrative mechanism test using evidence-supported
categories, not a claim about NBC's exact focal books.

**Decision-time situation.** NBC receives changed dated exposure records and a
participant-visible due review notice, but current counterparty information is
stale. The external run audit labels the trigger
`ILLUSTRATIVE_CONSTRUCTION_ASSUMPTION`; that label is not in NBC's observation.
It may also possess a current,
admissible legal assessment that later post-possession advances would lack the
specified lien or charge, without knowing whether possession will occur.
Existing clearing obligations remain active.

**Required response.** NBC verifies exposure or counterparty information,
seeks authority, proposes a bounded credit posture, limits new discretionary
credit, or records a blocker and revisit event. It cannot read future
suspension, cancel current duties privately, or use an undocumented threshold.

**Environment boundary.** Actual balances, collateral, new credit booking,
settlement, and later recovery remain external.

**Perturbation.** Supply current information showing that existing exposure is
covered within authorized terms while leaving the incremental
post-possession rule unchanged. Verification urgency should fall for the
existing position, but the legal tail-risk category remains available for new
activity. Termination remains one possible future choice only if independently
activated and authorized.

### Case C — one request, courier versus sponsor (`RECONSTRUCTED / OUTCOME_EXPOSED`)

**Evidence class.** Reconstructed from later title-level accounts; the exact
request, participant, and mandate remain unresolved.

**Decision-time situation.** NBC receives one Knickerbocker request with
sufficient sender authority and content. NBC may transmit it, but its own
sponsorship authority is unknown.

**Required response.** NBC classifies its role. It may forward once with
unaltered provenance while seeking sponsorship authority, ask for role/route
clarification, or decline to add an NBC position. It may not silently convert
carriage into a joint request.

**Environment boundary.** Transport, NYCH receipt/classification, disposition,
and support remain outside NBC.

**Perturbation.** Deliver scoped NBC sponsorship authority. Sponsorship becomes
admissible and must add a distinct NBC basis; NYCH acceptance remains external.

### Case D — bank-selected versus committee-directed notice (`STRUCTURAL_SENSITIVITY`)

**Evidence class.** Structural sensitivity grounded in the two general
authority paths; neither is historically selected for the focal action.

**Decision-time situation.** In one version no NYCH direction has been
delivered, NBC holds scoped relationship-review authority, and a due review
notice identifies the dated records and an NBC-legible basis. The external run
audit labels the trigger `sensitivity_assignment` and remains invisible. In the
other, a valid NYCH direction is delivered for the same relationship.

**Required response.** In the bank-selected path NBC may continue, condition,
seek information/authority, or issue a notice with its own basis. In the
committee-directed path it must process the direction within the notice and
remaining-obligation rules, seeking clarification only for a genuine scope or
provenance ambiguity.

**Environment boundary.** Notice validity, delivery, remaining exchanges, and
effective termination remain authoritative process results.

**Perturbation.** Remove the delivered direction. Compliance no longer
justifies notice; an NBC-selected response requires its own authority and basis.

### Case E — notice issued but not yet effective (`RECONSTRUCTED / OUTCOME_EXPOSED`)

**Evidence class.** Reconstructed notice-lifecycle case using the known
announcement without inferring NBC's internal policy.

**Decision-time situation.** An authorized notice is issued. Delivery or the
reported next-day relationship boundary is still pending; the scenario carries
the actual focal contract and any remaining duty rather than inferring Section
25 applicability.

**Required response.** NBC preserves obligations still in force, may request
delivery/effective-time clarification, and may issue a bounded communication.
It does not privately mark the relation inactive.

**Environment boundary.** Transport, recipient knowledge, final exchanges, and
effective relationship change remain external.

**Perturbation.** Make delivery fail. The intended change remains unrealized;
a retry, clarification, or maintained failure state replaces invented effect.

### Cross-case falsification plan

| Test | Expected result | Failure meaning |
|---|---|---|
| actor-name erasure | replacing NBC's historical name while preserving semantics leaves the choice envelope unchanged | hidden name/date script |
| exposure masking | missing or stale exposure yields verification or narrower action | hidden financial truth drives policy |
| exposure-record contrast | changing cited dated exposure records under the same declared review rule changes credit/review behavior without mechanically fixing termination | exposure records are decorative or an undisclosed classifier controls behavior |
| participant-trigger completeness | a review notice without subject, cited delivered records, NBC-legible basis, or date becomes `unknown`/`disputed` and cannot justify restriction or notice | a qualitative label is acting as a hidden threshold |
| audit-label masking | changing only classifier/version or historical/construction/sensitivity audit labels while preserving NBC's projected notice and records leaves policy behavior unchanged | researcher knowledge has leaked into the Agent |
| legal-scope contrast | changing possession notice and the timing of new activity changes only the incremental recovery assessment, not the status of all earlier exposure | Chapter 522 has been converted into a general unsecured-exposure shortcut |
| sender-mandate removal | sponsorship/representation narrows; NBC cannot create Knickerbocker authority | clearing relation is treated as blanket agency |
| request-role contrast | courier and sponsor produce distinct authority and content records | intermediation roles are collapsed |
| committee-direction contrast | delivered direction changes provenance and authority path | external direction is decorative or secretly assumed |
| notice lifecycle | prepared, issued, delivered, and effective remain distinct | NBC owns transport or result |
| routine-mechanics deletion | removing per-item Agent decisions leaves all autonomous choices intact | infrastructure is being personified |
| result ladder | failed, partial, delayed, effective, and reversed results change later posture | result semantics are too thin |
| always-abstain | an activated, sufficiently informed and authorized situation produces a bounded response | the policy is behaviorally empty |
| future-fact injection | future suspension, later debit, and receiver outcomes are rejected | temporal leakage |
| aggregate/split | internal actors are added only when different information and interacting intents explain a predeclared process pattern | organizational detail is aesthetic |

Reject or narrow the model if credit, intermediation, or clearing continuation
is shown to be mechanically fixed; if exposure, mandate, authority, and
direction perturbations produce no distinguishable path; or if the aggregate
conceals necessary independent NBC actors.

## 10. Limitations, references, and provenance

### Assumptions, limitations, and withdrawal conditions

1. The aggregate NBC interface is a modeling assumption, not a recovered
   internal organization chart.
2. The exact NBC representative, deciding body, mandate, and information set
   remain unresolved.
3. Exact focal credit terms, balances, collateral, exposure, and limits are not
   identified.
4. Chapter 522 verifies only the post-possession incremental lien rule; NBC's
   focal use of the rule and the legal quality of its earlier coverage remain
   unresolved.
5. Section 25 supplies a general institutional comparison, but a contemporary
   August 1907 source says no trust company was then among the nonmembers for
   which NYCH members cleared. Its direct application to Knickerbocker and the
   exact focal notice duties remain disputed.
6. The request account conflicts with Sprague's retrospective narrative.
7. Focal termination provenance may be bank-initiated, NYCH-directed, combined,
   disputed, or unknown.
8. Credit extension, request participation, and the clearing notice are exposed
   outcomes and cannot validate the mechanisms.
9. The Agent does not explain Knickerbocker authorization, NYCH disposition,
   depositor choice, private rescue, or panic propagation.
10. No historical calibration, independent held-out validation, cross-event
   reuse, predictive validity, or individual psychology is claimed.

Withdraw or materially revise:

- `M-NBC-01` if primary records show no exposure discretion or contradict the
  asserted recovery mechanism;
- `M-NBC-02` if NBC's focal role was mechanically limited to transport;
- `M-NBC-03` if one rule or NYCH direction uniquely governed the path;
- `M-NBC-04` if NBC did not control the modeled communication;
- the aggregate representation if internal bodies require independent
  observations and intents; and
- any qualitative or numerical bound whose source time or definition is
  incompatible with its modeled use.

### Design provenance

Version `0.1.0` is the first accepted NBC Definition. It is derived from the
H2EPR ten-module template, the event role map, reviewed evidence and
participant-behavior research, and comparison with the two existing
participant Definitions. No executable mapping or simulation result is used
as evidence for the behavioral model.

The bounded public-source study is complete. It resolved the legal rule's
identity and narrow effect and strengthened the structural authority and
post-action exposure record; it did not locate a focal NBC decision record. The
Definition therefore remains intentionally incomplete on exact authority,
ordering, credit terms, information, pre-possession coverage, Section 25's
focal applicability, and internal decision evidence. The accepted version
preserves these limits rather than selecting a historical policy from the
known outcome.

### References

- Cannon, James G. 1910. *Clearing-House Methods and Practices*. Washington,
  DC: Government Printing Office.
- “The New Legislation Affecting Clearing for Non-Members in the New York
  Clearing House.” 1907. *The Banking Law Journal* 24 (8): 595–602; Chapter
  522, Laws of New York, 1907, reproduced at 635–636.
- Moen, Jon R., and Ellis W. Tallman. “The Panic of 1907.” Federal Reserve
  History.
- New York Clearing House Association. 1906–1907. Constitution, Section 25 and
  amendment, in the Yale Program on Financial Stability constitution bundle.
- *Commercial and Financial Chronicle*. October 26, 1907.
- *New-York Tribune*. October 22 and 23, 1907.
- Rand McNally. 1907. *Bankers' Directory*, January 1907, New York City bank
  listings.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*. Washington, DC: Government Printing Office.
- Tallman, Ellis W. 2012. “The Panic of 1907.” Federal Reserve Bank of
  Cleveland Working Paper 12-28.
- U.S. House of Representatives, Committee on Banking and Currency. 1913.
  *Report of the Committee Appointed Pursuant to House Resolutions 429 and 504
  to Investigate the Concentration of Control of Money and Credit*.
- U.S. House of Representatives, Subcommittee of the Committee on Banking and
  Currency. 1913. *Money Trust Investigation*, Part 8, testimony of Mr. Frew,
  hearing pp. 630–633.
