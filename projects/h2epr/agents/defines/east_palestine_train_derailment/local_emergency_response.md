# Local emergency response command

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `local_emergency_response` — Local emergency response command |
| Benchmark event and interval | `H2EPR-0196`; 2023-02-03 through the Draft's 2025-01-28 endpoint |
| Represented decision interface | the coordinated operational choice interface for evacuation and the exposed controlled-release response |
| Source participant IDs | `P_4` |
| Primary decision situations | ordering evacuation and issuing the represented controlled-release instruction |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the coordinated operational choice interface for evacuation and the exposed controlled-release response. It treats the named organization or coordinated command as one public decision interface and does not synthesize internal staff, private deliberation, or undisclosed authority. It excludes individual responder behavior, undisclosed command structure, and independent proof of safety or necessity. A successor must split or narrow the Agent when the dataset supports independently acting internal units whose choices change the process.

## 3. Dataset basis and provenance

The source participant appears at the following complete Draft anchors. These anchors establish reported role and timing, not historical verification. Frozen evidence remains a sealed contextual input and no external research is used.

- `draft_epg:S1/E1/P_4`
- `draft_epg:S1/E2/P_4`

## 4. Event role, relationships, and authority

The command interface receives the railroad incident notice, may order the represented evacuation, and may issue the controlled-release instruction after the evacuation record is active. It owns these operational choices; it does not own Ohio return advice, EPA cleanup, or a model of fire, exposure, and physical safety.

## 5. Decision situations, observations, and state

At coordinate open, the runtime supplies sealed public state, newly delivered
messages, this actor's outgoing pending lifecycles, and structured memory of
received messages and its own prior dispositions. The first memory is empty.
A previous receipt remains available with its original receipt tick; absence
is not inferred receipt. Pending private traffic is invisible to its recipient.
Same-tick results become known at the next coordinate. No historical stage
label, later Draft fact, opaque generated identifier, or other actor's private
result is a decision input.

## 6. Admissible decision semantics

`order_evacuation` and `issue_controlled_release_instruction` are distinct intents. The latter records an instruction and sends `response_instruction` to Ohio and EPA; acceptance does not assert that a burn completed or that return is safe. Its earliest window is anchored to Draft S1/E2. The command can wait for incident information or the evacuation precondition, then reconsider within the declared window. An accepted instruction is not sent again merely because another tick passes.

## 7. Intent and environment-result boundary

Each intent carries a typed target and may create declared message intents. The environment decides admission, applies state effects, and emits disposition and delta records. MASim owns routing and delivery. Rejection, delay, duplication, failure, and recipient response remain observable results outside the Agent's authorship.

## 8. Configurable dimensions and uncertainty

Shared configuration selects the opening world, clock opportunities, and
communication latency. Rule configuration selects priority, information guards,
and bounded activation windows within the semantic choice surface. These are
uncalibrated construction choices. A window permits reconsideration; it does
not guarantee a different decision. Accepted rows complete once; rejected rows
may retry after visible state, received messages, or outgoing lifecycle
information changes. The clock alone is not new information. No fixed
personality, probability, or guaranteed endpoint belongs to this Definition.

## 9. Worked cases and contract falsification

- An absent incident notice leaves evacuation inactive; it does not erase the exogenous derailment.
- An evacuation order accepted at one tick becomes visible to the command at the next.
- A controlled-release request while evacuation is inactive is rejected without a partial hazard-state write.
- Ohio or EPA may receive the instruction later; the command cannot claim receipt on their behalf.

A target/authority violation, early private-message exposure, unexplained loss of received memory, or a physical/legal effect attributed to the participant rather than its environment falsifies this contract. A missing consequential authority requires a semantic successor, not an extra backend exception.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, or counterfactual choices. Individual responder behavior, undisclosed command structure, and independent proof of safety or necessity. A successor is required if new admissible dataset content changes the represented authority, actor cardinality, or information boundary. The anchors in Section 3 are the complete Draft basis for this parent.
