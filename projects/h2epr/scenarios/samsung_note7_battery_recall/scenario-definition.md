# Samsung Galaxy Note7 Battery Recall — Scenario Definition

## 1. Model overview

This scenario compiles `H2EPR-0481` into the shared benchmark-simulation contract. It is a deterministic Rule construction practice based only on `event_spec`, `frozen_evidence`, and the fully exposed `draft_epg`.

## 2. Event boundary and process coverage

The process begins at the first exposed Draft episode and closes after the last declared action plus one terminal delivery barrier. It represents only the published participant actions, messages, state transitions, annotations, and termination invariants; omitted precursors, internal deliberation, magnitudes, and aftermath are not synthesized.

## 3. Dataset basis, exposure, and time boundary

Input discovery is direct-path only. Reference EPG, held-out suffixes, evaluation-only content, external research, and network retrieval are prohibited. Full Draft exposure is recorded in every downstream package and run.

## 4. Temporal structure and exogenous inputs

- tick 1: `note7.c01` → S1/E1 — global launch
- tick 2: `note7.c02` → S1/E1 — sales and initial supply
- tick 3: `note7.c03` → S1/E2 — initial incident reports
- tick 4: `note7.c04` → S1/E2 — testing and shipment delay
- tick 5: `note7.c05` → S2/E3 — partial global recall
- tick 6: `note7.c06` → S2/E4 — China test-unit requirement
- tick 7: `note7.c07` → S2/E4 — China test-unit recall
- tick 8: `note7.c08` → S2/E5 — domestic battery supply
- tick 9: `note7.c09` → S2/E5 — China incidents and supplier denial
- tick 10: `note7.c10` → S2/E5 — external-heating claim
- tick 11: `note7.c11` → S2/E5 — China-market apology
- tick 12: `note7.c12` → S3/E6 — flight fire report
- tick 13: `note7.c13` → S3/E6 — production suspension
- tick 14: `note7.c14` → S3/E7 — production and sales termination
- tick 15: `note7.c15` → S4/E8 — consumer litigation
- tick 16: `note7.c16` → S4/E8 — internal investigation
- tick 17: `note7.c17` → S4/E8 — independent findings
- tick 18: `note7.c18` → S4/E9 — cause report publication
- tick 19: `note7.c19` → S4/E9 — terminal delivery barrier

Logical coordinates preserve Draft stage and episode identity while allowing more than one causal barrier inside an episode. The baseline introduces no undeclared exogenous event stream.

## 5. Participant assembly and causal ownership

- `aqsiq` — AQSIQ (agent)
- `atl` — Amperex Technology Limited (agent)
- `china_consumers` — Chinese mainland regular Note7 purchasers (population)
- `global_consumers` — Global early Note7 purchasers (population)
- `independent_investigators` — Independent third-party investigation consortium (agent)
- `samsung` — Samsung Electronics (agent)
- `samsung_sdi` — Samsung SDI (agent)
- `southwest_airlines` — Southwest Airlines (agent)

Every Draft participant is retained in the roster. Participants without a decision boundary become explicit world state or institutional process mappings rather than disappearing.

## 6. World, institutions, relationships, and resources

State is normalized as `state_version` plus typed `entities`. Event-specific behavior is declarative: state fields, intent handlers, preconditions, effects, conflict policy, annotations, and termination invariants are pinned in `scenario-mechanism.json`. The MASim reducer is the sole commit authority.

## 7. Observation and communication routing

All active actors observe one sealed prestate per coordinate, their permitted action types, delivered messages, and pending message lifecycles. No actor sees a same-coordinate write before deciding.

Routes are explicit and have one-tick latency. A terminal delivery coordinate follows the last action so every published message reaches a terminal disposition before the run closes.

## 8. Intent, adjudication, lifecycle, and result

The participant interface declares eligibility; the scenario mechanism owns preconditions and effects; the MASim reducer owns authoritative admission and atomic state changes. The environment rejects unknown actors, targets, fields, parameters, and conflicting writes.

## 9. Configuration, variants, termination, and identity

The run must consume every coordinate, satisfy all declared terminal state invariants, replay to the same final state, cover every trace record in Generated EPG, and leave zero unresolved messages. These checks establish engineering and method closure only.

Shared configuration owns the timeline, opening values, routes, exposure, and termination flags. Backend configuration owns Rule rows. Semantic changes require a new package identity and rematerialized backend comparison group.

## 10. Worked cases, falsification, and limitations

- Unknown actors, targets, fields, parameters, routes, and stale implementation hashes fail closed.
- Distinct concurrent writes to one field reject the later intent without partial effects; identical sets are admitted as idempotent no-effect actions.
- Delayed messages must reach a terminal transport status before closeout.
- Any exposed transition requiring undeclared state or authority falsifies this definition and requires a successor.

Full Draft exposure and synthetic logical barriers preclude historical-fit, calibration, held-out, causal, scientific-validity, or universal-generality claims.
