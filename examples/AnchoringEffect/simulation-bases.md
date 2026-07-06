# AnchoringEffect — Simulation Design Basis

---

## Table of Contents

| §   | Section                           | Subsections                                                                                                                                                                                             |
|-----|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| §1  | Phenomenon Definition             | §1.1 Origin and Source Analysis (Intellectual Lineage, Real-World Events, Practitioner Literature)                                                                                                      |
| §2  | Theoretical Foundation            | Anchoring & Insufficient Adjustment; Expert Anchoring; Consensus Forecasts; Rational Expectations; Momentum & Trend Following                                                                           |
| §3  | Market Design Principles          | 3.0 Idealised Market Type; 3.1 Price Formation Model; 3.2 Additional Mechanisms; 3.3 Information Broadcast                                                                                              |
| §4  | Investor Taxonomy (9 types)       | §4.1 AnchoredTrader; §4.2 HistoricalAnchor; §4.3 RationalUpdater; §4.4 MomentumTrader; §4.5 NoiseTrader; §4.6 DispositionTrader; §4.7 ContrarianTrader; §4.8 FundamentalAnalyst; §4.9 LiquidityProvider |
| §5  | Agent Diversity Verification      | Time-horizon matrix, information-set coverage, strategy taxonomy                                                                                                                                        |
| §6  | Parameter Table                   | All configurable parameters with default values and academic calibration sources                                                                                                                        |
| §7  | Communication and Round Structure | Star topology, message format, round lifecycle                                                                                                                                                          |
| §8  | Historical Case Studies           | Analyst Earnings Anchoring; Real Estate Appraisal Anchoring; IPO Aftermarket Anchoring                                                                                                                  |
| §9  | Variant Comparison Preview        | Rule vs LLM vs RuleLLM vs Rag — expected behavioural differences                                                                                                                                        |
| §10 | Equilibrium Analysis              | Steady-state derivation, biased equilibrium P* > F, convergence eigenvalue, two-phase dynamics                                                                                                          |
| §11 | Limitations and Assumptions       | Simplifying assumptions, agent limitations, model scope boundary, known fragilities                                                                                                                     |

**Agent Design Summary (§4)**:

| #   | Agent              | Role in Ecosystem         | Theoretical Basis                       | Bias / Strategy           |
|-----|--------------------|---------------------------|-----------------------------------------|---------------------------|
| 4.1 | AnchoredTrader     | Primary anchoring source  | Tversky & Kahneman (1974)               | Insufficient adjustment   |
| 4.2 | HistoricalAnchor   | Path-dependent anchor     | Kahneman (2011); De Bondt (1993)        | Moving-average anchoring  |
| 4.3 | RationalUpdater    | Corrective arbitrage      | Fama (1970); Grossman & Stiglitz (1980) | Fundamental-driven        |
| 4.4 | MomentumTrader     | Trend amplifier           | Jegadeesh & Titman (1993)               | Short-term momentum       |
| 4.5 | NoiseTrader        | Liquidity / entropy       | Black (1986); DeLong et al. (1990)      | Random                    |
| 4.6 | DispositionTrader  | Prospect-theory bias      | Shefrin & Statman (1985)                | Sell winners, hold losers |
| 4.7 | ContrarianTrader   | Overreaction corrector    | De Bondt & Thaler (1985)                | Mean-reversion betting    |
| 4.8 | FundamentalAnalyst | Conservative learner      | Barberis, Shleifer & Vishny (1998)      | Slow belief updating      |
| 4.9 | LiquidityProvider  | Market maker / stabilizer | Glosten & Milgrom (1985)                | Two-sided quoting         |

---

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | **Anchoring Effect** — a cognitive bias causing traders to insufficiently adjust price estimates from an initial reference point (the "anchor"), producing persistent deviations from fundamental value and slowing price discovery                                                                                                                                                                                                        |
| Category           | Behavioural bias / cognitive heuristic / slow price discovery / market inefficiency                                                                                                                                                                                                                                                                                                                                                        |
| Core Mechanism     | Agents set an initial anchor (first observed price, historical average, or round number) and adjust toward true fundamental value by only a fraction of the required adjustment. Even when fundamental value is publicly known, anchoring prevents agents from trading at the correct price, creating persistent mispricings. The fundamental value is observable to all — the anchoring is a cognitive failure, not an informational one. |
| Real-World Origin  | Documented in equity analyst earnings forecasts (Campbell & Sharpe, 2009: ~50% under-revision), real estate appraisal (Northcraft & Neale, 1987: experts anchor to listed prices), IPO aftermarket pricing (Loughran & Ritter, 2002: prices cluster near IPO anchor), and post-earnings announcement drift                                                                                                                                 |
| Research Relevance | Anchoring is one of the most empirically robust cognitive biases in financial markets. It explains slow price discovery, momentum effects, analyst forecast conservatism, and the well-documented post-earnings drift anomaly — all of which have direct implications for market efficiency, arbitrage profitability, and behavioural finance theory.                                                                                      |

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Anchoring entered behavioural decision theory through Tversky and Kahneman's
1974 account of heuristics under uncertainty. Their central observation was
that people start numerical estimates from a salient reference value and then
adjust insufficiently, even when the anchor is arbitrary. This simulation keeps
that mechanism literal: the first observed market price becomes the
`AnchoredTrader` reference point, while the true fundamental value is visible
but underweighted.

The finance-specific lineage comes from expert valuation and forecast-revision
studies. Northcraft and Neale (1987) show that professional appraisers remain
pulled toward listing-price anchors, and Campbell and Sharpe (2009) show that
consensus financial forecasts underreact to new information. These sources
justify the two primary biased agents: `AnchoredTrader`, which uses the first
price anchor, and `HistoricalAnchor`, which anchors to a rolling price average.

The model includes `RationalUpdater` to represent the rational-expectations
counterforce from Muth (1961) and Fama (1970). It also includes
`MomentumTrader` and `NoiseTrader` to prevent a purely two-agent tug-of-war:
momentum amplifies local trends, while noise creates realistic background order
flow. This combination turns an individual cognitive bias into an observable
market-level slow price-discovery process.

#### §1.1.2 Real-World Event Catalogue

| Event Name                      | Date(s)                  | Market / Asset              | Trigger                                         | Magnitude                                                                                                        | Duration                                               | Correspondence to Simulation                                                                | Primary Source                                                                 |
|---------------------------------|--------------------------|-----------------------------|-------------------------------------------------|------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Consensus forecast anchoring    | 1992–2006                | US macro/earnings forecasts | Forecasters revise from prior values after news | Under-revision roughly 30–70%; forecast-error autocorrelation around 0.4                                         | Quarterly forecast cycles                              | `AnchoredTrader` and `HistoricalAnchor` under-adjust toward the public fundamental          | Campbell & Sharpe (2009), JFQA, https://doi.org/10.1017/S0022109009090127      |
| Real-estate appraisal anchoring | 1987 study               | Residential real estate     | Listing price supplied before valuation         | Expert valuations shift materially toward the listing price; study reports strong listing-price correlation      | Single appraisal task with persistent valuation impact | `HistoricalAnchor` treats past/listed prices as reference values despite valuation evidence | Northcraft & Neale (1987), OBHDP, https://doi.org/10.1016/0749-5978(87)90046-X |
| IPO aftermarket anchoring       | Multi-decade IPO samples | Newly listed equities       | Offer price becomes salient public reference    | IPO aftermarket prices cluster around offer-price anchors; large first-year effects documented in IPO literature | Months after issuance                                  | `initial_price = 105` seeds a first-price anchor above `fundamental_value = 100`            | Loughran & Ritter (2002), RFS, https://doi.org/10.1093/rfs/15.2.413            |

#### §1.1.3 Book and Practitioner Literature

| Title                                      | Author(s)          | Year      | Publisher                  | Relevance to This Simulation                                                                                                     |
|--------------------------------------------|--------------------|-----------|----------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| *Thinking, Fast and Slow*                  | Daniel Kahneman    | 2011      | Farrar, Straus and Giroux  | Practitioner-readable synthesis of anchoring-and-adjustment experiments and why anchors remain influential even when recognized. |
| *Irrational Exuberance*                    | Robert J. Shiller  | 2000/2015 | Princeton University Press | Connects salient reference prices and narratives to slow-moving market expectations and behavioural price persistence.           |
| *Behavioral Finance and Wealth Management* | Michael M. Pompian | 2006      | Wiley                      | Practitioner taxonomy of anchoring and adjustment bias in investment decision-making, useful for persona descriptions.           |


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
- **Relevance to This Simulation**: The market-level Mean Absolute Deviation and mean-reversion half-life observed in the simulation are the aggregated price-formation consequence of many anchoring agents, exactly the mechanism Campbell & Sharpe (2009) document at the consensus-forecast level. The simulation therefore reproduces at the price layer what their paper measures at the forecast layer.
- **Calibration Implication**: The θ ≈ 0.3 lower-bound estimate directly calibrates `adjustment_factor = 0.3` in `AnchoredTrader` (anchoring reduces update to 30 % of the rational level); the paper's autocorrelated forecast-error range calibrates the §5 target Mean Absolute Deviation band `[3 %, 10 %]` and persistence half-life band `[20, 60 rounds]`; the paper's ~50 % under-revision median justifies the slow mean-reversion parameter `γ = 0.01` in §3.

---

### Theory: Rational Expectations Benchmark

- **Citation**: Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1905537
- **Core Insight**: Under rational expectations, agents optimally use all available information. Prices fully reflect all available information; no systematic deviations from fundamental value are exploitable. The contrast between Muth-rational agents (who update fully to any new information) and anchoring agents (who update only partially) is the central theoretical tension driving the AnchoringEffect simulation.
- **Mathematical Formulation**: Rational update: `E[P(t+1) | info(t)] = F(t)` (full updating). Anchored update: `E[P(t+1) | info(t)] = anchor + α × (F(t) − anchor)` (partial updating, α < 1).
- **Empirical Evidence**: Fama (1970) documents that prices approximate rational expectations in liquid markets on short horizons; however, Campbell & Sharpe (2009), Lo & MacKinlay (1988), and the broader behavioural finance literature establish that medium-horizon deviations from rational expectations are systematic and persistent.
- **Relevance to This Simulation**: `RationalUpdater` embodies Muth's rational agent — it uses the true `deviation = (price − fundamental) / fundamental` with no anchoring bias, acting as the benchmark corrective force.
- **Calibration Implication**: `RationalUpdater` trade_threshold = 0.02 encodes the Muth-rational agent that trades whenever price departs from fundamental by more than 2 %; setting the threshold much smaller than the anchoring-induced MAD range [3 %, 10 %] ensures that RU is always active as a corrective force against anchored demand.

---

### Theory: Short-Horizon Momentum and Trend Following

- **Citation**: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- **Core Insight**: Stocks with strong recent price performance (past 3–12 months) tend to continue outperforming in the near term. Momentum traders who follow this pattern amplify existing price trends, interacting with anchoring bias to either extend mispricings (when trend aligns with anchor) or accelerate correction (when trend reverses toward fundamental).
- **Mathematical Formulation**: `momentum_signal = (price − prev_price) / prev_price`; trade when `|momentum_signal| > entry_threshold`; position size proportional to signal magnitude.
- **Empirical Evidence**: Jegadeesh & Titman (1993) document 12.01% annualised momentum return in US equities (1965–1989). The momentum effect interacts with anchoring: anchored prices that are drifting slowly toward fundamental provide a weak but predictable trend that momentum traders can amplify temporarily.
- **Relevance to This Simulation**: `MomentumTrader` amplifies existing trends, including the slow anchoring-driven drift toward or away from fundamental. During the initial overvalued phase, MomentumTrader may briefly extend the mispricing; during correction, it may accelerate it.
- **Calibration Implication**: `entry_threshold = 0.02` calibrates MomentumTrader to activate on 1-round moves consistent with Jegadeesh & Titman's (1993) empirical positive-serial-correlation regime; larger thresholds silence the agent, smaller thresholds turn it into a noise amplifier.

---

### Theory: Prospect Theory Disposition Effect

- **Citation**: Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x; Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–292. https://doi.org/10.2307/1914185
- **Core Insight**: Loss-averse investors realise gains at roughly 1.5 – 2.5× the rate at which they realise losses of equal magnitude, because the S-shaped prospect-theory value function is concave for gains and convex for losses. The reference point is the purchase price (cost basis), creating an asymmetric response independent of fundamental value.
- **Mathematical Formulation**: `sell if (P − cost) / cost > gain_threshold`; `hold if (cost − P) / cost < gain_threshold × loss_aversion_mult`; `V(x) = x^α for x ≥ 0, −λ(−x)^β for x < 0` with `α ≈ β ≈ 0.88`, `λ ≈ 2.25` (Tversky & Kahneman 1992).
- **Empirical Evidence**: Odean (1998) documents 1.68× gain-vs-loss realisation ratio for retail brokerage accounts. Weber & Camerer (1998) reproduce the disposition effect in controlled experiments. The 2.0 – 2.5× loss-aversion multiplier is stable across markets and countries.
- **Relevance to This Simulation**: `DispositionTrader` sells early when its position gains above `gain_threshold = 0.04` but holds losing positions until the loss reaches `gain_threshold × loss_aversion_mult ≈ 10 %`, producing asymmetric selling pressure that interacts with the anchoring drift.
- **Calibration Implication**: `gain_threshold = 0.04` and `loss_aversion_mult = 2.5` calibrate the agent to the empirical 4 % gain-realisation median and the 2.25 – 2.5× loss-aversion multiplier documented by Kahneman & Tversky (1979) and Odean (1998).

---

### Theory: Overreaction and Short-Horizon Reversal

- **Citation**: De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x; Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881–898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
- **Core Insight**: Cumulative returns over short horizons overshoot fair value and are followed by reversals. Contrarian traders exploit this by shorting after cumulative rises and buying after cumulative falls, providing a stabilising counterweight to trend followers.
- **Mathematical Formulation**: `cum_ret = (P_t − P_{t−k}) / P_{t−k}`; short if `cum_ret > entry_threshold`, long if `cum_ret < −entry_threshold`; position size scales linearly with |cum_ret|.
- **Empirical Evidence**: De Bondt & Thaler (1985) find 25 % cumulative excess return to contrarian portfolios over 3-year horizons. Jegadeesh (1990) documents negative serial correlation over 1 – 4-week horizons in US equity returns.
- **Relevance to This Simulation**: `ContrarianTrader` fades the short-horizon cumulative return over a 10-round window, opposing MomentumTrader and providing statistical mean-reversion that complements the deterministic γ term.
- **Calibration Implication**: `lookback = 10` maps to Jegadeesh's (1990) 2-week reversal horizon scaled to daily rounds; `entry_threshold = 0.05` matches De Bondt & Thaler's (1985) 5 % overreaction threshold.

---

### Theory: Conservatism and Slow Belief Updating

- **Citation**: Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
- **Core Insight**: Institutional investors update beliefs conservatively in response to new information. The BSV model predicts that conservatism produces post-announcement drift as beliefs slowly converge toward the true fundamental, matching the post-earnings announcement drift anomaly.
- **Mathematical Formulation**: `b_{t+1} = b_t + η × (F − b_t)` (exponential smoothing of belief toward fundamental); trade on `(b_t − P) / P` with a `dev_threshold`.
- **Empirical Evidence**: Bernard & Thomas (1989) document post-earnings announcement drift lasting 60 – 90 trading days. Barberis, Shleifer & Vishny (1998) estimate learning rates `η ≈ 0.03 – 0.08` from cross-sectional analyst-forecast data.
- **Relevance to This Simulation**: `FundamentalAnalyst` starts each run with `belief = initial_price = 105` (i.e., anchored to the same salient value as `AnchoredTrader`) and converges toward `F = 100` at rate `η`. Early in the run it aligns with anchored demand; later in the run it aligns with `RationalUpdater` and adds corrective force.
- **Calibration Implication**: `learning_rate = 0.05` is the midpoint of Barberis, Shleifer & Vishny's (1998) empirical range; `dev_threshold = 0.02` matches the RationalUpdater threshold so the two corrective agents have compatible activation.

---

### Theory: Market Making and Two-Sided Quoting

- **Citation**: Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3; Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011). Does algorithmic trading improve liquidity? *Journal of Finance*, 66(1), 1–33. https://doi.org/10.1111/j.1540-6261.2010.01624.x
- **Core Insight**: Market makers post continuous two-sided quotes around a short-term fair-value estimate (here, an EMA of the price) and profit from the spread. They neither speculate on direction nor react to the true fundamental; they absorb transient order-flow imbalance and dampen short-term volatility.
- **Mathematical Formulation**: `EMA_t = (1 − w) · EMA_{t−1} + w · P_t` with `w = 2 / (ema_window + 1)`; `bid = EMA · (1 − half_spread)`, `ask = EMA · (1 + half_spread)`; buy when `P < bid`, sell when `P > ask`.
- **Empirical Evidence**: Huang & Stoll (1997) estimate effective half-spreads of 0.5 – 2 % for actively traded stocks. Hendershott, Jones & Menkveld (2011) show that algorithmic liquidity providers reduce intraday volatility by 15 – 25 %.
- **Relevance to This Simulation**: `LiquidityProvider` uses `ema_window = 20` and `half_spread = 0.015` to absorb `NoiseTrader` shocks and to dampen short-horizon volatility without contributing directional pressure. Its presence keeps the anchoring dynamics visible instead of drowning under noise.
- **Calibration Implication**: `ema_window = 20` is the mid-range algorithmic-MM update interval documented by Hendershott, Jones & Menkveld (2011); `half_spread = 0.015` sits within Huang & Stoll's (1997) empirically observed 0.5 – 2 % effective half-spread band.


## §3 Market Design Principles

### 3.0 Idealised Market Type and Real-World Mapping

**Market type**: single-asset, single-venue, USD-denominated equity-style spot market with continuous quote-driven price formation. The simulation is deliberately abstract — there is no derivatives layer, no leverage, no credit risk, no cross-asset effect, no FX rate, no funding cost. All scenarios in this codebase share this canonical abstraction; scenarios whose real-world phenomenon lives in another asset class (FX, credit, rates, commodities) **map** the empirical dynamic onto this abstraction rather than modelling its native microstructure.

**Why a single abstraction**: Empirical anchoring evidence (Tversky & Kahneman 1974; Northcraft & Neale 1987; Campbell & Sharpe 2009) is asset-class-invariant — the cognitive bias appears in equity, real estate, FX, and analyst forecast settings. A unified abstraction enables direct cross-scenario comparison without conflating mechanism heterogeneity with bias heterogeneity. This is the standard practice in agent-based finance:

- Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8-9), 1235-1274. https://doi.org/10.1016/S0165-1889(98)00011-6
- LeBaron, B. (2006). Agent-based computational finance. In *Handbook of Computational Economics, Vol. 2*, 1187-1233. North-Holland. https://doi.org/10.1016/S1574-0021(05)02024-1
- Lux, T., & Marchesi, M. (1999). Scaling and criticality in a stochastic multi-agent model of a financial market. *Nature*, 397(6719), 498-500. https://doi.org/10.1038/17290

**Mapping table**:

| Symbol | Real-world counterpart                                | Abstraction in this scenario                           |
|--------|-------------------------------------------------------|--------------------------------------------------------|
| `P(t)` | Quoted last price of any tradable asset               | Scalar equity-like price, USD per share                |
| `F`    | Consensus fair value (DCF, comparable, model-implied) | Constant scalar, USD per share                         |
| `D(t)` | Net order flow at the venue                           | Net signed quantity from all investors                 |
| `λ`    | Kyle's lambda / market impact coefficient             | Calibrated to keep round-over-round price moves modest |
| `γ`    | Mean-reversion intensity (slow arbitrage)             | Calibrated to allow persistence over 20-60 rounds      |
| `ε(t)` | Microstructure noise, liquidity shocks                | Gaussian, σ ≈ 0.5                                      |

**Explicit non-features** (intentionally absent from the model):

- No FX rates — all prices are quoted in a single numéraire (USD).
- No yield curves, term structure, or duration risk.
- No credit spreads, default risk, or recovery rates.
- No leverage, margin, or funding cost.
- Single venue — no fragmentation, no latency arbitrage.
- No options, futures, or other derivatives.
- No transaction cost, no bid-ask spread (continuous quote-driven price).

**Mapping examples for non-equity scenarios**:

- *LTCMCollapse* — `P(t)` represents the spread between on-the-run and off-the-run treasury bonds; `F` represents the long-run no-arbitrage spread. Investor decision rules (anchor, momentum, rational arbitrage) retain their qualitative meaning without claiming faithful microstructure of the bond repo market.
- *CarryTradeUnwind* — `P(t)` represents the carry-currency exchange rate; `F` represents the interest-rate-parity-implied rate.
- *ArchegosCollapse* — `P(t)` represents a synthetic equity exposure price; collateral and leverage dynamics are absent and replaced by abstract demand pressure.

**For AnchoringEffect specifically**: the asset stands for any single equity whose consensus fair value is anchored by analysts to a stale reference (Campbell & Sharpe 2009 study analyst forecasts; Northcraft & Neale 1987 study real-estate appraisal anchoring — the simulation is faithful to the *cognitive* mechanism in both, regardless of asset class). All dollar amounts in the simulation are abstract numéraire units.

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
- Mathematical Formulation: In this simulation, 1 RationalUpdater out of 9 investor agents = ~11% informed trader proportion; Grossman-Stiglitz predicts incomplete information incorporation proportional to this share.
- Empirical Evidence: Chordia, Roll & Subrahmanyam (2005) show that informed institutional trading corrects public information-based mispricings in 0–5 days; consistent with RationalUpdater's immediate response to deviations.
- Relevance to This Investor: With only 3 instances (23% of agents), RationalUpdater provides significant but insufficient corrective force — consistent with the Grossman-Stiglitz prediction that partial efficiency is the equilibrium with costly information.

#### 4.3.3  Design Purpose and Activation Scenarios

Purpose: RationalUpdater provides the corrective force that keeps the simulation's mispricing in a bounded range [3%, 10%] rather than growing without limit. It is the theoretical foil to the anchoring agents — by observing how quickly it fails to correct the mispricing, we measure the strength of the anchoring effect.

Activation Scenarios:
- Price above fundamental by > 2% (price > 102): Sells; provides direct corrective downward pressure.
- Price below fundamental by > 2% (price < 98): Buys; prevents over-correction and provides support.
- Within ±2% of fundamental: Holds; consistent with a 2% minimum threshold required to cover transaction friction.

Market Contribution: **Stabilising** — the only purely corrective agent type in the simulation. However, at 1 instance vs. 4 anchoring agents (2 AnchoredTrader + 2 HistoricalAnchor), its corrective force is intentionally weaker than the biased demand block, consistent with the Grossman-Stiglitz incomplete-efficiency prediction.

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
- Empirical Evidence: Glosten & Milgrom (1985) estimate that uninformed (noise) trading accounts for 30–60% of total order flow in liquid equity markets. In the 9-investor simulation, 2 NoiseTrader instances with trade_probability = 0.05 provide sparse background liquidity without dominating systematic anchoring and rational-updating flows.
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

---

### §4.6 DispositionTrader

#### 4.6.1  Summary

DispositionTrader represents the retail investor who systematically sells winning positions too early and holds losing positions too long. This agent models the Disposition Effect (Shefrin & Statman, 1985) — a behavioural pattern rooted in Prospect Theory (Kahneman & Tversky, 1979) where the asymmetric value function makes realised gains feel less painful to lock in while realised losses feel disproportionately aversive. In the AnchoringEffect simulation, DispositionTrader introduces asymmetric liquidity: when prices are elevated above its cost basis (a gain scenario), it sells quickly, adding downward pressure that partially offsets anchoring-driven overvaluation. When prices fall below cost basis (a loss scenario), it refuses to sell, removing potential liquidity and allowing mispricings to persist with less corrective flow.

#### 4.6.2  Theoretical and Empirical Foundation

**The Disposition Effect**:
- Theory / Study: Disposition to Sell Winners Too Early and Ride Losers Too Long
- Citation: Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Core Insight: Investors are approximately 1.5–2.5× more likely to sell a position showing a gain than one showing a loss of equal magnitude. This asymmetry is a direct consequence of Prospect Theory's S-shaped value function and reference-point dependence. The reference point is the purchase price (cost basis).
- Mathematical Formulation:
  ```
  gain_pct(t) = (P(t) − cost_basis) / cost_basis
  If gain_pct > gain_threshold (+4%): sell (lock in profit)
  If gain_pct < −gain_threshold / loss_aversion_mult (< −1.6%): buy ("average down" into perceived bargain)
  Else: hold (loss aversion prevents selling losers; no trigger for winners)
  ```
- Empirical Evidence: Odean (1998, *Journal of Finance*) documents that individual investors at a large brokerage realise gains at 1.68× the rate of losses. Weber & Camerer (1998, *Journal of Economic Behavior and Organization*) confirm disposition effects in controlled experiments. The asymmetry ratio 1.5–2.5× calibrates the `loss_aversion_mult = 2.5` parameter.
- Relevance to This Investor: DispositionTrader's cost basis starts near the initial_price (≈105) because it holds position from round 1. As anchoring keeps prices elevated (101–105), the trader remains near breakeven and is inactive. Once prices rise above cost basis by 4%, it sells — providing temporary downward pressure that partially counteracts anchoring-driven overvaluation.

**Prospect Theory Foundation**:
- Theory / Study: Asymmetric Value Function and Reference-Point Dependence
- Citation: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–292. https://doi.org/10.2307/1914185
- Core Insight: The value function is concave for gains (risk averse) and convex for losses (risk seeking), with losses weighted approximately 2.25× more heavily than equivalent gains. This creates the disposition effect: the disutility of realising a $X loss exceeds the utility of realising a $X gain by factor ~2.25.
- Mathematical Formulation: `V(x) = x^α if x ≥ 0; −λ(−x)^β if x < 0` where α ≈ 0.88, β ≈ 0.88, λ ≈ 2.25 (Tversky & Kahneman 1992).
- Relevance to This Investor: The `loss_aversion_mult = 2.5` parameter approximates λ = 2.25 from cumulative prospect theory, controlling the asymmetry between gain-triggered selling and loss-triggered inaction.

#### 4.6.3  Design Purpose and Activation Scenarios

Purpose: DispositionTrader introduces realistic asymmetric liquidity provision that interacts with the anchoring lifecycle in a phase-dependent manner. During the overvaluation phase (Phase 2), when prices hover above fundamental but near cost basis, the agent is largely inactive. During rallies above cost basis, it sells — providing temporary downward pressure. During corrections below cost basis, it holds — removing potential selling flow and allowing mispricings to persist on the downside.

Activation Scenarios:
- Price above cost basis by > 4% (gain zone): Sells to lock in profit. Adds downward pressure that partially offsets anchoring-driven overvaluation.
- Price below cost basis by > 1.6% (loss_threshold = gain_threshold / loss_aversion_mult): Buys ("averaging down" — the disposition investor's tendency to reinforce losing positions). Adds upward pressure.
- Price within ±4% / ±1.6% of cost basis: Holds — the asymmetric inaction zone where neither gain-taking nor loss-aversion-driven buying is triggered.

Market Contribution: **Asymmetrically destabilizing** — accelerates profit-taking when prices are elevated, but removes liquidity during corrections. The asymmetry interacts with anchoring to create sharper peaks and slower troughs.

Interaction with other agents: Partially offsets AnchoredTrader's upward support (by selling winners above cost basis); reinforces HistoricalAnchor's inertia during declines (both refuse to sell into falling markets, though for different reasons).

#### 4.6.4  Behavioral Framework

**4.6.4.1  Decision Information Set**

| Signal       | Type             | Rationale                                                                                |
|--------------|------------------|------------------------------------------------------------------------------------------|
| `price`      | Continuous       | Current market price; compared to cost_basis reference point                             |
| `cost_basis` | Persistent state | Running weighted-average purchase price; updated on each buy; the Prospect Theory anchor |

Does NOT use: `fundamental`, `deviation`, `prev_price`. DispositionTrader's reference is its own purchase history, not any external fundamental or momentum signal.

**4.6.4.2  Core Behavioral Mechanism**

1. Maintains `cost_basis` = weighted average of all historical purchase prices (initial = initial_price at round 1).
2. Each round: computes `gain_pct = (price − cost_basis) / cost_basis`.
3. If `gain_pct > gain_threshold (+0.04)`: sells — disposition effect profit-taking.
4. If `gain_pct < −gain_threshold / loss_aversion_mult (−0.016)`: buys — averaging down into perceived bargain.
5. Otherwise: holds — the asymmetric inaction zone.
6. On each buy, `cost_basis` updates: `cost_basis = (old_cost_basis × old_position + price × quantity) / (old_position + quantity)`.

**4.6.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  gain_pct(t) = (P(t) − cost_basis) / cost_basis
  Sell: gain_pct(t) > gain_threshold = 0.04
  Buy:  gain_pct(t) < −gain_threshold / loss_aversion_mult = −0.016
  Hold: otherwise
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(gain_pct(t)) × 500)
  Bounded by cash (buy) or position (sell)
  ```
- State variables: `cost_basis` — updated on every buy trade
- Parameter definitions:

| Symbol                    | Meaning                               | Config Path                     | Source                                                               |
|---------------------------|---------------------------------------|---------------------------------|----------------------------------------------------------------------|
| gain_threshold = 0.04     | Minimum gain to trigger profit-taking | players.yml → DispositionTrader | Odean (1998): median disposition investors realise gains at 4–8%     |
| loss_aversion_mult = 2.5  | Loss aversion asymmetry multiplier    | players.yml → DispositionTrader | Kahneman & Tversky (1979): λ ≈ 2.25; rounded to 2.5 for conservatism |
| base_position_size = 15.0 | Maximum trade size                    | players.yml → DispositionTrader | Smaller than anchoring agents; retail scale                          |

**4.6.4.4  Behavioral Properties**

- Time horizon: Medium — reference point is static (cost basis); unchanged until next trade
- Risk tolerance: Asymmetric — risk-averse for gains (quick selling), risk-seeking for losses (holding)
- Information asymmetry: None about fundamentals; unique private reference (cost basis)
- Psychological profile: Prospect Theory (Kahneman & Tversky 1979); Disposition Effect (Shefrin & Statman 1985); Mental Accounting (Thaler 1985)

#### 4.6.5  Decision Process Walkthrough

```
Given:  price = 108.0,  cost_basis = 103.5,  gain_threshold = 0.04,  loss_aversion_mult = 2.5

Step 1: Compute gain percentage
        gain_pct = (108.0 − 103.5) / 103.5 = +0.0435

Step 2: Compare to thresholds
        +0.0435 > +0.04 → sell condition satisfied (profit-taking)

Step 3: Compute quantity
        Q* = min(15.0, 0.0435 × 500) = min(15.0, 21.7) = 15 shares (capped)

Result: action = sell, quantity = 15, bid_price = 108.0
Rationale: Price 4.35% above cost basis triggers disposition-effect profit-taking.
This selling adds downward pressure during the anchoring overvaluation phase.
```

#### 4.6.6  Worked Numerical Example

```
Market state:  price = 97.0,  cost_basis = 105.0,  position = 100 shares

Calculation:
  gain_pct = (97.0 − 105.0) / 105.0 = −0.0762  (7.6% loss)
  Compare: −0.0762 < −0.016 → buy condition (averaging down)
  Q* = min(15.0, 0.0762 × 500) = min(15.0, 38.1) = 15 shares (capped)
  Cash check: 15 × 97.0 = $1,455 (sufficient from initial $10,000)

Decision: action = buy, quantity = 15, bid_price = 97.0
Update: cost_basis = (105.0 × 100 + 97.0 × 15) / 115 = 103.96

Rationale: Despite price being 3% below fundamental (100), DispositionTrader buys because it
perceives a loss relative to cost basis and "averages down" — the classic disposition-effect
behaviour of reinforcing losing positions. This buying adds upward price support at levels
where rational agents would hold or sell.
```

#### 4.6.7  Academic References

| # | Citation                                                                                                                                                                                         | Notes                                                                                     |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 1 | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x  | Core theoretical foundation; establishes gain/loss asymmetry in individual investors      |
| 2 | Kahneman, D., & Tversky, A. (1979). Prospect theory. *Econometrica*, 47(2), 263–292. https://doi.org/10.2307/1914185                                                                             | Grounds the disposition effect in value function asymmetry; calibrates λ ≈ 2.25           |
| 3 | Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775–1798. https://doi.org/10.1111/0022-1082.00072                                               | Empirical confirmation: gains realised 1.68× more frequently than losses; large brokerage |
| 4 | Weber, M., & Camerer, C. F. (1998). The disposition effect in securities trading. *Journal of Economic Behavior and Organization*, 33(2), 167–184. https://doi.org/10.1016/S0167-2681(97)00089-9 | Controlled experiment confirming disposition effect magnitude                             |

---

### §4.7 ContrarianTrader

#### 4.7.1  Summary

ContrarianTrader represents the disciplined mean-reversion investor who bets against recent trends without reference to fundamental value. Unlike RationalUpdater (who exploits the price-fundamental gap), ContrarianTrader uses purely statistical reasoning: when cumulative 10-round returns exceed ±5%, it trades in the opposite direction expecting mean reversion. This agent models the empirically documented overreaction-correction cycle (De Bondt & Thaler, 1985) and provides a correction mechanism distinct from fundamental arbitrage — one that would operate even if F were unknown.

#### 4.7.2  Theoretical and Empirical Foundation

**Market Overreaction and Contrarian Profits**:
- Theory / Study: Long-Run Stock Market Overreaction
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Stocks that have performed extremely well ("winners") over 3–5 years subsequently underperform, while extreme "losers" subsequently outperform. This reversal pattern is consistent with investors overreacting to recent information and prices eventually mean-reverting. Contrarian strategies exploit this predictable overreaction.
- Mathematical Formulation:
  ```
  cumulative_return(t) = (P(t) − P(t−lookback)) / P(t−lookback)
  Sell if cumulative_return > +entry_threshold (+5%)
  Buy  if cumulative_return < −entry_threshold (−5%)
  ```
- Empirical Evidence: De Bondt & Thaler (1985) document 25% cumulative excess return to contrarian portfolios over 3 years; Jegadeesh (1990, *Journal of Finance*) confirms short-horizon reversals at 1-month intervals; Bondt (1993) and Chopra, Lakonishok & Ritter (1992) extend to multiple horizons.
- Relevance to This Investor: In the AnchoringEffect simulation, anchoring agents create a slow upward drift followed by correction. ContrarianTrader detects the cumulative upward drift and sells against it, providing an additional correction force beyond RationalUpdater. During the correction phase, it may buy the dip, partially cushioning the decline.

**Short-Horizon Mean Reversion**:
- Theory / Study: Evidence of Predictable Behavior of Security Returns
- Citation: Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881–898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
- Core Insight: At short horizons (1–4 weeks), stock returns exhibit negative serial correlation — reversals rather than momentum. This justifies a 10-round contrarian lookback window as the simulation-compressed equivalent of a 2-week reversal horizon.
- Relevance to This Investor: The `lookback_window = 10` parameter maps to Jegadeesh's documented short-horizon reversal window.

#### 4.7.3  Design Purpose and Activation Scenarios

Purpose: Provide a correction mechanism that is distinct from RationalUpdater. ContrarianTrader does not know or use the fundamental value — it trades on pure price-path statistics. This tests whether price corrections in the simulation require fundamental knowledge or can emerge from statistical mean-reversion beliefs alone.

Activation Scenarios:
- 10-round cumulative return > +5%: Sells (expects reversal from overextension).
- 10-round cumulative return < −5%: Buys (expects bounce from oversold condition).
- Within ±5%: Holds — insufficient trend to trigger contrarian response.

Market Contribution: **Stabilizing** — provides correction force distinct from fundamental arbitrage; dampens both upward overextension and downward overshooting.

Interaction with other agents: Opposes MomentumTrader directly (when momentum signal is strong, contrarian signal fires in opposite direction); complements RationalUpdater during correction phase (both sell into overvaluation, but for different reasons); may temporarily oppose RationalUpdater during rapid corrections (ContrarianTrader buys the dip while RationalUpdater holds).

#### 4.7.4  Behavioral Framework

**4.7.4.1  Decision Information Set**

| Signal                           | Type       | Rationale                                               |
|----------------------------------|------------|---------------------------------------------------------|
| `price`                          | Continuous | Current price; end-point of lookback return calculation |
| `price_history` (last 10 rounds) | Series     | Required for cumulative return over lookback window     |

Does NOT use: `fundamental`, `deviation`. ContrarianTrader ignores fundamental value entirely — its signal is purely statistical (price-path based).

**4.7.4.2  Core Behavioral Mechanism**

1. Maintains a rolling list of recent prices (up to `lookback_window = 10` rounds).
2. Each round: computes `cum_return = (price − price_10_rounds_ago) / price_10_rounds_ago`.
3. If `cum_return > entry_threshold (+0.05)`: sells — expects mean reversion from upward overextension.
4. If `cum_return < −entry_threshold (−0.05)`: buys — expects bounce from oversold.
5. Otherwise: holds.

**4.7.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  P_ref = price_history[max(0, t − lookback_window)]
  cum_return(t) = (P(t) − P_ref) / P_ref
  Sell: cum_return(t) > +0.05
  Buy:  cum_return(t) < −0.05
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(cum_return(t)) × 400)
  Bounded by cash (buy) or position (sell)
  ```
- State variables: `price_history` — rolling list of last 10 prices
- Parameter definitions:

| Symbol                    | Meaning                                               | Config Path                    | Source                                                         |
|---------------------------|-------------------------------------------------------|--------------------------------|----------------------------------------------------------------|
| lookback_window = 10      | Number of rounds for cumulative return                | players.yml → ContrarianTrader | Jegadeesh (1990): short-horizon reversal at 1–4 week intervals |
| entry_threshold = 0.05    | Minimum cumulative return to trigger contrarian trade | players.yml → ContrarianTrader | De Bondt & Thaler (1985): ~5% overreaction threshold           |
| base_position_size = 20.0 | Maximum trade size                                    | players.yml → ContrarianTrader | Standardised                                                   |

**4.7.4.4  Behavioral Properties**

- Time horizon: Short-to-medium (10-round lookback; ~2 weeks compressed)
- Risk tolerance: Medium — 5% threshold provides buffer against false signals
- Information asymmetry: None about fundamentals; uses only public price history
- Psychological profile: Statistical mean-reversion belief; contrarian temperament; De Bondt & Thaler (1985) overreaction hypothesis

#### 4.7.5  Decision Process Walkthrough

```
Given:  price = 107.5,  price_10_rounds_ago = 102.0,  entry_threshold = 0.05

Step 1: Compute cumulative return
        cum_return = (107.5 − 102.0) / 102.0 = +0.0539

Step 2: Compare to threshold
        +0.0539 > +0.05 → sell condition (contrarian reversal bet)

Step 3: Compute quantity
        Q* = min(20.0, 0.0539 × 400) = min(20.0, 21.6) = 20 shares (capped)

Result: action = sell, quantity = 20, bid_price = 107.5
Rationale: Cumulative 10-round return exceeded +5%; ContrarianTrader bets on mean reversion.
This sells into the anchoring-driven overvaluation, adding corrective pressure from a
purely statistical (non-fundamental) perspective.
```

#### 4.7.6  Worked Numerical Example

```
Market state:  price = 96.5,  price_10_rounds_ago = 103.0

Calculation:
  cum_return = (96.5 − 103.0) / 103.0 = −0.0631  (6.3% decline over 10 rounds)
  −0.0631 < −0.05 → buy condition (contrarian buy-the-dip)
  Q* = min(20.0, 0.0631 × 400) = min(20.0, 25.2) = 20 shares (capped)

Decision: action = buy, quantity = 20, bid_price = 96.5
Rationale: 10-round cumulative return is −6.3%, exceeding the 5% reversal threshold.
ContrarianTrader bets that the decline is an overreaction and prices will bounce.
Note: unlike RationalUpdater who buys because price < F, ContrarianTrader buys purely
because the decline is "too large" statistically — a fundamentally different information set.
```

#### 4.7.7  Academic References

| # | Citation                                                                                                                                                                           | Notes                                                        |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| 1 | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x              | Core foundation; documents 25% reversal profits over 3 years |
| 2 | Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881–898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x               | Short-horizon reversals; calibrates lookback_window = 10     |
| 3 | Chopra, N., Lakonishok, J., & Ritter, J. R. (1992). Measuring abnormal performance. *Journal of Financial Economics*, 31(2), 235–268. https://doi.org/10.1016/0304-405X(92)90005-I | Cross-validates overreaction effects across market caps      |

---

### §4.8 FundamentalAnalyst

#### 4.8.1  Summary

FundamentalAnalyst represents the institutional investor who knows the true fundamental value exists but incorporates it only gradually — modelling the conservatism bias documented by Barberis, Shleifer & Vishny (1998). Unlike RationalUpdater (who uses F directly with no delay), FundamentalAnalyst maintains a `belief` that exponentially smooths toward F at rate λ_b = 0.05 per round. This means it takes approximately 40–60 rounds for FundamentalAnalyst's belief to converge within 90% of the true fundamental. The result is a gradually strengthening correction force that is weak early in the simulation (when anchoring dominates) but increasingly effective in later rounds — modelling how institutional research slowly incorporates new information.

#### 4.8.2  Theoretical and Empirical Foundation

**Conservatism Bias and Slow Belief Updating**:
- Theory / Study: Conservatism and Underreaction in Investor Beliefs
- Citation: Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: Investors update beliefs too slowly in response to new information (conservatism), especially when the information is statistical or abstract. This leads to systematic underreaction to earnings surprises and slow price adjustment. The BSV model shows that conservatism causes prices to initially underreact, then drift as information gradually incorporates — matching the post-earnings announcement drift anomaly.
- Mathematical Formulation:
  ```
  belief(t) = (1 − λ_b) × belief(t−1) + λ_b × F
  where λ_b = 0.05 (learning rate); belief(0) = initial_price = 105.0
  Convergence: belief approaches F exponentially with half-life = −ln(2)/ln(1−λ_b) ≈ 13.5 rounds
  90% convergence: ≈ 45 rounds (well within 200-round simulation)
  ```
- Empirical Evidence: Bernard & Thomas (1989, *Journal of Accounting and Economics*) document post-earnings announcement drift lasting 60–90 trading days; Barberis, Shleifer & Vishny (1998) attribute this to conservative belief updating with effective λ_b ≈ 0.03–0.08.
- Relevance to This Investor: FundamentalAnalyst's λ_b = 0.05 means its belief converges from 105 toward 100 over approximately 45 rounds — matching the documented speed of institutional information incorporation. Early on, it is nearly as "anchored" as AnchoredTrader; late in the simulation, it is nearly as rational as RationalUpdater.

**Institutional Investor Conservatism**:
- Theory / Study: Limits to Arbitrage and Gradual Information Processing
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even when institutional investors recognise mispricing, they adjust portfolios gradually due to career concerns, benchmark tracking, and risk limits. This creates "limits to arbitrage" where correct fundamental information is priced in slowly rather than instantaneously.
- Relevance to This Investor: FundamentalAnalyst's gradual belief convergence models these institutional constraints — even though F is known, the agent cannot instantly move to full fundamental trading.

#### 4.8.3  Design Purpose and Activation Scenarios

Purpose: FundamentalAnalyst fills the gap between AnchoredTrader (permanently biased) and RationalUpdater (instantly rational). It models the realistic middle ground: an investor who is correct eventually but slow to arrive. This creates a richer phase structure — early rounds are dominated by anchoring, middle rounds see FundamentalAnalyst gradually joining RationalUpdater in correcting, and late rounds show strong convergence pressure.

Activation Scenarios:
- Price above belief by > 2%: Sells — interprets price as overvalued relative to gradually-learned fair value.
- Price below belief by > 2%: Buys — interprets price as undervalued relative to belief.
- Within ±2% of belief: Holds.

Market Contribution: **Weakly stabilizing → increasingly stabilizing** — correction force strengthens over time as belief converges to F. Creates a natural bridge between the persistence phase and correction phase of the anchoring lifecycle.

Interaction with other agents: In early rounds, may align with AnchoredTrader (both have elevated beliefs); in later rounds, aligns with RationalUpdater (both drive price toward F); provides a gradual transition between bias and rationality that smooths the correction path.

#### 4.8.4  Behavioral Framework

**4.8.4.1  Decision Information Set**

| Signal        | Type             | Rationale                                                                         |
|---------------|------------------|-----------------------------------------------------------------------------------|
| `price`       | Continuous       | Current market price; compared to evolving belief                                 |
| `fundamental` | Continuous       | True F; used for belief update each round                                         |
| `belief`      | Persistent state | Exponentially-smoothed estimate of fair value; starts at initial_price, converges |

**4.8.4.2  Core Behavioral Mechanism**

1. Initialises `belief = initial_price = 105.0` (starts biased, like AnchoredTrader).
2. Each round: updates belief: `belief = (1 − learning_rate) × belief + learning_rate × fundamental`.
3. Computes `dev_from_belief = (price − belief) / belief`.
4. If `dev_from_belief > +0.02`: sells (price above what FA believes is fair).
5. If `dev_from_belief < −0.02`: buys (price below FA's fair value belief).
6. Otherwise: holds.

**4.8.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Belief evolution:
  ```
  belief(t) = 0.95 × belief(t−1) + 0.05 × F
  belief(0) = 105.0; belief(∞) → 100.0
  Half-life of belief convergence: ln(2)/ln(1/0.95) ≈ 13.5 rounds
  ```
- Trigger function:
  ```
  dev(t) = (P(t) − belief(t)) / belief(t)
  Sell: dev(t) > +0.02
  Buy:  dev(t) < −0.02
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(dev(t)) × 1000)
  Bounded by cash (buy) or position (sell)
  ```
- Parameter definitions:

| Symbol                    | Meaning                                  | Config Path                      | Source                                                                    |
|---------------------------|------------------------------------------|----------------------------------|---------------------------------------------------------------------------|
| learning_rate = 0.05      | Exponential smoothing rate toward F      | players.yml → FundamentalAnalyst | Barberis et al. (1998): institutional learning over ~45 rounds (≈60 days) |
| base_position_size = 25.0 | Maximum trade size (institutional scale) | players.yml → FundamentalAnalyst | Slightly larger than retail agents                                        |

**4.8.4.4  Behavioral Properties**

- Time horizon: Long — belief evolves slowly; full convergence in ~45 rounds
- Risk tolerance: Medium — 2% threshold; institutional-scale position limits
- Information asymmetry: Has access to F but processes it with conservatism (slow incorporation)
- Psychological profile: Conservatism bias (Barberis et al. 1998); limits to arbitrage (Shleifer & Vishny 1997); institutional inertia

#### 4.8.5  Decision Process Walkthrough

```
Given:  round = 30,  price = 102.0,  fundamental = 100.0
        belief(29) = 102.8 (has partially converged from 105.0)

Step 1: Update belief
        belief(30) = 0.95 × 102.8 + 0.05 × 100.0 = 97.66 + 5.0 = 102.66

Step 2: Compute deviation from belief
        dev = (102.0 − 102.66) / 102.66 = −0.0064

Step 3: Compare to threshold
        |−0.0064| < 0.02 → below threshold; HOLD

Result: Despite price being 2% above true fundamental, FundamentalAnalyst holds because
        its belief (102.66) is still elevated — it has not yet fully learned that F = 100.
        By round 60, belief ≈ 100.25, and the same price would trigger selling.
```

#### 4.8.6  Worked Numerical Example

```
Market state:  round = 60,  price = 103.0,  fundamental = 100.0
               belief(59) = 100.75 (nearly converged after 60 rounds)

Calculation:
  belief(60) = 0.95 × 100.75 + 0.05 × 100.0 = 95.71 + 5.0 = 100.71
  dev = (103.0 − 100.71) / 100.71 = +0.0227  (>+0.02 → sell)
  Q* = min(25.0, 0.0227 × 1000) = min(25.0, 22.7) = 22 shares

Decision: action = sell, quantity = 22, bid_price = 103.0
Rationale: After 60 rounds of exponential smoothing, FundamentalAnalyst's belief has nearly
converged to F = 100. It now detects that price = 103 is 2.3% above its fair value estimate
and sells — adding correction pressure that was absent in early rounds. This demonstrates
the time-varying stabilization force that distinguishes FA from RationalUpdater.
```

#### 4.8.7  Academic References

| # | Citation                                                                                                                                                                        | Notes                                                                                |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| 1 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Core foundation; conservatism → slow belief updating → post-announcement drift       |
| 2 | Bernard, V. L., & Thomas, J. K. (1989). Post-earnings-announcement drift. *Journal of Accounting and Economics*, 11(1), 1–36. https://doi.org/10.1016/0165-4101(89)90013-8      | Empirical: drift lasts 60–90 days; calibrates λ_b ≈ 0.05                             |
| 3 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                           | Institutional constraints explaining why convergence is slow despite correct beliefs |

---

### §4.9 LiquidityProvider

#### 4.9.1  Summary

LiquidityProvider represents the passive market-maker or algorithmic liquidity provider that quotes around a short-term exponential moving average (EMA), supplying two-sided liquidity without any fundamental view. It buys when price dips below its fair quote minus a half-spread, and sells when price rises above fair quote plus half-spread. This agent smooths price volatility, dampens short-term oscillations, and provides the continuous liquidity that allows other agents' strategies to execute without excessive slippage. In the anchoring lifecycle, LiquidityProvider dampens noise-driven spikes while having no systematic effect on the direction of mispricing.

#### 4.9.2  Theoretical and Empirical Foundation

**Market Making and Bid-Ask Dynamics**:
- Theory / Study: Bid-Ask Spread and Market Making
- Citation: Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3
- Core Insight: Market makers quote bid and ask prices around their expectation of fair value, earning the spread as compensation for adverse selection risk. The spread widens when information asymmetry increases. In this simulation, LiquidityProvider uses an EMA as its fair-value estimate (agnostic to true fundamental) and quotes with a fixed half-spread.
- Mathematical Formulation:
  ```
  ema(t) = α_ema × P(t) + (1 − α_ema) × ema(t−1),  α_ema = 2 / (ema_window + 1)
  fair_quote(t) = 0.5 × (P(t) + ema(t))
  Buy:  P(t) < fair_quote(t) − half_spread × fair_quote(t)
  Sell: P(t) > fair_quote(t) + half_spread × fair_quote(t)
  ```
- Empirical Evidence: Huang & Stoll (1997, *Review of Financial Studies*) estimate effective half-spreads of 0.5–2% for actively traded stocks. Comerton-Forde et al. (2010, *Journal of Financial Economics*) document that algorithmic market makers reduce intraday volatility by 15–25% through liquidity provision.
- Relevance to This Investor: LiquidityProvider with `half_spread = 0.015` (1.5%) provides realistic two-sided quoting that dampens NoiseTrader-driven price spikes and smooths the anchoring-driven drift path without directionally biasing the market.

**Volatility Dampening and Price Stabilization**:
- Theory / Study: Algorithmic Market Making and Volatility
- Citation: Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011). Does algorithmic trading improve liquidity? *Journal of Finance*, 66(1), 1–33. https://doi.org/10.1111/j.1540-6261.2010.01624.x
- Core Insight: Algorithmic liquidity providers narrow spreads and reduce short-term volatility by providing continuous two-sided liquidity. They do not speculate on direction — they profit from the spread between buy and sell executions.
- Relevance to This Investor: LiquidityProvider absorbs NoiseTrader shocks and MomentumTrader-driven spikes, reducing rolling volatility without altering the fundamental correction process.

#### 4.9.3  Design Purpose and Activation Scenarios

Purpose: Provide realistic two-sided liquidity that smooths the price path; model the institutional/algorithmic market-making layer that exists in all modern equity markets; prevent NoiseTrader large orders from creating unrealistically large price dislocations.

Activation Scenarios:
- Price below fair_quote − 1.5% spread: Buys (provides bid-side liquidity).
- Price above fair_quote + 1.5% spread: Sells (provides ask-side liquidity).
- Within ±1.5% spread of fair_quote: Holds (no profit opportunity within spread).

Market Contribution: **Neutral/stabilizing** — reduces price volatility; does not systematically correct toward F (agnostic to fundamental); absorbs demand shocks.

Interaction with other agents: Absorbs NoiseTrader random orders (dampens their price impact); partially offsets MomentumTrader trend-following (provides counter-side liquidity); does not interact with anchoring mechanism directly (no fundamental view).

#### 4.9.4  Behavioral Framework

**4.9.4.1  Decision Information Set**

| Signal  | Type             | Rationale                                                   |
|---------|------------------|-------------------------------------------------------------|
| `price` | Continuous       | Current market price; compared to fair_quote                |
| `ema`   | Persistent state | 20-round exponential moving average; basis for fair quoting |

Does NOT use: `fundamental`, `deviation`. LiquidityProvider is fundamentals-agnostic — it quotes around recent price average, not intrinsic value.

**4.9.4.2  Core Behavioral Mechanism**

1. Maintains `ema` with decay factor `α = 2 / (ema_window + 1) = 2/21 ≈ 0.095`.
2. Each round: updates `ema = α × price + (1 − α) × ema`.
3. Computes `fair_quote = 0.5 × (price + ema)` (midpoint of current and smoothed).
4. Computes `spread_band = half_spread × fair_quote`.
5. If `price < fair_quote − spread_band`: buys (price is below bid threshold).
6. If `price > fair_quote + spread_band`: sells (price is above ask threshold).
7. Otherwise: holds (price within no-trade spread zone).

**4.9.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- EMA evolution:
  ```
  α = 2 / (20 + 1) = 0.0952
  ema(t) = α × P(t) + (1 − α) × ema(t−1)
  ema(0) = initial_price = 105.0
  ```
- Trigger function:
  ```
  fair_quote(t) = 0.5 × (P(t) + ema(t))
  band(t) = half_spread × fair_quote(t) = 0.015 × fair_quote(t)
  Buy:  P(t) < fair_quote(t) − band(t)
  Sell: P(t) > fair_quote(t) + band(t)
  ```
- Sizing function:
  ```
  deviation_from_band = abs(P(t) − fair_quote(t)) / fair_quote(t)
  Q*(t) = min(base_position_size, deviation_from_band × 2000)
  Bounded by cash (buy) or position (sell)
  ```
- Parameter definitions:

| Symbol                    | Meaning                                  | Config Path                     | Source                                                                |
|---------------------------|------------------------------------------|---------------------------------|-----------------------------------------------------------------------|
| ema_window = 20           | EMA lookback window                      | players.yml → LiquidityProvider | Hendershott et al. (2011): algorithmic MM update window ~20 intervals |
| half_spread = 0.015       | Half-spread as fraction of fair quote    | players.yml → LiquidityProvider | Huang & Stoll (1997): 0.5–2% effective half-spread for mid-caps       |
| base_position_size = 30.0 | Maximum trade size (high liquidity role) | players.yml → LiquidityProvider | Larger than other agents; reflects MM capital commitment              |

**4.9.4.4  Behavioral Properties**

- Time horizon: Very short — responds to current price vs. EMA; no long-term view
- Risk tolerance: Low directional risk — earns spread, not directional gains; large position capacity
- Information asymmetry: None — uses only public price data; fundamentals-agnostic
- Psychological profile: No cognitive bias — pure mechanical market-making; models the algorithmic/institutional liquidity layer

#### 4.9.5  Decision Process Walkthrough

```
Given:  price = 102.0,  ema(prev) = 103.5,  half_spread = 0.015

Step 1: Update EMA
        α = 0.0952
        ema = 0.0952 × 102.0 + 0.9048 × 103.5 = 9.71 + 93.65 = 103.36

Step 2: Compute fair quote
        fair_quote = 0.5 × (102.0 + 103.36) = 102.68

Step 3: Compute spread band
        band = 0.015 × 102.68 = 1.54

Step 4: Compare
        lower = 102.68 − 1.54 = 101.14
        upper = 102.68 + 1.54 = 104.22
        price = 102.0 → within band [101.14, 104.22]; HOLD

Result: Price is within the no-trade spread zone. LiquidityProvider does not trade.
```

#### 4.9.6  Worked Numerical Example

```
Market state:  price = 99.0 (sharp drop from NoiseTrader sell),  ema = 103.2

Calculation:
  ema_new = 0.0952 × 99.0 + 0.9048 × 103.2 = 9.42 + 93.38 = 102.80
  fair_quote = 0.5 × (99.0 + 102.80) = 100.90
  band = 0.015 × 100.90 = 1.51
  lower = 100.90 − 1.51 = 99.39
  price = 99.0 < 99.39 → buy condition (price below bid threshold)
  deviation = abs(99.0 − 100.90) / 100.90 = 0.0188
  Q* = min(30.0, 0.0188 × 2000) = min(30.0, 37.6) = 30 shares (capped)

Decision: action = buy, quantity = 30, bid_price = 99.0
Rationale: A NoiseTrader sell pushed price below LiquidityProvider's bid threshold.
LP buys 30 shares, absorbing the shock and dampening the drop. This is the
classic liquidity-provision role — buying into short-term dislocations.
```

#### 4.9.7  Academic References

| # | Citation                                                                                                                                                                                 | Notes                                                                           |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3                  | Core market-making theory; spread as adverse selection compensation             |
| 2 | Huang, R. D., & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995–1034. https://doi.org/10.1093/rfs/10.4.995                          | Calibrates half_spread = 0.015 from empirical spread decomposition              |
| 3 | Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011). Does algorithmic trading improve liquidity? *Journal of Finance*, 66(1), 1–33. https://doi.org/10.1111/j.1540-6261.2010.01624.x | Algorithmic MMs reduce volatility 15–25%; motivates LiquidityProvider dampening |


## §5 Agent Diversity Verification

```
Diversity Check:
  Different time horizons:
    - Instantaneous: MomentumTrader (1-round return), NoiseTrader (random each round)
    - Short-term: ContrarianTrader (10-round cumulative return), LiquidityProvider (EMA-based)
    - Medium-term: AnchoredTrader (permanent first-price anchor), DispositionTrader (cost-basis reference)
    - Long-term: HistoricalAnchor (60-round rolling average), FundamentalAnalyst (exponential belief convergence)
    - Fundamental-instant: RationalUpdater (immediate deviation from F)

  Different information sets:
    - First-price anchor: AnchoredTrader (anchor + fundamental; biased update)
    - Historical average: HistoricalAnchor (rolling 60-round average; ignores fundamental)
    - True fundamental: RationalUpdater (pure deviation from F)
    - Gradual fundamental: FundamentalAnalyst (exponentially-smoothed belief toward F)
    - Price momentum: MomentumTrader (prev_price vs. current price only)
    - Cumulative returns: ContrarianTrader (10-round return; no fundamental)
    - Purchase price: DispositionTrader (cost basis; no fundamental or market signal)
    - Short-term EMA: LiquidityProvider (20-round EMA; fundamentals-agnostic)
    - None: NoiseTrader (random; no systematic information)

  Conflicting incentives:
    - AnchoredTrader buys at 98–104 (biased buying zone) → RationalUpdater sells above 102 (corrective)
    - HistoricalAnchor buys below rolling average → may buy even below fundamental
    - MomentumTrader amplifies trends in both directions → neutral aggregate effect
    - ContrarianTrader opposes MomentumTrader directly (sells when cum_ret > 5%)
    - DispositionTrader sells winners (above cost basis) ↔ AnchoredTrader may still be buying
    - FundamentalAnalyst initially aligned with AnchoredTrader (belief ≈ 105), later aligned with RationalUpdater
    - LiquidityProvider absorbs NoiseTrader shocks without directional bias

  Mix of stabilising/destabilising:
    - Destabilising (×2 types × 2 each = 4 agents): AnchoredTrader, HistoricalAnchor
    - Asymmetrically destabilising (×1 type × 2 = 2 agents): DispositionTrader
    - Stabilising-instant (×1 type × 1 = 1 agent): RationalUpdater
    - Stabilising-gradual (×1 type × 1 = 1 agent): FundamentalAnalyst
    - Stabilising-statistical (×1 type × 1 = 1 agent): ContrarianTrader
    - Neutral-amplifying (×1 type × 2 = 2 agents): MomentumTrader
    - Neutral-liquidity (×1 type × 1 = 1 agent): LiquidityProvider
    - Neutral-noise (×1 type × 2 = 2 agents): NoiseTrader
    Total: 14 investor agents plus 1 market coordinator = 15 players

  Different risk tolerances:
    - High: MomentumTrader (trades on 2% price change), NoiseTrader (random large orders)
    - Medium: AnchoredTrader (3% biased threshold), HistoricalAnchor (3% dampened threshold),
             RationalUpdater (2% true threshold), FundamentalAnalyst (2% from belief),
             ContrarianTrader (5% cumulative return)
    - Asymmetric: DispositionTrader (4% gain / 1.6% loss asymmetry)
    - Low directional: LiquidityProvider (1.5% spread; large position capacity)
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
| `gain_threshold`     | 0.04     | Odean (1998): median gain-realisation at 4–8%                                   | Disposition sell trigger (DispositionTrader)          | Medium — lower value increases profit-taking frequency                                            |
| `loss_aversion_mult` | 2.5      | Kahneman & Tversky (1979): λ ≈ 2.25                                             | Asymmetry between gain/loss thresholds                | **High** — controls disposition asymmetry; 1.0 = symmetric agent                                  |
| `lookback_window`    | 10       | Jegadeesh (1990): short-horizon reversal window                                 | Contrarian cumulative-return window                   | Medium — shorter = more frequent trading                                                          |
| `ct_entry_threshold` | 0.05     | De Bondt & Thaler (1985): 5% overreaction threshold                             | Contrarian trigger level (ContrarianTrader)           | Medium                                                                                            |
| `learning_rate`      | 0.05     | Barberis et al. (1998): institutional learning speed                            | Belief convergence rate (FundamentalAnalyst)          | **High** — controls how fast FA joins RU as correction force                                      |
| `ema_window`         | 20       | Hendershott et al. (2011): algorithmic MM update interval                       | EMA lookback for fair quote (LiquidityProvider)       | Low                                                                                               |
| `half_spread`        | 0.015    | Huang & Stoll (1997): effective half-spread 0.5–2%                              | LiquidityProvider quoting half-spread                 | Medium — tighter spread = more active LP                                                          |


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

Topology: Star — Market at centre broadcasts to all 14 investors; investors send orders back to Market.

Initialization: Market starts at `initial_price = 105.0` (5% above fundamental 100.0). AnchoredTrader records this as its permanent anchor on round 1; DispositionTrader records its cost basis; FundamentalAnalyst initialises belief to 105.0; LiquidityProvider initialises EMA to 105.0. These initialise the mispricing that the simulation then studies.


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
  - 200-round full experiment represents the post-IPO adjustment period with enough tail rounds to observe slow convergence
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


## §10 Equilibrium Analysis

This section derives the theoretical steady-state price P* given the 9 agent demand functions and the price formation model, showing why anchoring agents create a biased equilibrium above fundamental value.

### 10.1 Price Formation Recap

```
P(t+1) = P(t) + λ×D(t) + γ×[F − P(t)] + ε(t)
```

where D(t) = Σ_i demand_i(t) is aggregate net demand, λ = 0.4 (price impact), γ = 0.01 (mean-reversion), F = 100, ε ~ N(0, σ²).

### 10.2 Agent Demand Functions (Linearised)

At steady state, we set E[P(t+1)] = P(t) = P* and E[ε] = 0:

| Agent                   | Demand Function (simplified)                     | Demand at P = P*                  |
|-------------------------|--------------------------------------------------|-----------------------------------|
| AnchoredTrader (AT)     | d_AT = k_AT × (perceived_target − P)             | k_AT × [(1−α)(anchor−F) + F − P*] |
| HistoricalAnchor (HA)   | d_HA = k_HA × (price_avg − P)                    | k_HA × (P* − P*) = 0 at true SS   |
| RationalUpdater (RU)    | d_RU = k_RU × (F − P)                            | k_RU × (F − P*)                   |
| MomentumTrader (MT)     | d_MT = k_MT × (P − P_lag) → 0 at SS              | 0                                 |
| NoiseTrader (NT)        | d_NT ~ N(0, σ_NT²) → E[d_NT] = 0                 | 0                                 |
| DispositionTrader (DT)  | d_DT depends on gain/loss relative to cost basis | Approximately 0 at long-run SS    |
| ContrarianTrader (CT)   | d_CT = k_CT × (F − P) (similar to RU, lagged)    | k_CT × (F − P*)                   |
| FundamentalAnalyst (FA) | d_FA = k_FA × (belief − P); belief → F slowly    | k_FA × (F − P*) at long-run SS    |
| LiquidityProvider (LP)  | d_LP ≈ 0 (two-sided quoting, net neutral)        | 0                                 |

### 10.3 Steady-State Derivation

At equilibrium: P(t+1) = P(t) = P*, so:

```
0 = λ×D* + γ×(F − P*)
```

Substituting demand functions (retaining only non-zero terms at SS):

```
D* = n_AT × k_AT × [(1−α)(anchor−F) + (F−P*)] + (n_RU×k_RU + n_CT×k_CT + n_FA×k_FA) × (F−P*)
```

Let K_bias = n_AT × k_AT and K_corr = n_RU×k_RU + n_CT×k_CT + n_FA×k_FA + n_AT×k_AT:

```
0 = λ × [K_bias × (1−α)(anchor−F) − K_corr × (P*−F)] + γ × (F−P*)
```

Solving for P*:

```
P* = F + [λ × K_bias × (1−α) × (anchor−F)] / [λ × K_corr + γ]
```

### 10.4 Key Insights

1. **Biased equilibrium**: Since anchor > F and α < 1, the numerator is positive, so P* > F. The market equilibrium is permanently biased above fundamental value when anchoring agents are present.

2. **Magnitude**: With baseline parameters (anchor = 105, F = 100, α = 0.3, n_AT = 2):
   ```
   Bias = P* − F ∝ (1−0.3) × 5 = 3.5 (normalised by corrective capacity)
   ```
   Depending on K_corr and γ, the equilibrium bias is approximately 1–3% above F.

3. **Correction speed**: The eigenvalue governing convergence toward P* is:
   ```
   λ_conv = 1 − λ×K_corr − γ ≈ 1 − 0.01 − 0.01 = 0.98
   ```
   Half-life ≈ −ln(2)/ln(λ_conv) ≈ 35 rounds (consistent with calibration target [20, 60]).

4. **Parameter sensitivity**:
   - Increasing γ reduces P* toward F (mechanical mean-reversion dominates)
   - Increasing n_RU/K_corr reduces the bias (more corrective capacity)
   - Decreasing α increases the bias (stronger anchoring)
   - HistoricalAnchor contributes zero demand at true SS but *delays* convergence by temporarily supporting prices during the transient

### 10.5 Dynamic Convergence Path

Starting from P(0) = 105 toward P* ≈ 101–103:

```
P(t) ≈ P* + (P(0) − P*) × λ_conv^t
```

The system approaches P* exponentially with half-life ≈ 35 rounds. Then P* itself slowly converges toward F as HistoricalAnchor’s rolling average updates (its anchor drifts toward F over its 60-round window), reducing the effective bias term.

This two-phase convergence (fast approach to biased SS, then slow drift of SS toward F) explains why the simulation shows:
- Phase 2 (Persistence): Price near P* > F
- Phase 3 (Slow Correction): P* itself migrating toward F
- Phase 4 (Convergence): P* ≈ F after HistoricalAnchor’s window fully updates


## §11 Limitations and Assumptions

This section explicitly acknowledges simplifying assumptions, model boundaries, and what the simulation cannot study.

### 11.1 Simplifying Assumptions

| Assumption                             | Justification                                                                        | Consequence if Violated                                                        |
|----------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Constant fundamental value F = 100     | Isolates anchoring effect from fundamental uncertainty; all deviation is bias-driven | Cannot study anchoring under fundamental drift or mean-reverting F             |
| No derivatives or leverage             | Keeps agent dynamics tractable; avoids amplification through margin calls            | Underestimates real-world correction speed (leveraged arb is faster)           |
| No credit or bankruptcy constraints    | Agents can always trade; no forced liquidation                                       | Removes forced-selling cascades that accelerate real-world corrections         |
| Single venue, single asset             | Focuses on pure anchoring dynamics without cross-market arbitrage                    | Cannot study fragmentation, dark pools, or multi-asset contagion               |
| No transaction costs or bid-ask spread | Simplifies analysis; all price impact is via λ-term                                  | Overestimates trading frequency; real agents would trade less often            |
| Synchronous decision-making            | All agents decide simultaneously per round; no priority or speed advantage           | Cannot study high-frequency effects or latency arbitrage                       |
| No information asymmetry               | F is known to all agents; anchoring is cognitive, not informational                  | Clean attribution: all mispricing is bias-driven, not adverse-selection-driven |

### 11.2 Agent Limitations

| Limitation                          | Description                                                                          | Real-World Difference                                           |
|-------------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| No learning or strategy adaptation  | Agent parameters (α, anchor_weight, lookback_period) are fixed throughout simulation | Real agents update beliefs and may de-bias over time            |
| No strategic interaction            | Agents do not model other agents’ behaviour; no game-theoretic considerations        | Real markets have strategic interdependence (market makers)     |
| No memory update for AnchoredTrader | The anchor is permanently set on round 1; never updates to reflect new information   | Real anchoring may fade as anchors become stale                 |
| Homogeneous parameters within type  | All instances of a given agent type share identical parameters                       | Real-world heterogeneity within strategies is significant       |
| Fixed order size logic              | Quantity decisions are formula-driven, not adaptive to market conditions             | Real agents adjust position sizing based on conviction and risk |
| No portfolio constraints            | No maximum position limit, no risk management, no diversification requirement        | Real agents face VaR limits, stop-losses, and compliance rules  |

### 11.3 What Cannot Be Studied With This Model

- **Flash crashes**: No mechanism for sudden liquidity withdrawal or cascading stop-losses
- **Multi-asset contagion**: Single-asset model cannot produce cross-market spillovers
- **Margin calls and deleveraging**: No leverage means no forced-selling spirals
- **Regulatory interventions**: No circuit breakers, trading halts, or short-sale bans
- **Information arrival shocks**: F is constant; cannot study earnings surprises or macro news
- **Long-run evolutionary dynamics**: No agent entry/exit, no strategy selection pressure
- **Social learning and imitation**: Agents do not observe or copy each other’s strategies

### 11.4 Model Scope Boundary

**What the model IS designed to study**:
- How cognitive anchoring bias translates into market-level mispricing
- The speed and mechanism of price correction given heterogeneous agents
- Whether anchoring effects can be reproduced by LLM-driven agents
- How parameter variations (α, γ, agent mix) affect anchoring magnitude and persistence

**What the model is NOT designed to prove**:
- That real markets exhibit exactly these dynamics (the model is a demonstration, not a calibrated forecast)
- That anchoring is the primary cause of any specific real-world anomaly
- That LLM agents are superior or inferior to rule-based agents (the comparison is descriptive)

### 11.5 Known Model Fragilities

| Parameter Region          | Behaviour                                                 | Resolution                                            |
|---------------------------|-----------------------------------------------------------|-------------------------------------------------------|
| γ > 0.05                  | Mean-reversion dominates; anchoring effect negligible     | Keep γ ≤ 0.02 for meaningful anchoring demonstration  |
| λ > 1.0                   | Price overshoots wildly; possible divergence              | λ = 0.4 is calibrated; do not exceed 0.8              |
| noise_std > 2.0           | Noise overwhelms all signals; metrics meaningless         | Keep noise_std ≤ 1.0 for clean anchoring signal       |
| α > 0.8                   | Near-rational; anchoring effect below detection threshold | α ≤ 0.5 for observable effect; α = 0.3 is the default |
| n_RU > n_AT + n_HA + n_DT | Corrective agents overwhelm biased; instant correction    | Maintain biased/corrective ratio ≥ 1.5                |

