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

The Agent may emit only registered intents and messages over declared routes. Draft relation rows are not executable authority because several reverse direction or name the wrong participant. The Agent cannot mutate state, declare delivery, validate another institution, or convert a report into a public-health outcome.

## 5. Decision situations, observations, and state

| Observation | Producer and availability | Missing or stale rule | Use |
|---|---|---|---|
| public state | Runtime at coordinate open | Fail if absent | Check declared preconditions |
| delivered messages | MASim transport before decisions | Empty when none are due | Activate message-gated choices |
| pending lifecycles | MASim transport | Empty when none exist | Keep request and delivery distinct |

Future Draft facts are unavailable before their logical coordinate. World state is persistent under environment ownership; backend reasoning is transient.

## 6. Admissible decision semantics

The admissible non-default intents are `confirm_nicd_cases`. A declared coordinate and every state or message guard must match. Missing, stale, or adverse information yields `no_op` or a typed rejection, never a substitute act. Exact Rule rows and model settings remain outside this Definition.

## 7. Intent and environment-result boundary

Each intent carries a typed target and may create declared messages. The environment decides admission and effects; MASim owns routing and delivery. Rejection, delay, failure, resource limits, downstream response, and epidemiological truth remain outside the Agent's authorship.

## 8. Configurable dimensions and uncertainty

Coordinate selection, route latency, decision priority, and activation are configuration values. Abstention, delay, or omitted participation are sensitivity choices. No personality, probability, prompt, threshold, or guaranteed result is fixed here.

## 9. Worked cases and contract falsification

- Required state and messages permit the relevant intent; missing evidence permits `no_op`.
- An invalid target or payload is rejected without silent repair.
- A sent report remains pending until transport delivers it.
- Environment denial does not rewrite the participant's original intent.
- Changing a material delivered message may change the response while semantic identity remains stable.

The Definition is falsified if `nicd_south_africa` needs authority outside the laboratory choice to issue the represented NICD confirmation report or if its modeled choice is causally inert under every meaningful perturbation.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes sample collection, clinical diagnosis beyond the report, Angola policy, and independent verification of laboratory accuracy. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
