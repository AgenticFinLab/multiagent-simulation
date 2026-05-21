# MomentumEffect Simulation Bases

## §1 Phenomenon Definition

MomentumEffect models return continuation: recent price increases attract
additional buying and recent losses attract additional selling. The mechanism
is endogenous because trend-following demand feeds back into future prices,
while contrarian, passive, liquidity-supplying, and fundamental-value agents
limit but do not immediately erase the trend.

## §2 Theoretical Foundation

### §2.1 Return Momentum

Jegadeesh and Titman-style momentum evidence shows that recent winners can keep
outperforming over intermediate horizons. In this simulation, `MomentumTrader`
and `TrendFollower` represent positive-feedback demand.

### §2.2 Underreaction And Information Diffusion

Momentum can emerge when information is incorporated gradually. Persistent
fundamental drift in the market state creates a sequence of signals that trend
followers respond to with delay.

### §2.3 Overreaction And Mean Reversion

Contrarian and fundamental-value trading provide an offset once prices move too
far relative to recent trend or fundamental value.

### §2.4 Technical Trading And Crowding

Moving-average signals can reinforce recent price movement. When several
technical or trend-following agents respond in the same direction, order flow
can become crowded.

## §3 Market Mechanism

The Rule and LLM markets maintain `price`, `fundamental`, persistent drift, and
recent-return history. Price updates combine net demand, weak mean reversion to
fundamental value, and noise.

The RuleLLM and Rag coordinators use a liquidity-sensitive variant of the
market equation and require API orders to include `provides_liquidity`. This is
a retained runtime difference in the current implementation and must be
reflected in prompt and parser contracts.

## §4 Investor Archetypes

### §4.1 MomentumTrader

**Summary**: Buys after positive recent returns and sells after negative recent
returns.  
**Theoretical and Empirical Basis**: Return momentum and positive-feedback
trading.  
**Design Purpose**: Create the core continuation pressure.  
**Behavioral Framework**: Rule uses `lookback_window=5`,
`momentum_threshold=0.02`, `scale=3.0`, `max_position=100.0`.  
**Decision Process**: Trade in the direction of the 5-period momentum signal
once it exceeds the threshold.  
**Worked Numerical Example**: A 4% positive momentum signal exceeds the 2%
threshold and triggers a buy scaled by signal strength.  
**Academic References**: Jegadeesh and Titman (1993).

### §4.2 ContrarianTrader

**Summary**: Trades against recent momentum once the move is large enough.  
**Theoretical and Empirical Basis**: Overreaction and mean-reversion evidence.  
**Design Purpose**: Prevent unchecked continuation.  
**Behavioral Framework**: Rule uses `reversion_threshold=0.03`,
`scale=2.0`, `max_position=80.0`.  
**Decision Process**: Convert the momentum signal into an opposite-side order
when the absolute signal exceeds the threshold.  
**Worked Numerical Example**: A 5% positive momentum signal generates a sell
signal.  
**Academic References**: De Bondt and Thaler (1985).

### §4.3 IndexFund

**Summary**: Maintains a target equity allocation.  
**Theoretical and Empirical Basis**: Passive portfolio rebalancing.  
**Design Purpose**: Add slow baseline flow that is not trend-seeking.  
**Behavioral Framework**: Rule uses `target_allocation=0.6` and
`rebalance_threshold=0.05`.  
**Decision Process**: Rebalance gradually when portfolio allocation drifts too
far from target.  
**Worked Numerical Example**: If equity allocation falls below target by more
than 5%, the fund buys part of the gap.  
**Academic References**: Portfolio rebalancing literature.

### §4.4 MarketMaker

**Summary**: Supplies liquidity by reverting inventory toward a target.  
**Theoretical and Empirical Basis**: Inventory-control market making.  
**Design Purpose**: Dampen order imbalance without becoming a directional
investor.  
**Behavioral Framework**: Rule uses `inventory_target=0.0` and
`reversion_speed=0.2`.  
**Decision Process**: Buy or sell toward target inventory subject to cash and
position constraints.  
**Worked Numerical Example**: Positive inventory above target generates a sell
order.  
**Academic References**: Ho and Stoll (1981).

### §4.5 TechnicalTrader

**Summary**: Uses moving-average crossover signals.  
**Theoretical and Empirical Basis**: Technical trend-following and signal
crowding.  
**Design Purpose**: Reinforce continuation with a distinct signal rule.  
**Behavioral Framework**: Rule uses `short_window=3`, `long_window=10`,
`scale=2.0`, `max_position=60.0`.  
**Decision Process**: Buy when the short moving average exceeds the long moving
average and sell when it falls below.  
**Worked Numerical Example**: A short average 1.5% above the long average
triggers a buy.  
**Academic References**: Technical trading and trend-following literature.

### §4.6 FundamentalTrader / FundamentalAnchor

**Summary**: Trades against mispricing relative to fundamental value.  
**Theoretical and Empirical Basis**: Fundamental-value anchoring and limits of
arbitrage.  
**Design Purpose**: Provide long-run gravity against trend overshoot.  
**Behavioral Framework**: Rule uses `value_threshold=0.05`, `scale=1.5`,
`max_position=50.0`.  
**Decision Process**: Buy undervaluation and sell overvaluation once mispricing
exceeds threshold.  
**Worked Numerical Example**: Price 8% below fundamental triggers a buy.  
**Academic References**: Value investing and limits-of-arbitrage literature.

### §4.7 TrendFollower

**Summary**: An API-variant aggressive trend follower.  
**Theoretical and Empirical Basis**: Trend-following and crowded momentum
strategies.  
**Design Purpose**: Increase API-variant continuation pressure without adding a
passive rebalancer.  
**Behavioral Framework**: LLM, RuleLLM, and Rag variants use prompt rules based
on medium-horizon momentum direction.  
**Decision Process**: Buy when the trend is positive, sell when it is negative,
and size more aggressively than a baseline momentum trader when conviction is
high.  
**Worked Numerical Example**: Positive 10-period momentum supports a larger
buy than a moderate 5-period signal.  
**Academic References**: Time-series momentum and trend-following literature.

## §5 Agent Diversity Verification

The Rule baseline contains six archetypes:
MomentumTrader, ContrarianTrader, IndexFund, MarketMaker, TechnicalTrader, and
FundamentalTrader.

The API variants contain five archetypes:
MomentumTrader, ContrarianTrader, TechnicalTrader, TrendFollower, and
FundamentalAnchor. They omit IndexFund and MarketMaker, and introduce
TrendFollower as an API-only momentum-amplifying role. This is a retained
runtime design and must be documented rather than silently normalized.

## §6 Parameter Table

| Parameter | Value | Used By | Role In Mechanism |
|---|---:|---|---|
| `price_impact` | 0.08 | Rule/LLM Market | Converts net demand to price pressure |
| `mean_reversion` | 0.01 | Rule/LLM Market | Weak pull toward fundamental value |
| `drift_persistence` | 0.95 | Rule/LLM Market | Creates persistent trend opportunities |
| `drift_volatility` | 0.5 | Rule/LLM Market | Adds stochastic trend shocks |
| `momentum_threshold` | 0.02 | MomentumTrader | Activates trend-following orders |
| `reversion_threshold` | 0.03 | ContrarianTrader | Activates opposing orders |
| `target_allocation` | 0.6 | IndexFund | Passive baseline allocation |
| `inventory_target` | 0.0 | MarketMaker | Liquidity-provider inventory anchor |
| `short_window` / `long_window` | 3 / 10 | TechnicalTrader | Moving-average crossover signal |
| `value_threshold` | 0.05 | FundamentalTrader | Fundamental mispricing trigger |
| `base_liquidity` | 50.0 | RuleLLM/Rag Market | Baseline liquidity for API market variant |

## §7 Communication And Round Structure

Each round:

1. The market broadcasts current price, returns, momentum, and fundamental
   state.
2. Investors submit `bid_price`, `quantity`, and `strategy`.
3. LLM-family variants additionally include reasoning; RuleLLM/Rag include
   `provides_liquidity`.
4. The market aggregates net demand and updates price.

## §8 Historical Case Studies

### §8.1 Cross-Sectional Equity Momentum

Equity winners often continue to outperform over intermediate horizons, which
motivates the MomentumTrader role.

### §8.2 CTA And Time-Series Momentum Crowding

Trend-following funds can reinforce persistent moves when many strategies react
to the same price signal.

### §8.3 Momentum Reversal After Crowding

Momentum crashes and reversals occur when crowded positions unwind or
fundamental anchors overpower trend demand.

## §9 Variant Comparison Preview

- **Rule**: full six-role baseline with deterministic momentum, contrarian,
  passive, liquidity, technical, and value mechanisms.
- **LLM**: five-role persona-driven API variant with an explicit TrendFollower.
- **RuleLLM**: five-role API variant constrained by explicit strategy rules.
- **Rag**: RuleLLM-style API variant plus retrieved reference context and
  retrieval-quality artifacts.
