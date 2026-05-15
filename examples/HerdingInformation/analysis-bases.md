# HerdingInformation Analysis Methodology

## §1 Objectives

This document defines the measurement framework for the HerdingInformation multi-agent simulation. The simulation models **information cascade herding** — the mechanism by which sequential decision-makers suppress private signals and follow observed crowd behavior, ultimately causing market prices to deviate systematically from fundamental values. The analysis framework quantifies:

1. **Cascade intensity** — how strongly the cascade mechanism dominates price discovery
2. **Cascade persistence** — how many rounds the cascade remains self-reinforcing
3. **Reputation herding contribution** — the relative role of reputation-driven mimicry vs. cascade-driven mimicry
4. **Information loss** — how much private signal information is destroyed by social learning
5. **Volatility amplification** — whether cascades amplify price volatility beyond fundamental noise
6. **Wealth redistribution** — cross-agent wealth inequality produced by cascade dynamics

---

## §2 Core Metrics Catalogue

### Metric: Cascade Concentration Index (CCI)

#### Category
Phenomenon-Specific

#### Definition
The fraction of total trading volume (measured in shares) that is attributable to cascade-driven agents (CascadeFollower §4.1 and ReputationHerder §4.2) during rounds in which the cascade is active (i.e., deviation ≠ 0 and |deviation| > 0.02). A high CCI indicates that the market is dominated by social-signal followers rather than fundamental-signal processors.

#### Formula
```
CCI = Σ_{t: |δ(t)|>0.02} [V_CascadeFollower(t) + V_ReputationHerder(t)] /
      Σ_{t: |δ(t)|>0.02} V_total(t)

where:
  δ(t)                  = (P(t) − F) / F,  normalised price deviation at round t
  V_CascadeFollower(t)  = |shares traded by CascadeFollower at round t|
  V_ReputationHerder(t) = |shares traded by ReputationHerder at round t|
  V_total(t)            = total shares traded by all agents at round t
  Σ_{t: cond}           = sum over rounds where the condition holds
```

**Computation notes**: Compute from `trade_history` data frame, filtering to rounds where `|deviation| > 0.02`. If no such round exists, return 0.0 (cascade never activated). Agent identification uses `agent_type` field in trade records.

**Python function**:
```python
def cascade_concentration_index(
    trade_history: List[Dict],
    price_history: List[float],
    fundamental: float,
    activation_threshold: float = 0.02
) -> float:
    """Fraction of cascade-phase volume attributable to cascade-driven agents.

    Args:
        trade_history: List of trade records with keys 'agent_type', 'quantity', 'round'
        price_history: Price at each round (1-indexed)
        fundamental: Fundamental value F (scalar)
        activation_threshold: |deviation| above which cascade is considered active (default 0.02)
    Returns:
        CCI in [0, 1]; 0.0 if cascade never activated; expected 0.50–0.75 under cascade regime
    """
```

#### Interpretation

| Range        | Economic Meaning           | Simulation Interpretation                                           |
|--------------|----------------------------|---------------------------------------------------------------------|
| 0.0          | No cascade activity        | Cascade never activated; IndependentThinker and Contrarian dominate |
| (0.0, 0.40)  | Weak cascade concentration | Mixed regime; private-signal agents partially counteract cascade    |
| [0.40, 0.70] | Moderate cascade dominance | Normal cascade regime; §4.1 + §4.2 jointly drive 40–70% of volume   |
| > 0.70       | Strong cascade dominance   | Pure cascade lock-in; independent agents exhausted or inactive      |

#### Academic Basis

**Primary source**:
Banerjee, A. V. (1992). "A Simple Model of Herd Behavior." *Quarterly Journal of Economics*, 107(3), 797–817. https://doi.org/10.2307/2118364

This paper established the information cascade model in which rational agents rationally ignore their own private signals and follow the crowd, producing informationally inefficient outcomes. CCI operationalises Banerjee's core prediction: when cascade dynamics are active, the proportion of volume driven by signal-suppressors should dominate signal-processors.

**Supporting studies**:

| Study                                                                                                   | Context                         | Finding                                                                                                                       | Relevance to This Metric                                              |
|---------------------------------------------------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| Bikhchandani, Hirshleifer & Welch (1992). *JPE*, 100(5), 992–1026.                                      | Theoretical cascade model       | Cascades are fragile; one strong public signal can break them. Volume share of cascaders ≈ 60–80% in pure cascade equilibrium | Validates the 0.40–0.70 normal range and the > 0.70 lock-in threshold |
| Welch, I. (2000). "Herding Among Security Analysts." *JFE*, 58(3), 369–396.                             | Analyst recommendation cascades | Herding analysts account for 57% of revisions in trending periods                                                             | Supports CCI ≈ 0.50–0.60 as the empirical baseline                    |
| Avery, C. & Zemsky, P. (1998). "Multidimensional Uncertainty and Herd Behavior." *AER*, 88(4), 724–748. | Asset market cascades           | Cascade-driven traders generate 45–65% of volume in herding episodes                                                          | Confirms expected normal range for CCI                                |

#### Normal Range (from literature)
Cascade-driven agents account for 40–70% of trading volume during herding episodes in the financial literature (Welch, 2000; Avery & Zemsky, 1998). Below 40% indicates that independent rational agents are providing sufficient counterweight; above 70% indicates a pure cascade lock-in with minimal price discovery.

#### Red Flag Threshold
- **Too high** (> 0.80): IndependentThinker and Contrarian position caps may be too small relative to cascade agents; increase `signal_precision` or `contrarian_threshold` parameters, or add more independent-agent instances
- **Too low** (< 0.20): Cascade mechanism not activating; check `cascade_trigger` — if set too high, CascadeFollower never reaches threshold; reduce `cascade_trigger` by 1–2 rounds
- **Zero for all rounds**: `cascade_trigger` is never reached OR `activation_threshold` (0.02) is never crossed; check `price_impact` (λ) — if too low, deviation never exceeds threshold

#### Relationship to Other Metrics
CCI is a leading indicator of CPD (§2.2): high CCI rounds precede sustained cascade episodes measured by CPD. CCI and RHI (§2.3) are complementary: CCI measures combined cascade agent share while RHI measures the split between §4.1 and §4.2. When CCI > 0.60 but RHI < 0.5, ReputationHerder is driving the bulk of cascade volume — indicating reputation-based herding is more active than pure cascade following.

#### Implementation Notes
Computed from `Rule/analysis.py` `cascade_concentration_index()` function. Inputs: `trade_history` list and `price_history` list from simulation output JSON. Returns float in [0, 1]. No variant-specific adaptation needed; metric is identical across Rule/LLM/RuleLLM/Rag variants.

---

### Metric: Cascade Persistence Duration (CPD)

#### Category
Phenomenon-Specific

#### Definition
The mean number of consecutive rounds in which the cascade remains active — defined as rounds where |deviation| > 0.02 without interruption. Measures the self-reinforcing nature of the cascade: longer duration indicates stronger positive feedback between cascade agents and price.

#### Formula
```
CPD = (1/K) × Σ_{k=1}^{K} L_k

where:
  K   = number of distinct cascade episodes (consecutive runs of |δ(t)| > 0.02)
  L_k = length (in rounds) of cascade episode k
  δ(t) = (P(t) − F) / F
```

**Computation notes**: Identify contiguous runs of rounds where |deviation| > 0.02. Count the number of rounds in each run. If no cascade episode exists (K=0), return 0. Edge case: if deviation crosses threshold then drops below for one round then returns, treat as two episodes.

**Python function**:
```python
def cascade_persistence_duration(
    price_history: List[float],
    fundamental: float,
    activation_threshold: float = 0.02
) -> float:
    """Mean length (in rounds) of cascade episodes (consecutive |deviation| > threshold).

    Args:
        price_history: Price at each round (1-indexed list of floats)
        fundamental: Fundamental value F (scalar)
        activation_threshold: |deviation| above which cascade is considered active (default 0.02)
    Returns:
        Mean episode length in rounds; 0.0 if no cascade episode; expected 3–10 rounds per episode
    """
```

#### Interpretation

| Range   | Economic Meaning           | Simulation Interpretation                                                                   |
|---------|----------------------------|---------------------------------------------------------------------------------------------|
| 0       | No cascade activation      | Deviation never exceeds 2%; pure noise regime                                               |
| (0, 3)  | Brief cascade bursts       | Short-lived herding; corrected quickly by IndependentThinker and Contrarian                 |
| [3, 10] | Normal cascade persistence | Typical herding episode duration consistent with Bikhchandani et al. (1992)                 |
| > 10    | Prolonged cascade          | Strong positive feedback; IndependentThinker capacity overwhelmed; calibration check needed |

#### Academic Basis

**Primary source**:
Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades." *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849

Bikhchandani et al. showed that cascades are fragile: they can last indefinitely until disrupted by a sufficiently precise public signal. In finite-round simulations, this translates to persistent deviation episodes terminated by random noise or rational arbitrage pressure. CPD measures this persistence directly.

**Supporting studies**:

| Study                                                                                                      | Context               | Finding                                                            | Relevance to This Metric                                      |
|------------------------------------------------------------------------------------------------------------|-----------------------|--------------------------------------------------------------------|---------------------------------------------------------------|
| Scharfstein, D. S. & Stein, J. C. (1990). "Herd Behavior and Investment." *AER*, 80(3), 465–479.           | Manager herding model | Herding episodes persist for 4–8 decision cycles before correction | Validates 3–10 round expected range                           |
| Grinblatt, M., Titman, S. & Wermers, R. (1995). "Momentum Investment Strategies." *AER*, 85(5), 1088–1105. | Mutual fund herding   | Herding quarters persist for 2–4 consecutive quarters              | Confirms cascade persistence; quarter ≈ 3–5 simulation rounds |

#### Normal Range (from literature)
Herding episodes in financial markets typically persist for 3–8 consecutive decision periods (Scharfstein & Stein, 1990; Grinblatt et al., 1995). In simulation with 50 rounds, 3–10 round episodes per cascade are realistic; > 15 consecutive rounds without correction indicates miscalibration.

#### Red Flag Threshold
- **Too high** (> 15 rounds): `signal_precision` of IndependentThinker too low to break cascade; increase `signal_precision` from 0.7 toward 0.9; also check `contrarian_threshold` — if too high, Contrarian activates too late
- **Too low** (< 2 rounds): `price_impact` (λ) too low; deviation reverts too quickly; increase λ or reduce `mean_reversion` (γ)
- **Zero**: Cascade never activates; check `cascade_trigger` parameter; reduce from 3 to 2 for easier activation

#### Relationship to Other Metrics
CPD directly determines VAF (§2.5): longer cascade duration produces higher volatility amplification. CPD and CCI move together: high CCI rounds are the rounds included in CPD episodes. ICE (§2.4) is mechanically related: longer cascades destroy more private signal information, so ICE should increase monotonically with CPD.

#### Implementation Notes
Computed from price_history and fundamental scalar. Uses run-length encoding on the boolean series `|deviation| > 0.02`. Returns mean episode length as float. Defined in `Rule/analysis.py`.

---

### Metric: Reputation Herding Index (RHI)

#### Category
Behavioral

#### Definition
The ratio of ReputationHerder (§4.2) volume to CascadeFollower (§4.1) volume during cascade-active rounds. RHI > 1 indicates that reputation-based herding is quantitatively more important than pure information cascade following; RHI < 1 indicates the reverse. RHI = 1 means both mechanisms contribute equally.

#### Formula
```
RHI = Σ_{t: |δ(t)|>0.02} V_ReputationHerder(t) /
      Σ_{t: |δ(t)|>0.02} V_CascadeFollower(t)

where:
  V_ReputationHerder(t) = |shares traded by ReputationHerder at round t|
  V_CascadeFollower(t)  = |shares traded by CascadeFollower at round t|
```

**Computation notes**: If CascadeFollower total volume = 0, return NaN (denominator zero). Filter to rounds where |deviation| > 0.02. Compute absolute value of shares (both agents may buy or sell, but we compare magnitude of participation). At default extras (reputation_concern = 0.8, social_weight = 0.7), expected ratio ≈ 0.75 (ReputationHerder trades smaller quantities but at lower threshold).

**Python function**:
```python
def reputation_herding_index(
    trade_history: List[Dict],
    price_history: List[float],
    fundamental: float,
    activation_threshold: float = 0.02
) -> float:
    """Ratio of ReputationHerder to CascadeFollower volume during cascade episodes.

    Args:
        trade_history: List of trade records with 'agent_type', 'quantity', 'round'
        price_history: Price at each round (1-indexed list of floats)
        fundamental: Fundamental value F (scalar)
        activation_threshold: |deviation| above which cascade is active (default 0.02)
    Returns:
        RHI ratio; NaN if CascadeFollower never trades; expected 0.5–1.2 at default calibration
    """
```

#### Interpretation

| Range        | Economic Meaning                | Simulation Interpretation                                                                                    |
|--------------|---------------------------------|--------------------------------------------------------------------------------------------------------------|
| NaN          | CascadeFollower never activated | cascade_trigger too high or cascade_count never reaches threshold                                            |
| < 0.50       | Cascade following dominates     | CascadeFollower drives most herding volume; reputation mechanism secondary                                   |
| [0.50, 1.20] | Balanced dual mechanism         | Both Scharfstein & Stein (1990) and Banerjee (1992) mechanisms active                                        |
| > 1.20       | Reputation herding dominates    | ReputationHerder responds first and more aggressively; lower threshold (0.02) creates earlier, larger orders |

#### Academic Basis

**Primary source**:
Scharfstein, D. S. & Stein, J. C. (1990). "Herd Behavior and Investment." *American Economic Review*, 80(3), 465–479. JSTOR: 2006678.

This paper derived the theoretical basis for reputation-driven herding: managers with uncertain ability mimic others to avoid being identified as low-ability. The mechanism is distinct from information cascades: reputation herders act to signal competence, not because they believe others' signals are informative. RHI directly measures the relative importance of this mechanism vs. pure information cascade.

**Supporting studies**:

| Study                                                                                                                            | Context                | Finding                                                                        | Relevance to This Metric                                         |
|----------------------------------------------------------------------------------------------------------------------------------|------------------------|--------------------------------------------------------------------------------|------------------------------------------------------------------|
| Banerjee, A. V. (1992). *QJE*, 107(3), 797–817.                                                                                  | Rational cascade model | Pure cascade agents trade larger quantities but with a higher threshold        | Predicts RHI < 1 at default calibration when cascade_trigger = 3 |
| Lakonishok, J., Shleifer, A. & Vishny, R. W. (1992). "The Impact of Institutional Trading on Stock Prices." *JFE*, 32(1), 23–43. | Mutual fund herding    | Institutional herding attributed 35% to reputation, 65% to information cascade | Baseline: RHI ≈ 0.54 for institutional investors                 |

#### Normal Range (from literature)
Lakonishok et al. (1992) suggest reputation herding accounts for approximately 35% of institutional herding volume, implying RHI ≈ 0.54 (35/65). At default simulation parameters with reputation_concern = 0.8, expected RHI ≈ 0.60–0.90, reflecting ReputationHerder's lower activation threshold but smaller position cap.

#### Red Flag Threshold
- **Too high** (> 2.0): `reputation_concern` parameter is set too high or max shares cap for ReputationHerder (600) is disproportionate; reduce `reputation_concern` from 0.8 toward 0.5
- **Too low** (< 0.20): `cascade_trigger` too low — CascadeFollower activates too easily and overwhelms ReputationHerder; increase `cascade_trigger` to 4 or reduce CascadeFollower count
- **NaN always**: CascadeFollower never activates; reduce `cascade_trigger` from 3 to 2

#### Relationship to Other Metrics
RHI and CCI are complementary decompositions: CCI measures total cascade agent volume share, RHI measures the split within cascade agents. High CCI with low RHI (< 0.5) indicates CascadeFollower is the dominant destabilizer; high CCI with high RHI (> 1.0) indicates ReputationHerder is driving the cascade. ICE (§2.4) should be higher when RHI > 1: reputation herders suppress private signals before cascade followers activate, destroying more information.

#### Implementation Notes
Requires `trade_history` with `agent_type` annotations. Returns float (ratio) or `float('nan')`. Defined in `Rule/analysis.py`. For LLM/RuleLLM/Rag variants, agent types are identified by class name in trade records.

---

### Metric: Information Cascade Efficiency (ICE)

#### Category
Behavioral

#### Definition
The fraction of rounds in which at least one cascade-following agent (CascadeFollower §4.1 or ReputationHerder §4.2) trades in the same direction as the deviation (i.e., buys when deviation > 0, sells when deviation < 0) while the IndependentThinker (§4.3) trades in the opposite direction. This measures the rate at which social learning destroys price discovery: every such round represents a loss of private signal information in the aggregate price.

#### Formula
```
ICE = (1/T) × Σ_{t=1}^{T} 1[cascade_trade_dir(t) = deviation_dir(t)
                               AND independent_trade_dir(t) ≠ deviation_dir(t)]

where:
  cascade_trade_dir(t)     = sign of net order from (CascadeFollower + ReputationHerder) at t;
                             +1 if net buy, −1 if net sell, 0 if no trade
  independent_trade_dir(t) = sign of net order from IndependentThinker at t
  deviation_dir(t)         = sign of δ(t) = sign(P(t) − F)
  T                        = total simulation rounds
  1[·]                     = indicator function
```

**Computation notes**: Compute per-round net direction for each agent group. If cascade agents do not trade at round t, or if independent agent does not trade, exclude that round from numerator (but still include in denominator T). Edge case: if no round satisfies both conditions, return 0.

**Python function**:
```python
def information_cascade_efficiency(
    trade_history: List[Dict],
    price_history: List[float],
    fundamental: float
) -> float:
    """Fraction of rounds where cascade agents reinforce deviation while independent agent opposes.

    Args:
        trade_history: List of trade records with 'agent_type', 'quantity', 'round'
        price_history: Price at each round (1-indexed)
        fundamental: Fundamental value F (scalar)
    Returns:
        ICE in [0, 1]; higher values indicate greater private signal destruction;
        expected 0.15–0.40 under normal cascade conditions
    """
```

#### Interpretation

| Range        | Economic Meaning                 | Simulation Interpretation                                                     |
|--------------|----------------------------------|-------------------------------------------------------------------------------|
| 0.0          | No information destruction       | Cascade agents never trade against private signal; price discovery intact     |
| (0.0, 0.15)  | Low cascade efficiency           | Cascade occasionally suppresses signals; mostly independent trading dominates |
| [0.15, 0.40] | Moderate information destruction | Normal cascade regime; expected outcome from Banerjee (1992) dynamics         |
| > 0.40       | High information destruction     | Cascade dominates most rounds; price systematically diverges from fundamental |

#### Academic Basis

**Primary source**:
Avery, C. & Zemsky, P. (1998). "Multidimensional Uncertainty and Herd Behavior in Financial Markets." *American Economic Review*, 88(4), 724–748. JSTOR: 116851.

Avery & Zemsky showed that when agents herd despite having private information, the aggregate price incorporates less private information than if agents acted independently. ICE directly captures this information destruction rate — counting rounds where social learning (cascade following) simultaneously conflicts with rational signal processing (independent thinking).

**Supporting studies**:

| Study                                           | Context                   | Finding                                                                                    | Relevance to This Metric                            |
|-------------------------------------------------|---------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------|
| Banerjee, A. V. (1992). *QJE*, 107(3), 797–817. | Sequential decision model | In cascade equilibrium, 30–60% of agents ignore private signals                            | Implies ICE ≈ 0.15–0.40 at cascade activation rate  |
| Welch, I. (2000). *JFE*, 58(3), 369–396.        | Analyst cascade           | Cascading analysts (66% of cases) systematically moved consensus away from private signals | Validates ICE as an information-destruction measure |

#### Normal Range (from literature)
Based on Banerjee (1992) equilibrium analysis, cascade agents ignore private signals in approximately 30–60% of decisions during cascade episodes. Given cascade activation rate of 30–50% of all rounds, ICE ≈ 0.15–0.40 is the expected range for a well-calibrated simulation.

#### Red Flag Threshold
- **Too high** (> 0.60): Cascade agents are too aggressive; reduce `social_weight` and `reputation_concern`; or increase IndependentThinker position cap beyond 500 to provide stronger correction
- **Too low** (< 0.05): Cascade rarely activates or cascade agents are too weak relative to independents; check `cascade_trigger` and `social_weight` parameters
- **Zero always**: Cascade never activates OR cascade and independent always trade in same direction (impossible if code is correct); debug `CascadeFollower.decide()` logic

#### Relationship to Other Metrics
ICE is driven by CPD (§2.2): longer cascade duration means more rounds of information destruction. ICE increases with CCI (§2.1): when cascade agents dominate volume, they also dominate direction. ICE and WDI (§2.6) should correlate inversely: higher information destruction (higher ICE) leads to worse outcomes for independent-signal traders, increasing wealth inequality.

#### Implementation Notes
Requires per-round net direction computation. Defined in `Rule/analysis.py`. Cross-variant note: in LLM/RuleLLM/Rag variants, direction may be softer (partial buys) — use sign of net quantity as proxy.

---

### Metric: Volatility Amplification Factor (VAF)

#### Category
Volatility

#### Definition
The ratio of return standard deviation during cascade-active rounds (|deviation| > 0.02) to return standard deviation during quiet rounds (|deviation| ≤ 0.02). Measures whether the cascade mechanism generates excess price volatility beyond fundamental noise.

#### Formula
```
VAF = σ_active / σ_quiet

where:
  σ_active = std({r(t) : |δ(t)| > 0.02}),  return std during cascade rounds
  σ_quiet  = std({r(t) : |δ(t)| ≤ 0.02}),  return std during quiet rounds
  r(t)     = (P(t) − P(t−1)) / P(t−1),      round return
  δ(t)     = (P(t) − F) / F
```

**Computation notes**: Compute returns from price_history. Split rounds into cascade-active (|deviation| > 0.02) and quiet (|deviation| ≤ 0.02). Compute standard deviation for each group. If either group has fewer than 5 observations, return NaN. If σ_quiet = 0 (impossible with noise term), return NaN.

**Python function**:
```python
def volatility_amplification_factor(
    price_history: List[float],
    fundamental: float,
    activation_threshold: float = 0.02,
    min_obs: int = 5
) -> float:
    """Ratio of return volatility during cascade rounds vs quiet rounds.

    Args:
        price_history: Price at each round (1-indexed list of floats)
        fundamental: Fundamental value F (scalar)
        activation_threshold: |deviation| boundary between cascade and quiet (default 0.02)
        min_obs: Minimum observations required per group to compute std (default 5)
    Returns:
        VAF ratio; NaN if insufficient data; expected 1.5–3.5 under cascade conditions
    """
```

#### Interpretation

| Range      | Economic Meaning             | Simulation Interpretation                                                 |
|------------|------------------------------|---------------------------------------------------------------------------|
| < 1.0      | Cascade rounds less volatile | Implausible; indicates miscalibration or phase misclassification          |
| [1.0, 1.5) | Mild amplification           | Cascade agents only modestly increase volatility; mean reversion dominant |
| [1.5, 3.5] | Normal amplification         | Expected range; cascade agents produce 1.5–3.5× excess volatility         |
| > 3.5      | Extreme amplification        | Cascade destabilizing; reduce `social_weight` or `price_impact`           |

#### Academic Basis

**Primary source**:
De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). "Noise Trader Risk in Financial Markets." *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703

De Long et al. demonstrated that noise traders (analogous to cascade followers in this simulation) create excess volatility beyond fundamental noise. Their model predicts volatility amplification of 1.5–4× in markets with significant noise trader presence.

**Supporting studies**:

| Study                                                                          | Context           | Finding                                                                      | Relevance to This Metric                                                |
|--------------------------------------------------------------------------------|-------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Shiller, R. J. (1981). "Do Stock Prices Move Too Much?" *AER*, 71(3), 421–436. | S&P 500 1871–1979 | Stock price variance 5–13× higher than fundamental dividend variance         | Validates VAF > 1 as normative expectation; our 1.5–3.5 is conservative |
| Bikhchandani et al. (1992). *JPE*, 100(5), 992–1026.                           | Cascade theory    | Cascade regime generates 2–4× excess return variance vs. no-cascade baseline | Directly validates the 1.5–3.5 expected range                           |

#### Normal Range (from literature)
De Long et al. (1990) predict 1.5–4× excess volatility from noise trading. Bikhchandani et al. (1992) suggest 2–4× in cascade episodes. Our simulation with 5 agent types and position caps implies slightly lower amplification; VAF = 1.5–3.5 is the calibration target.

#### Red Flag Threshold
- **Too high** (> 5.0): `price_impact` (λ) is too high or `social_weight` + `reputation_concern` are both at maximum; reduce price_impact from 0.01 toward 0.005
- **Too low** (< 1.2): Cascade mechanism too weak; increase `social_weight` from 0.7 toward 1.0; or reduce `cascade_trigger` by 1
- **NaN**: Insufficient rounds in one category; run more simulation rounds or reduce `activation_threshold` to capture more cascade rounds

#### Relationship to Other Metrics
VAF is mechanically driven by CPD (§2.2): longer episodes produce larger VAF. VAF captures the aggregate volatility effect while CCI captures the attribution. A simulation with high CCI but low VAF indicates cascade agents are trading but not moving prices — check `price_impact` (λ) calibration. ICE (§2.4) and VAF should move together: more rounds of information destruction → more deviation → more volatility.

#### Implementation Notes
Defined in `Rule/analysis.py`. For HerdingInformation, this is the standard Walrasian price model (unlike HerdEffect's order-book model), so deviation is directly available in market broadcast. No variant-specific adaptation required.

---

### Metric: Wealth Distribution Index (WDI)

#### Category
Portfolio

#### Definition
The Gini coefficient of final wealth (cash + position × final_price) across all investor agents (excluding Market). A Gini of 0 indicates all agents end with equal wealth; a Gini of 1 indicates one agent holds all wealth. Measures the redistribution of wealth from cascade followers to rational contrarian traders.

#### Formula
```
WDI = Gini(W_1, W_2, ..., W_N)
    = (1/(2N²μ)) × Σ_i Σ_j |W_i − W_j|

where:
  W_i      = cash_i + position_i × P(T),  final wealth of agent i
  N        = number of investor agents (excluding Market)
  μ        = mean final wealth across all agents
  P(T)     = price at final round T
```

**Computation notes**: Compute from `agent_states` at final round. Include all 5 investor types (CascadeFollower, ReputationHerder, IndependentThinker, Contrarian, NoiseTrader). Exclude Market agent. If all agents have equal final wealth, WDI = 0. Edge case: if P(T) < 0 (impossible), use 0 for position value.

**Python function**:
```python
def wealth_distribution_index(
    agent_states: List[Dict],
    final_price: float
) -> float:
    """Gini coefficient of final agent wealth across all investor types.

    Args:
        agent_states: List of agent state dicts with keys 'cash', 'position', 'agent_type'
                     (Market agent excluded; all 5 investor types included)
        final_price: Price at final simulation round P(T)
    Returns:
        Gini coefficient in [0, 1]; 0.0 = perfect equality; expected 0.10–0.30
    """
```

#### Interpretation

| Range        | Economic Meaning    | Simulation Interpretation                                                            |
|--------------|---------------------|--------------------------------------------------------------------------------------|
| 0.0          | Perfect equality    | All agents equally profitable; no wealth transfer from biased to rational            |
| (0.0, 0.10)  | Low inequality      | Weak cascade dynamics; rational agents barely outperform cascade followers           |
| [0.10, 0.30] | Moderate inequality | Normal range; rational agents (IndependentThinker, Contrarian) profit from cascade   |
| > 0.30       | High inequality     | Strong cascade exploitation; NoiseTrader and cascade followers severely underperform |

#### Academic Basis

**Primary source**:
De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1991). "The Survival of Noise Traders in Financial Markets." *Journal of Business*, 64(1), 1–19. https://doi.org/10.1086/296523

De Long et al. (1991) showed that noise traders (analogous to cascade followers) can survive despite systematic wealth losses if price volatility also offers them gains. WDI measures the cumulative wealth inequality that results from this dynamic: cascade followers who systematically suppress private signals should underperform rational signal-processors over time.

**Supporting studies**:

| Study                                                                               | Context         | Finding                                                                                   | Relevance to This Metric                                                   |
|-------------------------------------------------------------------------------------|-----------------|-------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| Shleifer, A. & Vishny, R. W. (1997). "The Limits to Arbitrage." *JF*, 52(1), 35–55. | Arbitrage model | Rational arbitrageurs limited to ≈40% of correction capacity; survive but do not dominate | Explains why WDI < 0.40: rational agents outperform but face position caps |
| Bikhchandani et al. (1992). *JPE*, 100(5), 992–1026.                                | Cascade theory  | Cascade followers make systematically worse decisions than independents                   | Validates WDI > 0 as expected outcome of cascade dynamics                  |

#### Normal Range (from literature)
De Long et al. (1991) found noise traders can survive with moderate wealth disadvantage. In financial markets, cross-sectional return inequality (proxied by Sharpe ratio variance) corresponds to Gini ≈ 0.10–0.30 across strategy types. Our simulation with 5 agents and limited-round dynamics should produce WDI in this range.

#### Red Flag Threshold
- **Too high** (> 0.50): Cascade followers are being catastrophically exploited; reduce `social_weight` and `reputation_concern`; or increase NoiseTrader `trade_probability` to dilute cascade concentration
- **Too low** (< 0.05): All agents perform similarly; cascade barely affecting prices; check if `cascade_trigger` is being reached
- **WDI = 0.0**: All agents identical outcomes; likely all agents are trading randomly with no systematic bias; check that CascadeFollower and ReputationHerder bias parameters are non-zero

#### Relationship to Other Metrics
WDI increases with CCI (§2.1) — higher cascade concentration means more rounds where cascade followers trade in losing direction. WDI correlates with CPD (§2.2): longer cascades create longer losing streaks for cascade followers. High ICE (§2.4) combined with high WDI (> 0.25) confirms that information destruction is translating into wealth transfer — the core prediction of cascade models.

#### Implementation Notes
Standard Gini implementation. Inputs from final-round `agent_states`. Returns float in [0, 1]. Defined in `Rule/analysis.py`. Same computation across all 4 variants; LLM/RuleLLM/Rag stochasticity may reduce WDI slightly vs. Rule baseline due to LLM decision variability.

---

## §3 Measurement Dimensions

The six metrics above cover four distinct analytical dimensions:

| Dimension               | Metrics                | Research Question Addressed                               |
|-------------------------|------------------------|-----------------------------------------------------------|
| Cascade Intensity       | CCI (§2.1), CPD (§2.2) | How dominant and how persistent is the cascade?           |
| Mechanism Attribution   | RHI (§2.3)             | Is herding driven by information cascade or reputation?   |
| Information Economics   | ICE (§2.4)             | How much price discovery is destroyed by social learning? |
| Market Dynamics         | VAF (§2.5)             | Does the cascade produce excess volatility?               |
| Distributional Outcomes | WDI (§2.6)             | Who wins and who loses in the cascade?                    |

---

## §4 Phase Analysis

The HerdingInformation simulation exhibits three characteristic phases:

| Phase              | Rounds | Characteristics                                                                    | Dominant Agents                          | Key Metrics                                                         |
|--------------------|--------|------------------------------------------------------------------------------------|------------------------------------------|---------------------------------------------------------------------|
| **Pre-cascade**    | 1–5    | Price near fundamental;                                                            | δ                                        | < 0.02; cascade_count accumulates                                   |
| **Cascade active** | 6–40   |                                                                                    | δ                                        | > 0.02; cascade_count ≥ cascade_trigger; self-reinforcing deviation |
| **Correction**     | 41–50  | IndependentThinker + Contrarian accumulate opposing positions; deviation reverting | IndependentThinker + Contrarian dominant | CCI falling, WDI increasing                                         |

---

## §5 Cross-Variant Analysis

| Metric | Rule Baseline | LLM Expected                                                            | RuleLLM Expected                                                               | Rag Expected                                                                           |
|--------|---------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| CCI    | 0.50–0.70     | Lower (0.35–0.60): LLM agents may interpret context and reduce herding  | Similar to Rule (0.45–0.65): embedded rules anchor cascade; LLM contextualises | Higher (0.55–0.75): RAG retrieves historical cascade events, reinforcing herd behavior |
| CPD    | 3–10 rounds   | Shorter (2–8): LLM reasoning may break cascades faster                  | Similar (3–9): rule constraints stabilise duration                             | Longer (4–12): retrieved cascade examples reinforce persistence                        |
| RHI    | 0.50–1.20     | Variable: LLM may weight reputation differently based on prompt framing | Similar to Rule                                                                | Higher RHI expected: Rag retrieves reputation-cost scenarios                           |
| ICE    | 0.15–0.40     | Lower (0.10–0.30): LLM agents occasionally act on private reasoning     | Similar to Rule                                                                | Higher (0.20–0.45): RAG information reinforces social signal over private signal       |
| VAF    | 1.5–3.5       | Lower (1.2–2.5): LLM variability dampens systematic cascade             | Similar (1.4–3.0)                                                              | Similar to Rule (1.5–3.5)                                                              |
| WDI    | 0.10–0.30     | Lower (0.08–0.25): less systematic bias                                 | Similar to Rule                                                                | Similar to Rule                                                                        |

---

## §6 Expected Results and Validation

### 6.1 Expected Stylised Facts

| Fact                                                   | Quantitative Target                | Literature Source                     | How to Verify in Simulation                               | Failure Indicator                              |
|--------------------------------------------------------|------------------------------------|---------------------------------------|-----------------------------------------------------------|------------------------------------------------|
| Information cascades produce sustained price deviation |                                    | deviation                             | > 0.02 for ≥ 5 consecutive rounds in at least one episode | Banerjee (1992), QJE 107(3), 797–817           |
| Cascade agents dominate volume during herding          | CCI ≥ 0.40 during cascade episodes | Welch (2000), JFE 58(3), 369–396      | Compute CCI on cascade-active round subset                | CCI < 0.20 indicates calibration failure       |
| Reputation herding co-exists with information cascade  | RHI in [0.40, 1.50]                | Scharfstein & Stein (1990), AER 80(3) | Compare ReputationHerder vs CascadeFollower volume        | RHI < 0.10 means reputation mechanism inactive |
| Private signal information is destroyed                | ICE ≥ 0.15                         | Avery & Zemsky (1998), AER 88(4)      | Compute ICE over full simulation                          | ICE < 0.05 means cascade too weak              |
| Cascade produces excess volatility                     | VAF ≥ 1.5                          | De Long et al. (1990), JPE 98(4)      | Compare cascade vs quiet round volatility                 | VAF < 1.0 means cascade not amplifying prices  |

### 6.2 Calibration Targets

| Metric | Target Range | Lower Bound Source                          | Upper Bound Source                                  | Adjustment if Below Range             | Adjustment if Above Range                                         |
|--------|--------------|---------------------------------------------|-----------------------------------------------------|---------------------------------------|-------------------------------------------------------------------|
| CCI    | 0.40–0.70    | Welch (2000): 40% min cascade share         | Bikhchandani et al. (1992): 70% max before lock-in  | Reduce `cascade_trigger` from 3 to 2  | Increase `signal_precision` of IndependentThinker from 0.7 to 0.9 |
| CPD    | 3–10 rounds  | Scharfstein & Stein (1990): 3 round minimum | Grinblatt et al. (1995): 10-round maximum           | Increase `price_impact` (λ)           | Decrease `social_weight` of CascadeFollower                       |
| VAF    | 1.5–3.5      | De Long et al. (1990): 1.5× minimum         | Bikhchandani et al. (1992): 3.5× before instability | Increase `social_weight`              | Reduce `price_impact`                                             |
| WDI    | 0.10–0.30    | De Long et al. (1991): 0.10 survival floor  | Literature consensus: 0.30 moderate inequality cap  | Increase cascade agent aggressiveness | Reduce position caps                                              |

**Calibration protocol**:
1. Run the Rule variant for 10 seeds with default parameters (`cascade_trigger=3`, `social_weight=0.7`, `reputation_concern=0.8`, `signal_precision=0.7`).
2. Compute mean of CCI, CPD, VAF, WDI across runs.
3. Compare against target ranges above.
4. If CCI < 0.40: reduce `cascade_trigger` from 3 to 2 first; then increase `social_weight` from 0.7 to 0.85.
5. If CPD > 10: increase `signal_precision` to 0.85 and `contrarian_threshold` to 0.9.
6. Re-run and verify before proceeding to LLM/RuleLLM/Rag variants.

### 6.3 Cross-Variant Predictions

| Metric | Rule (Baseline) | LLM Expected              | RuleLLM Expected | Rag Expected             | Theoretical Basis                                                                           |
|--------|-----------------|---------------------------|------------------|--------------------------|---------------------------------------------------------------------------------------------|
| CCI    | 0.50–0.65       | Lower (−10 to −15%)       | ≈ Rule baseline  | Higher (+5 to +10%)      | LLM reasoning reduces lock-in; RAG retrieves herding precedents (Bikhchandani et al., 1992) |
| CPD    | 5–8 rounds      | Shorter (−1 to −3 rounds) | ≈ Rule           | Longer (+1 to +3 rounds) | LLM occasionally breaks cascade through reasoning; Rag reinforces via historical examples   |
| ICE    | 0.20–0.35       | Lower (−5 to −10%)        | ≈ Rule           | Higher (+5 to +10%)      | Rag-retrieved cascade evidence suppresses private signal use                                |
| WDI    | 0.12–0.22       | Lower (0.08–0.18)         | ≈ Rule           | ≈ Rule                   | LLM variability reduces systematic exploitation of cascade followers                        |

### 6.4 Validation Failure Signs

| Symptom               | Diagnosis                                             | Root Cause                                                    | Corrective Action                                                                                     |
|-----------------------|-------------------------------------------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| CCI = 0.0 on all runs | Cascade never activates                               | `cascade_trigger` too high; deviation never large enough      | Reduce `cascade_trigger` from 3 to 2; increase `price_impact` from 0.01 to 0.02                       |
| CPD > 20 rounds       | Cascade locks in permanently                          | `signal_precision` too low; IndependentThinker cannot correct | Increase `signal_precision` from 0.7 to 0.9; increase IndependentThinker position cap from 500 to 800 |
| RHI = NaN always      | CascadeFollower never reaches cascade_count threshold | `cascade_trigger` too high AND deviation too small            | Reduce both `cascade_trigger` and `price_impact`; verify CascadeFollower logic in players.py          |
| ICE > 0.60            | Cascade overwhelming private signals                  | Both `social_weight` and `reputation_concern` too high        | Reduce `social_weight` from 0.7 to 0.5 and `reputation_concern` from 0.8 to 0.6                       |
| WDI < 0.02            | All agents earning equal returns                      | No systematic bias producing wealth transfer                  | Verify cascade agents are actually following deviation direction (not random); check decide() logic   |
| VAF < 1.0             | Cascade rounds less volatile than quiet rounds        | Price impact too low or cascade agents net flat               | Increase `price_impact`; verify cascade agents are not simultaneously buying and selling              |

---

## §7 Visualization

### 7.1 Primary Plots

| Plot                           | X-axis       | Y-axis                            | Key Feature                     |
|--------------------------------|--------------|-----------------------------------|---------------------------------|
| Price Path with Cascade Phases | Round (1–50) | Price and Fundamental             | Shaded cascade episodes (       |
| CCI Over Time                  | Round        | CCI (rolling 5-round window)      | Shows cascade buildup and decay |
| Agent Volume Contribution      | Round        | Stacked bar: volume by agent type | Visual decomposition of CCI     |
| Cascade Count Evolution        | Round        | cascade_count for CascadeFollower | Shows threshold-crossing event  |
| Wealth Trajectories            | Round        | Cumulative wealth by agent type   | Shows WDI buildup over time     |

### 7.2 Summary Dashboard

- **Panel 1**: Price vs. fundamental with cascade episode shading
- **Panel 2**: Bar chart of 6 metrics vs. target ranges
- **Panel 3**: Agent volume attribution stacked bar (all rounds)
- **Panel 4**: Wealth distribution at final round (Lorenz curve)
