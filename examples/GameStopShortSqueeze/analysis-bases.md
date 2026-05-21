# GameStopShortSqueeze — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question                                                                                                 | Primary Metric(s) | Expected Finding                                                                           | Failure Indicator                        |
|-----------|-------------------------------------------------------------------------------------------------------------------|-------------------|--------------------------------------------------------------------------------------------|------------------------------------------|
| O1        | Does the three-agent buying coalition (§4.1, §4.2, §4.3) generate an explosive price spike far above fundamental? | SQI, PAR          | Price rises 5–20× fundamental before InstitutionalValue exhausts the squeeze               | Price never exceeds 200% of fundamental  |
| O2        | Which agent contributes most to squeeze magnitude — coordinated retail, short covering, or gamma hedging?         | SQI, AGC          | Three-agent coalition each contributes; short covering cascade is largest single amplifier | One agent contributes >90% of all buying |
| O3        | How quickly does the squeeze collapse after the primary buying force (§4.1) is depleted?                          | SCP, PAR          | Squeeze collapses sharply once RetailCoordinated cash floor is hit                         | Squeeze plateau without collapse         |
| O4        | How does LLM/RAG variant change squeeze magnitude and duration vs. rule baseline?                                 | SQI, SCP          | LLM/RAG produces lower SQI and shorter squeeze                                             | Identical dynamics across variants       |

---

## §2 Core Metrics Catalogue

### Metric: Squeeze Intensity Index (SQI)

#### Category
Price Dynamics / Phenomenon-Specific

#### Definition
The peak price deviation from fundamental during the simulation, measuring the maximum magnitude of the short squeeze price spike. SQI captures the "height" of the squeeze — how far above fundamental the coordinated buying coalition drives the price.

#### Formula
```
SQI = max(dev(t) for all t)

where dev(t) = (P(t) − F) / F
```

**Computation notes**: Single maximum over all rounds. If fundamental = 0, return NaN. In historical GME context, SQI ≈ 24 (P=$483, F≈$20).

**Python function**:
```python
def squeeze_intensity_index(price_history: list, fundamental: float) -> float:
    """Maximum price deviation from fundamental across all rounds.

    Args:
        price_history: List of prices P(t) for t=1..T
        fundamental: Fundamental value F (must be > 0)
    Returns:
        SQI ≥ 0; SQI = 0 means no squeeze occurred; GME analog ≈ 24
    """
```

#### Interpretation

| Range      | Economic Meaning      | Simulation Interpretation                                    |
|------------|-----------------------|--------------------------------------------------------------|
| < 0.5      | No meaningful squeeze | Three-agent coalition failed to coordinate                   |
| [0.5, 2.0) | Mild squeeze          | Partial activation; cover_threshold or buy_pressure too high |
| [2.0, 5.0] | Moderate squeeze      | Consistent with typical short squeeze events                 |
| > 5.0      | Extreme squeeze       | Approaching GameStop-level dynamics                          |

#### Academic Basis

**Primary source**: Lyocsa, S. et al. (2022). "YOLO trading: Riding with the Herd during the GameStop Episode." *Finance Research Letters*, 47, 102785. https://doi.org/10.1016/j.frl.2022.102785

GME peak deviation ≈ 24× fundamental provides the empirical upper bound for SQI in real short squeezes. Typical historical squeezes (VW 2008: ×5; Silver 1980: ×8) suggest SQI of 2–8 is realistic for calibrated runs.

**Supporting studies**:

| Study                                       | Context                 | Finding                                                 | Relevance                                                |
|---------------------------------------------|-------------------------|---------------------------------------------------------|----------------------------------------------------------|
| Brunnermeier & Pedersen (2009). *RFS* 22(6) | VW squeeze 2008         | VW ×5 in 2 days; float exhaustion mechanism             | Sets SQI realistic upper bound ≈ 5–10 for calibrated sim |
| Jones & Lamont (2002). *JFE* 66(2–3)        | US short squeeze events | Typical short squeeze returns 50–200% above fundamental | Sets SQI lower benchmark ≈ 0.5–2.0 for realistic events  |

#### Normal Range (from literature)
SQI of 1.0–5.0 in calibrated simulation; extreme parameterization → SQI ≈ 10–20.

#### Red Flag Threshold
- **Too high** (> 20): λ and buy_pressure combination creates runaway price; reduce both by 50%
- **Too low** (< 0.3): Squeeze never starts; check that cover_threshold and fomo_threshold are reachable
- **= 0**: RetailCoordinated never activates; verify cash > price × 50 condition is met at initialization

#### Relationship to Other Metrics
SQI is the maximum of the deviation time series that PAR tracks as an area. High SQI combined with low SCD (Squeeze Collapse Duration) indicates a sharp spike-and-crash pattern consistent with real short squeezes. SQI and AGC (Agent Contribution) together reveal which agents drove the spike.

---

### Metric: Price-Area Ratio (PAR)

#### Category
Price Dynamics / Duration

#### Definition
The time-integrated area of positive price deviation (deviation > 0) relative to the total simulation length, measuring not just peak squeeze height but also its duration and breadth — how long the squeeze persisted above fundamental.

#### Formula
```
PAR = (1/T) × Σ_{t: dev(t) > 0} dev(t)

where dev(t) = (P(t) − F) / F, T = total rounds
```

**Python function**:
```python
def price_area_ratio(dev_history: list) -> float:
    """Time-averaged positive deviation area.

    Args:
        dev_history: deviation(t) per round
    Returns:
        PAR ≥ 0; units: fraction of fundamental, time-averaged
    """
```

#### Interpretation

| Range      | Economic Meaning          | Simulation Interpretation                                      |
|------------|---------------------------|----------------------------------------------------------------|
| < 0.1      | Brief or mild squeeze     | Squeeze dissipated quickly; InstitutionalValue effective       |
| [0.1, 0.5) | Moderate squeeze duration | Multi-round squeeze with partial correction                    |
| [0.5, 1.5] | Sustained squeeze         | Coalition holds price above fundamental for most of simulation |
| > 1.5      | Prolonged extreme squeeze | Fundamental forces overwhelmed throughout simulation           |

#### Academic Basis

**Primary source**: Jarrow, R.A. & Li, S. (2021). "Short Squeeze Risk." *Annals of Finance*, 17, 635–659.

The duration dimension of a short squeeze is empirically important — GME remained above 200% of fundamental for 5 trading days, creating billions in loss for short sellers. PAR captures this duration-weighted intensity.

#### Normal Range
PAR of 0.2–1.0 expected; historical squeeze analogs suggest sustained overvaluation of 50–200% for 3–10 trading sessions.

#### Red Flag Threshold
- **Too high** (> 2.0): mean_reversion too weak; the squeeze never corrects; increase γ
- **Too low** (< 0.05): Squeeze is instantaneous spike; no real squeeze dynamics; reduce cover_threshold

---

### Metric: Agent Coalition Contribution (ACC)

#### Category
Agent Activity / Attribution

#### Definition
The fraction of total squeeze-phase buying volume (rounds where deviation > 0.5) attributable to each buying agent (§4.1, §4.2, §4.3), measuring the relative contribution of coordinated retail buying, short covering, and gamma hedging to squeeze magnitude.

#### Formula
```
ACC_i = Σ_{t: dev(t) > 0.5} quantity_i(t) / Σ_{t: dev(t) > 0.5} Σ_j quantity_j(t)

where i ∈ {RetailCoordinated, ShortSellerHF, MarketMakerGamma}
and only buy actions counted
```

**Python function**:
```python
def agent_coalition_contribution(agent_volumes: dict, dev_history: list, threshold: float = 0.5) -> dict:
    """Fraction of squeeze-phase buying attributable to each agent.

    Args:
        agent_volumes: {agent_name: [buy_qty_per_round]} for buying agents
        dev_history: deviation(t) per round
        threshold: minimum deviation to define squeeze phase
    Returns:
        Dict {agent_name: fraction in [0, 1]}; fractions sum to 1.0
    """
```

#### Interpretation

| Agent                  | Expected Contribution | Low Signal               | High Signal                                                      |
|------------------------|-----------------------|--------------------------|------------------------------------------------------------------|
| §4.1 RetailCoordinated | 40–60%                | buy_pressure too low     | buy_pressure dominates; gamma/short covering marginal            |
| §4.2 ShortSellerHF     | 20–40%                | cover_threshold too high | Forced covering overwhelms retail — realistic for acute squeezes |
| §4.3 MarketMakerGamma  | 10–30%                | gamma_exposure too low   | Gamma loop dominates — realistic for options-heavy squeezes      |

#### Academic Basis

**Primary source**: Hu, J. et al. (2021). "The Rise of Retail Investor Activism." *Journal of Financial Economics*, 141(3), 1100–1121.

Hu et al. (2021) estimate that options gamma hedging contributed 2–3× amplification to GME move above direct retail buying alone. This implies ACC_§4.3 / ACC_§4.1 ≈ 0.5–1.0, and total coalition ≈ 3× fundamentals-only price movement.

**Supporting studies**:

| Study                                 | Context | Finding                                                   | Relevance                                                   |
|---------------------------------------|---------|-----------------------------------------------------------|-------------------------------------------------------------|
| Lyocsa et al. (2022). *FRL* 47        | GME     | WSB buying ≈ 35–50% of total squeeze volume               | Sets ACC_§4.1 expected range                                |
| Brunnermeier & Pedersen (2009). *RFS* | VW 2008 | Short covering ≈ 60% of squeeze buying (float exhaustion) | Sets ACC_§4.2 upper bound for high short-interest scenarios |

#### Normal Range
ACC_§4.1: 40–60%; ACC_§4.2: 20–40%; ACC_§4.3: 10–30%. Sum = 1.0 by definition.

#### Red Flag Threshold
- **ACC_§4.1 = 1.0**: Gamma and short covering never activated; cover_threshold and fomo_threshold may be too high
- **ACC_§4.2 = 0**: ShortSellerHF never covered; check that cover_threshold is reachable and initial_position < 0
- **ACC_§4.3 = 0**: MarketMakerGamma never activated; check that deviation > 0 condition is met

---

### Metric: Squeeze Collapse Duration (SCD)

#### Category
Price Dynamics / Recovery

#### Definition
The number of rounds from peak deviation to the first round where deviation falls below 20% of peak deviation, measuring how quickly the squeeze collapses after the buying coalition is depleted.

#### Formula
```
SCD = t_collapse − t_peak

where t_peak = argmax(dev(t))
t_collapse = first t > t_peak where dev(t) < 0.2 × dev(t_peak)
```

**Python function**:
```python
def squeeze_collapse_duration(dev_history: list) -> int:
    """Rounds from peak deviation to 80% collapse.

    Args:
        dev_history: deviation(t) per round
    Returns:
        SCD in rounds; SCD = -1 if no peak or collapse not reached
    """
```

#### Interpretation

| Range          | Economic Meaning        | Simulation Interpretation                                        |
|----------------|-------------------------|------------------------------------------------------------------|
| 1–3 rounds     | Sharp crash             | RetailCoordinated cash depleted suddenly; collapse instantaneous |
| [3, 10] rounds | Moderate collapse       | Realistic squeeze unwinding                                      |
| > 10 rounds    | Slow deflation          | mean_reversion γ dominates; no crash                             |
| = −1           | Squeeze never collapsed | Squeeze lasted entire simulation; increase γ                     |

#### Academic Basis

**Primary source**: Brunnermeier, M.K. & Pedersen, L.H. (2009). "Market Liquidity and Funding Liquidity." *Review of Financial Studies*, 22(6), 2201–2238.

The collapse of a short squeeze is typically sharp (funding liquidity crisis): once the margin-call cascade ends, price collapses to fundamental within days. GME collapsed from $483 to $50 in 7 trading days after the Robinhood trading restriction.

#### Normal Range
SCD of 2–8 rounds in calibrated simulation; consistent with 3–10 trading day collapse pattern in historical squeezes.

#### Red Flag Threshold
- **SCD = 1**: Collapse is instantaneous tick; unrealistic; check mean_reversion magnitude
- **SCD = −1**: Squeeze persists indefinitely; mean_reversion too weak for simulation length

---

### Metric: Institutional Exhaustion Point (IEP)

#### Category
Agent Activity / Stabilization Failure

#### Definition
The round at which InstitutionalValue (§4.4) exhausts its position (position = 0 after selling max 1,000 shares), indicating when the only stabilizing agent in the simulation loses its corrective capacity. A low IEP means the squeeze was not resisted for long; a high IEP means InstitutionalValue had supply to sell throughout the simulation.

#### Formula
```
IEP = first t where position_{§4.4}(t) = 0

If §4.4 never exhausts position: IEP = T (total rounds)
```

**Python function**:
```python
def institutional_exhaustion_point(position_history_iv: list) -> int:
    """First round where InstitutionalValue position reaches zero.

    Args:
        position_history_iv: InstitutionalValue position(t) per round
    Returns:
        IEP in [1, T]; T if never exhausted
    """
```

#### Interpretation

| IEP        | Economic Meaning                   | Simulation Interpretation                                          |
|------------|------------------------------------|--------------------------------------------------------------------|
| Round 1–5  | Rapid institutional exhaustion     | Squeeze overwhelms selling instantly                               |
| Round 6–15 | Moderate resistance                | InstitutionalValue sells but cannot stop squeeze                   |
| Round > 15 | Sustained institutional resistance | InstitutionalValue provides meaningful price anchor                |
| IEP = T    | Never exhausted                    | InstitutionalValue position never fully depleted; squeeze was mild |

#### Academic Basis

**Primary source**: Shleifer, A. & Vishny, R.W. (1997). "The Limits of Arbitrage." *Journal of Finance*, 52(1), 35–55.

Limits to arbitrage theory predicts that institutional sellers face capital constraints and position limits. IEP directly measures when InstitutionalValue hits its position limit — the moment when the rational corrective force is entirely neutralized.

#### Normal Range
IEP of 3–10 rounds expected; consistent with InstitutionalValue exhausting 1,000 shares at 100–500 shares per round.

#### Red Flag Threshold
- **IEP = 1**: InstitutionalValue sells entire position in round 1; sell_threshold too low
- **IEP = T**: squeeze never triggers InstitutionalValue; sell_threshold too high for price level

---

### Metric: Wealth Transfer Index (WTI)

#### Category
Portfolio

#### Definition
The net wealth transfer from ShortSellerHF (§4.2) to the buying agents (§4.1, §4.3, §4.5) during the simulation, measuring the redistributive effect of the short squeeze.

#### Formula
```
WTI = −ΔW_{§4.2} / initial_wealth_{all}

ΔW_{§4.2} = W_{§4.2}(T) − W_{§4.2}(0)
```

**Python function**:
```python
def wealth_transfer_index(short_seller_wealth_initial: float, short_seller_wealth_final: float,
                          total_initial_wealth: float) -> float:
    """Fraction of aggregate initial wealth transferred from ShortSellerHF.

    Args:
        short_seller_wealth_initial: §4.2 wealth at round 0
        short_seller_wealth_final: §4.2 wealth at round T
        total_initial_wealth: Sum of all agents' initial wealth
    Returns:
        WTI ≥ 0; higher = more wealth transferred from short seller
    """
```

#### Interpretation

| Range        | Economic Meaning        | Simulation Interpretation              |
|--------------|-------------------------|----------------------------------------|
| < 0.05       | Minor short seller loss | Squeeze mild; cover_threshold too high |
| [0.05, 0.20] | Moderate loss           | Realistic short squeeze loss           |
| [0.20, 0.50] | Severe loss             | Approaching Melvin Capital analog      |
| > 0.50       | Catastrophic loss       | Short seller effectively wiped out     |

#### Normal Range
WTI of 0.10–0.40 expected; Melvin Capital lost ~53% of assets = WTI ≈ 0.35–0.45 normalized to fund size.

#### Red Flag Threshold
- **WTI ≈ 0**: Short seller never covered; cover_threshold too high; check that squeeze reaches cover_threshold
- **WTI > 0.90**: Short seller bankrupt in simulation; check position arithmetic

---

### Metric: API and RAG Quality (AQR)

#### Category
API Quality / RAG Diagnostics

#### Definition
Structural quality of LLM-family decisions and retrieval coverage in the Rag variant. Short-squeeze metrics are meaningful only when accepted decisions are parseable, canonical, and auditable.

#### Formula
```
retrieval_failure_rate = retrieval_failure_rounds / total_rag_rounds
api_contract_issue_rate = malformed_or_retry_exhausted_decisions / total_api_decisions
```

**Python function**:
```python
def analyze_rag_knowledge_effect(rag_contexts: dict[str, dict[int, object]]) -> dict:
    """Calculate retrieval coverage from recorded RAG contexts."""
```

#### Interpretation

| Range | Economic Meaning | Simulation Interpretation |
|---|---|---|
| clean | valid behavioral evidence | preferred state |
| low retry-only issue rate | stochastic API noise recovered by retry | attach quality note |
| any exhausted contract failure | incomplete behavioral sample | repair or rerun before acceptance |

#### Academic Basis

**Primary source**: Project Level-2 quality standard. API outputs must be structurally valid before economic interpretation.

#### Red Flag Threshold
- **Any exhausted parser/provider contract failure**: incomplete run; repair or rerun.
- **Missing `rag_stats.json`**: RAG retrieval behavior is not auditable.

#### Relationship to Other Metrics
AQR gates interpretation of SQI, PAR, ACC, SCD, IEP, and WTI for LLM-family variants.

---

## §3 Analysis Dimensions

### Dimension 1: Squeeze Dynamics

**Purpose**: Track the full price spike trajectory — onset, peak, and collapse.

**Metrics Used**: SQI, PAR, SCD
**Visualization**: Line plot — price vs. fundamental across all rounds; annotations for activation of each buying agent
**Expected Pattern**: Price rises sharply in early rounds (§4.1 initiates, §4.2 and §4.3 join), peaks when §4.1 cash is depleted, then collapses as mean-reversion takes over

### Dimension 2: Coalition Attribution

**Purpose**: Identify which of the three buying agents contributes most to squeeze magnitude.

**Metrics Used**: ACC (§4.1, §4.2, §4.3)
**Visualization**: Stacked area chart of buying volume by agent type over time; ACC pie chart at peak deviation
**Expected Pattern**: §4.1 dominant in early rounds; §4.2 dominant at peak (forced covering cascade); §4.3 provides continuous mechanical buying throughout

### Dimension 3: Institutional Resistance

**Purpose**: Measure how long InstitutionalValue can resist the squeeze before being overwhelmed.

**Metrics Used**: IEP, SQI
**Visualization**: §4.4 position over time; mark IEP on price chart
**Expected Pattern**: IEP occurs in the first third of simulation; after IEP, price accelerates without resistance

### Dimension 4: Wealth Redistribution

**Purpose**: Quantify the wealth transfer from short seller to buyers during the squeeze.

**Metrics Used**: WTI
**Visualization**: Wealth trajectory of each agent over time; bar chart of final wealth

---

## §4 Phase Analysis Framework

| Phase | Name             | Entry Condition                          | Exit Condition         | Key Indicators                                |
|-------|------------------|------------------------------------------|------------------------|-----------------------------------------------|
| 1     | Pre-Squeeze      | Round 1; dev ≈ 0                         | dev > 0.1              | §4.1 initiating buying; price creeping up     |
| 2     | Squeeze Onset    | dev > cover_threshold                    | §4.2 activates         | §4.2 begins covering; ACC_§4.2 rises          |
| 3     | Peak Squeeze     | §4.2 fully covering; §4.1 cash depleting | §4.1 cash ≤ price × 50 | SQI recorded; IEP occurs; §4.3 at maximum     |
| 4     | Squeeze Collapse | §4.1 inactive (cash floor)               | dev < 20% of SQI       | SCD counting; WTI accumulating                |
| 5     | Post-Squeeze     | dev < 0.2                                | End of simulation      | Mean-reversion dominant; volatility declining |

---

## §5 Cross-Variant Comparison Framework

| Axis                     | Measurement | Expected Ordering                         |
|--------------------------|-------------|-------------------------------------------|
| Squeeze magnitude        | SQI         | Rule > RuleLLM ≥ LLM ≈ Rag                |
| Squeeze duration         | PAR         | Rule highest; Rag lowest                  |
| Institutional resistance | IEP         | Similar across variants (rule-based §4.4) |
| Wealth transfer          | WTI         | Rule > LLM > Rag                          |

---

## §6 Expected Results and Validation

### 6.1 Expected Stylised Facts

| Fact                                   | Quantitative Target    | Literature Source                    | How to Verify           | Failure Indicator           |
|----------------------------------------|------------------------|--------------------------------------|-------------------------|-----------------------------|
| Squeeze drives extreme overvaluation   | SQI ≥ 2.0              | Brunnermeier & Pedersen (2009) VW ×5 | Compute SQI on Rule run | SQI < 0.5                   |
| Three-agent coalition each contributes | No single ACC_i > 0.7  | Lyocsa et al. (2022) GME attribution | Compute ACC             | ACC_§4.2 = 0 (never covers) |
| Institutional seller exhausted         | IEP < T/2 (first half) | Shleifer & Vishny (1997)             | Compute IEP             | IEP = T (never exhausted)   |
| Squeeze collapses sharply              | SCD ≤ 8 rounds         | Brunnermeier & Pedersen (2009)       | Compute SCD             | SCD = −1 (never collapses)  |

### 6.2 Calibration Targets

| Metric | Target Range  | Lower Bound Source                    | Upper Bound Source          | Adj if Below                                      | Adj if Above                  |
|--------|---------------|---------------------------------------|-----------------------------|---------------------------------------------------|-------------------------------|
| SQI    | [1.0, 5.0]    | Jones & Lamont (2002) typical squeeze | GME 2021 (+1700%)           | Increase buy_pressure or decrease cover_threshold | Decrease λ                    |
| PAR    | [0.1, 1.0]    | Short squeeze 3–10 day duration       | GME sustained overvaluation | Decrease γ (slower mean-reversion)                | Increase γ                    |
| SCD    | [2, 8] rounds | Sharp collapse pattern                | Slow deflation              | Increase γ                                        | Decrease γ                    |
| WTI    | [0.05, 0.40]  | Typical hedge fund loss               | Melvin Capital −53%         | Lower cover_threshold                             | Reduce initial short position |

**Calibration protocol**: 1. Run Rule variant 10 seeds. 2. Compute SQI, PAR, SCD, ACC, IEP, WTI. 3. Compare against targets. 4. Adjust buy_pressure (highest sensitivity for SQI) and γ (controls SCD). 5. Re-run before LLM/RuleLLM/Rag.

### 6.3 Cross-Variant Predictions

| Metric | Rule    | LLM Expected                                  | RuleLLM Expected | Rag Expected                      | Theoretical Basis                                         |
|--------|---------|-----------------------------------------------|------------------|-----------------------------------|-----------------------------------------------------------|
| SQI    | Highest | Lower (LLM may reason about unsustainability) | Near-Rule        | Lowest (retrieves collapse cases) | RAG retrieves GME and VW collapse patterns                |
| PAR    | Highest | Moderate                                      | Near-Rule        | Lowest                            | LLM may reduce buy_pressure when overvaluation is extreme |
| WTI    | Highest | Moderate                                      | Near-Rule        | Lowest                            | Short seller loss reflects squeeze magnitude              |

### 6.4 Validation Failure Signs

| Symptom      | Diagnosis                          | Root Cause                                          | Corrective Action                                  |
|--------------|------------------------------------|-----------------------------------------------------|----------------------------------------------------|
| SQI = 0      | Squeeze never starts               | buy_pressure too low or cover_threshold too high    | Lower cover_threshold; increase buy_pressure       |
| ACC_§4.2 = 0 | ShortSellerHF never covers         | initial_position ≥ 0 or cover_threshold unreachable | Set initial_position = −1000; lower cover_threshold |
| ACC_§4.3 = 0 | MarketMakerGamma inactive          | gamma_exposure = 0 or deviation never > 0           | Set gamma_exposure > 0; verify squeeze starts      |
| IEP = T      | InstitutionalValue never exhausted | sell_threshold too high                             | Lower sell_threshold to 0.30                       |
| SCD = −1     | Squeeze never collapses            | γ too small; simulation too short                   | Increase γ or lengthen simulation                  |

---

## §7 Visualization Catalogue

| Plot Name                | Type         | X-axis  | Y-axis              | Overlays                      | Purpose                                |
|--------------------------|--------------|---------|---------------------|-------------------------------|----------------------------------------|
| squeeze_price_trajectory | Line         | Round   | Price + Fundamental | Phase annotations; IEP marker | Shows full squeeze lifecycle           |
| coalition_volume_stacked | Stacked area | Round   | Buy volume          | By agent (§4.1, §4.2, §4.3)   | Shows relative contribution to squeeze |
| short_cover_position     | Line         | Round   | §4.2 position       | cover_threshold line          | Shows forced covering cascade          |
| institutional_position   | Line         | Round   | §4.4 position       | IEP annotation                | Shows when rational resistance fails   |
| wealth_trajectories      | Line         | Round   | Wealth              | By agent                      | Shows WTI accumulation                 |
| acc_pie                  | Pie          | —       | ACC fractions       | Agent labels                  | Coalition attribution summary          |
| cross_variant_sqi        | Bar          | Variant | SQI                 | GME analog reference          | Research comparison                    |
| rag_stats.json           | JSON         | Agent/Round | Retrieval coverage | no-context marker counts      | RAG retrieval quality audit            |
