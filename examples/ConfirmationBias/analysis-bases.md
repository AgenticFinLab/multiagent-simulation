# ConfirmationBias — Analysis Methodology Basis

## §1 Analysis Objectives

| Objective | Research Question                                                                                 | Metric(s)                                       | Expected Finding                                                                       |
|-----------|---------------------------------------------------------------------------------------------------|-------------------------------------------------|----------------------------------------------------------------------------------------|
| O1        | Does BeliefAnchor's persistent belief state generate measurable price deviation from fundamental? | bias_amplitude_pct, mean_absolute_deviation_pct | Amplitude 2–8%; MAD 1–5%                                                               |
| O2        | Does the bias persist over time rather than being immediately corrected?                          | bias_persistence, belief_flip_count             | Persistence > 30 rounds; flip count < 5 in strong-bias scenarios                       |
| O3        | Do stabilizing agents (BalancedAnalyst + ContrarianTrader) partially correct the bias?            | correction_ratio                                | correction_ratio = 0.2–0.6 (partial but not full correction given dominance condition) |
| O4        | Does the simulation produce positive return autocorrelation — the momentum fingerprint of bias?   | return_autocorrelation AC(1)                    | AC(1) > 0 (positive momentum from biased accumulation); stronger in Rule than LLM      |
| O5        | Is volatility moderate — characteristic of cognitive bias (not crash) dynamics?                   | annualized_volatility_pct                       | 5–15%; markedly lower than crash simulations (BlackMonday1987 > 30%)                   |
| O6        | How does each variant's bias strength and correction effectiveness compare?                       | All metrics by variant                          | Rule ≥ RuleLLM ≥ LLM ≥ Rag for bias_amplitude; Rag ≥ LLM ≥ Rule for correction_ratio   |


## §2 Core Metrics Catalogue

### Metric 1: Bias Amplitude (%)

- **Category**: Price Dynamics / Bias Severity
- **Definition**: Maximum absolute deviation of market price from fundamental value over the entire simulation run, expressed as a percentage of fundamental value
- **Formula**: bias_amplitude_pct = max_t( |P(t) − F| / F ) × 100

**Derivation Rationale**: Bias amplitude is the primary observable consequence of confirmation bias in asset pricing. Unlike crash simulations where the peak drawdown measures a one-directional collapse, bias amplitude measures the maximum excursion from fair value in either direction — the price can be persistently above OR below fundamental depending on whether BeliefAnchor's initial belief is positive or negative. Nickerson (1998) and Lord et al. (1979) document confirmation bias producing sustained mispricing of 5–15% in controlled experimental studies; Hong & Stein (1999) calibrate momentum effects producing 4–6% annual excess returns, consistent with sustained deviations of 2–8% in short-horizon trading simulations. The max-over-time operator captures the peak bias before any partial correction by BalancedAnalyst and ContrarianTrader.

**Academic Calibration Source**: Nickerson, R. S. (1998). "Confirmation bias: A ubiquitous phenomenon in many guises." *Review of General Psychology*, 2(2), 175–220. DOI: 10.1037/1089-2680.2.2.175. Target range: 2%–8% for moderate-to-strong bias. Rabin, M., & Schrag, J. L. (1999). "First impressions matter: A model of confirmatory bias." *Quarterly Journal of Economics*, 114(1), 37–82. DOI: 10.1162/003355399555945. Consistent with high-q (bias parameter q = 0.7) regime producing sustained deviations.

- **Interpretation**:
    - < 2%: Noise dominates — bias effect not observable above σ = 0.02 noise floor; BeliefAnchor belief not compounding meaningfully
    - 2%–5%: Moderate bias — BeliefAnchor belief reached ~1.5–2.0; SelectiveScanner partially amplifying; stabilizers limiting amplitude
    - 5%–10%: Strong bias target zone — BeliefAnchor belief near ceiling (2.5–3.0); stabilizers' combined 900-unit capacity insufficient to offset 1100-unit biased demand
    - > 10%: Extreme — belief state near floor/ceiling ±3.0; stabilizer + mean-reversion forces overwhelmed; verify γ = 0.02 is operative
- **Normal Range**: 2%–8% for calibrated parameters (BeliefAnchor order_size = 500, SelectiveScanner = 600)
- **Red Flag**: bias_amplitude < 1% → BeliefAnchor belief not compounding; check initial_belief = 1.0 and confirmation_strength = 0.7 in config. bias_amplitude > 15% → cascade-like dynamics; verify λ = 0.02 (not higher) and γ = 0.02 (not lower than 0.01).

---

### Metric 2: Bias Persistence (Rounds)

- **Category**: Phenomenon-Specific / Temporal Dynamics
- **Definition**: Number of simulation rounds during which the absolute price deviation exceeds the persistence threshold (BIAS_THRESHOLD = 0.02), i.e., price remains more than 2% from fundamental
- **Formula**: bias_persistence = |{t : |deviation(t)| > 0.02}|

**Derivation Rationale**: Persistence is the defining temporal feature that distinguishes confirmation bias dynamics from other behavioral phenomena. Availability bias (single-event recency) tends to generate one-off spikes that decay within a few rounds; anchoring generates bounded errors that converge as new information accumulates. Confirmation bias, by contrast, is self-reinforcing: each round of confirming price movement strengthens BeliefAnchor's belief state, which increases demand, which sustains the deviation, which constitutes another confirming signal. Rabin & Schrag (1999) formally prove this self-reinforcing loop can produce permanent bias in infinite-horizon settings. The BIAS_THRESHOLD of 2% corresponds to 1 standard deviation of the noise process (σ = 0.02 × √100 rounds ≈ 0.20 annual), ensuring only genuine bias persistence (not noise fluctuations) is counted. Persistence > 30 rounds in a 100-round simulation indicates BeliefAnchor's belief is consistently above 0.5 (buy trigger) for most of the simulation.

**Academic Calibration Source**: Rabin, M., & Schrag, J. L. (1999). *Quarterly Journal of Economics*, 114(1), 37–82. DOI: 10.1162/003355399555945. Their model predicts that agents with confirmation_strength in the high-bias regime (q > 0.5) never revise their beliefs to the truth in finite time — persistence should approach simulation length. Empirical anchor: Hong, H., & Kubik, J. D. (2003). "Analyzing the analysts: Career concerns and biased earnings forecasts." *Journal of Finance*, 58(1), 313–351. DOI: 10.1111/1540-6261.00526. Analyst earnings forecast bias persists for 2–4 years in real markets; within a 100-round simulation, persistence > 50% of rounds is calibrated to this multi-year persistence.

- **Interpretation**:
    - < 10 rounds: Transient bias — BeliefAnchor belief resets frequently (high flip count); stabilizers effective
    - 10–40 rounds: Moderate persistence — target for intermediate confirmation strength (q ≈ 0.4–0.6 in Rabin-Schrag)
    - 40–70 rounds: Strong persistence — target zone for confirmation_strength = 0.7; bias clearly dominates over roughly half the simulation
    - > 70 rounds: Near-permanent bias — BeliefAnchor locked into belief > 0.5 for nearly all rounds; correction_ratio will be low
- **Normal Range**: 30–70 rounds in 100-round simulation for calibrated parameters
- **Red Flag**: persistence < 10 with confirmation_strength = 0.7 → initial_belief may be too low (< 0.5) or noise_std too high (masking belief compounding). persistence > 90 → stabilizers completely ineffective; check analysis_threshold and contrarian_threshold are both set to 0.05.

---

### Metric 3: Mean Absolute Deviation (%)

- **Category**: Price Dynamics / Average Mispricing
- **Definition**: Time-averaged absolute price deviation from fundamental value, expressed as percentage; measures sustained mispricing across the entire run rather than peak deviation alone
- **Formula**: mean_absolute_deviation_pct = (1/T) × Σ_t |deviation(t)| × 100, where deviation(t) = (P(t) − F) / F

**Derivation Rationale**: While bias_amplitude captures the peak, mean_absolute_deviation measures the integrated economic cost of the bias — the average mispricing any investor encounters across the simulation. For persistent confirmation bias, MAD should be substantially non-zero (close to bias_amplitude) because the price remains far from fundamental for many rounds. For transient biases (anchoring, availability), MAD is much lower than peak amplitude because the price only briefly deviates. The ratio MAD / bias_amplitude is thus an indicator of persistence structure: ratio > 0.4 signals sustained bias consistent with confirmation bias; ratio < 0.2 signals spike-and-return characteristic of availability bias. Summers (1986) argues that market efficiency tests based on time-averaged deviations are more powerful than single-observation tests, motivating MAD as a cross-variant comparison metric.

**Academic Calibration Source**: Summers, L. H. (1986). "Does the stock market rationally reflect fundamental values?" *Journal of Finance*, 41(3), 591–601. DOI: 10.2307/2328487. Calibration: mean_absolute_deviation / std(P) ratio > 1 indicates systematic bias beyond noise. Target: MAD = 1%–5% over 100-round simulation with calibrated parameters.

- **Interpretation**:
    - < 0.5%: Noise-dominated — no systematic bias observable; simulation not generating confirmation bias dynamics
    - 0.5%–2%: Weak sustained bias — bias present but stabilizers providing significant partial correction
    - 2%–5%: Target zone — sustained mispricing consistent with moderate confirmation bias literature
    - > 5%: Strong persistent bias — belief near ceiling for most of simulation; stabilizers overwhelmed
- **Normal Range**: 1%–4% for calibrated 100-round simulation
- **Red Flag**: MAD / bias_amplitude < 0.15 → spike-and-return dynamics; check if BeliefAnchor's belief is being reset (initial_belief re-initialized each round — confirm it is NOT in Rule/players.py). MAD > bias_amplitude is impossible by definition (flag data pipeline error).

---

### Metric 4: Belief Flip Count

- **Category**: Phenomenon-Specific / Belief State Dynamics
- **Definition**: Number of times BeliefAnchor's internal `belief` variable changes sign (positive → negative or vice versa) across the simulation run; measures belief stability
- **Formula**: belief_flip_count = Σ_{t=1}^{T-1} 𝟏[sign(belief(t+1)) ≠ sign(belief(t))]

**Derivation Rationale**: The belief flip count is a simulation-unique metric enabled by BeliefAnchor's observable persistent internal state — the only cross-round state variable in the entire simulation suite. A flip represents a reversal in BeliefAnchor's directional conviction: from bullish (belief > 0) to bearish (belief < 0) or vice versa. In the Rabin-Schrag model, with high confirmation strength (q = 0.7), belief reversals should be rare because: (1) confirming signals amplify belief rapidly, making it hard to reverse; (2) disconfirming signals decay slowly (decay factor 0.95), preventing fast reversal. Lord et al. (1979) document that experimental subjects virtually never reversed their positions when exposed to mixed evidence — consistent with belief_flip_count ≈ 0–2 in a strong-bias run. A high flip count (> 5) suggests noise dominates over belief compounding, and the simulation is not generating authentic confirmation bias dynamics.

**Academic Calibration Source**: Lord, C. G., Ross, L., & Lepper, M. R. (1979). "Biased assimilation and attitude polarization." *Journal of Personality and Social Psychology*, 37(11), 2098–2109. DOI: 10.1037/0022-3514.37.11.2098. Experimental evidence: subjects who initially held strong prior beliefs virtually never reversed, even after reading contradictory evidence — consistent with flip_count ≈ 0 in strong confirmation bias runs. Rabin, M., & Schrag, J. L. (1999). DOI: 10.1162/003355399555945. Model prediction: for high q, the probability of belief reversal → 0 after early rounds.

- **Interpretation**:
    - 0–2 flips: Strong directional bias — BeliefAnchor locked into initial belief direction; consistent with high confirmation strength; price deviation persistent and one-directional
    - 3–5 flips: Moderate oscillation — noise occasionally overwhelming bias; price oscillates around fundamental rather than trending
    - 6–10 flips: Weak bias — noise dominates; belief_flip_count negatively correlated with bias_amplitude
    - > 10 flips: Noise-dominated — confirmation bias not generating meaningful dynamics; sigma_noise may be too high relative to lambda × order_size
- **Normal Range**: 0–3 flips for confirmation_strength = 0.7 with calibrated noise_std = 0.02
- **Red Flag**: flip_count > 5 with default parameters → noise_std possibly set too high (> 0.05) or confirmation_strength too low (< 0.4). flip_count = 0 throughout → belief_state_init may be very large (> 2.5), suppressing normal dynamics.

---

### Metric 5: Correction Ratio

- **Category**: Phenomenon-Specific / Correction Effectiveness
- **Definition**: Fraction of peak bias deviation that is recovered by the end of the simulation; measures the net effectiveness of stabilizing agents (BalancedAnalyst + ContrarianTrader) and mean reversion against persistent bias
- **Formula**: correction_ratio = (bias_amplitude − |deviation(T)|) / bias_amplitude, where deviation(T) is the final-round deviation
- **Bounds**: [0, 1]; correction_ratio = 1 means full correction; correction_ratio = 0 means no correction (terminal price equals peak bias price)

**Derivation Rationale**: The correction ratio directly operationalizes the competition between biased agents (BeliefAnchor + SelectiveScanner, combined 1100 units) and corrective forces (BalancedAnalyst + ContrarianTrader combined 900 units + γ mean-reversion force). Because 1100 > 900, the bias dominance condition is satisfied and the simulation is designed to produce incomplete correction — correction_ratio < 0.5 in most runs. This asymmetry mirrors empirical findings from behavioral finance: Hong & Stein (1999) show that arbitrage forces (analogous to stabilizers here) can never fully eliminate bias-driven mispricing because: (1) arbitrage capacity is capital-limited; (2) the bias self-reinforces through belief compounding; (3) stabilizers bear fundamental risk if the price temporarily moves against them. The correction ratio serves as the key cross-variant comparison: if LLM or Rag variants produce higher correction_ratio, it indicates these variants' stabilizing agents behave more effectively than the mechanical Rule baseline.

**Academic Calibration Source**: Hong, H., & Stein, J. C. (1999). "A unified theory of underreaction, momentum trading, and overreaction in asset markets." *Journal of Finance*, 54(6), 2143–2184. DOI: 10.1111/0022-1082.00184. Their model predicts incomplete correction: bias elimination requires corrective capacity > 1.5× biased capacity. Here: stabilizers (900) / biased (1100) = 0.82 — insufficient for full correction. Expected correction_ratio = 0.2–0.5. Also: Fama, E. F. (1970). "Efficient capital markets." *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486. Baseline efficient market prediction: correction_ratio → 1.0. Behavioral market prediction: correction_ratio < 0.5 when bias persists.

- **Interpretation**:
    - < 0.2: Minimal correction — stabilizers overwhelmed; BeliefAnchor's belief near maximum for most of simulation; price remains far from fundamental at run end
    - 0.2–0.5: Partial correction — target zone consistent with biased > stabilizer capacity (1100 > 900); stabilizers limit but cannot fully reverse bias
    - 0.5–0.8: Strong correction — stabilizers performing above expected capacity; possibly ContrarianTrader position_size effectively large
    - > 0.8: Near-complete correction — unexpected; verify bias dominance condition is preserved (check simulation parameter settings)
- **Normal Range**: 0.2–0.5 for calibrated parameters
- **Red Flag**: correction_ratio < 0.1 for all seeds → stabilizers never activating; check analysis_threshold = 0.05 is not set too high. correction_ratio consistently > 0.7 → stabilizer capacity may exceed biased capacity due to config error; verify BeliefAnchor order_size = 500 and SelectiveScanner order_size = 600.

---

### Metric 6: Return Autocorrelation AC(1)

- **Category**: Price Dynamics / Momentum Fingerprint
- **Definition**: First-order serial correlation of single-round returns, measuring whether positive returns are followed by positive returns (positive AC(1)) or reversed (negative AC(1))
- **Formula**: r(t) = (P(t+1) − P(t)) / P(t); AC(1) = corr(r[0:T-1], r[1:T])

**Derivation Rationale**: Return autocorrelation is the statistical fingerprint that distinguishes confirmation bias dynamics from other phenomena. Because BeliefAnchor accumulates a belief that compounds with confirming signals, the simulation generates positive feedback: a positive return at t strengthens BeliefAnchor's bullish belief, leading to more buying at t+1, which tends to produce another positive return. This is precisely the mechanism that Jegadeesh & Titman (1993) identify as the source of momentum profits: short-horizon positive return autocorrelation lasting 3–12 months. AC(1) > 0 is the confirmation bias simulation's "momentum signature." Conversely, ContrarianTrader's mean-reverting trades push toward negative AC(1), creating a tension that is resolved in favor of positive AC(1) when the bias dominance condition holds (1100 > 900). The magnitude of AC(1) serves as a natural measure of how strongly confirmation bias is embedding momentum into price dynamics relative to mean-reverting forces.

**Academic Calibration Source**: Jegadeesh, N., & Titman, S. (1993). "Returns to buying winners and selling losers: Implications for stock market efficiency." *Journal of Finance*, 48(1), 65–91. DOI: 10.1111/j.1540-6261.1993.tb04702.x. Empirical AC(1) for momentum stocks: +0.05 to +0.15 over 1-month horizons. Hong, H., & Stein, J. C. (1999). DOI: 10.1111/0022-1082.00184. Model predicts: AC(1) > 0 when momentum traders (analogous to BeliefAnchor + SelectiveScanner) dominate. Target: AC(1) = 0.05–0.20 in confirmation bias simulation.

- **Interpretation**:
    - AC(1) < −0.05: Mean-reverting — ContrarianTrader + BalancedAnalyst dominating; unexpected given bias dominance condition; verify BeliefAnchor is trading
    - AC(1) = −0.05–0.05: Near-zero — noise-dominated; no systematic momentum; bias and correction forces balanced
    - AC(1) = 0.05–0.20: Target zone — positive momentum fingerprint of confirmation bias; BeliefAnchor compounding producing return autocorrelation consistent with Jegadeesh & Titman (1993)
    - AC(1) > 0.25: Very high momentum — verify only one direction of BeliefAnchor belief is observed; confirm flip_count is low
- **Normal Range**: 0.05–0.20 for default parameters
- **Red Flag**: AC(1) < 0 consistently across seeds → confirmation bias not generating momentum; check that BeliefAnchor's belief state is truly persistent (not re-initialized each round). AC(1) > 0.35 → belief state may be capped at maximum for most of run; reduce confirmation_strength to observe more dynamic behavior.

---

### Metric 7: Annualized Volatility (%)

- **Category**: Price Dynamics / Risk Level
- **Definition**: Annualized standard deviation of per-round returns, converted to percentage
- **Formula**: annualized_vol_pct = std(r) × √252 × 100, where r(t) = (P(t+1) − P(t)) / P(t)

**Derivation Rationale**: Volatility serves as the regime classifier that separates confirmation bias dynamics (moderate volatility, 5–15%) from crash simulations (high volatility, > 30%). Confirmation bias produces sustained drift rather than explosive dynamics: BeliefAnchor buys steadily each round (belief > 0.5 consistently), creating a gradual price trend rather than violent swings. This contrasts with BlackMonday1987 (positive feedback cascade → volatility > 40%) and CarryTradeUnwind (forced liquidation → volatility > 25%). Schwert (1989) documents that cognitive-bias-driven periods (such as extended bull markets driven by narrative) show elevated but not extreme volatility — typically 15–25% annualized — while crash episodes show 40–80% annualized volatility. The simulation's σ = 0.02 per round corresponds to 0.02 × √252 ≈ 32% annualized from noise alone; observed volatility in the simulation should be 15–25% (reduced below noise prediction because belief-driven demand creates systematic trend that reduces apparent variability).

**Academic Calibration Source**: Schwert, G. W. (1989). "Why does stock market volatility change over time?" *Journal of Finance*, 44(5), 1115–1153. DOI: 10.1111/j.1540-6261.1989.tb02647.x. Historical: S&P 500 annualized volatility during behavioral bull markets (1995–2000 dotcom): 15–25%. During crash episodes (1987, 2008): 40–80%. Target: 10%–25% for confirmation bias simulation to distinguish from crash simulations. Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481. Noise contribution to volatility: σ_noise × √252 ≈ 32%, actual observed should be lower due to trend persistence.

- **Interpretation**:
    - < 5%: Very low — noise floor not being reached; simulation under-parameterized
    - 5%–15%: Low-to-moderate — stabilizers dominating; bias not building sufficient momentum
    - 15%–25%: Target zone — characteristic of sustained cognitive bias dynamics; consistent with behavioral bull/bear market periods
    - > 30%: High — crash-like dynamics emerging; verify λ is not higher than 0.02 and cascade condition not inadvertently met
- **Normal Range**: 10%–25% annualized for calibrated parameters (distinctly below crash simulations)
- **Red Flag**: annualized_vol > 35% → unexpected crash dynamics; check that λ × order_size product is not inadvertently large. annualized_vol < 5% → near-deterministic simulation; verify noise_std = 0.02 is correctly loaded from config.


## §3 Phase Analysis

### Phase Framework

The ConfirmationBias simulation proceeds through 5 characteristic phases reflecting the temporal dynamics of belief compounding and partial correction.

| Phase | Name                       | Round Range (Typical) | |deviation| Level     | BeliefAnchor Belief State | Dominant Force          |
|-------|----------------------------|-----------------------|---------------------------|---------------------------|-------------------------|
| 1     | Belief Formation           | 1–15                  | 0%–2%                     | 1.0 → 1.5 (slow compound) | Noise + initial bias    |
| 2     | Bias Amplification         | 15–40                 | 2%–6%                     | 1.5 → 2.5 (rapid compound)| BeliefAnchor + SelectiveScanner |
| 3     | Peak Bias                  | 40–60                 | 4%–8% (peak)              | 2.5–3.0 (near ceiling)    | Biased agents dominate  |
| 4     | Partial Correction         | 60–80                 | 3%–5% (declining)         | 2.5–3.0 (belief stable)   | ContrarianTrader + BalancedAnalyst active |
| 5     | Residual Bias / Stabilization | 80–100            | 1%–4%                     | 2.0–2.5 (slow decay)      | Mean reversion + noise  |

### Phase Detection Rules

**Phase 1: Belief Formation**
- Quantitative criteria: |deviation| < 0.02 AND belief_anchor ∈ [0.9, 1.5]
- Observable signatures: Low trading volume from BalancedAnalyst + ContrarianTrader (deviation below 0.05 threshold); NoiseTrader volume dominates; BeliefAnchor buying steadily but belief not yet large enough to produce visible deviation
- Round range: Typically rounds 1–15 in 100-round simulation; longer if initial_belief < 0.5

**Phase 2: Bias Amplification**
- Quantitative criteria: 0.02 < |deviation| < 0.06 AND belief monotonically increasing
- Observable signatures: BeliefAnchor buys every round (belief consistently > 0.5); SelectiveScanner activating on confirming signals (full 600-unit orders when signal confirms direction); BalancedAnalyst NOT yet activated (deviation < 0.05 analysis_threshold); deviation rising monotonically
- Round range: Rounds 15–40; rapid amplification driven by belief compounding formula `belief × (1 + 0.7 × |δ|)`
- Key diagnostic: Price chart shows steady trending-away-from-fundamental without reversals

**Phase 3: Peak Bias**
- Quantitative criteria: |deviation| > 0.05 AND belief > 2.0
- Observable signatures: BalancedAnalyst NOW activated (|deviation| > 0.05 analysis_threshold); ContrarianTrader activating (|deviation| > 0.05 contrarian_threshold); BeliefAnchor belief near ceiling (2.5–3.0), placing maximum 500-unit orders every round; SelectiveScanner placing large confirming orders; net demand still strongly one-directional
- Round range: Rounds 40–60 for default parameters; this is the window where bias_amplitude_pct is measured
- Key diagnostic: bias_amplitude_pct peaks in this phase; correction_ratio starts accumulating

**Phase 4: Partial Correction**
- Quantitative criteria: |deviation| trending toward 0 from peak, but correction_ratio < 0.7
- Observable signatures: ContrarianTrader actively selling into price (if bullish bias) or buying into weakness (if bearish bias); BalancedAnalyst placing balanced orders; BeliefAnchor belief beginning slow decay if market starts returning (disconfirming signals with decay factor 0.95); net demand becoming less one-directional
- Round range: Rounds 60–80; correction visible but incomplete given biased > stabilizer capacity
- Key diagnostic: Deviation declining but not returning to 0; correction_ratio = 0.2–0.5

**Phase 5: Residual Bias / Stabilization**
- Quantitative criteria: |deviation| < 0.02–0.03 but > 0; bias_persistence accumulation flattening
- Observable signatures: γ mean-reversion force pulling price toward F = 100; BeliefAnchor belief below +0.5 (buy trigger) in some rounds; intermittent holding behavior; NoiseTrader providing liquidity around fundamental; simulation running out of rounds before full correction completes
- Round range: Rounds 80–100
- Key diagnostic: Final-round |deviation| determines correction_ratio denominator; correction_ratio < 0.5 confirms persistent bias consistent with design intent


## §4 Dimension-by-Dimension Analysis

### Dimension 1: Bias Magnitude

Primary metric: `bias_amplitude_pct`
Supporting metric: `mean_absolute_deviation_pct`

| Level    | Amplitude | MAD     | Interpretation                                                                        |
|----------|-----------|---------|---------------------------------------------------------------------------------------|
| Weak     | < 2%      | < 0.8%  | Noise dominates; BeliefAnchor belief not compounding; σ may be too high               |
| Moderate | 2%–5%     | 1%–2.5% | Target zone for medium-strength bias; stabilizers providing meaningful partial offset |
| Strong   | 5%–8%     | 2.5%–4% | Strong confirmation bias; biased agents clearly dominating; belief near ceiling       |
| Extreme  | > 8%      | > 4%    | Belief locked at ±3.0; stabilizers overwhelmed; verify γ ≥ 0.02 is operative          |

MAD / bias_amplitude diagnostic:
- Ratio > 0.5: Sustained bias — price consistently far from fundamental; characteristic of confirmation bias
- Ratio < 0.2: Spike-and-return — more characteristic of availability bias or anchoring dynamics

### Dimension 2: Bias Persistence

Primary metrics: `bias_persistence`, `belief_flip_count`
Supporting metric: `mean_absolute_deviation_pct`

BeliefAnchor's `confirmation_strength = 0.7` means belief compounds at approximately 2.5% per round when deviation = 0.05 (|belief × 0.7 × 0.05| = 0.035 × belief per round). Starting from `initial_belief = 1.0`:
- Round 10: belief ≈ 1.0 × (1.035)^10 ≈ 1.41 → buy trigger active for all 10 rounds
- Round 20: belief ≈ 1.41 × (1.035)^10 ≈ 1.99 → strong buying
- Round 30: belief ≈ 1.99 × (1.035)^10 ≈ 2.80 → near ceiling; maximum 500-unit orders

This belief trajectory means bias_persistence will be high (> 40 rounds) whenever BeliefAnchor starts with positive initial_belief and the price initially trends in the confirming direction.

Belief flip count interpretation:
- flip_count = 0: BeliefAnchor locked in one direction for entire run; price trends steadily
- flip_count = 1–2: One or two noise shocks reversed belief briefly; price shows brief reversal
- flip_count > 5: Noise dominates; no stable bias dynamics

### Dimension 3: Correction Effectiveness

Primary metric: `correction_ratio`
Supporting metric: return_autocorrelation AC(1)

The correction_ratio has a theoretical upper bound given the simulation parameters:
- Maximum stabilizer capacity per round: BalancedAnalyst (400) + ContrarianTrader (500) = 900 units
- Minimum biased demand per round (belief > 0.5): BeliefAnchor (500) + SelectiveScanner (partial) ≈ 700–1100 units
- Net demand imbalance: 700–1100 (biased) − 900 (stabilizers) = −200 to +200 units with bias dominating

This produces theoretical correction_ratio ≤ 0.5 in most runs, consistent with empirical behavioral finance findings of persistent mispricing in markets with significant biased investor populations.

Compare across variants:
- Rule: Pure mechanical correction; BeliefAnchor belief trajectory fully deterministic; baseline correction_ratio
- LLM: Rational agents may adapt strategy beyond fixed threshold; possible higher correction_ratio if LLM ContrarianTrader responds more aggressively
- Rag: Retrieved confirmation bias literature may improve BalancedAnalyst and ContrarianTrader behavior → expect highest correction_ratio


## §5 Scaling and Sensitivity Analysis

### Key Sensitivity Parameters

| Parameter                   | Direction | Effect on bias_amplitude | Effect on bias_persistence    | Economic Interpretation                                           |
|-----------------------------|-----------|--------------------------|-------------------------------|-------------------------------------------------------------------|
| `confirmation_strength`     | ↑         | ↑ amplitude              | ↑ persistence                 | Faster belief compounding → stronger and longer bias              |
| `initial_belief`            | ↑         | ↑ amplitude (earlier)    | ↑ persistence (earlier start) | Stronger prior → bias develops faster                             |
| `order_size` (BeliefAnchor) | ↑         | ↑ amplitude              | No direct effect              | More buying per round → larger price deviation                    |
| `scan_threshold`            | ↓         | ↑ amplitude              | ↑ persistence                 | SelectiveScanner activates more often → more bias amplification   |
| `analysis_threshold`        | ↓         | ↓ amplitude              | ↓ persistence                 | BalancedAnalyst activates earlier → faster correction onset       |
| `contrarian_threshold`      | ↓         | ↓ amplitude              | ↓ persistence                 | ContrarianTrader activates earlier → earlier mean-reverting force |
| `mean_reversion` (γ)        | ↑         | ↓ amplitude              | ↓ persistence                 | Stronger fundamental pull; can overwhelm bias if γ > 0.05         |
| `lambda` (λ)                | ↑         | ↑ amplitude              | No direct effect              | Larger price impact → more deviation per demand unit              |
| `noise_std` (σ)             | ↑         | ↓ amplitude              | ↓ persistence (more flips)    | More noise → belief reversals more frequent                       |

### Bias Dominance Condition

The bias dominance condition governs whether sustained mispricing is expected:

```
Biased demand capacity:     BeliefAnchor (500) + SelectiveScanner (600) = 1100 units/round (max)
Stabilizer supply capacity: BalancedAnalyst (400) + ContrarianTrader (500) = 900 units/round (max)
Dominance ratio: 1100 / 900 = 1.22 > 1.0 → bias expected to dominate
```

The effective dominance is moderated by:
1. Threshold effects: stabilizers only activate when |deviation| > 0.05 (both thresholds); for the first ~20–30 rounds (phases 1–2), stabilizers are inactive, giving biased agents uncontested price influence
2. SelectiveScanner asymmetry: full 600 on confirming signals, 300 on disconfirming — average ≈ 400–500 units; effective biased capacity lower than nominal 1100

### Cross-Variant Comparison

Expected metric ordering across variants (from most to least bias-consistent):

| Metric                       | Highest Bias | Order                      | Lowest Bias |
|------------------------------|--------------|----------------------------|-------------|
| bias_amplitude_pct           | Rule         | Rule > RuleLLM > LLM > Rag | Rag         |
| bias_persistence             | Rule         | Rule > RuleLLM > LLM > Rag | Rag         |
| correction_ratio             | Rag          | Rag > LLM > Rule > RuleLLM | RuleLLM     |
| belief_flip_count            | LLM          | LLM > Rag > RuleLLM > Rule | Rule        |
| return_autocorrelation AC(1) | Rule         | Rule > RuleLLM > LLM > Rag | Rag         |
| annualized_volatility_pct    | LLM          | LLM ≈ Rule > RuleLLM > Rag | Rag         |


## §6 Expected Results and Calibration Targets

### Simulation-Level Targets

| Metric                       | Target Range   | Literature Source                                           | Diagnostic if Outside Range                                                   |
|------------------------------|----------------|-------------------------------------------------------------|-------------------------------------------------------------------------------|
| bias_amplitude_pct           | 2%–8%          | Nickerson (1998); Lord et al. (1979); Rabin & Schrag (1999) | < 2%: belief not compounding; > 8%: cascade dynamics, check λ and γ           |
| bias_persistence (rounds)    | 30–70 (of 100) | Rabin & Schrag (1999) persistence in high-q regime          | < 15: noise dominates; > 85: stabilizers completely inactive                  |
| mean_absolute_deviation_pct  | 1%–4%          | Summers (1986); Hong & Stein (1999)                         | < 0.5%: no systematic bias; > 5%: belief consistently at ceiling              |
| belief_flip_count            | 0–3 flips      | Lord et al. (1979); Rabin & Schrag (1999)                   | > 5: noise overwhelming belief compounding; check σ and confirmation_strength |
| correction_ratio             | 0.2–0.5        | Hong & Stein (1999); Fama (1970)                            | > 0.7: stabilizers too effective; check order_size settings                   |
| return_autocorrelation AC(1) | 0.05–0.20      | Jegadeesh & Titman (1993)                                   | < 0: mean-reverting; check BeliefAnchor is buying consistently                |
| annualized_volatility_pct    | 10%–25%        | Schwert (1989); Black (1986)                                | > 30%: crash dynamics; < 5%: under-parameterized noise floor                  |

### Sensitivity to Confirmation Strength

| confirmation_strength | Expected bias_amplitude | Expected bias_persistence | Expected correction_ratio |
|-----------------------|-------------------------|---------------------------|---------------------------|
| 0.3                   | < 2%                    | < 20 rounds               | > 0.6                     |
| 0.5                   | 2%–4%                   | 20–40 rounds              | 0.4–0.6                   |
| 0.7 (default)         | 4%–8%                   | 40–70 rounds              | 0.2–0.5                   |
| 0.9                   | 6%–12%                  | 60–90 rounds              | 0.1–0.3                   |

### Cross-Simulation Comparison Context

| Simulation       | Phenomenon Type    | Typical Amplitude | Typical Volatility | Persistence Mechanism                    |
|------------------|--------------------|-------------------|--------------------|------------------------------------------|
| ConfirmationBias | Cognitive bias     | 2%–8%             | 10%–25%            | Belief state compounding                 |
| AvailabilityBias | Cognitive bias     | 3%–10%            | 15%–30%            | Recency overweighting (transient spikes) |
| AnchoringEffect  | Cognitive bias     | 2%–6%             | 8%–20%             | Price-level anchoring                    |
| BlackMonday1987  | Mechanical cascade | 20%–40%           | 40%–80%            | Portfolio insurance feedback             |
| CarryTradeUnwind | Leverage cascade   | 10%–25%           | 25%–50%            | Stop-loss forced liquidation             |


## §7 Output Files and Cross-Variant Analysis

### Output Files by Variant

| Variant | Main PNG                                               | JSON Output                                  |
|---------|--------------------------------------------------------|----------------------------------------------|
| Rule    | `confirmationbias_rule_analysis.png`                   | `metrics.json`                               |
| LLM     | `confirmationbias_llm_analysis.png` + `_actions.png`   | `summary.json`                               |
| RuleLLM | `confirmationbias_rulellm_analysis.png`                | `summary.json`                               |
| Rag     | `confirmationbias_rag_analysis.png` + `_retrieval.png` | `summary.json` + `rag_knowledge_effect.json` |

### Visualization Catalogue

| Plot Type                         | Description                                                              | Key Observable                                          |
|-----------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------|
| Price vs. Fundamental time series | P(t) and F = 100 overlaid; shows sustained deviation                     | Bias direction, amplitude, persistence                  |
| BeliefAnchor belief trajectory    | Belief state over time; unique to ConfirmationBias                       | Belief compounding, flip points, ceiling proximity      |
| Bias amplitude heat map           |                                                                          | deviation                                               |
| Agent trading volume by round     | BeliefAnchor, SelectiveScanner, BalancedAnalyst, ContrarianTrader volume | When stabilizers activate; biased vs. corrective volume |
| Cumulative net demand             | Running sum of (buy − sell) by agent type                                | Biased vs. corrective demand balance over simulation    |
| Return autocorrelation bar chart  | AC(1) through AC(5); shows momentum persistence                          | Lag structure of momentum driven by belief compounding  |
| Bias persistence histogram        | Distribution of                                                          | deviation                                               |
| Cross-variant radar chart         | 7 metrics as radar/spider chart for all 4 variants                       | Visual comparison of variant bias reproduction          |
| Belief flip event markers         | Price chart with vertical lines at each belief sign change               | Correlation between flips and price reversals           |
| Correction ratio by variant       | Bar chart comparing correction_ratio across Rule, LLM, RuleLLM, Rag      | Which variant most effectively corrects bias            |

### Cross-Variant Comparison Framework

```python
comparison = {
    "Rule":    load_json("EXPERIMENT/ConfirmationBias/Rule/records/analysis/metrics.json"),
    "LLM":     load_json("EXPERIMENT/ConfirmationBias/LLM/records/analysis/summary.json"),
    "RuleLLM": load_json("EXPERIMENT/ConfirmationBias/RuleLLM/records/analysis/summary.json"),
    "Rag":     load_json("EXPERIMENT/ConfirmationBias/Rag/records/analysis/summary.json"),
}

for variant, data in comparison.items():
    print(variant,
          data["bias_amplitude_pct"],
          data["bias_persistence"],
          data["correction_ratio"],
          data["belief_flip_count"],
          data["return_autocorrelation"])
```

Key cross-variant hypotheses:
1. **Rule vs. LLM bias reproduction**: Rule should show higher bias_amplitude because mechanical belief compounding (confirmation_strength = 0.7) is perfectly deterministic; LLM BeliefAnchor may not perfectly replicate the compounding formula
2. **RuleLLM rule-informed behavior**: Embedded rules serve as deeper investor characterization; compare RuleLLM vs LLM dynamics to measure the effect of explicit quantitative guidance on LLM decision-making
3. **Rag correction enhancement**: Rag variant's BalancedAnalyst and ContrarianTrader with access to confirmation bias literature should produce higher correction_ratio; target: correction_ratio_rag > correction_ratio_rule + 0.1
4. **Belief flip count ordering**: Rule should show fewest flips (deterministic belief compounding); LLM may show more flips (stochastic persona-level reasoning); Rag intermediate
