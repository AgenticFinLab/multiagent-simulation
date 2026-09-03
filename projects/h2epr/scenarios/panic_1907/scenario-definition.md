# Panic of 1907 — Scenario Definition

## 1. Model overview

This scenario compiles `H2EPR-0288` into the shared benchmark-simulation contract. It is a deterministic Rule construction practice based only on `event_spec`, `frozen_evidence`, and the fully exposed `draft_epg`.

## 2. Event boundary and process coverage

The process begins at the first exposed Draft episode and closes after the last declared action plus one terminal delivery barrier. It represents only the published participant actions, messages, state transitions, annotations, and termination invariants; omitted precursors, internal deliberation, magnitudes, and aftermath are not synthesized.

## 3. Dataset basis, exposure, and time boundary

Input discovery is direct-path only. Reference EPG, held-out suffixes, evaluation-only content, external research, and network retrieval are prohibited. Full Draft exposure is recorded in every downstream package and run.

## 4. Temporal structure and exogenous inputs

- tick 1: `panic.c01` → S1/E1 — failed corner
- tick 2: `panic.c02` → S1/E2 — affiliated-bank run
- tick 3: `panic.c03` → S1/E3 — clearing-house stabilization
- tick 4: `panic.c04` → S2/E4 — support request
- tick 5: `panic.c05` → S2/E4 — support denials
- tick 6: `panic.c06` → S2/E5 — suspension and trust run
- tick 7: `panic.c07` → S2/E6 — call-market seizure
- tick 8: `panic.c08` → S2/E6 — exchange-liquidity support
- tick 9: `panic.c09` → S3/E7 — clearing-house measures
- tick 10: `panic.c10` → S3/E8 — private bailout
- tick 11: `panic.c11` → S3/E9 — gold imports
- tick 12: `panic.c12` → S3/E10 — commission establishment
- tick 13: `panic.c13` → S3/E10 — commission recommendations
- tick 14: `panic.c14` → S3/E10 — Federal Reserve establishment
- tick 15: `panic.c15` → S3/E10 — terminal delivery barrier

Logical coordinates preserve Draft stage and episode identity while allowing more than one causal barrier inside an episode. The baseline introduces no undeclared exogenous event stream.

## 5. Participant assembly and causal ownership

- `affiliated_banks_cohort` — Heinze/Morse affiliated banks (population)
- `depositors_cohort` — General public bank depositors (population)
- `european_money_centers_cohort` — European money centers (population)
- `heinze` — F. Augustus Heinze (agent)
- `jp_morgan` — J.P. Morgan (agent)
- `knickerbocker_trust` — Knickerbocker Trust Company (agent)
- `member_banks_cohort` — New York Clearing House member banks (population)
- `morse` — Charles W. Morse (agent)
- `national_monetary_commission` — National Monetary Commission (agent)
- `nych` — New York Clearing House (agent)
- `other_trusts_cohort` — Other New York trust companies (population)
- `us_congress` — United States Congress (agent)

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
