# IHiS operational and SCM management

## Model overview

| Field | Value |
|---|---|
| Model name | IHiS operational information-integration and escalation role set |
| Event and modeled interval | SingHealth Data Breach; operational-management decisions on 9 and 10 July 2018 |
| Choice unit | One IHiS operational-management responsibility holder who can gather cross-team information, convene review, assign follow-up, or route a bounded concern upward |
| Host, institution, or account scope | Infrastructure Services, application or SCM service leadership, and cluster-operational coordination within IHiS; each unit retains its own function, information, and authority |
| Causal role in the event | Convert fragmented R1 technical findings into a source-preserving management account and decide whether further verification or senior escalation is required |
| Evidence use and explanatory scope | Official retrospective inquiry evidence supports an event-bound qualitative reconstruction; later findings informed construction but are excluded from participant-time information |

The role set represents the operational bridge between technical investigation
and the Group Chief Information Officer (GCIO). It preserves the choices that
made the 9 July cross-team integration possible without treating IHiS
management as a single actor or reconstructing every named manager as an
individual Agent.

## 1. Scope and representation

One choice unit is the smallest operational-management assignment that can
receive reports from several technical responsibility units and decide how to
coordinate them. Units fall within three event-relevant types:

- **infrastructure coordination**, responsible for bringing together domain
  towers and assigning infrastructure follow-up;
- **application and SCM service coordination**, responsible for seeking and
  interpreting accounts about the application and database service; and
- **cluster-operational coordination**, responsible for relating domain work
  to the SingHealth operating context.

The scenario assigns historical officeholders and determines which units are
active. Serena Yong and Clarence Kua anchor documented examples of the first
two types, but the model does not infer personal dispositions from their names.
A unit receives only the reports and meeting material routed to it. It does not
inherit the logs, assessments, or authority of the R1 technical units, SIRM,
Cluster ISO, GCIO, or another management unit.

The R1 technical population retains investigation, peer communication, and
local-control choices. This model begins when a management responsibility
holder receives one or more bounded accounts and can gather, correlate,
verify, convene, assign, or escalate. Incident classification, executive
direction, SingHealth governance, message delivery, and technical effects are
outside the role set.

A named Agent would be required if accepted evidence showed that one person's
unique authority or durable personal history, rather than a typed management
responsibility, determined the transition. The model should instead return to
scenario ownership if convening and escalation are shown to have been
mechanical routing steps with no role-local interpretation or choice.

## 2. Evidence and institutional basis

The [participant-evidence record](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
provides the source and claim ledger. This model relies principally on:

- `0616-R2-C01`--`0616-R2-C02` for the infrastructure and application-service
  responsibility types;
- `0616-R2-C03`, `0616-R2-C04`, `0616-R2-C05`, and `0616-R2-C25` for
  cross-team gathering, convening, and the possibility of continuing without
  escalation; and
- `0616-R2-C06`--`0616-R2-C07` for two distinct reasons to escalate despite
  incomplete or partly incorrect information.

The official inquiry reconstructs meetings, messages, assigned roles, and
attributed explanations. Its later criticism and completed attack account are
not observations available to a unit on 9 July.

No general management or cybersecurity theory is imposed. Two event-specific
mechanisms organize the evidence:

1. **Cross-team information integration.** A management unit can seek and
   combine accounts that remain separated across technical responsibilities.
2. **Precautionary upward communication.** An unexplained source, serious
   protected system, or unresolved cross-system connection can justify a
   qualified escalation before technical certainty.

Message quality, role-local expertise, reporting knowledge, and the presence
of a sufficiently senior convenor remain competing explanations. The model
does not assign mechanism weights or a universal escalation threshold.

## 3. Information, private state, and heterogeneity

### Participant observations

| Observation | Unit-specific meaning | Source and availability | Missing or stale behavior |
|---|---|---|---|
| `delivered_role_local_account` | A bounded technical finding, action, uncertainty, or management request delivered to the unit | Named technical, operational-management, or authorized senior sender through scenario-owned delivery or an attended meeting | Missing source material remains unknown; the unit may request it but cannot infer it |
| `coordination_meeting_record` | Presented evidence, questions, decisions, and acknowledged action owners | Available only to attending or addressed units after the meeting record is delivered | Attendance does not convey undisclosed prior messages or another attendee's assessment |
| `verification_result_notice` | Delivered result of a requested query, log, source, audit, or scope check | Named technical producer or institutional process | No notice leaves the question open; a claimed result retains its source and uncertainty |
| `management_route_context` | Available GCIO or other authorized senior route, including scope and reporting relationship | Scenario-owned institutional relation visible to the unit | An unavailable route may justify another authorized route or a bounded wait, not silent delivery |
| `intent_lifecycle_notice` | Acknowledgement, progress, completion, partial result, failure, expiry, cancellation, or supersession of an earlier unit intent | Named recipient or institutional process | Silence leaves the intent unresolved and cannot be treated as success |

Each unit may retain:

- `current_cross_team_assessment`: `unassembled`, `fragmented`, `correlated`,
  or `senior_attention_needed`;
- `open_verification_items`: the source, scope, relationship, or result still
  required;
- `last_consolidated_account`: the latest source-preserving account the unit
  prepared or acknowledged; and
- `active_management_intents`: one reference for each information request,
  review, assignment, or escalation intent, with its latest observed lifecycle
  state: pending, acknowledged, completed, partial, failed, expired, cancelled,
  or superseded.

These items begin empty or unassembled and update only after legitimate
delivery, intent issuance, or a delivered lifecycle notice. They are private
to the unit and do not become a second copy of meeting, reporting, or incident
truth.

Heterogeneity is functional rather than numerical. Infrastructure units can
coordinate tower-spanning work; application or SCM units can seek service and
query context; cluster-operational units can relate the issue to local service
responsibility. Actual assignments, access, staffing, and meeting membership
remain scenario facts.

## 4. Behavior and choice

A unit activates when it receives a material role-local account, a new fact
connecting previously separated accounts, a request for management
coordination, or an adverse result for an earlier intent. It first identifies
the source and uncertainty, checks its own responsibility and available route,
then chooses among information gathering, cross-functional review, follow-up,
or qualified escalation.

### Situation A — fragmented operational account

The unit may request a named missing account, seek source or audit
verification, convene the relevant functions, or continue a bounded local
review. If it continues locally, it must identify the missing fact and the
event or review time that reopens the choice. A material account cannot be
dismissed merely because no single message establishes the completed attack.

### Situation B — cross-system connection

When delivered material connects unauthorized access, unusual queries,
credential use, or unexplained source activity, the unit must either convene
or escalate a source-preserving account. Technical uncertainty determines the
content of the message, not whether the recipient may be told that uncertainty
exists. A current acknowledged equivalent escalation suppresses duplication.

### Situation C — missing or adverse response

A pending equivalent request normally supports waiting until its review
condition. Failure, expiry, cancellation, material new evidence, or an
unacknowledged urgent escalation reopens the choice. The unit may retry,
broaden the recipient set within its authority, convene a review, or escalate
the unresolved coordination gap. It cannot declare that requested
investigation, delivery, or senior action occurred.

Within these constraints, cross-team integration favors gathering and
convening, while precautionary communication favors escalation when the
source remains unexplained or the connected scope is material. The evidence
does not select a unique action in every admissible case.

## 5. Intent, result, and scenario boundary

| Intent | Meaning | Target | Required content | Scenario-owned result |
|---|---|---|---|---|
| `request_operational_account` | Seek a bounded role-local finding, action history, or explanation | Named technical or operational responsibility unit | Question, relevant artifact or interval, reason, uncertainty, and reply route | Delivery, access, reply, content, delay, or failure |
| `convene_cross_functional_review` | Request a meeting of the functions needed to correlate a material issue | Named responsibility holders and meeting process | Purpose, known facts, open questions, required functions, urgency, and proposed time | Admissibility, invitations, attendance, presented material, decisions, and timing |
| `request_fact_verification` | Ask for a source, query-result, audit, identity, or scope claim to be checked | Named technical producer or authorized process | Claim, source, requested check, urgency, and review condition | Access, execution, verified or disputed result, failure, and timing |
| `assign_operational_follow_up` | Propose bounded follow-up within the unit's management responsibility | Named operational or technical responsibility unit | Task, scope, priority, dependencies, return route, and review condition | Authority check, acceptance, work, result, delay, or refusal |
| `escalate_operational_concern` | Deliver a qualified cross-team account to an authorized senior route | GCIO or other authorized management recipient | Sources, event time, known facts, uncertainty, actions, open questions, and requested decision | Delivery, acknowledgement, recipient interpretation, direction, classification, and further routing |

Every issued intent is referenced in `active_management_intents`. An
equivalent unresolved intent is not silently duplicated; a failed, expired,
cancelled, or superseded intent may be revised. Counts or sequences of unit
intents are analysis outputs only and do not create a collective management
decision maker.

## 6. Cases, uncertainty, and falsification

### Afternoon cross-team review — reconstructed, exposed outcome

A cluster-operational or infrastructure unit attends a review that correlates
June and July activity but does not establish one explanation or senior route.
It may seek a named clarification, request follow-up, or continue until the
stated review condition. It must not infer later query results or treat meeting
attendance as universal understanding.

**Controlled change.** Add a verified cross-system connection while leaving
final impact unknown. The minimum response shifts from continued local review
to convening or qualified escalation.

### Urgent evening integration — reconstructed, exposed outcome

Application-service and infrastructure units assemble the chronology, retain
an unverified zero-result account, and cannot identify the source of the
queries. Precautionary escalation and a further verification request are both
admissible; stating uncertainty is mandatory.

**Controlled change.** Identify a documented authorized audit as the source.
Source verification remains appropriate, but unexplained-source escalation
loses its basis unless another material indicator remains.

### Pending escalation — illustrative

A unit has already issued a qualified escalation and has no acknowledgement.
Before the review time, an unchanged duplicate is suppressed. At expiry or
after material new scope, the unit must follow up, revise the account, or use
another authorized route.

**Controlled change.** Replace the missing acknowledgement with a delivered
senior request for evidence. The response changes from escalation follow-up to
supplying the requested bounded account or seeking the missing source.

The model fails if unit names determine behavior after authority and
information are held fixed, if all units share facts automatically, if an
unverified result becomes truth, if repeated abstention remains possible after
material integration, or if an intent creates its own meeting, delivery, or
senior response.

## 7. Limitations and references

The inquiry supports event-specific responsibility types and decisions, not a
complete census, population weights, a numerical escalation threshold, or a
general management response law. The role set suppresses personal biography
and any internal conflict not expressed through distinct information,
authority, or messages. It should be narrowed, split, or externalized if later
evidence changes those boundaries.

The full historical outcome informed construction. The cases explain and
challenge the model but do not independently evaluate its historical accuracy
or support transfer to another incident.

- Committee of Inquiry. *Public Report into the Cyber Attack on Singapore
  Health Services Private Limited's Patient Database on or around 27 June
  2018*. 10 January 2019. https://file.go.gov.sg/singhealthcoi.pdf
