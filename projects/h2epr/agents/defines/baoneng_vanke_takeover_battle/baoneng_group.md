# Baoneng Group Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.1031.agent.baoneng_group.v1` |
| Agent ID | `baoneng_group` |
| Benchmark | H2EPR-1031, July 2015–June 2017 |
| Interface | affiliated acquirer disclosure and shareholder-proposal interface |
| Source ID | `P_1` |
| Primary choices | Disclose two successive stake reports, oppose the proposed asset issue, request management removal, and reaffirm its position during discussion. |
| Cadence | Decide from each sealed coordinate prestate within declared availability windows; no continuous-time interpretation. |
| State authority | Intent producer only; environment admission and the authoritative reducer own records. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

Its opposition is a position statement. It neither cancels the restructuring by itself nor removes directors. The two late Draft hold-stake actions are passive status continuations, not two new purchases.

Affiliate-level leverage, funding legality, securities settlement, sellers, board control and a verified voting majority are outside this interface. There is no calibrated utility, personality score or immutable
investment-risk parameter in this Definition. It constrains the represented
choices; the selected Rule settings remain a separate, replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E1/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S1/E2/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S2/E4/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S2/E5/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S3/E6/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S3/E7/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S3/E8/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S4/E9/P_1 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S4/E10/P_1 | Participant appearance and local actions | Draft content, not independently verified history |

Frozen evidence anchors: SRC001, SRC004, SRC002, SRC005, SRC010. Several relation/transaction endpoints incorrectly make Baoneng the Metro agreement party or Evergrande seller; these do not confer authority.
The Source Profile seals all three permitted files. Relationships are interpreted
from actor-local actions and narrative consistency, not corrupt endpoint IDs.
The communication dependencies below are explicit construction assumptions.

## 4. Event role, relationships, and authority

This Agent may disclose two successive stake reports, oppose the proposed asset issue, request management removal, and reaffirm its position during discussion. Each intent below is restricted to this actor;
none lets it act as another shareholder, manager, regulator, exchange or voter.
Messages communicate statements and requests. Their recipients retain their own
authority. Holdings mentioned in disclosures are not spendable balances.

Vanke can record a board rejection of the removal request. Baoneng must not treat delivery of its request as a granted vote.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate, before decisions | Missing contract fails; unrecorded state remains a valid observation. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; another actor's pending private message is invisible. |
| Received and own-action memory | Runtime-derived history through the previous disposition/current delivery | Reuse actually received information; rejected attempts are not completions. |

If the proposal message is absent, the selected Rule waits on opposition and the removal request; the earlier stake disclosures remain separate choices. Memory persists over this bounded event window; no calibrated
age cutoff is selected. New visible information may reopen a rejected row. Clock
advance or its own rejection alone cannot cause an identical retry. Accepted
rows are complete. No future stage text, later nominee outcome, hidden ballot,
Reference content or generated opaque identifier is decision evidence.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `disclose_initial_stake` | available source interval and own record not yet made | Record the initial shareholding disclosure, without settling any shares. |
| `disclose_increased_stake` | stake_disclosures.baoneng_initial = reported_22_45_percent | Record the later affiliate-aggregated shareholding disclosure. |
| `oppose_asset_proposal` | known metro_asset_proposal from vanke_corporate_governance; proposal.corporate_announcement = recorded | Record Baoneng opposition, not a computed shareholder veto. |
| `submit_removal_request` | positions.baoneng_opposition = recorded | Request removal of management; the board response remains separate. |
| `reaffirm_opposition` | known discussion_invitation from vanke_corporate_governance; positions.baoneng_opposition = recorded | Reaffirm an earlier opposed position without creating a new purchase. |

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
| `disclose_initial_stake` | `stake_disclosures` | `stake_disclosures.baoneng_initial`: unrecorded → reported_22_45_percent |
| `disclose_increased_stake` | `stake_disclosures` | `stake_disclosures.baoneng_increase`: unrecorded → reported_24_3_percent |
| `oppose_asset_proposal` | `positions` | `positions.baoneng_opposition`: unrecorded → recorded |
| `submit_removal_request` | `governance` | `governance.removal_request`: unrecorded → submitted |
| `reaffirm_opposition` | `negotiation` | `negotiation.baoneng_position`: unrecorded → opposition_reaffirmed |

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

- Normal: After the Metro proposal is actually known, Baoneng may record opposition and later submit a removal request. A request is not a successful dismissal.
- Missing information: If the proposal message is absent, the selected Rule waits on opposition and the removal request; the earlier stake disclosures remain separate choices.
- Pending: Its outgoing statement remains unknown to a recipient until delivery. The sender can observe its own pending lifecycle but cannot mark it delivered.
- Authority or adverse result: Vanke can record a board rejection of the removal request. Baoneng must not treat delivery of its request as a granted vote.
- Perturbation: Delaying the proposal changes the earliest opposition/request ticks and can leave the request absent at the bounded horizon.

Premature action before the stated information condition contradicts this Rule
realization. A foreign actor writing the record, future nominee knowledge in an
early observation, or a notice generating securities/election effects contradicts
the shared semantic contract and must fail review or admission.

## 10. Limitations and source anchors

Affiliate-level leverage, funding legality, securities settlement, sellers, board control and a verified voting majority are outside this interface. Several relation/transaction endpoints incorrectly make Baoneng the Metro agreement party or Evergrande seller; these do not confer authority.
Any change to the represented owner, admissible choice, information prerequisite
or record meaning requires revising this parent and rebuilding dependent
registries/configuration/package identities. Timing-only choices remain in
configuration within these bounds. Source anchors are the complete appearances
above and the named frozen records, available only through the sealed Source
Profile. No external retrieval, historical fit or scientific validity is claimed.
