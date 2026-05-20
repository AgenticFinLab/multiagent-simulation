# AnchoringEffect — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | **Anchoring Effect** — a cognitive bias causing traders to insufficiently adjust price estimates from an initial reference point (the "anchor"), producing persistent deviations from fundamental value and slowing price discovery                                                                                                                                                                                                        |
| Category           | Behavioural bias / cognitive heuristic / slow price discovery / market inefficiency                                                                                                                                                                                                                                                                                                                                                        |
| Core Mechanism     | Agents set an initial anchor (first observed price, historical average, or round number) and adjust toward true fundamental value by only a fraction of the required adjustment. Even when fundamental value is publicly known, anchoring prevents agents from trading at the correct price, creating persistent mispricings. The fundamental value is observable to all — the anchoring is a cognitive failure, not an informational one. |
| Real-World Origin  | Documented in equity analyst earnings forecasts (Campbell & Sharpe, 2009: ~50% under-revision), real estate appraisal (Northcraft & Neale, 1987: experts anchor to listed prices), IPO aftermarket pricing (Loughran & Ritter, 2002: prices cluster near IPO anchor), and post-earnings announcement drift                                                                                                                                 |
| Research Relevance | Anchoring is one of the most empirically robust cognitive biases in financial markets. It explains slow price discovery, momentum effects, analyst forecast conservatism, and the well-documented post-earnings drift anomaly — all of which have direct implications for market efficiency, arbitrage profitability, and behavioural finance theory.                                                                                      |


## §2 Theoretical Foundation

### Theory: Anchoring and Insufficient Adjustment

- **Citation**: Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124
- **Core Insight**: When estimating an unknown quantity, people start from an initial value (the "anchor") and adjust from it toward a more appropriate estimate. Critically, this adjustment is systematically insufficient — people stop adjusting too soon and remain biased toward the anchor. Even when the anchor is known to be arbitrary or irrelevant, its influence on the final estimate persists. This is one of the most replicated findings in experimental psychology.
- **Mathematical Formulation**:
  ```
  perceived_target = anchor + (true_value − anchor) × α
  where α ∈ (0, 1) is the adjustment factor; α = 1 = full rational update; α ≈ 0.3 from experimental data
  Anchoring bias = (true_value − perceived_target) / true_value = (1 − α) × (true_value − anchor) / true_value
  ```
- **Empirical Evidence**: Tversky & Kahneman (1974) classic wheel-of-fortune experiment: subjects who saw a high random number estimated African nations' UN membership percentage at a higher value than subjects who saw a low number. The effect holds even when subjects know the anchor is random. In financial contexts, Northcraft & Neale (1987) find that expert appraisers' valuations correlate r ≈ 0.7 with the listing price anchor.
- **Relevance to This Simulation**: `AnchoredTrader` anchors to the first price observed (initial_price = 105.0). With α = 0.3, their perceived target is `105.0 + (100.0 − 105.0) × 0.3 = 103.5` — they believe fair value is 3.5% above the true fundamental, even though they can see fundamental = 100.
- **Calibration Implication**: `adjustment_factor = 0.3` is the experimentally measured central estimate from Tversky & Kahneman (1974); Campbell & Sharpe (2009) estimate θ ≈ 0.3–0.5 for financial forecast revisions.

---

### Theory: Expert Anchoring to Past Prices

- **Citation**: Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective on property pricing decisions. *Organizational Behavior and Human Decision Processes*, 39(1), 84–97. https://doi.org/10.1016/0749-5978(87)90046-X
- **Core Insight**: Even domain experts (professional real estate appraisers) anchor strongly to listed prices when estimating fair property value — their estimates shift significantly toward the listed price anchor despite having all necessary professional judgment tools. Expert knowledge does not eliminate anchoring; it merely reduces but does not eliminate the magnitude of the effect.
- **Mathematical Formulation**:
  ```
  perceived_deviation = (price − hist_avg) / hist_avg × (1 − anchor_weight)
  where anchor_weight ∈ [0, 1]; higher = stronger anchoring to history; lower = more fundamental-driven
  Effective underreaction = anchor_weight × raw_deviation
  ```
- **Empirical Evidence**: Northcraft & Neale (1987) find expert appraisers anchored ~12% toward the listed price (vs. ~21% for novices). This establishes that expert anchoring is a real but weaker effect. In financial markets, Campbell & Sharpe (2009) find professional analysts anchor ~50% toward prior-period forecasts — consistent with `anchor_weight = 0.5`.
- **Relevance to This Simulation**: `HistoricalAnchor` represents the expert who anchors to a 60-round rolling price average, modelling the "long-run average" as a price anchor. The `(1 − anchor_weight)` dampening factor directly implements the Northcraft & Neale finding that experts underreact to current price deviations from historical norms.
- **Calibration Implication**: `anchor_weight = 0.5` (50% anchoring to history) and `lookback = 60` (60-round rolling window) are calibrated to Campbell & Sharpe's (2009) documented professional analyst anchoring parameters.

---

### Theory: Anchoring in Consensus Financial Forecasts

- **Citation**: Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127
- **Core Insight**: Consensus economic forecasts systematically underreact to new information because forecasters anchor to prior-period values. Revisions are only 30–70% of what a fully rational Bayesian update would imply. This creates predictable, persistent forecast errors that systematically bias market prices toward historical values and away from true fundamentals.
- **Mathematical Formulation**: `forecast_revision(t) = θ × (new_information − prior_forecast)` where θ ≈ 0.3–0.7 due to anchoring. Campbell & Sharpe estimate θ ≈ 0.5 for consensus monthly economic indicators.
- **Empirical Evidence**: Using Bloomberg consensus data (1992–2006), Campbell & Sharpe (2009) find: (1) forecast errors autocorrelate at r ≈ 0.4 (predictable, not random); (2) average under-revision is ~50% of optimal Bayesian update; (3) trading strategies based on forecast revision predictability earn Sharpe ratios of ~0.6. This confirms that anchoring creates exploitable, persistent market mispricings.
- **Relevance to This Simulation**: Directly calibrates `adjustment_factor = 0.3` (anchoring reduces update to 30% of rational level); provides target for Mean Absolute Deviation [3%, 10%] and persistence half-life [20, 60 rounds]; justifies the slow mean-reversion parameter (γ = 0.01) as the market-level consequence of anchoring agents.

---

### Theory: Rational Expectations Benchmark

- **Citation**: Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1905537
- **Core Insight**: Under rational expectations, agents optimally use all available information. Prices fully reflect all available information; no systematic deviations from fundamental value are exploitable. The contrast between Muth-rational agents (who update fully to any new information) and anchoring agents (who update only partially) is the central theoretical tension driving the AnchoringEffect simulation.
- **Mathematical Formulation**: Rational update: `E[P(t+1) | info(t)] = F(t)` (full updating). Anchored update: `E[P(t+1) | info(t)] = anchor + α × (F(t) − anchor)` (partial updating, α < 1).
- **Empirical Evidence**: Fama (1970) documents that prices approximate rational expectations in liquid markets on short horizons; however, Campbell & Sharpe (2009), Lo & MacKinlay (1988), and the broader behavioural finance literature establish that medium-horizon deviations from rational expectations are systematic and persistent.
- **Relevance to This Simulation**: `RationalUpdater` embodies Muth's rational agent — it uses the true `deviation = (price − fundamental) / fundamental` with no anchoring bias, acting as the benchmark corrective force.

---

### Theory: Short-Horizon Momentum and Trend Following

- **Citation**: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- **Core Insight**: Stocks with strong recent price performance (past 3–12 months) tend to continue outperforming in the near term. Momentum traders who follow this pattern amplify existing price trends, interacting with anchoring bias to either extend mispricings (when trend aligns with anchor) or accelerate correction (when trend reverses toward fundamental).
- **Mathematical Formulation**: `momentum_signal = (price − prev_price) / prev_price`; trade when `|momentum_signal| > entry_threshold`; position size proportional to signal magnitude.
- **Empirical Evidence**: Jegadeesh & Titman (1993) document 12.01% annualised momentum return in US equities (1965–1989). The momentum effect interacts with anchoring: anchored prices that are drifting slowly toward fundamental provide a weak but predictable trend that momentum traders can amplify temporarily.
- **Relevance to This Simulation**: `MomentumTrader` amplifies existing trends, including the slow anchoring-driven drift toward or away from fundamental. During the initial overvalued phase, MomentumTrader may briefly extend the mispricing; during correction, it may accelerate it.


## §3 Market Design Principles

### 3.1 Price Formation Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

**Variable Definitions**:

| Symbol | Name              | Definition                                                                                              | Role in Anchoring                                                  |
|--------|-------------------|---------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| P(t)   | Current price     | Market price at round t; initialised at 105.0 (above fundamental)                                       | The anchor reference for AnchoredTrader; drift variable            |
| D(t)   | Net demand        | Σ(buy) − Σ(sell) across all investors                                                                   | Typically small; anchoring agents generate modest demand signals   |
| F      | Fundamental value | True intrinsic value = 100.0 (constant baseline); observable to all agents                              | The target that anchoring agents fail to reach                     |
| λ      | Price impact      | 0.01 (LOW — anchoring agents generate small demand; low λ prevents excess volatility)                   | Ensures anchoring-driven demand moves prices modestly              |
| γ      | Mean reversion    | 0.01 (LOW — deliberately weak to allow mispricings to persist; high γ would eliminate anchoring effect) | Provides very slow background gravitational pull toward F          |
| ε(t)   | Noise             | ~ N(0, noise_std²), noise_std = 0.5                                                                     | Adds realistic price variability; prevents "too clean" mispricings |

**Economic Design Rationale**:
- Low λ + low γ design allows anchoring-induced deviations to persist for many rounds without being washed out by price impact or mean reversion.
- The noise term (σ = 0.5) is relatively large compared to λ × D (which is typically λ × 20 ≈ 0.2 per round), meaning price path is noisy but with a persistent upward bias from anchoring agents who buy when price dips below their biased target.
- The fundamental value is constant (not growing), ensuring all price deviations are purely attributable to anchoring bias, not to fundamental growth.

**Sensitivity**:
- γ = 0.01 is deliberately low to allow slow correction; increasing to γ = 0.05 would nearly eliminate the anchoring effect by pulling prices rapidly to F regardless of agent behaviour
- λ = 0.01 means 20 shares of net demand move price by only $0.20 — much smaller than AssetBubble (λ = 0.15)

### 3.2 Additional Market Mechanisms

**Short-Selling**: Allowed but limited to existing long position; no explicit short-selling costs (contrast with AssetBubble). Rationale: anchoring creates persistent overvaluation without requiring short-selling constraints — the bias alone is sufficient.

**Price Floor**: `new_price = max(0.01, calculated_price)` — prevents numerical instability.

**Cash Constraint**: Investors cannot spend more than their available `cash` state on purchases; sell quantity limited to current `position` (no naked shorts).

**Fundamental Visibility**: All agents receive the true fundamental value F each round. The anchoring bias is modelled as a cognitive failure to act on known information (α < 1 adjustment), not an informational barrier.

### 3.3 Information Broadcast Design

Each round, the Market broadcasts to all investors:

| Field         | Type  | Rationale                                                                                 |
|---------------|-------|-------------------------------------------------------------------------------------------|
| `price`       | float | Current market price; primary input for all agents                                        |
| `prev_price`  | float | Price from previous round; required for MomentumTrader signal calculation                 |
| `fundamental` | float | True fundamental value F; given to all agents — anchoring is cognitive, not informational |
| `deviation`   | float | `(price − fundamental) / fundamental`; precomputed for RationalUpdater                    |
| `round`       | int   | Current round number; used for phase tracking and initialisation                          |

**Design note**: Making `fundamental` visible to all agents (including AnchoredTrader) is the critical design choice that makes this a "cognitive bias" simulation rather than an "information asymmetry" simulation. AnchoredTrader sees that fundamental = 100 but still cannot adjust fully to it — this is the empirically documented nature of the anchoring bias.


## §4 Investor Taxonomy

### §4.1 AnchoredTrader

#### 4.1.1  Summary

AnchoredTrader represents the archetypal retail investor or buy-side analyst who anchors strongly to the first price they observed and adjusts toward fundamental value by only a fraction of the necessary amount. This agent directly models the Tversky-Kahneman anchoring-and-adjustment heuristic: it knows the fundamental value but cannot bring itself to use it fully, believing its biased "perceived target" to be the true fair value. AnchoredTrader is the primary driver of persistent mispricing in the simulation — its refusal to trade at the true fundamental price is what keeps prices elevated above F for extended periods.

#### 4.1.2  Theoretical and Empirical Foundation

**Anchoring and Insufficient Adjustment**:
- Theory / Study: Anchoring Heuristic in Numerical Estimation
- Citation: Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124
- Core Insight: Estimates insufficiently adjust from initial anchor values even when the anchor is arbitrary. The resulting bias toward the anchor is systematic and persistent, not reducible with expertise or incentives.
- Mathematical Formulation: `perceived_target = anchor + (F − anchor) × α`, where α = 0.3 from experimental calibration.
- Empirical Evidence: Tversky & Kahneman (1974) median estimates in the "spin the wheel" experiment shifted 10–15% toward the anchor value; Chapman & Johnson (1999, *Organizational Behavior and Human Decision Processes*) confirm α ≈ 0.25–0.40 across diverse estimation tasks.
- Relevance to This Investor: With anchor = 105.0 and F = 100.0, `perceived_target = 105.0 + (100.0 − 105.0) × 0.3 = 103.5`. AnchoredTrader treats 103.5 as "fair value" rather than the true 100.0, causing it to buy too aggressively at prices near 103–104 and sell too cautiously.

**Anchoring in Financial Forecast Revisions**:
- Theory / Study: Consensus Forecast Anchoring
- Citation: Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127
- Core Insight: Professional forecasters revise their estimates by only 30–70% of what the new information implies. The under-revision is directly proportional to the distance from the prior anchor, and it is persistent across many revision cycles.
- Mathematical Formulation: `revision = θ × (new_info − prior_forecast)`, where θ ≈ 0.3–0.5 empirically.
- Empirical Evidence: Campbell & Sharpe (2009) document mean forecast error autocorrelation r ≈ 0.4 in Bloomberg consensus data (1992–2006), confirming that under-revision is predictable and persistent — not random.
- Relevance to This Investor: `adjustment_factor = 0.3` calibrated directly from Campbell & Sharpe's θ estimates; the persistent mispricing in the simulation replicates the predictable forecast errors they document.

#### 4.1.3  Design Purpose and Activation Scenarios

Purpose: AnchoredTrader generates the persistent price stickiness that is the core phenomenon. It buys when price dips below its biased perceived target (103.5), providing upward price support that prevents the market from efficiently correcting to fundamental (100.0).

Activation Scenarios:
- Price below perceived target by > 3% (price < 100.4): Buys; interprets as undervaluation relative to biased reference; provides upward price support.
- Price above perceived target by > 3% (price > 106.6): Sells; interprets as overvaluation; provides downward correction relative to biased reference.
- Price within ±3% of perceived target: Holds; consistent with the "close enough" behaviour documented when deviations are near threshold.

Market Contribution: **Destabilising** — sustains mispricings by refusing to correct to the true fundamental. When F = 100 and anchor = 105, AnchoredTrader's buying support keeps prices elevated above fundamental, preventing efficient price discovery.

Interaction with other agents: Directly opposes RationalUpdater (who tries to correct deviation); is reinforced by MomentumTrader (who amplifies the upward drift); partially overlaps with HistoricalAnchor (both resist correction, but from different anchors).

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**

| Signal         | Type             | Rationale                                                                                                          |
|----------------|------------------|--------------------------------------------------------------------------------------------------------------------|
| `price`        | Continuous       | Current market price; compared to perceived_target                                                                 |
| `fundamental`  | Continuous       | True F; used in perceived_target calculation with α < 1; agent knows F but does not act on it directly             |
| Anchor (state) | Persistent state | Set once on first round to initial_price = 105.0; never updated; embodies the "first observation" anchoring effect |

Does NOT use: `prev_price`, `momentum`, `net_demand`. AnchoredTrader makes decisions based on its biased valuation estimate, not market dynamics signals.

**4.1.4.2  Core Behavioral Mechanism**

1. On first round: records `anchor = initial_price = 105.0` (the first price observed).
2. Each round: computes `perceived_target = anchor + (fundamental − anchor) × adjustment_factor` = 105.0 + (100.0 − 105.0) × 0.3 = 103.5.
3. Computes `perceived_dev = (price − perceived_target) / perceived_target`.
4. If `perceived_dev < −0.03` (price more than 3% below perceived target): buys — it looks cheap from the biased perspective.
5. If `perceived_dev > +0.03` (price more than 3% above perceived target): sells — it looks expensive.
6. Sizes trade proportionally to perceived deviation magnitude, bounded at base_position_size.
7. Note: AnchoredTrader will never aggressively correct price to F = 100 because its perceived target is already at 103.5, not 100.0.

**4.1.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  perceived_target = anchor + (F − anchor) × adjustment_factor   [computed once; anchor = 105.0 fixed]
  perceived_dev(t) = (P(t) − perceived_target) / perceived_target
  Buy:  perceived_dev(t) < −0.03
  Sell: perceived_dev(t) > +0.03
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(perceived_dev(t)) × 1000)
  Constrained by cash (buy) or position (sell)
  ```
- State variables: `anchor` — set once on first round to initial_price; never updated
- Parameter definitions:

| Symbol                    | Meaning                                               | Config Path                  | Source                                                      |
|---------------------------|-------------------------------------------------------|------------------------------|-------------------------------------------------------------|
| adjustment_factor = 0.3   | Fraction of gap to anchor that agent adjusts toward F | players.yml → AnchoredTrader | Tversky & Kahneman (1974): α ≈ 0.3 from experimental data   |
| base_position_size = 20.0 | Maximum trade size                                    | players.yml → AnchoredTrader | Standardised across agents                                  |
| threshold = 0.03          | Minimum perceived deviation before trading            | players.yml → AnchoredTrader | Consistent with 3% "noise band" in Campbell & Sharpe (2009) |

**4.1.4.4  Behavioral Properties**

- Time horizon: Medium-term — adjusts slowly; anchor is permanent (set once and never updated)
- Risk tolerance: Medium — trades only when perceived deviation exceeds 3%; positions bounded at 20 shares
- Information asymmetry: None — has access to true F but cognitively discounts it through α < 1 adjustment
- Psychological profile: Anchoring bias (Tversky & Kahneman, 1974); conservatism bias (Barberis, Shleifer, & Vishny, 1998 — investors underreact to new information); the "reference point" psychology of Kahneman & Tversky (1979) Prospect Theory

#### 4.1.5  Decision Process Walkthrough

```
Given:  price = 101.5,  fundamental = 100.0,  anchor = 105.0 (set on round 1)
        adjustment_factor = 0.3,  base_position_size = 20.0

Step 1: Compute perceived_target
        perceived_target = 105.0 + (100.0 − 105.0) × 0.3 = 105.0 − 1.5 = 103.5

Step 2: Compute perceived deviation
        perceived_dev = (101.5 − 103.5) / 103.5 = −0.0193

Step 3: Compare to threshold
        |−0.0193| < 0.03 → below threshold; HOLD

Result: Despite price being 1.5% above true fundamental, AnchoredTrader holds
        because relative to its biased perceived target (103.5), the price looks
        only 1.9% undervalued — below its 3% action threshold.
        This illustrates how anchoring sustains mispricings.
```

#### 4.1.6  Worked Numerical Example

```
Market state:  price = 98.0,  fundamental = 100.0,  anchor = 105.0 (permanent)

Calculation:
  perceived_target = 105.0 + (100.0 − 105.0) × 0.3 = 103.5
  perceived_dev    = (98.0 − 103.5) / 103.5 = −0.0531   (price 5.3% below biased target)
  −0.0531 < −0.03 → buy condition satisfied
  Q* = min(20.0, 0.0531 × 1000) = min(20.0, 53.1) = 20 shares (capped at base_position_size)

Decision: action = buy, quantity = 20, bid_price = 98.0

Rationale: Price at 98 is actually 2% BELOW true fundamental (100), so a rational agent would hold or sell.
But AnchoredTrader perceives it as 5.3% below its biased target (103.5) and buys aggressively.
This buying creates upward price pressure at levels that rational agents would not support,
directly producing and maintaining the anchoring-driven mispricing.
```

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                        | Notes                                                                                       |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| 1 | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124           | Core theoretical foundation; calibrates α = 0.3                                             |
| 2 | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts. *JFQA*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127                               | Financial market application; calibrates MAD target [3%, 10%] and half-life [20, 60 rounds] |
| 3 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–292. https://doi.org/10.2307/1914185                        | Grounds reference-point psychology underlying anchor as subjective "fair value"             |
| 4 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Connects anchoring to conservatism bias and underreaction in financial markets              |

---

### §4.2 HistoricalAnchor

#### 4.2.1  Summary

HistoricalAnchor represents the sophisticated analyst or institutional investor who anchors to a long-run price average rather than a fixed first-observation point. This agent models the "reversion to historical mean" heuristic: it uses 60 rounds of price history as its reference, dampening its perceived deviation from that average by `(1 − anchor_weight)`. When a new price regime begins — for instance, when fundamental value shifts — HistoricalAnchor's 60-round historical average takes many rounds to update, creating a regime-transition anchoring effect that resists the new equilibrium for an extended period.

#### 4.2.2  Theoretical and Empirical Foundation

**Expert Anchoring to Historical Prices**:
- Theory / Study: Anchoring Effects in Expert Valuation
- Citation: Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective. *Organizational Behavior and Human Decision Processes*, 39(1), 84–97. https://doi.org/10.1016/0749-5978(87)90046-X
- Core Insight: Expert appraisers anchor to historical comparable prices ("comps") when estimating current value. Their adjustments from this historical anchor toward current market conditions are systematically insufficient. Expert anchoring (12% toward anchor) is real but weaker than novice anchoring (21%).
- Mathematical Formulation: `perceived_dev = (price − hist_avg) / hist_avg × (1 − anchor_weight)`. With anchor_weight = 0.5, only 50% of the raw deviation from historical average is perceived — the rest is dismissed as noise.
- Empirical Evidence: In financial markets, mean-reversion traders (analysts who anchor to historical P/E averages) systematically under-react to regime changes in fundamental value, as documented by Lakonishok, Shleifer & Vishny (1994) who find that "value traps" form when analysts anchor to historical high-P/E and ignore structural deterioration.
- Relevance to This Investor: `anchor_weight = 0.5` calibrated to Northcraft & Neale's professional expert anchoring magnitude (~12% toward anchor, vs. 50% for `anchor_weight`); `lookback = 60` represents ~60 trading days (one quarter), consistent with the "current quarter vs. prior quarter" anchoring documented in Campbell & Sharpe (2009).

**Mean Reversion Heuristic and Its Failure**:
- Theory / Study: Mean Reversion as Anchoring to Historical Average
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Investors overreact to recent events and anchor to the belief that prices will revert to historical averages. "Winner" stocks (with recent gains) are sold because they are expected to mean-revert, while "loser" stocks are bought in expectation of recovery. This creates excess return predictability that contradicts the efficient market hypothesis.
- Mathematical Formulation: `hist_avg = (1/lookback) × Σ_{t-lookback}^{t} P(t)` — rolling arithmetic average as the mean-reversion anchor. `perceived_dev = (price − hist_avg) / hist_avg × (1 − anchor_weight)`.
- Empirical Evidence: De Bondt & Thaler (1985) find that portfolios of extreme losers outperform extreme winners by 25% over 3 years, consistent with historical-mean anchoring causing systematic overreaction that is later corrected.
- Relevance to This Investor: HistoricalAnchor's 60-round rolling average embodies the De Bondt-Thaler mean-reversion belief; in a regime where prices are persistently above F, the rolling average itself becomes anchored above F, creating a self-reinforcing anchoring cycle.

#### 4.2.3  Design Purpose and Activation Scenarios

Purpose: HistoricalAnchor introduces regime-dependent anchoring — its resistance to correction depends on how long prices have been elevated. In the early rounds (before history fills with above-fundamental prices), it anchors to its initial price history; after many rounds of above-F prices, its average drifts up, reducing its corrective force and sustaining mispricings.

Activation Scenarios:
- Price below historical average by > 3%: Buys; interprets recent decline as a deviation from the "correct" long-run level.
- Price above historical average by > 3%: Sells; interprets recent rise as mean-reversion opportunity.
- Within ±3% of historical average: Holds.

Market Contribution: **Destabilising** — creates regime-dependent price stickiness. When the market has been elevated for many rounds, HistoricalAnchor's rolling average rises with it, reducing its selling pressure and allowing the mispricing to persist.

Interaction with other agents: Complements AnchoredTrader (both resist correction but from different anchor types); opposes RationalUpdater; MomentumTrader may temporarily align with HistoricalAnchor when historical average and momentum point in the same direction.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**

| Signal                           | Type       | Rationale                                                                                                           |
|----------------------------------|------------|---------------------------------------------------------------------------------------------------------------------|
| `price`                          | Continuous | Current price; compared to historical average                                                                       |
| `price_history` (last 60 rounds) | Series     | Required for rolling average calculation; the longer the history, the more it encapsulates the sustained mispricing |

Does NOT use: `fundamental`, `deviation`. HistoricalAnchor ignores the true fundamental entirely — its reference is historical price, not intrinsic value. This is the defining feature of its anchoring type.

**4.2.4.2  Core Behavioral Mechanism**

1. Maintains a rolling list of past prices (up to `lookback = 60` rounds).
2. Each round: computes `hist_avg = mean(price_history[-60:])`.
3. Computes perceived deviation: `perceived_dev = (price − hist_avg) / hist_avg × (1 − anchor_weight)`. The `(1 − 0.5) = 0.5` factor means only half of the raw price deviation from historical average is perceived.
4. If `perceived_dev < −0.03`: buys (price seems cheap vs. history).
5. If `perceived_dev > +0.03`: sells (price seems expensive vs. history).
6. Hold if within threshold.

**4.2.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  hist_avg(t)     = mean(price_history[-lookback:])   lookback = 60
  raw_dev(t)      = (P(t) − hist_avg(t)) / hist_avg(t)
  perceived_dev(t) = raw_dev(t) × (1 − anchor_weight)  anchor_weight = 0.5
  Buy:  perceived_dev(t) < −0.03
  Sell: perceived_dev(t) > +0.03
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(perceived_dev(t)) × 1000)
  Bounded by cash (buy) or position (sell)
  ```
- State variables: `price_history` — rolling list of last 60 prices; updated each round
- Parameter definitions:

| Symbol              | Meaning                                                 | Config Path                    | Source                                                                                  |
|---------------------|---------------------------------------------------------|--------------------------------|-----------------------------------------------------------------------------------------|
| anchor_weight = 0.5 | Dampening factor; how strongly agent anchors to history | players.yml → HistoricalAnchor | Campbell & Sharpe (2009): ~50% under-revision from historical baseline                  |
| lookback = 60       | Rolling average window                                  | players.yml → HistoricalAnchor | One quarter (60 trading days); consistent with quarterly anchoring in Campbell & Sharpe |

**4.2.4.4  Behavioral Properties**

- Time horizon: Long-term — 60-round lookback means history dominates current-price signal; regime changes take many rounds to register
- Risk tolerance: Medium — trades at 3% perceived threshold; bounded position sizes
- Information asymmetry: None about fundamentals; has unique "memory" of price history that other agents lack
- Psychological profile: Representativeness heuristic (Tversky & Kahneman, 1974) — uses historical average as representative of "normal" price; De Bondt & Thaler (1985) contrarian psychology — buys underperformers, sells outperformers relative to historical mean

#### 4.2.5  Decision Process Walkthrough

```
Given:  price = 102.0,  hist_avg (last 60 rounds) = 104.5,  anchor_weight = 0.5

Step 1: Compute raw deviation
        raw_dev = (102.0 − 104.5) / 104.5 = −0.0239

Step 2: Apply anchor dampening
        perceived_dev = −0.0239 × (1 − 0.5) = −0.0120

Step 3: Compare to threshold
        |−0.0120| < 0.03 → below threshold; HOLD

Result: Despite price being 2.4% below historical average, HistoricalAnchor perceives
        only 1.2% deviation after dampening — insufficient to trigger a trade.
        This is how anchor_weight dampens corrective action.
```

#### 4.2.6  Worked Numerical Example

```
Market state:  price = 97.0,  hist_avg (60-round rolling) = 104.5

Calculation:
  raw_dev       = (97.0 − 104.5) / 104.5 = −0.0718
  perceived_dev = −0.0718 × 0.5 = −0.0359  (<−0.03 → buy condition)
  Q*            = min(20.0, 0.0359 × 1000) = min(20.0, 35.9) = 20 shares (capped)

Decision: action = buy, quantity = 20, bid_price = 97.0

Rationale: Price has fallen 7.2% below historical average. HistoricalAnchor perceives this as
a 3.6% buying opportunity (50% of raw signal). Despite price being 3% BELOW true fundamental (100),
HistoricalAnchor buys because its reference is historical average (104.5), not fundamental (100).
This illustrates how historical anchoring can support prices even below fundamental value.
```

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                                                         | Notes                                                                          |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1 | Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate. *OBHDP*, 39(1), 84–97. https://doi.org/10.1016/0749-5978(87)90046-X                                                | Core foundation; calibrates anchor_weight = 0.5 and expert anchoring magnitude |
| 2 | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts. *JFQA*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127                                                | Calibrates lookback = 60 (quarterly horizon) and persistence                   |
| 3 | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                            | Grounds historical-mean anchoring in documented over/under-reaction cycle      |
| 4 | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541–1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | Documents anchoring to historical valuation ratios in institutional investors  |

---

### §4.3 RationalUpdater

#### 4.3.1  Summary

RationalUpdater represents the Muth-rational agent who acts optimally on all available information — the theoretical benchmark that every other agent in this simulation deviates from. It uses the true fundamental deviation directly, with no anchoring adjustment, and trades immediately when price differs from fundamental by more than 2%. RationalUpdater is the corrective force that prevents the anchoring-induced mispricing from growing without limit and provides the "rational expectations" baseline against which the bias magnitude of other agents can be measured.

#### 4.3.2  Theoretical and Empirical Foundation

**Rational Expectations and Fundamental-Based Trading**:
- Theory / Study: Rational Expectations Hypothesis
- Citation: Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1905537
- Core Insight: Rational agents form expectations using all available information optimally. Prices that deviate from fundamental value represent profit opportunities that rational agents immediately exploit, pushing prices toward fundamental. The speed of price discovery depends on the proportion of rational to anchoring agents.
- Mathematical Formulation: `trade if |deviation| > threshold; Q* ∝ |deviation| × base_size`; no anchoring, no history — pure fundamental-gap exploitation.
- Empirical Evidence: Fama (1970) documents that professional traders provide near-immediate correction of public information-based mispricings. The failure of this correction mechanism to fully overcome anchoring is consistent with the limits-to-arbitrage literature (fewer rational agents than anchoring agents in this simulation).
- Relevance to This Investor: RationalUpdater acts as the simulation's "market efficiency engine" — it provides the corrective force that prevents anchoring mispricings from becoming arbitrarily large.

**Market Microstructure and Informed Trading**:
- Theory / Study: Informed vs. Uninformed Trader Framework
- Citation: Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393–408. https://www.jstor.org/stable/1805228
- Core Insight: For markets to be informationally efficient, informed traders (here, RationalUpdater) must earn returns sufficient to compensate for their information-gathering costs. The ratio of informed to uninformed traders determines the degree of market efficiency.
- Mathematical Formulation: In this simulation, 3 RationalUpdaters out of 13 total agents = ~23% informed trader proportion; Grossman-Stiglitz predicts incomplete information incorporation proportional to this share.
- Empirical Evidence: Chordia, Roll & Subrahmanyam (2005) show that informed institutional trading corrects public information-based mispricings in 0–5 days; consistent with RationalUpdater's immediate response to deviations.
- Relevance to This Investor: With only 3 instances (23% of agents), RationalUpdater provides significant but insufficient corrective force — consistent with the Grossman-Stiglitz prediction that partial efficiency is the equilibrium with costly information.

#### 4.3.3  Design Purpose and Activation Scenarios

Purpose: RationalUpdater provides the corrective force that keeps the simulation's mispricing in a bounded range [3%, 10%] rather than growing without limit. It is the theoretical foil to the anchoring agents — by observing how quickly it fails to correct the mispricing, we measure the strength of the anchoring effect.

Activation Scenarios:
- Price above fundamental by > 2% (price > 102): Sells; provides direct corrective downward pressure.
- Price below fundamental by > 2% (price < 98): Buys; prevents over-correction and provides support.
- Within ±2% of fundamental: Holds; consistent with a 2% minimum threshold required to cover transaction friction.

Market Contribution: **Stabilising** — the only purely corrective agent in the simulation. However, at 3 instances vs. 6 anchoring agents (3 AnchoredTrader + 3 HistoricalAnchor), its corrective force is typically insufficient to fully eliminate the mispricing, consistent with the Grossman-Stiglitz incomplete-efficiency prediction.

Interaction with other agents: Directly opposes AnchoredTrader (sells when AT buys) and HistoricalAnchor (sells when HA buys). Aligns with the γ-term mean reversion in the price formula.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**

| Signal        | Type       | Rationale                                                               |
|---------------|------------|-------------------------------------------------------------------------|
| `price`       | Continuous | Current price; used directly in deviation formula                       |
| `fundamental` | Continuous | True F; the benchmark for rational valuation                            |
| `deviation`   | Continuous | Precomputed (price − F) / F; used directly for trade trigger and sizing |

Does NOT use: anchor, price_history, momentum, sentiment. RationalUpdater processes only the true fundamental deviation — no cognitive biases or heuristics.

**4.3.4.2  Core Behavioral Mechanism**

1. Receives `deviation = (price − F) / F` from Market broadcast.
2. If `deviation > 0.02` (price above F by > 2%): sells; size proportional to deviation.
3. If `deviation < −0.02` (price below F by > 2%): buys; size proportional to deviation.
4. Holds otherwise.
5. No anchoring adjustment, no history, no cognitive bias — pure rational exploitation of fundamental gap.

**4.3.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function: `|deviation(t)| > threshold = 0.02`
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(deviation(t)) × 1000)
  Buy when deviation < −0.02; sell when deviation > +0.02
  ```
- State variables: None — each decision is independent of history
- Parameter definitions:

| Symbol                    | Meaning                              | Config Path                   | Source                                                                                 |
|---------------------------|--------------------------------------|-------------------------------|----------------------------------------------------------------------------------------|
| threshold = 0.02          | Minimum deviation (2%) before action | players.yml → RationalUpdater | Muth (1961): efficient market threshold; Fama (1970): transaction costs typically 1–2% |
| base_position_size = 20.0 | Max trade size                       | players.yml → RationalUpdater | Standardised                                                                           |

**4.3.4.4  Behavioral Properties**

- Time horizon: Short-term — immediate response to any deviation > 2%
- Risk tolerance: Medium — bounded position sizes; no leverage
- Information asymmetry: Fundamental-information informed — uses F directly which anchoring agents cognitively discount
- Psychological profile: Muth-rational — no cognitive biases; processes all information optimally; the "textbook" efficient-markets agent that behavioural finance literature contrasts with real investors

#### 4.3.5  Decision Process Walkthrough

```
Given:  price = 103.5,  fundamental = 100.0,  threshold = 0.02

Step 1: Compute deviation
        deviation = (103.5 − 100.0) / 100.0 = 0.035

Step 2: Compare to threshold
        0.035 > 0.02 → sell condition satisfied

Step 3: Compute quantity
        Q* = min(20.0, 0.035 × 1000) = min(20.0, 35.0) = 20 shares

Step 4: Send order
        action = sell, quantity = 20, bid_price = 103.5

Result: Provides −20 to net demand D(t); contributes λ × (−20) = −$0.20 downward pressure.
        This is the corrective force that (partially) counteracts the buying by AnchoredTrader.
```

#### 4.3.6  Worked Numerical Example

```
Market state:  price = 104.2,  fundamental = 100.0

Calculation:
  deviation = (104.2 − 100.0) / 100.0 = 0.042  (4.2% above fundamental)
  Q* = min(20.0, 0.042 × 1000) = min(20.0, 42.0) = 20 shares

Decision: action = sell, quantity = 20, bid_price = 104.2

Rationale: Price is 4.2% above fundamental. RationalUpdater sells immediately and aggressively.
However, AnchoredTrader's perceived_target is 103.5, so it would BUY at 104.2 only if
price dropped to ~100.4. The two agents are pulling in opposite directions — RationalUpdater
sells while AnchoredTrader may hold or buy if price dips. This tug-of-war creates the
persistent deviation zone [100, 104] characteristic of the AnchoringEffect simulation.
```

#### 4.3.7  Academic References

| # | Citation                                                                                                                                                    | Notes                                                                    |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1 | Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1905537                | Core theoretical foundation for rational updating behaviour              |
| 2 | Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486 | Grounds empirical basis for rational price-discovery mechanism           |
| 3 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393–408.           | Explains why 23% informed traders produces partial (not full) efficiency |

---

### §4.4 MomentumTrader

#### 4.4.1  Summary

MomentumTrader represents the short-horizon trend follower who ignores both fundamentals and anchors, trading purely on round-to-round price changes. In the AnchoringEffect context, MomentumTrader plays an amplifying role: when anchoring creates slow upward price drift, MomentumTrader buys into the trend, extending the overvaluation; when correction begins, MomentumTrader sells, potentially accelerating the mean-reversion. Its effect is context-dependent — it can be both destabilising (extending bubbles) and stabilising (accelerating corrections), depending on the direction of the prevailing trend.

#### 4.4.2  Theoretical and Empirical Foundation

**Short-Horizon Momentum**:
- Theory / Study: Momentum Premium in Equities
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks with strong recent performance tend to continue outperforming in the near term. Momentum traders who follow price trends create self-reinforcing demand during trending periods and sudden reversals when the trend breaks.
- Mathematical Formulation: `return_pct = (price − prev_price) / prev_price`; `trade when |return_pct| > entry_threshold (0.02)`.
- Empirical Evidence: Jegadeesh & Titman (1993) document 12.01% annualised momentum return for 6-month formation/6-month holding periods. For the very short 1-round momentum window used in this simulation, the effect is noisier but consistent with positive autocorrelation documented by Lo & MacKinlay (1988).
- Relevance to This Investor: `entry_threshold = 0.02` (2% price change triggers trade); position size proportional to return magnitude; direction follows price trend.

**Momentum-Anchoring Interaction**:
- Theory / Study: Interaction of Momentum and Fundamental Anchoring
- Citation: Barberis, N., Shleifer, A., & Vishny, R. W. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: Conservatism (underreaction, similar to anchoring) combined with representativeness (overreaction to trends) produces a two-phase price pattern: initial underreaction followed by momentum, then eventual mean reversion. In the AnchoringEffect simulation, anchoring agents produce the initial underreaction, and MomentumTrader provides the momentum phase that extends it.
- Empirical Evidence: Barberis et al. (1998) calibrate their model to explain why returns exhibit short-run momentum (consistent with MomentumTrader's trend-following) and long-run mean reversion (consistent with eventual correction by RationalUpdater and γ-term).
- Relevance to This Investor: MomentumTrader's interaction with anchoring agents produces the Barberis-Shleifer-Vishny two-phase pattern: underreaction (anchoring) → momentum extension (MomentumTrader amplifies slow drift) → correction (RationalUpdater + γ).

#### 4.4.3  Design Purpose and Activation Scenarios

Purpose: MomentumTrader introduces trend-following demand that amplifies price trends in either direction. Its presence prevents the anchoring simulation from being too "clean" (a simple exponential decay toward fundamental) and models the realistic interaction of multiple behavioral biases.

Activation Scenarios:
- Price rising > 2% in last round: Buys; amplifies upward trend (potentially extending overvaluation).
- Price falling > 2% in last round: Sells; amplifies downward trend (potentially accelerating correction).
- Price change within ±2%: Holds.

Market Contribution: **Neutral to Amplifying** — can destabilise (extending bubbles) or stabilise (accelerating corrections) depending on trend direction. Net contribution over the full simulation is approximately neutral.

Interaction with other agents: When price is drifting down toward fundamental, MomentumTrader sells alongside RationalUpdater — briefly accelerating correction. When price is rising, it buys alongside AnchoredTrader — briefly extending the mispricing.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**

| Signal       | Type       | Rationale                                                              |
|--------------|------------|------------------------------------------------------------------------|
| `price`      | Continuous | Current price; numerator of return calculation                         |
| `prev_price` | Continuous | Previous price; denominator of return; required for signal computation |

Does NOT use: `fundamental`, `deviation`, `anchor`. Pure price-trend agent with no fundamental grounding.

**4.4.4.2  Core Behavioral Mechanism**

Simple single-round momentum: if price rose more than 2% from last round, buy; if fell more than 2%, sell; otherwise hold. Size proportional to return magnitude.

**4.4.4.3  Mathematical Model**

- Decision variable: Q*(t)
- Trigger: `return_pct = (price − prev_price) / prev_price`; trade if `|return_pct| > 0.02`
- Sizing: `Q*(t) = min(base_position_size, abs(return_pct) × 1000)`
- State variables: None
- Key parameter: `entry_threshold = 0.02` (Jegadeesh & Titman: 2% threshold consistent with 1-round momentum signal)

**4.4.4.4  Behavioral Properties**

- Time horizon: Very short-term — single-round price change
- Risk tolerance: High — acts on 2% price changes without fundamental check
- Information asymmetry: None — purely reactive to public price data
- Psychological profile: Recency bias; trend extrapolation; consistent with the "representativeness" component of Barberis et al. (1998)

#### 4.4.5  Decision Process Walkthrough

```
Given:  price = 103.0,  prev_price = 100.5,  entry_threshold = 0.02

Step 1: Compute return
        return_pct = (103.0 − 100.5) / 100.5 = 0.0249

Step 2: Compare to threshold
        0.0249 > 0.02 → buy condition satisfied

Step 3: Compute quantity
        Q* = min(20.0, 0.0249 × 1000) = min(20.0, 24.9) = 20 shares

Result: Buys 20 shares; adds to upward pressure; extends the overvaluation slightly
```

#### 4.4.6  Worked Numerical Example

```
Market state:  price = 99.0 (correction phase),  prev_price = 101.5
  return_pct = (99.0 − 101.5) / 101.5 = −0.0246  (<−0.02 → sell)
  Q* = min(20.0, 0.0246 × 1000) = 20 shares (sell)

Decision: action = sell, quantity = 20, bid_price = 99.0
Rationale: Price fell 2.5% in last round; MomentumTrader follows the correction downward,
amplifying the mean-reversion that RationalUpdater initiated. This is the Barberis et al. (1998)
"correction phase" where momentum reinforces the return to fundamental value.
```

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                           | Notes                                                                  |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x           | Core momentum theory; calibrates entry_threshold = 0.02                |
| 2 | Barberis, N., Shleifer, A., & Vishny, R. W. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Grounds anchoring-momentum interaction in a coherent behavioural model |

---

### §4.5 NoiseTrader

#### 4.5.1  Summary

NoiseTrader represents the uninformed retail participant who trades on impulse, rumour, and random sentiment rather than any systematic signal. In the AnchoringEffect simulation, NoiseTrader serves a specific design purpose: it prevents anchoring-induced mispricings from being too "clean" (perfect exponential decay), adds realistic background volatility, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its high trade volume (100–500 shares vs. 20 shares for other agents) means it has disproportionate short-term price impact.

#### 4.5.2  Theoretical and Empirical Foundation

**Noise Trading and Market Microstructure**:
- Theory / Study: Noise Trading and Its Market Effects
- Citation: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- Core Insight: Noise traders (those who trade on noise rather than information) create liquidity and price volatility. Without noise traders, markets would be too thin — only information-based trades would occur. Noise traders make markets more active but also more volatile; their presence is necessary for market function.
- Mathematical Formulation: `Q_noise ~ Uniform(min_order, max_order)` with random direction (buy/sell each with probability 0.5); `P(trade) = 0.05` per round.
- Empirical Evidence: Glosten & Milgrom (1985) estimate that uninformed (noise) trading accounts for 30–60% of total order flow in liquid equity markets. In the 13-agent simulation, 2 NoiseTrader instances with trade_probability = 0.05 produce approximately this proportion of noise volume.
- Relevance to This Investor: Large order size (100–500 shares vs. 20 for anchoring agents) means even occasional trades create significant price volatility, adding realistic noise to the clean anchoring signal.

#### 4.5.3  Design Purpose and Activation Scenarios

Purpose: Add background noise that prevents the simulation from being too mechanistic; provide liquidity; model the realistic presence of uninformed order flow in all markets.

Activation Scenarios:
- With probability 0.05 per round: trades (95% chance of holding each round).
- Random direction (buy or sell with equal probability).
- Random quantity drawn from Uniform(100, 500).

Market Contribution: **Neutral** — expected net demand = 0 over many rounds; but provides large random demand shocks that prevent prices from following a smooth path.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**: None — NoiseTrader does not use any market signals systematically.

**4.5.4.2  Core Behavioral Mechanism**: Probabilistic random trading: trade with probability 0.05, otherwise hold. Trade direction and size are uniformly random.

**4.5.4.3  Mathematical Model**

- Trigger: `random() < trade_probability = 0.05`
- Direction: `random() > 0.5 → buy; else sell`
- Sizing: `Q ~ Uniform(min_order = 100, max_order = 500)`
- Constrained by cash (buy) or position (sell)

**4.5.4.4  Behavioral Properties**

- Time horizon: Random — no consistent horizon
- Risk tolerance: Not applicable — no risk model
- Information asymmetry: None — actively ignores all information
- Psychological profile: Pure noise; no systematic bias; models impulse trading, random sentiment, and order flow noise

#### 4.5.5  Decision Process Walkthrough

```
Round 47:
  Step 1: random() = 0.03 < 0.05 → active this round
  Step 2: random() = 0.72 > 0.5 → buy
  Step 3: quantity = Uniform(100, 500) → 247 shares (constrained by cash)
  Action: buy 247 shares at current price

Round 48:
  Step 1: random() = 0.71 > 0.05 → inactive; hold
```

#### 4.5.6  Worked Numerical Example

```
Market state:  price = 101.0; NoiseTrader cash = 5,000

Trade fires (probability 0.05 rolls 0.03):
  direction: random = 0.2 < 0.5 → sell
  quantity:  Uniform(100, 500) → 183 shares
  position check: current_position = 100 → sell min(183, 100) = 100 shares (limited by position)

Decision: action = sell, quantity = 100, bid_price = 101.0
Market impact: adds −100 to net demand D(t); contributes λ × (−100) = −$1.00 to price
Rationale: A large random sell creates a temporary downward price shock that may trigger
RationalUpdater to hold (price closer to F after shock) or MomentumTrader to sell (following the drop).
```

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                                                                                             | Notes                                                                           |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                                                                                                    | Foundational rationale for noise trading; establishes trade_probability concept |
| 2 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3 | Establishes informed vs. uninformed order flow fractions                        |


## §5 Agent Diversity Verification

```
Diversity Check:
  Different time horizons:
    - Instantaneous: MomentumTrader (1-round return), NoiseTrader (random each round)
    - Medium-term: AnchoredTrader (permanent first-price anchor)
    - Long-term: HistoricalAnchor (60-round rolling average), RationalUpdater (immediate but fundamental-based)

  Different information sets:
    - First-price anchor: AnchoredTrader (anchor + fundamental; biased update)
    - Historical average: HistoricalAnchor (rolling 60-round average; ignores fundamental)
    - True fundamental: RationalUpdater (pure deviation from F)
    - Price momentum: MomentumTrader (prev_price vs. current price only)
    - None: NoiseTrader (random; no systematic information)

  Conflicting incentives:
    - AnchoredTrader buys at 98–104 (biased buying zone) → RationalUpdater sells above 102 (corrective)
    - HistoricalAnchor buys below rolling average → may buy even below fundamental
    - MomentumTrader amplifies trends in both directions → neutral aggregate effect

  Mix of stabilising/destabilising:
    - Destabilising (×2 types × 3 each = 6 agents): AnchoredTrader, HistoricalAnchor
    - Stabilising (×1 type × 3 = 3 agents): RationalUpdater
    - Neutral-amplifying (×1 type × 2 = 2 agents): MomentumTrader
    - Neutral (×1 type × 2 = 2 agents): NoiseTrader
    Total: 15 agents

  Different risk tolerances:
    - High: MomentumTrader (trades on 2% price change), NoiseTrader (random large orders)
    - Medium: AnchoredTrader (3% biased threshold), HistoricalAnchor (3% dampened threshold), RationalUpdater (2% true threshold)
```


## §6 Parameter Table

| Parameter            | Value    | Source Citation                                                                 | Description                                           | Sensitivity                                                                                       |
|----------------------|----------|---------------------------------------------------------------------------------|-------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `initial_price`      | 105.0    | Design choice (5% above fundamental)                                            | Starting price; seeds initial anchoring mispricing    | High — changes initial deviation magnitude                                                        |
| `fundamental_value`  | 100.0    | Design baseline                                                                 | True intrinsic value (constant)                       | Medium                                                                                            |
| `price_impact` (λ)   | 0.01     | Calibrated for anchoring dynamics                                               | Price sensitivity to net demand; LOW                  | **High** — higher λ amplifies noise; lower λ reduces price responsiveness                         |
| `mean_reversion` (γ) | 0.01     | Campbell & Sharpe (2009): slow correction consistent with anchoring persistence | Fundamental pull strength; LOW                        | **High** — γ = 0.01 is essential for persistent mispricings; γ = 0.05 eliminates anchoring effect |
| `noise_std`          | 0.5      | Standard calibration for anchoring market                                       | Gaussian noise std; moderate for anchoring dynamics   | Medium                                                                                            |
| `adjustment_factor`  | 0.3      | Tversky & Kahneman (1974): experimental mean α                                  | Anchor adjustment fraction (AnchoredTrader)           | **High** — core anchoring bias parameter; α = 1 eliminates bias                                   |
| `anchor_weight`      | 0.5      | Northcraft & Neale (1987); Campbell & Sharpe (2009)                             | Historical anchor dampening weight (HistoricalAnchor) | **High** — higher value = stronger historical anchoring                                           |
| `lookback`           | 60       | Campbell & Sharpe (2009): quarterly window                                      | Rolling window for historical average                 | Medium — longer lookback = slower regime updating                                                 |
| `entry_threshold`    | 0.02     | Jegadeesh & Titman (1993): 2% momentum threshold                                | Momentum signal threshold (MomentumTrader)            | Medium                                                                                            |
| `trade_probability`  | 0.05     | Black (1986): noise trader prevalence                                           | Noise trader activity probability per round           | Low — background noise level                                                                      |
| `initial_cash`       | 10,000.0 | Standard                                                                        | Starting cash                                         | Low                                                                                               |
| `initial_position`   | 100.0    | Standard                                                                        | Starting share position                               | Low                                                                                               |
| `base_position_size` | 20.0     | Calibrated                                                                      | Max shares per trade (anchoring and rational agents)  | Medium                                                                                            |


## §7 Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {price, prev_price, fundamental, deviation, round}

  2. Each investor:
     a. perceive() — extract market_data; update price_history (HistoricalAnchor);
                     initialise anchor on first round (AnchoredTrader)
     b. decide()   — apply anchoring/momentum/rational/random strategy
     c. act()      — update portfolio (cash, position); send order to Market

  3. Market:
     a. perceive() — collect all investor orders; aggregate buy/sell quantities
     b. decide()   — apply P(t+1) = P(t) + λ×D(t) + γ×[F−P(t)] + ε(t); compute deviation
     c. act()      — broadcast new market state to all investors

  4. Logging via HistoryBuffer; per-agent portfolio state persisted each round
```

Topology: Star — Market at centre broadcasts to all 15 investors; investors send orders back to Market.

Initialization: Market starts at `initial_price = 105.0` (5% above fundamental 100.0). AnchoredTrader records this as its permanent anchor on round 1, seeding the initial mispricing that the simulation then studies.


## §8 Historical Case Studies

### Event: Analyst Earnings Forecast Anchoring (US Equity Markets, 1992–2006)

- **Date**: 1992–2006 (Campbell & Sharpe, 2009 study period)
- **Market**: US equity markets; Bloomberg consensus earnings forecasts
- **Trigger**: Analysts revise quarterly EPS forecasts after receiving new data; anchoring causes insufficient revisions
- **Key Dynamics**:
  - Analysts update forecasts based on prior-period actuals plus new information
  - Revisions are only 30–70% of the optimal Bayesian update (consistent with α = 0.3–0.7)
  - Creates predictable, persistent forecast errors exploitable by quantitative strategies
  - Effect is strongest for companies with high earnings volatility (where anchoring creates the largest errors)
- **Quantitative Data**: Average under-revision approximately 50% of optimal update; forecast error autocorrelation r ≈ 0.4 (systematic, not random); trading strategy based on revision predictability earns Sharpe ratio ≈ 0.6 (Campbell & Sharpe, 2009)
- **Agent Mapping**:
  - Buy-side analysts anchoring to prior-quarter EPS → `AnchoredTrader` (α = 0.3 under-revision)
  - Institutional investors anchoring to long-run average EPS → `HistoricalAnchor` (60-quarter rolling average)
  - Quantitative funds exploiting predictable forecast errors → `RationalUpdater`
- **Lessons for Simulation**:
  - Calibrate `adjustment_factor = 0.3–0.5` to match empirical under-revision rates
  - Simulation should show persistent price deviation: 5–15% above/below fundamental — matching Campbell & Sharpe's measured forecast error magnitudes
  - Source: Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts. *JFQA*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127

### Event: Real Estate Appraisal Anchoring (Northcraft & Neale, 1987)

- **Date**: 1987 (laboratory study published)
- **Market**: Residential real estate (Tucson, Arizona)
- **Trigger**: Listed asking price used as anchor in valuation experiment; professional appraisers given identical property data but different listing prices
- **Key Dynamics**:
  - High listing price group estimated significantly higher market value than low listing price group
  - Both expert appraisers and student novices anchored toward the listing price
  - Experts showed smaller but still statistically significant anchoring (~12% vs. ~21% for novices)
  - Effect persists even when participants are explicitly warned about anchoring
- **Quantitative Data**: Expert valuations anchored ~12% toward the listed price anchor; student valuations anchored ~21%; correlation between listed price and estimated value: r ≈ 0.7
- **Agent Mapping**:
  - Expert appraisers using historical comps → `HistoricalAnchor` (anchors to 60-round rolling average)
  - Retail investors anchoring to asking price or 52-week high → `AnchoredTrader` (first-price anchor)
- **Lessons for Simulation**:
  - Even experts anchor; `anchor_weight = 0.5` reflects the professional (not student) anchoring magnitude
  - The persistent mispricing zone [F, anchor] replicates the expert-client disagreement on property value documented by Northcraft & Neale
  - Source: Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate. *OBHDP*, 39(1), 84–97.

### Event: IPO Aftermarket Price Anchoring

- **Date**: Persistent phenomenon across multiple decades and markets
- **Market**: Primary and secondary equity markets globally
- **Trigger**: IPO offer price serves as natural anchor for all subsequent retail investor valuations
- **Key Dynamics**:
  - Retail investors treat IPO price as "fair value" reference for 6–12 months after issuance
  - Post-IPO underperformance partly attributable to anchor-based overvaluation at issuance
  - Price frequently oscillates around the IPO price anchor for extended periods
  - When price falls below IPO anchor, retail investors hold losses (loss aversion + disposition effect interaction)
- **Quantitative Data**: Loughran & Ritter (2002) document significant IPO price anchoring effect on 1-year aftermarket pricing; stocks rarely trade 20%+ below IPO price in first month even when fundamentals justify it
- **Agent Mapping**:
  - Retail investors anchoring to IPO price as "fair value" → `AnchoredTrader` (first-price = IPO price anchor)
  - Institutional value investors ignoring IPO price → `RationalUpdater`
- **Lessons for Simulation**:
  - `initial_price = 105.0` (above fundamental 100.0) seeds the IPO-style initial overvaluation
  - 100-round simulation represents the post-IPO adjustment period
  - Source: Loughran, T., & Ritter, J. R. (2002). Why don't issuers get upset about leaving money on the table in IPOs? *Review of Financial Studies*, 15(2), 413–444. https://doi.org/10.1093/rfs/15.2.413


## §9 Variant Comparison Preview

| Aspect                   | Rule                                                                    | LLM                                                            | RuleLLM                                                              | Rag                                                                             |
|--------------------------|-------------------------------------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------|---------------------------------------------------------------------------------|
| Decision Logic           | Deterministic formulas (α = 0.3 exactly)                                | Persona-guided reasoning; "slow to update" trait               | Formula-anchored LLM (α = 0.3 in DECISION RULES)                     | RAG-augmented: retrieves anchoring research; may reduce bias                    |
| Determinism              | Fully deterministic                                                     | Stochastic                                                     | Semi-deterministic (rules constrain ±20%)                            | Stochastic                                                                      |
| Anchoring Implementation | Hardcoded formula                                                       | Implicit via "slow to update, trust first price" persona       | Explicit formula in == DECISION RULES ==                             | Formula + retrieved anchoring literature may reduce α                           |
| Expected MAD             | Stable, predictable 3–8%                                                | Variable, 2–12% with LLM variance                              | Bounded, ≈ Rule ± 20%                                                | Potentially lower if RAG retrieves corrective research                          |
| Adjustment Rate          | Constant α = 0.3                                                        | LLM-inferred; varies by context                                | Constrained α ≈ 0.3 ± 20%                                            | α modified by retrieved knowledge about anchoring bias                          |
| Research Question        | Can anchoring formulas reproduce empirically observed price stickiness? | Do LLM personas reproduce anchoring without explicit formulas? | Does embedding rules constrain LLM anchoring to match Rule baseline? | Does domain knowledge about anchoring bias reduce anchoring-driven mispricings? |
