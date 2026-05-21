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
outperforming over intermediate horizons (DOI: 10.1111/j.1540-6261.1993.tb04702.x).
In this simulation, `MomentumTrader` and `TrendFollower` represent
positive-feedback demand.

### §2.2 Underreaction And Information Diffusion

Momentum can emerge when information is incorporated gradually, as in gradual
information-diffusion models (DOI: 10.1111/0022-1082.00184). Persistent
fundamental drift in the market state creates a sequence of signals that trend
followers respond to with delay.

### §2.3 Overreaction And Mean Reversion

Contrarian and fundamental-value trading provide an offset once prices move too
far relative to recent trend or fundamental value, matching long-horizon
overreaction evidence (DOI: 10.1111/j.1540-6261.1985.tb05004.x).

### §2.4 Technical Trading And Crowding

Moving-average signals can reinforce recent price movement. When several
technical or trend-following agents respond in the same direction, order flow
can become crowded, as in time-series momentum evidence (DOI:
10.1016/j.jfineco.2011.11.003).

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
**Academic References**: Jegadeesh and Titman (1993), DOI:
10.1111/j.1540-6261.1993.tb04702.x.

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
**Academic References**: De Bondt and Thaler (1985), DOI:
10.1111/j.1540-6261.1985.tb05004.x.

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
**Academic References**: Portfolio rebalancing and constant-mix allocation
literature; Perold and Sharpe (1988).

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
**Academic References**: Ho and Stoll (1981), DOI: 10.1016/0304-405X(81)90020-5.

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
**Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI:
10.1016/j.jfineco.2011.11.003.

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
**Academic References**: Shleifer and Vishny (1997), DOI:
10.1111/j.1540-6261.1997.tb03807.x.

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
**Academic References**: Moskowitz, Ooi, and Pedersen (2012), DOI:
10.1016/j.jfineco.2011.11.003.

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

| Parameter | Value | Used By | Role In Mechanism | Source / Rationale |
|---|---:|---|---|---|
| `price_impact` | 0.08 | Rule/LLM Market | Converts net demand to price pressure | Calibrates visible continuation without one-round collapse |
| `mean_reversion` | 0.01 | Rule/LLM Market | Weak pull toward fundamental value | Keeps momentum persistent but not permanent |
| `drift_persistence` | 0.95 | Rule/LLM Market | Creates persistent trend opportunities | Implements gradual-information momentum |
| `drift_volatility` | 0.5 | Rule/LLM Market | Adds stochastic trend shocks | Produces repeated signals for trend followers |
| `momentum_threshold` | 0.02 | MomentumTrader | Activates trend-following orders | Intermediate-horizon winner/loser evidence |
| `reversion_threshold` | 0.03 | ContrarianTrader | Activates opposing orders | Overreaction offset threshold |
| `target_allocation` | 0.6 | IndexFund | Passive baseline allocation | Standard balanced allocation anchor |
| `inventory_target` | 0.0 | MarketMaker | Liquidity-provider inventory anchor | Inventory-control market making |
| `short_window` / `long_window` | 3 / 10 | TechnicalTrader | Moving-average crossover signal | Short/medium trend-following separation |
| `value_threshold` | 0.05 | FundamentalTrader | Fundamental mispricing trigger | Limits-of-arbitrage offset |
| `base_liquidity` | 50.0 | RuleLLM/Rag Market | Baseline liquidity for API market variant | Maintains API-market depth under liquidity flags |

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
