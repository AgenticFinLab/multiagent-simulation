# LTCMCollapse — Simulation Design Basis

## §1 Phenomenon Definition

| Item | Description |
|---|---|
| Phenomenon Name | Long-Term Capital Management leveraged convergence-arbitrage collapse |
| Category | Leverage cycle, limits to arbitrage, liquidity spiral, systemic-risk intervention |
| Historical Anchor | August-September 1998 LTCM crisis following the Russian default and global flight to liquidity |
| Core Mechanism | Highly leveraged convergence trades become distressed when spreads widen instead of converge. Losses erode equity, VaR constraints and margin pressure force deleveraging, liquidity providers withdraw, and emergency official-sector coordination can stabilize the market. |
| Research Relevance | The scenario tests whether interacting arbitrageurs, leveraged traders, risk managers, liquidity providers, and lender-of-last-resort intervention can reproduce a stylized liquidity crisis without assuming an exogenous crash path. |

### §1.1 Origin And Source Analysis

LTCM is a canonical case where sophisticated arbitrage strategies were locally rational but systemically fragile. The fund's positions were designed to profit from convergence between related securities. After the Russian default in August 1998, investors moved toward liquidity and safety, spreads widened, and convergence trades lost money at precisely the moment leverage was highest.

The simulation abstracts that history into a single risky asset with a fixed fundamental anchor. Price deviation from the fundamental value is used as the common stress signal. A negative deviation stands in for widening spreads, liquidity discounts, and falling mark-to-market values on convergence positions.

### §1.2 Real-World Event Catalogue

| Event | Date | Magnitude | Agent Correspondence | Simulation Use |
|---|---:|---|---|---|
| Russian default and ruble devaluation | 1998-08 | Flight to liquidity; spread widening across global fixed-income markets | Exogenous stress represented by market noise plus endogenous sell pressure | Historical trigger for the LTCM stress state |
| LTCM losses and margin pressure | 1998-08 to 1998-09 | Equity reportedly fell sharply from roughly $4.7B at start of 1998 | `LeverageTrader`, `RiskManager` | Forced deleveraging and VaR cuts |
| Dealer and counterparty coordination | 1998-09 | Major banks coordinated a private-sector rescue | `CentralBank` as coordination proxy | Emergency liquidity injection |
| Liquidity withdrawal in convergence trades | 1998 | Previously correlated spreads moved adversely under stress | `LiquidityProvider` | Liquidity provision stops when deviation is large |
| Post-crisis risk-management debate | 1998 onward | VaR and leverage controls reassessed | `RiskManager` | Risk-cutting can stabilize individual books while amplifying market pressure |

## §2 Theoretical Foundation

### §2.1 Limits To Arbitrage

- **Citation**: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- **Mechanism**: Arbitrageurs may be correct about long-run convergence but still be forced out when short-run losses trigger investor withdrawals or margin pressure.
- **Mathematical Formulation**:
  ```
  trade when |delta(t)| > theta_entry
  exposure(t) = leverage * cash(t) * |delta(t)| / P(t)
  ```
  where `delta(t) = (P(t) - F) / F`.
- **Empirical Relevance**: LTCM held relative-value positions that were expected to converge, but losses expanded when spreads moved further away from fundamental value.
- **Agent Mapping**: `ConvergenceArbitrageur` in §4.1.

### §2.2 Leverage Cycle And Margin Pressure

- **Citation**: Geanakoplos, J. (2010). The leverage cycle. In *NBER Macroeconomics Annual 2009*, 24, 1-65. https://doi.org/10.1086/648285
- **Mechanism**: Leverage expands balance sheets in tranquil periods and forces rapid contraction when asset values fall.
- **Mathematical Formulation**:
  ```
  equity(t) = cash(t) + position(t) * P(t) - |position(t) * P(t)| / leverage_ratio
  margin breach when equity(t) < margin_call_threshold * |position(t) * P(t)|
  ```
- **Empirical Relevance**: LTCM's high leverage made small spread moves large relative to equity.
- **Agent Mapping**: `LeverageTrader` in §4.2.

### §2.3 VaR-Based Risk Management And Procyclicality

- **Citation**: Jorion, P. (2000). Risk management lessons from Long-Term Capital Management. *European Financial Management*, 6(3), 277-300. https://doi.org/10.1111/1468-036X.00125
- **Mechanism**: Risk limits reduce individual exposure but can be procyclical when many institutions cut positions at the same time.
- **Mathematical Formulation**:
  ```
  risk breach when |delta(t)| > 3 * VaR_limit
  cut_quantity(t) = 0.50 * |position(t)|
  ```
- **Empirical Relevance**: The crisis exposed model-risk and tail-risk limitations in risk systems calibrated on normal-market correlations.
- **Agent Mapping**: `RiskManager` in §4.3.

### §2.4 Liquidity Black Holes

- **Citation**: Morris, S., & Shin, H. S. (2004). Liquidity black holes. *Review of Finance*, 8(1), 1-18. https://doi.org/10.1093/rof/8.1.1
- **Mechanism**: When traders expect others to withdraw or sell, liquidity can disappear endogenously, producing a self-reinforcing price move.
- **Mathematical Formulation**:
  ```
  provide liquidity when |delta(t)| <= theta_stress
  withdraw when |delta(t)| > theta_stress
  ```
- **Empirical Relevance**: During the LTCM crisis, positions that appeared liquid became hard to unwind without large price concessions.
- **Agent Mapping**: `LiquidityProvider` in §4.4.

### §2.5 Lender Of Last Resort

- **Citation**: Bagehot, W. (1873). *Lombard Street: A Description of the Money Market*. Henry S. King.
- **Mechanism**: During systemic panic, a credible liquidity backstop can arrest fire-sale dynamics.
- **Mathematical Formulation**:
  ```
  intervene when delta(t) < -theta_intervention and u < rescue_probability
  injection_quantity = 2000
  ```
- **Empirical Relevance**: The Federal Reserve Bank of New York facilitated a private-sector rescue of LTCM to reduce systemic spillovers.
- **Agent Mapping**: `CentralBank` in §4.5.

## §3 Market Design Principles

### §3.1 Price Formation Model

The market uses a linear order-imbalance model:

```
P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 0.01)
D(t) = buy_volume(t) - sell_volume(t)
epsilon(t) ~ N(0, sigma^2)
delta(t) = (P(t) - F) / F
```

| Symbol | Config / Code Field | Baseline | Meaning |
|---|---|---:|---|
| `P(t)` | `state.custom_state["price"]` | 100.0 initial | Market price |
| `F` | `extras["fundamental_value"]` | 100.0 | Fundamental anchor |
| `lambda` | `extras["price_impact"]` | 0.03 | Price impact per net-demand unit |
| `gamma` | `extras["mean_reversion"]` | 0.01 | Mean reversion toward fundamental |
| `sigma` | `extras["noise_std"]` | 0.015 | Gaussian noise standard deviation |

### §3.2 Market Broadcast

Each round the market broadcasts:

| Field | Meaning | Consumed By |
|---|---|---|
| `price` | Current simulated price | all investors |
| `fundamental` | Fundamental anchor | all investors |
| `deviation` | `(price - fundamental) / fundamental` | all investors |
| `round` | Simulation round | state tracking and records |

### §3.3 Order Schema

Investor actions are standard trading orders:

```json
{"type": "order", "action": "buy|sell|hold", "quantity": 0}
```

LLM-family variants additionally request `bid_price` and `reasoning` in the decision JSON for parser consistency, but the market clearing code consumes `action` and `quantity`.

## §4 Investor Taxonomy

### §4.1 ConvergenceArbitrageur

#### §4.1.1 Summary

The `ConvergenceArbitrageur` represents an LTCM-style relative-value trader that sees deviations from fundamental value as convergence opportunities. It is destabilizing when the trade is leveraged because buying into widening discounts or selling overvalued prices increases exposure while the market can continue moving against the position.

The simulation uses this investor to model the central LTCM hypothesis: sophisticated arbitrage can be correct in the long run and still fragile under short-run funding pressure.

#### §4.1.2 Theoretical and Empirical Foundation

Primary theory is limits to arbitrage (§2.1). The agent uses `entry_spread`, `leverage`, and `max_position` to translate deviations into leveraged order size. Empirically, LTCM's convergence trades were exposed to spread widening after the Russian default, making the strategy a natural mapping to this agent.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) <= entry_spread` | Hold | No spread opportunity | §2.1 |
| `deviation < -entry_spread` | Buy up to leveraged cash and cap | Attempts convergence, absorbs supply but increases exposure | §2.1 |
| `deviation > entry_spread` | Sell existing holdings | Bets on downward convergence | §2.1 |

#### §4.1.4 Behavioral Framework

Information set: `price`, `fundamental`, `deviation`, `cash`, `position`. Trigger function: `abs(deviation) > entry_spread`. Sizing function:

```
Q(t) = min(floor(cash(t) * leverage * |deviation(t)| / P(t)), max_position)
```

State variables are cash and position. Position is updated after order execution.

#### §4.1.5 Decision Process Walkthrough

If price is 95 and fundamental is 100, then `deviation = -0.05`. With `entry_spread = 0.03`, `leverage = 15`, and positive cash, the agent buys because the discount exceeds its entry threshold.

#### §4.1.6 Worked Numerical Example

With cash 2,000,000, price 95, deviation -0.05, and leverage 15:

```
raw_quantity = floor(2,000,000 * 15 * 0.05 / 95) = 15,789
quantity = min(15,789, 5,000) = 5,000
```

#### §4.1.7 Academic References

Shleifer & Vishny (1997); Jorion (2000); Lowenstein (2000), *When Genius Failed*.

### §4.2 LeverageTrader

#### §4.2.1 Summary

The `LeverageTrader` represents balance-sheet-constrained investors whose actions are dominated by leverage and margin pressure. Under normal undervaluation the trader may buy; under equity erosion it must deleverage.

This investor produces forced selling pressure after losses accumulate, capturing the leverage-cycle channel of the LTCM crisis.

#### §4.2.2 Theoretical and Empirical Foundation

The primary basis is the leverage cycle (§2.2). The code computes equity from portfolio value and leverage exposure, then triggers a 30% deleveraging order when equity falls below a margin-call threshold.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| Equity below margin threshold | Deleverage 30% of absolute position | Fire-sale pressure or short covering | §2.2 |
| `deviation < -0.03` and no margin breach | Buy with leveraged capacity | Adds convergence exposure | §2.1, §2.2 |
| Otherwise | Hold | No new pressure | §2.2 |

#### §4.2.4 Behavioral Framework

Trigger:

```
equity(t) < margin_call_threshold * |position(t) * P(t)|
```

Sizing:

```
Q_delever(t) = floor(0.30 * |position(t)|)
```

The agent tracks cash and position and reacts to price through current portfolio value.

#### §4.2.5 Decision Process Walkthrough

When losses reduce equity below the margin-call threshold, the trader sells if long and buys if short. If no margin call is active and the asset is undervalued by more than 3%, the trader adds a leveraged long.

#### §4.2.6 Worked Numerical Example

If position is 500 shares, the forced deleveraging quantity is:

```
Q = floor(0.30 * 500) = 150
```

#### §4.2.7 Academic References

Geanakoplos (2010); Brunnermeier & Pedersen (2009); Jorion (2000).

### §4.3 RiskManager

#### §4.3.1 Summary

The `RiskManager` represents institutional risk-control desks that cut exposure when deviations exceed allowed risk limits. The agent is stabilizing at the individual-book level but can amplify systemic stress when many agents cut positions simultaneously.

#### §4.3.2 Theoretical and Empirical Foundation

The design is based on VaR procyclicality (§2.3). It operationalizes a risk breach when price deviation exceeds three times the configured VaR limit.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 3 * var_limit` and long | Sell 50% of position | Risk reduction, possible sell pressure | §2.3 |
| `abs(deviation) > 3 * var_limit` and short | Buy to cover 50% | Risk reduction, possible buy pressure | §2.3 |
| Within risk limits | Hold | No action | §2.3 |

#### §4.3.4 Behavioral Framework

Trigger:

```
|delta(t)| > 3 * VaR_limit
```

Sizing:

```
Q_cut(t) = floor(0.50 * |position(t)|)
```

#### §4.3.5 Decision Process Walkthrough

At `var_limit = 0.05`, a 16% deviation exceeds `3 * var_limit = 15%`, causing a 50% position cut.

#### §4.3.6 Worked Numerical Example

If position is 500 and deviation is -0.16:

```
Q = floor(0.50 * 500) = 250 sell
```

#### §4.3.7 Academic References

Jorion (2000); Danielsson et al. (2001), "An academic response to Basel II."

### §4.4 LiquidityProvider

#### §4.4.1 Summary

The `LiquidityProvider` represents market makers that supply liquidity when deviations are moderate but withdraw when stress becomes large. Its withdrawal is central to the liquidity-black-hole mechanism.

#### §4.4.2 Theoretical and Empirical Foundation

The design follows Morris & Shin's liquidity black-hole mechanism (§2.4). Liquidity provision is conditionally stabilizing and disappears in stressed deviations.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) > 0.05` | Hold | Withdraws liquidity under stress | §2.4 |
| `abs(position) < inventory_limit` and `deviation > 0` | Sell up to 500 | Mean-reversion supply | §2.4 |
| `abs(position) < inventory_limit` and `deviation <= 0` | Buy up to 500/cash limit | Mean-reversion demand | §2.4 |

#### §4.4.4 Behavioral Framework

The stress trigger is `abs(deviation) > 0.05`; the inventory cap is `inventory_limit`. Normal-market size is capped at 500 shares per round.

#### §4.4.5 Decision Process Walkthrough

If deviation is -2% and inventory room remains, the agent buys. If deviation is -7%, it withdraws and holds.

#### §4.4.6 Worked Numerical Example

With inventory limit 2,000 and current position 1,000, inventory room is 1,000. The per-round cap binds at 500 shares.

#### §4.4.7 Academic References

Morris & Shin (2004); Brunnermeier & Pedersen (2009).

### §4.5 CentralBank

#### §4.5.1 Summary

The `CentralBank` represents official-sector or coordinated private-sector lender-of-last-resort intervention. It is not a literal central-bank asset purchase model; it abstracts the 1998 coordination role into a stabilizing liquidity injection.

#### §4.5.2 Theoretical and Empirical Foundation

The design follows Bagehot's lender-of-last-resort principle (§2.5) and the historical New York Fed-facilitated coordination among LTCM counterparties.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -intervention_threshold` and random draw succeeds | Buy 2,000 | Stabilizing liquidity injection | §2.5 |
| Stress below threshold or failed probability draw | Hold | No intervention | §2.5 |

#### §4.5.4 Behavioral Framework

Trigger:

```
delta(t) < -intervention_threshold and u < rescue_probability
```

Sizing is fixed at 2,000 shares to model a discrete support operation.

#### §4.5.5 Decision Process Walkthrough

At deviation -12%, threshold 10%, and a successful probability draw, the agent buys 2,000 shares.

#### §4.5.6 Worked Numerical Example

With price 90, a 2,000-share intervention contributes 180,000 notional buy demand before market impact.

#### §4.5.7 Academic References

Bagehot (1873); Lowenstein (2000); Jorion (2000).

## §5 Agent Diversity Verification

| Agent | Direction In Stress | Stabilizing? | Distinct Signal |
|---|---|---|---|
| `ConvergenceArbitrageur` | Adds convergence exposure | Mixed | `abs(deviation) > entry_spread` |
| `LeverageTrader` | Forced deleveraging | Destabilizing | equity/margin condition |
| `RiskManager` | Cuts exposure | Individually stabilizing, systemically destabilizing | `abs(deviation) > 3 * var_limit` |
| `LiquidityProvider` | Withdraws under stress | Stabilizing only in normal range | `abs(deviation) > 0.05` |
| `CentralBank` | Buys in severe stress | Stabilizing | `deviation < -intervention_threshold` |

The mix covers rational arbitrage, funding fragility, institutional risk control, liquidity supply, and emergency support. No two investor types share the same trigger and market role.

## §6 Parameter Table

| Parameter | Baseline | Config Location | Source / Rationale |
|---|---:|---|---|
| `initial_price` | 100.0 | `market.extras` | normalized price index |
| `fundamental_value` | 100.0 | `market.extras` | normalized fundamental anchor |
| `price_impact` | 0.03 | `market.extras` | stress-market order impact calibration |
| `mean_reversion` | 0.01 | `market.extras` | slow correction during liquidity crisis |
| `noise_std` | 0.015 | `market.extras` | small exogenous price disturbance |
| `entry_spread` | 0.03 | `convergencearbitrageur.extras` | convergence trade activation threshold |
| `leverage` | 15 | `convergencearbitrageur.extras` | stylized LTCM leverage exposure |
| `max_position` | 5000 | `convergencearbitrageur.extras` | position cap for numerical stability |
| `leverage_ratio` | 25 | `leveragetrader.extras` | high leverage consistent with LTCM-style balance sheet |
| `margin_call_threshold` | 0.04 | `leveragetrader.extras` | equity buffer trigger |
| `var_limit` | 0.05 | `riskmanager.extras` | VaR-style risk threshold |
| `inventory_limit` | 2000 | `liquidityprovider.extras` | market-maker inventory capacity |
| `intervention_threshold` | 0.10 | `centralbank.extras` | systemic stress threshold |
| `rescue_probability` | 0.5 | `centralbank.extras` | probabilistic intervention to model coordination uncertainty |

## §7 Communication And Round Structure

Each round follows:

1. Market receives prior investor orders and updates price.
2. Market broadcasts `market_update`.
3. Investors perceive the update and update local state.
4. Rule investors compute deterministic actions; API variants call an LLM using the same market state.
5. Investor actions are emitted as `order` messages.
6. The next market round clears those orders.

The simulation is configured for 200 rounds in all variants.

## §8 Historical Case Studies

### §8.1 LTCM 1998

The main case is LTCM's 1998 collapse. The model maps convergence arbitrage to `ConvergenceArbitrageur`, balance-sheet pressure to `LeverageTrader`, risk reduction to `RiskManager`, liquidity disappearance to `LiquidityProvider`, and rescue coordination to `CentralBank`.

### §8.2 Russian Default And Flight To Liquidity

The Russian default is represented indirectly as the stress environment in which deviations widen and liquidity providers withdraw. It motivates the negative-deviation stress signal rather than a separate exogenous news actor.

### §8.3 Later Deleveraging Episodes

Episodes such as 2007-2008 quant deleveraging and 2020 Treasury-market stress provide analogues for liquidity spirals and coordinated support. These cases are relevant to RAG knowledge content but are not separate modeled events.

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Expected Use |
|---|---|---|
| Rule | deterministic formulas from §4 | calibrated baseline |
| LLM | persona-only market reasoning | tests whether language agents reproduce similar stress responses without explicit formula execution |
| RuleLLM | persona plus explicit decision rules | should stay close to Rule while allowing LLM reasoning variation |
| Rag | RuleLLM-style agents with retrieved crisis context | tests whether historical knowledge changes risk-taking, deleveraging, or intervention timing |
