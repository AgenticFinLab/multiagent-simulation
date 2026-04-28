# FramingEffect — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                                            | Primary Metric(s) | Expected Finding                                                     | Failure Indicator                           |
|-----------|------------------------------------------------------------------------------|-------------------|----------------------------------------------------------------------|---------------------------------------------|
| O1        | Does framing asymmetry produce systematic price deviations from fundamental? | FDI, FAR          | Price oscillates above/below fundamental with asymmetric magnitude   | Price stays near 0 deviation for all rounds |
| O2        | Do gain-frame and loss-frame traders amplify or dampen price movements?      | FAR, FVI          | Framing agents amplify; rational agents dampen                       | All agents behave identically               |
| O3        | How persistent are framing-induced mispricings before rational correction?   | FDI, VTM          | Mispricings persist 5–15 rounds before correction                    | Immediate reversion every round             |
| O4        | How does LLM/RAG variant change framing susceptibility vs. rule baseline?    | FAR, FDI          | LLM/RAG shows lower framing susceptibility; more moderate deviations | Identical behavior across variants          |

---

## 2. Core Metrics Catalogue

### Metric: Framing Deviation Index (FDI)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
The mean absolute price deviation from fundamental over all rounds, measuring the average intensity of framing-induced mispricing across the simulation. A high FDI indicates that framing biases are persistently distorting prices away from fundamental value.

#### Formula
```
FDI = (1/T) × Σ_{t=1}^{T} |P(t) − F| / F

where:
  T = total number of rounds
  P(t) = market price at round t
  F = fundamental value (constant)
```

**Computation notes**: Sum absolute deviations over all rounds, divide by T. If F = 0, return NaN. Computed from `price_history` (list) and `fundamental_value` (float).

**Python function**:
```python
def framing_deviation_index(price_history: list, fundamental: float) -> float:
    """Mean absolute deviation from fundamental across all rounds.

    Args:
        price_history: List of prices P(t) for t=1..T
        fundamental: Fundamental value F (must be > 0)
    Returns:
        FDI in [0, ∞); typical range 0.0–0.25 for calibrated simulations
    """
```

#### Interpretation

| Range        | Economic Meaning                     | Simulation Interpretation                                |
|--------------|--------------------------------------|----------------------------------------------------------|
| = 0          | Price tracks fundamental perfectly   | Rational agents dominate; no framing distortion          |
| (0, 0.03)    | Mild framing distortion              | Biased agents active but quickly corrected by §4.3, §4.4 |
| [0.03, 0.10] | Moderate persistent framing bias     | Framing agents and rational agents in equilibrium        |
| > 0.10       | Strong persistent framing distortion | Biased agents overwhelm rational correction capacity     |

#### Academic Basis

**Primary source**: Tversky & Kahneman (1981). "The Framing of Decisions." *Science*, 211, 453–458. https://doi.org/10.1126/science.7455683

Mean absolute deviation from fundamental is the direct quantitative analogue of the preference reversal rate documented in framing experiments. A 70% preference reversal rate corresponds to approximately 5–15% price deviation in market settings (LeBaron, 2006, ABM calibration).

**Supporting studies**:

| Study                                                 | Context       | Finding                                                                      | Relevance                     |
|-------------------------------------------------------|---------------|------------------------------------------------------------------------------|-------------------------------|
| LeBaron (2006). *Handbook of Computational Economics* | ABM review    | Framing-biased ABMs produce 3–12% mean absolute deviation in calibrated runs | Establishes FDI normal range  |
| Kuhberger (1998). *OBHDP* 76(2)                       | Meta-analysis | Effect size d=0.51; translates to ~5–10% price impact in market context      | Calibrates expected FDI range |

#### Normal Range (from literature)
FDI of 0.03–0.10 in calibrated framing simulations (LeBaron, 2006); empirical framing-induced fund flow asymmetries produce 2.5× differential ≈ 0.04–0.08 normalized deviation (Barber & Odean, 2001).

#### Red Flag Threshold
- **Too high** (> 0.20): Price_impact λ is too large; reduce λ by 30%
- **Too low** (< 0.01): Framing agents inactive; increase framing_scale or reduce threshold
- **Zero for all rounds**: GainFrameFollower and LossFrameReactor are not activating; check that deviations exceed 0.02 threshold

#### Relationship to Other Metrics
FDI and FAR (Framing Asymmetry Ratio) are complementary: FDI measures average intensity, FAR measures directional asymmetry. FDI should be correlated with FVI (Framing Volume Impact) — rounds with high FDI should also show high FVI. If FDI is high but FVI is low, framing may be driven by external noise rather than agent trading.

---

### Metric: Framing Asymmetry Ratio (FAR)

#### Category
Behavioral / Phenomenon-Specific

#### Definition
The ratio of average absolute deviation in positive-deviation rounds to average absolute deviation in negative-deviation rounds, measuring whether gain framing and loss framing produce symmetric or asymmetric market impacts.

#### Formula
```
FAR = mean(|dev(t)| for t where dev(t) > 0) / mean(|dev(t)| for t where dev(t) < 0)

where dev(t) = (P(t) − F) / F
```

**Computation notes**: If no positive or no negative deviation rounds exist, return NaN. A ratio > 1 means gain-framing episodes are larger on average; ratio < 1 means loss-framing episodes dominate.

**Python function**:
```python
def framing_asymmetry_ratio(price_history: list, fundamental: float) -> float:
    """Ratio of average positive deviation magnitude to average negative deviation magnitude.

    Args:
        price_history: List of prices P(t)
        fundamental: Fundamental value F
    Returns:
        FAR > 0; FAR = 1.0 means symmetric; FAR > 1.0 means gain-frame dominance
    """
```

#### Interpretation

| Range      | Economic Meaning                            | Simulation Interpretation                       |
|------------|---------------------------------------------|-------------------------------------------------|
| ≈ 1.0      | Symmetric framing effects                   | Gain-frame and loss-frame agents equally active |
| (1.0, 1.5) | Mild gain-frame dominance                   | GainFrameFollower slightly more influential     |
| (1.5, 2.5) | Moderate asymmetry consistent with λ ≈ 2.25 | Loss aversion operating as expected             |
| > 2.5      | Extreme asymmetry                           | LossFrameReactor overwhelms GainFrameFollower   |

#### Academic Basis

**Primary source**: Tversky & Kahneman (1992). "Advances in Prospect Theory." *Journal of Risk and Uncertainty*, 5(4), 297–323. https://doi.org/10.1007/BF00122574

Loss aversion coefficient λ ≈ 2.25 predicts that loss-frame episodes should produce approximately 2.25× the impact of equivalent gain-frame episodes. FAR captures this asymmetry in the price series.

**Supporting studies**:

| Study                           | Context              | Finding                                                    | Relevance                                                |
|---------------------------------|----------------------|------------------------------------------------------------|----------------------------------------------------------|
| Odean (1998). *JF* 53(5)        | US retail brokerage  | Losses held 1.7× longer than gains sold                    | Confirms asymmetry in real market behavior               |
| Haigh & List (2005). *JF* 60(1) | Professional traders | Loss aversion still present but λ ≈ 1.35 for professionals | Sets lower bound for FAR in professional-dominant market |

#### Normal Range
FAR of 0.8–2.5 is expected; theoretical prediction from λ = 2.25 implies FAR ≈ 1.5–2.0 when both frame types are active.

#### Red Flag Threshold
- **Too high** (> 3.0): LossFrameReactor trade sizing is miscalibrated; reduce framing_scale for loss-frame agents
- **Too low** (< 0.5): GainFrameFollower is inactive; check gain_threshold parameter
- **= 1.0 exactly**: Both agents are behaving identically (check that gain/loss logic is correctly separated)

#### Relationship to Other Metrics
FAR is a directional decomposition of FDI. When FAR deviates significantly from 1.0, FDI will be higher because one framing type dominates and rational agents have less capacity to correct it.

---

### Metric: Framing Volume Impact (FVI)

#### Category
Agent Activity / Behavioral

#### Definition
The average absolute net demand in rounds where framing agents are active (|deviation| > 0.02), measuring how much trading volume framing agents generate relative to the total simulation.

#### Formula
```
FVI = mean(|D(t)| for t where |dev(t)| > threshold)

where D(t) = net_demand at round t = total_buy − total_sell
threshold = 0.02
```

**Python function**:
```python
def framing_volume_impact(net_demand_history: list, dev_history: list, threshold: float = 0.02) -> float:
    """Average absolute net demand in framing-active rounds.

    Args:
        net_demand_history: D(t) = buy_volume − sell_volume per round
        dev_history: deviation(t) per round
        threshold: minimum |deviation| to define framing-active rounds
    Returns:
        FVI ≥ 0; units: shares per round
    """
```

#### Interpretation

| Range      | Economic Meaning          | Simulation Interpretation                      |
|------------|---------------------------|------------------------------------------------|
| = 0        | No framing-driven trading | Framing agents never activate                  |
| (0, 200)   | Mild framing volume       | Framing agents active but small positions      |
| [200, 600] | Moderate framing volume   | Consistent with calibrated parameters          |
| > 600      | High framing volume       | Price impact high; check for runaway deviation |

#### Academic Basis

**Primary source**: Barber & Odean (2001). "Boys Will Be Boys." *Quarterly Journal of Economics*, 116(1), 261–292. https://doi.org/10.1162/003355301556400

Retail trading volume is 40–80% higher in periods of strong positive framing (market up > 5%); FVI captures this volume amplification effect in simulation.

#### Normal Range
200–600 shares/round in active framing periods; consistent with 800-share max and 30–70% activation frequency.

#### Red Flag Threshold
- **Too high** (> 1000): Price_impact λ will produce runaway deviations; reduce λ
- **Too low** (< 50): Framing agents rarely activate; check thresholds and parameter initialization

---

### Metric: Rational Correction Efficiency (RCE)

#### Category
Behavioral / Portfolio

#### Definition
The fraction of framing-induced price deviations that are corrected within 5 rounds, measuring how effectively FrameInvariantTrader and ArbitrageFramer limit framing persistence.

#### Formula
```
RCE = |{t : |dev(t+5)| < |dev(t)| × 0.5 and |dev(t)| > 0.05}| / |{t : |dev(t)| > 0.05}|
```

**Python function**:
```python
def rational_correction_efficiency(dev_history: list, lookahead: int = 5, threshold: float = 0.05) -> float:
    """Fraction of large deviations that halve within lookahead rounds.

    Args:
        dev_history: deviation(t) per round
        lookahead: rounds to look ahead for correction
        threshold: minimum deviation to be considered a framing event
    Returns:
        RCE in [0, 1]; higher is more efficient correction
    """
```

#### Interpretation

| Range      | Economic Meaning              | Simulation Interpretation                               |
|------------|-------------------------------|---------------------------------------------------------|
| > 0.7      | Efficient rational correction | Rational agents dominate; framing effect is short-lived |
| [0.4, 0.7] | Moderate correction           | Realistic mixed market                                  |
| [0.1, 0.4] | Weak correction               | Framing agents overwhelm rational capacity              |
| < 0.1      | Near-zero correction          | Rational agents essentially absent                      |

#### Academic Basis

**Primary source**: Shleifer & Vishny (1997). *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x

Rational correction should occur when mispricing exceeds noise trader risk; in this simulation, the 5% rational activation threshold implies correction attempts begin when mispricings are ≥ 5%.

#### Normal Range
RCE of 0.35–0.65 expected in calibrated simulation; pure rational market → RCE ≈ 0.90; pure noise market → RCE ≈ 0.10.

---

### Metric: Volatility Amplification Factor (VAF)

#### Category
Volatility

#### Definition
The ratio of realized return volatility in framing-active rounds vs. framing-inactive rounds, measuring how much framing agents amplify price volatility relative to the baseline.

#### Formula
```
VAF = std(returns in framing-active rounds) / std(returns in framing-inactive rounds)

where return(t) = (P(t) − P(t−1)) / P(t−1)
framing-active: |dev(t)| > 0.02
framing-inactive: |dev(t)| ≤ 0.02
```

**Python function**:
```python
def volatility_amplification_factor(price_history: list, dev_history: list, threshold: float = 0.02) -> float:
    """Ratio of return std in high-deviation rounds to low-deviation rounds.

    Args:
        price_history: List of prices
        dev_history: deviation(t) per round
        threshold: deviation threshold separating framing-active from inactive
    Returns:
        VAF ≥ 0; VAF = 1.0 means no amplification
    """
```

#### Normal Range
VAF of 1.5–3.5 expected; empirical studies show volatility 2–4× higher during market stress episodes (Bollerslev et al., 2009).

#### Red Flag Threshold
- **Too high** (> 5.0): Framing agents are creating runaway volatility; reduce framing_scale
- **Too low** (< 1.1): Framing effects are not producing distinguishable volatility regime; check parameters

---

### Metric: Wealth Distribution Index (WDI)

#### Category
Portfolio

#### Definition
The Gini coefficient of final agent wealth (cash + position × final_price), measuring inequality in outcomes across agent types. A high WDI means rational agents significantly outperformed biased agents.

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

#### Normal Range
WDI of 0.15–0.35 expected; rational agents should modestly outperform biased agents over a full simulation run.

#### Red Flag Threshold
- **Too high** (> 0.6): One agent type has collapsed; check position constraints
- **Too low** (< 0.05): All agents produce identical returns; check that agent logic is actually differentiating

---

## 3. Analysis Dimensions

### Dimension 1: Framing Distortion Dynamics

**Purpose**: Track how price deviates from fundamental over simulation rounds, identifying when and how strongly framing effects manifest.

**Metrics Used**: FDI, FAR
**Visualization**: Line plot — price vs. fundamental, with phase annotations at deviation threshold crossings
**Expected Pattern**: Price oscillates above/below fundamental with asymmetric magnitude; peaks above more frequent than troughs below if gain framing dominates

### Dimension 2: Rational vs. Biased Agent Conflict

**Purpose**: Measure how effectively rational agents (§4.3, §4.4) counteract framing-biased agents (§4.1, §4.2).

**Metrics Used**: RCE, FVI
**Visualization**: Stacked bar chart of round-by-round buy/sell volume by agent type
**Expected Pattern**: Rational agents counter large deviations; partial but incomplete correction visible

### Dimension 3: Volatility Regime Analysis

**Purpose**: Identify whether framing creates distinct high-volatility regimes vs. low-volatility baseline.

**Metrics Used**: VAF
**Visualization**: Return volatility over time with deviation threshold overlay

### Dimension 4: Agent Wealth Outcomes

**Purpose**: Compare final wealth across agent types to validate that rational agents outperform biased agents.

**Metrics Used**: WDI
**Visualization**: Bar chart of final wealth by agent type across variants

---

## 4. Phase Analysis Framework

| Phase | Name                | Entry Condition | Exit Condition | Key Indicators               |
|-------|---------------------|-----------------|----------------|------------------------------|
| 1     | Baseline            | Round 1;        | dev            | ≤ 0.02                       |
| 2     | Framing Onset       |                 | dev            | > 0.02 for first time        |
| 3     | Active Framing      |                 | dev            | > 0.05                       |
| 4     | Rational Correction |                 | dev            | drops from >0.05 toward 0.02 |

---

## 5. Cross-Variant Comparison Framework

| Axis                   | Measurement | Expected Ordering                                      |
|------------------------|-------------|--------------------------------------------------------|
| Framing susceptibility | FDI         | Rule > RuleLLM ≥ LLM ≈ Rag                             |
| Behavioral asymmetry   | FAR         | Rule most asymmetric; LLM/Rag more moderate            |
| Rational correction    | RCE         | Rule ≤ LLM ≤ Rag (RAG retrieves rational case studies) |

---

## 6. Expected Results and Validation

### 6.1 Expected Stylised Facts

| Fact                                  | Quantitative Target          | Literature Source                      | How to Verify           | Failure Indicator    |
|---------------------------------------|------------------------------|----------------------------------------|-------------------------|----------------------|
| Framing produces systematic deviation | FDI ≥ 0.03                   | Kuhberger (1998) meta-analysis         | Compute FDI on Rule run | FDI < 0.01           |
| Asymmetric gain/loss impact           | FAR ≠ 1.0; within [0.8, 2.5] | Tversky & Kahneman (1992) λ=2.25       | Compute FAR             | FAR = 1.0 exactly    |
| Rational agents partially correct     | RCE ∈ [0.35, 0.65]           | Shleifer & Vishny (1997) limits to arb | Compute RCE             | RCE < 0.05 or > 0.90 |
| Framing amplifies volatility          | VAF > 1.5                    | Bollerslev et al. (2009)               | Compute VAF             | VAF < 1.1            |

### 6.2 Calibration Targets

| Metric | Target Range | Lower Bound Source               | Upper Bound Source            | Adj if Below                | Adj if Above            |
|--------|--------------|----------------------------------|-------------------------------|-----------------------------|-------------------------|
| FDI    | [0.03, 0.10] | Kuhberger (1998)                 | LeBaron (2006)                | Increase λ or framing_scale | Decrease λ              |
| FAR    | [0.8, 2.5]   | Haigh & List (2005)              | Tversky & Kahneman (1992)     | Recheck gain/loss logic     | Lower framing_scale     |
| RCE    | [0.35, 0.65] | Full rational market upper bound | Full noise market lower bound | Increase rational_scale     | Decrease rational_scale |

**Calibration protocol**: 1. Run Rule variant 10 seeds. 2. Compute mean FDI, FAR, RCE, VAF. 3. Compare against targets. 4. Adjust λ first (largest sensitivity). 5. Re-run before LLM/RuleLLM/Rag.

### 6.3 Cross-Variant Predictions

| Metric | Rule            | LLM Expected                          | RuleLLM Expected | Rag Expected                    | Theoretical Basis                                             |
|--------|-----------------|---------------------------------------|------------------|---------------------------------|---------------------------------------------------------------|
| FDI    | Baseline        | Lower (LLM less rigidly biased)       | Near-Rule        | Moderated                       | Framing requires rigid perception; LLM may partially override |
| FAR    | Most asymmetric | More symmetric                        | Moderate         | Moderate                        | LLM persona allows partial framing resistance                 |
| RCE    | Baseline        | Higher (LLM may recognize mispricing) | Near-Rule        | Higher (retrieves case studies) | RAG retrieves framing literature                              |

### 6.4 Validation Failure Signs

| Symptom           | Diagnosis                                        | Root Cause                                   | Corrective Action                |
|-------------------|--------------------------------------------------|----------------------------------------------|----------------------------------|
| FDI = 0 every run | Framing agents never activate                    | gain_threshold too high                      | Lower threshold to 0.02          |
| FAR exactly = 1.0 | GainFrameFollower and LossFrameReactor identical | Both have same `decide()` logic (code bug)   | Inspect decide() implementations |
| RCE = 0           | Rational agents never activate                   | rational_threshold too high                  | Lower to 0.05                    |
| VAF = 1.0         | No volatility regime difference                  | noise_std dominates; framing scale too small | Increase framing_scale           |

---

## 7. Visualization Catalogue

| Plot Name              | Type        | X-axis     | Y-axis              | Overlays                 | Purpose                               |
|------------------------|-------------|------------|---------------------|--------------------------|---------------------------------------|
| price_vs_fundamental   | Line        | Round      | Price + Fundamental | ±2%, ±5% threshold lines | Shows framing distortion dynamics     |
| deviation_timeseries   | Line        | Round      | deviation(t)        | Phase annotations        | Shows framing onset and correction    |
| agent_volume_breakdown | Stacked bar | Round      | Buy/sell volume     | By agent type            | Shows relative contribution           |
| wealth_by_agent        | Bar         | Agent type | Final wealth        | Benchmark line           | Shows rational vs. biased performance |
| cross_variant_fdi      | Bar         | Variant    | FDI mean ± std      | —                        | Research comparison summary           |
