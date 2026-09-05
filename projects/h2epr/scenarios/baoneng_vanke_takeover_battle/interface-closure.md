# Baoneng–Vanke Takeover Battle interface closure

## Scope and human parents

Eight reviewed Agent Definitions project into eight runtime actors, four
observations, 27 event intents plus `no_op`, and two lifecycles. The Scenario
contains 28 domain fields plus the interface's runtime state_version. No
Population is required by this source roster. Semantic parent hashes are bound
by the participant index and rechecked by package compilation.

## Source action crosswalk

The Draft contains 31 actor-local action rows. 27 retained action meanings map
to distinct event intents. Two late Baoneng hold-stake rows are passive; Yu's
nomination is received information; one repeated Metro nomination merges with
the same June19 proposal. The table preserves every row's disposition. Corrupt
transaction endpoint rows do not introduce a second hidden action source.

| Source action anchors | Runtime treatment | Authority / qualification |
| --- | --- | --- |
| S1/E1/P_1; SRC001 | `disclose_initial_stake` | Record the initial shareholding disclosure, without settling any shares. |
| S1/E2/P_4; SRC001 | `state_takeover_opposition` | Record Wang's own public opposition. |
| S1/E2/P_5; SRC001 | `state_management_risk` | Record Yu's management-risk statement, not a proved financial-risk model. |
| S1/E2/P_4; SRC001 | `publish_management_statement` | Publish the received management statement. |
| S1/E3/P_2; SRC001 | `issue_suspension_notice` | Issue a corporate suspension/restructuring notice; exchange permission is not simulated. |
| S2/E4/P_2; SRC004 | `record_conditional_loi` | Record a conditional LOI with an unidentified investor, not a completed issuance. |
| S2/E4/P_1; SRC004 | `disclose_increased_stake` | Record the later affiliate-aggregated shareholding disclosure. |
| S2/E4/P_6; SRC002 | `submit_restructuring_terms` | Submit the mid-2016 proposed asset-restructuring terms. |
| S2/E5/P_2; SRC002 | `announce_metro_proposal` | Announce the conditional Metro proposal; no dilution follows automatically. |
| S2/E5/P_6; SRC002 | `confirm_proposal_participation` | Confirm participation in the proposal, without closing an asset transaction. |
| S2/E5/P_1; SRC002 | `oppose_asset_proposal` | Record Baoneng opposition, not a computed shareholder veto. |
| S3/E8/P_3 and S2/E5 description; SRC002 | `oppose_asset_proposal_cr` | Record China Resources opposition as a separate shareholder choice. |
| S3/E6/P_1; SRC002 | `submit_removal_request` | Request removal of management; the board response remains separate. |
| S3/E6/P_2; SRC002 | `issue_resumption_notice` | Record the issuer resumption notice, not exchange execution or stock-price change. |
| S3/E8/P_8; SRC002 | `issue_governance_guidance` | Issue guidance to resolve the dispute through corporate governance; no imposed winner. |
| S3/E6/P_2; SRC002 | `record_board_rejection` | Record the board-owned rejection of the removal request, not a manager action. |
| S3/E7/P_7; SRC003 | `disclose_evergrande_stake` | Record the Evergrande acquisition announcement; no assumed seller or price effect. |
| S3/E8/P_2; SRC005 | `open_resolution_discussion` | Open the represented discussion channel; invitation routing is a construction assumption. |
| S3/E8/P_1; SRC005 | `reaffirm_opposition` | Reaffirm an earlier opposed position without creating a new purchase. |
| S3/E8/P_6; SRC005 | `submit_negotiation_position` | Record continuing negotiation participation; no consensus is inferred. |
| S3/E8/P_7; SRC005 | `record_negotiation_participation` | Record participation after the discussion invitation. |
| S3/E8/P_2; SRC005 | `report_operating_impacts` | Record the exposed H1 operating-impact statement; the dispute is not a calibrated cause of profits. |
| S4/E9/P_6; SRC010 | `disclose_metro_acquisition` | Record the later acquisition disclosure independently of the unexecuted 2016 swap. |
| S4/E9/P_6 and S4/E10/P_6; SRC010 | `submit_board_nominees` | Submit the single June19 nominee proposal; nominees are not elected. |
| S4/E9/P_2; SRC010 | `register_board_nominees` | Register the received proposal for corporate processing. |
| S4/E10/P_4; SRC010 | `decline_board_nomination` | Record declining re-nomination and an endorsement; no successor appointment. |
| S4/E10/P_2; SRC010 | `schedule_shareholder_meeting` | Issue a notice for the June30 vote; the election result stays unobserved. |
| S4/E9/P_1 and S4/E10/P_1 hold-stake actions | Passive continuing status; no extra intent | No purchase, sale or ownership rank update is invented. |
| S4/E10/P_5 nominated-as-chairman | Received proposal/endorsement memory; no Yu intent | Nomination is not a choice made by its recipient or a completed appointment. |
| S4/E10/P_6 repeated June19 nominee proposal | Merged with S4/E9/P_6 submit_board_nominees | One exposed proposal, not two separate slates. |

## Observation, authority and effect closure

Every current actor has the same four observation classes and an actor-specific
intent list. All fields are public records; own memory remains actor-specific.
Each non-default handler has one eligible actor, a declared target_id and
state preconditions. The runtime and reducer own all effects. The board-response
intent is corporate-interface-only; regulator guidance is CSRC-only. The election
field has no writer. Positive directed routes cover all selected message pairs.

## Review cases and failure routing

Record an absent nominee proposal as missing information, never as a silently
received slate. A foreign actor invoking another owner's handler is rejected.
Conflicting scalar writes follow the common reducer contract. A delayed proposal
may miss the decision horizon, but all pending transport must receive terminal
accounting. Generated graph reconstruction and independent publication validate
actual evidence, not whether all descriptive expectations were met.

Source conflicts and changed representation route to Source Profile and Agent
parents. Actor/intent/field drift routes to these registries and Scenario.
Timing and route choices route to configuration. Runtime defects require a
reduced generic test before shared code changes. Graph or release failures keep
the exact failed custody; no producer boolean can waive independent checks.

## Disposition

Semantic closure is accepted for compiler/runtime verification with the stated
composite-board, calendar, disclosure-only and election limits. This review is
the author's explicit semantic self-review, not a claim of a second independent
human reviewer. Runtime and publication success must be established separately.
