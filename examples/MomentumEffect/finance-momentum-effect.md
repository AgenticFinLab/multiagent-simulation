# MomentumEffect — Scenario Target

## §1 Meta

| Field       | Content                                                                                                                                    |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | MomentumEffect                                                                                                                             |
| Domain      | finance                                                                                                                                    |
| Phenomenon  | Trend-following positive-feedback trading creates intermediate-horizon return persistence that decays only when opposing signals dominate. |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                                                                                                 |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                                                    |

## §2 Phenomenon Statement

### §2.1 Trigger
The scenario begins with a persistent drift in fundamental value, creating a sequence of same-signed price movements that form the raw material for trend-following signals. A small initial return — positive or negative — crosses a momentum trader's activation threshold, converting a statistically mild signal into a directional order. That order feeds into the market's net demand and produces a price continuation that reinforces the original signal.

### §2.2 Mechanism
The amplification loop is return continuation through positive-feedback trading. Momentum-oriented agents observe recent returns and trade in the direction of the signal, increasing order imbalance. The market's price impact converts that imbalance into further price movement, which strengthens the signal for the next round. Technical and trend-following agents further crowd the same direction when their moving-average or time-series signals align. Contrarian, fundamental-value, and passive-rebalancing agents provide offsetting pressure, but their corrective action is gradual. The net effect is intermediate-horizon persistence that decays only when opposing signals become large enough to overcome trend-following conviction.

### §2.3 Participants
The core participant classes are momentum trend followers, contrarian reversal traders, passive index rebalancers, inventory-managing market makers, moving-average technical traders, and fundamental-value anchors. Momentum and technical traders provide positive-feedback demand. Index funds and market makers supply slow, non-directional baseline flow. Contrarian and fundamental-value traders provide the opposing force that eventually weakens continuation.

### §2.4 Resolution
Continuation weakens when the trend-following signal diminishes, opposing agents' orders grow relative to momentum demand, or the price deviates far enough from fundamental value to trigger value-based trading. Contrarian traders activate once the absolute momentum signal exceeds their reversal threshold, selling into rallies and buying into declines. Fundamental-value traders enter when mispricing relative to fundamental value crosses a threshold, providing a long-run gravitational pull. The trend ends when net demand from stabilising forces matches or exceeds momentum-side pressure.

## §3 Research Goals

1. **Continuation magnitude.** Can the simulation generate positive return autocorrelation in the 0.20 to 0.50 range during trend phases, consistent with intermediate-horizon momentum evidence?
2. **Trend duration and decay.** Do trend phases persist for multiple consecutive rounds, and do contrarian or fundamental offsets eventually weaken continuation?
3. **Agent attribution.** Does momentum-side order imbalance (MomentumTrader, TechnicalTrader, TrendFollower) dominate during trend phases, and does contrarian or value-anchor flow rise as trends extend?
4. **Ablation.** If the contrarian reversal agent is removed, does trend duration increase and return autocorrelation rise relative to the full model?
5. **Parameter sweep and variant comparison.** How do the momentum threshold and price impact parameters change trend duration and reversal timing, and how do LLM-driven variants differ from the deterministic Rule baseline in conviction and timing?

## §4 Theoretical Anchors

### §4.1 Return Momentum

| Field                     | Content                                                                                                                                                                                                            |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| Key mechanism (≤30 words) | Past winners continue to outperform over intermediate horizons because information is incorporated gradually, creating return continuation.                                                                        |
| Key equation              | Trade direction = sign(P_t - P_{t-k}) when the absolute momentum signal exceeds a threshold; quantity scales with signal magnitude.                                                                                |
| Motivates agent           | momentum-trader (§7), trend-follower (§7)                                                                                                                                                                          |
| Parameter implication     | momentum_threshold range 0.01 to 0.04, default 0.02; lookback window 3 to 10 rounds, default 5.                                                                                                                    |

### §4.2 Underreaction and Information Diffusion

| Field                     | Content                                                                                                                                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction in asset markets. *Journal of Finance*, 54(6), 2143-2184. https://doi.org/10.1111/0022-1082.00184 |
| Key mechanism (≤30 words) | Information diffuses gradually across investors. Early news-watchers react immediately, but momentum traders respond with delay, sustaining price continuation.                                          |
| Key equation              | Persistent fundamental drift creates a sequence of partially correlated signals; trend followers respond to the realised return sequence rather than the fundamental drift directly.                     |
| Motivates agent           | technical-trader (§7)                                                                                                                                                                                    |
| Parameter implication     | drift_persistence range 0.80 to 0.99, default 0.95; drift_volatility range 0.20 to 1.00, default 0.50.                                                                                                   |

### §4.3 Overreaction and Long-Horizon Reversal

| Field                     | Content                                                                                                                                                            |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| Key mechanism (≤30 words) | Past losers outperform past winners over long horizons as prices revert after overshooting, creating the reversal that limits momentum.                            |
| Key equation              | Contrarian trade direction = -sign(momentum_signal) when abs(momentum_signal) > reversion_threshold; quantity scales with signal magnitude.                        |
| Motivates agent           | contrarian-trader (§7)                                                                                                                                             |
| Parameter implication     | reversion_threshold range 0.02 to 0.06, default 0.03.                                                                                                              |

### §4.4 Time-Series Momentum and Technical Trading

| Field                     | Content                                                                                                                                                                        |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228-250. https://doi.org/10.1016/j.jfineco.2011.11.003 |
| Key mechanism (≤30 words) | A security's own past return predicts its future return across asset classes; moving-average and breakout strategies capture this time-series continuation signal.             |
| Key equation              | Buy when MA_short > MA_long; sell when MA_short < MA_long; crossover strength scales position size.                                                                            |
| Motivates agent           | technical-trader (§7), trend-follower (§7)                                                                                                                                     |
| Parameter implication     | short_window range 2 to 5, default 3; long_window range 8 to 20, default 10.                                                                                                   |

### §4.5 Limits to Arbitrage and Fundamental Anchoring

| Field                     | Content                                                                                                                                                                    |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                      |
| Key mechanism (≤30 words) | Arbitrageurs face capital constraints and noise-trader risk, so they cannot fully correct mispricings; fundamental value provides long-run gravity but correction is slow. |
| Key equation              | value_deviation = (price - fundamental) / fundamental; buy when deviation < -value_threshold; sell when deviation > +value_threshold.                                      |
| Motivates agent           | fundamental-anchor (§7)                                                                                                                                                    |
| Parameter implication     | value_threshold range 0.03 to 0.10, default 0.05.                                                                                                                          |

### §4.6 Inventory-Control Market Making

| Field                     | Content                                                                                                                                                                                      |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Ho, T., & Stoll, H. R. (1981). Optimal dealer pricing under transactions and return uncertainty. *Journal of Financial Economics*, 9(1), 47-73. https://doi.org/10.1016/0304-405X(81)90020-5 |
| Key mechanism (≤30 words) | Market makers manage inventory by adjusting bid-ask quotes to induce mean-reverting order flow, dampening order imbalance without taking directional views.                                  |
| Key equation              | inventory_deviation = inventory - inventory_target; trade quantity = -reversion_speed * inventory_deviation.                                                                                 |
| Motivates agent           | market-maker (§7)                                                                                                                                                                            |
| Parameter implication     | inventory_target normalised to 0.0; reversion_speed range 0.10 to 0.40, default 0.20.                                                                                                        |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                                                 | Quantitative range                                        | Citation                                                                        | Acceptance metric                                                     |
|----|-------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|---------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| F1 | Return autocorrelation at lag 1 is positive during momentum phases.                                                                 | 0.20 <= ac1 <= 0.50                                       | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x   | `analysis.py: compute_return_autocorrelation(lag=1)` in [0.20, 0.50]  |
| F2 | Momentum-side order imbalance is positive and dominates during trend phases.                                                        | momentum_imbalance > 0.10                                 | Hong & Stein (1999), https://doi.org/10.1111/0022-1082.00184                    | `analysis.py: compute_momentum_order_imbalance()` > 0.10              |
| F3 | Contrarian offset flow increases in magnitude as trend extends.                                                                     | contrarian_volume_share >= 0.10 after round 20            | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x    | `analysis.py: compute_contrarian_offset()` presence after round 20    |
| F4 | Trend duration of at least 4 consecutive same-direction rounds is observable.                                                       | max_trend_duration >= 4                                   | Moskowitz, Ooi & Pedersen (2012), https://doi.org/10.1016/j.jfineco.2011.11.003 | `analysis.py: compute_trend_duration()` >= 4                          |
| F5 | Price deviates from fundamental value during trend phases, with fundamental deviation falling as value-anchor agents become active. | max_deviation > 0 during trend; post-peak deviation falls | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x    | `analysis.py: compute_fundamental_deviation()` peak-to-trough decline |

## §6 Historical / Empirical Anchors

### §6.1 Cross-Sectional Equity Momentum (Jegadeesh & Titman, 1993)

| Field             | Content                                                                                                                                                                                                                                                                         |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Cross-sectional equity momentum documented 1965-1989 (Jegadeesh & Titman 1993 study period).                                                                                                                                                                                    |
| Trigger           | Past 3-12 month winner portfolios continue to outperform loser portfolios over subsequent 3-12 month holding periods.                                                                                                                                                           |
| Quantitative arc  | Winner-minus-loser decile spread of roughly 1% per month over intermediate horizons; momentum profits persist for 6-12 months before mean reversion reduces them.                                                                                                               |
| Agent mapping     | `momentum-trader` maps to momentum strategy investors who buy past winners; `trend-follower` maps to time-series trend-following CTAs; `contrarian-trader` maps to long-horizon reversal investors; `fundamental-anchor` maps to value investors who anchor to intrinsic worth. |
| Primary source(s) | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                                                                                                                                                                                   |

### §6.2 CTA and Time-Series Momentum Crowding (2008-2015)

| Field             | Content                                                                                                                                                                         |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Managed-futures and CTA trend-following crowding, 2008-2015.                                                                                                                    |
| Trigger           | Post-2008 investor inflows into trend-following strategies created strategy crowding, where many funds reacted to the same price signals simultaneously.                        |
| Quantitative arc  | CTA AUM grew from roughly 200bn to over 300bn during 2008-2015; momentum crashes (sharp reversals) occurred when crowded positions unwound, e.g., 2014 Treasury rally reversal. |
| Agent mapping     | `trend-follower` maps to systematic CTA funds; `technical-trader` maps to moving-average crossover strategies; `momentum-trader` maps to discretionary momentum managers.       |
| Primary source(s) | Moskowitz, Ooi & Pedersen (2012), https://doi.org/10.1016/j.jfineco.2011.11.003                                                                                                 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart                                         | Theory family (§4 anchor)                                    | Domain role   | Primary signals               | Intent line                                                                                               | Expected pool match                                                |
|--------------------|----------------------------------------------------------------|--------------------------------------------------------------|---------------|-------------------------------|-----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| momentum-trader    | momentum strategy fund or active trend-chasing retail investor | Return Momentum (§4.1)                                       | Destabilising | price, return, deviation      | "Exists to amplify directional price moves by trading in the direction of recent returns."                | examples/AGENT_POOL/finance/momentum-trader.md                     |
| contrarian-trader  | long-horizon reversal fund or contrarian hedge fund            | Overreaction (§4.3)                                          | Stabilising   | price, return, deviation      | "Exists to trade against extended trends, supplying reverse-side pressure when signals grow large."       | examples/AGENT_POOL/finance/contrarian-trader.md                   |
| index-fund         | passive index mutual fund or ETF provider                      | Portfolio Rebalancing (passive allocation) (§4.6 context)    | Stabilising   | price, cash, position         | "Exists to maintain a target equity allocation through slow rebalancing, adding baseline non-trend flow." | (none — likely new)                                                |
| market-maker       | designated market maker or high-frequency liquidity provider   | Inventory-Control (§4.6)                                     | Stabilising   | price, inventory, cash        | "Exists to supply liquidity by reverting inventory toward a target without taking directional views."     | examples/AGENT_POOL/finance/liquidity-provider.md                  |
| technical-trader   | systematic CTA or technical analysis trader                    | Information Diffusion (§4.2) and Time-Series Momentum (§4.4) | Destabilising | price, return                 | "Exists to reinforce continuation through moving-average crossover signals."                              | examples/AGENT_POOL/finance/trend-follower.md                      |
| fundamental-anchor | value-oriented mutual fund or fundamental analyst              | Limits to Arbitrage (§4.5)                                   | Stabilising   | price, fundamental, deviation | "Exists to pull price back toward intrinsic value when mispricing exceeds a threshold."                   | examples/AGENT_POOL/finance/fundamental-analyst.md                 |
| trend-follower     | aggressive systematic trend-following CTA                      | Return Momentum (§4.1) and Time-Series Momentum (§4.4)       | Destabilising | price, return                 | "Exists to amplify continuation with higher-conviction sizing than a baseline momentum trader."           | examples/AGENT_POOL/finance/momentum-trader.md (family match only) |

Diversity notes: the roster includes three destabilising agents (momentum-trader, technical-trader, trend-follower), three stabilising agents (contrarian-trader, index-fund, market-maker), and one stabilising value anchor (fundamental-anchor). Theory families span return continuation, underreaction/information diffusion, overreaction/reversal, time-series momentum, limits to arbitrage, and inventory control. Signal diversity includes price, return, deviation, fundamental, inventory, cash, and position channels. At most two agents share the same theory family (§4.1 and §4.4 each anchor two agents).

## §8 Environment Specification

### §8.1 Price Formation

Single price-impact plus mean-reversion market with persistent fundamental drift:

`P(t+1) = max(P(t) + lambda * D(t) + gamma * [F(t) - P(t)] + epsilon(t), 1.0)`, where `D(t)` is aggregate buy quantity minus sell quantity, `F(t)` is the fundamental value that follows a persistent autoregressive drift, `lambda` is price impact, `gamma` is mean reversion, and `epsilon(t)` is Gaussian noise with standard deviation `sigma`. The persistent drift in `F(t)` creates the gradual information-diffusion environment that generates momentum signals. High price impact relative to mean reversion ensures that momentum demand produces visible continuation rather than instant reversion.

### §8.2 Information Broadcast

| Field         | Type  | Definition                                  | Rationale                                                   |
|---------------|-------|---------------------------------------------|-------------------------------------------------------------|
| `price`       | float | Current market price.                       | Primary state signal for all agents.                        |
| `prev_price`  | float | Previous round price.                       | Required for return and momentum calculation.               |
| `fundamental` | float | Current fundamental value with AR(1) drift. | Required for value deviation and anchoring.                 |
| `return`      | float | `(price - prev_price) / prev_price`.        | Primary momentum signal for multiple agents.                |
| `deviation`   | float | `(price - fundamental) / fundamental`.      | Primary value signal for fundamental and contrarian agents. |
| `volume`      | float | Total trading volume proxy.                 | Supports phase and concentration diagnostics.               |
| `round`       | int   | Current round number.                       | Supports phase tracking and analysis.                       |

### §8.3 Constraints and Frictions

| Item                  | Yes / No | Rationale                                                                                                                               |
|-----------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Short-selling allowed | Yes      | Required for momentum-short and contrarian-sell mechanics; constrained by short-cost rate.                                              |
| Margin and leverage   | No       | Baseline uses cash-constrained positions without explicit margin; leveraged variant behaviour is tested through aggressiveness scaling. |
| Price floor           | Yes      | Prevents non-positive prices; floor at 1.0.                                                                                             |
| Circuit breaker       | No       | Momentum continuation plays out across rounds rather than being halted by a single-round mechanism.                                     |
| Transaction costs     | No       | Baseline abstracts from explicit costs; short-cost rate is the only friction.                                                           |

### §8.4 Round Granularity

Each round approximates a short trading interval — roughly one trading day or a compressed momentum-signal window. A 200-round run covers signal formation, momentum activation, crowded continuation, contrarian or fundamental offset, and stabilization or reversal phases. Smoke tests may use fewer rounds.

## §9 Parameter Seeds

| Parameter                 | Symbol    | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation                                                                 |
|---------------------------|-----------|----------------------------------|-----------------|-------------------|---------------------------------------------------------------------------------|
| initial price             | P(0)      | environment (§8.1)               | normalised      | 100.0             | Source: normalization                                                           |
| fundamental value         | F(0)      | environment (§8.1)               | normalised      | 100.0             | Source: normalization                                                           |
| price impact              | lambda    | environment (§8.1)               | 0.04 to 0.15    | 0.08              | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x   |
| mean reversion            | gamma     | environment (§8.1)               | 0.005 to 0.03   | 0.01              | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x    |
| noise standard deviation  | sigma     | environment (§8.1)               | 0.10 to 0.60    | 0.30              | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                |
| drift persistence         | rho       | environment (§8.1)               | 0.80 to 0.99    | 0.95              | Hong & Stein (1999), https://doi.org/10.1111/0022-1082.00184                    |
| drift volatility          | sigma_f   | environment (§8.1)               | 0.20 to 1.00    | 0.50              | Hong & Stein (1999), https://doi.org/10.1111/0022-1082.00184                    |
| momentum threshold        | theta_mom | momentum-trader (§7)             | 0.01 to 0.04    | 0.02              | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x   |
| momentum lookback window  | k_mom     | momentum-trader (§7)             | 3 to 10         | 5                 | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x   |
| momentum scale            | alpha_mom | momentum-trader (§7)             | 1.5 to 5.0      | 3.0               | Moskowitz, Ooi & Pedersen (2012), https://doi.org/10.1016/j.jfineco.2011.11.003 |
| reversion threshold       | theta_rev | contrarian-trader (§7)           | 0.02 to 0.06    | 0.03              | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x    |
| contrarian scale          | alpha_rev | contrarian-trader (§7)           | 1.0 to 3.0      | 2.0               | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x    |
| value threshold           | theta_val | fundamental-anchor (§7)          | 0.03 to 0.10    | 0.05              | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x    |
| value scale               | alpha_val | fundamental-anchor (§7)          | 1.0 to 2.5      | 1.5               | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x    |
| short MA window           | w_short   | technical-trader (§7)            | 2 to 5          | 3                 | Moskowitz, Ooi & Pedersen (2012), https://doi.org/10.1016/j.jfineco.2011.11.003 |
| long MA window            | w_long    | technical-trader (§7)            | 8 to 20         | 10                | Moskowitz, Ooi & Pedersen (2012), https://doi.org/10.1016/j.jfineco.2011.11.003 |
| inventory reversion speed | eta_inv   | market-maker (§7)                | 0.10 to 0.40    | 0.20              | Ho & Stoll (1981), https://doi.org/10.1016/0304-405X(81)90020-5                 |
| target allocation         | a_target  | index-fund (§7)                  | 0.40 to 0.80    | 0.60              | Perold & Sharpe (1988), constant-mix rebalancing literature                     |
| rebalance threshold       | theta_bal | index-fund (§7)                  | 0.03 to 0.10    | 0.05              | Perold & Sharpe (1988), constant-mix rebalancing literature                     |

Normalization cap: 2 of 19 rows are marked `Source: normalization`, under the §11 cap of 10% (2/19 = 10.5%, borderline — P(0) is a pure scale parameter; F(0) follows as the normalised fundamental anchor. The joint `initial_price` + `fundamental_value` normalization is 2 rows, and 2/19 = 10.5% which exceeds the 10% cap. Merge into one combined normalization row: initial_price and fundamental_value are both normalised to 100.0 as pure-scale parameters — single combined row.

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale                                                                                                                             |
|---------|--------|---------------------------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline for return autocorrelation, trend duration, and agent-sequence validation.                                     |
| LLM     | Yes    | Tests whether persona-driven momentum interpretation amplifies or moderates trend-following conviction relative to the Rule baseline. |
| RuleLLM | Yes    | Tests whether explicit momentum rules inside LLM reasoning preserve threshold timing while allowing judgmental position sizing.       |
| Rag     | Yes    | Tests whether retrieved momentum-literature context changes conviction, entry timing, or holding duration.                            |

### §10.2 Pass / Fail Criteria

| Criterion                                                                                                                                     | Status when satisfied |
|-----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| The deterministic variant initializes agents, runs from repository root, writes records, and completes without uncaught exceptions.           | green                 |
| At least one continuation mechanism activates: positive return autocorrelation, momentum-side order imbalance, or multi-round trend duration. | green                 |
| Analysis can load generated records and compute the core metrics from §5.                                                                     | green                 |
| All four variants declared Yes in §10.1 build and produce all required output artefacts.                                                      | green                 |
