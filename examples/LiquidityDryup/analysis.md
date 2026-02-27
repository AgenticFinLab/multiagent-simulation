# LiquidityDryup Analysis Methodology

## Overview

This document describes the evaluation metrics for detecting **liquidity dry-up** dynamics in market simulations. Based on Grossman-Miller (1988) market maker inventory model and Brunnermeier-Pedersen (2009) liquidity spirals.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                  | Rounds | Observable Phenomena                                    | Economic Interpretation                                     |
|------------------------|--------|---------------------------------------------------------|-------------------------------------------------------------|
| **Normal Liquidity**   | 1-20   | Tight spreads (1-2%); deep order book; low price impact | Market maker actively providing liquidity                   |
| **Stress Signal**      | 21-30  | One-sided flow emerges; inventory imbalance grows       | Informed traders or panic begins                            |
| **Spread Widening**    | 31-45  | Spreads expand 3-5x; market maker reduces quotes        | MM compensating for inventory risk                          |
| **Withdrawal**         | 46-60  | MM stops quoting; no bid or ask available               | Risk exceeds tolerance; liquidity vacuum                    |
| **Illiquidity Spiral** | 61-80  | Small trades cause large price moves; panic amplified   | Positive feedback: low liquidity → impact → lower liquidity |

### Key Observable Curves

1. **Bid-Ask Spread**: Exponential widening during stress
2. **Market Depth**: Step function drop to near-zero
3. **Price Impact**: Hockey-stick increase during dry-up
4. **MM Inventory**: Extreme imbalance triggers withdrawal

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                              | Expected Pattern                      | What It Validates       |
|---------------------------------------|---------------------------------------|-------------------------|
| **Spread widens 3-10x during stress** | Matches empirical data                | Realistic MM response   |
| **Depth drops 80-100%**               | Near-complete withdrawal              | Proper risk management  |
| **Price impact spikes 5-20x**         | Small trades move market              | Illiquidity mechanics   |
| **Spiral visible**                    | Withdrawal → impact → more withdrawal | Feedback loop present   |
| **Recovery when stress ends**         | Liquidity returns gradually           | Market structure intact |

### Unreasonable Results (Simulation Failure Indicators)

- Spreads unchanged during stress → MM not responding to risk
- MM never withdraws → Infinite risk tolerance
- Instant withdrawal (1 round) → Missing gradual deterioration
- No recovery → Market structure broken

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                    | Rationale       |
|----------------|--------------------------------------|-----------------|
| **50 rounds**  | Stress event + withdrawal visible    | Basic mechanism |
| **100 rounds** | Full dry-up cycle + partial recovery | Standard cycle  |
| **200 rounds** | Multiple stress events possible      | Test resilience |
| **500 rounds** | Long-term liquidity patterns         | Regime dynamics |

### Observable Metrics by Round Count

```
Round 50:  One dry-up event; may not see full recovery
Round 100: Complete cycle; spread normalizes by round 90
Round 200: Possible second dry-up event
Round 500: Statistical properties of dry-up frequency
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                     | Economic Interpretation     |
|---------------------------|-------------------------------------|-----------------------------|
| **3-5 agents**            | Extreme fragility; frequent dry-ups | Single agent can exhaust MM |
| **8-10 agents** (default) | Clear dry-up dynamics               | Realistic order flow        |
| **20-30 agents**          | More resilient; harder to trigger   | Diverse flow directions     |
| **50+ agents**            | Very stable; dry-up rare            | Natural diversification     |

### Agent Type Effects

| More of This Agent   | Effect on Liquidity                     |
|----------------------|-----------------------------------------|
| **Informed Traders** | Faster MM withdrawal; adverse selection |
| **Noise Traders**    | More stable liquidity; random flow      |
| **Market Makers**    | Higher resilience; multiple providers   |
| **Momentum Traders** | More one-sided flow; triggers dry-up    |

### Critical Ratios

```
Momentum/Directional traders / Noise traders:

Ratio > 3:1 → Frequent, severe dry-ups
Ratio 2:1   → Occasional dry-ups (realistic)
Ratio 1:1   → Rare dry-ups; stable liquidity
Ratio < 1:2 → Very stable; almost no dry-ups
```

---

## Key Metrics

| Metric               | Formula                        | Source          | Purpose             |
|----------------------|--------------------------------|-----------------|---------------------|
| Bid-Ask Spread       | Spread = ask - bid             | O'Hara (1995)   | Liquidity measure   |
| Market Depth         | Depth = Σ(bid_size + ask_size) | Standard        | Total liquidity     |
| Price Impact         | λ = ΔP / volume                | Kyle (1985)     | Illiquidity measure |
| Inventory Imbalance  | Inv = Σ(buy) - Σ(sell)         | Grossman-Miller | MM risk exposure    |
| Liquidity Withdrawal | LW = depth_t / depth_0         | Standard        | Liquidity ratio     |

---

## Liquidity Dry-up Mechanism

**Inventory Risk → Spread Widening → Withdrawal:**
1. Stress event creates one-sided order flow
2. Market maker inventory becomes imbalanced
3. MM widens spread to compensate for risk
4. If volatility too high, MM withdraws completely
5. Illiquidity spiral: less liquidity → more impact → more withdrawal

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    # Core Metrics
    calculate_returns,
    calculate_rolling_volatility,
    calculate_liquidity_metrics,
    
    # Volume Analysis
    calculate_volume_metrics,
    calculate_agent_impact,
    calculate_net_demand,
    
    # Visualization
    plot_price_dynamics,
    plot_volatility_analysis,
    plot_agent_activity,
    plot_multi_panel_summary,
)

# Example: Analyze liquidity dry-up
prices = {...}  # Load from simulation output

# Liquidity metrics
liquidity = calculate_liquidity_metrics(prices, volumes)

# Volatility and price impact
volatility = calculate_rolling_volatility(prices, window=5)
impact = calculate_agent_impact(investor_quantities)

plot_price_dynamics(prices, output_path="price.png")
plot_agent_activity(impact, output_path="activity.png")
```

---

## Success Criteria

| Criterion              | Target                               | Evidence                |
|------------------------|--------------------------------------|-------------------------|
| **Spread Widening**    | Spread increases > 3× during stress  | Liquidity deterioration |
| **MM Withdrawal**      | MarketMaker bid/ask size → 0         | Complete withdrawal     |
| **Price Impact**       | Small orders cause large ΔP          | Illiquidity confirmed   |
| **Illiquidity Spiral** | Impact → withdrawal → more impact    | Feedback loop           |
| **Stress Trigger**     | High volatility initiates withdrawal | Mechanism validated     |

---

## References

1. Grossman, S.J., & Miller, M.H. (1988). Liquidity and Market Structure. *Journal of Finance*, 43(3), 617-633.
2. Brunnermeier, M.K., & Pedersen, L.H. (2009). Market Liquidity and Funding Liquidity. *Review of Financial Studies*, 22(6), 2201-2238.
3. Amihud, Y., & Mendelson, H. (1986). Asset pricing and the bid-ask spread. *Journal of Financial Economics*, 17(2), 223-249.
4. Kyle, A.S. (1985). Continuous Auctions and Insider Trading. *Econometrica*, 53(6), 1315-1335.
