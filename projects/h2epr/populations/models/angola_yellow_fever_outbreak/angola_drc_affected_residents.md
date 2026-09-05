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

At coordinate open, the actor receives sealed public state, its newly delivered
messages, only its outgoing pending lifecycles, and structured received/own-action
memory. Received messages retain their receipt tick. Its own accepted, rejected,
and no-op results become available at the next coordinate. Private pending
messages are not exposed to a recipient; absent information stays absent.
Runtime clock coordinates contain no historical stage label or future Draft
fact. Memory is evidence-derived, not an invented private deliberation.

## 6. Choice model and heterogeneity

The Population can emit local or scaled campaign-participation requests, or
wait. An earlier received campaign notice remains available within the selected
window; national response records remain separate prerequisites for the scaled
choice. Accepted participation is recorded once and does not prove a dose was
administered. Location, eligibility, access, trust, and willingness are plausible
heterogeneity dimensions, but the three admitted inputs supply no distributions
or stable individual panel. This is one aggregate response surface with explicit
Luanda-to-Angola-to-Angola/DRC scope drift, not a micro-population.

## 7. Intent and environment-result boundary

The Population may request local or scaled campaign participation and send an aggregate participation report. Route delivery, eligibility, stock availability, administration, coverage, adverse effects, and health outcomes remain environment-owned or unmodeled.

## 8. Configuration and uncertainty

Aggregation scope, logical timing, route latency, and Rule selection belong to configuration. Country split, refusal, delay, or partial participation are sensitivity dimensions. No population count, probability, preference, or vaccine-effect parameter belongs to this semantic identity.

## 9. Worked cases and falsification

- Deliver scaled guidance at c13: the Population retains it until the c14 response opportunity.
- Withhold one national response record: the selected scaled choice remains pending or rejected, without fabricated coverage.
- Delay a notice inside its window: the Population can respond later; a notice still pending is invisible.
- A rejected request appears in next-coordinate own-action memory. A clock tick alone does not turn it into acceptance.
- Distinct country information or subgroup uptake requires a supported semantic successor rather than hidden individual states.

The representation fails if one aggregate record obscures a material independent choice needed by the intended simulation.

## 10. Limitations and source anchors

The principal losses are geographic scope drift, aggregation, and absent microdata. The model excludes individual infection, mortality, eligibility, dose receipt, coverage, medical outcome, and a stable micro-population spanning both countries. The anchors listed in Section 3 are the complete Draft basis; no external evidence or Reference content is used.
