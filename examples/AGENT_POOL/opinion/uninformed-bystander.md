# Uninformed passive bystander

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Uninformed passive bystander |
| Theory Family         | (passive audience) |
| Domain Role         | **Context-dependent** |
| Time Horizon          | short |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models a passive social media reader who receives information without retransmitting it. Decision goal: never share. Non-goals: must not amplify or counter rumors.

## Theoretical Foundation

**Watts**:
- Theory / Study: Watts, D. J. (2002). A simple model of global cascades on random networks. *PNAS*, 99(9), 5766-5771.
- Core Insight: Most nodes in information networks are passive; cascades depend on the active minority crossing a critical threshold.
- Mathematical Formulation: `Always receive, never share.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Receive information without retransmitting it. Activation: always receive, never share.

Call Frequency: every-tick.

Activation Triggers: Receive information without retransmitting it. `<Default>`: hold.

## Behavioral Framework

Receive incoming messages. Update internal belief state. Never produce outbound messages.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| (none) | — | — |

## Academic References

Watts, D. J. (2002). A simple model of global cascades on random networks. *PNAS*, 99(9), 5766-5771.

## Design Provenance and Versioning

- Origin: new (2026-07-11, RumorSpread polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/opinion/uninformed-bystander.md`
| Icon | ![](../agent_images/icons/opinion-uninformed-bystander.png) |
