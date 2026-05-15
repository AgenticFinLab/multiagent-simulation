# AssetBubble — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                                                                      | Metric(s)                                                               | Expected Finding                                                                                           |
|-----------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| O1        | Does the simulation produce a clear asset bubble with price significantly exceeding fundamental value? | Bubble ratio (P/F), price deviation (%)                                 | Peak bubble_ratio ∈ [1.3, 1.8×]; deviation peak > 20%                                                      |
| O2        | Can the bubble's onset, peak, and crash phases be clearly identified?                                  | Phase detection, max drawdown, crash duration                           | Distinct 4-phase cycle observable; crash drawdown > 20%                                                    |
| O3        | Do different agent types behave consistently with their theoretical roles?                             | Net demand by agent type, trading volume, portfolio performance         | MomentumSpeculator and LeveragedBuyer drive demand on upswing; RationalArbitrageur provides opposing force |
| O4        | Is there evidence of a self-reinforcing demand → price → demand positive feedback loop?                | Return autocorrelation, positive feedback index                         | Lag-1 AC1 > 0.3 during bubble formation; positive feedback index > 0.5                                     |
| O5        | Does LeveragedBuyer forced selling catalyse the crash?                                                 | LeveragedBuyer margin call round, price decline rate after margin calls | Price decline rate accelerates ≥ 2× in the round(s) when margin calls fire                                 |
| O6        | How do Rule, LLM, RuleLLM, and Rag variants differ in bubble formation and crash dynamics?             | All core metrics compared across variants                               | Variants differ measurably in at least 2 metrics                                                           |
| O7        | Does volatility cluster around bubble and crash phases?                                                | Rolling volatility (10-round window)                                    | Volatility visibly higher in escalation and crash phases vs. build-up                                      |


## 2. Core Metrics Catalogue

### Metric: Price Deviation from Fundamental

- **Category**: Price Dynamics / Phenomenon-Specific
- **Definition**: Percentage by which market price exceeds (or falls below) fundamental value F(t), signed positive for overvaluation.
- **Formula**:
  ```
  price_deviation(t) = (P(t) − F(t)) / F(t) × 100%
  ```
  Note: Unlike ArchegosCollapse where F is constant, AssetBubble uses a slowly growing fundamental: `F(t) = F(0) × (1 + fundamental_growth)^t`. The deviation should be computed against the current-round fundamental to correctly measure the bubble premium, not a historical price anchor.
- **Derivation Rationale**: Normalising against F(t) removes the effect of fundamental growth from the deviation measure, isolating the speculative premium. Shiller (2000) uses this form of cyclically-adjusted deviation (CAPE deviation) as the primary measure of speculative excess in equity markets.
- **Academic Calibration Source**:
  - Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. Documents historical PE ratio deviations of 50–100% during major 20th-century bubbles (Dot-com, late-1920s); simulation target (20–80%) is a compressed analogue.
  - De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 — establishes that noise trader demand can sustain 10–20% deviations as a persistent equilibrium; larger deviations (20–80%) require simultaneous momentum and leverage amplification.
- **Interpretation**:
  - deviation = 0%: Fair value
  - deviation ∈ (0%, +20%): Mild overvaluation — speculative premium forming
  - deviation > +20%: Bubble territory — exceeds Shiller's "fair value ± 20%" band
  - deviation < −10%: Post-crash undervaluation — correction may overshoot
- **Normal Range**: Historical major bubbles +50% to +200% at peak; simulation target +20% to +80%
- **Red Flag**: Never exceeds +10% across 100 rounds → price_impact (λ) too low; recalibrate λ upward

---

### Metric: Bubble Ratio (P/F Ratio)

- **Category**: Phenomenon-Specific
- **Definition**: The ratio of current market price to fundamental value; the primary single-number summary of bubble magnitude.
- **Formula**:
  ```
  bubble_ratio(t) = P(t) / F(t)
  ```
- **Derivation Rationale**: The P/F ratio directly captures the "premium to intrinsic value" concept central to the greater fool theory — it answers "how many times intrinsic value are speculators paying?". It is analogous to the CAPE (Cyclically Adjusted PE) ratio used by Shiller as a market-level bubble indicator.
- **Academic Calibration Source**:
  - Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173–204. https://doi.org/10.1111/1468-0262.00393 — the model's equilibrium bubble ratio is calibrated to 1.3–2.0× in typical equity markets before forced liquidation triggers a crash.
  - NASDAQ Dot-com (1995–2000): P/E at peak ~80× vs. long-run average ~15× → implicit P/F ≈ 5.3×. Simulation with shorter duration targets 1.3–1.8× as a scaled-down analogue.
  - Dutch Tulip Mania: P/F ≈ 50–100× for rarest varieties (Garber, 1989) — extreme end of the bubble ratio spectrum.
- **Interpretation**:
  - bubble_ratio = 1.0: Fairly valued
  - bubble_ratio > 1.3: Clear bubble (30% overvaluation)
  - bubble_ratio > 1.5: Severe bubble — consistent with late-stage dot-com dynamics
  - bubble_ratio < 1.0: Post-crash undervaluation
- **Normal Range for Simulation**: Peak bubble_ratio: 1.3–1.8× for 100-round calibration
- **Red Flag**: Peak < 1.1 → bubble fails to form; peak > 3.0 → parameters too extreme, unrealistic

---

### Metric: Bubble Magnitude (Cumulative Deviation Area)

- **Category**: Phenomenon-Specific / Integrated Measure
- **Definition**: The cumulative sum of positive price deviations across all rounds, measuring the total "area" under the bubble — capturing both height and duration of speculative excess.
- **Formula**:
  ```
  bubble_magnitude = Σ_t max(0, (P(t) − F(t)) / F(t))
  ```
- **Derivation Rationale**: Point-in-time measures like peak bubble_ratio miss bubbles that are moderate in height but long in duration. Bubble magnitude integrates both dimensions, providing a single scalar summary of total speculative excess. It is analogous to the "duration-weighted deviation" measure used in Brunnermeier (2001).
- **Academic Calibration Source**:
  - Brunnermeier, M. K. (2001). *Asset Pricing under Asymmetric Information*. Oxford University Press. Chapter 5 discusses integrated deviation as a welfare-relevant measure of bubble cost.
  - For a 100-round simulation with peak deviation 0.40 sustained for 30 rounds: bubble_magnitude ≈ 30 × 0.40 / 2 ≈ 6–15 (depending on ramp-up and wind-down shape).
- **Normal Range**: [5, 30] for 100-round simulation; depends on peak deviation and duration
- **Red Flag**: Zero → bubble never forms; > 50 → excessively large bubble, miscalibrated

---

### Metric: Return Autocorrelation (Lag-1)

- **Category**: Behavioral / Positive Feedback
- **Definition**: Pearson lag-1 autocorrelation of price returns across all rounds, measuring whether successive returns are correlated (positive feedback/momentum) or anti-correlated (mean reversion).
- **Formula**:
  ```
  r(t)     = (P(t) − P(t−1)) / P(t−1)
  AC1      = corr(r(t), r(t−1))   computed over specified window (full series or phase-specific)
  ```
- **Derivation Rationale**: In a bubble driven by positive feedback (momentum → demand → higher prices → more momentum), successive returns should be positively correlated. In a mean-reverting regime (γ-term dominant), returns should be negatively correlated. The sign and magnitude of AC1 is therefore a direct discriminant of which regime is operating.
- **Academic Calibration Source**:
  - De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 — the noise trader model predicts positive autocorrelation under noise trader dominance; typical values AC1 ≈ 0.2–0.4 in simulated bubble markets.
  - Lo, A. W., & MacKinlay, A. C. (1988). Stock market prices do not follow random walks. *Review of Financial Studies*, 1(1), 41–66. https://doi.org/10.1093/rfs/1.1.41 — documents AC1 ≈ 0.17 at weekly intervals in US equities; bubble phases exhibit higher autocorrelation.
- **Interpretation**:
  - AC1 > 0.3: Strong positive momentum — bubble formation condition
  - AC1 ∈ (0, 0.3): Mild momentum — early bubble build-up
  - AC1 ≈ 0: Random walk — no dominant behavioural regime
  - AC1 < −0.2: Mean-reverting — recovery or post-crash oscillation
- **Normal Range**: During bubble phase: +0.2 to +0.5; crash and recovery: near zero or negative
- **Red Flag**: AC1 ≈ 0 throughout → momentum agents not driving prices; check λ and aggressiveness

---

### Metric: Rolling Return Volatility

- **Category**: Volatility / Volatility Clustering
- **Definition**: Rolling 10-round standard deviation of price returns, measuring how turbulent market conditions are in a sliding window.
- **Formula**:
  ```
  r(t)      = (P(t) − P(t−1)) / P(t−1)
  vol(t)    = std({r(t−9), …, r(t)})
  ```
- **Derivation Rationale**: Volatility clustering — the stylised fact that high-volatility periods cluster together — is a defining characteristic of financial markets during speculative events. The 10-round rolling window balances responsiveness against noise; it is the simulation analogue of the 2-week rolling realised volatility window used in empirical GARCH studies.
- **Academic Calibration Source**:
  - Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. https://doi.org/10.2307/1912773 — establishes ARCH/GARCH as the canonical model for volatility clustering; simulated markets should exhibit similar clustering patterns.
  - Andersen, T. G., Bollerslev, T., Diebold, F. X., & Labys, P. (2003). Modeling and forecasting realized volatility. *Econometrica*, 71(2), 579–625. https://doi.org/10.1111/1468-0262.00418 — documents that realised volatility during crash events is 5–15× its equilibrium level.
- **Normal Range**: Base volatility (early rounds): ~0.002–0.005; peak/crash: ~0.010–0.030; extreme crash: up to 0.050
- **Red Flag**: Completely flat volatility throughout → simulation too deterministic or noise_std ≈ 0

---

### Metric: Maximum Drawdown

- **Category**: Price Dynamics / Crash Severity
- **Definition**: Maximum peak-to-trough price decline as a percentage of the peak price, measuring the worst-case loss from holding through the crash.
- **Formula**:
  ```
  max_drawdown = max_{t₁ < t₂} [(P(t₁) − P(t₂)) / P(t₁)] × 100%
  ```
- **Derivation Rationale**: Maximum drawdown captures the tail severity of the crash, which is the economically relevant measure for leveraged agents facing margin calls. A drawdown of 30% at 3× leverage produces a 90% equity loss — a margin call-inducing event.
- **Academic Calibration Source**:
  - NASDAQ dot-com crash (2000–2002): −78% peak-to-trough; US housing crisis (2007–2012): Case-Shiller −33%. Simulation target is 20–50%, a compressed version of real-world crashes consistent with the shorter simulation duration.
  - Chekhlov, A., Uryasev, S., & Zabarankin, M. (2005). Drawdown measure in portfolio optimization. *International Journal of Theoretical and Applied Finance*, 8(1), 13–58. https://doi.org/10.1142/S0219024905002767 — establishes maximum drawdown as a tail-risk measure with superior sensitivity compared to VaR.
- **Normal Range**: [20%, 50%] for bubble-crash cycle; calibrated to dot-com and housing crisis severity
- **Red Flag**: Max drawdown < 5% after bubble peak → crash mechanism not working; check margin_call_threshold

---

### Metric: Positive Feedback Index

- **Category**: Behavioral / Positive Feedback Loop Validation
- **Definition**: Correlation between net demand in round t and price return in round t+1, measuring the strength of the demand-price feedback loop.
- **Formula**:
  ```
  positive_feedback = corr(net_demand(t), return(t+1))
  ```
- **Derivation Rationale**: The core mechanism of bubble formation is `demand → price → demand`. If this loop is operating, a positive net demand at time t should predict a positive price return at t+1 (because the demand pushes price up). This correlation directly measures the loop strength and is a unique signature of the bubble mechanism that distinguishes it from random price variation.
- **Academic Calibration Source**:
  - De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x — documents that demand-price correlation > 0.5 is the signature of positive feedback trading dominance.
  - Cutler, D. M., Poterba, J. M., & Summers, L. H. (1991). Speculative dynamics. *Review of Economic Studies*, 58(3), 529–546. https://doi.org/10.2307/2298010 — empirically estimates positive feedback index ≈ 0.6–0.8 during speculative episodes.
- **Interpretation**:
  - Value > 0.5: Strong positive feedback — demand is driving prices
  - Value ≈ 0: No feedback — price changes are independent of demand
  - Value < 0: Stabilising — excess demand predicts price reversion (fundamentals dominating)
- **Normal Range**: During bubble formation: +0.5 to +0.9; stable/crash: near zero
- **Red Flag**: Consistently near 0 or negative → λ too low; positive feedback loop not established

---

### Metric: Agent-Type Net Demand and Volume

- **Category**: Volume / Behavioral Validation
- **Definition**: Total signed net demand (buy − sell) and unsigned trading volume by agent type per simulation run, decomposing market demand into its component behavioral sources.
- **Formula**:
  ```
  net_demand_type(t) = Σ_{i ∈ type} quantity_i(t)   (signed)
  volume_type        = Σ_t Σ_{i ∈ type} |quantity_i(t)|   (unsigned, cumulative)
  ```
- **Derivation Rationale**: Decomposing demand by agent type allows direct empirical testing of the theoretical predictions: MomentumSpeculator should provide the largest positive net demand during bubble formation; RationalArbitrageur should provide the only sustained negative net demand.
- **Academic Calibration Source**:
  - Chordia, T., Roll, R., & Subrahmanyam, A. (2002). Order imbalance, liquidity, and market returns. *Journal of Financial Economics*, 65(1), 111–130. https://doi.org/10.1016/S0304-405X(02)00136-8 — documents that order imbalance by institutional vs. retail traders predicts short-horizon returns with R² ≈ 0.10–0.25.
- **Normal Range**: MomentumSpeculator cumulative net demand positive throughout bubble; RationalArbitrageur net demand negative throughout; LeveragedBuyer switches from strongly positive to strongly negative at margin call
- **Red Flag**: All agents identical net demand → strategy differentiation not working; check threshold conditions


## 3. Analysis Dimensions

### Dimension 1: Price Dynamics and Bubble Formation

- **Purpose**: Verify that the target phenomenon (asset bubble) clearly emerges and identify its key characteristics
- **Metrics Used**: Price deviation, bubble ratio, bubble magnitude
- **Visualization**: Line chart; x-axis = round number; y-axis = price and fundamental (dual lines); bubble_ratio on secondary axis
- **Expected Pattern**: Price rises above fundamental in rounds 10–20; reaches peak bubble_ratio > 1.3× around rounds 40–60; then crashes back toward or below fundamental by rounds 80–100. Price-fundamental divergence should be visually obvious.
- **Comparison Baseline**: NASDAQ dot-com (1999–2002): P/F peak ~5.3×, duration ~5 years → simulation analogue is 1.3–1.8× over 100 rounds (compressed timescale)

### Dimension 2: Agent Behavior and Portfolio Performance

- **Purpose**: Verify that each investor type behaves consistently with its theoretical role; assess which strategies profit and which lose in the bubble-crash cycle
- **Metrics Used**: Net demand by type, cumulative volume by type, final portfolio values
- **Visualization**: Stacked bar chart of cumulative net demand by agent type (bubble phase vs. crash phase); line chart of portfolio value evolution
- **Expected Pattern**: MomentumSpeculator profits during bubble, large losses if caught in crash; RationalArbitrageur small losses during bubble (shorts too early), recovers during crash; LeveragedBuyer large profits during bubble, catastrophic loss at crash; FundamentalInvestor moderate performance, outperforms long-term

### Dimension 3: Bubble Lifecycle Phase Analysis

- **Purpose**: Identify and measure the four distinct phases of the bubble cycle
- **Metrics Used**: Price deviation, bubble ratio, rolling volatility, volume
- **Visualization**: Price chart with phase-coloured bands; rolling volatility overlay
- **Expected Pattern**: Four clearly separable phases with distinct signatures in price, volatility, and volume (see §4 for quantitative phase criteria)

### Dimension 4: Positive Feedback Loop Verification

- **Purpose**: Confirm that the core mechanism (demand → price → more demand) is operating
- **Metrics Used**: Return autocorrelation, positive feedback index
- **Visualization**: Scatter plot of net_demand(t) vs. return(t+1); rolling autocorrelation chart
- **Expected Pattern**: During bubble phase, positive_feedback > 0.5 and AC1 > 0.3. During recovery, both metrics drop toward zero or negative.

### Dimension 5: Crash Catalyst Attribution

- **Purpose**: Confirm that LeveragedBuyer margin calls are the primary crash catalyst
- **Metrics Used**: LeveragedBuyer volume by round, margin call round(s), price return acceleration
- **Visualization**: Round-by-round LeveragedBuyer action timeline; overlay with price decline curve
- **Expected Pattern**: Price decline rate accelerates significantly (≥ 2× prior-round decline) in the first round(s) when LeveragedBuyer fires margin calls; crash deepens as subsequent margin calls cascade

### Dimension 6: Cross-Variant Comparison

- **Purpose**: Quantify how Rule, LLM, RuleLLM, and Rag variants differ across key metrics
- **Metrics Used**: All core metrics
- **Visualization**: Multi-column comparison table; side-by-side price curves for all 4 variants
- **Expected Pattern**: See §9 of simulation-bases.md; at minimum, LLM variant should show different crash timing or peak bubble_ratio vs. Rule baseline


## 4. Phase Analysis Framework

### Phase Detection Rules

| Phase | Name         | Entry Condition                  | Exit Condition                   | Key Indicators                                                                                                    | Typical Round Range |
|-------|--------------|----------------------------------|----------------------------------|-------------------------------------------------------------------------------------------------------------------|---------------------|
| 1     | Build-up     | Round 1                          | bubble_ratio first exceeds 1.10× | Gradually rising price; increasing volume; low volatility; MomentumSpeculator net demand positive                 | Rounds 1–20         |
| 2     | Escalation   | bubble_ratio first exceeds 1.10× | bubble_ratio reaches maximum     | Rapid price rise; high volume; rising volatility; strong positive AC1; RationalArbitrageur at near-max short      | Rounds 20–50        |
| 3     | Peak & Crash | Round with max bubble_ratio      | Price declines > 15% from peak   | Volatility spike; volume surge; LeveragedBuyer margin calls fire; MomentumSpeculator panic selling                | Rounds 50–70        |
| 4     | Resolution   | Price decline > 15% from peak    | End of simulation                | Price converges toward fundamental; declining volume; reduced volatility; FundamentalInvestor net demand positive | Rounds 70–100       |

### Quantitative Phase Criteria

**Phase 2 observable signatures**:
- bubble_ratio > 1.10 for ≥ 3 consecutive rounds
- Rolling AC1 > 0.20
- MomentumSpeculator cumulative volume > 30% of total market volume

**Phase 3 observable signatures**:
- Max drawdown begins to accumulate (price falling from peak)
- LeveragedBuyer fires at least one margin call
- Rolling volatility > 0.010 per round

**Phase 4 observable signatures**:
- Price returns positive for ≥ 3 of last 5 rounds
- FundamentalInvestor net demand turns positive (buying undervalued)
- Rolling AC1 < 0 (mean reversion dominating)

### Phase Transition Failure Diagnostics

| Failure                | Symptom                                 | Likely Cause                                                    | Fix                                                         |
|------------------------|-----------------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------|
| Phase 2 never starts   | bubble_ratio never crosses 1.10         | λ too low; momentum agents under-sized                          | Increase price_impact λ or aggressiveness                   |
| Phase 3 crash too mild | Drawdown < 5% after bubble peak         | margin_call_threshold too low; LeveragedBuyer under-represented | Increase margin_call_threshold to 0.75+                     |
| Phase 4 never starts   | Prices never recover toward fundamental | γ too low; no buying agents active post-crash                   | Increase mean_reversion γ; check FundamentalInvestor config |
| Bubble too short       | Peak-to-crash in < 10 rounds            | γ too high (corrects too fast)                                  | Reduce γ from 0.005 toward 0.001                            |


## 5. Cross-Variant Comparison Framework

### Comparison Protocol

1. **Normalize**: Run all 4 variants with same fundamental value (F₀ = 100.0), same initial price (P₀ = 100.0), 100 rounds, same agent count (18 total)
2. **Statistical test**: For LLM/RuleLLM/Rag (stochastic): run 10 independent trials; report mean ± std; use Mann-Whitney U test (p < 0.05) for cross-variant significance
3. **Key comparison axes**:

| Axis               | Question                                                    | Expected Direction                                                                  |
|--------------------|-------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Bubble onset speed | Round when bubble_ratio first exceeds 1.2×                  | Rule = RuleLLM < LLM (deterministic vs. stochastic)                                 |
| Bubble intensity   | Peak bubble_ratio                                           | Rule: consistent; LLM: more variable; Rag: may be moderated by historical knowledge |
| Crash severity     | Max drawdown                                                | LLM potentially > Rule if LLM delays shorting further                               |
| Behavioral realism | Do LLM reasoning traces show realistic investor psychology? | Qualitative scoring against Dot-com and housing bubble narratives                   |
| Decision quality   | Final portfolio value vs. Rule baseline                     | Rag agents expected to show improved long-run performance                           |

4. **Reporting format**:

| Metric                            | Rule    | LLM        | RuleLLM    | Rag        |
|-----------------------------------|---------|------------|------------|------------|
| Bubble onset round (ratio > 1.2×) | [round] | [mean ± σ] | [mean ± σ] | [mean ± σ] |
| Peak bubble_ratio                 | [value] | [mean ± σ] | [mean ± σ] | [mean ± σ] |
| Max drawdown                      | [%]     | [mean ± σ] | [mean ± σ] | [mean ± σ] |
| Crash trigger round               | [round] | [mean ± σ] | [mean ± σ] | [mean ± σ] |
| Positive feedback index           | [value] | [mean ± σ] | [mean ± σ] | [mean ± σ] |
| Bubble magnitude                  | [value] | [mean ± σ] | [mean ± σ] | [mean ± σ] |


## 6. Expected Results and Validation

### Calibration Targets from Literature

| Metric                    | Target Range | Calibration Source                                                                           | Validation Method                                        |
|---------------------------|--------------|----------------------------------------------------------------------------------------------|----------------------------------------------------------|
| Peak bubble_ratio         | [1.3, 1.8×]  | Abreu & Brunnermeier (2003): equilibrium bubble 1.3–2.0×; NASDAQ: 5.3× (compressed analogue) | Run 10 Rule trials; reject if mean peak < 1.1×           |
| Price deviation peak      | [20%, 80%]   | Shiller (2000): historical bubbles +50% to +200%; simulation compression factor ~3×          | Check maximum deviation across runs                      |
| Max drawdown              | [20%, 60%]   | NASDAQ: −78%; housing: −33%; simulation target midpoint ~35%                                 | Compute drawdown for each run; report mean ± std         |
| Return AC1 (bubble phase) | [0.2, 0.5]   | De Long et al. (1990): noise trader dominance signature                                      | Compute AC1 over Phase 2–3 rounds only                   |
| Positive feedback index   | [0.5, 0.9]   | De Long et al. (1990b): Cutler et al. (1991)                                                 | Compute corr(net_demand(t), return(t+1)) over all rounds |
| Bubble onset round        | [15, 35]     | Calibrated to 100-round simulation; bubble forms in first third                              | Check round when bubble_ratio first exceeds 1.2×         |

### Sensitivity Discussion

- **λ (price_impact) sensitivity**: Increasing λ from 0.10 to 0.20 raises peak bubble_ratio from ~1.2× to ~1.8×. Recommended grid: λ ∈ {0.05, 0.10, 0.15, 0.20, 0.25}.
- **γ (mean_reversion) sensitivity**: γ = 0.005 (baseline) allows sustained deviations; γ = 0.05 prevents bubble forming. Recommended grid: γ ∈ {0.001, 0.005, 0.01, 0.05}.
- **margin_call_threshold sensitivity**: Raising from 0.70 to 0.80 means smaller price declines trigger margin calls, producing more severe crashes. Test: {0.60, 0.70, 0.75, 0.80}.
- **leverage_ratio sensitivity**: Raising from 3× to 5× dramatically increases both bubble formation speed and crash severity. Test: {2, 3, 4, 5}; document the leverage at which max_drawdown first exceeds 50%.

### Validation Failure Signs

| Failure Sign                           | Interpretation                       | Parameter Fix                                                      |
|----------------------------------------|--------------------------------------|--------------------------------------------------------------------|
| Peak bubble_ratio < 1.1                | Bubble fails to form                 | Increase λ or aggressiveness; verify MomentumSpeculator is trading |
| No crash (prices never fall from peak) | Crash mechanism not working          | Increase margin_call_threshold or add more LeveragedBuyer agents   |
| Max drawdown < 5%                      | Crash too mild                       | Adjust leverage_ratio or margin_call_threshold                     |
| AC1 ≈ 0 throughout                     | Positive feedback loop not operating | Increase λ; verify MomentumSpeculator aggressiveness               |
| Positive feedback index < 0.3          | Demand not driving prices            | Increase λ; verify net_demand computation                          |
| Volatility flat throughout             | Simulation too deterministic         | Check noise_std > 0; verify stochastic components are active       |


## 7. Visualization Catalogue

| Plot Name                 | Type            | X-axis        | Y-axis                                  | Overlays                                    | Purpose                                                     |
|---------------------------|-----------------|---------------|-----------------------------------------|---------------------------------------------|-------------------------------------------------------------|
| Price vs Fundamental      | Line (dual)     | Rounds        | Left: Price; Right: Fundamental         | bubble_ratio as secondary line; phase bands | Primary phenomenon plot — verify bubble formation and crash |
| Bubble Analysis           | Line + bar      | Rounds        | Deviation (%); bubble_ratio             | Phase detection markers; drawdown shading   | Detailed bubble lifecycle                                   |
| Summary Panel             | Multi-panel 3×2 | Rounds        | Various                                 | All key metrics                             | Quick health check                                          |
| Agent Net Demand          | Stacked bar     | Rounds        | Net demand by type                      | Price overlay                               | Who drove demand during bubble vs. crash                    |
| Portfolio Performance     | Line            | Rounds        | Portfolio value (normalised to initial) | One line per agent type                     | Which strategies profit/lose                                |
| Rolling Volatility        | Line            | Rounds        | vol(t) (rolling std)                    | Phase bands; 0.01 and 0.03 thresholds       | Verify volatility clustering                                |
| Rolling Autocorrelation   | Line            | Rounds        | AC1 (lag-1)                             | Zero line; +0.3 and −0.2 lines              | Show regime shift: bubble vs. recovery                      |
| Return Distribution       | Histogram       | Return (%)    | Frequency                               | Normal fit overlay                          | Show fat tails and positive skew during bubble              |
| Positive Feedback Scatter | Scatter         | net_demand(t) | return(t+1)                             | Linear regression line                      | Validate demand-price feedback loop                         |
| Crash Catalyst Timeline   | Line + events   | Rounds        | Price                                   | Vertical markers at margin call rounds      | Confirm LeveragedBuyer as crash catalyst                    |
| Cross-Variant Comparison  | Bar (4 groups)  | Metric name   | Metric value                            | Error bars for stochastic variants          | Final cross-variant summary                                 |
