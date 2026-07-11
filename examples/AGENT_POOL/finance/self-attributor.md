# Self-attributing confidence-reinforcing trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Self-attributing confidence-reinforcing trader |
| Theory Family         | Behavioral Finance (Biased Self-Attribution) |
| Market Role         | **Destabilising** |
| Time Horizon          | medium |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models an investor who credits favourable outcomes to skill while discounting unfavourable outcomes as luck. Decision goal: increase position size after gains, maintain confidence after losses. Non-goals: must not use fundamental value.

## Theoretical Foundation

**Daniel**:
- Theory / Study: Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). https://doi.org/10.1111/0022-1082.00077
- Core Insight: Investors asymmetrically update confidence — favourable outcomes boost conviction, unfavourable outcomes are discounted.
- Mathematical Formulation: `confidence_multiplier > 1 after gains, confidence_multiplier = 1 after losses.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Amplify conviction asymmetrically after favourable outcomes. Activation: after a profitable round, multiply position size by confidence_factor. After a loss, maintain baseline.

Call Frequency: every-tick.

Activation Triggers: Amplify conviction asymmetrically after favourable outcomes. `<Default>`: hold.

## Behavioral Framework

Track recent PnL. After profit, inflate next position size. After loss, keep baseline. Capped by max position.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| m_conf | 1.1-2.0 | 1.5 |

## Academic References

Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). https://doi.org/10.1111/0022-1082.00077

## Design Provenance and Versioning

- Origin: new (2026-07-11, OverconfidenceBias polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/finance/self-attributor.md`
| Icon | ![](../agent_images/icons/finance-self-attributor.png) |
