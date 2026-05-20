# MomentumEffect Simulation Bases

## §1 Phenomenon Definition

MomentumEffect models return continuation created by trend-following demand,
technical signals, delayed contrarian response, passive rebalancing, and
fundamental anchoring.

## §2 Theoretical Foundation

### §2.1 Price Momentum

Empirical asset pricing documents that recent winners can continue to
outperform over intermediate horizons.

### §2.2 Positive Feedback Trading

Trend followers buy after price increases and sell after declines, creating
continuation pressure.

### §2.3 Limits To Reversal

Contrarian and fundamental traders eventually oppose mispricing but may be too
slow to eliminate short-run momentum.

## §3 Market Mechanism

The market broadcasts price history and deviation from fundamental. Investors
use recent returns, moving averages, allocation targets, and value thresholds to
submit orders. Net demand updates price.

## §4 Investor Archetypes

### §4.1 MomentumTrader

**Summary**: Buys recent winners and sells recent losers.
**Theoretical and Empirical Basis**: Momentum and positive-feedback trading.
**Design Purpose**: Generate return continuation.
**Behavioral Framework**: Uses `momentum_threshold`, `scale`, and
`max_position`.
**Decision Process**: Trade in the direction of recent price movement when
momentum exceeds threshold.
**Worked Numerical Example**: A positive recent return above threshold triggers
a buy scaled by signal strength.
**Academic References**: Jegadeesh and Titman (1993).

### §4.2 ContrarianTrader

**Summary**: Trades against large moves after reversion threshold.
**Theoretical and Empirical Basis**: Mean reversion and overreaction.
**Design Purpose**: Limit runaway trends.
**Behavioral Framework**: Uses `reversion_threshold`, `scale`, and
`max_position`.
**Decision Process**: Sell after excessive rise or buy after excessive fall.
**Worked Numerical Example**: A price move beyond reversion threshold triggers
opposite-side order.
**Academic References**: De Bondt and Thaler (1985).

### §4.3 IndexFund

**Summary**: Rebalances toward target allocation.
**Theoretical and Empirical Basis**: Passive allocation rebalancing.
**Design Purpose**: Add slow stabilizing flow.
**Behavioral Framework**: Uses `target_allocation` and `rebalance_threshold`.
**Decision Process**: Buy or sell to restore target allocation.
**Worked Numerical Example**: If allocation drifts below target, buys.
**Academic References**: Portfolio rebalancing literature.

### §4.4 MarketMaker

**Summary**: Supplies liquidity around an inventory target.
**Theoretical and Empirical Basis**: Inventory-control market making.
**Design Purpose**: Provide liquidity and mild mean reversion.
**Behavioral Framework**: Uses `inventory_target` and `reversion_speed`.
**Decision Process**: Trade toward inventory target and dampen order imbalance.
**Worked Numerical Example**: Excess inventory leads to sell quotes.
**Academic References**: Ho and Stoll (1981).

### §4.5 TechnicalTrader

**Summary**: Uses moving-average signals.
**Theoretical and Empirical Basis**: Technical trend-following.
**Design Purpose**: Add signal-based trend reinforcement.
**Behavioral Framework**: Uses `short_window`, `long_window`, `scale`, and
`max_position`.
**Decision Process**: Buy when short-window trend exceeds long-window trend;
sell when it falls below.
**Worked Numerical Example**: Short average above long average triggers buy.
**Academic References**: Technical trading literature.

### §4.6 FundamentalTrader

**Summary**: Trades against deviation from fundamental value.
**Theoretical and Empirical Basis**: Fundamental-value anchoring.
**Design Purpose**: Provide long-run anchor against momentum overshoot.
**Behavioral Framework**: Uses `value_threshold`, `scale`, and `max_position`.
**Decision Process**: Buy undervaluation, sell overvaluation.
**Worked Numerical Example**: Price 15% below fundamental with 10% threshold
triggers buy.
**Academic References**: Value investing and limits-of-arbitrage literature.

## §5 Agent Diversity Verification

The population includes trend followers, contrarians, passive rebalancers,
liquidity suppliers, technical traders, and fundamental anchors.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `momentum_threshold` | Trend activation | MomentumTrader | High |
| `reversion_threshold` | Contrarian activation | ContrarianTrader | Medium |
| `target_allocation` | Passive target | IndexFund | Low |
| `inventory_target` | Market-maker inventory | MarketMaker | Medium |
| `short_window` / `long_window` | Technical signal windows | TechnicalTrader | High |
| `value_threshold` | Fundamental activation | FundamentalTrader | Medium |

## §7 Communication And Round Structure

Market broadcasts state and price history; agents compute trend, reversion, or
value signals; market aggregates orders and updates price.

## §8 Historical Case Studies

### §8.1 Equity Momentum

Cross-sectional momentum is widely documented in equities and motivates
MomentumTrader and TechnicalTrader behavior.

### §8.2 Trend-Following Crowding

Crowded trend-following strategies can reinforce market moves until contrarian
capital enters.

## §9 Variant Comparison Preview

Rule should show the cleanest continuation. LLM may soften or exaggerate
signals. RuleLLM preserves explicit signal rules. Rag may use retrieved momentum
research to adjust conviction.
