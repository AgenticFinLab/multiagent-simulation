# HerdEffect

## §1 Meta

| Field       | Content                                                                                                                  |
|-------------|--------------------------------------------------------------------------------------------------------------------------|
| Name        | HerdEffect                                                                                                               |
| Domain      | finance                                                                                                                  |
| Phenomenon  | Emergent herding arises when heterogeneous investors independently react to shared price-return signals and converge.     |
| Pipeline    | masim/skills/create-simulation-pipeline.md                                                                               |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                                  |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon starts when random order flow or a small public price move creates a positive return in a risky asset whose price is initially close to fundamental value. No agent directly observes or copies another investor's decision. The trigger is a shared market signal: price, return, volume, and net demand become visible to all investors through the market broadcast. This signal is strong enough to activate momentum-oriented strategies before stabilising investors can fully absorb it.

### §2.2 Mechanism

The amplification mechanism is an emergent positive-feedback herding loop. Noise trading initiates a price move, momentum investors buy because returns are positive, aggressive investors add acceleration-sensitive demand, and risk-averse investors reduce exposure as volatility rises. The aggregate result resembles crowd imitation even though each agent follows its own rule and no explicit HerdingInvestor exists. Contrarian investors resist the movement through a fundamental anchor, but their capped order sizes make them an incomplete stabilising force during the acceleration phase.

### §2.3 Participants

The causal participants are momentum investors, contrarian investors, risk-averse investors, noise traders, aggressive investors, and a stock-market coordinator. Momentum and aggressive investors are the primary converging demand sources. Noise traders provide stochastic initial shocks, while risk-averse investors create early-exit pressure when volatility rises. Contrarian investors read fundamental value from their own parameters and provide the mean-reversion force that ends the herd episode.

### §2.4 Resolution

The episode resolves when price becomes sufficiently stretched from the fundamental anchor, volatility rises, and stabilising or exit pressure overwhelms momentum demand. Contrarian investors sell overvaluation, risk-averse investors reduce target exposure, and aggressive momentum demand weakens once acceleration turns negative. The same return signal that aligned buying can align selling during reversal. The final state is a correction toward the fundamental value, with possible drawdown after the momentum peak.

## §3 Research Goals

1. Can heterogeneous investors generate statistically visible herd-like momentum episodes without an explicit imitation agent?
2. Does weakening MomentumInvestor or AggressiveInvestor reduce the Emergent Momentum Index and momentum-phase contribution share?
3. How sensitive are herding intensity and reversal depth to `supply_elasticity`, `lambda_price`, `kappa`, and `accel_bonus`?
4. Does RiskAverseInvestor reduce exposure before the price peak often enough to validate the mean-variance early-exit mechanism?
5. Do Rule, LLM, RuleLLM, and Rag variants differ in EMI, MDD, HVR, ACC, REI, and final wealth dispersion?

## §4 Theoretical Anchors

### §4.1 Positive Feedback Trading and Momentum

| Field                     | Content                                                                                                                                                                                               |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457-510. https://doi.org/10.2307/2534436                                                   |
| Key mechanism (≤30 words) | Rising prices attract additional buying, so independent trend-following rules can align orders and amplify price movement.                                                                            |
| Key equation              | `Q_mom(t) = beta * r(t) * cash / [P(t) * (1 + lambda_price * r(t))]`, where `r(t)` is the latest return.                                 |
| Motivates agent           | momentum-investor                                                                                                                                                                                     |
| Parameter implication     | `lambda_price` in [0.5, 2.0] and `beta` in [0.1, 0.5] scale momentum demand.                                                            |

### §4.2 Contrarian Reversal and Fundamental Anchoring

| Field                     | Content                                                                                                                                                                                |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                 |
| Key mechanism (≤30 words) | Overreaction eventually reverses as value-oriented investors sell overvaluation or buy undervaluation around a fundamental anchor.                                                     |
| Key equation              | `Q_contra(t) = beta * (F - P(t)) / P(t) * cash / bid_price`, where `F` is the agent's fundamental value.                                                                               |
| Motivates agent           | contrarian-investor                                                                                                                                                                   |
| Parameter implication     | `fundamental` near 100, `beta` in [0.1, 0.5], and `noise_std` in [0.1, 5.0] govern stabilising pressure.                                                                               |

### §4.3 Mean-Variance Risk Reduction

| Field                     | Content                                                                                                                                                                    |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Markowitz, H. (1952). Portfolio selection. *Journal of Finance*, 7(1), 77-91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x                                           |
| Key mechanism (≤30 words) | Risk-averse investors reduce exposure as variance rises, creating early exit pressure before momentum episodes peak.                                                       |
| Key equation              | `target_qty(t) = k / Var(P[t-lookback:t]) * cash / P(t)`, with trade size `0.30 * (target_qty - position)`.                                                                |
| Motivates agent           | risk-averse-investor                                                                                                                                                       |
| Parameter implication     | `k` in [0.1, 500] and `lookback` in [3, 10] determine volatility sensitivity.                                                                                               |

### §4.4 Noise Trader Risk

| Field                     | Content                                                                                                                                                                                               |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x |
| Key mechanism (≤30 words) | Noise orders create non-fundamental price moves that rational and momentum investors react to, making risk endogenous.                                                                                |
| Key equation              | `Q_noise(t) = N(0, qty_noise_std) - position * position_mean_reversion`, and `bid_price = P(t) + N(0, price_noise_std)`.                                                                             |
| Motivates agent           | noise-trader                                                                                                                                                                                         |
| Parameter implication     | `price_noise_std` in [1.0, 5.0], `qty_noise_std` in [5.0, 20.0], and `position_mean_reversion` in [0.1, 0.4] govern stochastic triggering.                                                          |

### §4.5 Institutional Herding and Acceleration Chasing

| Field                     | Content                                                                                                                                                                      |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Nofsinger, J. R., & Sias, R. W. (1999). Herding and feedback trading by institutional and individual investors. *Journal of Finance*, 54(6), 2263-2295. https://doi.org/10.1111/0022-1082.00188 |
| Key mechanism (≤30 words) | Institutional-style momentum strategies can converge on the same public return signal and amplify acceleration.                                                              |
| Key equation              | `Q_agg(t) = beta * r(t) * cash / [P(t) * (1 + kappa * r(t))] + accel_bonus * acceleration(t)`.                                                                               |
| Motivates agent           | aggressive-investor                                                                                                                                                         |
| Parameter implication     | `kappa` in [1.0, 4.0], `beta` in [0.2, 0.6], and `accel_bonus` in [0.3, 2.0] govern acceleration-driven herding.                                                            |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                   | Quantitative range                                  | Citation                                                                                                         | Acceptance metric                                  |
|----|---------------------------------------------------------------------------------------|-----------------------------------------------------|------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| F1 | Sustained positive-return episodes emerge beyond noise-driven fluctuations.           | `0.08 <= EMI <= 0.20`                               | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                   | `analysis.py: emergent_momentum_index()` in range  |
| F2 | Momentum and aggressive investors jointly dominate momentum-phase trading volume.      | `ACC_momentum + ACC_aggressive >= 0.50`             | Grinblatt, Titman & Wermers (1995), AER 85(5), 1088-1105                                                        | `analysis.py: agent_convergence_contribution()`    |
| F3 | Risk-averse investors exit before the local price peak in many momentum episodes.     | `REI >= 0.40`                                       | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x                                            | `analysis.py: risk_averse_early_exit_index()`      |
| F4 | Herding episodes have higher volatility than quiet periods.                           | `HVR >= 1.5` and target range `[1.5, 3.0]`          | Nofsinger & Sias (1999), https://doi.org/10.1111/0022-1082.00188                                                | `analysis.py: herding_volatility_ratio()`          |
| F5 | Momentum episodes are followed by a meaningful reversal or drawdown.                  | `0.10 <= MDD <= 0.30`                               | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                                    | `analysis.py: maximum_drawdown()` in range         |

## §6 Historical / Empirical Anchors

### §6.1 US Dot-Com Momentum Herding, 1998-2000

| Field             | Content                                                                                                                                                                              |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | NASDAQ and internet-stock momentum herding, 1998-2000.                                                                                                                               |
| Trigger           | Revenue-less internet IPOs and positive return feedback attracted mutual funds, hedge funds, and retail speculators.                                                                 |
| Quantitative arc  | NASDAQ 100 rose several-fold before the 2000 peak and then suffered a major drawdown.                                                                                                |
| Agent mapping     | Noise traders initiate shocks, momentum investors follow returns, aggressive investors amplify acceleration, risk-averse investors exit as variance rises, and contrarian investors resist overvaluation. |
| Primary source(s) | Brunnermeier, M. K., & Nagel, S. (2004). Hedge funds and the technology bubble. *Journal of Finance*, 59(5), 2013-2040. https://doi.org/10.1111/j.1540-6261.2004.00690.x             |

### §6.2 Bitcoin FOMO Rally, 2020-2021

| Field             | Content                                                                                                                                                 |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Bitcoin retail and institutional momentum rally, October 2020-November 2021.                                                                            |
| Trigger           | Institutional adoption news and retail FOMO created repeated positive-return signals.                                                                    |
| Quantitative arc  | Bitcoin rose from roughly $10,000 to about $69,000 before a large reversal.                                                                              |
| Agent mapping     | Aggressive and momentum investors map to leveraged crypto traders and trend followers; noise traders map to retail FOMO; contrarians map to valuation-aware sellers. |
| Primary source(s) | Cong, L. W., Li, Y., & Wang, N. (2021). Tokenomics: Dynamic adoption and valuation. *Review of Financial Studies*, 34(3), 1105-1155. https://doi.org/10.1093/rfs/hhaa089 |

### §6.3 Mutual Fund Herding in US Growth Stocks, 1975-1984

| Field             | Content                                                                                                                                                           |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Mutual fund herding in US growth stocks, documented across 1975-1984 holdings.                                                                                    |
| Trigger           | Quarterly rebalancing and past-winner buying caused independent funds to buy the same high-return stocks.                                                         |
| Quantitative arc  | Momentum-oriented funds and herded growth stocks generated positive abnormal returns before reversal pressure emerged.                                             |
| Agent mapping     | Momentum investors map to mutual funds; aggressive investors map to high-conviction growth funds; contrarians map to value funds; noise traders map to retail flow. |
| Primary source(s) | Grinblatt, M., Titman, S., & Wermers, R. (1995). Momentum investment strategies, portfolio performance, and herding. *American Economic Review*, 85(5), 1088-1105. |

## §7 Agent Roster

| Agent name (kebab)     | Real-world counterpart                    | Theory family (§4 anchor)                                      | Domain role       | Primary signals                         | Intent line                                                                                                  | Expected pool match                                   |
|------------------------|-------------------------------------------|----------------------------------------------------------------|-------------------|-----------------------------------------|--------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| momentum-investor      | momentum mutual fund / trend follower     | Positive Feedback Trading and Momentum (§4.1)                  | Destabilising     | price, return, cash, position           | Converts positive returns into demand and creates shared-signal convergence without direct imitation.        | masim/agents/defines/finance/momentum-investor.md     |
| contrarian-investor    | value investor / mean-reversion trader    | Contrarian Reversal and Fundamental Anchoring (§4.2)           | Stabilising       | price, fundamental, cash, position      | Trades against price-fundamental gaps and provides the reversal force after herd episodes.                  | masim/agents/defines/finance/contrarian-investor.md   |
| risk-averse-investor   | mean-variance portfolio manager           | Mean-Variance Risk Reduction (§4.3)                            | Stabilising exit  | price history, variance, cash, position | Reduces target exposure as volatility rises, creating early-exit pressure before the peak.                  | masim/agents/defines/finance/risk-averse-investor.md  |
| noise-trader           | retail noise trader / uninformed flow     | Noise Trader Risk (§4.4)                                       | Triggering noise  | price, position, random draws           | Injects stochastic order flow that can start positive-return runs.                                           | masim/agents/defines/finance/noise-trader.md          |
| aggressive-investor    | leveraged growth fund / acceleration chaser | Institutional Herding and Acceleration Chasing (§4.5)        | Destabilising     | price, return, acceleration, cash       | Amplifies sustained price acceleration with larger bid aggressiveness and order caps.                       | masim/agents/defines/finance/aggressive-investor.md   |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a stock-market coordinator with order-book-style clearing. Price follows `P(t+1) = P(t) + supply_elasticity * net_demand + mean_reversion * (fundamental_value - P(t)) + epsilon(t)`, where `epsilon(t)` is market noise. Buy and sell orders are represented by signed quantities and bid prices. The design deliberately uses shared market-return broadcasts rather than direct peer imitation.

### §8.2 Information Broadcast

Each round broadcasts `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, and `round`. The market does not broadcast public fundamental or deviation fields. Contrarian investors read fundamental value from their own extras. This separation is required so herding emerges from common price-return signals rather than explicit fundamental consensus.

### §8.3 Constraints and Frictions

MomentumInvestor has a +/-50 share position cap, ContrarianInvestor has a +/-50 share cap, RiskAverseInvestor has a +/-20 share cap, AggressiveInvestor has a +/-80 share cap, and NoiseTrader mean-reverts its inventory stochastically. All investors update cash and position in their decision path and submit `{bid_price, quantity, strategy, cash, position}` orders to the coordinator.

### §8.4 Round Granularity

One round represents a compressed trading interval in which the market first broadcasts the latest state, investors compute bids from that shared state, and the market clears aggregated signed demand. The time scale is calibrated to identify short momentum episodes, their peak, and subsequent reversal rather than literal calendar days.

## §9 Parameter Seeds

| Parameter               | Symbol | Belongs to (agent / environment) | Empirical range            | Candidate default | Source citation                                                                                     |
|-------------------------|--------|----------------------------------|----------------------------|-------------------|-----------------------------------------------------------------------------------------------------|
| initial_price           | P0     | environment (§8.1)               | 50-200                     | 100.0             | Source: simulation-bases.md §6 normalization                                                        |
| fundamental_value       | F      | environment (§8.1)               | 80-120                     | 100.0             | Source: simulation-bases.md §6 stable fundamental assumption                                        |
| supply_elasticity       | alpha  | environment (§8.1)               | 0.01-0.20                  | 0.1               | Source: simulation-bases.md §6 order-book depth analog                                              |
| mean_reversion          | gamma  | environment (§8.1)               | 0.01-0.10                  | 0.02              | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                       |
| noise_std               | sigma  | environment (§8.1)               | 0.1-2.0                    | 0.5               | De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x                          |
| initial_cash            | C0     | all investors (§7)               | 10000-scale normalization  | 10000.0           | Source: simulation-bases.md §6 normalization                                                        |
| initial_position        | q0     | all investors (§7)               | zero-start normalization   | 0.0               | Source: simulation-bases.md §6 normalization                                                        |
| lambda_price            | lambda | momentum-investor (§7)           | 0.5-2.0                    | 0.5               | Shiller (1984), https://doi.org/10.2307/2534436                                                     |
| beta                    | beta_m | momentum-investor (§7)           | 0.1-0.5                    | 0.3               | Grinblatt et al. (1995), AER 85(5), 1088-1105                                                       |
| fundamental             | F_i    | contrarian-investor (§7)         | same as market fundamental | 100.0             | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                       |
| noise_std               | sigma_b | contrarian-investor (§7)        | 0.1-5.0                    | 0.5               | Source: simulation-bases.md §6 bid price uncertainty                                                |
| beta                    | beta_c | contrarian-investor (§7)         | 0.1-0.5                    | 0.5               | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                       |
| k                       | k      | risk-averse-investor (§7)        | 0.1-500                    | 0.5               | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x                               |
| lookback                | L      | risk-averse-investor (§7)        | 3-10 rounds                | 5                 | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x                               |
| price_noise_std         | sigma_p | noise-trader (§7)               | 1.0-5.0                    | 2.0               | De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x                          |
| qty_noise_std           | sigma_q | noise-trader (§7)               | 5.0-20.0                   | 5.0               | De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x                          |
| position_mean_reversion | rho_q  | noise-trader (§7)                | 0.1-0.4                    | 0.1               | De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x                          |
| kappa                   | kappa  | aggressive-investor (§7)         | 1.0-4.0                    | 1.0               | Nofsinger & Sias (1999), https://doi.org/10.1111/0022-1082.00188                                  |
| beta                    | beta_a | aggressive-investor (§7)         | 0.2-0.6                    | 0.5               | Nofsinger & Sias (1999), https://doi.org/10.1111/0022-1082.00188                                  |
| accel_bonus             | a      | aggressive-investor (§7)         | 0.3-2.0                    | 0.3               | Nofsinger & Sias (1999), https://doi.org/10.1111/0022-1082.00188                                  |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence)                                                                  |
|---------|--------|------------------------------------------------------------------------------------------|
| Rule    | Yes    | Provides the deterministic baseline for emergent herding from explicit formulas.          |
| LLM     | Yes    | Tests whether persona-only reasoning moderates or reproduces shared-signal convergence.   |
| RuleLLM | Yes    | Tests whether rule-constrained language reasoning preserves the baseline mechanism.        |
| Rag     | Yes    | Tests whether retrieval of herding and momentum literature changes bid aggressiveness.    |

### §10.2 Pass / Fail Criteria

| Criterion                                                                        | Status when satisfied |
|----------------------------------------------------------------------------------|-----------------------|
| Emergent Momentum Index falls in the target range or calibrated deviations are reported. | green                 |
| MomentumInvestor and AggressiveInvestor jointly account for at least half of momentum-phase volume. | green                 |
| RiskAverseInvestor early-exit behaviour is measurable before price peaks.         | green                 |
| Herding volatility ratio exceeds quiet-period volatility by at least 1.5x.        | green                 |
| All built variants expose metrics needed for cross-variant comparison.            | green                 |
