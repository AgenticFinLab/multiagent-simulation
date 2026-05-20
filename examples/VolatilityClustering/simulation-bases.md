# VolatilityClustering Simulation Bases

## §1 Phenomenon Definition

VolatilityClustering models the empirical fact that large price changes tend to
be followed by large price changes and calm periods by calm periods. The
scenario combines trend following, slow belief updating, volatility-sensitive
trading, and fundamental anchoring.

## §2 Theoretical Foundation

### §2.1 Conditional Heteroskedasticity

ARCH/GARCH-style models describe volatility persistence in financial returns.

### §2.2 Trend Following Under Volatility

Trend followers can increase trading during volatile trends, reinforcing
clusters of large returns.

### §2.3 Slow Information Adaptation

Slow adapters update beliefs gradually, causing persistent reactions after
shocks.

## §3 Market Mechanism

The market broadcasts price, fundamental, returns, and volatility state. Agents
trade based on value, trend, noise, slow adaptation, or volatility thresholds.
Net demand updates price, creating clustered high- and low-volatility regimes.

## §4 Investor Archetypes

### §4.1 Fundamentalist

**Summary**: Trades toward fundamental value.
**Theoretical and Empirical Basis**: Fundamental anchoring.
**Design Purpose**: Provide stabilizing mean-reversion pressure.
**Behavioral Framework**: Uses `value_sensitivity`, `value_noise_std`,
`trade_frequency`, and `base_position_size`.
**Decision Process**: Buy undervaluation and sell overvaluation with noise.
**Worked Numerical Example**: A 10% discount creates buy pressure scaled by
value sensitivity.
**Academic References**: Fundamental trading literature.

### §4.2 TrendFollower

**Summary**: Trades with recent trends and responds to volatility.
**Theoretical and Empirical Basis**: Trend following and volatility targeting.
**Design Purpose**: Amplify volatile trends.
**Behavioral Framework**: Uses `lookback_window`, `trend_threshold`,
`baseline_volatility`, `volatility_sensitivity`, and `base_position_size`.
**Decision Process**: Trade with trend when signal exceeds threshold, with size
affected by volatility.
**Worked Numerical Example**: A trend above threshold in high volatility creates
larger order.
**Academic References**: Trend-following and managed-futures literature.

### §4.3 NoiseTrader

**Summary**: Random trader with mean-reverting position process.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add stochastic shocks.
**Behavioral Framework**: Uses `position_volatility` and
`mean_reversion_speed`.
**Decision Process**: Random position change with reversion toward zero.
**Worked Numerical Example**: A random shock creates buy/sell order.
**Academic References**: Black (1986).

### §4.4 SlowAdapter

**Summary**: Updates beliefs slowly after price changes.
**Theoretical and Empirical Basis**: Adaptive expectations.
**Design Purpose**: Create persistence after shocks.
**Behavioral Framework**: Uses `lookback_window`, `update_weight`, and
`base_position_size`.
**Decision Process**: Gradually adjusts desired position based on lagged
information.
**Worked Numerical Example**: A shock affects orders for several rounds because
beliefs update slowly.
**Academic References**: Adaptive learning literature.

### §4.5 VolatilityTrader

**Summary**: Trades differently in high- and low-volatility regimes.
**Theoretical and Empirical Basis**: Volatility regime and clustering models.
**Design Purpose**: Make volatility state directly affect order flow.
**Behavioral Framework**: Uses `vol_lookback`, `low_vol_threshold`,
`high_vol_threshold`, and `base_position_size`.
**Decision Process**: Change exposure when volatility crosses configured
thresholds.
**Worked Numerical Example**: Volatility above high threshold triggers defensive
order.
**Academic References**: ARCH/GARCH and volatility timing literature.

## §5 Agent Diversity Verification

The population includes fundamental anchors, trend amplifiers, random shocks,
slow adapters, and volatility-regime traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `value_sensitivity` | Fundamental response | Fundamentalist | Medium |
| `trend_threshold` | Trend activation | TrendFollower | High |
| `volatility_sensitivity` | Volatility-scaled trend size | TrendFollower | High |
| `position_volatility` | Noise shock size | NoiseTrader | Medium |
| `update_weight` | Adaptation speed | SlowAdapter | High |
| `high_vol_threshold` | High-vol regime trigger | VolatilityTrader | High |

## §7 Communication And Round Structure

Market broadcasts state; agents compute value, trend, volatility, noise, or
adaptive signals; orders update price and future volatility.

## §8 Historical Case Studies

### §8.1 Equity Volatility Clustering

Daily equity returns show persistent high-volatility periods after shocks.

### §8.2 Crisis And Calm Regime Alternation

Markets often alternate between calm periods and clustered stress episodes,
matching conditional volatility models.

## §9 Variant Comparison Preview

Rule gives explicit clustering mechanisms. LLM may alter perceived regime
changes. RuleLLM anchors decisions to volatility rules. Rag may retrieve
volatility-model context and affect regime interpretation.
