# Trust Company of America

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | Trust Company of America (TCA) |
| Modeled role | authorized company-level interface for condition verification, scoped disclosure and examination consent, route-specific support seeking, collateral proposals, operating-posture choices, communication, and response to delivered results |
| Event and interval | H2EPR-0288, Panic of 1907 acute New York phase, approximately 22–26 October 1907 |
| Primary decision situations | materially changed withdrawal/liquidity condition; request for company information or examination; support-route formation; collateral proposal; payment-service posture; public condition statement; delivered assistance or operating result |
| Decision cadence | event-driven by dated condition reports, authority records, examination requests/results, support-route events, resource/collateral information, service-condition reports, communication proposals and delivered results |
| Decision form | constrained set-valued institutional policy with route-specific request lifecycles and explicit information, governance, resource, operational and communication boundaries |
| State authority | condition, request, examination, collateral control, service, communication, resource and result truth is scenario-owned; the Agent retains declared decision posture and references to delivered records |
| Evidence use and explanatory scope | Contemporary reports and retrospective participant testimony informed an event-bound reconstruction; exact governance, participant-time values, and numerical policy remain unresolved |

This Definition represents the choices made through TCA's authorized
institutional interface while the company faced large withdrawals and sought
information, examination, operating and support responses. It separates the
company's actions from depositors, examiners, assistance committees, Morgan,
supporting institutions, payment mechanics and realized resource effects.

Its central research questions are:

1. How do liquidity, asset value, pledgeability and service pressure remain
   distinct in institutional decision making?
2. How can TCA disclose information and consent to examination without owning
   the examiner's finding?
3. How do multiple support routes retain separate requests, terms, collateral
   packages and results?
4. How can operating and communication choices be modeled without treating
   the known continuation of TCA as proof that the choices were correct?

## 2. Historical participant and representation

TCA was a distinct New York trust company led publicly by president Oakleigh
Thorne (`TCA-C01`). Thorne later described company-side choices to supply a
daily statement, consent conditionally to examination, open records to
examiners, increase paying capacity, seek support through different routes and
offer company notes and collateral (`TCA-C02`–`TCA-C06`). A contemporary public
statement attributed to him distinguished immediate liquidity from valuable
but illiquid collateral (`TCA-C07`).

The Agent is an **aggregate procedural institutional interface**. It includes
only the authorized company functions necessary to:

- verify and assess dated company condition information;
- authorize a scoped disclosure or examination consent;
- open, revise, withdraw and follow route-specific assistance requests;
- propose company-controlled collateral or terms;
- propose or authorize an operating-posture change;
- authorize and issue a bounded institutional statement; and
- respond to delivered examination, assistance, communication and operating
  results.

It does not represent Thorne's personal psychology, every director or officer,
depositors, examiners, Morgan or his associates, the five-person committee,
supporting banks and trust companies, payment clerks, resource providers or
the public. Exact focal board delegation is unavailable (`TCA-C09`), so every
material intent carries scoped authority rather than inferring power from
Thorne's title.

Split the Agent if direct records show behaviorally independent board,
management, treasury or communications bodies with different information and
interacting decisions. Narrow it if a supposed choice proves mechanically
fixed by an external assistance or operating protocol.

## 3. Evidence and theoretical foundation

### Event-specific evidence

| Evidence | Supports | Does not support |
|---|---|---|
| `TCA-C01`, `BASE-S03`, `R2-S01` | company identity and Thorne's office | all-company cognition or unrestricted presidential authority |
| `TCA-C02`–`TCA-C03`, `R2-S01` | daily statement, conditional examination consent, records/assets supplied | objective solvency, examiner conclusion or exact board mandate |
| `TCA-C04`, `R2-S01` | reported expansion from one to seven paying windows | fixed window count, queue policy, payment effect or universal operating rule |
| `TCA-C05`–`TCA-C06`, `R2-S01` | separate support routes, notes and collateral proposals | recipient commitment, collateral sufficiency, actual funds or unique route priority |
| `TCA-C07`, `R2-S02` | dated public participant explanation of liquidity versus asset value | truth of the claim or audience response |
| `TCA-C08`–`TCA-C11` | exposed outcomes, governance gaps, lifecycle and parameter limits | permission to fit thresholds or reproduce continuation |

The 1911 hearing is retrospective participant testimony in an adversarial
setting. It is valuable for actions, distinctions and proposed routes but not
an independent finding of financial condition or motive. Reported run amounts,
support and continued operation were known during model construction.

### Theory and empirical research

Moen and Tallman (`TH-C04`) support separating cash liquidity, capital-based
solvency and clearinghouse access at the institutional level. Their results do
not supply TCA's policy or coefficients. Simon (`TH-C01`–`TH-C03`) motivates a
bounded-information procedure in which missing information, authority and
resource conditions generate search, fallback and explicit pending states
instead of perfect optimization.

### Evidence-to-mechanism translation

```text
daily statement + opened records
  -> company can disclose, examiner independently evaluates
  -> disclosure, examination, report and later aid remain separate

separate Morgan and Hanover routes
  -> assistance is route-specific, not one global rescue state
  -> requests, terms, pending state and results cannot overwrite one another

company notes/collateral proposals
  -> TCA can propose only assets it is authorized to control
  -> counterpart and reducer decide admissibility, value, transfer and effect

expanded paying windows + public liquidity explanation
  -> operational capacity and communication are autonomous but fallible choices
  -> neither creates cash, payment, audience belief or continued operation
```

Withdrawing the participant testimony would narrow the Agent to communication
and externally reported context. Withdrawing exact amounts changes worked
examples, not the qualitative mechanisms.

## 4. Institutional role and relationships

### Mandate and obligations

The represented interface manages a bounded institutional response to
withdrawal and liquidity pressure. It may preserve operations, obtain and
provide information, seek external terms, propose controlled collateral and
communicate. It must not misstate authority, use hidden world truth or declare
another participant's choice or resource effect.

| Object | TCA may | TCA may not |
|---|---|---|
| company information | verify, classify and provide a scoped authorized package | declare hidden world truth or examiner conclusion |
| examination | consent, condition consent, provide access, request scope/result clarification | appoint itself examiner or declare completion/finding |
| support request | create/update/withdraw one authorized route-specific request | create recipient acceptance or merge unrelated routes |
| company note/collateral | propose an authorized package and terms | self-value, self-accept, transfer or realize proceeds |
| operating posture | propose/authorize a company-side capacity or service posture | create staff, process queues, make payments or override resources |
| communication | authorize/issue a bounded dated claim | turn the claim into public receipt, truth, confidence or stability |
| delivered result | consume and adapt once | rewrite the prior request, proposal or world result |

### Relationships

- **Depositors:** create requests through a population/process; TCA does not own
  their motives or aggregate demand.
- **Examiners:** receive authorized information and own methods/findings.
- **Morgan/private coordination and assistance recipients:** receive distinct
  requests/proposals and independently decide replies.
- **Five-person committee:** owns application review, information calls and
  advice if the route is invoked.
- **Banks/trust companies/contributors:** own commitments and resources.
- **Scenario:** owns service demand, queues, staffing execution, collateral
  control/valuation, resource feasibility, transport, payment and results.

## 5. Decision situations, information, and state

### Activation

The Agent activates on a delivered material-condition notice; a request for
information or examination; a support-route/authority event; a resource or
collateral report; an operating-capacity report; a communication proposal; or
a delivered disposition/result. “Panic,” date, actor name and eventual survival
are not inputs.

### Observation interface

| Observation | Meaning/channel | Domain, freshness and missing behavior | Consumers |
|---|---|---|---|
| `participant_condition_notice` | dated participant-visible notice citing the company records/signals that require review | `{routine, changed, material_review_due, disputed, unknown}`; source/basis required; missing basis becomes unknown | `DC-TCA-01`, `DC-TCA-04`, `DC-TCA-05` |
| `company_condition_information` | dated cash/liquidity, asset category, obligation and service information authorized for management | typed categories/intervals with source and uncertainty; stale/disputed values trigger verification | `DC-TCA-01`, `DC-TCA-04`, `DC-TCA-05` |
| `governance_authority` | scope-specific board/officer/delegated authorization | `{authorized, pending, denied, disputed, absent, unknown}`; unknown grants no authority | `DC-TCA-01`, `DC-TCA-02`, `DC-TCA-03`, `DC-TCA-04`, `DC-TCA-05`, `DC-TCA-06` |
| `examination_request_or_result` | requester, scope, conditions, required package and delivered report | request/report lifecycle with producer and `as-of`; report not available before delivery | `DC-TCA-02`, `DC-TCA-06` |
| `support_route_state` | recipient, route, request identity, content, status, terms and expiry | separate per route; `{not_open, draft, submitted, pending, information_needed, conditioned, declined, withdrawn, closed}` | `DC-TCA-03`, `DC-TCA-06` |
| `collateral_control_information` | company authority/control over proposed note/security categories and dated description | qualitative/typed; valuation and eligibility remain external; missing control prevents proposal | `DC-TCA-03` |
| `service_condition` | delivered demand/capacity report available to authorized management | ordinal/interval with source/time; no global queue truth | `DC-TCA-04` |
| `communication_matter` | proposed audience, claims, sources, authority and `as-of` | content must be verifiable and scoped; stale/disputed claim is narrowed/withheld | `DC-TCA-05` |
| `delivered_case_result` | typed examination, assistance, collateral, communication or operating result | delayed/partial/failed/executed/withdrawn/disputed; linked to one process | `DC-TCA-06` |

### Forbidden information

The Agent cannot read depositor private states, exact future withdrawals,
hidden asset truth, examiner deliberation, recipient/contributor private
intentions, undelivered results, other institutions' resources, future
continuation/suspension, later accounts as event-time knowledge, Reference EPG
or evaluation data.

### Process and decision state

| State | Owner | Update | Consequence |
|---|---|---|---|
| company condition record | scenario/company information process | dated verified/corrected report | source for assessment, never hidden truth |
| governance record | company governance process | scoped authorization/denial/dispute | opens/closes a specific intent class |
| examination case | examiner/scenario | request, consent, package receipt, report, closure | separates disclosure from finding |
| support request per route | scenario/recipient | submission, receipt, terms, disposition, expiry | prevents duplicate/merged requests |
| collateral package | company proposes; scenario/counterparty adjudicates | proposal, verification, acceptance/rejection/result | separates offer from resource effect |
| service process | scenario | capacity and payment result | TCA may propose posture, not execute mechanics |
| communication record | governance/transport | authorize, issue, deliver, fail, expire | separates claim from public knowledge/effect |
| `institutional_response_posture` | Agent decision state | delivered information/process/result | `{verifying, disclosing, seeking_support, proposing_collateral, adapting_operations, communicating, following_result, closing}` |
| last-consumed versions | Agent | consumed authoritative record | replay/staleness control |

## 6. Behavioral model

### Decision procedure and determinacy

| Stage | Required question | Minimum response | Remaining choice |
|---|---|---|---|
| 1. verify activation | What dated participant-visible condition or process event requires response? | classify and identify source/basis; dispute or request clarification if insufficient | no hidden numerical activation |
| 2. establish authority | Which interface may disclose, consent, request, pledge, alter posture or communicate? | use scoped authority, seek it, or record a blocker | no authority from title alone |
| 3. separate information/resource concepts | What is known about cash, assets, pledgeability, obligations and service demand? | verify or express bounded qualitative assessment | no single solvency/stress score |
| 4. select route-specific response | Is information, examination, support, collateral, operating or communication action admissible? | emit at least one bounded response or named pending state | multiple lawful responses may remain |
| 5. preserve lifecycles | Is an equivalent request/proposal already pending, conditioned or closed? | update existing process or create a materially different route/version | no repeated identical request each tick |
| 6. follow result | What authoritative disposition/result arrived? | adapt only linked posture and communicate/revise/close | no self-declared effect |

The policy is constrained but set-valued. A valid material notice or process
event cannot be answered by indefinite abstention. Missing authority or
information must trigger a request, narrower action or named waiting event.

### Invariants

1. All condition inputs are dated, sourced and participant-visible.
2. Cash liquidity, asset value, pledgeability, service capacity and solvency
   are not one scalar.
3. Governance authority is scoped and replayable.
4. Disclosure and examination finding have different owners.
5. Each support route has its own request, terms, pending state and result.
6. TCA proposes collateral; counterpart/environment decides admissibility,
   value, transfer and effect.
7. Operating intent is not service execution or payment.
8. Communication is a fallible claim, not world truth or audience response.
9. Intent, issue/delivery, commitment, execution and result remain distinct.
10. Invalid and unauthorized attempts remain visible.
11. No hidden threshold, future outcome or evaluation evidence may drive policy.

### Mechanisms

#### `M-TCA-01` — information and examination cooperation

The company can provide scoped dated information and conditionally consent to
independent examination. The causal prediction is an observable information
and report sequence before any support result (`TCA-C02`–`TCA-C03`). A
competing account is that an external coordinator mechanically required the
sequence, leaving no TCA discretion; direct terms could narrow the mechanism.

#### `M-TCA-02` — route-specific support search

TCA can pursue distinct assistance routes with different recipients,
information and terms (`TCA-C05`). A delivered pending or conditioned state
changes only its route. The mechanism is falsified if all routes share one
hidden global rescue status or if duplicate requests have no consequence.

#### `M-TCA-03` — authorized collateral proposal

Company notes/assets may be proposed as collateral, but control, eligibility,
valuation, acceptance and realization are separate (`TCA-C06`). Remove or
narrow this mechanism if direct evidence shows that the package was wholly
formed by an outside party without company choice.

#### `M-TCA-04` — operational capacity adaptation

Management may propose or authorize a service-capacity response to delivered
demand (`TCA-C04`). The exposed seven-window report motivates the mechanism,
not a count or threshold. A competing explanation is that routine operating
protocol fixed the response; evidence of that would externalize it.

#### `M-TCA-05` — bounded public condition communication

TCA may issue an authorized, dated and fallible interpretation of its
liquidity/asset position (`TCA-C07`). It does not own truth or audience effect.
The mechanism is narrowed if the statement proves externally dictated or
unauthorized.

### Decision Commitments

#### `DC-TCA-01` — respond to a material condition notice

**Situation.** A sourced participant-visible condition notice is delivered.
**Basis.** `TCA-C04`, `TCA-C07`, `TCA-C11`; `M-TCA-04`–`05`. **Information.**
Condition notice, dated company information, authority and active processes.
**Alternatives.** Verify; seek information/authority; open/update a support
route; propose operating posture; prepare communication; or record a blocker.
**Minimum response.** Name the condition and select at least one bounded
response or a specific missing item/revisit event. **Permitted intents.**
`verify_institutional_condition`, `request_information_or_terms`,
`open_or_update_support_request`, `propose_operational_capacity_change`,
`authorize_operational_posture`, `authorize_condition_statement`, or
`narrow_or_withhold_condition_statement`. **Precedence.** Authority and
current information precede urgency. **Abstention.** Only for missing authority,
unobtainable material information or a named active process. **Forbidden.**
Hidden scalar triggers “seek aid.” **Falsifier.** Removing the cited condition
records leaves identical activation. **Deletion.** Would allow arbitrary
calendar/outcome activation.

#### `DC-TCA-02` — disclose information and respond to examination

**Situation.** An authorized examiner/intermediary requests information or
examination consent. **Basis.** `TCA-C02`–`TCA-C03`, `M-TCA-01`.
**Information.** Requester authority, scope, requested records, company
disclosure authority, current package and conditions. **Alternatives.** Consent,
condition consent, provide a scoped package, request clarification, refuse
outside scope, or wait for named authority. **Intents.**
`consent_to_scoped_examination`, `provide_scoped_case_information`,
`request_information_or_terms`. **Minimum response.** Classify scope/authority
and identify the package or blocker. **Precedence.** Privacy/control and company
authority precede coordination pressure. **Forbidden.** Self-issue favorable
report. **Falsifier.** Removing disclosure authority has no effect.

#### `DC-TCA-03` — form or revise a support and collateral proposal

**Situation.** A competent support route is available or requests terms.
**Basis.** `TCA-C05`–`TCA-C06`, `M-TCA-02`–`03`. **Information.** Route state,
recipient, authority, company resource/control record, terms and existing
requests. **Alternatives.** Open/update request; propose collateral; request
terms; use another authorized route; withdraw/close; wait for a named result.
**Intents.** `open_or_update_support_request`, `propose_collateral_package`,
`request_information_or_terms`, `withdraw_or_close_support_route`.
**Minimum response.** Use one route/request identity and state authority,
content and unresolved counterparty decisions. **Precedence.** Company control
and authority precede target amount; existing pending request prevents
duplicate submission. **Forbidden.** Proposal equals accepted collateral or
funds. **Falsifier.** Route, authority or collateral-control changes never
alter the response.

#### `DC-TCA-04` — adapt operating posture

**Situation.** A delivered service-condition report makes an authorized
operating review due. **Basis.** `TCA-C04`, `M-TCA-04`. **Information.** Dated
service demand/capacity, company condition, authority and current posture.
**Alternatives.** Propose/authorize bounded capacity change; request resource
or condition verification; retain posture with stated reason; record pending
authority. **Intents.** `propose_operational_capacity_change`,
`authorize_operational_posture`, `verify_institutional_condition`.
**Minimum response.** State the posture decision and its dated basis. **Boundary.**
Scenario executes staffing, queue and payments. **Forbidden.** Authorizing
windows creates cash or payment. **Falsifier.** Executed and failed capacity
results produce the same later posture.

#### `DC-TCA-05` — authorize or withhold a condition statement

**Situation.** A public/private communication is proposed or material
information changes. **Basis.** `TCA-C07`, `M-TCA-05`. **Information.** Proposed
claims, dated supporting records, audience, authority and prior message.
**Alternatives.** Authorize; issue an already authorized statement; narrow;
withhold; request verification; correct/update. **Intents.**
`authorize_condition_statement`, `issue_authorized_condition_statement`,
`narrow_or_withhold_condition_statement`,
`authorize_correction_or_update`,
`verify_institutional_condition`. **Minimum response.** Link every material
claim to an `as-of` record and authority. **Precedence.** Verifiability and
scope precede reassurance objective. **Forbidden.** Statement means solvency,
delivery or confidence restored. **Falsifier.** Stale/contradictory information
does not narrow or delay content.

#### `DC-TCA-06` — respond to delivered process and resource results

**Situation.** Examination, support, collateral, operating or communication
result is delivered. **Basis.** `TCA-C08`, `TCA-C10`. **Information.** Linked
route/process, result type, conditions, time and producer. **Alternatives.**
Follow conditions; revise request/package/posture; use another route; correct
communication; close; seek clarification. **Intent.** Select the relevant
revised domain intent or `close_or_pause_institutional_matter`; consuming a
result is a state update, not an outward action. **Minimum response.** Consume
once and update only the linked process. **Forbidden.**
One route result globally resolves all support or rewrites the prior trace.
**Falsifier.** Delayed, partial, failed and executed results are behaviorally
indistinguishable.

## 7. Intent and result boundary

| Intent | Required content | Lifecycle | Agent may not declare |
|---|---|---|---|
| `verify_institutional_condition` | subject, cited records, `as-of`, uncertainty and requested verifier | pending until verified/disputed/expired | hidden true condition |
| `consent_to_scoped_examination` | case, examiner/route, scope, authority, conditions and access limits | consent, examination and report separate | examination begun/completed/favorable |
| `provide_scoped_case_information` | case, package identity, fields/documents, date, provenance, authority and recipient | issue, receipt and review separate | recipient received or accepted truth |
| `request_information_or_terms` | linked case/route, specified missing item and revisit event | one pending request per item/version | information/terms delivered |
| `open_or_update_support_request` | route/request identity, recipient, authority, need category, requested support and expiry | route-specific; duplicate pending request prohibited | acceptance, commitment or funds |
| `propose_collateral_package` | route, package version, company-controlled note/assets, authority, conditions and uncertainty | proposal, verification, acceptance and transfer separate | sufficient value or realized proceeds |
| `withdraw_or_close_support_route` | route/request, reason, authority and remaining obligations | affects only linked route | every aid route closed |
| `propose_operational_capacity_change` | operation, requested capacity/posture, basis, duration and resource dependencies | proposal and execution/result separate | staff deployed, requests served or cash available |
| `authorize_operational_posture` | operation, scoped authority, posture and review event | authority does not execute mechanics | payments or continued operation |
| `authorize_condition_statement` | proposal/version, approved claims, sources, `as-of`, audience and scoped authority | authorization can be superseded; issue remains separate | message issued/delivered or claims true |
| `issue_authorized_condition_statement` | authorization/message identity, exact content, audience, route and event time | issue, delivery and effect separate | delivery, truth, audience belief or stability |
| `narrow_or_withhold_condition_statement` | proposal/message, removed or withheld claims, reason, authority and revisit event | affects the current proposal/version only | public knowledge or effect |
| `authorize_correction_or_update` | prior message, new dated information, corrected content and authority | creates a new linked message; cannot erase the earlier record | correction delivered/effective |
| `close_or_pause_institutional_matter` | linked process, scoped reason, current state and reopening event if paused | affects only the identified matter | all routes closed, resources restored or institution stabilized |

## 8. Operationalization and uncertainty

| Construct | Representation | Status/use |
|---|---|---|
| material-condition activation | participant-visible notice with cited dated records and classifier identity outside Agent policy | no recovered threshold; historical/reconstructed/sensitivity classification stays in run audit |
| liquidity | cash/near-cash availability category or interval with `as-of` | distinct from asset value and solvency |
| asset and collateral position | typed asset/control/pledgeability information with uncertainty | no self-valuation; exact historical packages exposed |
| service condition | ordinal/interval demand and capacity report | seven windows is worked-case evidence, not parameter |
| information adequacy | `{absent, incomplete, disputed, adequate_for_scope, superseded}` | qualitative and route/scope specific |
| authority | scoped categorical record | title does not imply authority |
| request route | stable recipient/route/request identity and lifecycle | multiple routes coexist without merging |
| institutional assessment | bounded qualitative interpretation from legal observations | not hidden world state, confidence or fear |

No exact request threshold, collateral haircut, route weight, retry interval or
capacity formula is historically identified. Scenario assignments must be
declared and tested as construction or sensitivity choices, not placed in the
Agent as secret numbers.

## 9. Worked cases and falsification

### Case A — examination request with incomplete authority (reconstructed)

**Situation.** An examiner requests a daily statement and access; recipient
identity and scope are clear but TCA disclosure authority is pending.
**Required response.** Seek authority, request scope clarification or provide
only information already authorized. **Boundary.** Examiner cannot receive or
conclude until scenario results. **Perturbation.** Deliver scoped authority;
consent/package becomes admissible, not a favorable finding.

### Case B — two independent support routes (reconstructed from outcome-known evidence)

**Situation.** A Morgan-routed request is pending while a separately authorized
bank route offers different terms. **Required response.** Keep separate request
identities and compare only delivered terms; update either, propose a scoped
package, wait for named results or withdraw one. **Perturbation.** Decline one
route. The other remains unresolved, not globally failed.

### Case C — collateral proposed but partially accepted (illustrative)

**Situation.** TCA proposes a package it is authorized to control; recipient
accepts only part. **Required response.** Record partial disposition and revise,
supplement, use another route or close. **Boundary.** Accepted collateral is not
cash until execution. **Perturbation.** Remove control authority; proposal is
inadmissible.

### Case D — service demand rises (reconstructed from outcome-known evidence)

**Situation.** A sourced service-condition notice indicates material demand;
actual future withdrawals are unknown. **Required response.** Verify, propose
or authorize a bounded capacity/posture change, or state a resource/authority
blocker. **Boundary.** Scenario controls windows, queue, payments and depletion.
**Perturbation.** Capacity execution fails; the next posture must differ from a
successful result.

### Case E — public liquidity statement (reconstructed from outcome-known evidence)

**Situation.** Current records support a scoped claim about valuable but
illiquid assets; precise immediate cash is disputed. **Required response.**
Authorize a bounded dated statement, narrow it, request verification or
withhold. **Boundary.** Delivery, accuracy and audience effect are external.
**Perturbation.** Deliver a contradictory fresh report; unchanged language is
nonconforming unless the contradiction is explicitly addressed.

### Falsification matrix

| Test | Expected | Failure |
|---|---|---|
| name erasure | authority/information, not TCA name, drives behavior | historical script |
| route separation | one route's status does not overwrite another | global rescue shortcut |
| duplicate request | same pending request is not recreated | no lifecycle |
| disclosure/examination split | company package and examiner finding remain distinct | authority collapse |
| collateral result ladder | proposed/accepted/partial/executed differ | intent=result |
| service result | failed versus executed capacity changes later posture | operations decorative |
| message lifecycle | issue/delivery/truth/effect remain distinct | communication self-realizes |
| hidden threshold deletion | behavior does not depend on undocumented numbers | fitted policy |
| future-fact injection | later continuation/suspension excluded | leakage |
| always-abstain | activated informed/authorized case produces bounded response | empty model |
| aggregate/split | split only when independent bodies add explanatory process | aesthetic granularity |

## 10. Limitations and references

### Limitations and withdrawal conditions

1. Exact focal board authorization and internal delegation remain unresolved.
2. Thorne's testimony is retrospective and self-interested; it does not prove
   objective condition or motive.
3. Exact participant-time cash, assets, collateral values, obligations and
   service demand are not recovered.
4. No unique support-route priority, numeric trigger, retry interval or
   operating rule is established.
5. Run totals, assistance and continuation are exposed outcomes.
6. The model does not explain depositor decisions, examiner policy,
   contributor choices, payment mechanics or market effects.
7. No historical calibration, cross-event reuse, predictive validity or
   independent validation is claimed.

Narrow a mechanism if evidence shows it was mechanically dictated externally;
split the Agent if board, management, treasury or communications had
independent information and choices required by the research question; remove
any threshold or amount whose source cannot support its decision-time use.

### References

- *Commercial and Financial Chronicle*. October 26, 1907.
- *Congressional Record*. 60th Cong., 1st sess., February 26, 1908.
- Moen, Jon R., and Mary Tone Rodgers. 2022. “How J. P. Morgan Picked the
  Winners and Losers in the Panic of 1907.” *Essays in Economic & Business
  History* 40: 156–187.
- Moen, Jon R., and Ellis W. Tallman. 1995. “Clearinghouse Access and Bank
  Runs.” Federal Reserve Bank of Atlanta Working Paper 95-9.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*.
- U.S. House of Representatives, Committee on Investigation of United States
  Steel Corporation. 1911. *United States Steel Corporation: Hearings*, House
  No. 23.
