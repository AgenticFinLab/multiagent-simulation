# H2EPR-0288 Event Scenario Definition

> Accepted `0.1.0` · event-bound scholarly specification · not an
> executable configuration

## 1. Model overview

| Field | Description |
|---|---|
| Historical event | Panic of 1907, H2EPR event `H2EPR-0288` |
| Modeled interval | Analytic boundary begins 18 October and ends at an exact, configuration-pinned early-November 1907 horizon; primary acute window: 21–26 October. The Definition does not manufacture a final day or intraday time where the accepted evidence supplies only a broader interval. |
| Research questions | How institution-specific information, authority, clearing and support routes, depositor requests, distributed resource commitments, and call-money obligations interact; which process differences arise from participant mechanisms rather than a scripted chronology. |
| Semantic inputs | `H2EPR-0288-ROSTER-DEFINITION-RELEASE-v0.1`; accepted consolidated mapping `H2EPR-0288-CONSOLIDATED-MAPPING-v0.1`; event evidence ledger and source register; H2EPR Contracts V1 as carrier target. |
| Scenario form | Mixed event-driven scenario with bounded historical windows, explicit exogenous inputs, same-prestate decision barriers, and authoritative post-decision adjudication. |
| Structural baseline | Conservative evidence boundary: no evidenced competent alternative NYCH support route; no delivered NYCH direction is presumed for NBC; independent resource owners; conservative committee procedure; Morgan personal-coordination attribution; relationship-history mechanism disabled. |
| Sensitivity variants | Bounded NYCH alternative-route discretion; delivered/combined/disputed NBC direction provenance; continuity-supportive committee recommendation; scoped Morgan firm delegation; dated-relationship sensitivity; disclosed population, lending, borrowing, facility-use, and venue policies. |
| State authority | Scenario registries and reducer-owned processes hold identities, institutions, relationships, authority, resources, claims, cases, messages, service, market, execution, and results. Participants hold only their released decision state and delivered record references. |
| Evidence and model status | All focal outcomes used during construction are `FULL_DRAFT_EXPOSED`. Parameters and population composition are uncalibrated unless a future configuration says otherwise. No held-out historical validation, predictive validity, or cross-event validity is claimed. |
| Scenario identity | `h2epr.scenario.0288.panic_1907`, semantic version `0.1.0` |

The scenario represents the acute event as a linked set of institutional and
market processes rather than a sequence of predetermined historical actions.
Participant models decide whether to request, review, communicate, offer,
commit, call, repay, or wait. The event world determines whether those intents
are authorized, delivered, feasible, executed, partially realized, delayed,
or unsuccessful. This separation allows the same participant release to be
tested under different evidence-bounded institutional interpretations without
giving an Agent control over another institution or over its own result.

The most important interpretive limit is exposure: the research team already
knows the major run, suspension, support, pool, and market outcomes. A run may
demonstrate semantic closure, causal consistency, and the consequences of a
declared mechanism. It cannot independently establish that the mechanism is
the historical truth.

## 2. Event boundary and causal question

### Historical setting

The boundary begins after United Copper and affiliated-bank distress has
created a relevant information and relationship context but before the focal
Knickerbocker support, clearing, withdrawal, and suspension processes are
resolved. It includes the subsequent trust-company response, the formation of
the five-person presidents' committee, Morgan-centered coordination, selected
collective resource decisions, later trust-company depositor response, and the
acute call-money funding process. The boundary ends after the acute processes
have either reached a terminal state or have been explicitly carried forward
as unresolved at the analytic horizon.

### Endogenous processes

The scenario may explain through the released participants and authoritative
environment processes:

- Knickerbocker condition review, authorization, information provision,
  support-request formation, operational contingency, and communication;
- NBC exposure review, credit posture, request intermediation, clearing
  continuation or notice, and institutional communication;
- NYCH focal request intake, route classification, review, authority seeking,
  disposition, and communication under the two accepted route
  interpretations;
- depositor request or retention choices and host-scoped contagion response;
- TCA information, examination, support-route, collateral, operating, and
  communication choices;
- Lincoln's narrow board-authorized communication process;
- the presidents' committee's application, information, examination,
  recommendation, and separately authorized coordination choices;
- Morgan's information, convening, proposal, solicitation, plan, and
  communication choices;
- institution-preserving bank contributions and certificate applications;
- lender and broker-borrower responses to call-loan and replacement-funding
  processes; and
- authoritative message, service, resource, market, settlement, and result
  processes needed to adjudicate those choices.

### Boundary inputs and deliberately exogenous choices

The scenario treats the following as initial or exogenous because their
autonomous decision makers are not in the accepted release:

- pre-boundary United Copper and affiliated-bank distress;
- the initial legal entities, deposit claims, loan obligations, resource
  projections, memberships, and relationship records selected by a versioned
  configuration;
- publication of source-backed public reports and any explicitly synthetic
  information-coverage events;
- constitution of the trust-company presidents' committee and delivery of its
  mandate by the wider presidents' forum;
- Treasury public-deposit decisions and resource injections;
- activation and rules of the later NYCH certificate facility, whose supply
  decision is outside the focal NYCH Agent Definition;
- NYSE calendar/governance decisions and loan-stand availability; and
- private-need events and synthetic population composition used for
  sensitivity analysis.

Exogenous does not mean unrecorded. Every such input has a stable identity,
event time, source class, recipients or state target, and exposure label. It
may alter authoritative state but may not reveal why an excluded actor chose
it or disclose a later outcome to a participant.

### Exclusions

The model does not endogenize Charles T. Barney as an individual, the full
Knickerbocker or TCA boards, every trust-company president, an independent
examiner's policy, Treasury officials, NYSE governors, broker customers,
beneficial owners, receiver/reorganization decisions, or the complete public.
National Bank of Commerce is the request and clearing intermediary in the
focal chain; it is not a transparent wire. Lincoln remains a narrow
communication Agent. The wider presidents' meeting, Treasury, NYSE governance,
and the later certificate-supply decision remain scenario processes.

If answering a later research question requires one of these excluded actors
to make an autonomous, behaviorally consequential choice, the scenario must
stop and return to the roster process rather than hiding that choice in an
environment rule.

### Causal transitions of interest

```text
dated institutional state and delivered information
  -> participant-specific observation
  -> authorization, request, review, communication, funding, or waiting choice
  -> route and institutional admissibility
  -> independent counterparty decision or environment feasibility
  -> delivery, execution, partial effect, failure, or no effect
  -> authoritative state/result
  -> later participant-visible feedback
  -> institution-specific and cross-market adaptation
```

The key empirical contrasts are not whether one terminal event occurs, but
whether changes to information access, relationship status, authority,
resource ownership, request route, service results, and funding terms produce
the process differences predicted by the released Definitions.

### Claim boundary

A completed run can support four bounded claims: the fixed semantic inputs can
be assembled without duplicate authority or resources; participant-time
information can be enforced; business objects can retain causal lineage; and
declared structural assumptions produce inspectable differences. It cannot by
itself show that 1907 has been calibrated, replicated, validated, predicted,
or explained uniquely.

## 3. Evidence, theory, and temporal boundary

### Scenario mechanism ledger

| Scenario element | Claim/theory basis | Scenario use | Participant-time rule | Exposure/use | Withdrawal consequence |
|---|---|---|---|---|---|
| Knickerbocker identity, condition, governance, request, and clearing context | `KT-C01`–`KT-C14`, `NBC-C01`–`NBC-C16` | initial institution/relationship state; authorization, request, and clearing processes | only dated company, channel, request, and result records actually delivered to the relevant interface | construction; focal outcomes exposed | remove unsupported initial values or narrow company/channel mechanisms; never replace with later outcome |
| NYCH membership, procedure, and focal route uncertainty | `NYCH-C01`–`NYCH-C15`, `P4-S01`–`P4-S04` | membership, case, authority, resource, and structural-route rules | committee/private records remain hidden until delivered; later certificate rules unavailable before activation | construction and structural sensitivity | retire or narrow one route interpretation if direct evidence resolves the focal authority path |
| Knickerbocker and later depositor response | `KDP-C01`–`KDP-C07`, `LDP-C01`–`LDP-C09`, `TH-C04` | host claims, information delivery, service observation, request/payment lifecycle | units see only host/account/public products delivered through configured coverage; no future suspension | construction; profile mixtures synthetic/sensitivity-only | remove endogenous response claims if population choice is replaced by exogenous demand |
| NBC credit, intermediation, and notice | `NBC-C01`–`NBC-C16` | credit, two-hop request, clearing relation, notice and result processes | later debit, suspension, recovery, and undelivered NYCH direction are forbidden | construction and provenance sensitivity | narrow NBC to protocol if a unique external rule or purely mechanical forwarding is established |
| TCA and Lincoln institutional response | `TCA-C01`–`TCA-C11`, `LTC-C01`–`LTC-C06` | examination, support route, collateral, service, statement, and communication processes | each institution receives only its dated condition, authority, message, and result records | construction; all focal outcomes exposed | narrow TCA mechanisms or return Lincoln to scenario if autonomy is not supported |
| Presidents' committee | `TPC-C01`–`TPC-C09` | mandate, application, information, examination, recommendation, and coordination processes | later NYCH certificate procedure cannot define the earlier committee; contributor replies require delivery | construction and structural sensitivity | split/narrow committee if member-level choice or pure conduit is demonstrated |
| Morgan coordination | `MG-C01`–`MG-C09` | case, report, meeting, proposal, solicitation, plan, and result processes | committee reports, contributor replies, firm authority, and resources require their own delivered records | construction; attribution and relationship sensitivities | narrow/split personal, firm, associate, or committee ownership when direct evidence requires it |
| Bank contributions and certificate demand | `CBC-C01`–`CBC-C10` | institution-preserving units, independent commitments, facility applications | each institution sees only its own authority/resources and delivered proposal/facility information | construction; postures and amounts uncalibrated | remove endogenous contribution choice if a binding collective rule is recovered |
| Call-money lenders, borrowers, and venue | `CML-C01`–`CML-C09`, `CMB-C01`–`CMB-C08` | loan, call, replacement funding, collateral, position-reduction, matching, and settlement processes | each unit sees only its contracts, routes, terms, resources, and delivered market products | construction; outcomes exposed; policies uncalibrated | narrow contract/venue rules when focal evidence contradicts the general institutional description |
| Bounded choice under incomplete information | `TH-C01`–`TH-C03` | missing/stale/disputed state, search, qualification, fallback, and set-valued response | theory never supplies event facts or hidden participant knowledge | modeling lens, not event evidence | retain evidence boundary even if a different behavioral theory replaces the lens |

### Temporal admissibility

Each material record carries at least `event_time`, `as_of`, `source_or_owner`,
`record_version`, `visibility`, and `delivery_state`. Research-source time and
participant-available time remain distinct. A later source may justify the
researcher's construction of an earlier institution or rule, but its text is
not an Agent observation unless the scenario separately identifies a
contemporaneous information product.

All focal historical outcomes are exposed. The scenario therefore uses three
labels instead of a fictitious held-out split:

- `HISTORICAL_RECORD`: a supported event input or state instantiated at its
  defensible event time;
- `CONSTRUCTION_ASSUMPTION`: a required but unavailable setting whose effect
  is exposed; and
- `STRUCTURAL_SENSITIVITY`: an alternative mechanism selected before a run.

These labels are system-only audit metadata. Participants receive only the
admissible record projected under the selected construction.

### Conflicting and unavailable evidence

Conflict is represented by disputed records, bounded alternatives, or an
unknown value. It is never averaged into one confidence score. Exact focal
liquidity thresholds, participant population weights, committee votes, bank
postures, lender policies, borrower mandates, collateral haircuts, and
intraday ordering are not identified by the accepted evidence. A derived
configuration must label any chosen value or order and provide a sensitivity
or withdrawal rule where the choice is behaviorally material.

## 4. Temporal structure and exogenous inputs

### Clock and causal order

The scenario uses a partially ordered event clock. A source-supported exact
time may be used; otherwise the configuration uses a bounded window and an
explicit tie/order policy. It may not manufacture minute-level precision to
force a desired result.

Within one decision barrier the logical order is:

1. freeze the authoritative prestate and due event set;
2. admit scheduled exogenous inputs and already-due deliveries;
3. produce participant-specific observations from the frozen versions;
4. obtain all activated decisions from the same prestate;
5. validate intents and materialize permitted messages without adding meaning;
6. adjudicate institutional, lifecycle, resource, service, and venue effects;
7. let the authoritative reducer commit ordered state changes and results;
8. schedule or deliver result observations for a later barrier; and
9. evaluate phase opportunities, horizon, and fail-closed conditions.

This is a semantic ordering requirement, not an implementation prescription.

### Causal opportunity phases

Phases organize available processes and information. They do not require the
historical outcome shown in the label.

| Phase | Historical window and entry | Processes that may activate | Permitted persistence or reversal | Exit |
|---|---|---|---|---|
| `P0_BOUNDARY_SETUP` | 18–20 Oct.; fixed release/config loaded and pre-boundary distress admitted | entity/relationship/resource initialization; dated public information; ordinary deposit and call-loan service | all unresolved objects persist; no focal outcome injected | first focal institutional review/request or 21 Oct. boundary event |
| `P1_FOCAL_INSTITUTIONAL_REVIEW` | approximately 21 Oct.; KT/NBC/NYCH matter, review, or relationship event delivered | KT authorization/request; NBC credit/intermediation/clearing review; NYCH intake/review/disposition; related messages | request, review, notice, and relationship may remain pending, disputed, or unchanged | focal route/process reaches a stable pending/terminal state or withdrawal-service activation becomes due |
| `P2_KNICKERBOCKER_SERVICE_PRESSURE` | approximately 22 Oct.; depositor decisions and host service are active | host-scoped withdrawal choice; request admission; queue/service/payment; KT operations/communication; relationship/result feedback | partial payment, delay, restriction, continued operation, or suspension are all admissible results | acute host service reaches configured horizon or terminal operational state |
| `P3_TRUST_CONTAGION_AND_REVIEW` | approximately 23 Oct.; later-host signals/requests and committee mandate may be delivered | TCA/Lincoln decisions; later-depositor response; committee cases; Morgan information/convening/proposal | several trust cases and support routes may coexist; one host result does not resolve another | cases are pending/closed and resource-coordination opportunity opens or horizon advances |
| `P4_RESOURCE_AND_CALL_MARKET_COORDINATION` | approximately 24–25 Oct.; valid proposals, calls, venue routes, or settlement needs exist | contributor decisions; Morgan/committee plan assembly; lender calls/offers; borrower replacement/repayment/reduction; venue matching and settlement | partial, failed, expired, revised, and second-round plans remain possible | acute obligations close, carry forward, or the later facility window opens |
| `P5_LATER_INSTITUTIONAL_FACILITIES` | approximately 26 Oct. onward; exogenous facility/treasury inputs are activated by config | member certificate applications; collateral review/issue; Treasury resource effects; continued service/funding adaptation | facility use is optional; issuance and effects remain separate | configured follow-through horizon or all material objects terminal |
| `P6_FOLLOW_THROUGH_AND_CLOSE` | after the acute window through the configuration-pinned early-November horizon | delivery, correction, repayment, release, closure, expiry, and unresolved-object accounting | no new autonomous role is invented to finish history | normal completion, bounded incomplete run, or fail-closed termination |

Multiple phases may be open when their processes overlap. Phase identity is a
system analysis label and is not exposed as an Agent observation unless a
separate dated information product conveys an equivalent participant-known
fact.

### Exogenous input register

| Input | Source/event time | Delivery or visibility | Authoritative effect | Boundary reason | Sensitivity treatment |
|---|---|---|---|---|---|
| United Copper and affiliated-bank distress | ledger-supported prehistory before focal boundary | only source-backed public or relationship-scoped products are delivered | initializes relationships, public information, and eligible review events; does not directly choose an Agent action | responsible actors outside accepted roster | fixed historical boundary; alternative information coverage may vary |
| dated public reports and statements | source-backed event dates, or explicitly synthetic publication event | public product is not visible until issue and delivery; host/scope retained | adds versioned information product only | public-information producer generally unmodeled | fixed content for sourced case; coverage/delay sensitivity disclosed |
| presidents' forum constitutes five-person committee | `TPC-C01`–`TPC-C03`, approximately 23 Oct. | committee and permitted recipients receive mandate/roster record | creates committee entity activation, mandate, and reporting forum | full presidents' forum not in roster | fixed event-bound input; no committee policy supplied |
| Treasury public deposit | source-backed or bounded configured date/recipient | recipient sees resource result only after authoritative delivery | transfers/adds the specified public-deposit resource under one owner and provenance chain | Treasury decision maker excluded | fixed sourced input or omitted/bounded timing sensitivity |
| later NYCH certificate facility activation/rules | dated after 26 Oct.; `CBC-C04`–`CBC-C05`, `P4-S02` | eligible members receive rules only after activation/delivery | opens application/review/issue lifecycle; does not create applications or certificates | supply decision excluded from focal NYCH Definition | fixed later-context input or omitted; never back-projected |
| NYSE calendar, loan stand, and governance state | sourced institutional schedule or declared construction input | venue users receive only dated route/market products | opens/closes venue operations and eligible matching/settlement paths | NYSE is scenario-owned venue in v0.1 | conservative venue policy plus declared synthetic sensitivities |
| population composition and private-need events | explicit pre-run configuration/event generator | unit-private; never public | initializes/updates unit-private input, not world outcome | microdata unavailable | synthetic/sensitivity-only; no fitting to known totals |
| analytic horizon | scenario configuration within the accepted early-November boundary | system only | closes scheduling and marks unresolved objects | research boundary rather than historical actor choice | exact date/time must be pinned and justified; bounded alternatives reported |

## 5. Participant assembly and causal ownership

### Named decision interfaces

| Entity/interface | Released capability | Runtime decision interface | Authority owner | Resource owner | Scenario dependencies |
|---|---|---|---|---|---|
| Knickerbocker Trust Company | `knickerbocker_trust` | one named institutional actor | KT governance records by scope | KT canonical resource ledger | condition records, depositor service, NBC relation, support routes, messages/results |
| New York Clearing House | `new_york_clearing_house` | one aggregate procedural actor for the focal request | NYCH governance/committee/association records | NYCH/member resources remain separately owned | membership, focal case/review, route interpretation, forum and communication processes |
| National Bank of Commerce | `national_bank_of_commerce` | one named multi-capability actor | NBC governance records by credit/intermediation/relationship scope | NBC canonical resource/exposure ledger | KT clearing relation, request hops, NYCH direction, notice, credit and result processes |
| J. Pierpont Morgan | `j_pierpont_morgan` | one named personal coordination actor | personal/firm/joint attribution record by act | no direct resource capability in this release | cases, reports, meeting, proposal, contributor replies, plan and result processes |
| Trust Company of America | `trust_company_of_america` | one named institutional actor | TCA governance records by disclosure/support/operations/communication scope | TCA canonical resource/collateral ledger | condition, examination, route, service, collateral, communication and result processes |
| Lincoln Trust Company | `lincoln_trust_company` | one narrow institutional communication actor | competent-forum and statement-authorization records | Lincoln resource ledger is observed only when a communication record requires it; no resource action | condition report, statement proposal, authorization, message and correction processes |
| Trust-company presidents' committee | `trust_presidents_committee` | one aggregate procedural committee actor | committee mandate and any separate coordination authority | no ownership of member/contributor resources | case, examination, reporting forum, recommendation, solicitation, plan and result processes |

### Population and composed-capability assembly

| Entity or unit pattern | Released capability | Unit/actor rule | Authority/resource rule | Required scenario scope |
|---|---|---|---|---|
| Knickerbocker depositor unit | `knickerbocker_depositor` | one or more weighted host-scoped units | unit-private need/request state; claim owned by unit/host account relation | host=`Knickerbocker`; weight, claim, profile, signal and access coverage explicit |
| Later trust depositor unit | `later_trust_depositor` | weighted unit scoped to exactly one configured host | no cross-host private state, claim, request, or result | TCA, Lincoln, or another explicitly admitted host; host-specific profiles disclosed |
| Member/correspondent bank unit | `bank_resource_decision` | weight-one institution-preserving unit; compose into a named actor when entity IDs coincide | institution's one authority graph and resource owner | membership, capability, request/facility route, posture and amount method explicit |
| Call-money lender unit | `call_money_lender` | institution-preserving lender capability; compose with bank resource capability under one actor | same institution resource/exposure truth across capabilities | own loan book, authority, resources, relationships, postures and routes explicit |
| Broker-borrower unit | `call_money_broker_borrower` | one authorized firm/exchange-member funding interface | one mandate, resource/collateral/position control record and obligation ledger | borrower, loan, route, offer, settlement and response posture explicit |

The assembly is configuration-specific, but four rules are invariant:

1. one historical/legal entity has one `entity_id`, one endogenous actor, one
   ParticipantArtifact, one authority graph, and one canonical resource owner;
2. composing `bank_resource_decision` and `call_money_lender` adds capability
   surfaces, not a second institution or balance sheet;
3. depositor units retain host, claim, weight, private input, observation, and
   request scope; and
4. NYSE, wider presidents' forum, examiner execution, Treasury decisions,
   message transport, and reducer processes do not become hidden Agents.

If one actor requires an intent not present in its released capability union,
or if one scenario process must choose among meaningful alternatives on behalf
of an excluded actor, assembly fails and returns to the Roster Definition
process.

## 6. World, institutions, relationships, and resources

### Authoritative state families

| ID | State family and owner | Initial basis | Valid update events | Visibility | Invariants |
|---|---|---|---|---|---|
| `WS-ENTITY` | entity, actor, capability, population-unit, host, and business-object registry; scenario assembly owns identity | accepted release plus versioned scenario configuration | configuration validation before run; no behavioral mutation | identity projections may be public or scoped | one legal entity and one actor/resource owner; IDs never recycled |
| `WS-AUTH` | governance, mandate, delegated authority, and competent-forum records; relevant institutional governance process owns truth | sourced or explicitly assumed authority record with scope and effective interval | request, institutional decision, expiry, supersession, dispute, or exogenous mandate event | only the covered actor/process receives the scoped result | `unknown`, absent, expired, or wrong-scope authority grants nothing |
| `WS-REL` | membership, clearing, correspondent, host, coordination, support-route, and account relationships; relationship registry owns truth | dated source record or declared construction input | admitted formation/condition/notice/effective change, expiry, correction, or exogenous institutional rule | parties receive only permissible projections; public only after communication | relation status is versioned; notice is not effective change; no actor privately edits it |
| `WS-RESOURCE` | canonical cash, near-cash, public deposits, credit capacity, reserved/committed/transferred resources, and resource ownership; resource ledger/reducer owns truth | sourced amount/band or labeled configuration | admitted reservation, commitment, release, transfer, repayment, loss, or exogenous Treasury input | owner gets scoped projection; others see only delivered offer/result | one owner/control chain; no double spending or coordinator-owned participant funds |
| `WS-CLAIM` | depositor claim and host account relation; host account/service ledger owns truth | scenario-declared account or weighted claim | authoritative paid/cancelled/corrected result | unit and host-scoped service only | request does not reduce claim; only realized paid amount does |
| `WS-EXPOSURE` | NBC credit/clearing exposure and institutional loan/exposure state; financial ledger owns truth | dated record or bounded configuration | booking, settlement, repayment, loss, correction, or exogenous opening record | institution-scoped projection | proposal/offer is not exposure; later report cannot be backfilled as earlier truth |
| `WS-COLLATERAL` | asset identity, owner/control, encumbrance, custody, eligibility, and valuation result; collateral ledger/facility/venue process owns truth | sourced or labeled package/control projection | submission, validation, acceptance/rejection, encumbrance, release, realization | owner and reviewing counterparty receive scoped records | proposer cannot self-value or self-accept; one asset cannot secure incompatible claims twice |
| `WS-OPS` | host operating state, service capacity, withdrawal admission/queue, payment form, access, restriction, and suspension; host service process owns truth | bounded host condition and service configuration | withdrawal request, capacity result, payment, failure, restriction, reopening, or authorized external event | host management and affected units receive separate projections | operational intent is not execution; queue/global cash is never automatically public |
| `WS-CASE` | authority requests, support cases, examinations, proposals, solicitations, commitments, applications, and business dispositions; lifecycle-specific process owns truth | absent or explicitly carried-in object | admitted intent/message, delivery, recipient decision, time/expiry, execution, correction | owner/parties receive delivered version only | stable identity, version, owner, predecessor, status, and terminal condition required |
| `WS-COMM` | statement/notice/message content, issue, transport, delivery, receipt, correction, and expiry; issuing authority plus transport owns successive tracks | no message or carried-in record | admitted action, message materialization, routing, delivery/failure, correction, expiry | content becomes visible to a recipient only after delivery | authorization, issue, delivery, truth, response, and effect remain distinct |
| `WS-LOAN` | call-loan contract, call/term notice, funding request, offer, acceptance, match, booking, transfer, repayment/default, and obligation state; loan/funding process plus reducer owns truth | sourced or synthetic contract/obligation configuration | party intent, delivery, contract/admissibility check, match, booking, realized transfer/repayment/default | lender/borrower/venue projections are separately scoped | market stress creates neither call right nor capacity; each realized component updates once |
| `WS-VENUE` | NYSE schedule, route availability, loan stand, matching, rate, order/trade, settlement, and market-result records; scenario-owned venue process | sourced institutional rule or labeled venue configuration | schedule, admitted request/offer/order, match/allocation, trade, settlement, failure | public market product or party-specific result after production/delivery | venue does not choose participant policy; proposal/announcement is not match or funding |
| `WS-INFO` | information products, source/as-of, provenance, visibility, route, delivery, correction, dispute, and supersession; producer plus information-delivery process | source-backed or labeled synthetic information inventory | issue/production, transport, delivery, correction, dispute, expiry | public, relationship-scoped, role-scoped, or unit-private | world truth and delivered knowledge remain separate; no future/held-out access |
| `WS-TIME` | event clock, causal order, phase opportunities, scheduled exogenous inputs, and horizon; scenario scheduler | versioned configuration | due event, committed transition, or horizon rule | system-only except independently delivered time/calendar information | causal order stable under replay; phase label never substitutes for participant information |

### Institutional and relationship rules

| Requirement | Authoritative owner | Scope | Rule |
|---|---|---|---|
| KT–NBC clearing/correspondent relation | `WS-REL` | focal pre-notice and notice/effective intervals | relationship terms and direct Section 25 applicability remain explicit/unknown where unresolved; NBC duties persist until an authoritative effective change |
| NBC membership in NYCH | `WS-REL` and NYCH membership registry | dated institutional interval | membership enables only the rules and routes actually active; it does not give NBC NYCH decision authority |
| Knickerbocker nonmembership and focal support path | NYCH membership and focal case process | 21 Oct. focal matter | member-facility restriction is fixed; availability of another competent route is selected by `SV-NYCH-ROUTE` |
| depositor host/account relation | `WS-CLAIM` | one unit, host, and claim | no request, observation, result, or resource crosses host/claim scope without an explicit public or account channel |
| trust-company presidents' committee | `WS-AUTH`, `WS-REL`, and committee case process | after dated constitution event | committee mandate, full presidents' forum, Morgan cooperation, and contributor authority remain distinct |
| Morgan coordination relation | case/proposal process | one matter/proposal version | convening and solicitation do not bind invitees or contributors; action-level personal/firm attribution required |
| support and resource routes | route registry plus lifecycle owner | one request/proposal/target/version | route admission is not recipient acceptance; each offer and commitment retains actual resource owner |
| call-loan lender–borrower relation | `WS-LOAN` | one contract/loan/version | contract status, call right, call duty, term compatibility, offer, booking, and repayment are separately adjudicated |
| NYSE venue relation | `WS-VENUE` | eligible venue participant and route interval | venue may match/adjudicate but never supplies participant authority, collateral ownership, or a hidden policy answer |

### Authority rules

Every authority record identifies the competent forum or institutional
process, actor, permitted capability and intent scope, target/object scope,
resource scope where relevant, effective interval, state, version, and source
class. Authority requests enter `LF-AUTH`; they do not become effective merely
because an Agent cites them. An officer title, committee participation,
membership, urgency, relationship, invitation, attendance, recommendation, or
historically observed action is not a substitute for a valid scoped record.

Where the exact focal governance body is unavailable, a configuration may
instantiate a bounded `CONSTRUCTION_ASSUMPTION` authority record. It must not
claim a recovered institutional procedure, and removing or narrowing it must
predictably remove or narrow the affected intent.

### Resource and conservation rules

The scenario distinguishes available, reserved, offered, conditionally
offered, committed, scheduled, transferred, repaid, released, impaired, and
unknown resource states. The following always hold:

1. a proposal, target, solicitation, application, or accepted action does not
   create a resource;
2. a commitment requires compatible authority, owner/control, resource type,
   amount or qualitative band, terms, expiry, and current prestate version;
3. reservations and commitments reduce the same owner's remaining envelope
   once, even when the institution has several capabilities;
4. only realized transfer/payment/repayment components change counterpart
   balances, claims, exposures, or funding gaps;
5. partial, failed, delayed, no-effect, released, and reversed components keep
   their original amount/terms and reason in the trace;
6. collateral ownership, control, eligibility, valuation, encumbrance,
   custody, and realization are separate; and
7. public deposits, certificates, bank cash/credit, trust-company notes,
   collateral, call credit, and depositor claims are not interchangeable
   merely because a narrative calls them “liquidity.”

### Operational and venue rules

Depositor choices create requested demand. `WS-OPS` validates the host and
claim, admits or rejects the request, orders service under a declared queue
policy, checks operational capacity and resources, produces a payment form and
amount if feasible, and commits host/claim effects. Operational restriction or
suspension is an environment result from declared institutional/feasibility
conditions, not an Agent action and not a predetermined historical timestamp.

The venue receives only admitted, authorized loan, funding, collateral, or
position-related objects. It may publish a dated market product and may match,
allocate, schedule, execute, settle, partially realize, delay, reject, or fail
an eligible object under a versioned venue policy. It may not transform a
Morgan proposal into lender capacity, a borrower request into an offer, or a
position-reduction request into an executed sale.

## 7. Information production, routing, and observation

### Information-product families

| ID | Product and authoritative producer | Eligible recipients and route | Time, missing, and dispute rule | Typical released consumers |
|---|---|---|---|---|
| `IP-IDENTITY` | entity/actor/unit/capability/host/roster projection from `WS-ENTITY` | relevant actor or unit at assembly; public subset only when historically public | immutable for run; missing identity fails assembly | institution/borrower profiles, participant roster/roles, host institution |
| `IP-AUTHORITY` | scoped governance/mandate/competent-forum record from `WS-AUTH` | covered actor through institutional route | effective interval/version required; absent/unknown/denied grants nothing | corporate, NYCH, NBC, TCA, Lincoln, committee, contributor, lender, borrower authority |
| `IP-RELATIONSHIP` | membership, clearing, host, support, exposure, or market-route projection from `WS-REL` | parties or public after dated issue/delivery | status/effective interval retained; dispute stays explicit | clearing/relationship/channel/route/profile observations |
| `IP-RESOURCE` | owner-scoped cash, claim, exposure, collateral, capacity, need, or control projection from `WS-RESOURCE`, `WS-CLAIM`, `WS-EXPOSURE`, or `WS-COLLATERAL` | owner/authorized interface or counterparty reviewer | dated version/band/uncertainty; missing is not zero; later effect not backfilled | liquidity, claim, exposure, collateral, resource-envelope and gap inputs |
| `IP-CONDITION` | bounded company, applicant, counterparty, service, or recovery information product | role/relationship-scoped delivery | source/as-of/scope required; stale/disputed/unknown preserved | condition, financial information, applicant/borrower information, review notices |
| `IP-REQUEST` | sender-owned request/application/obligation envelope from `WS-CASE` or `WS-LOAN` | one route/hop at a time | issue, hop delivery, recipient receipt/classification separate; missing mandate/content triggers clarification | delivered request, counterparty request, assistance application, solicitation, borrower request, call obligation |
| `IP-CASE` | recipient case/review/disposition projection from lifecycle owner | requester, reviewer, forum, or authorized intermediary | case/version/owner required; silence is no disposition | review, route, eligibility, support-route, request, and case-status observations |
| `IP-REPORT` | examiner, committee, or information producer | scoped recipient after delivery | producer/scope/limitations retained; undelivered work unavailable | examination/report and case-information observations |
| `IP-PROPOSAL` | proposing actor plus authoritative proposal/plan process | specified recipients through circulation/solicitation route | version, predecessor, terms, unresolved items, and expiry retained | proposal, collateral package, funding offer, term basis |
| `IP-REPLY` | independently deciding recipient and reply lifecycle | requesting coordinator/committee/party after delivery | conditioned/committed/declined/expired/disputed states distinct | contributor and commitment replies |
| `IP-FACILITY` | scenario-owned institutional/venue facility process | eligible participants after dated activation | no earlier availability; membership/eligibility/rules versioned | facility state, market/pool route, funding route |
| `IP-COMMUNICATION` | authorized issuing participant plus `WS-COMM` | explicit audience, fanout, or public channel | authorization, issue, delivery, correction, expiry distinct | institution/host/public signals, communication matter, message/notice lifecycle |
| `IP-SERVICE` | host service or venue process | affected host/unit/participant; public subset only after delivery | own/local scope; exact global queue/resource hidden | withdrawal pressure, service/access, peer activity, settlement obligation |
| `IP-ACCOUNT` | host account/loan ledger | account/loan parties only | last delivered claim/loan/result version | remaining claim, existing loan, contractual status |
| `IP-MARKET` | scenario-owned venue/publication process | eligible venue participants or public channel | fallible dated band/route state; no future values | market observation, rate/route/collateral context |
| `IP-RESULT` | authoritative lifecycle/reducer result producer | affected actor/unit after separate delivery | result type, reason, realized component, object/version and event time retained | delivered dispositions, own request results, loan/credit/relationship/process results |
| `IP-PRIVATE` | versioned unit-private configuration or permitted private event | exactly one unit/actor scope | never public; source class and update event recorded | withdrawal need, response/posture assignment, own qualitative assessment |

### Production and delivery chain

```text
authoritative record/version
  -> source-scoped information product
  -> issue/publication or permitted direct projection
  -> transport/fanout
  -> recipient delivery record
  -> immutable decision-time observation snapshot
  -> DecisionRecord observation reference
```

Production does not imply issue; issue does not imply transport admission;
transport admission does not imply delivery; delivery does not imply business
acceptance; and a public product does not imply that every population unit
received it. Fanout creates one delivery lifecycle per recipient or one
explicitly defined public-coverage event whose coverage set is frozen.

### Projection and version coherence

An observation snapshot contains only material atomic values needed by the
released Definition plus stable source/object/version references. A backend
cannot dereference those references into live world state. Compound products
such as exposure records, request envelopes, collateral packages, offers, or
results close only when all material components share the declared coherent
version set. Mixed-version projections fail closed as `disputed` or
`unavailable`; they are not repaired by selecting convenient fields.

The observation gate is conjunctive:

```text
released Definition permits the concept
AND scenario information process can produce it
AND event-time/evidence boundary permits the source and delivery
AND accepted mapping can freeze the semantic placement
```

Failure of any term yields the released missing/stale/disputed/unknown path.
No implementation default may fill the value.

### Freshness, corrections, and forbidden knowledge

Freshness is a semantic relation between `as_of`, decision time, mechanism,
and any superseding record—not a universal timeout. A correction creates a
new product/version linked to the prior one; it never edits the prior
observation or trace. Disputed records retain competing provenance or a typed
dispute reason.

Forbidden knowledge includes undelivered private records, exact global state,
other units' private observations/results, future suspension or survival,
future market values, known pool totals before replies/execution, later
institutional rules before activation, Reference EPG, evaluation evidence,
and system-only variant or construction labels.

## 8. Interaction, lifecycle, adjudication, and results

### Canonical business object

Every lifecycle object contains one stable ID, family, semantic owner, current
state/version, actor and counterparty references, authority and relationship
references where required, source/predecessor/supersession links, event and
expiry times, and causal parents. The current state has one owner even when
several participants retain delivered references.

### Lifecycle registry

| ID | Family and primary owner | Valid semantic tracks | Main transition causes | Duplicate/expiry rule | Result feedback |
|---|---|---|---|---|---|
| `LF-AUTH` | governance/authority; competent institution or forum | absent/not-requested, requested, pending, authorized, denied, disputed, superseded, expired | seek-authority intent, forum decision, correction, time | one unresolved question per actor/scope/object/version | scoped authority result through `IP-AUTHORITY`/`IP-RESULT` |
| `LF-INFO` | information/examination; producer/examiner plus delivery | request, admitted, pending, produced, issued, delivered, disputed, corrected, withdrawn, expired, closed | information/examination request, producer work/result, message delivery, correction | one equivalent pending item per case/scope/producer; revisions link predecessor | package/report/clarification delivery |
| `LF-SUPPORT` | support/request case; recipient institutional process | draft, authorized, issued, hop-delivered, received, classified, reviewing, information-needed, referred, declined, conditioned, delayed, partial, executed, failed, withdrawn, closed/reopened | request/revision/withdrawal, each delivery hop, review/disposition, execution result | one equivalent unresolved request per sender/need/route; revision preserves ID lineage | sender/intermediary/recipient receive only their routed status/result |
| `LF-PROPOSAL` | coordination/proposal/plan; proposing process | draft, circulating, revising, ready-for-assembly, assembled, authorized, scheduled, withdrawn, expired, closed | form/revise/circulate/assemble intent, independent replies, authority/result | versioned; old version immutable; one owner per version | proposal/plan status and execution result |
| `LF-SOLICIT` | solicitation/reply; recipient independent process | prepared, issued, delivered, reviewing, conditioned, committed, declined, disputed, expired, superseded | solicitation, delivery, recipient decision, revision/cancel/time | one pending equivalent solicitation per plan/target/scope | reply delivered to requesting owner |
| `LF-RESOURCE` | resource commitment/execution; resource owner plus reducer | available, offered, reserved, committed, scheduled, partial, executed, no-effect, failed, released, reversed, expired | valid offer/commitment, reservation, schedule, transfer/result/release | same owner/resource/prestate cannot back incompatible commitments | owner/counterparty receive realized component and updated projection |
| `LF-CREDIT_CLEARING` | credit exposure and clearing relation/notice; financial/relationship ledgers | active/current, review-due, proposed/conditioned, notice-prepared, notice-issued, delivered, ending-at-time, inactive, booked/adjusted, repaid, failed, disputed, closed | NBC/party intent, direction, notice delivery, effective time, booking/repayment/result | one active relationship/credit object; revisions preserve prior terms/notice | dated exposure, relationship, notice, and result observations |
| `LF-COMM` | institutional communication; issuing authority plus transport | proposal, pending-authority, authorized, narrowed/withheld, issued, transport-pending, delivered, failed, expired, corrected/superseded, closed | authorize/issue/withhold/correct intent, route/delivery/time | exact content/version deduplicated; reissue/correction links prior message | message lifecycle and recipient information product |
| `LF-WITHDRAWAL` | withdrawal/service/payment; depositor unit plus host service/reducer | choice, request-created, admitted/rejected, queued, serving, partial, paid, alternate-form, delayed, failed, unavailable, expired/cancelled, claim-updated, closed | unit choice, service admission/capacity, payment/result/time | one equivalent unresolved request per unit/host/claim/scope | own request/result, access projection, claim/resource effects |
| `LF-FACILITY` | collateral/facility application; applicant, facility authority, collateral ledger/reducer | package/application draft, submitted, reviewing, information-needed, eligible/ineligible, accepted/declined, issued/booked, partial, released, failed, expired | application/package intent, facility review, valuation, issue/result | one active package/application version per owner/facility/scope | eligibility, disposition, issue/result and collateral/resource update |
| `LF-CALL` | call-loan contract; lender, borrower, loan ledger/reducer | active, review-due, continued, term-change-proposed, call-issued/delivered, borrower-responding, repayment-pending, partial/repaid, defaulted, failed, closed | lender review/call/terms, borrower response, transfer/repayment/result | one active contract; one pending equivalent notice/response per version | each party receives contract, call, repayment, and exposure result |
| `LF-FUNDING` | replacement funding; borrower, lender, venue/reducer | request, delivered/reviewing, offer/conditioned, revision, accepted/declined, matching, booked, transfer-pending, partial/funded, repayment-pending, repaid/defaulted, expired/closed | borrower request/term response, lender offer, match, booking, transfer/repayment | one request/offer per case/route/version; acceptance cannot skip match/booking | own offer/booking/funding/repayment result |
| `LF-POSITION` | position reduction and venue execution; authorized owner plus NYSE/reducer | requested, admitted/rejected, pending-match, partial/executed, settlement-pending, settled, failed/cancelled/expired | authorized request, venue admission/match/trade/settlement | one equivalent pending reduction per controlled position/scope | realized proceeds and obligation/funding-gap effect only after settlement |

The thirteen families cover all released business objects. Credit and clearing
share one family because both require an institution-owned exposure/relation
record and a separately effective result; their subtracks remain distinct.

### Adjudication ladder

Every outward intent follows the same ownership-preserving ladder:

1. **semantic and schema admission** — capability-qualified action type,
   required parameters, observations, decision, target, time, and idempotency;
2. **identity and authority** — actor, target, object, relationship, forum,
   resource owner/control, scope, and effective versions resolve;
3. **business lifecycle** — current object state permits the requested
   transition and no unresolved equivalent makes it a duplicate;
4. **institutional admissibility** — membership, jurisdiction, route,
   contract, facility, or venue rules permit consideration;
5. **feasibility and concurrency** — resource, collateral, service, capacity,
   timing, and competing commitments are evaluated against one prestate;
6. **scheduling and execution** — transport, review, service, match, transfer,
   payment, trade, or settlement occurs or remains pending; and
7. **result and delivery** — typed business/execution result and state deltas
   are committed, then separately projected and delivered.

An intent may be accepted at step 1 and later be institutionally rejected,
delayed, partially executed, fail, or have no effect. The trace therefore
keeps ActionDisposition, CommunicationDisposition, delivery, business
disposition, execution result, StateDelta, and later observation separate.

### Required cross-object validation

- request and message hops preserve original sender, represented party,
  content, mandate, intermediary role, final recipient, correlation, and
  predecessor; KT delivery to NBC never creates NYCH receipt;
- every case, proposal, plan, statement, loan, claim, facility, collateral,
  commitment, or result reference resolves to the exact current or cited
  historical version;
- a Morgan or committee plan has one owner and contains only delivered,
  unexpired contributor replies; overlapping solicitations receive an
  explicit duplicate/overlap disposition;
- an institution with contributor and lender capabilities reads and updates
  one resource/exposure prestate; capability composition cannot multiply
  capacity;
- a depositor request resolves to one unit, host, claim, request lifecycle,
  profile, and private state; no other host's private state is admissible;
- a call, offer, repayment, collateral, or position response resolves to one
  lender, borrower, contract/obligation, authority/control record, and active
  lifecycle;
- a market observation creates no call right, authority, capacity, match, or
  term-compatibility answer; and
- invalid, unauthorized, duplicate, expired, out-of-scope, or infeasible
  attempts remain visible with attempted parameters and reasons rather than
  being clamped or rewritten.

## 9. Operationalization, variants, termination, and identity

### Configuration boundary

This Definition fixes meanings, owners, admissible categories, and causal
rules. A later versioned scenario configuration supplies the actual actor
assembly, population units, records, values, windows, profiles, posture
assignments, route availability, and structural selections. A configuration
value is valid only when it records its semantic concept, source class,
identification status, unit/category, admissible domain, effective time,
visibility, and sensitivity role.

| Parameter family | Semantic meaning | Admissible representation | Identification rule | Owner/use |
|---|---|---|---|---|
| temporal window/order | event, delivery, deadline, expiry, effective interval, or unresolved tie | source-backed time; bounded interval; declared partial order | no invented precision; competing orders become separate variants | `WS-TIME`, scheduler and lifecycle |
| resource/claim/exposure | owner-controlled amount, band, claim, capacity, commitment, or realized component | sourced number/unit; bounded interval; qualitative envelope; `unknown` | unknown is not zero/unlimited; commensurate arithmetic only | canonical resource/claim/exposure ledger |
| population composition | unit, host, claim, weight, private need, response profile, information coverage | explicit synthetic/sensitivity configuration | never fitted silently to known withdrawal totals or host outcomes | assembly plus unit-private state |
| authority and relationship | forum, scope, state, version, parties, effective interval | categorical record with source class | title/name/urgency cannot instantiate authority or relation | `WS-AUTH`/`WS-REL` |
| information coverage/delay | recipient set, route, issue/delivery window, freshness, dispute | categorical or bounded schedule | public issue is not universal receipt; modeler labels hidden | `WS-INFO`/transport |
| service and queue | admission, ordering, capacity, payment form, access/result policy | versioned rule or categorical/bounded capacity | historical case, construction, or sensitivity label required | `WS-OPS` |
| review/classification | case standard, required information, permitted waiver, qualitative assessment | pre-run finite rule with cited inputs | no hidden score, outcome-dependent class, or backend-specific rule | case/review process; participant sees only result projection |
| proposal/commitment amount method | how a participant selects a bounded requested/offered band | sourced band; fixed sensitivity amount; qualitative band | cannot allocate a target automatically or exceed current owner envelope | participant intent plus resource adjudication |
| facility/venue policy | eligibility, routes, matching, collateral, schedule, settlement | dated institutional rule or explicitly synthetic policy | later rule unavailable earlier; venue cannot supply Agent policy | `WS-VENUE`/`LF-FACILITY`/`LF-FUNDING` |
| horizon/revisit | decision revisit event and normal analytic end | object event, deadline, bounded horizon | no indefinite no-op; unresolved state preserved | scheduler and run status |

### Structural identities

Structural variants change a mechanism or admissibility rule and are therefore
immutable system-only inputs covered by scenario/run identity. They are not
Agent traits and are never selected after inspecting the run outcome.

| ID | Conservative baseline | Sensitivity alternatives | Shared fixed boundary | Retirement evidence |
|---|---|---|---|---|
| `SV-NYCH-ROUTE` | `NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE` | `BOUNDED_ALTERNATIVE_ROUTE_DISCRETION` | direct member-facility restriction remains fixed; request, review, disposition, communication, and execution remain separate | direct focal rule/minutes establishing either absolute exclusion or a competent alternative route |
| `SV-NBC-DIRECTION` | `NO_NYCH_DIRECTION_DELIVERED` | `NYCH_DIRECTION_DELIVERED`, `COMBINED_PROVENANCE`, `DISPUTED_PROVENANCE` | NBC and NYCH identities, active duties, authority, notice issue/delivery/effect separation | direct focal record fixing who initiated or compelled the clearing change |
| `SV-TPC-RECOMMENDATION` | `PROCEDURE_CONSERVATIVE` | `BOUNDED_CONTINUITY_SUPPORTIVE` | declared review standard, delivered information, mandate, qualified advice, and independent resources | committee minutes or equivalent evidence identifying the focal advice rule |
| `SV-POOL-OWNERSHIP` | `INDEPENDENT_RESOURCE_OWNERS` | none in v0.1 | Morgan/committee may solicit and assemble but never own contributor resources | a roster/evidence revision establishing a genuinely collective resource owner |
| `SV-MORGAN-ATTRIBUTION` | `NAMED_PERSONAL_COORDINATION` | `SCOPED_FIRM_DELEGATION` | action-level provenance; no direct firm-resource capability is inferred | direct action/authority records resolving personal, firm, or associate ownership |
| `SV-MORGAN-RELATIONSHIP` | `RELATIONSHIP_HISTORY_DISABLED` | `DATED_RELATIONSHIP_SENSITIVITY` | dated relationship input only; no prestige/closeness score or known-winner fitting | prospective/direct evidence and a distinct predeclared process prediction |
| `SV-FACILITY` | `LATER_RULES_AVAILABLE_ONLY_AFTER_ACTIVATION` | facility omitted or bounded timing/rule sensitivity | no October 26 rule is back-projected to October 21–23 | direct evidence changing activation/rules or a roster revision endogenizing supply |
| `SV-VENUE` | `CONSERVATIVE_RECORDED_ROUTE_AND_SETTLEMENT` | explicitly synthetic matching/allocation sensitivities | NYSE remains scenario-owned; no proposal, request, or announcement creates a match/effect | focal venue/loan-stand records supporting a more specific policy |

Participant-profile assignments—depositor response, bank participation,
certificate use, lender/borrower posture, mixed-signal rule, amount method, and
private need—are also pinned and hashed. They are configuration sensitivities,
not event-level mechanism claims, and they never acquire a historical label
merely by matching a known outcome.

### Normal completion and unresolved work

A run reaches `NORMAL_COMPLETE` when the configured horizon has arrived, all
due same-time transitions have been committed, no executable event remains at
or before the horizon, and every nonterminal business object is either:

- explicitly carried forward with owner, state, version, unresolved reason,
  and next event beyond the horizon; or
- closed, expired, withdrawn, failed, or otherwise terminal under its
  lifecycle.

Normal completion does not require a historical suspension, rescue, pool,
certificate issue, market stabilization, or any other known outcome.

A run is `BOUNDED_INCOMPLETE` when execution remains internally valid but a
required exogenous input, unresolved authority/evidence choice, or active
object prevents the declared research question from being answered. Its trace
is retained, but it is not treated as a complete scenario result.

A run is `FAILED_CLOSED` on identity/hash mismatch, unauthorized future or
hidden information, duplicate entity/resource authority, mixed-version
compound observation, invalid lifecycle transition, silently repaired intent,
resource conservation failure, reducer/version inconsistency, nonreplayable
causal ordering, or an autonomous choice required from an unmodeled actor.

### Reproducibility identity

The reproducibility record pins at least:

- Roster Definition release ID, commit, manifest hash, and product hashes;
- consolidated mapping ID/hash and mapping-profile identity;
- Scenario Definition ID/version/hash and exact configuration hash;
- evidence ledger/use-boundary and source-register hashes;
- structural-variant and participant-profile assignments;
- entity/actor/capability/population-unit assembly, hosts, weights, authority,
  relationships, initial resources, routes, and lifecycle policies;
- applicable Contracts and component versions;
- backend/policy identity and random sources/seed; and
- horizon, scheduler/tie policy, and any labeled construction assumption.

Rule and future LLM backends must receive the same frozen external semantic
envelope. A backend-specific prompt, memory, input, action, route, or hidden
state changes identity and is not a conforming comparison.

## 10. Worked cases, falsification, limitations, and provenance

### Case 1 — Knickerbocker to NBC to NYCH request lineage

**Evidence class.** `RECONSTRUCTED / FULL_DRAFT_EXPOSED`.

**Prestate.** KT has a positive support need, a scoped authorization result,
an active NBC route, sufficient bounded request content, and no equivalent
pending request. NBC has a valid relationship and receives only the KT request
hop; NYCH has no case.

**Expected process.** KT may submit one request. `LF-SUPPORT` creates the KT
object and `WS-COMM` routes it to NBC. NBC classifies courier, sponsor,
representative, joint, declined, or unresolved role under its authority. A
permitted forward/sponsorship action creates a second hop carrying the original
request, represented sender, unchanged content, NBC role, and provenance.
Only delivery to NYCH can create a NYCH intake observation and case.

**Invalid attempts.** KT declaring NYCH receipt; NBC silently adding
sponsorship; duplicate pending request; NYCH using an undelivered request.

**Perturbation.** Remove NBC sponsorship authority. Pure forwarding may remain
available, but an NBC endorsement must disappear. Removing final-hop delivery
must leave NYCH without the request.

### Case 2 — compound exposure observation with incoherent versions

**Evidence class.** `ILLUSTRATIVE CONFORMANCE CASE`.

**Prestate.** NBC's projected `clearing_exposure_record` combines balances from
version 4 with obligations from superseded version 3.

**Expected process.** `IP-RESOURCE` rejects the compound projection as
incoherent and delivers `disputed`/`unknown` according to the released domain.
NBC may verify or narrow action. The reference cannot expose live version 4 to
the backend.

**Perturbation.** Replace all material components with the coherent version-4
snapshot. The observation becomes deliverable; its system audit label remains
invisible to NBC.

### Case 3 — host-scoped depositor request and partial service

**Evidence class.** `ILLUSTRATIVE / SYNTHETIC POPULATION`.

**Prestate.** A TCA-hosted later-depositor unit has one positive claim, no
pending request, a disclosed responsive profile, and a newly delivered
host-scoped adverse signal. Lincoln and Knickerbocker private state exist but
are not visible.

**Expected process.** The unit creates one TCA request. `LF-WITHDRAWAL`
adjudicates host/claim identity, service admission, queue, capacity, and
payment. A partial certified-check result reduces only the realized claim
component, preserves payment form, and later reopens only the remainder when
the lifecycle permits.

**Perturbation.** Change only the host to Lincoln without changing claim and
signal identities. Assembly or intent validation fails; no cross-host repair is
allowed.

### Case 4 — NYCH route interpretation

**Evidence class.** `STRUCTURAL_SENSITIVITY`.

**Prestate.** The same delivered nonmember focal request, member-facility
restriction, available information, and NYCH authority are used in two runs.

**Expected process.** Under the conservative baseline, absent evidence of a
competent alternative route produces information seeking, typed decline,
referral only to an evidenced route, or bounded closure. Under the discretion
sensitivity, a separately competent and authorized alternative may support a
conditioned proposal. Neither route declares resources committed or aid
executed.

**Perturbation.** Remove competent-route authority in the sensitivity. The
conditioned proposal must become unavailable; the two variants converge at the
shared boundary.

### Case 5 — one bank, two capabilities, one resource owner

**Evidence class.** `ILLUSTRATIVE CONFORMANCE CASE`.

**Prestate.** One member bank actor composes `bank_resource_decision` and
`call_money_lender`. It receives a committee solicitation and a broker funding
request against one bounded resource envelope.

**Expected process.** Both decisions may emit separate offer intents, but
resource adjudication uses one prestate and one owner. Same-prestate
concurrency can reserve, partially admit, condition, delay, or reject the
second demand under a deterministic rule. No capability receives its own copy
of capacity.

**Perturbation.** Give each capability a separate resource owner. Assembly
fails before behavior; aggregate funding may not be reported.

### Case 6 — TCA examination, collateral, service, and route separation

**Evidence class.** `RECONSTRUCTED / FULL_DRAFT_EXPOSED`.

**Prestate.** TCA receives a scoped examination request, a service-condition
notice, and two support routes. Disclosure authority is pending; one
collateral package is controlled but not valued.

**Expected process.** TCA may seek/receive authority, consent and provide a
scoped package; the examiner owns the report. It may separately propose an
operating posture and route-specific collateral/request objects. Service
execution, collateral valuation/acceptance, recipient commitments, and funds
remain separate results. One route's decline does not close the other.

**Perturbation.** Remove collateral control. Proposal admission fails for that
package without changing examination consent or the independent route.

### Case 7 — Morgan, committee, and independent contributors

**Evidence class.** `RECONSTRUCTED / STRUCTURAL`.

**Prestate.** A committee report is delivered to Morgan; the committee has a
separate mandate and Morgan owns a versioned proposal. Three institutions are
eligible independent contributors.

**Expected process.** Morgan may form and circulate a proposal and issue one
solicitation per target. The committee report remains committee-produced.
Each institution conditions, commits, declines, or requests information under
its own authority/resource state. Morgan assembles only delivered unexpired
replies. Target amount, invitations, advice, and silence create no resources.

**Perturbation.** Make the committee—not Morgan—the owner of a second plan with
an equivalent solicitation. The overlap check must retain both plan identities
and produce a typed duplicate/conflict decision; it may not merge ownership.

### Case 8 — broker replacement funding and adverse result

**Evidence class.** `RECONSTRUCTED / FULL_DRAFT_EXPOSED`.

**Prestate.** A broker receives a valid call that creates a positive bounded
funding gap, has a delivered regular-bank route and controlled collateral, and
holds no position-reduction authority.

**Expected process.** It may request replacement funding and submit controlled
collateral. A lender may condition an offer; the broker may accept, request
revision, or decline. Acceptance does not book funds. A partial booking and
transfer reduce only the realized gap. Position reduction remains
inadmissible without authority.

**Perturbation.** Deliver scoped position authority and select the parallel
response posture. A separate `LF-POSITION` request becomes possible; it still
cannot self-execute or create sale proceeds.

### Case 9 — Lincoln authorized issue, delivery failure, and correction

**Evidence class.** `RECONSTRUCTED / FULL_DRAFT_EXPOSED`.

**Prestate.** Lincoln has current supporting information, a competent decision
forum, and an authorized exact statement version.

**Expected process.** Lincoln may issue once. A transport failure preserves
authorization and issue but creates no public observation. A later material
information update may produce a linked correction/withholding decision; the
old message remains immutable.

**Perturbation.** Remove decision authority. Issue is rejected even when the
content is historically known and reassuring.

### Case 10 — duplicate, expiry, and deterministic replay

**Evidence class.** `CROSS-FAMILY CONFORMANCE CASE`.

**Prestate.** A request, solicitation, withdrawal, and loan offer are each
pending at known versions. The same decisions are replayed against the same
prestate, scheduler order, configuration, and seed.

**Expected process.** Each equivalent duplicate receives the same typed
disposition and creates no second business object or resource effect. After an
expiry/reopening event, a versioned replacement may be admitted when the
released semantics permit it. Replaying the complete causal record produces
the same object versions, dispositions, state deltas, and final identity.

**Perturbation.** Change only a material parameter or target. The idempotency
identity changes only if the semantic object is genuinely revised; silent
duplicate evasion is rejected.

### Event-level falsification plan

| Test | Expected implication | Failure ownership |
|---|---|---|
| remove an authority record | affected intent narrows, seeks authority, or fails; unrelated capabilities remain | Scenario if authority leaked; Definition if behavior does not respond as declared |
| withhold a message/report/result | recipient cannot use its content; later behavior changes only after delivery | Scenario/information mapping |
| swap historical names while retaining semantics | permissible envelope is unchanged | Definition/backend name scripting |
| change one host/unit private state | no other host/unit reads it | Scenario assembly/visibility |
| constrain one multi-capability institution's resource | all its capability surfaces use the same new envelope; other institutions do not | Scenario resource ownership |
| change one contributor reply | only linked plan component and valid aggregate change | Scenario lifecycle/plan mapping |
| replace executed with partial/failed/no-effect | only realized component updates and later feedback differs | Scenario adjudication/result mapping |
| remove a route or contract right | route-dependent intent becomes unavailable; urgency cannot recreate it | Scenario relationship/contract semantics |
| inject future outcome or later institutional rule | projection is rejected | Evidence/time boundary or implementation |
| replay identical sealed causal inputs | identical ordered states/results and identity | implementation/reducer; concrete carrier failure only if irreducible |
| delete an entire scenario process | corresponding released observations/intents lose a producer/adjudicator | Scenario minimality/closure; unused process should be removed |

Failures route to the smallest owning layer. A missing historical fact returns
to evidence; a wrong participant mechanism to the Definition release; a world,
route, information, lifecycle, or result gap to this Scenario Definition; a
capability/field projection gap to mapping; a coding or replay mismatch to
implementation; and only a reproducible, irreducible V1 semantic loss to a
narrow Contracts review.

### Limitations

The Definition does not recover exact intraday chronology, institution books,
depositor microdata, private decision records, committee votes, contributor
policies, call contracts, collateral values, queue discipline, market
matching, or resource totals. Several institutional events are exogenous
because their decision makers are outside the accepted roster. Population
profiles, posture assignments, amount methods, route coverage, and many
resource states are declared sensitivities. The NYSE is a scenario-owned
process, not a validated historical microstructure model. The later NYCH
facility supply is not an action of the focal NYCH Agent.

The design is broad enough to connect all released roles, but it must be
implemented incrementally. Interface closure is not evidence that every
mechanism should be activated in one first run or that a full-event result is
scientifically interpretable before focused component tests.

### References

The event evidence ledger and source register hold page-level adoption,
archived assets, conflicts, and SHA-256 identities. Principal conventional
references for this Scenario Definition are:

- Cannon, James G. 1910. *Clearing-House Methods and Practices*.
- *Commercial and Financial Chronicle*. 26 October 1907, “New York Banking
  Affairs.”
- “The New Legislation Affecting Clearing for Non-Members in the New York
  Clearing House.” 1907. *The Banking Law Journal* 24 (8).
- Moen, Jon R., and Ellis W. Tallman. 1995. “Clearinghouse Access and Bank
  Runs: Comparing New York and Chicago During the Panic of 1907.”
- Moen, Jon R., and Mary Tone Rodgers. 2022. “How J. P. Morgan Picked the
  Winners and Losers in the Panic of 1907.”
- New York Clearing House Association. 1906–1907. Constitution and amendments.
- *New-York Tribune*. 22–23 October 1907.
- Simon, Herbert A. 1956. “Rational Choice and the Structure of the
  Environment.” *Psychological Review* 63 (2): 129–138.
- Sprague, O. M. W. 1910. *History of Crises Under the National Banking
  System*.
- U.S. House of Representatives. 1911. *United States Steel Corporation:
  Hearings*.
- U.S. House of Representatives. 1913. *Money Trust Investigation* and the
  associated committee report.

### Provenance and version history

`0.1.0` is the first accepted event-level Scenario Definition. It was
normalized from owner-accepted candidate `0.1.0-candidate.1`, SHA-256
`d8a198495394e2ea942e3ca91f55e355ba54de533461bebb5893293cf30808c7`,
after complete interface closure and substantive review. The normalization
changes status, version, and provenance wording only.

The Definition was derived from the fixed Roster Definition release, accepted
consolidated mapping and carrier review, event semantic skeleton, accepted
evidence ledger and source register, all twelve released semantic products,
and their five interface preflights. No new source, network access, simulation
result, Rule policy, LLM output, or held-out evidence was used.

The accepted Definition adds no participant behavior. It assigns event-world
ownership, defines information and business-process semantics, and identifies
the configuration and structural decisions required before implementation.
Exact executable values remain the responsibility of a separately reviewed,
versioned scenario configuration.
