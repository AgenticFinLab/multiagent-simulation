# StatusQuoBias Simulation Bases

## §1 Phenomenon Definition

StatusQuoBias models investors who prefer existing allocations and require
strong evidence before changing positions. The scenario contrasts inertia and
default following with active rebalancing, momentum trading, and noise.

## §2 Theoretical Foundation

### §2.1 Status Quo Bias

Individuals disproportionately prefer current states even when alternatives
have higher expected value.

### §2.2 Default Effects

Default allocations influence investor choices because active decisions require
attention and psychological effort.

### §2.3 Active Rebalancing

Rational or rules-based rebalancers provide a benchmark that responds to new
information rather than current holdings.

## §3 Market Mechanism

The market broadcasts price, fundamental value, and signal state. Inertial and
default agents underreact; active and momentum agents adjust positions; noise
adds background order flow.

## §4 Investor Archetypes

### §4.1 InertialHolder

**Summary**: Strongly prefers maintaining current portfolio.
**Theoretical and Empirical Basis**: Status quo bias.
**Design Purpose**: Generate underreaction and sticky holdings.
**Behavioral Framework**: Requires overwhelming evidence to change.
**Decision Process**: Holds unless signal strength exceeds a high threshold.
**Worked Numerical Example**: A moderate negative signal is ignored because the
current position is psychologically favored.
**Academic References**: Samuelson and Zeckhauser (1988).

### §4.2 DefaultFollower

**Summary**: Follows default allocation suggestions.
**Theoretical and Empirical Basis**: Default effects in savings and investment.
**Design Purpose**: Add passive allocation inertia.
**Behavioral Framework**: Accepts default rather than optimizing actively.
**Decision Process**: Trade only when default allocation changes or drift is
large.
**Worked Numerical Example**: If default remains unchanged, the agent holds.
**Academic References**: Madrian and Shea (2001).

### §4.3 ActiveRebalancer

**Summary**: Adjusts positions based on new information.
**Theoretical and Empirical Basis**: Rational portfolio rebalancing.
**Design Purpose**: Provide active benchmark.
**Behavioral Framework**: Responds directly to signal/fundamental changes.
**Decision Process**: Buy or sell to target improved allocation.
**Worked Numerical Example**: A positive signal triggers a buy even if current
position is comfortable.
**Academic References**: Portfolio choice literature.

### §4.4 MomentumTrader

**Summary**: Trades on price trends, overcoming inertia.
**Theoretical and Empirical Basis**: Momentum trading.
**Design Purpose**: Add responsive trend-following demand.
**Behavioral Framework**: Uses trend signal.
**Decision Process**: Buy rising trends and sell falling trends.
**Worked Numerical Example**: Strong positive trend triggers buy.
**Academic References**: Jegadeesh and Titman (1993).

### §4.5 NoiseTrader

**Summary**: Random uninformed trader.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add stochastic baseline liquidity.
**Behavioral Framework**: Random low-intensity orders.
**Decision Process**: Random buy/sell/hold.
**Worked Numerical Example**: A random draw generates a small order.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The population includes inertial holders, default followers, active
rebalancers, momentum traders, and noise traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| inertia threshold | Evidence needed to act | InertialHolder | High |
| default allocation | Passive target | DefaultFollower | Medium |
| active signal sensitivity | Response to new information | ActiveRebalancer | High |
| momentum threshold | Trend activation | MomentumTrader | Medium |
| noise intensity | Random order flow | NoiseTrader | Low |

## §7 Communication And Round Structure

Market broadcasts state; agents decide whether to maintain default/current
positions or actively trade; market aggregates orders and updates price.

## §8 Historical Case Studies

### §8.1 Retirement Plan Defaults

Default contribution and allocation choices strongly affect investor behavior.

### §8.2 Portfolio Inertia In Brokerage Accounts

Investors often fail to rebalance despite changes in risk or fundamentals.

## §9 Variant Comparison Preview

Rule fixes inertia thresholds. LLM may rationalize holding. RuleLLM keeps
explicit thresholds. Rag may retrieve behavioral evidence about default effects.
