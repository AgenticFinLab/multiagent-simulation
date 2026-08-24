# IHiS technical administration and line security staff

## Model overview

| Field | Value |
|---|---|
| Model name | IHiS technical detection and local response role set |
| Event and modeled interval | `H2EPR-0616`; participant response from 18 January through 20 July 2018, with acute response from 11 June |
| Choice unit | One institution-preserving technical responsibility unit: the smallest event-time assignment that receives the observation and can choose a local response |
| Host, institution, or account scope | IHiS personnel and units deployed to or supporting SingHealth systems; each unit remains attached to its own function, information, access, and authority |
| Causal role in the event | Detect, interpret, investigate, communicate, and locally respond to technical signals before or alongside formal incident classification and escalation |
| Evidence and outcome-exposure boundary | `FULL_DRAFT_EXPOSED`; official retrospective inquiry evidence; no held-out, clean-builder, calibration, or validity claim |
| Identity, version, and status | `h2epr-0616-technical-response-role-set`, `0.1.0`, accepted standard Population Model |

This model preserves distributed technical choices needed to explain CT-4 of
the accepted event frame. It does not model “IHiS technical staff” as a single
actor. It also does not reconstruct every named employee as an Agent when the
research question needs their role-local information and choices rather than
individual biography.

## 1. Scope and representation

One choice unit represents the smallest documented technical responsibility
assignment that both receives a bounded observation and can choose a local
response. The scenario may attach that assignment to a responsible practitioner
or an operating team, but the model does not alternate its decision granularity
within an episode. Units fall within three role types:

- **application/database operations**, which observes application monitoring,
  database sessions, queries, and local application controls;
- **Citrix/infrastructure administration**, which observes host, credential,
  session, access, and infrastructure evidence and controls; and
- **security engineering/CERT**, which receives delivered security signals,
  performs bounded investigation or forensics, and communicates findings to
  the SIRM or other authorized recipients.

The scenario owns which units exist, their responsibility holders, assignments,
account and host relations, availability, and event-time access. If a team
contains distinct responsibility holders with different information or
authority, it must be instantiated as separate units rather than given a team
mind. A unit does not inherit another unit's logs, messages, expertise, or
authority. The population has no shared voice, belief, incident classification,
reporting authority, or control budget.
Aggregate analysis may count or group unit intents and delivered findings, but
that aggregate is not a new decision-maker.

The model excludes the SIRM and Cluster ISO offices, senior IHiS management,
SingHealth management, the threat actor, endpoint users, and later investigators.
Formal incident classification and upward escalation belong to the separately
modeled offices or later roster rows; delivery and technical effects belong to
the scenario.

The representation should be split if a later accepted question requires a
named person's unique authority, durable personal history, or cross-role control
that the typed unit cannot express. It should return to scenario ownership if
evidence shows that the material actions were mechanically prescribed and left
no role-local interpretation or choice.

## 2. Evidence and institutional basis

The [R1 participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
supplies the shared source identity, claim status, participant-time limits, and
withdrawal consequences. This model relies principally on:

- `0616-R1-C01`--`0616-R1-C02` for the multi-unit response structure and
  uneven reporting guidance;
- `0616-R1-C03`--`0616-R1-C05` for January and June observations, local action,
  communication, and compartmentalization; and
- `0616-R1-C06` for independent investigation and local-control choices in
  early July.

The institutional basis is event-specific. The official inquiry reconstructs
actions and messages from testimony and records, but its later attribution and
adequacy judgments were not known to the participants. Historical initiative
does not become a fixed “vigilant staff” type, and historical omissions do not
become a fixed failure policy.

Two provisional mechanisms organize the evidence:

1. **Local problem ownership under incomplete reporting guidance.** A unit may
   continue investigation or local containment because it has actionable local
   access but lacks a clear reporting route or complete incident account.
2. **Fragmented information integration.** Units receive different artifacts
   and may share them with different recipients, so no one unit necessarily
   observes the cross-system pattern.

Workload, technical expertise, message quality, and organizational direction
remain competing explanations. No general theory, numerical distribution, or
cross-event response law is adopted.

## 3. Information, private state, and heterogeneity

### Participant observations

| Observation | Unit-specific meaning | Source and availability | Missing or stale behavior |
|---|---|---|---|
| `local_technical_signal` | Alert, query, callback, session, process, credential use, or log visible through the unit's assigned system | Produced by monitoring or local investigation and visible only when routed to that unit | Absence means no activation from that signal; it is not evidence that the event is safe |
| `delivered_peer_finding` | A technical finding, screenshot, message, or request delivered by another unit | Available only after scenario-owned delivery with sender, content, time, and recipient | Missing context remains missing; delivery does not imply comprehension or agreement |
| `local_control_state` | The unit's observed account, host, session, query, or tool state relevant to a proposed action | Role- and access-bounded scenario observation | Stale state may trigger verification rather than an assumed current result |
| `security_response_request` | A delivered request or direction from an authorized security interface | Available to the addressed unit after delivery | No request does not remove local authority already established by role and scenario |
| `action_result_notice` | Delivered result of a prior investigation, communication, or local-control intent | Produced by the scenario or receiving participant | Missing results keep the matter open; the unit may not assume success |

Each unit may retain three qualitative private items:

- `local_assessment`: `unexamined`, `routine_possible`, `suspicious`, or
  `security_review_needed`;
- `open_questions`: the bounded artifacts, identities, routes, or explanations
  still sought; and
- `last_shared_finding`: an identifier for the most recent communication the
  unit itself issued or acknowledged.

These items belong to the unit, begin empty or unexamined, and change only
after a legitimate local observation or delivered message. They are not
authoritative incident state and are never shared automatically.

Role type supplies only event-relevant heterogeneity. Application/database
units can inspect queries and application behavior; Citrix/infrastructure units
can inspect and alter bounded host, account, session, or network controls;
security-engineering units can perform the investigation available to them and
route findings through Security Management. Actual access and feasibility
remain scenario facts.

## 4. Behavior and choice

A unit activates when it receives a new local signal, a delivered technical
finding, a security request, or a result that leaves a material question open.
It first checks its role and current access, then compares the signal with known
local activity, identifies missing context, and chooses from actions it is
authorized to request.

### Situation A — anomalous local signal

Available choices are to inspect the signal, seek peer context, communicate a
bounded finding, request security review, apply an authorized local control, or
continue monitoring with an explicit reopening condition. A unit cannot remain
indefinitely inactive once it assesses a signal as needing security review: it
must either communicate the finding, request review, or record a concrete
missing fact and the next observation that reopens the choice.

### Situation B — a new cross-system connection

When a delivered or locally discovered fact connects previously separate
signals, the unit may verify the connection, share it with identified
recipients, request coordinated review, or apply a bounded control within its
own authority. It cannot treat knowledge held by another unit as already
delivered to Security Management.

### Situation C — incomplete or adverse result

Failure, ambiguity, or reappearance after a local-control attempt keeps the
underlying question open. The unit may retry an authorized control, broaden a
request, seek another unit's evidence, or request security coordination. It may
not rewrite an attempted or partial result as successful containment.

The baseline is set-valued. Local problem ownership can favor investigation or
control, while fragmented information can delay cross-team integration.
Expertise, workload, message clarity, and received direction may alter the
admissible selection. No parameter fixes the historical action.

## 5. Intent, result, and scenario boundary

| Intent | Meaning | Target | Required content | Scenario-owned result |
|---|---|---|---|---|
| `investigate_local_signal` | Request or undertake an authorized bounded inspection | The unit's assigned system, artifact, host, account, or record | Signal identity, scope, requested check, and event time | Access, execution, evidence returned, failure, and timing |
| `request_peer_context` | Ask another technical unit for logs, identity, explanation, or corroborating context | Named technical unit or responsible practitioner | Question, relevant artifact or interval, and reply route | Delivery, availability, reply, and content |
| `share_technical_finding` | Communicate a bounded observation or interpretation | Named peer, SIRM, Cluster ISO, or authorized group | Sender, recipient, event time, artifact or proposition, uncertainty, and requested attention | Delivery, acknowledgement, interpretation, and follow-up |
| `request_security_review` | Ask the security-response interface to assess or coordinate a suspected issue | SIRM or authorized Security Management route | Observed facts, uncertainty, affected scope, local actions, and open questions | Delivery, classification, coordination, or escalation |
| `apply_local_control` | Request an authorized local account, session, host, query, firewall, or monitoring intervention | Scenario-owned technical process within the unit's authority | Target, intended restriction or check, duration or review condition, and reason | Admissibility, execution, partial effect, failure, side effects, and observed result |

Population-level counts, clusters, or sequences of these intents are analysis
outputs only. They do not create a population instruction, incident decision,
or authoritative technical state.

## 6. Cases, uncertainty, and falsification

### January callback signal — reconstructed, exposed outcome

A security-engineering unit receives a malware alert and callback evidence but
does not know the later attack attribution. It may investigate, apply a bounded
local control, communicate the address and host evidence, and request broader
review. A historical local containment action is admissible but not required.
The model fails if it gives the unit later command-and-control attribution or
guarantees that a network-wide block would prevent the breach.

### June unauthorized account use — reconstructed, exposed outcome

A Citrix/infrastructure unit observes unauthorized credential use while other
units have not received its full account. Local password or host actions and a
security-review request are both admissible. The model fails if every technical
unit automatically learns the account identity, investigation results, or
message significance.

### July active database queries — reconstructed, exposed outcome

Application/database units observe continuing unusual queries, seek context,
terminate queries, and develop a blocking script while security roles receive
fragmented communications. The model must permit both urgent local control and
explicit reporting. It fails if intended query termination declares that data
was not returned or that the attacker was contained.

The principal structural uncertainty is unit composition: the event record
supports role types and particular examples, not a complete population census
or numerical weights. A later accepted source showing unique cross-unit
authority would trigger a split into an Agent; evidence that all material
choices were centrally mandatory would trigger scenario externalization.

## 7. Limitations, provenance, and review

This model is event-bound, qualitative, uncalibrated, and non-executable. It
does not claim to reproduce every technical employee, measure cybersecurity
competence, predict staff behavior, establish the effect of a counterfactual
control, or validate the event simulation. It describes permissible
participant intents and information boundaries, not an implementation policy.

Provenance:

- Event Build Brief v0.1 and frame evidence v0.1 accepted at repository commit
  `6228dee373743317e8984d8ef55303f8557e301b`;
- participant claims `0616-R1-C01`--`0616-R1-C06` in the adjacent R1 evidence
  record;
- `OD-R1-01`, accepted by the project owner on 24 August 2026; and
- method baseline `bea83b1a51256198d264760a88268e041d990700`.

Review status: `READY_FOR_REFERENCE_CANDIDATE`; accepted after concise
standard-profile review and the shared R1 interface preflight.

## Interface handoff

| Surface | Meaning and owner |
|---|---|
| observations and timing | Role-local technical signals and delivered messages; scenario owns production, delivery, event time, and freshness |
| private state and isolation | Unit-local assessment, open questions, and last shared finding; never visible to another unit without an explicit message |
| intents and counterparties | Investigate, request peer context, share findings, request security review, and apply bounded local control |
| routes and scenario dependencies | Named technical, SIRM, Cluster ISO, and authorized group routes; scenario owns delivery, access, and technical effects |
| authority, resources, and lifecycles | Authority is unit- and assignment-specific; scenario owns hosts, accounts, tools, requests, results, expiry, and failure |
| aggregation or analysis output | Counts or sequences of unit intents and delivered findings; no collective decision or belief |
| interface classification | `MAPPING_EXTENSION_EXPECTED`; semantic fit is reviewable, but no wire mapping or carrier is selected |

This handoff authorizes no mapping, configuration, policy, binding, runtime, or
simulation work.
