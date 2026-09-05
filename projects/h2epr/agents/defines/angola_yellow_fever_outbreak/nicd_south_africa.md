# NICD South Africa laboratory-reporting interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `nicd_south_africa` — NICD South Africa laboratory-reporting interface |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Represented decision interface | the laboratory choice to issue the represented NICD confirmation report |
| Source participant IDs | `P_4` |
| Primary decision situations | issuing the 19 January laboratory confirmation after a routed sample referral |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the laboratory choice to issue the represented NICD confirmation report. It treats the named organization or committee as one public decision interface without inventing internal staff, deliberation, or private information. It excludes sample collection, clinical diagnosis beyond the report, Angola policy, and independent verification of laboratory accuracy. A successor must split or narrow the Agent if admitted data expose independently acting internal units whose choices alter the process.

## 3. Dataset basis and provenance

The source participant appears at every Draft anchor below. These anchors establish dataset-authored role and timing, not verified history. Frozen evidence is sealed context only; no external research is added.

- `draft_epg:S1/E2/P_4`

## 4. Event role, relationships, and authority

NICD owns one bounded laboratory-reporting choice for the initial samples.
It receives a referral from Angola and can issue the represented NICD result to
WHO. IP-D has a separate result and authority; WHO owns combined recording.

## 5. Decision situations, observations, and state

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Admissible decision semantics

`confirm_nicd_cases` may wait for a retained referral within the laboratory
window. The c02 opportunity compresses 19–20 January across the two labs and
does not distinguish intra-interval timing. Acceptance records the configured
confirmation statement, not a simulated test with measured accuracy. A completed
row does not issue duplicate confirmations at later ticks.

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

- Remove the referral: NICD does not create a result from a clock tick.
- Delay it: NICD can report within its remaining window.
- Deliver NICD and IP-D reports at different ticks: WHO retains the first while waiting for the second.
- A NICD intent cannot write IP-D's laboratory result.

Early private-message exposure, lost received memory, unauthorized state writes, or attribution of an unmodeled health effect to a participant falsifies the contract. New authority or materially independent internal units require a semantic successor.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes sample collection, clinical diagnosis beyond the report, Angola policy, and independent verification of laboratory accuracy. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
