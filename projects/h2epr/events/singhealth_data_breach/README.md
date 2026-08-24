# H2EPR-0616: SingHealth Data Breach

This is the coordination entry and Event Build Brief for the second H2EPR
event. The event and primary question are accepted. Official-source research
now supports a review candidate for the temporal boundary, causal ownership,
and roster dispositions; event framing remains open until owner and semantic
review.

The event follows a **same-stage quality, proportionate-work** rule: it may use
fewer files and less engineering than the Panic of 1907 baseline, but an
equivalent phase may not have weaker semantics, evidence responsibility, or
ownership boundaries.

## Event profile

| Field | Event record |
|---|---|
| Event | `H2EPR-0616`, SingHealth Data Breach; slug `singhealth_data_breach` |
| Coordination entry | `projects/h2epr/events/singhealth_data_breach/README.md` |
| Brief identity and status | Event Build Brief v0.1, event-frame review candidate |
| Method baseline | Repository commit `bea83b1a51256198d264760a88268e041d990700`; [event workflow](../../WORKFLOW.md), [Event Build Brief template](../../event-build-brief-template.md), [participant workflow](../../agents/WORKFLOW.md), and [historical evidence research](../../skills/historical-evidence-research/SKILL.md) |
| Primary question | Within the accepted event boundary, which interactions across information, authority, and response chains turned an initial intrusion into a large-scale healthcare data breach, and how did the timing of detection, escalation, containment, and notification alter the event's evolution? |
| Purpose and claim boundary | Forward-test whether the H2EPR event method transfers from a financial crisis to a healthcare cybersecurity event without treating financial state as universal. The intended depth is semantically complete and engineering-minimal. This work makes no clean-builder, held-out, historical-validity, scientific-validity, calibration, predictive, or policy-effectiveness claim. |
| Temporal boundary | Proposed analytic interval: about 23 August 2017, the earliest evidenced compromise, through the public announcement on 20 July 2018; observe patient-notification delivery through 23 July. The primary information-and-response window begins on 11 June 2018, when unauthorized credential use was specifically recognized, and includes exfiltration from 27 June through 4 July, cross-institution escalation on 10 July, later containment, and notification. Earlier vulnerabilities and decisions are initial context unless a later causal gate admits them. Post-23 July investigation, liability, penalties, and reform are retrospective evidence or excluded aftermath. |
| Evidence and exposure | The [event-frame evidence](frame-evidence-v0.1.md) adopts four official sources for framing and retains the frozen bundle as discovery-only material. This context is `FULL_DRAFT_EXPOSED` because it previously saw target Reference content; it cannot support a clean-builder claim. `draft_epg.json` was not read in this framing cycle. Reference, held-out suffix, and evaluation-only content remain protected. |
| Current authorized phase and endpoint | Complete official-source research, produce the event-frame review candidate, and obtain the owner and semantic dispositions needed to close **Frame the event**. Stop before participant production, mapping, configuration, implementation, or simulation. |
| Excluded work | Reference, draft EPG, held-out, or evaluation access; external research beyond the accepted framing questions; final Agent admission or participant authoring; scenario or mapping closure; configuration; policy or runtime work; simulation; calibration; post-seal evaluation; external repository actions; and validity claims. |
| Decision owner and review | The project owner accepts scope and material representation choices. Event framing requires one proportionate evidence and semantic review after its open boundaries close. |
| Exact upstream inputs | Method baseline `bea83b1a51256198d264760a88268e041d990700`; event specification SHA-256 `5a69486c0c3cff4dab019e43a75b9f959ebb47e3b52b17241bb637dd0cdfbbfb`; frozen evidence SHA-256 `ea356fc9f0f7dfede9e7415f61d144e8ba13e61c3ad5647318abe7b5449f5e7c`; event-frame evidence v0.1 review candidate |

> This cycle may produce and review the event frame and stops before accepting
> any participant-production package.

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
| Authoritative chronology from initial compromise through notification | `RESOLVED_FOR_EVENT_FRAMING` | Supports the proposed outer interval, primary response window, exfiltration period, and notification horizon; it does not supply a runtime schedule. |
| Organizational authority and responsibility across SingHealth, IHiS, technical units, and government response bodies | `RESOLVED_FOR_EVENT_FRAMING_WITH_REPRESENTATION_GATES` | Supports separate responsibility interfaces; it does not decide which gates become Agents. |
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
| `CT-4` | Role-local alerts, unauthorized access findings, or anomalous activity | Signals are interpreted, communicated, classified, deferred, or escalated | IHiS technical administrators, security response roles, and management | Institutional communication and incident-lifecycle process | Supported with separate representation gates |
| `CT-5` | Suspected or confirmed incident | Local and inter-agency containment changes continued access and observed malicious activity | IHiS operational and management roles with SingHealth, MOH, and CSA response interfaces | Scenario-owned containment result and system state | Supported for framing |
| `CT-6` | Material breach and bounded organizational knowledge | Public announcement and patient notification are authorized and delivered | SingHealth management in routed coordination with IHiS, MOH, MCI, and CSA | Institutional notification and delivery process | Supported for framing; internal authority granularity gated |

## Causal role map and roster dispositions

The evidence resolves broad responsibility but not every participant form.
Representation gates preserve decisions that must precede Agent admission.

| Entity or process | Candidate disposition | Causal responsibility | Representation question |
|---|---|---|---|
| External threat actor | Representation gate | Access, persistence, expansion, and data-acquisition choices | Agent, bounded adversarial process, or exogenous attack sequence? |
| IHiS technical administrators and application/database teams | Representation gate: population, small role set, or scenario context | Observe alerts and logs, investigate, communicate, and apply bounded local controls | Preserve heterogeneous local information and actions; do not create a collective technical-staff Agent. |
| IHiS Security Incident Response Manager | Separate Agent candidate gate | Lead and coordinate security incident response; decide whether and how to escalate | Central causal choice with later-outcome exposure; requires role-specific behavior research. |
| IHiS Cluster Information Security Officer for SingHealth | Separate Agent candidate gate | Hold accountability for the response team and exercise independent classification/escalation judgement | Distinct authority from the SIRM; cannot be merged merely to reduce roster size. |
| IHiS senior management | Representation gate | Receive compressed reports, classify severity, mobilize resources, and notify higher or external authorities | Determine whether one bounded management interface or several materially distinct choices are needed. |
| SingHealth governance and data-owner management | Representation gate | Retain ownership and supervisory responsibility; authorize or coordinate incident reporting and patient communication | Keep responsibility distinct from IHiS operation; admit only choices required by the primary question. |
| End users and endpoint operators | Representation gate | Security-relevant local actions or signals, if causally material | Heterogeneous population, selected role, or scenario context? |
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
| Event question, boundary, and authorization | This coordination entry | Event-frame review candidate |
| Source register, claim ledger, and evidence-use review | [Event-frame evidence v0.1](frame-evidence-v0.1.md) | Resolved for framing with bounded representation gates |
| Participant, scenario, configuration, and release authorities | None | Not yet authorized or opened for this event |

## Current work package

| Field | Current decision |
|---|---|
| Work mode | Event framing |
| Roles or processes in this package | Incident progression from initial access opportunity through detection, containment, and notification |
| Participant production profiles | Not assigned; participant production is not authorized |
| Required project Skills and templates | Event Build Brief, historical evidence research, participant disposition rules, and phase closeout |
| Expected outputs | This event-frame review candidate, its event-frame evidence record, and an owner disposition |
| Review and verification | Claim-appropriate source review, temporal and participant-availability review, causal ownership review, link and repository checks |
| Stop conditions | The owner rejects or changes the temporal boundary, primary question, claim boundary, or role split; semantic review finds an ownership defect; protected content would be required; or the work would enter participant production |
| Next legal action | Owner review of the proposed temporal boundary and representation gates, followed by one event-frame semantic and closeout review if accepted |

The non-authorizing target for later phases is **semantically complete,
engineering-minimal**: complete dispositions and accepted products for the
causally necessary roster, accepted scenario and mapping semantics, and one
high-information non-financial lineage through bounded conformance. It does
not imply a full-roster runtime or broad simulation.

## Open decisions

| ID | Decision or risk | Owner | Minimum input needed | Dependent work |
|---|---|---|---|---|
| `OD-EV-01` | Accept the proposed 23 August 2017–20 July 2018 core interval, with patient-notification observation through 23 July and an 11 June–20 July primary response window | Project owner | `0616-FR-C01`–`0616-FR-C04` and the primary-question consequence | Frame acceptance |
| `OD-RP-01` | Threat actor representation | Project owner after evidence and behavior research | Choice granularity, observability, and scenario-externalization cost | Roster acceptance |
| `OD-RP-02` | Preserve separate gates for technical administrators, SIRM, Cluster ISO, IHiS senior management, SingHealth management, and routed government response | Project owner | `0616-FR-C05`–`0616-FR-C16` and the causal role map | Frame acceptance and later Roster research |

## Phase status

Frame the event readiness:

- [x] Event identity, accepted primary question, method baseline, purpose, claim
  exclusions, construction exposure, and current stopping boundary are explicit.
- [x] Protected inputs and the current local source boundary are explicit.
- [x] Candidate causal transitions, dispositions, and shared concepts identify
  the questions that evidence must resolve.
- [ ] The evidence-supported temporal boundary is accepted by the owner.
- [x] External source permission and the adopted event-frame evidence set are
  closed for their stated use.
- [x] Material causal transitions have supported owners or bounded
  representation gates.
- [ ] Shared information and authority boundaries have received event-framing
  review.

**Current disposition: Owner decision required.** Event framing remains open
until the temporal boundary and role gates are accepted and receive one
event-frame semantic review. Participant production would test a later phase.
