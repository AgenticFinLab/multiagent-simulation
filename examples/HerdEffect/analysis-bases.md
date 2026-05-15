# HerdEffect — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question                                                                                            | Primary Metric(s)     | Expected Finding                                                                   | Failure Indicator                                 |
|-----------|--------------------------------------------------------------------------------------------------------------|-----------------------|------------------------------------------------------------------------------------|---------------------------------------------------|
| O1        | Does the emergent herding mechanism produce momentum episodes that clearly exceed noise-driven fluctuations? | EMI, MDD              | Price shows sustained momentum runs (EMI high) without any explicit imitator       | Price is indistinguishable from random walk       |
| O2        | Do MomentumInvestor and AggressiveInvestor activate together to create herding, or is one agent sufficient?  | ACC (§4.1, §4.5), EMI | Both momentum agents activate simultaneously during peak episodes (ACC each > 20%) | One agent accounts for > 90% of momentum volume   |
| O3        | Does RiskAverseInvestor exit early, before the momentum peak, validating the mean-variance mechanism?        | RVI                   | §4.3 position reduces before price peaks in ≥50% of episodes                       | §4.3 never changes position throughout simulation |
| O4        | How does LLM/RAG variant reduce emergent herding intensity vs. rule baseline?                                | EMI, MDD              | LLM/RAG produces lower EMI and smaller drawdown                                    | Identical dynamics across variants                |

---

## §2 Core Metrics Catalogue

### Metric: Emergent Momentum Index (EMI)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
The maximum sustained positive return run (longest consecutive-positive-return episode weighted by magnitude) observed during the simulation, measuring the intensity of momentum episodes that emerge from agent interactions. A high EMI indicates that the positive feedback loop successfully generates a sustained momentum episode beyond random noise.

#### Formula
```
EMI = max over all consecutive-positive-return episodes e of:
  Σ_{t ∈ e} r(t)

where r(t) = (P(t) − P(t−1)) / P(t−1) = return at round t
episode e = maximal contiguous run of t where r(t) > 0
```

**Computation notes**: Compute all maximal runs of consecutive positive returns; for each run, sum the returns. EMI = maximum sum across all runs.

**Python function**:
```python
def emergent_momentum_index(price_history: list) -> float:
    """Maximum cumulative return of any consecutive-positive-return episode.

    Args:
        price_history: List of prices P(t) for t=1..T
    Returns:
        EMI ≥ 0; in fractional units (0.10 = 10% cumulative run)
    """
```

#### Interpretation

| Range        | Economic Meaning            | Simulation Interpretation                                                    |
|--------------|-----------------------------|------------------------------------------------------------------------------|
| < 0.03       | No distinguishable momentum | MomentumInvestor and AggressiveInvestor not generating feedback              |
| [0.03, 0.10) | Mild momentum               | Short positive feedback runs; quickly damped by ContrarianInvestor           |
| [0.10, 0.25] | Moderate momentum episode   | Emergent herding consistent with Jegadeesh-Titman 1.01%/month for ~10 rounds |
| > 0.25       | Strong herding episode      | AggressiveInvestor acceleration dominates; extreme positive feedback         |

#### Academic Basis

**Primary source**: Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners and Selling Losers." *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x

Monthly momentum premium of 1.01% (12-month formation) maps to approximately 10–12% over a 10-round simulation — EMI ≈ 0.10–0.12 for calibrated simulation.

**Supporting studies**:

| Study                                   | Context             | Finding                                                                          | Relevance                                 |
|-----------------------------------------|---------------------|----------------------------------------------------------------------------------|-------------------------------------------|
| Grinblatt et al. (1995). *AER* 85(5)    | Mutual fund trading | 77% of funds are momentum traders; 14.4% abnormal annual return in herded stocks | Sets EMI normal range                     |
| Brunnermeier & Nagel (2004). *JF* 59(5) | Dot-com hedge funds | Momentum funds rode 271% NASDAQ rally; EMI analogs ≈ 30–50% cumulative           | Sets EMI upper bound for extreme episodes |

#### Normal Range (from literature)
EMI of 0.08–0.20 in calibrated simulations; Jegadeesh-Titman analog → EMI ≈ 0.10–0.12.

#### Red Flag Threshold
- **Too high** (> 0.40): AggressiveInvestor acceleration dominates; kappa too high; reduce kappa
- **Too low** (< 0.02): Positive feedback loop not activating; increase lambda_price or kappa

#### Relationship to Other Metrics
EMI measures the height of the best momentum episode; MDD (Maximum Drawdown) measures the subsequent reversal. High EMI combined with high MDD indicates a full bubble-and-crash cycle. EMI should be positively correlated with ACC_§4.5 — the more AggressiveInvestor dominates buying volume, the larger the EMI.

---

### Metric: Maximum Drawdown (MDD)

#### Category
Price Dynamics / Reversal

#### Definition
The maximum peak-to-trough decline in price during the simulation, measuring the eventual correction magnitude after a momentum episode. In the context of emergent herding, MDD captures the "crash" phase when ContrarianInvestor and RiskAverseInvestor reassert fundamental value.

#### Formula
```
MDD = max over all (t_peak, t_trough) pairs where t_trough > t_peak of:
  (P(t_peak) − P(t_trough)) / P(t_peak)

where t_peak is a local maximum and t_trough is the subsequent minimum
```

**Python function**:
```python
def maximum_drawdown(price_history: list) -> float:
    """Maximum peak-to-trough price decline fraction.

    Args:
        price_history: List of prices P(t)
    Returns:
        MDD in [0, 1]; MDD = 0.20 means 20% peak-to-trough decline
    """
```

#### Interpretation

| Range        | Economic Meaning     | Simulation Interpretation                                                    |
|--------------|----------------------|------------------------------------------------------------------------------|
| < 0.05       | Mild correction      | Momentum episode shallow or quickly absorbed                                 |
| [0.05, 0.15) | Moderate drawdown    | Consistent with Jegadeesh-Titman reversal pattern                            |
| [0.15, 0.40] | Significant drawdown | ContrarianInvestor + RiskAverseInvestor exit producing meaningful correction |
| > 0.40       | Crash-level drawdown | Extreme bubble followed by crash; AggressiveInvestor dominated               |

#### Academic Basis

**Primary source**: De Bondt, W.F.M. & Thaler, R.H. (1985). "Does the Stock Market Overreact?" *Journal of Finance*, 40(3), 793–805.

Past 5-year winners underperform by 25% over the next 3 years — the long-run reversal magnitude. In simulation time compression, MDD of 0.15–0.30 is the calibrated expected range.

**Supporting studies**:

| Study                                   | Context                | Finding                                           | Relevance                                       |
|-----------------------------------------|------------------------|---------------------------------------------------|-------------------------------------------------|
| Jegadeesh & Titman (2001). *JF* 56(2)   | Extended study 1965–97 | Momentum profits reverse after 12 months          | MDD should follow EMI with characteristic delay |
| Brunnermeier & Nagel (2004). *JF* 59(5) | Dot-com hedge funds    | Tech hedge funds suffered 25–40% MDD in 2000–2001 | Sets MDD upper bound for extreme cases          |

#### Normal Range
MDD of 0.10–0.30 expected; consistent with momentum-then-reversal pattern in Jegadeesh & Titman (1993/2001).

#### Red Flag Threshold
- **MDD ≈ 0**: No reversal — simulation is purely upward trend; ContrarianInvestor not activating
- **MDD > 0.60**: Crash too extreme; fundamental force (mean_reversion) may need adjustment

---

### Metric: Agent Convergence Contribution (ACC)

#### Category
Agent Activity / Emergent Herding Attribution

#### Definition
The fraction of total trading volume (sum of |quantity| across all agents and rounds) attributable to each agent during momentum episodes (rounds where r(t) > 0.01), measuring which agents contribute most to the emergent herding dynamics.

#### Formula
```
ACC_i = Σ_{t: r(t) > 0.01} |quantity_i(t)| / Σ_{t: r(t) > 0.01} Σ_j |quantity_j(t)|
```

**Python function**:
```python
def agent_convergence_contribution(agent_quantities: dict, return_history: list,
                                    threshold: float = 0.01) -> dict:
    """Fraction of momentum-phase volume attributable to each agent.

    Args:
        agent_quantities: {agent_name: [|quantity| per round]}
        return_history: r(t) per round
        threshold: minimum return to define momentum-active rounds
    Returns:
        Dict {agent_name: fraction in [0, 1]}; fractions sum to 1.0
    """
```

#### Interpretation

| Agent                   | Expected ACC | Interpretation                                     |
|-------------------------|--------------|----------------------------------------------------|
| §4.1 MomentumInvestor   | 20–40%       | Primary momentum signal follower                   |
| §4.5 AggressiveInvestor | 30–50%       | Dominant amplifier due to ±80 cap and acceleration |
| §4.2 ContrarianInvestor | 5–15%        | Low during momentum; sells against trend           |
| §4.3 RiskAverseInvestor | 3–10%        | Reduces position; low activity during momentum     |
| §4.4 NoiseTrader        | 10–25%       | Background noise; randomly buys and sells          |

#### Academic Basis

**Primary source**: Nofsinger, J.R. & Sias, R.W. (1999). "Herding and Feedback Trading by Institutional and Individual Investors." *Journal of Finance*, 54(6), 2263–2295.

Institutional momentum trading (MomentumInvestor + AggressiveInvestor) accounts for approximately 40–50% of return autocorrelation. Expected combined ACC_§4.1 + ACC_§4.5 ≈ 50–80%.

**Supporting studies**:

| Study                                | Context             | Finding                                                                         | Relevance                               |
|--------------------------------------|---------------------|---------------------------------------------------------------------------------|-----------------------------------------|
| Grinblatt et al. (1995). *AER* 85(5) | Mutual fund herding | 77% momentum traders → fund herding explains 40%+ of momentum stock performance | Sets expected ACC_§4.1 + ACC_§4.5 range |
| De Long et al. (1990). *JF* 45(2)    | Noise trader risk   | Noise traders create 15–25% of price variability                                | Sets ACC_§4.4 expected range            |

#### Normal Range
ACC_§4.1 + ACC_§4.5 ≥ 50% during momentum episodes confirms emergent herding is present.

#### Red Flag Threshold
- **ACC_§4.5 = 0**: AggressiveInvestor never activates; kappa = 0 or price history too short for acceleration
- **ACC_§4.1 + ACC_§4.5 < 30%**: Momentum agents not dominant; emergent herding not occurring

---

### Metric: Risk-Averse Early Exit Index (REI)

#### Category
Agent Activity / Early Warning Signal

#### Definition
The fraction of momentum episodes where RiskAverseInvestor (§4.3) reduces its position by at least 20% of peak position **before** the price peak is reached, measuring whether the mean-variance mechanism correctly predicts and exits the bubble ahead of the crash.

#### Formula
```
REI = |{episodes e: §4.3 reduces position 20% before argmax P(t) ∈ e}| / |{episodes e}|

where an episode is a consecutive-positive-return run of length ≥ 3 rounds
```

**Python function**:
```python
def risk_averse_early_exit_index(ra_position_history: list, price_history: list,
                                  min_episode_length: int = 3) -> float:
    """Fraction of momentum episodes where §4.3 reduces position before peak.

    Args:
        ra_position_history: §4.3 position(t) per round
        price_history: prices P(t)
        min_episode_length: minimum run length to be considered an episode
    Returns:
        REI in [0, 1]; REI > 0.5 means §4.3 typically exits before peak
    """
```

#### Interpretation

| Range        | Economic Meaning                 | Simulation Interpretation                                        |
|--------------|----------------------------------|------------------------------------------------------------------|
| < 0.20       | §4.3 rarely exits early          | Volatility signal is too slow; k too large or lookback too short |
| [0.20, 0.50) | §4.3 sometimes exits early       | Mixed signal quality                                             |
| [0.50, 0.80] | §4.3 typically exits before peak | Mean-variance mechanism working correctly                        |
| > 0.80       | §4.3 consistently exits early    | Risk aversion dominates; lookback window too sensitive           |

#### Academic Basis

**Primary source**: Markowitz, H. (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77–91.

Mean-variance optimization should reduce position when variance rises above the risk tolerance threshold, which typically happens during momentum acceleration (before the peak).

#### Normal Range
REI of 0.40–0.70 expected; consistent with Markowitz prediction that risk-averse agents exit before extreme momentum episodes peak.

---

### Metric: Herding Volatility Ratio (HVR)

#### Category
Volatility

#### Definition
The ratio of return volatility during momentum episodes (r(t) > 0.01) to return volatility during quiet periods (|r(t)| ≤ 0.005), measuring the volatility amplification produced by emergent herding vs. baseline noise.

#### Formula
```
HVR = std(r(t) for t where r(t) > 0.01) / std(r(t) for t where |r(t)| ≤ 0.005)
```

**Python function**:
```python
def herding_volatility_ratio(return_history: list, momentum_threshold: float = 0.01,
                              quiet_threshold: float = 0.005) -> float:
    """Ratio of return std during momentum to quiet periods.

    Args:
        return_history: r(t) = return per round
        momentum_threshold: minimum return for momentum-active classification
        quiet_threshold: maximum |return| for quiet classification
    Returns:
        HVR ≥ 0; HVR = 1.0 means same volatility in both regimes
    """
```

#### Interpretation

| Range      | Economic Meaning            | Simulation Interpretation                                   |
|------------|-----------------------------|-------------------------------------------------------------|
| ≈ 1.0      | No volatility amplification | Momentum episodes not distinct from noise                   |
| [1.5, 3.0] | Moderate amplification      | Emergent herding creating distinguishable volatility regime |
| > 3.0      | Strong amplification        | AggressiveInvestor acceleration creating extreme volatility |

#### Normal Range
HVR of 1.5–3.0 expected; consistent with Nofsinger & Sias (1999) finding that institutional herding increases stock volatility 1.5–2× during herding episodes.

#### Red Flag Threshold
- **HVR < 1.1**: No volatility distinction; momentum episodes not distinguishable from noise
- **HVR > 5.0**: AggressiveInvestor acceleration creating unstable dynamics; reduce accel_bonus

---

### Metric: Wealth Distribution Index (WDI)

#### Category
Portfolio

#### Definition
The Gini coefficient of final agent wealth, measuring inequality in outcomes. In emergent herding, expectation is that ContrarianInvestor modestly outperforms over a full simulation run (catches the mean-reversion phase).

#### Formula
```
WDI = Gini({W_i})   where W_i = cash_i + position_i × P(T)
```

**Python function**:
```python
def wealth_distribution_index(agent_wealth: list) -> float:
    """Gini coefficient of agent wealth distribution.

    Args:
        agent_wealth: List of final wealth W_i for each agent
    Returns:
        WDI in [0, 1]
    """
```

#### Normal Range
WDI of 0.05–0.25 expected; ContrarianInvestor should modestly outperform, but AggressiveInvestor may also outperform if momentum episodes dominate.

---

## §3 Analysis Dimensions

### Dimension 1: Emergent Momentum Dynamics

**Purpose**: Identify and characterize momentum episodes that emerge from agent interaction.

**Metrics Used**: EMI, HVR
**Visualization**: Price time series with annotations marking consecutive-positive-return episodes; return histogram overlay
**Expected Pattern**: Price shows sustained upward runs (≥3 rounds) followed by corrections; HVR > 1.5 in momentum episodes

### Dimension 2: Agent Convergence Attribution

**Purpose**: Identify which agents drive emergent herding and whether both momentum types contribute.

**Metrics Used**: ACC
**Visualization**: Stacked area chart of |quantity| by agent type per round; highlight momentum-active rounds
**Expected Pattern**: §4.1 + §4.5 dominate momentum rounds; §4.2 provides counter-trading

### Dimension 3: Risk-Averse Early Warning

**Purpose**: Test whether §4.3 correctly predicts and exits before momentum peaks.

**Metrics Used**: REI, MDD
**Visualization**: §4.3 position over time; overlay with price; mark episode peaks
**Expected Pattern**: §4.3 position decreases in rounds before price peaks in ≥50% of episodes

### Dimension 4: Momentum vs. Reversal Lifecycle

**Purpose**: Track the full EMI → MDD cycle across the simulation.

**Metrics Used**: EMI, MDD
**Visualization**: Cumulative return curve; mark EMI endpoint and MDD trough
**Expected Pattern**: EMI episode followed by MDD reversal with characteristic 3–5 round delay

### Dimension 5: Wealth Outcomes

**Purpose**: Validate which strategy benefits most from emergent herding.

**Metrics Used**: WDI
**Visualization**: Bar chart of final wealth by agent type

---

## §4 Phase Analysis Framework

| Phase | Name                  | Entry Condition                                    | Exit Condition                                     | Key Indicators                                         |
|-------|-----------------------|----------------------------------------------------|----------------------------------------------------|--------------------------------------------------------|
| 1     | Noise Baseline        | Round 1;                                           | r                                                  | ≤ 0.01                                                 |
| 2     | Momentum Initiation   | r > 0.01 for 2+ consecutive rounds                 | §4.5 acceleration triggers                         | MomentumInvestor (§4.1) buying; EMI accumulating       |
| 3     | Herding Amplification | §4.5 acceleration active                           | RiskAverseInvestor (§4.3) begins reducing position | ACC_§4.5 rises; HVR rising; REI events                 |
| 4     | Peak and Reversal     | §4.3 position at minimum; price near local maximum | r < 0                                              | ContrarianInvestor (§4.2) dominant selling; MDD begins |
| 5     | Correction            | r < 0; ContrarianInvestor buying                   |                                                    | r                                                      |

---

## §5 Cross-Variant Comparison Framework

| Axis                   | Measurement | Expected Ordering                                   |
|------------------------|-------------|-----------------------------------------------------|
| Momentum intensity     | EMI         | Rule > RuleLLM ≥ LLM ≈ Rag                          |
| Reversal depth         | MDD         | Rule highest; Rag lowest                            |
| Herding amplification  | HVR         | Rule most; Rag least                                |
| Early warning accuracy | REI         | Similar across variants (§4.3 is rule-based in all) |

---

## §6 Expected Results and Validation

### 6.1 Expected Stylised Facts

| Fact                            | Quantitative Target                          | Literature Source         | How to Verify           | Failure Indicator  |
|---------------------------------|----------------------------------------------|---------------------------|-------------------------|--------------------|
| Momentum episodes emerge        | EMI ≥ 0.08                                   | Jegadeesh & Titman (1993) | Compute EMI on Rule run | EMI < 0.02         |
| Both momentum agents contribute | ACC_§4.1 + ACC_§4.5 ≥ 50% in momentum rounds | Grinblatt et al. (1995)   | Compute ACC             | Single agent > 90% |
| Risk-averse early exit occurs   | REI ≥ 0.40                                   | Markowitz (1952)          | Compute REI             | REI = 0            |
| Herding amplifies volatility    | HVR ≥ 1.5                                    | Nofsinger & Sias (1999)   | Compute HVR             | HVR < 1.1          |

### 6.2 Calibration Targets

| Metric | Target Range | Lower Bound Source         | Upper Bound Source | Adj if Below                         | Adj if Above            |
|--------|--------------|----------------------------|--------------------|--------------------------------------|-------------------------|
| EMI    | [0.08, 0.20] | Jegadeesh-Titman 1%/month  | Dot-com +271%      | Increase lambda_price or kappa       | Decrease kappa          |
| MDD    | [0.10, 0.30] | De Bondt & Thaler reversal | Dot-com −78%       | Increase fundamental contrarion beta | Decrease mean_reversion |
| HVR    | [1.5, 3.0]   | Nofsinger & Sias 1.5×      | Extreme momentum   | Increase lambda_price                | Decrease accel_bonus    |

**Calibration protocol**: 1. Run Rule variant 10 seeds. 2. Compute EMI, MDD, ACC, REI, HVR. 3. Compare against targets. 4. Adjust kappa (highest sensitivity for EMI) and contrarion beta. 5. Re-run before LLM/RuleLLM/Rag.

### 6.3 Cross-Variant Predictions

| Metric | Rule    | LLM Expected                           | RuleLLM Expected | Rag Expected                         | Theoretical Basis                      |
|--------|---------|----------------------------------------|------------------|--------------------------------------|----------------------------------------|
| EMI    | Highest | Lower (LLM may moderate momentum bids) | Near-Rule        | Lowest (retrieves De Bondt reversal) | RAG may reduce momentum aggressiveness |
| MDD    | Highest | Moderate                               | Near-Rule        | Lowest                               | Reduced momentum → smaller reversal    |
| REI    | Similar | Similar (§4.3 formula unchanged)       | Similar          | Similar                              | §4.3 is rules-based in all variants    |

### 6.4 Validation Failure Signs

| Symptom      | Diagnosis                            | Root Cause                                            | Corrective Action                                      |
|--------------|--------------------------------------|-------------------------------------------------------|--------------------------------------------------------|
| EMI < 0.02   | No momentum episodes                 | lambda_price and kappa both too small                 | Increase lambda_price ≥ 1.0 and kappa ≥ 2.0            |
| ACC_§4.5 = 0 | AggressiveInvestor never fires       | price_history too short for acceleration OR kappa = 0 | Ensure ≥ 3 rounds of history; set kappa > lambda_price |
| REI = 0      | RiskAverseInvestor never exits early | lookback too long; volatility rises too slowly        | Reduce lookback to 3–5 rounds                          |
| HVR < 1.1    | No volatility amplification          | Noise dominates; supply_elasticity too low            | Increase supply_elasticity                             |
| MDD ≈ 0      | No reversal                          | ContrarianInvestor not selling                        | Check fundamental is correctly set in §4.2 extras      |

---

## §7 Visualization Catalogue

| Plot Name               | Type         | X-axis          | Y-axis                | Overlays                                   | Purpose                                  |
|-------------------------|--------------|-----------------|-----------------------|--------------------------------------------|------------------------------------------|
| price_momentum_episodes | Line         | Round           | Price                 | Momentum episode shading; fundamental line | Shows emergent herding runs              |
| return_timeseries       | Line         | Round           | r(t)                  | ±1%, ±2% thresholds                        | Shows momentum episode amplitude         |
| agent_quantity_stacked  | Stacked area | Round           | \|quantity\|          | By agent type                              | Shows convergence attribution (ACC)      |
| risk_averse_position    | Line         | Round           | §4.3 position         | Price overlay (secondary axis)             | Shows REI early-exit pattern             |
| emi_mdd_pairs           | Scatter      | EMI per episode | MDD following episode | —                                          | Validates momentum-reversal relationship |
| wealth_by_agent         | Bar          | Agent type      | Final wealth          | —                                          | Shows wealth distribution outcome        |
| cross_variant_emi       | Bar          | Variant         | EMI mean ± std        | Jegadeesh-Titman reference                 | Research comparison                      |
