# StatusQuoBias — Simulation Design Basis

## §1 Phenomenon Definition

| Item | Description |
|---|---|
| Phenomenon Name | Status quo bias in financial portfolio decisions |
| Category | Behavioral bias / allocation inertia |
| Core Mechanism | Investors overweight their current allocation or default option. Moderate valuation signals are ignored until a large deviation forces action, so prices adjust slowly relative to fundamental value. |
| Real-World Origin | Experimental evidence in Samuelson and Zeckhauser (1988), retirement-plan defaults in Madrian and Shea (2001), and household portfolio inertia in brokerage and pension accounts. |
| Research Relevance | Status quo bias links micro-level inaction to underreaction, weak rebalancing, and slow correction of mispricing. |

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Samuelson and Zeckhauser (1988) established that individuals choose the current
state disproportionately often even when alternatives are economically
attractive. Their experiments and field examples motivated the `InertialHolder`
agent, which requires a large deviation before changing position.

Kahneman, Knetsch, and Thaler (1991) connected status quo bias to loss aversion
and the endowment effect. In this simulation, the current portfolio is treated
as a reference allocation. The cost of changing away from it is represented by
high action thresholds rather than a separate utility function.

Madrian and Shea (2001) showed that retirement-plan defaults change savings
participation and asset allocation. This evidence motivates the
`DefaultFollower`, which stays near a passive default allocation unless drift is
large enough to justify action.

Active rebalancing and momentum trading are included as contrasts. Rational
rebalancers represent the benchmark that reacts to valuation gaps, while
momentum traders represent price-trend demand that can overcome inertia. Noise
traders add low-information liquidity so the market is not mechanically
determined by biased agents alone.

#### §1.1.2 Real-World Event Catalogue

| Event Name | Date(s) | Market / Asset | Trigger | Magnitude | Duration | Correspondence to Simulation | Primary Source |
|---|---|---|---|---|---|---|---|
| Retirement plan default enrollment | 1998-1999 sample | US 401(k) plans | Automatic enrollment default | Participation rose from about 49% to 86% for new hires | First 3-15 months of employment | `DefaultFollower` accepts passive allocation until drift is large | Madrian and Shea (2001), *Quarterly Journal of Economics*, https://doi.org/10.1162/003355301753265543 |
| Swedish Premium Pension default fund | 2000 onward | Swedish retirement accounts | Default fund introduced at launch | Majority of later entrants remained in default allocation | Multi-year pension cohort behavior | Default option persistence maps to `DefaultFollower` | Cronqvist and Thaler (2004), *American Economic Review*, https://doi.org/10.1257/0002828041301633 |
| Household portfolio inertia | 1991-1996 | US discount brokerage accounts | Investors failed to rebalance after information and price changes | Individual investors underperformed market benchmarks by several percentage points annually | Multi-year account panel | `InertialHolder` and `NoiseTrader` reproduce delayed adjustment and background trading | Barber and Odean (2000), *Journal of Finance*, https://doi.org/10.1111/0022-1082.00226 |
| Pension plan contribution inertia | 1990s-2000s | US defined-contribution plans | Employees retained contribution and allocation defaults | Large fraction of participants kept defaults for years | Multi-year plan records | Sticky allocation supports default-adherence metric | Benartzi and Thaler (2007), *Journal of Economic Perspectives*, https://doi.org/10.1257/jep.21.3.81 |
| Price momentum anomaly | 1965-1989 sample | US equities | Trend-following return continuation | 3- to 12-month winners outperformed losers by about 1% per month | 3-12 month horizons | `MomentumTrader` offsets pure inertia when price trends are visible | Jegadeesh and Titman (1993), *Journal of Finance*, https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |

#### §1.1.3 Book and Practitioner Literature

| Title | Author(s) | Year | Publisher | Relevance to This Simulation |
|---|---|---|---|---|
| *Nudge* | Thaler and Sunstein | 2008 | Yale University Press | Explains how defaults shape financial behavior and motivates default-following agents. |
| *Misbehaving* | Thaler | 2015 | W. W. Norton | Provides practitioner-facing examples of status quo bias, endowment effects, and savings-plan inertia. |

## §2 Theoretical Foundation

### §2.1 Status Quo Bias

- **Primary Citation**: Samuelson, W., and Zeckhauser, R. (1988). "Status quo bias in decision making." *Journal of Risk and Uncertainty*, 1, 7-59. https://doi.org/10.1007/BF00055564
- **Core Mechanism**: The current state receives an implicit preference premium. An investor changes only when perceived benefit exceeds a psychological switching cost.
- **Model**:
  ```text
  act iff |delta(t)| > theta_status
  delta(t) = [P(t) - F] / F
  ```
- **Empirical Evidence**: Experiments and field examples show persistent selection of the incumbent option.
- **Simulation Mapping**: `InertialHolder` in §4.1 uses `change_threshold` and `inertia_strength` to convert this switching cost into a high trading threshold.

### §2.2 Default Effects

- **Primary Citation**: Madrian, B. C., and Shea, D. F. (2001). "The power of suggestion: Inertia in 401(k) participation and savings behavior." *Quarterly Journal of Economics*, 116(4), 1149-1187. https://doi.org/10.1162/003355301753265543
- **Core Mechanism**: When a default option is supplied, inattention and decision costs cause many participants to accept it passively.
- **Model**:
  ```text
  trade iff |delta(t)| > theta_default
  desired_trade_size = base_size * |delta(t)| / theta_default * default_weight
  ```
- **Empirical Evidence**: Automatic enrollment sharply changed participation and default allocation choices.
- **Simulation Mapping**: `DefaultFollower` in §4.2 trades only after deviation exceeds `active_deviation`.

### §2.3 Reference Dependence and Endowment Effects

- **Primary Citation**: Kahneman, D., Knetsch, J. L., and Thaler, R. H. (1991). "Anomalies: The endowment effect, loss aversion, and status quo bias." *Journal of Economic Perspectives*, 5(1), 193-206. https://doi.org/10.1257/jep.5.1.193
- **Core Mechanism**: Current holdings form a reference point, and losses from changing away from that point loom larger than symmetric gains.
- **Model**:
  ```text
  perceived_gain = valuation_signal - switching_disutility(current_position)
  hold when perceived_gain <= 0
  ```
- **Empirical Evidence**: Laboratory and field evidence documents endowment-driven reluctance to trade.
- **Simulation Mapping**: The model is represented by high hold rates and conservative sizing for §4.1 and §4.2 agents.

### §2.4 Active Rebalancing

- **Primary Citation**: Markowitz, H. (1952). "Portfolio selection." *Journal of Finance*, 7(1), 77-91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
- **Core Mechanism**: A rational investor responds to valuation and risk signals by moving toward a desired allocation.
- **Model**:
  ```text
  trade iff |delta(t)| > theta_rebalance
  Q(t) = position_size * |delta(t)| / theta_rebalance
  ```
- **Empirical Evidence**: Rebalancing is a standard benchmark in portfolio management.
- **Simulation Mapping**: `ActiveRebalancer` in §4.3 supplies the non-inertial benchmark.

### §2.5 Momentum and Noise Trading

- **Primary Citations**: Jegadeesh, N., and Titman, S. (1993), *Journal of Finance*, https://doi.org/10.1111/j.1540-6261.1993.tb04702.x; Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- **Core Mechanism**: Trend followers trade with recent price movement, while noise traders generate non-informational orders.
- **Model**:
  ```text
  momentum_action = sign(delta) when |delta| > theta_momentum
  noise_action ~ Bernoulli(trade_probability)
  ```
- **Empirical Evidence**: Momentum returns and uninformed order flow are both documented in empirical finance.
- **Simulation Mapping**: `MomentumTrader` in §4.4 and `NoiseTrader` in §4.5 prevent a pure two-type model.

## §3 Market Design Principles

### §3.1 Price Formation Model

```text
P(t+1) = max(0.01, P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t))
```

| Symbol | Python Variable | Meaning | Config Path | Value |
|---|---|---|---|---|
| P(t) | `price` | Current market price | `extras.initial_price` | 100.0 |
| F | `fundamental` | Constant fundamental value | `extras.fundamental_value` | 100.0 |
| D(t) | `net_demand` | Buy quantity minus sell quantity | computed from orders | round-specific |
| lambda | `price_impact` | Demand impact coefficient | `extras.price_impact` | 0.02 |
| gamma | `mean_reversion` | Pull toward fundamental value | `extras.mean_reversion` | 0.02 |
| epsilon(t) | `noise` | Gaussian market noise | `extras.noise_std` | 0.01 |

### §3.2 Additional Mechanisms

| Mechanism | Trigger | Action | Economic Rationale |
|---|---|---|---|
| Portfolio affordability | Buy order exceeds cash | Quantity capped by `cash / price` | Prevents impossible leveraged buying. |
| Inventory constraint | Sell order exceeds holdings | Quantity capped by current position | Prevents short selling in this bias benchmark. |
| Inertia band | Valuation deviation remains below threshold | Investor holds | Represents switching costs and default persistence. |

## §4 Investor Archetypes

### §4.1 InertialHolder

#### §4.1.1 Summary

This investor represents households, trustees, and portfolio managers who prefer
not to disturb an existing allocation unless the signal is extreme.

In the simulation it generates sticky holdings and delayed price response. It is
the strongest direct representation of Samuelson and Zeckhauser's status quo
bias.

#### §4.1.2 Theoretical and Empirical Foundation

Samuelson and Zeckhauser (1988) show that current states receive excess choice
weight. Kahneman, Knetsch, and Thaler (1991) explain the same reluctance through
reference dependence and endowment effects.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `abs(deviation) <= change_threshold` | Hold | Produces underreaction | §2.1 |
| `deviation < -change_threshold` | Buy limited shares | Corrects large undervaluation slowly | §2.1 |
| `deviation > change_threshold` | Sell limited shares | Corrects large overvaluation slowly | §2.3 |

#### §4.1.4 Behavioral Framework

The agent observes price, fundamental, and deviation. It ignores moderate
signals and acts only when `abs(deviation)` exceeds `change_threshold`. Quantity
uses `base_size`, scaled by signal strength and damped by `inertia_strength`.

#### §4.1.5 Decision Process Walkthrough

If price is 130, fundamental is 100, and `change_threshold=0.3`, the agent is
just at the boundary and generally holds. If price reaches 145, it submits a
small sell order at the current price.

#### §4.1.6 Worked Numerical Example

```text
P=145, F=100, delta=0.45, threshold=0.30
Q = base_size * delta / threshold * (1 - inertia_strength + 0.1)
Q = 200 * 1.5 * 0.2 = 60 shares
```

#### §4.1.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Samuelson and Zeckhauser (1988), https://doi.org/10.1007/BF00055564 | High switching threshold. |
| 2 | Kahneman, Knetsch, and Thaler (1991), https://doi.org/10.1257/jep.5.1.193 | Reference dependence around current holdings. |

### §4.2 DefaultFollower

#### §4.2.1 Summary

This investor represents retirement-plan participants and passive allocators who
accept a default portfolio unless drift is highly visible.

In the simulation it creates allocation persistence that is distinct from pure
status quo bias because the reference point is an externally supplied default.

#### §4.2.2 Theoretical and Empirical Foundation

Madrian and Shea (2001) document automatic-enrollment effects. Cronqvist and
Thaler (2004) show persistent default choices in pension allocation.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `abs(deviation) <= active_deviation` | Hold | Maintains default allocation | §2.2 |
| `deviation < -active_deviation` | Buy | Rebalances only after large undervaluation | §2.2 |
| `deviation > active_deviation` | Sell | Trims only after large overvaluation | §2.2 |

#### §4.2.4 Behavioral Framework

The agent uses `active_deviation`, `default_weight`, and `base_size`. It treats
the default allocation as acceptable unless the valuation gap is large.

#### §4.2.5 Decision Process Walkthrough

At a 10% deviation and `active_deviation=0.15`, the agent holds. At a 20%
deviation, it submits a trade scaled by default weight.

#### §4.2.6 Worked Numerical Example

```text
P=80, F=100, delta=-0.20, active_deviation=0.15
Q = base_size * |delta| / active_deviation * default_weight
Q = 250 * 1.333 * 0.5 = 166 shares
```

#### §4.2.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Madrian and Shea (2001), https://doi.org/10.1162/003355301753265543 | Default-induced allocation persistence. |
| 2 | Cronqvist and Thaler (2004), https://doi.org/10.1257/0002828041301633 | Pension default portfolio persistence. |

### §4.3 ActiveRebalancer

#### §4.3.1 Summary

This investor represents portfolio managers who respond directly to valuation
gaps and rebalance toward fundamental value.

It is the rational benchmark against which inertial and default-following agents
are compared.

#### §4.3.2 Theoretical and Empirical Foundation

Markowitz (1952) motivates active portfolio adjustment. Standard rebalancing
practice motivates trading after valuation drift exceeds a threshold.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -rebalance_threshold` | Buy | Speeds undervaluation correction | §2.4 |
| `deviation > rebalance_threshold` | Sell | Speeds overvaluation correction | §2.4 |
| Small deviation | Hold | Avoids noise trading | §2.4 |

#### §4.3.4 Behavioral Framework

The agent uses `rebalance_threshold` and `position_size`. Quantity increases
with absolute deviation and is bounded by cash or inventory.

#### §4.3.5 Decision Process Walkthrough

If price is 94, fundamental is 100, and threshold is 5%, the agent buys because
the asset is undervalued by 6%.

#### §4.3.6 Worked Numerical Example

```text
P=94, F=100, delta=-0.06, threshold=0.05
Q = 350 * 0.06 / 0.05 = 420 shares
```

#### §4.3.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x | Rational portfolio response benchmark. |
| 2 | Benartzi and Thaler (2007), https://doi.org/10.1257/jep.21.3.81 | Contrast between active choice and inertia. |

### §4.4 MomentumTrader

#### §4.4.1 Summary

This investor represents trend followers who react to visible price movement
rather than default allocations.

It offsets pure inaction and can temporarily amplify mispricing by buying into
positive deviations or selling into negative deviations.

#### §4.4.2 Theoretical and Empirical Foundation

Jegadeesh and Titman (1993) document intermediate-horizon momentum returns. The
simulation uses deviation direction as the observable trend proxy.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation > entry_threshold` | Buy | Reinforces upward trend | §2.5 |
| `deviation < -entry_threshold` | Sell | Reinforces downward trend | §2.5 |
| Weak trend | Hold | Avoids excessive churn | §2.5 |

#### §4.4.4 Behavioral Framework

The agent uses `entry_threshold` and `position_size`. It follows deviation sign
as a compact proxy for trend pressure in this scenario.

#### §4.4.5 Decision Process Walkthrough

A 2% positive deviation with `entry_threshold=1%` triggers buying. A 0.5%
positive deviation does not.

#### §4.4.6 Worked Numerical Example

```text
P=102, F=100, delta=0.02, entry_threshold=0.01
Q = 300 * 0.02 / 0.01 = 600 shares, capped by cash
```

#### §4.4.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Jegadeesh and Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Momentum trading pressure. |
| 2 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x | Contrast with noise-driven orders. |

### §4.5 NoiseTrader

#### §4.5.1 Summary

This investor represents uninformed background flow from liquidity needs,
mistakes, or idiosyncratic portfolio changes.

It prevents the market from being fully deterministic and supplies baseline
orders for volume and price-path variation.

#### §4.5.2 Theoretical and Empirical Foundation

Black (1986) defines noise as information-free trading that makes markets
possible but imperfect. De Long et al. (1990) show that noise-trader risk can
affect prices.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| Random draw below `trade_probability` | Buy or sell random size | Background liquidity | §2.5 |
| Random draw above threshold | Hold | No informational content | §2.5 |

#### §4.5.4 Behavioral Framework

The agent uses `trade_probability` and `noise_size`. Action direction is random;
quantity is bounded by affordability and inventory.

#### §4.5.5 Decision Process Walkthrough

If the random draw activates and direction is buy, the order size is sampled
between 1 and `noise_size` shares, then capped by cash.

#### §4.5.6 Worked Numerical Example

```text
trade_probability=0.30, noise_size=100
draw=0.21 -> active; sampled quantity=64; action=random buy/sell
```

#### §4.5.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x | Noise-trader concept. |
| 2 | De Long et al. (1990), *Journal of Political Economy*, https://doi.org/10.1086/261703 | Noise-trader risk and price effects. |

## §5 Agent Diversity Verification

| Role | Agents | Diversity Contribution |
|---|---|---|
| Strong inertia | `InertialHolder` | Creates high hold rate after moderate signals. |
| Passive default | `DefaultFollower` | Separates external default effects from pure endowment. |
| Rational correction | `ActiveRebalancer` | Provides benchmark correction pressure. |
| Trend pressure | `MomentumTrader` | Allows market movement despite inertia. |
| Background liquidity | `NoiseTrader` | Adds non-informational volume. |

The scenario would not isolate status quo bias without the contrast between
§4.1/§4.2 and §4.3/§4.4.

## §6 Parameter Table

| Parameter | Meaning | Used By | Value | Source / Rationale | Sensitivity |
|---|---|---|---:|---|---|
| `initial_price` | Starting market price | Market | 100.0 | Normalized price base | Low |
| `fundamental_value` | Valuation anchor | Market | 100.0 | Normalized fundamental base | Medium |
| `price_impact` | Demand impact lambda | Market | 0.02 | Small impact to permit gradual underreaction | High |
| `mean_reversion` | Fundamental pull gamma | Market | 0.02 | Slow correction to preserve inertia effects | High |
| `noise_std` | Market shock sigma | Market | 0.01 | Low background volatility | Low |
| `change_threshold` | Status quo action threshold | InertialHolder | 0.30 | High switching threshold from §2.1 | High |
| `inertia_strength` | Dampens inertial order size | InertialHolder | 0.90 | Strong preference for current state | High |
| `active_deviation` | Default-follower action threshold | DefaultFollower | 0.15 | Default effect lower than pure inertia but higher than active benchmark | High |
| `default_weight` | Scaling of default-driven trade | DefaultFollower | 0.50 | Passive allocation adjustment | Medium |
| `rebalance_threshold` | Active trading threshold | ActiveRebalancer | 0.05 | Rational response band | High |
| `position_size` | Active/momentum sizing base | ActiveRebalancer, MomentumTrader | 300-350 | Calibrated to be visible but bounded | Medium |
| `entry_threshold` | Momentum activation threshold | MomentumTrader | 0.01 | Low trend-following threshold from §2.5 | Medium |
| `trade_probability` | Noise activation probability | NoiseTrader | 0.30 | Background liquidity intensity | Low |
| `noise_size` | Maximum sampled noise order | NoiseTrader | 100 | Keeps noise below strategic flow | Low |

## §7 Communication And Round Structure

1. The market broadcasts `price`, `fundamental`, `deviation`, `round`,
   `volume`, and `net_demand`.
2. Investors update cash, position, and observed market state.
3. Rule investors compute deterministic orders; API variants request canonical
   `<decision>` JSON with `action`, `bid_price`, `quantity`, and `reasoning`.
4. Orders are routed back to the market.
5. The market aggregates net demand and records the next price path.

## §8 Historical Case Studies

### §8.1 401(k) Automatic Enrollment

Automatic enrollment changed participation by assigning a default choice.
Madrian and Shea (2001) found participation for new hires rose from roughly
half to more than four-fifths. The `DefaultFollower` captures this by requiring
a large deviation before leaving the passive state.

### §8.2 Swedish Premium Pension Default

Cronqvist and Thaler (2004) document persistent use of default pension funds in
Sweden. This motivates the model's default-adherence metric and the distinction
between default following and active rebalancing.

### §8.3 Household Brokerage Inertia

Barber and Odean (2000) show that individual investors often trade poorly and
underperform. In this simulation, inertial and noise-driven investors create
sticky or low-information order flow that active traders must overcome.

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Research Use |
|---|---|---|
| Rule | Config-driven deterministic thresholds | Establishes baseline status quo underreaction. |
| LLM | Persona-only language reasoning with canonical order JSON | Tests whether language agents rationalize inaction. |
| RuleLLM | Persona plus explicit rule guidance | Tests whether rule text constrains LLM behavior. |
| Rag | RuleLLM-style persona plus retrieved behavioral-finance context | Tests whether domain evidence changes inertia and explanation quality. |
