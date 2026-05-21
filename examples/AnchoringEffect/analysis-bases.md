# AnchoringEffect — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question                                                                        | Metric(s)                                          | Expected Finding                                                                       |
|-----------|------------------------------------------------------------------------------------------|----------------------------------------------------|----------------------------------------------------------------------------------------|
| O1        | Do anchoring agents create persistent price deviations from fundamental value?           | Price deviation (%), Mean Absolute Deviation (MAD) | Prices remain 3–10% above fundamental for extended periods                             |
| O2        | How long does it take the market to revert to fundamental after initial mispricing?      | Anchoring persistence half-life                    | Slow convergence: half-life 20–60 rounds (vs. ~5 rounds in a fully rational market)    |
| O3        | What is the relative corrective power of RationalUpdater vs. anchoring agent resistance? | Agent-type order contribution, deviation slope     | RationalUpdater partially corrects but is insufficient to overcome 4 anchoring agents  |
| O4        | Does simulation anchoring magnitude match empirical literature calibration targets?      | MAD vs. Campbell & Sharpe (2009) benchmarks        | MAD ∈ [3%, 10%] matching analyst forecast error magnitudes                             |
| O5        | How does anchoring affect agent portfolio performance?                                   | Portfolio Sharpe ratio, final wealth by agent type | RationalUpdater outperforms AnchoredTrader and HistoricalAnchor long-run               |
| O6        | Do all variants (Rule/LLM/RuleLLM/Rag) reproduce the anchoring phenomenon?               | Cross-variant MAD and half-life                    | All variants show persistent deviation; LLM more variable; Rag potentially reduced MAD |


## §2 Core Metrics Catalogue

### Metric: Price Deviation from Fundamental

- **Category**: Price Dynamics / Phenomenon-Specific
- **Definition**: Signed percentage difference between market price and fundamental value, measuring the magnitude and direction of anchoring-induced mispricing.
- **Formula**:
  ```
  deviation(t) = (P(t) − F) / F
  ```
- **Function Signature**: `def calculate_price_deviation(market_prices: dict[int, float], fundamentals: dict[int, float]) -> list[float]`
  Note: F = 100.0 (constant in baseline AnchoringEffect configuration). Unlike AssetBubble where F grows, the constant F here ensures all price deviations are attributable purely to anchoring bias, not fundamental growth.
- **Derivation Rationale**: The percentage form is the standard normalised measure used in the anchoring literature (Campbell & Sharpe, 2009 measure forecast errors as % of prior estimate). A signed measure allows detection of both upward anchoring (prices above F) and downward anchoring (prices resist falling below anchor).
- **Academic Calibration Source**:
  - Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127 — documents systematic forecast errors of 3–10% attributed to anchoring; this is the primary calibration target.
  - Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124 — the foundational paper establishing that estimates insufficiently adjust from anchors; calibrates the 5% initial mispricing (initial_price = 105) as a realistic anchoring scenario.
- **Interpretation**:
  - deviation = 0: Price at fundamental — no anchoring effect visible
  - deviation ∈ (0%, +5%): Mild overvaluation — anchoring agents partially resist correction
  - deviation > +5%: Strong anchoring — persistent elevation above F
  - deviation ∈ (−5%, 0%): Post-correction zone; anchoring may hold prices slightly above F
  - deviation < −5%: Over-correction; rational agents or MomentumTrader overshoot
- **Normal Range**: [−0.15, +0.15] for anchoring-populated markets; |deviation| > 0.15 signals excessive anchoring
- **Red Flag**: `mean(|deviation|) < 0.01` throughout all rounds → anchoring has no market effect; check `adjustment_factor` and `price_impact`

---

### Metric: Mean Absolute Deviation (MAD)

- **Category**: Phenomenon-Specific / Integrated Anchoring Measure
- **Definition**: Time-averaged magnitude of price deviation from fundamental across all rounds, providing a single scalar summary of overall anchoring-induced mispricing intensity.
- **Formula**:
  ```
  MAD = (1/T) × Σ_t |P(t) − F| / F
  ```
- **Function Signature**: `def _compute_mad(prices_list: list[float], fundamental: float) -> float`
  where T is the total number of rounds.
- **Derivation Rationale**: A single-round deviation can be temporarily elevated by noise (NoiseTrader) without reflecting true anchoring. MAD integrates over all rounds, correctly capturing persistent mispricings while averaging out transient noise shocks. It is the appropriate measure for comparing simulation anchoring magnitude to Campbell & Sharpe's (2009) time-averaged forecast errors.
- **Academic Calibration Source**:
  - Campbell, S. D., & Sharpe, S. A. (2009): Documents average quarterly analyst forecast errors of approximately 3–8% (mean 5%) attributable to anchoring. This directly calibrates MAD target range to [0.03, 0.10].
  - Northcraft, G. B., & Neale, M. A. (1987): Expert valuation bias of ~12% toward listing price anchor; average market-wide effect would be ~5–8% after dilution by rational participants — consistent with MAD ∈ [0.03, 0.10].
- **Interpretation**:
  - MAD < 0.02: Weak anchoring effect — corrective agents dominate
  - MAD ∈ [0.03, 0.10]: Calibrated anchoring-driven mispricing — target range
  - MAD > 0.15: Excessive mispricing; anchoring too strong; check price_impact or mean_reversion
- **Normal Range**: [0.03, 0.10]
- **Red Flag**: MAD < 0.01 (anchoring ineffective) or MAD > 0.20 (overcalibrated)

---

### Metric: Anchoring Persistence (Half-Life)

- **Category**: Phenomenon-Specific / Temporal Dynamics
- **Definition**: Number of rounds required for the initial deviation to decay to 50% of its starting value, measuring how long the anchoring bias sustains the mispricing.
- **Formula**:
  ```
  Fit: |deviation(t)| ≈ D₀ × exp(−t / τ)
  half_life = τ × ln(2)
  ```
- **Function Signature**: `def _compute_half_life(prices_list: list[float], fundamental: float) -> float`
  where D₀ = initial deviation (= 0.05, since initial_price = 105 and F = 100), and τ is the exponential decay constant estimated by regression.
- **Derivation Rationale**: The exponential decay model is appropriate because the system has a linear restoring force (the γ-term and RationalUpdater provide forces proportional to deviation), leading to exponential convergence in the absence of noise. The half-life is the most interpretable summary of correction speed — it directly answers "how many rounds does the anchoring bias last?".
- **Academic Calibration Source**:
  - Campbell, S. D., & Sharpe, S. A. (2009): Quarterly earnings forecast errors persist for 1–3 quarters before full correction — equivalent to approximately 25–75 trading days, or 25–75 simulation rounds. This calibrates the target half-life to [20, 60] rounds.
  - Fama, E. F., & French, K. R. (1988). Permanent and temporary components of stock prices. *Journal of Political Economy*, 96(2), 246–273. https://doi.org/10.1086/261535 — estimates mean-reversion half-life for fundamental-driven deviations at 3–5 years in real equity markets; the simulation's [20, 60] round target represents a compressed timescale analogue.
- **Interpretation**:
  - half_life < 10 rounds: Near-rational market; anchoring corrects quickly (RationalUpdater dominant)
  - half_life ∈ [20, 60]: Realistic anchoring persistence — calibration target
  - half_life > 80 rounds: Very strong anchoring; mean_reversion (γ) too low
  - half_life = NaN: Price diverges or never reverts — critical miscalibration
- **Normal Range**: [20, 60] rounds
- **Red Flag**: half_life < 5 (trivially rational) or half_life = NaN (price diverges)

---

### Metric: Rolling Volatility

- **Category**: Volatility / Market Quality
- **Definition**: Rolling 10-round standard deviation of log returns, measuring the turbulence of the price path.
- **Formula**:
  ```
  r(t)    = log(P(t) / P(t−1))
  vol(t)  = std({r(t−9), …, r(t)})
  ```
- **Function Signature**: `def _compute_rolling_volatility(prices_list: list[float], window: int = 10) -> list[float]`
  Note: Uses log returns (not arithmetic) consistent with standard financial time series analysis.
- **Derivation Rationale**: Anchoring creates a specific volatility signature: moderate, persistent volatility with no large spikes (unlike AssetBubble which has a crash-driven volatility spike). The anchoring-specific expected pattern is relatively flat rolling volatility that represents the noise term σ = 0.5 modulated by small anchoring demand shocks.
- **Academic Calibration Source**:
  - Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x — establishes that uninformed trading (modelled by NoiseTrader) creates realistic background volatility without the extreme spikes of informed trading or forced liquidation.
  - Andersen, T. G., Bollerslev, T., Diebold, F. X., & Labys, P. (2003). Modeling and forecasting realized volatility. *Econometrica*, 71(2), 579–625. https://doi.org/10.1111/1468-0262.00418 — daily equity return volatility is typically 0.5–2% for stable markets; 2–5% during events. Anchoring simulation target is 0.5–2%.
- **Normal Range**: [0.5%, 2.0%] per round
- **Red Flag**: vol > 5% per round → simulation unstable (NoiseTrader or MomentumTrader orders too large); vol ≈ 0% → no noise (check noise_std)

---

### Metric: Return Autocorrelation (Lag-1)

- **Category**: Behavioral / Market Dynamics
- **Definition**: Pearson lag-1 autocorrelation of price returns, measuring whether the anchoring-induced drift is momentum-like (positive AC1) or mean-reverting (negative AC1).
- **Formula**:
  ```
  r(t)  = (P(t) − P(t−1)) / P(t−1)
  AC1   = corr(r(t), r(t−1))
  ```
- **Function Signature**: `def _compute_autocorrelation(prices_list: list[float], lag: int = 1) -> float`
- **Derivation Rationale**: In an anchoring-driven market, the persistent upward price support from AnchoredTrader creates mild positive return autocorrelation early in the simulation (when prices are above their biased anchor targets). As the market corrects, AC1 should turn negative (mean-reverting). This phase shift in AC1 is a diagnostic signature of the anchoring lifecycle.
- **Academic Calibration Source**:
  - Lo, A. W., & MacKinlay, A. C. (1988). Stock market prices do not follow random walks. *Review of Financial Studies*, 1(1), 41–66. https://doi.org/10.1093/rfs/1.1.41 — documents AC1 ≈ 0.17 at weekly intervals in US equities. For anchoring simulations, AC1 ∈ [0.0, 0.30] is consistent with mild persistent drift rather than strong momentum.
- **Interpretation**:
  - AC1 ≈ 0: Near-efficient — no dominant drift pattern (noise trader dominated)
  - AC1 > 0.2: Positive momentum — anchoring sustains slow upward drift
  - AC1 < −0.2: Mean reversion dominating — rational agents and γ-term correcting
- **Normal Range**: [0.0, 0.30] for anchoring-dominant market
- **Red Flag**: |AC1| > 0.6 → excessive trend or over-correction; check agent calibration

---

### Metric: Anchoring Bias Magnitude

- **Category**: Phenomenon-Specific / Behavioral
- **Definition**: The gap between AnchoredTrader's biased perceived_target and the true fundamental value, measuring the magnitude of the cognitive distortion.
- **Formula**:
  ```
  bias_magnitude = |perceived_target − F| / F
                 = |anchor + (F − anchor) × α − F| / F
                 = (1 − α) × |anchor − F| / F
  ```
- **Function Signature**: `def _compute_bias_magnitude(prices_list: list[float], fundamental: float, adjustment_factor: float) -> float`
  For anchor = 105, F = 100, α = 0.3: `bias_magnitude = 0.7 × 5/100 = 0.035` (3.5%)
- **Derivation Rationale**: The bias magnitude is theoretically fixed given the parameters (it depends only on α and the anchor-fundamental gap). Computing it from simulation outputs validates that the anchoring mechanism is operating as designed.
- **Academic Calibration Source**:
  - Tversky, A., & Kahneman (1974): α ≈ 0.3 experimentally → bias_magnitude = (1−0.3) × 0.05 = 0.035 (3.5% upward bias in perceived fair value). Campbell & Sharpe (2009) find 3–8% average bias — consistent with this calibration.
- **Normal Range**: [0.02, 0.10] given α = 0.3 and initial price 5% above fundamental
- **Red Flag**: bias_magnitude > 0.20 → adjustment_factor too low (< 0.1); unrealistic extreme anchoring

---

### Metric: Max Drawdown

- **Category**: Portfolio / Risk
- **Definition**: Maximum peak-to-trough price decline over the simulation, measuring the worst realized correction from the anchored high.
- **Formula**:
  ```
  max_drawdown = max_{t₁ < t₂} [(P(t₁) − P(t₂)) / P(t₁)]
  ```
- **Function Signature**: `def _compute_max_drawdown(prices_list: list[float]) -> float`
- **Derivation Rationale**: In an anchoring simulation, the drawdown is expected to be moderate (not crash-scale). The max drawdown captures the maximum correction that anchoring agents fail to prevent — measuring how quickly corrective forces (RationalUpdater, γ-term) overcome the anchoring resistance.
- **Academic Calibration Source**: Standard risk metric; for anchoring-driven markets, drawdowns of 5–20% are typical (much smaller than leveraged crash scenarios). Northcraft & Neale (1987) document that expert anchoring reduces price adjustments by ~12%, so a 5–20% downward correction starting from 5% overvaluation is the expected range.
- **Normal Range**: [5%, 20%] for anchoring-driven correction; not a crash, just a gradual return to fundamental
- **Red Flag**: max_drawdown > 40% → price overshoots fundamental significantly; check noise_std and γ

---

### Metric: Agent-Type Trading Volume

- **Category**: Investor Behaviour / Mechanism Attribution
- **Definition**: Cumulative buy and sell quantities by investor identity, used to verify that anchoring, rational-updating, momentum, and noise mechanisms all contribute to the price path.
- **Formula**:
  ```
  buy_volume_i = Σ_t quantity_i(t) where action_i(t) = buy
  sell_volume_i = Σ_t quantity_i(t) where action_i(t) = sell
  total_volume_i = buy_volume_i + sell_volume_i
  ```
- **Function Signature**: `def calculate_metrics(data: dict[str, object], config: dict) -> dict[str, object]`
- **Derivation Rationale**: Price-level metrics alone cannot identify whether the anchoring effect is produced by the intended agents. Volume attribution verifies that AnchoredTrader and HistoricalAnchor provide biased support, RationalUpdater supplies corrective pressure, MomentumTrader amplifies local trends, and NoiseTrader adds background liquidity.
- **Academic Calibration Source**: Grossman & Stiglitz (1980) motivate informed-trader share; Black (1986) motivates noise-trader background order flow.
- **Normal Range**: Anchoring and rational agents should both have non-zero volume in 200-round runs; NoiseTrader volume is stochastic but should be sparse.
- **Red Flag**: Any intended active agent type has zero total volume across 200 rounds; check initial positions, cash constraints, and thresholds.


## §3 Analysis Dimensions

### Dimension 1: Price Dynamics and Anchoring Persistence

- **Purpose**: Verify that anchoring agents create measurable, persistent price deviations from fundamental value
- **Metrics Used**: Price deviation, MAD, half-life
- **Visualization**: Line chart — Price vs. Fundamental over time; horizontal reference line at F = 100; shaded deviation band; annotations at half-life milestone
- **Expected Pattern**: Price starts at 105 (5% above fundamental); slow convergence toward 100 over the 200-round full experiment; deviation remains above 2% through the persistence phase; final price approaches fundamental after the tail correction phase

### Dimension 2: Anchoring Bias Lifecycle Analysis

- **Purpose**: Identify phases of mispricing: establishment, persistence, and correction
- **Metrics Used**: Deviation time-series, half-life, rolling AC1
- **Visualization**: Deviation time-series with phase annotations; overlaid RationalUpdater trade volume bars
- **Expected Pattern**: Phase 1 (rounds 1–10): AnchoredTrader sets anchor; HistoricalAnchor fills price history. Phase 2 (rounds 10–60): Persistent elevation; RationalUpdater provides partial correction but is overwhelmed. Phase 3 (rounds 60–100): Gradual convergence as HistoricalAnchor's 60-round average catches up toward F.

### Dimension 3: Agent Behavior and Portfolio Analysis

- **Purpose**: Confirm each agent type behaves as designed; assess which strategies profit from anchoring
- **Metrics Used**: Agent-type volume, portfolio wealth by type (final cash + position × final price)
- **Visualization**: Grouped bar chart of cumulative volume by type; line chart of portfolio value evolution
- **Expected Pattern**: AnchoredTrader and HistoricalAnchor show moderate activity with biased decisions; RationalUpdater achieves higher Sharpe by selling into the mispricing; MomentumTrader shows high variance; NoiseTrader shows lowest Sharpe

### Dimension 4: Volatility and Market Quality

- **Purpose**: Confirm that anchoring creates realistic moderate volatility, not crash-scale spikes
- **Metrics Used**: Rolling volatility, AC1, max drawdown
- **Visualization**: Rolling volatility over time; AC1 phase chart; drawdown chart
- **Expected Pattern**: Moderate, persistent volatility (0.5–2% per round); positive AC1 (0.1–0.3) during persistence phase, turning slightly negative during correction; max drawdown 5–15%

### Dimension 5: Cross-Variant Comparison

- **Purpose**: Assess whether LLM/RuleLLM/Rag variants reproduce the anchoring phenomenon
- **Metrics Used**: MAD, half-life, rolling AC1 across all variants
- **Visualization**: Multi-panel: deviation time-series for all 4 variants overlaid
- **Expected Pattern**: Rule shows cleanest anchoring signal (MAD = 3–8%, half-life = 20–60); LLM shows same phenomenon with higher variance; RuleLLM tracks Rule closely (±20%); Rag may show reduced MAD if retrieved knowledge includes anchoring awareness


## §4 Phase Analysis Framework

### Phase Detection Rules

| Phase | Name                  | Entry Condition                                 | Exit Condition                              | Key Indicators                                                                         | Typical Round Range |
|-------|-----------------------|-------------------------------------------------|---------------------------------------------|----------------------------------------------------------------------------------------|---------------------|
| 1     | Anchor Establishment  | Round 1                                         | deviation stable within ±0.5% for 5+ rounds | AnchoredTrader sets anchor = 105; HistoricalAnchor begins filling history              | Rounds 1–10         |
| 2     | Persistent Mispricing | `mean(deviation[-5:]) > 0.02` stable            | `mean(deviation[-5:]) < 0.02`               | RationalUpdater buying but price stays elevated; AC1 > 0.1                             | Rounds 10–60        |
| 3     | Slow Correction       | `deviation` declining for 5+ consecutive rounds | `deviation < 0.01`                          | HistoricalAnchor's rolling average converging toward F; anchoring resistance weakening | Rounds 60–90        |
| 4     | Convergence           | `deviation < 0.01`                              | End of simulation                           | Price near fundamental; AC1 near zero; all agents near equilibrium                     | Rounds 90–100       |

### Quantitative Phase Criteria

**Phase 2 observable signatures**:
- AnchoredTrader places buy orders in ≥ 60% of rounds
- RationalUpdater places sell orders in ≥ 70% of rounds
- deviation > 0.02 for ≥ 10 consecutive rounds

**Phase 3 observable signatures**:
- deviation declining for ≥ 5 rounds
- HistoricalAnchor's rolling average approaches F (hist_avg < 102.0)
- RationalUpdater volume decreasing (less deviation to correct)

**Phase 4 observable signatures**:
- deviation < 0.01 for ≥ 5 consecutive rounds
- AnchoredTrader volume decreasing (perceived_dev near zero)
- Rolling volatility at background level (noise-only)

### Phase Transition Failure Diagnostics

| Failure                         | Symptom                          | Likely Cause                                                        | Fix                                                              |
|---------------------------------|----------------------------------|---------------------------------------------------------------------|------------------------------------------------------------------|
| Phase 2 too brief (< 10 rounds) | Rapid correction to F            | Too many RationalUpdater agents or γ too high                       | Reduce γ from 0.01 toward 0.005; or reduce RationalUpdater count |
| Phase 3 never starts            | Permanent deviation > 5%         | γ too low or RationalUpdater too few                                | Increase γ toward 0.02; check RationalUpdater is trading         |
| Phase 4 never reached           | Price stays 2–3% above F forever | Anchoring agents replenish buying support faster than correction    | Expected behaviour if simulation too short; extend to 150 rounds |
| half_life = NaN (diverges)      | Price rises continuously         | γ too small; MomentumTrader + anchoring agents overwhelm correction | Increase γ; reduce NoiseTrader max_order                         |


## §5 Cross-Variant Comparison Framework

### Comparison Protocol

1. **Normalize**: Identical initial conditions across all variants: `initial_price = 105`, `fundamental = 100`, 200 full rounds, same agent roster (9 investors plus 1 market coordinator)
2. **Statistical test**: For stochastic variants (LLM, RuleLLM, Rag): run ≥ 10 trials; report mean ± std; compare to Rule baseline using t-test (p < 0.05)
3. **Key comparison axes**:

| Axis                 | Question                                         | Expected Direction                                                                                              |
|----------------------|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Phenomenon emergence | Does anchoring mispricing appear and persist?    | All variants: yes (Rule deterministic; others probabilistic)                                                    |
| MAD                  | Average deviation from F across all rounds       | Rule baseline; LLM similar with higher variance; Rag potentially lower                                          |
| Half-life            | How quickly does deviation decay?                | Rule: 20–60 rounds; LLM: more variable; Rag: potentially shorter if RAG retrieves corrective information        |
| Adjustment rate      | How quickly do anchoring agents update toward F? | α = 0.3 in Rule; implicit in LLM (should be ≈ 0.3); Rag may show α closer to 0.5 if retrieves awareness of bias |

4. **Reporting format**:

| Metric             | Rule | LLM (mean ± std) | RuleLLM (mean ± std) | Rag (mean ± std) |
|--------------------|------|------------------|----------------------|------------------|
| MAD (%)            | X.XX | X.XX ± X.XX      | X.XX ± X.XX          | X.XX ± X.XX      |
| Half-life (rounds) | X    | X ± X            | X ± X                | X ± X            |
| Max drawdown (%)   | X.XX | X.XX ± X.XX      | X.XX ± X.XX          | X.XX ± X.XX      |
| AC1 (full series)  | X.XX | X.XX ± X.XX      | X.XX ± X.XX          | X.XX ± X.XX      |


## §6 Expected Results and Validation

### Calibration Targets from Literature

| Metric             | Target Range           | Calibration Source                                                                      | Validation Method                                               |
|--------------------|------------------------|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| MAD (%)            | [3%, 10%]              | Campbell & Sharpe (2009): mean analyst forecast error ~5%                               | Compute MAD across all 200 full-round observations; reject if < 1% |
| Half-life (rounds) | [20, 60]               | Campbell & Sharpe (2009): quarterly persistence → 25–75 trading days                    | Fit exponential decay; extract τ                                |
| Max drawdown       | [5%, 20%]              | Typical equity correction magnitude; anchoring creates moderate not extreme corrections | Compute across full simulation                                  |
| Rolling volatility | [0.5%, 2.0%] per round | Black (1986): noise trader background volatility range                                  | Compute rolling std; report mean ± std                          |
| AC1 (bubble phase) | [0.0, 0.30]            | Lo & MacKinlay (1988): weekly autocorrelation in equities                               | Compute AC1 over rounds 10–60 (persistence phase)               |
| Bias magnitude     | [2%, 5%]               | Tversky & Kahneman (1974): α = 0.3 with 5% initial anchor → 3.5% bias                   | Compute `(1 − α) × (anchor − F) / F` from simulation parameters |

### Sensitivity Discussion

- **α (adjustment_factor) sensitivity**: Increasing from 0.3 to 0.6 reduces MAD from ~5% to ~2% and halves the half-life. Grid: α ∈ {0.1, 0.2, 0.3, 0.5, 0.7, 1.0}; document the α at which anchoring effect becomes negligible (MAD < 1%).
- **γ (mean_reversion) sensitivity**: γ = 0.01 (baseline) produces half-life ≈ 30–50 rounds. γ = 0.05 nearly eliminates anchoring (half-life < 10). Recommended grid: γ ∈ {0.005, 0.01, 0.02, 0.05}.
- **anchor_weight sensitivity**: Increasing from 0.5 to 0.8 (stronger HistoricalAnchor) raises MAD by ~40%. Grid: {0.3, 0.5, 0.7, 0.9}.

### Validation Failure Signs

| Failure Sign                   | Interpretation                     | Parameter Fix                                                     |
|--------------------------------|------------------------------------|-------------------------------------------------------------------|
| MAD < 0.01                     | Anchoring has no market effect     | Check `adjustment_factor` ≠ 1.0; verify AnchoredTrader is trading |
| MAD > 0.20                     | Excessive mispricing; unstable     | Reduce λ or increase γ                                            |
| half_life < 5 rounds           | Rational agents correct too fast   | Add more anchoring agents; reduce RationalUpdater count           |
| half_life = NaN (no reversion) | Price diverges                     | Increase γ toward 0.02–0.05                                       |
| Rolling vol > 5%               | Market unstable; noise dominating  | Reduce NoiseTrader max_order or count                             |
| AC1 > 0.5 throughout           | Excessive momentum (not anchoring) | Check MomentumTrader is not dominating; reduce aggressiveness     |


## §7 Visualization Catalogue

| Plot Name                 | Type                 | X-axis     | Y-axis                        | Overlays                                              | Purpose                                               |
|---------------------------|----------------------|------------|-------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| Price vs Fundamental      | Line                 | Round      | Price; dashed line at F = 100 | Phase bands; MAD reference lines                      | Primary phenomenon verification                       |
| Deviation Time-Series     | Line                 | Round      | deviation (%)                 | Zero line; ±5% and ±10% thresholds; phase annotations | Anchoring persistence and decay                       |
| Anchoring Persistence Fit | Line + regression    | Round      | deviation (%)                 | Exponential decay fit; half-life annotation           | Quantify persistence as half-life                     |
| Agent-Type Volume         | Bar                  | Agent type | Cumulative volume (shares)    | —                                                     | Which agents drive market activity                    |
| Portfolio Performance     | Line                 | Round      | Portfolio value ($)           | One line per agent type                               | Who profits/loses from anchoring                      |
| Return Distribution       | Histogram            | Return (%) | Frequency                     | Normal distribution overlay                           | Fat tails and asymmetry from anchoring                |
| Rolling Volatility        | Line                 | Round      | Volatility (%)                | Rolling window = 10; 0.5% and 2% thresholds           | Volatility regime; detect instability                 |
| Rolling Autocorrelation   | Line                 | Round      | AC1 (lag-1)                   | Zero line; ±0.2 reference lines                       | Phase shift: persistence → correction                 |
| Bias Magnitude            | Bar (per agent type) | Agent type | bias_magnitude (%)            | True fundamental reference                            | Compare perceived_target to F for each anchoring type |
| Cross-Variant Comparison  | Bar (4 groups)       | Metric     | Metric value                  | Error bars for stochastic variants                    | Summary cross-variant result                          |
