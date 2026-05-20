# ReversalEffect Simulation Bases

## §1 Phenomenon Definition

ReversalEffect models price overreaction followed by correction. Contrarian and
value investors oppose excessive moves, while momentum and overconfident traders
can delay reversal.

## §2 Theoretical Foundation

### §2.1 Overreaction And Reversal

Behavioral finance documents that extreme price moves can reverse when initial
reaction overshoots fundamentals.

### §2.2 Contrarian Trading

Contrarian strategies buy losers and sell winners when deviations become large.

### §2.3 Overconfidence And Momentum Delay

Overconfident and momentum traders can extend mispricing before reversal occurs.

## §3 Market Mechanism

The market publishes price, fundamental, deviation, and recent history.
Contrarian/value orders pull prices back, while momentum/noise orders can
extend overshoot.

## §4 Investor Archetypes

### §4.1 ContrarianInvestor

**Summary**: Trades against excessive recent moves.
**Theoretical and Empirical Basis**: Contrarian reversal evidence.
**Design Purpose**: Generate reversal pressure.
**Behavioral Framework**: Uses `lookback_window`, `reversal_threshold`,
`value_sensitivity`, and `base_position_size`.
**Decision Process**: Buy after excessive declines; sell after excessive rises.
**Worked Numerical Example**: A 15% decline beyond threshold triggers buy.
**Academic References**: De Bondt and Thaler (1985).

### §4.2 MomentumInvestor

**Summary**: Chases recent trends and delays reversal.
**Theoretical and Empirical Basis**: Positive-feedback trading.
**Design Purpose**: Compete against contrarian pressure.
**Behavioral Framework**: Uses `momentum_threshold`, `momentum_multiplier`, and
`base_position_size`.
**Decision Process**: Trade with recent trend when it exceeds threshold.
**Worked Numerical Example**: A strong recent rise triggers buy.
**Academic References**: Jegadeesh and Titman (1993).

### §4.3 OverconfidentTrader

**Summary**: Overreacts to signals because confidence is inflated.
**Theoretical and Empirical Basis**: Overconfidence models.
**Design Purpose**: Amplify initial overreaction.
**Behavioral Framework**: Uses `reaction_threshold`,
`overconfidence_factor`, and `overconfidence_multiplier`.
**Decision Process**: Trades aggressively when perceived signal exceeds
threshold.
**Worked Numerical Example**: A modest signal becomes a large order after
overconfidence multiplier.
**Academic References**: Daniel, Hirshleifer, and Subrahmanyam (1998).

### §4.4 NoiseTrader

**Summary**: Random liquidity/noise participant.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add stochastic price pressure.
**Behavioral Framework**: Uses `position_volatility` and `mean_reversion`.
**Decision Process**: Random position changes with mild reversion.
**Worked Numerical Example**: Random positive draw creates buy order.
**Academic References**: Black (1986).

### §4.5 ValueInvestor

**Summary**: Trades on fundamental mispricing.
**Theoretical and Empirical Basis**: Value investing and limits of arbitrage.
**Design Purpose**: Anchor price to fundamental.
**Behavioral Framework**: Uses `value_threshold`, `value_sensitivity`,
`value_noise`, and `base_position_size`.
**Decision Process**: Buy undervaluation and sell overvaluation.
**Worked Numerical Example**: Price 20% below fundamental triggers buy.
**Academic References**: Graham (1949); Shleifer and Vishny (1997).

### §4.6 IndexTracker

**Summary**: Rebalances toward target index exposure.
**Theoretical and Empirical Basis**: Passive index allocation.
**Design Purpose**: Add slow stabilizing benchmark demand.
**Behavioral Framework**: Uses `target_position` and `rebalance_threshold`.
**Decision Process**: Trade toward target when drift exceeds threshold.
**Worked Numerical Example**: If position falls below target by threshold, buy.
**Academic References**: Passive investment rebalancing literature.

## §5 Agent Diversity Verification

The population includes reversal traders, momentum chasers, overconfident
overreactors, noise traders, value anchors, and passive trackers.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `reversal_threshold` | Contrarian activation | ContrarianInvestor | High |
| `momentum_threshold` | Momentum activation | MomentumInvestor | High |
| `overconfidence_factor` | Signal inflation | OverconfidentTrader | High |
| `position_volatility` | Noise size | NoiseTrader | Low |
| `value_threshold` | Fundamental activation | ValueInvestor | Medium |
| `rebalance_threshold` | Passive rebalance trigger | IndexTracker | Low |

## §7 Communication And Round Structure

Market broadcasts state; agents compute trend, reversal, value, or noise
signals; market aggregates orders and updates price.

## §8 Historical Case Studies

### §8.1 Post-Earnings Overreaction

Initial investor overreaction can reverse as fundamentals are reassessed.

### §8.2 Crisis Relief Rallies

Oversold markets often rebound when value and contrarian capital enters.

## §9 Variant Comparison Preview

Rule produces explicit reversal thresholds. LLM may vary perceived overreaction.
RuleLLM anchors rules while allowing explanation variance. Rag may use
historical overreaction context.
