# Lincoln Trust Company

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | Lincoln Trust Company |
| Modeled role | thin board-authorized institutional communication interface for verifying, authorizing, issuing, withholding and correcting a dated company-condition statement |
| Event and interval | H2EPR-0288, Panic of 1907 acute New York phase, approximately 23–26 October 1907 |
| Primary decision situations | officer/public-communication proposal; missing or disputed condition information; scoped board authorization; message issue/delivery uncertainty; materially changed information requiring correction |
| Decision cadence | event-driven by communication proposals, dated condition reports, governance records, transport results and material corrections |
| Decision form | constrained set-valued governance-and-communication policy |
| State authority | condition, board authorization, message and transport truth is scenario/institutional-process owned; the Agent retains only declared communication posture and references to delivered records |
| Evidence and model status | narrow event-bound construction using one directly supported board-authorized focal communication plus explicit evidence-unavailability findings; no reconstructed support, collateral or operating policy |
| Definition identity | `h2epr.agent-definition.0288.lincoln-trust-company`, version `0.1.0` |

This Agent models one small but causally meaningful interface: whether Lincoln
authorizes and issues a bounded public statement about its asserted condition.
It does not become a reduced TCA Agent. The difference in repertoire reflects
the evidence, not lower documentation quality.

The model asks whether board authority, dated information, issue, delivery,
claim accuracy and public effect can remain separate. It does not explain
Lincoln's assistance, collateral, internal liquidity allocation, service
operation, depositor behavior or ultimate survival.

## 2. Historical participant and representation

Lincoln was a separate trust company facing substantial withdrawals after the
Knickerbocker suspension (`LTC-C01`). Contemporary reporting states that on
October 25 its board authorized Louis Stern to say that the company could meet
demands, was in a stronger position and was seeing declining withdrawals
(`LTC-C02`–`LTC-C03`).

The Agent represents the **authorized institutional communication interface**,
not the board's full governance, Stern's personality, every officer, the
company's treasury, depositors or support providers. It aggregates:

- receipt and verification of a proposed condition statement;
- a scoped board/competent-body authorization decision;
- issue, narrowing, withholding or correction of the statement; and
- response to transport or updated-information records.

Later accounts report assistance but do not reveal the company-side request,
authority, terms, collateral or policy (`LTC-C04`–`LTC-C05`). Those acts remain
outside this Agent. Broaden or split the representation only when direct
evidence establishes an autonomous Lincoln support, resource, operating or
independently acting governance interface.

## 3. Evidence and theoretical foundation

### Evidence

| Evidence | Supports | Does not support |
|---|---|---|
| `LTC-C01`, `BASE-S03`, `P4-S01` | distinct institution and withdrawal context | exact decision-time condition or policy |
| `LTC-C02`–`LTC-C03`, `BASE-S03` | board authorization, named spokesperson and reported statement content | objective truth, exact information reviewed, publication effect or broad board policy |
| `LTC-C04`, `P4-S01`, `R2-S03` | exposed outside reports of assistance and possible Morgan-related context | Lincoln request, authorization, route, collateral or behavior |
| `LTC-C05`–`LTC-C06` | bounded evidence absence and communication lifecycle | permission to import TCA mechanisms |

The focal statement and later outcome are `FULL_DRAFT_EXPOSED`. The statement
is evidence of an authorized communication action and participant claim, not
evidence that its content was true or effective.

### Theory and translation

Simon (`TH-C01`–`TH-C03`) supports bounded action under incomplete information;
it supplies no Lincoln-specific cognition. The operative translation is:

```text
board-authorized officer statement
  -> governance and spokesperson are distinct
  -> content needs dated support and scoped authority
  -> authorization, issue, delivery, accuracy and effect remain separate

missing support/application evidence
  -> absence is a representation constraint, not permission to generalize
  -> support and collateral remain scenario-owned
  -> the Agent stays thin until direct evidence changes the boundary
```

Withdrawing `LTC-C02` would remove the current autonomous interface and return
Lincoln to a scenario-owned participant record.

## 4. Institutional role and relationships

The interface's sole mandate is to decide whether a proposed Lincoln condition
statement can be verified and issued under competent authority. It must not
create a generic institutional objective such as “restore confidence.”

| Object | Agent may | Agent may not |
|---|---|---|
| proposed statement | verify, narrow, authorize, withhold or correct | infer truth from reassuring language |
| governance | consume a scoped board/competent-body record and propose a decision | infer authority from Stern's title or create a board decision privately |
| company information | use dated records legally delivered to the interface | read hidden cash, future withdrawals or eventual assistance |
| message | authorize/issue with audience, source and `as-of` | control transport, public receipt, belief or effect |
| support/resources/operations | observe a delivered public/result record if relevant to communication | request aid, pledge collateral, change service capacity or transfer resources |

The board or competent institutional process owns authorization; Stern is the
named spokesperson; the scenario owns condition records, message transport,
public availability and effects. Depositors own their responses.

## 5. Decision situations, information, and state

### Activation and observations

| Observation | Meaning/channel | Domain/freshness/missing behavior | Consumers |
|---|---|---|---|
| `condition_statement_proposal` | proposed claims, audience, spokesperson, purpose and `as-of` | one proposal/version; missing scope or source triggers clarification | `DC-LTC-01` |
| `lincoln_condition_information` | dated records or authorized summaries cited by the proposal | typed qualitative/interval facts with provenance and uncertainty; stale/disputed items trigger verification/narrowing | `DC-LTC-01`–`DC-LTC-03` |
| `communication_decision_authority` | scoped record identifying the board/body competent to decide the proposed statement | `{competent_to_decide, pending, denied_scope, disputed, absent, unknown}`; unknown grants no decision authority | `DC-LTC-01` |
| `statement_authorization_state` | authoritative result of the competent interface's decision on one statement version | `{none, pending, authorized, narrowed, withheld, superseded, disputed}`; applies only to its exact content/scope | `DC-LTC-02`–`DC-LTC-03` |
| `message_lifecycle` | authoritative proposal/authorization/issue/transport/delivery/expiry/failure record | linked identity and event time; silence is no delivery | `DC-LTC-02`, `DC-LTC-04` |
| `material_information_update` | later delivered correction or changed condition relevant to an issued/pending statement | source, scope, `as-of`, relationship to prior claim | `DC-LTC-03` |

Forbidden information includes hidden world condition, other institutions'
state, undelivered assistance, exact future withdrawals, eventual survival,
later governance developments, depositor beliefs, Reference EPG and evaluation
evidence.

| Persistent state | Owner | Update | Consequence |
|---|---|---|---|
| condition record | scenario/company information process | dated report/correction | factual input, not private truth |
| decision-authority record | company governance process | identify, deny, dispute or supersede the competent forum/scope | determines who may decide; is not the statement decision |
| statement-authorization record | authoritative institutional process after Agent intent | authorize, narrow, withhold, supersede or dispute one proposal version | governs issue of exact content |
| message record | scenario/transport | proposal, issue, delivery, failure, expiry | preserves lifecycle |
| `communication_posture` | Agent decision state | delivered proposal, authority, information or result | `{verifying, awaiting_authority, authorized, withheld, issued, correction_due, closed}` |
| last-consumed versions | Agent | consumed record | replay and stale-input control |

## 6. Behavioral model

### Decision procedure

1. Confirm that a communication proposal exists and is within the narrow
   Lincoln interface.
2. Identify every material claim, its source, `as-of`, uncertainty and current
   freshness.
3. Establish the competent decision forum and spokesperson scope, then keep its
   statement-authorization result separate.
4. Authorize or narrow/withhold the proposal; after that result is delivered,
   issue it, request specified information/authority, or close with a reason.
5. Keep issue, delivery and effect separate.
6. When a material update arrives, decide whether to correct, update, withdraw
   a pending issue or request further verification.

A valid proposal with current information and competent authority must receive
a governance response. Abstention is limited to a named information,
authority, scope or transport blocker with a reopening event.

### Invariants

1. Every material claim has source, `as-of`, uncertainty and authority.
2. Officer proposal and board authorization are distinct.
3. Authorization, issue, delivery, truth and effect are distinct.
4. A reassuring claim is not an authoritative condition state.
5. Support, collateral, operating and resource intents are outside the Agent.
6. Only delivered information/results update behavior.
7. Invalid or unauthorized messages remain visible.
8. No hidden threshold, future fact or generic confidence objective is used.

### Mechanisms

#### `M-LTC-01` — governance-gated communication

An institutional statement requires a competent, scoped authorization rather
than a title or generic communications role (`LTC-C02`). The mechanism is
falsified if removing authority never changes issue behavior.

#### `M-LTC-02` — dated claim verification

Claims are limited to current delivered information and may be narrowed,
withheld or corrected when evidence is missing or disputed (`LTC-C03`). It is
not a truth-estimation model. A competing explanation is that the focal board
statement was purely ceremonial; direct minutes could narrow discretion.

#### `M-LTC-03` — non-self-realizing communication

A message can alter the event only through scenario-owned issue, delivery and
audience response (`LTC-C06`). This is a causal-boundary mechanism, not a claim
that the historical statement changed withdrawals.

### Decision Commitments

#### `DC-LTC-01` — review a proposed condition statement

**Situation.** A responsible interface submits a proposed statement.
**Basis.** `LTC-C02`–`LTC-C03`, `M-LTC-01`–`02`. **Information.** Proposal,
claim-level supporting records, spokesperson and decision authority. **Alternatives.**
Request information; seek authority; authorize; narrow; withhold; close.
**Intents.** `request_condition_information`,
`authorize_condition_statement`, `narrow_or_withhold_condition_statement`.
**Minimum response.** Identify the disposition of each material claim and the
competent decision scope. **Precedence.** Verifiability and decision authority precede desired
reassurance. **Abstention.** Only while a named report or authority event is
pending. **Forbidden.** Name/title supplies authority or truth. **Falsifier.**
Stale/disputed information never changes the statement. **Deletion.** Would
collapse governance into automatic publication.

#### `DC-LTC-02` — issue an authorized statement

**Situation.** A scoped statement-authorization result is delivered and its
approved content remains current. **Basis.**
`LTC-C02`, `M-LTC-01`, `M-LTC-03`. **Information.** Statement-authorization record, authorized content,
spokesperson, audience, issue route and message status. **Alternatives.** Issue;
request route clarification; withhold if authority/content is superseded;
close. **Intent.** `issue_authorized_condition_statement`. **Minimum response.**
Issue once or record the precise route/supersession blocker. **Precedence.**
Current authorization and content version bind. **Forbidden.** Issue means
delivered, believed or effective. **Falsifier.** Delivery failure is treated as
public receipt.

#### `DC-LTC-03` — correct or update a statement

**Situation.** A material delivered update contradicts or supersedes pending
or issued content. **Basis.** `LTC-C03`, `M-LTC-02`. **Information.** Prior
message, new record, scope, date and authority. **Alternatives.** Request
verification; authorize a correction/update; withdraw pending issue; record no
new public statement. **Intents.** `authorize_correction_or_update`,
`request_condition_information`,
`narrow_or_withhold_condition_statement`. **Minimum response.** Record how the
new information affects each material prior claim. **Forbidden.** Edit the old
message or trace. **Falsifier.** Contradiction never changes posture.

#### `DC-LTC-04` — follow message delivery

**Situation.** Issue occurred but transport/delivery is pending, failed or
disputed. **Basis.** `LTC-C06`, `M-LTC-03`. **Information.** Message identity and
authoritative transport result. **Alternatives.** Request clarification;
reissue only under current authority; close after delivered/expired result.
**Intent.** `request_message_delivery_clarification` or an authorized reissue.
**Minimum response.** Preserve issue and delivery as distinct. **Forbidden.**
Invent public knowledge or effect. **Falsifier.** All delivery states produce
the same trace and later information environment.

## 7. Intent and result boundary

| Intent | Required content | Lifecycle | Agent may not declare |
|---|---|---|---|
| `request_condition_information` | proposal/message, specified claim/item, source/producer and revisit event | pending until delivered/refused/expired | information obtained or true |
| `authorize_condition_statement` | proposal version, approved claims, sources, `as-of`, audience, spokesperson and scoped authority | authorization can be superseded; issue separate | message issued/delivered or claims true |
| `narrow_or_withhold_condition_statement` | proposal, removed/withheld claims, reason, authority and revisit event | affects current proposal only | public knows it was withheld |
| `issue_authorized_condition_statement` | authorization/message identity, exact content, audience, route and event time | issue/delivery/effect separate; duplicate issue visible | delivery, belief, lower withdrawals or solvency |
| `authorize_correction_or_update` | prior message, new information, corrected content, authority and `as-of` | creates a new linked message | earlier trace erased or correction delivered |
| `request_message_delivery_clarification` | message, disputed transport state and requested evidence | cannot overwrite prior issue/result | delivery occurred |
| `close_communication_matter` | matter, scoped reason and later reopening condition | no effect on unmodeled support/operations | company stabilized or all matters closed |

Any support, collateral, resource or operating output is out of domain and must
remain visible as nonconformance rather than be adapted silently.

## 8. Operationalization and uncertainty

| Construct | Representation | Status/use |
|---|---|---|
| claim support | claim-to-dated-record links with uncertainty and `as-of` | direct statement known; exact underlying board information unavailable |
| decision authority | scoped categorical competent-forum record | focal board competence is supported; no general delegation |
| statement authorization | exact proposal-version disposition | distinct from authority to decide and from message issue |
| freshness | event-time relation between source and message version | qualitative per claim; no arbitrary numeric expiry required |
| communication posture | finite replayable process state | modeling necessity, not historical office workflow |
| message result | typed issue/delivery/failure/expiry record | scenario-owned |

There is no Lincoln solvency score, confidence target, withdrawal threshold,
support propensity or reassurance intensity. Missing information remains
unknown and narrows content.

## 9. Worked cases and falsification

### Case A — focal board-authorized statement (`RECONSTRUCTED / EXPOSED`)

**Situation.** A proposal attributed to Louis Stern contains bounded claims
about capacity and recent withdrawal direction; dated information and board
authority are delivered. **Required response.** Verify claim scope, authorize
and issue or narrow/withhold unsupported content. **Boundary.** Accuracy,
delivery and depositor response remain external. **Perturbation.** Remove board
authority; issue becomes prohibited until authority is obtained.

### Case B — stale information (`ILLUSTRATIVE`)

**Situation.** The proposal cites an older condition report and a newer report
is missing. **Required response.** Request current information, narrow claims or
withhold; do not reuse the exposed historical statement automatically.
**Perturbation.** Deliver current corroborating information; authorization
becomes admissible but truth/effect remain external.

### Case C — issue without delivery (`ILLUSTRATIVE`)

**Situation.** An authorized message is issued but transport fails. **Required
response.** Preserve issue, request clarification/reissue if authorized, and do
not expose content to the public observation layer. **Perturbation.** Deliver
successfully; only then may the scenario make it public.

### Case D — corrective update (`COUNTERFACTUAL PROCESS TEST`)

**Situation.** A fresh authorized report materially contradicts an issued
claim. **Required response.** Review and authorize a correction/update,
request verification or record a reasoned no-new-message decision. **Boundary.**
The old message remains immutable. **Perturbation.** Remove materiality; no
correction is required merely for cosmetic change.

| Falsification test | Expected | Failure |
|---|---|---|
| name erasure | governance/information, not Lincoln name, drive policy | hidden historical script |
| authority removal | message cannot issue | officer/title authority leak |
| stale-information test | verification/narrowing/withholding appears | evidence decorative |
| issue/delivery split | failed transport prevents public observation | message self-realizes |
| TCA-state injection | no effect on Lincoln communication policy | copied cross-role behavior |
| support-intent attempt | remains visible as out of domain | representation silently broadened |
| future-fact injection | later assistance/survival excluded | temporal leakage |
| always-abstain | complete authorized proposal receives response | empty policy |

## 10. Limitations, references, and provenance

### Limitations and withdrawal conditions

1. The exact records reviewed by Lincoln's board are not recovered.
2. The model does not reconstruct the board's full procedure or internal vote.
3. Assistance reports are exposed external outcomes; no company-side request,
   collateral, resource or operating policy is modeled.
4. Message accuracy and causal effect are not established.
5. No numerical policy, historical calibration, predictive validity,
   cross-event reuse or independent validation is claimed.

Return Lincoln to a scenario-owned process if the board statement proves
mechanically fixed with no meaningful choice. Broaden or split only if direct
evidence establishes autonomous support, resource, operational or separate
governance decisions. Never broaden it by copying TCA.

### Design provenance

Version `0.1.0` is the first accepted R2 Roster-production Definition. It is
deliberately narrower than the Morgan and TCA candidates because the bounded
evidence supports a narrower causal interface. It derives from the accepted
roster and semantic skeleton, the evidence ledger candidate and H2EPR
ten-module template, not from simulation or a desired historical action.

### References

- *Commercial and Financial Chronicle*. October 26, 1907.
- Moen, Jon R., and Mary Tone Rodgers. 2022. “How J. P. Morgan Picked the
  Winners and Losers in the Panic of 1907.” *Essays in Economic & Business
  History* 40: 156–187.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*.
