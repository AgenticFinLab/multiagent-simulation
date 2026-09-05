# China Securities Regulatory Commission Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic parent | `h2epr.1031.agent.csrc.v1` |
| Agent ID | `csrc` |
| Benchmark | H2EPR-1031, July 2015–June 2017 |
| Interface | securities-regulator guidance issuance interface |
| Source ID | `P_8` |
| Primary choices | Issue the exposed corporate-governance guidance while the dispute is open. |
| Cadence | Decide from each sealed coordinate prestate within declared availability windows; no continuous-time interpretation. |
| State authority | Intent producer only; environment admission and the authoritative reducer own records. |
| Exposure | Full Draft exposed, dataset-conditioned descriptive Rule baseline. |

## 2. Benchmark participant and representation

Guidance issuance remains an Agent choice. Message transport owns the later delivery; it cannot substitute for that issuance choice. Receiving guidance grants no other actor new power.

No approval of a winning shareholder, takeover ban, forced divestment, adjudication or shareholder vote is modeled. There is no calibrated utility, personality score or immutable
investment-risk parameter in this Definition. It constrains the represented
choices; the selected Rule settings remain a separate, replaceable owner.

## 3. Dataset basis and provenance

| Anchor | Use | Qualification |
| --- | --- | --- |
| draft_epg:S3/E8/P_8 | Participant appearance and local actions | Draft content, not independently verified history |

Frozen evidence anchors: SRC002. The Draft groups oversight into an August2016–May2017 episode although SRC002 already reports it in July; availability uses the earlier exposed July interval and does not invent continuing interventions.
The Source Profile seals all three permitted files. Relationships are interpreted
from actor-local actions and narrative consistency, not corrupt endpoint IDs.
The communication dependencies below are explicit construction assumptions.

## 4. Event role, relationships, and authority

This Agent may issue the exposed corporate-governance guidance while the dispute is open. Each intent below is restricted to this actor;
none lets it act as another shareholder, manager, regulator, exchange or voter.
Messages communicate statements and requests. Their recipients retain their own
authority. Holdings mentioned in disclosures are not spendable balances.

A guidance message cannot resolve the control dispute or set nominee/election fields. Other actors cannot impersonate this issuer.

## 5. Decision situations, observations, and state

| Observation | Producer / availability | Missing or stale handling |
|---|---|---|
| Public record fields | Reducer-derived sealed prestate, before decisions | Missing contract fails; unrecorded state remains a valid observation. |
| Current delivered messages | MASim transport before decisions | Empty means no current delivery, never inferred receipt. |
| Own outgoing pending lifecycle | Runtime projection | Await terminal accounting; another actor's pending private message is invisible. |
| Received and own-action memory | Runtime-derived history through the previous disposition/current delivery | Reuse actually received information; rejected attempts are not completions. |

An unrecorded proposal leaves the selected guidance Rule waiting; the regulator is not invoked simply because a historical stage label says oversight. Memory persists over this bounded event window; no calibrated
age cutoff is selected. New visible information may reopen a rejected row. Clock
advance or its own rejection alone cannot cause an identical retry. Accepted
rows are complete. No future stage text, later nominee outcome, hidden ballot,
Reference content or generated opaque identifier is decision evidence.

## 6. Admissible decision semantics

| Intent | Activation / reopening | Permitted response and boundary |
| --- | --- | --- |
| `issue_governance_guidance` | proposal.corporate_announcement = recorded; positions.baoneng_opposition = recorded | Issue guidance to resolve the dispute through corporate governance; no imposed winner. |

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
| `issue_governance_guidance` | `regulation` | `regulation.guidance`: unrecorded → issued |

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

- Normal: Once a contested proposal is visible in the modeled dispute window, CSRC may issue guidance to the corporate and shareholder interfaces.
- Missing information: An unrecorded proposal leaves the selected guidance Rule waiting; the regulator is not invoked simply because a historical stage label says oversight.
- Pending: Its outgoing statement remains unknown to a recipient until delivery. The sender can observe its own pending lifecycle but cannot mark it delivered.
- Authority or adverse result: A guidance message cannot resolve the control dispute or set nominee/election fields. Other actors cannot impersonate this issuer.
- Perturbation: A delayed proposal can delay guidance; no forced settlement is generated when the guidance eventually arrives.

Premature action before the stated information condition contradicts this Rule
realization. A foreign actor writing the record, future nominee knowledge in an
early observation, or a notice generating securities/election effects contradicts
the shared semantic contract and must fail review or admission.

## 10. Limitations and source anchors

No approval of a winning shareholder, takeover ban, forced divestment, adjudication or shareholder vote is modeled. The Draft groups oversight into an August2016–May2017 episode although SRC002 already reports it in July; availability uses the earlier exposed July interval and does not invent continuing interventions.
Any change to the represented owner, admissible choice, information prerequisite
or record meaning requires revising this parent and rebuilding dependent
registries/configuration/package identities. Timing-only choices remain in
configuration within these bounds. Source anchors are the complete appearances
above and the named frozen records, available only through the sealed Source
Profile. No external retrieval, historical fit or scientific validity is claimed.
