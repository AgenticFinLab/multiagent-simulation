# East Palestine Train Derailment scenario

## 1. Model overview

This Scenario turns the fully exposed `H2EPR-0196` Draft into an eleven-coordinate, dataset-conditioned response process. Its semantic parents are the seven active decision units, participant registries, and Source Profile. Rule execution is a deterministic construction baseline; the supported claim is engineering closure and a bounded generated-process reading.

## 2. Event boundary and process coverage

The opening state precedes the derailment reported at `S1/E1`. Endogenous transitions cover incident notification, evacuation, controlled release, preliminary investigation, return advice, concern reporting, cleanup oversight, civil filings, anniversary concern, and exposed settlement announcements through `S4/E8`. Physical derailment mechanics, individual medical outcomes, court adjudication, cleanup effectiveness, payment execution, and post-Draft aftermath are outside the world model.

## 3. Dataset basis, exposure, and time boundary

The only inputs are the sealed `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json` paths in the Source Profile. The full Draft is exposed. Its seven participant IDs and 26 appearances are rostered exactly, while relation rows with inconsistent directions are not copied as authority. Runtime observations never reveal later coordinates early.

## 4. Temporal structure and exogenous inputs

Logical ticks preserve the ordering of `S1/E1` through `S4/E8` but do not calibrate elapsed calendar duration. A final `S4/E8` barrier drains the last one-tick settlement notice. The initial operating train, inactive response processes, and unreported community state are opening context. The Rule baseline introduces no hidden scheduled event or external data feed.

## 5. Participant assembly and causal ownership

Six named organizational/command Agents own bounded public choices; the resident Population owns aggregate acknowledgement and reporting choices. The environment owns all state effects. MASim owns route lifecycle, reducer ordering, trace, and seals. Legal proceedings and cleanup are stateful processes only after an eligible actor emits the initiating intent.

## 6. World, institutions, relationships, and resources

Eleven public fields represent incident, evacuation, hazard control, investigation, community response, cleanup, federal and state legal status, and two settlement announcements. Each has one typed domain and environment update authority. The Scenario models status transitions, not chemical quantities, money conservation, medical diagnoses, or institutional correctness. Distinct concurrent writes conflict; identical set writes may coexist deterministically.

## 7. Observation and communication routing

All actors see the same sealed public prestate plus only messages delivered to them and their pending lifecycle references. Incident alerts, evacuation orders, response updates, investigation notices, return advice, concern reports, cleanup directives, impact updates, settlement offers, and settlement notices travel on explicit directed routes. Missing delivery yields an empty observation and blocks message-gated Rule rows.

## 8. Intent, adjudication, lifecycle, and result

Fourteen non-default intents and `no_op` have exact actors, targets, parameter domains, preconditions, and effects. The backend proposes; the environment admits or rejects; the reducer commits deltas; MASim routes accepted-source messages. Invalid authority, target, parameter, precondition, or conflicting write returns a typed rejected disposition without partial hidden repair.

## 9. Configuration, variants, termination, and identity

The shared configuration selects coordinates, opening values, routes, visibility, and termination. Backend configuration selects only Rule decisions. Semantic identity changes when actors, state meaning, intent authority, or process boundary changes; selected timing or policy rows change configuration identity. Termination requires all eleven final field values and zero unresolved transport.

## 10. Worked cases, falsification, and limitations

- Without an incident alert, evacuation and investigation message guards do not fire.
- A return advisory is routed only after hazard-control completion; it does not validate safety.
- Cleanup begins only after both the response update and resident health report arrive at EPA.
- Federal and state civil filings update different fields at one coordinate without conflict.
- A municipal settlement record requires the routed settlement offer; the final barrier proves delivery closure.

The Scenario is falsified as an adequate process contract if a consequential autonomous participant is hidden in the environment, if a later Draft fact leaks into an earlier observation, or if any declared terminal state cannot be replayed from trace. Calendar compression, organizational aggregation, and the Draft's evidentiary limitations remain explicit.
