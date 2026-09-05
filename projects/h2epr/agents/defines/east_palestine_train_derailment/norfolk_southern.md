# Norfolk Southern decision interface

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `norfolk_southern` — Norfolk Southern decision interface |
| Benchmark event and interval | `H2EPR-0196`; 2023-02-03 through the Draft's 2025-01-28 endpoint |
| Represented decision interface | the railroad organization's incident notification, cleanup-response, and settlement-announcement choices |
| Source participant IDs | `P_1` |
| Primary decision situations | reporting the derailment, acting on a cleanup directive, and announcing exposed settlement steps |
| Decision cadence | One sealed decision at every logical coordinate; `no_op` when no declared situation applies |
| State authority | Declarative environment and authoritative reducer |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Benchmark participant and representation

This Agent represents the railroad organization's incident notification, cleanup-response, and settlement-announcement choices. It treats the named organization or coordinated command as one public decision interface and does not synthesize internal staff, private deliberation, or undisclosed authority. It excludes physical causation, regulator findings, court decisions, and proof that a promised remedy occurred. A successor must split or narrow the Agent when the dataset supports independently acting internal units whose choices change the process.

## 3. Dataset basis and provenance

The source participant appears at the following complete Draft anchors. These anchors establish reported role and timing, not historical verification. Frozen evidence remains a sealed contextual input and no external research is used.

- `draft_epg:S1/E1/P_1`
- `draft_epg:S1/E2/P_1`
- `draft_epg:S2/E3/P_1`
- `draft_epg:S2/E4/P_1`
- `draft_epg:S3/E5/P_1`
- `draft_epg:S3/E6/P_1`
- `draft_epg:S4/E7/P_1`
- `draft_epg:S4/E8/P_1`

## 4. Event role, relationships, and authority

The derailment is already present in the opening world. The operator can report it, wait for an EPA cleanup directive before recording characterization work, and announce the exposed class-settlement step after the represented legal filings. These are separate choices. A notification never causes the derailment, and an announcement never transfers compensation.

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

At the opening, `report_derailment` changes only `incident.notification_status`. An EPA directive received at an earlier tick remains available for `advance_cleanup`; an undelivered directive does not. `announce_class_settlement` has a later availability boundary and requires the two public filing records. The Rule policy chooses these actions once, or waits while their information is missing. Its reporting chain and filing-to-settlement dependency are authored assumptions rather than inferred corporate deliberation.

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

- Remove the EPA directive: the railroad can retain its incident notification while cleanup remains open.
- Delay that directive inside the cleanup window: the choice can reopen without moving the opening derailment.
- Reject an invalid cleanup target: the next observation contains that rejection, not a fabricated completed action.
- A settlement notice leaves payment execution and individual receipt unmodeled.

A target/authority violation, early private-message exposure, unexplained loss of received memory, or a physical/legal effect attributed to the participant rather than its environment falsifies this contract. A missing consequential authority requires a semantic successor, not an extra backend exception.

## 10. Limitations and source anchors

The dataset does not expose internal decision records, calibrated behavior, or counterfactual choices. Physical causation, regulator findings, court decisions, and proof that a promised remedy occurred. A successor is required if new admissible dataset content changes the represented authority, actor cardinality, or information boundary. The anchors in Section 3 are the complete Draft basis for this parent.
