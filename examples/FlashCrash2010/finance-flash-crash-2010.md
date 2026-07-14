# FlashCrash2010

## §1 Meta

| Field       | Content                                                                                                                              |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Name        | FlashCrash2010                                                                                                                       |
| Domain      | finance                                                                                                                              |
| Phenomenon  | HFT market-maker withdrawal and order-book depth collapse amplify a single large sell programme into a system-wide liquidity vacuum. |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                                                                                           |
| Target Spec | masim/skills/define-simulation-scenario-skill.md                                                                                     |

## §2 Phenomenon Statement

### §2.1 Trigger

The May 6, 2010 Flash Crash was triggered by a large institutional sell programme (Waddell & Reed, E-mini S&P 500 futures) that exhausted order-book depth in a market already exhibiting elevated volatility. The trigger is not a fundamental valuation shock but a liquidity-supply collapse initiated by a single large directional order interacting with a fragile order-book structure.

### §2.2 Mechanism

The core mechanism is a positive feedback loop between HFT market-maker withdrawal, order-book depth collapse, and price-impact amplification. When HFT market makers detect elevated price velocity, they widen spreads and then withdraw entirely, collapsing the depth denominator in the price-impact formula. This amplifies the price impact of each subsequent sell order, triggering momentum chasers and stop-loss cascades that further deplete depth.

### §2.3 Participants

The causal participants are HFT market makers (liquidity provision and withdrawal), momentum chasers (trend amplification), stop-loss traders (cascade selling), fundamental traders (stabilisation and recovery), and noise traders (background flow). HFT market makers are the primary amplification mechanism via withdrawal; momentum chasers accelerate the decline; stop-loss traders create discrete cascade waves; fundamental traders provide the recovery force.

### §2.4 Resolution

The crash resolves when fundamental traders recognise undervaluation and provide sufficient buy demand to overwhelm the remaining sell flow. As price stabilises, HFT market makers detect reduced velocity, return to the market, rebuild depth, and normalise spreads. The recovery is rapid (approximately 20 minutes in the real event) because the fundamental value was never impaired.

## §3 Research Goals

1. Can the interaction of HFT withdrawal, momentum chasing, and stop-loss cascades produce a >5% crash within a short window (analogous to 36 minutes)?
2. Does removing HFT market makers from the simulation eliminate the depth-collapse amplification and reduce crash severity?
3. How sensitive is crash depth and recovery time to the `withdrawal_threshold` and `price_impact` (lambda) parameters?
4. Do stop-loss traders create distinct cascade waves, and does varying `stop_percentage` across instances produce multi-wave structure?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in crash timing, depth collapse ratio, and recovery speed?

## §4 Theoretical Anchors

### §4.1 HFT Stress Response and Liquidity Withdrawal

| Field                     | Content                                                                                                                                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967-998. https://doi.org/10.1111/jofi.12498 |
| Key mechanism (≤30 words) | HFT market makers detect stress via price velocity and withdraw liquidity, collapsing order-book depth and amplifying price impact.                                                                      |
| Key equation              | `stressed = velocity > withdrawal_threshold`; withdrawal sets `quantity = 0` and `provides_liquidity = False`.                                                                                           |
| Motivates agent           | hft-market-maker                                                                                                                                                                                         |
| Parameter implication     | `withdrawal_threshold` in [0.005, 0.03] controls when HFT exits; staggered across instances.                                                                                                             |

### §4.2 Positive-Feedback Momentum Trading

| Field                     | Content                                                                                                                                                                                                                       |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.2307/2328662 |
| Key mechanism (≤30 words) | Trend-following traders amplify directional price moves by buying winners and selling losers, creating self-reinforcing momentum.                                                                                             |
| Key equation              | `velocity = (P[-1] - P[-lookback]) / P[-lookback]`; trade if `                                                                                                                                                                |
| Motivates agent           | momentum-chaser                                                                                                                                                                                                               |
| Parameter implication     | `lookback_window` in [3, 10] and `entry_threshold` in [0.001, 0.02].                                                                                                                                                          |

### §4.3 Fundamental Value Anchoring and Excess Volatility

| Field                     | Content                                                                                                                                                                                   |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shiller, R. J. (1981). Do stock prices move too much to be justified by subsequent changes in dividends? *American Economic Review*, 71(3), 421-436. https://doi.org/10.1257/aer.71.3.421 |
| Key mechanism (≤30 words) | Fundamental value serves as a gravity anchor; value traders buy undervaluation and sell overvaluation, providing the crash recovery force.                                                |
| Key equation              | `deviation = (P - F) / F`; buy if `deviation < -value_trigger`, sell if `deviation > value_trigger`.                                                                                      |
| Motivates agent           | fundamental-trader                                                                                                                                                                        |
| Parameter implication     | `value_trigger` in [0.03, 0.10] and `order_size` in [200, 1000].                                                                                                                          |

### §4.4 Stop-Loss Cascade and Predatory Trading

| Field                     | Content                                                                                                                                                    |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825-1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x |
| Key mechanism (≤30 words) | Pre-set stop-loss levels trigger correlated forced selling, creating cascading sell pressure that is predictable and exploitable.                          |
| Key equation              | `stop_level = entry_price * (1 - stop_percentage)`; sell entire position when `price <= stop_level`.                                                       |
| Motivates agent           | stop-loss-trader                                                                                                                                           |
| Parameter implication     | `stop_percentage` in [0.02, 0.08] varied across instances → multi-wave cascade.                                                                            |

### §4.5 Noise Trading and Background Liquidity

| Field                     | Content                                                                                                           |
|---------------------------|-------------------------------------------------------------------------------------------------------------------|
| Full citation             | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| Key mechanism (≤30 words) | Uninformed random order flow provides background volume and prevents trivial market microstructure.               |
| Key equation              | `trade ~ Bernoulli(trade_probability)`; direction uniform random; size in [min_order, max_order].                 |
| Motivates agent           | noise-trader                                                                                                      |
| Parameter implication     | `trade_probability` in [0.03, 0.10] and order sizes in [100, 500].                                                |

### §4.6 Equilibrium Fast Trading and Spread Dynamics

| Field                     | Content                                                                                                                                                                  |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Biais, B., Foucault, T., & Moinas, S. (2015). Equilibrium fast trading. *Journal of Financial Economics*, 116(2), 292-313. https://doi.org/10.1016/j.jfineco.2015.03.004 |
| Key mechanism (≤30 words) | Fast traders widen spreads under stress as adverse selection risk rises; withdrawal creates endogenous liquidity crises.                                                 |
| Key equation              | `spread = base_spread + volatility * 0.5`; multiplied by HFT withdrawal and volatility factors.                                                                          |
| Motivates agent           | hft-market-maker (spread dynamics)                                                                                                                                       |
| Parameter implication     | Spread widens up to 0.05 cap; stress multipliers ×3 (HFT withdrawal) and ×5 (high volatility).                                                                           |

### §4.7 Synchronised Liquidity Withdrawal

| Field                     | Content                                                                                                                               |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173-204. https://doi.org/10.1111/1468-0262.00393 |
| Key mechanism (≤30 words) | Coordination risk prevents early correction; synchronised withdrawal creates sudden liquidity vacuums.                                |
| Key equation              | Staggered `withdrawal_threshold` across HFT instances creates progressive withdrawal cascade.                                         |
| Motivates agent           | hft-market-maker (staggered withdrawal)                                                                                               |
| Parameter implication     | Diversity in `withdrawal_threshold` [0.005, 0.03] across 3-5 HFT instances.                                                           |

### §4.8 Order-Book Depth Collapse (Official Event Reconstruction)

| Field                     | Content                                                                                                                                                                         |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | CFTC & SEC (2010). Findings regarding the market events of May 6, 2010: Report of the staffs of the CFTC and SEC to the Joint Advisory Committee on Emerging Regulatory Issues. |
| Key mechanism (≤30 words) | Large sell programme exhausts order-book depth; reduced depth amplifies price impact of subsequent orders.                                                                      |
| Key equation              | `Depth(t) = base_depth * max(stress_factor, 0.1)` with stress cascading from volatility and HFT participation.                                                                  |
| Motivates agent           | Market (environment)                                                                                                                                                            |
| Parameter implication     | `base_depth` in [2000, 10000]; `price_impact` in [0.00005, 0.05].                                                                                                               |

## §5 Stylized Facts

| #  | Fact                                                                                                                  | Acceptance metric                                             | Source                                   |
|----|-----------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|------------------------------------------|
| F1 | The crash produces a drawdown exceeding 5% from pre-crash price within a compressed time window.                      | `max_drawdown(price_history) >= 0.05`                         | Kirilenko et al. (2017); CFTC-SEC (2010) |
| F2 | Order-book depth collapses to below 20% of baseline during the crash phase.                                           | `depth_collapse_ratio(depth_history, base_depth) <= 0.20`     | CFTC-SEC (2010)                          |
| F3 | Spreads widen by at least 5x normal during the stress period.                                                         | `spread_widening_factor(spread_history) >= 5.0`               | Biais et al. (2015); CFTC-SEC (2010)     |
| F4 | HFT market makers withdraw for multiple consecutive rounds during the cascade.                                        | `hft_withdrawal_rounds(orders) >= 3`                          | Kirilenko et al. (2017)                  |
| F5 | Stop-loss traders create at least 2 distinct cascade waves (rounds with stop-loss selling separated by quiet rounds). | `len(cascade_trigger_rounds(orders)) >= 2`                    | Brunnermeier & Pedersen (2005)           |
| F6 | Price recovers to within 2% of fundamental value after the crash.                                                     | `recovery_time(price_history, trough, fundamental, 0.02) > 0` | CFTC-SEC (2010)                          |

## §6 Historical / Empirical Anchors

| #  | Event                                     | Date       | Key facts                                                                              | Source                       |
|----|-------------------------------------------|------------|----------------------------------------------------------------------------------------|------------------------------|
| H1 | May 6, 2010 Flash Crash                   | 2010-05-06 | DJIA fell ~9% in 36 minutes; recovered in ~20 minutes; triggered by W&R sell programme | CFTC-SEC Joint Report (2010) |
| H2 | Individual stock flash crashes (P&G etc.) | 2010-05-06 | Several stocks fell >50% in minutes due to quote stuffing and depth collapse           | CFTC-SEC Joint Report (2010) |
| H3 | Knight Capital algo error                 | 2012-08-01 | KCG stock fell 70% in 45 min from runaway algorithm; related depth-collapse mechanism  | SEC investigation (2013)     |
| H4 | 2015 ETF Flash Crash                      | 2015-08-24 | ETFs fell 30% on market-on-open imbalance; similar HFT withdrawal dynamics             | SEC (2015)                   |

## §7 Agent Roster

| # | Archetype (kebab)  | Theory Family   | Market Role                                       | Time Horizon | Risk Tolerance    | Primary Signals                  |
|---|--------------------|-----------------|---------------------------------------------------|--------------|-------------------|----------------------------------|
| 1 | hft-market-maker   | microstructure  | stabilising (normal) / destabilising (withdrawal) | ultra-short  | low               | price velocity, volatility       |
| 2 | momentum-chaser    | behavioral      | destabilising                                     | short        | high              | price momentum, lookback returns |
| 3 | fundamental-trader | fundamental     | stabilising                                       | medium       | moderate          | price-fundamental deviation      |
| 4 | stop-loss-trader   | risk-management | destabilising (cascade)                           | one-shot     | none (mechanical) | price vs stop-level              |
| 5 | noise-trader       | behavioral      | neutral                                           | random       | high              | none (random)                    |

## §8 Environment Specification

### §8.1 Price Formation

```
P(t+1) = P(t) + lambda * NetOrderFlow / Depth(t) + gamma * (F - P(t)) + epsilon
```

Where:
- `lambda` = price_impact coefficient (0.05 default)
- `gamma` = mean_reversion coefficient (0.02 default)
- `epsilon ~ N(0, noise_std^2)` with noise_std = 0.01
- `Depth(t) = base_depth * max(stress_factor, 0.1)`

### §8.2 Stress Factor and Depth Dynamics

```
stress_factor = 1.0
if volatility > 0.01: stress_factor *= 0.5
if volatility > 0.02: stress_factor *= 0.3
if hft_participation < 0.30: stress_factor *= 0.5
```

### §8.3 Spread Model

```
spread = base_spread + volatility * 0.5
if hft_participation < 0.30: spread *= 3.0
if volatility > 0.02: spread *= 5.0
spread = min(spread, 0.05)
```

### §8.4 Information Broadcast

Broadcast payload: `{price, prev_price, return_pct, fundamental, deviation, spread, depth, volume, volatility, round}`

Order keys: `{bid_price, quantity, strategy, agent_type, provides_liquidity}`

### §8.5 Round Granularity

Six-phase round: Market.perceive (collect orders) → Market.decide (compute price) → Market.act (broadcast) → Investors.perceive (read market) → Investors.decide (compute orders) → Investors.act (send orders).

## §9 Parameter Seeds

| #  | Parameter              | Default | Empirical Range | Belongs to         | Source citation                |
|----|------------------------|---------|-----------------|--------------------|--------------------------------|
| 1  | initial_price          | 40.0    | 35-50           | Environment        | normalization                  |
| 2  | fundamental_value      | 40.0    | 38-42           | Environment        | normalization                  |
| 3  | base_depth             | 10000   | 2000-10000      | Environment        | CFTC-SEC (2010)                |
| 4  | price_impact (lambda)  | 0.05    | 0.00005-0.05    | Environment        | Kirilenko et al. (2017)        |
| 5  | mean_reversion (gamma) | 0.02    | 0.02-0.10       | Environment        | Shiller (1981)                 |
| 6  | noise_std              | 0.01    | 0.005-0.05      | Environment        | calibration                    |
| 7  | withdrawal_threshold   | 0.02    | 0.005-0.03      | hft-market-maker   | Kirilenko et al. (2017)        |
| 8  | normal_spread          | 0.0001  | 0.0001-0.001    | hft-market-maker   | Biais et al. (2015)            |
| 9  | stress_spread          | 0.005   | 0.001-0.01      | hft-market-maker   | Biais et al. (2015)            |
| 10 | inventory_limit        | 1000    | 500-2000        | hft-market-maker   | calibration                    |
| 11 | lookback_window        | 5       | 3-10            | momentum-chaser    | De Long et al. (1990)          |
| 12 | entry_threshold        | 0.001   | 0.001-0.02      | momentum-chaser    | De Long et al. (1990)          |
| 13 | position_multiplier    | 10000   | 5000-20000      | momentum-chaser    | calibration                    |
| 14 | value_trigger          | 0.05    | 0.03-0.10       | fundamental-trader | Shiller (1981)                 |
| 15 | order_size             | 500     | 200-1000        | fundamental-trader | calibration                    |
| 16 | stop_percentage        | 0.03    | 0.02-0.08       | stop-loss-trader   | Brunnermeier & Pedersen (2005) |
| 17 | entry_price            | 40.0    | 35-50           | stop-loss-trader   | normalization                  |
| 18 | trade_probability      | 0.05    | 0.03-0.10       | noise-trader       | Black (1986)                   |
| 19 | min_order              | 100     | 50-200          | noise-trader       | calibration                    |
| 20 | max_order              | 500     | 200-1000        | noise-trader       | calibration                    |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Notes                                                     |
|---------|--------|-----------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline with fixed thresholds              |
| LLM     | Yes    | LLM-driven investor decisions with persona prompts        |
| RuleLLM | Yes    | Hybrid: rule quantitative signals embedded in LLM prompts |
| Rag     | Yes    | RAG-augmented: historical flash crash knowledge retrieval |

### §10.2 Pass / Fail Criteria

1. Rule variant must produce max_drawdown >= 0.05 in a 200-round simulation.
2. Depth must collapse below 20% of base_depth during the cascade phase.
3. Recovery must occur (price returns within 2% of fundamental before round 200).
4. All four variants must compile cleanly, import cleanly, and complete a 5-round smoke run without exceptions.
