# Institut Pasteur Dakar laboratory-reporting interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `institut_pasteur_dakar` — Institut Pasteur Dakar laboratory-reporting interface |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Represented decision interface | the laboratory choice to issue the represented IP-D confirmation report |
| Source participant IDs | `P_5` |
| Primary decision situations | issuing the 20 January confirmatory report after a routed sample referral |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the laboratory choice to issue the represented IP-D confirmation report. It treats the named organization or committee as one public decision interface without inventing internal staff, deliberation, or private information. It excludes sample collection, clinical diagnosis beyond the report, Angola policy, and independent verification of laboratory accuracy. A successor must split or narrow the Agent if admitted data expose independently acting internal units whose choices alter the process.

## 3. Dataset basis and provenance

The source participant appears at every Draft anchor below. These anchors establish dataset-authored role and timing, not verified history. Frozen evidence is sealed context only; no external research is added.

- `draft_epg:S1/E2/P_5`

## 4. Event role, relationships, and authority

IP-D owns its own initial laboratory-reporting choice after an Angola referral.
Its report goes to WHO and is not a replacement for NICD's separate report.
Sample collection, diagnostic uncertainty, and country response are outside this interface.

## 5. Decision situations, observations, and state

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Admissible decision semantics

`confirm_ipd_cases` can use an earlier received referral and wait within the
laboratory window. The result content is the exposed 20 January confirmation
selected by this baseline. It does not simulate an assay, establish accuracy,
or grant authority over NICD's report. Accepted completion is remembered once.

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

- An earlier referral remains available at a later eligible tick.
- Without the IP-D report, WHO's selected dual-report recording remains open even if NICD reported.
- A rejected payload remains a rejection in own-action memory.
- No committee or national response effect follows directly from IP-D's intent.

Early private-message exposure, lost received memory, unauthorized state writes, or attribution of an unmodeled health effect to a participant falsifies the contract. New authority or materially independent internal units require a semantic successor.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes sample collection, clinical diagnosis beyond the report, Angola policy, and independent verification of laboratory accuracy. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
