# Integrated Health Information Systems (IHiS) Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.0616.agent.ihis_system_operator.v1` |
| Actor ID | `ihis_system_operator` |
| Benchmark | H2EPR-0616, June 2018–March 2019 represented response boundary; affected-record cohort dates begin May 2015 |
| Representation | agent; system-operator verification, review and remediation-program interface |
| Source ID | `P_3` |
| Primary choices | Verify the represented breach scope, initiate the directed security review, and announce a bounded improvement program after findings and penalty notice. |
| Cadence | Decide from each sealed coordinate prestate within inclusive availability windows. |
| State authority | Intent producer only; environment admission and reducer own results. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

P_3 consolidates the contracted system operator across six appearances. Historical control failures, failure to detect, cooperation, and receipt of a fine are environment context/results; only supported organizational records are selectable.

IHiS cannot author SingHealth's detection or acceptance, government disclosure, COI findings, PDPC orders, actual fine payment, completed control deployment, or cybersecurity effectiveness. The parent fixes no calibrated utility, personality,
risk score or backend timing parameter. It owns represented meaning and authority;
Rule configuration remains a separate replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E1/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S1/E2/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S2/E3/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E5/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S3/E6/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |
| draft_epg:S4/E7/P_3 | Participant appearance and actor-local action rows | Draft content; not independently reconciled history |

Frozen anchors: SRC001, SRC008 and SRC010. Frozen reporting supports inadequate controls and a directed review, but does not expose internal forensic microsteps or prove completed post-penalty implementation. Verification and program actions are qualified organizational records.
The Source Profile seals all three permitted inputs. Actor-local rows and coherent
narrative own capability; malformed relation or transaction endpoints do not.
Selected receipt dependencies are explicit construction assumptions.

## 4. Event role, relationships, and authority

This agent may verify the represented breach scope, initiate the directed security review, and announce a bounded improvement program after findings and penalty notice. It cannot act as another producer,
recipient, regulator, institution or environment process. A message reports a
statement or request; it never transfers the sender's state authority.

A scope summary does not disclose the breach publicly. A review announcement does not cure a vulnerability, and a penalty notice does not implement a security control.

The scope pilot admits qualified and unresolved internal assessment reports.
The environment records the selected report in IHiS-private state. It does not
perform forensic analysis or certify the statement as true. The qualified Rule
selection follows the exposed S2/E3/P_3 account; unresolved is an explicit
structural alternative used to test the information contract.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate | Unrecorded is valid; missing contract fails. |
| Own scope assessment | `ihis_system_operator.scope_verification`, actor-private sealed prestate | Unrecorded permits the initial report; another actor cannot inspect it. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; incoming pending private content is invisible. |
| Received and own-action memory | Runtime-derived actual history | Reuse delivered information; rejected attempts are not completions. |

Without delivered detection, no scope-verification row activates. Without the ministry direction or later penalty notice, the corresponding review/remediation row remains open. Memory persists across this bounded event without a
calibrated expiry. Accepted rows complete once; rejected rows reopen only after
changed visible information. Clock advance or repeated rejection alone is not
new evidence. Future stage descriptions, Reference content and generated opaque
identifiers are never participant observations.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `verify_breach_scope` | policy-selected detection receipt and an unrecorded own assessment | Submit a qualified or unresolved internal assessment; no technical forensic reconstruction. |
| `initiate_directed_security_review` | known `security_review_direction` from `singapore_ministry_of_health` | Record initiation of the directed review without treating recommendations as implemented controls. |
| `announce_security_improvement_program` | known `ihis_penalty_notice` from `personal_data_protection_commission`; `review.ihis_review` = `initiated` | Record an announced improvement program after review and penalty notice, not completed controls or effectiveness. |

`no_op` covers waiting, abstention, completed rows and closed windows. The current
Rule selects exposed bounded meanings; it is not a fitted preference model.
Broader alternatives require a reviewed semantic successor before backend work.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `verify_breach_scope` | `response` | `ihis_system_operator.scope_verification`: unrecorded → `qualified_scope_recorded` or `scope_unresolved`, from the admitted assessment parameter |
| `initiate_directed_security_review` | `review` | `review.ihis_review`: unrecorded → `initiated` |
| `announce_security_improvement_program` | `remediation` | `remediation.ihis_program`: unrecorded → `announced` |

The environment checks actor, target, parameters and preconditions against the
same sealed state. Rejection yields no delta. Coupled messages have independent
transport dispositions and do not prove action acceptance or recipient uptake.

Scope messages have typed status and scale. The ministry's shared disclosure
handler requires both a qualifying latest receipt and a qualified internal record.
A withdrawn statement cannot be replaced with an older positive receipt. The
one-shot assessment intent does not support repeated forensic revisions; a later
assessment cycle would require a separately reviewed lifecycle successor.

## 8. Configurable dimensions and uncertainty

| Construct | Owner | Behavioral use |
|---|---|---|
| Availability window | Rule configuration | Bounded waiting for supported information. |
| Priority | Rule configuration | Orders overlapping rows under one action per actor/tick. |
| Route latency | Shared configuration | Determines actual information availability. |
| Message payload | Backend configuration within this parent | Reports qualified content without granting effects. |

All are structural choices, not calibrated probabilities or historical timings.

## 9. Worked cases and contract falsification

- Normal: IHiS receives detection, sends a qualified scope summary, records the ministry-directed review, and later announces an improvement program after its penalty notice.
- Missing information: Without delivered detection, no scope-verification row activates. Without the ministry direction or later penalty notice, the corresponding review/remediation row remains open.
- Pending: Outgoing content is unknown to a recipient until transport admits delivery. The sender sees only its own pending lifecycle.
- Authority/adverse case: A scope summary does not disclose the breach publicly. A review announcement does not cure a vulnerability, and a penalty notice does not implement a security control.
- Perturbation: Withholding the scope summary blocks the dependent disclosure chain; delaying COI findings prevents timely penalties and the final remediation record.

A foreign-actor write, premature generated result or undeclared environment
effect fails this contract. Rule-only windows and receipt guards constrain the
selected policy; mandatory shared prerequisites require an explicit handler
projection. Event-specific capability names are vocabulary-exposed, as declared
in the Scenario, and do not establish historically prefix-clean observation.

## 10. Limitations and successor route

IHiS cannot author SingHealth's detection or acceptance, government disclosure, COI findings, PDPC orders, actual fine payment, completed control deployment, or cybersecurity effectiveness. Frozen reporting supports inadequate controls and a directed review, but does not expose internal forensic microsteps or prove completed post-penalty implementation. Verification and program actions are qualified organizational records.
Changing owner, choice, information prerequisite or record meaning revises this
parent and all dependent identities. Timing-only choices route to configuration.
The complete Draft anchors appear above; there is no external retrieval,
historical-fit, held-out or scientific-validity claim.
