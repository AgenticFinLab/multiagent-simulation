# R1 detection-and-escalation interface

| Item | Value |
|---|---|
| Status | accepted Roster-production semantic preflight |
| Event | `H2EPR-0616`, SingHealth Data Breach |
| Batch | `R1-DETECTION-AND-ESCALATION` |
| Event frame | accepted Event Build Brief v0.1 and frame evidence v0.1 |
| Products | technical response role-set Population Model `0.1.0`; SIRM Agent Definition `0.1.0`; Cluster ISO Agent Definition `0.1.0` |
| Construction exposure | `FULL_DRAFT_EXPOSED` |

## Purpose

This preflight checks that the three first-batch participant products form a
coherent information, authority, action, and result surface for CT-4 of the
accepted event frame. It does not choose wire fields, define a scenario,
complete the Roster, add configuration, select a carrier, create a policy, or
authorize implementation or simulation.

The reviewed products are:

- [technical administration and line security staff](../../../populations/defines/singhealth_data_breach/technical-administration-and-line-security-staff.md);
- [Security Incident Response Manager](../../defines/singhealth_data_breach/security-incident-response-manager.md);
- [Cluster Information Security Officer](../../defines/singhealth_data_breach/cluster-information-security-officer.md); and
- the shared [R1 participant evidence](../../../events/singhealth_data_breach/participant-evidence-v0.1.md).

## Cross-role causal chain

```text
role-local technical signal
  -> technical responsibility unit observes and interprets locally
  -> unit investigates, requests context, shares a finding, requests security
     review, or requests a local control
  -> scenario delivers bounded content to named SIRM and/or Cluster ISO routes
  -> each office observes only its delivered record and forms its own assessment
  -> SIRM may investigate, coordinate, activate, contain, seek help, or escalate
  -> Cluster ISO may clarify, check response, coordinate reporting, or escalate
  -> scenario owns delivery, authoritative incident state, technical execution,
     institutional classification, further routing, and realized effect
  -> delivered results or new evidence reopen the relevant participant choice
```

No participant owns the whole chain. A local finding is not automatically a
security report; delivery is not understanding; investigation is not
classification; a containment intent is not containment; and escalation is not
recipient acknowledgement or further reporting.

## Product surfaces

### Technical responsibility units

Units observe only assigned-system signals, delivered peer findings, local
control state, delivered security requests, and returned results. Their private
assessment and open questions remain unit-local. They may investigate, request
context, share findings, request security review, or request a bounded local
control. Population composition, assignment, access, delivery, execution, and
effect remain scenario-owned.

### SIRM office

The SIRM observes delivered signals, technical updates, response requests,
scope indicators, capacity state, reporting context, control results, and
feedback. It may request investigation, coordinate response, activate the
SIRT, provide bounded response status, request or direct containment, seek
assistance, escalate a suspected incident, or propose coverage. It cannot
perform technical work, privately activate the SIRT, classify world truth, or
declare a response successful.

### Cluster ISO office

The Cluster ISO observes delivered incident material, SIRM status, CII scope
indicators, technical summaries, response-team state, reporting context,
meeting records, and office availability. It may request clarification or
status, issue bounded coordination direction, request SIRT activation,
coordinate reporting, or escalate a potential CII incident. It does not inherit
SIRM assessment, execute technical controls, or declare activation,
classification, delivery, or containment.

## Interaction closure

| Sender intent | Route and content | Recipient observation and possible response | Scenario-owned result |
|---|---|---|---|
| Technical unit `share_technical_finding` or `request_security_review` | Named SIRM route; evidence, event time, uncertainty, local actions, and open question | SIRM `delivered_security_signal`; assess, investigate, coordinate, contain, or escalate under `DC-SIRM-1`--`DC-SIRM-3` | Delivery, acknowledgement, access to attachments, and later technical or institutional state |
| Technical unit `share_technical_finding` | Named Cluster ISO route; bounded facts and uncertainty | ISO `delivered_incident_signal` or `technical_finding_summary`; clarify, check response, coordinate, or escalate under `DC-CISO-1`--`DC-CISO-3` | Delivery, comprehension is not guaranteed, and no shared assessment is created |
| SIRM `request_security_investigation` | Named technical responsibility unit; signal, scope, question, priority, and reply route | Technical `security_response_request`; inspect, seek peer context, share a finding, or apply an authorized local control | Request admissibility, delivery, access, work, returned evidence, failure, and timing |
| SIRM `coordinate_incident_response` or `direct_local_containment` | Named technical unit; task, target, intended restriction, dependencies, and review condition | Technical `security_response_request`; choose an authorized local response and later consume the delivered result | Delivery, authority check, technical feasibility, execution, partial effect, failure, recurrence, and side effects |
| Cluster ISO `request_incident_clarification` or `issue_security_coordination_direction` | Named technical unit; question or bounded follow-up with scope and timing | Technical `security_response_request`; investigate, request context, or share a bounded finding | Delivery, admissibility, action, reply, and technical effect |
| Cluster ISO `request_response_status` | Named SIRM route; incident reference, requested status, and review condition | SIRM `delivered_response_request`; coordinate and optionally `provide_incident_response_status` under `DC-SIRM-2` | Delivery, reply availability, recipient interpretation, and follow-up |
| Cluster ISO `request_sirt_activation` | SIRM and institutional incident-response route; known evidence, uncertainty, requested functions, and urgency | SIRM `delivered_response_request`; assess and optionally `activate_incident_response_team` under `DC-SIRM-2` | Authority check, delivery, member availability, authoritative activation, and attendance |
| SIRM `provide_incident_response_status` | Named Cluster ISO route; known evidence, uncertainty, active work, capacity, and next review | ISO `sirm_response_update`; clarify, exercise accountability, or escalate | Delivery, acknowledgement, interpretation, and institutional use |
| SIRM `escalate_suspected_incident` | Cluster ISO or authorized management route; evidence, scope, uncertainty, actions, and requested decision | ISO `delivered_incident_signal` when addressed, or an external management observation outside R1 | Delivery, acknowledgement, institutional classification, direction, resources, and further routing |
| Cluster ISO `coordinate_incident_reporting` or `escalate_potential_cii_incident` | SIRM, technical contributor, GCIO, or authorized process; bounded facts, sources, uncertainty, and requested decision | In-batch recipients receive only the message addressed to them; management recipients remain outside R1 | Contribution, report creation, authorization, delivery, acknowledgement, classification, and further reporting |

Every route has a sender-owned intent, scenario-owned delivery, recipient-owned
interpretation, and scenario- or recipient-owned result. No adapter may fill a
missing response policy or convert a participant intent into its historical
outcome.

## Information and state boundaries

- Technical units do not share logs, assessment, access, or open questions
  unless a message or scenario observation explicitly routes them.
- SIRM and Cluster ISO assessments are separate even when they receive the same
  attachment or attend the same meeting.
- A message carries its sender, recipient, content, event time, uncertainty,
  and requested response; a filename, group membership, or copied address does
  not imply understanding.
- Office availability, delegation, SIRT activation, participant assignments,
  host and account state, incident category, and reporting status are
  authoritative institutional or scenario state.
- Participants may retain only their declared assessment, open requests,
  active intents, and acknowledged records. They cannot create a private copy
  of institutional truth.
- Later command-and-control attribution, full attack scope, query-result
  verification, final data loss, inquiry judgments, and public hindsight remain
  unavailable until a legitimate event-time route supplies the relevant fact.

## Authority and result boundaries

| Surface | Technical role set | SIRM | Cluster ISO | Scenario or later owner |
|---|---|---|---|---|
| Local technical investigation | Choose a bounded request or action within assigned access | Request and coordinate | Request clarification or follow-up | Access, tools, execution, evidence, and failure |
| Local technical control | Request within unit authority | Request or direct within response authority | Issue bounded coordination direction, not execute | Admissibility, execution, partial effect, recurrence, and side effects |
| Incident assessment | Unit-local technical interpretation only | SIRM's bounded assessment | ISO's independent bounded assessment | Authoritative institutional classification remains external |
| SIRT activation | Receive a delivered response request if assigned | Request formal activation | Request activation and check state | Authority validation, activation, staffing, and attendance |
| Response coordination | Share local findings and receive assigned work | Lead and coordinate technical response | Exercise independent accountability and reporting coordination | Delivery, assignment state, resource availability, and progress |
| Upward escalation | Request security review or share findings | Escalate suspected incident through authorized chain | Escalate potential CII incident through independent route | Delivery, acknowledgement, classification, direction, and further reporting |
| Containment or breach result | None | None | None | Technical and institutional processes own realized state and later evidence |

The distinction between SIRM technical-response leadership and Cluster ISO
independent accountability is causal, not cosmetic. Swapping only names leaves
nothing changed, but swapping their institutional authority changes which
coordination, activation, status, and reporting intents are admissible.

## Shared decision situations

### Partial June technical signal

A technical unit sees unauthorized activity and can investigate, control, or
share it. SIRM acts only after delivery and may coordinate or assess escalation.
Cluster ISO acts only on its own delivered content and may independently seek
clarification or response status. The historical outcome is not available to
any of them. A model in which one email creates identical beliefs across all
three products fails this preflight.

### 4 July active database queries

Technical units may terminate queries, seek context, and share evidence without
knowing final data loss. SIRM may coordinate the response and escalate with
uncertainty. Cluster ISO may request clarification, check response ownership,
or use its independent reporting route. Query termination and a file titled as
a breach do not themselves create authoritative containment or classification.

### Missing, delayed, or adverse result

Undelivered requests produce no recipient observation. A pending or failed
investigation remains open; a failed or partial control does not change world
state as intended; an unacknowledged escalation remains pending. Each product
contains a minimum response and reopening condition, so an always-wait policy
cannot conform after material new evidence or lifecycle failure.

## Interface classification and stopping point

| Interface family | Classification | Later question, if separately authorized |
|---|---|---|
| role-typed population identity and isolation | `MAPPING_EXTENSION_EXPECTED` | Represent responsibility-unit type, assignment, and host/account scope without a collective mind |
| office-level SIRM and Cluster ISO identity | `MAPPING_EXTENSION_EXPECTED` | Preserve separate institutional authority and private assessment surfaces |
| delivered technical and incident information | `MAPPING_EXTENSION_EXPECTED` | Select event semantic identities carrying sender, recipient, time, uncertainty, and freshness |
| investigation, coordination, status, activation, and escalation messages | `MAPPING_EXTENSION_EXPECTED` | Define message and request lifecycles without embedding response policy |
| technical control and containment | `MAPPING_EXTENSION_EXPECTED` | Keep target, authority, request, execution, partial effect, recurrence, and observation distinct |
| SIRT, reporting, and institutional classification state | `MAPPING_EXTENSION_EXPECTED` | Choose one authoritative scenario-owned lifecycle rather than participant copies |
| delayed, missing, failed, partial, expired, and superseded results | `MAPPING_EXTENSION_EXPECTED` | Preserve lifecycle and causal references if mapping is later opened |

The classifications state that later semantic mapping work would be required;
they are not a carrier decision or a concrete Contracts V1 counterexample. No
mapping question is opened in this batch.

## Preflight conclusion

`PASS_R1_SEMANTIC_INTERFACE_WITH_MAPPING_EXTENSION_EXPECTED`

The three products close the accepted CT-4 participant interface without
sharing private state, inventing collective authority, or allowing an intent to
self-realize its result. Out-of-batch management, reporting, delegation, and
external-assistance routes are named as external interfaces rather than hidden
inside an R1 participant. This preflight stops before complete Roster release,
scenario closure, mapping, configuration, binding, policy, runtime, simulation,
calibration, held-out construction, or evaluation.
