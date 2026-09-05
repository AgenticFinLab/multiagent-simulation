# Angola Yellow Fever Outbreak of 2016 scenario

## 1. Model overview

This Scenario turns the fully exposed `H2EPR-0551` Draft into a 20-coordinate, dataset-conditioned outbreak-response process. Its semantic parents are eight active decision units, two world-state participant dispositions, the shared registries, and the Source Profile. Rule execution is a deterministic construction baseline supporting engineering closure and a bounded generated-process reading.

## 2. Event boundary and process coverage

The opening contains institutional detection and response records, not a
susceptible/infected population simulation. Choices cover dual laboratory
statements, confirmation recording, case-surge reports, local campaigns,
cross-border risk documentation, two committee reviews, response records,
progress statements, Uganda's declaration, and continuing surveillance.
Individual infection, diagnosis, vector dynamics, vaccine stock, dose
administration, mortality, intervention effectiveness, and later surveillance
outcomes are outside the world model.

## 3. Dataset basis, exposure, and time boundary

The only inputs are the sealed `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`. The full Draft is exposed. All 10 participant IDs and 31 appearances are rostered; P_3's scope drift and contradictory relation rows remain explicit source limitations. Reference, held-out, evaluation-only, network, and external-research content never enters observations or construction.

## 4. Temporal structure and exogenous inputs

Logical coordinates preserve E1 through E9 order without calibrating calendar duration. The twentieth coordinate drains the final one-tick surveillance messages. The affected and imported-case groups mapped to world state motivate reported conditions but do not become hidden scheduled actors. No undisclosed outbreak, case count, or resource feed is injected during runtime.

## 5. Participant assembly and causal ownership

Seven named organizational or committee Agents own bounded public choices. One Population owns aggregate campaign participation under an explicitly unstable geographic scope. P_7 and P_10 remain world-state populations because the Draft assigns them affected status rather than supported autonomous decisions. The environment owns all field changes; MASim owns message lifecycle, reducer order, trace, and seals.

## 6. World, institutions, relationships, and resources

Twenty-six public record fields distinguish detection, two laboratory reports, confirmation, surge reporting, two campaign phases, risk, meetings, briefings, assessments, national response records and progress, Uganda's declaration, and four surveillance states. These are process labels. They do not measure infections, doses, stock, immunity, transmission, or successful containment. Distinct concurrent writes conflict; identical set writes may coexist under semantic ordering.

## 7. Observation and communication routing

Actors receive sealed public prestate, their delivered messages, outgoing
pending lifecycles, and trace-derived received/own-action memory. The recipient
cannot see a private pending message. Retained reports preserve receipt time;
the actor's current result becomes known at the next coordinate. All 17 routes
select one-tick latency. WHO can combine two laboratory or country reports
across ticks, and the Population can retain c13 guidance until c14. This removes
arrival-time alignment without changing the exposed earliest decision intervals.

## 8. Intent, adjudication, lifecycle, and result

Twenty-six non-default intents and `no_op` have exact actors, targets, parameter domains, preconditions, and effects. The backend proposes; the environment admits or rejects; the reducer commits deltas; MASim routes messages emitted by accepted source actions. Invalid authority, target, payload, precondition, route, or conflicting write produces typed evidence without partial repair.

## 9. Configuration, variants, termination, and identity

Shared configuration selects the 20 opportunities, opening records, routes,
and finite horizon. Rule configuration selects bounded waiting windows and
priorities; accepted rows do not repeat, and rejected rows reconsider only after
information changes. All rows end by c19, leaving c20 for delivery accounting.
The 26 outcome expectations are descriptive, not required endpoint equalities.
Actual trace, seals, replay, graph coverage, and zero unresolved transport remain
mandatory even when a review or campaign response stays open. Any changed
authority, information, or state meaning creates a new package identity and
requires fresh downstream evidence at the stable current paths.

## 10. Worked cases, falsification, and limitations

- A missing referral prevents a laboratory report; differently timed lab reports remain combinable in WHO memory.
- Missing country briefings can leave an assessment pending. The finite run may still produce a valid replay and graph.
- A committee assessment, WHO guidance, country response record, and Population participation are four distinct products.
- Uganda's declaration is independent of the WHO assessment; `not_declared` is not an assertion of early active infection.
- Public response records do not prove vaccination, absence of transmission, or successful containment.
- The terminal barrier accounts for transport while surveillance remains an open process.

The committee statement content is selected from the exposed Draft; this
baseline does not implement a risk classifier choosing among all possible
assessments. Paired-message requirements and ordered windows are authored
dependencies, not recovered internal institutional protocols. P_3 scope drift,
P_7 travel aggregation, contradictory Draft relations, and the open-ended source
boundary remain explicit losses. Unauthorized authority, early private
information, lost received memory, or unreplayable effects falsify the contract.
