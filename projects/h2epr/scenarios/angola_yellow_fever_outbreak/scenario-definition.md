# Angola Yellow Fever Outbreak of 2016 scenario

## 1. Model overview

This Scenario turns the fully exposed `H2EPR-0551` Draft into a 20-coordinate, dataset-conditioned outbreak-response process. Its semantic parents are eight active decision units, two world-state participant dispositions, the shared registries, and the Source Profile. Rule execution is a deterministic construction baseline supporting engineering closure and a bounded generated-process reading.

## 2. Event boundary and process coverage

The opening state precedes the represented detection in Luanda. Endogenous transitions cover dual laboratory reports, confirmation recording, case-surge reporting, local vaccination, cross-border risk, two emergency assessments, scaled response, progress updates, Uganda's related outbreak-end declaration, and continuing surveillance. Individual infection, clinical treatment, mosquito dynamics, vaccine stock conservation, dose administration, mortality, effectiveness, and any later surveillance outcome lie outside the world model.

## 3. Dataset basis, exposure, and time boundary

The only inputs are the sealed `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`. The full Draft is exposed. All 10 participant IDs and 31 appearances are rostered; P_3's scope drift and contradictory relation rows remain explicit source limitations. Reference, held-out, evaluation-only, network, and external-research content never enters observations or construction.

## 4. Temporal structure and exogenous inputs

Logical coordinates preserve E1 through E9 order without calibrating calendar duration. The twentieth coordinate drains the final one-tick surveillance messages. The affected and imported-case groups mapped to world state motivate reported conditions but do not become hidden scheduled actors. No undisclosed outbreak, case count, or resource feed is injected during runtime.

## 5. Participant assembly and causal ownership

Seven named organizational or committee Agents own bounded public choices. One Population owns aggregate campaign participation under an explicitly unstable geographic scope. P_7 and P_10 remain world-state populations because the Draft assigns them affected status rather than supported autonomous decisions. The environment owns all field changes; MASim owns message lifecycle, reducer order, trace, and seals.

## 6. World, institutions, relationships, and resources

Twenty-six public fields distinguish detection, two laboratory reports, confirmation, surge reporting, two campaign phases, risk, meetings, briefings, assessments, national response and progress, Uganda's declaration, and four surveillance states. These are process labels. They do not measure infections, doses, stock, immunity, transmission, or successful containment. Distinct concurrent writes conflict; identical set writes may coexist under semantic ordering.

## 7. Observation and communication routing

Every actor sees the same sealed public prestate plus messages delivered to it and its pending lifecycle references. Sample referrals, laboratory confirmations, campaign notices, briefings, assessments, guidance, progress updates, declarations, and surveillance updates use explicit directed routes. Missing delivery yields an empty observation; full-Draft exposure never makes later information visible early.

## 8. Intent, adjudication, lifecycle, and result

Twenty-six non-default intents and `no_op` have exact actors, targets, parameter domains, preconditions, and effects. The backend proposes; the environment admits or rejects; the reducer commits deltas; MASim routes messages emitted by accepted source actions. Invalid authority, target, payload, precondition, route, or conflicting write produces typed evidence without partial repair.

## 9. Configuration, variants, termination, and identity

Shared configuration selects coordinates, opening values, routes, observation timing, and termination. Rule configuration selects decisions only. Semantic identity changes with actorization, information, authority, field meaning, or mechanism; selected timing and rows change configuration identity. Termination requires all 26 configured process states and zero unresolved transport, while surveillance remains deliberately ongoing.

## 10. Worked cases, falsification, and limitations

- Without a sample-referral message, neither laboratory Rule row fires.
- WHO records initial confirmation only after both independent laboratory reports.
- Country briefings and committee assessment remain distinct lifecycles.
- Angola and DRC update separate response fields concurrently without conflict.
- A campaign-participation intent does not establish dose receipt or coverage.
- The terminal barrier closes transport while surveillance fields remain ongoing.

The Scenario is falsified if a consequential source choice is hidden as world state, P_3's scope drift is treated as stable microdata, a Draft relation row overrides declared authority, future information leaks backward, or replay cannot reproduce each delta. The open-ended source boundary and absence of epidemiological calibration remain explicit.
