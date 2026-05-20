# MarketCrash Simulation Bases

## §1 Phenomenon Definition

MarketCrash models a broad equity-market crash caused by leverage, volatility
targeting, liquidity withdrawal, panic selling, and delayed stabilizing demand.
The scenario emphasizes endogenous feedback: falling prices increase risk,
forced selling, and panic, which further lowers prices.

## §2 Theoretical Foundation

### §2.1 Leverage And Margin Spirals

Leveraged investors facing margin constraints sell into falling markets,
creating a self-reinforcing decline.

### §2.2 Volatility Targeting And Risk Parity

Risk-managed portfolios reduce exposure when realized volatility rises, adding
mechanical sell pressure during drawdowns.

### §2.3 Liquidity Withdrawal

Market makers reduce quote size and inventory risk when volatility rises,
making price impact larger exactly when liquidity is needed.

## §3 Market Mechanism

The market broadcasts price, fundamental value, deviation, volatility, and round
state. Net buy/sell demand moves price through a demand-impact equation with
mean reversion and noise. Liquidity-sensitive agents can reduce stabilizing
depth and increase effective crash severity.

## §4 Investor Archetypes

### §4.1 RiskParityFund

**Summary**: A volatility-targeting fund that rebalances toward target risk.
**Theoretical and Empirical Basis**: Risk parity and volatility-managed
portfolio literature.
**Design Purpose**: Add mechanical selling when volatility rises.
**Behavioral Framework**: Uses `target_volatility`, `rebalance_speed`, and
`base_position`.
**Decision Process**: Reduce exposure when observed volatility exceeds target.
**Worked Numerical Example**: If realized volatility doubles target volatility,
the fund sells part of the base position.
**Academic References**: Volatility-managed portfolio and risk-parity studies.

### §4.2 LeveragedHedgeFund

**Summary**: A leveraged trader subject to margin calls and liquidation.
**Theoretical and Empirical Basis**: Leverage-cycle and margin-spiral theory.
**Design Purpose**: Create forced selling after losses.
**Behavioral Framework**: Uses `margin_call_level`, `liquidation_level`, and
`momentum_sensitivity`.
**Decision Process**: Sell when losses approach margin constraints; liquidate
more aggressively below liquidation level.
**Worked Numerical Example**: A price drop below margin-call level triggers
partial deleveraging.
**Academic References**: Brunnermeier and Pedersen (2009).

### §4.3 MarketMaker

**Summary**: A liquidity supplier that withdraws when volatility is high.
**Theoretical and Empirical Basis**: Market microstructure and inventory-risk
models.
**Design Purpose**: Make liquidity endogenous.
**Behavioral Framework**: Uses `inventory_limit`, `normal_quote_size`, and
`volatility_withdraw_threshold`.
**Decision Process**: Provide quotes in normal markets; reduce quote size or
hold when volatility exceeds threshold.
**Worked Numerical Example**: When volatility crosses the withdrawal threshold,
quote size drops from normal size toward zero.
**Academic References**: Ho and Stoll (1981); liquidity spiral literature.

### §4.4 PassiveInvestor

**Summary**: A slow rebalancer that targets a long-run position.
**Theoretical and Empirical Basis**: Passive index and allocation rebalancing.
**Design Purpose**: Provide slow stabilizing demand.
**Behavioral Framework**: Uses `target_position` and `rebalance_frequency`.
**Decision Process**: Rebalance periodically toward target position.
**Worked Numerical Example**: If position falls below target on a rebalance
round, the investor buys.
**Academic References**: Portfolio rebalancing literature.

### §4.5 PanicSeller

**Summary**: A discretionary investor who sells after losses exceed a trigger.
**Theoretical and Empirical Basis**: Loss aversion and panic selling.
**Design Purpose**: Add behavioral selling during drawdowns.
**Behavioral Framework**: Uses `loss_threshold`, `crash_trigger`, and
`panic_sell_fraction`.
**Decision Process**: Sell a fraction of holdings when loss/crash thresholds
are crossed.
**Worked Numerical Example**: With a 20% panic fraction and 1000 shares, sells
200 shares after trigger.
**Academic References**: Prospect theory and crisis-selling evidence.

### §4.6 BottomFisher

**Summary**: A stabilizing buyer that enters after deep discounts.
**Theoretical and Empirical Basis**: Value investing and limits of arbitrage.
**Design Purpose**: Test whether contrarian capital can absorb panic selling.
**Behavioral Framework**: Uses `discount_threshold`, `crash_buy_threshold`,
`buy_size`, and `lookback`.
**Decision Process**: Buy when discount and crash-depth conditions are met.
**Worked Numerical Example**: If price is 30% below fundamental and threshold
is 20%, buys configured size if cash allows.
**Academic References**: Graham-style value investing; Shleifer and Vishny
(1997).

## §5 Agent Diversity Verification

The scenario combines mechanical deleveragers, liquidity withdrawers,
behavioral sellers, slow passive stabilizers, and contrarian buyers.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `target_volatility` | Risk target | RiskParityFund | High |
| `rebalance_speed` | Speed of risk reduction | RiskParityFund | High |
| `margin_call_level` | Deleveraging trigger | LeveragedHedgeFund | High |
| `liquidation_level` | Forced liquidation trigger | LeveragedHedgeFund | High |
| `volatility_withdraw_threshold` | Liquidity withdrawal trigger | MarketMaker | High |
| `panic_sell_fraction` | Behavioral sell size | PanicSeller | Medium |
| `discount_threshold` | Value entry threshold | BottomFisher | Medium |

## §7 Communication And Round Structure

Market broadcasts state; investors evaluate risk, leverage, liquidity, panic,
or value thresholds; orders return to market; price and volatility update.

## §8 Historical Case Studies

### §8.1 2008 Global Equity Crash

Deleveraging, funding constraints, liquidity withdrawal, and panic selling
combined to produce broad equity declines.

### §8.2 March 2020 COVID Liquidity Shock

Risk reduction and liquidity withdrawal amplified a rapid equity drawdown before
policy stabilization.

## §9 Variant Comparison Preview

Rule provides deterministic crash feedback. LLM may show discretionary panic or
hesitation. RuleLLM anchors agents to explicit rules. Rag may introduce crisis
precedent knowledge into risk and liquidity reasoning.
