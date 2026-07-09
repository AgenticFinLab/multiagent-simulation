# ReversalEffect — Scenario Target

## §1 Meta

| Field         | Content                                                                |
|---------------|------------------------------------------------------------------------|
| Name          | ReversalEffect                                                         |
| Domain        | finance                                                                |
| Requested By  | Zihan                                                                  |
| Produced By   | define-simulation-scenario-skill.md v1.2.0 (invoking agent: Claude Code) |
| Created       | 2026-07-07                                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md                             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.2)                |
| Status        | draft                                                                  |

| CHANGELOG | |
|---|---|
| 2026-07-07 | Polish Step 0: target file produced from `simulation-bases.md` and `analysis-bases.md` downstream artefacts via define-skill end-to-end invocation (Case B, pre-filled from existing). DOI gaps noted in §2.2 (Contrarian Trading) and §2.4 (Overconfidence and Noise) of simulation-bases.md — to be resolved in Step 1 research audit. |

## §2 Phenomenon Statement

### §2.1 Trigger
The scenario begins with an extended directional price move — a sustained uptrend or downtrend driven by momentum-chasing and overconfident demand. After the trend has run far enough, price reaches a level where mean-reversion forces become significant relative to trend-following pressure. A small reversal signal — a single opposite-direction return, or a fundamental-value threshold crossing — triggers contrarian agents to begin fading the trend.

### §2.2 Mechanism
Long-horizon reversal is the empirical phenomenon where past losers outperform past winners over multi-year horizons. The mechanism combines overreaction with eventual correction: momentum and overconfidence drive prices past fundamental value, but as deviation grows, contrarian and value investors enter with increasing conviction. Index-tracking and noise-trading agents add background flow. The net effect is that extreme past returns predict opposite-direction future returns — winners eventually underperform and losers eventually recover.

### §2.3 Participants
Six participant classes operate: contrarian reversal investors who fade extended trends, momentum investors who sustain them, overconfident traders who amplify them through inflated signal interpretation, value investors who anchor to fundamental worth, index trackers who supply slow non-directional rebalancing flow, and noise traders who add uninformed liquidity.

### §2.4 Resolution
Reversal completes when contrarian and value-investor order flow exceeds remaining momentum-side demand. The price crosses back toward fundamental value, the momentum signal weakens as returns turn opposite, and overconfident agents reduce conviction as unfavourable outcomes accumulate. Recovery is gradual because trend-following agents may interpret the reversal as a temporary pullback and re-enter.

## §3 Research Goals

1. **Long-horizon reversal signature.** Can the simulation generate negative return autocorrelation at longer lags (opposite-direction returns following extreme past returns), consistent with De Bondt and Thaler (1985)?
2. **Contrarian timing.** Does contrarian order flow activate after extended trends and increase with deviation magnitude?
3. **Winner-loser spread.** Do past-extreme-return assets show measurable return reversal relative to the market average?
4. **Ablation.** If the contrarian reversal investor is removed, does reversal magnitude fall and momentum persistence increase relative to the full model?
5. **Parameter sweep and variant comparison.** How do the reversion threshold and value-threshold parameters change reversal timing and magnitude, and how do LLM-driven variants differ from the Rule baseline in reversal conviction?

## §4 Theoretical Anchors

### §4.1 Long-Horizon Overreaction and Reversal

| Field                     | Content |
|---------------------------|---------|
| Full citation             | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| Key mechanism (≤30 words) | Extreme past loser portfolios outperform extreme past winner portfolios over subsequent 3-5 year horizons as prices revert from overreaction. |
| Key equation              | Contrarian trade direction = -sign(cumulative_return) when abs(cumulative_return) > reversion_threshold; quantity scales with cumulative return magnitude. |
| Motivates agent           | contrarian-investor (§7) |
| Parameter implication     | reversion_threshold range 0.05 to 0.20, default 0.10; lookback_window range 10 to 40 rounds, default 20. |

### §4.2 Return Momentum (Reference Anchor for Pre-Reversal Trend)

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| Key mechanism (≤30 words) | Intermediate-horizon return continuation provides the trend that reversal agents ultimately fade; momentum and reversal are paired phenomena. |
| Key equation              | Momentum trade direction = sign(recent_return) when abs(recent_return) > momentum_threshold; produces the trend that contrarian agents later fade. |
| Motivates agent           | momentum-investor (§7) |
| Parameter implication     | momentum_threshold range 0.01 to 0.04, default 0.02. |

### §4.3 Overconfidence and Noise-Driven Overreaction

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839-1885. https://doi.org/10.1111/0022-1082.00077 |
| Key mechanism (≤30 words) | Overconfident investors overestimate signal precision and overreact to private information, driving prices beyond fundamental value and setting up subsequent reversal. |
| Key equation              | Perceived signal = precision_overestimate * deviation; overconfident demand amplifies trend before reversal. |
| Motivates agent           | overconfident-trader (§7) |
| Parameter implication     | precision_overestimate range 1.2 to 3.0, default 2.0. |

### §4.4 Contrarian and Value-Based Reversal Trading

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541-1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x |
| Key mechanism (≤30 words) | Value and contrarian strategies exploit representativeness-driven extrapolation by buying out-of-favour assets and selling glamour stocks. |
| Key equation              | Value buy when price < fundamental * (1 - value_threshold); contrarian sell when cumulative_return > reversion_threshold. |
| Motivates agent           | value-investor (§7) |
| Parameter implication     | value_threshold range 0.05 to 0.20, default 0.08. |

### §4.5 Limits to Arbitrage

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Arbitrageurs face capital constraints and noise-trader risk, so correction of overreaction is gradual rather than instantaneous. |
| Key equation              | Corrective demand constrained by available capital and short-selling costs; reversal is partial per round. |
| Motivates agent           | value-investor (§7), contrarian-investor (§7) |
| Parameter implication     | max_position limits and short-cost rate define the gradual-reversal constraint. |

## §5 Stylized Facts

| #  | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|----|----------------------|--------------------|----------|-------------------|
| F1 | Extreme cumulative-return portfolios show subsequent return reversal. | autocorrelation at lag 10-20 < 0 (negative) | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x | `analysis.py: _compute_long_lag_autocorrelation()` < 0 |
| F2 | Contrarian order flow increases in magnitude after extended same-direction price moves. | contrarian_volume_share rising with abs(cumulative_return) | Lakonishok, Shleifer & Vishny (1994), https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | `analysis.py: contrarian_vs_cumulative_return_correlation()` > 0 |
| F3 | Price reverts toward fundamental value after overreaction-driven deviation peaks. | post-peak deviation magnitude falls over subsequent 10+ rounds | Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 | `analysis.py: _post_peak_reversion_rate()` > 0 |
| F4 | Value-investor order flow is counter-cyclical — buying when price is below fundamental and selling when above. | value_flow_below_fundamental > value_flow_above_fundamental | Lakonishok, Shleifer & Vishny (1994), https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | `analysis.py: _value_counter_cyclical_ratio()` > 1.0 |
| F5 | Reversal magnitude is larger following more extreme prior trends. | abs(reversal_return) correlated with abs(prior_trend_return) | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x | `analysis.py: _reversal_vs_prior_correlation()` > 0 |

## §6 Historical / Empirical Anchors

### §6.1 De Bondt-Thaler Winner-Loser Portfolios (1933-1980)

| Field             | Content |
|-------------------|---------|
| Name + dates      | De Bondt and Thaler long-horizon reversal study, CRSP monthly returns 1933-1980. |
| Trigger           | Formation of extreme winner and loser portfolios based on 3-5 year past cumulative returns. |
| Quantitative arc  | Loser portfolios outperformed winner portfolios by approximately 25% cumulatively over the subsequent 3-5 years. Reversal was strongest in the third year after portfolio formation. |
| Agent mapping     | `contrarian-investor` maps to investors who buy past losers and sell past winners; `momentum-investor` maps to those who sustain the initial trend; `value-investor` maps to fundamental-value buyers at depressed prices; `overconfident-trader` maps to investors who overreacted to the initial trend. |
| Primary source(s) | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|--------------------|------------------------|---------------------------|-------------|-----------------|-------------|---------------------|
| contrarian-investor | long-horizon contrarian fund or reversal strategist | Overreaction (§4.1) and Limits to Arbitrage (§4.5) | Stabilising | price, cumulative_return | "Exists to fade extended trends by trading against the cumulative return direction." | examples/AGENT_POOL/finance/contrarian-trader.md |
| momentum-investor | momentum strategy fund or trend-following CTA | Momentum (§4.2) | Destabilising | price, return | "Exists to sustain directional trends through positive-feedback trading, providing the deviation that reversal agents later fade." | examples/AGENT_POOL/finance/momentum-trader.md |
| overconfident-trader | overconfident retail or active institutional investor | Overconfidence (§4.3) | Destabilising | price, deviation | "Exists to amplify price moves beyond fundamental value through inflated signal interpretation." | (none — likely new) |
| value-investor | value-oriented mutual fund or fundamental analyst | Contrarian/Value (§4.4) and Limits to Arbitrage (§4.5) | Stabilising | price, fundamental, deviation | "Exists to buy undervalued assets and sell overvalued ones, providing fundamental gravity." | examples/AGENT_POOL/finance/fundamental-analyst.md |
| index-tracker | passive index fund or ETF provider | Passive Allocation (context) | Stabilising | price, cash, position | "Exists to maintain a target allocation through slow rebalancing, adding non-directional baseline flow." | (none — likely new) |
| noise-trader | uninformed retail liquidity provider | Noise Trading (Black 1986 context) | Context-dependent | price, cash, position | "Exists to add background liquidity and non-informational volatility." | examples/AGENT_POOL/finance/noise-trader.md |

Diversity notes: two destabilising (momentum-investor, overconfident-trader), three stabilising (contrarian-investor, value-investor, index-tracker), and one context-dependent (noise-trader). Theory families span overreaction/reversal, momentum, overconfidence, contrarian/value, limits to arbitrage, and noise trading.

## §8 Environment Specification

### §8.1 Price Formation

`P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 1.0)`, with constant fundamental `F`, price impact `lambda`, mean reversion `gamma`, and Gaussian noise.

### §8.2 Information Broadcast

| Field | Type | Definition | Rationale |
|-------|------|------------|-----------|
| `price` | float | Current market price. | Primary state signal. |
| `fundamental` | float | Constant fundamental value. | Value anchoring and deviation. |
| `deviation` | float | `(price - fundamental) / fundamental`. | Contrarian and value entry signal. |
| `return` | float | Recent period return. | Momentum signal and trend-phase tracking. |
| `cumulative_return` | float | Cumulative return over extended lookback. | Primary reversal signal. |
| `volume` | float | Trading volume proxy. | Phase and concentration diagnostics. |
| `round` | int | Current round number. | Phase tracking. |

### §8.3 Constraints and Frictions

| Item | Yes / No | Rationale |
|------|----------|-----------|
| Short-selling allowed | Yes | Required for contrarian-investor to sell into overvalued trends. |
| Price floor | Yes | Floor at 1.0 prevents non-positive prices. |
| Transaction costs | No | Abstracted from baseline. |

### §8.4 Round Granularity

One round approximates one trading day. A 200-round run covers trend formation, overreaction, contrarian activation, reversal, and partial recovery phases.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|-----------|--------|-----------------------------------|-----------------|-------------------|-----------------|
| initial price | P(0) | environment (§8.1) | normalised | 100.0 | Source: normalization |
| fundamental value | F | environment (§8.1) | normalised | 100.0 | Source: normalization |
| price impact | lambda | environment (§8.1) | 0.03 to 0.12 | 0.06 | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| mean reversion | gamma | environment (§8.1) | 0.005 to 0.03 | 0.01 | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| noise standard deviation | sigma | environment (§8.1) | 0.10 to 0.50 | 0.25 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| reversion threshold | theta_rev | contrarian-investor (§7) | 0.05 to 0.20 | 0.10 | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| contrarian lookback window | k_rev | contrarian-investor (§7) | 10 to 40 | 20 | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| momentum threshold | theta_mom | momentum-investor (§7) | 0.01 to 0.04 | 0.02 | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| precision overestimate | k_prec | overconfident-trader (§7) | 1.2 to 3.0 | 2.0 | Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 |
| value threshold | theta_val | value-investor (§7) | 0.05 to 0.20 | 0.08 | Lakonishok, Shleifer & Vishny (1994), https://doi.org/10.1111/j.1540-6261.1994.tb04772.x |
| noise trade probability | p_noise | noise-trader (§7) | 0.10 to 0.50 | 0.30 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale |
|---------|--------|-----------|
| Rule | Yes | Deterministic baseline for reversal timing, contrarian activation, and winner-loser spread. |
| LLM | Yes | Tests whether persona-driven reversal reasoning anticipates or delays mean reversion relative to Rule baseline. |
| RuleLLM | Yes | Tests whether explicit contrarian rules inside LLM reasoning preserve threshold timing while allowing judgmental sizing. |
| Rag | Yes | Tests whether retrieved behavioural-finance literature changes reversal conviction or entry timing. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|-----------|-----------------------|
| Deterministic variant initializes, runs, writes records, and completes without uncaught exceptions. | green |
| At least one reversal mechanism activates: long-lag negative autocorrelation, contrarian offset, or post-peak reversion. | green |
| Analysis loads records and computes core metrics from §5. | green |
| All four variants declared Yes in §10.1 build and produce required output artefacts. | green |
