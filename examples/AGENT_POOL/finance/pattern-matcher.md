# Pattern-matching representativeness trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Pattern-matching representativeness trader |
| Theory Family         | Behavioral Finance (Representativeness) |
| Market Role         | **Destabilising** |
| Time Horizon          | medium |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models an investor who identifies recent return sequences as matching known patterns and trades on the perceived regime. Decision goal: trade in the direction of a pattern match. Non-goals: must not use base rates.

## Theoretical Foundation

**Kahneman**:
- Theory / Study: Kahneman, D., & Tversky, A. (1972). https://doi.org/10.1016/0010-0285(72)90016-3
- Core Insight: People judge probability by similarity to a prototype, neglecting base rates.
- Mathematical Formulation: `regime_belief = f(similarity(recent_sequence, prototype)); trade when similarity > threshold.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Identify patterns in recent returns and trade on the perceived regime signal. Activation: when similarity(recent_returns, prototype) > similarity_threshold, buy or sell in pattern direction.

Call Frequency: every-tick.

Activation Triggers: Identify patterns in recent returns and trade on the perceived regime signal. `<Default>`: hold.

## Behavioral Framework

Compare recent N-period return sequence against prototype patterns (trend, reversal). If similarity exceeds threshold, submit directional order scaled by match confidence.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| theta_sim | 0.30-0.80 | 0.50 |
| w_rec | 0.50-0.95 | 0.80 |
| k_pat | 3-10 | 5 |

## Academic References

Kahneman, D., & Tversky, A. (1972). https://doi.org/10.1016/0010-0285(72)90016-3

## Design Provenance and Versioning

- Origin: new (2026-07-11, RepresentativenessBias polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/finance/pattern-matcher.md`
| Icon | ![](../agent_images/icons/finance-pattern-matcher.png) |
