# World Health Organization coordination interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `world_health_organization` — World Health Organization coordination interface |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Represented decision interface | WHO's public monitoring, documentation, meeting-convening, response-coordination, and regional-surveillance choices represented by the Draft |
| Source participant IDs | `P_1` |
| Primary decision situations | recording confirmation, documenting cross-border risk, convening two committee reviews, coordinating scaled response, and activating regional surveillance |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents WHO's public monitoring, documentation, meeting-convening, response-coordination, and regional-surveillance choices represented by the Draft. It treats the named organization or committee as one public decision interface without inventing internal staff, deliberation, or private information. It excludes country implementation, laboratory testing, committee assessment, vaccine allocation truth, and proof of public-health effectiveness. A successor must split or narrow the Agent if admitted data expose independently acting internal units whose choices alter the process.

## 3. Dataset basis and provenance

The source participant appears at every Draft anchor below. These anchors establish dataset-authored role and timing, not verified history. Frozen evidence is sealed context only; no external research is added.

- `draft_epg:S1/E1/P_1`
- `draft_epg:S1/E2/P_1`
- `draft_epg:S2/E3/P_1`
- `draft_epg:S2/E4/P_1`
- `draft_epg:S3/E5/P_1`
- `draft_epg:S3/E6/P_1`
- `draft_epg:S3/E7/P_1`
- `draft_epg:S4/E9/P_1`

## 4. Event role, relationships, and authority

WHO records laboratory confirmation, documents regional risk, convenes two
committee reviews, coordinates scaled response, and records regional surveillance.
It combines reports from distinct institutions without acquiring their decision
authority. Country briefings, the committee assessment, and national responses
are distinct actions and lifecycles.

## 5. Decision situations, observations, and state

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Admissible decision semantics

Initial recording needs both retained laboratory reports. Cross-border risk
uses DRC's report; second-review convening uses both retained country progress
updates. These conjunctions are authored information requirements and can remain
unsatisfied. Separate windows preserve the exposed review intervals. Regional
surveillance follows the second assessment in this baseline; Uganda's declaration
is informative but is not permission for surveillance in every jurisdiction.

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

- Receive the laboratory reports at different ticks: WHO can combine them later.
- Withhold one country progress update: the second-review choice can wait rather than treating a missing message as assent.
- Guidance received by a country remains separate from that country's response intent.
- Absence of Uganda's declaration does not veto all regional surveillance.

Early private-message exposure, lost received memory, unauthorized state writes, or attribution of an unmodeled health effect to a participant falsifies the contract. New authority or materially independent internal units require a semantic successor.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes country implementation, laboratory testing, committee assessment, vaccine allocation truth, and proof of public-health effectiveness. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
