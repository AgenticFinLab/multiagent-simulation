# East Palestine residents

## 1. Model overview

| Field | Account |
|---|---|
| Population ID and name | `east_palestine_residents` — East Palestine residents |
| Benchmark event and interval | `H2EPR-0196`; 2023-02-03 through the Draft's 2025-01-28 endpoint |
| Choice unit | Aggregate resident response represented by one deterministic baseline decision per coordinate |
| Source participant IDs | `P_2` |
| Runtime representation | Population |
| Primary decision situations | acknowledging evacuation, reporting health concerns, and reporting persistent impacts |
| Dataset exposure and scope | Full Draft exposed; dataset-only construction baseline |

## 2. Population scope and representation

The population covers residents represented by `P_2` across the Draft. The executable baseline aggregates them into one response surface because the dataset contains no stable individual identifiers or microdata. It excludes emergency workers, public authorities, and people outside the represented resident group. A successor must split this population if admissible data introduce distinct resident units whose choices or information materially diverge.

## 3. Dataset basis and provenance

The Draft directly exposes evacuation, reported symptoms or concerns, displacement, and settlement relevance at the anchors below. It does not expose a resident-level sampling frame, distribution, diagnosis, or causal estimate. Frozen evidence supplies context only through the sealed dataset input; no external material is added.

- `draft_epg:S1/E1/P_2`
- `draft_epg:S1/E2/P_2`
- `draft_epg:S2/E3/P_2`
- `draft_epg:S2/E4/P_2`
- `draft_epg:S3/E5/P_2`
- `draft_epg:S4/E7/P_2`
- `draft_epg:S4/E8/P_2`

## 4. Event role and relationships

Residents receive routed evacuation, return, and settlement notices and may emit bounded aggregate reports. Authorities and the environment retain delivery, safety, cleanup, legal, and settlement-effect authority. The model does not turn public concern into a verified environmental or medical finding.

## 5. Decision situations, observations, and state

| Observation | Producer and availability | Missing or stale rule | Use |
|---|---|---|---|
| public state | Runtime at coordinate open | Fail if absent | Read evacuation and response status |
| delivered messages | MASim transport before decisions | Empty list when none are due | React only to routed notices |
| pending lifecycles | MASim transport at every coordinate | Empty list when none exist | Avoid treating pending delivery as receipt |

Persistent world fields are environment-owned. Backend reasoning and unobserved individual variation are transient and are not written into authoritative state.

## 6. Choice model and heterogeneity

The admissible intents are `acknowledge_evacuation`, `report_health_concerns`, `report_persistent_impacts` plus `no_op`. Heterogeneity may concern evacuation compliance, trust, exposure, symptoms, displacement, and claim participation, but the current Rule baseline selects no distributional parameters. Missing notices permit `no_op`; a delivered notice does not prove agreement. Correlated or subgroup behavior requires an explicitly configured successor.

## 7. Intent and environment-result boundary

The population emits typed reports or acknowledgements. The environment checks target, state preconditions, timing, and authority and then records accepted or rejected dispositions. Message delivery and any downstream public action are separate lifecycles; residents never author their own medical validity or settlement outcome.

## 8. Configuration and uncertainty

Logical timing, aggregation level, communication latency, and the deterministic Rule row are selected by configuration. Meaningful sensitivity axes include subgroup splitting, delayed acknowledgement, and absent return advice. No exact preference, risk, or compliance parameter belongs to this semantic identity.

## 9. Worked cases and falsification

- A delivered evacuation order permits acknowledgement; an undelivered order does not.
- A return advisory may be followed by a concern report without asserting that return was safe or unsafe.
- Persistent concern can be reported after earlier concern state; it cannot overwrite legal or cleanup fields.
- Splitting the population into materially different subgroups should change only a successor configuration or semantic parent, never hidden backend state.

The model is falsified as a representation contract if a resident unit needs distinct authority or information that aggregation makes causally decisive.

## 10. Limitations and source anchors

The principal losses are aggregation, missing microdata, and the absence of verified causal health labels. Individual medical diagnoses, a representative preference distribution, and verified causal attribution of symptoms. A successor is required when a supported analysis needs individual trajectories, subgroup weights, or new source participant identities. The anchors listed in Section 3 are the complete Draft basis for this parent.
