# LUNACollapse Simulation Bases

## §1 Phenomenon Definition

LUNACollapse models the May 2022 Terra/LUNA collapse as an algorithmic stablecoin
death spiral. A confidence shock to UST-like stablecoin holders triggers
redemptions into the base token, increases effective base-token supply, weakens
the perceived fundamental anchor, and then feeds back through arbitrage,
liquidations, yield-protocol withdrawals, and overwhelmed value buying.

The simulation abstracts the historical episode into a single risky asset with a
fundamental anchor. The key mechanism is not ordinary volatility; it is the
endogenous conversion of confidence loss into sell pressure and forced
deleveraging.

## §2 Theoretical Foundation

### §2.1 Algorithmic Stablecoin Fragility

Algorithmic stablecoins rely on arbitrage and confidence rather than fully
reserved collateral. Klages-Mundt et al. (2020) describe how design choices can
create reflexive stability when confidence is high and reflexive instability
when redemptions dominate.

### §2.2 Death-Spiral Feedback

Death spirals occur when a stabilizing mechanism becomes destabilizing under
stress. In Terra/LUNA, redemption and arbitrage channels converted peg pressure
into base-token supply and selling pressure, worsening the very collateral
confidence needed to stabilize the peg.

### §2.3 DeFi Contagion And Liquidation Cascades

DeFi protocols transmit shocks through collateral thresholds, liquidity
withdrawals, and forced liquidations. Werner et al. (2022) and related DeFi risk
work motivate the lender/liquidator and yield-depositor agents.

## §3 Market Mechanism

The market follows a standard demand-impact model:

```text
P(t+1) = max(P(t) + lambda * D(t) + gamma * (F - P(t)) + epsilon(t), 0.01)
```

where `D(t)` is buy volume minus sell volume, `lambda` is price impact, `gamma`
is mean reversion toward fundamental value, and `epsilon(t)` is Gaussian noise.

The market publishes `price`, `fundamental`, `deviation`, and `round` each
round. Investors send `{action, quantity}` orders.

## §4 Investor Archetypes

### §4.1 StablecoinHolder

**Summary**: A holder who redeems stablecoin exposure when confidence breaks.

**Theoretical and Empirical Basis**: Algorithmic stablecoin redemption pressure
observed during Terra/LUNA and described in algorithmic stablecoin risk models.

**Design Purpose**: Represent panic redemption flow that turns peg stress into
base-token selling pressure.

**Behavioral Framework**: Monitors deviation from fundamental value. When the
deviation breaches the redemption threshold, sells a fraction of current
position.

**Decision Process**: If `deviation < -(1 - redemption_threshold)`, sell up to
50% of position; otherwise hold.

**Worked Numerical Example**: With `redemption_threshold = 0.98`,
`deviation = -0.04`, and `position = 100000`, the holder sells 50000 units.

**Academic References**: Klages-Mundt et al. (2020); Levy (2022).

### §4.2 Arbitrageur

**Summary**: A trader exploiting UST/LUNA-style arbitrage, amplifying the spiral
when the gap is large.

**Theoretical and Empirical Basis**: Arbitrage is intended to stabilize an
algorithmic peg but can increase base-token pressure during runs.

**Design Purpose**: Encode the arbitrage channel that scales with mispricing.

**Behavioral Framework**: Trades when absolute deviation exceeds
`arb_threshold`.

**Decision Process**: Quantity scales with `abs(deviation) * 100000`, capped at
5000 and constrained by cash or position.

**Worked Numerical Example**: With `deviation = -0.08`, target quantity is 5000;
the arbitrageur buys if cash allows.

**Academic References**: Klages-Mundt et al. (2020); Terra/LUNA postmortem
analyses.

### §4.3 DeFiLender

**Summary**: A lending protocol participant that liquidates collateral after a
sharp price decline.

**Theoretical and Empirical Basis**: DeFi liquidations transmit price shocks
through collateral thresholds.

**Design Purpose**: Add forced selling that is not discretionary once collateral
health deteriorates.

**Behavioral Framework**: Monitors deviation and liquidation threshold.

**Decision Process**: If price deviation implies collateral impairment beyond
`liquidation_threshold`, sell a protocol-defined fraction of position.

**Worked Numerical Example**: With `liquidation_threshold = 0.8` and a 25%
discount, the lender enters forced-sale mode.

**Academic References**: Werner et al. (2022); DeFi liquidation literature.

### §4.4 AnchorDepositor

**Summary**: A yield depositor who exits when confidence in the yield ecosystem
falls.

**Theoretical and Empirical Basis**: Anchor Protocol withdrawals were central to
the Terra confidence collapse.

**Design Purpose**: Represent slower but large deposit flight from yield
strategies.

**Behavioral Framework**: Uses `yield_threshold` and market deviation as a
confidence proxy.

**Decision Process**: Withdraw/sell when confidence falls below the configured
threshold; otherwise hold.

**Worked Numerical Example**: If confidence-implied yield falls below 15%, the
depositor exits part of the position.

**Academic References**: Terra/Anchor event analyses; DeFi run literature.

### §4.5 ValueBuyer

**Summary**: A contrarian buyer that attempts to buy deep discounts but is often
too small to stop the spiral.

**Theoretical and Empirical Basis**: Limits-of-arbitrage theory explains why
value buyers may be overwhelmed during funding stress.

**Design Purpose**: Provide a stabilizing force and test whether it can absorb
panic selling.

**Behavioral Framework**: Buys when `deviation < -discount_threshold`.

**Decision Process**: If discount is deep enough, buy cash-constrained quantity;
otherwise hold.

**Worked Numerical Example**: With `discount_threshold = 0.5`, the buyer waits
for a 50% discount before deploying capital.

**Academic References**: Shleifer and Vishny (1997); crisis arbitrage evidence.

## §5 Agent Diversity Verification

The scenario includes panic sellers, arbitrage amplifiers, forced liquidators,
yield exiters, and contrarian buyers. This creates a destabilizing majority with
one stabilizing archetype, matching the intended death-spiral design.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `initial_price` | Starting asset price | Market | Scale only |
| `fundamental_value` | Reference value | Market | Determines deviation |
| `price_impact` | Demand-to-price response | Market | High |
| `mean_reversion` | Pull toward fundamental | Market | Medium |
| `noise_std` | Exogenous noise | Market | Low |
| `redemption_threshold` | Stablecoin-holder panic trigger | StablecoinHolder | High |
| `arb_threshold` | Arbitrage activation threshold | Arbitrageur | Medium |
| `liquidation_threshold` | Forced-sale trigger | DeFiLender | High |
| `yield_threshold` | Yield exit trigger | AnchorDepositor | Medium |
| `discount_threshold` | Value-buyer entry discount | ValueBuyer | Medium |

## §7 Communication And Round Structure

Each round:

1. Market broadcasts price, fundamental, deviation, and round.
2. Investors perceive the broadcast and update internal state.
3. Investors submit buy/sell/hold orders.
4. Market aggregates net demand and updates price.
5. Artifacts record messages, orders, and market history.

## §8 Historical Case Studies

### §8.1 Terra/LUNA Collapse, May 2022

UST lost its dollar peg, LUNA issuance and selling pressure accelerated, Anchor
withdrawals intensified, and more than $40B in market value was destroyed. The
simulation maps this to redemption pressure, arbitrage pressure, DeFi exits, and
overwhelmed value buying.

### §8.2 Algorithmic Stablecoin Stress Episodes

Earlier algorithmic stablecoin failures showed that confidence-based
stabilization can invert into a run dynamic. These cases motivate the generic
stablecoin-holder and arbitrageur mechanisms.

## §9 Variant Comparison Preview

| Variant | Expected Behavior |
|---|---|
| Rule | Deterministic death-spiral mechanics from thresholds |
| LLM | Persona-driven panic and discretion may alter timing |
| RuleLLM | Rule formulas remain explicit but LLM may vary quantity/reasoning |
| Rag | Retrieved stablecoin/depeg context may amplify or moderate panic reasoning |
