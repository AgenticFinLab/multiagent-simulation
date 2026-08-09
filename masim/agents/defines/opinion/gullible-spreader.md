# Gullible rumor spreader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Gullible rumor spreader |
| Theory Family         | Information Diffusion |
| Domain Role         | **Destabilising** |
| Time Horizon          | short |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models a social media user who accepts and relays unverified claims without scrutiny. Decision goal: share when content is emotionally salient. Non-goals: must not verify claims.

## Theoretical Foundation

**Vosoughi**:
- Theory / Study: Vosoughi, S., Roy, D., & Aral, S. (2018). https://doi.org/10.1126/science.aap9559
- Core Insight: False news diffuses farther, faster, and more broadly than true news on social media.
- Mathematical Formulation: `Share when emotional_salience > gullibility_threshold.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Relay unverified claims without scrutiny when emotional salience exceeds a threshold. Activation: when emotional_salience > gullibility_threshold, share the rumor.

Call Frequency: every-tick.

Activation Triggers: Relay unverified claims without scrutiny when emotional salience exceeds a threshold. `<Default>`: hold.

## Behavioral Framework

Observe incoming message content and emotional salience score. If salience exceeds personal gullibility threshold, share the message to neighbours.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| theta_gull | 0.10-0.50 | 0.30 |
| p_share | 0.20-0.80 | 0.50 |

## Academic References

Vosoughi, S., Roy, D., & Aral, S. (2018). https://doi.org/10.1126/science.aap9559

## Design Provenance and Versioning

- Origin: new (2026-07-11, RumorSpread polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `masim/agents/defines/opinion/gullible-spreader.md`
| Icon | ![](../agent_images/icons/opinion-gullible-spreader.png) |
