# Skeptical rumor evaluator

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Skeptical rumor evaluator |
| Theory Family         | Misinformation Correction |
| Domain Role         | **Stabilising** |
| Time Horizon          | short |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models a critical-thinking user who interrogates claims by demanding evidence. Decision goal: evaluate before sharing. Non-goals: must not share unverified claims.

## Theoretical Foundation

**Lewandowsky**:
- Theory / Study: Lewandowsky, S., Ecker, U. K. H., et al. (2012). https://doi.org/10.1177/1529100612451018
- Core Insight: Corrections reduce but rarely eliminate misinformation's influence.
- Mathematical Formulation: `Share only when evidence_quality > skepticism_threshold.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Interrogate claims by demanding evidence, reducing propagation. Activation: when receiving a message, evaluate evidence quality. Share only if evidence exceeds skepticism threshold.

Call Frequency: every-tick.

Activation Triggers: Interrogate claims by demanding evidence, reducing propagation. `<Default>`: hold.

## Behavioral Framework

Observe message. Compare evidence quality to skepticism threshold. If below threshold, do not share. If above, share with qualification.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| theta_skep | 0.40-0.80 | 0.60 |
| p_share_s | 0.05-0.30 | 0.15 |

## Academic References

Lewandowsky, S., Ecker, U. K. H., et al. (2012). https://doi.org/10.1177/1529100612451018

## Design Provenance and Versioning

- Origin: new (2026-07-11, RumorSpread polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `masim/agents/defines/opinion/skeptical-evaluator.md`
| Icon | ![](../agent_images/icons/opinion-skeptical-evaluator.png) |
