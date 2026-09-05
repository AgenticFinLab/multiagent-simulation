# WHO Yellow Fever Emergency Committee decision interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `who_yellow_fever_emergency_committee` — WHO Yellow Fever Emergency Committee decision interface |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Represented decision interface | the ad hoc committee's represented risk-assessment and recommendation choices at its two meetings |
| Source participant IDs | `P_8` |
| Primary decision situations | issuing the May and August serious-public-health-event assessments without declaring a PHEIC |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the ad hoc committee's represented risk-assessment and recommendation choices at its two meetings. It treats the named organization or committee as one public decision interface without inventing internal staff, deliberation, or private information. It excludes WHO implementation, country response, legal force beyond the represented assessment, and proof that the assessment was correct. A successor must split or narrow the Agent if admitted data expose independently acting internal units whose choices alter the process.

## 3. Dataset basis and provenance

The source participant appears at every Draft anchor below. These anchors establish dataset-authored role and timing, not verified history. Frozen evidence is sealed context only; no external research is added.

- `draft_epg:S3/E5/P_8`
- `draft_epg:S3/E7/P_8`

## 4. Event role, relationships, and authority

The committee owns two represented assessment statements; WHO owns convening
and coordination, and countries own response. This separate actor preserves the
assessment choice and information handoff. No legal or epidemiological correctness
is established by an accepted statement.

## 5. Decision situations, observations, and state

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Admissible decision semantics

The first assessment can wait for both country briefings, retaining whichever
arrives first. The second can wait for the separately routed review brief.
The current baseline chooses the exposed serious-event/non-PHEIC statements;
the admissible alternative here is waiting or no statement, not an implemented
classifier over competing risk categories. Expanding that substantive choice
surface needs a semantic successor and supported information, not a hidden prompt.

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

- Briefings arriving on different ticks remain combinable.
- One missing briefing leaves the first assessment pending in a valid finite run.
- A first assessment cannot substitute for the second review brief.
- A committee intent cannot directly record national response or vaccination coverage.

Early private-message exposure, lost received memory, unauthorized state writes, or attribution of an unmodeled health effect to a participant falsifies the contract. New authority or materially independent internal units require a semantic successor.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes WHO implementation, country response, legal force beyond the represented assessment, and proof that the assessment was correct. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
