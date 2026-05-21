# MarketCrash Simulation Bases

## §1 Phenomenon Definition

MarketCrash models an endogenous crash in which falling prices, rising
volatility, liquidity withdrawal, and forced deleveraging amplify one another.
The scenario is not driven by one exogenous news shock. Its core mechanism is a
feedback loop among leverage, volatility targeting, liquidity depth, panic
selling, and delayed contrarian absorption.

This is a trading-schema scenario. Rule uses a six-archetype deterministic
baseline. LLM, RuleLLM, and Rag use five API archetypes and omit PassiveInvestor
to bound API cost and role count. RuleLLM and Rag additionally consume
`provides_liquidity` because their market coordinators distinguish passive
depth from directional demand.

## §2 Theoretical Foundation

### §2.1 Volatility Targeting

Volatility-targeting and risk-parity portfolios reduce exposure when realized
volatility rises. This creates procyclical selling after losses have already
increased risk estimates. See Moreira and Muir (2017, DOI: 10.1111/jofi.12575)
and Barroso and Santa-Clara (2015, DOI: 10.1016/j.jfineco.2015.05.006).

### §2.2 Leverage And Margin Spirals

Margin constraints force leveraged investors to sell into falling markets,
lowering prices and tightening constraints further. This follows the liquidity
and margin spiral mechanism in Brunnermeier and Pedersen (2009, DOI:
10.1093/rfs/hhn098).

### §2.3 Liquidity Withdrawal

Market makers reduce risk-bearing capacity when volatility and inventory risk
increase, raising price impact during stress. This is consistent with
liquidity-supply models such as Grossman and Miller (1988, DOI:
10.1111/j.1540-6261.1988.tb04594.x).

### §2.4 Behavioral Panic And Contrarian Absorption

Loss-sensitive investors can accelerate crashes through panic selling, while
contrarian capital often enters only after deep discounts. The timing mismatch
between panic liquidation and bottom-fishing demand determines whether the
crash stabilizes or cascades.

## §3 Market Mechanism

The market broadcasts price, previous price, return, volatility, liquidity,
volume, net demand, crash-state flags, and fundamental value. Investors submit
signed trading orders. The market updates price through liquidity-sensitive
impact, mean reversion, and stochastic noise:

`P(t+1) = max(1, P(t) + impact(t) * NetDemand + gamma * (F - P(t)) + epsilon)`

Rule computes liquidity internally from stress and market-maker behavior. LLM
uses an internal liquidity state. RuleLLM and Rag consume
`order["provides_liquidity"]` to compute explicit effective depth.

## §4 Investor Archetypes

### §4.1 RiskParityFund

**Summary**: A volatility-targeting institutional investor.
**Theoretical and Empirical Basis**: Volatility-managed portfolios reduce risky
exposure when volatility rises; see Moreira and Muir (2017, DOI:
10.1111/jofi.12575).
**Design Purpose**: Add mechanical procyclical selling after volatility spikes.
**Behavioral Framework**: Uses target volatility, recent volatility, rebalance
speed, and base position to scale exposure.
**Decision Process**: Estimate realized volatility; if volatility exceeds the
target, reduce exposure; if volatility is calm, rebalance gradually.
**Worked Numerical Example**: With target volatility 2.0, observed volatility
4.0, base position 50, and rebalance speed 0.3, desired exposure is roughly
25, so a current position of 50 produces a sell order near 7.5 shares.
**Academic References**: Moreira and Muir (2017); Barroso and Santa-Clara
(2015).

### §4.2 LeveragedHedgeFund

**Summary**: A leveraged investor subject to margin calls and liquidation.
**Theoretical and Empirical Basis**: Margin spirals force deleveraging into
drawdowns; see Brunnermeier and Pedersen (2009, DOI: 10.1093/rfs/hhn098).
**Design Purpose**: Create forced selling after losses and balance-sheet stress.
**Behavioral Framework**: Uses leverage, margin-call threshold, liquidation
threshold, and momentum sensitivity.
**Decision Process**: Mark portfolio equity to market; if equity ratio crosses
margin thresholds, sell to reduce leverage; otherwise trade with momentum.
**Worked Numerical Example**: If equity ratio falls from 0.6 to 0.45, below a
0.5 margin-call level, the fund sells part of its position to restore leverage.
**Academic References**: Brunnermeier and Pedersen (2009); Adrian and Shin
(2010, DOI: 10.1016/j.jfineco.2010.02.001).

### §4.3 MarketMaker

**Summary**: A liquidity supplier that withdraws under stress.
**Theoretical and Empirical Basis**: Liquidity suppliers require compensation
for immediacy and inventory risk; see Grossman and Miller (1988, DOI:
10.1111/j.1540-6261.1988.tb04594.x).
**Design Purpose**: Make crash severity depend on endogenous market depth.
**Behavioral Framework**: Uses volatility withdrawal threshold, inventory
limits, quote size, and spread multiplier.
**Decision Process**: Provide stabilizing quotes in normal markets; reduce
quantity when volatility exceeds threshold or inventory risk is high.
**Worked Numerical Example**: If normal quote size is 20 but volatility exceeds
the withdrawal threshold, the submitted liquidity quantity shrinks or turns to
defensive inventory reduction.
**Academic References**: Grossman and Miller (1988); Brunnermeier and Pedersen
(2009).

### §4.4 PassiveInvestor

**Summary**: A slow stabilizing allocator that rebalances occasionally.
**Theoretical and Empirical Basis**: Long-horizon rebalancing creates delayed
demand after price dislocations.
**Design Purpose**: Provide weak mean-reverting demand in the Rule baseline.
**Behavioral Framework**: Uses rebalance frequency and target position.
**Decision Process**: Remain inactive most rounds; on rebalance rounds, trade
toward target exposure.
**Worked Numerical Example**: If target position is 30 and current position is
20 on a rebalance round, the investor buys part of the 10-share gap.
**Academic References**: Gârleanu and Pedersen (2013, DOI:
10.1093/rfs/hhs083); rebalancing literature.

### §4.5 PanicSeller

**Summary**: A loss-sensitive investor that sells after drawdowns or sharp
one-round drops.
**Theoretical and Empirical Basis**: Behavioral loss aversion and feedback
trading can amplify market declines.
**Design Purpose**: Add discretionary crash amplification beyond mechanical
deleveraging.
**Behavioral Framework**: Uses loss threshold, crash trigger, and panic-sell
fraction.
**Decision Process**: Track price losses; if cumulative or one-round losses
cross the trigger, sell a configured fraction of holdings.
**Worked Numerical Example**: With a 10% loss threshold and 50% panic fraction,
a 15% drawdown can trigger sale of half the current position.
**Academic References**: Kahneman and Tversky (1979, DOI:
10.2307/1914185); Shiller (1984, DOI: 10.2307/2327670).

### §4.6 BottomFisher

**Summary**: A contrarian buyer that enters after large discounts.
**Theoretical and Empirical Basis**: Contrarian and value demand can absorb
forced sales after large deviations.
**Design Purpose**: Test whether opportunistic capital stabilizes the crash.
**Behavioral Framework**: Uses crash-buy threshold, discount threshold, buy
size, and lookback window.
**Decision Process**: Wait until price is sufficiently discounted or recent
returns indicate a crash; then submit buy orders subject to cash constraints.
**Worked Numerical Example**: If price is 15% below fundamental and the
discount threshold is 10%, the agent submits a buy order of the configured size.
**Academic References**: Lakonishok, Shleifer, and Vishny (1994, DOI:
10.1111/j.1540-6261.1994.tb04772.x).

## §5 Agent Diversity Verification

The Rule baseline contains six archetypes: RiskParityFund, LeveragedHedgeFund,
MarketMaker, PassiveInvestor, PanicSeller, and BottomFisher. The API variants
retain five archetypes: PanicSeller, RiskParityFund, LeveragedFund,
MarketMaker, and BottomFisher. The omitted PassiveInvestor is documented in
variant docs and should not be silently inferred during API comparison.

The population includes mechanical sellers, behavioral sellers, liquidity
providers, slow stabilizers, and contrarian buyers. This satisfies diversity by
time horizon, signal source, stabilizing/destabilizing role, and risk tolerance.

## §6 Parameter Table

| Parameter | Value | Used By | Role In Crash | Source / Rationale |
|---|---:|---|---|---|
| `base_price_impact` | 0.08 | Market | Net-demand impact | Calibrated scale for visible stress in 200 rounds |
| `mean_reversion` | 0.01 | Market | Fundamental pull | Slow recovery consistent with crisis persistence |
| `noise_std` | 0.5 | Market | Exogenous disturbance | Background microstructure noise |
| `target_volatility` | 2.0 | RiskParityFund | Deleveraging target | Volatility-management mechanism from Moreira and Muir (2017) |
| `margin_call_level` | 0.5 | LeveragedHedgeFund | Partial deleveraging trigger | Margin-spiral calibration from Brunnermeier and Pedersen (2009) |
| `liquidation_level` | 0.3 | LeveragedHedgeFund | Forced liquidation trigger | Stress threshold for severe balance-sheet impairment |
| `volatility_withdraw_threshold` | 5.0 | MarketMaker | Liquidity withdrawal trigger | Liquidity-supply stress proxy |
| `rebalance_frequency` | 20 | PassiveInvestor | Slow stabilizing cadence | Long-horizon rebalancing approximation |
| `panic_sell_fraction` | 0.5 | PanicSeller | Behavioral liquidation intensity | Loss-aversion stress response |
| `discount_threshold` | 0.10 | BottomFisher | Contrarian entry | Value/contrarian discount threshold |

## §7 Communication And Round Structure

Each round follows market broadcast, investor order, and market update. The
market broadcasts stress state. Investors decide signed quantity and price.
RuleLLM and Rag additionally emit `provides_liquidity`, and Rag records
`rag_context` for retrieval audit.

## §8 Historical Case Studies

### §8.1 2008 Global Financial Crisis

The scenario reflects leverage, funding stress, liquidity withdrawal, and panic
liquidation observed during the 2008 crisis.

### §8.2 March 2020 Liquidity Shock

Rapid liquidity evaporation and volatility-sensitive selling in March 2020
illustrate how risk limits and dealer balance sheets can magnify price moves.

## §9 Variant Comparison Preview

| Variant | Role Set | Runtime Contract | Expected Use |
|---|---|---|---|
| Rule | Six archetypes including PassiveInvestor | Deterministic orders | Full mechanism baseline |
| LLM | Five API archetypes | Canonical trading JSON | Persona-driven crash behavior |
| RuleLLM | Five API archetypes | Canonical trading JSON plus liquidity flag | Rule-constrained API behavior |
| Rag | Five API archetypes | RuleLLM contract plus `rag_context` | Retrieval effect on crisis reasoning |
