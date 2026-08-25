# H2EPR-0616 research roster

- Version: `0.2`
- Status: accepted research scope
- Event: SingHealth Data Breach
- Definition release: [`v0.1` semantic release](../../releases/singhealth_data_breach/roster-definition-v0.1/)

This roster identifies the participants and processes required by the accepted
event question. It is a research roster rather than an executable actor list:
some rows have Agent Definitions, some have population models, and the
remaining rows belong to the Scenario, an institutional process, initial
context, or excluded aftermath.

## Research boundary

H2EPR-0616 asks:

> Within the accepted event boundary, which interactions across information,
> authority, and response chains turned an initial intrusion into a large-scale
> healthcare data breach, and how did the timing of detection, escalation,
> containment, and notification alter the event's evolution?

The analytic interval begins with the earliest evidenced compromise around
23 August 2017 and ends with the public announcement on 20 July 2018, with
patient-notification delivery observed through 23 July. Event-specific
participant response begins on 18 January 2018; the acute response window
begins on 11 June. Earlier preparedness and vulnerabilities are initial
context. Later investigation, liability, penalties, and reform are
retrospective evidence or excluded aftermath.

The historical outcome was known during construction. The roster is
qualitative, uncalibrated, and not a claim of historical reconstruction,
prediction, policy effectiveness, or scientific validity.

## Roster

| Entity or process | Roster disposition | Causal responsibility | Boundary |
|---|---|---|---|
| External threat actor | Accepted disposition-only bounded adversarial process | Supplies source-bounded attack-attempt pressure across access, persistence, expansion, and data acquisition | Attack attempts may enter as exogenous inputs; Scenario owns access, execution, detection, containment, and data results. Reopen only for a future question about attacker strategy or adaptation. |
| IHiS technical administration and line security staff | Accepted standard role-typed Population Model for R1 | Observe alerts and logs, investigate, communicate, and apply bounded local controls across security, Citrix, application, and database work | Preserves responsibility-unit information and choices without a collective technical-staff Agent. |
| IHiS Security Incident Response Manager | Accepted deep office-level Agent Definition for R1 | Lead and coordinate security incident response; decide whether and how to escalate | Central causal choice retains explicit confirmation, capacity, containment-priority, burden, and false-alarm alternatives. |
| IHiS Cluster Information Security Officer for SingHealth | Accepted standard office-level Agent Definition for R1 | Hold accountability for the response team and exercise independent classification or escalation judgement | Preserves an independent clarification, coordination, and reporting route distinct from the SIRM. |
| IHiS operational and SCM management | Accepted standard role-typed Population Model for R2 | Aggregate role-local information, convene review, request verification, assign follow-up, and escalate a qualified account | Preserves functional heterogeneity without constructing a collective IHiS management Agent. |
| SingHealth GCIO | Accepted standard office-level Agent Definition for R2 | Bridge operational accounts to distinct IHiS and SingHealth routes and maintain patient-impact updates | Preserves dual accountability without merging recipient knowledge or authority. |
| IHiS CSG Director and healthcare Sector Lead | Accepted deep office-level Agent Definition for R2 | Assess category, seek verification, and use the CSA-reporting route | Preserves classification and reporting discretion, report lifecycle, and the concurrent-office boundary. |
| IHiS CEO | Accepted standard office-level Agent Definition for R2 | Review the executive account, request evidence, direct Sector Lead reporting, and assign investigation leadership | Keeps executive direction separate from Sector Lead classification and recipient execution. |
| SingHealth Deputy GCEO | Accepted standard office-level Agent Definition for R2 | Route the incident and lead reversible patient-outreach preparation and plan revision | Preserves its distinct receipt history and proposal role. |
| SingHealth GCEO | Accepted standard office-level Agent Definition for R2 | Direct the SingHealth reporting route and advise on audience and communication channel through consultation | Keeps senior direction and recommendation separate from collective adoption and delivery. |
| End users and endpoint operators | Accepted initial or exogenous context | Supply endpoint and account context; no causally necessary autonomous choice is established for the accepted question | Reopen only if later authorized evidence makes user choice material to the causal model. |
| Access control, network, database, monitoring, and incident lifecycle | Accepted Scenario or institutional process | Enforce requests, routes, permissions, signals, results, and timing | Must not be given participant policy or hidden discretion. |
| Affected patients | Accepted affected cohort; no participant product | Receive the consequences and notifications of the breach | Exposure and delivery remain Scenario-owned. Admit a population only if patient choices enter a later accepted question. |
| MOH, MCI, and CSA response interfaces | Accepted distinct routed institutional processes | Receive Category 1 notification, coordinate containment, support classification, and prepare public communication | Do not create one government Agent or share information automatically across the three institutions. |
| Later investigators, penalties, and reforms | Accepted retrospective evidence or excluded aftermath | Explain later findings and consequences | Not participant-time information within earlier decision situations. |

The roster preserves office and responsibility-unit boundaries inside IHiS and
SingHealth. It does not give either organization one mind, merge recipient
knowledge, or transfer institutional authority and realized results into a
participant model.

## Production record

The release contains seven office-level Agent Definitions and two role-typed
Population Models. The Security Incident Response Manager and Healthcare
Sector Lead received deep treatment because their causally central choices and
outcome exposure created higher semantic risk; the other products use the
standard profile. Two cross-participant interface accounts preserve the
detection-and-escalation and classification-and-institutional-escalation
chains.

The external threat actor, government routes, endpoint context, affected
patients, technical and institutional processes, and later aftermath retain
the non-participant dispositions above. A new participant requires a changed
research question or evidence that an omitted autonomous choice is causally
necessary.

## Definition release gate

Roster Definition release v0.1 is complete because:

- every roster row has one reviewed disposition;
- every admitted Agent and population has an accepted event-bound product;
- the two cross-participant interfaces preserve information, authority,
  intent, and result boundaries;
- the event evidence records make participant-time availability and known
  outcome exposure explicit;
- the event semantic skeleton owns the shared event language without adding
  participant behavior; and
- the release manifest pins the roster, skeleton, evidence authorities,
  products, and interfaces.

The release is the semantic input to Scenario Definition and consolidated
mapping. It is not a configuration, binding, policy implementation, runtime,
simulation, calibration, or evaluation.

## Change policy

Roster v0.2 is frozen for its accepted question. Later phases may map or
instantiate its products, but they may not silently change the event boundary,
participant disposition, information interface, authority, or causal owner.
Such a change requires a reviewed successor. Evidence refinement within the
accepted boundary remains owned by the relevant evidence authority.
