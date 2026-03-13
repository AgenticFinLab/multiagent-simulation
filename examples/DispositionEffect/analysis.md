# DispositionEffect Analysis — Discussion and Summary

## Overview

This document discusses the evaluation methodology, the 7 output figures, expected
patterns, interpretation criteria, and known limitations for the DispositionEffect
simulation (Prospect Theory, Shefrin & Statman 1985).

All figures are saved to `EXPERIMENT/DispositionEffect/analysis/`.

---

## Output Figures

| Figure    | File                           | What It Shows                                                           |
|-----------|--------------------------------|-------------------------------------------------------------------------|
| **Fig 1** | `fig1_price_dynamics.png`      | Price path, fundamental baseline, per-round returns, rolling volatility |
| **Fig 2** | `fig2_pgr_plr_comparison.png`  | PGR vs PLR grouped bars + Disposition Coefficient per strategy          |
| **Fig 3** | `fig3_trading_activity.png`    | Buy/sell event counts + total traded volume per strategy                |
| **Fig 4** | `fig4_return_distribution.png` | Return histogram with normal overlay + summary statistics panel         |
| **Fig 5** | `fig5_disposition_ratio.png`   | PGR/PLR ratio bars + stacked gain/loss pool breakdown                   |
| **Fig 6** | `fig6_portfolio_evolution.png` | Position size + equity value trajectories per investor type             |
| **Fig 7** | `fig7_sell_gain_loss.png`      | Scatter of gain/loss % at each sell event + violin distribution         |

---

## Fig 1 — Price Dynamics

**Three panels:**
- **A. Price path vs fundamental (100)**: Green shading above = above fundamental (bullish phase),
  red shading below = undervalued phase. The price oscillates around 100 due to mean-reversion
  (`gamma = 0.015`), punctuated by news shocks (`prob = 0.15`, range ±5).
- **B. Per-round returns**: Color-coded bar chart (green = positive, red = negative). With
  `noise_std = 0.4` and news shocks of ±5 on a base of 100, returns range roughly ±5% with
  fat tails on shock days.
- **C. Rolling 20-round volatility**: Reveals heteroscedasticity — volatility clusters around
  news events, consistent with stylized fact of financial markets.

**What to look for**: Sufficient price movement to trigger `gain_threshold = 5%` repeatedly.
If the price rarely exceeds 105 or falls below 97.5 (from any cost basis), sell events are sparse
and PGR/PLR will have low statistical power.

---

## Fig 2 — PGR vs PLR Comparison (Core Metric)

**Panel A — Grouped PGR/PLR bars:**
PGR and PLR computed by Odean (1998) methodology:

```
PGR = realized_gains  / (realized_gains  + paper_gains)    [SELL & HOLD rounds only]
PLR = realized_losses / (realized_losses + paper_losses)   [SELL & HOLD rounds only]
```

Expected pattern:
- **DispositionInvestor**: PGR >> PLR (high gain realization, low loss realization)
- **RationalInvestor**: PGR ≈ PLR (no reference-point anchoring)
- **TaxAwareInvestor**: PGR < PLR (inverted — sells losers, holds winners)
- **IndexHolder**: both near zero (no trading)
- **InstitutionalInvestor**: PGR > PLR but gap smaller than Disposition

**Panel B — Disposition Coefficient (DC = PGR - PLR):**

| DC Range  | Interpretation             |
|-----------|----------------------------|
| DC > 0.15 | Strong disposition effect  |
| 0.10–0.15 | Moderate effect            |
| 0.05–0.10 | Weak but detectable        |
| DC ≤ 0    | No effect / reverse effect |

Validation threshold: `overall_score > 0.5` requires DC > ~0.08 with PGR > PLR.

---

## Fig 3 — Trading Activity

**Panel A — Buy vs Sell events:**
Key diagnostic for simulation health:
- If DispositionInvestor has **many sells, few buys** → position depleting (bad: kills future signal)
- If DispositionInvestor has **balanced buys and sells** → position cycling correctly
- `max_position = 30`, `buy_fraction = 0.2` means replenishment is conservative;
  expected 1–2 buys per sell cycle

**Panel B — Total volume:**
DispositionInvestor should generate more total volume than IndexHolder.
Higher volume indicates active reference-point-triggered trading.

---

## Fig 4 — Return Distribution

**Panel A — Histogram + normal overlay:**
- Returns from mean-reverting price process with noise. Distribution should be approximately
  normal with slight positive skew (due to news shock upside being symmetric but investors
  selling winners early, reducing upward momentum).
- Fat tails expected due to `news_impact_range = 5.0` on base price ~100 → up to ±5% shock.

**Panel B — Statistics:**
- **Skewness**: Ideally near 0 for pure Gaussian; negative skew possible if news shocks
  cluster on the downside.
- **Excess kurtosis > 0**: Leptokurtic (fat tails) expected given news shocks — stylized fact
  of real financial return distributions.
- **Volatility**: Expected ~1.2% per round (noise_std=0.4 on price≈100 ≈ 0.4% base noise
  + occasional 5% shock → overall std ~1-2%).

---

## Fig 5 — Disposition Ratio & Gain/Loss Pool Breakdown

**Panel A — PGR/PLR ratio (capped at 8x):**
- Red bars (>1): investor sells gains faster than losses → disposition effect present
- Blue bars (<1): inverse (e.g., TaxAwareInvestor)
- Disposition ratio = 3-5x is realistic for strong behavioral bias

**Panel B — Gain/Loss pool stacked bars:**
This is the denominator structure. A common failure mode is an empty pool (PGR = PLR = 0)
because either no trades occurred (position depleted) or all trades were HOLDs.
Expected healthy state:
- Large paper_gains pool for HOLD rounds in gain domain (agent keeps sitting on winners briefly)
- Realized gains > paper gains for DispositionInvestor (earns through realized quickly)
- Realized losses << paper losses for DispositionInvestor (almost never realizes losses)

---

## Fig 6 — Portfolio Evolution

**Panel A — Position size:**
- DispositionInvestor: Should cycle between ~18–30 shares (sell 40% on trigger → 18 shares,
  then gradually buy back to 30 via near-reference-point buys)
- IndexHolder: Flat at 50 (no trading)
- TaxAwareInvestor: Steps down on loss events, rebuilds

**Panel B — Equity value:**
- Equity = position × current_price. With mean-reverting price ≈ 100 and cycling position,
  DispositionInvestor equity should be slightly lower than IndexHolder over time
  (selling winners early → misses upside momentum from news shocks).
- This under-performance vs IndexHolder is a real-world stylized fact: Odean (1998) found
  disposition investors earn 3.4% lower annual returns than non-disposition investors.

---

## Fig 7 — Sell Events: Gain/Loss % at Realization

**Panel A — Scatter (round vs. gain/loss %):**
The most direct visual test of the disposition effect:
- **DispositionInvestor sells should cluster above +5%** (gain territory, near gain_threshold)
- **DispositionInvestor should have almost no sells below 0%** (only at extreme -30%)
- **TaxAwareInvestor sells should cluster below -5%** (loss territory for tax harvesting)
- **RationalInvestor sells should be spread above and below 0** (no reference-point anchoring)

Dotted reference lines at +5% (gain threshold) and -30% (loss threshold) make the
threshold-triggered behavior immediately visible.

**Panel B — Violin distribution:**
Distribution of gain/loss % at each sell event. For DispositionInvestor:
- Median should be positive (sells happen in gain domain)
- Distribution should be right-skewed with long left tail (rare loss sells at -30%)
- In contrast, RationalInvestor violin should be centered near 0

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase                   | Rounds  | Observable Phenomena                              | Economic Interpretation                                       |
|-------------------------|---------|---------------------------------------------------|---------------------------------------------------------------|
| **Position Building**   | 1-10    | Investors hold initial 30 shares; no sells        | No gain/loss formed yet relative to purchase_price = 100      |
| **First Gain Events**   | ~10-30  | Price spikes above 105; DispositionInvestor sells | Gain threshold (5%) hit; concave value function triggers sell |
| **Replenishment Cycle** | after   | Price reverts toward 100; investor buys back      | Near-reference-point comfort; position rebuilds to 30         |
| **Loss Holding**        | ongoing | Price below 97.5; DispositionInvestor HOLDs       | Convex value function: risk-seeking in loss domain            |
| **PGR/PLR Asymmetry**   | 50-200  | PGR stabilizes >> PLR for Disposition             | Cumulative evidence of systematic sell/hold asymmetry         |

### Key Observable Curves

1. **Fig 7A Scatter**: Sells clustered at small gains (+5% to +10%), almost none at small losses
2. **Fig 6A Position**: DispositionInvestor cycles 18-30 shares; IndexHolder flat at 50
3. **Fig 2 DC**: DC = 0.10–0.20 for DispositionInvestor; near 0 for Rational; negative for TaxAware
4. **Fig 5B Pool**: Realized gains >> paper gains (PGR > 0.5); realized losses << paper losses (PLR < 0.2)

---

## Validation Criteria

### Success (Simulation Valid)

| Criterion            | Target                     | Evidence Figure |
|----------------------|----------------------------|-----------------|
| **PGR > PLR**        | Required                   | Fig 2A          |
| **DC = PGR - PLR**   | > 0.10                     | Fig 2B          |
| **Sell cluster >0%** | Median sell in gain domain | Fig 7           |
| **Position cycling** | Not depleted to 0          | Fig 6A          |
| **Loss holds**       | <5% of trades at -5%       | Fig 7A          |
| **Overall score**    | > 0.50                     | summary.json    |

### Failure Indicators

| Observation               | Likely Cause                                     | Fix                                     |
|---------------------------|--------------------------------------------------|-----------------------------------------|
| PGR = PLR = 0             | Trade loader broken; no trades loaded            | Check `load_simulation_data()`          |
| Position → 0 in 10 rounds | `sell_fraction_gain` too high                    | Reduce to 0.3-0.4                       |
| DC < 0                    | TaxAwareInvestor counted as DispositionInvestor  | Check `generate_summary()` strategy ID  |
| All sells at losses       | `gain_threshold` too high vs. price range        | Reduce gain_threshold or increase noise |
| PGR ≈ PLR both high       | Both thresholds too tight; trades on every round | Increase gain_threshold or add cooldown |

---

## PGR/PLR Methodology Note (Odean 1998)

The PGR/PLR computation follows Odean (1998) exactly:

```
For each trade record of a given investor, per round:

  SELL round (qty < 0):
    realized_qty = min(|qty|, position)
    remaining    = position - realized_qty

    if price > purchase_price:   realized_gains  += realized_qty × unit_gain
                                 paper_gains     += remaining    × unit_gain
    else:                        realized_losses += realized_qty × |unit_gain|
                                 paper_losses    += remaining    × |unit_gain|

  HOLD round (qty = 0):
    if price > purchase_price:   paper_gains  += position × unit_gain
    else:                        paper_losses += position × |unit_gain|

  BUY round (qty > 0):
    → Update average cost basis only.
    → NOT a sell-opportunity observation → DO NOT count paper gains.
      (Counting paper gains on buy rounds inflates denominators → biases
       PGR and PLR toward zero → destroys the signal.)
```

This distinction is critical. A buy is not a decision between realizing and holding.
Including paper gain on buy rounds was a prior bug; the current implementation correctly
excludes them.

---

## Round Scaling Effects

| Total Rounds | Expected DC  | Sell Events | Notes                            |
|--------------|--------------|-------------|----------------------------------|
| 30           | Noisy; ~0.05 | ~5-10       | Insufficient for stable estimate |
| 100          | ~0.12-0.15   | ~20-30      | Clear pattern                    |
| 200          | ~0.15-0.20   | ~40-60      | Robust; recommended minimum      |
| 500          | ~0.18-0.22   | ~80-120     | Statistically very robust        |

---

## Parameter Sensitivity

| Parameter Change              | Effect                                            |
|-------------------------------|---------------------------------------------------|
| `gain_threshold` ↑ (e.g. 10%) | Fewer sell events → lower PGR → weaker DC         |
| `gain_threshold` ↓ (e.g. 2%)  | Very frequent sells → position depletes faster    |
| `sell_fraction_gain` ↑ (0.6)  | Position depletes in 4-5 sells → signal dies      |
| `sell_fraction_gain` ↓ (0.2)  | Very weak cycling; position always near max       |
| `loss_threshold` ↑ (-0.10)    | More frequent loss sells → PLR rises → DC shrinks |
| `loss_threshold` ↓ (-0.50)    | Never sells at loss → PLR → 0 → DC very high      |
| `noise_std` ↑ (1.0)           | More price crossings of gain_threshold per round  |
| `noise_std` ↓ (0.1)           | Price moves rarely cross threshold → few trades   |
| `buy_fraction` ↑ (0.5)        | Fast replenishment → position always near max     |
| `buy_fraction` ↓ (0.05)       | Slow recovery → extended depletion phases         |

---

## Prospect Theory Foundation

```
V(x) = {  x^α            if x >= 0  (gains: concave, risk-averse)
        { -λ × (-x)^β    if x <  0  (losses: convex, risk-seeking)

Where:
  α, β ≈ 0.88  (diminishing sensitivity — same curvature both sides)
  λ ≈ 2.25     (loss aversion — losses hurt 2.25x more than equivalent gains)

Simulation mapping:
  gain_threshold   = gain domain trigger (sell when V'(x) sufficiently diminished)
  loss_threshold   = loss domain escape (only sell when V_loss enormous, -30%)
  loss_aversion    = λ stored but directional asymmetry captured via threshold gap
```

---

## References

1. Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263–291.
2. Shefrin, H., & Statman, M. (1985). The Disposition to Sell Winners Too Early and Ride Losers Too Long. *Journal of Finance*, 40(3), 777–790.
3. Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775–1798.
4. Thaler, R. (1980). Toward a Positive Theory of Consumer Choice. *Journal of Economic Behavior & Organization*, 1(1), 39–60.
