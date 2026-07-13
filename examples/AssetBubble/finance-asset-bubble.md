# AssetBubble — Scenario Target

## §1 Meta

| Field       | Content                                                            |
|-------------|--------------------------------------------------------------------|
| Name        | AssetBubble                                                        |
| Domain      | finance                                                            |
| Produced By | define-simulation-scenario-skill.md v1.0.0 (invoking agent: Codex) |
| Created     | 2026-07-03                                                         |
| Pipeline    | masim/skills/create-simulation-pipeline.md                         |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0)            |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon starts from a liquid risky asset whose price is initially close to fundamental value. A sequence of positive returns, cheap leverage, and resale narratives convinces short-horizon traders that recent price appreciation is itself an actionable signal. This trigger is not a fundamental cash-flow shock; it is a coordination shift in which more participants believe that later buyers will pay higher prices. The initial condition is therefore a small price rise that activates momentum demand before value investors and arbitrageurs can fully offset it.

### §2.2 Mechanism

The core mechanism is a positive feedback loop: rising price increases momentum and sentiment signals, those signals increase speculative demand, and speculative demand pushes price farther above fundamental value. Limits to arbitrage prevent rational short sellers from eliminating the mispricing because short costs, position caps, and synchronization risk make early correction expensive. Leveraged buyers amplify the boom by expanding long exposure during rising prices. When demand exhausts or exit beliefs synchronize, the same leverage channel turns into forced selling and accelerates the crash.

### §2.3 Participants

The causal participants are momentum speculators, rational arbitrageurs, noise traders, fundamental investors, leveraged buyers, and conservative holders. Momentum speculators and noise traders supply destabilising demand based on recent price moves and sentiment. Rational arbitrageurs and fundamental investors supply stabilising pressure, but their force is limited by costs, risk limits, and slow trading cadence. Leveraged buyers are context-dependent during the boom but strongly destabilising when margin pressure forces liquidation.

### §2.4 Resolution

The bubble resolves when speculative inflow can no longer absorb arbitrage pressure, mean reversion, and forced liquidation. A price decline lowers portfolio equity for leveraged buyers, causing margin-call selling that increases net supply and pushes prices down faster. Momentum speculators then stop buying or become sellers, removing the original positive feedback. The end state is either convergence toward fundamental value or overshooting below fundamental value during the crash and recovery phase.

## §3 Research Goals

1. Can heterogeneous investor rules generate a clear asset bubble in which peak price exceeds fundamental value by at least 30 percent?
2. Does removing or weakening momentum-speculator demand measurably reduce the peak bubble ratio and cumulative bubble magnitude?
3. How sensitive are bubble height and crash severity to the price-impact coefficient and mean-reversion coefficient?
4. Do leveraged buyers act as the crash catalyst by producing a sharper post-peak drawdown when margin-call thresholds are active?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in bubble timing, peak ratio, drawdown, and feedback strength?

## §4 Theoretical Anchors

### §4.1 Greater Fool Demand and Momentum Trading

| Field                     | Content                                                                                                                                                                                                            |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| Key mechanism (≤30 words) | Past winners attract additional buyers, making short-horizon price appreciation self-reinforcing.                                                                                                                  |
| Key equation              | `momentum(t) = (P(t) - MA_k(t)) / MA_k(t)`, where `P(t)` is price and `MA_k(t)` is a k-round moving average.                                                                                                       |
| Motivates agent           | momentum-speculator                                                                                                                                                                                                |
| Parameter implication     | `lookback_short` in [3, 12] rounds and `aggressiveness` in [1.0, 4.0] scale momentum demand.                                                                                                                       |

### §4.2 Limits to Arbitrage

| Field                     | Content                                                                                                                                               |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Rational traders may identify overvaluation but cannot fully correct it under funding limits and short-sale risk.                                     |
| Key equation              | `Q_short = min(base_size * deviation * cost_penalty, max_short_position)`, with `cost_penalty = max(0.2, 1 - c_s * c_short * 10)`.                    |
| Motivates agent           | rational-arbitrageur                                                                                                                                  |
| Parameter implication     | `deviation_threshold` in [0.05, 0.10], `short_cost_rate` in [0.01, 0.05], and finite `max_short_position`.                                            |

### §4.3 Noise Trader Risk and Herding

| Field                     | Content                                                                                                                                                                                        |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703 |
| Key mechanism (≤30 words) | Sentiment shocks and trend extrapolation create persistent mispricing that rational arbitrage cannot diversify away.                                                                           |
| Key equation              | `sentiment(t) = epsilon(t) + h * return(t)`, where `epsilon(t) ~ N(0, sigma_sentiment^2)` and `h` is herding weight.                                                                           |
| Motivates agent           | noise-trader                                                                                                                                                                                   |
| Parameter implication     | `sentiment_volatility` in [0.12, 0.30] and `herding_weight` in [0.4, 0.8] control noise demand.                                                                                                |

### §4.4 Fundamental Valuation and Value Anchoring

| Field                     | Content                                                                                                                                                                    |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427-465. https://doi.org/10.1111/j.1540-6261.1992.tb04398.x |
| Key mechanism (≤30 words) | Value-oriented investors compare price to fundamentals and slowly buy undervaluation or resist overvaluation.                                                              |
| Key equation              | `Q_value = value_sensitivity * base_size * (F(t) - P(t)) / F(t)`, where `F(t)` is fundamental value.                                                                       |
| Motivates agent           | fundamental-investor, conservative-holder                                                                                                                                  |
| Parameter implication     | `value_sensitivity` in [0.3, 1.5], `trade_frequency` in [5, 10], and `rebalance_rate` in [0.1, 0.3].                                                                       |

### §4.5 Synchronization Risk and Leverage Cascades

| Field                     | Content                                                                                                                               |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173-204. https://doi.org/10.1111/1468-0262.00393 |
| Key mechanism (≤30 words) | Traders may ride known bubbles until exit beliefs synchronize, after which leveraged selling can trigger a crash.                     |
| Key equation              | `equity_ratio(t) = (cash(t) + position(t) * P(t)) / initial_equity`; forced sell when `equity_ratio < margin_call_threshold`.         |
| Motivates agent           | leveraged-buyer                                                                                                                       |
| Parameter implication     | `leverage_ratio` in [2.0, 3.0] and `margin_call_threshold` in [0.30, 0.70] govern forced deleveraging.                                |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                            | Quantitative range                                                       | Citation                                                                                                           | Acceptance metric                                                       |
|----|--------------------------------------------------------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| F1 | Asset prices exceed fundamental value during the boom.                         | `1.3 <= peak_bubble_ratio <= 1.8`                                        | Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press.                                        | `analysis.py: validate_asset_bubble().max_bubble_ratio` in [1.3, 1.8]   |
| F2 | The crash produces a material peak-to-trough drawdown.                         | `20% <= max_drawdown <= 50%`                                             | Ofek, E., & Richardson, M. (2003). *Journal of Finance*, 58(3), 1113-1137. https://doi.org/10.1111/1540-6261.00522 | `analysis.py: calculate_max_drawdown()` in [20, 50]                     |
| F3 | Demand and next-period returns show positive feedback during bubble formation. | `positive_feedback_index >= 0.5`                                         | De Long et al. (1990). https://doi.org/10.1111/j.1540-6261.1990.tb03695.x                                          | `analysis.py: positive_feedback_index` >= 0.5                           |
| F4 | Return autocorrelation is positive in the bubble phase.                        | `AC1 >= 0.2`                                                             | Lo, A. W., & MacKinlay, A. C. (1988). https://doi.org/10.1093/rfs/1.1.41                                           | `analysis.py: calculate_autocorrelation()[0]` >= 0.2                    |
| F5 | Volatility rises around the peak and crash relative to the build-up.           | peak/crash rolling volatility exceeds build-up volatility by at least 2x | Engle, R. F. (1982). https://doi.org/10.2307/1912773                                                               | `analysis.py: calculate_rolling_volatility()` crash/build-up ratio >= 2 |

## §6 Historical / Empirical Anchors

### §6.1 Dutch Tulip Mania, 1634-1637

| Field             | Content                                                                                                                                                                                                                                                                                                       |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Dutch Tulip Mania, 1634-1637, with collapse in February 1637.                                                                                                                                                                                                                                                 |
| Trigger           | Scarcity narratives and forward-like resale contracts pushed rare tulip prices beyond horticultural value.                                                                                                                                                                                                    |
| Quantitative arc  | Rare-bulb prices reportedly rose multiples above intrinsic value, then collapsed rapidly when buyers failed to appear at auctions.                                                                                                                                                                            |
| Agent mapping     | Momentum speculators map to resale traders; noise traders map to crowd followers; fundamental investors map to buyers anchored to bulb utility; leveraged buyers map to contract buyers exposed to settlement pressure; arbitrageurs and conservative holders map to rational observers refusing peak prices. |
| Primary source(s) | Garber, P. M. (1989). Tulipmania. *Journal of Political Economy*, 97(3), 535-560. https://doi.org/10.1086/261615                                                                                                                                                                                              |

### §6.2 NASDAQ Dot-com Bubble, 1995-2002

| Field             | Content                                                                                                                                                                                                                                                                                  |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | NASDAQ Dot-com Bubble, formation 1995-2000, crash 2000-2002.                                                                                                                                                                                                                             |
| Trigger           | Internet growth narratives and momentum buying overwhelmed earnings-based valuation.                                                                                                                                                                                                     |
| Quantitative arc  | NASDAQ rose roughly 400 percent from 1995 to March 2000 and then fell about 78 percent from peak to trough by October 2002.                                                                                                                                                              |
| Agent mapping     | Momentum speculators map to retail and trend funds; rational arbitrageurs map to constrained short sellers; noise traders map to media-following retail investors; leveraged buyers map to margin buyers; fundamental investors and conservative holders map to patient value investors. |
| Primary source(s) | Ofek, E., & Richardson, M. (2003). DotCom mania: The rise and fall of internet stock prices. *Journal of Finance*, 58(3), 1113-1137. https://doi.org/10.1111/1540-6261.00522                                                                                                             |

### §6.3 US Housing Bubble and Global Financial Crisis, 2002-2009

| Field             | Content                                                                                                                                                                                                                                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | US Housing Bubble and Global Financial Crisis, 2002-2009.                                                                                                                                                                                                                                                 |
| Trigger           | Cheap credit, securitization, leverage, and extrapolative beliefs sustained house-price appreciation.                                                                                                                                                                                                     |
| Quantitative arc  | Case-Shiller national home prices rose strongly before 2006 and later declined about one third from peak in the bust.                                                                                                                                                                                     |
| Agent mapping     | Momentum speculators map to house flippers; leveraged buyers map to high-LTV mortgage borrowers and intermediaries; noise traders map to media-driven buyers; fundamental investors and conservative holders map to valuation-aware institutions; arbitrageurs map to constrained short-credit investors. |
| Primary source(s) | Case, K. E., & Shiller, R. J. (2003). Is there a bubble in the housing market? *Brookings Papers on Economic Activity*, 2003(2), 299-342. https://doi.org/10.1353/eca.2004.0004                                                                                                                           |

## §7 Agent Roster

| Agent name (kebab)   | Real-world counterpart                      | Theory family (§4 anchor)                         | Domain role       | Primary signals                      | Intent line                                                                                  | Expected pool match                                |
|----------------------|---------------------------------------------|---------------------------------------------------|-------------------|--------------------------------------|----------------------------------------------------------------------------------------------|----------------------------------------------------|
| momentum-speculator  | active retail trader / trend-following fund | Greater Fool Demand and Momentum Trading (§4.1)   | Destabilising     | price, return, bubble_ratio          | Exists to amplify ongoing price appreciation through trend-following demand.                 | examples/AGENT_POOL/finance/momentum-trader.md     |
| rational-arbitrageur | hedge fund / short seller                   | Limits to Arbitrage (§4.2)                        | Stabilising       | price, fundamental, short_cost_rate  | Exists to push price back toward fundamental value while respecting short-sale constraints.  | examples/AGENT_POOL/finance/vol-arbitrageur.md     |
| noise-trader         | attention-driven retail trader              | Noise Trader Risk and Herding (§4.3)              | Destabilising     | return, price, volume                | Exists to inject sentiment shocks and herd with recent market moves.                         | examples/AGENT_POOL/finance/noise-trader.md        |
| fundamental-investor | value-oriented mutual fund                  | Fundamental Valuation and Value Anchoring (§4.4)  | Stabilising       | price, fundamental, bubble_ratio     | Exists to buy undervaluation and resist overvaluation using fundamental value.               | examples/AGENT_POOL/finance/fundamental-analyst.md |
| leveraged-buyer      | leveraged retail trader / margin buyer      | Synchronization Risk and Leverage Cascades (§4.5) | Context-dependent | price, portfolio_value, bubble_ratio | Exists to amplify booms through leverage and accelerate crashes through forced deleveraging. | examples/AGENT_POOL/finance/block-trade-buyer.md   |
| conservative-holder  | long-only pension fund / passive allocator  | Fundamental Valuation and Value Anchoring (§4.4)  | Stabilising       | price, fundamental, round            | Exists to provide slow rebalancing demand around a target long-term allocation.              | examples/AGENT_POOL/finance/fundamental-analyst.md |

## §8 Environment Specification

### §8.1 Price Formation

The environment uses a single-clearing-price finance market. Price evolves as `P(t+1) = P(t) + lambda * D(t) + gamma * (F(t) - P(t)) + epsilon(t)`, where `D(t)` is net order demand, `F(t)` is fundamental value, and `epsilon(t)` is exogenous noise. This form implements positive-feedback demand from De Long et al. (1990) while preserving a weak fundamental anchor. It is appropriate for compressed bubble dynamics because price impact is high and mean reversion is deliberately slow.

### §8.2 Information Broadcast

Each round broadcasts `price`, `prev_price`, `return`, `return_pct`, `fundamental`, `bubble_ratio`, `volume`, `net_demand`, `round`, and `short_cost_rate`. Price and return support momentum and herding. Fundamental and bubble ratio support value and arbitrage decisions. Volume, net demand, and short-cost fields expose the market state needed for feedback and limits-to-arbitrage mechanisms.

### §8.3 Constraints and Frictions

Short selling is allowed but capped by `max_short_position` and penalized by `short_cost_rate`. Leverage is allowed for leveraged buyers and momentum speculators, but margin pressure can trigger forced selling when equity ratios fall below threshold. There are no circuit breakers in the baseline because crash dynamics must remain observable. Trading is synchronous by round, with all investor orders collected before the market updates price.

### §8.4 Round Granularity

One round represents a compressed trading interval rather than a literal calendar day. The baseline 200-round horizon compresses multi-year events such as dot-com and housing bubbles into a tractable laboratory timescale. This scale is justified by the historical anchors in §6, where years-long booms and months-to-years crashes are represented by distinct build-up, escalation, peak-crash, and resolution phases. The analysis layer evaluates phase shape and relative timing rather than calendar time.

## §9 Parameter Seeds

| Parameter              | Symbol      | Belongs to (agent / environment) | Empirical range                             | Candidate default | Source citation                                                                                      |
|------------------------|-------------|----------------------------------|---------------------------------------------|-------------------|------------------------------------------------------------------------------------------------------|
| fundamental_value      | F0          | environment (§8.1)               | Source: normalization, 100-scale index      | 100.0             | Source: normalization                                                                                |
| initial_price          | P0          | environment (§8.1)               | Source: normalization, starts at fair value | 100.0             | Source: normalization                                                                                |
| price_impact           | lambda      | environment (§8.1)               | 0.05-0.25 simulation impact range           | 0.15              | De Long et al. (1990), https://doi.org/10.1086/261703                                                |
| mean_reversion         | gamma       | environment (§8.1)               | 0.005-0.05 per round                        | 0.005             | Abreu & Brunnermeier (2003), https://doi.org/10.1111/1468-0262.00393                                 |
| fundamental_growth     | g           | environment (§8.1)               | 0.0005-0.002 per round                      | 0.001             | Shiller (2000), *Irrational Exuberance*                                                              |
| noise_std              | sigma       | environment (§8.1)               | 0.1-0.5 price-index units                   | 0.3               | De Long et al. (1990), https://doi.org/10.1086/261703                                                |
| short_cost_rate        | c_short     | environment (§8.3)               | 0.01-0.05                                   | 0.02              | D'Avolio, G. (2002). *Journal of Financial Economics*, https://doi.org/10.1016/S0304-405X(02)00257-4 |
| lookback_short         | k           | momentum-speculator (§7)         | 3-12 rounds                                 | 3 or 5            | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                        |
| aggressiveness         | alpha       | momentum-speculator (§7)         | 1.0-4.0                                     | 2.0               | De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x                            |
| base_position_size     | q0          | all investor agents (§7)         | 10-50 shares                                | agent-specific    | Chordia et al. (2002), https://doi.org/10.1016/S0304-405X(02)00136-8                                 |
| leverage_multiplier    | ell_m       | momentum-speculator (§7)         | 1.0-2.0                                     | 1.5 or 2.0        | Adrian & Shin (2010), https://doi.org/10.1016/j.jfineco.2009.12.002                                  |
| deviation_threshold    | theta_dev   | rational-arbitrageur (§7)        | 0.05-0.10                                   | 0.05 or 0.10      | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                         |
| max_short_position     | q_short_max | rational-arbitrageur (§7)        | 30-40 shares                                | 30 or 40          | D'Avolio (2002), https://doi.org/10.1016/S0304-405X(02)00257-4                                       |
| short_cost_sensitivity | c_s         | rational-arbitrageur (§7)        | 0.5-2.0                                     | 0.5 or 2.0        | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                         |
| sentiment_volatility   | sigma_s     | noise-trader (§7)                | 0.12-0.30                                   | 0.3               | De Long et al. (1990), https://doi.org/10.1086/261703                                                |
| herding_weight         | h           | noise-trader (§7)                | 0.4-0.8                                     | 0.6 or 0.7        | Barber & Odean (2008), https://doi.org/10.1093/rfs/hhm079                                            |
| trade_frequency        | tau         | fundamental-investor (§7)        | 5-10 rounds                                 | 5                 | Barber & Odean (2000), https://doi.org/10.1111/0022-1082.00226                                       |
| value_sensitivity      | beta_v      | fundamental-investor (§7)        | 0.3-1.5                                     | 0.3 or 1.5        | Fama & French (1992), https://doi.org/10.1111/j.1540-6261.1992.tb04398.x                             |
| leverage_ratio         | ell         | leveraged-buyer (§7)             | 2.0-3.0                                     | 2.0 or 3.0        | Adrian & Shin (2010), https://doi.org/10.1016/j.jfineco.2009.12.002                                  |
| margin_call_threshold  | m           | leveraged-buyer (§7)             | 0.30-0.70                                   | 0.30 or 0.70      | Abreu & Brunnermeier (2003), https://doi.org/10.1111/1468-0262.00393                                 |
| initial_equity         | E0          | leveraged-buyer (§7)             | 10000-scale portfolio normalization         | 10000.0           | Source: normalization                                                                                |
| target_position        | q_target    | conservative-holder (§7)         | 10-30 shares                                | 20.0              | Fama & French (1992), https://doi.org/10.1111/j.1540-6261.1992.tb04398.x                             |
| rebalance_frequency    | tau_reb     | conservative-holder (§7)         | 5-20 rounds                                 | 10                | Barber & Odean (2000), https://doi.org/10.1111/0022-1082.00226                                       |
| rebalance_rate         | rho         | conservative-holder (§7)         | 0.1-0.3                                     | 0.2               | Fama & French (1992), https://doi.org/10.1111/j.1540-6261.1992.tb04398.x                             |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence)                                                                               |
|---------|--------|-------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for the finance scenario.                                             |
| LLM     | Yes    | Tests whether persona-only reasoning reproduces bubble psychology.                                    |
| RuleLLM | Yes    | Tests whether explicit quantitative rules constrain LLM decisions toward the deterministic mechanism. |
| Rag     | Yes    | Tests whether retrieved historical bubble knowledge changes decision quality and bubble dynamics.     |

### §10.2 Pass / Fail Criteria

| Criterion                                                                                          | Status when satisfied |
|----------------------------------------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges or reported with calibrated deviations        | green                 |
| Every §3 research question answerable from analysis outputs                                        | green                 |
| Ablating or weakening any §7 agent family produces a measurable change in at least one core metric | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions                               | green                 |
