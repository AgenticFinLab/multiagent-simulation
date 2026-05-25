# VolatilityClustering Simulation Bases

## §1 Phenomenon Definition

VolatilityClustering models the empirical regularity that large asset-price
changes tend to be followed by large changes, and quiet periods tend to be
followed by quiet periods. The simulation combines GARCH-style volatility
persistence with heterogeneous investors whose orders amplify, dampen, or delay
return shocks.

This is a trading-schema scenario. Rule and LLM variants use a GARCH market with
signed orders. RuleLLM and Rag use a liquidity-aware extension that consumes
`provides_liquidity` and changes price impact through effective depth.

## §2 Theoretical Foundation

### §2.1 Conditional Heteroskedasticity

ARCH and GARCH models represent volatility persistence by making current
variance depend on prior squared returns and prior variance. The market
coordinator implements this mechanism directly through a bounded GARCH(1,1)
update, following ARCH evidence (DOI: 10.2307/1912773) and GARCH modeling
(DOI: 10.1016/0304-4076(86)90063-1).

### §2.2 Heterogeneous Agent Feedback

Heterogeneous agent models show how fundamentalists, trend followers, and noise
traders can produce persistent nonlinear market dynamics. Trend following and
noise shocks help create clustered high-volatility periods; fundamentalists and
slow adapters provide stabilizing pressure (DOI:
10.1016/S0165-1889(98)00011-6).

### §2.3 Trend Following Under Volatility

Trend followers often size positions by market state. In this scenario,
volatility-sensitive trend demand can amplify price moves during turbulent
periods, consistent with time-series momentum evidence (DOI:
10.1016/j.jfineco.2011.11.003).

### §2.4 Slow Adaptation

Slow information processing spreads reactions across multiple rounds, making
the effect of a shock persist after the initial return, following adaptive
expectations and bounded-rationality market models.

### §2.5 Volatility Timing

Volatility traders react to high- and low-volatility regimes rather than price
direction alone, creating direct order-flow feedback from the volatility state.

## §3 Market Mechanism

The Rule and LLM market broadcasts price, previous price, return, volatility,
previous volatility, volume, net demand, and fundamental value. It aggregates
signed quantities and updates price using net-demand impact, mean reversion, and
GARCH-scaled noise:

`P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + sigma(t) * epsilon`

`sigma(t)^2 = omega + alpha * r(t-1)^2 + beta * sigma(t-1)^2`

RuleLLM and Rag retain the same volatility phenomenon but use a
liquidity-sensitive market. Orders marked with `provides_liquidity=true` add to
effective depth; low depth increases price impact. Missing Rag liquidity flags
default to `false`, which is conservative because it cannot inflate market
liquidity.

## §4 Investor Archetypes

### §4.1 Fundamentalist

**Summary**: Trades toward fundamental value at a low frequency.
**Theoretical and Empirical Basis**: Fundamental anchoring and stabilizing value
demand.
**Design Purpose**: Damp excessive deviation and prevent unbounded price drift.
**Behavioral Framework**: Uses `trade_frequency`, `value_sensitivity`,
`base_position_size`, and `value_noise_std`.
**Decision Process**: Trade only on configured rounds; estimate value with
noise; buy undervaluation and sell overvaluation.
**Worked Numerical Example**: If price is 95 and noisy estimated value is 100,
the positive deviation creates a buy order scaled by value sensitivity.
**Academic References**: Graham (1949); Brock and Hommes (1998), DOI:
10.1016/S0165-1889(98)00011-6.

### §4.2 TrendFollower

**Summary**: Trades with recent price trends and sizes by volatility.
**Theoretical and Empirical Basis**: Chartist and managed-futures trend
following.
**Design Purpose**: Amplify shocks and help create clustered large returns.
**Behavioral Framework**: Uses `lookback_window`, `trend_threshold`,
`baseline_volatility`, `volatility_sensitivity`, and `base_position_size`.
**Decision Process**: Compare current price with recent average; trade in the
trend direction if the signal exceeds threshold; increase size in high
volatility.
**Worked Numerical Example**: A price above its lookback average with volatility
twice baseline creates a larger buy order.
**Academic References**: Jegadeesh and Titman (1993), DOI:
10.1111/j.1540-6261.1993.tb04702.x; Moskowitz, Ooi, and Pedersen (2012), DOI:
10.1016/j.jfineco.2011.11.003.

### §4.3 NoiseTrader

**Summary**: Produces stochastic order flow with position mean reversion.
**Theoretical and Empirical Basis**: Noise-trader risk and uninformed liquidity
trading.
**Design Purpose**: Generate shocks that feed the GARCH volatility process.
**Behavioral Framework**: Uses `position_volatility` and
`mean_reversion_speed`.
**Decision Process**: Draw a random trade and offset extreme inventory through
mean reversion.
**Worked Numerical Example**: A positive random draw creates a buy order, while
a large existing long position reduces the order through reversion.
**Academic References**: Black (1986), DOI: 10.1111/j.1540-6261.1986.tb04513.x;
De Long et al. (1990), DOI: 10.1086/261703.

### §4.4 SlowAdapter

**Summary**: Updates perceived value gradually after market moves.
**Theoretical and Empirical Basis**: Adaptive expectations and delayed
information processing.
**Design Purpose**: Extend the effect of shocks over several rounds.
**Behavioral Framework**: Uses `lookback_window`, `update_weight`, and
`base_position_size`.
**Decision Process**: Blend fundamental value with a long moving average; trade
only when the deviation is material.
**Worked Numerical Example**: After a price shock, the moving average remains
away from fundamental and influences orders for multiple rounds.
**Academic References**: Hommes (2006); Brock and Hommes (1998), DOI:
10.1016/S0165-1889(98)00011-6.

### §4.5 VolatilityTrader

**Summary**: Changes exposure based on volatility regime.
**Theoretical and Empirical Basis**: Volatility timing and volatility
mean-reversion strategies.
**Design Purpose**: Make volatility state directly affect order flow.
**Behavioral Framework**: Uses `vol_lookback`, `high_vol_threshold`,
`low_vol_threshold`, and `base_position_size`.
**Decision Process**: Sell or reduce exposure when volatility is high relative
to its moving average; buy or increase exposure in low-volatility regimes.
**Worked Numerical Example**: If current volatility is 1.8 times its recent
average and the high threshold is 1.5, the trader sells.
**Academic References**: Engle (1982), DOI: 10.2307/1912773; Bollerslev (1986),
DOI: 10.1016/0304-4076(86)90063-1; volatility timing literature.

## §5 Agent Diversity Verification

The population contains one stabilizing value anchor, one trend amplifier, one
stochastic shock source, one delayed-response investor, and one volatility-regime
trader. This role mix is sufficient to produce clustered volatility through
both exogenous shocks and endogenous order-flow feedback.

All four variants preserve the same five archetypes. RuleLLM and Rag add the
liquidity flag required by their liquidity-aware market. Rag additionally
records retrieved context for post-run audit.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity | Source / Rationale |
|---|---|---|---|---|
| `initial_price` | Starting price | Market | Medium | Normalized starting point for volatility paths |
| `fundamental_value` | Value anchor | Market, Fundamentalist | High | Stabilizing reference value |
| `price_impact` / `base_price_impact` | Net-demand price impact | Market | High | Converts order-flow shocks into returns |
| `mean_reversion` | Pull toward fundamental | Market | Medium | Prevents unbounded drift |
| `garch_omega` | Long-run variance component | Market | High | GARCH baseline variance |
| `garch_alpha` | Return-shock variance loading | Market | High | ARCH shock response |
| `garch_beta` | Volatility persistence | Market | High | GARCH persistence channel |
| `min_volatility` / `max_volatility` | Volatility bounds | Market | Medium | Numerical stability and scenario observability |
| `trend_threshold` | Trend activation | TrendFollower | High | Activates continuation trades only on meaningful trends |
| `volatility_sensitivity` | Volatility-scaled trend size | TrendFollower | High | Links turbulence to order size |
| `position_volatility` | Noise-trader shock size | NoiseTrader | Medium | Generates shocks that feed volatility updates |
| `update_weight` | Slow-adapter fundamental weight | SlowAdapter | High | Controls delayed information processing |
| `high_vol_threshold` / `low_vol_threshold` | Volatility-regime triggers | VolatilityTrader | High | Implements volatility timing behavior |

## §7 Communication And Round Structure

Each round follows market broadcast, investor decision, order aggregation, and
market update. Investors record portfolio state and submit one order. The market
records price, volatility, and volume histories. API variants parse `<analysis>`
and `<decision>` sections; deterministic schema/config errors fail fast, while
explicit stochastic API fallback is allowed only when conservative and
quality-audited.

## §8 Historical Case Studies

### §8.1 Equity Index Stress Periods

Equity markets often show persistent high absolute returns after news shocks,
earnings uncertainty, or macro stress.

### §8.2 Calm-to-Stress Transitions

Markets can remain quiet for extended periods and then move into clustered
stress when trend followers, volatility traders, and noise shocks interact.

## §9 Variant Comparison Preview

| Variant | Decision Source | Expected Volatility-Clustering Behavior |
|---|---|---|
| Rule | Deterministic GARCH market and formulaic investors | Clean baseline with explicit volatility persistence. |
| LLM | Persona prompts and structured orders | Same volatility state with more variable role interpretation. |
| RuleLLM | Persona plus explicit rules under liquidity-aware pricing | Rule-constrained API orders and liquidity-depth effects. |
| Rag | RuleLLM plus retrieved volatility context | Same market contract plus auditable retrieval context. |
