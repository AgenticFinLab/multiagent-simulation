# East Palestine Train Derailment scenario

## 1. Model overview

This Scenario turns the fully exposed `H2EPR-0196` Draft into an eleven-coordinate, dataset-conditioned response process. Its semantic parents are the seven active decision units, participant registries, and Source Profile. Rule execution is a deterministic construction baseline; the supported claim is engineering closure and a bounded generated-process reading.

## 2. Event boundary and process coverage

The opening world contains the derailment at `S1/E1`. Participant choices cover
notification, evacuation instruction and acknowledgement, controlled-release
instruction, preliminary investigation, return advice, concern reports, cleanup
oversight and characterization records, civil filings, and settlement
announcements through `S4/E8`. A notification changes knowledge records, not
accident occurrence. Physical burn/exposure dynamics, medical outcomes, court
adjudication, completed remediation, executed payments, and post-Draft aftermath
are outside the environment.

## 3. Dataset basis, exposure, and time boundary

The only inputs are the sealed `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json` paths in the Source Profile. The full Draft is exposed. Its seven participant IDs and 26 appearances are rostered exactly, while relation rows with inconsistent directions are not copied as authority. Runtime observations never reveal later coordinates early.

## 4. Temporal structure and exogenous inputs

Eleven logical coordinates preserve Draft episode navigation and earliest
availability boundaries without calibrating elapsed calendar time. Windowed
choices may remain inactive or occur later when their information arrives.
Tick labels describe author-selected opportunities; they are not backend inputs
or independently emerged historical stages. The final coordinate drains notices
sent at c10. The derailment is an exogenous opening fact; inactive response
records and an unreported operator notification are structural starting choices.
No hidden scheduled event or external data feed supplies missing decisions.

## 5. Participant assembly and causal ownership

Six named organizational/command Agents own bounded public choices; the resident Population owns aggregate acknowledgement and reporting choices. The environment owns all state effects. MASim owns route lifecycle, reducer ordering, trace, and seals. Legal proceedings and cleanup are stateful processes only after an eligible actor emits the initiating intent.

## 6. World, institutions, relationships, and resources

Twelve public fields describe the already-derailed incident, its notification,
evacuation, controlled-release instruction, investigation, community response,
cleanup, federal/state filings, and two settlement announcements. The
`hazard_control.status=instruction_recorded` value means an operational command
was recorded, not that hazards are controlled. Each field has one environment
update authority. Distinct concurrent writes conflict; identical set writes may
coexist deterministically. Chemical quantities, money, and medical states are
not modeled conservation systems.

## 7. Observation and communication routing

Actors see sealed public prestate, their newly delivered messages, outgoing
pending lifecycles, and trace-derived received/own-action memory. A recipient
cannot inspect a private message while it is pending. Retained messages preserve
their receipt tick; own current results enter memory at the next coordinate.
All eleven routes select one-tick latency as an uncalibrated transport assumption.
EPA can combine the response instruction and health report even when they arrive
at different ticks; DOJ can retain a notice while its later filing window is closed.

## 8. Intent, adjudication, lifecycle, and result

Fourteen non-default intents and `no_op` have exact actors, targets, parameter domains, preconditions, and effects. The backend proposes; the environment admits or rejects; the reducer commits deltas; MASim routes accepted-source messages. Invalid authority, target, parameter, precondition, or conflicting write returns a typed rejected disposition without partial hidden repair.

## 9. Configuration, variants, termination, and identity

The shared configuration owns clock, initial state, routes, observation, and
finite-horizon selection. Backend configuration owns the selected policy within
the declared choice surface. Each Rule row has an inclusive availability window
and a unique actor priority; it completes once accepted, waits on missing
information, and retries a rejection only after observed information changes.
Scenario outcome expectations summarize the selected baseline but do not gate
validity. Completion requires horizon accounting, exact replay of the actual
state, valid seals/graph, and zero unresolved transport, even if a filing or
settlement remains absent. Semantic changes require new identities and fresh
downstream evidence at the same stable paths.

## 10. Worked cases, falsification, and limitations

- A missing incident alert can leave evacuation inactive without undoing the opening derailment.
- A recorded controlled-release instruction may support return advice but establishes no safety finding.
- EPA can retain the response instruction from c04 and combine it with a later c06 health report. Requiring those two inputs is an authored dependency, not a legal prerequisite established by the dataset.
- DOJ retains an early notice but cannot act before the legal window. Removing the notice may leave its descriptive filing expectation unmet in an otherwise valid run.
- A municipal settlement record requires a routed offer; no payment occurs in the modeled environment.

The Draft contains direction/role inconsistencies in relation and transaction
rows. Actor actions support the bounded authorities; those defective edges are
not copied as causal truth. Opening operator notification, notice-to-filing and
report-to-oversight dependencies, calendar compression, and single-interface
organizations are explicit construction assumptions. Unauthorized state writes,
early private information, lost memory, or unreplayable state falsify the
contract. The result supports dataset-conditioned engineering and descriptive
process analysis, not historical fit, calibration, causality, or scientific validity.
