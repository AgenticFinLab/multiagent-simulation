# Scenario Definition template

Keep the ten modules in this order.

## 1. Model overview

Identify event, simulation objective, source exposure, semantic parents,
window, clock, active decision units, environment, and supported claim.

## 2. Event boundary and process coverage

State opening conditions, endogenous interval, excluded precursors and
aftermath, and the process transitions the simulation represents. Do not add a
per-event research question.

## 3. Dataset basis, exposure, and time boundary

Record allowed dataset files, stable anchors, known conflicts, Draft exposure,
and information that may never enter runtime observations.

## 4. Temporal structure and exogenous inputs

Define logical time, tick semantics, ordering, scheduled inputs, latency,
expiry, and termination. Distinguish opening context from later exogenous
events.

## 5. Participant assembly and causal ownership

Map Agents, populations, world-state entities, and institutional processes to
the state and transitions they own. Scenario may not absorb an autonomous
choice merely to reduce actor count.

## 6. World, institutions, relationships, and resources

Define authoritative fields, owners, legal transitions, resource conservation,
authority checks, and relationship effects. Publish their executable projection
with the [Scenario Mechanism template](scenario-mechanism-template.md).

## 7. Observation and communication routing

Define observation producers, projections, recipient visibility, transport,
fanout, latency, missing/stale behavior, and prohibited information.

## 8. Intent, adjudication, lifecycle, and result

Define action/message admission, concurrency, failure routing, pending and
terminal states, environment effects, and reducer authority.

## 9. Configuration, variants, termination, and identity

List configurable dimensions and their domains. Selected values live in a
Scenario Configuration. Define semantic identity and successor rules.

## 10. Worked cases, falsification, and limitations

Exercise concurrency, resource contention, invalid authority, message delay,
and termination. State assumptions, omissions, and the process pattern that
would require revising the scenario.
