# Shenzhen Metro Group Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.1031.agent.shenzhen_metro.v1` |
| Agent ID | `shenzhen_metro` |
| Benchmark | H2EPR-1031, July 2015–June 2017 |
| Interface | proposed investor, later acquisition-disclosure and nominee-proposal interface |
| Source ID | `P_6` |
| Primary choices | Offer mid-2016 restructuring terms, confirm participation, discuss a position, disclose a later stake acquisition and propose nominees. |
| Cadence | Decide from each sealed coordinate prestate within declared availability windows; no continuous-time interpretation. |
| State authority | Intent producer only; environment admission and the authoritative reducer own records. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

The mid-2016 proposal and mid-2017 disclosure are separate fields and actions. The later disclosure does not require the earlier proposal to have been accepted. The two June19 nominee actions are the same exposed proposal, emitted once.

The 2016 proposed swap is not treated as an executed 2017 swap; no unidentified seller, cash balance, share issuance or elected board is manufactured. There is no calibrated utility, personality score or immutable
investment-risk parameter in this Definition. It constrains the represented
choices; the selected Rule settings remain a separate, replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S2/E4/P_6 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S2/E5/P_6 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S3/E8/P_6 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S4/E9/P_6 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S4/E10/P_6 | Participant appearance and local actions | Draft content, not independently verified history |

Frozen evidence anchors: SRC002, SRC004, SRC010. SRC004 leaves the December investor unnamed; Metro first has executable terms in the mid-2016 window. E9/E10 conflates a proposed RMB45.6bn swap with later near-30% ownership and has corrupt transfer endpoints.
The Source Profile seals all three permitted files. Relationships are interpreted
from actor-local actions and narrative consistency, not corrupt endpoint IDs.
The communication dependencies below are explicit construction assumptions.

## 4. Event role, relationships, and authority

This Agent may offer mid-2016 restructuring terms, confirm participation, discuss a position, disclose a later stake acquisition and propose nominees. Each intent below is restricted to this actor;
none lets it act as another shareholder, manager, regulator, exchange or voter.
Messages communicate statements and requests. Their recipients retain their own
authority. Holdings mentioned in disclosures are not spendable balances.

A proposal cannot write another shareholder's position, Vanke's registration or an election result. A disclosure is a recorded claim, not market clearing.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate, before decisions | Missing contract fails; unrecorded state remains a valid observation. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; another actor's pending private message is invisible. |
| Received and own-action memory | Runtime-derived history through the previous disposition/current delivery | Reuse actually received information; rejected attempts are not completions. |

Missing Vanke proposal acknowledgement leaves the agreement statement open; it does not automatically prevent the later independently exposed acquisition disclosure. Memory persists over this bounded event window; no calibrated
age cutoff is selected. New visible information may reopen a rejected row. Clock
advance or its own rejection alone cannot cause an identical retry. Accepted
rows are complete. No future stage text, later nominee outcome, hidden ballot,
Reference content or generated opaque identifier is decision evidence.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `submit_restructuring_terms` | available source interval and own record not yet made | Submit the mid-2016 proposed asset-restructuring terms. |
| `confirm_proposal_participation` | known metro_asset_proposal from vanke_corporate_governance; proposal.corporate_announcement = recorded | Confirm participation in the proposal, without closing an asset transaction. |
| `submit_negotiation_position` | known discussion_invitation from vanke_corporate_governance | Record continuing negotiation participation; no consensus is inferred. |
| `disclose_metro_acquisition` | available source interval and own record not yet made | Record the later acquisition disclosure independently of the unexecuted 2016 swap. |
| `submit_board_nominees` | stake_disclosures.metro = reported_nearly_30_percent | Submit the single June19 nominee proposal; nominees are not elected. |

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
| `submit_restructuring_terms` | `proposal` | `proposal.metro_terms`: unrecorded → recorded |
| `confirm_proposal_participation` | `proposal` | `proposal.metro_agreement`: unrecorded → recorded |
| `submit_negotiation_position` | `negotiation` | `negotiation.metro_position`: unrecorded → recorded |
| `disclose_metro_acquisition` | `stake_disclosures` | `stake_disclosures.metro`: unrecorded → reported_nearly_30_percent |
| `submit_board_nominees` | `nomination` | `nomination.metro_proposal`: unrecorded → submitted |

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

- Normal: After its own acquisition disclosure, Metro may submit a nominee slate. Recipients must actually receive it before the selected registration or response Rules use it.
- Missing information: Missing Vanke proposal acknowledgement leaves the agreement statement open; it does not automatically prevent the later independently exposed acquisition disclosure.
- Pending: Its outgoing statement remains unknown to a recipient until delivery. The sender can observe its own pending lifecycle but cannot mark it delivered.
- Authority or adverse result: A proposal cannot write another shareholder's position, Vanke's registration or an election result. A disclosure is a recorded claim, not market clearing.
- Perturbation: Suppressing nominee delivery leaves the acquisition disclosure intact while downstream nomination-dependent choices remain open.

Premature action before the stated information condition contradicts this Rule
realization. A foreign actor writing the record, future nominee knowledge in an
early observation, or a notice generating securities/election effects contradicts
the shared semantic contract and must fail review or admission.

## 10. Limitations and source anchors

The 2016 proposed swap is not treated as an executed 2017 swap; no unidentified seller, cash balance, share issuance or elected board is manufactured. SRC004 leaves the December investor unnamed; Metro first has executable terms in the mid-2016 window. E9/E10 conflates a proposed RMB45.6bn swap with later near-30% ownership and has corrupt transfer endpoints.
Any change to the represented owner, admissible choice, information prerequisite
or record meaning requires revising this parent and rebuilding dependent
registries/configuration/package identities. Timing-only choices remain in
configuration within these bounds. Source anchors are the complete appearances
above and the named frozen records, available only through the sealed Source
Profile. No external retrieval, historical fit or scientific validity is claimed.
