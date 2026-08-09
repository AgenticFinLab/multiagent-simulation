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

The shipped market is the openly disclosed single-risky-asset approximation of
`masim/agents/defines/market/crypto-algostable-depeg.md`. It isolates the LUNA
leg of the death spiral while preserving the depeg-to-selling causal chain:

```text
P(t+1) = max(P_floor,
             P(t) + lambda * D(t) / M
                  + gamma * (F - P(t))
                  + epsilon(t) + F * S(t))
```

where `D(t)` is feasible buy volume minus sell volume, `M` is market depth,
`lambda` is price impact, `gamma` is mean reversion, `epsilon(t)` is a
round/identity-seeded Gaussian draw, and `S(t)` is the bounded May 2022 depeg
identification stimulus from target §6.1 and §9. Depth normalization prevents
agent-count changes from producing an accidental price-unit explosion.

The market publishes `price`, `fundamental`, `deviation`, and `round` each
round. Investors send canonical orders containing `type`, `from`, `action`,
`bid_price`, `quantity`, `reasoning`, `agent_type`, and `strategy`. Each
investor writes the order into the decision payload's `outbound_messages`
before returning its Action, as required by the scheduler's routing hook.

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

**Decision Process**: If `deviation < -redemption_threshold`, sell up to
50% of position; otherwise hold.

**Worked Numerical Example**: With `redemption_threshold = 0.05`,
`deviation = -0.06`, and `position = 100000`, the holder sells 50000 units.

**Academic References**: Uhlig (2022), https://doi.org/10.3386/w30256;
Klages-Mundt et al. (2020), https://arxiv.org/abs/2006.12388.

### §4.2 Arbitrageur

**Summary**: A trader exploiting UST/LUNA-style arbitrage, amplifying the spiral
when the gap is large.

**Theoretical and Empirical Basis**: Arbitrage is intended to stabilize an
algorithmic peg but can increase base-token pressure during runs.

**Design Purpose**: Encode the arbitrage channel that scales with mispricing.

**Behavioral Framework**: Trades when absolute deviation exceeds
`arb_threshold`.

**Decision Process**: Quantity scales with `abs(deviation) * 100000`, capped at
5000 and constrained by inventory. Under negative deviation the conversion
channel sells the LUNA-like base token; buying here would incorrectly turn the
death-spiral channel into ordinary value arbitrage.

**Worked Numerical Example**: With `deviation = -0.08`, target quantity is 5000;
the arbitrageur sells up to its available inventory.

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

**Decision Process**: If `deviation < -liquidation_threshold`, sell a
protocol-defined fraction of position.

**Worked Numerical Example**: With `liquidation_threshold = 0.15` and a 20%
discount, the lender enters forced-sale mode.

**Academic References**: Werner et al. (2022),
https://doi.org/10.1145/3558535.3559780.

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

**Worked Numerical Example**: If confidence-implied stress exceeds 5%, the
depositor exits part of the position.

**Academic References**: Diamond and Dybvig (1983),
https://doi.org/10.1086/261155; SEC (2023),
https://www.sec.gov/files/terraform-labs-pte-ltd-amended-complaint.pdf.

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

**Worked Numerical Example**: With `discount_threshold = 0.30`, the buyer waits
for a 30% discount before deploying capital.

**Academic References**: Shleifer and Vishny (1997),
https://doi.org/10.1111/j.1540-6261.1997.tb03807.x.

## §5 Agent Diversity Verification

The scenario includes panic sellers, arbitrage amplifiers, forced liquidators,
yield exiters, and contrarian buyers. This creates a destabilizing majority with
one stabilizing archetype, matching the intended death-spiral design.

## §6 Parameter Table

| Parameter | Config Path | Meaning | Source Rationale | Sensitivity |
|---|---|---|---|---|
| `initial_price` | `market.extras.initial_price` | Starting asset price | Normalized index value for cross-scenario comparison | Scale only |
| `fundamental_value` | `market.extras.fundamental_value` | Reference value | Stablecoin peg/fundamental anchor abstraction | Determines deviation |
| `price_impact` | `market.extras.price_impact` | Demand-to-price response | Thin crisis liquidity during stablecoin runs | High |
| `mean_reversion` | `market.extras.mean_reversion` | Pull toward fundamental | Weak stabilizing arbitrage under stress | Medium |
| `noise_std` | `market.extras.noise_std` | Exogenous noise | Background market uncertainty | Low |
| `market_depth` | `market.extras.market_depth` | Order-flow normalization | Prevents population-scale unit explosions | High |
| `random_seed` | `market.extras.random_seed` | Reproducible noise | Pipeline replay invariant | Low |
| `price_floor` | `market.extras.price_floor` | Positive-price clamp | Numerical invariant | Low |
| `shock_schedule` | `market.extras.shock_schedule` | May 2022 identification stimulus | Target §6.1 and §9 | High |
| `redemption_threshold` | `stablecoinholder.extras.redemption_threshold` | Panic redemption trigger | Peg-break confidence threshold | High |
| `arb_threshold` | `arbitrageur.extras.arb_threshold` | Arbitrage activation threshold | Spread threshold for conversion trades | Medium |
| `liquidation_threshold` | `defilender.extras.liquidation_threshold` | Forced-sale trigger | Collateral impairment threshold | High |
| `yield_threshold` | `anchordepositor.extras.yield_threshold` | Yield exit trigger | Confidence-loss threshold for Anchor-style withdrawals | Medium |
| `discount_threshold` | `valuebuyer.extras.discount_threshold` | Value-buyer entry discount | Limits-of-arbitrage entry point | Medium |

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

### §8.3 Iron Finance / TITAN Collapse, June 2021

Iron Finance's partially algorithmic stablecoin design suffered a reflexive run
when redemption pressure and confidence loss overwhelmed stabilization
mechanisms. The episode motivates the simulation's conversion of peg stress into
base-token sell pressure and the limited ability of arbitrage to restore value
once confidence has broken.

## §9 Variant Comparison Preview

| Variant | Expected Behavior |
|---|---|
| Rule | Deterministic death-spiral mechanics from thresholds |
| LLM | Persona-driven panic and discretion may alter timing |
| RuleLLM | Rule formulas remain explicit but LLM may vary quantity/reasoning |
| Rag | Retrieved stablecoin/depeg context may amplify or moderate panic reasoning |

All four variants trace to target §10.1. The current polish run formally
calibrates Rule, performs bounded contract checks for LLM and RuleLLM, and
limits Rag to static configuration and import validation.
