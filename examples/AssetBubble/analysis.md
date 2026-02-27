# AssetBubble Analysis - Evaluation Methodology

## Overview

This document describes the evaluation methodology for detecting and measuring **asset bubbles** driven by positive feedback trading and "greater fool" dynamics.

---

## Observable Phenomena

### Expected Simulation Outcomes

When running this simulation, you should observe the following emergent behaviors:

| Phase                | Rounds | Observable Phenomena                                                                               | Economic Interpretation                                                       |
|----------------------|--------|----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| **Initiation**       | 1-20   | Price slowly drifts upward from fundamental (100); Momentum speculators begin accumulating         | Random noise creates initial positive returns; early speculators detect trend |
| **Amplification**    | 21-60  | Price acceleration; increased trading volume; momentum investors dominate                          | Positive feedback loop: higher prices → more buyers → higher prices           |
| **Peak Formation**   | 61-80  | Price reaches maximum deviation (typically 30-50% above fundamental); arbitrageur positions at max | "Greater fool" dynamics exhaust willing buyers; rational sellers emerge       |
| **Correction/Crash** | 81-100 | Sharp price decline; volatility spike; panic selling                                               | Bubble bursts when marginal buyer disappears; liquidity crisis                |

### Key Observable Curves

1. **Price vs Fundamental**: S-shaped divergence followed by rapid convergence
2. **Trading Volume**: U-shaped (low → high at peak → high during crash)
3. **Volatility**: Hockey-stick pattern (low → spike at crash)
4. **Bubble Magnitude**: Bell-shaped cumulative deviation

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                                                 | Expected Pattern                            | What It Validates                       |
|----------------------------------------------------------|---------------------------------------------|-----------------------------------------|
| **Price deviation peaks at 20-50%**                      | Not 1000% or 1%; matches historical bubbles | Realistic feedback strength calibration |
| **Crash occurs within 20-30 rounds of peak**             | Sudden, not gradual                         | Proper cascade mechanism                |
| **Arbitrageur position inversely correlated with price** | Short at highs, cover at lows               | Rational agent behavior                 |
| **Volume spikes during crash**                           | 2-3x normal volume                          | Panic/forced liquidation dynamics       |
| **Volatility clustering**                                | High vol follows high vol                   | GARCH-like realistic dynamics           |

### Unreasonable Results (Simulation Failure Indicators)

- Price stays at fundamental forever → Noise trader impact too weak
- Price goes to infinity → No arbitrage constraint
- No crash occurs → Bubble deflation mechanism missing
- Instant crash (1-2 rounds) → Feedback loop too strong

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                                      | Rationale                                   |
|----------------|--------------------------------------------------------|---------------------------------------------|
| **50 rounds**  | Partial bubble; may not reach full peak                | Insufficient time for feedback accumulation |
| **100 rounds** | Complete bubble cycle (formation → peak → crash)       | Standard duration for full dynamics         |
| **200 rounds** | Multiple bubble cycles possible                        | Re-accumulation after crash                 |
| **500 rounds** | 2-4 distinct bubble episodes; long-term mean reversion | Repeated boom-bust cycles                   |

### Observable Metrics by Round Count

```
Round 50:  Max deviation ~15%, likely no crash yet
Round 100: Max deviation ~30%, crash around round 80-90
Round 200: Second bubble may form around round 150
Round 500: Statistical properties stabilize; ~4 cycles
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                                          | Economic Interpretation                   |
|---------------------------|----------------------------------------------------------|-------------------------------------------|
| **3-5 agents**            | High volatility; individual actions visible; thin market | Each trade moves price significantly      |
| **8-10 agents** (default) | Balanced dynamics; emergent patterns clear               | Sufficient diversity for realistic market |
| **20-30 agents**          | Smoother price path; smaller individual impact           | Law of large numbers begins; more stable  |
| **50+ agents**            | Very smooth; bubble magnitude may decrease               | Diverse opinions dampen extreme moves     |

### Agent Composition Effects

| Composition Change        | Effect on Bubble                          |
|---------------------------|-------------------------------------------|
| More momentum speculators | Larger bubbles, faster formation          |
| More arbitrageurs         | Smaller bubbles, earlier correction       |
| More noise traders        | Higher baseline volatility, random shocks |
| Balanced mix              | Realistic boom-bust dynamics              |

### Critical Ratios

```
Destabilizing agents (momentum + noise) / Stabilizing agents (arbitrageur + fundamental)

Ratio > 3:1 → Extreme bubbles, potential instability
Ratio 2:1   → Pronounced but controlled bubbles (recommended)
Ratio 1:1   → Minimal price deviation
Ratio < 1:1 → Price anchored to fundamental
```

---

## Key Metrics

| Metric                   | Formula             | Source             | Purpose              |
|--------------------------|---------------------|--------------------|----------------------|
| **Price Deviation**      | (P - F) / F × 100%  | Standard           | Bubble magnitude     |
| **Cumulative Bubble**    | Σ(P - F)            | Shiller (2000)     | Total deviation      |
| **Buy Ratio**            | buy_vol / total_vol | Kyle (1985)        | Directional pressure |
| **Momentum Persistence** | corr(r_t, r_{t-1})  | Jegadeesh & Titman | Trend strength       |

---

## Bubble Lifecycle Phases

```
1. INITIATION: Random shock creates positive return
2. AMPLIFICATION: Greater fools buy expecting higher prices
3. ACCELERATION: Positive feedback loop intensifies
4. PEAK: Arbitrageurs cannot offset; maximum deviation
5. CORRECTION: Supply exceeds demand; price collapses
```

---

## Using the Evaluation Module

```python
from masim.evaluation.finance import (
    # Bubble Metrics
    calculate_price_deviation,
    calculate_bubble_magnitude,
    calculate_volume_metrics,
    calculate_strategy_contribution,
    
    # Visualization
    plot_price_dynamics,
    plot_bubble_crash_analysis,
    plot_multi_panel_summary,
)

# Load simulation data
prices = {...}  # {round: price}
investor_quantities = {...}

# Calculate bubble metrics
deviation = calculate_price_deviation(prices, fundamental=100.0)
bubble = calculate_bubble_magnitude(prices, fundamental=100.0)

print(f"Max deviation: {max(deviation.values()):.1f}%")
print(f"Peak bubble: ${max(bubble.values()):.1f}")

# Visualization
plot_bubble_crash_analysis(prices, output_path="bubble.png")
```

---

## Success Criteria

| Criterion                  | Target                 | Evidence              |
|----------------------------|------------------------|-----------------------|
| **Price Deviation**        | Peak > 20%             | Significant bubble    |
| **Bubble Duration**        | > 10 rounds            | Sustained deviation   |
| **Greater Fool Volume**    | > 50% of buys          | Speculative dominance |
| **Arbitrageur Constraint** | Active but overwhelmed | Limits to arbitrage   |

---

## References

1. Shleifer, A., & Vishny, R.W. (1997). The Limits of Arbitrage. *Journal of Finance*.
2. Kindleberger, C.P. (2000). *Manias, Panics, and Crashes*.
3. De Long et al. (1990). Positive Feedback Investment Strategies. *Journal of Finance*.
