# BlackMonday1987 — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                                                                 | Metric(s)                                                  | Expected Finding                                                               |
|-----------|---------------------------------------------------------------------------------------------------|------------------------------------------------------------|--------------------------------------------------------------------------------|
| O1        | Does portfolio insurance + program trading produce a measurable crash cascade?                    | Price deviation, max drawdown                              | Deviation < −20% sustained for ≥5 rounds; drawdown > 15%                       |
| O2        | How fast does the feedback loop amplify the initial decline?                                      | Crash onset round, crash velocity                          | Crash onset within rounds 5–15; peak within rounds 20–30                       |
| O3        | Do portfolio insurers and program traders dominate sell-side volume?                              | Agent-type volume, sell contribution ratio                 | PortfolioInsurer + ProgramTrader > 60% of total sell volume during cascade     |
| O4        | Does ValueInvestor provide a measurable price floor?                                              | Min price, floor activation round, net demand during floor | Price stabilization visible; ValueInvestor buying > 40% of cascade peak sell   |
| O5        | Does the feedback loop show positive autocorrelation during cascade and negative during recovery? | Return autocorrelation, rolling AC1                        | AC1 > 0.3 during cascade; AC1 < 0 post-peak                                    |
| O6        | How does cross-variant crash timing and depth compare?                                            | All core metrics by variant                                | Rule most deterministic; LLM may delay onset; Rag modifies with 1987 knowledge |


## 2. Core Metrics Catalogue

### Metric 1: Price Deviation from Fundamental

- **Category**: Price Dynamics / Phenomenon Core
- **Definition**: Percentage difference between market price and fundamental value at each round
- **Formula**: deviation(t) = (P(t) − F) / F × 100 where F = 100.0

**Derivation Rationale**: In a constant-fundamental simulation (F = 100.0 throughout), all price movements are pure endogenous cascade dynamics. Deviation directly measures how far the feedback loop has driven prices from fair value, independent of any fundamental news. This is the most direct quantitative test of the cascade mechanism. The choice of percentage (rather than absolute) deviation follows Shiller (2000)'s price-to-fundamentals ratio framework, making the metric scale-independent and comparable across simulations.

**Academic Calibration Source**: Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. Historical analysis of equity price deviations; calibration reference: 1987 Black Monday peak deviation = −22.6% on the Dow Jones Industrial Average. Brady Commission (1988) documents S&P 500 deviation of −20.5% on October 19.

- **Interpretation**:
    - 0%: Price at fundamental fair value
    - −5% to −10%: Feedback onset zone — portfolio insurance and initial program triggers active
    - −10% to −20%: Cascade escalation zone — program trading amplification dominant
    - Below −20%: Crash zone — consistent with 1987 Black Monday historical event; value investor floor activated
    - Above +5%: Recovery overshoot — mean reversion pulling back
- **Normal Range**: −5% to +5% in equilibrium; −15% to −35% during 1987-style cascade event
- **Red Flag**: Deviation never reaches −5% → automated strategies not triggering; verify rebalance_threshold and trigger_threshold configuration. Deviation stays above −10% → cascade not self-reinforcing; increase feedback_strength or reduce initial_price.

---

### Metric 2: Maximum Drawdown

- **Category**: Price Dynamics / Risk
- **Definition**: Largest peak-to-trough price decline as a percentage across the full simulation
- **Formula**: max_drawdown = max_{t1 < t2} [(P(t1) − P(t2)) / P(t1)] × 100

**Derivation Rationale**: Maximum drawdown is the canonical risk metric for crash severity — it captures the worst-case loss experienced by a fully invested agent from any peak to any subsequent trough. For the 1987 event, the single-session nature means the peak-to-trough decline occurred within one day. In the simulation, max drawdown measures whether the portfolio insurance + program trading feedback loop generates a Black Monday-sized event (target: 15–35%). Chekhlov et al. (2005) establish max drawdown as the theoretically preferred risk measure for strategies with heavy tail exposure.

**Academic Calibration Source**: Chekhlov, A., Uryasev, S., & Zabarankin, M. (2005). "Drawdown measure in portfolio optimization." *International Journal of Theoretical and Applied Finance*, 8(1), 13–58. DOI: 10.1142/S0219024905002767. Calibration target: historical Black Monday drawdown = 22.6% (DJIA), 20.5% (S&P 500). Simulation target range: 15%–35%.

- **Interpretation**:
    - < 5%: Cascade too weak — feedback loop not generating sufficient selling
    - 5%–15%: Moderate decline — consistent with pre-crash week (October 14–16) but not October 19 itself
    - 15%–25%: Target zone — consistent with 1987 Black Monday event
    - > 25%: Severe crash — exceeds historical precedent; verify no parameter miscalibration
- **Normal Range**: 15%–35% for this simulation calibration
- **Red Flag**: Drawdown < 10% → verify feedback_strength ≥ 0.3 and trigger_threshold ≤ 0.01. Drawdown > 40% → cascade is over-calibrated; verify initial_price is not too high relative to fundamental.

---

### Metric 3: Crash Velocity (Peak Decline Rate)

- **Category**: Phenomenon-Specific / Cascade Dynamics
- **Definition**: Maximum per-round rate of price decline during the crash phase; measures how explosive the feedback amplification is
- **Formula**: max_velocity = max_{t} |deviation(t) − deviation(t−1)| during crash phase (deviation < −0.05)

**Derivation Rationale**: The 1987 crash was remarkable not only for its depth but for its speed — 22.6% in a single trading day. Crash velocity captures the time-compression feature that distinguishes automated feedback crashes from normal bear markets. High velocity (>3% per round) indicates the feedback loop is operating as a self-reinforcing cascade; low velocity suggests the cascade is too gradual relative to the 1987 historical benchmark. Brady Commission (1988) documents the most intensive selling occurring in discrete 30-minute windows — each window corresponding to a simulation "round" in terms of its cascade dynamics.

**Academic Calibration Source**: Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. Intraday analysis shows the Dow fell at rates of 5–8% per 30-minute interval at peak cascade intensity. Calibration target: max_velocity ≥ 2% per round during cascade escalation.

- **Interpretation**:
    - < 0.5% per round: Cascade too slow; individual feedback rounds insufficient to replicate 1987 single-session dynamics
    - 0.5%–2%: Moderate velocity — multi-session crash dynamic; realistic but not Black Monday-like
    - 2%–5%: Target zone — consistent with intraday Black Monday dynamics
    - > 5%: Very fast cascade; verify noise_std not set too high which could create artificially volatile swings
- **Normal Range**: 1%–5% per round at peak cascade
- **Red Flag**: Max velocity < 0.5% → feedback_strength too low or base_sell quantity too small; increase to match Brady Commission order flow estimates.

---

### Metric 4: Return Autocorrelation (Momentum Persistence)

- **Category**: Behavioral / Feedback Loop Characterization
- **Definition**: Lag-1 autocorrelation of per-round price returns; captures whether the market is in a momentum (self-reinforcing) or mean-reversion regime
- **Formula**: AC1 = Corr(r(t), r(t−1)) where r(t) = [P(t) − P(t−1)] / P(t−1)

**Derivation Rationale**: Positive autocorrelation (AC1 > 0) is the statistical fingerprint of the feedback loop mechanism: negative returns beget further negative returns, consistent with the portfolio insurance and program trading cascade. Negative autocorrelation (AC1 < 0) indicates the mean-reversion and ValueInvestor effects are dominant — the crash has bottomed and recovery is underway. Lo & MacKinlay (1988) establish that high-frequency return autocorrelation is the canonical test for momentum versus mean-reversion, and their methodology is directly applied here to the simulation's discrete rounds.

**Academic Calibration Source**: Lo, A. W., & MacKinlay, A. C. (1988). "Stock market prices do not follow random walks: Evidence from a simple specification test." *Review of Financial Studies*, 1(1), 41–66. DOI: 10.1093/rfs/1.1.41. Historical Black Monday AC1 during crash phase: estimated 0.40–0.65 from intraday price sequence analysis.

- **Interpretation**:
    - AC1 > 0.3: Strong positive feedback — cascade self-reinforcing; simulation correctly captures 1987 momentum
    - AC1 ≈ 0: Random walk regime — cascade absent or mixed with sufficient noise
    - AC1 < 0: Mean-reverting — ValueInvestor and γ-mean-reversion dominant; recovery phase
- **Normal Range**: AC1 = 0.3–0.6 during cascade phase; AC1 = −0.2 to −0.1 during recovery
- **Red Flag**: AC1 ≈ 0 throughout → no feedback loop active; significantly increase feedback_strength. AC1 negative even during crash phase → mean_reversion (γ) too high, overcorrecting against cascade.

---

### Metric 5: Agent-Type Sell Volume Contribution

- **Category**: Volume / Activity / Attribution
- **Definition**: Fraction of total sell volume attributable to each agent type; measures which agents dominate the cascade versus which absorb supply
- **Formula**: sell_fraction_type = Σ_{t=onset}^{peak} Σ_{i ∈ type} max(0, −quantity_i(t)) / Σ_{t=onset}^{peak} Σ_i max(0, −quantity_i(t))

**Derivation Rationale**: The Brady Commission's central empirical finding was that portfolio insurance and program trading together accounted for a disproportionate share of sell-side volume on October 19 — despite being only 2 of many market participants. Replicating this volume concentration validates that the simulation correctly captures the cascade mechanism at the agent level, not just in aggregate price dynamics. Volume attribution is the primary micro-validation test for the multi-agent structure.

**Academic Calibration Source**: Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. Documented that portfolio insurance accounted for ~25–30% of NYSE institutional sell volume; program trading contributed an additional ~15–20%; combined ≥ 40–50% of total sell volume during peak cascade hours. Combined target: PortfolioInsurer + ProgramTrader ≥ 50% of total cascade-phase sell volume.

- **Interpretation**:
    - PortfolioInsurer + ProgramTrader ≥ 50%: Cascade mechanism correctly concentrated in automated strategies
    - ValueInvestor > 0% during crash phase: Floor mechanism active — critical for realistic price recovery
    - NoiseTrader > 30% of sell volume: Noise is dominating simulation; reduce noise_std or increase agent position sizes
- **Normal Range**: PortfolioInsurer: 25–40%; ProgramTrader: 20–35%; IndexArbitrageur: 5–15%; ValueInvestor (buy-side): 15–25% of total buy volume during crash; NoiseTrader: 5–10% of total volume
- **Red Flag**: ValueInvestor volume = 0 → floor mechanism not activating; check value_discount configuration. PortfolioInsurer volume < 15% → hedge_ratio too low or rebalance_threshold too high.

---

### Metric 6: Crash Onset Round

- **Category**: Phenomenon-Specific / Timing
- **Definition**: The simulation round in which the cascade crosses the −5% deviation threshold for the first time; measures how quickly automated strategies respond to the initial price weakness
- **Formula**: t_onset = min{t : deviation(t) < −0.05}

**Derivation Rationale**: On October 19, 1987, the most intense cascade selling began within the first 30–90 minutes of trading (consistent with the first 5–15 simulation rounds at round ≈ 10–20 minutes each). A very early onset (round 1–4) suggests the simulation begins in an already-unstable regime; a very late onset (round > 30) suggests the initial conditions are too stable to generate the crash reliably. The onset round also serves as the reference point for all phase-transition metrics.

**Academic Calibration Source**: Calibrated from Brady Commission (1988) intraday timeline analysis and Shiller (1987) survey. Target range: rounds 5–20 of a typical 100-round simulation.

- **Interpretation**:
    - t_onset ≤ 5: Too fast — initial conditions predispose immediate crash; consider raising initial stability
    - t_onset = 5–20: Target range — consistent with October 19 timeline where crash accelerated mid-morning
    - t_onset > 30: Too slow — cascade not triggering reliably; reduce trigger_threshold or increase initial_position for automated agents
- **Normal Range**: Rounds 5–20 for typical 100-round simulation
- **Red Flag**: t_onset never reached → check noise term is generating initial price movements that break through rebalance_threshold; consider starting simulation with a small initial trigger shock.

---

### Metric 7: ValueInvestor Floor Activation and Absorption Ratio

- **Category**: Phenomenon-Specific / Stabilization
- **Definition**: Measures whether and when the ValueInvestor activates, and the fraction of cascade selling it absorbs during the floor formation phase
- **Formula**: 
  - activation_round = min{t : deviation(t) < −0.15}
  - absorption_ratio = Σ_{t=activation_round}^{peak} Q_ValueInvestor_buy(t) / Σ_{t=activation_round}^{peak} Q_cascade_sell(t)
  where Q_cascade_sell = sum of PortfolioInsurer + ProgramTrader sells

**Derivation Rationale**: Graham's margin of safety principle (value_discount = 0.15) defines when the floor mechanism activates. The absorption ratio measures how effectively a single large value buyer can counteract the combined cascade selling — testing the Shleifer & Vishny (1997) limits-of-arbitrage prediction that a single stabilizing buyer cannot fully arrest a cascade driven by many automated sellers. A low absorption ratio (< 30%) confirms the limits-of-arbitrage result; a high ratio (> 80%) would suggest over-parameterization of ValueInvestor relative to cascade agents.

**Academic Calibration Source**: Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35–55. DOI: 10.2307/2329555. Expected: absorption_ratio = 20%–50% during peak cascade phase (consistent with partial but incomplete stabilization). Graham, B. (1949). *The Intelligent Investor*. value_discount = 0.15 calibrated to Graham's standard margin of safety.

- **Interpretation**:
    - absorption_ratio < 20%: ValueInvestor provides negligible floor — cascade is overwhelmingly dominant; crash likely to undershoot
    - absorption_ratio = 20%–50%: Target zone — partial floor consistent with limits-of-arbitrage theory
    - absorption_ratio > 60%: ValueInvestor over-sized relative to cascade agents; floor too strong; reduce order_size
- **Normal Range**: activation_round between t_onset+10 and t_onset+20; absorption_ratio = 20%–50%
- **Red Flag**: ValueInvestor never activates (absorption_ratio = 0) → deviation never crosses −15%; cascade too mild; verify feedback_strength and hedge_ratio are calibrated correctly.


## 3. Analysis Dimensions

### Dimension 1: Price Crash Dynamics

**Purpose**: Verify that the portfolio insurance + program trading feedback produces a measurable, Black Monday-calibrated crash cascade
**Metrics Used**: Price deviation (Metric 1), max drawdown (Metric 2), crash velocity (Metric 3)
**Visualization**: Price vs. fundamental line chart with crash threshold overlays at −10%, −15%, −20%; rolling per-round price change rate
**Expected Pattern**: Sharp price decline below fundamental; cascade deepens with each feedback round (velocity > 2% per round at peak); partial recovery after ValueInvestor activates; total drawdown in 15–35% range
**Comparison Baseline**: Rule variant as deterministic reference; 1987 historical data as external benchmark

### Dimension 2: Feedback Loop Attribution

**Purpose**: Confirm that PortfolioInsurer and ProgramTrader generate the dominant selling pressure during cascade, consistent with Brady Commission empirical findings
**Metrics Used**: Agent-type volume (Metric 5), crash onset round (Metric 6)
**Visualization**: Stacked bar chart of cumulative sell volume by agent type; per-round sell volume time series for each agent; bar chart comparing cascade-phase vs. recovery-phase volume distribution
**Expected Pattern**: PortfolioInsurer + ProgramTrader ≥ 50% of total cascade-phase sell volume; ProgramTrader volume increases convexly with |deviation| (reflecting amplification formula); IndexArbitrageur adds supplementary sell pressure

### Dimension 3: Feedback Loop Intensity and Lifecycle

**Purpose**: Measure cascade self-reinforcement through autocorrelation and velocity analysis; track the full feedback lifecycle from initiation through peak to recovery
**Metrics Used**: Return autocorrelation (Metric 4), crash velocity (Metric 3), price deviation phase trajectory
**Visualization**: Three-panel layout — (a) deviation over time with phase markers; (b) rolling 10-round return autocorrelation; (c) per-round sell volume by agent type
**Expected Pattern**: Strong positive autocorrelation (AC1 > 0.3) during cascade phase (rounds t_onset to t_peak); shift to negative autocorrelation post-peak (ValueInvestor + mean reversion dominant); velocity peaks at t_peak

### Dimension 4: ValueInvestor Floor Effectiveness

**Purpose**: Quantify how effectively a single large value buyer arrests the cascade; test the limits-of-arbitrage prediction
**Metrics Used**: ValueInvestor floor activation (Metric 7), net demand decomposition during floor phase
**Visualization**: Net demand time series decomposed by agent type; cumulative buy/sell balance from ValueInvestor vs. cascade agents; scatter plot of absorption_ratio vs. cascade depth across multiple runs
**Expected Pattern**: ValueInvestor activates at deviation ≈ −15%; absorption_ratio = 20%–50%; price decline slows but does not immediately reverse; eventual floor forms between −15% and −30% depending on cascade magnitude

### Dimension 5: Cross-Variant Comparison

**Purpose**: Compare crash dynamics across Rule, LLM, RuleLLM, Rag variants; quantify behavioral differences induced by variant type
**Metrics Used**: All core metrics (1–7) compared across variants
**Visualization**: Side-by-side price deviation curves for all 4 variants; bar chart of max_drawdown mean ± std across 10 runs per variant; table of t_onset, t_peak, and absorption_ratio by variant
**Expected Pattern**: Rule variant most deterministic (lowest std across runs); LLM introduces psychological delay or amplification depending on persona interpretation; RuleLLM near-Rule but with ±20% variance; Rag variant potentially shows altered PortfolioInsurer behavior due to 1987 historical knowledge


## 4. Phase Analysis Framework

### Phase Detection Rules

| Phase | Name                | Entry Condition                  | Exit Condition                             | Key Indicators                                                                           | Typical Round Range |
|-------|---------------------|----------------------------------|--------------------------------------------|------------------------------------------------------------------------------------------|---------------------|
| 1     | Pre-Crash Stability | Round 1                          | deviation(t) < −0.05                       | Price fluctuating near fundamental; automated strategies inactive (                      | deviation           |
| 2     | Feedback Onset      | deviation(t) < −0.05             | deviation(t) < −0.10                       | PortfolioInsurer first activates; initial selling cascade; AC1 turning positive          | Rounds 10–25        |
| 3     | Cascade Escalation  | deviation(t) < −0.10             | deviation(t) reaches minimum               | ProgramTrader amplification active; all automated sellers contributing; volume spike     | Rounds 20–40        |
| 4     | Crash Peak          | deviation(t) = minimum           | deviation(t) rising ≥ 2 consecutive rounds | Maximum drawdown achieved; ValueInvestor absorbing at capacity; net demand near zero     | Rounds 35–50        |
| 5     | Recovery            | deviation(t) rising from minimum | deviation(t) > −0.05                       | Mean reversion + ValueInvestor dominant; automated sellers largely inactive or reversing | Rounds 45–80        |

### Quantitative Phase Criteria

**Phase 1 → Phase 2 Transition**: Triggered when noise or initial selling pushes deviation below −0.05. Diagnostic: is PortfolioInsurer selling at this round? If yes, cascade has begun.

**Phase 2 → Phase 3 Transition**: Deviation crosses −0.10, activating ProgramTrader's higher-amplitude tiers. Diagnostic: ProgramTrader volume should increase by ≥ 50% relative to Phase 2.

**Phase 3 → Phase 4 Transition**: Rate of deviation change (velocity) peaks and begins declining. Diagnostic: per-round deviation change turns from increasingly negative to less negative.

**Phase 4 → Phase 5 Transition**: ValueInvestor absorption ratio > 50% AND deviation turning positive for 2 consecutive rounds. Diagnostic: net_demand turns positive; AC1 turns negative.

### Observable Signatures by Phase

| Phase              | PortfolioInsurer             | ProgramTrader            | IndexArbitrageur | ValueInvestor   | AC1          |
|--------------------|------------------------------|--------------------------|------------------|-----------------|--------------|
| Pre-Crash          | Inactive                     | Inactive                 | Inactive         | Inactive        | ≈ 0          |
| Feedback Onset     | Active (small sells)         | Inactive or minimal      | Active (sells)   | Inactive        | +0.1 to +0.3 |
| Cascade Escalation | Active (growing sells)       | Active (amplified sells) | Active (sells)   | Inactive        | +0.3 to +0.6 |
| Crash Peak         | Constrained (position limit) | Large sells              | Mixed            | Active (buying) | +0.1 to +0.3 |
| Recovery           | Inactive or buying           | Inactive                 | Buying           | Active (buying) | −0.2 to 0    |


## 5. Cross-Variant Comparison Framework

### Comparison Protocol

1. **Normalize**: Compare all variants using same fundamental value (100.0) and same initial price; ensures deviations are directly comparable.
2. **Statistical test**: Compare max_drawdown, t_onset, and absorption_ratio across variants using mean ± std over 10 simulation runs per variant.
3. **Key comparison axes**:
   - **Cascade initiation speed**: Rule vs. LLM vs. RuleLLM vs. Rag — which variant triggers earliest?
   - **Crash depth**: Peak deviation magnitude — does LLM persona faithfully replicate mechanical selling or show discretionary restraint?
   - **Feedback loop strength**: Return autocorrelation — Rule should show highest AC1; LLM variants lower if personas introduce deliberation
   - **Rag modification**: Does 1987 historical knowledge in RAG context change PortfolioInsurer or ProgramTrader behavior? Expected: Rag variant may show earlier or deeper crash if agents "recall" the 1987 dynamics.
4. **Reporting format**: Table with mean ± std for each metric across all 4 variants; t-test for Rule vs. LLM significance

### Expected Cross-Variant Behavioral Differences

| Behavioral Dimension        | Rule                                                  | LLM                                                                                                   | RuleLLM                           | Rag                                                                                           |
|-----------------------------|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------|-----------------------------------|-----------------------------------------------------------------------------------------------|
| PortfolioInsurer selling    | Mechanical; every threshold crossing                  | May deliberate or explain before selling; possible 1–3 round delay                                    | Formula-anchored; near-mechanical | Modified by historical Black Monday context; may sell faster or more conservatively           |
| ProgramTrader amplification | Exact formula; deterministic                          | May interpret "amplify sells" differently per LLM call                                                | Near-formula; ±20%                | May recall that program trading was identified as a crash cause and self-modify               |
| ValueInvestor activation    | Exact at deviation < −0.15                            | May activate earlier ("the crash is clearly underway") or later ("conditions not extreme enough yet") | Near-exact threshold              | May recall Buffett's 1987 buying behavior and activate earlier                                |
| NoiseTrader                 | Purely stochastic (5% probability, uniform direction) | Varied language outputs creating different action distributions                                       | Constrained stochastic            | Potentially biased toward panic behavior if RAG context includes retail investor descriptions |


## 6. Expected Results and Validation

### Expected Stylized Facts (Literature-Sourced)

| Stylized Fact                                  | Target Value   | Literature Source                                | DOI                   |
|------------------------------------------------|----------------|--------------------------------------------------|-----------------------|
| Maximum price deviation (crash depth)          | −15% to −35%   | Brady Commission (1988); 1987 historical: −22.6% | — (government report) |
| Crash onset speed                              | Rounds 5–20    | Brady Commission (1988) intraday timeline        | —                     |
| Return autocorrelation during cascade          | AC1 ≥ 0.30     | Lo & MacKinlay (1988)                            | 10.1093/rfs/1.1.41    |
| PortfolioInsurer + ProgramTrader sell fraction | ≥ 50%          | Brady Commission (1988) volume attribution       | —                     |
| ValueInvestor absorption ratio                 | 20%–50%        | Shleifer & Vishny (1997)                         | 10.2307/2329555       |
| Crash velocity at peak                         | ≥ 2% per round | Brady Commission (1988) 30-minute interval data  | —                     |

### Sensitivity Discussion

- **Increasing λ (price impact)**: Faster crash onset, deeper trough, higher velocity. Most sensitive parameter for crash depth. Brady Commission estimated λ implicitly from order flow and price movement data.
- **Increasing feedback_strength**: More convex amplification by ProgramTrader; sharper Phase 2→3 transition; higher velocity at peak. Brunnermeier & Pedersen (2009) calibrate feedback_strength at 0.25–0.40 for liquidity spirals.
- **Decreasing value_discount**: Earlier ValueInvestor activation; higher absorption ratio; shallower crash floor. Graham's original margin of safety of 20–33% suggests value_discount = 0.15 is already conservative.
- **Reducing γ (mean reversion)**: Slower recovery; lower recovery autocorrelation (AC1 stays positive longer). Poterba & Summers (1988) estimate γ ≈ 0.01–0.03 for equity markets.

### Validation Failure Diagnostics

| Failure Mode                         | Symptom                                        | Likely Cause                                        | Corrective Action                                                                          |
|--------------------------------------|------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------------------------------------------|
| Cascade absent                       | Deviation never < −5%                          | rebalance_threshold too high or hedge_ratio too low | Reduce rebalance_threshold to 0.01; verify PortfolioInsurer position = 3000                |
| Cascade too shallow                  | Max drawdown < 10%                             | feedback_strength too low; λ too low                | Increase feedback_strength to 0.4; increase λ to 0.003                                     |
| Recovery too fast                    | Deviation returns to 0 within 5 rounds of peak | γ too high (> 0.05)                                 | Reduce γ to 0.01–0.02                                                                      |
| ValueInvestor never activates        | Absorption ratio = 0                           | value_discount too high; crash doesn't reach −15%   | Verify cascade agents generate sufficient selling; reduce value_discount to 0.12 if needed |
| ProgramTrader dominates from round 1 | t_onset = 1; immediate crash                   | trigger_threshold too low                           | Increase trigger_threshold to 0.02; ensure initial price starts at 100.0                   |


## 7. Visualization Catalogue

| Plot Name                         | Type         | X-axis     | Y-axis                     | Overlays / Annotations                           | Purpose                                                        |
|-----------------------------------|--------------|------------|----------------------------|--------------------------------------------------|----------------------------------------------------------------|
| Price vs. Fundamental             | Line         | Rounds     | Price                      | Fundamental dashed; −10%, −20% threshold lines   | Primary crash dynamics; shows cascade depth and floor          |
| Price Deviation Time Series       | Line         | Rounds     | Deviation (%)              | Phase markers; −5%, −10%, −15%, −20% thresholds  | Cascade phase identification; quantitative crash measure       |
| Per-Round Price Returns           | Bar/Line     | Rounds     | Return (%)                 | Zero line; crash onset marker                    | Identifies velocity peaks; autocorrelation visualization       |
| Return Distribution               | Histogram    | Return (%) | Frequency                  | Normal distribution overlay                      | Documents fat-tail crash returns vs. equilibrium               |
| Rolling Return Autocorrelation    | Line         | Rounds     | AC1 (10-round rolling)     | Zero line; +0.3 threshold line                   | Shows feedback loop intensity over time; Phase 2→4 marker      |
| Agent Sell Volume by Type         | Stacked Bar  | Agent type | Total sell volume          | Brady Commission 50% benchmark line              | Volume attribution test; validates cascade concentration       |
| Per-Round Sell Volume Time Series | Line         | Rounds     | Sell volume                | Separate line per agent type; t_onset marker     | Shows cascade escalation dynamics; ProgramTrader amplification |
| Net Demand Decomposition          | Area         | Rounds     | Net demand (buy−sell)      | Zero line; colored by contributor                | Tests ValueInvestor floor absorption; cascade vs. recovery     |
| ValueInvestor Activation          | Line+Scatter | Rounds     | Cumulative buy volume      | t_activation marker; absorption_ratio annotation | Floor mechanism effectiveness; limits-of-arbitrage test        |
| Cross-Variant Price Comparison    | Line         | Rounds     | Deviation (%)              | One line per variant; Rule as reference baseline | Quantifies behavioral differences across Rule/LLM/RuleLLM/Rag  |
| Rule Adherence (RuleLLM)          | Bar          | Agent      | Adherence rate (%)         | 80% target threshold                             | Validates quantitative rule anchoring in RuleLLM variant       |
| RAG Retrieval Rate (Rag)          | Bar          | Agent      | Retrieval success rate (%) | 50% minimum threshold                            | Measures 1987 historical context retrieval effectiveness       |
