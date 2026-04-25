# AvailabilityBias — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                                                        | Metric(s)                                       | Expected Finding                                                                        |
|-----------|------------------------------------------------------------------------------------------|-------------------------------------------------|-----------------------------------------------------------------------------------------|
| O1        | Does availability bias produce measurable persistent deviation from fundamental value?   | Price deviation, bias persistence score         | Availability-biased agents create 5–15% persistent mispricings vs. rational baseline    |
| O2        | Which availability channel (recency vs. media) generates larger or more persistent bias? | Channel-specific volume, deviation by phase     | RecentEventOverweighter: larger per-round impact; MediaInfluencedTrader: more sustained |
| O3        | Do stabilizing agents (SystematicAnalyst, ValueTrader) limit mispricing effectively?     | Stabilization ratio, floor/ceiling activation   | Combined stabilization limits maximum deviation to ≤15% in most runs                    |
| O4        | Does availability bias create measurable overreaction followed by reversal?              | Return autocorrelation, post-peak reversal rate | Positive AC1 during bias episode; negative AC1 during correction                        |
| O5        | How does the LLM variant's bias magnitude compare to the Rule baseline?                  | Cross-variant deviation, agent volume           | LLM may over- or under-apply bias intensity; RuleLLM near-Rule                          |
| O6        | Does the Rag variant's historical overreaction context change agent behavior?            | Rag vs. Rule deviation comparison               | Rag may show moderated bias if agents "recall" correction outcomes                      |


## 2. Core Metrics Catalogue

### Metric 1: Price Deviation from Fundamental

- **Category**: Price Dynamics / Bias Magnitude
- **Definition**: Percentage difference between market price and fundamental value; the primary measure of bias-induced mispricing
- **Formula**: deviation(t) = (P(t) − F) / F × 100, where F = 100.0 (constant)

**Derivation Rationale**: With constant fundamental (F = 100.0), all price movements represent endogenous cognitive bias effects rather than rational responses to news. Deviation is the most direct quantitative measure of the availability bias's market impact. Baker & Wurgler (2007) use similar deviation-from-fundamental measures to document sentiment-driven mispricing episodes. The formula is scale-independent (percentage) enabling comparison across simulation variants.

**Academic Calibration Source**: Baker, M., & Wurgler, J. (2007). "Investor sentiment in the stock market." *Journal of Economic Perspectives*, 21(2), 129–151. DOI: 10.1257/jep.21.2.129. Historical availability-bias-driven mispricings: 5–15% for typical episodes (post-announcement drift, sentiment cycles); up to 30% for extreme events (COVID crash initial phase). Simulation target: 5–15% peak deviation.

- **Interpretation**:
    - 0%: Price at fundamental — no net bias effect
    - 1%–5%: Mild bias effect — consistent with noise-level availability activation
    - 5%–15%: Moderate bias episode — target zone; consistent with Baker & Wurgler (2007) sentiment-driven mispricings
    - > 15%: Strong bias effect — all biased agents actively reinforcing direction; stabilizing agents overwhelmed
- **Normal Range**: −15% to +15%; most rounds within ±5%
- **Red Flag**: Deviation never exceeds ±3% → biased agents not generating sufficient signal; check recency_weight and media_weight. Deviation exceeds ±20% persistently → stabilizing agents insufficient; increase position_size or reduce λ.

---

### Metric 2: Bias Persistence Score

- **Category**: Phenomenon-Specific / Temporal Dynamics
- **Definition**: Fraction of simulation rounds in which deviation remains above a threshold magnitude (|deviation| > 0.05) continuously for ≥5 rounds; measures how long availability bias episodes last
- **Formula**: persistence_score = count{t : all of t, t−1, t−2, t−3, t−4 have |deviation| > 0.05} / (T − 4)

**Derivation Rationale**: Availability bias differs from cascade crises in its temporal dynamics: it creates persistent moderate mispricings rather than acute crashes. The persistence score quantifies this "slow burn" characteristic — how many simulation rounds feature sustained bias-driven mispricing. Tetlock (2007) documents that media-driven return effects persist for 2–3 weeks (consistent with 5+ round persistence in simulation terms). De Bondt & Thaler (1985) document 3-year overreaction cycles — at the simulation's time scale, this corresponds to multi-round persistent episodes.

**Academic Calibration Source**: Tetlock, P. C. (2007). "Giving content to investor sentiment." *Journal of Finance*, 62(3), 1139–1168. DOI: 10.1111/j.1540-6261.2007.01232.x. Media-driven effects persist 2–3 weeks; De Bondt & Thaler (1985) overreaction persists 2–3 years. Calibration target: persistence_score ≥ 0.10 (10%+ of rounds in sustained episode).

- **Interpretation**:
    - < 5%: Low persistence — bias episodes are transient; stabilizing agents correct quickly
    - 5%–20%: Moderate persistence — target zone; consistent with Tetlock's 2–3 week media effect
    - > 20%: High persistence — bias overwhelms stabilizing forces; significant sustained mispricing
- **Normal Range**: 5%–20% for this calibration
- **Red Flag**: Persistence score = 0 → bias creates no sustained episodes; increase recency_weight to ≥ 3.0 or check noise_std not too high. Persistence > 40% → stabilizing agents inactive or under-parameterized.

---

### Metric 3: Availability Bias Magnitude (Overreaction Measure)

- **Category**: Phenomenon-Specific / Agent-Level
- **Definition**: Ratio of biased agent actual trade size to the rational baseline trade size at the same deviation; directly quantifies how much agents are overreacting relative to rational behavior
- **Formula**: bias_magnitude(i, t) = Q_actual_i(t) / Q_rational(t) where Q_rational(t) = min(300, |deviation(t)| × 5000) is the SystematicAnalyst's formula applied at the same deviation

**Derivation Rationale**: The core of availability bias is overreaction — biased agents trade larger quantities than their fundamental information warrants. Comparing biased agent trade sizes to the rational baseline (SystematicAnalyst's formula) directly quantifies the bias premium in action at each round. A bias_magnitude of 2.0 means the biased agent traded twice what rational analysis would justify. Tversky & Kahneman (1973) predict overweighting of 2–4× for highly salient events, suggesting bias_magnitude ≥ 2.0 during active availability episodes.

**Academic Calibration Source**: Tversky, A., & Kahneman, D. (1973). "Availability heuristic." *Cognitive Psychology*, 5(2), 207–232. DOI: 10.1016/0010-0285(73)90033-9. Expected overweighting: 2–4× for salient events. Simulation target: average bias_magnitude ≥ 2.0 when RecentEventOverweighter/MediaInfluencedTrader are active.

- **Interpretation**:
    - bias_magnitude = 1.0: No bias — agent trading exactly at rational level
    - 1.0–2.0: Mild bias — modest overreaction
    - 2.0–4.0: Target zone — consistent with Tversky & Kahneman (1973) experimental evidence
    - > 4.0: Extreme bias — verify recency_weight not miscalibrated
- **Normal Range**: 2.0–4.0 for RecentEventOverweighter; 2.5–4.5 for MediaInfluencedTrader (higher combined amplification)
- **Red Flag**: Average bias_magnitude < 1.5 → biased agents barely overreacting; recency_weight or media_weight too low. bias_magnitude consistently = Q_max/Q_rational (i.e., biased agent always maxing out at 300) → both biased and rational agents are capping at 300; signals are too large for the Q_max constraint to allow differentiation.

---

### Metric 4: Return Autocorrelation (Overreaction → Reversal Pattern)

- **Category**: Behavioral / Temporal Patterns
- **Definition**: Lag-1 autocorrelation of per-round returns; positive during availability bias episodes (momentum from overreaction); negative during correction (reversal)
- **Formula**: AC1(window) = Corr(r(t), r(t−1)) over a rolling window of W rounds

**Derivation Rationale**: The availability heuristic creates a two-phase return pattern: (1) Overreaction phase — availability-biased agents pile in the direction of the salient signal → positive AC1 (momentum); (2) Correction phase — mean reversion and rational agents correct the mispricing → negative AC1 (reversal). De Bondt & Thaler (1985) documented this exact AC1 sign flip in their 3-year overreaction/reversal study. In the simulation context, the rolling window captures this temporal dynamic at the round level.

**Academic Calibration Source**: De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreact?" *Journal of Finance*, 40(3), 793–805. DOI: 10.2307/2327804. AC1 during overreaction phase (extreme past losers/winners): positive momentum; AC1 during reversal phase: negative. Lo & MacKinlay (1988): short-horizon AC1 ≈ +0.1 to +0.3 in momentum-driven markets. Target: AC1 = +0.2 to +0.4 during bias episodes; AC1 = −0.1 to −0.2 during correction.

- **Interpretation**:
    - AC1 > +0.2: Availability bias generating momentum — overreaction reinforcing itself
    - AC1 ≈ 0: Random walk — bias effects and corrections balancing
    - AC1 < −0.1: Mean reversion/reversal dominant — rational correction underway
- **Normal Range**: +0.2 to +0.4 during active availability episodes; −0.2 to 0 during recovery
- **Red Flag**: AC1 ≈ 0 throughout → bias not creating persistent momentum; reduce γ to allow bias effects to build. AC1 strongly negative throughout → mean reversion dominates entirely; γ too high.

---

### Metric 5: Agent-Type Volume by Bias Channel

- **Category**: Volume / Activity / Attribution
- **Definition**: Total trading volume by agent type, disaggregated into recency-channel (RecentEventOverweighter), media-channel (MediaInfluencedTrader), rational (SystematicAnalyst, ValueTrader), and noise (NoiseTrader)
- **Formula**: volume_channel = Σ_t Σ_{i ∈ channel} |quantity_i(t)|

**Derivation Rationale**: To isolate the contribution of each availability bias channel, volume must be attributed to agent type. The Tetlock (2007) finding that media-driven effects are distinct from recency effects is testable only if the two channels can be separated. Volume attribution also validates that biased agents are actually trading (not holding too often due to threshold calibration) and that stabilizing agents are providing sufficient corrective volume.

**Academic Calibration Source**: Tetlock, P. C. (2007) documents that media-driven sentiment creates order flow distinct from momentum-driven order flow. Expected: roughly equal volumes from RecentEventOverweighter and MediaInfluencedTrader (different channels, similar parameterization). Expected: SystematicAnalyst volume ≥ 30% of biased agent volume to provide effective correction.

- **Interpretation**:
    - RecentEventOverweighter and MediaInfluencedTrader: each should contribute 15–25% of total volume
    - SystematicAnalyst + ValueTrader: combined ≥ 30% of total volume (sufficient for correction)
    - NoiseTrader: 20–40% (30% trade probability × random direction)
- **Normal Range**: RecentEventOverweighter: 15–25%; MediaInfluencedTrader: 15–25%; SystematicAnalyst: 10–20%; ValueTrader: 5–15% (activates less frequently); NoiseTrader: 20–40%
- **Red Flag**: ValueTrader volume = 0 → deviation never reached 10%; bias effects moderate. RecentEventOverweighter or MediaInfluencedTrader volume = 0 → salience threshold or amplification misconfigured; agent not activating.

---

### Metric 6: Stabilization Ratio

- **Category**: Phenomenon-Specific / Market Correction
- **Definition**: Ratio of stabilizing agent (SystematicAnalyst + ValueTrader) corrective volume to destabilizing agent (RecentEventOverweighter + MediaInfluencedTrader) biased volume during active bias episodes
- **Formula**: stabilization_ratio = [V_SystematicAnalyst + V_ValueTrader] / [V_RecentEvent + V_MediaInfluenced] during rounds where |deviation| > 0.05

**Derivation Rationale**: The fundamental tension in the availability bias simulation is between bias amplification and rational correction. The stabilization ratio directly measures the balance of forces. Baker & Wurgler (2007) find that institutional arbitrage partially but incompletely corrects sentiment-driven mispricing — implying stabilization_ratio should be < 1.0 (insufficient to fully correct bias) but > 0.3 (meaningful corrective force). Shleifer & Vishny (1997) predict stabilization_ratio < 0.5 in the presence of limits-to-arbitrage.

**Academic Calibration Source**: Baker, M., & Wurgler, J. (2007): institutional arbitrage corrects ~50–60% of sentiment mispricing on average. Shleifer, A., & Vishny, R. W. (1997). DOI: 10.2307/2329555. Target: stabilization_ratio = 0.4–0.8 (partial correction; persistent mispricing remains).

- **Interpretation**:
    - stabilization_ratio < 0.3: Bias overwhelms correction — persistent large mispricings
    - stabilization_ratio = 0.4–0.8: Target zone — partial correction consistent with limits-of-arbitrage
    - stabilization_ratio > 1.0: Rational agents dominate — bias effects corrected quickly; simulation too stable
- **Normal Range**: 0.4–0.8 during active bias episodes
- **Red Flag**: stabilization_ratio consistently < 0.3 → reduce Q_max for biased agents or increase SystematicAnalyst position limits. Ratio > 1.2 → stabilizing agents are over-parameterized relative to biased agents.

---

### Metric 7: Post-Episode Reversal Rate

- **Category**: Phenomenon-Specific / Dynamics Validation
- **Definition**: Average return in the 5 rounds following the peak deviation of a bias episode; tests whether overreaction is followed by mean-reverting correction (as De Bondt & Thaler predict)
- **Formula**: reversal_return(episode) = [P(t_peak + 5) − P(t_peak)] / P(t_peak); average over all identified bias episodes (defined as periods where |deviation| > 0.05 for ≥5 rounds)

**Derivation Rationale**: The behavioral finance literature's key prediction about availability bias is that overreaction is followed by reversal. De Bondt & Thaler (1985) document a 24.6% 3-year reversal for extreme past losers. Tetlock (2007) finds reversal within 2–3 weeks for media-driven returns. The post-episode reversal rate tests whether the simulation reproduces this canonical prediction: price moves driven by availability bias should reverse, not persist, as rational agents (SystematicAnalyst, ValueTrader) provide correction and biased agents exhaust their activation conditions.

**Academic Calibration Source**: De Bondt, W. F. M., & Thaler, R. H. (1985). DOI: 10.2307/2327804. Expected: reversal_return < 0 following positive bias episodes (overvaluation corrects); reversal_return > 0 following negative bias episodes (undervaluation corrects). Magnitude: 2–8% per 5 rounds in simulation (consistent with partial correction over short horizon).

- **Interpretation**:
    - No reversal (reversal_return same sign as episode direction): Bias is persistent, not correcting — overpowered stabilization
    - Reversal of 2%–8% per 5 rounds: Target zone — consistent with Tetlock (2007) and De Bondt & Thaler (1985)
    - Reversal > 10%: Overcorrection — γ mean reversion too aggressive
- **Normal Range**: −2% to −8% following positive bias episodes; +2% to +8% following negative episodes
- **Red Flag**: No reversal in any episode → stabilizing agents completely inactive; check ValueTrader and SystematicAnalyst parameterization.


## 3. Analysis Dimensions

### Dimension 1: Bias-Induced Price Dynamics

**Purpose**: Verify that availability bias produces measurable, literature-calibrated persistent deviations from fundamental value
**Metrics Used**: Price deviation (Metric 1), bias persistence score (Metric 2)
**Visualization**: Price vs. fundamental time series with ±5% and ±10% threshold lines; bias episode count and duration bar chart
**Expected Pattern**: Price oscillates around fundamental; availability bias agents create directional overreaction episodes of 5–15% lasting ≥5 rounds; stabilizing agents gradually correct; no permanent divergence

### Dimension 2: Overreaction Magnitude by Channel

**Purpose**: Isolate and compare the recency-channel (RecentEventOverweighter) versus media-channel (MediaInfluencedTrader) contributions to bias-driven mispricing
**Metrics Used**: Bias magnitude (Metric 3), agent-type volume (Metric 5)
**Visualization**: Side-by-side comparison of perceived_signal distribution (RecentEventOverweighter) vs. amplified_signal distribution (MediaInfluencedTrader); per-agent volume time series during bias episodes
**Expected Pattern**: Both channels produce overreaction (bias_magnitude > 2.0); recency channel is more volatile (reacts to recent_return noise); media channel is more persistent (responds to sustained deviation)

### Dimension 3: Overreaction-Reversal Dynamics

**Purpose**: Test whether availability bias produces the characteristic overreaction → reversal return pattern documented by De Bondt & Thaler (1985) and Tetlock (2007)
**Metrics Used**: Return autocorrelation (Metric 4), post-episode reversal rate (Metric 7)
**Visualization**: Rolling AC1 time series with phase markers (positive during bias episode, turning negative during correction); scatter plot of peak deviation vs. subsequent 5-round return reversal
**Expected Pattern**: Positive AC1 during active bias episodes; negative AC1 during post-episode correction; post-episode reversal_return consistently opposite in sign to episode direction

### Dimension 4: Stabilization Effectiveness

**Purpose**: Measure how effectively rational agents (SystematicAnalyst, ValueTrader) limit the magnitude and duration of availability-bias-driven mispricings
**Metrics Used**: Stabilization ratio (Metric 6), ValueTrader activation count
**Visualization**: Net demand decomposition (biased vs. rational agent contributions) during bias episodes; stabilization ratio over time; ValueTrader activation rounds annotated on price chart
**Expected Pattern**: Stabilization ratio = 0.4–0.8 (partial correction, consistent with limits-of-arbitrage); ValueTrader activates when |deviation| > 10%; combined stabilization limits max persistent deviation to ≤15%

### Dimension 5: Cross-Variant Comparison

**Purpose**: Compare bias magnitude, persistence, and reversal patterns across Rule, LLM, RuleLLM, and Rag variants
**Metrics Used**: All core metrics (1–7) by variant
**Visualization**: Side-by-side price deviation curves; bar chart of mean ± std for each metric across 10 runs per variant
**Expected Pattern**: Rule variant most deterministic; LLM variant may show stronger or weaker bias depending on persona; Rag variant potentially moderated if historical overreaction correction examples are retrieved


## 4. Phase Analysis Framework

### Phase Detection Rules

| Phase | Name                  | Entry Condition                   | Exit Condition | Key Indicators            | Typical Round Range                                      |
|-------|-----------------------|-----------------------------------|----------------|---------------------------|----------------------------------------------------------|
| 1     | Equilibrium           | Round 1                           |                | deviation(t)              | > 0.05 for ≥2 consecutive                                |
| 2     | Bias Onset            |                                   | deviation(t)   | > 0.05 for ≥2 consecutive |                                                          |
| 3     | Active Bias Episode   |                                   | deviation(t)   | > 0.10                    | Biased agents reduce volume; deviation plateaus or turns |
| 4     | Correction            | Deviation plateauing or reversing |                | deviation(t)              | < 0.05                                                   |
| 5     | Return to Equilibrium |                                   | deviation(t)   | < 0.05                    | Round T (end of simulation)                              |

### Quantitative Phase Transition Criteria

**Phase 1 → 2**: Deviation exceeds 5% for 2+ rounds. Diagnostic: at least one of RecentEventOverweighter or MediaInfluencedTrader is generating non-zero volume.

**Phase 2 → 3**: Deviation exceeds 10%. Diagnostic: both biased channels active; combined volume from RecentEventOverweighter + MediaInfluencedTrader > combined volume from SystematicAnalyst + ValueTrader.

**Phase 3 → 4**: Deviation stops increasing or reverses sign. Diagnostic: stabilization_ratio rising; per-round deviation change turns from amplifying to diminishing.

**Phase 4 → 5**: Deviation falls below 5% and stays there. Diagnostic: biased agents returning to hold state; AC1 turning near-zero or negative.

### Observable Signatures by Phase

| Phase          | RecentEventOverweighter                            | MediaInfluencedTrader             | SystematicAnalyst                      | ValueTrader                               | AC1          |
|----------------|----------------------------------------------------|-----------------------------------|----------------------------------------|-------------------------------------------|--------------|
| Equilibrium    | Inactive                                           | Inactive                          | Occasionally active                    | Inactive                                  | ≈ 0          |
| Bias Onset     | Active (moderate perceived_signal)                 | Active (small deviation triggers) | Active (countering)                    | Inactive                                  | +0.1 to +0.2 |
| Active Episode | Active (large perceived_signal from recent return) | Active (sustained amplification)  | Active (insufficient to fully correct) | Possibly active                           | +0.2 to +0.4 |
| Correction     | Reducing (recent returns normalizing)              | Reducing                          | Active (increasing)                    | Active (buying/selling at 10%+ threshold) | 0 to −0.2    |
| Equilibrium    | Inactive                                           | Inactive                          | Occasional small trades                | Inactive                                  | ≈ 0          |


## 5. Cross-Variant Comparison Framework

### Comparison Protocol

1. **Normalize**: Same initial price (100.0), same fundamental (100.0) across all variants.
2. **Statistical test**: Compare bias_persistence_score, peak_deviation, and stabilization_ratio across variants using mean ± std over 10 simulation runs per variant.
3. **Key comparison axes**:
   - **Bias magnitude**: Does LLM variant over- or under-apply availability bias? Rule variant is the calibrated baseline.
   - **Channel distinction**: Do LLM personas for RecentEventOverweighter and MediaInfluencedTrader produce distinct behaviors (different signals, different timing)?
   - **Stabilization**: Do LLM versions of SystematicAnalyst and ValueTrader maintain rational discipline or succumb to availability bias in their reasoning?
   - **Rag modification**: Does retrieving historical overreaction examples (De Bondt & Thaler, post-crash recoveries) moderate the biased agents' behavior?

### Expected Cross-Variant Behavioral Differences

| Behavioral Dimension                | Rule                          | LLM                                                                               | RuleLLM                     | Rag                                                                                                       |
|-------------------------------------|-------------------------------|-----------------------------------------------------------------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------|
| RecentEventOverweighter activation  | Mechanical at                 | perceived_signal                                                                  | > 0.05                      | LLM may show stronger narrative-driven overreaction ("that was a dramatic move!") or deliberate restraint |
| MediaInfluencedTrader amplification | Exact 3× deviation scaling    | LLM may interpret "heavy media coverage" differently each call; varying intensity | Near-3× with ±20% variation | May retrieve examples of media-driven reversal and reduce amplification                                   |
| SystematicAnalyst rationality       | Perfect — uses deviation only | May inadvertently reference recent returns in reasoning; slight contamination     | Near-perfect rational       | May over-emphasize rational behavior based on retrieved efficient-market evidence                         |
| ValueTrader activation              | Exact at                      | deviation                                                                         | > 10%                       | May activate at 8–12% range due to narrative judgment                                                     |


## 6. Expected Results and Validation

### Expected Stylized Facts (Literature-Sourced)

| Stylized Fact                              | Target Value                | Literature Source                                | DOI                              |
|--------------------------------------------|-----------------------------|--------------------------------------------------|----------------------------------|
| Peak availability bias deviation           | 5%–15%                      | Baker & Wurgler (2007) sentiment mispricings     | 10.1257/jep.21.2.129             |
| Bias persistence duration                  | ≥5 rounds sustained         | Tetlock (2007) media effects persist 2–3 weeks   | 10.1111/j.1540-6261.2007.01232.x |
| Overreaction bias magnitude                | 2.0×–4.0× rational baseline | Tversky & Kahneman (1973)                        | 10.1016/0010-0285(73)90033-9     |
| Return autocorrelation during bias episode | AC1 > +0.2                  | De Bondt & Thaler (1985)                         | 10.2307/2327804                  |
| Post-episode reversal                      | 2%–8% per 5 rounds          | De Bondt & Thaler (1985); Tetlock (2007)         | 10.2307/2327804                  |
| Stabilization ratio                        | 0.4–0.8                     | Baker & Wurgler (2007); Shleifer & Vishny (1997) | 10.2307/2329555                  |

### Sensitivity Discussion

- **Increasing recency_weight**: Stronger per-round overreaction; larger peak deviation; faster bias onset. Most sensitive parameter for RecentEventOverweighter channel.
- **Increasing media_weight or social_amplification**: More sustained overreaction (responds to deviation level, not recency); higher persistence score. Key parameter for MediaInfluencedTrader.
- **Decreasing γ (mean reversion)**: More persistent mispricings; higher bias_persistence_score. Risk: simulation may not return to equilibrium within run length.
- **Increasing SystematicAnalyst position limits**: Higher stabilization_ratio; lower peak deviation; shorter episode duration.
- **Increasing ValueTrader deviation_threshold**: ValueTrader activates less frequently; deeper mispricings possible before floor/ceiling engaged.

### Validation Failure Diagnostics

| Failure Mode                   | Symptom                                   | Likely Cause                                         | Corrective Action                                                                              |
|--------------------------------|-------------------------------------------|------------------------------------------------------|------------------------------------------------------------------------------------------------|
| No bias effect                 | Deviation always < ±3%                    | recency_weight too low or noise_std too high         | Increase recency_weight to 3.5; reduce noise_std to 0.3                                        |
| No persistence                 | All bias episodes < 3 rounds              | γ too high (corrects too fast)                       | Reduce γ to 0.01; check stabilizing agent volumes                                              |
| No reversal                    | Post-episode returns same sign as episode | Biased agents maintain activation; γ too low         | Ensure salience_threshold creates natural deactivation; increase γ to 0.03                     |
| No ValueTrader activation      | Absorption ratio = 0                      | Deviation never crosses 10%                          | Verify biased agents generating sufficient combined signal; reduce deviation_threshold to 0.08 |
| MediaInfluencedTrader dominant | Media channel >> recency channel          | amplified_signal = 3× deviation activates too easily | Raise implicit threshold from 0.03 to 0.05; reduce social_amplification                        |


## 7. Visualization Catalogue

| Plot Name                          | Type        | X-axis              | Y-axis                               | Overlays / Annotations                          | Purpose                                                           |
|------------------------------------|-------------|---------------------|--------------------------------------|-------------------------------------------------|-------------------------------------------------------------------|
| Price vs. Fundamental              | Line        | Rounds              | Price                                | Fundamental dashed; ±5%, ±10% threshold lines   | Primary bias dynamics; shows episode depth and correction         |
| Price Deviation Time Series        | Line        | Rounds              | Deviation (%)                        | Phase markers; ±5%, ±10%, ±15% thresholds       | Bias episode identification; quantitative mispricing measure      |
| Perceived Signal Distribution      | Histogram   | Signal value        | Frequency                            | Salience threshold marked                       | Shows RecentEventOverweighter activation frequency and magnitude  |
| Amplified Signal Distribution      | Histogram   | Signal value        | Frequency                            | 0.03 threshold marked                           | Shows MediaInfluencedTrader activation frequency and magnitude    |
| Agent Volume by Type               | Stacked Bar | Agent               | Total volume                         | SystematicAnalyst+ValueTrader combined baseline | Volume attribution; validates both availability channels active   |
| Per-Round Volume Time Series       | Line        | Rounds              | Volume                               | One line per agent; bias episode markers        | Shows when each channel activates; stabilization timing           |
| Rolling Return Autocorrelation     | Line        | Rounds              | AC1 (10-round rolling)               | Zero line; +0.2 and −0.1 thresholds             | Overreaction → reversal pattern; momentum vs. mean-reversion      |
| Bias Magnitude by Agent            | Bar/Scatter | Round (when active) | Bias magnitude (Q_actual/Q_rational) | 1.0 rational baseline; 2.0, 4.0 benchmarks      | Quantifies overreaction relative to rational baseline             |
| Stabilization Ratio Time Series    | Line        | Rounds              | Stabilization ratio                  | 0.4 and 0.8 target range lines                  | Tests limits-of-arbitrage prediction; rational vs. biased balance |
| Post-Episode Reversal Analysis     | Scatter     | Peak deviation      | Post-5-round return                  | Zero return line; reversal target range         | Validates De Bondt & Thaler overreaction → reversal prediction    |
| Cross-Variant Deviation Comparison | Line        | Rounds              | Deviation (%)                        | One line per variant (Rule/LLM/RuleLLM/Rag)     | Quantifies behavioral differences across implementation types     |
| Rule Adherence (RuleLLM variant)   | Bar         | Agent               | Adherence rate (%)                   | 80% target threshold                            | Validates quantitative rule anchoring in RuleLLM variant          |
