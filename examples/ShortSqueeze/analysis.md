# ShortSqueeze Analysis Methodology

## Overview

This document describes the evaluation metrics for detecting **short squeeze** dynamics in market simulations. Based on supply-demand imbalance mechanics and margin constraint theory.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase               | Rounds | Observable Phenomena                                          | Economic Interpretation                       |
|---------------------|--------|---------------------------------------------------------------|-----------------------------------------------|
| **Short Build-up**  | 1-15   | Short interest accumulates; price stable or declining         | Shorts betting on overvaluation               |
| **Catalyst Event**  | 16-25  | Positive news/buyer emerges; price rises 10-20%               | Triggers margin pressure on shorts            |
| **Forced Covering** | 26-45  | Short sellers buy to cover; price accelerates 50-100%+        | Margin calls force buying regardless of price |
| **Peak Squeeze**    | 46-60  | Maximum price spike; shorts exhausted; extreme volatility     | Supply overwhelmed by forced demand           |
| **Normalization**   | 61-100 | Price declines toward (but above) pre-squeeze; shorts reduced | New equilibrium; some shorts still trapped    |

### Key Observable Curves

1. **Price**: Exponential spike followed by partial reversion
2. **Short Interest**: Step-function decline during covering
3. **Volume**: Massive spike during squeeze (10-20x normal)
4. **Short P&L**: Increasingly negative during squeeze

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                   | Expected Pattern                      | What It Validates                       |
|----------------------------|---------------------------------------|-----------------------------------------|
| **Price spike 50-200%**    | Matches real squeezes (GME: 1700%)    | Realistic squeeze magnitude             |
| **Short covering visible** | Short positions decrease rapidly      | Forced buying mechanism                 |
| **Volume spike**           | 10x+ normal during squeeze            | Panic covering                          |
| **Feedback loop**          | Covering → price rise → more covering | Self-reinforcing dynamics               |
| **Partial reversion**      | Price settles above but below peak    | Not pure bubble; some fundamental shift |

### Unreasonable Results (Simulation Failure Indicators)

- Price spike < 20% → Not enough short pressure
- No short covering → Margin mechanism not working
- Instant spike (1-2 rounds) → Missing gradual cascade
- No reversion → Pure bubble, not squeeze mechanics

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                         | Rationale                        |
|----------------|-------------------------------------------|----------------------------------|
| **50 rounds**  | Squeeze starts but may not complete       | Insufficient time for full cycle |
| **100 rounds** | Full squeeze cycle with normalization     | Standard squeeze duration        |
| **200 rounds** | Possible second squeeze or re-shorting    | New shorts may enter             |
| **500 rounds** | Multiple squeeze cycles if shorts rebuild | Long-term dynamics               |

### Observable Metrics by Round Count

```
Round 50:  Squeeze in progress; peak may not be reached
Round 100: Peak around round 50-60; normalization by 90
Round 200: Complete cycle; possible second squeeze attempt
Round 500: Multiple cycles; short interest rebuilds
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                           | Economic Interpretation     |
|---------------------------|-------------------------------------------|-----------------------------|
| **3-5 agents**            | Extreme squeeze; single buyer can trigger | Very thin market            |
| **8-10 agents** (default) | Clear squeeze dynamics                    | Sufficient for cascade      |
| **20-30 agents**          | More gradual squeeze; longer duration     | Distributed short positions |
| **50+ agents**            | Squeeze may be dampened; diverse opinions | Natural buffers             |

### Agent Type Effects

| More of This Agent     | Effect on Squeeze                   |
|------------------------|-------------------------------------|
| **Short Sellers**      | Higher squeeze potential; more fuel |
| **Momentum Buyers**    | Amplifies squeeze; joins covering   |
| **Contrarian Sellers** | Dampens squeeze; provides supply    |
| **Market Makers**      | Moderates extremes; adds liquidity  |

### Critical Ratios

```
Short Interest / Float (simulated):

SI > 100% → Extreme squeeze potential (GME-like)
SI 50-100% → High squeeze risk
SI 20-50%  → Moderate squeeze potential
SI < 20%   → Low squeeze risk
```

---

## Key Metrics

| Metric               | Formula                              | Source       | Purpose                 |
|----------------------|--------------------------------------|--------------|-------------------------|
| Short Interest       | SI = shares_short / float            | Standard     | Squeeze vulnerability   |
| Short Covering Ratio | SCR = covering_volume / daily_volume | Standard     | Covering pressure       |
| Price Spike          | ΔP_max = max(P) - P_0                | Standard     | Squeeze magnitude       |
| Margin Pressure      | MP = loss / margin                   | Broker rules | Forced covering trigger |
| Days to Cover        | DTC = SI / avg_daily_volume          | Standard     | Time to exit shorts     |

---

## Short Squeeze Mechanism

**Forced Covering Feedback Loop:**
1. High short interest creates vulnerability
2. Positive catalyst triggers price rise
3. Short sellers face margin pressure
4. Forced covering → more buying → higher price
5. Feedback loop until shorts exhausted

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    # Core Metrics
    calculate_returns,
    calculate_rolling_volatility,
    calculate_max_drawdown,  # Inverted for squeeze
    
    # Volume Analysis
    calculate_volume_metrics,
    calculate_net_demand,
    calculate_strategy_contribution,
    
    # Visualization
    plot_price_dynamics,
    plot_agent_activity,
    plot_strategy_contribution,
    plot_multi_panel_summary,
)

# Example: Analyze short squeeze
prices = {...}  # Load from simulation output
investor_quantities = {...}

# Measure squeeze intensity
returns = calculate_returns(prices)
max_return = max(returns)

# Track short covering vs momentum buying
contribution = calculate_strategy_contribution(investor_quantities)

plot_price_dynamics(prices, output_path="price.png")
plot_strategy_contribution(contribution, output_path="contribution.png")
```

---

## Success Criteria

| Criterion                       | Target                                | Evidence                |
|---------------------------------|---------------------------------------|-------------------------|
| **Price Spike**                 | ΔP > 50% at peak                      | Squeeze magnitude       |
| **Forced Covering**             | ShortSeller switches to buying        | Covering detected       |
| **Feedback Loop**               | Covering → price rise → more covering | Positive feedback       |
| **Exhaustion**                  | Price stabilizes after shorts covered | Natural end of squeeze  |
| **MomentumBuyer Amplification** | Momentum traders add to buying        | Amplification mechanism |

---

## References

1. Lamont, O.A., & Thaler, R.H. (2003). Can the Market Add and Subtract? Mispricing in Tech Stock Carve-Outs. *Journal of Political Economy*, 111(2), 227-268.
2. Dechow, P.M., Hutton, A.P., Meulbroek, L., & Sloan, R.G. (2001). Short-sellers, fundamental analysis, and stock returns. *Journal of Financial Economics*, 61(1), 77-106.
3. GameStop case studies (2021). Market mechanics of short squeeze.
