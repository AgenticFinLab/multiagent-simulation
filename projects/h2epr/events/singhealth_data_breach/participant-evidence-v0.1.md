# H2EPR-0616 R1 participant evidence

This record supports the first H2EPR-0616 participant batch: technical
administration and line security staff, the Security Incident Response Manager
(SIRM), and the Cluster Information Security Officer for SingHealth (Cluster
ISO). It extends the accepted event frame only for those representation and
behavior questions.

- Status: `ACCEPTED_R1_PARTICIPANT_EVIDENCE_WITH_EXPLICIT_ALTERNATIVES`
- Event: `H2EPR-0616`, SingHealth Data Breach
- Modeled interval: participant response from 18 January through 20 July 2018;
  acute response from 11 June
- Production profiles: technical role set `standard`; SIRM `deep`; Cluster ISO
  `standard`
- Construction exposure: `FULL_DRAFT_EXPOSED`
- External boundary: existing local copies of accepted public official sources;
  no new network, private, credentialed, paid, Reference, draft EPG, held-out,
  or evaluation material

## Evidence basis

The role study reuses one source already adopted by the
[event-frame evidence](frame-evidence-v0.1.md):

### `0616-FR-S01` — Committee of Inquiry public report

- Citation: Committee of Inquiry. *Public Report into the Cyber Attack on
  Singapore Health Services Private Limited's Patient Database on or around
  27 June 2018*. 10 January 2019.
- Public file: https://file.go.gov.sg/singhealthcoi.pdf
- Locations used here: paragraphs 68--76, 92--120, 302--327, 329--458, and
  465--593.
- Source relation: official retrospective investigation drawing on testimony,
  messages, documents, forensic work, and expert evidence.
- Use: assigned responsibilities, event-time messages and observations,
  reconstructed actions, bounded participant explanations, representation,
  decision situations, mechanism alternatives, and falsifiers.
- Limitation: the report is outcome-exposed and retrospective. Committee
  judgments and later attack attribution are not participant-time observations
  and are not evidence of a general behavioral law.

The accepted Event Build Brief and frame claims provide scope and lineage, not
independent corroboration. The other three accepted official sources add no
role-specific detail needed for this batch and are not counted again merely to
increase the source total. The frozen 12-record bundle remains discovery-only.

## Participant claims

`Direct` below means the adopted source records the stated institutional fact,
message, action, or attributed explanation for the bounded use. `Retrospective`
marks a later inquiry assessment that may be used only as a falsifier or
construction warning.

| ID | Atomic proposition and event time | Support and relation | Participant availability | Status and allowed use | Withdrawal consequence |
|---|---|---|---|---|---|
| `0616-R1-C01` | The SIRM led and coordinated technical incident response, while the Cluster ISO owned communication and reporting duties and stood in the initial reporting chain; the SIRT joined security, infrastructure, and application roles. | `0616-FR-S01`, paras. 75--76 and 107--113, direct institutional account. | Assigned authority, not shared knowledge. | `DIRECT / REPRESENTATION_AND_AUTHORITY`. | Reopen both office-level gates and the shared routing model. |
| `0616-R1-C02` | Line technical staff had no written incident-reporting protocol; the SIRF was not widely communicated and the IR-SOP was shared only with limited security-management recipients. | Paras. 101--105 and 352--354, direct institutional finding. | The absence or limited delivery is a participant-time information constraint. | `DIRECT / INFORMATION_AND_HETEROGENEITY`. | Remove the reporting-knowledge mechanism and reassess scenario externalization. |
| `0616-R1-C03` | Between 18 and 22 January, a security engineer investigated malware and callbacks, applied local controls, and shared findings, while the SIRM treated the matter as contained common malware and did not escalate it. | Paras. 302--327, direct reconstruction. | The engineer and addressed recipients saw particular alerts and messages; later attacker attribution and missed-opportunity findings were unavailable. | `DIRECT_RECONSTRUCTION / TECHNICAL_AND_SIRM_DECISION_SITUATION`. | Remove the January situation from the technical and SIRM products. |
| `0616-R1-C04` | From 11 to 13 June, database and Citrix staff independently observed unauthorized activity, changed credentials, gathered artifacts, and routed only parts of the emerging account to Security Management. | Paras. 329--386, direct reconstruction. | Each team held local observations; email delivery did not create common interpretation. | `DIRECT_RECONSTRUCTION / LOCAL_CHOICE_AND_INFORMATION_ROUTE`. | Narrow the technical representation or remove the multi-route interface. |
| `0616-R1-C05` | Material facts remained compartmentalized: the Citrix team initially restricted distribution of its investigation, and the security engineer did not learn of the S.A. account until 26 June. | Paras. 387--398, direct reconstruction. | Available only to named local recipients until later delivery. | `DIRECT_RECONSTRUCTION / INFORMATION_FRAGMENTATION`. | Remove the fragmentation mechanism and reconsider a smaller role set. |
| `0616-R1-C06` | From 4 through 7 July, technical staff independently investigated or stopped suspicious queries, sought logs or advice, terminated sessions, bypassed normal change procedure for a blocking script, and altered account or network controls. | Paras. 465--509 and 516--540, direct reconstruction. | Choices and observations remain with the involved application, database, Citrix, directory, and security units; effects remain scenario-owned. | `DIRECT_RECONSTRUCTION / POPULATION_CHOICE_REPERTOIRE`. | Externalize these operations to scenario and close the technical participant row. |
| `0616-R1-C07` | The SIRM office was unstaffed during the manager's June absence, no covering officer was designated, and neither the SIRM nor Cluster ISO activated the SIRT. | Paras. 412--416, direct reconstruction with institutional assessment. | Absence and activation state were event-time organizational facts; the later adequacy judgment was unavailable. | `DIRECT_WITH_ASSESSMENT / CAPACITY_AND_DELEGATION`. | Remove delegation and response-capacity state from the SIRM model. |
| `0616-R1-C08` | Across January, June, and early July, the SIRM could investigate, coordinate, isolate, seek help, or escalate, but applied a high confirmation standard; by 6 July the manager also described escalation-update pressure as a reason for delay. | Paras. 313--327, 420--458, 483--496, and 541--544, reconstructed actions plus attributed explanation. | Received messages and the manager's own assessments are bounded to their dates. Later causal condemnation is excluded from participant state. | `DIRECT_RECONSTRUCTION_AND_ATTRIBUTED_EXPLANATION / SIRM_MECHANISM_ALTERNATIVES`. | Remove the confirmation-and-coordination hypothesis; retain only institutional duties or reopen representation. |
| `0616-R1-C09` | The Cluster ISO had an independent reporting and accountability role, received or viewed June messages, asked questions, but did not confirm response state, activate the team, instruct the investigation, or escalate. | Paras. 75--76, 108, 367--386, and 409--416, direct reconstruction with institutional finding. | Only delivered messages, meetings, and assigned duties are available; the ISO does not inherit all SIRM or team knowledge. | `DIRECT_WITH_FINDING / ISO_AUTHORITY_AND_DECISION_SITUATION`. | Merge the ISO into routing context or reopen the separate Agent row. |
| `0616-R1-C10` | On 4 and 5 July, the Cluster ISO joined review and meetings but treated the evidence as an unconfirmed potential breach, assumed investigation should precede escalation, and did not integrate unauthorized access with suspicious queries. | Paras. 488--499 and 516--522, attributed assessment and direct reconstruction. | The interpretation is bounded to the information described at those times. | `DIRECT_RECONSTRUCTION_AND_ATTRIBUTED_INTERPRETATION / ISO_MECHANISM_ALTERNATIVES`. | Remove the July ISO commitment and reassess whether independent discretion remains material. |
| `0616-R1-C11` | On 9 July, cross-team consolidation assembled previously separated facts; senior escalation followed despite incomplete and partly incorrect information. | Paras. 548--570, direct reconstruction. | Participants received only the meeting account and routed reports; later query verification was unavailable until 10 July. | `DIRECT_RECONSTRUCTION / INFORMATION_INTEGRATION_FALSIFIER`. | Remove the information-integration contrast used to test all three products. |
| `0616-R1-C12` | The inquiry later found strong front-line initiative alongside inadequate classification, coordination, and escalation by particular response roles. | Paras. 510--515, 544--546, and 593, retrospective finding. | Unavailable during the event. | `RETROSPECTIVE / FALSIFIER_AND_CONSTRUCTION_WARNING_ONLY`. | Remove the exposed-outcome falsifier; no participant boundary otherwise changes. |

## Evidence-to-model findings

### Technical role set

The evidence supports role-typed choice units in application and database
operations, Citrix or infrastructure administration, and security engineering
or CERT. They had different observations and local control authority. A
Population Model is preferable to either one collective technical-staff Agent
or named biographies for every employee.

The bounded mechanisms are local problem ownership under incomplete reporting
guidance and fragmented cross-team information integration. Workload,
expertise, and message quality remain competing explanations. The evidence is
`RESOLVED_FOR_STATED_USE` for a standard Population Model, not for weights,
population composition, numerical thresholds, or a universal cybersecurity
response policy.

### Security Incident Response Manager

The SIRM office had a defensible decision interface for investigation
coordination, incident-response activation, containment direction, outside
assistance, and escalation. The evidence supports explicit alternatives among
a high confirmation standard, incomplete information, limited forensic
capacity, office availability, escalation burden, and false-alarm concern.

The evidence is `READY_WITH_EXPLICIT_ALTERNATIVES` for a deep office-level
Agent Definition. It does not select one explanation, authorize a precise
threshold, or make the historical delay mandatory.

### Cluster Information Security Officer

The Cluster ISO had a distinct communication, reporting, accountability, and
independent escalation interface. Treating the role as a SIRM proxy would erase
a causally material route by which incomplete information could be queried,
coordinated, or escalated.

The evidence is `READY_WITH_EXPLICIT_ALTERNATIVES` for a standard office-level
Agent Definition. Reliance on technical investigation, incomplete message
content, limited comprehension, availability, and role ambiguity remain
separate possible explanations.

## Evidence closure

```text
research_question=H2EPR_0616_R1_REPRESENTATION_AND_ROLE_BEHAVIOR
authorized_scope=EXISTING_LOCAL_OFFICIAL_ARCHIVE_AND_ACCEPTED_FRAME
sources_considered=FOUR_ACCEPTED_OFFICIAL_SOURCES
sources_adopted=ONE_ROLE_RELEVANT_OFFICIAL_INQUIRY_SOURCE
claim_families=REPRESENTATION_AUTHORITY_INFORMATION_ACTION_MECHANISM_FALSIFIER
new_claims=12
temporal_boundary=2018_01_18_TO_2018_07_20_WITH_ACUTE_WINDOW_FROM_2018_06_11
exposure_boundary=FULL_DRAFT_EXPOSED_NOT_CLEAN_BUILDER
verdict=RESOLVED_FOR_THREE_ACCEPTED_R1_PRODUCTS_WITH_EXPLICIT_ALTERNATIVES
supported_for=ROLE_BOUNDARIES_PARTICIPANT_TIME_INFORMATION_DECISION_SITUATIONS_INTENT_REPERTOIRES_AND_FALSIFIERS
not_supported_for=GENERAL_BEHAVIORAL_LAW_NUMERICAL_PARAMETERS_FIXED_HISTORICAL_POLICY_RUNTIME_VALIDITY_OR_OTHER_ROLES
unresolved_alternatives=SIRM_AND_CLUSTER_ISO_MECHANISM_WEIGHTS_AND_TECHNICAL_UNIT_COMPOSITION
modeling_consequence=PRESERVE_SET_VALUED_BEHAVIOR_INFORMATION_ISOLATION_AND_SCENARIO_OWNED_RESULTS
next_evidence_if_any=NONE_FOR_CURRENT_PRODUCTS_REOPEN_ONLY_IF_A_MATERIAL_BOUNDARY_OR_CLAIM_CHANGES
```

**Evidence disposition: Accepted for the three R1 participant products with
explicit mechanism alternatives.**
This record supplies no executable policy, event schedule, mapping, runtime
value, historical validation, or scientific validation.
