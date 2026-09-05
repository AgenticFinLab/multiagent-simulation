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

At coordinate open, the runtime supplies sealed public state, newly delivered
messages, this actor's outgoing pending lifecycles, and structured memory of
received messages and its own prior dispositions. The first memory is empty.
A previous receipt remains available with its original receipt tick; absence
is not inferred receipt. Pending private traffic is invisible to its recipient.
Same-tick results become known at the next coordinate. No historical stage
label, later Draft fact, opaque generated identifier, or other actor's private
result is a decision input.

## 6. Choice model and heterogeneity

The population can acknowledge a received evacuation order, report health
concerns after return advice, report persistent concerns in the later review
interval, or wait. These report choices are separate from compliance, actual
exposure, diagnosis, displacement measurement, and compensation receipt.

The selected Rule rows use retained notices and the population's earlier
reported state. They complete once accepted and may wait inside their own
windows. The return-advice dependency is a modeling choice; it is not evidence
that residents could report symptoms only after official advice. No microdata
support a distribution over compliance, trust, exposure, or claim participation,
so this remains one aggregate reporting interface. A subgroup choice would need
new semantic support rather than hidden per-person backend behavior.

## 7. Intent and environment-result boundary

The population emits typed reports or acknowledgements. The environment checks target, state preconditions, timing, and authority and then records accepted or rejected dispositions. Message delivery and any downstream public action are separate lifecycles; residents never author their own medical validity or settlement outcome.

## 8. Configuration and uncertainty

Shared configuration sets aggregate scope, logical opportunities, and routing;
Rule configuration selects message/state guards, priorities, and bounded waiting.
These choices can test delayed or absent notices without fabricating individual
preferences. A rejected report is preserved in next-coordinate own-action memory;
an accepted report is not repeated automatically. New subgroup weights or
independent resident trajectories require source support and a semantic successor.

## 9. Worked cases and falsification

- A delayed evacuation order can still be acknowledged inside the response window; a missing order stays missing.
- Return advice received previously remains known when a later concern report is considered.
- Missing return advice leaves initial concern reporting inactive under this policy; the resulting open record is reportable, not a failed checksum.
- Persistent concerns require an earlier report and a later availability boundary, not a new medical finding.
- Individual symptom trajectories, distributional compliance, and verified causal attribution cannot be inferred from the aggregate record.

The representation needs a successor if materially different resident groups require distinct information, authority, or response states.

## 10. Limitations and source anchors

The principal losses are aggregation, missing microdata, and the absence of verified causal health labels. Individual medical diagnoses, a representative preference distribution, and verified causal attribution of symptoms. A successor is required when a supported analysis needs individual trajectories, subgroup weights, or new source participant identities. The anchors listed in Section 3 are the complete Draft basis for this parent.
