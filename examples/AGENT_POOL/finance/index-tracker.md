# Passive index-tracking rebalancer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Passive index-tracking rebalancer |
| Theory Family         | Portfolio Theory |
| Market Role         | **Stabilising** |
| Time Horizon          | medium |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models an index-tracking fund that rebalances toward a target exposure. Decision goal: maintain target position through slow rebalancing. Non-goals: must not chase trends or trade on fundamentals.

## Theoretical Foundation

**Perold**:
- Theory / Study: Perold, A. F., & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*.
- Core Insight: Passive rebalancing provides slow, non-directional baseline flow that stabilises markets.
- Mathematical Formulation: `gap = target_position - current_position; trade = gap * rebalance_rate when abs(gap) > threshold.`
- Relevance to This Agent: The agent operationalises this mechanism as its primary decision rule.
- Falsification Conditions: If the agent behaves contrary to the described mechanism, the design is invalid.

## Design Purpose and Activation Triggers

Purpose: Maintain target equity exposure through periodic rebalancing. Activation: when abs(position - target) > rebalance_threshold, trade toward target.

Call Frequency: every-tick.

Activation Triggers: Maintain target equity exposure through periodic rebalancing. `<Default>`: hold.

## Behavioral Framework

Compare current position to target_position. If deviation exceeds threshold, submit a small rebalancing order.

Action Space: Buy / Sell / Hold based on signal thresholds. Quantity clamped to cash and position constraints.

## Parameters

| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| Q_target | configurable | varies |
| theta_bal | 0.03-0.10 | 0.05 |

## Academic References

Perold, A. F., & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*.

## Design Provenance and Versioning

- Origin: new (2026-07-11, ReversalEffect polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/finance/index-tracker.md`
| Icon | ![](../agent_images/icons/finance-index-tracker.png) |
