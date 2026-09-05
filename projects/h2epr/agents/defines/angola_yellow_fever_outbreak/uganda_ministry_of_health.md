# Uganda Ministry of Health decision interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `uganda_ministry_of_health` — Uganda Ministry of Health decision interface |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Represented decision interface | Uganda's represented outbreak-end declaration and continuing surveillance choices |
| Source participant IDs | `P_9` |
| Primary decision situations | declaring the related Uganda outbreak ended and sustaining post-outbreak surveillance |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents Uganda's represented outbreak-end declaration and continuing surveillance choices. It treats the named organization or committee as one public decision interface without inventing internal staff, deliberation, or private information. It excludes individual case truth, proof of transmission interruption, Angola or DRC response, and regional WHO authority. A successor must split or narrow the Agent if admitted data expose independently acting internal units whose choices alter the process.

## 3. Dataset basis and provenance

The source participant appears at every Draft anchor below. These anchors establish dataset-authored role and timing, not verified history. Frozen evidence is sealed context only; no external research is added.

- `draft_epg:S4/E8/P_9`
- `draft_epg:S4/E9/P_9`

## 4. Event role, relationships, and authority

Uganda independently owns its represented outbreak-end declaration and
continuing domestic surveillance. Its declaration is a national public statement,
not WHO permission, regional disease eradication, or proof of an Angola-to-Uganda
causal transmission path.

## 5. Decision situations, observations, and state

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Admissible decision semantics

`declare_uganda_outbreak_end` becomes available in the exposed Uganda interval
and does not require the WHO second assessment. The selected Rule baseline emits
the Draft declaration content. Initial `not_declared` and terminal `declared_ended`
describe this announcement record, not a simulated infection trajectory.
Domestic surveillance can follow that record in its later window.

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

- A missing WHO assessment does not remove Uganda's own declaration authority.
- The declaration is unavailable before its own source-anchored interval.
- A rejected declaration target leaves its record unchanged.
- Continued surveillance does not imply a new outbreak or prove elimination.

Early private-message exposure, lost received memory, unauthorized state writes, or attribution of an unmodeled health effect to a participant falsifies the contract. New authority or materially independent internal units require a semantic successor.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes individual case truth, proof of transmission interruption, Angola or DRC response, and regional WHO authority. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
