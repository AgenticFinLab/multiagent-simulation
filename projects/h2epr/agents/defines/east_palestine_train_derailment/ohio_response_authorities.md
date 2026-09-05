# Ohio state and local response authorities

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `ohio_response_authorities` — Ohio state and local response authorities |
| Benchmark event and interval | `H2EPR-0196`; 2023-02-03 through the Draft's 2025-01-28 endpoint |
| Represented decision interface | the composite public-authority interface for return advice, state legal action, and municipal settlement recording |
| Source participant IDs | `P_5` |
| Primary decision situations | lifting evacuation, filing the exposed state action, and recording the exposed municipal settlement |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the composite public-authority interface for return advice, state legal action, and municipal settlement recording. It treats the named organization or coordinated command as one public decision interface and does not synthesize internal staff, private deliberation, or undisclosed authority. It excludes unexposed internal agency disagreement, federal authority, and proof that public assurances were scientifically correct. A successor must split or narrow the Agent when the dataset supports independently acting internal units whose choices change the process.

## 3. Dataset basis and provenance

The source participant appears at the following complete Draft anchors. These anchors establish reported role and timing, not historical verification. Frozen evidence remains a sealed contextual input and no external research is used.

- `draft_epg:S2/E3/P_5`
- `draft_epg:S2/E4/P_5`
- `draft_epg:S3/E5/P_5`
- `draft_epg:S3/E6/P_5`
- `draft_epg:S4/E8/P_5`

## 4. Event role, relationships, and authority

This aggregate authority combines the Draft state/local response and municipal roles. It may issue return advice after a response instruction, file the represented state civil action, and record the municipal settlement after a routed offer. Aggregation suppresses possible disagreement among agencies and the village; it grants no federal or judicial authority.

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

The response instruction is information, not verified safety. `lift_evacuation` records the represented return advisory under its own availability window. `file_state_civil_action` reads the public preliminary-investigation record. `record_municipal_settlement` reads an already delivered offer and the public class announcement. Each choice may wait independently, and later priorities cannot silently repeat an earlier accepted choice. Return advice, lawsuit filing, municipal agreement, court adjudication, and payment are different products.

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

- Without the response instruction, Ohio can leave evacuation active while the finite run still closes its evidence.
- A delayed offer may reopen the municipal choice before the final delivery barrier.
- An offer received early cannot move the municipal choice before its configured earliest opportunity.
- A state filing cannot write the federal legal field; a municipal record cannot prove compensation reached residents.

A target/authority violation, early private-message exposure, unexplained loss of received memory, or a physical/legal effect attributed to the participant rather than its environment falsifies this contract. A missing consequential authority requires a semantic successor, not an extra backend exception.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, or counterfactual choices. Unexposed internal agency disagreement, federal authority, and proof that public assurances were scientifically correct. A successor is required if new admissible dataset content changes the represented authority, actor cardinality, or information boundary. The anchors in Section 3 are the complete Draft basis for this parent.
