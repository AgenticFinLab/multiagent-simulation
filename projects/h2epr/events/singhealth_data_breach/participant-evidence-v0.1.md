# SingHealth Data Breach participant evidence: detection and escalation

This record supports three participant models: IHiS technical administration
and line security staff, the Security Incident Response Manager (SIRM), and the
Cluster Information Security Officer for SingHealth (Cluster ISO). It extends
the event frame only where their representation, information, authority, and
behavior require more specific evidence.

The analysis uses an official retrospective inquiry. The authors had access to
the reported outcome while constructing the models, so later findings may
inform representation, cases, and falsifiers but never a participant's
event-time information or an independent test of the model.

## Evidence basis

The role study reuses one source already cited in the
[event-frame evidence](frame-evidence-v0.1.md):

### `0616-FR-S01` — Committee of Inquiry public report

- Citation: Committee of Inquiry. *Public Report into the Cyber Attack on
  Singapore Health Services Private Limited's Patient Database on or around
  27 June 2018*. 10 January 2019.
- Public file: https://file.go.gov.sg/singhealthcoi.pdf
- Locations used here: paragraphs 67--76, 92--120, 302--327, 329--458, and
  465--593.
- Identity locator: paragraph 67 gives the SIRM officeholder's source-form
  name, Tan Choon Kiat Ernest.
- Source relation: official retrospective investigation drawing on testimony,
  messages, documents, forensic work, and expert evidence.
- Use: assigned responsibilities, event-time messages and observations,
  reconstructed actions, bounded participant explanations, representation,
  decision situations, mechanism alternatives, and falsifiers.
- Limitation: Committee judgments and later attack attribution were not
  available to participants during the event and do not establish a general
  behavioral law.

The Event Build Brief and frame evidence supply scope and lineage rather than
independent corroboration. Three other official sources used for the frame add
no role-specific detail needed here and are not counted again merely to
increase the source total.

## Participant claims

“Direct” denotes an institutional fact, message, action, or attributed
explanation recorded by the inquiry. “Retrospective” denotes a later assessment
used only to challenge or delimit a model. Claims are separated when different
participant models or different withdrawal consequences are involved.

| ID | Proposition and event time | Support and relation | Participant availability | Evidence use | Withdrawal consequence |
|---|---|---|---|---|---|
| `0616-R1-C01` | The SIRM led and coordinated technical incident response. | `0616-FR-S01`, paras. 75--76 and 107--113, direct institutional account. | Assigned authority, not shared technical knowledge. | Supports the SIRM representation and response authority. | Reopen the SIRM representation and its coordination commitments. |
| `0616-R1-C02` | Line technical staff had no written incident-reporting protocol; the SIRF was not widely communicated and the IR-SOP reached only limited Security Management recipients. | Paras. 101--105 and 352--354, direct institutional finding. | The absence or limited delivery is a participant-time information constraint. | Supports reporting-knowledge heterogeneity among technical units. | Remove that heterogeneity mechanism and reconsider whether reporting is scenario-prescribed. |
| `0616-R1-C03` | Between 18 and 22 January, a security engineer investigated malware and callbacks, applied local controls, and shared findings. | Paras. 302--327, direct reconstruction. | The engineer and addressed recipients saw particular alerts and messages; later attacker attribution was unavailable. | Supports the January technical decision situation and intent repertoire. | Remove the January case from the technical population model. |
| `0616-R1-C04` | From 11 to 13 June, database and Citrix staff independently observed unauthorized activity, changed credentials, gathered artifacts, and routed only parts of the emerging account to Security Management. | Paras. 329--386, direct reconstruction. | Each team held local observations; email delivery did not create common interpretation. | Supports local choice and multiple information routes. | Narrow the technical representation or remove the multiple-route account. |
| `0616-R1-C05` | Material facts remained compartmentalized: the Citrix team initially restricted distribution of its investigation, and the security engineer did not learn of the S.A. account until 26 June. | Paras. 387--398, direct reconstruction. | Available only to named local recipients until later delivery. | Supports the fragmented-information mechanism. | Remove that mechanism and reconsider whether fewer technical units suffice. |
| `0616-R1-C06` | From 4 through 7 July, application and database staff investigated suspicious queries, sought logs or advice, and terminated queries or sessions. | Paras. 465--509 and 516--540, direct reconstruction. | Observations and choices remained with the responsible units; effects remained external to their decisions. | Supports application/database investigation and local-control choices. | Remove those choices from the population repertoire. |
| `0616-R1-C07` | The SIRM office was unstaffed during the manager's June absence and no covering officer was designated. | Paras. 412--416, direct reconstruction. | Office availability and designated coverage were event-time organizational facts. | Supports the SIRM coverage decision situation. | Remove coverage and delegation from the SIRM model. |
| `0616-R1-C08` | Across January, June, and early July, the SIRM repeatedly sought stronger confirmation before treating the activity as an incident requiring escalation. | Paras. 313--327, 420--458, and 483--496, reconstructed actions and attributed assessments. | The SIRM's assessment is bounded to the evidence received at each date. | Supports confirmation-seeking as one event-specific mechanism. | Remove that mechanism while retaining the office's institutional duties. |
| `0616-R1-C09` | During June, the Cluster ISO received or viewed security messages and asked questions but did not establish the response state, direct the investigation, or escalate the concern. | Paras. 367--386 and 409--416, direct reconstruction with an institutional finding. | Only delivered messages, meetings, and assigned duties were available; the ISO did not inherit all team knowledge. | Supports the June ISO decision situation. | Remove that case without removing the office's independently evidenced role. |
| `0616-R1-C10` | On 4 and 5 July, the Cluster ISO treated the evidence as an unconfirmed potential breach, expected investigation to precede escalation, and did not connect unauthorized access with suspicious queries. | Paras. 488--499 and 516--522, attributed assessment and direct reconstruction. | The interpretation is bounded to the information described at those times. | Supports the ongoing-investigation mechanism and July case. | Remove that mechanism and case while retaining other ISO alternatives. |
| `0616-R1-C11` | On 9 July, cross-team consolidation assembled previously separated facts, and senior escalation followed despite incomplete and partly incorrect information. | Paras. 548--570, direct reconstruction. | Participants received only the meeting account and routed reports; later query verification was unavailable until 10 July. | Supports the information-integration contrast used across the three models. | Remove that contrast from their cases and shared interface. |
| `0616-R1-C12` | The inquiry later found strong front-line initiative alongside inadequate classification, coordination, and escalation by particular response roles. | Paras. 510--515, 544--546, and 593, retrospective finding. | Unavailable during the event. | Used only as a falsifier and warning against scripting the observed response. | Remove this retrospective falsifier; participant boundaries otherwise remain unchanged. |
| `0616-R1-C13` | The Cluster ISO held communication and incident-reporting responsibilities and stood in the initial reporting chain. | Paras. 75--76 and 108, direct institutional account. | Assigned authority, not automatic access to the SIRM's or technical teams' information. | Supports a distinct Cluster ISO representation and reporting authority. | Reopen the Cluster ISO representation and reporting commitments. |
| `0616-R1-C14` | The SIRT brought together Security Management, infrastructure, and application roles. | Paras. 109--113, direct institutional account. | Membership did not imply activation, attendance, or shared knowledge. | Supports a multi-unit coordination route rather than a single technical actor. | Remove the SIRT membership assumptions from the shared interface. |
| `0616-R1-C15` | In January, the SIRM assessed the malware matter as common and contained and did not escalate it. | Paras. 313--327, direct reconstruction and attributed assessment. | The SIRM had only the routed January evidence and its own assessment. | Supports the January SIRM case, not a fixed non-escalation policy. | Remove that SIRM case without removing the technical-unit reconstruction. |
| `0616-R1-C16` | In early July, technical staff developed and deployed a blocking script outside the normal change procedure. | Paras. 465--509 and 516--540, direct reconstruction. | The responsible units knew the proposed change and local reason; execution and effect remained separate facts. | Supports an urgent local-control choice under procedural pressure. | Remove the procedure-sensitive control case from the population model. |
| `0616-R1-C17` | In early July, technical units changed bounded account or network controls in response to suspicious activity. | Paras. 465--509 and 516--540, direct reconstruction. | Each unit observed only the controls and results delivered within its assignment. | Supports infrastructure/security local-control choices. | Remove those control choices from the population repertoire. |
| `0616-R1-C18` | By 6 July, the SIRM described the expected pressure of frequent escalation updates on the response team as a reason for delay. | Paras. 541--544, attributed explanation. | The explanation belongs to the SIRM at that time; the inquiry's later judgment was unavailable. | Supports escalation burden as a competing mechanism. | Remove that mechanism without changing confirmation seeking or formal duties. |
| `0616-R1-C19` | Neither the SIRM nor the Cluster ISO activated the SIRT during the June period reconstructed by the inquiry. | Paras. 412--416, direct reconstruction. | Activation state was an event-time institutional fact; later adequacy judgments were unavailable. | Supports an observed coordination outcome used in both office-level cases. | Remove that outcome from the cases without changing independently supported authority. |

## Evidence-to-model findings

### Technical role set

The evidence supports distinct application/database, Citrix/infrastructure,
and security-engineering/CERT responsibility units. Their observations and
local control authority differ, making a population model preferable to either
one collective technical-staff Agent or a biography for every employee.

Local problem ownership under incomplete reporting guidance and fragmented
cross-team information are the principal mechanisms. Workload, expertise, and
message quality remain alternatives. The record does not identify population
weights, numerical thresholds, or a general cybersecurity response policy.

### Security Incident Response Manager

The SIRM office has a defensible decision interface for investigation
coordination, response-team activation, containment direction, outside
assistance, and escalation. Confirmation seeking, incomplete information,
limited forensic capacity, office availability, escalation burden, and
false-alarm concern remain explicit alternatives rather than one fitted rule.

### Cluster Information Security Officer

The Cluster ISO has a distinct communication, reporting, accountability, and
escalation interface. Treating the role as a SIRM proxy would erase a route by
which incomplete information could be queried, coordinated, or escalated.
Reliance on ongoing investigation, incomplete messages, limited comprehension,
availability, and role ambiguity remain competing explanations.

## Evidence limits

This source set is sufficient for the three bounded participant models and
their shared detection-and-escalation account. It does not identify numerical
mechanism weights, complete technical-unit composition, fixed historical
policies, or behavior for other roster roles. New evidence is needed only if a
material participant boundary, authority claim, or mechanism changes.
