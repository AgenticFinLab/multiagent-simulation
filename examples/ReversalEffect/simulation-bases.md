# ReversalEffect Simulation Bases

## §1 Phenomenon Definition

ReversalEffect models short-horizon overreaction followed by partial correction
toward fundamental value. The mechanism requires an initial price move large
enough to attract contrarian and value demand, trend-following pressure that can
delay the correction, and a market-clearing rule that converts net order flow
into the next price.

The scenario is a trading-schema example. Investor orders carry `bid_price`,
signed `quantity`, `strategy`, and variant-specific explanatory fields. The
Rule baseline uses deterministic trading rules. LLM, RuleLLM, and Rag use API
generated decisions while preserving the same market state variables and
portfolio accounting.

## §2 Theoretical Foundation

### §2.1 Overreaction And Reversal

De Bondt and Thaler (1985) argue that extreme prior winners and losers can
subsequently reverse as investors reassess exaggerated expectations (DOI:
10.1111/j.1540-6261.1985.tb05004.x). The simulation implements this as price
pressure away from fundamentals followed by order flow that trades against the
extreme move.

### §2.2 Contrarian Trading

Contrarian trading buys after sufficiently negative recent returns and sells
after sufficiently positive recent returns. This creates explicit correction
pressure when the recent price path exceeds a threshold.

### §2.3 Momentum And Delayed Correction

Momentum and positive-feedback traders can continue the current move before the
reversal takes hold. This makes the reversal timing endogenous rather than an
immediate mechanical snap-back, matching winner-loser continuation evidence
(DOI: 10.1111/j.1540-6261.1993.tb04702.x).

### §2.4 Overconfidence And Noise

Overconfident traders overweight recent signals and place larger orders than a
calibrated trader would. Noise traders add stochastic background flow so that the
path is not fully deterministic even when the main mechanism is threshold based.

### §2.5 Fundamental Anchoring

Value investors compare price with fundamental value. Their orders anchor the
longer-run path and distinguish reversal from an unconstrained random walk,
subject to limits of arbitrage (DOI: 10.1111/j.1540-6261.1997.tb03807.x).

## §3 Market Mechanism

The market coordinator broadcasts current price, previous price, round return,
trading volume, net demand, liquidity where applicable, and fundamental value.
Agents respond with signed quantities. Positive quantity is demand to buy;
negative quantity is demand to sell.

Rule and LLM variants use a mean-reverting price update that combines order
impact, fundamental pull, and stochastic noise. RuleLLM and Rag use the
liquidity-aware extension: passive liquidity supplied by agents increases
effective depth, while low liquidity increases price impact. This preserves the
same reversal concept but makes liquidity provision an explicit contract field.

## §4 Investor Archetypes

### §4.1 ContrarianInvestor

**Summary**: Trades against large recent moves.
**Theoretical and Empirical Basis**: Mean-reversion evidence after investor
overreaction.
**Design Purpose**: Generate direct reversal pressure.
**Behavioral Framework**: Uses lookback returns, `reversal_threshold`,
`base_position_size`, and value sensitivity.
**Decision Process**: Buy after excessive declines and sell after excessive
rises.
**Worked Numerical Example**: If the recent return is -15% and the threshold is
10%, the agent submits a buy order scaled by the excess move.
**Academic References**: De Bondt and Thaler (1985), DOI:
10.1111/j.1540-6261.1985.tb05004.x; Lakonishok, Shleifer, and Vishny (1994),
DOI: 10.1111/j.1540-6261.1994.tb04772.x.

### §4.2 MomentumInvestor

**Summary**: Trades with the recent trend.
**Theoretical and Empirical Basis**: Short-horizon continuation and
positive-feedback trading.
**Design Purpose**: Delay correction and create competition with contrarian
pressure.
**Behavioral Framework**: Uses recent return, `momentum_threshold`,
`momentum_multiplier`, and `base_position_size`.
**Decision Process**: Buy into positive momentum and sell into negative
momentum when the signal exceeds threshold.
**Worked Numerical Example**: A recent +6% move above a 3% threshold creates a
buy order proportional to the excess trend.
**Academic References**: Jegadeesh and Titman (1993), DOI:
10.1111/j.1540-6261.1993.tb04702.x; Shleifer and Summers (1990).

### §4.3 OverconfidentTrader

**Summary**: Overweights recent signals and trades too aggressively.
**Theoretical and Empirical Basis**: Overconfidence models of excessive trading
and delayed correction.
**Design Purpose**: Amplify the initial move and increase reversal amplitude.
**Behavioral Framework**: Uses `reaction_threshold`, `overconfidence_factor`,
and `overconfidence_multiplier`.
**Decision Process**: Convert recent returns into larger directional orders than
a calibrated investor would place.
**Worked Numerical Example**: A +4% return is inflated by the overconfidence
factor and can trigger a larger buy order.
**Academic References**: Daniel, Hirshleifer, and Subrahmanyam (1998), DOI:
10.1111/0022-1082.00077; Barber and Odean (2001), DOI:
10.1111/0022-1082.00308.

### §4.4 NoiseTrader

**Summary**: Adds random order flow with weak discipline.
**Theoretical and Empirical Basis**: Noise-trader risk and non-informational
trading.
**Design Purpose**: Prevent perfectly deterministic paths and provide background
volume.
**Behavioral Framework**: Uses stochastic position draws and mild reversion to
avoid unbounded inventory.
**Decision Process**: Submit small random buy or sell orders, sometimes acting
as liquidity supply in liquidity-aware variants.
**Worked Numerical Example**: A positive random draw creates a small buy order
near current price.
**Academic References**: Black (1986), DOI: 10.1111/j.1540-6261.1986.tb04513.x;
De Long et al. (1990), DOI: 10.1086/261703.

### §4.5 ValueInvestor

**Summary**: Trades on price-fundamental deviations.
**Theoretical and Empirical Basis**: Fundamental value anchoring and limits of
arbitrage.
**Design Purpose**: Pull price back toward fundamental value.
**Behavioral Framework**: Uses `value_threshold`, `value_sensitivity`,
`value_noise`, and `base_position_size`.
**Decision Process**: Buy when price is below fundamental by enough margin and
sell when it is above fundamental by enough margin.
**Worked Numerical Example**: Price at 80 against a fundamental of 100 creates a
buy signal scaled by the 20% undervaluation.
**Academic References**: Graham (1949); Shleifer and Vishny (1997), DOI:
10.1111/j.1540-6261.1997.tb03807.x.

### §4.6 IndexTracker

**Summary**: Rebalances toward target exposure.
**Theoretical and Empirical Basis**: Passive allocation and benchmark
rebalancing.
**Design Purpose**: Add slow stabilizing demand in the Rule baseline.
**Behavioral Framework**: Uses `target_position` and `rebalance_threshold`.
**Decision Process**: Buy or sell when inventory drifts beyond the rebalance
band.
**Worked Numerical Example**: If current position is materially below target,
the agent buys the gap subject to threshold rules.
**Academic References**: Index rebalancing and passive-investment literature;
Perold and Sharpe (1988).

## §5 Agent Diversity Verification

The scenario separates six theoretical roles. The Rule baseline includes all six
roles, including `IndexTracker`. API variants include contrarian,
overconfident, value, momentum-chaser, and noise roles; they omit the passive
index tracker to keep API cost and stochastic role count bounded. This is a
documented role-count difference, not a schema exception.

The diversity check is whether the population contains at least one reversal
force, one continuation force, one fundamental anchor, and one stochastic order
source. RuleLLM and Rag additionally require the `provides_liquidity` field
because their market calculates liquidity-sensitive price impact.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity | Source / Rationale |
|---|---|---|---|---|
| `initial_price` | Starting traded price | Market | Medium | Normalized starting point for price-path comparison |
| `fundamental_value` | Value anchor | Market, ValueInvestor | High | Defines reversal target |
| `price_impact` / `base_price_impact` | Net-demand impact scale | Market | High | Converts excess order flow into overshoot |
| `mean_reversion` | Pull toward fundamental | Market | High | Creates correction pressure |
| `noise_std` | Exogenous price noise | Market | Medium | Prevents deterministic path degeneracy |
| `reversal_threshold` | Contrarian activation threshold | ContrarianInvestor | High | Implements overreaction trigger |
| `momentum_threshold` | Trend-following activation threshold | MomentumInvestor | High | Allows delayed correction |
| `overconfidence_factor` | Signal inflation | OverconfidentTrader | High | Encodes overconfident reaction strength |
| `value_threshold` | Fundamental-deviation activation | ValueInvestor | Medium | Avoids value trading on trivial deviations |
| `base_liquidity` | Baseline market depth | RuleLLM, Rag market | High | Controls liquidity-aware price impact |

## §7 Communication And Round Structure

Each round follows a broadcast-order-update loop. The market broadcasts current
state. Investors update portfolio state and generate orders. The market
aggregates buy and sell quantities, computes volume and net demand, applies
price impact and mean reversion, and records price and volume histories.

LLM-family variants parse decisions from `<analysis>` and `<decision>` tags.
Deterministic schema/config errors fail fast. Explicit stochastic API fallback
is allowed only when it is conservative, logged, and reviewed by post-run
quality audit.

## §8 Historical Case Studies

### §8.1 Post-Earnings Overreaction

Initial earnings surprises can trigger exaggerated buying or selling. Later
rounds may reverse as fundamental and contrarian capital reassesses the move.

### §8.2 Oversold Relief Rallies

During stressed markets, rapid selling can push price below plausible
fundamental value. Reversal emerges when value and contrarian demand dominate
continuation selling.

## §9 Variant Comparison Preview

| Variant | Decision Source | Expected Reversal Behavior |
|---|---|---|
| Rule | Deterministic formulas | Clean threshold-driven reversal with all six roles. |
| LLM | Persona prompt and structured JSON order | Same order schema with more variable timing and sizing. |
| RuleLLM | Persona plus explicit quantitative rules | Liquidity-aware market with rule-constrained API orders. |
| Rag | RuleLLM plus retrieved domain context | Same liquidity-aware contract plus auditable retrieval context. |
