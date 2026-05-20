# Volmageddon Simulation Bases

## §1 Phenomenon Definition

Volmageddon models the February 2018 volatility shock in which short-volatility
strategies and inverse-volatility exchange-traded products were forced to
rebalance into a rising VIX, creating positive feedback between volatility
products and equity-market stress.

## §2 Theoretical Foundation

### §2.1 Short-Volatility Carry

Short volatility earns carry in calm markets but is exposed to convex losses
when volatility spikes.

### §2.2 Inverse-ETN Rebalancing

Inverse volatility products must buy volatility exposure after volatility rises,
which can amplify the spike.

### §2.3 Volatility-Equity Feedback

Volatility shocks can force risk reduction in equities, linking derivatives and
cash markets.

## §3 Market Mechanism

The market tracks a volatility/price proxy updated by net demand, mean
reversion, and noise. Volatility-product orders can reinforce shocks when VIX
rises and equity traders de-risk.

## §4 Investor Archetypes

### §4.1 ShortVolTrader

**Summary**: Sells volatility for carry but faces stop-loss tail risk.
**Theoretical and Empirical Basis**: Short-volatility risk-premium strategies.
**Design Purpose**: Provide fragile calm-market supply of volatility.
**Behavioral Framework**: Uses `stop_loss`.
**Decision Process**: Reduces or reverses position when losses breach stop-loss.
**Worked Numerical Example**: A volatility spike beyond stop-loss triggers
buy-to-cover pressure.
**Academic References**: Volatility risk-premium literature.

### §4.2 VolETNManager

**Summary**: Rebalances inverse VIX ETN exposure mechanically.
**Theoretical and Empirical Basis**: Inverse volatility product rebalancing.
**Design Purpose**: Encode positive-feedback demand during VIX spikes.
**Behavioral Framework**: Uses `rebalance_threshold` and `rebalance_size`.
**Decision Process**: Buys volatility exposure when threshold is breached.
**Worked Numerical Example**: A VIX rise beyond threshold triggers rebalance
quantity.
**Academic References**: 2018 inverse-VIX ETN analyses.

### §4.3 LongVolHedger

**Summary**: Holds long volatility as portfolio insurance.
**Theoretical and Empirical Basis**: Volatility hedging and crash insurance.
**Design Purpose**: Provide stabilizing or profit-taking behavior during spikes.
**Behavioral Framework**: Uses `hedge_ratio`.
**Decision Process**: Adjusts hedge quantity with volatility stress.
**Worked Numerical Example**: A higher hedge ratio increases long-vol demand.
**Academic References**: Portfolio insurance and volatility hedging literature.

### §4.4 VolArbitrageur

**Summary**: Trades volatility term-structure dislocations.
**Theoretical and Empirical Basis**: Volatility arbitrage.
**Design Purpose**: Add liquidity and partial mean reversion.
**Behavioral Framework**: Uses `entry_threshold`.
**Decision Process**: Trades only when dislocation exceeds entry threshold.
**Worked Numerical Example**: A large spread triggers arbitrage order.
**Academic References**: VIX futures term-structure research.

### §4.5 EquityTrader

**Summary**: Trades equities under volatility-based risk limits.
**Theoretical and Empirical Basis**: Volatility targeting and risk parity.
**Design Purpose**: Connect vol spike to equity de-risking.
**Behavioral Framework**: Uses `risk_limit`.
**Decision Process**: Sells/de-risks when volatility breaches risk limit.
**Worked Numerical Example**: A volatility jump above risk limit triggers equity
sell pressure.
**Academic References**: Volatility targeting literature.

## §5 Agent Diversity Verification

The scenario includes short-vol carry sellers, mechanical inverse-product
rebalancers, long-vol hedgers, arbitrageurs, and equity de-riskers.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `stop_loss` | Short-vol loss trigger | ShortVolTrader | High |
| `rebalance_threshold` | ETN rebalance trigger | VolETNManager | High |
| `rebalance_size` | Rebalance order size | VolETNManager | High |
| `hedge_ratio` | Long-vol hedge scale | LongVolHedger | Medium |
| `entry_threshold` | Arbitrage activation | VolArbitrageur | Medium |
| `risk_limit` | Equity de-risking trigger | EquityTrader | High |

## §7 Communication And Round Structure

Market broadcasts volatility/price state; agents update risk or product
exposure; orders are routed to market; net demand updates volatility and price
state.

## §8 Historical Case Studies

### §8.1 February 2018 Volmageddon

The VIX spiked sharply and inverse volatility products suffered extreme losses,
with mechanical rebalancing reinforcing volatility demand.

### §8.2 Volatility-Targeting Deleveraging Episodes

Risk-parity and volatility-control strategies have repeatedly reduced exposure
after volatility jumps, linking derivative shocks to broader markets.

## §9 Variant Comparison Preview

Rule encodes mechanical volatility feedback. LLM may introduce discretionary
hesitation or panic. RuleLLM keeps explicit rules with natural-language
variation. Rag may use historical Volmageddon context to change rebalancing
urgency.
