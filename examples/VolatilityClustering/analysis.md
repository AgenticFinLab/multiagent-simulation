# VolatilityClustering Analysis - Evaluation Methodology

## Overview

This document describes the evaluation methodology for detecting **volatility clustering** (GARCH-like dynamics) in the simulation. Volatility clustering is the empirical observation that "large changes tend to be followed by large changes, of either sign" (Mandelbrot, 1963).

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                      | Rounds | Observable Phenomena                                 | Economic Interpretation                                |
|----------------------------|--------|------------------------------------------------------|--------------------------------------------------------|
| **Low Volatility Regime**  | 1-20   | Small price changes (±1%); squared returns near zero | Market calm; fundamentalists dominate                  |
| **Shock Event**            | 21-25  | Sudden large move (5-10%); volatility spikes         | News/noise triggers regime change                      |
| **High Volatility Regime** | 26-50  | Persistent large moves; volatility elevated          | "Volatility begets volatility"; trend followers active |
| **Decay Phase**            | 51-70  | Gradually decreasing volatility; moves shrinking     | Mean reversion in volatility                           |
| **Return to Calm**         | 71-100 | Back to low volatility regime                        | Fundamentalists re-anchor prices                       |

### Key Observable Curves

1. **Returns**: Approximately zero autocorrelation (random walk)
2. **Squared Returns**: Positive autocorrelation (volatility clustering)
3. **Rolling Volatility**: Regime-switching pattern (low → high → low)
4. **Volatility Persistence**: Exponential decay after shocks

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                         | Expected Pattern                | What It Validates          |
|----------------------------------|---------------------------------|----------------------------|
| **Return ACF ≈ 0**               | No predictability in returns    | Market efficiency          |
| **Squared Return ACF > 0.1**     | Large moves cluster together    | GARCH-like dynamics        |
| **Clustering Ratio > 2**         | sq_ACF / return_ACF             | Proper vol dynamics        |
| **Regime duration 10-30 rounds** | Persistent high/low vol periods | Realistic regime switching |
| **Gradual vol decay**            | Half-life 5-15 rounds           | Not instant normalization  |

### Unreasonable Results (Simulation Failure Indicators)

- Return ACF > 0.2 → Market not efficient; momentum too strong
- Squared Return ACF < 0 → No volatility clustering
- Vol regimes last 1-2 rounds → Too rapid switching
- Vol never decays → Infinite persistence (unrealistic)

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                              | Rationale                   |
|----------------|------------------------------------------------|-----------------------------|
| **50 rounds**  | One regime transition visible                  | May miss full cycle         |
| **100 rounds** | 1-2 complete high-low cycles                   | Standard observation window |
| **200 rounds** | Multiple regime switches; robust ACF estimates | Statistical significance    |
| **500 rounds** | Stable GARCH parameters estimable              | Long-run properties visible |

### Observable Metrics by Round Count

```
Round 50:  One vol spike; ACF estimates noisy
Round 100: Clear clustering; sq_ACF ~ 0.15
Round 200: Multiple regimes; robust clustering ratio
Round 500: GARCH(1,1) parameters estimable
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                                | Economic Interpretation        |
|---------------------------|------------------------------------------------|--------------------------------|
| **3-5 agents**            | Extreme clustering; single agent can trigger   | Thin market; high impact       |
| **8-10 agents** (default) | Clear volatility regimes                       | Sufficient for regime dynamics |
| **20-30 agents**          | Smoother transitions; shorter high-vol periods | Heterogeneity dampens shocks   |
| **50+ agents**            | Weak clustering; efficient market              | Diverse opinions stabilize     |

### Agent Type Effects

| More of This Agent     | Effect on Volatility Clustering              |
|------------------------|----------------------------------------------|
| **Trend Followers**    | Stronger clustering; longer high-vol regimes |
| **Fundamentalists**    | Faster decay; shorter high-vol periods       |
| **Noise Traders**      | More regime switches; random shocks          |
| **Volatility Traders** | Dampens extremes; shorter regimes            |

### Critical Ratios

```
Trend followers / Fundamentalists:

Ratio > 2:1 → Strong clustering; persistent high vol
Ratio 1:1   → Moderate GARCH dynamics (realistic)
Ratio 1:2   → Weak clustering; quick vol normalization
Ratio < 1:3 → No clustering; constant low volatility
```

---

## Key Metrics

| Metric                     | Formula               | Source            | Purpose                   |
|----------------------------|-----------------------|-------------------|---------------------------|
| **Return ACF**             | corr(r_t, r_{t-k})    | Engle (1982)      | Should be ~0 (efficiency) |
| **Squared Return ACF**     | corr(r²_t, r²_{t-k})  | Bollerslev (1986) | Should be >0 (GARCH)      |
| **Volatility Persistence** | Half-life of σ shocks | GARCH theory      | Measures decay speed      |
| **Regime Detection**       | High/Low vol episodes | Cont (2001)       | Identify vol regimes      |

---

## GARCH Signature Test

The key test for volatility clustering:

1. **Returns should be approximately uncorrelated** (efficient market)
2. **Squared returns should be positively autocorrelated** (volatility clustering)

```
GARCH(1,1): σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}

Persistence = α + β (higher = slower mean reversion)
```

---

## Using the Evaluation Module

```python
from masim.evaluation.finance import (
    # GARCH Metrics
    calculate_garch_signature,
    calculate_volatility_persistence,
    calculate_return_clustering,
    detect_volatility_regimes,
    
    # Core Metrics
    calculate_returns,
    calculate_rolling_volatility,
    
    # Visualization
    plot_returns_analysis,
    plot_volatility_analysis,
    plot_multi_panel_summary,
)

# Load simulation data
prices = {...}  # {round: price}

# GARCH signature test
garch_result = calculate_garch_signature(prices)
print(f"Has GARCH signature: {garch_result['has_garch_signature']}")
print(f"Interpretation: {garch_result['interpretation']}")

# Volatility regimes
volatility = calculate_rolling_volatility(prices, window=10)
regimes = detect_volatility_regimes(volatility)
print(f"High vol episodes: {len(regimes['high_vol_episodes'])}")

# Visualization
plot_returns_analysis(prices, output_path="returns_analysis.png")
plot_volatility_analysis(prices, output_path="volatility.png")
```

---

## Success Criteria

| Criterion              | Target                  | Evidence                      |
|------------------------|-------------------------|-------------------------------|
| **Return ACF**         | \|ACF\| < 0.15 at lag 1 | Returns uncorrelated          |
| **Squared Return ACF** | ACF > 0.1 at lag 1      | Volatility clusters           |
| **Clustering Ratio**   | > 2.0                   | sq_return_acf / return_acf    |
| **Regime Persistence** | > 5 rounds              | Episodes last multiple rounds |

---

## Expected Behavior

```
Phase 1: LOW VOLATILITY (Fundamentalists dominate)
  - Return ACF ≈ 0
  - Squared Return ACF ≈ 0
  - Stable prices near fundamental

Phase 2: SHOCK (Noise trader or trend trigger)
  - Volatility spike
  - Trend followers react

Phase 3: HIGH VOLATILITY REGIME
  - Squared Return ACF > 0.1 (clustering)
  - Trend followers amplify
  - Volatility persists

Phase 4: DECAY (Fundamentalists pull back)
  - Gradual mean reversion
  - Volatility decreases
```

---

## References

1. Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. *Journal of Econometrics*.
2. Engle, R.F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*.
3. Cont, R. (2001). Empirical Properties of Asset Returns: Stylized Facts. *Quantitative Finance*.
4. Mandelbrot, B. (1963). The Variation of Certain Speculative Prices. *Journal of Business*.
