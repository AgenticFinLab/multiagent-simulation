# Authoritative fact-checker

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Authoritative fact-checker |
| Theory Family         | Misinformation Correction |
| Domain Role         | **Stabilising** |
| Time Horizon          | short |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models a professional fact-checking organisation that broadcasts verified corrections. Decision goal: broadcast corrections that counteract prior rumor exposure. Non-goals: must not amplify rumors.

## Theoretical Foundation

**Lewandowsky et al**:
- Theory / Study: Lewandowsky et al. (2012). https://doi.org/10.1177/1529100612451018; Ecker et al. (2022). https://doi.org/10.1038/s44159-021-00006-y
- Core Insight: Corrections reduce but rarely eliminate misinformation's influence; the continued-influence effect means retracted claims still affect reasoning.
- Mathematical Formulation: `correction_reach = broadcast_rate * audience_size; effective_correction = (1 - decay_factor).`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Broadcast verified corrections that partially counteract prior rumor exposure. Activation: when rumor belief in the population exceeds a threshold, broadcast a correction.

Call Frequency: every-tick.

Activation Triggers: Broadcast verified corrections that partially counteract prior rumor exposure. `<Default>`: hold.

## Behavioral Framework

Monitor population belief. When belief deviates from truth beyond a threshold, broadcast a correction message to all neighbours.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| r_corr | 0.10-0.50 | 0.25 |
| d_corr | 0.50-0.90 | 0.70 |

## Academic References

Lewandowsky et al. (2012). https://doi.org/10.1177/1529100612451018; Ecker et al. (2022). https://doi.org/10.1038/s44159-021-00006-y

## Design Provenance and Versioning

- Origin: new (2026-07-11, RumorSpread polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/opinion/fact-checker.md`
| Icon | ![](../agent_images/icons/opinion-fact-checker.png) |
