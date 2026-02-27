# FlashCrash Analysis Methodology

## Overview

This document describes the evaluation metrics for detecting **flash crash** dynamics in market simulations. Based on market microstructure theory and Kirilenko et al. (2017) analysis of the 2010 Flash Crash.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                | Rounds | Observable Phenomena                                                        | Economic Interpretation                                          |
|----------------------|--------|-----------------------------------------------------------------------------|------------------------------------------------------------------|
| **Normal Trading**   | 1-15   | Price fluctuates ±2% around fundamental; normal volatility                  | Market in equilibrium; liquidity adequate                        |
| **Trigger Event**    | 16-20  | Sudden 3-5% drop; HFT begins aggressive selling                             | Exogenous shock or large sell order initiates cascade            |
| **Cascade Phase**    | 21-30  | Rapid 10-20% crash in 5-10 rounds; stop-loss triggers; volatility spikes 5x | Self-reinforcing: sells trigger more sells; liquidity evaporates |
| **Liquidity Vacuum** | 25-35  | Bid-ask spread widens dramatically; market maker withdraws                  | No buyers at any price; "air pocket" in order book               |
| **Recovery**         | 36-50  | V-shaped rebound; price returns to ±5% of pre-crash                         | Fundamental traders provide floor; opportunistic buying          |

### Key Observable Curves

1. **Price**: V-shaped or W-shaped crash-recovery pattern
2. **Volatility**: Sharp spike (5-10x normal) during crash, rapid normalization
3. **Volume**: Massive spike during crash (panic selling), elevated during recovery
4. **Bid-Ask Spread**: Extreme widening during vacuum, gradual normalization

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                       | Expected Pattern                                | What It Validates             |
|--------------------------------|-------------------------------------------------|-------------------------------|
| **Crash depth 5-20%**          | Matches real flash crashes (2010: 9%, 2015: 5%) | Realistic cascade calibration |
| **Recovery within 30 rounds**  | Quick rebound like actual events                | Proper floor mechanism        |
| **HFT amplifies initial drop** | More selling when price falling                 | Momentum-based strategy works |
| **Stop-loss cascade visible**  | Clustered sells at price thresholds             | Proper trigger mechanism      |
| **Market maker withdrawal**    | Reduced quotes during high volatility           | Risk management behavior      |

### Unreasonable Results (Simulation Failure Indicators)

- No recovery after crash → Missing floor mechanism
- Gradual decline instead of sudden crash → Cascade mechanism not working
- Price drops 50%+ → No circuit breakers or fundamental anchor
- Crash every few rounds → Market too unstable, parameters wrong

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                              | Rationale                          |
|----------------|------------------------------------------------|------------------------------------|
| **30 rounds**  | May see crash but incomplete recovery          | Insufficient time for full V-shape |
| **50 rounds**  | One complete crash-recovery cycle              | Standard flash crash duration      |
| **100 rounds** | 1-2 flash crashes possible                     | Random triggers may recur          |
| **200 rounds** | 2-4 flash crashes; statistical patterns emerge | Multiple events for analysis       |

### Observable Metrics by Round Count

```
Round 30:  Crash likely, recovery may be incomplete
Round 50:  Full V-shape recovery expected
Round 100: Second flash crash may occur around round 70-80
Round 200: ~3 crash events expected; recovery patterns consistent
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                                   | Economic Interpretation                |
|---------------------------|---------------------------------------------------|----------------------------------------|
| **3-5 agents**            | Extreme volatility; single agent can crash market | Thin market, high impact per trade     |
| **8-10 agents** (default) | Realistic flash crash dynamics                    | Cascade requires multiple participants |
| **20-30 agents**          | More diffuse crash; slower cascade                | Multiple small traders vs few large    |
| **50+ agents**            | Crashes may be dampened; more resilience          | Heterogeneity provides natural buffers |

### Agent Type Effects

| More of This Agent      | Effect on Flash Crash                    |
|-------------------------|------------------------------------------|
| **HFT Traders**         | Faster, deeper crashes; quicker recovery |
| **Stop-Loss Traders**   | More cascade triggers; clustered selling |
| **Market Makers**       | More liquidity; shallower crashes        |
| **Fundamental Traders** | Stronger floor; faster recovery          |

### Critical Ratios

```
HFT agents / Fundamental agents:

Ratio > 3:1 → Severe flash crashes, may not recover
Ratio 2:1   → Pronounced V-shaped crashes (realistic)
Ratio 1:1   → Mild volatility spikes only
Ratio < 1:1 → Market too stable, no flash crash
```

---

## Key Metrics

| Metric              | Formula                          | Source               | Purpose                          |
|---------------------|----------------------------------|----------------------|----------------------------------|
| Price Drop          | ΔP_min = min(P) - P_0            | Standard             | Maximum crash magnitude          |
| Recovery Time       | T_rec = t(P ≈ P_0) - t(P_min)    | Standard             | Time to recover from crash       |
| Liquidity           | L = 1 / (ask - bid)              | O'Hara (1995)        | Market maker liquidity provision |
| Volatility Spike    | σ_spike = σ_crash / σ_normal     | Standard             | Relative volatility increase     |
| Order Flow Toxicity | OFT = sell_volume / total_volume | Easley et al. (2011) | Measure sell pressure            |

---

## Flash Crash Mechanism

**HFT + Stop-Loss + Liquidity Withdrawal:**
1. Initial price shock triggers HFT selling
2. Stop-loss orders cascade, amplifying decline
3. Market makers withdraw (liquidity vacuum)
4. Price collapses rapidly (5-10% in minutes)
5. Fundamental traders provide floor, recovery begins

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    # Core Metrics
    calculate_returns,
    calculate_rolling_volatility,
    calculate_max_drawdown,
    calculate_liquidity_metrics,
    
    # Volume Analysis
    calculate_volume_metrics,
    calculate_agent_impact,
    
    # Visualization
    plot_price_dynamics,
    plot_volatility_analysis,
    plot_multi_panel_summary,
)

# Example: Analyze flash crash
prices = {...}  # Load from simulation output

# Detect crash depth
drawdown = calculate_max_drawdown(prices)

# Volatility spike during crash
volatility = calculate_rolling_volatility(prices, window=5)

# Agent-level impact during crash
impact = calculate_agent_impact(investor_quantities)

plot_price_dynamics(prices, fundamental=100.0, output_path="price.png")
plot_volatility_analysis(prices, volatility, output_path="volatility.png")
```

---

## Success Criteria

| Criterion             | Target                             | Evidence                    |
|-----------------------|------------------------------------|-----------------------------|
| **Crash Magnitude**   | ΔP > 5% in < 5 rounds              | Flash crash detected        |
| **Recovery**          | Price recovers to ±2% of pre-crash | V-shaped recovery           |
| **Liquidity Vacuum**  | MarketMaker withdraws during crash | Spread widens dramatically  |
| **Volatility Spike**  | σ_crash > 3× σ_normal              | Abnormal volatility         |
| **Stop-Loss Cascade** | StopLossTrader triggers chain      | Cascade mechanism validated |

---

## References

1. Kirilenko, A., Kyle, A.S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-Frequency Trading in an Electronic Market. *Journal of Finance*, 72(3), 967-998.
2. O'Hara, M. (1995). *Market Microstructure Theory*. Blackwell Publishers.
3. Easley, D., López de Prado, M.M., & O'Hara, M. (2011). The microstructure of the "flash crash". *Journal of Portfolio Management*, 37(2), 118-128.
4. SEC/CFTC (2010). *Findings Regarding the Market Events of May 6, 2010*. U.S. Securities and Exchange Commission.
