# ShortSqueeze Analysis Methodology

## Overview

This document describes the evaluation metrics for detecting **short squeeze** dynamics in market simulations. Based on supply-demand imbalance mechanics and margin constraint theory.

---

## Observable Phenomena

### Expected Simulation Outcomes

| Phase               | Rounds | Observable Phenomena                                          | Economic Interpretation                       |
|---------------------|--------|---------------------------------------------------------------|-----------------------------------------------|
| **Short Build-up**  | 1-15   | Short interest accumulates; price stable or declining         | Shorts betting on overvaluation               |
| **Catalyst Event**  | 16-25  | Positive news/buyer emerges; price rises 10-20%               | Triggers margin pressure on shorts            |
| **Forced Covering** | 26-45  | Short sellers buy to cover; price accelerates 50-100%+        | Margin calls force buying regardless of price |
| **Peak Squeeze**    | 46-60  | Maximum price spike; shorts exhausted; extreme volatility     | Supply overwhelmed by forced demand           |
| **Normalization**   | 61-100 | Price declines toward (but above) pre-squeeze; shorts reduced | New equilibrium; some shorts still trapped    |

### Key Observable Curves

1. **Price**: Exponential spike followed by partial reversion
2. **Short Interest**: Step-function decline during covering
3. **Volume**: Massive spike during squeeze (10-20x normal)
4. **Short P&L**: Increasingly negative during squeeze

---

## Validation Evidence

### How Results Demonstrate Reasonable Simulation

| Evidence                   | Expected Pattern                      | What It Validates                       |
|----------------------------|---------------------------------------|-----------------------------------------|
| **Price spike 50-200%**    | Matches real squeezes (GME: 1700%)    | Realistic squeeze magnitude             |
| **Short covering visible** | Short positions decrease rapidly      | Forced buying mechanism                 |
| **Volume spike**           | 10x+ normal during squeeze            | Panic covering                          |
| **Feedback loop**          | Covering → price rise → more covering | Self-reinforcing dynamics               |
| **Partial reversion**      | Price settles above but below peak    | Not pure bubble; some fundamental shift |

### Unreasonable Results (Simulation Failure Indicators)

- Price spike < 20% → Not enough short pressure
- No short covering → Margin mechanism not working
- Instant spike (1-2 rounds) → Missing gradual cascade
- No reversion → Pure bubble, not squeeze mechanics

---

## Round Scaling Effects

### What Happens as Total Rounds Increase

| Total Rounds   | Expected Behavior                         | Rationale                        |
|----------------|-------------------------------------------|----------------------------------|
| **50 rounds**  | Squeeze starts but may not complete       | Insufficient time for full cycle |
| **100 rounds** | Full squeeze cycle with normalization     | Standard squeeze duration        |
| **200 rounds** | Possible second squeeze or re-shorting    | New shorts may enter             |
| **500 rounds** | Multiple squeeze cycles if shorts rebuild | Long-term dynamics               |

### Observable Metrics by Round Count

```
Round 50:  Squeeze in progress; peak may not be reached
Round 100: Peak around round 50-60; normalization by 90
Round 200: Complete cycle; possible second squeeze attempt
Round 500: Multiple cycles; short interest rebuilds
```

---

## Agent Scaling Effects

### What Happens as Number of Agents Increases

| Agent Count               | Market Behavior                           | Economic Interpretation     |
|---------------------------|-------------------------------------------|-----------------------------|
| **3-5 agents**            | Extreme squeeze; single buyer can trigger | Very thin market            |
| **8-10 agents** (default) | Clear squeeze dynamics                    | Sufficient for cascade      |
| **20-30 agents**          | More gradual squeeze; longer duration     | Distributed short positions |
| **50+ agents**            | Squeeze may be dampened; diverse opinions | Natural buffers             |

### Agent Type Effects

| More of This Agent     | Effect on Squeeze                   |
|------------------------|-------------------------------------|
| **Short Sellers**      | Higher squeeze potential; more fuel |
| **Momentum Buyers**    | Amplifies squeeze; joins covering   |
| **Contrarian Sellers** | Dampens squeeze; provides supply    |
| **Market Makers**      | Moderates extremes; adds liquidity  |

### Critical Ratios

```
Short Interest / Float (simulated):

SI > 100% → Extreme squeeze potential (GME-like)
SI 50-100% → High squeeze risk
SI 20-50%  → Moderate squeeze potential
SI < 20%   → Low squeeze risk
```

---

## Mathematical Detail of Each Metric

### 1. Short Interest Ratio — Squeeze Vulnerability Index

```
Short Interest Ratio (SI):
  SI(t) = short_position(t) / float_shares
        = Σ_i max(0, −Q_i_cumulative(t)) / total_float

Days-to-Cover (DTC) — Asquith-Pathak-Ritter (2005):
  DTC(t) = short_position(t) / avg_daily_volume
         = SI(t) · float / avg_daily_volume

Squeezeability zones:
  DTC < 2:   Low squeeze risk
  DTC 2–5:   Moderate risk
  DTC 5–10:  High risk
  DTC > 10:  Extreme vulnerability (GME-like conditions)
```

**Short P&L mechanics** (squeeze loss accumulation):
```
Short P&L per unit at time t:
  PnL_short(t) = (P_entry − P(t)) / P_entry   [% return]

Short seller's total loss:
  L(t) = |short_qty| · max(0, P(t) − P_entry)

Margin call condition:
  L(t) > margin_buffer → forced covering
  ⇔ P(t) > P_entry · (1 + margin_buffer / |short_qty|)

Forced cover quantity:
  Q_cover(t) = min(|short_position(t)|, forced_cover_fraction · |short_qty|)
```

---

### 2. Price Spike Magnitude — Squeeze Intensity

```
Price Spike:
  PS = (P_peak − P_0) / P_0
  where P_0 = pre-squeeze price, P_peak = maximum price

Benchmark real squeezes:
  GameStop (GME, Jan 2021):  PS ≈ 1,700%
  Volkswagen (2008):         PS ≈ 450%
  Typical simulated squeeze: PS ≈ 50–200%

Rate of price increase during forced covering:
  dP/dt|_{squeeze} = λ · [Q_forced_cover + Q_momentum]
                   = λ · [k · |ShortPos| + β · r · W_m/P]
```

**Self-reinforcing feedback loop equation:**
```
dP(t+1) / dP(t) = 1 + λ · k · |ShortPos(t)| / P(t)

This ratio > 1 while shorts remain ⇒ squeeze is self-sustaining

Squeezeamplification factor (SAF):
  SAF = Σ_t [dP(t+1)/dP(t) − 1]   (cumulative over squeeze rounds)
  SAF > 5: strong self-reinforcing dynamics
```

---

### 3. Short Covering Ratio — Covering Intensity

```
Short Covering Volume at round t:
  SCV(t) = Σ_i max(0, Q_i(t) · ᵢ(was_short))  [forced buying by short sellers]

Short Covering Ratio:
  SCR(t) = SCV(t) / total_volume(t)

Interpretation:
  SCR < 0.1:  Normal; shorts not covering
  SCR 0.1–0.3: Moderate covering pressure
  SCR > 0.5:  Panic covering; squeeze in progress
  SCR > 0.8:  Extreme; near-complete short exhaustion
```

**Volume spike during squeeze:**
```
Volume(t)_squeeze / Volume(t)_normal ≈ 10–20×

This spike is the empirical signature of a squeeze:
  VSI = max(Volume) / median(Volume_{pre-squeeze})
  Expected: VSI > 5 (5× volume spike)
```

---

### 4. Margin Pressure Index — Forced Covering Trigger

```
Margin Pressure Index (MPI) for short seller i:
  MPI_i(t) = L_i(t) / (initial_margin_i + mark-to-market_buffer_i)
           = |short_qty_i| · (P(t) − P_entry_i) / margin_buffer_i

Forced covering triggers when MPI_i(t) > 1:
  Q_cover_i = short_position_i · cover_fraction

Aggregate margin pressure:
  AMP(t) = (# shorts with MPI > 1) / total_shorts
  AMP > 0.5: majority of shorts facing margin calls = major squeeze underway
```

**Squeeze exhaustion condition:**
```
Squeeze ends when:
  short_position(t) ≈ 0   (all shorts covered)
  OR  P(t) < P_entry_i for new entrant shorts (price too high to maintain)

Post-squeeze equilibrium:
  P_final = P_0 + PS · α_persist   where 0 < α_persist < 1
  (some premium persists due to reduced float and changed market structure)
```

---

### 5. MomentumBuyer Amplification Factor

```
MomentumBuyer order during squeeze:
  Q_m(t) = β · r(t−1) · cash / P(t)

Contribution to squeeze:
  Amplification = D_momentum(t) / D_forced(t)
               = (β · r · W_m/P) / (k · |ShortPos|)

Amplification > 1: momentum traders dominate price action
Amplification 0.3–1.0: shorts and momentum jointly drive price
Amplification < 0.3: mainly short-covering driven (purer squeeze)
```

---

### 6. Validation Score Formula

```
score_spike = 1.0 if PS > 0.50  else 0.5 if PS > 0.20  else 0.0
score_cover = 1.0 if max(SCR) > 0.5 else 0.5 if max(SCR) > 0.3 else 0.0
score_vol   = 1.0 if VSI > 5.0  else 0.5 if VSI > 2.0  else 0.0
score_feed  = 1.0 if SAF > 5.0  else 0.5 if SAF > 2.0  else 0.0
score_rev   = 0.5 if P_final < P_peak else 0.0  (partial reversion bonus)

overall_score = 0.35·score_spike + 0.25·score_cover + 0.20·score_vol
              + 0.15·score_feed  + 0.05·score_rev
```

Target: `overall_score > 0.6` (significant price spike with short covering cascade).

---

## Key Metrics

| Metric               | Formula                              | Source       | Purpose                 |
|----------------------|--------------------------------------|--------------|-------------------------|
| Short Interest       | SI = shares_short / float            | Standard     | Squeeze vulnerability   |
| Short Covering Ratio | SCR = covering_volume / daily_volume | Standard     | Covering pressure       |
| Price Spike          | ΔP_max = max(P) - P_0                | Standard     | Squeeze magnitude       |
| Margin Pressure      | MP = loss / margin                   | Broker rules | Forced covering trigger |
| Days to Cover        | DTC = SI / avg_daily_volume          | Standard     | Time to exit shorts     |

---

## Short Squeeze Mechanism

**Forced Covering Feedback Loop:**
1. High short interest creates vulnerability
2. Positive catalyst triggers price rise
3. Short sellers face margin pressure
4. Forced covering → more buying → higher price
5. Feedback loop until shorts exhausted

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    # Core Metrics
    calculate_returns,
    calculate_rolling_volatility,
    calculate_max_drawdown,  # Inverted for squeeze
    
    # Volume Analysis
    calculate_volume_metrics,
    calculate_net_demand,
    calculate_strategy_contribution,
    
    # Visualization
    plot_price_dynamics,
    plot_agent_activity,
    plot_strategy_contribution,
    plot_multi_panel_summary,
)

# Example: Analyze short squeeze
prices = {...}  # Load from simulation output
investor_quantities = {...}

# Measure squeeze intensity
returns = calculate_returns(prices)
max_return = max(returns)

# Track short covering vs momentum buying
contribution = calculate_strategy_contribution(investor_quantities)

plot_price_dynamics(prices, output_path="price.png")
plot_strategy_contribution(contribution, output_path="contribution.png")
```

---

## Success Criteria

| Criterion                       | Target                                | Evidence                |
|---------------------------------|---------------------------------------|-------------------------|
| **Price Spike**                 | ΔP > 50% at peak                      | Squeeze magnitude       |
| **Forced Covering**             | ShortSeller switches to buying        | Covering detected       |
| **Feedback Loop**               | Covering → price rise → more covering | Positive feedback       |
| **Exhaustion**                  | Price stabilizes after shorts covered | Natural end of squeeze  |
| **MomentumBuyer Amplification** | Momentum traders add to buying        | Amplification mechanism |

---

## References

1. Lamont, O.A., & Thaler, R.H. (2003). Can the Market Add and Subtract? Mispricing in Tech Stock Carve-Outs. *Journal of Political Economy*, 111(2), 227-268.
2. Dechow, P.M., Hutton, A.P., Meulbroek, L., & Sloan, R.G. (2001). Short-sellers, fundamental analysis, and stock returns. *Journal of Financial Economics*, 61(1), 77-106.
3. GameStop case studies (2021). Market mechanics of short squeeze.
