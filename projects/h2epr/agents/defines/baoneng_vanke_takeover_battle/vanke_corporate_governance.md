# Vanke corporate-governance interface Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.1031.agent.vanke_corporate_governance.v1` |
| Agent ID | `vanke_corporate_governance` |
| Benchmark | H2EPR-1031, July 2015–June 2017 |
| Interface | issuer disclosures and the separately attributed corporate board-response record |
| Source ID | `P_2` |
| Primary choices | Issue suspension/resumption notices, record the conditional LOI and Metro proposal, record the board response, disclose operating impacts, open discussion, register nominations and schedule a meeting. |
| Cadence | Decide from each sealed coordinate prestate within declared availability windows; no continuous-time interpretation. |
| State authority | Intent producer only; environment admission and the authoritative reducer own records. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

The source P_2 covers both issuer communication and a board rejection. This composite interface records an authorized board outcome; Wang and Yu cannot emit that intent. A study of management-versus-board disagreement would require separate parents and actors.

Individual director votes, exchange admission, asset/share clearing, automatic dilution and the June 30 election result are not modeled. There is no calibrated utility, personality score or immutable
investment-risk parameter in this Definition. It constrains the represented
choices; the selected Rule settings remain a separate, replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E1/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S1/E2/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S1/E3/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S2/E4/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S2/E5/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S3/E6/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S3/E7/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S3/E8/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S4/E9/P_2 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S4/E10/P_2 | Participant appearance and local actions | Draft content, not independently verified history |

Frozen evidence anchors: SRC001, SRC004, SRC002, SRC005, SRC010. E6 dates the board response differently from SRC002; the trace uses logical precedence, not a reconciled calendar date. The unidentified December LOI is not retrospectively assigned to Metro.
The Source Profile seals all three permitted files. Relationships are interpreted
from actor-local actions and narrative consistency, not corrupt endpoint IDs.
The communication dependencies below are explicit construction assumptions.

## 4. Event role, relationships, and authority

This Agent may issue suspension/resumption notices, record the conditional LOI and Metro proposal, record the board response, disclose operating impacts, open discussion, register nominations and schedule a meeting. Each intent below is restricted to this actor;
none lets it act as another shareholder, manager, regulator, exchange or voter.
Messages communicate statements and requests. Their recipients retain their own
authority. Holdings mentioned in disclosures are not spendable balances.

A manager attempting the board-response intent must be rejected. A valid resumption notice never grants exchange permission or updates a simulated stock price.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate, before decisions | Missing contract fails; unrecorded state remains a valid observation. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; another actor's pending private message is invisible. |
| Received and own-action memory | Runtime-derived history through the previous disposition/current delivery | Reuse actually received information; rejected attempts are not completions. |

Without the nominee proposal the Rule cannot register it or schedule the modeled nomination-linked meeting. Its earlier business disclosure and board response remain independently available. Memory persists over this bounded event window; no calibrated
age cutoff is selected. New visible information may reopen a rejected row. Clock
advance or its own rejection alone cannot cause an identical retry. Accepted
rows are complete. No future stage text, later nominee outcome, hidden ballot,
Reference content or generated opaque identifier is decision evidence.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `issue_suspension_notice` | known initial_stake_report from baoneng_group | Issue a corporate suspension/restructuring notice; exchange permission is not simulated. |
| `record_conditional_loi` | corporate.suspension_notice = recorded | Record a conditional LOI with an unidentified investor, not a completed issuance. |
| `announce_metro_proposal` | known metro_terms from shenzhen_metro; proposal.metro_terms = recorded | Announce the conditional Metro proposal; no dilution follows automatically. |
| `issue_resumption_notice` | corporate.suspension_notice = recorded | Record the issuer resumption notice, not exchange execution or stock-price change. |
| `record_board_rejection` | known removal_request from baoneng_group; governance.removal_request = submitted | Record the board-owned rejection of the removal request, not a manager action. |
| `open_resolution_discussion` | positions.baoneng_opposition = recorded | Open the represented discussion channel; invitation routing is a construction assumption. |
| `report_operating_impacts` | available source interval and own record not yet made | Record the exposed H1 operating-impact statement; the dispute is not a calibrated cause of profits. |
| `register_board_nominees` | known board_nominee_proposal from shenzhen_metro; nomination.metro_proposal = submitted | Register the received proposal for corporate processing. |
| `schedule_shareholder_meeting` | nomination.corporate_registration = recorded | Issue a notice for the June30 vote; the election result stays unobserved. |

`no_op` is allowed while information or prerequisites are missing, after a row
is completed, or outside its selected window. The current Rule selects the
exposed statements and bounded waiting; it is not a utility-maximizing takeover
strategy. The semantic contract does not supply invented support/opposition
alternatives where the dataset only supports the represented statement. Adding
such alternatives requires a reviewed semantic successor before backend tuning.
Selected earliest/latest ticks and priority belong to Rule configuration.

## 7. Intent and environment-result boundary

| Intent | Eligible target | Environment-owned record |
| --- | --- | --- |
| `issue_suspension_notice` | `corporate` | `corporate.suspension_notice`: unrecorded → recorded |
| `record_conditional_loi` | `corporate` | `corporate.conditional_loi`: unrecorded → recorded |
| `announce_metro_proposal` | `proposal` | `proposal.corporate_announcement`: unrecorded → recorded |
| `issue_resumption_notice` | `corporate` | `corporate.resumption_notice`: unrecorded → recorded |
| `record_board_rejection` | `governance` | `governance.board_response`: unrecorded → rejection_recorded |
| `open_resolution_discussion` | `negotiation` | `negotiation.invitation`: unrecorded → issued |
| `report_operating_impacts` | `corporate` | `corporate.operating_report`: unrecorded → recorded |
| `register_board_nominees` | `nomination` | `nomination.corporate_registration`: unrecorded → recorded |
| `schedule_shareholder_meeting` | `nomination` | `nomination.meeting_notice`: unrecorded → scheduled |

Every event intent carries exactly its declared `target_id`. The environment
checks actor, target, parameters and record preconditions against the same
sealed state; the reducer applies accepted deltas. A rejection is a terminal
attempt disposition, not an adverse historical outcome. Messages are separately
routed statements, not proof of delivery or acceptance of the coupled action.

## 8. Configurable dimensions and uncertainty

| Construct | Domain / owner | Behavioral use |
|---|---|---|
| Availability / waiting window | Inclusive logical coordinates, Rule configuration | Allows later information within the bounded process window. |
| Priority | Distinct ordered integers for overlapping own rows, Rule configuration | At most one action per actor per coordinate. |
| Message route latency | Positive logical ticks, shared configuration | Determines when information is actually knowable. |
| Statement payload | Declared content consistent with the parent, backend configuration | Describes a request/report without granting effects. |

These are structural choices, not fitted behavioral parameters. Share amounts,
leverage, prices, voting thresholds and calendar durations are not estimated.

## 9. Worked cases and contract falsification

- Normal: A received removal request permits the board-response record. A received nominee proposal permits registration; a later corporate meeting notice does not elect the nominees.
- Missing information: Without the nominee proposal the Rule cannot register it or schedule the modeled nomination-linked meeting. Its earlier business disclosure and board response remain independently available.
- Pending: Its outgoing statement remains unknown to a recipient until delivery. The sender can observe its own pending lifecycle but cannot mark it delivered.
- Authority or adverse result: A manager attempting the board-response intent must be rejected. A valid resumption notice never grants exchange permission or updates a simulated stock price.
- Perturbation: Withholding the Metro nominee message leaves nomination registration and the modeled meeting notice open without invalidating replay or publication.

Premature action before the stated information condition contradicts this Rule
realization. A foreign actor writing the record, future nominee knowledge in an
early observation, or a notice generating securities/election effects contradicts
the shared semantic contract and must fail review or admission.

## 10. Limitations and source anchors

Individual director votes, exchange admission, asset/share clearing, automatic dilution and the June 30 election result are not modeled. E6 dates the board response differently from SRC002; the trace uses logical precedence, not a reconciled calendar date. The unidentified December LOI is not retrospectively assigned to Metro.
Any change to the represented owner, admissible choice, information prerequisite
or record meaning requires revising this parent and rebuilding dependent
registries/configuration/package identities. Timing-only choices remain in
configuration within these bounds. Source anchors are the complete appearances
above and the named frozen records, available only through the sealed Source
Profile. No external retrieval, historical fit or scientific validity is claimed.
