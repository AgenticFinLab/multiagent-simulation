# GamblerFallacy — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                                                    | Primary Metric(s) | Expected Finding                                                           | Failure Indicator                            |
|-----------|--------------------------------------------------------------------------------------|-------------------|----------------------------------------------------------------------------|----------------------------------------------|
| O1        | Does streak-based trading produce systematic price deviations from fundamental?      | GFI, SAR          | Price oscillates above/below fundamental driven by fallacy-induced herding | Price stays near 0 deviation for all rounds  |
| O2        | Do StreakReversalTrader and HotHandTrader produce distinguishable market signatures? | SAR, HHM          | StreakReversalTrader amplifies reversals; HotHandTrader amplifies momentum | Both agents produce identical price dynamics |
| O3        | How efficiently do rational arbitrageurs correct fallacy-induced mispricings?        | ACI               | Mispricings persist 5–15 rounds before partial correction                  | Immediate reversion every round              |
| O4        | How does LLM/RAG variant change streak susceptibility vs. rule baseline?             | GFI, ACI          | LLM/RAG reduces streak-following; more moderate deviations                 | Identical behavior across variants           |

---

## 2. Core Metrics Catalogue

### Metric: Gambler's Fallacy Index (GFI)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
The mean absolute price deviation from fundamental over all rounds, measuring the average intensity of streak-belief-induced mispricing across the simulation. A high GFI indicates that gambler's fallacy and hot-hand biases are persistently distorting prices away from fundamental value.

#### Formula
```
GFI = (1/T) × Σ_{t=1}^{T} |P(t) − F| / F

where:
  T = total number of rounds
  P(t) = market price at round t
  F = fundamental value (constant)
```

**Computation notes**: Sum absolute deviations over all rounds, divide by T. If F = 0, return NaN. Computed from `price_history` (list) and `fundamental_value` (float).

**Python function**:
```python
def gambler_fallacy_index(price_history: list, fundamental: float) -> float:
    """Mean absolute deviation from fundamental across all rounds.

    Args:
        price_history: List of prices P(t) for t=1..T
        fundamental: Fundamental value F (must be > 0)
    Returns:
        GFI in [0, ∞); typical range 0.02–0.12 for calibrated simulations
    """
```

#### Interpretation

| Range        | Economic Meaning                     | Simulation Interpretation                                |
|--------------|--------------------------------------|----------------------------------------------------------|
| = 0          | Price tracks fundamental perfectly   | Rational agents dominate; no fallacy distortion          |
| (0, 0.02)    | Mild fallacy distortion              | Biased agents active but quickly corrected by §4.3, §4.4 |
| [0.02, 0.08] | Moderate persistent fallacy bias     | Streak traders and rational agents in rough equilibrium  |
| > 0.08       | Strong persistent fallacy distortion | Biased agents overwhelm rational correction capacity     |

#### Academic Basis

**Primary source**: Tversky, A. & Kahneman, D. (1971). "Belief in the Law of Small Numbers." *Psychological Bulletin*, 76(2), 105–110. https://doi.org/10.1037/h0031322

The gambler's fallacy produces systematic probability distortions of 8–15% after streaks of length 3–5. In a market context, this translates to predictable mispricing of comparable magnitude (Rabin, 2002). GFI measures the time-averaged intensity of this distortion across all simulation rounds.

**Supporting studies**:

| Study                                                 | Context         | Finding                                                               | Relevance                                                    |
|-------------------------------------------------------|-----------------|-----------------------------------------------------------------------|--------------------------------------------------------------|
| Croson & Sundali (2005). *Management Science* 51(1)   | Casino gambling | 8% probability distortion after 3+ consecutive same outcomes          | Sets expected GFI ≈ 0.03–0.10 for realistic parameterization |
| Rabin (2002). *American Economic Review* 92(4)        | Formal model    | Gambler's fallacy intensity increases non-linearly with streak length | GFI expected to rise during long-deviation episodes          |
| LeBaron (2006). *Handbook of Computational Economics* | ABM review      | Streak-based ABMs produce 2–10% mean absolute deviation               | Establishes GFI normal range for simulation                  |

#### Normal Range (from literature)
GFI of 0.02–0.08 in calibrated gambler's fallacy simulations; Croson & Sundali (2005) 8% distortion after 3-streak maps to GFI ≈ 0.03–0.06 in continuous market context.

#### Red Flag Threshold
- **Too high** (> 0.15): Price impact λ is too large; reduce λ by 30%
- **Too low** (< 0.01): Streak agents inactive; check that initial deviations exceed 0.02 threshold
- **Zero for all rounds**: StreakReversalTrader and HotHandTrader never activate; check that deviation field is correctly broadcast from Market agent

#### Relationship to Other Metrics
GFI and SAR (Streak Asymmetry Ratio) are complementary: GFI measures average magnitude, SAR measures directional bias. GFI should be positively correlated with HHM (Hot Hand Momentum) — rounds with high GFI should also show high trading activity by both biased agents. If GFI is high but HHM is low, fallacy may be driven by StreakReversalTrader alone.

---

### Metric: Streak Asymmetry Ratio (SAR)

#### Category
Behavioral / Phenomenon-Specific

#### Definition
The ratio of average absolute deviation in upward-streak rounds (deviation > 0) to average absolute deviation in downward-streak rounds (deviation < 0), measuring whether upward and downward streak-following by biased agents produces symmetric or asymmetric market impact.

#### Formula
```
SAR = mean(|dev(t)| for t where dev(t) > 0) / mean(|dev(t)| for t where dev(t) < 0)

where dev(t) = (P(t) − F) / F
```

**Computation notes**: If no positive or no negative deviation rounds exist, return NaN. A ratio > 1 means upward streaks produce larger deviations (HotHandTrader dominance in bull runs); ratio < 1 means downward streaks dominate (StreakReversalTrader premature selling amplifying drops).

**Python function**:
```python
def streak_asymmetry_ratio(price_history: list, fundamental: float) -> float:
    """Ratio of average positive deviation magnitude to average negative deviation magnitude.

    Args:
        price_history: List of prices P(t)
        fundamental: Fundamental value F
    Returns:
        SAR > 0; SAR = 1.0 means symmetric; SAR > 1.0 means upward streak dominance
    """
```

#### Interpretation

| Range      | Economic Meaning         | Simulation Interpretation                                    |
|------------|--------------------------|--------------------------------------------------------------|
| ≈ 1.0      | Symmetric streak effects | Both biased agents equally active in both directions         |
| (0.7, 1.0) | Mild downward asymmetry  | StreakReversalTrader selling into drops amplifies them       |
| (1.0, 1.5) | Mild upward asymmetry    | HotHandTrader buying into rallies amplifies upward moves     |
| > 1.5      | Strong upward asymmetry  | HotHandTrader momentum-chasing dominates simulation dynamics |

#### Academic Basis

**Primary source**: Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners and Selling Losers." *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x

The 1.01% per month momentum premium implies that momentum-following (hot-hand) strategy produces larger upward than downward deviations over 3–12 month horizons. In a simulation context, SAR > 1 reflects hot-hand momentum dominance consistent with the Jegadeesh-Titman finding.

**Supporting studies**:

| Study                                              | Context               | Finding                                                                  | Relevance                                                                                  |
|----------------------------------------------------|-----------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| De Bondt & Thaler (1985). *JF* 40(3)               | US equities 1926–1982 | Past 5-year losers outperform winners by 25% (long-run reversal)         | Establishes gambler's fallacy reversal expectation; aligns with StreakReversalTrader logic |
| Ayton & Fischer (2004). *Memory & Cognition* 32(8) | Lab experiment        | Gambler's fallacy strongest for chance events; hot hand for skill events | SAR near 1.0 expected when market character is ambiguous                                   |

#### Normal Range
SAR of 0.7–1.5 expected; symmetric simulation → SAR ≈ 1.0; HotHandTrader-dominated → SAR ≈ 1.2–1.5.

#### Red Flag Threshold
- **Too high** (> 2.0): HotHandTrader is over-parameterized; check trade sizing formula
- **Too low** (< 0.3): StreakReversalTrader is causing crash-like asymmetry; check position limits
- **= 1.0 exactly**: StreakReversalTrader and HotHandTrader are behaving identically (check that their decide() code correctly differentiates)

#### Relationship to Other Metrics
SAR is a directional decomposition of GFI. When SAR deviates significantly from 1.0, GFI will be higher because one fallacy type dominates. SAR > 1.5 implies HotHandTrader is generating excess GFI; SAR < 0.7 implies StreakReversalTrader is driving excess downward volatility.

---

### Metric: Hot Hand Momentum (HHM)

#### Category
Agent Activity / Behavioral

#### Definition
The average absolute net demand in rounds where biased streak agents are active (|deviation| > 0.02), measuring how much trading volume the two fallacy agents (StreakReversalTrader + HotHandTrader) generate relative to total market volume.

#### Formula
```
HHM = mean(|D(t)| for t where |dev(t)| > threshold)

where D(t) = net_demand at round t = total_buy − total_sell
threshold = 0.02
```

**Python function**:
```python
def hot_hand_momentum(net_demand_history: list, dev_history: list, threshold: float = 0.02) -> float:
    """Average absolute net demand in streak-active rounds.

    Args:
        net_demand_history: D(t) = buy_volume − sell_volume per round
        dev_history: deviation(t) per round
        threshold: minimum |deviation| to define streak-active rounds
    Returns:
        HHM ≥ 0; units: shares per round
    """
```

#### Interpretation

| Range      | Economic Meaning         | Simulation Interpretation                             |
|------------|--------------------------|-------------------------------------------------------|
| = 0        | No streak-driven trading | Fallacy agents never activate                         |
| (0, 150)   | Mild streak volume       | Both fallacy agents active but taking small positions |
| [150, 500] | Moderate streak volume   | Consistent with calibrated parameters                 |
| > 500      | High streak volume       | Risk of runaway deviation; check position caps        |

#### Academic Basis

**Primary source**: Bloomfield, R., O'Hara, M. & Saar, G. (2009). "How Noise Trading Affects Markets." *Review of Financial Studies*, 22(6), 2275–2302. https://doi.org/10.1093/rfs/hhn102

Uninformed trend-following traders (analogous to HotHandTrader) increase total volume by 30–50% in controlled laboratory markets when streak signals are active. HHM captures this volume amplification effect in simulation.

**Supporting studies**:

| Study                               | Context             | Finding                                                           | Relevance                                                  |
|-------------------------------------|---------------------|-------------------------------------------------------------------|------------------------------------------------------------|
| Barber & Odean (2001). *QJE* 116(1) | US retail brokerage | Retail investors trade 40–80% more during streaks of market gains | Sets expected HHM range for realistic activation frequency |
| Griffin et al. (2003). *JFE* 70(2)  | 46 countries        | Momentum trading volume highest during 6–12 month winning streaks | Confirms HHM as a valid streak-activity measure            |

#### Normal Range
150–500 shares/round in active streak periods; consistent with 800-share max for biased agents and 30–70% activation frequency.

#### Red Flag Threshold
- **Too high** (> 800): Max position cap may be violated; inspect position arithmetic
- **Too low** (< 30): Fallacy agents rarely activate; reduce deviation activation threshold

---

### Metric: Arbitrage Correction Index (ACI)

#### Category
Behavioral / Correction Efficiency

#### Definition
The fraction of fallacy-induced large price deviations that are corrected by at least 50% within 5 rounds, measuring how effectively IndependentAssessor (§4.3) and Arbitrageur (§4.4) limit fallacy persistence.

#### Formula
```
ACI = |{t : |dev(t+5)| < |dev(t)| × 0.5 and |dev(t)| > 0.05}| / |{t : |dev(t)| > 0.05}|
```

**Python function**:
```python
def arbitrage_correction_index(dev_history: list, lookahead: int = 5, threshold: float = 0.05) -> float:
    """Fraction of large deviations that halve within lookahead rounds.

    Args:
        dev_history: deviation(t) per round
        lookahead: rounds to look ahead for correction
        threshold: minimum deviation to be considered a fallacy event
    Returns:
        ACI in [0, 1]; higher is more efficient correction
    """
```

#### Interpretation

| Range      | Economic Meaning              | Simulation Interpretation                             |
|------------|-------------------------------|-------------------------------------------------------|
| > 0.7      | Efficient rational correction | Rational agents dominate; fallacy effects short-lived |
| [0.4, 0.7] | Moderate correction           | Realistic mixed market                                |
| [0.1, 0.4] | Weak correction               | Fallacy agents overwhelm rational capacity            |
| < 0.1      | Near-zero correction          | Rational agents essentially absent                    |

#### Academic Basis

**Primary source**: Shleifer, A. & Vishny, R.W. (1997). "The Limits of Arbitrage." *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x

Rational arbitrageurs face limits imposed by noise trader risk and capital constraints. In this simulation, rational agents are capped at 500 shares (vs. 800 for biased agents), producing a 0.625 capacity ratio consistent with Pontiff (2006) finding that arbitrage capital is 40–60% of theoretical maximum.

**Supporting studies**:

| Study                                 | Context             | Finding                                                    | Relevance                                                       |
|---------------------------------------|---------------------|------------------------------------------------------------|-----------------------------------------------------------------|
| Pontiff (2006). *JFE* 80(2)           | US equity anomalies | Arbitrage capital approximately 50% of theoretical maximum | Predicts ACI ≈ 0.40–0.60 due to limited rational agent capacity |
| Jegadeesh & Titman (1993). *JF* 48(1) | US equities         | Momentum persists 3–12 months despite arbitrage            | Confirms that ACI should be well below 1.0 for streak phenomena |

#### Normal Range
ACI of 0.35–0.65 expected in calibrated simulation; pure rational market → ACI ≈ 0.90; pure noise market → ACI ≈ 0.10.

#### Red Flag Threshold
- **Too high** (> 0.85): Rational agents dominate; fallacy never has time to build; increase fallacy agent trade sizing
- **Too low** (< 0.05): Rational agents never correct anything; check that their decide() activates at |dev| > 0.05
- **= 0**: IndependentAssessor and Arbitrageur not activating; inspect rational_threshold in extras

#### Relationship to Other Metrics
ACI is inversely related to GFI: high ACI → faster correction → lower average GFI. ACI and HHM together reveal the balance of power: when HHM is high and ACI is low, fallacy agents overwhelm rational correction. When HHM is low and ACI is high, rational agents dominate and the simulation is not demonstrating the phenomenon.

---

### Metric: Volatility Amplification Factor (VAF)

#### Category
Volatility

#### Definition
The ratio of realized return volatility in streak-active rounds vs. streak-inactive rounds, measuring how much fallacy agents amplify price volatility relative to the baseline NoiseTrader-only regime.

#### Formula
```
VAF = std(returns in streak-active rounds) / std(returns in streak-inactive rounds)

where return(t) = (P(t) − P(t−1)) / P(t−1)
streak-active: |dev(t)| > 0.02
streak-inactive: |dev(t)| ≤ 0.02
```

**Python function**:
```python
def volatility_amplification_factor(price_history: list, dev_history: list, threshold: float = 0.02) -> float:
    """Ratio of return std in high-deviation rounds to low-deviation rounds.

    Args:
        price_history: List of prices
        dev_history: deviation(t) per round
        threshold: deviation threshold separating streak-active from inactive
    Returns:
        VAF ≥ 0; VAF = 1.0 means no amplification
    """
```

#### Interpretation

| Range      | Economic Meaning                 | Simulation Interpretation                                     |
|------------|----------------------------------|---------------------------------------------------------------|
| < 1.0      | Fallacy agents reduce volatility | Agents are mean-reverting in fallacy-active rounds (unlikely) |
| [1.0, 1.5) | Mild amplification               | Fallacy traders partially offset noise                        |
| [1.5, 3.5] | Moderate amplification           | Consistent with calibrated parameters                         |
| > 3.5      | Strong amplification             | Fallacy agents create explosive volatility                    |

#### Academic Basis

**Primary source**: Bollerslev, T., Tauchen, G. & Zhou, H. (2009). "Expected Stock Returns and Variance Risk Premia." *Review of Financial Studies*, 22(11), 4463–4492. https://doi.org/10.1093/rfs/hhp008

Empirical volatility is 2–4× higher during high-dispersion (streak-active) market episodes. VAF of 1.5–3.5 maps directly to this empirical range.

**Supporting studies**:

| Study                                     | Context        | Finding                                                 | Relevance                                               |
|-------------------------------------------|----------------|---------------------------------------------------------|---------------------------------------------------------|
| Bloomfield et al. (2009). *RFS* 22(6)     | Lab markets    | Trend-following traders increase return volatility 2.1× | Sets expected VAF ≈ 2.0 for HotHandTrader activation    |
| Croson & Sundali (2005). *Mgmt Sci* 51(1) | Casino streaks | Reversal bets increase variance of outcomes by 1.5–2.0× | Sets expected VAF lower bound from StreakReversalTrader |

#### Normal Range
VAF of 1.5–3.5 expected; lower end when StreakReversalTrader dominates (mean-reverting tendency); upper end when HotHandTrader dominates (momentum amplification).

#### Red Flag Threshold
- **Too high** (> 5.0): Fallacy agents are creating runaway volatility; reduce trade sizing or max position
- **Too low** (< 1.1): Fallacy effects not producing distinguishable volatility regime; check parameters

---

### Metric: Wealth Distribution Index (WDI)

#### Category
Portfolio

#### Definition
The Gini coefficient of final agent wealth (cash + position × final_price), measuring inequality in outcomes across agent types. A high WDI means rational agents significantly outperformed biased agents; a low WDI means all agents achieved similar outcomes regardless of strategy quality.

#### Formula
```
WDI = Gini({W_i})   where W_i = cash_i + position_i × P(T)

Gini(x) = Σ_i Σ_j |x_i − x_j| / (2 × n² × mean(x))
```

**Python function**:
```python
def wealth_distribution_index(agent_wealth: list) -> float:
    """Gini coefficient of agent wealth distribution.

    Args:
        agent_wealth: List of final wealth values W_i for each agent
    Returns:
        WDI in [0, 1]; 0 = perfect equality; 1 = extreme inequality
    """
```

#### Interpretation

| Range        | Economic Meaning        | Simulation Interpretation                                     |
|--------------|-------------------------|---------------------------------------------------------------|
| < 0.05       | Near-equal final wealth | All agent strategies equally (in)effective                    |
| [0.05, 0.20] | Mild inequality         | Rational agents modestly outperform biased agents             |
| [0.20, 0.45] | Moderate inequality     | Rational agents clearly outperform; biased agents lose wealth |
| > 0.45       | High inequality         | One agent type catastrophically outperforms                   |

#### Academic Basis

**Primary source**: De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1991). "The Survival of Noise Traders in Financial Markets." *Journal of Business*, 64(1), 1–19. https://doi.org/10.1086/296523

The DeLong et al. (1991) model shows that noise traders can survive and sometimes outperform rational traders when noise trader risk is high — implying WDI should be modest even when biased agents are clearly irrational. Pure rational dominance (WDI > 0.5) contradicts the noise trader survival literature.

**Supporting studies**:

| Study                             | Context           | Finding                                               | Relevance                                       |
|-----------------------------------|-------------------|-------------------------------------------------------|-------------------------------------------------|
| Barber & Odean (2000). *JF* 55(2) | US retail trading | Active (biased) traders underperform by 6.5% per year | Sets WDI expected direction (rational > biased) |
| Odean (1998). *JF* 53(5)          | Retail brokerage  | Overconfident streak-following trades lose money      | Confirms rational agents should outperform WDI  |

#### Normal Range
WDI of 0.10–0.35 expected; rational agents should modestly outperform biased agents over a full simulation run due to position-limit asymmetry (500 vs. 800 max shares).

#### Red Flag Threshold
- **Too high** (> 0.60): One agent type has collapsed; check position constraints
- **Too low** (< 0.03): All agents produce identical returns; check that agent logic is differentiating correctly

---

## 3. Analysis Dimensions

### Dimension 1: Fallacy Distortion Dynamics

**Purpose**: Track how price deviates from fundamental over simulation rounds, identifying when and how strongly gambler's fallacy and hot-hand biases manifest.

**Metrics Used**: GFI, SAR
**Visualization**: Line plot — price vs. fundamental, with phase annotations at deviation threshold crossings
**Expected Pattern**: Price oscillates above/below fundamental; upward deviations tend to be larger (HotHandTrader amplification) than downward deviations (SAR > 1.0)

### Dimension 2: Rational vs. Biased Agent Conflict

**Purpose**: Measure how effectively rational agents (§4.3, §4.4) counteract fallacy-biased agents (§4.1, §4.2).

**Metrics Used**: ACI, HHM
**Visualization**: Stacked bar chart of round-by-round buy/sell volume by agent type
**Expected Pattern**: Rational agents counter large deviations; ACI ∈ [0.35, 0.65] reflects partial but incomplete correction

### Dimension 3: Volatility Regime Analysis

**Purpose**: Identify whether streak-following creates distinct high-volatility regimes vs. low-volatility baseline.

**Metrics Used**: VAF
**Visualization**: Return volatility over time with deviation threshold overlay
**Expected Pattern**: Volatility visibly higher in streak-active rounds; VAF ≥ 1.5

### Dimension 4: Agent Wealth Outcomes

**Purpose**: Compare final wealth across agent types to validate that rational agents outperform biased agents.

**Metrics Used**: WDI
**Visualization**: Bar chart of final wealth by agent type across variants

---

## 4. Phase Analysis Framework

| Phase | Name                | Entry Condition | Exit Condition | Key Indicators               |
|-------|---------------------|-----------------|----------------|------------------------------|
| 1     | Baseline            | Round 1;        | dev            | ≤ 0.02                       |
| 2     | Fallacy Onset       |                 | dev            | > 0.02 for first time        |
| 3     | Active Fallacy      |                 | dev            | > 0.05                       |
| 4     | Rational Correction |                 | dev            | drops from >0.05 toward 0.02 |

---

## 5. Cross-Variant Comparison Framework

| Axis                   | Measurement | Expected Ordering                                             |
|------------------------|-------------|---------------------------------------------------------------|
| Fallacy susceptibility | GFI         | Rule > RuleLLM ≥ LLM ≈ Rag                                    |
| Directional asymmetry  | SAR         | Rule most asymmetric; LLM/Rag more moderate                   |
| Rational correction    | ACI         | Rule ≤ LLM ≤ Rag (RAG retrieves rational studies on momentum) |

---

## 6. Expected Results and Validation

### 6.1 Expected Stylised Facts

| Fact                                  | Quantitative Target          | Literature Source                      | How to Verify           | Failure Indicator    |
|---------------------------------------|------------------------------|----------------------------------------|-------------------------|----------------------|
| Fallacy produces systematic deviation | GFI ≥ 0.02                   | Croson & Sundali (2005) 8% distortion  | Compute GFI on Rule run | GFI < 0.005          |
| Asymmetric streak impact              | SAR ≠ 1.0; within [0.7, 1.5] | Jegadeesh & Titman (1993) momentum     | Compute SAR             | SAR = 1.0 exactly    |
| Rational agents partially correct     | ACI ∈ [0.35, 0.65]           | Shleifer & Vishny (1997) limits to arb | Compute ACI             | ACI < 0.05 or > 0.85 |
| Streak agents amplify volatility      | VAF > 1.5                    | Bloomfield et al. (2009)               | Compute VAF             | VAF < 1.1            |

### 6.2 Calibration Targets

| Metric | Target Range | Lower Bound Source                | Upper Bound Source                 | Adj if Below                       | Adj if Above            |
|--------|--------------|-----------------------------------|------------------------------------|------------------------------------|-------------------------|
| GFI    | [0.02, 0.08] | Croson & Sundali (2005)           | Rabin (2002)                       | Increase λ or activation threshold | Decrease λ              |
| SAR    | [0.7, 1.5]   | De Bondt & Thaler (1985) reversal | Jegadeesh & Titman (1993) momentum | Increase StreakReversal sizing     | Increase HotHand sizing |
| ACI    | [0.35, 0.65] | Full noise market (ACI≈0.10)      | Full rational market (ACI≈0.90)    | Increase rational_scale            | Decrease rational_scale |

**Calibration protocol**: 1. Run Rule variant 10 seeds. 2. Compute mean GFI, SAR, ACI, VAF. 3. Compare against targets. 4. Adjust λ first (highest sensitivity). 5. Re-run before LLM/RuleLLM/Rag.

### 6.3 Cross-Variant Predictions

| Metric | Rule            | LLM Expected                                   | RuleLLM Expected | Rag Expected                           | Theoretical Basis                                                |
|--------|-----------------|------------------------------------------------|------------------|----------------------------------------|------------------------------------------------------------------|
| GFI    | Baseline        | Lower (LLM less rigidly biased toward streaks) | Near-Rule        | Moderated                              | Streak-following requires rigid rule; LLM may partially override |
| SAR    | Most asymmetric | More symmetric                                 | Moderate         | Moderate                               | LLM persona allows partial momentum resistance                   |
| ACI    | Baseline        | Higher (LLM may recognize streak mispricing)   | Near-Rule        | Higher (retrieves momentum literature) | RAG retrieves Jegadeesh-Titman and contrarian studies            |

### 6.4 Validation Failure Signs

| Symptom              | Diagnosis                                        | Root Cause                                                               | Corrective Action                                                       |
|----------------------|--------------------------------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------|
| GFI = 0 every run    | Fallacy agents never activate                    | deviation threshold too high                                             | Lower activation threshold to 0.02                                      |
| SAR exactly = 1.0    | StreakReversalTrader and HotHandTrader identical | Both have same decide() logic (code bug)                                 | Inspect decide() implementations for correct directional logic          |
| ACI = 0              | Rational agents never activate                   | rational activation threshold too high                                   | Lower to 0.05                                                           |
| VAF = 1.0            | No volatility regime difference                  | noise_std dominates; fallacy scale too small                             | Increase trade sizing for fallacy agents                                |
| GFI high but WDI ≈ 0 | All agents profit equally                        | Fallacy agents riding momentum profitably (DeLong noise trader survival) | Expected behavior — not a failure; report noise trader survival finding |

---

## 7. Visualization Catalogue

| Plot Name              | Type        | X-axis     | Y-axis              | Overlays                 | Purpose                                       |
|------------------------|-------------|------------|---------------------|--------------------------|-----------------------------------------------|
| price_vs_fundamental   | Line        | Round      | Price + Fundamental | ±2%, ±5% threshold lines | Shows fallacy distortion dynamics             |
| deviation_timeseries   | Line        | Round      | deviation(t)        | Phase annotations        | Shows fallacy onset and correction            |
| agent_volume_breakdown | Stacked bar | Round      | Buy/sell volume     | By agent type            | Shows StreakReversal vs. HotHand contribution |
| wealth_by_agent        | Bar         | Agent type | Final wealth        | Benchmark line           | Shows rational vs. biased performance         |
| cross_variant_gfi      | Bar         | Variant    | GFI mean ± std      | —                        | Research comparison summary                   |
| sar_by_variant         | Bar         | Variant    | SAR                 | SAR = 1.0 reference      | Shows directional asymmetry across variants   |
