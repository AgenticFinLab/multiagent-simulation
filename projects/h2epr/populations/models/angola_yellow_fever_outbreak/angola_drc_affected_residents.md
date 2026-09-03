# Angola and DRC affected residents

## 1. Model overview

| Field | Account |
|---|---|
| Population ID and name | `angola_drc_affected_residents` — Angola and DRC affected residents |
| Benchmark event and interval | `H2EPR-0551`; late December 2015 through the Draft's open-ended surveillance stage |
| Choice unit | Aggregate campaign-participation response under changing geographic scope |
| Source participant IDs | `P_3` |
| Runtime representation | One Population actor |
| Primary decision situations | responding to the initial Angola campaign and the later Angola-DRC scaled campaign |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Population scope and representation

The Draft reuses `P_3` for Luanda residents, Angola residents, and a combined Angola-DRC affected group. This model preserves that source identity as one aggregate runtime actor and makes the scope change explicit. It excludes imported case group `P_7` and Uganda group `P_10`, which have no supported choice boundary. A successor must split the Population if a comparison requires country-specific uptake or stable individual units.

## 3. Dataset basis and provenance

The following anchors expose affected-population status and vaccination receipt. They do not expose a sampling frame, individual choices, eligibility, refusal, dose counts, or causal outcomes. Treating campaign participation as an emitted intent is an executable structural assumption; the environment retains actual receipt and coverage authority.

- `draft_epg:S1/E1/P_3`
- `draft_epg:S2/E3/P_3`
- `draft_epg:S3/E6/P_3`

## 4. Event role and relationships

The Population receives campaign notices and may emit aggregate participation intents and reports. Angola, DRC, and WHO retain campaign organization and public reporting authority. Disease status, mortality, vaccine availability, allocation, and effectiveness remain world or institutional state.

## 5. Decision situations, observations, and state

| Observation | Producer and availability | Missing or stale rule | Use |
|---|---|---|---|
| public state | Runtime at coordinate open | Fail if absent | Observe campaign status |
| delivered messages | MASim transport before decisions | Empty when none are due | Respond only to routed campaign guidance |
| pending lifecycles | MASim transport | Empty when none exist | Keep request distinct from result |

Persistent fields record only aggregate participation status under environment authority. No hidden individual or medical state is generated.

## 6. Choice model and heterogeneity

The admissible intents are `participate_local_vaccination`, `participate_scaled_vaccination` plus `no_op`. Potential heterogeneity includes location, eligibility, access, trust, and willingness, but the dataset supplies no distributions. The current Rule baseline selects one aggregate participation path. Missing guidance permits `no_op`; a participation intent does not prove vaccination.

## 7. Intent and environment-result boundary

The Population may request local or scaled campaign participation and send an aggregate participation report. Route delivery, eligibility, stock availability, administration, coverage, adverse effects, and health outcomes remain environment-owned or unmodeled.

## 8. Configuration and uncertainty

Aggregation scope, logical timing, route latency, and Rule selection belong to configuration. Country split, refusal, delay, or partial participation are sensitivity dimensions. No population count, probability, preference, or vaccine-effect parameter belongs to this semantic identity.

## 9. Worked cases and falsification

- A delivered local campaign notice permits local participation; no notice permits `no_op`.
- Scaled guidance permits a later regional participation response without proving dose receipt.
- Environment denial leaves participation pending or rejected rather than fabricating coverage.
- Splitting Angola and DRC may change responses and therefore requires a successor population/configuration pair.

The model is falsified if one source subgroup acquires independent authority or observably different information that one aggregate interface cannot preserve.

## 10. Limitations and source anchors

The principal losses are geographic scope drift, aggregation, and absent microdata. The model excludes individual infection, mortality, eligibility, dose receipt, coverage, medical outcome, and a stable micro-population spanning both countries. The anchors listed in Section 3 are the complete Draft basis; no external evidence or Reference content is used.
