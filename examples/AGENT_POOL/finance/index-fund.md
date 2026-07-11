# Passive index fund rebalancer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Passive index fund rebalancer |
| Theory Family         | Portfolio Theory |
| Market Role           | **Stabilising** - provides slow baseline flow |
| Time Horizon          | long |
| Risk Tolerance        | moderate |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

Models a passive index fund or ETF that maintains a target equity allocation through periodic rebalancing. The real-world counterpart is a passive mutual fund, index ETF, or institutional allocation mandate.

The decision goal is to rebalance toward a target position when the portfolio drifts beyond a tolerance band. Non-goals: must not chase trends, trade on fundamentals, or provide liquidity.

## Theoretical Foundation

**Constant-Mix Portfolio Rebalancing**:
- Theory / Study: Dynamic strategies for asset allocation.
- Citation: Perold, A. F., & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*.
- Core Insight: Constant-mix strategies buy when prices fall and sell when prices rise, providing contrarian rebalancing flow that dampens volatility.
- Mathematical Formulation: `gap = target_position - current_position; trade = gap * rebalance_rate` when `abs(gap) > rebalance_threshold`.
- Empirical Evidence: Rebalancing premiums documented in multi-asset portfolio studies.
- Relevance to This Agent: Provides non-directional baseline flow against trend-following agents.
- Calibration Source: Perold & Sharpe (1988).
- Falsification Conditions: If the agent trades with the trend direction, the rebalancing mechanism is broken.

## Design Purpose and Activation Triggers

Purpose: Maintain target equity exposure through slow periodic rebalancing.

Call Frequency: every N rounds (configurable, typically 5-10).

Prerequisite Signals: `price`, `position` available.

Activation Triggers: `abs(target_position - position) > rebalance_threshold`: submit rebalancing order. `<Default>`: hold.

Deactivation Conditions: Already at target within tolerance band.

Market Contribution by Regime: Calm: Stabilising (provides baseline flow). Stress: Stabilising (absorbs excess volatility).

## Behavioral Framework

#### Decision Information Set
| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | float | 1 round | Required for position value calculation |
| `position` | float | current | Current portfolio allocation |
| `target_position` | float | static | Strategic target allocation |

Core Behavioral Mechanism: Compare current position to target. If deviation exceeds threshold, place a rebalancing order proportional to the gap. Capped at ±10 units per trade.

Action Space: Buy (quantity > 0) when position below target; Sell (quantity < 0) when position above target; Hold otherwise.

Worked Numerical Example: If target_position=60 and current=55 with threshold=5, gap=5, rebalance_rate=0.5, then quantity=+2.5.

## Parameters
| Parameter | Symbol | Range | Default |
|-----------|--------|-------|---------|
| target_allocation | a_target | 0.4-0.8 | 0.6 |
| rebalance_frequency | f_reb | 3-10 | 5 |
| rebalance_threshold | theta_reb | 0.03-0.10 | 0.05 |

## Academic References
Perold, A. F., & Sharpe, W. F. (1988). Dynamic strategies for asset allocation. *Financial Analysts Journal*.

## Design Provenance and Versioning
- Origin: new (2026-07-11, MomentumEffect polish)
- Polish audit: 2026-07-11 against agent-design-skill.md
- Pool reference: `examples/AGENT_POOL/finance/index-fund.md`
| Icon | ![](../agent_images/icons/finance-index-fund.png) |
