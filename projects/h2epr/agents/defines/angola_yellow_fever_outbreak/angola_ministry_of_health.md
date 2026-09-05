# Angola Ministry of Health decision interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `angola_ministry_of_health` — Angola Ministry of Health decision interface |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Represented decision interface | Angola's outbreak detection, reporting, vaccination-response, committee-briefing, progress-reporting, and surveillance choices |
| Source participant IDs | `P_2` |
| Primary decision situations | detecting the outbreak, reporting a case surge, launching local vaccination, briefing the committee, implementing scaled response, reporting progress, and sustaining surveillance |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents Angola's outbreak detection, reporting, vaccination-response, committee-briefing, progress-reporting, and surveillance choices. It treats the named organization or committee as one public decision interface without inventing internal staff, deliberation, or private information. It excludes laboratory confirmation, WHO or committee authority, individual vaccination outcomes, and verified epidemiological effectiveness. A successor must split or narrow the Agent if admitted data expose independently acting internal units whose choices alter the process.

## 3. Dataset basis and provenance

The source participant appears at every Draft anchor below. These anchors establish dataset-authored role and timing, not verified history. Frozen evidence is sealed context only; no external research is added.

- `draft_epg:S1/E1/P_2`
- `draft_epg:S2/E3/P_2`
- `draft_epg:S2/E4/P_2`
- `draft_epg:S3/E5/P_2`
- `draft_epg:S3/E6/P_2`
- `draft_epg:S3/E7/P_2`
- `draft_epg:S4/E9/P_2`

## 4. Event role, relationships, and authority

Angola can record detection and refer initial samples, report a case surge,
launch a campaign, supply a committee briefing, record its national response,
report progress, and sustain surveillance. Laboratory reporting, committee
assessment, and WHO coordination remain separate authorities. These choices
alter institutional records; they do not generate infections or administer doses.

## 5. Decision situations, observations, and state

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Admissible decision semantics

The represented detection opens sample referrals. Local campaign and progress
choices use public records; briefing and response choices use retained invitations
or guidance. Each row may wait within its own availability window. The Rule
selection follows exposed report content, including the later progress statement;
it does not infer that a recorded response caused cases to fall.

## 7. Intent and environment-result boundary

Each intent carries a typed target and may create declared messages. The environment decides admission and effects; MASim owns routing and delivery. Rejection, delay, failure, resource limits, downstream response, and epidemiological truth remain outside the Agent's authorship.

## 8. Configurable dimensions and uncertainty

Shared configuration selects the finite clock, public opening records, and
transport latency. Rule configuration selects bounded availability windows,
priority, and message/state guards within the semantic choice surface. These
are uncalibrated construction choices. A row completes once accepted; after a
rejection it may retry when visible state, received information, or outgoing
lifecycle information changes. The clock alone does not reopen it. No fixed
personality, probability, epidemiological threshold, or guaranteed outcome is
part of the Definition.

## 9. Worked cases and contract falsification

- A sample referral can be delayed without erasing a detection record.
- A late first-meeting invitation can still produce Angola's briefing inside its window.
- WHO guidance does not write Angola's response record; Angola must emit its own intent.
- An absent response record can block a progress statement under this policy without invalidating the finite run.

Early private-message exposure, lost received memory, unauthorized state writes, or attribution of an unmodeled health effect to a participant falsifies the contract. New authority or materially independent internal units require a semantic successor.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes laboratory confirmation, WHO or committee authority, individual vaccination outcomes, and verified epidemiological effectiveness. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
