# Category-overgeneralizing classifier

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Category-overgeneralizing classifier |
| Theory Family         | Behavioral Finance (Representativeness) |
| Market Role         | **Destabilising** |
| Time Horizon          | medium |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models an investor who classifies assets into good or bad categories based on recent performance, ignoring base rates. Decision goal: buy 'winners', sell 'losers'. Non-goals: must not update beliefs with Bayesian reasoning.

## Theoretical Foundation

**Grether**:
- Theory / Study: Grether, D. M. (1980). https://doi.org/10.2307/1885092
- Core Insight: People systematically neglect prior probabilities when individuating evidence is presented.
- Mathematical Formulation: `Classify as winner when recent_return > threshold; loser when below.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Classify assets into winner/loser categories based on recent returns, ignoring statistical base rates of regime persistence. Activation: when recent return exceeds a threshold, classify as 'winner' and buy; when below, classify as 'loser' and sell.

Call Frequency: every-tick.

Activation Triggers: Classify assets into winner/loser categories based on recent returns, ignoring statistical base rates of regime persistence. `<Default>`: hold.

## Behavioral Framework

Track recent N-period cumulative return. If positive beyond threshold, classify asset as winner and buy. If negative beyond threshold, classify as loser and sell.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| eta_switch | 0.05-0.25 | 0.12 |
| pi_trend | 0.05-0.25 | 0.10 |

## Academic References

Grether, D. M. (1980). https://doi.org/10.2307/1885092

## Design Provenance and Versioning

- Origin: new (2026-07-11, RepresentativenessBias polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/finance/category-overgeneralizer.md`
| Icon | ![](../agent_images/icons/finance-category-overgeneralizer.png) |
