# New York Clearing House member banks — Population Model

## 1. Model overview

| Field | Account |
|---|---|
| Semantic ID | `h2epr.0288.population.member_banks_cohort.v0.4` |
| Runtime actor | `member_banks_cohort` |
| Benchmark event | Panic of 1907 (`H2EPR-0288`) |
| Source participant | `P_12` — New York Clearing House Member Banks Group |
| Representation | `population` |
| Event role | liquidity recipients and implementers |
| Dataset exposure | Full Draft exposed; construction practice only |

## 2. Population scope and representation

This semantic parent retains the participant as an autonomous action-bearing boundary because one or more Draft episodes assign it an exposed transition. No member-bank-specific policy or reserves are modeled.

Runtime uses one unweighted aggregate choice unit for this cohort. The dataset provides no member-level count, weight, distribution, or microtrajectory from which heterogeneous agents could be sampled. A successor must split the cohort if later benchmark material supplies independently acting units; a named unit with distinct authority must instead become an Agent.

## 3. Dataset basis and provenance

Source anchors:

- `draft_epg:S3/E7/P_12`

These anchors are benchmark records, not independently verified history. The asset adds no external evidence or hidden participant state.

## 4. Event role and relationships

Role: liquidity recipients and implementers.

Authority boundary: May enact the declared convertibility restriction.

Routes and eligible targets are declared by the participant interface and shared configuration. Relationship status and event outcomes remain authoritative scenario state.

## 5. Decision situations, observations, and state

At each coordinate the runtime provides the same sealed public state, any actor-private projection, delivered messages, pending message lifecycles, and this actor's permitted intents. The definition grants no undeclared source access.

Unavailable observations are not reconstructed. Missing or stale information permits only an aggregate response that does not claim the absent fact, normally `no_op`. Pending transport remains pending until the runtime records a terminal lifecycle.

The environment, rather than the participant object, owns authoritative state. This participant can propose transitions affecting:

- `entities.member_banks.deposit_convertibility`

## 6. Choice model and heterogeneity

The backend may choose only:

- `no_op`
- `suspend_deposit_convertibility`

These are aggregate construction choices, not sampled member behavior. Rule selects with published coordinate and guard rows; an unmatched coordinate produces `no_op`, while LLM and RuleLLM remain planned and fail closed. The backend may choose among listed aggregate alternatives but may not invent individual distributions, weights, or correlated microbehavior. Unsupported heterogeneity remains unavailable evidence rather than a synthetic population.

## 7. Intent and environment-result boundary

The participant emits one typed action intent and zero or more typed message
intents. The H2EPR environment owns domain admission and constructs typed
dispositions and state deltas. The MASim reducer owns the single authoritative
commit; MASim also owns transport, trace, seals, and replay. The participant
cannot declare success.

## 8. Configuration and uncertainty

Logical coordinates, initial values, and routes are selected by shared configuration. Rule rows belong to backend configuration. This semantic parent fixes no probability, personality, threshold, model prompt, or fitted historical parameter.

## 9. Worked cases and falsification

- **Aggregate action:** at an activated coordinate the cohort may emit one listed non-`no_op` transition; the environment still owns admission and effect.
- **Contrasting response:** the cohort may instead emit `no_op`, or another listed aggregate transition when one exists. The dataset does not support attributing different responses to invented members.
- **Missing information:** an absent or stale required observation yields `no_op` or a listed response that makes no claim about the missing fact.
- **Aggregation change:** adding weights, subgroups, distributions, or independently acting units changes the choice unit and therefore requires a successor rather than an in-place parameter edit.
- **Environment rejection:** an invalid target, failed precondition, unavailable route, or conflicting write is recorded by the environment; the cohort cannot turn a partial or rejected result into aggregate success.
- **Falsifier:** source support for stable, behaviorally distinct member classes would invalidate the single unweighted aggregate representation.

## 10. Limitations and source anchors

No member-bank-specific policy or reserves are modeled. Full Draft exposure makes this a dataset-conditioned construction baseline, not a held-out reconstruction or calibrated behavioral model. Any change to identity, representation kind, authority, or intent scope requires a successor and regenerated downstream identities.

Anchors retained by the machine semantic index:

- `draft_epg:S3/E7/P_12`
