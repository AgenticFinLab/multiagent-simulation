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

## Mathematical Detail of Each Metric

### 1. Return ACF — Market Efficiency Test

Let r(t) = [P(t) − P(t−1)] / P(t−1).

```
AC_r(τ) = Corr(r(t), r(t−τ))

Null hypothesis (efficient market): AC_r(τ) = 0 for all τ ≥ 1
```

**Ljung-Box Q-test for return autocorrelation:**
```
Q_r(m) = T(T+2) · Σ_{τ=1}^{m} AC_r(τ)² / (T − τ)

Under H0: Q_r(m) ~ χ²(m)

For volatility clustering: Q_r(10) < 18.3 (not significant at 5%)
⇒ returns are approximately unpredictable even when volatility clusters
```

Targets:
```
|AC_r(1)| < 0.15  (market approximately efficient)
|AC_r(5)| < 0.10  (no multi-round predictability)
```

---

### 2. Squared Return ACF — ARCH/GARCH Volatility Clustering Test

The **key diagnostic** for volatility clustering: squared returns must be autocorrelated
even when returns themselves are not.

```
AC_r2(τ) = Corr(r(t)², r(t−τ)²)

GARCH(1,1) theoretical ACF of squared returns:
  AC_r2(τ) = [α(α+β)]^{τ-1} · α² / [1 − (α+β)² − 2α²ρ]
  where ρ = Corr(r²(t), σ²(t))

Simplified at lag 1:
  AC_r2(1) ≈ α² + αβ = α(α+β)
```

For the GARCH(1,1) with typical parameters (α = 0.2, β = 0.7):
```
AC_r2(1) ≈ 0.2 · (0.2 + 0.7) = 0.18
```

**Engle (1982) ARCH-LM test:**
```
Regress: r(t)² = a_0 + a_1·r(t−1)² + ... + a_m·r(t−m)² + ε(t)

LM statistic: T · R² ~ χ²(m)

Reject no-ARCH when: T·R² > χ²_{0.05}(m)
  For m=5, T=100: critical value = 11.07
```

Target: AC_r2(1) > 0.10 (GARCH signature present).

---

### 3. Clustering Ratio — GARCH vs Random Walk Discrimination

```
Clustering Ratio (CR) = AC_r2(1) / |AC_r(1)|

Interpretation:
  CR >> 1: volatility clusters but prices don’t trend (GARCH-like, realistic)
  CR ≈ 1:  both cluster equally (momentum dominates)
  CR < 1:  returns autocorrelated more than squared (unusual / unstable)
```

**Theoretical baseline values:**
```
For pure GARCH(1,1) with α+β = 0.9, α = 0.2:
  AC_r(1) ≈ 0 (by market efficiency)
  AC_r2(1) ≈ 0.18
  CR → ∞ (theoretically infinite)

For our multi-agent simulation:
  Expected CR ≈ 2–10 (strong GARCH signature)
  CR < 2:  volatility clustering marginal
  CR > 5:  clean GARCH regime switching
```

---

### 4. Volatility Persistence — GARCH Half-Life

The GARCH(1,1) formal specification:

```
σ²(t) = ω + α · r²(t−1) + β · σ²(t−1)

Persistence parameter:  p = α + β
  p < 1:  covariance-stationary (volatility reverts to unconditional mean)
  p = 1:  IGARCH (volatility is permanent)
  p > 1:  explosive (unrealistic)

Unconditional variance:
  σ²_∞ = ω / (1 − α − β)  for p < 1

Half-life of volatility shock:
  t_½ = log(0.5) / log(α + β)

Typical values:
  p = 0.90 → t_½ ≈ 6.6 rounds
  p = 0.95 → t_½ ≈ 13.5 rounds
  p = 0.99 → t_½ ≈ 69 rounds
```

Expected in simulation: p ≈ 0.85–0.95, t_½ ≈ 5–15 rounds.

---

### 5. Regime Detection — High-Low Volatility Episodes

```
Rolling volatility:
  σ(t) = std(r[t−w+1:t])  where w = 10 rounds

Threshold classification:
  High-vol regime: σ(t) > μ_σ + 1.5 · std_σ
  Low-vol regime:  σ(t) < μ_σ + 0.5 · std_σ

Episode length distribution:
  If volatility follows a 2-state Markov chain with transition probabilities
  p_HH (persist in high vol), p_LL (persist in low vol):

  E[high-vol episode length] = 1 / (1 − p_HH)
  E[low-vol episode length]  = 1 / (1 − p_LL)
```

Expected: high-vol episodes last 5–20 rounds, low-vol episodes last 10–40 rounds.

---

### 6. Validation Score Formula

```
score_eff   = 1.0 if |AC_r(1)| < 0.10 else 0.5 if |AC_r(1)| < 0.20 else 0.0
score_garch = 1.0 if AC_r2(1) > 0.10  else 0.5 if AC_r2(1) > 0.05 else 0.0
score_cr    = 1.0 if CR > 2.0          else 0.5 if CR > 1.5         else 0.0
score_reg   = 1.0 if N_regimes ≥ 2     else 0.5 if N_regimes == 1  else 0.0
  where N_regimes = number of distinct high-vol episodes

overall_score = 0.30 · score_eff + 0.35 · score_garch + 0.25 · score_cr + 0.10 · score_reg
```

Target: `overall_score > 0.6` (GARCH signature with efficient returns).

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
