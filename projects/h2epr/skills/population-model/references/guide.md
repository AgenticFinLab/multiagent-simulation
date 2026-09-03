# Population Model authoring guide

## When a population is warranted

A population represents repeated or heterogeneous choice units whose
individual identities are absent, unnecessary, or deliberately aggregated.
It is not a label for passive context and it is not a shortcut for many named
Agents.

| Dataset situation | Representation |
|---|---|
| named unit with distinct authority | Agent Definition |
| repeated units with a common choice surface | Population Model |
| group only affected by others, with no modeled choice | context or world state |
| automatic institutional transition | scenario process |
| missing microdata but aggregate behavior is required | aggregate population with explicit limits |

## Required accounting

State the unit of choice, inclusion/exclusion rule, source participant IDs,
runtime cardinality, weighting, aggregation direction, and promotion trigger.
If one runtime actor represents the group, identify which individual
differences are unavailable and which aggregate alternatives remain testable.

Separate four things that are often conflated:

- observed dataset group labels;
- assumed heterogeneity dimensions;
- configured counts, weights, distributions, or seeds;
- generated unit or aggregate outcomes.

Only the first belongs to dataset provenance. Domains may be declared in the
Model; selected values belong to configuration.

## Choice and aggregation contract

1. Define activation and visible information at the unit and aggregate level.
2. Declare admissible responses, duties, abstention, adaptation, and lifecycle
   effects without fixing a backend policy.
3. Name unit state, aggregate state, update authority, and missing behavior.
4. Define how unit intents aggregate, how resource constraints are applied,
   and which results remain environment-owned.
5. State correlation assumptions and what cannot be inferred without
   microdata.
6. Give the condition under which a unit must become a named Agent or the
   behavior must return to the scenario.

## Worked cases

When microdata are supported, contrast at least two units under different
observations or latent categories and show how aggregation changes. When the
dataset supports only an aggregate actor, compare at least two admissible
aggregate configurations instead of inventing individual trajectories.

Also cover missing information, an environment rejection or partial result,
and an aggregation perturbation. A useful falsifier is a source pattern in
which one unit acquires independent authority that the aggregate interface
cannot represent.

## Failure routing

Named authority goes to an Agent Definition. Resource conservation, route
delivery, and institutional truth go to the Scenario. Exact population size,
weights, probabilities, and seeds go to configuration. Selection algorithms
and prompts go to backend realization. Unsupported micro-level behavior is a
recorded limitation, not a synthetic fact.

## Completion evidence

Record the stable model ID, source scope and anchors, choice unit, runtime
representation, aggregation losses, heterogeneity domains, interface mapping,
worked cases, falsifier, successor trigger, review disposition, and content
hash. Acceptance means the aggregate semantics are explicit and testable; it
does not validate a chosen distribution or generated outcome.
