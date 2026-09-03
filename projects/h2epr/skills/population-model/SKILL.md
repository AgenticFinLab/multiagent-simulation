---
name: population-model
description: Define a heterogeneous dataset-bounded population choice model and its aggregate runtime representation.
---

# Population Model

Read [references/guide.md](references/guide.md) before choosing a population
representation. It distinguishes cohort context from a genuine choice unit and
specifies aggregation, heterogeneity, worked cases, and handoff evidence.

## Procedure

1. Confirm why a named Agent or scenario process is insufficient.
2. Define the choice unit, source scope, inclusion/exclusion, aggregation, and
   whether runtime uses one aggregate actor or several units.
3. Anchor the group role to allowed dataset records. Mark unobserved
   heterogeneity and distributions as assumptions.
4. Define unit observations, state, admissible decisions, population
   interactions, aggregate outputs, and environment results.
5. Declare heterogeneity dimensions and parameter domains; leave selected
   counts, weights, distributions, and seeds to configuration.
6. Test contrasting units, missing information, aggregation change, and
   promotion of one unit to a named Agent. If the runtime uses one aggregate
   actor and the dataset contains no microdata, state that heterogeneous
   microbehavior is unavailable and test aggregate alternatives; do not invent
   individual trajectories merely to satisfy the case list.

Stop if the candidate gives a group one personality, duplicates institutional
authority, or invents unsupported microdata.
