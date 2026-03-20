# HerdEffect Analysis - Metrics Documentation

## Overview

This document describes all analysis metrics used to detect and measure **emergent herding behavior** in the HerdEffect simulation. These metrics are based on academic literature on behavioral finance and information cascades.

---

## Metrics Summary

| Metric                     | Formula                   | Source                     | Purpose                     |
|----------------------------|---------------------------|----------------------------|-----------------------------|
| Bid Convergence (CV)       | CV = σ(bids) / μ(bids)    | Standard statistics        | Measure bid dispersion      |
| Directional Agreement (DA) | DA = \|Σ sign(ΔBid)\| / N | Chang et al. (2000)        | Detect behavioral alignment |
| Information Cascade        | ICM = contrarian_ratio    | Bikhchandani et al. (1992) | Measure signal ignoring     |
| Cross-Sectional Std        | CSSD = σ(bids)            | LSV (1992)                 | LSV herding measure         |
| Price Deviation            | PD = (P - F) / F          | Standard                   | Bubble magnitude            |
| Rolling Volatility         | σ(P[-w:])                 | Standard                   | Market stability            |
| Autocorrelation            | corr(r_t, r_{t-lag})      | Jegadeesh & Titman (1993)  | Momentum persistence        |
| Bubble Magnitude           | Σ(P - F)                  | Standard                   | Cumulative deviation        |

---

## Detailed Metric Definitions

### 1. Bid Convergence Index (CV)

**Definition**: Coefficient of Variation of investor bids at each round.

```
CV_t = std(Bid_1,t, Bid_2,t, ..., Bid_N,t) / mean(Bid_1,t, ..., Bid_N,t)
```

**Academic Source**: Standard statistical measure, applied to behavioral finance.

**Interpretation**:
| CV Value         | Interpretation                             |
|------------------|--------------------------------------------|
| CV < 0.05        | **Strong Herding** - bids highly converged |
| 0.05 ≤ CV < 0.10 | Moderate herding                           |
| 0.10 ≤ CV < 0.20 | Weak herding / normal market               |
| CV ≥ 0.20        | Dispersed opinions - no herding            |

**Success Criteria**: Simulation shows CV decreasing over time as herding forms.

---

### 2. Directional Agreement (DA)

**Definition**: Proportion of investors moving in the same direction.

```
DA_t = |Σ(sign(Bid_{i,t} - Bid_{i,t-1}))| / N
```

**Academic Source**: 
- Chang, E.C., Cheng, J.W., & Khorana, A. (2000). *An examination of herd behavior in equity markets: An international perspective*. Journal of Banking & Finance, 24(10), 1651-1679.

**Interpretation**:
| DA Value       | Interpretation                                           |
|----------------|----------------------------------------------------------|
| DA > 0.8       | **Strong Herding** - all investors moving same direction |
| 0.6 < DA ≤ 0.8 | Moderate alignment                                       |
| 0.4 < DA ≤ 0.6 | Random behavior (no herding)                             |
| DA ≤ 0.4       | Contrarian dominance                                     |

**Success Criteria**: DA > 0.8 for multiple consecutive rounds indicates herding.

---

### 3. Information Cascade Measure (ICM)

**Definition**: Proportion of investors ignoring their private signal (fundamental value).

```
Logic:
- If P > F (fundamental): rational signal = SELL
- If investor bids ABOVE market anyway: ignoring signal = CASCADE

ICM_t = (investors ignoring private signal) / N
```

**Academic Source**:
- Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). *A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades*. Journal of Political Economy, 100(5), 992-1026.

**Interpretation**:
| ICM Value       | Interpretation                                      |
|-----------------|-----------------------------------------------------|
| ICM > 0.6       | **Strong Cascade** - majority ignoring fundamentals |
| 0.4 < ICM ≤ 0.6 | Moderate cascade                                    |
| ICM ≤ 0.4       | Market following fundamentals                       |

**Success Criteria**: ICM rises during bubble formation.

---

### 4. Cross-Sectional Standard Deviation (CSSD)

**Definition**: Standard deviation of bids across all investors at each round.

```
CSSD_t = std(Bid_1,t, Bid_2,t, ..., Bid_N,t)
```

**Academic Source**:
- Lakonishok, J., Shleifer, A., & Vishny, R.W. (1992). *The impact of institutional trading on stock prices*. Journal of Financial Economics, 32(1), 23-43.
- Christie, W.G., & Huang, R.D. (1995). *Following the pied piper: Do individual returns herd around the market?* Financial Analysts Journal, 51(4), 31-37.

**Interpretation**:
| CSSD Value    | Interpretation           |
|---------------|--------------------------|
| Low (< $2)    | High consensus = herding |
| Medium ($2-5) | Normal dispersion        |
| High (> $5)   | Diverse opinions         |

**Success Criteria**: CSSD decreases as herding intensifies.

---

### 5. Price Deviation from Fundamental

**Definition**: Percentage deviation of market price from fundamental value.

```
PD_t = (P_t - F) / F × 100%

Where: F = 100.0 (fundamental value)
```

**Interpretation**:
| PD Value        | Interpretation                         |
|-----------------|----------------------------------------|
| PD > 20%        | **Bubble** - significant overvaluation |
| 10% < PD ≤ 20%  | Moderate deviation                     |
| -10% ≤ PD ≤ 10% | Normal range                           |
| PD < -10%       | Undervaluation / crash                 |

**Success Criteria**: PD rises during herd-driven bubble, crashes during correction.

---

### 6. Rolling Volatility

**Definition**: Standard deviation of prices over a rolling window.

```
σ_t = std(P_{t-w+1}, ..., P_t)

Where: w = window size (default 10 rounds)
```

**Academic Source**: Standard financial volatility measure.

**Interpretation**:
| Phase           | Volatility Behavior  |
|-----------------|----------------------|
| Normal          | Low, stable          |
| Bubble build-up | Increasing           |
| Bubble peak     | High                 |
| Crash           | Spike, then decrease |

**Success Criteria**: Volatility increases during herding, spikes during crash.

---

### 7. Price Return Autocorrelation

**Definition**: Correlation of returns with lagged returns (momentum persistence).

```
AC_t = corr(r_{t-w:t}, r_{t-w-lag:t-lag})

Where: r_t = (P_t - P_{t-1}) / P_{t-1}
```

**Academic Source**:
- Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*. Journal of Finance, 48(1), 65-91.

**Interpretation**:
| AC Value     | Interpretation                          |
|--------------|-----------------------------------------|
| AC > 0.3     | **Strong Momentum** - trend persistence |
| 0 < AC ≤ 0.3 | Moderate momentum                       |
| AC ≈ 0       | Random walk                             |
| AC < 0       | Mean reversion                          |

**Success Criteria**: Positive autocorrelation during herding (momentum effect).

---

### 8. Cumulative Bubble Magnitude

**Definition**: Accumulated deviation from fundamental over time.

```
Bubble_t = Σ_{s=1}^{t} (P_s - F)
```

**Interpretation**:
| Bubble Value    | Interpretation        |
|-----------------|-----------------------|
| Rising positive | Bubble forming        |
| Peak positive   | Maximum bubble        |
| Falling         | Correction/crash      |
| Negative        | Undervaluation period |

**Success Criteria**: Bubble magnitude shows clear rise-peak-fall pattern.

---

## Mathematical Detail of Each Metric

### 1. Bid Convergence Index (CV) — Formal Derivation

Let B_i(t) be the bid price submitted by investor i at round t, with N investors.

```
μ_bids(t) = (1/N) · Σ_i B_i(t)
σ_bids(t) = sqrt[(1/N) · Σ_i (B_i(t) − μ_bids(t))²]

CV(t) = σ_bids(t) / μ_bids(t)
```

**Why CV captures herding:** In a heterogeneous market with no herding, each agent
bids according to its own strategy. Strategy dispersion implies:
```
CV_baseline = sqrt[Σ w_i · (μ_i − μ)²] / μ ≈ 0.15–0.20
```
During a cascade, all bids converge toward the current market price P(t), since
momentum traders bid P·(1+λr) and aggressive traders also anchor to P(t). Thus:
```
CV(t)|_{cascade} → ε_small / P(t) ≈ 0.01–0.03
```
The **CV collapse** is the quantitative signature of emergent herding.

---

### 2. Directional Agreement (DA) — Signed Order Flow Correlation

Let s_i(t) = sign(B_i(t) − B_i(t−1)) be the direction of bid change for investor i.

```
DA(t) = |Σ_i s_i(t)| / N

  DA = 1.0  : all N investors moved bids in the same direction
  DA = 0.0  : exactly half up, half down (random / no herding)
  DA > 0.8  : strong behavioral convergence threshold
```

**Statistical baseline under no herding (null hypothesis):**
If each s_i is independently Bernoulli(½), then Σ s_i ~ Binomial(N, ½) − N/2.
E[DA] = E[|X|]/N where X ~ Binomial(N, 1/2) shifted. For large N:
```
E[DA_null] ≈ sqrt(2/(πN))   (half-normal approximation)
For N = 10: E[DA_null] ≈ 0.25
```
Herding signal when DA significantly exceeds sqrt(2/πN), especially DA > 0.8.

---

### 3. Information Cascade Measure (ICM) — Signal Abandonment Rate

Bikhchandani-Hirshleifer-Welch (1992) cascade condition formalized:

```
Private signal for rational investor: SELL if P > F (overvalued)

Cascade event: investor bids ABOVE market price when P > F
  (i.e., buys despite private signal saying sell)

ICM(t) = |{i : B_i(t) > P(t) AND P(t) > F}| / N
        + |{i : B_i(t) < P(t) AND P(t) < F}| / N
        (both overreaction cases)
```

**Bayesian interpretation:** In a rational Bayesian model, an agent ignores her
private signal if the public history (= price trend) is sufficiently strong:
```
Ignore signal when: P(public history) / P(private signal) > likelihood_ratio_threshold

In our emergent model: ICM rises as price trend overpowers fundamental anchor,
corresponding to agents weighting recent price history over F = 100.
```

---

### 4. Cross-Sectional Std (CSSD) — LSV Institutional Herding Measure

Lakonishok-Shleifer-Vishny (1992) measure of correlated institutional trading:

```
CSSD(t) = std(B_1(t), B_2(t), ..., B_N(t))
         = sqrt[(1/(N−1)) · Σ_i (B_i(t) − μ_bids(t))²]
```

Note: CSSD and CV convey related information but differ in scale. CSSD is in dollar
units (absolute dispersion); CV is dimensionless (relative dispersion). During herding:
```
CSSD → 0 as all bids converge
```

Relationship: CSSD(t) = CV(t) · μ_bids(t). For μ_bids ≈ P(t) ≈ 100–130 during bubble:
```
CSSD threshold: CSSD < $2 ≡ CV < 0.015–0.02 (strong herding)
```

---

### 5. Price Deviation from Fundamental — Bubble Gauge

```
PD(t) = (P(t) − F) / F = (P(t) − 100) / 100

Cumulative bubble area (total mispricing over simulation):
  BA = Σ_t max(0, P(t) − F) · Δt
```

The **decomposition** of price into fundamentals + bubble:
```
P(t) = F + B(t) + η(t)
  B(t) = endogenous bubble component driven by positive feedback
  η(t) = residual noise (mean-reverting)
```

Bubble formation speed (Phase 2–3 average):
```
dP/dt|_{bubble} = λ · [D_m + D_a − D_c − D_r]
               ≈ 0.1 · [0.8 · r · W / P − 0.5 · (P−F) · W_c / P²]
```
Peak deviation occurs when the net force equals zero (dP/dt = 0), defining the bubble top.

---

### 6. Rolling Volatility — Regime Indicator

```
σ(t) = std(P[t−w+1 : t])  where w = 10 (default window)

VZ-score (volatility z-score relative to baseline):
  VZ(t) = (σ(t) − μ_σ) / std_σ

  VZ > 2: elevated volatility (bubble formation or crash)
  VZ > 5: extreme volatility (crash/correction phase)
```

In the RiskAverseInvestor position rule:
```
Q_r ∝ 1/σ²(t) ⇒ as σ doubles, Q_r falls to 1/4
```
This creates a **positive feedback in volatility**: rising σ reduces stabilizing
capital, which allows more extreme moves, further raising σ. The volatility-position
feedback amplifies the crash once σ exceeds a critical threshold.

---

### 7. Return Autocorrelation — Momentum Persistence Score

Let r(t) = [P(t) − P(t−1)] / P(t−1) be the round-t return.

```
AC(τ) = Corr(r(t), r(t−τ)) = Cov(r,r_{−τ}) / Var(r)

For momentum effect:  AC(τ) > 0  for τ = 1, 2, ..., 10
For reversal/crash:   AC(τ) < 0  for τ = 10, ..., 20
```

**ARMA representation of cascade dynamics:**
During herding, prices approximately follow AR(1):
```
P(t) = (1 + α) · P(t−1) − γ · F + ε(t)
  α = 0.1 · (0.3 + 0.5) · W / P² (positive feedback coefficient)
```
AC(1) ≈ α during bubble formation. Typical AC(1) ≈ 0.2–0.4 during herding.

---

### 8. Cumulative Bubble Magnitude — Integral Measure

```
BM(T) = Σ_{t=1}^{T} (P(t) − F)   [sum over all rounds]

Normalized version:
  BM_norm = BM(T) / (F · T) = average % deviation per round
```

For a pure AR(1) bubble with coefficient α:
```
E[BM(T)] = P_0 · [(1+α)^T − 1] / α − F · T   (growing faster than linearly)
```
The peak of BM and its subsequent decline traces the full bubble lifecycle.

---

### 9. Validation Score Formula

The simulation passes if the following composite score exceeds 0.6:

```
score_cv  = 1.0 if min(CV)  < 0.05 else  0.5 if min(CV)  < 0.10 else 0.2
score_da  = 1.0 if max(DA)  > 0.80 else  0.5 if max(DA)  > 0.60 else 0.2
score_icm = 1.0 if max(ICM) > 0.50 else  0.5 if max(ICM) > 0.30 else 0.2
score_pd  = 1.0 if max(PD)  > 0.15 else  0.5 if max(PD)  > 0.08 else 0.2

overall_score = 0.30 · score_cv + 0.30 · score_da + 0.20 · score_icm + 0.20 · score_pd
```

The equal weight on CV and DA reflects that both bid convergence and directional
alignment are necessary (but individually insufficient) conditions for herding.

---

## Running Analysis

```bash
# Run simulation
python examples/HerdEffect/run_herd.py -c configs/HerdEffect/simulation.yml
```

### Using Centralized Evaluation Module

All analysis functions are available in `masim.evaluation.finance`:

```python
from masim.evaluation.finance import (
    # Herding Metrics
    calculate_bid_convergence_cv,
    calculate_directional_agreement,
    calculate_cascade_measure,
    calculate_cross_sectional_std,
    
    # Core Metrics
    calculate_price_deviation,
    calculate_rolling_volatility,
    calculate_autocorrelation,
    calculate_returns,
    
    # Visualization
    plot_price_dynamics,
    plot_herding_metrics,
    plot_multi_panel_summary,
)

# Example: Analyze herding behavior
prices = {...}  # Load from simulation output
investor_bids = {...}

cv_series = calculate_bid_convergence_cv(investor_bids)
agreement = calculate_directional_agreement(investor_bids)

plot_herding_metrics(cv_series, agreement, output_path="herding.png")
plot_price_dynamics(prices, investor_bids=investor_bids, output_path="price.png")
```

## Output Files

| File                           | Description                         |
|--------------------------------|-------------------------------------|
| `00_summary_panel.png`         | 6-panel comprehensive summary       |
| `01_price_chart.png`           | Market price & investor bids        |
| `02_quantity_chart.png`        | Trading quantities                  |
| `03_price_deviation.png`       | Deviation from fundamental          |
| `04_bid_convergence.png`       | **KEY**: Bid CV (herding indicator) |
| `05_group_consensus.png`       | LSV-inspired bid dispersion         |
| `06_volatility.png`            | Rolling price volatility            |
| `07_contagion_heatmap.png`     | Investor deviation heatmap          |
| `08_directional_agreement.png` | **KEY**: Behavioral alignment       |
| `09_cascade_measure.png`       | **KEY**: Information cascade        |
| `10_bubble_magnitude.png`      | Cumulative bubble                   |
| `11_volume_analysis.png`       | Volume & feedback share             |
| `12_autocorrelation.png`       | Momentum persistence                |

---

## Success Criteria for Emergent Herding

The simulation successfully demonstrates emergent herding if:

| Criterion                 | Target                              | Evidence                                        |
|---------------------------|-------------------------------------|-------------------------------------------------|
| **Bid Convergence**       | CV < 0.10 for ≥3 consecutive rounds | Investors converging without explicit imitation |
| **Directional Agreement** | DA > 0.8 for ≥3 rounds              | All investors moving same direction             |
| **Information Cascade**   | ICM > 0.5                           | Investors ignoring fundamental signals          |
| **Price Deviation**       | PD peaks > 15%                      | Bubble forms from feedback                      |
| **Volatility Pattern**    | Rise → Peak → Spike                 | Classic bubble lifecycle                        |
| **Autocorrelation**       | AC > 0 during bubble                | Momentum persistence                            |

### Expected Bubble Lifecycle

```
Phase 1: TRIGGER (Round 1-5)
  - NoiseTrader random activity
  - CV: 0.15-0.20 (dispersed)
  - DA: 0.4-0.6 (random)
  - PD: ±5%

Phase 2: BUILD-UP (Round 6-20)
  - MomentumInvestor follows trend
  - CV: 0.10-0.15 (converging)
  - DA: 0.6-0.8 (aligning)
  - PD: 5-15%

Phase 3: CASCADE (Round 21-35)
  - AggressiveInvestor amplifies
  - CV: 0.05-0.10 (converged)
  - DA: 0.8-1.0 (strong herding)
  - ICM: 0.5-0.7 (cascade forming)
  - PD: 15-25%

Phase 4: PEAK (Round 36-45)
  - Maximum bubble
  - CV: < 0.05 (highly converged)
  - DA: > 0.9 (extreme alignment)
  - PD: peak value

Phase 5: CORRECTION (Round 46-50)
  - RiskAverseInvestor exits
  - CV: increases (diverging)
  - DA: decreases
  - Volatility: spike
  - PD: falling
```

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                                      | Rationale                    |
|----------------|--------------------------------------------------------|------------------------------|
| **50 rounds**  | One herding cycle; may see peak but limited correction | Standard observation window  |
| **100 rounds** | Full herding cycle with correction                     | Complete cascade + bust      |
| **200 rounds** | Multiple herding episodes possible                     | New cascade after correction |
| **500 rounds** | 3-5 herding cycles; statistical properties stabilize   | Long-term herding dynamics   |

### Observable Metrics by Round Count

```
Round 50:  CV drops to ~0.08; DA peaks at ~0.85; single cycle
Round 100: Full CV recovery; 2 DA peaks possible
Round 200: Clear multi-cycle pattern; herding strength varies
Round 500: Statistical distribution of herding episodes
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                                 | Economic Interpretation         |
|---------------------------|-------------------------------------------------|---------------------------------|
| **3-5 agents**            | Extreme herding; single agent can drive cascade | Individual behavior dominates   |
| **8-10 agents** (default) | Clear herding patterns                          | Sufficient for cascade dynamics |
| **20-30 agents**          | Stronger herding; more robust patterns          | More followers available        |
| **50+ agents**            | Very smooth herding; CV drops faster            | Law of large numbers effect     |

### Agent Type Effects

| More of This Agent       | Effect on Herding                           |
|--------------------------|---------------------------------------------|
| **Momentum Investors**   | Stronger herding; deeper cascades           |
| **Noise Traders**        | Delays herding formation; random disruption |
| **Fundamental Traders**  | Limits herding; earlier correction          |
| **Aggressive Investors** | Amplifies cascade; extreme CV drops         |

### Critical Ratios

```
Trend-following agents / Contrarian agents:

Ratio > 4:1 → Extreme herding; CV < 0.03
Ratio 2:1   → Pronounced herding (default)
Ratio 1:1   → Weak herding; CV stays > 0.15
Ratio < 1:2 → No herding; dispersed opinions
```

---

## References

1. Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades. *Journal of Political Economy*, 100(5), 992-1026.

2. Chang, E.C., Cheng, J.W., & Khorana, A. (2000). An examination of herd behavior in equity markets: An international perspective. *Journal of Banking & Finance*, 24(10), 1651-1679.

3. Christie, W.G., & Huang, R.D. (1995). Following the pied piper: Do individual returns herd around the market? *Financial Analysts Journal*, 51(4), 31-37.

4. De Bondt, W.F.M., & Thaler, R. (1985). Does the Stock Market Overreact? *Journal of Finance*, 40(3), 793-805.

5. De Long, J.B., Shleifer, A., Summers, L.H., & Waldmann, R.J. (1990). Noise Trader Risk in Financial Markets. *Journal of Political Economy*, 98(4), 703-738.

6. Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency. *Journal of Finance*, 48(1), 65-91.

7. Lakonishok, J., Shleifer, A., & Vishny, R.W. (1992). The impact of institutional trading on stock prices. *Journal of Financial Economics*, 32(1), 23-43.

8. Markowitz, H. (1952). Portfolio Selection. *Journal of Finance*, 7(1), 77-91.

9. Shiller, R.J. (1984). Stock Prices and Social Dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457-510.
