# Wang Shi Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.1031.agent.wang_shi.v1` |
| Agent ID | `wang_shi` |
| Benchmark | H2EPR-1031, July 2015–June 2017 |
| Interface | named chairman personal statement and nomination choice |
| Source ID | `P_4` |
| Primary choices | State opposition, publish the available Yu management statement and decline a later board nomination while endorsing Yu. |
| Cadence | Decide from each sealed coordinate prestate within declared availability windows; no continuous-time interpretation. |
| State authority | Intent producer only; environment admission and the authoritative reducer own records. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

The source distinguishes Wang personal opposition and publication from corporate notices. Declining re-nomination records his choice, not an immediate externally verified vacancy or completed succession.

He cannot issue the corporate board rejection, acquire stock on Metro behalf, appoint Yu or decide the shareholder election. There is no calibrated utility, personality score or immutable
investment-risk parameter in this Definition. It constrains the represented
choices; the selected Rule settings remain a separate, replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S1/E2/P_4 | Participant appearance and local actions | Draft content, not independently verified history |
| draft_epg:S4/E10/P_4 | Participant appearance and local actions | Draft content, not independently verified history |

Frozen evidence anchors: SRC001, SRC010. S4 relation rows attach shareholder and executive roles to wrong IDs. Actor-local Wang actions are retained instead of those endpoints.
The Source Profile seals all three permitted files. Relationships are interpreted
from actor-local actions and narrative consistency, not corrupt endpoint IDs.
The communication dependencies below are explicit construction assumptions.

## 4. Event role, relationships, and authority

This Agent may state opposition, publish the available Yu management statement and decline a later board nomination while endorsing Yu. Each intent below is restricted to this actor;
none lets it act as another shareholder, manager, regulator, exchange or voter.
Messages communicate statements and requests. Their recipients retain their own
authority. Holdings mentioned in disclosures are not spendable balances.

Endorsing Yu does not set Yu chairman status. A request to write the corporate election result is outside this intent set.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate, before decisions | Missing contract fails; unrecorded state remains a valid observation. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; another actor's pending private message is invisible. |
| Received and own-action memory | Runtime-derived history through the previous disposition/current delivery | Reuse actually received information; rejected attempts are not completions. |

Without Yu's statement he cannot publish that statement; without the modeled nominee notice the selected late Rule waits. The two information requirements are distinct. Memory persists over this bounded event window; no calibrated
age cutoff is selected. New visible information may reopen a rejected row. Clock
advance or its own rejection alone cannot cause an identical retry. Accepted
rows are complete. No future stage text, later nominee outcome, hidden ballot,
Reference content or generated opaque identifier is decision evidence.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `state_takeover_opposition` | known initial_stake_report from baoneng_group | Record Wang's own public opposition. |
| `publish_management_statement` | known management_risk_statement from yu_liang | Publish the received management statement. |
| `decline_board_nomination` | known board_nominee_proposal from shenzhen_metro | Record declining re-nomination and an endorsement; no successor appointment. |

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
| `state_takeover_opposition` | `management` | `management.wang_opposition`: unrecorded → recorded |
| `publish_management_statement` | `management` | `management.wang_publication`: unrecorded → recorded |
| `decline_board_nomination` | `nomination` | `nomination.wang_choice`: unrecorded → declined_recorded |

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

- Normal: With Yu's management-risk statement known, Wang may publish it. With the later nominee notice known, he may decline re-nomination and communicate his endorsement.
- Missing information: Without Yu's statement he cannot publish that statement; without the modeled nominee notice the selected late Rule waits. The two information requirements are distinct.
- Pending: Its outgoing statement remains unknown to a recipient until delivery. The sender can observe its own pending lifecycle but cannot mark it delivered.
- Authority or adverse result: Endorsing Yu does not set Yu chairman status. A request to write the corporate election result is outside this intent set.
- Perturbation: Delay the nominee notice while retaining the June acquisition disclosure: Wang can know the shareholder development yet still lack the specific nomination input used by this Rule.

Premature action before the stated information condition contradicts this Rule
realization. A foreign actor writing the record, future nominee knowledge in an
early observation, or a notice generating securities/election effects contradicts
the shared semantic contract and must fail review or admission.

## 10. Limitations and source anchors

He cannot issue the corporate board rejection, acquire stock on Metro behalf, appoint Yu or decide the shareholder election. S4 relation rows attach shareholder and executive roles to wrong IDs. Actor-local Wang actions are retained instead of those endpoints.
Any change to the represented owner, admissible choice, information prerequisite
or record meaning requires revising this parent and rebuilding dependent
registries/configuration/package identities. Timing-only choices remain in
configuration within these bounds. Source anchors are the complete appearances
above and the named frozen records, available only through the sealed Source
Profile. No external retrieval, historical fit or scientific validity is claimed.
