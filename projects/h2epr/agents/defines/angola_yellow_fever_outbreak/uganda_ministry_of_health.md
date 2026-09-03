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

The Agent may emit only registered intents and messages over declared routes. Draft relation rows are not executable authority because several reverse direction or name the wrong participant. The Agent cannot mutate state, declare delivery, validate another institution, or convert a report into a public-health outcome.

## 5. Decision situations, observations, and state

| Observation | Producer and availability | Missing or stale rule | Use |
|---|---|---|---|
| public state | Runtime at coordinate open | Fail if absent | Check declared preconditions |
| delivered messages | MASim transport before decisions | Empty when none are due | Activate message-gated choices |
| pending lifecycles | MASim transport | Empty when none exist | Keep request and delivery distinct |

Future Draft facts are unavailable before their logical coordinate. World state is persistent under environment ownership; backend reasoning is transient.

## 6. Admissible decision semantics

The admissible non-default intents are `declare_uganda_outbreak_end`, `activate_uganda_surveillance`. A declared coordinate and every state or message guard must match. Missing, stale, or adverse information yields `no_op` or a typed rejection, never a substitute act. Exact Rule rows and model settings remain outside this Definition.

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

The Definition is falsified if `uganda_ministry_of_health` needs authority outside Uganda's represented outbreak-end declaration and continuing surveillance choices or if its modeled choice is causally inert under every meaningful perturbation.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, counterfactual choices, or independently verified outcomes. The model excludes individual case truth, proof of transmission interruption, Angola or DRC response, and regional WHO authority. A successor is required if new admissible dataset content changes authority, cardinality, or information boundaries. The anchors listed in Section 3 are the complete Draft basis.
