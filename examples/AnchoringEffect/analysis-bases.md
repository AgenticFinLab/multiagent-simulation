# AnchoringEffect — Analysis Methodology Basis

---

## Table of Contents

| §   | Section                                   | Content Summary                                                                              |
|-----|-------------------------------------------|----------------------------------------------------------------------------------------------|
| §1  | Analysis Objectives                       | 6 research questions (O1–O6) with expected findings and metric mappings                      |
| §2  | Core Metrics Catalogue                    | 42 metrics with full specifications (formula, calibration source, interpretation, red flags) |
| §3  | Analysis Dimensions                       | 7 orthogonal analysis perspectives with visualization plans                                  |
| §4  | Phase Analysis Framework                  | 4-phase lifecycle detection rules, quantitative criteria, failure diagnostics                |
| §5  | Cross-Variant Comparison Framework        | Protocol for Rule vs LLM vs RuleLLM vs Rag statistical comparison                            |
| §6  | Expected Results and Validation           | Literature calibration targets, sensitivity grids, failure signs                             |
| §7  | Visualization Catalogue                   | 12 plot types with axes, overlays, and purpose specifications                                |
| §8  | Registered Metrics Catalogue (extensible) | 44 metrics × 9 categories; validation gates; 11-panel dashboard set                          |
| §9  | Statistical Methodology                   | Sample size requirements, bootstrap, OLS fit, Ljung-Box, ADF, variance ratios                |
| §10 | Limitations and Known Constraints         | Model limitations, analysis-specific limitations, failure modes, scope boundary              |

**§2 Metrics Overview (42 detailed specifications)**:

*Core 19 (documented in §2 base section; #19 Strategy Correlation Matrix follows HHI):*

| #  | Metric                            | Category               | Key Calibration Target            |
|----|-----------------------------------|------------------------|-----------------------------------|
| 1  | Price Deviation from Fundamental  | Price Dynamics         | [−15, +15]%                       |
| 2  | Mean Absolute Deviation (MAD)     | Anchoring-Specific     | [3, 10]% (Campbell & Sharpe 2009) |
| 3  | Anchoring Persistence (Half-Life) | Temporal Dynamics      | [20, 60] rounds                   |
| 4  | Rolling Volatility                | Market Quality         | [0.5, 2.0]% per round             |
| 5  | Return Autocorrelation (Lag-1)    | Market Dynamics        | [0.0, 0.30]                       |
| 6  | Anchoring Bias Magnitude          | Behavioural            | [2, 5]%                           |
| 7  | Max Drawdown                      | Risk                   | [5, 20]%                          |
| 8  | Agent-Type Trading Volume         | Mechanism Attribution  | Non-zero for all active agents    |
| 9  | Agent Terminal Wealth             | Wealth Dynamics        | Dispersal ratio [1.05, 1.50]      |
| 10 | Gini Coefficient                  | Wealth Inequality      | [0.03, 0.30]                      |
| 11 | Wealth Transfer Direction         | Wealth Redistribution  | transfer > 0                      |
| 12 | Price Efficiency Ratio            | Information Efficiency | Starts < 0.3, rises toward 1.0    |
| 13 | Forecast Error Persistence        | Learning Speed         | [0.7, 0.95]                       |
| 14 | Deviation Decay Slope             | Convergence Rate       | [−0.005, −0.0005] per round       |
| 15 | Information Share by Strategy     | Mechanism Attribution  | RU share 40–60%                   |
| 16 | Value-at-Risk (95%)               | Tail Risk              | [−4, −1]% per round               |
| 17 | Conditional VaR (CVaR-95)         | Expected Shortfall     | [−6, −1.5]% per round             |
| 18 | Herfindahl Concentration (HHI)    | Market Concentration   | [0.07, 0.20]                      |

*Extended 23 (documented in subsections §2.2–§2.7):*

| Subsection | Category              | Metrics                                                                                  |
|------------|-----------------------|------------------------------------------------------------------------------------------|
| §2.2       | Price Dynamics        | Half-Life Threshold, Return Skewness, Return Kurtosis, Variance Ratio (Lo & MacKinlay)   |
| §2.3       | Anchoring-Specific    | Anchor Dispersion, Under-Revision Ratio, Regime Transition Lag, Price-to-Anchor Distance |
| §2.4       | Agent Behaviour       | Action Frequency, Net Position TS, Terminal PnL, Sharpe Ratio, Silent Agent Count        |
| §2.5       | Microstructure        | Order Imbalance, Signed Volume AC, Corrective/Biased Ratio, Momentum-Anchoring Coupling  |
| §2.6       | Statistical Inference | MAD Bootstrap CI, Half-Life Bootstrap CI, Ljung-Box p-value, ADF Unit Root p-value       |
| §2.7       | Phase Decomposition   | Phase Assignment TS, Per-Phase Metrics Table                                             |

**§3 Dimensions at a Glance**:

| Dim | Focus                              | Primary Metrics                                  |
|-----|------------------------------------|--------------------------------------------------|
| 1   | Price Dynamics & Persistence       | Deviation, MAD, Half-life                        |
| 2   | Anchoring Bias Lifecycle           | Deviation TS, Phase assignment, Rolling AC1      |
| 3   | Agent Behaviour & Portfolios       | Volume by type, Wealth, Sharpe                   |
| 4   | Volatility & Market Quality        | Rolling vol, AC1, Max drawdown                   |
| 5   | Cross-Variant Comparison           | MAD, Half-life across Rule/LLM/RuleLLM/Rag       |
| 6   | Wealth Dynamics & Redistribution   | Terminal wealth, Gini, Wealth transfer           |
| 7   | Information Efficiency & Tail Risk | PER, VaR, CVaR, HHI, Strategy correlation matrix |

---

## §1 Analysis Objectives

| Objective | Research Question                                                                        | Metric(s)                                          | Expected Finding                                                                                                      |
|-----------|------------------------------------------------------------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| O1        | Do anchoring agents create persistent price deviations from fundamental value?           | Price deviation (%), Mean Absolute Deviation (MAD) | Prices remain 3–10% above fundamental for extended periods                                                            |
| O2        | How long does it take the market to revert to fundamental after initial mispricing?      | Anchoring persistence half-life                    | Slow convergence: half-life 20–60 rounds (vs. ~5 rounds in a fully rational market)                                   |
| O3        | What is the relative corrective power of RationalUpdater vs. anchoring agent resistance? | Agent-type order contribution, deviation slope     | RationalUpdater partially corrects but is insufficient to overcome 6 biased/destabilising agents (AT×2 + HA×2 + DT×2) |
| O4        | Does simulation anchoring magnitude match empirical literature calibration targets?      | MAD vs. Campbell & Sharpe (2009) benchmarks        | MAD ∈ [3%, 10%] matching analyst forecast error magnitudes                                                            |
| O5        | How does anchoring affect agent portfolio performance?                                   | Portfolio Sharpe ratio, final wealth by agent type | RationalUpdater outperforms AnchoredTrader and HistoricalAnchor long-run                                              |
| O6        | Do all variants (Rule/LLM/RuleLLM/Rag) reproduce the anchoring phenomenon?               | Cross-variant MAD and half-life                    | All variants show persistent deviation; LLM more variable; Rag potentially reduced MAD                                |


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


### Metric: Agent Terminal Wealth

- **Category**: Wealth Dynamics / Redistribution
- **Definition**: Final portfolio value per agent — cash balance plus mark-to-market position value at the last-round clearing price. Measures who captured value from the anchoring mispricing.
- **Formula**:
  ```
  W_i(T) = cash_i(T) + position_i(T) × P(T)
  ```
- **Function Signature**: `def m_agent_wealth_terminal(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Wealth redistribution is the economic payoff of behavioural heterogeneity. In anchoring markets, biased agents overpay during the persistence phase; rational agents sell into the overvaluation and realize gains when prices revert. Tracking terminal wealth by strategy type validates the theoretical prediction that corrective strategies profit at the expense of biased strategies (De Long et al., 1990).
- **Academic Calibration Source**:
  - De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 — establishes that noise/biased traders systematically lose wealth to rational arbitrageurs in expectation.
  - Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777–790. — demonstrates that prospect-theory agents may realize intermediate returns through premature gain-taking.
- **Interpretation**:
  - RationalUpdater wealth > initial: Rational agents profited from selling overvalued assets
  - AnchoredTrader wealth < initial: Biased agents overpaid during the persistence phase
  - DispositionTrader wealth ≈ initial: Gain-taking limits both upside and downside
- **Normal Range**: Wealth dispersal (max/min ratio) ∈ [1.05, 1.50] for calibrated anchoring
- **Red Flag**: All agents have identical wealth (no trading occurred) or any agent has negative wealth (unrealistic leverage)

---

### Metric: Gini Coefficient of Terminal Wealth

- **Category**: Wealth Dynamics / Inequality
- **Definition**: Gini index (0 = perfect equality, 1 = one agent holds all wealth) measuring the degree of wealth concentration induced by the anchoring-driven redistribution.
- **Formula**:
  ```
  Gini = (2 × Σᵢ i × W_sorted(i)) / (N × Σᵢ W_sorted(i)) − (N + 1) / N
  ```
- **Function Signature**: `def m_gini_coefficient(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Wealth inequality emerges endogenously from heterogeneous trading strategies. In efficient markets Gini ≈ 0 (no persistent alpha). In behavioural markets with persistent mispricing, rational agents extract rents, increasing inequality. The Gini coefficient quantifies this effect in a scale-invariant manner, allowing cross-simulation comparison.
- **Academic Calibration Source**:
  - Levy, M., & Solomon, S. (1997). New evidence for the power-law distribution of wealth. *Physica A*, 242(1–2), 90–94. — agent-based simulations produce wealth distributions with Gini 0.3–0.7 depending on strategy heterogeneity.
- **Interpretation**:
  - Gini < 0.05: No meaningful redistribution (market near-efficient or agents identical)
  - Gini ∈ [0.05, 0.25]: Moderate redistribution — expected for 100-round anchoring scenarios
  - Gini > 0.40: Extreme concentration — one strategy dominates profits
- **Normal Range**: [0.03, 0.30] for anchoring-populated 9-agent simulations
- **Red Flag**: Gini > 0.5 or Gini = 0 exactly (no trading)

---

### Metric: Wealth Transfer Direction

- **Category**: Wealth Dynamics / Mechanism Attribution
- **Definition**: Net wealth change from biased agents (AnchoredTrader, HistoricalAnchor, DispositionTrader) to corrective agents (RationalUpdater, FundamentalAnalyst, ContrarianTrader), validating the expected wealth flow in anchoring markets.
- **Formula**:
  ```
  transfer = Σ ΔW_corrective − Σ ΔW_biased
  ```
- **Function Signature**: `def m_wealth_transfer_direction(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Wealth transfer direction is the ultimate test of whether the anchoring mispricing has real economic consequences: if biased agents lose and rational agents gain, the simulation reproduces the theoretical prediction. A negative transfer would indicate that biased agents are somehow profiting from anchoring, contradicting theory.
- **Interpretation**:
  - transfer > 0: Expected direction — corrective agents capture value from mispricing
  - transfer ≈ 0: No meaningful redistribution (anchoring effect too weak)
  - transfer < 0: Anomalous — biased strategies outperform (possible overcorrection by rational agents)
- **Normal Range**: transfer > 0 in all calibrated scenarios
- **Red Flag**: Persistently negative transfer across multiple runs

---

### Metric: Price Efficiency Ratio

- **Category**: Information Efficiency / Market Quality
- **Definition**: Ratio of price change variance to mispricing variance — measures how much of the available correction opportunity is actually captured by price movements each round.
- **Formula**:
  ```
  PER = Var(ΔP) / Var(F − P_{t-1})
  ```
- **Function Signature**: `def m_price_efficiency_ratio(data, config) -> dict[str, Any]`
- **Derivation Rationale**: In a perfectly efficient market, PER = 1.0 (every round, price moves exactly to correct the existing mispricing). In an anchoring-dominated market, PER << 1 because price adjustments are sluggish — biased agents resist correction. PER >> 1 indicates over-correction (oscillation). This metric captures the fundamental information processing capacity of the market.
- **Academic Calibration Source**:
  - Hasbrouck, J. (1993). Assessing the quality of a security market: A new approach to transaction-cost measurement. *Review of Financial Studies*, 6(1), 191–212. — introduces the information share concept for measuring price discovery efficiency.
  - Chordia, T., Roll, R., & Subrahmanyam, A. (2008). Liquidity and market efficiency. *Journal of Financial Economics*, 87(2), 249–268. — documents that efficiency ratios below 0.5 indicate significant market frictions.
- **Interpretation**:
  - PER < 0.3: Anchoring strongly inhibits price discovery (early persistence phase)
  - PER ∈ [0.3, 0.7]: Partial efficiency — correction happening but slowly
  - PER ∈ [0.7, 1.3]: Near-efficient — prices track fundamental changes
  - PER > 1.5: Over-correction — oscillatory price dynamics
- **Normal Range**: Starts < 0.3 during anchoring phase, rises toward 1.0 during correction
- **Red Flag**: PER > 3.0 (unstable oscillation) or PER = 0 (prices frozen)

---

### Metric: Forecast Error Persistence

- **Category**: Information Efficiency / Learning Speed
- **Definition**: Lag-1 autocorrelation of the deviation (not return) series — measures how persistent forecast errors are, i.e., whether the market "remembers" its mispricing from one round to the next.
- **Formula**:
  ```
  ρ_dev = Corr(dev(t), dev(t−1))
  ```
- **Function Signature**: `def m_forecast_error_persistence(data, config) -> dict[str, Any]`
- **Derivation Rationale**: In rational markets, deviations from fundamental should be unpredictable (random walk around F). High lag-1 autocorrelation of the deviation series indicates that mispricing is persistent and predictable — the defining characteristic of anchoring. As the market corrects, persistence should decline toward zero.
- **Academic Calibration Source**:
  - Campbell, S. D., & Sharpe, S. A. (2009): Documents that analyst forecast errors have first-order autocorrelation > 0.8 at quarterly frequency, declining to < 0.3 at annual frequency. This directly motivates the expectation that ρ_dev > 0.8 during anchoring persistence.
- **Interpretation**:
  - ρ_dev > 0.9: Very strong anchoring — market not learning at all
  - ρ_dev ∈ [0.7, 0.9]: High persistence — typical anchoring phase
  - ρ_dev ∈ [0.3, 0.7]: Moderate persistence — correction underway
  - ρ_dev < 0.3: Low persistence — market approaching efficiency
- **Normal Range**: [0.7, 0.95] over full simulation (dominated by persistence phase)
- **Red Flag**: ρ_dev < 0.3 (anchoring too weak) or ρ_dev = 1.0 exactly (prices frozen)

---

### Metric: Deviation Decay Slope

- **Category**: Information Efficiency / Convergence Rate
- **Definition**: OLS regression slope of |deviation| on round number — a linear approximation to the convergence rate that complements the exponential half-life estimate.
- **Formula**:
  ```
  |dev(t)| = β₀ + β₁ × t + ε(t)
  slope = β₁
  ```
- **Function Signature**: `def m_deviation_decay_slope(data, config) -> dict[str, Any]`
- **Derivation Rationale**: The half-life metric assumes exponential decay, which may not hold exactly in multi-agent simulations with phase transitions. The linear slope provides a model-free measure of convergence speed. A negative slope confirms that mispricing is shrinking over time regardless of the functional form.
- **Interpretation**:
  - slope < −0.001: Meaningful convergence (mispricing shrinking ~0.1% per round)
  - slope ≈ 0: No convergence — price permanently deviates (or oscillates)
  - slope > 0: Divergence — mispricing growing (critical failure)
- **Normal Range**: [−0.005, −0.0005] per round for calibrated anchoring
- **Red Flag**: slope > 0 (diverging) or slope < −0.01 (converging too rapidly)

---

### Metric: Information Share by Strategy

- **Category**: Information Efficiency / Mechanism Attribution
- **Definition**: Fraction of total corrective trading volume contributed by each strategy type — identifies which agents drive price discovery.
- **Formula**:
  ```
  share_s = corrective_vol_s / Σ_s corrective_vol_s
  ```
  where corrective volume = selling when P > F, or buying when P < F.
- **Function Signature**: `def m_information_share_by_strategy(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Not all agents contribute equally to price correction. This metric decomposes the correction process to identify which strategy types are the primary sources of information incorporation, validated against the theoretical expectation that RationalUpdater and FundamentalAnalyst should have the largest corrective shares.
- **Academic Calibration Source**:
  - Hasbrouck, J. (1995). One security, many markets: Determining the contributions to price discovery. *Journal of Finance*, 50(4), 1175–1199. — introduces information share decomposition for multi-agent price formation.
- **Interpretation**:
  - RationalUpdater share > 50%: Expected primary corrector in anchoring scenario
  - FundamentalAnalyst share > 20%: Exponential smoothing provides secondary correction
  - ContrarianTrader share > 10%: Mean-reversion betting contributes to correction
- **Normal Range**: RationalUpdater dominates with 40–60% share
- **Red Flag**: No strategy has share > 10% (correction is purely mechanical via γ-term)

---

### Metric: Value-at-Risk (95%)

- **Category**: Tail Risk / Downside Exposure
- **Definition**: 5th percentile of the return distribution — the worst expected per-round loss at 95% confidence.
- **Formula**:
  ```
  VaR₉₅ = Percentile₅(r(1), r(2), …, r(T))
  ```
- **Function Signature**: `def m_value_at_risk_95(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Anchoring creates a specific tail risk profile — moderate left-tail risk (not extreme crashes, but persistent underperformance during correction). VaR quantifies this tail exposure, confirming that the simulation produces realistic risk levels rather than extreme crashes typical of bubble scenarios.
- **Academic Calibration Source**:
  - Jorion, P. (2006). *Value at Risk: The New Benchmark for Managing Financial Risk*. McGraw-Hill. — VaR at 95% for major equity indices is typically −1.5% to −3% daily.
- **Interpretation**:
  - VaR₉₅ ∈ [−4%, −1%]: Normal moderate risk — expected for anchoring scenarios
  - VaR₉₅ ∈ [−8%, −4%]: Elevated risk — possible during correction phases
  - VaR₉₅ < −10%: Extreme risk — more consistent with crash/bubble than anchoring
- **Normal Range**: [−4%, −1%] per round for calibrated anchoring simulation
- **Red Flag**: VaR₉₅ < −8% (simulation unstable) or VaR₉₅ > −0.5% (negligible risk)

---

### Metric: Conditional Value-at-Risk (CVaR-95)

- **Category**: Tail Risk / Expected Shortfall
- **Definition**: Mean of returns below the VaR-95 threshold — the expected loss given that a tail event occurs.
- **Formula**:
  ```
  CVaR₉₅ = E[r | r ≤ VaR₉₅]
  ```
- **Function Signature**: `def m_conditional_var_95(data, config) -> dict[str, Any]`
- **Derivation Rationale**: CVaR (Expected Shortfall) provides a more complete picture of tail risk than VaR alone. In anchoring markets, CVaR should be only moderately worse than VaR (thin tails), unlike crash scenarios where CVaR >> VaR (fat tails). This validates the "moderate correction, not crash" signature of anchoring.
- **Academic Calibration Source**:
  - Acerbi, C., & Tasche, D. (2002). On the coherence of expected shortfall. *Journal of Banking & Finance*, 26(7), 1487–1503. — establishes CVaR as a coherent risk measure superior to VaR for tail risk assessment.
- **Interpretation**:
  - CVaR/VaR ratio ≈ 1.2–1.5: Thin-tailed (expected for anchoring)
  - CVaR/VaR ratio > 2.0: Fat-tailed (more consistent with crash dynamics)
- **Normal Range**: CVaR₉₅ ∈ [−6%, −1.5%] per round
- **Red Flag**: CVaR₉₅ < −12% (extreme tail events) or CVaR = VaR exactly (insufficient data)

---

### Metric: Herfindahl Volume Concentration (HHI)

- **Category**: Tail Risk / Market Concentration
- **Definition**: Herfindahl-Hirschman Index of trading volume across agents — measures whether one agent dominates the order book or volume is dispersed.
- **Formula**:
  ```
  HHI = Σᵢ (vol_i / Σ_i vol_i)²
  ```
- **Function Signature**: `def m_herfindahl_volume_concentration(data, config) -> dict[str, Any]`
- **Derivation Rationale**: In a well-calibrated multi-agent simulation, trading volume should be distributed across multiple agent types. High concentration (one agent generates most volume) indicates degenerate dynamics and undermines the ecological validity of the anchoring demonstration. HHI near 1/N (where N = number of agents) indicates healthy dispersal.
- **Academic Calibration Source**:
  - Rhoades, S. A. (1993). The Herfindahl-Hirschman Index. *Federal Reserve Bulletin*, 79, 188–189. — standard concentration metric; HHI < 0.15 = unconcentrated, 0.15–0.25 = moderate, > 0.25 = concentrated.
- **Interpretation**:
  - HHI ≈ 1/N (= 1/14 ≈ 0.071 for 14 investors): Well-dispersed
  - HHI ∈ [0.07, 0.20]: Moderate concentration — acceptable
  - HHI > 0.30: One strategy dominates volume — check agent calibration
- **Normal Range**: [0.07, 0.20] for 14-agent anchoring simulation
- **Red Flag**: HHI > 0.40 (single-agent dominance) or all agents have equal volume (unlikely with heterogeneous strategies)

---

### Metric: Strategy Correlation Matrix

- **Category**: Tail Risk / Systemic Risk
- **Definition**: Pairwise Pearson correlation of net demand (buy − sell) between each strategy type per round — measures whether strategies are herding (correlated) or diversifying (anti-correlated).
- **Formula**:
  ```
  corr(s₁, s₂) = Pearson(demand_s₁(t), demand_s₂(t))
  ```
- **Function Signature**: `def m_strategy_correlation_matrix(data, config) -> dict[str, Any]`
- **Derivation Rationale**: High correlation between strategies indicates herding, which amplifies mispricing and creates systemic risk. Anti-correlation between biased and rational strategies confirms that they provide opposing forces as designed. The correlation matrix is the definitive diagnostic for verifying the intended interaction structure.
- **Academic Calibration Source**:
  - Cont, R., & Bouchaud, J.-P. (2000). Herd behavior and aggregate fluctuations in financial markets. *Macroeconomic Dynamics*, 4(2), 170–196. — establishes that herding (correlated strategies) amplifies volatility and mispricing.
- **Interpretation**:
  - AT-RU correlation < 0: Expected — anchoring and rational forces oppose each other
  - AT-HA correlation > 0: Expected — both biased strategies reinforce mispricing
  - MT-AT correlation > 0: Momentum amplifies anchoring (mild positive expected)
  - NT-all correlation ≈ 0: Noise is uncorrelated with all strategies (by design)
- **Normal Range**: |corr| < 0.7 for all pairs (no extreme herding)
- **Red Flag**: Any pair with |corr| > 0.9 (strategies are virtually identical — redundant)

---

### §2.2 Price Dynamics — Extended Metrics

#### Metric: Half-Life (Threshold-Crossing Method)

- **Category**: Price Dynamics / Temporal Convergence
- **Definition**: The first round at which |deviation(t)| falls below 50% of its initial value, providing a model-free estimate of anchoring persistence without assuming exponential decay.
- **Formula**:
  ```
  half_life_threshold = min{t : |dev(t)| < |dev(1)| / 2}
  ```
- **Function Signature**: `def m_half_life_threshold(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Unlike the OLS exponential fit (half_life_fitted), the threshold method makes no distributional assumptions. It directly answers "when does the mispricing halve?" — robust to non-exponential decay paths common in multi-agent systems with phase transitions. Particularly useful when agents create regime shifts that violate the linear restoring force assumption.
- **Academic Calibration Source**:
  - Campbell, S. D., & Sharpe, S. A. (2009): Documents forecast error reduction timelines consistent with 20–60 round equivalent crossings.
  - Fama, E. F., & French, K. R. (1988): Mean-reversion half-life framework for equity prices.
- **Interpretation**:
  - threshold < fitted half-life: Convergence accelerates after initial slow phase (convex decay)
  - threshold > fitted half-life: Convergence decelerates (concave decay — anchoring reinforcement)
  - threshold = NaN: Deviation never reaches 50% of initial — strong anchoring throughout
- **Normal Range**: [15, 70] rounds (slightly wider than fitted due to noise sensitivity)
- **Red Flag**: threshold = NaN (never crosses) or threshold < 5 (trivially rational)

---

#### Metric: Return Skewness

- **Category**: Price Dynamics / Distribution Shape
- **Definition**: Third standardised moment of the per-round return distribution, measuring asymmetry. Negative skewness indicates larger downside moves (correction from anchored high); positive skewness indicates larger upside moves.
- **Formula**:
  ```
  skewness = (1/T) × Σ_t [(r(t) − r̄) / σ_r]³
  ```
- **Function Signature**: `def m_return_skewness(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Anchoring creates a specific skewness signature: during the persistence phase, returns are slightly positively skewed (small upward drift); during correction, returns become negatively skewed (larger downward moves). Over the full simulation, net skewness should be mildly negative (the correction moves are larger in magnitude than the drift).
- **Academic Calibration Source**:
  - Cont, R. (2001). Empirical properties of asset returns: Stylized facts and statistical issues. *Quantitative Finance*, 1(2), 223–236. https://doi.org/10.1080/713665670 — documents negative skewness (−0.1 to −0.5) as a stylized fact of equity returns.
- **Interpretation**:
  - skewness ∈ [−0.5, 0.0]: Expected for anchoring with gradual correction
  - skewness < −1.0: Large correction event dominates (possible over-correction)
  - skewness > +0.5: Unusual — anchoring creating sustained upward jumps
- **Normal Range**: [−0.8, +0.3] for 200-round anchoring simulation
- **Red Flag**: |skewness| > 2.0 (extreme non-normality; check NoiseTrader or MomentumTrader)

---

#### Metric: Return Kurtosis (Excess)

- **Category**: Price Dynamics / Tail Heaviness
- **Definition**: Excess fourth standardised moment of returns (excess kurtosis = kurtosis − 3), measuring the propensity for extreme moves relative to a Gaussian distribution.
- **Formula**:
  ```
  excess_kurtosis = [(1/T) × Σ_t ((r(t) − r̄) / σ_r)⁴] − 3
  ```
- **Function Signature**: `def m_return_kurtosis(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Multi-agent heterogeneity creates fat tails (positive excess kurtosis) because different agent types activate at different price levels, creating regime-dependent return distributions. Anchoring specifically creates moderate kurtosis — not the extreme kurtosis of crash-prone bubble markets, but heavier tails than pure noise.
- **Academic Calibration Source**:
  - Cont, R. (2001): Documents excess kurtosis of 3–50 for daily equity returns across markets. For a 200-round simulation with moderate heterogeneity, excess kurtosis of 1–5 is expected.
  - Mandelbrot, B. (1963). The variation of certain speculative prices. *Journal of Business*, 36(4), 394–419. — foundational paper establishing fat tails in financial returns.
- **Interpretation**:
  - excess_kurtosis ∈ [0, 1]: Near-Gaussian — noise dominates (weak heterogeneity)
  - excess_kurtosis ∈ [1, 5]: Moderate fat tails — expected for anchoring scenario
  - excess_kurtosis > 10: Extreme tails — possible instability
- **Normal Range**: [0.5, 6.0] for anchoring-populated multi-agent simulation
- **Red Flag**: excess_kurtosis > 15 (unstable) or < 0 (platykurtic — homogeneous agents)

---

#### Metric: Variance Ratio (Lo & MacKinlay)

- **Category**: Price Dynamics / Random Walk Test
- **Definition**: Ratio of multi-period return variance to single-period return variance, scaled by the holding period. Tests whether log prices follow a random walk — a VR significantly different from 1.0 rejects the random walk hypothesis.
- **Formula**:
  ```
  VR(q) = Var(r_t(q)) / [q × Var(r_t(1))]
  where r_t(q) = log(P(t)) − log(P(t−q)) is the q-period log return
  ```
  Computed at q ∈ {2, 4, 8} following Lo & MacKinlay (1988).
- **Function Signature**: `def m_variance_ratio_lo_mackinlay(data, config) -> dict[str, Any]`
- **Derivation Rationale**: VR > 1 indicates positive autocorrelation (momentum/persistence) — expected during the anchoring phase when prices drift slowly away from the anchor. VR < 1 indicates mean-reversion — expected during the correction phase. The multi-period structure (q = 2, 4, 8) captures different time-scale dynamics of the anchoring phenomenon.
- **Academic Calibration Source**:
  - Lo, A. W., & MacKinlay, A. C. (1988). Stock market prices do not follow random walks: Evidence from a simple specification test. *Review of Financial Studies*, 1(1), 41–66. https://doi.org/10.1093/rfs/1.1.41 — VR(q=2) ≈ 1.17 for US weekly returns.
  - Lo, A. W., & MacKinlay, A. C. (1989). The size and power of the variance ratio test. *Review of Financial Studies*, 2(2), 187–217. — establishes that n ≥ 8q observations are needed for adequate power.
- **Interpretation**:
  - VR(q) ∈ [0.9, 1.1]: Cannot reject random walk (noise dominant)
  - VR(q) ∈ [1.1, 1.5]: Mild persistence — consistent with anchoring-induced drift
  - VR(q) > 1.5: Strong persistence — anchoring extremely dominant
  - VR(q) < 0.8: Strong mean-reversion — correction phase dominates
- **Normal Range**: VR(2) ∈ [1.0, 1.3]; VR(4) ∈ [0.9, 1.4]; VR(8) ∈ [0.8, 1.5]
- **Red Flag**: VR(q) > 2.0 or VR(q) < 0.5 (extreme departure from random walk)

---

### §2.3 Anchoring-Specific — Extended Metrics

#### Metric: Anchor Dispersion

- **Category**: Anchoring-Specific / Cross-Agent Heterogeneity
- **Definition**: Standard deviation of perceived_target values across all AnchoredTrader instances within a given round, measuring whether biased agents converge toward the same anchor or diverge.
- **Formula**:
  ```
  dispersion(t) = std({perceived_target_i(t)} for all AnchoredTrader i)
  ```
- **Function Signature**: `def m_anchor_dispersion(data, config) -> dict[str, Any]`
- **Derivation Rationale**: In a well-calibrated simulation, all AnchoredTrader instances should share the same anchor (initial_price = 105) and adjustment factor (α = 0.3), producing zero dispersion. Non-zero dispersion arises only if agents have heterogeneous parameters or if instance-specific noise perturbs perceived targets. High dispersion indicates that the anchoring mechanism is not monolithic — useful for LLM variants where perceived targets may drift.
- **Academic Calibration Source**:
  - Tversky, A., & Kahneman, D. (1974): Individual-level anchor effects show inter-subject variability; standard deviation of adjustment ≈ 30% of mean adjustment in lab settings.
- **Interpretation**:
  - dispersion = 0: Homogeneous anchoring (expected for Rule variant with identical parameters)
  - dispersion ∈ (0, 2%]: Mild heterogeneity (acceptable for LLM variants)
  - dispersion > 5%: High disagreement among biased agents — anchoring mechanism fragmenting
- **Normal Range**: [0, 3%] for Rule variant; [0, 8%] for LLM variant
- **Red Flag**: dispersion > 10% (anchoring agents behaving incoherently)

---

#### Metric: Under-Revision Ratio

- **Category**: Anchoring-Specific / Persistence Verification
- **Definition**: Fraction of simulation rounds during which the price deviation retains the same sign as the initial deviation, measuring how long the anchoring-induced directional bias persists.
- **Formula**:
  ```
  under_revision_ratio = |{t : sign(P(t) - F) = sign(P(1) - F)}| / T
  ```
- **Function Signature**: `def m_under_revision_ratio(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Campbell & Sharpe (2009) document that analyst forecasts maintain the same directional error for 50–80% of forecast periods (under-revision). This metric directly replicates their methodology: if anchoring persists, the market price stays above F (same sign as initial 5% overvaluation) for the majority of rounds.
- **Academic Calibration Source**:
  - Campbell, S. D., & Sharpe, S. A. (2009): ~50% under-revision rate in quarterly forecasts; simulation target [0.5, 0.85] for 200-round runs.
- **Interpretation**:
  - ratio > 0.8: Very strong anchoring — price almost never crosses fundamental
  - ratio ∈ [0.5, 0.8]: Moderate anchoring persistence — expected target range
  - ratio < 0.5: Anchoring collapses early (rapid correction)
- **Normal Range**: [0.50, 0.85]
- **Red Flag**: ratio < 0.3 (anchoring ineffective) or ratio > 0.95 (no correction occurring)

---

#### Metric: Regime Transition Lag

- **Category**: Anchoring-Specific / Convergence Timing
- **Definition**: The first round at which |deviation| falls below 1% — the point where the market has essentially corrected the anchoring-induced mispricing.
- **Formula**:
  ```
  regime_lag = min{t : |dev(t)| < 0.01}
  ```
- **Function Signature**: `def m_regime_transition_lag(data, config) -> dict[str, Any]`
- **Derivation Rationale**: While half-life measures the 50% decay point, regime_transition_lag measures the full correction point (below 1% deviation). This completes the convergence picture: half-life tells how fast the mispricing shrinks; regime lag tells when it’s effectively gone. In a 200-round simulation, we expect regime transition between rounds 80–180.
- **Academic Calibration Source**:
  - Campbell & Sharpe (2009): Full forecast error correction typically requires 3–6 quarters — equivalent to 75–150 simulation rounds.
- **Interpretation**:
  - lag < 50: Rapid correction (strong γ or many RationalUpdaters)
  - lag ∈ [80, 180]: Normal convergence for calibrated anchoring
  - lag = NaN (never reached): Anchoring persists throughout simulation
- **Normal Range**: [60, 180] rounds for 200-round simulation
- **Red Flag**: lag = NaN (never converges) or lag < 20 (anchoring trivial)

---

#### Metric: Price-to-Anchor Distance Time-Series

- **Category**: Anchoring-Specific / Anchor Proximity
- **Definition**: Per-round percentage distance between the market price and the canonical anchor price (initial_price = 105), measuring how far the market has moved from the original anchor reference point.
- **Formula**:
  ```
  distance(t) = (P(t) − anchor) / anchor × 100%
  ```
- **Function Signature**: `def m_price_to_anchor_distance_ts(data, config) -> dict[str, Any]`
- **Derivation Rationale**: The deviation metric measures distance from fundamental; this metric measures distance from the anchor itself. Together they decompose the price position: a price exactly at the anchor has zero anchor-distance but +5% fundamental deviation. As the market corrects toward F, anchor-distance becomes increasingly negative. This dual-reference decomposition reveals whether price is moving toward fundamental or simply drifting from the anchor.
- **Academic Calibration Source**:
  - Tversky & Kahneman (1974): Anchoring persists when stimuli remain close to the anchor; drift away from anchor weakens the bias. The distance time-series tests whether the anchoring effect weakens monotonically with price-anchor separation.
- **Interpretation**:
  - distance ≈ 0: Price at anchor — anchoring agents holding price near reference
  - distance < −5%: Price well below anchor, approaching fundamental — correction phase
  - distance > 0: Price above anchor — momentum overshoot or additional upward pressure
- **Normal Range**: distance evolves from ≈0% (round 1) to ≈−5% (round 200) as P converges to F
- **Red Flag**: distance persistently > +5% (diverging from both anchor and fundamental)

---

### §2.4 Agent Behaviour — Extended Metrics

#### Metric: Agent Action Frequency

- **Category**: Agent Behaviour / Activity Profile
- **Definition**: Per-agent counts of buy, sell, and hold actions across all simulation rounds, profiling each agent's decision pattern and engagement level.
- **Formula**:
  ```
  freq_i = {buy: |{t: action_i(t) = buy}|,
            sell: |{t: action_i(t) = sell}|,
            hold: |{t: action_i(t) = hold}|}
  ```
- **Function Signature**: `def m_agent_action_frequency(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Volume alone does not distinguish between agents who trade frequently in small sizes vs. agents who trade rarely in large blocks. Action frequency reveals the decision-making tempo of each agent type: AnchoredTrader should buy frequently (supporting anchor); RationalUpdater should sell frequently (correcting); NoiseTrader should show balanced random activity; LiquidityProvider should show high hold frequency (quoting but not always executing).
- **Academic Calibration Source**:
  - Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. — distinguishes informed (infrequent, large) from uninformed (frequent, small) trading patterns.
- **Interpretation**:
  - AnchoredTrader: buy freq > sell freq (supporting the anchor)
  - RationalUpdater: sell freq > buy freq when P > F; buy freq > sell freq when P < F
  - NoiseTrader: approximately balanced buy/sell with high activity rate
  - LiquidityProvider: high hold frequency (market-making with selective execution)
- **Normal Range**: All agents should have total actions = T (200 rounds); hold fraction < 0.8 for active agents
- **Red Flag**: Any active agent with hold fraction > 0.95 (effectively silent) or buy = sell = 0

---

#### Metric: Agent Net Position Time-Series

- **Category**: Agent Behaviour / Position Dynamics
- **Definition**: Cumulative net position (shares held) per agent over time, revealing inventory accumulation and liquidation patterns.
- **Formula**:
  ```
  position_i(t) = position_i(t−1) + quantity_i(t) × sign(action_i(t))
  where sign(buy) = +1, sign(sell) = −1, sign(hold) = 0
  ```
- **Function Signature**: `def m_agent_net_position_ts(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Position evolution reveals the economic exposure each agent type takes in response to the anchoring phenomenon. AnchoredTrader should accumulate long positions (buying into the overvaluation); RationalUpdater should build short positions (selling into overvaluation) then flatten as price corrects. The shape of the position curve validates that agents respond to mispricing as their strategy dictates.
- **Academic Calibration Source**:
  - Glosten & Milgrom (1985): Market makers maintain bounded inventory; directional traders accumulate until their signal expires.
- **Interpretation**:
  - AnchoredTrader: monotonically increasing position (persistent buying)
  - RationalUpdater: initially short (selling into overvaluation), flattening during correction
  - MomentumTrader: follows recent price direction (positive in persistence, negative in correction)
  - NoiseTrader: random walk around zero
- **Normal Range**: |position_i(T)| < initial_cash / P(T) for all agents (no unlimited leverage)
- **Red Flag**: Any agent position exceeds 5× initial endowment equivalent (unrealistic leverage)

---

#### Metric: Agent Terminal PnL

- **Category**: Agent Behaviour / Performance Attribution
- **Definition**: Per-agent mark-to-market profit-and-loss at the final round: (terminal_wealth − initial_wealth), attributing economic gains and losses to each strategy.
- **Formula**:
  ```
  PnL_i = W_i(T) − W_i(0)
        = [cash_i(T) + position_i(T) × P(T)] − [cash_i(0) + position_i(0) × P(0)]
  ```
- **Function Signature**: `def m_agent_pnl_terminal(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Terminal PnL is the ultimate performance measure for evaluating whether the theoretical prediction holds: rational agents should profit (positive PnL) by trading against the mispricing, while biased agents should lose (negative PnL) by maintaining overvalued positions. This validates De Long et al.’s (1990) result that noise/biased traders lose to rational traders in expectation.
- **Academic Calibration Source**:
  - De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *JPE*, 98(4), 703–738. — biased traders lose on average.
  - De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. — contrarian strategy earns positive alpha.
- **Interpretation**:
  - RationalUpdater PnL > 0: Expected — profited from selling overvalued assets
  - AnchoredTrader PnL < 0: Expected — bought and held overvalued assets
  - ContrarianTrader PnL > 0: Expected — mean-reversion betting profitable
- **Normal Range**: |PnL_i| < 30% of initial_wealth for calibrated parameters
- **Red Flag**: Any agent PnL > +100% (unrealistic leverage gains) or total PnL ≠ 0 (conservation violation)

---

#### Metric: Agent Sharpe Ratio (Terminal)

- **Category**: Agent Behaviour / Risk-Adjusted Performance
- **Definition**: Per-agent ratio of mean round-level PnL to its standard deviation, measuring risk-adjusted strategy performance.
- **Formula**:
  ```
  Sharpe_i = mean(pnl_i(t)) / std(pnl_i(t))
  where pnl_i(t) = W_i(t) − W_i(t−1)
  ```
- **Function Signature**: `def m_agent_sharpe_terminal(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Raw PnL can be positive due to either skill or luck (high variance). The Sharpe ratio distinguishes consistent performers (high Sharpe) from lucky gamblers (high PnL, high variance, low Sharpe). RationalUpdater should show the highest Sharpe (consistent small gains from corrective trading); NoiseTrader should show Sharpe ≈ 0 (random); MomentumTrader may show high PnL but moderate Sharpe (variable returns).
- **Academic Calibration Source**:
  - Sharpe, W. F. (1966). Mutual fund performance. *Journal of Business*, 39(1), 119–138. — original reward-to-variability ratio.
  - For simulation: annualised Sharpe > 1.0 (round-level Sharpe > 0.07 for 200 rounds) indicates consistent alpha.
- **Interpretation**:
  - Sharpe > 0.1: Consistent outperformance (expected for RationalUpdater)
  - Sharpe ≈ 0: No systematic edge (expected for NoiseTrader)
  - Sharpe < −0.05: Consistent underperformance (expected for AnchoredTrader)
- **Normal Range**: [−0.15, +0.20] for round-level Sharpe ratios
- **Red Flag**: |Sharpe| > 0.5 (unrealistically consistent; check data integrity)

---

#### Metric: Silent Agent Count

- **Category**: Agent Behaviour / System Health
- **Definition**: Number of agents that never executed a trade (zero total volume) across the entire simulation, serving as a critical system health diagnostic.
- **Formula**:
  ```
  silent_count = |{i : total_volume_i = 0}|
  ```
- **Function Signature**: `def m_silent_agent_count(data, config) -> dict[str, Any]`
- **Derivation Rationale**: A silent agent indicates either a bug (agent never activated), an overly restrictive threshold (perceived deviation too small to trigger action), or a cash/position constraint preventing any trade. In a well-calibrated 200-round simulation with heterogeneous agents, all agents should trade at least once. Silent agents undermine the ecological validity of the multi-agent demonstration.
- **Academic Calibration Source**:
  - Not calibrated to empirical literature — this is a simulation health metric. Expected value: 0 silent agents for all variants.
- **Interpretation**:
  - silent_count = 0: All agents active — simulation functioning as designed
  - silent_count = 1–2: Minor issue — check threshold parameters for inactive agents
  - silent_count > 3: Critical — significant portion of agent ecosystem non-functional
- **Normal Range**: 0 (expected)
- **Red Flag**: silent_count > 0 triggers advisory warning in validation output

---

### §2.5 Microstructure Metrics

#### Metric: Order Imbalance Time-Series

- **Category**: Microstructure / Demand Pressure
- **Definition**: Per-round ratio of net signed demand to gross volume, measuring the directional pressure on price from order flow asymmetry.
- **Formula**:
  ```
  imbalance(t) = (buy_vol(t) − sell_vol(t)) / (buy_vol(t) + sell_vol(t))
  ```
  Values range from −1 (all sell) to +1 (all buy); 0 = balanced.
- **Function Signature**: `def m_order_imbalance_ts(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Order imbalance is the most direct measure of demand-side pressure on price. In anchoring markets, persistent positive imbalance (buy pressure) during the persistence phase reflects biased agents supporting the overvalued price. The transition from positive to negative imbalance marks the correction onset. Chordia et al. (2002) show that order imbalance predicts short-term returns and captures institutional demand shocks.
- **Academic Calibration Source**:
  - Chordia, T., Roll, R., & Subrahmanyam, A. (2002). Order imbalance, liquidity, and market returns. *Journal of Financial Economics*, 65(1), 111–130. https://doi.org/10.1016/S0304-405X(02)00136-8 — order imbalance predicts 1-day returns with mean imbalance |μ| ≈ 0.05–0.15.
- **Interpretation**:
  - mean imbalance > +0.1: Persistent buy pressure (anchoring agents dominant)
  - mean imbalance ≈ 0: Balanced market (correction complete or noise-dominated)
  - mean imbalance < −0.1: Persistent sell pressure (correction/rational agents dominant)
- **Normal Range**: mean |imbalance| ∈ [0.02, 0.25] for heterogeneous agent simulation
- **Red Flag**: |imbalance| = 1 for any round (one-sided market — no counterparty)

---

#### Metric: Signed Volume Autocorrelation

- **Category**: Microstructure / Order Flow Persistence
- **Definition**: Lag-1 autocorrelation of the net signed demand series, measuring whether buy/sell pressure persists across rounds.
- **Formula**:
  ```
  signed_vol_AC1 = Corr(net_demand(t), net_demand(t−1))
  where net_demand(t) = buy_vol(t) − sell_vol(t)
  ```
- **Function Signature**: `def m_signed_volume_autocorr(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Positive signed volume autocorrelation indicates that order flow is persistent — the same directional pressure continues across rounds. In anchoring markets, this is expected during the persistence phase (AnchoredTrader consistently buys). Negative autocorrelation suggests alternating pressure (oscillation). Hasbrouck (1991) demonstrates that trade direction persistence is a key microstructure signature.
- **Academic Calibration Source**:
  - Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179–207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x — signed trade autocorrelation ≈ 0.1–0.4 in equity markets.
- **Interpretation**:
  - AC > 0.3: Strong persistence — anchoring-driven sustained buying
  - AC ∈ [0.0, 0.3]: Mild persistence — normal market
  - AC < 0: Alternating pressure — suggests oscillatory dynamics
- **Normal Range**: [0.0, 0.5] for anchoring-dominant periods; [−0.2, 0.2] for correction phase
- **Red Flag**: |AC| > 0.7 (order flow frozen in one direction; check agent diversity)

---

#### Metric: Corrective-to-Biased Volume Ratio

- **Category**: Microstructure / Force Balance
- **Definition**: Ratio of RationalUpdater corrective trading volume to combined AnchoredTrader + HistoricalAnchor biased volume — directly measures the relative strength of corrective vs. biased forces.
- **Formula**:
  ```
  ratio = volume_RU / (volume_AT + volume_HA)
  ```
- **Function Signature**: `def m_corrective_to_biased_volume_ratio(data, config) -> dict[str, Any]`
- **Derivation Rationale**: This metric operationalises Shleifer & Vishny’s (1997) "limits of arbitrage" concept: rational corrective agents (RU) face finite resources and must overcome biased agents’ combined volume. A ratio < 1 means biased agents dominate volume-wise; a ratio > 1 means corrective agents trade more actively. The balance between these forces determines convergence speed.
- **Academic Calibration Source**:
  - Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x — demonstrates that rational arbitrage is resource-constrained.
- **Interpretation**:
  - ratio < 0.5: Biased agents strongly dominant — slow correction expected
  - ratio ∈ [0.5, 1.5]: Balanced — gradual correction
  - ratio > 2.0: Corrective agents dominant — fast correction
- **Normal Range**: [0.3, 2.0] for calibrated 14-agent anchoring simulation
- **Red Flag**: ratio < 0.1 (RU effectively inactive) or ratio > 5 (biased agents non-functional)

---

#### Metric: Momentum-Anchoring Coupling

- **Category**: Microstructure / Strategy Interaction
- **Definition**: Pearson correlation between AnchoredTrader net demand and MomentumTrader net demand per round, measuring whether momentum amplifies or counteracts anchoring.
- **Formula**:
  ```
  coupling = Corr(demand_AT(t), demand_MT(t))
  ```
- **Function Signature**: `def m_momentum_anchoring_coupling(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Hong & Stein (1999) show that momentum traders can amplify or dampen existing mispricings depending on their position relative to the mispricing lifecycle. During the persistence phase, MomentumTrader should align with AnchoredTrader (both buying into the drift), creating positive coupling. During correction, MomentumTrader reverses (selling into the decline), creating negative coupling. The net correlation over all rounds captures the degree to which momentum amplifies anchoring.
- **Academic Calibration Source**:
  - Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum, and overreaction in asset markets. *Journal of Finance*, 54(6), 2143–2184. https://doi.org/10.1111/0022-1082.00184 — momentum traders interact with slow-information-diffusion (analogous to anchoring).
- **Interpretation**:
  - coupling > 0.3: Momentum amplifying anchoring — persistence enhanced
  - coupling ∈ [−0.1, 0.3]: Weak coupling — momentum neutral to anchoring
  - coupling < −0.2: Momentum opposing anchoring — correction accelerated
- **Normal Range**: [−0.2, 0.5] for full-simulation correlation
- **Red Flag**: coupling > 0.8 (strategies effectively identical) or coupling < −0.5 (extreme oscillation risk)

---

### §2.6 Statistical Inference Metrics

#### Metric: MAD Block Bootstrap 95% CI

- **Category**: Statistical Inference / Confidence Estimation
- **Definition**: Moving-block bootstrap confidence interval for the Mean Absolute Deviation (MAD), providing uncertainty quantification for the primary anchoring magnitude metric.
- **Formula**:
  ```
  1. Choose block length b = ⌈n^(1/3)⌉ (Politis & Romano optimal rule)
  2. Draw K = 2000 bootstrap replicates by randomly selecting ⌈n/b⌉ blocks
  3. Compute MAD for each replicate
  4. CI = [percentile_2.5(MAD*), percentile_97.5(MAD*)]
  ```
- **Function Signature**: `def m_mad_block_bootstrap_ci_95(data, config) -> dict[str, Any]`
- **Derivation Rationale**: A single-point MAD estimate has no error bar. Serial dependence in the deviation series (caused by the persistent anchoring mechanism) violates IID assumptions required by standard bootstrap. The moving-block bootstrap preserves within-block serial correlation, yielding valid confidence intervals. The block length b = n^(1/3) minimises MSE for dependent data (Politis & Romano, 1994).
- **Academic Calibration Source**:
  - Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313. https://doi.org/10.1080/01621459.1994.10476870 — establishes moving-block bootstrap for serially dependent time series.
  - Künsch, H. R. (1989). The jackknife and the bootstrap for general stationary observations. *Annals of Statistics*, 17(3), 1217–1241. — theoretical justification for block resampling.
- **Interpretation**:
  - CI entirely within [3%, 10%]: Anchoring calibration confirmed with 95% confidence
  - CI lower bound > 10%: Significant overcalibration
  - CI upper bound < 3%: Anchoring too weak (cannot reject no-anchoring null)
- **Normal Range**: CI width < 4% (tight estimate); CI_low > 2% and CI_high < 12%
- **Red Flag**: CI width > 8% (insufficient precision; need more rounds or replicates)

---

#### Metric: Half-Life Block Bootstrap 95% CI

- **Category**: Statistical Inference / Persistence Uncertainty
- **Definition**: Moving-block bootstrap confidence interval for the fitted exponential half-life, quantifying uncertainty in the convergence speed estimate.
- **Formula**:
  ```
  1. Block length b = ⌈n^(1/3)⌉
  2. Draw K = 2000 replicates; for each, fit OLS on log|dev| vs. round
  3. Compute half_life = −ln(2)/slope for each valid replicate
  4. CI = [percentile_2.5(HL*), percentile_97.5(HL*)]
  ```
- **Function Signature**: `def m_half_life_block_bootstrap_ci_95(data, config) -> dict[str, Any]`
- **Derivation Rationale**: The half-life estimate is highly sensitive to the tail behaviour of the deviation series. A few noisy late-round observations can shift the OLS slope significantly. The bootstrap CI reveals whether the half-life is precisely estimated or merely a rough central tendency. Replicates where the slope is positive or zero produce NaN half-lives (filtered as invalid).
- **Academic Calibration Source**:
  - Politis & Romano (1994): Block bootstrap methodology (same as MAD CI).
  - Campbell & Sharpe (2009): Expected half-life 20–60 rounds provides the calibration target against which the CI is validated.
- **Interpretation**:
  - CI within [15, 80]: Well-estimated half-life consistent with calibration
  - CI lower bound < 5: Some replicates show near-instant correction (noise-driven)
  - CI upper bound > 150: Some replicates show very slow or no convergence
- **Normal Range**: CI width < 40 rounds; valid_replicates > 90% of K
- **Red Flag**: valid_replicates < 50% (log-deviation series too noisy for exponential fit)

---

#### Metric: Ljung-Box Returns P-Value

- **Category**: Statistical Inference / Autocorrelation Test
- **Definition**: Ljung-Box Q-statistic testing the null hypothesis that return autocorrelations at lags 1–10 are jointly zero — i.e., testing whether returns are serially independent.
- **Formula**:
  ```
  Q(m) = n(n+2) × Σ_{k=1}^{m} [ρ̂(k)² / (n−k)]
  H₀: ρ(1) = ρ(2) = … = ρ(m) = 0  (returns are IID)
  p-value from χ²(m) distribution
  ```
  Uses m = 10 lags following standard practice.
- **Function Signature**: `def m_ljung_box_returns_pvalue(data, config) -> dict[str, Any]`
- **Derivation Rationale**: In an efficient market, returns should be unpredictable (IID). Anchoring creates predictable return patterns (positive drift during persistence, negative drift during correction). Rejecting H₀ (p < 0.05) confirms that anchoring generates statistically detectable serial dependence in returns — the market is not efficient in the weak-form sense.
- **Academic Calibration Source**:
  - Ljung, G. M., & Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika*, 65(2), 297–303. https://doi.org/10.1093/biomet/65.2.297 — standard portmanteau test for serial correlation.
  - For anchoring simulation: expect p < 0.05 (reject null) during persistence phase, p > 0.10 (cannot reject) during convergence.
- **Interpretation**:
  - p < 0.01: Strong evidence of serial dependence (anchoring confirmed)
  - p ∈ [0.01, 0.05]: Moderate evidence — consistent with mild anchoring
  - p > 0.10: No evidence of serial dependence — market appears efficient
- **Normal Range**: p ∈ [0.001, 0.10] for full-simulation return series
- **Red Flag**: p > 0.50 (no detectable anchoring signal) or Q-statistic < 5 (very weak dependence)

---

#### Metric: ADF Unit Root P-Value

- **Category**: Statistical Inference / Stationarity Test
- **Definition**: Augmented Dickey-Fuller test statistic for the price level series, testing whether prices have a unit root (random walk) or are mean-reverting (stationary around fundamental).
- **Formula**:
  ```
  ΔP(t) = α + βP(t−1) + ε(t)
  H₀: β = 0 (unit root / random walk)
  H₁: β < 0 (stationary / mean-reverting)
  t-statistic compared to Dickey-Fuller critical values
  ```
  Uses ADF(0) (no lagged differences) given short series.
- **Function Signature**: `def m_adf_unit_root_pvalue(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Anchoring creates a price path that is neither pure random walk nor immediately stationary: it’s a slowly mean-reverting process. The ADF test quantifies where on this spectrum the simulation falls. Rejecting the unit root hypothesis confirms that the γ-term and rational agents create statistically detectable mean-reversion, validating the convergence mechanism. Failure to reject suggests that within the simulation horizon, the anchoring effect is too strong for detectable reversion.
- **Academic Calibration Source**:
  - Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427–431. https://doi.org/10.1080/01621459.1979.10482531
  - MacKinnon, J. G. (1991). Critical values for cointegration tests. In R. F. Engle & C. W. J. Granger (Eds.), *Long-Run Economic Relationships*. Oxford University Press. — tabulated critical values used for approximate p-value.
- **Interpretation**:
  - p < 0.05: Reject unit root — prices are stationary (mean-reverting confirmed)
  - p ∈ [0.05, 0.20]: Borderline — slow mean-reversion (consistent with long half-life)
  - p > 0.20: Cannot reject unit root — prices appear non-stationary within simulation horizon
- **Normal Range**: p ∈ [0.01, 0.20] for 200-round anchoring simulation with γ = 0.01
- **Red Flag**: p > 0.50 (no detectable mean-reversion; γ may be too low) or p < 0.001 (instant convergence)

---

### §2.7 Phase Decomposition Metrics

#### Metric: Phase Assignment Time-Series

- **Category**: Phase Decomposition / Lifecycle Identification
- **Definition**: Per-round assignment of the simulation state to one of four phases (Anchor Establishment, Persistent Mispricing, Slow Correction, Convergence) based on the quantitative criteria defined in §4.
- **Formula**:
  ```
  phase(t) = {
    1 (Establishment):  t ≤ 10 and deviation stabilising
    2 (Persistence):    mean(dev[t-4:t]) > 0.02
    3 (Correction):     deviation declining for 5+ rounds
    4 (Convergence):    |deviation| < 0.01 for 5+ rounds
  }
  ```
  Applied sequentially with transitions requiring sustained conditions.
- **Function Signature**: `def m_phase_assignment_ts(data, config) -> dict[str, Any]`
- **Derivation Rationale**: The anchoring lifecycle is not a monotonic decay — it has distinct regimes with qualitatively different dynamics (establishment, persistence, correction, convergence). Phase decomposition enables per-phase metric computation (see per_phase_metrics_table), validation of expected phase durations against §4 targets, and identification of phase transition failures.
- **Academic Calibration Source**:
  - Campbell & Sharpe (2009): Documents a multi-phase pattern of forecast error emergence, persistence, and eventual correction over quarterly cycles.
  - Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357–384. — regime-switching models as theoretical motivation for discrete phase assignments.
- **Interpretation**:
  - Phase 1 duration ≈ 10 rounds: Normal initialisation
  - Phase 2 duration 30–60 rounds: Expected persistence phase
  - Phase 3 duration 30–80 rounds: Gradual correction
  - Phase 4 reached before round 180: Successful convergence
- **Normal Range**: All 4 phases present; Phase 2 > Phase 1; Phase 4 begins before round 180
- **Red Flag**: Only 1–2 phases detected (no lifecycle); Phase 2 lasts entire simulation (no correction)

---

#### Metric: Per-Phase Metrics Table

- **Category**: Phase Decomposition / Conditional Statistics
- **Definition**: Within-phase summary statistics (MAD, volatility, mean return) for each detected phase, enabling comparison of market behaviour across lifecycle stages.
- **Formula**:
  ```
  For each phase p:
    MAD_p = mean(|deviation(t)|) for t in phase p
    vol_p = std(returns(t)) for t in phase p
    ret_p = mean(returns(t)) for t in phase p
  ```
- **Function Signature**: `def m_per_phase_metrics_table(data, config) -> dict[str, Any]`
- **Derivation Rationale**: Aggregate metrics over the full simulation mix together different market regimes, potentially obscuring important dynamics. Per-phase decomposition reveals that MAD is highest in Phase 2 (persistence), volatility may spike at phase transitions, and mean returns are negative in Phase 3 (correction). This conditional analysis validates the theoretical predictions for each lifecycle stage independently.
- **Academic Calibration Source**:
  - Hamilton (1989): Regime-switching analysis demonstrates that financial time series exhibit different statistical properties across regimes.
  - For anchoring simulation: Phase 2 MAD > Phase 3 MAD > Phase 4 MAD (monotonically decreasing as correction proceeds).
- **Interpretation**:
  - Phase 2 MAD > 3%: Anchoring active (expected)
  - Phase 3 MAD < Phase 2 MAD: Correction proceeding (expected)
  - Phase 4 MAD < 1%: Convergence achieved (expected)
  - Phase 3 volatility > Phase 2 volatility: Correction creates turbulence (common)
- **Normal Range**: MAD decreasing across phases 2→3→4; volatility stable or mildly elevated in Phase 3
- **Red Flag**: Phase 4 MAD > 2% (convergence not achieved) or Phase 2 MAD < Phase 3 MAD (counter-intuitive pattern)

---


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

### Dimension 6: Wealth Dynamics and Redistribution

- **Purpose**: Track how anchoring-induced mispricing redistributes wealth between biased and rational agents
- **Metrics Used**: Agent terminal wealth, Gini coefficient, wealth transfer direction
- **Visualization**: Bar chart of terminal wealth by strategy type; Gini annotation; wealth transfer arrow diagram
- **Expected Pattern**: RationalUpdater and FundamentalAnalyst accumulate wealth by selling into overvaluation; AnchoredTrader and HistoricalAnchor lose wealth by buying at inflated prices; DispositionTrader shows mixed results (profit-taking partially offsets loss-holding); Gini increases from initial equality as rational agents extract value from biased agents

### Dimension 7: Information Efficiency and Tail Risk

- **Purpose**: Quantify how efficiently the market incorporates fundamental information and assess tail risk exposure
- **Metrics Used**: Price efficiency ratio, forecast error persistence, deviation decay slope, VaR-95, CVaR-95, HHI volume concentration
- **Visualization**: Efficiency ratio time-series; tail risk histogram with VaR/CVaR annotations; strategy correlation heatmap
- **Expected Pattern**: Efficiency ratio starts low (< 0.3 during anchoring phase) and rises toward 1.0 during correction; forecast error persistence starts > 0.8 and decays; VaR-95 is moderate (-2% to -4% per round); HHI shows dispersed trading (near 1/N)


## §4 Phase Analysis Framework

### Phase Detection Rules

| Phase | Name                  | Entry Condition                                 | Exit Condition                              | Key Indicators                                                                         | Typical Round Range |
|-------|-----------------------|-------------------------------------------------|---------------------------------------------|----------------------------------------------------------------------------------------|---------------------|
| 1     | Anchor Establishment  | Round 1                                         | deviation stable within ±0.5% for 5+ rounds | AnchoredTrader sets anchor = 105; HistoricalAnchor begins filling history              | Rounds 1–10         |
| 2     | Persistent Mispricing | `mean(deviation[-5:]) > 0.02` stable            | `mean(deviation[-5:]) < 0.02`               | RationalUpdater buying but price stays elevated; AC1 > 0.1                             | Rounds 10–60        |
| 3     | Slow Correction       | `deviation` declining for 5+ consecutive rounds | `deviation < 0.01`                          | HistoricalAnchor's rolling average converging toward F; anchoring resistance weakening | Rounds 60–90        |
| 4     | Convergence           | `deviation < 0.01`                              | End of simulation                           | Price near fundamental; AC1 near zero; all agents near equilibrium                     | Rounds 90+          |

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

| Metric             | Target Range           | Calibration Source                                                                      | Validation Method                                                  |
|--------------------|------------------------|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| MAD (%)            | [3%, 10%]              | Campbell & Sharpe (2009): mean analyst forecast error ~5%                               | Compute MAD across all 200 full-round observations; reject if < 1% |
| Half-life (rounds) | [20, 60]               | Campbell & Sharpe (2009): quarterly persistence → 25–75 trading days                    | Fit exponential decay; extract τ                                   |
| Max drawdown       | [5%, 20%]              | Typical equity correction magnitude; anchoring creates moderate not extreme corrections | Compute across full simulation                                     |
| Rolling volatility | [0.5%, 2.0%] per round | Black (1986): noise trader background volatility range                                  | Compute rolling std; report mean ± std                             |
| AC1 (bubble phase) | [0.0, 0.30]            | Lo & MacKinlay (1988): weekly autocorrelation in equities                               | Compute AC1 over rounds 10–60 (persistence phase)                  |
| Bias magnitude     | [2%, 5%]               | Tversky & Kahneman (1974): α = 0.3 with 5% initial anchor → 3.5% bias                   | Compute `(1 − α) × (anchor − F) / F` from simulation parameters    |

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
| Wealth Dynamics           | Bar + annotation     | Agent type | Terminal wealth ($)           | Gini annotation; wealth transfer direction arrows     | Who profits/loses from anchoring mispricing           |
| Information & Tail Risk   | Multi-panel (2×2)    | Various    | Efficiency / VaR / HHI / Corr | VaR threshold line; correlation colour scale          | Market efficiency and risk concentration diagnostics  |


## §8 Registered Metrics Catalogue (extensible)

From AnchoringEffect-Analysis-Overhaul (2026-Q1) the analysis pipeline is
*registry-driven*: every scalar quantity reported by
`examples/AnchoringEffect/Rule/analysis.py` is produced by a metric function in
`examples/AnchoringEffect/metrics.py` and registered with the shared
`MetricsRegistry` (`examples/AnchoringEffect/standard_rule_analysis.py`). Adding a new metric
requires only two steps:

1. Implement `def m_my_metric(data, config) -> dict[str, Any]:` raising
   `MetricUnavailable` when its inputs are missing.
2. Append `REGISTRY.register(Metric(name="my_metric", category=..., fn=m_my_metric, output_keys=(...,)))`.

The driver enumerates the registry; no file edits are required. Output keys
are *validated*: a metric whose returned dict is missing any declared key
raises `ValueError` (fail-fast). Metrics that cannot run on a given run are
reported under `summary.json["metrics_unavailable"]`.
The dashboard set contains 11 panels (panels 00–10), each rendering one or
two category groups with annotated reference lines and calibration targets.

### Categories and Default Coverage (44 metrics)

| # | Category                    | Count | Representative metrics                                                                                                                                                                                                                                                 |
|---|-----------------------------|------:|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | price_dynamics              |    12 | `price_deviation_ts`, `mad_pct`, `half_life_threshold`, `half_life_fitted`, `rolling_volatility_ts`, `mean_volatility_pct`, `max_drawdown_pct`, `return_skewness`, `return_kurtosis`, `return_autocorr_lag1`, `return_autocorr_profile`, `variance_ratio_lo_mackinlay` |
| 2 | anchoring_specific          |     5 | `bias_magnitude_pct`, `anchor_dispersion`, `under_revision_ratio`, `regime_transition_lag`, `price_to_anchor_distance_ts`                                                                                                                                              |
| 3 | agent_behaviour             |     6 | `agent_volume_buy_sell`, `agent_action_frequency`, `agent_net_position_ts`, `agent_pnl_terminal`, `agent_sharpe_terminal`, `silent_agent_count`                                                                                                                        |
| 4 | microstructure              |     4 | `order_imbalance_ts`, `signed_volume_autocorr`, `corrective_to_biased_volume_ratio`, `momentum_anchoring_coupling`                                                                                                                                                     |
| 5 | statistical_inference       |     4 | `mad_block_bootstrap_ci_95`, `half_life_block_bootstrap_ci_95`, `ljung_box_returns_pvalue`, `adf_unit_root_pvalue`                                                                                                                                                     |
| 6 | phase_decomposition         |     2 | `phase_assignment_ts`, `per_phase_metrics_table`                                                                                                                                                                                                                       |
| 7 | wealth_dynamics             |     3 | `agent_wealth_terminal`, `gini_coefficient`, `wealth_transfer_direction`                                                                                                                                                                                               |
| 8 | information_efficiency      |     4 | `price_efficiency_ratio`, `forecast_error_persistence`, `deviation_decay_slope`, `information_share_by_strategy`                                                                                                                                                       |
| 9 | tail_risk_and_concentration |     4 | `value_at_risk_95`, `conditional_var_95`, `herfindahl_volume_concentration`, `strategy_correlation_matrix`                                                                                                                                                             |

### Validation Gates (analysis-bases.md §6 — tightened)

`_validate_anchoring_effect` enforces three component scores plus a weighted
overall:

| Component      | Target band     | Weight | Hard gate        |
|----------------|-----------------|-------:|------------------|
| `mad_pct`      | [3, 10] %       |   0.40 | component ≥ 0.50 |
| `half_life`    | [20, 60] rounds |   0.40 | component ≥ 0.50 |
| `max_drawdown` | [5, 20] %       |   0.20 | component ≥ 0.50 |
| **Weighted**   | —               |      — | overall ≥ 0.60   |

Non-blocking advisories are emitted (but do not flip `is_valid`) when
`silent_agent_count > 0`, `under_revision_ratio < 0.7`, or
`|signed_volume_autocorr| > 0.5`.

### Dashboard Set (registry-driven, 11 panels)

| File                           | Content                                                                                                                                |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `00_investor_bids.png`         | Headline: market price + every investor's bid (one coloured line per investor).                                                        |
| `01_price_dynamics.png`        | Price vs fundamental with phase shading; signed deviation with ±3/±10 % bands and fitted half-life mark.                               |
| `02_volatility_returns.png`    | Rolling volatility + return histogram annotated with skewness / excess kurtosis.                                                       |
| `03_autocorrelation.png`       | Return autocorrelation profile (lags 1..10) + Lo & MacKinlay variance ratios at q ∈ {2, 4, 8}.                                         |
| `04_anchoring_specific.png`    | Anchoring magnitude table (MAD, bias, alpha, anchor, F, under-revision, regime-transition lag) + price-to-anchor distance time-series. |
| `05_agent_volume.png`          | Per-agent buy/sell volume + per-agent {buy, sell, hold} action frequency.                                                              |
| `06_agent_performance.png`     | Per-agent net position over time + terminal PnL & Sharpe bars.                                                                         |
| `07_microstructure.png`        | Order imbalance time-series + diagnostics table (signed-volume AC, RU/(AT+HA) ratio, MT–AT correlation).                               |
| `08_inference.png`             | Block-bootstrap 95 % CIs for MAD and half-life + Ljung-Box / ADF table.                                                                |
| `09_wealth_dynamics.png`       | Terminal wealth bars by strategy type + Gini coefficient annotation + wealth transfer direction arrow.                                 |
| `10_information_tail_risk.png` | Price efficiency ratio time-series + VaR/CVaR tail histogram + HHI annotation + strategy correlation heatmap.                          |

Cross-variant artefacts are produced by
`examples/AnchoringEffect/compare_variants.py`:

* `cross_variant_table.json` — per-metric scalar across variants.
* `cross_variant_metrics.png` — bar grid (one panel per metric).
* `cross_variant_validation.png` — weighted-score bars vs. 0.60 gate, coloured
  green (VALID) or red (INVALID).


## §9 Statistical Methodology

This section documents the statistical methods underpinning the inference metrics and explains design choices, assumptions, and limitations.

### 9.1 Sample Size Requirements

| Method              | Minimum Rounds | Recommended Rounds | Reason                                                               |
|---------------------|---------------:|-------------------:|----------------------------------------------------------------------|
| MAD point estimate  |             10 |                 50 | Averaging over < 10 rounds produces high-variance estimate           |
| Block bootstrap CI  |             30 |                100 | Need ≥ n/b = 5 blocks for valid resampling (b ≈ 6 for n = 200)       |
| Half-life OLS fit   |             20 |                 80 | Need sufficient post-peak observations for decay slope estimation    |
| Ljung-Box Q         |             20 |                100 | Asymptotic χ² approximation degrades below n = 20 at m = 10 lags     |
| Variance ratio      |             16 |                 64 | Require n ≥ 8q; at q = 8, minimum n = 64                             |
| ADF unit root       |             30 |                100 | Power of ADF is low at small n; critical values shift                |
| Phase decomposition |             50 |                150 | Need ≥10 rounds per expected phase for meaningful within-phase stats |

### 9.2 Block Bootstrap (Politis & Romano, 1994)

- **Method**: Moving-block bootstrap — divide the time series into overlapping blocks of length b, resample blocks with replacement to form pseudo-series of length n.
- **Block length selection**: b = ⌈n^(1/3)⌉ (rate-optimal rule minimising bootstrap MSE for weakly dependent data). For n = 200, b = 6.
- **Why moving-block** (not IID bootstrap): The deviation series has high autocorrelation (ρ > 0.8). IID resampling destroys this dependence, producing anti-conservative confidence intervals. Block resampling preserves within-block serial correlation.
- **Replicate count**: K = 2000 (standard; doubling to 4000 changes CI endpoints by < 0.1%).
- **Limitation**: Block bootstrap assumes local stationarity within blocks. Phase transitions (non-stationarity) can inflate CI width. The 95% CI should be interpreted as approximate.

### 9.3 OLS Exponential Decay Fit

- **Model**: log|dev(t)| = a + b×t + ε(t); half_life = −ln(2)/b.
- **Assumption**: Linear restoring force produces exponential convergence. The γ-term in the price formation model provides this linear force. Violated when: (a) phase transitions cause non-exponential decay, (b) AnchoredTrader creates a price floor producing piecewise-linear not exponential convergence.
- **Robustness**: When R² < 0.3, the exponential model is a poor fit; the threshold-crossing half-life should be preferred.
- **Filtering**: Rounds where |deviation| < 0.1% are excluded (log of near-zero is unstable).

### 9.4 Ljung-Box Q-Statistic

- **Null**: Returns are IID (no serial correlation at lags 1–10).
- **Distribution**: Under H₀, Q ~ χ²(m) asymptotically. Valid for n > 3m (i.e., n > 30 for m = 10).
- **Power**: At n = 100 and true AC1 = 0.2, power ≈ 80% (adequate). At n = 50, power drops to ~50%.
- **Multiple testing note**: We do not apply Bonferroni correction across multiple Q-tests because: (a) only one Q-test is computed per simulation run, (b) metrics are correlated (adjusting would be over-conservative).

### 9.5 ADF Unit Root Test

- **Implementation**: ADF(0) without lagged differences (the price series is short and adding lags reduces power). The t-statistic for β is compared to Dickey-Fuller critical values tabulated by MacKinnon (1991).
- **Approximate p-value**: Since `scipy.stats` is not a dependency, the implementation uses a lookup table of MacKinnon (1991) critical values at {1%, 5%, 10%} significance levels, with linear interpolation for intermediate p-values. This is an approximation — precision is ±2%.
- **Power consideration**: ADF has notoriously low power against near-unit-root alternatives. For γ = 0.01, the expected β ≈ −0.01, which may not be detectable at n = 100. Borderline p-values (0.05–0.20) are expected and should be interpreted cautiously.

### 9.6 Variance Ratio Test

- **Period selection**: q ∈ {2, 4, 8} following Lo & MacKinlay (1988). These periods capture short-term (2-round), medium-term (4-round), and longer-term (8-round) persistence.
- **Requirement**: n ≥ 8q observations. At q = 8, need n ≥ 64 (satisfied by 200-round runs).
- **Heteroscedasticity**: The basic VR test assumes homoscedastic returns. Our simulation has mild heteroscedasticity (volatility varies across phases). The reported VR values should be interpreted as indicative rather than providing formal statistical tests. A robust (heteroscedasticity-consistent) version could be implemented in future.

### 9.7 Multiple Testing and Correlation Structure

The 44 metrics are highly correlated (e.g., MAD and half-life share the same deviation series; VaR and CVaR are mechanically linked). Formal multiple-testing corrections (Bonferroni, FDR) are **not applied** because:
1. Metrics are not independent hypotheses — correction would be over-conservative.
2. The validation gates (§8) use a small, curated subset (MAD, half-life, max_drawdown) as the formal decision rule.
3. All other metrics are **advisory** — they inform interpretation but do not gate pass/fail.

When interpreting multiple metric outputs, focus on **convergent patterns** (multiple metrics pointing the same direction) rather than isolated outliers.


## §10 Limitations and Known Constraints

This section explicitly documents what the analysis can and cannot detect, known failure modes, and interpretation boundaries.

### 10.1 Model Limitations

| Limitation                      | Impact on Analysis                                                                 | Mitigation                                                          |
|---------------------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Constant fundamental F = 100    | Cannot study anchoring under fundamental uncertainty or drift                      | All deviation is purely bias-driven; simplifies attribution         |
| No exogenous event shocks       | Tail risk metrics (VaR, CVaR) reflect only endogenous dynamics                     | Compare to event-driven simulations separately                      |
| No agent learning or adaptation | Agents do not update their strategies over time; no evolution of α                 | Interpret as “single-episode” anchoring rather than adaptive market |
| Single-asset, single-venue      | Cannot study cross-asset contagion or venue fragmentation                          | Keep scope limited to single-market anchoring                       |
| No short-selling constraints    | RationalUpdater can sell without limit; real arbitrage is constrained              | Over-estimates correction speed relative to real markets            |
| Discrete round structure        | Intraday dynamics, continuous trading, and high-frequency effects are not modelled | Interpret each round as “one decision period” (daily equivalent)    |

### 10.2 Analysis-Specific Limitations

| Metric / Method             | Known Limitation                                                                                                                  |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Half-life (OLS fit)         | Assumes exponential decay; violated when agents create piecewise-linear convergence or when phase transitions cause regime shifts |
| Gini coefficient            | Sensitive to agent count (N = 14); small N inflates or deflates Gini compared to large-N populations                              |
| VaR / CVaR at 95%           | With ~200 observations, the 5th percentile is estimated from ≤10 data points — high estimation variance                           |
| Block bootstrap CI          | Block length b = 6 may not capture long-range dependence if ρ > 0.95; CI can be anti-conservative for very persistent series      |
| ADF p-value                 | Approximate (lookup table, not exact); low power at n = 200 for near-unit-root processes                                          |
| Variance ratio              | Assumes homoscedastic returns; mild heteroscedasticity in phase transitions biases VR toward 1                                    |
| Strategy correlation matrix | Pearson correlation assumes linear relationships; non-linear strategy interactions (e.g., threshold activation) are not captured  |

### 10.3 What the Analysis Cannot Detect

- **Nonlinear phase transitions**: The phase decomposition uses heuristic thresholds; subtle regime shifts within phases are not identified.
- **Emergent coordination**: If agents spontaneously synchronise behaviour (herding) without explicit coordination mechanisms, the current metrics may attribute this to individual strategy properties rather than emergent dynamics.
- **Long-memory effects**: Metrics are designed for short/medium persistence (ρ ≈ 0.8). True long-memory processes (Hurst exponent > 0.5) would require R/S analysis or GPH estimation (not currently implemented).
- **Higher-order interactions**: Pairwise strategy correlation (§2 metric) captures only bilateral interactions. Three-way or higher-order strategy interactions (e.g., AT + MT + HA coalition) are not measured.
- **Causal direction**: Correlations and volume ratios indicate association, not causation. The analysis cannot formally prove that anchoring *causes* mispricing vs. being an artifact of the price formation model.

### 10.4 Minimum Viable Simulation Length

| Rounds | Capability Level                                                                                                    |
|-------:|---------------------------------------------------------------------------------------------------------------------|
|     30 | Basic MAD and deviation only; no bootstrap, no phase decomposition, no variance ratios                              |
|     50 | Point estimates for all metrics; bootstrap CIs unreliable; phase decomposition marginal                             |
|    100 | Full pipeline operational; bootstrap CIs reasonable; 3–4 phases typically detectable                                |
|    200 | **Recommended**: All metrics at full power; clean phase decomposition; robust CIs; adequate VR and ADF observations |
|    500 | Extended: enables sub-phase analysis, rolling metric windows, and higher-order autocorrelation studies              |

### 10.5 Known Failure Modes

| Failure Mode                       | Symptom                                                 | Consequence for Analysis                                                    |
|------------------------------------|---------------------------------------------------------|-----------------------------------------------------------------------------|
| All agents hold (no trading)       | All volumes = 0; metrics degenerate to NaN              | Pipeline crashes or produces meaningless zeros                              |
| NoiseTrader dominates              | Very high volatility; MAD ≈ 0 (noise averages out bias) | Anchoring signal buried; bootstrap CI extremely wide                        |
| MomentumTrader runaway             | Price diverges; half_life = NaN; max_drawdown > 50%     | Analysis detects instability but cannot provide anchoring-specific insights |
| Identical agent parameters         | Gini = 0; strategy correlation = 1; HHI = 1/N exactly   | Analysis reports “healthy” but simulation lacks genuine heterogeneity       |
| Simulation too short (< 50 rounds) | Insufficient observations for most inferential metrics  | Pipeline runs but outputs are unreliable; no phase decomposition possible   |

