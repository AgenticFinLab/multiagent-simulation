# CarryTradeUnwind — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question                                                            | Metric(s)                                    | Expected Finding                                                               |
|-----------|------------------------------------------------------------------------------|----------------------------------------------|--------------------------------------------------------------------------------|
| O1        | Does the LeveragedCarryFund stop_loss trigger generate a measurable cascade? | Max drawdown, unwind velocity, cascade onset | Drawdown 10–25%; velocity spike at LCF activation; onset within 10–30 rounds   |
| O2        | How fast does the cascade propagate once LCF stop_loss is breached?          | Unwind velocity, cascade duration            | Rapid velocity spike; duration ≥ 5 rounds of deviation < −5%                   |
| O3        | Is the cascade condition (LCF sell >> FCB buy) realized in simulation?       | LCF vs. FCB sell-buy volume ratio            | LCF selling > 8× FCB buying during cascade phase                               |
| O4        | Does FundingCurrencyBuyer + mean reversion produce meaningful recovery?      | Recovery ratio, post-cascade mean reversion  | Recovery ratio = 0.3–0.8 depending on stabilizer capacity                      |
| O5        | Does HedgedCarryTrader exit earlier than LeveragedCarryFund?                 | Exit round comparison, sell volume timing    | HedgedCarryTrader exits ≥ 3 rounds before LCF stop_loss trigger                |
| O6        | How does cross-variant carry crash behavior compare?                         | All core metrics by variant                  | Rule most deterministic; Rag potentially shows altered leveraged exit behavior |


## §2 Core Metrics Catalogue

### Metric 1: Maximum Drawdown (%)

- **Category**: Price Dynamics / Crash Severity
- **Definition**: Largest peak-to-trough decline in the FX rate as a percentage
- **Formula**: max_drawdown = max_{t1 < t2} [(P(t1) − P(t2)) / P(t1)] × 100
- **Python function**:
  `def _compute_max_drawdown(prices_list: list[float]) -> float`

**Derivation Rationale**: In an FX carry crash, the peak-to-trough decline directly measures the total loss experienced by a fully invested carry trader from the optimal entry to the worst point. This is the canonical carry crash severity metric. Brunnermeier et al. (2009) document historical carry crash drawdowns of 10–25% for JPY carry positions; the 2008 USD/JPY carry unwind produced a 29% peak-to-trough decline. Chekhlov et al. (2005) establish max drawdown as the preferred risk measure for leveraged strategies with heavy left tail.

**Academic Calibration Source**: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). "Carry trades and currency crashes." *NBER Macroeconomics Annual*, 23(1), 313–347. DOI: 10.1086/593088. Historical calibration: 2008 JPY carry = −29%; 2022 JPY carry = −20%; typical carry crash = −10% to −25%. Simulation target: 10%–25%.

- **Interpretation**:
    - < 5%: No cascade — LCF stop_loss not triggered; verify noise is generating initial trigger shock
    - 5%–10%: Partial cascade — some forced exits but stabilizers limiting damage
    - 10%–25%: Target zone — full cascade consistent with 2008-2022 historical carry crashes
    - > 25%: Severe — verify cascade condition parameters (LCF leverage, position_size, λ)
- **Normal Range**: 10%–25% for calibrated parameters
- **Red Flag**: Drawdown < 5% → stop_loss = 0.03 not being triggered; verify initial_price, fundamental_value, and noise_std generate sufficient negative deviation to breach stop_loss.

---

### Metric 2: Unwind Velocity (Peak Per-Round FX Rate Change)

- **Category**: Phenomenon-Specific / Cascade Speed
- **Definition**: Maximum absolute price change in a single simulation round; captures the explosive nature of forced carry liquidation
- **Formula**: unwind_velocity = max_t |P(t+1) − P(t)|
- **Python function**:
  `def _compute_unwind_velocity(prices_list: list[float]) -> float`

**Derivation Rationale**: Carry crashes are characterized by sudden, violent price discontinuities — the "elevator down" dynamic. Velocity measures how explosive the cascade is at its peak. A high velocity spike (> 10× noise_std per round) indicates forced liquidation dominates rather than gradual selling. Brady Commission (1988) and Brunnermeier et al. (2009) both document intraday price moves 5–10× normal during cascade peaks. With noise_std = 0.02 per round, a velocity > 0.20 indicates cascade dominance.

**Academic Calibration Source**: Brady Commission (1988). Also: BIS (2015). *Foreign Exchange Market Liquidity*. Bank for International Settlements. Target: max velocity > 10 × noise_std = 10 × 0.02 = 0.20 during cascade phase. In normalized terms: velocity > 0.167 (> 14% of P=1.20) during peak cascade.

- **Interpretation**:
    - velocity ≤ 2 × noise_std: No cascade — driven by noise only; stop_loss not triggering LCF sells
    - velocity = 2–10 × noise_std: Partial cascade — some forced selling but limited amplification
    - velocity > 10 × noise_std: Target zone — LCF forced selling dominant; explosive cascade dynamics
- **Normal Range**: 0.10–0.40 (in FX rate units) at cascade peak
- **Red Flag**: velocity ≤ 5 × noise_std = 0.10 throughout → LCF never activating or position already exhausted early; check initial_position for LCF agents.

---

### Metric 3: Unwind Duration (Rounds)

- **Category**: Phenomenon-Specific / Persistence
- **Definition**: Number of simulation rounds during which deviation is below the crisis threshold (−5%)
- **Formula**: unwind_duration = count{t : deviation(t) < −0.05}
- **Python function**:
  `def _compute_unwind_duration(prices_list: list[float], fundamental: float, threshold: float = -0.05) -> int`

**Derivation Rationale**: The duration of the carry crash measures how long the FX rate remains below the crisis threshold — a measure of the stabilization challenge. Brunnermeier et al. (2009) document that JPY carry crashes typically last days to weeks (consistent with 5–30 simulation rounds); shorter crashes indicate stronger stabilization (FCB + mean reversion); longer crashes indicate the cascade overwhelms recovery forces. The crisis threshold of −5% is calibrated to the level at which FundingCurrencyBuyer activates and the crisis is clearly in progress.

**Academic Calibration Source**: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). Historical carry crash duration: 2008 JPY (3–6 weeks below major stress levels ≈ 15–30 simulation rounds); 2022 JPY (4 weeks ≈ 20 rounds). Target: unwind_duration = 5–30 rounds.

- **Interpretation**:
    - < 5 rounds: Quick cascade and recovery — stabilizers effective; FCB + mean reversion sufficient
    - 5–20 rounds: Moderate duration — target zone consistent with historical carry crashes
    - > 30 rounds: Persistent crisis — stabilizer capacity overwhelmed; consider increasing FCB position_size or γ
- **Normal Range**: 5–30 rounds at calibrated parameters
- **Red Flag**: duration = 0 → no crisis occurred; verify LCF stop_loss is being triggered. duration > 50 → simulation may not recover within run length; check γ ≥ 0.01.

---

### Metric 4: Crisis Onset Round

- **Category**: Phenomenon-Specific / Timing
- **Definition**: First round in which deviation crosses the −5% crisis threshold; measures how quickly the cascade escalates from the initial trigger
- **Formula**: t_onset = min{t : deviation(t) < −0.05}; t_onset = −1 if no crisis
- **Python function**:
  `def _compute_cascade_onset(prices_list: list[float], fundamental: float, threshold: float = -0.05) -> int | None`

**Derivation Rationale**: The crisis onset round provides the timeline reference for all phase transitions. Early onset (round < 15) indicates the initial noise trigger quickly escalates; late onset (round > 40) suggests the simulation spends significant time in the pre-crisis accumulation phase, more realistically modeling multi-period carry build-up. The onset round also separates pre-crisis from crisis for agent volume attribution analysis.

**Academic Calibration Source**: Calibrated from 2008 JPY carry unwind timeline: cascade accelerated over approximately 2–3 weeks from initial sell-off to crisis peak. Target: t_onset within rounds 10–40 of a 200-round simulation.

- **Interpretation**:
    - t_onset < 10: Very fast cascade — initial noise immediately triggers LCF; parameters may be too sensitive
    - t_onset = 10–40: Target zone — realistic accumulation then cascade timeline
    - t_onset = −1: No crisis — LCF stop_loss never triggered; reduce stop_loss or increase noise_std
- **Normal Range**: Rounds 10–40 for 200-round simulation
- **Red Flag**: t_onset = −1 → no carry crash occurring; cascade condition not met; verify LCF position_size and leverage are sufficient relative to FCB capacity.

---

### Metric 5: Recovery Ratio

- **Category**: Price Dynamics / Recovery
- **Definition**: Fraction of the maximum deviation that is recovered by the end of the simulation
- **Formula**: recovery_ratio = (|dev_min| − |dev_final|) / |dev_min|, where dev_min = min deviation, dev_final = final-round deviation
- **Python function**:
  `def _compute_recovery_ratio(prices_list: list[float]) -> float`

**Derivation Rationale**: Recovery ratio captures how much of the crash is reversed by the simulation end — testing the combined effectiveness of PPP mean-reversion (γ) and FundingCurrencyBuyer buying. Brunnermeier et al. (2009) document that carry crashes partially reverse within months (recovery_ratio = 0.3–0.7 over a few weeks). Full recovery to PPP fundamental requires years in FX markets. recovery_ratio = 0.3–0.7 within the simulation run length is the empirically consistent target.

**Academic Calibration Source**: Rogoff, K. (1996). "The purchasing power parity puzzle." *Journal of Economic Literature*, 34(2), 647–668. DOI: 10.2307/2729217. PPP convergence half-life: 3–5 years. Over simulation run length (~months equivalent), partial recovery of 30–70% is consistent with Rogoff's findings. Also: Brunnermeier et al. (2009): 2008 JPY crash showed ~60% recovery within 6 months.

- **Interpretation**:
    - recovery_ratio > 0.7: Near-full recovery — stabilizers very effective; γ or FCB may be over-parameterized
    - 0.3–0.7: Target zone — partial recovery consistent with historical carry crash recoveries
    - < 0.3: Persistent depression — crash too deep for stabilizers; consider increasing γ or FCB position_size
- **Normal Range**: 0.3–0.7 for calibrated parameters
- **Red Flag**: recovery_ratio ≈ 0 → simulation ends with price still at crash floor; 200 rounds insufficient for mean reversion; reduce cascade severity or increase γ.

---

### Metric 6: Return Autocorrelation AC(1)

- **Category**: Behavioral / Dynamics
- **Definition**: Lag-1 autocorrelation of per-round FX returns; captures cascade momentum vs. mean-reversion regime
- **Formula**: AC1 = Corr(r(t), r(t−1)) where r(t) = [P(t) − P(t−1)] / P(t−1)
- **Python function**:
  `def _compute_autocorrelation(prices_list: list[float], lag: int = 1) -> float`

**Derivation Rationale**: During carry crashes, returns show negative autocorrelation at very high frequency (rapid reversal) but positive autocorrelation at the cascade scale (each forced sell triggers more forced sells). At the simulation round level, AC1 measures whether the cascade is self-reinforcing (AC1 > 0, momentum phase) or mean-reverting (AC1 < 0, recovery phase). Burnside et al. (2011) document negative return autocorrelation following carry crash events, consistent with the reversal of excess carry returns. Lo & MacKinlay (1988) provide the statistical framework.

**Academic Calibration Source**: Lo, A. W., & MacKinlay, A. C. (1988). "Stock market prices do not follow random walks." *Review of Financial Studies*, 1(1), 41–66. DOI: 10.1093/rfs/1.1.41. Target: AC1 > +0.2 during cascade phase (self-reinforcing); AC1 < −0.1 during recovery.

- **Interpretation**:
    - AC1 > +0.2: Cascade in progress — momentum dominant; LCF forced sells generating sequential price falls
    - AC1 ≈ 0: Random walk regime; no systematic cascade or recovery
    - AC1 < −0.1: Recovery regime — mean reversion and FCB buying dominant; price reverting
- **Normal Range**: +0.2 to +0.5 during cascade; −0.3 to −0.1 during recovery
- **Red Flag**: AC1 ≈ 0 throughout → no cascade dynamics; forced exits not generating momentum.

---

### Metric 7: Annualized Volatility (%)

- **Category**: Market Quality / Risk
- **Definition**: Annualized standard deviation of FX returns, scaled to per-round returns
- **Formula**: annualized_vol = std(r(t)) × √252 × 100, where r(t) = per-round return
- **Python function**:
  `def _compute_peak_rolling_volatility(prices_list: list[float], window: int = 10) -> float`

**Derivation Rationale**: FX volatility is the primary risk metric for carry trade sustainability. Menkhoff et al. (2012) show that carry trade capacity is inversely related to FX volatility — high volatility periods produce carry unwinds. The annualized volatility metric tests whether the simulation generates realistic volatility regimes: low during accumulation (< 10%), high during cascade (> 20%), declining during recovery.

**Academic Calibration Source**: Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). "Carry trades and global foreign exchange volatility." *Journal of Finance*, 67(2), 681–718. DOI: 10.1111/j.1540-6261.2012.01728.x. BIS Triennial Survey 2022: major currency pair FX volatility = 8–12% annualized in normal conditions; 20–40% during stress events.

- **Interpretation**:
    - < 8%: Very low — normal FX regime; carry trade active
    - 8%–15%: Moderate — HedgedCarryTrader may begin reducing position
    - 15%–25%: High — full carry unwind in progress; consistent with historical crash volatility
    - > 25%: Extreme — cascade peak; consistent with October 2008 and January 2015
- **Normal Range**: 5%–12% during accumulation; 15%–30% during cascade peak
- **Red Flag**: Volatility < 5% throughout → cascade never occurring; noise too low or LCF never triggering.


## §3 Analysis Dimensions

### Dimension 1: Crash Severity and Cascade Dynamics

**Purpose**: Verify that the LeveragedCarryFund stop_loss trigger generates a 10–25% drawdown consistent with historical carry crashes
**Metrics Used**: Max drawdown (Metric 1), unwind velocity (Metric 2), annualized volatility (Metric 7)
**Visualization**: FX rate vs. fundamental line chart with crisis thresholds at −5%, −10%, −15%; velocity time series; volatility regime chart
**Expected Pattern**: Gradual accumulation phase (P ≈ F) → noise-triggered initial decline → LCF stop_loss activation → cascade velocity spike → drawdown 10–25% → gradual recovery

### Dimension 2: Cascade Attribution

**Purpose**: Confirm that the cascade_condition is realized: LCF forced selling overwhelms FCB counter-buying
**Metrics Used**: Agent-type volume (sell vs. buy by agent during crisis phase), crisis onset round (Metric 4)
**Visualization**: Per-round sell volume time series decomposed by agent type; bar chart of cascade-phase net demand by agent; cascade condition verification: LCF_sell / FCB_buy ratio
**Expected Pattern**: LCF selling dominates during rounds t_onset through t_peak; FCB buying visible but insufficient; net demand sharply negative during cascade; LCF:FCB volume ratio ≥ 8×

### Dimension 3: Recovery Analysis

**Purpose**: Measure the recovery process and test the combined effect of FCB buying and PPP mean reversion
**Metrics Used**: Recovery ratio (Metric 5), return autocorrelation (Metric 6)
**Visualization**: Deviation time series from peak through recovery; AC1 rolling window chart; FCB cumulative buying vs. cascade cumulative selling
**Expected Pattern**: Recovery ratio = 0.3–0.7; AC1 turns negative post-peak; FCB buying increases relative to LCF selling during recovery phase

### Dimension 4: Timing and Sophistication Comparison

**Purpose**: Test whether HedgedCarryTrader's volatility-based exit is earlier than LeveragedCarryFund's forced exit
**Metrics Used**: Exit round comparison between HedgedCarryTrader and LeveragedCarryFund; HCT sell volume during cascade
**Visualization**: Timeline showing when each agent exits (first sell during cascade); scatter plot of HCT exit round vs. LCF activation round across multiple runs
**Expected Pattern**: HedgedCarryTrader exits ≥ 3 rounds before LCF stop_loss triggers; HCT sell volume at cascade peak is 350 vs. LCF 4000 — 11× smaller per instance

### Dimension 5: Cross-Variant Comparison

**Purpose**: Compare cascade depth, speed, and recovery across Rule, LLM, RuleLLM, Rag variants
**Metrics Used**: All core metrics (1–7) by variant
**Visualization**: Side-by-side FX rate deviation curves; bar chart of mean ± std for each metric; table of recovery_ratio and crisis_onset_round by variant
**Expected Pattern**: Rule most deterministic (lowest std); LLM may show delayed exit (persona deliberation before forced sell) or earlier exit (anticipatory behavior); Rag potentially modified by 2008 JPY or 2015 CHF historical context


## §4 Phase Analysis Framework

### Phase Detection Rules

| Phase | Name               | Entry Condition                    | Exit Condition                         | Key Indicators                                                        | Typical Round Range |
|-------|--------------------|------------------------------------|----------------------------------------|-----------------------------------------------------------------------|---------------------|
| 1     | Carry Accumulation | Round 1                            | deviation(t) < −0.02                   | P ≈ F; CarryTrader and HedgedCarryTrader building long positions      | Rounds 1–30         |
| 2     | Initial Stress     | deviation(t) < −0.02               | deviation(t) < −0.05                   | CarryTrader begins selling; HedgedCarryTrader volatility check active | Rounds 15–40        |
| 3     | Cascade Onset      | deviation(t) < −0.05               | LCF stop_loss triggered                | FundingCurrencyBuyer activates; velocity increasing                   | Rounds 25–50        |
| 4     | Full Cascade       | LCF stop_loss triggered            | deviation reaching minimum             | LCF forced selling dominant; velocity at peak; drawdown accelerating  | Rounds 30–60        |
| 5     | Recovery           | deviation at minimum; LCF sold out | deviation > −0.05 or end of simulation | FCB buying + mean reversion pulling price back; AC1 turning negative  | Rounds 50–200       |

### Quantitative Phase Transition Criteria

**Phase 1 → 2**: First round where deviation < −0.02 AND CarryTrader generates sell order. Diagnostic: check if CarryTrader sell quantity > 0.

**Phase 2 → 3**: First round where deviation < −0.05. Diagnostic: FundingCurrencyBuyer should have activated by this point.

**Phase 3 → 4**: First round where LeveragedCarryFund generates a forced sell (stop_loss = −0.03 breached). Diagnostic: LCF sell volume = min(4000, position) should appear in agent order log.

**Phase 4 → 5**: LCF sell volume drops to zero (position exhausted or deviation recovering). Diagnostic: velocity drops sharply; AC1 turns negative or near-zero.

### Observable Signatures by Phase

| Phase          | CarryTrader           | LeveragedCarryFund       | HedgedCarryTrader     | FundingCurrencyBuyer | AC1               |
|----------------|-----------------------|--------------------------|-----------------------|----------------------|-------------------|
| Accumulation   | Buying                | Holding                  | Buying (if vol low)   | Inactive             | ≈ 0               |
| Initial Stress | Selling (small)       | Holding                  | Selling (if vol high) | Inactive             | Slightly positive |
| Cascade Onset  | Selling (growing)     | Triggered (selling)      | May have exited       | Activated (buying)   | +0.2 to +0.4      |
| Full Cascade   | Selling (max)         | Forced sell (4000/round) | Exited (zero volume)  | Active (500/round)   | +0.3 to +0.5      |
| Recovery       | Inactive or small buy | Exhausted (zero volume)  | Possibly re-entering  | Still active         | −0.2 to 0         |


## §5 Cross-Variant Comparison Framework

### Comparison Protocol

1. **Normalize**: Same initial_price (1.20), fundamental (1.20), λ, γ across all variants.
2. **Statistical test**: Compare max_drawdown, unwind_velocity, recovery_ratio, and crisis_onset_round across variants using mean ± std over 10 runs per variant.
3. **Key comparison axes**:
   - **Cascade timing**: Rule variant should trigger cascade consistently; LLM may show delayed activation (deliberation before forced exit).
   - **Recovery**: Rag variant potentially shows modified behavior if 2008 JPY or 2015 CHF historical knowledge is retrieved.
   - **Forced exit discipline**: Key test for LLM — does the LeveragedCarryFund persona faithfully execute the forced exit without deliberative delay?
   - **HedgedCarryTrader sophistication**: Does LLM persona for HedgedCarryTrader show better volatility awareness than Rule variant?

### Expected Cross-Variant Behavioral Differences

| Behavioral Dimension            | Rule                       | LLM                                                                      | RuleLLM                      | Rag                                                    |
|---------------------------------|----------------------------|--------------------------------------------------------------------------|------------------------------|--------------------------------------------------------|
| LCF forced exit execution       | Exact threshold; immediate | May deliberate ("should I really exit now?"); possible 1–5 round delay   | Near-exact; ±20% on quantity | Modified by retrieved historical forced-exit knowledge |
| CarryTrader unwind timing       | Exact at deviation < −0.02 | May show earlier intuitive exit or later denial                          | Near-exact                   | May recall 2008 JPY dynamics and exit earlier          |
| FundingCurrencyBuyer activation | Exact at deviation < −0.05 | May activate earlier ("crisis is clearly underway")                      | Near-exact                   | May recall JPY safe-haven flow patterns                |
| HedgedCarryTrader vol exit      | Exact dual condition       | LLM may better articulate the volatility rationale but may also hesitate | Near-exact                   | May use historical volatility spikes as reference      |


## §6 Expected Results and Validation

### Expected Stylized Facts (Literature-Sourced)

| Stylized Fact                           | Target Value | Literature Source                     | DOI                              |
|-----------------------------------------|--------------|---------------------------------------|----------------------------------|
| Maximum FX drawdown                     | 10%–25%      | Brunnermeier, Nagel & Pedersen (2009) | 10.1086/593088                   |
| Recovery ratio                          | 0.3–0.7      | Rogoff (1996) PPP convergence         | 10.2307/2729217                  |
| Annualized volatility at crisis peak    | > 20%        | BIS (2022); Menkhoff et al. (2012)    | 10.1111/j.1540-6261.2012.01728.x |
| Cascade condition: LCF/FCB volume ratio | ≥ 8×         | Plantin & Shin (2018)                 | 10.3982/TE2739                   |
| Return AC1 during cascade               | > +0.2       | Lo & MacKinlay (1988)                 | 10.1093/rfs/1.1.41               |

### Cascade Condition Analytical Check

The cascade proceeds if:
```
Cascade condition: (base_qty × leverage × N_LCF) > (position_size × N_FCB)
Default: (800 × 5.0 × 2) = 8000 > (500 × 2) = 1000 → cascade expected
```

Sensitivity: If FCB position_size is increased to 2000, cascade condition becomes marginal (8000 vs. 4000). If position_size = 4000: cascade may be arrested. This provides a natural "circuit breaker" test by adjusting FCB capacity.

### Validation Failure Diagnostics

| Failure Mode        | Symptom              | Likely Cause                                    | Corrective Action                                    |
|---------------------|----------------------|-------------------------------------------------|------------------------------------------------------|
| No cascade          | Drawdown < 5%        | LCF stop_loss not triggered; noise insufficient | Reduce stop_loss to 0.02; increase noise_std to 0.04 |
| Too shallow         | Drawdown 5–8%        | LCF position small relative to λ                | Increase LCF leverage to 7.0 or base_qty to 1200     |
| No recovery         | recovery_ratio < 0.1 | γ too low; FCB insufficient                     | Increase γ to 0.03; increase FCB position_size       |
| Cascade too fast    | t_onset < 5          | LCF stop_loss too low; noise too high           | Increase stop_loss to 0.04; reduce noise_std         |
| FCB never activates | FCB volume = 0       | risk_threshold too high; crash not reaching −5% | Reduce risk_threshold to 0.03; verify cascade depth  |


## §7 Visualization Catalogue

| Plot Name                         | Type        | X-axis     | Y-axis                          | Overlays / Annotations                                | Purpose                                                           |
|-----------------------------------|-------------|------------|---------------------------------|-------------------------------------------------------|-------------------------------------------------------------------|
| FX Rate vs. Fundamental           | Line        | Rounds     | FX Rate (P)                     | Fundamental dashed; −5%, −10%, −15% crisis levels     | Primary crash dynamics; accumulation → cascade → recovery         |
| FX Deviation Time Series          | Line        | Rounds     | Deviation (%)                   | Phase markers; −3% (LCF stop_loss), −5% (FCB trigger) | Cascade phase identification; crisis thresholds                   |
| Per-Round Price Velocity          | Line        | Rounds     |                                 | ΔP                                                    | per round                                                         |
| Annualized Volatility Time Series | Line        | Rounds     | Annualized vol (%)              | vol_threshold = 5%; HedgedCarryTrader exit marker     | Volatility regime transitions; HCT activation logic validation    |
| Return Distribution               | Histogram   | Return (%) | Frequency                       | Normal distribution overlay                           | Documents carry crash negative skewness                           |
| Agent Volume by Type              | Stacked Bar | Agent      | Total sell volume               | Cascade condition reference (8000:1000)               | Volume attribution; cascade dominance validation                  |
| Per-Round Net Demand              | Area        | Rounds     | Net demand (buy−sell)           | Zero line; colored by agent type contribution         | Tests cascade condition; FCB vs. LCF volume balance               |
| Return Autocorrelation (Rolling)  | Line        | Rounds     | AC1 (10-round window)           | Zero line; +0.2 and −0.1 thresholds                   | Cascade momentum vs. recovery regime identification               |
| Recovery Ratio by Variant         | Bar         | Variant    | Recovery ratio                  | 0.3 and 0.7 target range                              | Cross-variant stabilization effectiveness comparison              |
| HedgedCarryTrader vs. LCF Exit    | Scatter     | Run        | HCT exit round / LCF exit round | 45-degree line (simultaneous)                         | Tests whether HCT exits earlier than LCF (sophistication test)    |
| Cross-Variant FX Deviation        | Line        | Rounds     | Deviation (%)                   | One line per variant; Rule as reference               | Quantifies crash depth and recovery differences by variant        |
| Rule Adherence (RuleLLM)          | Bar         | Agent      | Adherence rate (%)              | 80% target threshold                                  | Validates forced exit rule adherence in RuleLLM variant           |
| RAG Retrieval Rate (Rag)          | Bar         | Agent      | Retrieval success (%)           | 70% target threshold                                  | Measures historical carry crash knowledge retrieval effectiveness |
