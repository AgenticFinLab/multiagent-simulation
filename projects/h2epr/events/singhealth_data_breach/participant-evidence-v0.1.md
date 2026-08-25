# SingHealth Data Breach participant evidence

This record supports the participant models for technical detection,
incident-response escalation, senior classification and reporting, and
SingHealth governance and notification. It extends the event frame only where
their representation, information, authority, and behavior require more
specific evidence.

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
- Locations used here: paragraphs 23--40, 67--120, 302--327, 329--458, and
  465--645.
- Identity locators: paragraphs 23, 31, 67, 72, 555, and 568 identify the
  officeholders and operational leaders used in the participant models.
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
| `0616-R2-C01` | Infrastructure Services was divided into domain towers and a horizontal cluster grouping intended to propagate information and actions across clusters. | Paras. 67--68, direct institutional account. | This establishes typed operational-management responsibility, not shared knowledge across towers. | Supports the infrastructure-coordination type in the operational-management role set. | Remove that type and reassess whether scenario routing is sufficient. |
| `0616-R2-C02` | Service Delivery and the SCM Application Team had a distinct production-support and issue-resolution function. | Para. 69, direct institutional account. | Role and service responsibility were institutional facts; incident details still required delivery. | Supports the application-service coordination type. | Remove that type and narrow the operational-management model. |
| `0616-R2-C03` | The 1:00pm meeting on 9 July brought security, Citrix, directory, and infrastructure participants together to correlate June and July events and discuss controls. | Paras. 548--550, direct reconstruction. | Attendees knew only the material presented and discussed; later inquiry assessment was unavailable. | Supports the cross-team aggregation situation. | Remove that situation from the operational-management model. |
| `0616-R2-C04` | Applications Service Lead Clarence Kua sought information from SCM and security contacts and learned material June and July facts not previously available to him. | Paras. 555--556, direct reconstruction. | Clarence acquired only the accounts delivered by those contacts. | Supports application-service information gathering. | Remove that choice from the operational-management repertoire. |
| `0616-R2-C05` | Infrastructure Services Director Serena Yong treated Clarence's bounded account as serious and convened an urgent cross-functional meeting. | Paras. 557--558, direct reconstruction. | Serena received Clarence's summary, not the complete technical record. | Supports infrastructure-led convening under incomplete information. | Externalize meeting initiation and narrow the infrastructure-coordination choice. |
| `0616-R2-C06` | After the urgent meeting retained an unverified claim that the queries returned no records, Serena chose escalation because over-communication was preferable despite no observed operational impact. | Paras. 558--561, reconstructed action and attributed explanation. | The meeting account and uncertainty were available; later verification was not. | Supports precautionary escalation as an event-specific mechanism. | Remove that mechanism from the operational-management model. |
| `0616-R2-C07` | Clarence separately supported escalation because the query source remained unidentified despite possible benign and adverse explanations. | Paras. 559--561, reconstructed action and attributed explanation. | The unresolved alternatives were available; later attack attribution was not. | Supports unresolved-source escalation as a competing operational route. | Remove that mechanism from the application-service type. |
| `0616-R2-C08` | The SingHealth GCIO was accountable both to SingHealth management for CIO services and to the IHiS CEO for service quality and IHiS leadership responsibilities. | Paras. 70--75, direct institutional account. | Dual accountability did not confer complete technical or management knowledge. | Supports a boundary-spanning GCIO office distinct from either organization. | Reconsider the separate GCIO representation and its reporting routes. |
| `0616-R2-C09` | On 9 July GCIO Benedict Tan received a vague, compressed, and partly incorrect account, yet immediately relayed it to the IHiS CEO and CSG Director and arranged further review. | Paras. 561--565, direct reconstruction and attributed assessment. | Only the relayed content, including the zero-result claim and uncertainty, was available. | Supports ambiguity-tolerant upward routing. | Remove that mechanism and reconsider scenario ownership of the bridge. |
| `0616-R2-C10` | The IHiS CSG Director, acting as healthcare Sector Lead point of contact, was responsible for incident categorization and reporting to CSA and for reporting security incidents through designated healthcare leadership routes. | Paras. 78--84, 93--108, and 571, direct institutional account. | This was office authority and procedure, not proof of an event-time classification or automatic report. | Supports the Sector Lead classification and reporting interface. | Reopen that representation and return the route to institutional procedure unless another owner is evidenced. |
| `0616-R2-C11` | The IHiS CEO had ultimate responsibility for ensuring that reportable incidents were reported to CSA. | Para. 108, direct institutional account. | Executive responsibility did not confer the Sector Lead's private assessment. | Supports a separate IHiS executive reporting-direction interface. | Reassess the IHiS CEO representation and authority. |
| `0616-R2-C12` | On the night of 9 July Kim Chuan considered whether the event was deliberate and reportable and which category applied, but lacked important compromise facts and deferred CSA reporting until the scheduled executive call. | Paras. 565--566 and 571--573, direct reconstruction and attributed reasoning. | He knew the compressed account and absence of an audit or red-team exercise, not the full credential-compromise record. | Supports incomplete-information classification and bounded deferral. | Remove that decision situation from the Sector Lead model. |
| `0616-R2-C13` | Bruce Liang directed urgent review and a next-day conference call but did not then categorize the matter because prior unauthorized-access events had not always been security incidents. | Paras. 564 and 567--573, direct reconstruction and attributed explanation. | Bruce received the brief account and zero-result statement; later verification was unavailable. | Supports staged executive review as an event-specific mechanism. | Remove that mechanism and reconsider scenario ownership of executive timing. |
| `0616-R2-C14` | After learning on 10 July that a rerun returned data and a compromised device was implicated, Kim Chuan directed scope estimation, formed a provisional Category 1 assessment, and waited for the scheduled CEO briefing before reporting. | Paras. 575--578, direct reconstruction and attributed assessment. | The new results became available at the morning meeting; the completed investigation remained unknown. | Supports evidence-responsive classification and the executive-briefing alternative. | Remove the affected mechanism and reopen the Sector Lead review. |
| `0616-R2-C15` | After receiving a fuller account, Bruce requested the query logs and additional explanation. | Paras. 579--583, direct reconstruction. | He received the slide summary, logs, and meeting answers sequentially. | Supports executive information seeking before direction. | Remove information seeking from the IHiS CEO model. |
| `0616-R2-C16` | Kim Chuan categorized the event as Category 1 when Bruce asked how it should be treated. | Para. 584, direct reconstruction. | Classification followed the fuller account; it did not itself notify CSA. | Supports the Sector Lead classification choice. | Return categorization to scenario procedure. |
| `0616-R2-C17` | The GCIO delivered a bounded incident account to SingHealth management and requested advice on using the MOH reporting route. | Para. 588, direct reconstruction. | SingHealth saw only the delivered summary; the GCIO did not decide its response. | Supports the cross-institution GCIO report-and-advice interface. | Remove that interface after IHiS classification. |
| `0616-R2-C18` | On 9 July Deputy GCEO Kenneth Kwek asked whether the matter was serious and should be reported to MOH, then did not inform the GCEO after the GCIO said more information was needed and promised a next-day update. | Para. 568, direct reconstruction. | Kenneth knew the GCIO's vague account and reply; the GCEO did not receive it through this route that night. | Supports a separate Deputy GCEO information and escalation choice. | Reassess whether one SingHealth management interface is sufficient. |
| `0616-R2-C19` | On 10 July GCEO Ivy Lim stated that unauthorized access should be reported to MOH immediately and later directed use of the formal protocol after receiving the written account. | Paras. 581 and 588, direct reconstruction. | Ivy acted only after the lunch disclosure and later email. | Supports the GCEO reporting-direction interface. | Externalize that direction or remove the separate GCEO model. |
| `0616-R2-C20` | SingHealth senior management treated prompt patient information, protection of ongoing forensics, avoidance of uncontrolled disclosure, and verified scope, integrity, and exfiltration information as jointly material to announcement timing. | Paras. 624--626, direct institutional reconstruction. | This was a documented management position after incident notification, not each manager's earlier private belief or a numerical threshold. | Supports evidence-sufficiency and investigation-protection mechanisms. | Remove those mechanisms from the SingHealth governance models. |
| `0616-R2-C21` | Kenneth began mobilizing the communications team after the 12 July consultation while affected-patient estimates remained unsettled. | Para. 627, direct reconstruction. | The decision preceded later exfiltration and integrity updates. | Supports anticipatory outreach preparation. | Remove resource mobilization from the Deputy GCEO model. |
| `0616-R2-C22` | Kenneth took direct charge of patient outreach and communications in close consultation with Ivy. | Para. 631, direct institutional reconstruction. | This supports related but distinct executive offices, not automatic shared knowledge. | Supports the Deputy GCEO lead and GCEO consultation interface. | Reopen both representations and their consultation route. |
| `0616-R2-C23` | SingHealth chose to notify a wider patient date range than the technically identified affected interval to address recall and record-timing uncertainty. | Paras. 632--633, direct reconstruction. | The choice followed IHiS' 18 July scope update; patient response and delivery remained external. | Supports a notification-audience proposal and review choice. | Remove that choice from the SingHealth governance models. |
| `0616-R2-C24` | Ivy suggested making SMS the primary notification channel to support rapid large-scale dissemination. | Para. 635, direct reconstruction. | The suggestion was available during outreach planning; organizational adoption and delivery remained separate. | Supports the GCEO channel-recommendation choice. | Treat channel selection as entirely scenario-owned. |
| `0616-R2-C25` | The 1:00pm meeting on 9 July ended without a decision to escalate the matter to the GCIO. | Paras. 552--554, direct reconstruction. | Participants had the discussion record; later inquiry criticism was unavailable. | Supports continue-without-escalation as an operational alternative. | Remove that alternative from the operational-management case. |
| `0616-R2-C26` | After reviewing the fuller 10 July account, Bruce directed that the matter be reported to CSA. | Para. 584, direct reconstruction. | The direction followed executive briefing; report issuance and CSA response remained separate. | Supports the IHiS CEO external-report direction. | Remove that intent from the IHiS CEO repertoire. |
| `0616-R2-C27` | Bruce assigned Leong Seng to lead IHiS' investigation. | Para. 587, direct reconstruction. | Assignment was an executive responsibility decision; investigation and findings remained external. | Supports investigation-resource assignment. | Remove that intent from the IHiS CEO repertoire. |
| `0616-R2-C28` | Kim Chuan instructed CSG staff to notify CSA through its hotline and separately contacted CSA. | Para. 592, direct reconstruction. | The intent followed Category 1 classification; delivery, acknowledgement, and CSA response remained separate. | Supports the Sector Lead CSA-reporting action. | Return that route to scenario ownership. |
| `0616-R2-C29` | From 11 July the GCIO led the War Room's patient-impact cell and used its findings to keep SingHealth updated. | Paras. 602 and 604, direct institutional reconstruction. | SingHealth received routed updates; the GCIO did not determine authoritative breach scope or communication choices. | Supports the continuing patient-impact information bridge. | Narrow the GCIO to the initial report. |
| `0616-R2-C30` | Exfiltration information delivered on 13 July and data-integrity information delivered on 14 July enabled SingHealth to develop its outreach plan further. | Paras. 628--629, direct reconstruction. | Each fact became available at its meeting time; neither was available on 10 July. | Supports evidence-responsive outreach revision. | Remove that mechanism from the SingHealth governance models. |
| `0616-R2-C31` | Bruce Liang concurrently held the offices of IHiS CEO and MOH CIO. | Paras. 23 and 37, direct institutional account. | The appointments did not identify the capacity used for every communication or provide access to all MOH information. | Supports an explicit dual-capacity boundary around the IHiS CEO model. | Remove that boundary without admitting a separate MOH actor. |
| `0616-R2-C32` | Kim Chuan concurrently held the offices of IHiS CSG Director and MOH CISO and reported to Bruce in both capacities. | Paras. 23 and 37, direct institutional account. | The appointments and reporting relation did not create shared IHiS/MOH state. | Supports an explicit dual-capacity boundary around the Sector Lead model. | Retain only independently supported IHiS CSG and Sector Lead authority. |

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

### Operational and SCM management role set

Infrastructure and application-service leaders exercised separate
information-gathering, convening, verification, and escalation choices. A
role-typed population preserves those differences without treating the
temporary meetings or IHiS management as one decision maker. Cross-team
information integration and precautionary escalation are event-specific
mechanisms; role-local expertise and message quality remain alternatives.

### SingHealth Group Chief Information Officer

The GCIO office bridges operational reports to IHiS executive and Sector Lead
routes and separately to SingHealth management. Its dual accountability and
documented routing under ambiguity justify a distinct office interface without
granting it institutional classification, technical execution, or SingHealth
notification authority.

### IHiS Cyber Security Governance Director and healthcare Sector Lead

The CSG Director and Sector Lead point of contact owns the bounded
classification and CSA-reporting judgment. The record supports changing
assessment as information improves and preserves immediate qualified
reporting, further verification, and bounded executive briefing as explicit
alternatives. The concurrent MOH appointment is an authority boundary, not a
separate participant or a source of shared government knowledge.

### IHiS Chief Executive Officer

The IHiS CEO owns executive review, reporting direction, and investigation-
lead assignment rather than Sector Lead classification. The model preserves
staged problem framing under a compressed account. Bruce Liang's concurrent
MOH CIO appointment does not enlarge the IHiS office's modeled authority.

### SingHealth Deputy Group Chief Executive Officer

The Deputy GCEO separately received the 9 July account and later led patient
outreach. The model therefore preserves early internal-routing choice,
anticipatory resource mobilization, and evidence-responsive outreach planning
without attributing all later management deliberation to the officeholder's
private belief.

### SingHealth Group Chief Executive Officer

The GCEO first received the incident on 10 July and independently directed MOH
reporting, later consulted on outreach, and proposed the primary communication
channel. A separate office model retains that information boundary without
turning SingHealth senior management into a shared mind.

## Evidence limits

This source set is sufficient for the bounded R1 and R2 participant models and
their shared detection, classification, reporting, and notification account.
It does not identify numerical mechanism weights, complete population
composition, fixed historical policies, or behavior for other roster roles.
New evidence is needed only if a material participant boundary, authority
claim, or mechanism changes.
