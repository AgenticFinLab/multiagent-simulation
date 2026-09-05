# National Transportation Safety Board decision interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `national_transportation_safety_board` — National Transportation Safety Board decision interface |
| Benchmark event and interval | `H2EPR-0196`; 2023-02-03 through the Draft's 2025-01-28 endpoint |
| Represented decision interface | the investigative authority's choice to open and communicate a preliminary investigation state |
| Source participant IDs | `P_3` |
| Primary decision situations | opening the preliminary investigation after receiving the incident notice |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the investigative authority's choice to open and communicate a preliminary investigation state. It treats the named organization or coordinated command as one public decision interface and does not synthesize internal staff, private deliberation, or undisclosed authority. It excludes a final cause finding, liability adjudication, and any result not present in the exposed Draft. A successor must split or narrow the Agent when the dataset supports independently acting internal units whose choices change the process.

## 3. Dataset basis and provenance

The source participant appears at the following complete Draft anchors. These anchors establish reported role and timing, not historical verification. Frozen evidence remains a sealed contextual input and no external research is used.

- `draft_epg:S1/E1/P_3`
- `draft_epg:S2/E4/P_3`

## 4. Event role, relationships, and authority

The NTSB interface receives incident information, opens a preliminary investigation, and sends the represented investigation notice. Investigation status is a process record, distinct from a final cause finding. DOJ retains its own later filing choice.

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

`open_investigation` is available after the initial incident opportunity and can wait for a routed alert. Once accepted, it completes this represented row. The preliminary notice is retained by DOJ when delivered; no five-tick delay is needed to make it coincide with a legal filing. The modeled NTSB-to-DOJ communication dependency is structural: Draft role anchors support the actors, not proof that this notice was legally necessary.

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

- Delay the incident alert inside the investigation window: the NTSB can open later.
- Remove that alert: the preliminary investigation can remain unstarted in a valid completed run.
- An accepted opening does not authorize repeated notices or a final cause finding.
- A notice delivered before the legal window must not make DOJ file before that window opens.

A target/authority violation, early private-message exposure, unexplained loss of received memory, or a physical/legal effect attributed to the participant rather than its environment falsifies this contract. A missing consequential authority requires a semantic successor, not an extra backend exception.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, or counterfactual choices. A final cause finding, liability adjudication, and any result not present in the exposed draft. A successor is required if new admissible dataset content changes the represented authority, actor cardinality, or information boundary. The anchors in Section 3 are the complete Draft basis for this parent.
