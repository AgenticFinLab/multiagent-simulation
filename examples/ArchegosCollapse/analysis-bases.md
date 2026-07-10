# ArchegosCollapse — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question                                                         | Metric(s)                                                                                               | Expected Finding                                                                               |
|-----------|---------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| O1        | Does forced liquidation produce a measurable price cascade?               | Price deviation, max drawdown                                                                           | Deviation < −15% sustained for ≥10 rounds; drawdown in [20%, 60%]                              |
| O2        | How fast does the cascade develop and resolve?                            | Cascade onset round, cascade half-life                                                                  | Onset within rounds 10–30; recovery over 20–40 rounds after peak                               |
| O3        | Do prime broker timing differences produce a measurable payoff gap?       | Agent sell price (PrimeBrokerFirstMover vs PrimeBrokerDelayedLiquidator), volume-weighted average price | PrimeBrokerFirstMover achieves ≥5% better average sell price than PrimeBrokerDelayedLiquidator |
| O4        | Does BlockTradeBuyer provide a measurable price floor?                    | Min price round, deviation at floor, recovery onset round                                               | Price stabilization observable ≤ 5 rounds after BlockTradeBuyer first activates                |
| O5        | How does LLM variant cascade timing compare to Rule baseline?             | Cross-variant peak deviation, onset round                                                               | LLM may delay or accelerate onset by ≥5 rounds relative to Rule                                |
| O6        | Does InformationTrader's front-running generate measurable excess return? | InformationTrader PnL vs ConcentratedFund PnL                                                           | InformationTrader captures ≥2× per-share return relative to ConcentratedFund                   |


## §2 Core Metrics Catalogue

### Metric: Price Deviation from Fundamental

- **Category**: Price Dynamics / Phenomenon-Specific
- **Definition**: Percentage difference between market price P(t) and the fixed fundamental value F, measuring the magnitude of mispricing caused by forced selling.
- **Formula**:
  ```
  deviation(t) = (P(t) − F) / F × 100
  ```
- **Python Function Signature**: `def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`
  where F = 100.0 (ArchegosCollapse baseline fundamental value, per §6 parameter table).
- **Derivation Rationale**: Normalising by F removes the dependency on absolute price levels and produces a scale-invariant measure of dislocation. The percentage form matches the standard mispricing measure used in the behavioural finance literature (Shiller, 2000; DeLong et al., 1990) and directly maps to margin maintenance thresholds, which are typically stated as percentage-of-notional.
- **Academic Calibration Source**:
  - Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. Chapters 1–3 establish deviation from fundamental as the primary empirical measure of speculative excess; observed deviations of 20–40% characterized major 20th-century crashes.
  - DeLong, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 — documents persistent deviations of 10–20% attributable to noise trader demand.
- **Interpretation**:
  - deviation = 0: Price at fundamental fair value
  - deviation ∈ (−10%, 0%): Mild discount — InformationTrader activates; ConcentratedFund approaching threshold
  - deviation < −10%: Cascade zone — PrimeBrokerFirstMover liquidation threshold breached
  - deviation < −15%: Deep cascade — PrimeBrokerDelayedLiquidator liquidation threshold breached
  - deviation < −30%: Extreme stress; sensitivity check required
- **Normal Range**: −5% to +5% in pre-cascade equilibrium; −20% to −40% during peak cascade (ViacomCBS fell ~60% in March 2021)
- **Red Flag**: Deviation never reaches −10% → ConcentratedFund not triggering; check `leverage_trigger` config and initial position size

---

### Metric: Maximum Drawdown

- **Category**: Price Dynamics / Risk
- **Definition**: The largest peak-to-trough price decline expressed as a percentage of the peak price, measuring the worst realized loss from a long position held throughout the simulation.
- **Formula**:
  ```
  max_drawdown = max_{t₁ < t₂} [(P(t₁) − P(t₂)) / P(t₁)] × 100
  ```
- **Python Function Signature**: `def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`
- **Derivation Rationale**: Maximum drawdown is the canonical measure of tail-risk severity for leveraged liquidation events because it captures the worst-case realized loss without averaging away the extremes. For systemic risk analysis, the severity of the cascade peak matters more than its average magnitude.
- **Academic Calibration Source**:
  - Chekhlov, A., Uryasev, S., & Zabarankin, M. (2005). Drawdown measure in portfolio optimization. *International Journal of Theoretical and Applied Finance*, 8(1), 13–58. https://doi.org/10.1142/S0219024905002767 — establishes maximum drawdown as a coherent risk measure with superior tail sensitivity compared to VaR.
  - Archegos post-mortem: ViacomCBS dropped from ~$100 to ~$40 over five trading days (March 24–29, 2021), producing a realized maximum drawdown of approximately 60%. Source: Financial Stability Board (2022), *Non-bank Financial Intermediation Report*, pp. 47–51.
- **Interpretation**:
  - max_drawdown > 20%: Cascade-scale event consistent with prime broker liquidation dynamics
  - max_drawdown 20%–40%: Moderate Archegos-scale event (Morgan Stanley scenario)
  - max_drawdown 40%–60%: Severe event (Credit Suisse scenario; delayed liquidation)
  - max_drawdown < 5%: Cascade too mild — adjust leverage parameters or initial position
- **Normal Range**: [20%, 60%] calibrated from Archegos event; target central scenario: 25%–40%
- **Red Flag**: max_drawdown < 10% → liquidation mechanics not producing sufficient cascade; increase `price_impact` (λ) or `initial_position`

---

### Metric: Cascade Volatility (Rolling Standard Deviation of Returns)

- **Category**: Volatility / Cascade Intensity
- **Definition**: Rolling 10-round standard deviation of price returns during the cascade phase, measuring how turbulent the sell-off is on a round-by-round basis.
- **Formula**:
  ```
  r(t)     = (P(t) − P(t−1)) / P(t−1)
  vol(t)   = std({r(t−9), r(t−8), …, r(t)})
  ```
- **Python Function Signature**: `def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`
- **Derivation Rationale**: A 10-round rolling window balances responsiveness to changing conditions against noise; it roughly corresponds to two trading days of intraday observations if one simulation round maps to a 48-minute interval. Realized volatility is the standard empirical measure of market stress (Andersen et al., 2003).
- **Academic Calibration Source**:
  - Garman, M. B., & Klass, M. J. (1980). On the estimation of security price volatilities from historical data. *Journal of Business*, 53(1), 67–78. https://doi.org/10.1086/296072 — establishes the theoretical basis for realized volatility estimation from historical price sequences.
  - Andersen, T. G., Bollerslev, T., Diebold, F. X., & Labys, P. (2003). Modeling and forecasting realized volatility. *Econometrica*, 71(2), 579–625. https://doi.org/10.1111/1468-0262.00418 — documents that intraday volatility spikes to 5–15× its normal level during market stress events.
  - Archegos calibration: Archegos-affected stocks exhibited intraday volatility of approximately 5–8% per day during March 25–29, 2021 (Financial Stability Board, 2022).
- **Interpretation**:
  - vol(t) near 0: No meaningful price movement (pre-cascade phase)
  - vol(t) > 3% per round: Active cascade — agents are producing significant price moves
  - vol(t) > 8% per round: Extreme cascade — test whether price impact (λ) is too high
- **Normal Range**: 2%–8% per round during cascade phase; <1% in pre-cascade phase
- **Red Flag**: Volatility > 15% per round → cascade unrealistically extreme; reduce `price_impact` (λ)

---

### Metric: Return Autocorrelation (Lag-1)

- **Category**: Behavioral / Cascade Self-Reinforcement
- **Definition**: Pearson lag-1 autocorrelation of the price return series, indicating whether the cascade is self-reinforcing (positive AC1) or mean-reverting (negative AC1).
- **Formula**:
  ```
  AC1 = corr(r(t), r(t−1))   computed over all rounds in the analysis window
  ```
- **Python Function Signature**: `def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`
- **Derivation Rationale**: In a cascade driven by feedback loops (selling → lower prices → more margin calls → more selling), successive returns should be positively correlated during the cascade phase. When stabilizing forces (BlockTradeBuyer, mean-reversion term γ) dominate, autocorrelation should turn negative. This phase-shift in AC1 sign is a direct signature of the two regimes.
- **Academic Calibration Source**:
  - Lo, A. W., & MacKinlay, A. C. (1988). Stock market prices do not follow random walks: Evidence from a simple specification test. *Review of Financial Studies*, 1(1), 41–66. https://doi.org/10.1093/rfs/1.1.41 — establishes that positive autocorrelation (AC1 ≈ 0.17–0.35 at weekly intervals) is the empirical signature of momentum in equity markets.
  - Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 — the funding-liquidity spiral they document predicts positive autocorrelation during a deleveraging cascade: each round of forced selling is amplified by the next margin call.
- **Interpretation**:
  - AC1 ∈ (0.2, 0.5): Momentum phase — cascade self-reinforcing; liquidators dominant
  - AC1 ≈ 0: Random walk — no dominant behavioral regime
  - AC1 ∈ (−0.3, 0): Mean reversion — recovery phase; BlockTradeBuyer and γ-term dominant
- **Normal Range**: AC1 = 0.2–0.5 during cascade onset; AC1 < 0 during recovery phase
- **Red Flag**: AC1 ≈ 0 throughout entire simulation → cascade not self-reinforcing; increase `price_impact` (λ) or verify ConcentratedFund is repeatedly triggering

---

### Metric: Agent-Type Volume and Volume-Weighted Average Price (VWAP)

- **Category**: Volume / Activity / Behavioral Validation
- **Definition**: Total trading volume (shares) by agent type per simulation run, plus the volume-weighted average price at which each agent type executes.
- **Formula**:
  ```
  volume_type      = Σ_t Σ_{i ∈ type} |quantity_i(t)|
  VWAP_type        = Σ_t Σ_{i ∈ type} [|quantity_i(t)| × P(t)] / volume_type
  price_gap        = VWAP_PrimeBrokerFirstMover − VWAP_PrimeBrokerDelayedLiquidator   (should be > 0)
  ```
- **Python Function Signature**: `def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`
- **Derivation Rationale**: The first-mover advantage hypothesis (Gorton & Metrick, 2012) specifically predicts that PrimeBrokerFirstMover should liquidate at higher prices than PrimeBrokerDelayedLiquidator because it acts when prices are less depressed. VWAP is the correct measure because simple volume comparisons do not capture the price quality difference.
- **Academic Calibration Source**:
  - Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016 — establishes that first-moving creditors recover 5–15% more per unit of collateral in repo run scenarios.
  - Chordia, T., Roll, R., & Subrahmanyam, A. (2002). Order imbalance, liquidity, and market returns. *Journal of Financial Economics*, 65(1), 111–130. https://doi.org/10.1016/S0304-405X(02)00136-8 — documents that order imbalance (concentrated selling by one agent type) predicts negative returns with R² ≈ 0.10–0.25 at short horizons.
- **Interpretation**: Reveals which agents drive the cascade vs. which absorb supply; PrimeBroker volumes should exceed ConcentratedFund after the margin call; price_gap > 0 validates first-mover advantage
- **Normal Range**: PrimeBrokerFirstMover VWAP should exceed PrimeBrokerDelayedLiquidator VWAP by ≥5%; BlockTradeBuyer volume > 0 after round 20
- **Red Flag**: BlockTradeBuyer has zero volume → floor mechanism not activating; check `discount_threshold` config. price_gap ≤ 0 → timing asymmetry not working; check threshold separation

---

### Metric: Cascade Onset Round

- **Category**: Phenomenon-Specific / Timing
- **Definition**: The first simulation round in which price deviation crosses the −10% threshold (the PrimeBrokerFirstMover liquidation trigger), marking the beginning of the creditor race.
- **Formula**:
  ```
  t_onset = min { t : deviation(t) < −0.10 }
  If no such t exists, t_onset = NaN (cascade did not occur)
  ```
- **Python Function Signature**: `def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`
- **Derivation Rationale**: The −10% threshold mirrors PrimeBrokerFirstMover's `liquidation_threshold = 0.10` parameter in the simulation config. Using the broker's own trigger as the cascade onset definition ensures the metric directly measures when the creditor race mechanism begins, rather than a model-free price threshold.
- **Academic Calibration Source**:
  - Archegos timeline: Forced liquidations began March 25–26, 2021 (approximately 1–2 trading days after ViacomCBS first declined significantly on March 22–23). With 50 simulation rounds per run and an initial position-building phase, rounds 10–30 correspond to the first 1–3 trading days of the event.
  - Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007–2008. *Journal of Economic Perspectives*, 23(1), 77–100. https://doi.org/10.1257/jep.23.1.77 — documents that in leverage-driven cascades, the interval from initial shock to creditor action is 1–3 trading days, matching the [10, 30] round calibration target.
- **Interpretation**: Measures how quickly leverage unwinds once the price trigger is hit; earlier onset → more violent cascade; very late onset → position building taking too long
- **Normal Range**: Rounds 10–30 of a 50-round simulation
- **Red Flag**: t_onset never reached → `leverage_trigger` too high or initial position too small; t_onset < 5 → cascade starting before agents fully deploy capital, producing unrealistic dynamics

---

### Metric: Cascade Recovery Half-Life

- **Category**: Phenomenon-Specific / Recovery Dynamics
- **Definition**: The number of rounds required for price deviation to recover from its minimum (peak cascade) to half the distance back toward zero.
- **Formula**:
  ```
  dev_min       = min_t { deviation(t) }   (peak cascade round t_peak)
  half_life     = min { t > t_peak : deviation(t) ≥ dev_min / 2 } − t_peak
  ```
- **Python Function Signature**: `def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]`
- **Derivation Rationale**: The half-life captures the pace of mean reversion after the cascade floor, which depends on the balance between the mean-reversion parameter γ and residual selling pressure. A short half-life indicates γ is strong; a long half-life indicates that selling pressure persists.
- **Academic Calibration Source**:
  - Fama, E. F., & French, K. R. (1988). Permanent and temporary components of stock prices. *Journal of Political Economy*, 96(2), 246–273. https://doi.org/10.1086/261535 — estimates the half-life of mean reversion in equity prices at 3–5 years for fundamental-driven deviations; short-horizon cascade recoveries are faster (days to weeks).
  - Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617–637. https://doi.org/10.1111/j.1540-6261.1988.tb04594.x — block trade buyers provide near-immediate stabilization once the discount exceeds the risk-compensation threshold, suggesting a recovery half-life of 5–15 rounds once BlockTradeBuyer activates.
- **Normal Range**: 5–20 rounds after peak cascade
- **Red Flag**: half_life < 3 rounds → γ (mean_reversion) too high; recovery unrealistically fast. half_life > 40 rounds → γ too low; recovery never occurs within simulation window


## §3 Analysis Dimensions

### Dimension 1: Price Cascade Dynamics

- **Purpose**: Verify that forced liquidation produces a sustained, measurable price cascade consistent with the Archegos theoretical framework
- **Metrics Used**: Price deviation, max drawdown, cascade volatility
- **Visualization**: Price vs. fundamental line chart with cascade threshold overlays at deviation = −10%, −15%, −20%
- **Expected Pattern**: Price falls sharply below fundamental in cascade zone, maintains depressed level while multiple agents liquidate, then partially recovers as BlockTradeBuyer activates and γ-term pulls toward fundamental
- **Comparison Baseline**: Rule variant as deterministic reference; all other variants compared against Rule max_drawdown ± 10%

### Dimension 2: Agent Behavior Validation

- **Purpose**: Confirm that each agent type behaves as designed — liquidators sell on schedule, buyer provides floor, InformationTrader front-runs
- **Metrics Used**: Agent-type volume, VWAP by type, cascade onset round
- **Visualization**: Stacked bar chart of cumulative volume by agent type; round-by-round action heatmap
- **Expected Pattern**: PrimeBrokerFirstMover volume peaks 2–5 rounds before PrimeBrokerDelayedLiquidator; BlockTradeBuyer activates at price floor; InformationTrader volume concentrated in early rounds (before ConcentratedFund peaks)
- **Comparison Baseline**: Agent-type volumes should match theoretical liquidation fractions from §4 (ConcentratedFund: 50%; PrimeBrokerFirstMover: 40%; PrimeBrokerDelayedLiquidator: 35%)

### Dimension 3: Cascade Intensity and Lifecycle

- **Purpose**: Measure cascade severity and recovery path; identify the four phases
- **Metrics Used**: Max drawdown, return autocorrelation, rolling volatility, recovery half-life
- **Visualization**: 4-panel: (a) deviation over time with phase annotations, (b) rolling volatility, (c) rolling autocorrelation, (d) agent cumulative volume over time
- **Expected Pattern**: High positive autocorrelation (AC1 > 0.2) during cascade, turning negative during recovery; volatility peaks in cascade phase then drops

### Dimension 4: First-Mover Advantage Quantification

- **Purpose**: Measure the payoff gap between PrimeBrokerFirstMover and PrimeBrokerDelayedLiquidator attributable to timing advantage
- **Metrics Used**: VWAP by broker type, price_gap = VWAP_PB1 − VWAP_PB2
- **Visualization**: Side-by-side VWAP comparison bar; timeline overlay showing when each broker sells
- **Expected Pattern**: price_gap > 0 in all runs; price_gap ≥ 5% of initial price; gap larger in runs with steeper cascade (higher max_drawdown)

### Dimension 5: Cross-Variant Comparison

- **Purpose**: Compare cascade dynamics across Rule, LLM, RuleLLM, Rag
- **Metrics Used**: All core metrics, cascade onset round, recovery half-life
- **Visualization**: Side-by-side price curves for all 4 variants (same axis scale)
- **Expected Pattern**: Rule is most predictable; LLM introduces timing variability (onset ± 5 rounds); RuleLLM near-Rule (onset ± 2 rounds); Rag modified by historical knowledge (LTCM/Archegos precedents may alter BlockTradeBuyer timing)


## §4 Phase Analysis Framework

### Phase Detection Rules

| Phase | Name          | Entry Condition               | Exit Condition             | Key Indicators                                                                         | Typical Round Range |
|-------|---------------|-------------------------------|----------------------------|----------------------------------------------------------------------------------------|---------------------|
| 1     | Pre-Cascade   | Round 1                       | deviation(t) < −0.10       | Normal price fluctuation; ConcentratedFund building toward threshold                   | Rounds 1–20         |
| 2     | Cascade Onset | deviation(t) < −0.10          | deviation(t) < −0.15       | PrimeBrokerFirstMover initiates liquidation; volume spike; AC1 turns positive          | Rounds 10–25        |
| 3     | Peak Cascade  | deviation(t) < −0.15          | deviation(t) starts rising | Maximum drawdown; PrimeBrokerDelayedLiquidator active; BlockTradeBuyer first activates | Rounds 15–35        |
| 4     | Recovery      | deviation rising from minimum | deviation(t) > −0.05       | BlockTradeBuyer absorbing supply; AC1 turns negative; γ-term dominant                  | Rounds 25–50        |

### Quantitative Phase Criteria

**Phase 2 observable signatures**:
- Agent action log: PrimeBrokerFirstMover places sell orders in ≥2 consecutive rounds
- Rolling volatility vol(t) crosses 3% per round
- AC1 of last 10 rounds > 0.15

**Phase 3 observable signatures**:
- Agent action log: PrimeBrokerDelayedLiquidator places sell orders in ≥1 round
- Max deviation in Phase 3 < −0.20 (target for parameter validation)
- BlockTradeBuyer places at least one buy order

**Phase 4 observable signatures**:
- Price returns r(t) > 0 in ≥3 of last 5 rounds
- Rolling AC1 < 0 (mean-reversion dominating)
- ConcentratedFund and both PrimeBrokers show zero or near-zero volume (position exhausted)

### Phase Transition Failure Diagnostics

| Failure              | Symptom                                           | Likely Cause                                            | Fix                                                               |
|----------------------|---------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------------|
| Phase 2 never starts | deviation never < −0.10                           | leverage_trigger too high or initial_position too small | Reduce ConcentratedFund leverage_trigger to 0.10                  |
| Stuck in Phase 2     | deviation stays in (−0.15, −0.10) for > 30 rounds | PrimeBrokerDelayedLiquidator threshold too high         | Reduce PrimeBrokerDelayedLiquidator liquidation_threshold to 0.12 |
| Phase 3 too brief    | Peak cascade lasts < 3 rounds                     | price_impact (λ) too low; selling pressure insufficient | Increase λ from 0.03 to 0.05                                      |
| Phase 4 never starts | deviation stays < −0.20 indefinitely              | BlockTradeBuyer not activating; γ too low               | Check discount_threshold; increase mean_reversion γ               |


## §5 Cross-Variant Comparison Framework

### Comparison Protocol

1. **Normalize**: Compare all variants using same fundamental value (F = 100.0) and same initial price (P₀ = 100.0) — any differences in results are attributable to variant decision logic, not initial conditions
2. **Statistical test**: Run each variant 10 times; report mean ± std of all core metrics; use one-way ANOVA (p < 0.05) to test for significant cross-variant differences in max_drawdown
3. **Key comparison axes**:

| Axis                | Question                              | Expected Direction                                                         |
|---------------------|---------------------------------------|----------------------------------------------------------------------------|
| Cascade onset speed | Which variant triggers first?         | Rule = RuleLLM < LLM (deterministic vs stochastic)                         |
| Cascade depth       | Peak deviation magnitude              | LLM > Rule (stochastic amplification possible)                             |
| First-mover gap     | VWAP price_gap PB1 vs PB2             | Rule > LLM (LLM timing variability reduces gap reliability)                |
| Recovery speed      | half_life by variant                  | Rag < Rule (historical precedent may trigger earlier buying)               |
| Behavioral realism  | Does LLM reproduce denial-then-panic? | Qualitative scoring of LLM action narrative vs empirical Archegos behavior |

4. **Reporting format**: Table with mean ± std of each core metric across all variants; flag any variant where a metric falls outside the Normal Range defined in §2


## §6 Expected Results and Validation

### Calibration Targets from Literature

| Metric                                  | Target Range       | Calibration Source                                                  | Validation Method                                     |
|-----------------------------------------|--------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| Max drawdown                            | [20%, 60%]         | Archegos (ViacomCBS −60%); Morgan Stanley scenario (−25%–40%)       | Run 10 Rule-variant simulations; reject if mean < 15% |
| Cascade onset round                     | [10, 30]           | Archegos unfolded over 3–5 trading days from initial decline        | Check t_onset in all runs                             |
| Cascade volatility (peak)               | [3%, 8%] per round | Archegos affected stocks: 5–8% intraday; FSB (2022)                 | Rolling vol during Phase 3                            |
| AC1 during cascade                      | [0.20, 0.50]       | Brunnermeier & Pedersen (2009): leverage spiral signature           | Compute AC1 over Phase 2–3 rounds only                |
| PrimeBrokerFirstMover VWAP gap over PB2 | ≥ 5%               | Gorton & Metrick (2012): first-mover recovers 5–15% better          | Compute price_gap over 10 runs; report mean           |
| Recovery half-life                      | [5, 20] rounds     | Grossman & Miller (1988): block buyers provide near-immediate floor | Compute half_life for each run                        |

### Sensitivity Discussion

- **λ (price_impact) sensitivity**: Doubling λ from 0.03 to 0.06 approximately doubles max_drawdown. Recommended sensitivity test: run grid λ ∈ {0.02, 0.03, 0.04, 0.05} with all other parameters fixed. Document the λ value that produces mean max_drawdown closest to the 30%–40% target.
- **γ (mean_reversion) sensitivity**: γ controls recovery speed. γ = 0.01 (baseline) produces half_life ≈ 15–20 rounds. γ = 0.05 produces half_life ≈ 5 rounds. Recommended test: γ ∈ {0.005, 0.01, 0.02, 0.05}.
- **Threshold separation sensitivity**: The gap between PrimeBrokerFirstMover.threshold (0.10) and PrimeBrokerDelayedLiquidator.threshold (0.15) determines the first-mover payoff gap. Narrowing the gap to 0.02 should reduce price_gap below 5%. Test: {0.02, 0.05, 0.10} separation.

### Validation Failure Signs

| Failure Sign                             | Interpretation                                                       | Parameter Fix                                                     |
|------------------------------------------|----------------------------------------------------------------------|-------------------------------------------------------------------|
| Deviation never crosses −0.10            | ConcentratedFund not selling; cascade not starting                   | Reduce `leverage_trigger` or increase `initial_position`          |
| Recovery too fast (half_life < 3 rounds) | γ (mean_reversion) too high; prices snap back before cascade deepens | Reduce γ from 0.01 to 0.005                                       |
| All agents identical VWAP                | Agent timing differentiation failing; threshold separation too small | Widen PrimeBroker threshold gap to ≥0.05                          |
| AC1 ≈ 0 throughout                       | Cascade not self-reinforcing; price impact too small                 | Increase λ from 0.03 to 0.05                                      |
| BlockTradeBuyer volume = 0               | Floor mechanism never activating                                     | Reduce `discount_threshold` from 0.10 to 0.08                     |
| max_drawdown > 60%                       | Cascade too extreme; λ or initial_position too high                  | Reduce λ; validate position fractions sum to < 3× total liquidity |


## §7 Visualization Catalogue

| Plot Name                        | Type         | X-axis     | Y-axis            | Overlays                                                     | Purpose                                                       |
|----------------------------------|--------------|------------|-------------------|--------------------------------------------------------------|---------------------------------------------------------------|
| Price vs Fundamental             | Line         | Rounds     | Price             | Fundamental dashed line; phase bands (colors for Phases 1–4) | Shows cascade onset, depth, and recovery; annotate t_onset    |
| Price Deviation                  | Line         | Rounds     | Deviation (%)     | −10%, −15%, −20% horizontal threshold lines                  | Primary cascade severity measure; compare across variants     |
| Round Returns                    | Line         | Rounds     | Return (%)        | Zero line; ±σ band from pre-cascade baseline                 | Identifies momentum direction; cascade vs. recovery regimes   |
| Rolling Volatility               | Line         | Rounds     | vol(t) (%)        | 3% cascade threshold; 8% extreme threshold                   | Measures cascade turbulence; validates calibration targets    |
| Rolling Autocorrelation          | Line         | Rounds     | AC1 (lag-1)       | Zero line; +0.2 (momentum) and −0.2 (mean-reversion) lines   | Shows regime shift from cascade to recovery                   |
| Return Distribution              | Histogram    | Return (%) | Frequency         | Normal fit overlay                                           | Shows fat tails and negative skew from cascade                |
| Agent Volume by Type             | Bar          | Agent      | Total volume      | Volume fractions per §4 target lines                         | Reveals which agents drive cascade vs. absorb supply          |
| Agent VWAP Comparison            | Bar          | Agent      | VWAP ($)          | Initial price reference line                                 | Quantifies first-mover advantage (PB1 vs PB2 VWAP gap)        |
| Cumulative Agent Volume Timeline | Line (multi) | Rounds     | Cumulative volume | Vertical lines at Phase 2 and Phase 3 entry                  | Shows sequencing of agent activity across cascade lifecycle   |
| Cross-Variant Price Curves       | Line (multi) | Rounds     | Price             | Fundamental dashed; one curve per variant (4 total)          | Compares cascade depth and timing across Rule/LLM/RuleLLM/Rag |
| Rule Adherence Rate (RuleLLM)    | Bar          | Agent      | Adherence rate    | 80% target line                                              | Validates that RuleLLM agents follow quantitative rules       |
| RAG Retrieval Rate (Rag)         | Bar          | Agent      | Success rate      | 50% threshold line                                           | Measures knowledge retrieval effectiveness in Rag variant     |
