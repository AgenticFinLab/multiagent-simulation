# H2EPR-0616 event-frame evidence

This record supports only the H2EPR-0616 event frame. It combines the small
source register, claim ledger, unresolved questions, and evidence-use review
needed to set the event interval and causal responsibility map. Participant
behavior and Agent Definition research require later, role-specific work.

- Status: `REVIEW_CANDIDATE_FOR_EVENT_FRAMING`
- Research date: `2026-08-24`
- Construction exposure: `FULL_DRAFT_EXPOSED`
- External boundary: public Singapore government, official inquiry, and
  regulatory sources; no paid, private, credentialed, Reference, draft EPG,
  held-out, or evaluation material
- Archive policy: stable public locators only; no external source bytes were
  added to the repository

The 12 records in the local frozen evidence bundle were consulted for source
discovery but not adopted as claim authority. They include duplicated and
incident-irrelevant material and rely heavily on secondary reporting.

## Adopted sources

### `0616-FR-S01` — Committee of Inquiry public report

- Citation: Committee of Inquiry. *Public Report into the Cyber Attack on
  Singapore Health Services Private Limited's Patient Database on or around
  27 June 2018*. 10 January 2019.
- Class: official retrospective investigation based on testimony, documents,
  forensic work, and expert evidence.
- Public file: https://file.go.gov.sg/singhealthcoi.pdf
- Custody and retrieval: official government PDF, accessed 24 August 2026.
- Adopted locations: Executive Summary paragraphs 1–12; Part II paragraphs
  23–40; Part III paragraphs 139–209; Part IV paragraphs 288–593; Part V
  incident response and public communication sections; Part VI key findings.
- Adopted for: event interval, system and institutional ownership, technical
  and organizational response interfaces, participant-time signals,
  escalation, containment, notification, and bounded causal findings.
- Limitations: retrospective and outcome-exposed; the public edition omits
  protected national-security and patient-confidentiality material. A later
  inquiry finding is not automatically an observation available to an event
  participant.

### `0616-FR-S02` — PDPC grounds of decision

- Citation: Personal Data Protection Commission. *Singapore Health Services
  Pte. Ltd. & Ors.*, [2019] SGPDPC 3, Case No. DP-1807-B2435. Decision dated
  14 January 2019 and published 15 January 2019.
- Class: official regulatory decision based on the organisations'
  representations and relevant findings in the COI report.
- Public file: https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/Commissions-Decisions/Grounds-of-Decision---SingHealth-IHiS---150119.pdf
- Custody and retrieval: official PDPC PDF, accessed 24 August 2026.
- Adopted locations: paragraphs 54–58, 89–97, and the corresponding findings
  on SingHealth and IHiS responsibilities.
- Adopted for: separating SingHealth's overall and supervisory responsibility
  from IHiS' direct operational and data-intermediary responsibilities.
- Limitations: a later legal and regulatory determination, not participant-time
  evidence; it depends partly on the COI record and is not independent
  corroboration for every chronology claim.

### `0616-FR-S03` — 20 July joint public announcement

- Citation: Ministry of Communications and Information and Ministry of
  Health. “SingHealth's IT System Target of Cyberattack.” 20 July 2018.
- Class: official public statement issued on the day of public notification.
- Public page: https://www.moh.gov.sg/newsroom/singhealth%27s-it-system-target-of-cyberattack/
- Custody and retrieval: official MOH page, accessed 24 August 2026.
- Adopted locations: paragraphs 2–11.
- Adopted for: information made public on 20 July, then-current chronology,
  initial containment account, institutional descriptions, and the announced
  patient-notification process.
- Limitations: issued while investigation was continuing; later COI findings
  control where the two differ in detail or completeness.

### `0616-FR-S04` — 6 August ministerial statement

- Citation: Ministry of Health. “Cyberattack on SingHealth's IT System,”
  statement by the Minister for Health. 6 August 2018.
- Class: official parliamentary account produced shortly after the public
  announcement.
- Public page: https://www.moh.gov.sg/newsroom/cyberattack-on-singhealth%27s-it-system/
- Custody and retrieval: official MOH page, accessed 24 August 2026.
- Adopted locations: paragraphs 4–11 and the response sections that follow.
- Adopted for: public explanation of detection, escalation, inter-agency
  response, containment, announcement timing, and patient notification.
- Limitations: retrospective, public-facing, and based on the investigation as
  understood at that date; the later COI report supplies the more complete
  event reconstruction.

## Event-frame claims

`Direct` below means that an adopted source states or records the proposition
for the stated scope. `Bounded inference` is a model consequence, not a claim
that the source observed a participant policy. All claims are
`FULL_DRAFT_EXPOSED` and unavailable for an independent held-out claim.

| ID | Atomic proposition and event time | Support and relation | Participant availability | Status and allowed use | Modeling consequence |
|---|---|---|---|---|---|
| `0616-FR-C01` | The earliest evidence of compromise dates to about 23 August 2017; the COI treated the attack as continuing through 20 July 2018. | `0616-FR-S01`, para. 139, direct retrospective finding. | The outer interval was reconstructed later; no participant receives it as a completed event-time fact. | `DIRECT / EVENT_BOUNDARY`. | Use 23 August 2017 as the analytic start and preserve uncertainty about the exact initial-compromise moment. |
| `0616-FR-C02` | SCM database querying and patient-data exfiltration ran from 27 June through 4 July 2018. | `0616-FR-S01`, paras. 139 and 200–204; compatible public account in `0616-FR-S03`. | Individual participants knew only the queries, alerts, logs, and communications available to their roles. | `DIRECT / CHRONOLOGY_AND_SCENARIO`. | Separate database access, query execution, returned data, copying, and external transfer. |
| `0616-FR-C03` | IHiS staff stopped the observed database copying on 4 July; later malicious activity was seen on 18 and 19 July, and no further suspicious activity was observed after internet surfing separation began on 20 July. | `0616-FR-S01`, paras. 204–209 and response findings; `0616-FR-S04`, paras. 6 and 10, compatible official account. | Local controls and observed alerts were role-bound; later assurance about no further activity was not known in advance. | `DIRECT / RESPONSE_AND_TERMINATION`. | Containment is a sequence of intents and observed results, not one successful action. |
| `0616-FR-C04` | The public announcement was made on 20 July 2018; SingHealth sent patient notifications from 20 through 23 July. | `0616-FR-S01`, public-communication findings; `0616-FR-S03`, para. 9; `0616-FR-S04`, paras. 10–11. | Public only after publication or message delivery; recipients do not see internal investigation state. | `DIRECT / NOTIFICATION_HORIZON`. | End the core incident at the 20 July announcement and retain notification delivery through 23 July as a bounded observation horizon. |
| `0616-FR-C05` | SingHealth legally owned the SCM system and was its Critical Information Infrastructure owner. | `0616-FR-S01`, Part II paras. 30–33, direct institutional finding. | Institutional authority; not a universal observation of every SingHealth employee. | `DIRECT / IDENTITY_AND_AUTHORITY`. | Retain a SingHealth governance/data-owner boundary distinct from technical operation. |
| `0616-FR-C06` | IHiS administered and operated SCM, implemented cybersecurity measures, and owned security incident response and reporting responsibilities. | `0616-FR-S01`, Executive Summary para. 3 and Part II paras. 34–40, direct institutional finding. | Responsibility was distributed across deployed teams and roles; whole-organisation knowledge cannot be assumed. | `DIRECT / IDENTITY_AUTHORITY_AND_ROSTER`. | Split technical administration, security response, and management escalation interfaces instead of creating one IHiS mind. |
| `0616-FR-C07` | IHiS was the central public-healthcare IT agency accountable to MOH, while its employees were deployed into healthcare clusters in role-specific positions. | `0616-FR-S01`, Part II paras. 34–40, direct institutional finding. | A role sees its assigned systems, communications, and authority rather than every MOH or IHiS fact. | `DIRECT / ORGANIZATIONAL_STRUCTURE`. | Preserve concurrent, deployed, and reporting relationships explicitly; organization names alone do not define Agents. |
| `0616-FR-C08` | SingHealth retained primary and supervisory responsibility for personal-data protection while IHiS held a more direct operational responsibility; one did not erase the responsibility of the other. | `0616-FR-S02`, paras. 54–58 and 89–97, direct regulatory finding. | Later legal determination; use for authority design, not as participant-time belief. | `DIRECT / AUTHORITY_AND_SCENARIO_BOUNDARY`. | Model separate governance and operational responsibilities, with no silent delegation of all SingHealth responsibility to IHiS. |
| `0616-FR-C09` | By the evening of 11 June, an IHiS administrator believed a local administrator password had been stolen and used for unauthorized access; passwords were changed, but the matter was not then reported to the Security Management Department. | `0616-FR-S01`, paras. 344–347, direct reconstruction. | Available to the administrator and nearby technical team through logs and investigation; not yet available to security management. | `DIRECT / PARTICIPANT_TIME_AND_ESCALATION`. | This is the first high-information internal decision point in the primary response window. |
| `0616-FR-C10` | On 12 June the Citrix team raised abnormal database access and suspicious artifacts to Security Management, but the communication did not clearly convey all significance and follow-up was incomplete. | `0616-FR-S01`, paras. 364–368, direct reconstruction and inquiry assessment. | Different recipients received different screenshots, explanations, and context. | `DIRECT_WITH_INQUIRY_ASSESSMENT / INFORMATION_ROUTE`. | Messages require sender, content, recipient, timing, and acknowledgement; delivery does not create shared understanding. |
| `0616-FR-C11` | By 26 June cumulative evidence was highly indicative of a security incident, yet the responsible incident-response interface did not escalate it; the COI treated this as the last major missed opportunity before data theft. | `0616-FR-S01`, paras. 452–458 and Part VI key findings, direct inquiry finding. | Relevant technical and security roles held different parts of the evidence; the later causal assessment was unavailable at event time. | `DIRECT_FINDING / ESCALATION_AND_FALSIFIER`. | Preserve incomplete information integration and an explicit escalate/defer choice; do not script the historical failure. |
| `0616-FR-C12` | On 4 July an application-team analyst investigated monitoring alerts, identified unusual queries, and IHiS teams introduced controls that stopped further observed database copying. | `0616-FR-S01`, paras. 465–510 and 204, direct reconstruction. | Alerts and query information were initially local to the analyst and collaborating technical teams. | `DIRECT / DETECTION_AND_LOCAL_RESPONSE`. | Detection, interpretation, local mitigation, security classification, and management escalation are distinct transitions. |
| `0616-FR-C13` | On 9 July the matter reached IHiS senior management with the then-incorrect understanding that the unusual queries had returned no records; the next-day meeting was to decide whether MOH and CSA should be informed. | `0616-FR-S01`, paras. 560–566, direct reconstruction. | Senior managers received a compressed and partly incorrect account, not the complete logs or later result. | `DIRECT / INFORMATION_QUALITY_AND_ESCALATION`. | Information content and uncertainty must travel with escalation; senior authority does not imply full information. |
| `0616-FR-C14` | On 10 July the evidence that queries returned data changed the assessed severity; IHiS classified the matter as Category 1 and notified SingHealth management, MOH, and CSA, with a formal MOH incident report that evening. | `0616-FR-S01`, paras. 584–592; compatible summary in `0616-FR-S03` and `0616-FR-S04`. | Each body became informed through a specific call, email, hotline, meeting, or report during 10 July. | `DIRECT / CLASSIFICATION_AND_CROSS_INSTITUTION_ROUTE`. | Keep classification, notification, inter-agency coordination, and formal reporting as separate acts and deliveries. |
| `0616-FR-C15` | After 10 July, IHiS, SingHealth, MOH, MCI, and CSA performed distinct but coordinated investigation, containment, public-communication, and patient-outreach work. | `0616-FR-S01`, Part V; `0616-FR-S04`, paras. 8–11, direct official accounts. | Teams received only routed updates needed for their functions; the public learned through later announcement and messages. | `DIRECT / RESPONSE_OWNERSHIP`. | Model a routed inter-agency process rather than one government actor with shared state and authority. |
| `0616-FR-C16` | The COI found both vigilant technical detection and material failures in cybersecurity understanding, incident classification, and timely escalation across particular response roles. | `0616-FR-S01`, Part VI key findings 1–2, direct inquiry findings. | The evaluative synthesis is retrospective; event-time roles had only their local observations and interpretations. | `DIRECT_RETROSPECTIVE_FINDING / REPRESENTATION_AND_FALSIFICATION`. | The roles are causally distinct, but later behavior research must recover mechanisms and alternatives rather than turn findings into fixed failure policies. |

## Unresolved questions and limits

| Question | Verdict | Required treatment |
|---|---|---|
| Exact initial-compromise moment and complete threat-actor decision process | `BOUNDED_UNRESOLVED` | Use about 23 August 2017 as the earliest evidenced compromise and retain the threat actor as a representation gate; do not invent identity, objective, or perfect observability. |
| Counterfactual effect of each missed escalation | `BOUNDED_UNRESOLVED` | The COI supports prevent-or-mitigate relevance, not a unique quantitative outcome. Use alternatives or falsifiers, not deterministic outcome reversal. |
| Individual versus role-interface representation for technical administrators | `OWNER_DECISION_REQUIRED_AFTER_BEHAVIOR_RESEARCH` | Preserve heterogeneous observations and local actions; do not create one collective technical-staff Agent. |
| SIRM and Cluster ISO representation | `OWNER_DECISION_REQUIRED_AFTER_BEHAVIOR_RESEARCH` | Keep separate gates because they had distinct assigned responsibility, information, and response failures. |
| IHiS senior management and SingHealth management representation | `OWNER_DECISION_REQUIRED_AFTER_BEHAVIOR_RESEARCH` | Preserve distinct authority and notification routes; admit Agents only where autonomous choice is necessary for the primary question. |
| MOH, MCI, and CSA after 10 July | `RESOLVED_AS_ROUTED_INSTITUTIONAL_PROCESS_WITH_REPRESENTATION_GATES` | Keep containment, classification, communication, and public-notification authority distinct; open an Agent gate only for a material choice the scenario cannot own. |
| Affected patients | `RESOLVED_AS_AFFECTED_COHORT_FOR_CURRENT_QUESTION` | Retain exposure and delivered notification without a patient behavior model; reopen only if patient choice enters a revised question. |
| Post-23 July inquiry, liability, penalties, and reforms | `RESOLVED_AS_RETROSPECTIVE_EVIDENCE_OR_EXCLUDED_AFTERMATH` | They may constrain interpretation and authority but are not runtime-visible in the primary incident. |

## Evidence closure

```text
research_question=H2EPR-0616 event chronology, responsibility, detection,
  escalation, containment, and notification boundaries
authorized_scope=PUBLIC_OFFICIAL_SINGAPORE_SOURCES_FOR_EVENT_FRAMING_ONLY
sources_considered=12_LOCAL_DISCOVERY_RECORDS_PLUS_4_OFFICIAL_EXTERNAL_SOURCES
sources_adopted=4_OFFICIAL_EXTERNAL_SOURCES
claim_families=TIME_IDENTITY_AUTHORITY_INFORMATION_ACTION_RESULT_INTERPRETATION
temporal_boundary=2017-08-23_APPROX_TO_2018-07-20_CORE_WITH_NOTIFICATION_TO_2018-07-23
exposure_boundary=FULL_DRAFT_EXPOSED_NOT_CLEAN_BUILDER
verdict=RESOLVED_FOR_EVENT_FRAMING_WITH_BOUNDED_REPRESENTATION_GATES
supported_for=OUTER_INTERVAL_PRIMARY_RESPONSE_WINDOW_CAUSAL_TRANSITIONS_INSTITUTIONAL_RESPONSIBILITIES_AND_ROSTER_GATES
not_supported_for=AGENT_BEHAVIOR_POLICY_NUMERICAL_PARAMETERS_ATTACKER_IDENTITY_COUNTERFACTUAL_MAGNITUDES_HISTORICAL_OR_SCIENTIFIC_VALIDITY
unresolved_alternatives=THREAT_ACTOR_FORM_TECHNICAL_STAFF_GRANULARITY_SIRM_CLUSTER_ISO_AND_MANAGEMENT_AGENT_ADMISSION
modeling_consequence=PROCEED_TO_OWNER_REVIEW_OF_EVENT_FRAME_NOT_PARTICIPANT_PRODUCTION
next_evidence_if_any=ROLE_SPECIFIC_BEHAVIOR_RESEARCH_ONLY_AFTER_FRAME_ACCEPTANCE_AND_BATCH_AUTHORIZATION
```

**Evidence disposition: Resolved for event framing with bounded
representation gates.** The source set is sufficient to propose the event
interval, causal transitions, institutional boundaries, and roster questions.
It does not authorize or supply participant behavior, Agent Definitions,
runtime observations, or validity claims.
