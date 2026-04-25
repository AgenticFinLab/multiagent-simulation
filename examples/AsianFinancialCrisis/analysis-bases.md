# AsianFinancialCrisis — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                                                   | Metric(s)                                         | Expected Finding                                                                      |
|-----------|-------------------------------------------------------------------------------------|---------------------------------------------------|---------------------------------------------------------------------------------------|
| O1        | Does the simulation produce a currency crisis of calibrated depth?                  | Max drawdown, price deviation                     | Drawdown [30%, 60%]; deviation reaches −30% to −60% at peak                           |
| O2        | How quickly does the crisis develop?                                                | Crisis onset round, crisis velocity               | Onset within rounds 10–20; velocity > 2% per round during cascade                     |
| O3        | Does the HotMoneyFunder → ContagionTrader cascade sequence operate correctly?       | Agent activation sequence, sell volume by round   | HotMoneyFunder activates first; ContagionTrader follows 2–5 rounds later              |
| O4        | Does IMFRescuer activate at the correct threshold and provide measurable floor?     | IMF activation round, price floor after IMF entry | IMF activates at first round with deviation < −5%; price decline decelerates post-IMF |
| O5        | Does contagion signal produce momentum-driven selling (positive AC1 during crisis)? | Return autocorrelation during crisis phase        | AC1 > 0.25 during contagion phase                                                     |
| O6        | How do variants differ in crisis depth, speed, and recovery?                        | All core metrics across Rule/LLM/RuleLLM/Rag      | LLM shows highest variance; RuleLLM near Rule; Rag potentially moderated by knowledge |


## 2. Core Metrics Catalogue

### Metric: Price Deviation from Fundamental

- **Category**: Price Dynamics / Phenomenon-Specific
- **Definition**: Signed percentage difference between current exchange rate / price and pre-crisis fundamental value.
- **Formula**:
  ```
  deviation(t) = (P(t) − F) / F   where F = 100.0 (constant)
  ```
- **Derivation Rationale**: The deviation from pre-crisis fundamental is the primary measure of currency crisis severity. A negative deviation represents currency depreciation (the core crisis phenomenon). Using a constant F = 100.0 isolates the crisis-driven component from any fundamental change — all deviation is attributable to the capital-flow dynamics modelled by the simulation agents.
- **Academic Calibration Source**:
  - Radelet, S., & Sachs, J. (1998). The East Asian financial crisis. *Brookings Papers*, 1998(1), 1–90. https://doi.org/10.1353/eca.1998.0009 — documents currency depreciations of 30–83% in the 1997 crisis; calibrates target range for simulation max deviation.
  - Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises. *AER*, 89(3), 473–500. https://doi.org/10.1257/aer.89.3.473 — finds that currencies depreciate an average of 25–40% in balance-of-payments crises before IMF intervention; calibrates `rescue_threshold = −0.05` as a lower bound.
- **Interpretation**:
  - deviation > −0.02: Pre-crisis stable zone; hot money holds position
  - deviation ∈ (−0.05, −0.02): Early crisis; HotMoneyFunder active; ContagionTrader approaching threshold
  - deviation ∈ (−0.10, −0.05): Contagion phase; both destabilising agents active; IMFRescuer just activated
  - deviation < −0.10: Deep crisis; peak contagion cascade
  - deviation < −0.30: Target calibration zone for peak severity
- **Normal Range**: Peak deviation −30% to −60% (from Radelet & Sachs 1997 data)
- **Red Flag**: Maximum deviation < −10% → crisis too mild; check HotMoneyFunder position size and λ

---

### Metric: Maximum Drawdown

- **Category**: Price Dynamics / Crisis Severity
- **Definition**: Largest peak-to-trough price decline as a percentage of the peak price, representing the worst-case currency depreciation.
- **Formula**:
  ```
  max_drawdown = max_{t₁ < t₂} [(P(t₁) − P(t₂)) / P(t₁)] × 100%
  ```
  Since initial price = fundamental = 100.0, max_drawdown ≈ |min(deviation)| × 100% in most runs.
- **Derivation Rationale**: In a currency crisis context, max_drawdown directly measures the peak depreciation — the primary empirical indicator of crisis severity. It corresponds to "how much did the baht/won/rupiah fall from peak to trough?" — the question policymakers and researchers use to classify crisis severity.
- **Academic Calibration Source**:
  - Historical data: Thai baht −55%, Indonesian rupiah −83%, South Korean won −54%, Malaysian ringgit −48% (Radelet & Sachs, 1998).
  - Kaminsky & Reinhart (1999): average currency crisis produces −25% to −40% drawdown in their 26-episode sample; extreme cases (Indonesia, Russia 1998) produce −50% to −80%.
  - Simulation target: [30%, 60%] — the moderate-to-severe range that excludes the most extreme cases but captures the typical 1997 pattern.
- **Normal Range**: [30%, 60%]
- **Red Flag**: max_drawdown < 15% → contagion mechanism too weak; max_drawdown > 80% → calibration too extreme

---

### Metric: Crisis Velocity (Maximum Round-to-Round Price Change)

- **Category**: Phenomenon-Specific / Speed
- **Definition**: Maximum absolute price change per round during the crisis phase, measuring the speed of the crisis cascade.
- **Formula**:
  ```
  crisis_velocity = max_t |P(t) − P(t−1)|
  ```
  Computed over all rounds (the maximum will occur during the crisis phase).
- **Derivation Rationale**: Currency crises are characterised by "sudden stop" dynamics — the deterioration is not gradual but sharp and concentrated in a few rounds. Crisis velocity distinguishes sharp sudden-stop crises (ArchegosCollapse-style) from gradual corrections (AnchoringEffect-style). For the Asian crisis, Radelet & Sachs (1998) document that the Thai baht fell 15–20% in a single day after depegging.
- **Academic Calibration Source**:
  - Radelet & Sachs (1998): Thai baht −15–20% on depegging day; Indonesian rupiah −20% on October 23, 1997 ("Black Thursday"); consistent with simulation velocity target > 2% per round.
  - Calvo, G. A. (1998). Capital flows and capital-market crises: sudden stops typically produce concentrated price drops of 10–30% in 1–5 trading days, translated to 1–5 rounds in the simulation.
- **Normal Range**: > 2.0% per round during crisis cascade; peak velocity > 5% in most calibrations
- **Red Flag**: Crisis velocity < 1% per round → crisis too gradual; increase λ or HotMoneyFunder sell_ratio

---

### Metric: Return Autocorrelation (Lag-1)

- **Category**: Behavioral / Cascade Dynamics
- **Definition**: Pearson lag-1 autocorrelation of price returns across all rounds, identifying crisis momentum (positive AC1) vs. recovery mean reversion (negative AC1).
- **Formula**:
  ```
  r(t)  = (P(t) − P(t−1)) / P(t−1)
  AC1   = corr(r(t), r(t−1))   over specified phase window
  ```
- **Derivation Rationale**: The contagion cascade creates a positive feedback loop: selling → price falls → more agents hit thresholds → more selling. This produces strong positive return autocorrelation during the crisis phase. The AC1 sign shift (positive during crisis → negative during recovery) is the statistical signature of the phase transition.
- **Academic Calibration Source**:
  - Kaminsky, G. L., & Reinhart, C. M. (1999): contagion episodes exhibit positive AC1 ≈ 0.3–0.5 during the crisis phase in their cross-country dataset; mean reversion during recovery produces AC1 ≈ −0.1 to −0.3.
  - Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 — the funding-liquidity spiral they document predicts strong positive AC1 during capital flow crises.
- **Normal Range**: AC1 > 0.25 during crisis cascade phase; < 0 during recovery
- **Red Flag**: AC1 ≈ 0 throughout → cascade mechanism not creating momentum; check contagion signal formula

---

### Metric: Agent-Type Volume by Phase

- **Category**: Behavioral Validation
- **Definition**: Total signed net demand and unsigned volume by agent type, decomposed into crisis and recovery phases.
- **Formula**:
  ```
  sell_volume_type(crisis) = Σ_{t in crisis phase} Σ_{i ∈ type} max(0, −quantity_i(t))
  buy_volume_type(recovery) = Σ_{t in recovery phase} Σ_{i ∈ type} max(0, quantity_i(t))
  ```
- **Derivation Rationale**: The expected pattern is highly asymmetric: HotMoneyFunder + ContagionTrader should dominate sell volume during crisis; IMFRescuer + ValueContrarian should dominate buy volume during recovery. Confirming this pattern validates that each agent's behavioural design is producing the theoretically predicted market impact.
- **Academic Calibration Source**:
  - Radelet & Sachs (1998): foreign capital outflows dominated the 1997 Asian crisis; IMF and bilateral rescue capital provided the stabilising floor. The expected volume pattern in the simulation directly mirrors this real-world dynamic.
  - Kaminsky & Reinhart (1999): domestic bank deleveraging (analogous to ContagionTrader) contributed 25–40% of total capital outflows.
- **Normal Range**: HotMoneyFunder + ContagionTrader account for > 70% of sell volume during crisis phase; IMFRescuer accounts for > 50% of buy volume during early recovery
- **Red Flag**: IMFRescuer volume = 0 → never activated; check rescue_threshold and crisis depth

---

### Metric: Crisis Onset Round

- **Category**: Phenomenon-Specific / Timing
- **Definition**: First round in which deviation crosses −10% (significant crisis threshold indicating the crisis is fully established beyond initial HotMoneyFunder reversal).
- **Formula**:
  ```
  t_onset = min { t : deviation(t) < −0.10 }
  ```
  Note: The −10% threshold (vs. −2% for HotMoneyFunder trigger) represents when the crisis has propagated beyond the initial hot money reversal to the broader contagion phase.
- **Derivation Rationale**: −10% deviation corresponds to "clear crisis" territory — beyond simple hot money retreat into active contagion. Kaminsky & Reinhart (1999) use a 10% depreciation threshold as the standard definition of a currency crisis episode in their dataset.
- **Academic Calibration Source**:
  - Kaminsky & Reinhart (1999): define currency crisis as ≥ 10% depreciation in a single quarter; consistent with `t_onset = first round where deviation < −0.10`.
  - Historical data: Thai baht reached −10% within 2 days of depegging; Indonesian rupiah reached −10% within 1 week; for a 50-round simulation, target t_onset ∈ [10, 20] rounds.
- **Normal Range**: Rounds 10–20
- **Red Flag**: t_onset = NaN (never reaches −10%) → calibration too conservative; t_onset < 5 → crisis starts too fast

---

### Metric: IMF Rescue Activation Round

- **Category**: Phenomenon-Specific / Rescue Timing
- **Definition**: First round in which IMFRescuer activates (deviation first crosses −5% threshold), measuring the delay between crisis onset and rescue.
- **Formula**:
  ```
  t_imf = min { t : deviation(t) < −0.05 }
  ```
- **Derivation Rationale**: The gap between crisis onset (`t_onset`) and IMF activation (`t_imf`) is a key policy-relevant measure. In the 1997 crisis, there was a significant lag between the initial Thai baht depegging (July 2) and the first IMF program announcement (August 14) — approximately 6 weeks. In simulation terms, this corresponds to the gap between HotMoneyFunder first activation (rounds 5–10) and IMFRescuer activation (rounds 10–25 when deviation reaches −5%).
- **Academic Calibration Source**: Corsetti, G., Pesenti, P., & Roubini, N. (1999) document the 6–8 week delay in 1997 programs; Fischer (1999) argues this delay deepened the crisis unnecessarily.
- **Normal Range**: `t_imf` ∈ rounds 10–25; `t_imf − t_onset` ∈ [5, 15] rounds
- **Red Flag**: `t_imf = NaN` → crisis never deep enough to trigger IMF; `t_imf < t_onset` → logical error in thresholds


## 3. Analysis Dimensions

### Dimension 1: Price Crisis Dynamics

- **Purpose**: Verify that the simulated crisis depth, speed, and trajectory match the 1997 Asian crisis calibration targets
- **Metrics Used**: Price deviation, max drawdown, crisis velocity, crisis onset round
- **Visualization**: (a) Price vs. Fundamental time series with crisis threshold lines (−5%, −10%, −30%); (b) deviation over time with phase annotations; (c) round-by-round price change bar chart
- **Expected Pattern**: Price stable at 100 for 5–10 rounds; rapid fall to −30% to −60% over rounds 10–30; floor established by IMFRescuer and ValueContrarian; partial recovery in rounds 30–50
- **Comparison Baseline**: Thai baht −55%, Indonesian rupiah −83%, South Korean won −54%

### Dimension 2: Agent Behavior and Cascade Sequencing

- **Purpose**: Verify the theoretically predicted cascade sequence: HotMoneyFunder → ContagionTrader → IMFRescuer → ValueContrarian
- **Metrics Used**: Agent-type volume by phase, agent activation rounds
- **Visualization**: Round-by-round sell volume bar chart (stacked by agent type); overlay with price deviation curve
- **Expected Pattern**: HotMoneyFunder first activates (threshold = −2%); ContagionTrader follows 2–5 rounds later (composite signal threshold = −0.025); IMFRescuer activates at −5%; ValueContrarian at −8%

### Dimension 3: Contagion Signal Analysis

- **Purpose**: Confirm the dual-channel contagion mechanism (deviation + momentum) produces expected cascade dynamics
- **Metrics Used**: Return autocorrelation (crisis phase), contagion signal time series
- **Visualization**: Return time series with phase annotations; autocorrelation chart; contagion signal components (deviation vs. return) plotted separately
- **Expected Pattern**: AC1 > 0.25 during cascade phase (positive feedback from dual-signal contagion); signal turns positive as IMF rescue stabilises prices

### Dimension 4: Rescue Effectiveness Analysis

- **Purpose**: Measure IMFRescuer's floor-setting effectiveness and the gap between crisis onset and rescue
- **Metrics Used**: IMF activation round, price floor after IMF entry, rate of price decline before vs. after IMF
- **Visualization**: Price trajectory with IMF activation marker; rate-of-change before vs. after IMF entry
- **Expected Pattern**: Price decline rate decelerates in rounds immediately after IMFRescuer activates; complete arrest of decline requires additional ValueContrarian activation

### Dimension 5: Cross-Variant Comparison

- **Purpose**: Compare crisis dynamics across Rule, LLM, RuleLLM, Rag
- **Metrics Used**: All core metrics across all variants
- **Visualization**: Side-by-side price curves (4 variants); comparison table with mean ± std
- **Expected Pattern**: Rule: fastest onset, most consistent depth; LLM: most variable (crisis persona may amplify or delay); RuleLLM: near Rule; Rag: potentially moderated by historical crisis knowledge


## 4. Phase Analysis Framework

### Phase Detection Rules

| Phase | Name                  | Entry Condition                                          | Exit Condition                            | Key Indicators                                                                       | Typical Round Range |
|-------|-----------------------|----------------------------------------------------------|-------------------------------------------|--------------------------------------------------------------------------------------|---------------------|
| 1     | Stable                | Round 1                                                  | deviation(t) < −0.02                      | All agents near equilibrium; NoiseTrader dominant                                    | Rounds 1–8          |
| 2     | Hot Money Exit        | deviation(t) < −0.02                                     | deviation(t) < −0.025 (contagion trigger) | HotMoneyFunder selling; price declining; AC1 turning positive                        | Rounds 5–15         |
| 3     | Contagion Cascade     | deviation(t) < −0.025 (first ContagionTrader activation) | deviation at minimum                      | Both destabilising agents active; AC1 > 0.25; high crisis velocity                   | Rounds 10–25        |
| 4     | Crisis Peak and Floor | deviation at minimum                                     | IMFRescuer active for ≥ 3 rounds          | IMFRescuer and ValueContrarian buying; selling pressure weakening                    | Rounds 20–35        |
| 5     | Recovery              | Price rising from minimum                                | deviation(t) > −0.10                      | IMFRescuer continuing deployment; AC1 turns negative; HotMoneyFunder exits exhausted | Rounds 30–50        |

### Quantitative Phase Criteria

**Phase 2 observable signatures**:
- HotMoneyFunder places sell orders for ≥ 2 consecutive rounds
- Deviation falls below −0.02
- Crisis velocity > 1% per round

**Phase 3 observable signatures**:
- ContagionTrader composite signal < −0.025 for ≥ 1 round
- Both HotMoneyFunder and ContagionTrader selling in same round
- AC1 of last 10 rounds > 0.20

**Phase 4 observable signatures**:
- Deviation at or near minimum
- IMFRescuer first buy order placed
- Selling volume declining from previous round

**Phase 5 observable signatures**:
- Price rising for ≥ 3 consecutive rounds
- IMFRescuer continuing to buy
- AC1 turning negative (mean reversion)

### Phase Transition Failure Diagnostics

| Failure                          | Symptom                        | Likely Cause                                       | Fix                                     |
|----------------------------------|--------------------------------|----------------------------------------------------|-----------------------------------------|
| Phase 2 never starts             | Deviation never reaches −2%    | HotMoneyFunder position too small or λ too low     | Increase initial_position or λ          |
| Phase 3 delayed (> round 25)     | ContagionTrader not activating | Contagion threshold too low (−0.025 not reached)   | Reduce contagion_threshold to −0.015    |
| Phase 4 never stabilises         | Price falls indefinitely       | IMFRescuer cash exhausted before floor established | Increase initial_cash; reduce buy_ratio |
| Crisis too mild (drawdown < 15%) | Weak cascade                   | λ too low; sell ratios too small                   | Increase λ from 0.04 to 0.06            |


## 5. Cross-Variant Comparison Framework

### Comparison Protocol

1. **Normalize**: Identical initial conditions: `initial_price = fundamental = 100.0`, same agent configuration, same simulation length
2. **Statistical test**: 10 runs per variant; mean ± std; Mann-Whitney U test for non-normal distributions (crisis metrics tend to be skewed)
3. **Key comparison axes**:

| Axis               | Question                         | Expected Direction                                                                          |
|--------------------|----------------------------------|---------------------------------------------------------------------------------------------|
| Crisis depth       | Peak deviation magnitude         | Rule: consistent; LLM: most variable (may deepen through panic narrative)                   |
| Crisis onset speed | t_onset round                    | Rule = RuleLLM < LLM (formula triggers faster than persona hesitation)                      |
| IMF timing         | t_imf round                      | Rule = RuleLLM (exact threshold); LLM possibly delayed (persona may not recognise severity) |
| Recovery speed     | Rounds from peak to 50% recovery | Rag potentially faster (historical knowledge of recovery timelines)                         |
| Behavioral realism | Qualitative narrative quality    | LLM > Rag > RuleLLM > Rule                                                                  |

4. **Reporting format**:

| Metric                      | Rule | LLM (mean ± σ) | RuleLLM (mean ± σ) | Rag (mean ± σ) |
|-----------------------------|------|----------------|--------------------|----------------|
| Max drawdown (%)            | X.XX | X.XX ± X.XX    | X.XX ± X.XX        | X.XX ± X.XX    |
| Crisis onset round          | X    | X ± X          | X ± X              | X ± X          |
| Crisis velocity (% / round) | X.XX | X.XX ± X.XX    | X.XX ± X.XX        | X.XX ± X.XX    |
| AC1 (crisis phase)          | X.XX | X.XX ± X.XX    | X.XX ± X.XX        | X.XX ± X.XX    |
| IMF rescue round            | X    | X ± X          | X ± X              | X ± X          |


## 6. Expected Results and Validation

### Calibration Targets from Literature

| Metric                             | Target Range   | Calibration Source                                                            | Validation Method                                          |
|------------------------------------|----------------|-------------------------------------------------------------------------------|------------------------------------------------------------|
| Max drawdown                       | [30%, 60%]     | Thai baht −55%, Korean won −54%; Kaminsky & Reinhart (1999) average −30–40%   | Run 10 Rule trials; reject if mean < 20%                   |
| Crisis onset round                 | [10, 20]       | Kaminsky & Reinhart: 10% depreciation within 1–3 weeks of trigger             | Check t_onset in all runs                                  |
| Crisis velocity                    | > 2% per round | Radelet & Sachs (1998): 15–20% in one day after depegging                     | Compute max single-round price change                      |
| Return AC1 (crisis phase)          | > 0.25         | Kaminsky & Reinhart (1999): contagion produces positive AC1                   | Compute over Phase 3 rounds only                           |
| IMF rescue round                   | [10, 25]       | Corsetti et al. (1999): 6–8 weeks after initial trigger                       | Check t_imf in all runs                                    |
| Recovery (% of drawdown recovered) | [40%, 70%]     | Historical 1998–1999 recovery; partial not full recovery in simulation window | Compute deviation at last round relative to peak deviation |

### Sensitivity Discussion

- **λ sensitivity**: λ = 0.04 produces moderate crisis; λ = 0.08 doubles crisis velocity and depth. Test: λ ∈ {0.02, 0.04, 0.06, 0.08}.
- **IMFRescuer cash sensitivity**: Reducing initial_cash from $5M to $500K dramatically reduces floor effectiveness; test: {$500K, $1M, $2M, $5M}. Document the threshold below which crisis depth increases by > 20%.
- **Threshold sensitivity**: Reducing `reversal_threshold` from 0.02 to 0.01 accelerates crisis onset by ~5 rounds. Test: {0.01, 0.02, 0.03, 0.05}.

### Validation Failure Signs

| Failure Sign          | Interpretation                       | Parameter Fix                                              |
|-----------------------|--------------------------------------|------------------------------------------------------------|
| Max drawdown < 15%    | Crisis too mild                      | Increase λ or HotMoneyFunder sell_ratio                    |
| t_onset > 30          | Crisis starts too late               | Reduce reversal_threshold or increase initial_position     |
| IMFRescuer volume = 0 | Never activated                      | Reduce rescue_threshold; check crisis depth reaches −5%    |
| AC1 ≈ 0 during crisis | Cascade not self-reinforcing         | Increase λ; check ContagionTrader composite signal formula |
| Max drawdown > 80%    | Crisis too extreme                   | Reduce λ; add more stabilising agents                      |
| Recovery never starts | IMF and ValueContrarian insufficient | Increase initial_cash or reduce thresholds                 |


## 7. Visualization Catalogue

| Plot Name                  | Type           | X-axis     | Y-axis             | Overlays                                                     | Purpose                                             |
|----------------------------|----------------|------------|--------------------|--------------------------------------------------------------|-----------------------------------------------------|
| Price vs Fundamental       | Line           | Rounds     | Price              | F = 100 dashed; −5%, −10%, −30% threshold lines; phase bands | Primary crisis depth verification                   |
| Price Deviation            | Line           | Rounds     | deviation (%)      | −2%, −5%, −8%, −10% thresholds; phase annotations            | Crisis cascade trajectory                           |
| Crisis Velocity            | Bar            | Rounds     |                    | ΔP                                                           | per round                                           |
| Return Time Series         | Line           | Rounds     | Return (%)         | Zero line; phase bands                                       | Momentum vs. mean reversion identification          |
| Return Distribution        | Histogram      | Return (%) | Frequency          | Normal overlay                                               | Left fat tail from cascade selling                  |
| Agent Volume by Phase      | Stacked bar    | Rounds     | Net volume by type | Phase band overlays                                          | Cascade sequence validation                         |
| Agent Sell Sequence        | Event timeline | Rounds     | Agent type         | First activation markers                                     | Visual confirmation of HMF → CT → IMF → VC sequence |
| Cross-Variant Price Curves | Line (4)       | Rounds     | Price              | F dashed; same axis scale                                    | Compare crisis depth across variants                |
| Rule Adherence (RuleLLM)   | Bar            | Agent      | Adherence rate     | 80% target                                                   | Validate LLM follows quantitative thresholds        |
| RAG Retrieval Rate (Rag)   | Bar            | Agent      | Success rate       | 50% threshold                                                | Measure knowledge retrieval effectiveness           |
