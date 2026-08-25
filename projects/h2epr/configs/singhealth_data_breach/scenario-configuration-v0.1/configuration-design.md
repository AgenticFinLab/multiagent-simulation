# H2EPR-0616 Scenario Configuration design

## Configuration identity

| Field | Value |
|---|---|
| Event ID | `H2EPR-0616` |
| Configuration ID | `h2epr.0616.scenario.mechanism-coverage.v0_1` |
| Version | `0.1.0` |
| Status | accepted non-executable configuration |
| Declared purpose | mechanism coverage |
| Modeled interval | approximately 23 August 2017 through the 20 July 2018 core horizon, with notification delivery observed through 23 July 2018 |
| Historical calibration | no |
| Historical validation | no |
| Known-outcome fitting | no |
| Machine representation | `scenario-configuration.json`, using provisional semantic format `h2epr.scenario-configuration-semantic-candidate.v0_1` |
| Accepted configuration decisions | `OD-CFG-05` through `OD-CFG-08` |

## 1. Purpose and claim boundary

This configuration assembles the accepted participant and Scenario semantics so
that fragmented information, qualified technical-to-institutional escalation,
delayed or failed delivery, and typed results can be studied in one coherent
mechanism-coverage setting. It fixes configuration-owned choices; it does not
redefine the Event Scenario Definition or any participant.

The configuration declares a clock, canonical institutions and technical objects,
actor and responsibility-unit identities, opening records, bounded exogenous
inputs, selected policy meanings, sensitivity alternatives, and completion
rules. It does not establish a historical replay, calibration, prediction,
policy-effectiveness result, or empirical, historical, or scientific validity.

The known outcome informed construction of the event assets but is not a target
to be reproduced. No private state, delivery result, technical result,
institutional decision, or notification result is selected to force it.

## 2. Pinned semantic inputs

| Input authority | Stable identity | SHA-256 | Consumed scope |
|---|---|---|---|
| Event Scenario Definition release | `H2EPR-0616-EVENT-SCENARIO-DEFINITION-v0.1` | `948b9ba9e29ba6947abefd65663bd4e9ef1ff47ebb1f465a08524378b20b8795` | release identity and closure |
| Event Scenario Definition | `h2epr.scenario.0616.singhealth_data_breach@0.1.0` | `1e670f70c6755243dad354b268b1bad16a8240b2220b7577f18708af9cb07401` | world, information, lifecycle, result, and boundary semantics |
| Scenario interface closure | released artifact | `3d3909b3454780205289167531b60fa0b02640296b2e25441972bbe336216039` | Definition-to-participant obligations |
| Roster Definition release | `H2EPR-0616-ROSTER-DEFINITION-RELEASE-v0.1` | `188f5117f02958997f8e1140d3d19fcbada296b1750223d8b3025e1cf537625e` | seven Agent Definitions and two Population Models |
| Consolidated mapping release | `H2EPR-0616-CONSOLIDATED-MAPPING-v0.1` | `7a603d97bb25f8dddab08d7a8865fd6305a94e4db108f5f32b8ad65d28695bb9` | semantic inventory and carrier obligations |
| Mapping profile | `h2epr.roster-consolidated-mapping.0616.v0_1` | `1249dbe94dcad61b40c4e543435186e6e71eaab0d95c7f2877e31c0e3575a1bb` | capability-qualified placement rules |
| Semantic skeleton | version `0.2` | `8c68e9b3f52d2d31f3482be7588418fe9b4209770e8e28cce8d1c16b3bf5556f` | research question and event-level roles |
| Event-frame evidence | accepted event-frame evidence | `b3dc712fcf182bedbb7654cbc7ab7d4e09f8022c737c12ea152171fe26d56f74` | event frame and dated constraints |
| Participant evidence | accepted participant evidence | `d37bcd8df93082226a69c10674f61b76d4f36eb6651344273f38768091e1f5f0` | identities, offices, responsibilities, capacities, and routes |

Each integrity value is computed over the accepted artifact named in the table.
No implementation behavior or simulation output supplies a semantic default.

## 3. Execution boundary

The configuration is not execution eligible. The provisional representation has not
been admitted by a machine schema or exact loader; the nine policy meanings are
unbound; and no carrier projection, participant binding, runtime identity, or
execution authorization exists. A consumer must reject execution while any of
these conditions remains unresolved. Parsing the document changes none of them.

The existing v0.1 admission schema does not represent this event's
responsibility-unit structure without event-inapplicable fields. The configuration
therefore identifies its semantic format explicitly and makes no schema-
conformance claim. Compatibility or schema evolution belongs to a separately
reviewed admission stage.

## 4. Clock and structural baseline

### Clock and causal order

The timezone is `Asia/Singapore` and the clock is event driven. The modeled
start is approximately 23 August 2017; participant response begins on
18 January 2018; and the acute interval runs from 11 June through 20 July 2018.
The core horizon is 20 July, while recipient-specific notification observation
may continue through 23 July. These bounds preserve accepted date precision and
do not imply that the incident or its consequences ended on either date.

At equal modeled times, the configuration first admits exogenous input, then
processes Scenario or technical events, produces information, transports and
delivers it, freezes observations, permits participant decisions, adjudicates
and executes intents, applies typed state deltas, and only then exposes later
information. Stable event identity breaks otherwise unordered ties. Intraday
precision absent from the evidence is not invented.

### Structural selections

| Structural ID | Baseline selection | Basis | Causal limit | Sensitivity |
|---|---|---|---|---|
| `SV-0616-ATTACK-PRESSURE` | `BOUNDED_ADVERSARIAL_OPPORTUNITY_PROCESS` | `0616-FR-C01`; `0616-FR-C02`; `0616-FR-C03` | opens opportunities but selects no access, persistence, query, copy, or disclosure result | `SENS-0616-ATTACK-DELAY` |
| `SV-0616-ROUTE-DELIVERY` | `DISTINCT_NAMED_ROUTES_WITH_EXPLICIT_DELIVERY` | `0616-FR-C11`; `0616-FR-C12`; `0616-FR-C14`; `0616-FR-C15` | eligibility implies neither issue nor receipt, acknowledgement, interpretation, or action | `SENS-0616-ROUTE-DELAY` |
| `SV-0616-RESPONSIBILITY-UNITS` | `INSTITUTION_PRESERVING_FUNCTION_SPECIFIC_UNITS` | `OD-R1-01`, `OD-R2-01`, `OD-SC-07` | composition creates no shared knowledge, authority, state, or policy | `SENS-0616-NARROWER-UNIT-SET` |
| `SV-0616-OFFICE-CAPACITY` | `CAPACITY_QUALIFIED_AUTHORITY_AND_ROUTES` | `0616-R1-C07`; `0616-R2-C31`; `0616-R2-C32`; `OD-SC-07` | title supplies neither availability nor authority outside the selected capacity | `SENS-0616-OFFICE-COVERAGE-DELAY` |
| `SV-0616-TECHNICAL-RESULT` | `AUTHORITY_PRESTATE_ACCESS_AND_FEASIBILITY_ADJUDICATED` | `OD-SC-07`, `OD-CM-06` | defines adjudication dimensions, not a realized result | `SENS-0616-TECHNICAL-NO-EFFECT` |
| `SV-0616-NOTIFICATION` | `PLANNING_AUTHORIZATION_ISSUE_DELIVERY_SEPARATED` | `0616-FR-C04`; `0616-R2-C20`; `0616-R2-C21`; `0616-R2-C22`; `0616-R2-C23`; `0616-R2-C24` | planning, advice, authorization, issue, delivery, correction, and receipt remain distinct | `SENS-0616-NOTIFICATION-PARTIAL` |

The machine document materializes every baseline in a corresponding profile.
This makes each sensitivity operation exact without adding a calibrated value or
reproducing a historical outcome.

## 5. Actor and responsibility-unit assembly

### Named office actors

| Actor ID | Participant product | Primary institution | Capacity ID(s) | Authority graph |
|---|---|---|---|---|
| `actor.0616.office.cluster-iso` | Cluster Information Security Officer | IHiS | `capacity.0616.ihis.cluster-iso` | `authority.0616.office.cluster-iso` |
| `actor.0616.office.sector-lead` | Cyber Security Governance Director and Healthcare Sector Lead | IHiS | `capacity.0616.ihis.csg-director`; `capacity.0616.moh.healthcare-sector-lead` | `authority.0616.office.sector-lead` |
| `actor.0616.office.ihis-ceo` | IHiS Chief Executive Officer | IHiS | `capacity.0616.ihis.ceo`; `capacity.0616.moh.cio` | `authority.0616.office.ihis-ceo` |
| `actor.0616.office.sirm` | Security Incident Response Manager | IHiS | `capacity.0616.ihis.sirm` | `authority.0616.office.sirm` |
| `actor.0616.office.singhealth-deputy-gceo` | SingHealth Deputy Group Chief Executive Officer | SingHealth | `capacity.0616.singhealth.deputy-gceo` | `authority.0616.office.singhealth-deputy-gceo` |
| `actor.0616.office.singhealth-gceo` | SingHealth Group Chief Executive Officer | SingHealth | `capacity.0616.singhealth.gceo` | `authority.0616.office.singhealth-gceo` |
| `actor.0616.office.singhealth-gcio` | SingHealth Group Chief Information Officer | IHiS | `capacity.0616.ihis.gcio-service-lead`; `capacity.0616.singhealth.gcio` | `authority.0616.office.singhealth-gcio` |

Each office authority record names its capacity scope, granting institution,
configuration-effective interval, and availability rule. Concurrent capacities
are not interchangeable: an intent must name the capacity under which it is
issued. The GCIO remains one actor with separate IHiS and SingHealth routes;
those routes do not merge knowledge, authority, resources, or delivery history.

### Population responsibility units

| Unit ID | Actor ID | Function and host | Capacity ID | Access scope IDs |
|---|---|---|---|---|
| `unit.0616.technical.security-engineering` | `actor.0616.unit.technical.security-engineering` | security engineering; IHiS | `capacity.0616.unit.technical.security-engineering` | host, account, network-route, and monitoring/control contexts |
| `unit.0616.technical.infrastructure-citrix` | `actor.0616.unit.technical.infrastructure-citrix` | infrastructure and Citrix; IHiS | `capacity.0616.unit.technical.infrastructure-citrix` | host, account, credential, network-route, and monitoring/control contexts |
| `unit.0616.technical.scm-application-database` | `actor.0616.unit.technical.scm-application-database` | SCM application and database; IHiS | `capacity.0616.unit.technical.scm-application-database` | SCM system, application, database, account, credential, and monitoring/control contexts |
| `unit.0616.operations.infrastructure-coordination` | `actor.0616.unit.operations.infrastructure-coordination` | infrastructure coordination; IHiS | `capacity.0616.unit.operations.infrastructure-coordination` | host, network-route, and monitoring/control coordination context |
| `unit.0616.operations.application-scm-coordination` | `actor.0616.unit.operations.application-scm-coordination` | application and SCM coordination; IHiS | `capacity.0616.unit.operations.application-scm-coordination` | SCM system, application, and database coordination context |
| `unit.0616.operations.cluster-coordination` | `actor.0616.unit.operations.cluster-coordination` | SingHealth cluster coordination; IHiS | `capacity.0616.unit.operations.cluster-coordination` | SCM system, network-route, and monitoring/control coordination context |

Each unit has one actor, host, function, assignment, capacity, availability
record, composition, private state, and result history. Technical access and
coordination context are distinguished. Reusing a Population Model creates
neither a collective actor nor shared observations, intents, or results.

### Canonical technical objects

| Object ID | Kind | Ownership / operation | Opening interpretation |
|---|---|---|---|
| `asset.0616.system.scm` | system | SingHealth / IHiS | identity present; operational and security state unknown |
| `asset.0616.application.scm` | application | SingHealth / IHiS | identity present; operational and security state unknown |
| `asset.0616.database.scm` | database | SingHealth / IHiS | identity present; operational and security state unknown |
| `asset.0616.host.supporting-context` | host context | ownership unresolved / IHiS-bounded operation | bounded identity envelope; exact hosts and prestate unknown |
| `asset.0616.account.assigned-context` | account context | ownership unresolved / IHiS-bounded operation | bounded identity envelope; exact accounts, assignments, and prestate unknown |
| `asset.0616.credential.assigned-context` | credential context | ownership unresolved / IHiS-bounded operation | bounded identity envelope; exact credentials, assignments, and prestate unknown |
| `asset.0616.network.assigned-route-context` | network-route context | ownership unresolved / IHiS-bounded operation | bounded identity envelope; exact routes, reachability, and prestate unknown |
| `asset.0616.monitoring-control.assigned-context` | monitoring/control context | ownership unresolved / IHiS-bounded operation | bounded identity envelope; exact controls, coverage, and prestate unknown |

The context objects provide stable references without inventing an asset
inventory. Exact instances and states may enter only through admitted,
assignment-scoped input and delivery.

## 6. Opening records and exogenous inputs

### Opening-record crosswalk

All 33 opening records have an explicit owner, target or endpoint set,
identification class, visibility, source class, and basis. Effective intervals
on office and unit records describe this configuration's scope, not a claim
about complete historical tenure or staffing.

| Record ID | Family | Exact target or endpoints | Basis | Opening meaning |
|---|---|---|---|---|
| `opening.0616.authority.cluster-iso` | authority/capacity | `actor.0616.office.cluster-iso` | `0616-R1-C13`; `OD-SC-07`; `OD-CFG-07` | cluster-ISO capacity, interval, and qualified availability |
| `opening.0616.authority.sector-lead` | authority/capacity | `actor.0616.office.sector-lead` | `0616-R2-C10`; `0616-R2-C32`; `OD-SC-07`; `OD-CFG-07` | separate IHiS CSG and MOH sector-lead capacities |
| `opening.0616.authority.ihis-ceo` | authority/capacity | `actor.0616.office.ihis-ceo` | `0616-R2-C11`; `0616-R2-C31`; `OD-SC-07`; `OD-CFG-07` | separate IHiS CEO and MOH CIO capacities |
| `opening.0616.authority.sirm` | authority/capacity | `actor.0616.office.sirm` | `0616-R1-C01`; `0616-R1-C07`; `OD-SC-07`; `OD-CFG-07` | SIRM authority with explicit absence/coverage qualification |
| `opening.0616.authority.singhealth-deputy-gceo` | authority/capacity | `actor.0616.office.singhealth-deputy-gceo` | `0616-R2-C18`; `0616-R2-C20`; `0616-R2-C21`; `0616-R2-C22`; `0616-R2-C23`; `OD-CFG-07` | SingHealth supervisory capacity |
| `opening.0616.authority.singhealth-gceo` | authority/capacity | `actor.0616.office.singhealth-gceo` | `0616-R2-C19`; `0616-R2-C20`; `0616-R2-C22`; `0616-R2-C23`; `0616-R2-C24`; `OD-CFG-07` | SingHealth executive capacity |
| `opening.0616.authority.singhealth-gcio` | authority/capacity | `actor.0616.office.singhealth-gcio` | `0616-R2-C08`; `0616-R2-C09`; `0616-R2-C17`; `OD-CFG-07` | distinct IHiS and SingHealth capacities without shared authority |
| `opening.0616.assignment.technical.security-engineering` | unit assignment | `unit.0616.technical.security-engineering` | `0616-R1-C03`; `0616-R1-C14`; `0616-R1-C17`; `OD-R1-01`; `OD-CFG-07` | security-engineering function, interval, availability, and exact access scopes |
| `opening.0616.assignment.technical.infrastructure-citrix` | unit assignment | `unit.0616.technical.infrastructure-citrix` | `0616-R1-C04`; `0616-R1-C05`; `0616-R1-C17`; `OD-R1-01`; `OD-CFG-07` | infrastructure/Citrix function, interval, availability, and exact access scopes |
| `opening.0616.assignment.technical.scm-application-database` | unit assignment | `unit.0616.technical.scm-application-database` | `0616-R1-C06`; `0616-R1-C16`; `0616-R2-C02`; `OD-R1-01`; `OD-CFG-07` | SCM technical function, interval, availability, and exact access scopes |
| `opening.0616.assignment.operations.infrastructure-coordination` | unit assignment | `unit.0616.operations.infrastructure-coordination` | `0616-R2-C01`; `0616-R2-C03`; `0616-R2-C05`; `0616-R2-C06`; `OD-R2-01`; `OD-CFG-07` | infrastructure-coordination function and scoped context |
| `opening.0616.assignment.operations.application-scm-coordination` | unit assignment | `unit.0616.operations.application-scm-coordination` | `0616-R2-C02`; `0616-R2-C04`; `0616-R2-C07`; `0616-R2-C25`; `OD-R2-01`; `OD-CFG-07` | application/SCM coordination function and scoped context |
| `opening.0616.assignment.operations.cluster-coordination` | unit assignment | `unit.0616.operations.cluster-coordination` | `0616-R2-C01`; `0616-R2-C03`; `0616-FR-C07`; `OD-R2-01`; `OD-CFG-07` | cluster-coordination function and scoped context |
| `opening.0616.relationship.ihis-singhealth-scm` | institutional relationship | `institution.0616.ihis` ↔ `institution.0616.singhealth` | `0616-FR-C05`; `0616-FR-C06`; `0616-FR-C07`; `0616-FR-C08` | IHiS operation remains distinct from SingHealth ownership and supervision |
| `opening.0616.route.technical-security` | route | `actor.0616.unit.technical.security-engineering`; `actor.0616.unit.technical.infrastructure-citrix`; `actor.0616.unit.technical.scm-application-database` ↔ `actor.0616.office.sirm`; `actor.0616.office.cluster-iso` | `0616-R1-C02`; `0616-R1-C03`; `0616-R1-C04`; `0616-R1-C14` | one exact sender and recipient per message |
| `opening.0616.route.technical-operations` | route | `actor.0616.unit.technical.security-engineering`; `actor.0616.unit.technical.infrastructure-citrix`; `actor.0616.unit.technical.scm-application-database` ↔ `actor.0616.unit.operations.infrastructure-coordination`; `actor.0616.unit.operations.application-scm-coordination`; `actor.0616.unit.operations.cluster-coordination` | `0616-R1-C04`; `0616-R1-C05`; `0616-R1-C06`; `0616-R2-C03`; `0616-R2-C04` | assignment-qualified, explicitly addressed technical/operational exchange |
| `opening.0616.route.operations-gcio` | route | `actor.0616.unit.operations.infrastructure-coordination`; `actor.0616.unit.operations.application-scm-coordination`; `actor.0616.unit.operations.cluster-coordination` ↔ `actor.0616.office.singhealth-gcio` | `0616-R2-C04`; `0616-R2-C05`; `0616-R2-C06`; `0616-R2-C07`; `0616-R2-C09` | explicitly addressed operational escalation or clarification |
| `opening.0616.route.gcio-ihis` | route | `actor.0616.office.singhealth-gcio` ↔ `actor.0616.office.ihis-ceo`; `actor.0616.office.sector-lead` | `0616-R2-C08`; `0616-R2-C09` | IHiS-capacity route with recipient-specific history |
| `opening.0616.route.gcio-singhealth` | route | `actor.0616.office.singhealth-gcio` ↔ `actor.0616.office.singhealth-deputy-gceo`; `actor.0616.office.singhealth-gceo` | `0616-R2-C08`; `0616-R2-C17`; `0616-R2-C18`; `0616-R2-C19` | SingHealth-capacity route with recipient-specific history |
| `opening.0616.route.sector-csa` | route | `actor.0616.office.sector-lead` ↔ `institution.0616.csa` | `0616-R2-C10`; `0616-R2-C12`; `0616-R2-C14`; `0616-R2-C16` | sector-lead-capacity route; no automatic reporting or receipt |
| `opening.0616.route.singhealth-moh` | route | `actor.0616.office.singhealth-gcio`; `actor.0616.office.singhealth-deputy-gceo`; `actor.0616.office.singhealth-gceo` ↔ `institution.0616.moh` | `0616-R2-C17`; `0616-R2-C18`; `0616-R2-C19`; `0616-R2-C20`; `0616-R2-C21`; `0616-R2-C22`; `0616-R2-C23`; `0616-R2-C24` | sender-capacity-qualified SingHealth/MOH route |
| `opening.0616.route.institutional-mci` | route | `institution.0616.singhealth` ↔ `institution.0616.mci` | `0616-FR-C14`; `0616-FR-C15` | route remains distinct from MOH and CSA routes |
| `opening.0616.technical.system.scm` | technical state | `asset.0616.system.scm` | `0616-FR-C05`; `0616-FR-C06`; `0616-FR-C08`; `0616-FR-C09`; `OD-CFG-07` | canonical identity present; state unknown |
| `opening.0616.technical.application.scm` | technical state | `asset.0616.application.scm` | `0616-FR-C05`; `0616-FR-C06`; `0616-FR-C08`; `0616-FR-C09`; `0616-R2-C02`; `OD-CFG-07` | canonical identity present; state unknown |
| `opening.0616.technical.database.scm` | technical state | `asset.0616.database.scm` | `0616-FR-C05`; `0616-FR-C06`; `0616-FR-C08`; `0616-FR-C09`; `0616-R1-C06`; `OD-CFG-07` | canonical identity present; state unknown |
| `opening.0616.technical.host-context` | technical state | `asset.0616.host.supporting-context` | `0616-FR-C09`; `0616-FR-C17`; `0616-R1-C03`; `0616-R1-C04`; `OD-CFG-07` | exact hosts and prestate unknown until admitted context |
| `opening.0616.technical.account-context` | technical state | `asset.0616.account.assigned-context` | `0616-FR-C09`; `0616-R1-C04`; `0616-R1-C17`; `OD-CFG-07` | exact accounts, assignments, and prestate unknown |
| `opening.0616.technical.credential-context` | technical state | `asset.0616.credential.assigned-context` | `0616-FR-C09`; `0616-R1-C04`; `0616-R1-C17`; `OD-CFG-07` | exact credentials, assignments, and prestate unknown |
| `opening.0616.technical.network-route-context` | technical state | `asset.0616.network.assigned-route-context` | `0616-FR-C09`; `0616-FR-C17`; `0616-R1-C03`; `0616-R1-C17`; `OD-CFG-07` | exact routes, reachability, and prestate unknown |
| `opening.0616.technical.monitoring-control-context` | technical state | `asset.0616.monitoring-control.assigned-context` | `0616-FR-C17`; `0616-FR-C18`; `0616-R1-C03`; `0616-R1-C06`; `0616-R1-C16`; `0616-R1-C17`; `OD-CFG-07` | exact controls, coverage, and prestate unknown |
| `opening.0616.incident-process` | business-object state | `process.0616.incident-and-response` | `OD-CFG-05`; `OD-CFG-07`; `OD-SC-07` | no authoritative incident object at the modeled start |
| `opening.0616.notification-process` | business-object state | `process.0616.notification` | `OD-CFG-05`; `OD-CFG-07`; `OD-SC-07` | no plan, authorization, issue, or delivery object at the modeled start |
| `opening.0616.affected-cohort` | cohort state | `process.0616.affected-cohort` | `OD-CFG-05`; `OD-CFG-07`; `OD-SC-07` | no authoritative exposure or recipient-delivery result at the modeled start |

### Exogenous inputs

| Input ID | Activation | Exact target IDs | Typed effect | Causal limit | Outcome forcing? |
|---|---|---|---|---|---|
| `exo.0616.bounded-attack-opportunity` | approximate modeled start or bounded window | `process.0616.attack` | opens an adjudicated access or execution opportunity | selects no success, persistence, scope, detection, query, copy, disclosure, or containment | no |
| `exo.0616.endpoint-account-context` | when an admitted technical opportunity requires context | `asset.0616.host.supporting-context`; `asset.0616.account.assigned-context`; `asset.0616.credential.assigned-context`; `asset.0616.network.assigned-route-context`; `asset.0616.monitoring-control.assigned-context` | supplies bounded precondition context to exact assets and then eligible assigned units | supplies neither user choice nor shared technical knowledge | no |
| `exo.0616.institutional-framework-and-appointments` | modeled boundary or later effective change | `opening.0616.authority.cluster-iso`; `opening.0616.authority.sector-lead`; `opening.0616.authority.ihis-ceo`; `opening.0616.authority.sirm`; `opening.0616.authority.singhealth-deputy-gceo`; `opening.0616.authority.singhealth-gceo`; `opening.0616.authority.singhealth-gcio` | versions authority, capacity, and route context | appointment supplies neither delivery nor action | no |
| `exo.0616.office-capacity-events` | accepted capacity record becomes effective or is delivered | `opening.0616.authority.sirm`; `opening.0616.authority.sector-lead`; `opening.0616.authority.ihis-ceo` | versions availability, coverage, or capacity qualification | assumes no delegation, access, or response | no |
| `exo.0616.government-response-opportunities` | eligible report or request reaches a named route | `opening.0616.route.sector-csa`; `opening.0616.route.singhealth-moh`; `opening.0616.route.institutional-mci` | admits recipient-specific acknowledgement, coordination, or authorization opportunities | merges no institution and guarantees no response | no |
| `exo.0616.notification-authorization-and-delivery-opportunity` | an eligible plan reaches an authorization or delivery gate | `process.0616.notification`; `process.0616.affected-cohort` | admits authorization, issue, delivery, failure, or correction opportunities | selects no approval, issue, delivery, receipt, or historical success | no |

## 7. Policy semantics

| Policy ID | Selected meaning | Closed semantic family | Binding consequence |
|---|---|---|---|
| `POL-0616-TIME-01` | event-driven partial order with declared same-time precedence | clock, phase order, and reopening | unbound; fail closed |
| `POL-0616-INFO-01` | source, version, route, delivery, freshness, correction, and visibility separated | information production and observation | unbound; fail closed |
| `POL-0616-TECH-01` | authority, prestate, access, and feasibility adjudicated without selected result | technical access, control, query, copy, disclosure, and monitoring | unbound; fail closed |
| `POL-0616-ROUTE-01` | named recipient routes with distinct issue, transport, delivery, and acknowledgement | communication, escalation, reporting, and feedback | unbound; fail closed |
| `POL-0616-COORD-01` | invitation, attendance, presented material, assignment, and result separated | meeting, coordination, SIRT, and assignment | unbound; fail closed |
| `POL-0616-AUTH-01` | capacity-qualified authority, relationship, access, and resource checks | institutions, offices, units, capacity, and resources | unbound; fail closed |
| `POL-0616-INCIDENT-01` | proposal, assessment, category, report, and institutional acceptance separated | incident assessment, reporting, and executive direction | unbound; fail closed |
| `POL-0616-LIFECYCLE-01` | typed lifecycle, idempotency, adjudication, result, delta, and later observation | eleven shared lifecycle families | unbound; fail closed |
| `POL-0616-NOTIFY-01` | preparation, consultation, authorization, issue, delivery, and correction separated | outreach, notification, and affected cohort | unbound; fail closed |

These selections name semantic alternatives only. They contain no policy
algorithm, calibrated value, runtime class, or backend default.

## 8. Sensitivity overlays

Each overlay performs two exact replacements: the structural selection and the
profile that materializes it. An applied overlay changes only the named fields;
all other opening records, causal limits, and information boundaries remain
unchanged.

| Overlay ID | Structural replacement | Coupled materialization replacement | Disclosed derived effect |
|---|---|---|---|
| `SENS-0616-ATTACK-DELAY` | `SV-0616-ATTACK-PRESSURE.selection` → `LOWER_OR_DELAYED_BOUNDED_OPPORTUNITY` | `attack_pressure_profile` → lower/delayed admitted opportunities with result still adjudicated | none |
| `SENS-0616-ROUTE-DELAY` | `SV-0616-ROUTE-DELIVERY.selection` → `ROUTE_DELAY_OR_FAILURE` | `route_delivery_profile` → delayed or failed result per explicitly addressed message | none |
| `SENS-0616-NARROWER-UNIT-SET` | `SV-0616-RESPONSIBILITY-UNITS.selection` → `NARROWER_DECLARED_UNIT_SET_WITH_INFORMATION_LOSS` | active population actors → SCM technical unit and application/SCM operational unit | other declared unit assignments and route endpoints become ineligible; their records are not deleted |
| `SENS-0616-OFFICE-COVERAGE-DELAY` | `SV-0616-OFFICE-CAPACITY.selection` → `OFFICE_ABSENT_OR_DELAYED_COVERAGE` | office profile → SIRM unavailable until an admitted capacity change | no covering actor or delegated authority is invented |
| `SENS-0616-TECHNICAL-NO-EFFECT` | `SV-0616-TECHNICAL-RESULT.selection` → `NO_EFFECT_OR_ADVERSE_RESULT` | technical result profile → no-effect/adverse-result sensitivity branch | changes a sensitivity branch, not the baseline or a historical claim |
| `SENS-0616-NOTIFICATION-PARTIAL` | `SV-0616-NOTIFICATION.selection` → `PARTIAL_OR_FAILED_DELIVERY` | notification profile → partial/failed delivery sensitivity branch | recipient histories remain distinct |

The narrower-unit overlay deliberately retains only the two population actors in
the bounded lineage. This gives the information-loss alternative one stable,
reproducible meaning. The office-coverage overlay names the SIRM because the
accepted evidence identifies that office's absence and lack of designated
coverage; it does not generalize the condition to another office.

## 9. Completion and validation expectations

Normal completion occurs at the core horizon, the notification-observation
horizon, or an early process closure. Pending objects produce bounded-incomplete
closure and retain owner, state, version, reason, and next eligible event.
Invariant failure closes fail-safe. Completion does not require the historical
outcome.

| Derived expectation or invariant | Expected value | Derivation authority | Verification method |
|---|---:|---|---|
| semantic products | 9 | Roster release | exact product-set equality |
| decision and population commitments | 29 | consolidated mapping | inventory equality |
| observation placements | 62 | consolidated mapping | inventory equality |
| private-state placements | 44 | consolidated mapping | inventory equality |
| intent placements | 54 | consolidated mapping | inventory equality |
| lifecycle families | 11 | Scenario Definition and mapping | family-set equality |
| named / population actors | 7 / 6 | accepted assembly | unique actor and product references |
| population units / technical assets | 6 / 8 | accepted assembly and opening projection | unique IDs and exact reference closure |
| opening records / routes | 33 / 8 | configuration inventory | unique IDs, non-empty bases, and exact endpoint closure |
| structural selections / exogenous inputs | 6 / 6 | Scenario Definition | family coverage and allowed-domain checks |
| selected policies / sensitivity overlays | 9 / 6 | Scenario Definition | complete policy families and paired exact overlay operations |
| execution eligibility | false | configuration boundary | reject while admission, implementations, projection, binding, and authorization are absent |

These counts are integrity expectations. They do not establish participant
behavior, runtime readiness, historical correspondence, or scientific
validity.

## 10. Definition closure, review, and promotion

### High-information lineage

The illustrative lineage is:

`actor.0616.unit.technical.scm-application-database` →
`actor.0616.unit.operations.application-scm-coordination` →
`actor.0616.office.singhealth-gcio`.

It uses `opening.0616.route.technical-operations` and
`opening.0616.route.operations-gcio`. Its four semantic intents are
`share_technical_finding`, `request_fact_verification`,
`escalate_operational_concern`, and `request_operational_clarification` under
their respective participant capabilities. Intent, message, issue, delivery,
acknowledgement, verification result, interpretation, and later observation
remain separate. The configuration includes no implementation and confers no
execution authority.

### Closure and review

| Definition/configuration family | Configuration carrier | Closure | Retained boundary |
|---|---|---|---|
| purpose, claims, and accepted inputs | top-level identity, flags, and `semantic_inputs` | closed | mechanism coverage is not historical replay or validity |
| time and structural alternatives | `clock`, `structural_variants`, and `variant_materialization` | closed | unsupported precision and realized outcomes remain unset |
| actors, units, capacities, and resources | canonical institutions, actors, units, technical assets, and opening records | closed | one actor per office/unit; concurrent capacities and resource ownership remain scoped |
| information, routes, and exogenous input | eight exact routes and six bounded inputs | closed | issue, delivery, receipt, interpretation, and action remain distinct |
| policies and sensitivities | nine policy meanings and six paired overlays | closed | policy implementations remain unbound; overlays change no undeclared family |
| completion and later lineage | completion policy and bounded lineage | closed | unresolved objects carry forward; no implementation or execution authority supplied |

The substantive review resolved four `MAJOR` and two `MINOR` findings and found
no open semantic defect. The project owner accepted `OD-CFG-05` through
`OD-CFG-08` on 25 August 2026. [ADR-0009](../../../decisions/ADR-0009-singhealth-scenario-configuration-boundary.md)
records the accepted purpose, assembly, structural/input boundary, and
non-executable release boundary.

Atomic promotion adds [README.md](README.md), [manifest.json](manifest.json),
and [SHA256SUMS](SHA256SUMS). The manifest preserves the exact hashes of the
four reviewed candidate files and enumerates the release-only metadata and
template-alignment delta. The machine semantics, opening records, structural
selections, overlays, and execution boundary are unchanged.

### Limitations and next boundary

The configuration is a semantic assembly, not a runtime. Exact asset instances,
technical prestate, event-time office changes, route delivery, institutional
response, and notification results remain unresolved until admitted input or
adjudication supplies them. The exposed historical outcome prevents any
held-out, predictive, or historical-validity claim.

The next legal stage is a separately authorized bounded configuration-admission
preflight. Admission compatibility, exact loading, carrier projection,
participant binding, policy implementation, runtime conformance, simulation,
and evaluation remain separate stages.
