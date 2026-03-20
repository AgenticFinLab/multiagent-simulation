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
| **Max Drawdown**  | (peak − trough) / peak | Standard              | Crash severity   |
| **Sell Pressure** | sell_vol / total_vol   | Kyle (1985)           | Panic intensity  |
| **Liquidity**     | bid_depth              | Market microstructure | Available buyers |
| **Cascade Speed** | Δprice / Δtime         | Brunnermeier (2009)   | Crash velocity   |

---

## Mathematical Detail of Each Metric

### 1. Maximum Drawdown (MDD)

```
Running maximum price:
  P_max(t) = max_{s ≤ t} P(s)

Drawdown at round t:
  DD(t) = [P_max(t) − P(t)] / P_max(t)  ∈ [0, 1]

Maximum drawdown over horizon T:
  MDD = max_{t ≤ T} DD(t)

Calmar Ratio (return per unit of drawdown risk):
  Calmar = Total Return / MDD

Crash classification:
  MDD < 0.10  → minor dip
  MDD 0.10–0.20 → correction
  MDD 0.20–0.40 → crash (2008: 57%, 2020: 34%)
  MDD > 0.40  → depression-level crash
```

### 2. Sell Pressure Ratio

```
Sell Volume(t) = Σ_{i: q_i(t) < 0} |q_i(t)|
Buy  Volume(t) = Σ_{i: q_i(t) > 0}  q_i(t)

Sell Ratio(t) = Sell Volume(t) / [Sell Volume(t) + Buy Volume(t)]

Panic threshold: Sell Ratio > 0.75 (3:1 sellers dominate)

Cumulative Sell Pressure over crash window [t1, t2]:
  CSP = Σ_{t=t1}^{t2} Sell Volume(t) / Σ_{t} Total Volume(t)
```

### 3. Liquidity Drop & Recovery

```
Liquidity at time t:
  L(t) = BaseLiquidity + MM_Provision(t)

Liquidity ratio (normalised by pre-crash level):
  LR(t) = L(t) / L(0)

Crash onset: LR < 0.5 (more than 50% liquidity lost)

Price impact multiplier:
  λ(t) = BASE_IMPACT / L(t)

  L drops from 1.0 to 0.1:  λ increases 10×
  A 100-unit sell at L=1.0 moves price by λ·100 = 0.08·100 = 8
  A 100-unit sell at L=0.1 moves price by 0.08/0.1·100 = 80  (⇒ catastrophic)
```

### 4. Cascade Speed (Velocity)

```
Crash velocity (price decline rate):
  v(t) = [P(t) − P(t−1)] / P(t−1)   (negative during crash)

Peak crash velocity:
  v_peak = min_{t} v(t)    (most negative round-over-round return)

Crash duration:
  τ = t_bottom − t_peak   (rounds from peak to trough)

Classification:
  τ < 5 rounds   → flash crash
  τ = 5–20 rounds → acute crash (1987, 2020)
  τ > 20 rounds  → bear market (2007–2009)
```

### 5. Volatility Clustering During Crash

```
Rolling volatility (w = 10):
  σ(t) = Std({r(t−w+1), ..., r(t)})

Volatility ratio (crash vs pre-crash):
  VR = σ_crash / σ_pre
  VR > 3 indicates panic regime

GARCH(1,1) representation of crash dynamics:
  σ²(t) = ω + α⋅r²(t−1) + β⋅σ²(t−1)
  During crashes: high r²(t−1) → σ² spikes → volatility clustering.
```

### 6. Liquidity Spiral Score & Validation

```
Liquidity Spiral Index (LSI):
  LSI = Corr(DD(t), 1/L(t))   over crash window

  LSI > 0.6  → strong spiral: drawdown and illiquidity co-move
  LSI < 0.3  → crash driven by fundamentals, not spiral

Overall fit score:
  s1 = min(MDD / 0.20, 1.0)          → rewards MDD ≥ 20%
  s2 = min(CSP / 0.70, 1.0)          → rewards sustained sell ratio ≥ 70%
  s3 = min((1 − LR_min) / 0.50, 1.0) → rewards ≥50% liquidity drop
  s4 = 1.0 if recovery_detected else 0.5

  overall_score = 0.40×s1 + 0.30×s2 + 0.20×s3 + 0.10×s4

Target: overall_score ≥ 0.60.
```

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
