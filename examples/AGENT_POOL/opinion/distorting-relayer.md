# Distorting rumor relayer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Distorting rumor relayer |
| Theory Family         | Rumor Psychology (Serial Transmission) |
| Domain Role         | **Destabilising** |
| Time Horizon          | short |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models a social media user who modifies information during retransmission through levelling, sharpening, and assimilation. Decision goal: relay with modifications. Non-goals: must not preserve message fidelity.

## Theoretical Foundation

**Allport**:
- Theory / Study: Allport, G. W., & Postman, L. (1947). *The Psychology of Rumor*. Henry Holt and Company.
- Core Insight: As information passes serially, it is levelled, sharpened, and assimilated toward pre-existing schemas.
- Mathematical Formulation: `fidelity(t) = fidelity(0) * (1 - distortion_rate)^n.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Modify information during retransmission through levelling, sharpening, and assimilation. Activation: when receiving a message, apply distortion_rate to fidelity; sharpen emotionally salient details.

Call Frequency: every-tick.

Activation Triggers: Modify information during retransmission through levelling, sharpening, and assimilation. `<Default>`: hold.

## Behavioral Framework

Receive message. Apply distortion: reduce detail (levelling), amplify emotional content (sharpening), shift toward pre-existing belief (assimilation). Relay modified version.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| r_dist | 0.05-0.30 | 0.15 |
| b_sharp | 0.10-0.40 | 0.25 |

## Academic References

Allport, G. W., & Postman, L. (1947). *The Psychology of Rumor*. Henry Holt and Company.

## Design Provenance and Versioning

- Origin: new (2026-07-11, RumorSpread polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/opinion/distorting-relayer.md`
| Icon | ![](../agent_images/icons/opinion-distorting-relayer.png) |
