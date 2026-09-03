# SingHealth Data Breach — Scenario Definition

## 1. Model overview

This scenario compiles `H2EPR-0616` into the shared benchmark-simulation contract. It is a deterministic Rule construction practice based only on `event_spec`, `frozen_evidence`, and the fully exposed `draft_epg`.

## 2. Event boundary and process coverage

The process begins at the first exposed Draft episode and closes after the last declared action plus one terminal delivery barrier. It represents only the published participant actions, messages, state transitions, annotations, and termination invariants; omitted precursors, internal deliberation, magnitudes, and aftermath are not synthesized.

## 3. Dataset basis, exposure, and time boundary

Input discovery is direct-path only. Reference EPG, held-out suffixes, evaluation-only content, external research, and network retrieval are prohibited. Full Draft exposure is recorded in every downstream package and run.

## 4. Temporal structure and exogenous inputs

- tick 1: `singhealth.c01` → S1/E1 — persistent access
- tick 2: `singhealth.c02` → S1/E2 — concentrated exfiltration
- tick 3: `singhealth.c03` → S2/E3 — initial detection
- tick 4: `singhealth.c04` → S2/E3 — verification and containment
- tick 5: `singhealth.c05` → S2/E4 — public response
- tick 6: `singhealth.c06` → S3/E5 — inquiry establishment
- tick 7: `singhealth.c07` → S3/E5 — root-cause findings
- tick 8: `singhealth.c08` → S3/E6 — regulatory penalties
- tick 9: `singhealth.c09` → S4/E7 — reform implementation
- tick 10: `singhealth.c10` → S4/E8 — public attribution
- tick 11: `singhealth.c11` → S4/E8 — terminal delivery barrier

Logical coordinates preserve Draft stage and episode identity while allowing more than one causal barrier inside an episode. The baseline introduces no undeclared exogenous event stream.

## 5. Participant assembly and causal ownership

- `committee_of_inquiry` — SingHealth Data Breach Committee of Inquiry (agent)
- `ihis` — Integrated Health Information Systems (agent)
- `lee_hsien_loong` — Lee Hsien Loong (agent)
- `moh` — Singapore Ministry of Health (agent)
- `pdpc` — Personal Data Protection Commission (agent)
- `singhealth` — Singapore Health Services (agent)
- `symantec` — Symantec (agent)
- `whitefly` — Whitefly (agent)

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
