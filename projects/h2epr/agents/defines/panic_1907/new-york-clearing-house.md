# New York Clearing House Association

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | New York Clearing House Association (NYCH) |
| Modeled role | member-governed procedural interface for request receipt, route and eligibility classification, information review, authority formation, and institutional disposition |
| Event and interval | H2EPR-0288, Panic of 1907; the October 21 request receipt, classification, review, authority, and response boundary |
| Primary decision situations | request classification; incomplete information or authority; member-facility boundary; conditioned proposal; case disposition, communication delivery, and later result |
| Decision cadence | event-driven when a request, relationship fact, information item, forum/authority state, proposal state, or result changes; an activated case must produce a procedural response record |
| Decision form | constrained set-valued procedural policy: all implementations share classification, minimum response, authority, and result boundaries while some institutionally permitted choices remain open |
| State authority | case, review, authority, commitment, and result truth is environment-owned institutional process state; the Agent may propose transitions and retain delivered references |
| Evidence use and explanatory scope | Contemporary, institutional, and retrospective sources informed an event-bound reconstruction; the alternative-route baseline and sensitivity variant are modeling choices rather than validated procedures |

This Agent represents the New York Clearing House Association as a member-based procedural institution, not as
a single banker or a modern central bank. It explains how a support-related request may be received, classified
by membership and route, examined for information and authority, referred or reviewed, and answered through a
typed institutional communication or conditioned proposal.

The model separates association governance, committee authority, manager/clearing operations, member-bank
resources, collateral review, and particular facilities. It therefore rejects both a generic
`willingness_to_help` score and a single fungible “NYCH resource pool.” The participant may propose, authorize,
refer, request, communicate, decline, delay, or abstain within a documented interface. It cannot directly
transfer member resources or declare that a requester or the financial system has been stabilized.

Claim identifiers resolve in the event-owned [participant-evidence record](../../../events/panic_1907/participant-evidence-v0.1.md);
source identities, public locators, adopted passages, and file hashes are recorded in the
[source register](../../../events/panic_1907/source-register-v0.1.md).

### Scope and research purpose

The Definition is designed to examine five questions:

1. Do membership and the named route change the institutional choice set before a resource preference is
   applied?
2. Does missing financial, authorization, or route information produce review and information behavior rather
   than hidden inference?
3. Can a procedural aggregate represent NYCH without erasing material committee/member differences?
4. Can member-facility ineligibility be modeled without falsely proving a universal nonmember-support ban?
5. Can an authorized proposal remain distinct from member commitment, collateral acceptance, execution, and
   effect?

The model does not endogenize individual member-bank preferences, NBC’s clearing decision, J. P. Morgan’s
private coordination, depositor response, or the later October 26 certificate program as if it governed
October 21.

## 2. Historical participant and representation

NYCH was an association of member banks with a general meeting, officers, manager, standing committees, and
special committees. Cannon describes one vote per member, a clearing-house committee second in authority to
the association, a manager responsible for clearing operations and records, and separate conference,
admissions, arbitration, and special loan functions (Cannon 1910, 159–174; `NYCH-C01`–`NYCH-C04`).

The Agent aggregates these components as a **procedural institutional interface**. Aggregation preserves which
kind of institutional condition is present—receipt, classification, examination, committee review,
membership-level authorization, or member commitment—even when the first model does not create a separate
Agent for each body.

The Agent excludes:

- any individual banker’s private preferences;
- member banks’ uncommunicated information and unilateral actions;
- NBC’s exposure and clearing-agent decision;
- Knickerbocker’s internal financial state;
- later private coordination not available at the focal time; and
- a central-bank-style statutory mandate or balance sheet.

Split the participant if focal archival evidence shows that committees or member banks possessed different
participant-available observations and issued interacting intents that cannot be represented as transparent
procedural states.

## 3. Evidence and theoretical foundation

### Institutional foundation

The 1906 constitution and amendment establish the regulated distinction between membership and clearing for an
outside institution. Cannon’s institutional account and reproduced forms establish general meeting,
committee, manager, examination, statement, security, consent, and corporate-authorization arrangements.
These materials support a procedural representation but do not reproduce the October 21 decision.

### Event-specific and archival boundary

Later institutional histories describe an NBC/Knickerbocker request followed by refusal with a member-resource
rationale. Sprague describes a late unofficial examination and says apparently no proposal to assist was
considered. Columbia’s finding aid locates original committee minutes through October 30, 1907, a typed copy,
and nonmember weekly statements, but these records were not publicly available online (`NYCH-C09`). Exact
forum, sequence, information package, and authorization therefore remain unresolved.

### Empirical and behavioral foundation

Moen and Tallman find that cash liquidity and clearinghouse membership/access are associated with smaller
deposit contraction in their 1907 cross-section, while their capital-based solvency proxy is not statistically
significant. They caution, however, that this does not disprove insolvency perceptions and that the membership
measure is crude. This Definition treats access as a possible bundle of liquidity, monitoring, collective
guarantee, and signaling mechanisms rather than a rescue probability (`NYCH-C11`, `NYCH-C12`).

Simon’s bounded-rationality theory supports a limited-information, environment-relative procedural model. It
does not prove NYCH’s internal algorithm or justify a numerical institutional preference.

### Evidence-to-mechanism translation

```text
delivered request and relationship facts
    -> membership, route, information, and authorization classification
    -> competent procedural forum and bounded alternatives
    -> information request, review, referral, typed decline,
       conditioned proposal, communication, delay, or abstention
    -> environment/member-owned commitment, execution, and result
```

The claim ledger remains authoritative for evidence status, time, exposure, conflict, and withdrawal.

## 4. Institutional role and relationships

### Mandate and duties represented

The modeled interface administers clearinghouse relationships and procedures, protects the integrity of
member-governed mechanisms, obtains institutionally relevant information, and coordinates or proposes action
only through a competent forum. It may consider member obligations and clearing-system continuity where an
authorized route requires them.

### Authority interfaces

| Interface | Represented authority | Explicit limit |
|---|---|---|
| manager/clearing operation | receive and record clearing-related material; administer ordinary process under committee control | receipt and recordkeeping do not authorize support |
| clearing-house committee | supervise affairs; examine within its jurisdiction; require security from members; permit/refuse a member clearing for an outside institution; establish subordinate rules subject to association approval | exact focal support authority remains unproven |
| conference plus clearing-house committees | specified concurrence for extreme member suspension, followed by association review | not a generic nonmember-support procedure |
| association meeting | membership-level governance, vote, and approval where required | cannot be assumed convened or resolved without a dated event |
| special loan or crisis committee | particular delegated facility functions when constituted | October 26 procedure is not back-projected to October 21 |
| member banks | own resources and may bear collective obligations under an authorized mechanism | their private choices and resources are not automatically NYCH state |

### Membership and nonmember clearing

A nonmember could clear through a special arrangement with a member. The member carried responsibility for the
outside institution’s exchanges within the notice rule, while the clearing-house committee could permit or
refuse the member’s clearing privilege. Examination and weekly condition reporting accompanied this
relationship (`NYCH-C05`–`NYCH-C07`). Clearing access, membership, and facility eligibility are therefore three
different institutional facts.

### Resource relations

The Agent may control association procedures and specified association assets; review or hold collateral under
an authorized facility; and coordinate or propose member commitments. It does not own all member-bank cash,
credit, reserves, or risk capacity. Actual member commitment, collateral acceptance, scheduling, transfer, and
effect belong to authoritative institutional/environment processes.

## 5. Decision situations, information, and state

### Activation and decision situations

The Agent is active when:

- a clearing relationship requires ordinary administration or examination;
- a support-related request is delivered to an NYCH interface;
- membership, route, or institutional authority must be classified;
- current information, examination, or collateral material is required;
- a committee or association process is opened, advanced, or resolved;
- a proposed collective/member-related measure requires authorization; or
- an institutional disposition or status communication must be issued.

It is not activated by a historical date, a global panic scalar, a future suspension, or researcher knowledge of
the eventual result.

### Epistemic interface

| Observation | Semantic domain | Source and visibility | Freshness and missing behavior | Principal consumers |
|---|---|---|---|---|
| `delivered_request` | request identity, represented institution, sender/channel, requested route/resource, authorization evidence, time | delivered institutional message only | absent delivery means no case; missing fields trigger classification or information request | all commitments |
| `relationship_status` | membership; clearing member/agent; relationship effective time; notice state | institutional records and delivered relationship events | actor identity does not fill a missing relationship | `DC-NYCH-01`, `DC-NYCH-03` |
| `route_classification` | `{member_facility, nonmember_clearing_matter, other_identified_route, unresolved}` | request plus institutional rule interpretation | unresolved grants neither permission nor prohibition | all commitments |
| `facility_eligibility` | `{eligible, ineligible, not_applicable, disputed, unknown}` for the named facility | dated membership/rule determination | a gate applies only to its named facility | `DC-NYCH-01`, `DC-NYCH-03` |
| `request_authorization_evidence` | `{sufficient, incomplete, disputed, absent, unknown}` plus represented scope | documents/messages actually received | no mandate inferred from officer title | `DC-NYCH-01`, `DC-NYCH-02` |
| `financial_information_status` | `{not_received, incomplete, stale, adequate_for_scope, disputed, unknown}` plus `as-of` and provenance | submitted statements/examination material | no hidden Knickerbocker balance or future solvency judgment | `DC-NYCH-02`, `DC-NYCH-04` |
| `review_state` | `{not_open, collecting_information, examining, awaiting_forum, decision_ready, complete, closed}` plus competent interface and authoritative record identity | environment-owned institutional process event delivered to the Agent | not modeled as a random delay and not privately editable | `DC-NYCH-02`–`DC-NYCH-04` |
| `authority_state` | `{no_competent_authority_identified, committee_scope, membership_scope_required, authorized, denied, disputed, unknown}` with route/proposal scope and authoritative record identity | institutional rules and environment-owned dated decisions | unknown creates no authority; the Agent cannot create authority by changing its own memory | `DC-NYCH-02`–`DC-NYCH-04` |
| `resource_proposal_status` | `{none, information_needed, collateral_review, member_consultation, conditionally_authorized, scheduled, partial, failed, executed, withdrawn}` | environment-owned institutional/member process and result events | proposal is not member commitment or effect | `DC-NYCH-04`, `DC-NYCH-05` |
| `case_disposition_status` | `{none, pending, information_needed, referred, facility_declined, other_scoped_decline, conditioned_proposal, closed}` plus case, scope, reason, and issuing-authority references | environment-owned case/institutional decision record delivered to the Agent | a disposition is not message issue, delivery, counterparty acceptance, or resource effect | `DC-NYCH-05` |
| `case_communication_status` | `{not_issued, issued, transport_pending, delivered, expired, failed, unknown}` plus message, recipient, route, and event-time references | environment-owned issue and communication-transport records delivered to the Agent | issued is not delivered; delivered is not business acceptance or effect | `DC-NYCH-05` |
| `delivered_case_result` | `{none, delayed, partial, failed, executed, withdrawn}` plus typed reason and result reference | delivered authoritative execution/resource/process result | silence is no result; the result cannot rewrite the prior disposition or communication record | `DC-NYCH-05` |

#### Explicitly forbidden information

- Knickerbocker’s hidden true solvency, liquidity, or future suspension;
- unsubmitted internal records or collateral;
- NBC’s private reasoning and uncommunicated exposure;
- exact private state of every member bank;
- future Morgan coordination, October 26 certificate actions, or January 1908 rules;
- later depositor contraction and regression results as participant knowledge;
- the eventual severity of the panic; and
- Reference or evaluation-only material.

Public stress is not a complete institutional input by itself. It may become relevant only through a dated,
delivered member or market report whose role in a specific commitment is declared.

### Authoritative process state and participant decision state

The case, classification, review, authority, member/collateral commitment, case disposition, communication
issue/delivery, and realized result are authoritative institutional or environment-owned records. The Agent may propose a transition and retain the
last delivered record identity; it cannot privately mutate a second copy. Optional qualitative assessments and
the last-consumed record versions are Agent decision state and must remain declared and replayable.

| State | Owner | Initial condition | Legitimate updates | Behavioral consequence |
|---|---|---|---|---|
| case reference and receipt | environment-owned case process; Agent stores reference/version | none | delivered request and authoritative closure/withdrawal | prevents duplicate case creation and links messages |
| route and eligibility record | environment-owned classification process | unresolved | authorized classification using request and institutional facts | determines which scoped gate or procedure applies |
| information dossier | environment-owned case record; Agent observes scope/freshness | absent/incomplete | delivered statements, examination result, or verified correction | changes review sufficiency without revealing hidden truth |
| review/forum state | environment-owned institutional process | not open | authorized procedural event | distinguishes receipt, examination, consultation, and decision readiness |
| authority record | environment-owned governance process | no competent authority identified or unknown | dated committee/association decision | opens or closes only the scoped intent |
| resource-commitment record | environment/member-owned process | none | proposal, member/collateral process, authoritative result | prevents double commitment and separates authorization from realization |
| case disposition | environment-owned institutional/case decision record | none | authorized pending, information-needed, referral, scoped-decline, proposal, or closure event | determines what may be communicated and the visible business posture; does not prove delivery or effect |
| case communication status | environment-owned issue/transport record | not issued | authorized message issue plus transport adjudication, delivery, expiry, or failure | determines what the counterparty could observe and whether follow-up is due; does not change the disposition or result |
| procedural assessment posture | Agent decision state derived from delivered records | no assessment beyond current records | new information, classification, authority, or result observation | supports bounded choice without competing with institutional truth |

The Agent may form qualitative institutional assessments—such as information adequate for a limited route or
member obligations materially constrained—but these assessments must derive from participant-available
observations. It does not possess a generic willingness, benevolence, panic, or confidence state.

## 6. Behavioral model

### Decision procedure and determinacy

This Definition specifies a **constrained set-valued procedural policy**. Implementations may differ when the
historical record leaves more than one institutionally permitted response, but they must classify the same case
facts, apply the same scoped gates, satisfy the same minimum procedural response, and record why a remaining
choice was selected. Neither random delay nor indefinite abstention may substitute for missing governance.

| Decision stage | Required question | Minimum response class | Remaining choice |
|---|---|---|---|
| 1. establish a case | Has a request or authorized ordinary matter actually been delivered? | create or update one case record; otherwise record that no case is active | no substantive support response may precede receipt |
| 2. classify institutional position | What are membership, clearing relationship, named route, facility eligibility, and requester-authorization status? | classify known facts and request clarification for material unknowns | a fixed eligibility boundary applies only to the evidenced facility or jurisdiction |
| 3. establish information and forum sufficiency | Is current information adequate, and which institutional interface is competent? | request specified information, open/continue review, seek the competent forum, refer, or issue a typed pending status | hidden solvency and random delay are not alternatives |
| 4. enforce scoped authority | Has the competent committee, association, or other evidenced forum authorized the contemplated response? | seek authority, remain within ordinary process, or issue a scoped no-authority disposition | no proposal or decline may claim broader authority than the record supports |
| 5. form a procedural response | Given route, information, authority, duties, and existing commitments, what response class is available? | advance review, issue a scoped disposition/referral, or form a conditioned proposal when its prerequisites are met | the exact response may vary only inside the selected structural variant |
| 6. follow commitment and result | Has a proposal, member/collateral process, message delivery, or execution result changed? | update the case and communicate, close, reopen, or request follow-up on the delivered state | proposal, commitment, execution, and effect remain distinct |

Abstention is permitted only when no request or authorized matter exists, jurisdiction or a competent forum
cannot be established, necessary information cannot presently be requested or obtained, an identified process
is awaiting a named event, or no institutionally permitted response remains. The record must state the blocker
and the event that would reopen the case. Repeated abstention after a delivered request is classifiable,
information is adequate, authority is available, and no process is pending is inconsistent with this Definition
unless declared as a competing institutional hypothesis.

### Model invariants

Every implementation representing this Agent must:

1. Act only on a delivered request or an explicitly authorized ordinary institutional process.
2. Distinguish membership, clearing-through-member status, route, and facility eligibility.
3. Apply the shared fixed eligibility boundary only to the member facility or jurisdiction for which evidence
   establishes it.
4. Treat unresolved other-route authority as unknown, not as permission or prohibition.
5. Use only dated information and institutional state available to NYCH through an authorized channel.
6. Keep review, forum, authority, and resource commitments explicit and replayable.
7. Never replace missing information or procedure with a random gate, hidden solvency, or willingness score.
8. Emit only declared domain intents and never submit a world-state or member-resource effect.
9. Separate intent, delivery, institutional admissibility, member/collateral commitment, execution, and result.
10. Keep invalid, unauthorized, duplicate, and out-of-envelope attempts auditable.
11. Exclude future facts, later procedures, and evaluation material.

A violation is implementation nonconformance, not evidence for or against the historical hypotheses.

### Behavioral mechanisms

#### `M-NYCH-01` — membership- and route-conditioned action

Membership and the named route change the institutionally permitted process before resource preference is
considered. A proven member-only facility can exclude a nonmember without implying that every possible referral
or other route is universally prohibited.

The institutional basis is the 1906–1907 Section 25 membership/clearing distinction and Cannon's account of
committee authority and nonmember clearing arrangements (`NYCH-C01`, `NYCH-C02`, `NYCH-C05`–`NYCH-C07`).

Competing explanation: the observed refusal may have reflected temporary resource or information constraints
rather than a general facility rule.

#### `M-NYCH-02` — information-contingent examination and review

Request delivery is not completed review. Missing, stale, or disputed authorization and financial information
can produce information seeking, examination, forum escalation, status communication, or abstention. General
nonmember-clearing examination rules inform this mechanism but are not silently copied as the exact focal loan
procedure.

Cannon's examination, statement, security, and committee procedures support the general mechanism; the absent
focal minutes prevent their treatment as a reconstructed October 21 sequence (`NYCH-C03`, `NYCH-C04`,
`NYCH-C08`, `NYCH-C09`).

Competing explanation: a focal route rule may have made examination irrelevant to the named route.

#### `M-NYCH-03` — collective-resource stewardship

Where an authorized collective mechanism exists, the institution accounts for the distinction among
association procedure, member resources, collateral, existing commitments, and mutual obligations. It may
propose or condition action without owning its realization.

Cannon's institutional account supports the separation of association authorization, security review, and
member obligations; it does not establish that the focal nonmember request entered such a mechanism
(`NYCH-C02`–`NYCH-C04`, `NYCH-C08`).

Competing explanation: no competent NYCH route may have existed for the focal nonmember request, leaving no
resource-allocation choice.

#### `M-NYCH-04` — access as a bundled institutional mechanism

Clearinghouse access may affect crisis behavior through liquidity, monitoring, collective guarantee, and
signaling. These pathways remain distinguishable in the model even when an empirical membership indicator
bundles them.

Moen and Tallman's cross-sectional evidence motivates this bundled-access mechanism but neither identifies a
participant policy nor supplies a rescue probability (`NYCH-C11`, `NYCH-C12`).

Competing explanation: portfolio-loss beliefs or city/institution differences may account for part of the
observed deposit contraction.

#### `M-NYCH-05` — bounded procedural discretion

When rules and authority do not uniquely determine a response, the institution follows a limited procedure
based on available information, competent forums, existing commitments, and role duties. It does not optimize a
global system objective with perfect information.

This is a bounded-rationality modeling interpretation informed by Simon (1956), not a recovered NYCH decision
algorithm. Whether it applies to the focal request depends on whether a competent alternative route existed.

Competing explanation: direct focal records may show that no competent alternative route existed or that one
route rule uniquely determined the response, in which case this mechanism should be removed for the focal
situation.

### Structural alternative: evidenced route absence or bounded alternative-route discretion

The restriction on the named member facility is a **shared fixed boundary** in both interpretations. It is not
the source of the structural fork. The unresolved question is whether a separate, competent institutional route
could consider a nonmember-related proposal.

| Variant | Use | Meaning | Allowed response beyond shared facility classification | Evidence that would revise or select it |
|---|---|---|---|---|
| `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` | current conservative baseline | the adopted public evidence does not establish a competent alternative NYCH route, so the model does not invent one; this is not proof of categorical historical prohibition | information/status communication, scoped facility decline, authority clarification, or an evidenced external referral | focal rule, minutes, or precedent identifying a competent alternative route would retire this baseline for the affected situation |
| `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` | structural-sensitivity variant | the named member facility remains unavailable, while a separately identified competent forum may consider another institutionally permitted proposal under information, authority, resource, and member constraints | review, information request, forum escalation, conditioned alternative proposal, supported decline, referral, or bounded abstention | focal rule, minutes, or precedent establishing or excluding such a competent route would narrow or retire the variant |

`NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` is the current baseline;
`BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` is retained only for structural sensitivity. One variant must be selected
and recorded before behavior is generated. They may never be mixed into a rescue probability, switched silently
inside one run, or selected from the known historical outcome. Neither variant is a historically validated
reconstruction of the October 21 procedure.

### Decision Commitments

#### `DC-NYCH-01` — receive and classify a request without treating delivery as acceptance

**Situation.** A support-related request is delivered to an NYCH interface.

**Basis.** `M-NYCH-01` and `M-NYCH-02`; direct rules support the membership and nonmember-clearing distinctions,
while the focal request's forum, dossier, and review sequence remain unresolved.

**Authorized information and state.** `delivered_request`, `relationship_status`, `route_classification`,
`facility_eligibility`, and `request_authorization_evidence`.

**Alternatives.** Record/classify; request clarification; identify a competent forum; request information;
refer; or abstain.

**Hypothesis.** Institutional position and route alter the response category before any resource effect is
considered.

**Permitted intents.** `record_and_classify_request`, `request_case_information`,
`seek_procedural_authority`, `refer_request`, `communicate_case_status`, or abstention.

**Precedence.** Actual receipt, relationship and route classification, and requester mandate precede any
resource or policy consideration. An unresolved classification triggers a specified procedural response rather
than a substantive support disposition.

**Minimum response.** A delivered request must create or update one case and produce a classification record.
Materially missing route, relationship, or mandate information must be named and followed by clarification,
information seeking, authority seeking, referral, or a typed status. Silent receipt is not conforming.

**Abstention boundary.** Abstention is limited to a recorded absence of jurisdiction, competent forum, or
permitted next step. It must preserve the case and state what event could reopen it.

**Expected pattern.** Delivery precedes classification and no resource state changes. **Forbidden pattern:**
actor name fills membership/route/authority. **Falsifier:** swapping membership or route leaves the institutional process
unchanged where the model claims it matters.

#### `DC-NYCH-02` — proceed under incomplete information or authorization

**Situation.** The case is identifiable, but financial information, requester mandate, or competent authority is
incomplete, stale, disputed, or absent.

**Basis.** `M-NYCH-02` and `M-NYCH-05`; general examination and governance records support information-contingent
procedure, but do not establish the exact focal loan process.

**Authorized information and state.** `financial_information_status`, `request_authorization_evidence`,
`review_state`, and `authority_state`.

**Alternatives.** Request specified information; open/continue examination or review; seek the competent forum;
communicate pending status; refer; or abstain.

**Hypothesis.** Information and procedural state produce observable intermediate actions rather than an
immediate unsupported terminal choice.

**Permitted intents.** `request_case_information`, `open_or_continue_review`, `seek_procedural_authority`,
`communicate_case_status`, `refer_request`, or abstention.

**Precedence.** Institutional jurisdiction and authority bind first; material information sufficiency governs
the scope of any later disposition. System pressure cannot replace either prerequisite.

**Minimum response.** The implementation must identify which information or authority is insufficient and then
request it, advance a competent review, seek the forum, refer the matter, or communicate a typed pending state.
A random or unexplained delay is not a response.

**Abstention boundary.** Abstention is conforming only when the missing item cannot presently be requested, no
competent forum or referral can be identified, or an active process is awaiting a named event.

**Expected pattern.** Information/authority events visibly precede a substantive disposition. **Forbidden
pattern:** hidden solvency or random delay fills the gap. **Falsifier:** missing or fresh information produces
identical behavior in all otherwise equal cases.

#### `DC-NYCH-03` — enforce the named facility boundary without inventing universal authority

**Situation.** Membership and the requested facility are established; the applicant is ineligible for the named
member facility, while other-route authority may remain unresolved.

**Basis.** `M-NYCH-01`; the member-facility distinction is supported, whereas a universal
nonmember-support prohibition is not established by the adopted sources.

**Authorized information and state.** `route_classification`, `facility_eligibility`, and scoped
`authority_state`.

**Alternatives.** Issue a typed facility decline through a competent interface; seek authority clarification;
refer to an evidenced route; communicate the boundary; or abstain.

**Hypothesis.** A facility gate changes the intent envelope structurally, but it does not settle an unproven
other route.

**Permitted intents.** `issue_typed_decline`, `seek_procedural_authority`, `refer_request`,
`communicate_case_status`, or abstention.

**Precedence.** The evidenced facility gate controls that facility before resource preference or system
pressure. It has no precedence outside its proven scope; unresolved other-route authority remains unknown.

**Minimum response.** Once ineligibility for the named member facility is established, the institution must
communicate the scoped boundary through a competent interface or, when other-route authority remains material,
seek clarification or make an evidenced referral. It cannot silently treat nonmembership as a universal result.

**Abstention boundary.** Abstention is limited to cases where no competent issuing interface or evidenced
referral exists; the facility classification and unresolved wider authority must still be recorded.

**Expected pattern.** The decline names its facility and reason. **Forbidden pattern:** “nonmember” becomes a
universal rescue prohibition or a probability. **Falsifier:** direct focal evidence establishes a different
scope or a unique rule.

#### `DC-NYCH-04` — form a conditioned collective or member-related proposal

**Situation.** A competent route and authority exist, information is adequate for scope, and a proposal may
require collateral, member consultation, or bounded commitments.

**Basis.** `M-NYCH-02`–`M-NYCH-05`; the general institutional mechanisms are evidenced, while applying a
collective proposal path to the focal nonmember request applies only under
`BOUNDED_ALTERNATIVE_ROUTE_DISCRETION`, selected before the model run.

**Authorized information and state.** `financial_information_status`, `review_state`, `authority_state`, and
`resource_proposal_status`.

**Alternatives.** Request collateral/information; seek member or association authorization; propose a conditioned
measure; delay; communicate; or abstain.

**Hypothesis.** Proposal content and timing respond to information, authority, and existing commitments rather
than a generic rescue preference.

**Permitted intents.** `request_case_information`, `seek_member_or_association_authorization`,
`propose_conditioned_measure`, `communicate_case_status`, or abstention.

**Precedence.** The frozen structural variant, competent authority, information sufficiency, and existing
commitments bind before a collective-resource objective. No urgency score can override those conditions.

**Minimum response.** Under `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION`, a competent route, adequate scoped
information, and available authority require the case to advance through a conditioned proposal, a necessary
member/association authorization step, a specifically identified condition request, or a typed supported
disposition. Indefinite delay is not conforming. Under
`NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`, this commitment is not applicable unless new evidence first
establishes a competent route.

**Abstention boundary.** Abstention requires a named unresolved commitment, condition, forum, or resource
constraint and a revisit event. It cannot replace a decision after all declared prerequisites are satisfied.

**Expected pattern.** Proposal precedes and remains distinct from member commitment and execution. **Forbidden
pattern:** NYCH directly spends member resources. **Falsifier:** resource/procedure conditions never change
proposal behavior, or focal evidence shows no competent route.

#### `DC-NYCH-05` — issue a typed disposition, communicate it, and follow later results

**Situation.** A competent process has produced a new case disposition; the associated communication has been
issued, delivered, delayed, expired, or failed; or a later authoritative execution/resource result has been
delivered.

**Basis.** `M-NYCH-02`–`M-NYCH-04`; explicit case, disposition, communication, and result lifecycles are
modeling requirements needed to keep institutional decision, counterparty information, member commitment,
execution, and effect analytically distinct.

**Authorized information and state.** `case_disposition_status`, `case_communication_status`,
`resource_proposal_status`, and `delivered_case_result`.

**Alternatives.** Issue or communicate the typed disposition; request follow-up information; address a failed or
expired communication through a permitted route; maintain or close review; reconsider only through an authorized
new event; abstain when no communication or follow-up is due.

**Hypothesis.** A case disposition changes NYCH's authoritative case posture; the counterparty can adapt only
after the corresponding message is delivered; and NYCH's later behavior differs among communication failure,
pending status, and delayed, partial, failed, executed, or withdrawn results.

**Permitted intents.** `communicate_case_status`, `issue_typed_decline`, `refer_request`,
`request_case_information`, `close_or_reopen_review`, or abstention.

**Precedence.** The authoritative case disposition determines what may be truthfully communicated. Communication
status determines whether delivery-dependent follow-up is due but cannot rewrite the disposition. A newer
authoritative execution/resource result supersedes the prior resource-process posture without erasing either the
disposition or communication history. Every action remains bounded by the issuing forum.

**Minimum response.** A new case disposition must produce the corresponding authorized communication act or a
recorded absence of a competent route/interface. A failed or expired communication must remain visible and
produce a permitted retry, route clarification, maintained failure state, or a scoped no-further-action record.
A newly delivered execution/resource result must update the case and produce the applicable follow-up,
communication, closure, or authorized reopening. A prior proposal may not remain the visible terminal state after
a delayed, partial, failed, executed, or withdrawn result.

**Abstention boundary.** Abstention is conforming only when no new communication or follow-up is due, or no
competent issuing/delivery path exists. The current disposition, communication status, blocking condition, and
revisit event must remain recorded.

**Expected pattern.** Case disposition, message issue, transport adjudication, message delivery, execution/result,
and later observation occur as distinct linked records. **Forbidden pattern:** a disposition is treated as
delivered, or a proposal immediately rescues the requester. **Falsifier:** communication status or result class
has no behavioral or trace consequence.

## 7. Intent and result boundary

The entries below are **modeled institutional capabilities** unless a nearby citation or worked-case label
identifies a reconstructed action. Reader-facing labels carry the argument; stable semantic identifiers in
parentheses support later mapping without turning the Definition into a wire contract.

| Reader-facing intent (semantic ID) | Required semantic content | Lifecycle and duplication | Result the Agent may not declare |
|---|---|---|---|
| Record and classify a request (`record_and_classify_request`) | case identity, sender/channel, represented institution, membership, named route, unresolved fields | one active case per business-equivalent request unless explicitly linked | request accepted or support available |
| Request case information (`request_case_information`) | case identity, requested information, `as-of` requirement, authorized recipient | may remain pending; later material must be evaluated for freshness/scope | information received, complete, or favorable |
| Open or continue institutional review (`open_or_continue_review`) | case identity, competent reviewing interface, scope, current information state | review state changes only through authorized process | review completed or decision made |
| Seek procedural authority (`seek_procedural_authority`) | case/proposal identity, route, authority question, proposed forum | remains pending until authoritative resolution | authority granted or prohibition established |
| Seek member or association authorization (`seek_member_or_association_authorization`) | proposal identity, competent forum, requested collective/member commitment, conditions | vote/commitment process is separate | members agreed or resources committed |
| Refer a request (`refer_request`) | case identity, basis for referral, evidenced receiving route | referral delivery/acceptance separate | recipient accepted or will assist |
| Issue a scoped decline (`issue_typed_decline`) | case identity, scoped reason `{facility_ineligible, no_competent_authority, insufficient_information, not_approved, other_supported_reason}`, issuing authority | message delivery and business closure separate | all possible routes prohibited or requester failed |
| Propose a conditioned measure (`propose_conditioned_measure`) | proposal identity, authorized route, scope, conditions, collateral/information requirements, requested commitments, expiry | proposal, member commitment, scheduling, execution, and result are separate | funds transferred, collateral accepted, or system stabilized |
| Communicate case status (`communicate_case_status`) | case identity, truthful procedural state, issuing authority, audience | delivery and counterparty response separate | decision or effect beyond the stated status |
| Close or reopen review (`close_or_reopen_review`) | case identity, reason, authority, new event if reopening | closure does not erase prior record | external process cancelled or outcome changed |

Abstention is a recorded no-intent decision with a scoped reason: no delivered case, no jurisdiction, unknown
route, missing information, no competent authority, unresolved prior process, or no institutionally permitted
alternative. It is subject to the commitment-specific boundaries above and is not a universal default.

## 8. Operationalization and uncertainty

| Construct | Representation | Evidence and use |
|---|---|---|
| membership/clearing relation | dated categorical institutional facts | strongly supported by direct rules and records |
| facility and route | typed categorical relation | member-facility boundary supported; other-route authority unresolved |
| information sufficiency | qualitative category plus provenance and `as-of` | exact focal dossier unavailable |
| review/forum/authority | categorical procedural state | general interfaces supported; October 21 sequence unavailable |
| resource commitment | proposal/commitment/result lifecycle with typed conditions | no single NYCH-owned resource scalar |
| case disposition | scoped business state with reason and issuing authority | distinct from communication transport and resource result |
| case communication | issue/delivery lifecycle with message, route, recipient, and time references | delivery does not create acceptance or effect |
| collateral/amount | quantity, unit, valuation date, and route only when source/scenario provides them | focal values unidentified |
| member/system pressure | delivered aggregate or qualitative report when a commitment consumes it | no participant-visible global exact state |
| empirical membership effect | scholarly result only | about 20 percentage points in one cross-sectional specification; not a policy parameter |

Generic confidence, institutional fear, benevolence, willingness, rescue probability, and a modern central-bank
loss function are omitted.

## 9. Worked cases and falsification

### Case A — ordinary nonmember clearing administration (historically grounded baseline)

**Evidence class.** Historically grounded institutional baseline; it is not a reconstruction of the October 21
support decision.

**Decision-time situation.** A nonmember clears through a member under an approved relationship and supplies a
dated condition statement. No support request is delivered.

**Required response.** NYCH may administer, record, examine, or enforce the existing clearing relationship only
through the relevant ordinary procedure. It must not open a support case or emit a crisis-support disposition
merely because the calendar approaches October 21.

**Environment boundary.** Relationship validity, statement delivery, examination events, and any resulting
institutional status remain authoritative process facts rather than Agent-created outcomes.

**Perturbation.** Remove current statement information. Examination or information-seeking behavior may change;
membership does not.

### Case B — incomplete support request (illustrative)

**Evidence class.** Illustrative case used to test the modeled information and authority boundary.

**Decision-time situation.** A request arrives through an authorized channel but does not identify a route or
contain sufficient requester-authorization and financial information.

**Required response.** Under `DC-NYCH-01` and `DC-NYCH-02`, NYCH must create or update one case, name the missing
route, mandate, or information, and then request the specified material, identify or seek a competent forum,
refer the matter, or communicate a typed pending status. Generic abstention and a complete inferred solvency
assessment are not conforming responses.

**Environment boundary.** Delivery, dossier completion, forum formation, and authority are authoritative case
or governance events. The Agent cannot make them true by recording an assessment.

**Perturbation.** Add current, verified information but leave authority unresolved. Information review can
advance, but a resource proposal remains unauthorized and the next required response concerns forum or
authority.

### Case C — nonmember request for a member facility (reconstructed from outcome-known evidence)

**Evidence class.** Reconstructed, outcome-exposed facility-boundary case; it cannot serve as held-out
validation.

**Decision-time situation.** The requester's nonmembership and the named facility's member restriction are
established, while wider institutional authority is either unresolved or outside that facility.

**Required response.** A competent interface must communicate a scoped facility decline or, if other-route
authority is material, seek authority clarification or make an evidenced referral. The disposition must not
turn nonmembership into a universal claim that no support route could exist.

**Environment boundary.** Facility eligibility and the competence of an issuing or alternative forum are
institutional facts. The Agent supplies a scoped intent; the environment owns admissibility, delivery, and case
effect.

**Perturbation.** Change only membership to `member`. The shared facility boundary changes, but examination,
collateral, authority, and resource feasibility may still block or condition a proposal.

### Case D — other-route authority unresolved (structural sensitivity)

**Evidence class.** Structural-sensitivity case for the unresolved existence of a competent alternative route.

**Decision-time situation.** The named member facility is unavailable, while a differently specified support or
coordination route is proposed. One structural variant has been frozen for the model instance.

**Required response.** Under `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE`, NYCH must communicate that no competent
alternative NYCH route is established, seek an evidenced external referral, or record why neither interface
exists. Under `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION`, a separately identified competent forum must advance
review, request necessary information, seek authorization, form a conditioned proposal, or issue a supported
disposition. The variants must produce visibly different process paths and may not be blended into a
probability.

**Environment boundary.** The selected variant is a frozen construction choice; actual forum authority,
authorization, commitments, and execution remain environment-owned.

**Perturbation.** Supply direct evidence of a competent route. The conservative baseline is retired for that
situation; approval and execution still remain unresolved.

### Case E — authorized proposal with failed execution (illustrative)

**Evidence class.** Illustrative adverse-result case used to test proposal, commitment, execution, and result
separation.

**Decision-time situation.** A competent forum has authorized a conditioned proposal, but member commitments,
collateral, or feasibility later produce delay, partial realization, no effect, or failure.

**Required response.** Once the authoritative result is delivered, NYCH must update the case and issue the
corresponding communication, follow-up, closure, or authorized reopening. It must not continue to present the
proposal as a completed result or rewrite the prior authorization as if it never occurred.

**Environment boundary.** Member commitments, collateral acceptance, scheduling, transfer, and realized effect
remain outside the Agent. The Agent owns only its next procedural intent after observing the delivered result.

**Perturbation.** Hold authorization constant and change collateral admissibility. The result changes without
changing the Agent's ownership of the proposal.

### Cross-case falsification plan

| Test | Expected result | Failure meaning |
|---|---|---|
| actor-name erasure | behavior depends on membership, route, information, and authority, not historical name | hidden script |
| membership/route swap | the institutionally permitted process changes where the facility boundary applies | institutional semantics are decorative |
| missing-information test | information request, review, delay, or abstention replaces a fully informed disposition | hidden solvency or defaults drive behavior |
| authority removal | substantive proposal/decline narrows to authority seeking, referral, status, or abstention | governance is decorative |
| alternative-route structural fork | the conservative baseline and sensitivity variant produce different process paths while sharing the member-facility boundary | structural uncertainty or the shared boundary has been collapsed |
| resource ownership test | NYCH cannot directly commit or transfer member resources | association and members are conflated |
| intent/result ladder | proposal, member commitment, scheduling, partial/failure, and delivered result remain distinct | Agent owns environmental outcomes |
| protocol sufficiency | if one rule uniquely fixes the focal response, the Agent shrinks to a protocol for that situation | unnecessary behavioral complexity |
| aggregate/split test | internal actors are added only when independent information/intents explain a predeclared pattern | granularity is aesthetic rather than causal |

The model should be narrowed or rejected if focal minutes show that no alternative-route decision existed, if
review and authority never affect any prediction under the sensitivity variant, or if member/committee
heterogeneity is necessary but hidden inside the aggregate.

## 10. Limitations and references

### Assumptions, limitations, and withdrawal conditions

1. The aggregate procedural interface is a modeling simplification, not a claim of unanimous institutional
   preference.
2. Exact October 21 minutes, forum, information package, and authorization are unavailable within the public
   scope used here.
3. The request narrative is disputed across retrospective accounts.
4. The proven member-facility boundary is shared by both variants and does not resolve every other route.
5. October 26 loan-certificate and January 1908 rules are not used as October 21 procedure.
6. Member-bank resources and private decisions remain outside NYCH’s direct control.
7. NBC and private coordination are external to the two-role participant set.
8. The empirical access effect bundles mechanisms and does not identify a policy or causal probability.
9. `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` represents conservative non-invention of an unsupported capacity,
   not evidence of categorical historical prohibition.
10. The known refusal and later outcome are exposed and cannot validate either structural variant or the wider
    model.
11. Cross-event portability, historical calibration, and system-level causal sufficiency are not claimed.

Withdraw or materially revise:

- `M-NYCH-02` for the focal route if original minutes show no information/review role;
- `M-NYCH-03` if no competent collective-resource route existed;
- `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` if direct rules exclude every modeled alternative route;
- `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` for any situation in which direct evidence establishes an
  authorized alternative route;
- the aggregate representation if separate committees/members require independent observations and intents;
  and
- any procedural state imported only from the later October 26 mechanism.

### References

- Cannon, James G. 1910. *Clearing-House Methods and Practices*. Washington, DC: Government Printing Office.
- Columbia University Rare Book & Manuscript Library. 2025. *New York Clearing House Association Records,
  1853–2006: Finding Aid*.
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
