# ReversalEffect Analysis Methodology

## Overview

This document describes the evaluation metrics for detecting **long-term reversal** (mean reversion) in market simulations. Based on De Bondt & Thaler (1985) overreaction hypothesis.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                    | Rounds | Observable Phenomena                                       | Economic Interpretation                                   |
|--------------------------|--------|------------------------------------------------------------|-----------------------------------------------------------|
| **Initial Overreaction** | 1-30   | Strong price movement away from fundamental (up or down)   | Representativeness heuristic: extrapolating recent events |
| **Peak Deviation**       | 31-50  | Maximum distance from fundamental value; extreme sentiment | Overconfidence peaks; "new paradigm" thinking             |
| **Recognition Phase**    | 51-70  | Contrarians identify mispricing; reversal begins           | Smart money enters opposite positions                     |
| **Mean Reversion**       | 71-100 | Price returns toward fundamental; previous winners lag     | Correction of irrational pricing                          |

### Key Observable Curves

1. **Price**: Swing pattern - overshoot then return to fundamental
2. **Deviation from Fundamental**: Bell-shaped or inverted bell-shaped
3. **Long-lag Autocorrelation**: Negative at lags 15-30 (reversal signature)
4. **Winner-Loser Spread**: Losers outperform winners over holding period

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                         | Expected Pattern                 | What It Validates           |
|----------------------------------|----------------------------------|-----------------------------|
| **Negative ACF at lag 15-30**    | ACF < -0.1 for long lags         | Mean reversion present      |
| **Winner-Loser Spread > 0**      | Past losers beat past winners    | De Bondt-Thaler effect      |
| **Peak deviation 20-40%**        | Significant but not extreme      | Realistic overreaction      |
| **Reversion takes 30-50 rounds** | Gradual, not instant             | Slow correction (realistic) |
| **Contrarian profit > 0**        | Betting against trend profitable | Validates mispricing        |

### Unreasonable Results (Simulation Failure Indicators)

- Positive long-lag ACF → Momentum, not reversal
- Instant reversion (1-5 rounds) → Too efficient
- No reversion after 100 rounds → Permanent mispricing
- Winner-Loser Spread < 0 → Momentum dominates

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                                | Rationale                        |
|----------------|--------------------------------------------------|----------------------------------|
| **50 rounds**  | Overreaction visible, reversion may not complete | Insufficient time for full cycle |
| **100 rounds** | One complete overreaction-reversion cycle        | Standard reversal horizon        |
| **200 rounds** | Multiple cycles; statistically robust            | Can measure effect size          |
| **500 rounds** | 3-5 cycles; long-term equilibrium visible        | Stable reversal statistics       |

### Observable Metrics by Round Count

```
Round 50:  Peak deviation visible; ACF(30) not computable
Round 100: Full cycle; ACF(20) ~ -0.15
Round 200: Clear reversal pattern; Winner-Loser spread stable
Round 500: Multiple cycles; statistically significant reversal
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                        | Economic Interpretation           |
|---------------------------|----------------------------------------|-----------------------------------|
| **3-5 agents**            | Extreme swings; noisy reversal         | Individual overreaction dominates |
| **8-10 agents** (default) | Clear overreaction-reversion cycle     | Balanced dynamics                 |
| **20-30 agents**          | Smoother patterns; faster reversion    | More contrarians speed correction |
| **50+ agents**            | Minimal overreaction; efficient market | Diverse opinions prevent extremes |

### Agent Type Effects

| More of This Agent      | Effect on Reversal                    |
|-------------------------|---------------------------------------|
| **Momentum Traders**    | Larger overreaction; delayed reversal |
| **Contrarian Traders**  | Faster reversion; smaller overshoot   |
| **Fundamental Traders** | Earlier correction; anchors price     |
| **Noise Traders**       | Delays reversion; adds randomness     |

### Critical Ratios

```
Contrarian traders / Momentum traders:

Ratio > 2:1 → Quick reversion; small overshoots
Ratio 1:1   → Balanced dynamics (realistic reversal)
Ratio 1:2   → Large overreaction; slow reversion
Ratio < 1:3 → Momentum dominates; no reversal
```

---

## Key Metrics

| Metric                     | Formula                                   | Source                   | Purpose                             |
|----------------------------|-------------------------------------------|--------------------------|-------------------------------------|
| Past Return                | R_past = (P_t - P_t-L) / P_t-L            | Standard                 | Compute formation period return     |
| Future Return              | R_future = (P_t+H - P_t) / P_t            | Standard                 | Compute holding period return       |
| Winner-Loser Spread        | WL = R_future(Losers) - R_future(Winners) | De Bondt & Thaler (1985) | Reversal magnitude                  |
| Autocorrelation (long-lag) | AC_L = corr(r_t, r_t-L)                   | Standard                 | Detect mean reversion               |
| Overreaction Index         | OI = σ(P) / σ(F)                          | Shiller (1981)           | Excess volatility from overreaction |

---

## Reversal Mechanism

**Overreaction → Correction:**
1. Initial news causes overreaction (representativeness heuristic)
2. Price overshoots fundamental value
3. Contrarian investors buy undervalued losers
4. Price reverts to fundamental over time

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    # Core Metrics
    calculate_returns,
    calculate_autocorrelation,
    calculate_price_deviation,
    calculate_rolling_volatility,
    
    # Visualization
    plot_price_dynamics,
    plot_returns_analysis,
    plot_multi_panel_summary,
)

# Example: Analyze reversal
prices = {...}  # Load from simulation output

# Long-lag autocorrelation (reversal = negative)
returns = calculate_returns(prices)
ac_long = calculate_autocorrelation(returns, lag=20)

# Price deviation from fundamental
deviation = calculate_price_deviation(prices, fundamental=100.0)

plot_price_dynamics(prices, fundamental=100.0, output_path="price.png")
plot_returns_analysis(prices, output_path="returns.png")
```

---

## Success Criteria

| Criterion                   | Target                       | Evidence                            |
|-----------------------------|------------------------------|-------------------------------------|
| **Negative Long-lag AC**    | AC < 0 for lag > 15 rounds   | Mean reversion detected             |
| **Winner-Loser Spread**     | WL > 0                       | Losers outperform winners           |
| **Overreaction Correction** | Price returns to fundamental | Overreaction followed by correction |
| **Contrarian Profit**       | ContrarianInvestor PnL > 0   | Strategy validates reversal         |

---

## References

1. De Bondt, W.F.M., & Thaler, R. (1985). Does the Stock Market Overreact? *Journal of Finance*, 40(3), 793-805.
2. Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. *Cognitive Psychology*, 3(3), 430-454.
3. Shiller, R.J. (1981). Do Stock Prices Move Too Much to be Justified by Subsequent Changes in Dividends? *American Economic Review*, 71(3), 421-436.
