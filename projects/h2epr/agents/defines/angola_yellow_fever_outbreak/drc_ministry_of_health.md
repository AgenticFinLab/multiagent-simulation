# DRC Ministry of Health decision interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `drc_ministry_of_health` — DRC Ministry of Health decision interface |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Represented decision interface | DRC's imported-case reporting, committee briefing conditions, scaled response, progress reporting, and surveillance choices |
| Source participant IDs | `P_6` |
| Primary decision situations | reporting imported cases, briefing the committee, implementing scaled response, reporting progress, and sustaining surveillance |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents DRC's imported-case reporting, committee briefing conditions, scaled response, progress reporting, and surveillance choices. It treats the named organization or committee as one public decision interface without inventing internal staff, deliberation, or private information. It excludes WHO and committee authority, Angola decisions, individual case movement, and proof of response effectiveness. A successor must split or narrow the Agent if admitted data expose independently acting internal units whose choices alter the process.

## 3. Dataset basis and provenance

The source participant appears at every Draft anchor below. These anchors establish dataset-authored role and timing, not verified history. Frozen evidence is sealed context only; no external research is added.

- `draft_epg:S2/E4/P_6`
- `draft_epg:S3/E5/P_6`
- `draft_epg:S3/E6/P_6`
- `draft_epg:S3/E7/P_6`
- `draft_epg:S4/E9/P_6`

## 4. Event role, relationships, and authority

DRC reports the represented imported cases, briefs the committee, records a
fractional-dose response, supplies progress information, and sustains domestic
surveillance. It does not own Angola decisions, WHO assessments, travel behavior,
or vaccine efficacy. The imported-case report is a statement, not modeled infection.

## 5. Decision situations, observations, and state

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Admissible decision semantics

The initial report reads the recorded outbreak confirmation. Subsequent
briefing and response choices wait for retained WHO messages. A response record
is separate from a later progress report, and each has its own earliest window.
The fractional-dose label records the selected response strategy without a
stock ledger, dosing model, administration count, or effectiveness estimate.

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

- Withhold the committee invitation: DRC can report imported cases while its briefing remains absent.
- Delay response guidance inside its window: DRC can respond later without repeating an accepted report.
- Reject an Angola target from a DRC intent: no foreign response field changes.
- A no-recent-cases report is not independent evidence that transmission ended.

Early private-message exposure, lost received memory, unauthorized state writes, or attribution of an unmodeled health effect to a participant falsifies the contract. New authority or materially independent internal units require a semantic successor.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes WHO and committee authority, Angola decisions, individual case movement, and proof of response effectiveness. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
