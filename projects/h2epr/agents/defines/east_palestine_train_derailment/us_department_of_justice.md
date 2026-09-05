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

DOJ owns the represented federal civil filing after an investigation notice is available. Ohio owns a separate state filing, and courts and settlement counterparties are not folded into DOJ. The absence of a court actor limits this model to a filing record, not a legal judgment.

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

`file_federal_civil_action` becomes available at the legal-action interval. The notice may have arrived several ticks earlier and remains in received memory. Waiting and later filing are legal policy outputs; silence does not manufacture an investigation finding. The notice requirement is a documented modeling assumption because the exposed Draft does not supply an internal prosecutorial decision protocol.

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

- Deliver the notice early: DOJ waits until its legal window instead of treating receipt as an immediate mandate.
- Deliver it late within that window: DOJ can still file.
- Never deliver it: a valid finite run can end with the federal filing absent and its descriptive expectation unmet.
- Reject a target outside the legal record: neither state nor federal status is silently repaired.

A target/authority violation, early private-message exposure, unexplained loss of received memory, or a physical/legal effect attributed to the participant rather than its environment falsifies this contract. A missing consequential authority requires a semantic successor, not an extra backend exception.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, or counterfactual choices. Court adjudication, damages, settlement implementation, and state legal authority. A successor is required if new admissible dataset content changes the represented authority, actor cardinality, or information boundary. The anchors in Section 3 are the complete Draft basis for this parent.
