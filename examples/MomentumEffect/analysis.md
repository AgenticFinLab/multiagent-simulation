# MomentumEffect Analysis - Evaluation Methodology

## Overview

This document describes the evaluation methodology for detecting the **momentum effect** - the tendency for past winners to continue outperforming.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                       | Rounds | Observable Phenomena                                          | Economic Interpretation                       |
|-----------------------------|--------|---------------------------------------------------------------|-----------------------------------------------|
| **Initial Trend Formation** | 1-15   | Random walk with occasional directional drift                 | No clear trend yet; noise dominates           |
| **Trend Recognition**       | 16-30  | Momentum traders detect pattern; consistent direction emerges | Underreaction: slow information incorporation |
| **Trend Amplification**     | 31-60  | Strong directional movement; positive autocorrelation visible | Positive feedback: trend followers join       |
| **Trend Exhaustion**        | 61-80  | Momentum weakens; autocorrelation decreases                   | Information fully incorporated                |
| **Potential Reversal**      | 81-100 | Trend may reverse; mean reversion begins                      | Overreaction correction sets in               |

### Key Observable Curves

1. **Price**: Staircase pattern with persistent directional moves
2. **Returns**: Clustered positive (or negative) runs of 5-15 rounds
3. **Autocorrelation Function**: Positive for lags 1-10, declining with lag
4. **Cumulative Returns**: Smooth upward (or downward) slope during trends

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                                 | Expected Pattern                       | What It Validates        |
|------------------------------------------|----------------------------------------|--------------------------|
| **Positive lag-1 autocorrelation > 0.1** | Returns predict next returns           | Momentum effect present  |
| **Trend duration 10-20 rounds**          | Matches 3-12 month real-world momentum | Realistic persistence    |
| **Momentum profit > 0**                  | Long winners, short losers profitable  | Tradeable anomaly        |
| **Gradual autocorrelation decay**        | ACF decreases with lag                 | Natural trend exhaustion |
| **Eventual reversal**                    | Long-lag ACF turns negative            | Overreaction correction  |

### Unreasonable Results (Simulation Failure Indicators)

- Zero or negative lag-1 ACF → No momentum; random walk
- ACF > 0.5 for all lags → Unrealistic trend persistence
- Trends last only 1-2 rounds → Noise, not momentum
- No reversal ever → Missing mean reversion

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                         | Rationale                 |
|----------------|-------------------------------------------|---------------------------|
| **30 rounds**  | One trend period visible                  | May not see full cycle    |
| **100 rounds** | 2-3 distinct trend periods                | Standard momentum horizon |
| **200 rounds** | Multiple momentum cycles + reversals      | Both effects visible      |
| **500 rounds** | Statistical momentum properties stabilize | Robust ACF estimates      |

### Observable Metrics by Round Count

```
Round 30:  One trend; ACF(1) ~0.15
Round 100: 2-3 trends; ACF(1) ~0.12, ACF(20) ~0
Round 200: Clear momentum + reversal; ACF pattern stable
Round 500: Statistically significant ACF; multiple cycles
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                           | Economic Interpretation       |
|---------------------------|-------------------------------------------|-------------------------------|
| **3-5 agents**            | Noisy trends; hard to detect momentum     | Individual impact too large   |
| **8-10 agents** (default) | Clear momentum patterns                   | Sufficient trend followers    |
| **20-30 agents**          | Stronger momentum; more persistent trends | More followers amplify signal |
| **50+ agents**            | Momentum may decrease; efficient market   | Diverse opinions cancel out   |

### Agent Type Effects

| More of This Agent      | Effect on Momentum                   |
|-------------------------|--------------------------------------|
| **Momentum Traders**    | Stronger, longer trends              |
| **Noise Traders**       | Disrupts trends; higher ACF variance |
| **Fundamental Traders** | Limits trend; earlier reversal       |
| **Contrarian Traders**  | Weakens momentum; faster reversal    |

### Critical Ratios

```
Momentum traders / Contrarian traders:

Ratio > 3:1 → Very strong momentum; delayed reversal
Ratio 2:1   → Clear momentum effect (realistic)
Ratio 1:1   → Weak momentum; quick reversals
Ratio < 1:1 → Reversal dominates; no momentum
```

---

## Mathematical Detail of Each Metric

### 1. Return Autocorrelation (AC) — Core Momentum Statistic

Let r(t) = [P(t) − P(t−1)] / P(t−1) be the log-approximation return.

```
AC(τ) = Cov(r(t), r(t−τ)) / Var(r(t))

       = [Σ_t (r(t) − r̄)(r(t−τ) − r̄)] / [Σ_t (r(t) − r̄)²]
```

**Theoretical AC under AR(1) momentum model:**
If P(t) = P(t−1) + α·[P(t−1) − P(t−2)] + ε(t) (AR(1) in changes), then:
```
AC(1) = α / (1 + α²)

For our model (α ≈ 0.15–0.25):  AC(1) ≈ 0.14–0.22
```

The **ACF decay** determines trend duration:
```
AC(τ) ≈ α^τ / (1 + α²) · correction_factor

Trend half-life:  t_½ = −log(2) / log(α) ≈ 6 rounds for α = 0.2
```

**Ljung-Box test for momentum significance:**
```
Q(m) = T(T+2) · Σ_{τ=1}^{m} AC(τ)² / (T − τ)

Under null (no momentum): Q(m) ~ χ²(m)
Momentum confirmed when: Q(m) > χ²_{0.05}(m)
  For m=10:  Q > 18.3  at 5% significance
```

---

### 2. Momentum Profit — Jegadeesh-Titman (1993) Strategy Return

The J&T (J, K) strategy: form portfolio on J-period past return, hold K periods.

```
Formation return (past J rounds):
  R_past(t, J) = [P(t) − P(t−J)] / P(t−J)

Winner portfolio: stocks with R_past > median_R_past
Loser portfolio:  stocks with R_past < median_R_past

Momentum profit:
  π(t, K) = R_future_winners(t, K) − R_future_losers(t, K)

Where:
  R_future(t, K) = [P(t+K) − P(t)] / P(t)
```

In our single-asset simulation, momentum profit is measured as the strategy P&L
of MomentumTrader vs ContrarianTrader:
```
π_momentum = PnL_MomentumTrader - PnL_ContrarianTrader

Expected π_momentum > 0 when AC(1) > 0  (momentum effect present)
```

---

### 3. Trend Persistence — Duration Distribution

A **trend** is a consecutive run of same-sign returns:
```
Trend starts at t_0 when sign(r(t_0)) ≠ sign(r(t_0−1))
Trend ends at t_0 + L when sign(r(t_0 + L + 1)) ≠ sign(r(t_0))

Trend length L is geometrically distributed under momentum:
  P(L = k) = (1 − p_flip)^{k−1} · p_flip
  where p_flip = P(r < 0 | r_{t−1} > 0) = (1 − AC(1)) / 2

Expected trend length:
  E[L] = 1 / p_flip = 2 / (1 − AC(1))

For AC(1) = 0.15:  E[L] ≈ 2.35 rounds
For AC(1) = 0.30:  E[L] ≈ 2.86 rounds
For full multi-agent simulation: effective L ≈ 8–15 rounds
  (agent capital effects extend persistence beyond theoretical minimum)
```

---

### 4. Cumulative Return — Trend Magnitude

The cumulative return over a trend of length L:
```
CR(L) = ∏_{k=t_0}^{t_0+L} (1 + r(k)) − 1
       ≈ Σ_{k=t_0}^{t_0+L} r(k)   (log approximation)

Expected cumulative return during trend:
  E[CR] = E[r] · E[L] = μ_r · 2 / (1 − AC(1))
```

The **momentum premium** (excess return over random walk):
```
Momentum excess = E[CR | momentum] − E[CR | random walk]
               = μ_r · [2/(1−AC(1)) − 2] / 2
               = μ_r · AC(1) / (1 − AC(1))

For AC(1) = 0.2, μ_r = 0.5%:  momentum premium ≈ 0.125% per round
```

---

### 5. Validation Score Formula

```
score_ac    = 1.0 if AC(1) > 0.10 else  0.5 if AC(1) > 0.05 else 0.0
score_dur   = 1.0 if E[L] > 5    else  0.5 if E[L] > 3    else 0.2
score_prof  = 1.0 if π_momentum > 0 else 0.0
score_rev   = 0.5 if AC(20) < 0  else 0.0   (eventual reversal bonus)

overall_score = 0.40 · score_ac + 0.30 · score_dur + 0.20 · score_prof + 0.10 · score_rev
```

Target: `overall_score > 0.5` (AC(1) > 0.05 with positive momentum profit).

---

## Key Metrics

| Metric                     | Formula                        | Source                    | Purpose           |
|----------------------------|--------------------------------|---------------------------|-------------------|
| **Return Autocorrelation** | corr(r_t, r_{t-k})             | Jegadeesh & Titman (1993) | Momentum strength |
| **Momentum Profit**        | Σ(long winners - short losers) | Standard                  | Strategy return   |
| **Trend Persistence**      | Duration of same-sign returns  | Technical analysis        | Trend length      |

---

## Momentum Theory

```
Behavioral Explanation:
- Underreaction: Investors slowly incorporate new information
- Positive feedback: Trend followers amplify initial moves
- Result: Returns persist for 3-12 months

Price Pattern:
  P(t+1) = P(t) + λ × trend_signal + ε
  
Where λ > 0 creates momentum (price continuation)
```

---

## Using the Evaluation Module

```python
from masim.evaluation.finance import (
    # Momentum Metrics
    calculate_autocorrelation,
    calculate_returns,
    calculate_rolling_volatility,
    
    # Visualization
    plot_returns_analysis,
    plot_price_dynamics,
)

# Load simulation data
prices = {...}

# Calculate momentum metrics
returns = calculate_returns(prices)
acf = calculate_autocorrelation(list(returns.values()), max_lag=10)

print(f"Lag-1 autocorrelation: {acf[0]:.3f}")
print(f"Momentum detected: {acf[0] > 0.1}")

# Visualization
plot_returns_analysis(prices, output_path="momentum.png")
```

---

## Success Criteria

| Criterion                | Target     | Evidence            |
|--------------------------|------------|---------------------|
| **Return ACF (lag 1-5)** | > 0.1      | Positive momentum   |
| **Trend Duration**       | > 5 rounds | Persistent trends   |
| **Momentum Profit**      | > 0        | Strategy profitable |

---

## References

1. Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers. *Journal of Finance*.
2. Hong, H., & Stein, J.C. (1999). A Unified Theory of Underreaction, Momentum Trading. *Journal of Finance*.
