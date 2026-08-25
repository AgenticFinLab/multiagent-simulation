# IHiS technical administration and line security staff

## 1. Model overview

| Field | Value |
|---|---|
| Model name | IHiS technical detection and local response role set |
| Event and interval | SingHealth Data Breach; decisions from 18 January through 10 July 2018, with later response context through 20 July |
| Choice unit | One institution-preserving technical responsibility unit: the smallest event-time assignment that receives the observation and can choose a local response |
| Population scope | IHiS personnel and units deployed to or supporting SingHealth systems; each unit remains attached to its own function, information, access, and authority |
| Primary decision situations | Detect, interpret, investigate, communicate, and locally respond to technical signals before or alongside formal incident classification and escalation |
| Aggregation boundary | Units may be summarized by technical responsibility type, but observations, assessments, authority, intents, and results remain local to each unit |
| State authority | Accounts, hosts, sessions, controls, delivery, incident classification, and technical results remain scenario- or institution-owned; units retain only their declared private state and observed intent lifecycles |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound qualitative reconstruction; later outcomes informed construction but are excluded from participant-time information |

This model preserves distributed technical choices needed to explain CT-4 of
the accepted event frame. It does not model “IHiS technical staff” as a single
actor. It also does not reconstruct every named employee as an Agent when the
research question needs their role-local information and choices rather than
individual biography.

## 2. Population scope and representation

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

## 3. Evidence and theoretical foundation

The [R1 participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
supplies the shared source identity, claim classification, participant-time limits, and
withdrawal consequences. This model relies principally on:

- `0616-R1-C02` and `0616-R1-C14` for the multi-unit response structure and
  uneven reporting guidance;
- `0616-R1-C03`--`0616-R1-C05` for January and June observations, local action,
  communication, and compartmentalization; and
- `0616-R1-C06` and `0616-R1-C16`--`0616-R1-C17` for investigation and
  local-control choices in early July.

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

## 4. Event role and relationships

Technical responsibility units supply local detection, investigation,
communication, and control choices while preserving the organizational routes
through which their findings may become a coordinated incident account.

| Relationship | Unit-side role | Other owner |
|---|---|---|
| unit ↔ assigned system or account | inspect an authorized target and request a bounded local control | the scenario owns access, execution, authoritative state, and technical effect |
| unit ↔ peer technical unit | request context or share a sourced finding | each peer retains its own observations, assessment, access, and response choice |
| unit ↔ SIRM or Cluster ISO | deliver a bounded finding or request security review | the addressed office owns classification, coordination, and escalation choices after delivery |
| unit ↔ operational management | answer a scoped request, provide follow-up, or communicate an unresolved issue | the management unit owns aggregation and upward routing; delivery remains institutional |

No relationship gives all technical units a common view or permits the
population to classify the incident, direct senior management, or declare a
control successful.

## 5. Decision situations, information, and state

### Participant observations

| Observation | Unit-specific meaning | Source and availability | Missing or stale behavior |
|---|---|---|---|
| `local_technical_signal` | Alert, query, callback, session, process, credential use, or log visible through the unit's assigned system | Produced by monitoring or local investigation and visible only when routed to that unit | Absence means no activation from that signal; it is not evidence that the event is safe |
| `delivered_peer_finding` | A technical finding, screenshot, message, or request delivered by another unit | Available only after scenario-owned delivery with sender, content, time, and recipient | Missing context remains missing; delivery does not imply comprehension or agreement |
| `local_control_state` | The unit's observed account, host, session, query, or tool state relevant to a proposed action | Role- and access-bounded scenario observation | Stale state may trigger verification rather than an assumed current result |
| `security_response_request` | A delivered request or direction from an authorized security interface | Available to the addressed unit after delivery | No request does not remove local authority already established by role and scenario |
| `action_result_notice` | Delivered result of a prior investigation, communication, or local-control intent | Produced by the scenario or receiving participant | Missing results keep the matter open; the unit may not assume success |

Each unit may retain four qualitative private items:

- `local_assessment`: `unexamined`, `routine_possible`, `suspicious`, or
  `security_review_needed`;
- `open_questions`: the bounded artifacts, identities, routes, or explanations
  still sought;
- `last_shared_finding`: an identifier for the most recent communication the
  unit itself issued or acknowledged; and
- `active_intent_references`: one entry for each investigation, peer request,
  security-review request, communication, or local-control intent that can
  affect a later choice. An entry records the intent kind, target, issue time,
  and latest delivered lifecycle notice: pending, acknowledged, completed,
  partial, failed, expired, cancelled, or superseded.

These items belong to the unit, begin empty or unexamined, and change only
after a legitimate local observation, intent issuance, or delivered message.
An active-intent entry records what the unit has attempted and the result it
has observed; it is not authoritative execution or incident state. None of
these items is shared automatically.

Role type supplies only event-relevant heterogeneity. Application/database
units can inspect queries and application behavior; Citrix/infrastructure units
can inspect and alter bounded host, account, session, or network controls;
security-engineering units can perform the investigation available to them and
route findings through Security Management. Actual access and feasibility
remain scenario facts.

## 6. Behavioral model

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

Failure, ambiguity, expiry, or reappearance after an issued intent keeps the
underlying question open. A pending equivalent intent normally suppresses a
duplicate, while a failed, expired, cancelled, or superseded intent permits a
new or revised response. The unit may retry an authorized control, broaden a
request, seek another unit's evidence, or request security coordination. It may
not treat an attempted, pending, or partial result as successful containment.

The baseline is set-valued. Local problem ownership can favor investigation or
control, while fragmented information can delay cross-team integration.
Expertise, workload, message clarity, and received direction may alter the
admissible selection. No parameter fixes the historical action.

## 7. Intent and result boundary

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

## 8. Operationalization and uncertainty

A scenario instantiates responsibility units by technical function and binds
each unit to explicit systems, accounts, access, availability, and reporting
routes. The model assigns no fixed population weights or response
probabilities. Aggregates such as the number of investigations, controls, or
shared findings are derived analysis outputs and retain the originating unit
and host.

Initial private state is `unexamined`, with empty questions, sharing history,
and intent references unless a dated participant-time prehistory is supplied.
Role composition, expertise, workload, message clarity, and reporting guidance
remain exposed qualitative uncertainties. The principal structural uncertainty
is unit composition: evidence of unique cross-unit authority would trigger a
split into an Agent, while evidence that all material actions were centrally
mandatory would return the behavior to the scenario.

## 9. Worked cases and falsification

### January callback signal — reconstructed, exposed outcome

A security-engineering unit receives a malware alert and callback evidence but
does not know the later attack attribution. It may investigate, apply a bounded
local control, communicate the address and host evidence, and request broader
review. A historical local containment action is admissible but not required.
The model fails if it gives the unit later command-and-control attribution or
guarantees that a network-wide block would prevent the breach.

**Controlled perturbation.** Remove the callback evidence while preserving the
initial alert. The response may remain a bounded local inspection, but a
callback-specific control or broader review request loses its stated basis.

### June unauthorized account use — reconstructed, exposed outcome

A Citrix/infrastructure unit observes unauthorized credential use while other
units have not received its full account. Local password or host actions and a
security-review request are both admissible. The model fails if every technical
unit automatically learns the account identity, investigation results, or
message significance.

**Controlled perturbation.** Deliver the same account-use finding to Security
Management. The producing unit's local authority is unchanged, but a security-
review response becomes available to the addressed office only after delivery.

### July active database queries — reconstructed, exposed outcome

Application/database units observe continuing unusual queries, seek context,
terminate queries, and develop a blocking script while security roles receive
fragmented communications. The model must permit both urgent local control and
explicit reporting. It fails if intended query termination declares that data
was not returned or that the attacker was contained.

**Controlled perturbation.** Replace a pending termination intent with a
delivered failure notice. Duplicate issuance remains inappropriate while the
intent is pending; after failure the unit must reconsider control, evidence
collection, or security coordination.

## 10. Limitations and references

This event-bound qualitative model does not reconstruct every technical
employee, measure cybersecurity competence, estimate population composition,
predict staff behavior outside the event, or identify the effect of an
unobserved counterfactual control. The complete historical outcome informed
construction, so the cases show explanatory behavior rather than independent
validation.

The [participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
contains the claim-level source locations and withdrawal consequences. The
shared [detection-and-escalation account](../../../agents/interfaces/singhealth_data_breach/r1-detection-and-escalation.md)
describes the model's relations with the SIRM and Cluster ISO.

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
