# AnchoringEffect — Scenario Target File (Reverse-Reconstructed)

<!--
  Produced By polish-simulation-pipeline.md Step 0 Case B reverse-reconstruction
  (2026-07-01). The scenario existed as `simulation-bases.md` + variant folders
  before the define skill was introduced; this target file was seeded from the
  §4.3 mapping table (§1 Meta ← folder name, §2 Phenomenon ← bases §1, §4
  Anchors ← union of bases §2 theories, §5 Stylized Facts ← analysis-bases §1
  + §6 metrics, §6 Historical Anchors ← bases §8 case studies, §7 Roster ←
  bases §4.1 – §4.9, §8 Environment ← bases §3, §9 Parameters ← bases §6,
  §10.1 Variants ← existing subdirectories).

  Post-reconstruction, this file MUST be handed to define-simulation-scenario-skill.md
  §9.3 revise mode for §11 three-PASS validation and Status transition
  draft → locked.
-->

## §1 Meta

| Field       | Content                                                                                                                                     |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | AnchoringEffect                                                                                                                             |
| Domain      | finance                                                                                                                                     |
| Phenomenon  | Traders anchor to stale reference prices and under-adjust to new information, creating persistent mispricing relative to fundamental value. |
| Pipeline    | masim/skills/create-simulation-pipeline.md                                                                                                  |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                                                     |

## §2 Phenomenon Statement

### §2.1 Trigger

The market opens at a first-observed price `initial_price = 105.0` that is
5 % above the publicly known fundamental value `F = 100.0`. Anchor-forming
agents (AnchoredTrader, HistoricalAnchor) register this first-observed price
(and its rolling average) as their reference and begin trading against it
rather than against `F`. The opening mispricing acts as the seed of the
phenomenon.

### §2.2 Mechanism

Anchored agents update their perceived fair value only fractionally toward
`F` (adjustment factor `α = 0.3`, dampening weight `1 − 0.5` for the
historical anchor), so their demand supports the biased price for many
rounds. Momentum, disposition, and contrarian agents amplify or fade the
resulting slow drift. Rational and fundamental agents pull toward `F`, but
the low price impact `λ = 0.01` and mean reversion `γ = 0.01` allow the
mispricing to persist. The feedback loop is anchor-driven demand supporting
a biased equilibrium.

### §2.3 Participants

The nine participant archetypes are: anchoring-biased agents
(`AnchoredTrader`, `HistoricalAnchor`), corrective agents (`RationalUpdater`,
`FundamentalAnalyst`), trend-following agents (`MomentumTrader`),
mean-reverting agents (`ContrarianTrader`), disposition-biased agents
(`DispositionTrader`), background-liquidity agents (`NoiseTrader`), and
market-making agents (`LiquidityProvider`). Together they produce a
heterogeneous ecology whose net demand at steady state is biased above `F`.

### §2.4 Resolution

The phenomenon ends when the rolling anchor window (60 rounds) drifts to `F`
and the corrective demand from `RationalUpdater`, `FundamentalAnalyst`, and
`ContrarianTrader` overwhelms the residual anchoring demand. The two-phase
convergence path predicts: fast approach to a biased steady state
`P* > F` (half-life ≈ 35 rounds), then slow drift of `P*` toward `F` as the
`HistoricalAnchor` window fully updates.

## §3 Research Goals

1. **Ablation.** Turning off the two `AnchoredTrader` instances is expected
   to shrink the mean absolute deviation (MAD) from fundamental by more than
   50 %. Answered via `analysis.py: mean_absolute_deviation()` before and
   after ablation.
2. **Parameter sweep.** Varying `adjustment_factor α ∈ {0.1, 0.3, 0.5, 0.7,
   0.9}` traces the anchoring-to-rationality curve. Answered via
   `analysis.py: anchoring_bias_index()` across the sweep grid.
3. **Variant comparison.** Do LLM personas without explicit rules reproduce
   the Rule variant's MAD half-life within a factor of 2? Answered by
   comparing `Rule` vs `LLM` MAD trajectories.

## §4 Theoretical Anchors

### §4.1 Anchoring and Insufficient Adjustment (Tversky & Kahneman 1974)

| Field                     | Content                                                                                                                                                               |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. https://doi.org/10.1126/science.185.4157.1124 |
| Key mechanism (≤30 words) | Agents start estimates from a salient reference (anchor) and adjust insufficiently toward the true value, even when the anchor is arbitrary.                          |
| Key equation              | `perceived_target = anchor + (F − anchor) × α`, `α ∈ (0, 1)`; classical experimental mean `α ≈ 0.3`.                                                                  |
| Motivates agent           | AnchoredTrader (§7)                                                                                                                                                   |
| Parameter implication     | `adjustment_factor = 0.3` (§9).                                                                                                                                       |

### §4.2 Expert Anchoring to Past Prices (Northcraft & Neale 1987)

| Field                     | Content                                                                                                                                                                                                                  |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective on property pricing decisions. *OBHDP*, 39(1), 84–97. https://doi.org/10.1016/0749-5978(87)90046-X |
| Key mechanism (≤30 words) | Experts anchor to a listed / historical price and only partially adjust; expert anchoring is smaller than novice anchoring but still material.                                                                           |
| Key equation              | `perceived_deviation = (P − hist_avg) / hist_avg × (1 − anchor_weight)`; `anchor_weight ∈ [0, 1]`, expert value ≈ 0.5.                                                                                                   |
| Motivates agent           | HistoricalAnchor (§7)                                                                                                                                                                                                    |
| Parameter implication     | `anchor_weight = 0.5`, `lookback = 60` (§9).                                                                                                                                                                             |

### §4.3 Anchoring in Consensus Financial Forecasts (Campbell & Sharpe 2009)

| Field                     | Content                                                                                                                                                                           |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *JFQA*, 44(2), 369–390. https://doi.org/10.1017/S0022109009090127 |
| Key mechanism (≤30 words) | Consensus forecasts systematically under-revise because forecasters anchor to prior values; revisions are 30 – 70 % of the Bayesian update.                                       |
| Key equation              | `forecast_revision(t) = θ × (new_info − prior_forecast)`, `θ ∈ [0.3, 0.7]`.                                                                                                       |
| Motivates agent           | AnchoredTrader (§7); calibrates persistence for HistoricalAnchor                                                                                                                  |
| Parameter implication     | `adjustment_factor = 0.3` cross-check; motivates half-life target `[20, 60]` rounds.                                                                                              |

### §4.4 Rational Expectations Benchmark (Muth 1961)

| Field                     | Content                                                                                                                                      |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1905537 |
| Key mechanism (≤30 words) | Under rational expectations, agents optimally use all information; no systematic deviation from fundamentals is exploitable.                 |
| Key equation              | `E[P(t+1)                                                                                                                                    |
| Motivates agent           | RationalUpdater (§7)                                                                                                                         |
| Parameter implication     | `trade_threshold = 0.02` for `RationalUpdater` (§9).                                                                                         |

### §4.5 Short-Horizon Momentum (Jegadeesh & Titman 1993)

| Field                     | Content                                                                                                                                                                  |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| Key mechanism (≤30 words) | Stocks with recent gains continue outperforming near-term; short-horizon momentum amplifies existing trends.                                                             |
| Key equation              | `momentum_signal = (P − P_prev) / P_prev`; trade when `                                                                                                                  |
| Motivates agent           | MomentumTrader (§7)                                                                                                                                                      |
| Parameter implication     | `entry_threshold = 0.02` (§9).                                                                                                                                           |

### §4.6 Prospect Theory Disposition Effect (Shefrin & Statman 1985; Kahneman & Tversky 1979)

| Field                     | Content                                                                                                                                                                                                                                          |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x; Kahneman & Tversky (1979) *Econometrica* 47(2). |
| Key mechanism (≤30 words) | Loss-averse investors sell winners early (gain threshold ≈ 4 %) and ride losers longer (loss threshold ≈ 2.5× harder to trigger).                                                                                                                |
| Key equation              | `sell if (P − cost) / cost > gain_threshold`; `hold if (cost − P) / cost < gain_threshold × loss_aversion_mult`.                                                                                                                                 |
| Motivates agent           | DispositionTrader (§7)                                                                                                                                                                                                                           |
| Parameter implication     | `gain_threshold = 0.04`, `loss_aversion_mult = 2.5` (§9).                                                                                                                                                                                        |

### §4.7 Overreaction and Short-Horizon Reversal (De Bondt & Thaler 1985; Jegadeesh 1990)

| Field                     | Content                                                                                                                                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x; Jegadeesh (1990) *Journal of Finance* 45(3). |
| Key mechanism (≤30 words) | Short-horizon cumulative returns overshoot fair value; contrarian traders fade the overshoot.                                                                                                                    |
| Key equation              | `cum_ret = (P_t − P_{t−k}) / P_{t−k}`; short if `cum_ret > entry_threshold`, long if `cum_ret < −entry_threshold`.                                                                                               |
| Motivates agent           | ContrarianTrader (§7)                                                                                                                                                                                            |
| Parameter implication     | `lookback = 10`, `entry_threshold = 0.05` (§9).                                                                                                                                                                  |

### §4.8 Conservatism / Slow Belief Updating (Barberis, Shleifer & Vishny 1998)

| Field                     | Content                                                                                                                                                                         |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0 |
| Key mechanism (≤30 words) | Institutional investors update beliefs conservatively; belief `b_t` converges toward `F` at learning rate `η`.                                                                  |
| Key equation              | `b_{t+1} = b_t + η × (F − b_t)`; trade on `(b_t − P) / P` with threshold.                                                                                                       |
| Motivates agent           | FundamentalAnalyst (§7)                                                                                                                                                         |
| Parameter implication     | `learning_rate = 0.05`, `dev_threshold = 0.02` (§9).                                                                                                                            |

### §4.9 Market Making and Two-Sided Quoting (Glosten & Milgrom 1985)

| Field                     | Content                                                                                                                                                                                                                              |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3 |
| Key mechanism (≤30 words) | Market makers post two-sided quotes around a short-term EMA and absorb transient order-flow imbalance for a small spread.                                                                                                            |
| Key equation              | Quote `bid = EMA − half_spread × EMA`, `ask = EMA + half_spread × EMA`; trade when observed price crosses either side.                                                                                                               |
| Motivates agent           | LiquidityProvider (§7)                                                                                                                                                                                                               |
| Parameter implication     | `ema_window = 20`, `half_spread = 0.015` (§9).                                                                                                                                                                                       |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                      | Quantitative range                      | Citation                                             | Acceptance metric                                       |
|----|----------------------------------------------------------------------------------------------------------|-----------------------------------------|------------------------------------------------------|---------------------------------------------------------|
| F1 | The Rule variant exhibits persistent mean absolute deviation of price from fundamental across the run.   | `3 % ≤ MAD ≤ 10 %`                      | Campbell & Sharpe (2009) 10.1017/S0022109009090127   | `analysis.py: mean_absolute_deviation()` ∈ [0.03, 0.10] |
| F2 | Price converges toward fundamental with a half-life consistent with anchoring persistence.               | `20 ≤ half_life ≤ 60`                   | Campbell & Sharpe (2009); §10 equilibrium derivation | `analysis.py: convergence_half_life()` ∈ [20, 60]       |
| F3 | Anchoring drives a positive bias in mean price above fundamental for the biased steady-state phase.      | `mean(P) − F ≥ 1.0`                     | Northcraft & Neale (1987); §10 SS analysis           | `analysis.py: biased_equilibrium_gap()` ≥ 1.0           |
| F4 | Turning off both AnchoredTrader instances reduces MAD by more than 50 %.                                 | `MAD_ablated ≤ 0.5 × MAD_full`          | This model (research goal 1)                         | `analysis.py: ablation_mad_ratio(anchored=off)` ≤ 0.5   |
| F5 | Momentum traders' cumulative P&L is positive during the biased-equilibrium phase and neutral thereafter. | `cum_pnl_momentum > 0` in rounds 1 – 80 | Jegadeesh & Titman (1993)                            | `analysis.py: momentum_pnl_phase()` sign matches phase  |

## §6 Historical / Empirical Anchors

### §6.1 Analyst Earnings Forecast Anchoring (US Equity Markets, 1992 – 2006)

| Field             | Content                                                                                                                                                                                                                                                                                                                                                                                                           |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Consensus Analyst Forecast Anchoring; 1992 – 2006 (Campbell & Sharpe 2009 sample).                                                                                                                                                                                                                                                                                                                                |
| Trigger           | Analysts revise quarterly EPS forecasts after data releases; anchoring causes under-revision by roughly 30 – 70 %.                                                                                                                                                                                                                                                                                                |
| Quantitative arc  | Average under-revision ≈ 50 %; forecast-error autocorrelation `r ≈ 0.4`; revision-based strategy Sharpe ratio ≈ 0.6.                                                                                                                                                                                                                                                                                              |
| Agent mapping     | Sell-side analysts → AnchoredTrader; institutional investors anchoring to long-run mean → HistoricalAnchor; quant funds exploiting drift → RationalUpdater; slow-learning institutions → FundamentalAnalyst; momentum HFs → MomentumTrader; short-horizon reversal HFs → ContrarianTrader; retail loss-averse holders → DispositionTrader; retail chatter → NoiseTrader; market-making desks → LiquidityProvider. |
| Primary source(s) | Campbell & Sharpe (2009), *JFQA*, https://doi.org/10.1017/S0022109009090127                                                                                                                                                                                                                                                                                                                                       |

### §6.2 Real-Estate Appraisal Anchoring (Northcraft & Neale 1987)

| Field             | Content                                                                                                                                                                                                                                                                                                                                                                               |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Real-Estate Appraisal Anchoring Experiment; 1987 laboratory study.                                                                                                                                                                                                                                                                                                                    |
| Trigger           | Professional appraisers given identical property data with high vs low listing-price anchors produced systematically different valuations.                                                                                                                                                                                                                                            |
| Quantitative arc  | Expert valuations anchored `≈ 12 %` toward listing price; novice valuations `≈ 21 %`; correlation `r ≈ 0.7`.                                                                                                                                                                                                                                                                          |
| Agent mapping     | Experts → HistoricalAnchor; novices → AnchoredTrader; corrective valuation service → RationalUpdater; slow-belief-updating appraisal firms → FundamentalAnalyst; trend-following house flippers → MomentumTrader; short-run bargain hunters → ContrarianTrader; loss-averse home owners → DispositionTrader; random walk-ins → NoiseTrader; broker market makers → LiquidityProvider. |
| Primary source(s) | Northcraft & Neale (1987), *OBHDP*, https://doi.org/10.1016/0749-5978(87)90046-X                                                                                                                                                                                                                                                                                                      |

### §6.3 IPO Aftermarket Price Anchoring

| Field             | Content                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | IPO Aftermarket Price Anchoring; multi-decade IPO samples.                                                                                                                                                                                                                                                                                                                                               |
| Trigger           | IPO offer price acts as natural anchor for retail investors for 6 – 12 months post-issuance.                                                                                                                                                                                                                                                                                                             |
| Quantitative arc  | Post-IPO price frequently within ± 20 % of the offer anchor in month 1 even when fundamentals justify larger moves (Loughran & Ritter 2002).                                                                                                                                                                                                                                                             |
| Agent mapping     | Retail using offer as fair value → AnchoredTrader; retail using 60-day historical average → HistoricalAnchor; institutional value → RationalUpdater; slow institutions → FundamentalAnalyst; IPO momentum funds → MomentumTrader; short-horizon reversal traders → ContrarianTrader; retail bag holders → DispositionTrader; retail noise → NoiseTrader; issuing bank market makers → LiquidityProvider. |
| Primary source(s) | Loughran, T., & Ritter, J. R. (2002). *RFS*, https://doi.org/10.1093/rfs/15.2.413                                                                                                                                                                                                                                                                                                                        |

## §7 Agent Roster

| Agent name (kebab)  | Real-world counterpart              | Theory family (§4 anchor)    | Domain role   | Primary signals                 | Intent line                                                                           | Expected pool match                                |
|---------------------|-------------------------------------|------------------------------|---------------|---------------------------------|---------------------------------------------------------------------------------------|----------------------------------------------------|
| anchored-trader     | Retail investor anchored to open    | Anchoring (§4.1)             | Destabilising | price, fundamental, deviation   | "Exists to hold demand near the first-observed price, resisting adjustment to F."     | examples/AGENT_POOL/finance/anchored-trader.md     |
| historical-anchor   | Institutional analyst / appraiser   | Expert Anchoring (§4.2)      | Destabilising | price, price_history, deviation | "Exists to anchor demand to a rolling historical average of price."                   | examples/AGENT_POOL/finance/historical-anchor.md   |
| rational-updater    | Quant arbitrage fund                | Rational Expectations (§4.4) | Stabilising   | price, fundamental, deviation   | "Exists to close deviations between price and observable fundamental."                | examples/AGENT_POOL/finance/rational-updater.md    |
| momentum-trader     | Trend-following hedge fund          | Momentum (§4.5)              | Destabilising | price, prev_price               | "Exists to amplify short-horizon directional price moves."                            | examples/AGENT_POOL/finance/momentum-trader.md     |
| noise-trader        | Retail noise flow                   | Noise (§4.5 / Black 1986)    | Context-dep.  | price (random draw)             | "Exists to inject small random background order flow around the price."               | examples/AGENT_POOL/finance/noise-trader.md        |
| disposition-trader  | Loss-averse retail holder           | Prospect Theory (§4.6)       | Context-dep.  | price, own cost-basis           | "Exists to sell winners early and hold losers, per prospect-theory asymmetry."        | examples/AGENT_POOL/finance/disposition-trader.md  |
| contrarian-trader   | Short-horizon mean-reversion desk   | Overreaction (§4.7)          | Stabilising   | cumulative return over lookback | "Exists to fade short-horizon cumulative overshoots back toward the mean."            | examples/AGENT_POOL/finance/contrarian-trader.md   |
| fundamental-analyst | Slow-learning institutional analyst | Conservatism (§4.8)          | Stabilising   | price, belief_t, fundamental    | "Exists to converge beliefs toward fundamental value and trade the residual gap."     | examples/AGENT_POOL/finance/fundamental-analyst.md |
| liquidity-provider  | Market-maker desk                   | Two-Sided Quoting (§4.9)     | Stabilising   | price, short-term EMA           | "Exists to post two-sided quotes around a short-term EMA and absorb order imbalance." | examples/AGENT_POOL/finance/liquidity-provider.md  |

Diversity: 4 stabilising, 3 destabilising, 2 context-dependent; theory
families do not repeat more than twice across agents; several agents rely on
non-price primary signals (fundamental, cost-basis, belief, EMA).

## §8 Environment Specification

### §8.1 Price Formation

Single-asset, single-venue, quote-driven equity-style market with the
`Kyle (1985)`-style linear impact model:

```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

`λ = 0.01` (price impact), `γ = 0.01` (mean reversion), `F = 100.0`
(constant fundamental), `ε(t) ~ N(0, 0.5²)`. Justified by Brock & Hommes
(1998), LeBaron (2006).

### §8.2 Information Broadcast

Each round, the market broadcasts `{price, prev_price, fundamental,
deviation, round}` to all investors. `fundamental` is deliberately visible
to isolate anchoring as a cognitive rather than informational failure
(Tversky & Kahneman 1974).

### §8.3 Constraints and Frictions

| Item              | Yes/No  | Rationale                                                       |
|-------------------|---------|-----------------------------------------------------------------|
| Short-selling     | Bounded | Sells limited to current position (no naked shorts).            |
| Margin / leverage | No      | Focuses attention on anchoring, not funding-liquidity spirals.  |
| Circuit breakers  | No      | Not needed at `λ = 0.01`.                                       |
| Bid-ask spread    | No      | Continuous quote-driven price; frictionless per §3 abstraction. |
| Transaction cost  | No      | Same rationale.                                                 |

### §8.4 Round Granularity

One round represents one analyst forecast-revision opportunity (roughly one
day for equity analysts, one appraisal for property, one trading day for
IPO aftermarket). Motivated by Campbell & Sharpe (2009) monthly-revision
cadence rescaled to daily rounds.

## §9 Parameter Seeds

| Parameter            | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation                                                       |
|----------------------|--------|----------------------------------|-----------------|-------------------|-----------------------------------------------------------------------|
| `initial_price`      | P0     | environment (§8.1)               | 1.03 F – 1.10 F | 105.0             | Source: normalization (5 % above F, IPO-style seed)                   |
| `fundamental_value`  | F      | environment (§8.1)               | 100.0           | 100.0             | Source: normalization                                                 |
| `price_impact`       | λ      | environment (§8.1)               | 0.005 – 0.05    | 0.01              | Hasbrouck (1991) 10.2307/2328883                                      |
| `mean_reversion`     | γ      | environment (§8.1)               | 0.005 – 0.05    | 0.01              | Campbell & Sharpe (2009) 10.1017/S0022109009090127                    |
| `noise_std`          | σ      | environment (§8.1)               | 0.1 – 1.0       | 0.5               | Lux & Marchesi (1999) 10.1038/17290                                   |
| `adjustment_factor`  | α      | AnchoredTrader (§7)              | 0.1 – 0.5       | 0.3               | Tversky & Kahneman (1974) 10.1126/science.185.4157.1124               |
| `anchor_weight`      | w      | HistoricalAnchor (§7)            | 0.3 – 0.7       | 0.5               | Northcraft & Neale (1987) 10.1016/0749-5978(87)90046-X                |
| `lookback`           | L      | HistoricalAnchor (§7)            | 20 – 90         | 60                | Campbell & Sharpe (2009)                                              |
| `entry_threshold`    | τ_MT   | MomentumTrader (§7)              | 0.01 – 0.05     | 0.02              | Jegadeesh & Titman (1993) 10.1111/j.1540-6261.1993.tb04702.x          |
| `trade_probability`  | p_NT   | NoiseTrader (§7)                 | 0.02 – 0.10     | 0.05              | Black (1986) 10.1111/j.1540-6261.1986.tb04513.x                       |
| `gain_threshold`     | g      | DispositionTrader (§7)           | 0.03 – 0.08     | 0.04              | Odean (1998) 10.1111/0022-1082.00072                                  |
| `loss_aversion_mult` | λ_LA   | DispositionTrader (§7)           | 2.0 – 2.5       | 2.5               | Kahneman & Tversky (1979) 10.2307/1914185                             |
| `lookback_window`    | L_CT   | ContrarianTrader (§7)            | 5 – 20          | 10                | Jegadeesh (1990) 10.1111/j.1540-6261.1990.tb03723.x                   |
| `ct_entry_threshold` | τ_CT   | ContrarianTrader (§7)            | 0.03 – 0.08     | 0.05              | De Bondt & Thaler (1985) 10.1111/j.1540-6261.1985.tb05004.x           |
| `learning_rate`      | η      | FundamentalAnalyst (§7)          | 0.02 – 0.10     | 0.05              | Barberis, Shleifer & Vishny (1998) 10.1016/S0304-405X(98)00027-0      |
| `ema_window`         | L_EMA  | LiquidityProvider (§7)           | 10 – 40         | 20                | Hendershott, Jones & Menkveld (2011) 10.1111/j.1540-6261.2010.01624.x |
| `half_spread`        | h      | LiquidityProvider (§7)           | 0.005 – 0.025   | 0.015             | Huang & Stoll (1997) 10.1093/rfs/10.4.995                             |
| `initial_cash`       | C0     | all investors (§7)               | 10000.0         | 10000.0           | Source: normalization                                                 |
| `initial_position`   | Q0     | all investors (§7)               | 100.0           | 100.0             | Source: normalization                                                 |
| `base_position_size` | b      | agent-specific (§7)              | 15 – 30         | 20                | Source: normalization                                                 |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤ 1 sentence)                                                                  |
|---------|--------|-------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for the §5 stylized-fact benchmark.                       |
| LLM     | Yes    | Answers research goal 3 (do LLM personas reproduce anchoring without explicit formulas?). |
| RuleLLM | Yes    | Answers research goal 3 hybrid: rules bound LLM behaviour.                                |
| Rag     | Yes    | Answers research goal 3 with a retrieval-augmented LLM (uses §6 anchors as corpus).       |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from `analysis.py`             | green                 |
| Ablating AnchoredTrader produces a measurable MAD reduction (≥ 50 %) | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
