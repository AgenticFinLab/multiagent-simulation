# H2EPR-0616: SingHealth Data Breach

This is the coordination entry and accepted Event Build Brief for the second
H2EPR event. The event frame remains accepted with its bounded temporal and
representation decisions. Two participant batches now cover the technical
detection-and-escalation chain and the classification-and-institutional-
escalation chain through SingHealth patient-communication planning.

The event follows a **same-stage quality, proportionate-work** rule: it may use
fewer files and less engineering than the Panic of 1907 baseline, but an
equivalent phase may not have weaker semantics, evidence responsibility, or
ownership boundaries.

## Event profile

| Field | Event record |
|---|---|
| Event | `H2EPR-0616`, SingHealth Data Breach; slug `singhealth_data_breach` |
| Coordination entry | `projects/h2epr/events/singhealth_data_breach/README.md` |
| Brief identity and status | Event Build Brief v0.1, accepted event frame |
| Method baseline | Repository commit `bea83b1a51256198d264760a88268e041d990700`; [event workflow](../../WORKFLOW.md), [Event Build Brief template](../../event-build-brief-template.md), [participant workflow](../../agents/WORKFLOW.md), and [historical evidence research](../../skills/historical-evidence-research/SKILL.md) |
| Primary question | Within the accepted event boundary, which interactions across information, authority, and response chains turned an initial intrusion into a large-scale healthcare data breach, and how did the timing of detection, escalation, containment, and notification alter the event's evolution? |
| Purpose and claim boundary | Forward-test whether the H2EPR event method transfers from a financial crisis to a healthcare cybersecurity event without treating financial state as universal. The intended depth is semantically complete and engineering-minimal. This work makes no clean-builder, held-out, historical-validity, scientific-validity, calibration, predictive, or policy-effectiveness claim. |
| Temporal boundary | Accepted analytic interval: about 23 August 2017, the earliest evidenced compromise, through the public announcement on 20 July 2018; observe patient-notification delivery through 23 July. The participant response window begins on 18 January 2018, when event-specific malware and callback signals entered IHiS Security Management. An acute information-and-response window begins on 11 June, when unauthorized credential use was specifically recognized, and includes exfiltration from 27 June through 4 July, cross-institution escalation on 10 July, later containment, and notification. Earlier general preparedness and vulnerabilities remain initial context. Post-23 July investigation, liability, penalties, and reform are retrospective evidence or excluded aftermath. |
| Evidence and exposure | The [event-frame evidence](frame-evidence-v0.1.md) adopts four official sources for framing. The complete historical outcome and target Reference material had already been seen during discovery, so this is not clean or held-out construction. `draft_epg.json` was not read in this framing cycle, and evaluation-only material remains outside the evidence set. |
| Current authorized phase and endpoint | **Define participants**, R1 detection-and-escalation and R2 classification-and-institutional-escalation batches complete: two Population Models and seven office-level Agent Definitions reviewed with one interface account per batch. |
| Excluded work | Reference, draft EPG, held-out, or evaluation access; new external research without a bounded permission; roles outside the two accepted batches; complete Roster release; scenario or mapping closure; configuration; binding; policy or runtime work; simulation; calibration; post-seal evaluation; external repository actions; and validity claims. |
| Decision owner and review | The project owner accepted `OD-EV-01`, `OD-RP-02`, `OD-R1-01` through `OD-R1-03`, and `OD-R2-01` through `OD-R2-06`. The SIRM and Sector Lead received deep review; the other products received standard review; both shared interfaces passed cross-role review. |
| Exact upstream inputs | Method baseline `bea83b1a51256198d264760a88268e041d990700`; event specification SHA-256 `5a69486c0c3cff4dab019e43a75b9f959ebb47e3b52b17241bb637dd0cdfbbfb`; frozen evidence SHA-256 `ea356fc9f0f7dfede9e7415f61d144e8ba13e61c3ad5647318abe7b5449f5e7c`; accepted event-frame evidence v0.1 |

> The accepted participant scope contains nine event-bound qualitative models
> and two shared interfaces. It stops before another participant batch,
> complete Roster release, or any later event phase.

## Evidence readiness

The event specification establishes identity and domain but supplies no usable
time hint. The frozen bundle's 12 scraped records remain discovery-only because
they contain duplicated, irrelevant, and predominantly secondary material.

The bounded external research adopted four official sources: the Committee of
Inquiry public report, the PDPC decision, the 20 July joint announcement, and
the 6 August ministerial statement. The adjacent evidence record identifies
their locators, limitations, atomic claims, participant-time boundaries, and
model uses. No source is treated as held out or as proof of behavior merely
because it is official.

| Evidence question | Current verdict | Consequence |
|---|---|---|
| Event identity and broad incident class | `RESOLVED_FOR_STATED_USE` from the event specification | The event and research question may be framed. |
| Authoritative chronology from initial compromise through notification | `RESOLVED_FOR_EVENT_FRAMING` | Supports the accepted outer interval, participant response window, acute response window, exfiltration period, and notification horizon; it does not supply a runtime schedule. |
| Organizational authority and responsibility across SingHealth, IHiS, technical units, and government response bodies | `RESOLVED_FOR_EVENT_FRAMING_WITH_ACCEPTED_REPRESENTATION_GATES` | Supports the accepted separate responsibility interfaces; it does not decide which gates become Agents. |
| Participant-time information and escalation channels | Resolved for event framing and for the accepted R1 and R2 products, with explicit alternatives in the participant-evidence record | Supports nine participant models and their two bounded interfaces; no other role or runtime schedule is inferred. |
| Later investigation, attribution, penalties, and recommendations | Retrospective and outcome-exposed | May guide source discovery and later interpretation; not participant-time input. |

The official-source search is closed for its stated uses. R1 and R2 behavior
research reused the archived inquiry report without new retrieval; another
role or claim requires its own bounded evidence question.

## Causal scope

These rows are evidence-supported event-frame propositions. They remain
semantic transitions rather than a runtime script.

| ID | Pre-state or opportunity | Transition to explain | Candidate decision or process owner | Authoritative result owner | Current status |
|---|---|---|---|---|---|
| `CT-1` | Exposed organizational or technical opportunity | Initial access becomes a persistent foothold | Threat actor; pre-existing security responsibilities remain institutional context | Scenario-owned access and system state | Supported outer boundary; exact initial action unresolved |
| `CT-2` | Foothold with bounded access | Access expands across credentials, hosts, and privileges toward SCM | Threat actor and IHiS operational interfaces | Scenario-owned authorization and network state | Supported for framing |
| `CT-3` | Access to SCM through compromised infrastructure | Queries, returned records, copying, and transfer produce material data exposure | Threat actor; IHiS access, database, and monitoring interfaces | Scenario-owned request, access, and disclosure results | Supported for framing |
| `CT-4` | Role-local alerts, unauthorized access findings, or anomalous activity | Signals are interpreted, communicated, classified, deferred, or escalated | Accepted R1 technical role set, SIRM, and Cluster ISO; accepted R2 operational role set, GCIO, Sector Lead, and IHiS CEO | Institutional communication, category, reporting, investigation, and incident-lifecycle processes | Supported from 18 January through the 10 July classification and reporting transition |
| `CT-5` | Suspected or confirmed incident | Local and inter-agency containment changes continued access and observed malicious activity | IHiS operational and management roles with SingHealth, MOH, and CSA response interfaces | Scenario-owned containment result and system state | Supported for framing |
| `CT-6` | Material breach and bounded organizational knowledge | Public announcement and patient notification are authorized and delivered | Accepted SingHealth Deputy GCEO and GCEO interfaces in routed coordination with IHiS, MOH, MCI, and CSA | Institutional notification approval, execution, and delivery process | Supported for planning choices through 20 July; external authorization and delivery remain outside the participant models |

## Causal role map and roster dispositions

The evidence resolves broad responsibility but not every participant form.
Representation gates preserve decisions that must precede Agent admission.

| Entity or process | Candidate disposition | Causal responsibility | Representation question |
|---|---|---|---|
| External threat actor | Representation gate | Access, persistence, expansion, and data-acquisition choices | Agent, bounded adversarial process, or exogenous attack sequence? |
| IHiS technical administration and line security staff | Accepted standard role-typed Population Model for R1 | Observe alerts and logs, investigate, communicate, and apply bounded local controls across security, Citrix, application, and database work | Preserves responsibility-unit information and choices without a collective technical-staff Agent. |
| IHiS Security Incident Response Manager | Accepted deep office-level Agent Definition for R1 | Lead and coordinate security incident response; decide whether and how to escalate | Central causal choice retains explicit confirmation, capacity, containment-priority, burden, and false-alarm alternatives. |
| IHiS Cluster Information Security Officer for SingHealth | Accepted standard office-level Agent Definition for R1 | Hold accountability for the response team and exercise independent classification or escalation judgement | Preserves an independent clarification, coordination, and reporting route distinct from the SIRM. |
| IHiS operational and SCM management | Accepted standard role-typed Population Model for R2 | Aggregate role-local information, convene review, request verification, assign follow-up, and escalate a qualified account | Preserves functional heterogeneity without constructing a collective IHiS management Agent. |
| SingHealth GCIO | Accepted standard office-level Agent Definition for R2 | Bridge operational accounts to distinct IHiS and SingHealth routes and maintain patient-impact updates | Preserves dual accountability without merging recipient knowledge or authority. |
| IHiS CSG Director and healthcare Sector Lead | Accepted deep office-level Agent Definition for R2 | Assess category, seek verification, and use the CSA-reporting route | Preserves classification and reporting discretion, report lifecycle, and the concurrent-office boundary. |
| IHiS CEO | Accepted standard office-level Agent Definition for R2 | Review the executive account, request evidence, direct Sector Lead reporting, and assign investigation leadership | Keeps executive direction separate from Sector Lead classification and recipient execution. |
| SingHealth Deputy GCEO | Accepted standard office-level Agent Definition for R2 | Route the incident and lead reversible patient-outreach preparation and plan revision | Preserves its distinct receipt history and proposal role. |
| SingHealth GCEO | Accepted standard office-level Agent Definition for R2 | Direct the SingHealth reporting route and advise on audience and communication channel through consultation | Keeps senior direction and recommendation separate from collective adoption and delivery. |
| End users and endpoint operators | Initial or exogenous context | Supply endpoint and account context; no causally necessary autonomous choice is established for the accepted question | Reopen only if later authorized evidence makes user choice material to the causal model. |
| Access control, network, database, monitoring, and incident lifecycle | Scenario or institutional process | Enforce requests, routes, permissions, signals, results, and timing | Must not be given participant policy or hidden discretion. |
| Affected patients | Affected cohort; no participant product currently proposed | Receive the consequences and notifications of the breach | Admit a population only if patient choices enter the accepted question. |
| MOH, MCI, and CSA response interfaces | Routed institutional process with representation gates | Receive Category 1 notification, coordinate containment, support classification, and prepare public communication | Do not create one government Agent or share all inter-agency information automatically. |
| Later investigators, penalties, and reforms | Retrospective evidence or excluded aftermath | Explain later findings and consequences | Not runtime-visible within earlier decision situations. |

## Shared semantics and ownership

| Concept | Event-bound meaning | Owner | Required boundary |
|---|---|---|---|
| Event time | Ordered incident, detection, response, and notification intervals with uncertainty preserved | Evidence and scenario | Do not substitute publication or investigation dates for event time. |
| Information signal | A bounded observation available through a named technical or organizational channel | Participant Definition or population model; delivery by scenario | Researcher knowledge and full system state are not participant knowledge. |
| Authority | Permission to access a system, interpret or escalate an incident, order containment, or authorize notification | Institution and participant product | Technical capability, formal authority, and realized result remain distinct. |
| Access request and result | An attempted operation and its separately adjudicated authorization and system effect | Intent by participant; result by scenario | Requested, allowed, executed, observed, and copied are not synonyms. |
| Incident escalation | Communication that changes who can know, classify, or act on a suspected incident | Participant intent and institutional routing | Preserve sender, recipient, timing, content, and acknowledgement. |
| Containment | An authorized intervention intended to limit continued compromise or exposure | Participant intent; scenario result | Intention does not script success or immediate effect. |
| Notification | An authorized disclosure to an internal, governmental, affected, or public audience | Participant intent and institutional delivery | Separate decision, delivery time, audience, and information content. |
| Organization and unit | A real institutional boundary with defined information, authority, and accountability | Evidence and roster | Do not give a whole organization one mind when units differ materially. |

No machine fields, schedules, policies, parameters, or numerical defaults are
defined at this phase.

## Responsibility-owned assets

| Responsibility | Current asset | Status |
|---|---|---|
| Event question, boundary, and authorization | This coordination entry | Accepted event frame |
| Source register, claim ledger, and evidence-use review | [Event-frame evidence v0.1](frame-evidence-v0.1.md) | Accepted for framing with bounded representation gates |
| Participant evidence | [Participant evidence](participant-evidence-v0.1.md) | Accepted for the R1 and R2 participant products with explicit mechanism alternatives |
| Technical administration and line security staff | [Technical response role-set Population Model](../../populations/defines/singhealth_data_breach/technical-administration-and-line-security-staff.md) | Accepted `0.1.0`, standard profile |
| Security Incident Response Manager | [SIRM Agent Definition](../../agents/defines/singhealth_data_breach/security-incident-response-manager.md) | Accepted `0.1.0`, deep profile |
| Cluster Information Security Officer | [Cluster ISO Agent Definition](../../agents/defines/singhealth_data_breach/cluster-information-security-officer.md) | Accepted `0.1.0`, standard profile |
| First-batch participant interface | [R1 detection-and-escalation preflight](../../agents/interfaces/singhealth_data_breach/r1-detection-and-escalation.md) | Accepted semantic interface; mapping extension expected but not opened |
| IHiS operational and SCM management | [Operational-management role-set Population Model](../../populations/defines/singhealth_data_breach/ihis-operational-and-scm-management.md) | Accepted standard profile |
| R2 office-level participants | [SingHealth Agent Definition index](../../agents/defines/singhealth_data_breach/README.md) | Five reviewed R2 Agent Definitions, including the deep Sector Lead profile |
| Second-batch participant interface | [R2 classification-and-institutional-escalation account](../../agents/interfaces/singhealth_data_breach/r2-classification-and-institutional-escalation.md) | Accepted semantic interface; mapping remains unopened |
| Scenario, mapping, configuration, implementation, and release authorities | None | Not authorized or opened for this event |

## Current work package

| Field | Current decision |
|---|---|
| Work mode | Roster production, R1 and R2 participant batches closed |
| Roles or processes in this package | R1 technical role set, SIRM, and Cluster ISO; R2 operational-management role set, GCIO, Sector Lead, IHiS CEO, Deputy GCEO, and GCEO |
| Participant production profiles | Two standard Population Models; five standard Agent Definitions; deep SIRM and Sector Lead Agent Definitions |
| Required project Skills and templates | Event participant batch, historical evidence research, participant behavior research, Agent Definition or Population model only after disposition, profile-proportionate review, and phase closeout |
| Accepted outputs | Thirty-two R2 claims appended to the shared ledger; two Population Models, seven Agent Definitions, and two semantic interface accounts across both batches |
| Review and verification | Deep SIRM and Sector Lead reviews; concise standard reviews; participant-time, intent/result, cross-role, public-profile, link, identity, repository-boundary, and final-diff checks |
| Stop conditions | Closed at the accepted R2 participant boundary; another role batch, source boundary, or later phase needs separate authorization |
| Next legal action | Explicit stop. A later action must name another bounded participant batch or separately authorize semantic Roster release; neither follows automatically from R2 completion. |

The non-authorizing target for later phases is **semantically complete,
engineering-minimal**: complete dispositions and accepted products for the
causally necessary roster, accepted scenario and mapping semantics, and one
high-information non-financial lineage through bounded conformance. It does
not imply a full-roster runtime or broad simulation.

## Owner decisions

| ID | Decision or risk | Owner | Minimum input needed | Dependent work | Disposition |
|---|---|---|---|---|---|
| `OD-EV-01` | Accept the about 23 August 2017–20 July 2018 core interval, 18 January–20 July participant response window, 11 June–20 July acute response window, and patient-notification observation through 23 July | Project owner | `0616-FR-C01`–`0616-FR-C04`, `0616-FR-C17`–`0616-FR-C18`, and the primary-question consequence | Frame acceptance | `ACCEPTED_WITH_BOUNDED_MODIFICATION_2026-08-24` |
| `OD-RP-01` | Threat actor representation | Project owner after evidence and behavior research | Choice granularity, observability, and scenario-externalization cost | Roster acceptance | `DEFERRED_TO_ROSTER_PHASE` |
| `OD-RP-02` | Preserve separate gates for technical administration and line security staff, SIRM, Cluster ISO, IHiS operational/SCM and senior management interfaces, SingHealth management, and routed government response; return endpoint users to initial or exogenous context | Project owner | `0616-FR-C05`–`0616-FR-C18` and the causal role map | Frame acceptance and later Roster research | `ACCEPTED_WITH_BOUNDED_ROLE_LABEL_CLARIFICATION_2026-08-24` |
| `OD-R1-01` | Admit technical administration and line security staff as a role-typed Population Model at `standard` depth | Project owner | Participant claims `0616-R1-C02`–`0616-R1-C06`, `0616-R1-C14`, and `0616-R1-C16`–`0616-R1-C17`; representation alternatives; shared information boundary | R1 participant production | `ACCEPTED_2026-08-24` |
| `OD-R1-02` | Admit the SIRM office as an Agent Definition at `deep` depth | Project owner | Participant claims `0616-R1-C01`, `0616-R1-C07`–`0616-R1-C08`, `0616-R1-C11`–`0616-R1-C12`, `0616-R1-C15`, and `0616-R1-C18`–`0616-R1-C19`; outcome-exposure risk; explicit competing mechanisms | R1 participant production | `ACCEPTED_2026-08-24` |
| `OD-R1-03` | Admit the Cluster ISO office as an Agent Definition at `standard` depth | Project owner | Participant claims `0616-R1-C09`–`0616-R1-C13` and `0616-R1-C19`; independent-authority counterfactual; explicit alternatives | R1 participant production | `ACCEPTED_2026-08-24` |
| `OD-R2-01` | Admit IHiS operational and SCM management as a role-typed Population Model at standard depth | Project owner | `0616-R2-C01`–`C07` and `C25`; aggregation alternatives and responsibility-unit boundary | R2 participant production | `ACCEPTED_2026-08-25` |
| `OD-R2-02` | Admit the SingHealth GCIO as a standard office-level Agent Definition | Project owner | `0616-R2-C08`, `C09`, `C17`, and `C29`; dual-accountability boundary | R2 participant production | `ACCEPTED_2026-08-25` |
| `OD-R2-03` | Admit the IHiS CSG Director and healthcare Sector Lead as a deep office-level Agent Definition | Project owner | `0616-R2-C10`, `C12`, `C14`, `C16`, `C28`, and `C32`; classification alternatives and concurrent-office boundary | R2 participant production | `ACCEPTED_2026-08-25` |
| `OD-R2-04` | Admit the IHiS CEO as a standard office-level Agent Definition | Project owner | `0616-R2-C11`, `C13`, `C15`, `C26`, `C27`, and `C31`; executive direction and assignment boundary | R2 participant production | `ACCEPTED_2026-08-25` |
| `OD-R2-05` | Admit the SingHealth Deputy GCEO as a standard office-level Agent Definition | Project owner | `0616-R2-C18`, `C20`–`C23`, and `C30`; distinct receipt and outreach-preparation role | R2 participant production | `ACCEPTED_2026-08-25` |
| `OD-R2-06` | Admit the SingHealth GCEO as a standard office-level Agent Definition | Project owner | `0616-R2-C19`, `C20`, and `C22`–`C24`; senior reporting and consultation role | R2 participant production | `ACCEPTED_2026-08-25` |

## Event-frame review and closeout

| Field | Closeout record |
|---|---|
| Event, phase, object, and inputs | `H2EPR-0616`; **Frame the event**; Event Build Brief v0.1 and event-frame evidence v0.1; method baseline, event specification, frozen discovery bundle, and four adopted official sources identified above |
| Authorized purpose and endpoint | Frame the accepted information-, authority-, and response-chain question; stop before participant behavior research or production |
| Outputs and status | Accepted question, temporal boundary, evidence permission, causal transitions, roster dispositions, shared semantics, and owner decisions; **Complete with recorded limitations** |
| Verification and limitations | The eight core closeout checks and the changed-evidence check pass. The exact initial-compromise moment, threat-actor form, and participant granularity remain bounded; the historical outcome was known during construction, and no validity claim is made. |
| Mainline and depth judgment | The result answers the accepted framing question with the smallest responsibility map that preserves material information and authority differences; no participant, mapping, configuration, or runtime asset was opened. |
| Next legal action | Explicit stop. A separately authorized participant phase must name its bounded batch, evidence question, and production profile. |

The phase stops at the **accepted event frame** because additional participant
behavior research, Agent or Population production, scenario closure, mapping,
configuration, or runtime work would test a different or later question.

## Phase status

Frame the event readiness:

- [x] Event identity, accepted primary question, method baseline, purpose, claim
  exclusions, construction exposure, and current stopping boundary are explicit.
- [x] Protected inputs and the current local source boundary are explicit.
- [x] Candidate causal transitions, dispositions, and shared concepts identify
  the questions that evidence must resolve.
- [x] The evidence-supported temporal boundary is accepted by the owner with a
  bounded response-window modification.
- [x] External source permission and the adopted event-frame evidence set are
  closed for their stated use.
- [x] Material causal transitions have supported owners or bounded
  representation gates.
- [x] The project owner accepted the bounded representation gates without
  admitting any Agent or authorizing participant production.
- [x] Shared information and authority boundaries have received event-framing
  review.

**Frame disposition: Complete with recorded limitations.** Event Build Brief
v0.1 remains accepted. Frame acceptance itself did not authorize participant
production; the R1 authorization below is a separate owner decision and does
not open any other participant batch or later phase.

## First participant batch

`R1-DETECTION-AND-ESCALATION` is a Roster-production batch, not a reference
pilot. It uses the causal role map and shared semantics embedded in this Brief
as roster and skeleton v0.1. Promotion is decided per representation gate;
interface review and closeout are shared across the batch.

The research questions are deliberately representation-changing:

- whether the technical administration and line security work is best retained
  as a heterogeneous population or small role set, or externalized as
  scenario context without losing material local choices;
- whether the SIRM has a defensible office-level decision interface for
  investigation coordination, incident classification, and escalation; and
- whether the Cluster ISO has a distinct information and authority interface
  whose independent judgement changes the accepted causal chain.

The existing 0616 official-source archive and accepted frame claims may be
re-read for these questions with the historical outcome already known. No new network source,
Reference content, draft EPG, held-out material, or evaluation evidence is
authorized by this batch. Historical actions and later inquiry findings may
constrain mechanisms and falsifiers, but cannot become participant-time facts
or fixed policies.

**Batch status: Complete with recorded limitations.** On 24 August 2026, the
project owner accepted `OD-R1-01` through `OD-R1-03`. The resulting standard
technical role-set Population Model, deep SIRM Agent Definition, and standard
Cluster ISO Agent Definition passed profile-proportionate review and the shared
semantic interface preflight. No other Roster row or later phase is implied.

## First-batch closeout

| Field | Closeout record |
|---|---|
| Event, phase, object, and inputs | `H2EPR-0616`; **Define participants**, R1 detection-and-escalation batch; accepted Event Build Brief v0.1, frame evidence v0.1, local official archive, and owner dispositions `OD-R1-01`--`OD-R1-03` |
| Authorized purpose and endpoint | Resolve and produce only the technical role set, SIRM, and Cluster ISO representation gates; stop after participant review and shared interface preflight |
| Outputs and status | Participant evidence v0.1, one Population Model `0.1.0`, two Agent Definitions `0.1.0`, and one interface preflight; **Complete with recorded limitations** |
| Verification and limitations | Nineteen participant claims support the three products; both Agent Definitions pass the public profile; substantive reviews have no open blocking or major finding; one retrospective official inquiry remains the behavior source, the mechanisms remain set-valued and uncalibrated, and the historical outcome was known during construction |
| Mainline and depth judgment | The batch preserves the smallest three decision interfaces needed for CT-4; deep treatment is limited to the causally central, outcome-exposed SIRM, and no unrelated role, source breadth, parameter, or engineering asset was added |
| Next legal action | Explicit stop before another participant batch, complete Roster release, scenario closure, mapping, configuration, binding, policy, runtime, simulation, calibration, held-out construction, or evaluation |

The eight core closeout checks pass: the products remain on the accepted
question; every addition has a current evidence, behavior, review, or interface
consumer; accepted upstream authorities were not changed; evidence,
participant, scenario, and result ownership remain separate; source permission
and participant-time limits are explicit; review depth follows the accepted
profiles; accepted assets are discoverable without promoting working notes;
and the handoff names limitations without opening the next phase.

The batch stops at the **reviewed R1 participant boundary** because additional
roles, semantic release, scenario, mapping, or implementation would answer a
different or later question.

## Second participant batch

The classification-and-institutional-escalation batch follows the bounded R1
handoff from operational correlation through IHiS classification and reporting
and into SingHealth governance and patient-communication planning. It resolves
three representation questions:

- whether operational and SCM management requires named individuals, a role-
  typed population, or scenario-owned routing;
- whether the GCIO bridge, Sector Lead classification, and IHiS CEO direction
  remain causally distinct; and
- whether the Deputy GCEO and GCEO require separate information and authority
  interfaces for reporting and patient communication.

The adopted evidence supports one operational-management Population Model,
separate GCIO, Sector Lead, and IHiS CEO Agent Definitions, and separate Deputy
GCEO and GCEO Agent Definitions. Government recipients remain institutional
routes, not additional Agents. The same archived official inquiry supplies the
event-bound behavior evidence; no new source or later engineering layer was
opened.

**Batch disposition: Complete with recorded limitations.** The six products
passed their profile-proportionate reviews and the shared R2 interface review.
The products retain qualitative alternatives because the evidence does not
identify population weights, numerical classification or notification
thresholds, or transferable mechanism weights.

## Second-batch closeout

| Field | Closeout record |
|---|---|
| Event, phase, object, and inputs | `H2EPR-0616`; **Define participants**, classification-and-institutional-escalation batch; accepted event frame, shared participant evidence, accepted R1 products and interface, and owner dispositions `OD-R2-01` through `OD-R2-06` |
| Authorized purpose and endpoint | Resolve and produce only the operational-management, IHiS senior-office, and SingHealth governance interfaces needed to connect R1 escalation with classification, reporting, and bounded patient-communication planning |
| Outputs and status | Thirty-two R2 claims, one Population Model, five Agent Definitions, and one cross-role interface; **Complete with recorded limitations** |
| Verification and limitations | All Agent Definitions pass the public profile; standard and deep substantive reviews have no open blocking, major, or minor finding; the interface closes represented routes. One retrospective official inquiry remains the role-specific behavior source, the model is qualitative, and the completed outcome was known during construction. |
| Mainline and depth judgment | The batch adds the smallest six decision interfaces needed for the accepted 9–20 July transition; deep treatment is limited to the outcome-exposed Sector Lead classification and concurrent-office boundary. |
| Next legal action | Explicit stop before another participant batch, complete semantic Roster release, Scenario, Mapping, configuration, binding, policy, runtime, simulation, calibration, held-out construction, or evaluation. |

The closeout checks pass: the products remain on the accepted primary question;
every participant and intent has an evidence, behavior, or interface consumer;
upstream frame and R1 authorities remain unchanged; evidence, participant,
scenario, and result ownership stay separate; participant-time and source
limits are explicit; review depth follows the accepted profiles; and the
public products are linked from their responsibility-owned directories.

The batch stops at the **reviewed R2 participant boundary** because a wider
roster, semantic release, scenario, mapping, or implementation would answer a
different or later question.
