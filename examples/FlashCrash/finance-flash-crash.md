# FlashCrash — Scenario Target

## §1 Meta

| Field         | Content                                                |
|---------------|--------------------------------------------------------|
| Name          | FlashCrash                                             |
| Domain        | finance                                                |
| Requested By  | a77                                                    |
| Produced By   | polish-simulation-pipeline.md (Case B reverse-seed)    |
| Created       | 2025-07-18                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Status        | released                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

A flash crash begins when a large directional sell programme or sudden momentum signal arrives in a thin market. The initial move depletes standing liquidity faster than market makers replenish it. The trigger is mechanical (an order-flow imbalance), not fundamental news.

### §2.2 Mechanism

The core mechanism is a positive-feedback liquidity vacuum: falling prices cause market makers to withdraw, withdrawal raises effective price impact, higher impact accelerates further price decline, and stop-loss cascades add lumpy forced selling. High-frequency traders amplify the first move; algorithmic trend-followers sustain it; stop-loss orders create discrete downward jumps. Fundamental traders eventually recognise undervaluation and supply stabilising demand.

### §2.3 Participants

Six agent archetypes participate: high-frequency traders (fastest momentum amplifiers), market makers (liquidity providers that withdraw under stress), algorithmic traders (medium-speed trend followers), stop-loss traders (forced sellers at predetermined levels), fundamental traders (value buyers providing recovery force), and retail traders (uninformed background noise).

### §2.4 Resolution

The crash resolves when fundamental traders begin buying at deep discounts, absorbing excess sell pressure. Market makers gradually return as volatility falls below their withdrawal threshold. Price converges back toward fundamental value, though recovery may overshoot or undershoot temporarily.

## §3 Research Goals

1. Can heterogeneous agent rules reproduce a flash-crash pattern (>5% intraday drop within 10-20 rounds followed by partial recovery)?
2. Does market-maker withdrawal quantifiably amplify crash depth relative to a constant-liquidity baseline?
3. How sensitive is crash depth to the `low_liquidity_threshold` and `high_impact_multiplier` parameters?
4. Do stop-loss cascades produce discrete multi-wave selling or a smooth continuous decline?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in crash depth, recovery speed, and liquidity vacuum duration?

## §4 Theoretical Anchors

### §4.1 HFT Behaviour and Flash Crash Dynamics

| Field | Content |
|-------|---------|
| Full citation | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967-998. https://doi.org/10.1111/jofi.12498 |
| Key mechanism (≤30 words) | HFT market-makers withdraw under extreme price velocity, creating a "hot potato" liquidity vacuum that amplifies crashes. |
| Key equation | `short_momentum = (P(t) - P(t-k)) / P(t-k)`; signal drives rapid directional bets. |
| Motivates agent | high-frequency-trader |
| Parameter implication | `momentum_sensitivity` in [0.5, 3.0], `speed_advantage` in [1.2, 2.0], `lookback` in [2, 5] rounds. |

### §4.2 Market-Maker Liquidity Provision and Withdrawal

| Field | Content |
|-------|---------|
| Full citation | Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-633. https://doi.org/10.1111/j.1540-6261.1988.tb02607.x |
| Key mechanism (≤30 words) | Market makers provide liquidity in calm conditions but withdraw when short-term volatility exceeds their risk tolerance. |
| Key equation | `provides_liquidity = (abs(return) <= volatility_threshold)`; withdrawal raises `liquidity_factor`. |
| Motivates agent | market-maker |
| Parameter implication | `volatility_threshold` in [0.005, 0.02]; `base_liquidity` in [30, 100]. |

### §4.3 Positive-Feedback Trading

| Field | Content |
|-------|---------|
| Full citation | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.2307/2328395 |
| Key mechanism (≤30 words) | Trend-following algorithms amplify directional moves by buying past winners and selling past losers. |
| Key equation | `quantity = trend * trend_sensitivity * base_position_size * trend_multiplier`; clamped to ±40. |
| Motivates agent | algorithmic-trader |
| Parameter implication | `trend_sensitivity` in [0.5, 2.0], `trend_window` in [3, 10] rounds, `trend_multiplier` in [5, 15]. |

### §4.4 Predatory Trading and Stop-Loss Cascades

| Field | Content |
|-------|---------|
| Full citation | Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825-1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x |
| Key mechanism (≤30 words) | Stop-loss traders are forced sellers at predetermined price levels, creating lumpy cascade selling as successive stops trigger. |
| Key equation | `if price < recent_high * (1 - stop_loss_percent): sell_all()`; one-shot exit. |
| Motivates agent | stop-loss-trader |
| Parameter implication | `stop_loss_percent` in [0.02, 0.10]; varied across instances to create multi-wave cascades. |

### §4.5 Excess Volatility and Fundamental Value Anchoring

| Field | Content |
|-------|---------|
| Full citation | Shiller, R. J. (1981). Do stock prices move too much to be justified by subsequent changes in dividends? *American Economic Review*, 71(3), 421-436. https://doi.org/10.1257/aer.71.3.421 |
| Key mechanism (≤30 words) | Fundamental value acts as a gravitational anchor; value-motivated traders buy deep discounts and provide recovery force. |
| Key equation | `quantity = deviation * base_position_size * value_sensitivity * value_multiplier` when `deviation > value_threshold`. |
| Motivates agent | fundamental-trader |
| Parameter implication | `value_threshold` in [0.03, 0.10], `value_sensitivity` in [0.5, 2.0], `value_multiplier` in [5, 15]. |

### §4.6 Noise Trading

| Field | Content |
|-------|---------|
| Full citation | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| Key mechanism (≤30 words) | Noise traders provide random background volume without directional bias, preventing market from being trivially one-sided. |
| Key equation | `quantity = gauss(0, noise_std) + (-position_mean_reversion * position)`; clamped ±15. |
| Motivates agent | retail-trader |
| Parameter implication | `trade_frequency` in [1, 5] rounds, `noise_std` in [1.0, 8.0], `position_mean_reversion` in [0.05, 0.2]. |

## §5 Stylized Facts

| ID | Stylized Fact | Numeric Range | Source | Acceptance Metric |
|----|---------------|---------------|--------|-------------------|
| F1 | Intraday price drops of 5-10% within minutes without fundamental news | 5-12% crash depth | Kirilenko et al. (2017); CFTC-SEC (2010) | `crash_depth` in [0.05, 0.12] |
| F2 | Liquidity vacuum lasts 5-20 minutes (rounds in simulation) | 5-20 rounds | Kirilenko et al. (2017) | `liquidity_vacuum_duration` in [5, 20] |
| F3 | Stop-loss cascades produce multi-wave forced selling | Discrete selling waves | Brunnermeier & Pedersen (2005) | `stop_loss_cascade_volume` > 0 with multiple trigger rounds |
| F4 | Price recovery occurs within 20-30 minutes via fundamental buying | 10-30 rounds | CFTC-SEC (2010) | `recovery_speed` in [10, 30] |
| F5 | Liquidity providers withdraw by 60-100% during crash window | 0.6-1.0 withdrawal fraction | Kirilenko et al. (2017) | `liquidity_provider_withdrawal_fraction` in [0.6, 1.0] |

## §6 Historical / Empirical Anchors

| Event | Date | Magnitude | Duration | Key Cause | Source |
|-------|------|-----------|----------|-----------|--------|
| May 6, 2010 Flash Crash | 2010-05-06 | -9% DJIA | 36 min | W&R institutional sell + HFT withdrawal | Kirilenko et al. (2017) https://doi.org/10.1111/jofi.12498 |
| AAPL Mini Flash Crash | 2012-04-23 | -10% in seconds | <60s | Fat-finger algorithmic order | CFTC-SEC (2010) |
| ETF Flash Crash | 2015-08-24 | -30% (ETFs) | 30 min | Market-on-open imbalance + circuit breakers | SEC (2015) |

## §7 Agent Roster

| Agent (kebab) | Theory Family | Market Role | Time Horizon | Risk Tolerance | Information Asymmetry | Determinism |
|---------------|---------------|-------------|--------------|----------------|----------------------|-------------|
| high-frequency-trader | Microstructure (Kirilenko 2017) | Destabilising | Ultra-short | Medium-high | Price-history only | High (Rule) / Low (LLM) |
| market-maker | Microstructure (Grossman & Miller 1988) | Stabilising → Destabilising under stress | Short | Low | Price + volatility | High (Rule) / Medium (LLM) |
| algorithmic-trader | Behavioral (De Long et al. 1990) | Destabilising | Short-Medium | Medium | Trend signal | High (Rule) / Low (LLM) |
| stop-loss-trader | Microstructure (Brunnermeier & Pedersen 2005) | Destabilising (cascade) | N/A (triggered) | Very low (forced) | Price vs stop level | Very high |
| fundamental-trader | Value (Shiller 1981) | Stabilising | Medium-Long | Medium | Fundamental deviation | High (Rule) / Medium (LLM) |
| retail-trader | Noise (Black 1986) | Neutral | Low-frequency | Low | None (random) | Low |

## §8 Environment Specification

### §8.1 Price Formation

Liquidity-sensitive pricing:
```
P(t+1) = P(t) + base_price_impact * net_demand * liquidity_factor
         + mean_reversion * (fundamental - P(t)) + epsilon
```

Where `liquidity_factor = high_impact_multiplier` when `total_liquidity < low_liquidity_threshold`, otherwise `1.0 + (low_liquidity_threshold / total_liquidity - 1.0) * 0.5`.

### §8.2 Information Broadcast

Market broadcasts: `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, `liquidity`, `round`, `fundamental`.

### §8.3 Constraints and Frictions

- Cash constraint: buy quantity limited by available cash
- Position constraint: sell quantity limited by current position
- Market makers toggle `provides_liquidity` flag under stress
- Stop-loss traders exit completely once triggered (irreversible)

### §8.4 Round Granularity

Star topology: Market (coordinator) ↔ all investors. One perceive-decide-act cycle per round. 200 rounds for full experiment.

## §9 Parameter Seeds

| Parameter | Default | Range | Belongs to | Source |
|-----------|---------|-------|------------|--------|
| initial_price | 100.0 | 80-120 | Environment | normalization |
| fundamental_value | 100.0 | 90-110 | Environment | normalization |
| base_price_impact | 0.05 | 0.001-0.05 | Environment | simulation-bases.md §3 |
| base_liquidity | 50.0 | 50-150 | Environment | simulation-bases.md §3 |
| low_liquidity_threshold | 50.0 | 25-75 | Environment | simulation-bases.md §3 |
| high_impact_multiplier | 3.0 | 2.0-5.0 | Environment | simulation-bases.md §3 |
| mean_reversion | 0.02 | 0.01-0.05 | Environment | simulation-bases.md §3 |
| noise_std | 0.3 | 0.05-0.5 | Environment | simulation-bases.md §3 |
| momentum_sensitivity | 3.0 | 0.5-3.0 | high-frequency-trader | Kirilenko et al. (2017) |
| base_position_size (HFT) | 40.0 | 20-60 | high-frequency-trader | simulation-bases.md §4.1 |
| speed_advantage | 1.5 | 1.2-2.0 | high-frequency-trader | simulation-bases.md §4.1 |
| lookback (HFT) | 2 | 2-5 | high-frequency-trader | simulation-bases.md §4.1 |
| volatility_threshold | 0.02 | 0.005-0.02 | market-maker | Grossman & Miller (1988) |
| trend_sensitivity | 2.0 | 0.5-2.0 | algorithmic-trader | De Long et al. (1990) |
| trend_multiplier | 10 | 5-15 | algorithmic-trader | simulation-bases.md §4.3 |
| trend_window | 3 | 3-10 | algorithmic-trader | simulation-bases.md §4.3 |
| stop_loss_percent | 0.05 | 0.02-0.10 | stop-loss-trader | Brunnermeier & Pedersen (2005) |
| value_threshold | 0.10 | 0.03-0.10 | fundamental-trader | Shiller (1981) |
| value_sensitivity | 1.0 | 0.5-2.0 | fundamental-trader | simulation-bases.md §4.5 |
| value_multiplier | 10 | 5-15 | fundamental-trader | simulation-bases.md §4.5 |
| trade_frequency | 5 | 1-5 | retail-trader | Black (1986) |
| noise_std (retail) | 8.0 | 1.0-8.0 | retail-trader | simulation-bases.md §4.6 |
| position_mean_reversion | 0.1 | 0.05-0.2 | retail-trader | simulation-bases.md §4.6 |
| initial_cash | 10000.0 | 5000-20000 | All investors | normalization |
| initial_position (SL) | 50.0 | 20-100 | stop-loss-trader | simulation-bases.md §4.4 |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Notes |
|---------|--------|-------|
| Rule | Yes | Deterministic baseline; all agents use formula-based decisions |
| LLM | Yes | LLM-powered investors; market coordinator uses internal liquidity state |
| RuleLLM | Yes | Hybrid: LLM with embedded quantitative rules in prompts |
| Rag | Yes | RAG-augmented LLM with historical crash knowledge retrieval |

### §10.2 Pass / Fail Criteria

1. Rule variant must produce a flash-crash pattern with `crash_depth` in [0.05, 0.12] within 200 rounds.
2. `liquidity_vacuum_duration` must be in [5, 20] rounds when `high_impact_multiplier` >= 2.0.
3. Stop-loss cascade must produce measurable forced selling volume (`stop_loss_cascade_volume` > 100).
4. Recovery must occur within 30 rounds of trough (`recovery_speed` <= 30 or -1 if extended).
