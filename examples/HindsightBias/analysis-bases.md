# HindsightBias — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question                                                                                 | Primary Metric(s) | Expected Finding                                                                                          | Failure Indicator                                         |
|-----------|---------------------------------------------------------------------------------------------------|-------------------|-----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| O1        | Does hindsight-induced overconfidence produce systematic price deviations from fundamental?       | HBI, OBI          | Price overshoots fundamental in the direction of recent moves; biased agents amplify momentum             | Price stays near 0 deviation for all rounds               |
| O2        | Do HindsightOverconfident and OutcomeLearner produce distinguishable market effects?              | OBI, HBI          | Both destabilize similarly; OutcomeLearner produces more persistent momentum due to selective attribution | Both produce identical dynamics at all parameter settings |
| O3        | How efficiently do ProcessEvaluator and ContrarianSkeptic correct hindsight-inflated mispricings? | ACI               | Mispricings partially corrected in 5–15 rounds; never fully corrected due to capacity asymmetry           | Immediate reversion every round or zero correction        |
| O4        | How does LLM/RAG variant reduce hindsight susceptibility vs. rule baseline?                       | HBI, ACI          | LLM/RAG produces lower HBI; higher ACI due to access to behavioral finance literature                     | Identical behavior across variants                        |

---

## §2 Core Metrics Catalogue

### Metric: Hindsight Bias Index (HBI)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
The mean absolute price deviation from fundamental over all rounds, measuring the average intensity of hindsight-induced overconfident mispricing. A high HBI indicates that HindsightOverconfident and OutcomeLearner are persistently distorting prices away from fundamental value.

#### Formula
```
HBI = (1/T) × Σ_{t=1}^{T} |P(t) − F| / F

where:
  T = total number of rounds
  P(t) = market price at round t
  F = fundamental value (constant)
```

**Computation notes**: Sum absolute deviations over all rounds, divide by T. If F = 0, return NaN. Computed from `price_history` (list) and `fundamental_value` (float).

**Python function**:
```python
def hindsight_bias_index(price_history: list, fundamental: float) -> float:
    """Mean absolute deviation from fundamental across all rounds.

    Args:
        price_history: List of prices P(t) for t=1..T
        fundamental: Fundamental value F (must be > 0)
    Returns:
        HBI in [0, ∞); typical range 0.02–0.10 for calibrated simulations
    """
```

#### Interpretation

| Range        | Economic Meaning                       | Simulation Interpretation                                |
|--------------|----------------------------------------|----------------------------------------------------------|
| = 0          | Price tracks fundamental perfectly     | Rational agents dominate; no hindsight distortion        |
| (0, 0.02)    | Mild hindsight distortion              | Biased agents active but quickly corrected by §4.3, §4.4 |
| [0.02, 0.08] | Moderate persistent hindsight bias     | Biased agents and rational agents in rough equilibrium   |
| > 0.08       | Strong persistent hindsight distortion | Biased agents overwhelm rational correction capacity     |

#### Academic Basis

**Primary source**: Fischhoff, B. (1975). "Hindsight ≠ Foresight." *Journal of Experimental Psychology: HPP*, 1(3), 288–299. https://doi.org/10.1037/0096-1523.1.3.288

Hindsight bias produces systematic belief distortions of 15–40% (Roese & Vohs, 2012 meta-analysis). In an asset pricing context, this translates to an overconfidence premium in position sizing that produces price deviations of comparable magnitude (Daniel et al., 1998).

**Supporting studies**:

| Study                                                             | Context                    | Finding                                                            | Relevance                                   |
|-------------------------------------------------------------------|----------------------------|--------------------------------------------------------------------|---------------------------------------------|
| Roese & Vohs (2012). *Perspectives on Psychological Science* 7(5) | Meta-analysis 800+ studies | Mean effect size d = 0.42; largest for negative financial outcomes | Calibrates expected HBI range: 0.02–0.10    |
| Daniel et al. (1998). *JF* 53(6)                                  | Asset pricing model        | Overconfidence produces momentum: 3–12 month return continuation   | Predicts HBI rises during momentum phase    |
| LeBaron (2006). *Handbook of Computational Economics*             | ABM review                 | Overconfidence-biased ABMs produce 2–10% mean absolute deviation   | Establishes HBI normal range for simulation |

#### Normal Range (from literature)
HBI of 0.02–0.08 in calibrated hindsight simulations; Daniel et al. (1998) momentum premium of 1–2% per month for 3–12 months maps to HBI ≈ 0.03–0.07 in normalized form.

#### Red Flag Threshold
- **Too high** (> 0.15): Price impact λ is too large; reduce λ by 30%
- **Too low** (< 0.01): Biased agents inactive; check that deviations exceed 0.02 activation threshold
- **Zero for all rounds**: HindsightOverconfident and OutcomeLearner never activating; verify deviation field is broadcast from Market

#### Relationship to Other Metrics
HBI and OBI (Outcome Bias Index) are complementary: HBI measures average magnitude over all rounds, OBI measures directional persistence in post-gain vs. post-loss periods. HBI should correlate positively with VAF — rounds with high HBI should also show higher return volatility. If HBI is high but VAF ≈ 1, the market is mispricings but not volatility-amplifying (check trade sizing parameters).

---

### Metric: Outcome Bias Index (OBI)

#### Category
Behavioral / Phenomenon-Specific

#### Definition
The ratio of average price deviation magnitude in post-gain rounds (rounds following a positive return) to average price deviation in post-loss rounds (rounds following a negative return), measuring whether hindsight-biased agents produce asymmetric momentum in bull vs. bear phases.

#### Formula
```
OBI = mean(|dev(t)| for t where P(t−1) > P(t−2)) / mean(|dev(t)| for t where P(t−1) < P(t−2))

where dev(t) = (P(t) − F) / F
```

**Computation notes**: Post-gain rounds are those following a positive return; post-loss rounds follow a negative return. If either class has no rounds, return NaN.

**Python function**:
```python
def outcome_bias_index(price_history: list, fundamental: float) -> float:
    """Ratio of mean |deviation| in post-gain rounds to post-loss rounds.

    Args:
        price_history: List of prices P(t)
        fundamental: Fundamental value F
    Returns:
        OBI > 0; OBI = 1.0 means symmetric; OBI > 1.0 means bull-phase dominance
    """
```

#### Interpretation

| Range      | Economic Meaning            | Simulation Interpretation                                                   |
|------------|-----------------------------|-----------------------------------------------------------------------------|
| ≈ 1.0      | Symmetric hindsight effects | Biased agents equally active after gains and losses                         |
| (0.7, 1.0) | Mild bear-phase dominance   | OutcomeLearner slow to reduce position in losses                            |
| (1.0, 1.5) | Mild bull-phase dominance   | HindsightOverconfident amplifies post-gain momentum                         |
| > 1.5      | Strong bull-phase dominance | Overconfidence strongest after gains; calibrated from Barber & Odean (2000) |

#### Academic Basis

**Primary source**: Fischhoff, B. & Beyth, R. (1975). "'I Knew It Would Happen'." *OBHP*, 13(1), 1–16. https://doi.org/10.1016/0030-5073(75)90002-1

Outcome bias is strongest for positive outcomes (success attribution is stronger than failure discount). This predicts OBI > 1.0 in well-calibrated simulations.

**Supporting studies**:

| Study                             | Context               | Finding                                             | Relevance                                   |
|-----------------------------------|-----------------------|-----------------------------------------------------|---------------------------------------------|
| Barber & Odean (2000). *JF* 55(2) | US retail 1991–96     | Active trading most intense after recent gains      | Predicts OBI > 1.0; expected value 1.1–1.5  |
| Baron & Hershey (1988). *JEP:HPP* | Professional judgment | Decision ratings 40% higher after positive outcomes | Validates OBI > 1.0 for success attribution |

#### Normal Range
OBI of 0.8–1.5 expected; theoretical prediction from asymmetric attribution implies OBI ≈ 1.1–1.3.

#### Red Flag Threshold
- **Too high** (> 2.0): success_attribution parameter too large; reduce for OutcomeLearner
- **Too low** (< 0.4): failure_discount is overwhelming success effects; check parameter calibration
- **= 1.0 exactly**: HindsightOverconfident and OutcomeLearner behave identically in both phases (expected at default extras = 1.0; only meaningful failure if extras differ)

#### Relationship to Other Metrics
OBI and HBI decompose the same signal: HBI is the average magnitude; OBI reveals whether bull or bear phases dominate. OBI > 1.5 combined with high HBI indicates the simulation is in a sustained momentum phase consistent with Daniel et al. (1998) overreaction prediction.

---

### Metric: Narrative Correction Efficiency (NCE)

#### Category
Behavioral / Correction Efficiency

#### Definition
The fraction of hindsight-inflated large price deviations (|deviation| > 0.05) that are corrected by at least 50% within 5 rounds, measuring how effectively ProcessEvaluator (§4.3) and ContrarianSkeptic (§4.4) limit hindsight-induced mispricing persistence.

#### Formula
```
NCE = |{t : |dev(t+5)| < |dev(t)| × 0.5 and |dev(t)| > 0.05}| / |{t : |dev(t)| > 0.05}|
```

**Python function**:
```python
def narrative_correction_efficiency(dev_history: list, lookahead: int = 5, threshold: float = 0.05) -> float:
    """Fraction of large deviations that halve within lookahead rounds.

    Args:
        dev_history: deviation(t) per round
        lookahead: rounds to look ahead for correction
        threshold: minimum deviation to be considered a hindsight event
    Returns:
        NCE in [0, 1]; higher is more efficient correction
    """
```

#### Interpretation

| Range      | Economic Meaning              | Simulation Interpretation                                          |
|------------|-------------------------------|--------------------------------------------------------------------|
| > 0.7      | Efficient rational correction | ProcessEvaluator/ContrarianSkeptic dominate; hindsight short-lived |
| [0.4, 0.7] | Moderate correction           | Realistic mixed market                                             |
| [0.1, 0.4] | Weak correction               | Biased agents overwhelm rational capacity                          |
| < 0.1      | Near-zero correction          | Rational agents essentially absent                                 |

#### Academic Basis

**Primary source**: Shleifer, A. & Vishny, R.W. (1997). "The Limits of Arbitrage." *Journal of Finance*, 52(1), 35–55.

Rational correction should occur when mispricing exceeds noise trader risk. The 5% threshold corresponds to ProcessEvaluator's and ContrarianSkeptic's activation level, ensuring NCE only measures events where both rational agents should be active.

**Supporting studies**:

| Study                            | Context              | Finding                                                                    | Relevance                                          |
|----------------------------------|----------------------|----------------------------------------------------------------------------|----------------------------------------------------|
| Pontiff (2006). *JFE* 80(2)      | US equity anomalies  | Arbitrage capital ≈ 50% of theoretical maximum                             | Predicts NCE ≈ 0.40–0.65 due to capacity asymmetry |
| Daniel et al. (1998). *JF* 53(6) | Overconfidence model | Long-run reversal occurs 12–36 months after overconfidence-driven momentum | NCE should be incomplete over short horizons       |

#### Normal Range
NCE of 0.35–0.65 expected in calibrated simulation; pure rational market → NCE ≈ 0.90; pure noise market → NCE ≈ 0.10.

#### Red Flag Threshold
- **Too high** (> 0.85): Rational agents over-parameterized; hindsight never builds; increase biased agent trade sizing
- **Too low** (< 0.05): Rational agents never activate; check threshold in ProcessEvaluator decide()
- **= 0**: ProcessEvaluator and ContrarianSkeptic not correcting; inspect 0.05 threshold activation

#### Relationship to Other Metrics
NCE is inversely related to HBI: high NCE → faster correction → lower HBI. NCE and VAF together describe the bias-correction cycle: when VAF is high (biased agents amplifying), NCE should be lower (correction is harder). If NCE is high and VAF is also high, check that rational agents are not accidentally amplifying rather than correcting.

---

### Metric: Volatility Amplification Factor (VAF)

#### Category
Volatility

#### Definition
The ratio of realized return volatility in bias-active rounds vs. bias-inactive rounds, measuring how much hindsight-induced overconfidence amplifies price volatility.

#### Formula
```
VAF = std(returns in bias-active rounds) / std(returns in bias-inactive rounds)

where return(t) = (P(t) − P(t−1)) / P(t−1)
bias-active: |dev(t)| > 0.02
bias-inactive: |dev(t)| ≤ 0.02
```

**Python function**:
```python
def volatility_amplification_factor(price_history: list, dev_history: list, threshold: float = 0.02) -> float:
    """Ratio of return std in high-deviation rounds to low-deviation rounds.

    Args:
        price_history: List of prices
        dev_history: deviation(t) per round
        threshold: deviation threshold separating bias-active from inactive
    Returns:
        VAF ≥ 0; VAF = 1.0 means no amplification
    """
```

#### Interpretation

| Range      | Economic Meaning              | Simulation Interpretation                                    |
|------------|-------------------------------|--------------------------------------------------------------|
| < 1.0      | Bias agents reduce volatility | Agents are mean-reverting in bias-active rounds (unexpected) |
| [1.0, 1.5) | Mild amplification            | Hindsight effects present but weak                           |
| [1.5, 3.5] | Moderate amplification        | Consistent with calibrated parameters                        |
| > 3.5      | Strong amplification          | Biased agents creating explosive volatility                  |

#### Academic Basis

**Primary source**: Bollerslev, T., Tauchen, G. & Zhou, H. (2009). "Expected Stock Returns and Variance Risk Premia." *Review of Financial Studies*, 22(11), 4463–4492.

Empirical volatility is 2–4× higher during overconfidence-driven momentum episodes. VAF of 1.5–3.5 maps to this empirical range.

**Supporting studies**:

| Study                              | Context              | Finding                                                                 | Relevance                                      |
|------------------------------------|----------------------|-------------------------------------------------------------------------|------------------------------------------------|
| Daniel et al. (1998). *JF* 53(6)   | Overconfidence model | Overconfidence generates excess return variance 2–3× rational benchmark | Sets expected VAF ≈ 2.0–3.0                    |
| Barber & Odean (2002). *RFS* 15(2) | Online trading       | Online trader volatility 40–60% higher than phone traders               | Confirms VAF > 1.5 for hindsight-biased cohort |

#### Normal Range
VAF of 1.5–3.5 expected; consistent with Daniel et al. (1998) overconfidence volatility prediction.

#### Red Flag Threshold
- **Too high** (> 5.0): Biased agents creating runaway volatility; reduce trade sizing
- **Too low** (< 1.1): Bias effects not producing distinguishable volatility regime; check that deviation threshold is right

---

### Metric: Overconfidence Wealth Penalty (OWP)

#### Category
Portfolio

#### Definition
The percentage by which hindsight-biased agents' final wealth (§4.1 + §4.2 average) falls below rational agents' final wealth (§4.3 + §4.4 average), measuring the wealth cost of sustained hindsight bias and outcome bias.

#### Formula
```
OWP = 1 − mean(W_biased) / mean(W_rational)

where W_i = cash_i + position_i × P(T)
W_biased = {W_{§4.1}, W_{§4.2}}
W_rational = {W_{§4.3}, W_{§4.4}}
```

**Python function**:
```python
def overconfidence_wealth_penalty(biased_wealth: list, rational_wealth: list) -> float:
    """Percentage wealth penalty for hindsight-biased agents vs. rational agents.

    Args:
        biased_wealth: Final wealth [W_{§4.1}, W_{§4.2}]
        rational_wealth: Final wealth [W_{§4.3}, W_{§4.4}]
    Returns:
        OWP in (−∞, 1]; positive = biased underperform; negative = biased outperform
    """
```

#### Interpretation

| Range        | Economic Meaning          | Simulation Interpretation                                 |
|--------------|---------------------------|-----------------------------------------------------------|
| < 0          | Biased agents outperform  | Noise trader survival — hindsight generates lucky profits |
| [0, 0.10)    | Mild underperformance     | Small penalty for overconfidence                          |
| [0.10, 0.30] | Moderate underperformance | Calibrated expected range                                 |
| > 0.30       | Severe underperformance   | Hindsight bias severely degrading wealth                  |

#### Academic Basis

**Primary source**: Barber, B.M. & Odean, T. (2000). "Trading Is Hazardous to Your Wealth." *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226

Active traders (overconfident, consistent with hindsight bias) underperform by 6.5% per year in US retail data. OWP of 0.10–0.25 across a simulation run is consistent with this finding.

**Supporting studies**:

| Study                                      | Context                     | Finding                                                                  | Relevance                                |
|--------------------------------------------|-----------------------------|--------------------------------------------------------------------------|------------------------------------------|
| De Long et al. (1991). *J. Business* 64(1) | Noise trader survival model | Noise traders can survive and occasionally outperform (OWP < 0 possible) | Sets expected OWP direction and variance |
| Odean (1998). *JF* 53(5)                   | Retail brokerage            | Overconfident trades negative DGTW-adjusted alpha                        | Confirms OWP > 0 is expected             |

#### Normal Range
OWP of 0.05–0.25 expected; consistent with 6.5% annual underperformance mapped to simulation timeframe.

#### Red Flag Threshold
- **OWP < −0.20**: Biased agents dramatically outperforming — momentum is so strong it rewards overconfidence; reduce λ to prevent bubble dynamics
- **OWP > 0.50**: Biased agents catastrophically underperforming; check position constraints

---

### Metric: Wealth Distribution Index (WDI)

#### Category
Portfolio

#### Definition
The Gini coefficient of final agent wealth across all 5 agents (cash + position × final_price), measuring overall wealth inequality in the simulation.

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

| Range        | Economic Meaning        | Simulation Interpretation            |
|--------------|-------------------------|--------------------------------------|
| < 0.05       | Near-equal final wealth | All strategies equally (in)effective |
| [0.05, 0.20] | Mild inequality         | Rational agents modestly outperform  |
| [0.20, 0.45] | Moderate inequality     | Clear rational advantage             |
| > 0.45       | High inequality         | One agent type collapsed             |

#### Normal Range
WDI of 0.10–0.35 expected; rational agents should modestly outperform across full simulation run.

#### Red Flag Threshold
- **Too high** (> 0.60): One agent type collapsed; check position constraints
- **Too low** (< 0.03): All agents produce identical returns; check differentiation

---

## §3 Analysis Dimensions

### Dimension 1: Hindsight Distortion Dynamics

**Purpose**: Track how price deviates from fundamental, identifying when hindsight-inflated momentum emerges.

**Metrics Used**: HBI, OBI
**Visualization**: Line plot — price vs. fundamental, with phase annotations at 2% and 5% threshold crossings
**Expected Pattern**: Price overshoots fundamental in direction of recent returns; OBI > 1.0 indicates bull-phase dominance

### Dimension 2: Rational vs. Biased Agent Conflict

**Purpose**: Measure how effectively ProcessEvaluator (§4.3) and ContrarianSkeptic (§4.4) counteract hindsight-biased agents.

**Metrics Used**: NCE, HBI
**Visualization**: Stacked bar chart of round-by-round buy/sell volume by agent type
**Expected Pattern**: NCE ∈ [0.35, 0.65] — partial but incomplete correction

### Dimension 3: Volatility Regime Analysis

**Purpose**: Identify whether hindsight creates distinct high-volatility regimes.

**Metrics Used**: VAF
**Visualization**: Return volatility over time with deviation threshold overlay

### Dimension 4: Agent Wealth Outcomes

**Purpose**: Validate that overconfident agents underperform rational agents.

**Metrics Used**: WDI, OWP
**Visualization**: Bar chart of final wealth by agent type; OWP bar across variants

---

## §4 Phase Analysis Framework

| Phase | Name                | Entry Condition | Exit Condition | Key Indicators        |
|-------|---------------------|-----------------|----------------|-----------------------|
| 1     | Baseline            | Round 1;        | dev            | ≤ 0.02                |
| 2     | Bias Onset          |                 | dev            | > 0.02 for first time |
| 3     | Active Momentum     |                 | dev            | > 0.05                |
| 4     | Rational Correction |                 | dev            | drops from >0.05      |

---

## §5 Cross-Variant Comparison Framework

| Axis                     | Measurement | Expected Ordering                                            |
|--------------------------|-------------|--------------------------------------------------------------|
| Hindsight susceptibility | HBI         | Rule > RuleLLM ≥ LLM ≈ Rag                                   |
| Post-gain dominance      | OBI         | Rule most asymmetric; LLM/Rag more balanced                  |
| Rational correction      | NCE         | Rule ≤ LLM ≤ Rag (RAG retrieves Fischhoff/Daniel literature) |

---

## §6 Expected Results and Validation

### 6.1 Expected Stylised Facts

| Fact                                    | Quantitative Target          | Literature Source             | How to Verify           | Failure Indicator                       |
|-----------------------------------------|------------------------------|-------------------------------|-------------------------|-----------------------------------------|
| Hindsight produces systematic deviation | HBI ≥ 0.02                   | Roese & Vohs (2012) d=0.42    | Compute HBI on Rule run | HBI < 0.005                             |
| Bull-phase momentum dominance           | OBI > 1.0; within [0.8, 1.5] | Barber & Odean (2000)         | Compute OBI             | OBI = 1.0 exactly at non-default extras |
| Rational agents partially correct       | NCE ∈ [0.35, 0.65]           | Shleifer & Vishny (1997)      | Compute NCE             | NCE < 0.05 or > 0.85                    |
| Biased agents amplify volatility        | VAF > 1.5                    | Daniel et al. (1998)          | Compute VAF             | VAF < 1.1                               |
| Biased agents underperform              | OWP ∈ [0.05, 0.25]           | Barber & Odean (2000) 6.5%/yr | Compute OWP             | OWP < 0 persistently                    |

### 6.2 Calibration Targets

| Metric | Target Range | Lower Bound Source                   | Upper Bound Source    | Adj if Below                                   | Adj if Above               |
|--------|--------------|--------------------------------------|-----------------------|------------------------------------------------|----------------------------|
| HBI    | [0.02, 0.08] | Roese & Vohs (2012)                  | Daniel et al. (1998)  | Increase λ or activation threshold             | Decrease λ                 |
| OBI    | [0.8, 1.5]   | Symmetric market                     | Barber & Odean (2000) | Check success_attribution vs. failure_discount | Reduce success_attribution |
| NCE    | [0.35, 0.65] | Full noise market                    | Full rational market  | Increase rational agent scale                  | Decrease rational scale    |
| OWP    | [0.05, 0.25] | De Long et al. (1991) noise survival | Barber & Odean (2000) | Lengthen simulation                            | Check position limits      |

**Calibration protocol**: 1. Run Rule variant 10 seeds. 2. Compute mean HBI, OBI, NCE, VAF, OWP. 3. Compare against targets. 4. Adjust λ first (highest sensitivity). 5. Re-run before LLM/RuleLLM/Rag.

### 6.3 Cross-Variant Predictions

| Metric | Rule            | LLM Expected                                  | RuleLLM Expected | Rag Expected                             | Theoretical Basis                                                          |
|--------|-----------------|-----------------------------------------------|------------------|------------------------------------------|----------------------------------------------------------------------------|
| HBI    | Baseline        | Lower (LLM may question "obvious" narratives) | Near-Rule        | Moderated                                | Hindsight requires rigid retrospective certainty; LLM may partially resist |
| OBI    | Most asymmetric | More balanced                                 | Moderate         | Moderate                                 | LLM persona allows partial narrative resistance                            |
| NCE    | Baseline        | Higher (LLM recognizes mispricing)            | Near-Rule        | Highest (retrieves Fischhoff literature) | RAG retrieves behavioral finance papers                                    |

### 6.4 Validation Failure Signs

| Symptom                                 | Diagnosis                                | Root Cause                                                 | Corrective Action                             |
|-----------------------------------------|------------------------------------------|------------------------------------------------------------|-----------------------------------------------|
| HBI = 0 every run                       | Biased agents never activate             | deviation threshold too high                               | Lower threshold to 0.02                       |
| OBI exactly = 1.0 at non-default extras | §4.1 and §4.2 behave identically         | success_attribution / failure_discount not differentiating | Set extras asymmetrically for experimentation |
| NCE = 0                                 | Rational agents never correct            | threshold in ProcessEvaluator too high                     | Verify 0.05 threshold                         |
| VAF = 1.0                               | No volatility regime difference          | noise_std too large relative to bias                       | Increase biased agent trade sizing            |
| OWP < 0 persistently                    | Biased agents consistently outperforming | Momentum too strong; agents riding trends profitably       | Reduce λ; note noise trader survival effect   |

---

## §7 Visualization Catalogue

| Plot Name                   | Type        | X-axis     | Y-axis              | Overlays                 | Purpose                                  |
|-----------------------------|-------------|------------|---------------------|--------------------------|------------------------------------------|
| price_vs_fundamental        | Line        | Round      | Price + Fundamental | ±2%, ±5% threshold lines | Shows hindsight-induced momentum         |
| deviation_timeseries        | Line        | Round      | deviation(t)        | Phase annotations        | Shows bias onset and rational correction |
| post_gain_vs_loss_deviation | Bar         | Phase type | Mean \|dev(t)\|     | OBI = 1.0 reference      | Shows bull vs. bear phase asymmetry      |
| agent_volume_breakdown      | Stacked bar | Round      | Buy/sell volume     | By agent type            | Shows §4.1/§4.2 vs. §4.3/§4.4 conflict   |
| wealth_by_agent             | Bar         | Agent type | Final wealth        | Benchmark line           | Shows rational advantage                 |
| owp_by_variant              | Bar         | Variant    | OWP                 | OWP = 0 reference        | Shows hindsight cost across variants     |
| cross_variant_hbi           | Bar         | Variant    | HBI mean ± std      | —                        | Research comparison summary              |
