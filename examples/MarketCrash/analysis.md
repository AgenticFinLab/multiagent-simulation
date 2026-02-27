# MarketCrash Analysis - Evaluation Methodology

## Overview

This document describes the evaluation methodology for detecting **market crash dynamics** including panic selling cascades and liquidity spirals.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                      | Rounds | Observable Phenomena                                                  | Economic Interpretation                       |
|----------------------------|--------|-----------------------------------------------------------------------|-----------------------------------------------|
| **Pre-Crash Stability**    | 1-20   | Price near fundamental with mild fluctuations; normal liquidity       | Market equilibrium; no stress signals         |
| **Trigger Event**          | 21-25  | External shock (margin call simulation); initial 5% drop              | Exogenous event destabilizes market           |
| **Panic Cascade**          | 26-40  | Rapid 20-40% decline; sell orders dominate 80%+; liquidity evaporates | Fear contagion: "sell at any price" mentality |
| **Capitulation**           | 41-50  | Extreme volatility; maximum drawdown reached; volume spikes           | Last bulls liquidate; market bottom forms     |
| **Recovery/Stabilization** | 51-70  | Slow price recovery or L-shaped bottom; reduced volatility            | Value buyers emerge; new equilibrium          |

### Key Observable Curves

1. **Price**: L-shaped or U-shaped crash (unlike V-shaped flash crash)
2. **Sell Volume**: Sustained high levels throughout crash (not just spike)
3. **Volatility**: Elevated for extended period (10-20 rounds)
4. **Drawdown**: Monotonically increasing until capitulation

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                          | Expected Pattern                                  | What It Validates                          |
|-----------------------------------|---------------------------------------------------|--------------------------------------------|
| **Drawdown 20-50%**               | Matches historical crashes (1929: 48%, 2008: 57%) | Realistic panic calibration                |
| **Crash duration 15-30 rounds**   | Not instant like flash crash                      | Proper fear cascade mechanism              |
| **Sell ratio > 70% sustained**    | Persistent one-sided flow                         | Genuine panic, not technical glitch        |
| **Slow/no recovery**              | Unlike flash crash V-shape                        | Different mechanism (fundamentals damaged) |
| **Liquidity permanently reduced** | Market structure change                           | Real crash aftermath                       |

### Unreasonable Results (Simulation Failure Indicators)

- Price instantly recovers → Flash crash dynamics, not market crash
- Drawdown < 15% → Insufficient panic cascade
- Crash in 1-2 rounds → Missing slow fear contagion
- Buy/sell balanced during crash → Panic mechanism not working

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                         | Rationale                   |
|----------------|-------------------------------------------|-----------------------------|
| **50 rounds**  | Crash visible, recovery unclear           | Still in capitulation phase |
| **100 rounds** | Full crash cycle with stabilization       | Standard crash + aftermath  |
| **200 rounds** | Possible second crash or genuine recovery | Long-term dynamics emerge   |
| **500 rounds** | Multiple crash cycles; boom-bust evident  | Economic cycles visible     |

### Observable Metrics by Round Count

```
Round 50:  Max drawdown ~30%, still falling or flat
Round 100: Drawdown stabilized at 35-45%, early recovery signs
Round 200: Price at 60-80% of original; new equilibrium
Round 500: 2-3 crash cycles; mean reversion visible
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                            | Economic Interpretation         |
|---------------------------|--------------------------------------------|---------------------------------|
| **3-5 agents**            | Crash may not develop; too few for cascade | Need critical mass for panic    |
| **8-10 agents** (default) | Realistic crash cascade                    | Sufficient for fear contagion   |
| **20-30 agents**          | Deeper crashes; stronger herding           | More participants amplify panic |
| **50+ agents**            | Very deep crashes possible; systemic risk  | Coordination failures dominate  |

### Agent Type Effects

| More of This Agent    | Effect on Crash                            |
|-----------------------|--------------------------------------------|
| **Leveraged Traders** | Deeper crashes; margin spirals             |
| **Panic Sellers**     | Faster cascade; earlier capitulation       |
| **Value Investors**   | Shallower crashes; earlier floor           |
| **Market Makers**     | More orderly decline; liquidity maintained |

### Critical Ratios

```
Panic-prone agents / Stabilizing agents:

Ratio > 4:1 → Catastrophic crashes (>50% drawdown)
Ratio 2:1   → Severe but recoverable crashes (30-40%)
Ratio 1:1   → Mild corrections (10-20%)
Ratio < 1:1 → No crash develops
```

---

## Key Metrics

| Metric            | Formula                | Source                | Purpose          |
|-------------------|------------------------|-----------------------|------------------|
| **Max Drawdown**  | (peak - trough) / peak | Standard              | Crash severity   |
| **Sell Pressure** | sell_vol / total_vol   | Kyle (1985)           | Panic intensity  |
| **Liquidity**     | bid_depth              | Market microstructure | Available buyers |
| **Cascade Speed** | Δprice / Δtime         | Brunnermeier (2009)   | Crash velocity   |

---

## Crash Cascade Mechanism

```
1. TRIGGER: Initial shock (margin call, bad news)
2. FORCED SELLING: Leveraged investors must sell
3. PRICE IMPACT: Sales push price down
4. MARGIN SPIRAL: Lower prices → more margin calls
5. LIQUIDITY DRY-UP: Buyers withdraw
6. CRASH: Rapid price collapse
```

---

## Using the Evaluation Module

```python
from masim.evaluation.finance import (
    # Crash Metrics
    calculate_max_drawdown,
    calculate_volume_metrics,
    calculate_liquidity_metrics,
    calculate_returns,
    
    # Visualization
    plot_price_dynamics,
    plot_bubble_crash_analysis,
    plot_agent_activity,
)

# Load simulation data
prices = {...}

# Calculate crash metrics
drawdown, peak_idx, trough_idx = calculate_max_drawdown(list(prices.values()))
print(f"Max drawdown: {drawdown:.1f}%")
print(f"Crash duration: {trough_idx - peak_idx} rounds")

# Visualization
plot_bubble_crash_analysis(prices, output_path="crash.png")
```

---

## Success Criteria

| Criterion          | Target             | Evidence                |
|--------------------|--------------------|-------------------------|
| **Max Drawdown**   | > 20%              | Significant crash       |
| **Crash Speed**    | < 5 rounds         | Rapid collapse          |
| **Sell Ratio**     | > 80% during crash | Panic dominance         |
| **Liquidity Drop** | > 50%              | Market maker withdrawal |

---

## References

1. Brunnermeier, M.K., & Pedersen, L.H. (2009). Market Liquidity and Funding Liquidity. *RFS*.
2. Kyle, A.S., & Obizhaeva, A.A. (2016). Market Microstructure Invariance.
3. Minsky, H.P. (1986). *Stabilizing an Unstable Economy*.
