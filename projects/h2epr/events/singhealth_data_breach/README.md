# H2EPR-0616: SingHealth Data Breach

This is the coordination entry and accepted Event Build Brief for the second
H2EPR event. The project owner accepted the evidence-supported temporal
boundary with a bounded response-window correction and accepted bounded
representation gates with clarified role labels. The event-frame semantic
review and closeout are complete; work stops before participant production.

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
| Evidence and exposure | The [event-frame evidence](frame-evidence-v0.1.md) adopts four official sources for framing and retains the frozen bundle as discovery-only material. This context is `FULL_DRAFT_EXPOSED` because it previously saw target Reference content; it cannot support a clean-builder claim. `draft_epg.json` was not read in this framing cycle. Reference, held-out suffix, and evaluation-only content remain protected. |
| Current authorized phase and endpoint | **Frame the event** is complete at the accepted Event Build Brief v0.1. No participant production, mapping, configuration, implementation, or simulation is authorized. |
| Excluded work | Reference, draft EPG, held-out, or evaluation access; external research beyond the accepted framing questions; final Agent admission or participant authoring; scenario or mapping closure; configuration; policy or runtime work; simulation; calibration; post-seal evaluation; external repository actions; and validity claims. |
| Decision owner and review | The project owner accepted `OD-EV-01` with a bounded response-window modification and `OD-RP-02` with bounded role-label clarification on 24 August 2026. The proportionate evidence and semantic closeout review passed with recorded limitations. |
| Exact upstream inputs | Method baseline `bea83b1a51256198d264760a88268e041d990700`; event specification SHA-256 `5a69486c0c3cff4dab019e43a75b9f959ebb47e3b52b17241bb637dd0cdfbbfb`; frozen evidence SHA-256 `ea356fc9f0f7dfede9e7415f61d144e8ba13e61c3ad5647318abe7b5449f5e7c`; accepted event-frame evidence v0.1 |

> This cycle accepts and closes the event frame and stops before accepting any
> participant-production package.

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
| Participant-time information and escalation channels | `RESOLVED_FOR_EVENT_FRAMING_ONLY` | Supports the causal route and information-boundary questions; role behavior still requires a later authorized study. |
| Later investigation, attribution, penalties, and recommendations | Retrospective and outcome-exposed | May guide source discovery and later interpretation; not participant-time input. |

The official-source search is closed for its stated use. Further evidence work
belongs to a later role-specific behavior question, not to event-frame breadth.

## Causal scope

These rows are evidence-supported event-frame propositions. They remain
semantic transitions rather than a runtime script.

| ID | Pre-state or opportunity | Transition to explain | Candidate decision or process owner | Authoritative result owner | Current status |
|---|---|---|---|---|---|
| `CT-1` | Exposed organizational or technical opportunity | Initial access becomes a persistent foothold | Threat actor; pre-existing security responsibilities remain institutional context | Scenario-owned access and system state | Supported outer boundary; exact initial action unresolved |
| `CT-2` | Foothold with bounded access | Access expands across credentials, hosts, and privileges toward SCM | Threat actor and IHiS operational interfaces | Scenario-owned authorization and network state | Supported for framing |
| `CT-3` | Access to SCM through compromised infrastructure | Queries, returned records, copying, and transfer produce material data exposure | Threat actor; IHiS access, database, and monitoring interfaces | Scenario-owned request, access, and disclosure results | Supported for framing |
| `CT-4` | Role-local alerts, unauthorized access findings, or anomalous activity | Signals are interpreted, communicated, classified, deferred, or escalated | IHiS technical administration and line security staff, SIRM and Cluster ISO roles, and operational or senior management interfaces | Institutional communication and incident-lifecycle process | Supported from 18 January; acute escalation window begins 11 June; separate representation gates accepted |
| `CT-5` | Suspected or confirmed incident | Local and inter-agency containment changes continued access and observed malicious activity | IHiS operational and management roles with SingHealth, MOH, and CSA response interfaces | Scenario-owned containment result and system state | Supported for framing |
| `CT-6` | Material breach and bounded organizational knowledge | Public announcement and patient notification are authorized and delivered | SingHealth management in routed coordination with IHiS, MOH, MCI, and CSA | Institutional notification and delivery process | Supported for framing; internal authority granularity gated |

## Causal role map and roster dispositions

The evidence resolves broad responsibility but not every participant form.
Representation gates preserve decisions that must precede Agent admission.

| Entity or process | Candidate disposition | Causal responsibility | Representation question |
|---|---|---|---|
| External threat actor | Representation gate | Access, persistence, expansion, and data-acquisition choices | Agent, bounded adversarial process, or exogenous attack sequence? |
| IHiS technical administration and line security staff | Representation gate: population, small role set, or scenario context | Observe alerts and logs, investigate, communicate, and apply bounded local controls across security, Citrix, application, and database work | Preserve heterogeneous local information and actions; do not create a collective technical-staff Agent. |
| IHiS Security Incident Response Manager | Separate representation gate | Lead and coordinate security incident response; decide whether and how to escalate | Central causal choice with later-outcome exposure; requires role-specific behavior research before Agent admission. |
| IHiS Cluster Information Security Officer for SingHealth | Separate representation gate | Hold accountability for the response team and exercise independent classification or escalation judgement | Distinct authority from the SIRM; cannot be merged merely to reduce roster size. |
| IHiS operational/SCM and senior management interfaces | Representation gate | Aggregate role-local information, receive compressed reports, classify severity, mobilize resources, and notify higher or external authorities | Preserve operational aggregation separately from senior classification and reporting; later research determines whether one or several participant products are needed. |
| SingHealth governance and data-owner management | Representation gate | Retain ownership and supervisory responsibility; authorize or coordinate incident reporting and patient communication | Keep responsibility distinct from IHiS operation; admit only choices required by the primary question. |
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
| Participant, scenario, configuration, and release authorities | None | Not yet authorized or opened for this event |

## Current work package

| Field | Current decision |
|---|---|
| Work mode | Accepted event frame; participant production not opened |
| Roles or processes in this package | Incident progression from initial access opportunity through detection, containment, and notification |
| Participant production profiles | Not assigned; participant production is not authorized |
| Required project Skills and templates | Event Build Brief, historical evidence research, participant disposition rules, and phase closeout |
| Expected outputs | Accepted Event Build Brief v0.1, accepted event-frame evidence v0.1, owner decisions, and compact phase closeout |
| Review and verification | Claim-appropriate source review, temporal and participant-availability review, causal ownership review, representation-boundary review, link and repository checks; complete with recorded limitations |
| Stop conditions | The owner rejects or changes the temporal boundary, primary question, claim boundary, or role split; semantic review finds an ownership defect; protected content would be required; or the work would enter participant production |
| Next legal action | Stop. A later participant phase may open only through separate owner authorization that names a bounded role batch and its behavior-research question. |

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

## Event-frame review and closeout

| Field | Closeout record |
|---|---|
| Event, phase, object, and inputs | `H2EPR-0616`; **Frame the event**; Event Build Brief v0.1 and event-frame evidence v0.1; method baseline, event specification, frozen discovery bundle, and four adopted official sources identified above |
| Authorized purpose and endpoint | Frame the accepted information-, authority-, and response-chain question; stop before participant behavior research or production |
| Outputs and status | Accepted question, temporal boundary, evidence permission, causal transitions, roster dispositions, shared semantics, and owner decisions; **Complete with recorded limitations** |
| Verification and limitations | The eight core closeout checks and the changed-evidence check pass. The exact initial-compromise moment, threat-actor form, and participant granularity remain bounded; construction remains `FULL_DRAFT_EXPOSED`, and no validity claim is made. |
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

**Current disposition: Complete with recorded limitations.** Event Build Brief
v0.1 is accepted. This acceptance closes only **Frame the event** and does not
authorize participant production or any later phase.
