# EquityPremium Analysis Methodology

## Overview

This document describes the evaluation metrics for detecting **equity premium puzzle** dynamics in market simulations. Based on Benartzi & Thaler (1995) myopic loss aversion explanation.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                   | Rounds | Observable Phenomena                                         | Economic Interpretation              |
|-------------------------|--------|--------------------------------------------------------------|--------------------------------------|
| **Initial Allocation**  | 1-20   | Myopic agents hold less risky assets; long-horizon hold more | Loss aversion × evaluation frequency |
| **Loss Event**          | 21-40  | Stock declines; myopic agents reduce exposure                | Short horizon sees more losses       |
| **Diverging Behavior**  | 41-70  | Myopic sell stocks; long-horizon hold or buy                 | Different evaluation frames          |
| **Equilibrium Premium** | 71-100 | Stock return > bond return by 4-8%                           | Compensation for perceived risk      |

### Key Observable Curves

1. **Stock Allocation**: Myopic < Long-Horizon throughout simulation
2. **Realized Premium**: Stock outperforms bonds by ~6% (annualized equivalent)
3. **Sell Frequency**: Myopic traders sell more often after declines
4. **Loss Exposure**: Short horizon investors see more negative observations

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                               | Expected Pattern             | What It Validates       |
|----------------------------------------|------------------------------|-------------------------|
| **Equity Premium 4-8%**                | Matches historical 6% puzzle | Realistic calibration   |
| **α_myopic < α_long**                  | Allocation difference 20-40% | Horizon effect present  |
| **More myopic selling after losses**   | Asymmetric response          | Loss aversion mechanism |
| **Higher λ → lower allocation**        | Parametric sensitivity       | Correct mechanism       |
| **Longer horizon → higher allocation** | Monotonic relationship       | Myopia effect validated |

### Unreasonable Results (Simulation Failure Indicators)

- Equity premium 0 or negative → No puzzle replicated
- Myopic allocation = long-horizon → No horizon effect
- Premium > 15% → Over-calibrated loss aversion
- No response to losses → Loss aversion not working

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                       | Rationale                         |
|----------------|-----------------------------------------|-----------------------------------|
| **50 rounds**  | Premium visible but noisy               | Limited return observations       |
| **100 rounds** | Clear premium difference                | Standard measurement period       |
| **200 rounds** | Robust premium estimate                 | Multiple market cycles            |
| **500 rounds** | Statistical significance on all metrics | Sufficient for hypothesis testing |

### Observable Metrics by Round Count

```
Round 50:  Premium estimate noisy; allocation differences visible
Round 100: Premium ~5-7%; clear α_myopic < α_long
Round 200: Statistically significant differences
Round 500: Can test horizon length sensitivity
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                                    | Economic Interpretation             |
|---------------------------|----------------------------------------------------|-------------------------------------|
| **3-5 agents**            | High variance in premium; dominated by individual  | Hard to measure equilibrium         |
| **8-10 agents** (default) | Clear premium emergence                            | Market equilibrium forms            |
| **20-30 agents**          | Very stable premium; robust allocation differences | Statistical power                   |
| **50+ agents**            | Premium may decrease; market becomes efficient     | Many rational traders dampen effect |

### Agent Composition Effects

| More of This Agent        | Effect on Equity Premium          |
|---------------------------|-----------------------------------|
| **Myopic Loss-Averse**    | Higher equilibrium premium        |
| **Long-Horizon Rational** | Lower premium; more stock holding |
| **Risk-Neutral**          | Eliminates premium (arbitrage)    |
| **Mixed Horizons**        | Realistic premium levels          |

### Critical Ratios

```
Myopic agents / Long-horizon agents:

Ratio > 3:1 → Very high premium (>10%)
Ratio 2:1   → Historical premium (~6%)
Ratio 1:1   → Moderate premium (~3%)
Ratio < 1:2 → Low premium; efficient market
```

---

## Key Metrics

| Metric               | Formula                          | Source                 | Purpose                    |
|----------------------|----------------------------------|------------------------|----------------------------|
| Equity Premium       | EP = E[R_stock] − R_f            | Mehra-Prescott (1985)  | Risk premium magnitude     |
| Loss Frequency       | LF = P(R < 0) at horizon H       | Benartzi-Thaler (1995) | Probability of seeing loss |
| Certainty Equivalent | CE = U^{-1}(E[U(W)])             | Prospect theory        | Risk-adjusted value        |
| Evaluation Horizon   | H = frequency of portfolio check | Thaler (1985)          | Myopia measure             |
| Stock Allocation     | α = W_stock / W_total            | Standard               | Risk tolerance indicator   |

---

## Mathematical Detail of Each Metric

### 1. Equity Premium Calculation

```
Per-round excess return:
  ER(t) = r_stock(t) − r_bond   (both per round)

Sample mean equity premium:
  EP = (1/T) Σ_{t=1}^{T} ER(t)

Annualised EP:
  EP_annual = EP × 252    (if rounds are daily)
  EP_annual = EP × 52     (if rounds are weekly)
  EP_annual = EP × 12     (if rounds are monthly)

Target: EP_annual ≈ 5–7%  (historical US equity premium)

Associated Sharpe Ratio:
  SR = EP / σ_stock
  Historical US: SR ≈ 0.33 (0.05 / 0.15)
```

### 2. Loss Frequency at Each Horizon

```
For myopic investor checking every T_eval rounds:

  T_eval-period return:
    R_H(t) = [P(t) − P(t−T_eval)] / P(t−T_eval)

  Empirical loss frequency:
    LF = |{t : R_H(t) < 0}| / (T / T_eval)

  Theoretical (under GBM):
    LF = Φ(−μ⋅√T_eval / σ)

  T_eval = 1:   LF ≈ 45%    (monthly evaluation)
  T_eval = 12:  LF ≈ 34%    (annual evaluation)
  T_eval = 120: LF ≈ 9%     (10-year evaluation)

Loss frequency drives the demand for equity premium:
  Higher LF ⇒ more frequent pain from losses ⇒ higher premium demanded.
```

### 3. Prospect Theory Certainty Equivalent

```
For an investment with return distribution P_H(r):

  Expected prospect value:
    E[V_H] = Σ_r V(r) · P_H(r)

  Where V(r) = r^0.88        if r ≥ 0
               −2.25|r|^0.88  if r < 0

Certainty equivalent return (CE):
  Solve: V(CE) = E[V_H]

For CE > 0: investor willing to hold stocks without extra premium
For CE < 0: investor demands premium (positive EP) to hold stocks

Benartzi & Thaler calibration:
  CE = 0 when H = 1 year  AND  EP = 6%
  ⇒ Annual evaluation + 6% premium = indifference between stocks and bonds.
```

### 4. Stock Allocation Gap (Δα)

```
Myopic allocation:
  α_myopic = W_stock_myopic / W_total_myopic

Long-horizon allocation:
  α_long = W_stock_long / W_total_long

Allocation gap:
  Δα = α_long − α_myopic

Expected from Benartzi & Thaler (1995):
  α_myopic ≈ 0.20 (20% equities)
  α_long   ≈ 0.70 (70% equities)
  Δα ≈ 0.50 (50 percentage points)

A well-functioning simulation should show Δα ≥ 0.30.
```

### 5. Validation Score

```
Fit score components:
  s1 = min(EP_annual / 0.06, 1.0)       → rewards EP near 6%
  s2 = 1.0 if Δα > 0.30 else Δα / 0.30  → rewards allocation divergence
  s3 = min(LF_ratio / 2.0, 1.0)         → LF_myopic / LF_long ≥ 2
  s4 = 1.0 if premium_positive else 0.0 → stocks must outperform bonds

  overall_score = 0.40×s1 + 0.30×s2 + 0.20×s3 + 0.10×s4

Target: overall_score ≥ 0.60.
```

---

## Equity Premium Mechanism

**Loss Aversion × Myopia = High Premium:**
1. Loss aversion: losses hurt 2.25× more than gains
2. Myopic evaluation: frequent portfolio checking
3. Short horizon → see more negative returns
4. Loss-averse investor demands compensation
5. Result: 6% equity premium (vs 1-2% from standard theory)

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    # Core Metrics
    calculate_returns,
    calculate_rolling_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    
    # Volume Analysis
    calculate_strategy_contribution,
    
    # Visualization
    plot_price_dynamics,
    plot_returns_analysis,
    plot_multi_panel_summary,
)

# Example: Analyze equity premium
stock_prices = {...}
bond_prices = {...}

# Compute equity premium
stock_returns = calculate_returns(stock_prices)
bond_returns = calculate_returns(bond_prices)
equity_premium = sum(stock_returns) / len(stock_returns) - sum(bond_returns) / len(bond_returns)

# Compare Sharpe ratios
sharpe_stock = calculate_sharpe_ratio(stock_returns, risk_free=0.02)
sharpe_bond = calculate_sharpe_ratio(bond_returns, risk_free=0.02)

plot_returns_analysis(stock_prices, output_path="stock_returns.png")
```

---

## Success Criteria

| Criterion                   | Target                            | Evidence             |
|-----------------------------|-----------------------------------|----------------------|
| **Equity Premium**          | EP ≈ 5-7% annualized              | Puzzle replicated    |
| **Myopic Allocation**       | MyopicInvestor holds less stock   | Myopia effect        |
| **Long-Horizon Allocation** | LongTermInvestor holds more stock | Horizon effect       |
| **Loss Aversion Impact**    | LossAverse demands higher premium | Behavioral mechanism |
| **Allocation Difference**   | α_long > α_myopic significantly   | Horizon matters      |

---

## References

1. Mehra, R., & Prescott, E.C. (1985). The equity premium: A puzzle. *Journal of Monetary Economics*, 15(2), 145-161.
2. Benartzi, S., & Thaler, R.H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92.
3. Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263-291.
4. Thaler, R.H. (1985). Mental accounting and consumer choice. *Marketing Science*, 4(3), 199-214.
