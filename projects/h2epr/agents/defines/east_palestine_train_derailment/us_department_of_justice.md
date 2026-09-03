# U.S. Department of Justice decision interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `us_department_of_justice` — U.S. Department of Justice decision interface |
| Benchmark event and interval | `H2EPR-0196`; 2023-02-03 through the Draft's 2025-01-28 endpoint |
| Represented decision interface | the federal enforcement choice to file the civil action exposed by the Draft |
| Source participant IDs | `P_7` |
| Primary decision situations | filing the federal civil action after a preliminary investigation notice |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the federal enforcement choice to file the civil action exposed by the Draft. It treats the named organization or coordinated command as one public decision interface and does not synthesize internal staff, private deliberation, or undisclosed authority. It excludes court adjudication, damages, settlement implementation, and state legal authority. A successor must split or narrow the Agent when the dataset supports independently acting internal units whose choices change the process.

## 3. Dataset basis and provenance

The source participant appears at the following complete Draft anchors. These anchors establish reported role and timing, not historical verification. Frozen evidence remains a sealed contextual input and no external research is used.

- `draft_epg:S3/E6/P_7`

## 4. Event role, relationships, and authority

The Agent may emit only its registered intents and messages over declared routes. It cannot mutate state, declare delivery, validate another institution's authority, or turn an announced action into an observed result. Its counterparties and public fields are fixed by the participant interface and Scenario Mechanism.

## 5. Decision situations, observations, and state

| Observation | Producer and availability | Missing or stale rule | Use |
|---|---|---|---|
| public state | Runtime at coordinate open | Fail if absent | Check declared preconditions |
| delivered messages | MASim transport before decisions | Empty list when none are due | Activate message-gated choices |
| pending lifecycles | MASim transport at every coordinate | Empty list when none exist | Keep submission distinct from delivery |

World state is persistent under environment ownership. Backend reasoning is transient. Future Draft facts are unavailable before their logical coordinate even though construction is full-Draft-exposed.

## 6. Admissible decision semantics

The admissible non-default intents are `file_federal_civil_action`. A declared coordinate, required message or state precondition, and eligible target must all match. Missing or adverse information leads to `no_op` or a typed rejection; it does not authorize a substitute act. The backend retains only the choice permitted by configuration and may not invent success.

## 7. Intent and environment-result boundary

Each intent carries a typed target and may create declared message intents. The environment decides admission, applies state effects, and emits disposition and delta records. MASim owns routing and delivery. Rejection, delay, duplication, failure, and recipient response remain observable results outside the Agent's authorship.

## 8. Configurable dimensions and uncertainty

Coordinate selection, route latency, rule priority, and action activation are selected in shared or Rule configuration. Alternative timing and abstention are sensitivity choices. No fixed personality, probability, model prompt, or guaranteed outcome is part of this Definition.

## 9. Worked cases and contract falsification

- With the required state and message, the configured intent is admissible; without either, `no_op` is valid.
- An invalid target or payload is rejected by the environment and cannot be repaired silently.
- A sent message remains pending until MASim routes it; the Agent cannot observe it early.
- A backend substitution or use of a later Draft fact at an earlier coordinate violates the contract.

The Definition is falsified if `us_department_of_justice` requires authority outside the federal enforcement choice to file the civil action exposed by the Draft or if removing its modeled choice leaves the generated process unchanged under a meaningful perturbation.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, or counterfactual choices. Court adjudication, damages, settlement implementation, and state legal authority. A successor is required if new admissible dataset content changes the represented authority, actor cardinality, or information boundary. The anchors in Section 3 are the complete Draft basis for this parent.
